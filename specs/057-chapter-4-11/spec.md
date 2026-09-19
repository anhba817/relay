# Feature Specification: Chapter 4.11 — the half of the union that was refused

**Feature Branch**: `057-chapter-4-11`

**Created**: 2026-09-19

**Status**: Draft

**Input**: User description: "next chapter"

## The brief, and the two things it does not say

`docs/12` §3 row 12, movement V: *"FR-MED-06. Chapter 3.24 shipped `media_not_available` (422)
to refuse `media_id` **by name**, as a discriminated union built for this arm to be filled. This
chapter fills it."*

Both halves are true. What the line does not say:

**FR-MED-06 NAMES TWO STATES AND THE SCHEMA PERMITS ONE.** The clause is *"a message may attach a
`media_id` in state `pending` or `ready`"*, and chapter 4.10's migration carries
`CONSTRAINT media_objects_state_check CHECK (state = 'pending')` with a comment saying why:
*"`ready` and `rejected` arrive [with the worker]… a schema claiming states nothing in the
platform can reach."* Verification is FR-MED-03, movement VI. So the clause's `ready` is
unreachable, its implied `rejected` refusal has nothing to refuse, and **a test of either cannot
fail** — the class this project names *"a test whose condition cannot occur is a test that cannot
fail."* This chapter builds the check the clause asks for and says which of its arms no fixture
can reach.

**AND THE CODE THIS CHAPTER RETIRES LEAVES A GAP IT MUST FILL.** `packages/protocol/src/codes.ts`
says of `media_not_available`: *"§4.14 REPLACES THE ARM RATHER THAN THIS CODE. When hosted media
ships, the `{ type: "media" }` arm starts accepting and this entry describes a state the platform
no longer has — at which point it is deleted, not repurposed."* Deleting it is right and it is not
the whole change: a `media_id` that does not exist, one belonging to another tenant, and one
belonging to another user all need an answer, and none of them is *"hosted media is not available
yet"*.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A photo sends the moment its upload finishes (Priority: P1)

A customer's user takes the slot chapter 4.10 issues, uploads the file straight to object storage,
and sends a message carrying `{ "type": "media", "media_id": "…" }`. The message is accepted and
delivered. The object is still `pending` — nothing has verified the bytes — and that is the
design: FR-MED-06's own note says *"the scan is a delivery gate for bytes, never for the
message."*

**Why this priority**: It is the half of FR-MSG-11 the platform has published and refused since
chapter 3.24, and every later media chapter needs a message that can carry a `media_id` to have
anything to act on.

**Independent Test**: Request a slot, upload to the signed URL, send a message naming the returned
`media_id`, and read the message back. Delivers the clause's whole accept path with nothing else
built.

**Acceptance Scenarios**:

1. **Given** a slot issued to a user token and an object uploaded to it, **When** that user sends a
   message attaching the `media_id`, **Then** the message is created and the attachment is stored
   in the order sent.
2. **Given** a slot issued to an API key, **When** that key sends a message attaching the
   `media_id`, **Then** the message is created.
3. **Given** a message carrying one media attachment and one URL attachment, **When** it is sent,
   **Then** both are stored, in order, and the ten-attachment cap counts them together.
4. **Given** a message carrying a media attachment and no text, **When** it is sent, **Then** it is
   accepted — chapter 3.24's rule for the URL arm, unchanged.

---

### User Story 2 - Somebody else's media cannot be attached (Priority: P2)

A caller attaches a `media_id` that belongs to another tenant, to another user, or to nobody at
all. Each is refused, and the three refusals are indistinguishable from each other.

**Why this priority**: FR-MED-06's second sentence is *"Attaching another tenant's or user's media
shall fail"*, and constitution I is what makes the indistinguishability part of the requirement
rather than a nicety: a refusal that tells a caller "that id exists but is not yours" is a
cross-tenant existence oracle.

**Independent Test**: Two tenants, two users, and one invented UUID. Four sends, one accepted,
three refused with the same code and the same message.

**Acceptance Scenarios**:

1. **Given** a `media_id` belonging to another environment, **When** a caller attaches it, **Then**
   the send is refused and no message row is created.
2. **Given** a `media_id` belonging to another user of the same environment, **When** a user token
   attaches it, **Then** the send is refused.
3. **Given** a `media_id` that no media object has, **When** a caller attaches it, **Then** the
   send is refused with the same code and message as the two above.
4. **Given** a message whose tenth attachment is a foreign `media_id`, **When** it is sent, **Then**
   the whole message is refused and none of the other nine is stored.

---

### User Story 3 - The clause's unreachable half is recorded, not faked (Priority: P3)

FR-MED-06 permits `pending` or `ready` and forbids everything else. Only `pending` exists. The
chapter builds the check and publishes which arms no fixture can reach and why.

**Why this priority**: It is what keeps the chapter honest, and it is this project's established
answer to a clause it cannot fully satisfy — chapter 4.7 amended FR-ANL-06 rather than publishing
a green number, and chapter 4.8 defined FR-ANL-10's quantity and computed nothing.

**Independent Test**: The state predicate is exercised against `pending`; an attempt to plant a
`ready` or `rejected` row is refused by the database, and the refusal is the evidence.

**Acceptance Scenarios**:

1. **Given** the shipped schema, **When** a fixture attempts to store a media object in state
   `ready`, **Then** the database refuses it by name.
2. **Given** that refusal, **When** the chapter publishes its state check, **Then** the unreachable
   arms are named in the code and in the record rather than covered by a test that cannot fail.

### Edge Cases

- **The same `media_id` twice in one message.** Chapter 3.24 settled the URL case — *"the same URL
  twice is two attachments, because the platform does not compare them."* The same rule applies
  here unless a reason to differ is found.
- **A media object attached to two different messages.** Nothing forbids it and nothing tracks it.
  FR-MED-10's unlink-and-sweep is a later chapter, so this chapter records what a second reference
  means for that sweep rather than building for it.
- **A `media_id` that is not a UUID.** The current arm accepts `z.string().min(1)`. A malformed id
  is a different failure from a well-formed id nobody owns, and the two must not be conflated —
  one is `invalid_request` at the schema, the other is this chapter's refusal.
- **An API key sends on behalf of a bot user.** The send path resolves a bot user from the body.
  Whether that bot counts as "the sending user" for a `user_id`-bearing object is the assumption
  flagged below.
- **A slot issued and never uploaded to.** `state` is `pending` either way — the platform cannot
  tell. `gaps.md` 056-1 records that a slot nobody uploads to holds its bytes forever; attaching
  one is the same blind spot from the other side.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `{ type: "media" }` attachment arm MUST accept a `media_id` that names a media
  object in the sending environment, instead of refusing unconditionally. **This is two doors, not
  one.** `messageSendSchema` embeds the same union, so a socket client's `message.send` frame
  carries attachments to the api through the internal seam — the arm accepting changes the REST
  route and the WebSocket path together.
- **FR-001a**: A socket client MUST be able to attach a `media_id` and MUST receive the same
  decision as the REST route: the message commits, or it is refused with the api's own code. The
  gateway already forwards a 4xx whose code is in the registry; what MUST NOT happen is a socket
  client getting `invalid_frame` for a well-formed id, which is what the arm's schema refusal
  produces today.
- **FR-001b**: The socket test that asserts today's refusal MUST be converted rather than deleted.
  Its comment states what it is for — *"the only thing that can tell the two-arm schema from a
  one-arm one on this door"* — and that property still needs an assertion once the arm accepts.
- **FR-002**: A send MUST be refused when the named media object belongs to another environment.
- **FR-003**: A send MUST be refused when the caller is a user token and the named media object
  was uploaded by a different user.
- **FR-004**: A send MUST be refused when no media object has the named id.
- **FR-005**: FR-002, FR-003 and FR-004 MUST return the same code and the same message. A caller
  MUST NOT be able to tell an id that exists elsewhere from one that exists nowhere.
- **FR-006**: A refused send MUST create no message row and no outbox row, and MUST NOT advance
  the channel's sequence.
- **FR-007**: The check MUST be applied to every attachment in the message, and one failure MUST
  refuse the whole message.
- **FR-008**: `media_not_available` MUST be removed from the error registry and from the published
  error reference, because the state it describes no longer exists. The registry's own note
  requires deletion rather than repurposing.
- **FR-008a**: `media_id` MUST be validated as a UUID before any lookup. A malformed id MUST be
  refused at the schema with `invalid_request` and the field named. Measured (research R3): the
  arm's current `z.string().min(1)` sends a non-UUID to the driver, which answers
  `invalid input syntax for type uuid`, and the error filter turns that into a **500 the caller
  triggered**.
- **FR-009**: The refusal FR-005 names MUST be a code of its own, documented in the error
  reference, with a status the error filter's ladder maps.
- **FR-009b**: The 422 rung's code MUST be named and documented like any other, with a sentence
  saying what a client does about it. It is a fallback with no thrower, which is what
  `service_unavailable` is, and the reference section is what stops it being a string in a
  registry nobody can act on.
- **FR-009a**: **422 MUST join that ladder.** It is the last status the platform uses that the
  filter falls through to `internal_error` for — chapter 4.10 added rungs for 402, 413, 415 and
  503 and left this one. Every 422 in the platform names its own code today, so the rung has no
  live user; it exists for the same reason `service_unavailable` does, which is that the next
  thrower to forget is the one it is for.
- **FR-010**: The state predicate MUST admit `pending` and `ready` and refuse anything else, and
  the chapter MUST record which of those arms no fixture can reach and why.
- **FR-011**: The check MUST read the media object inside the transaction that writes the message.
- **FR-012**: A media attachment MUST count toward FR-MSG-11's ten-attachment cap alongside URL
  attachments.
  *A bare `FR-012` means something else 400 lines from where this chapter works:
  `repository.ts:4877`'s tombstone comment uses it for "deleting a message unlinks its
  attachments". Both are feature-local ids from different features and the SRS has neither — the
  `FR-003a` class. Cite this one by the cap, not by the number, anywhere a reader meets both.*
- **FR-013**: Delivery MUST NOT carry attachment state, and that MUST be asserted rather than left
  to hold by default. FR-MED-07's `media.updated` and the state field are a later chapter, and
  adding either here would ship its surface without its checks. A message read back MUST carry the
  attachment array exactly as sent — the same shape chapter 4.10 gave FR-016, which needed a test
  precisely because "we did not add it" is not a property anything checks. **There are three doors
  to check, not one**: history, the live socket frame, and the backfill a resuming client reads,
  which passes `row.attachments` straight through.
- **FR-018**: **The durable reader MUST NOT refuse a shape its writer may produce.**
  `outboxEventSchema` validates `attachments` with the same union, twice, and
  `consumer/runtime.ts` answers a failed parse with `message.term()` — so a message committed by
  a new instance and read by an old one during a rolling deploy is **destroyed permanently**, with
  the send already acknowledged. Constitution II. The consumer never reads `attachments` (zero
  occurrences) and nothing downstream of the parse does either, so the strictness buys nothing and
  costs the message.
- **FR-018a**: The fix MUST be tested against the arm as it stands today, because the lane runs
  with the consumer switched off and cannot find this class on its own. `outbox/event.ts`'s own
  header records the previous instance: *"the api suite stayed green through 505 tests with the
  defect in place."*
- **FR-018b**: **The synchronous reader has the same obligation as the durable one.**
  `internalSendResponseSchema` is a `strictObject` carrying a required
  `attachments: z.array(attachmentSchema)`, and `services/gateway/src/api-client.ts:247` parses
  the api's send response with it. An old gateway reading a new api's response refuses the payload
  and the socket closes **1011** — the file's own words, from the chapter that added the field.
  The message is committed, so the client loses its acknowledgement and its connection, and an
  idempotent retry fails identically.
- **FR-018c**: The chapter MUST enumerate every place an attachment array is validated, and say
  which of them cross a process boundary. There are **ten**: seven that name `attachmentSchema`
  directly, and three that reach it by embedding `messageSchema`. They were found one per analysis
  pass; the next change to this union should read a list rather than rediscover it. **The
  enumeration MUST be by what is parsed, not by what is named** — the first version of this list
  asked "who parses this schema?" of each direct site, answered *"nothing at runtime"* for
  `messageSchema`, and missed the three hottest readers in the platform.
- **FR-018d**: The three readers that reach the union through `messageSchema` MUST accept an
  unrecognised attachment shape: the gateway's fanout consumer for `message.created`, the same
  consumer for a revision, and the gateway's backfill response reader. Each parses a payload the
  **api** produced, across a boundary the two services deploy independently. Today all three reject
  a media arm, and the live-delivery one drops the frame with a log line after the send has been
  acknowledged with a 201 — a committed message that reaches no socket.
  **`messageSchema` itself stays strict.** It is what the api BUILDS, and `Message` is inferred
  from it; widening it would weaken every construction site, which is the defect FR-022's own
  comment was written to prevent. The reader sites take a variant.
- **FR-020**: Editing a message that carries a media attachment MUST leave the attachment
  unchanged, asserted rather than assumed. `repository.ts:4604` states the property — *"an edit
  does not change attachments (FR-016)"* — and this chapter creates the first media attachment
  there is to preserve.
- **FR-026**: The composed api MUST be able to issue a usable upload slot. `compose.yaml`'s `api`
  service names `postgres:5432`, `nats:4222`, `redis:6379` and `clickhouse` in its environment and
  **names MinIO nowhere**, while `depends_on` waits on it — so `store.ts:18` falls back to
  `http://localhost:9100`, which inside that container is that container. `storeReady()`'s signed
  HEAD is refused, and FR-017 answers **503 `media_storage_unavailable` to every slot request**:
  4.10's outage refusal, permanent, for a reason that is not an outage.
  **AND THE ADDRESS IS A DECISION, NOT A MISSING LINE.** `storeConfig` has one `endpoint` and two
  consumers that want different ones: the probe needs an address the api can reach
  (`http://minio:9000`), the presigned URL needs one the **client** can reach
  (`http://localhost:9100`), and the host is inside the signature, so a URL signed for one is
  refused from the other. They coincide only because every lane runs the api as a host process.
  The chapter states which it splits and records the alternative.
- **FR-027**: The quickstart MUST run as written, and the chapter MUST say that it was run. Its
  prerequisite block starts stores and the api carries `profiles: ["services"]`, so nothing answers
  `localhost:4000`; and `$USER_TOKEN` has no published source — `ci.yml:305` says *"There is no
  public way to obtain one"* and uses `scripts/seed-demo-tenant.mjs`. NFR-USE-03 makes this a `T`
  clause at 100% and **no CI job runs any quickstart**, so the only verification available is
  running it.
- **FR-023**: The chapter MUST state which form constitution VI's *"tenant isolation MUST have
  100% branch coverage (NFR-MNT-02)"* takes over this chapter's predicate, and record the
  measurement either way. The predicate is a SQL `WHERE` and carries no JavaScript branches — 048
  recorded the same clause as unmeasurable for the same reason, that a schema has none. The
  JavaScript around it does: the caller-kind signal, the position-preserving set difference, and
  the refusal's `field` index. Those land in `repository.ts`, pinned at **branches 92** against a
  measured 92.66, so **an uncovered isolation arm passes the ratchet** with room to spare. Silence
  is what the plan's principle VI row currently offers, and it is the third Part 4 chapter to meet
  this clause in a form the number cannot show.
- **FR-024**: Deleting a message that carries a media attachment MUST be asserted: the tombstone's
  list is `[]`, the column is null, and the media row survives with its bytes and its quota. The
  code is arm-agnostic, which is the argument R6 rejected for the cap — and the reason is stronger
  here, because for the URL arm an unlink costs nothing and for this arm it is the first time
  unlinking strands bytes the platform stores and the quota counts.
- **FR-021**: The sealed outsider suite MUST carry the media arm. `integrate.itest.ts` is the one
  place the platform is exercised from outside with nothing but a published credential, and its
  attachment test annotates the frames it reads as `{ url?: string }[]` — the old assumption
  written into a type. A chapter whose claim is that a second arm now works end to end and that
  leaves this suite url-only has proven the claim everywhere except where it is worth proving.
- **FR-019**: The chapter MUST record that `attachment_count` in the analytical store changes
  meaning. `load-analytics.mjs` computes `JSONLength(m.attachments)`, which has counted external
  URLs for every row ever written and starts counting hosted media alongside them with nothing
  able to tell the two apart.
- **FR-014**: The cross-tenant suite MUST attack the new path, and the attack MUST plant a media
  object for each of two tenants so that an empty table cannot pass it.
- **FR-015**: The chapter MUST record what a second message referencing one media object means for
  FR-MED-10's unlink-and-sweep, which no chapter has built.
- **FR-016**: The fence chain MUST report **0** after the chapter, and the number MUST be stated
  absolutely rather than as a delta.
- **FR-017**: **Both copies of the Part 4 chapter table** MUST be amended with what row 12 did not
  say — `docs/12` §3 and `docs/07-tutorial-plan.md`'s Part 4 section, which carries the same table
  and has never been amended by any chapter. This chapter has three findings of that shape: the
  clause names a state the schema cannot reach, the arm ships a caller-triggered 500 the moment it
  accepts, and the assumption about a tenant-uploaded object is the opposite of what the row's
  own predecessor wrote the nullable column for.
  The second copy additionally carries three corrections it never received: row 11's *"four
  distinct refusals"* (056 amended `docs/12` alone), a chapter count stated as **23** when the
  second contraction took it to 22 on 2026-09-13, and *"milestones at 10, 18 and 23"* — original
  ordinals presented as current, where `docs/12:225-227` says in as many words that its first
  column keeps them and that the movement column is the stable address.

### Key Entities

- **Media object**: what chapter 4.10 creates — an id, the environment that owns it, the user who
  uploaded it or nothing when an API key did, a declared filename, MIME type and size, a state,
  and the key it occupies in the store. This chapter reads it and changes nothing about it.
- **Attachment**: one element of a message's array. Two arms today, discriminated on `type`. The
  URL arm carries a kind and a URL; the media arm carries an id and, after this chapter, means
  something.
- **Message**: the row the send writes. It stores the attachment array as sent, in order, with no
  de-duplication.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can request a slot, upload a file, and send a message carrying its `media_id`
  in one sequence, with no step refused.
- **SC-002**: Three refusals — another tenant's id, another user's id, and an id nobody owns —
  return byte-identical bodies apart from the request id, **for the same attachment position**.
  The qualifier is load-bearing: the refusal's `field` carries the attachment's index, so two
  refusals at different positions differ for a reason that has nothing to do with the property
  this criterion is about.
- **SC-002a**: A socket client attaching a valid `media_id` commits, and one attaching a foreign
  id receives the api's own code rather than `invalid_frame`. Measured on the socket, not inferred
  from the REST route passing.
- **SC-002b**: An outbox envelope carrying a media attachment parses under the consumer's schema,
  and the test that proves it **fails against the arm as it stands today**. A durable-reader test
  that cannot go red is the class this chapter is trying not to join.
- **SC-002c**: An api send response carrying a media attachment parses under the gateway's
  schema, and the test fails against the arm as it stands today — the same red-first requirement
  SC-002b places on the durable reader.
- **SC-012**: A slot requested from the **composed** api — `docker compose --profile services up`,
  not a host-spawned process — answers 201, and the URL it returns accepts a PUT from outside the
  compose network. Measured, with the 503 it answers today recorded beside it.
- **SC-011**: The predicate's coverage is recorded as a figure with the form named: how many of its
  clauses are SQL and carry no branch, how many JavaScript arms it adds, and what each of those
  arms measured. A statement that the clause is *met rather than pinned* counts only with the
  per-arm evidence beside it.
- **SC-002e**: Three tests, each red against the arm as it stands today: a fanned-out
  `message.created` carrying a media attachment is **delivered** rather than dropped, a revision
  carrying one is delivered, and a backfill response carrying one parses rather than degrading the
  resume. Red-first, for the reason SC-002b gives — a reader test that cannot go red is the class
  this chapter is trying not to join.
- **SC-002d**: The sealed suite delivers **one url attachment and one media attachment** to a
  socket, in order, using nothing but a published credential — a slot, an upload, a send, and the
  frame. Measured from outside the platform, which is the only place this claim is worth making.
- **SC-003**: A refused send leaves the channel's message count and sequence unchanged, measured
  before and after and scoped to the test's own channel.
- **SC-004**: `pnpm check:errors` passes in both directions after `media_not_available` is removed
  and the new code is added, and the counted success line is read rather than the exit code.
- **SC-005**: The cross-tenant suite reports every derived route classified and every classified
  route attacked, and the new attack fails when the environment predicate is removed.
- **SC-006**: An attempt to store a media object in state `ready` is refused by the database, and
  the refusal is quoted in the record.
- **SC-007**: `check:fences` reports **0**, stated as an absolute number.
- **SC-008**: The chapter's prose is 2,000–4,000 words outside code fences, measured with
  `relay-tutorial/scripts/prose-words.mjs`, and carries at least one `TRAP` box.
- **SC-009**: The tutorial job in CI succeeds on the chapter's push.
- **SC-010**: The dependency count across every `package.json` in `relay-platform` is unchanged,
  **measured at the opening and again at the close** rather than asserted once. It is 29 at
  `part4-ch10`.

## Assumptions

- **THE ONE FLAGGED ASSUMPTION, FOR `research.md` TO SETTLE AGAINST ITSELF.** FR-MED-06 says a user
  token may attach media *"uploaded by the sending user"*, and chapter 4.10 stores `user_id` as
  NULL when an API key took the slot. A NULL is not *"another user's media"* — it is the tenant's.
  The strict reading refuses a user token attaching a tenant-uploaded object; the permissive
  reading allows it, on the grounds that the tenant's own backend uploading on a user's behalf is
  the normal shape of a server-side integration. This specification assumes the **strict** reading,
  because the clause's sentence is about who uploaded it and NULL is not the sending user — and it
  is flagged because the permissive reading is what a customer would probably expect, and the two
  differ in what the platform permits rather than in how it is built.
- **One code for all three refusals**, following the send path's own precedent: `messages.service.ts`
  already records that a ban's refusal *"is the same for a channel that exists, one that belongs to
  another tenant, and one that was invented."* Distinguishing them would leak existence across the
  tenant boundary.
- **`media_not_available` is deleted rather than re-pointed at "no such object"**, because the
  registry's note forbids repurposing and because the two sentences are not the same claim: one is
  about the platform's capability and the other about one caller's id.
- **The state check is built as the clause reads**, with its unreachable arms named in the code —
  chapter 4.10's precedent, where `RESUMES` carries an entry no caller reaches and says so.
- **Nothing is added to delivery.** FR-MED-07 is row 15, movement VI.
- **No new dependency.** The check is a read the repository already has a client for.
- **The chapter is prose plus one tag on `relay-platform`**, the shape every Part 4 chapter has
  taken: `part4-ch11`.

## Dependencies

- Chapter 4.10's `media_objects` table, slot route and storage quota — shipped, tagged
  `part4-ch10`.
- Chapter 3.24's discriminated union and `ZodValidationPipe`'s `protocolCode` mechanism — shipped.
- `gaps.md` 056-1 and 056-2 are open and this chapter inherits both: a slot nobody uploads to is
  indistinguishable from one that was uploaded, and the quota counts declarations rather than
  bytes. Neither blocks this chapter; both bound what its acceptance can claim.

# Feature Specification: chapter 4.10 — the upload that never reaches us

**Feature directory**: `specs/056-chapter-4-10` · **Created**: 2026-09-18
**Chapter**: Part 4, **movement V's first** — hosted media. `docs/12` §3 row 11.
**Ships as chapter 4.10.** Name it by its movement and title; the structure record keeps
pre-contraction ordinals in its first column, so its "row 11" is this chapter and its "row 10"
is the milestone that shipped as 4.9.

## Why this chapter exists

Hosted media reverses a founding exclusion (SRS Appendix B), and ADR-13 already decided how:
**bytes never transit Relay compute.** The api brokers access to storage it never touches, so a
client uploads straight to an object store and Relay holds only the record that it did.

This chapter builds the first half of that: **the slot**. A caller declares what it intends to
upload, the platform decides whether to allow it, and — if it does — hands back a URL that is
good for fifteen minutes and a `media_id` in state `pending`. Nothing is uploaded through us and
nothing is verified yet; FR-MED-03 and FR-MED-04 are later chapters' work.

## What the brief does not say, and it is most of the chapter

`docs/12` row 11 reads *"FR-MED-01/02: the slot, the presigned URL, the four distinct refusals,
the storage quota"*. Four premises were checked against the tree before this specification was
written. Three of them contradict the brief.

**THERE IS NO OBJECT STORAGE.** `compose.yaml` runs postgres, redis, nats, clickhouse, mailpit
and three services. No MinIO, no S3, nothing that can issue a presigned URL. The SAD names one —
*"MinIO standing in for object storage"* at `docs/05-sad.md:1002`, and ADR-13's diagram has it —
but **the decision exists and the container does not**. A presigned URL is issued by the store,
so this chapter provisions the store before it can issue anything. That is a new infrastructure
dependency and constitution VII governs it.

**THE STORAGE QUOTA CANNOT BE CONFIGURED, AND THE SCHEMA REFUSES IT ON PURPOSE.**
`quotaConfigSchema` is `.strict()` over exactly three dimensions — `messages`, `active_users`,
`connection_minutes` — and its own comment says why: *"a dimension nobody implemented is a parse
failure rather than a silently ignored cap."* A `storage_bytes` cap is a parse failure today, and
the same comment says a new key must land in the parser **and** in the migration's `CHECK`
together, because the constraint would otherwise accept a config the parser rejects and `capsFor`
fails closed — so the cap would silently become no cap.

**AND FR-RTL-05 DOES NOT NAME STORAGE.** FR-MED-02's third refusal leans on *"the environment's
storage quota"*, and FR-MED-12 says stored bytes are *"included in quota enforcement
(FR-RTL-05)"*. FR-RTL-05 reads: *"configurable monthly quotas on messages sent, unique active
persons, and connection-minutes."* Three quantities, and storage is not one of them. **Two
clauses cite a third that does not say what they need**, which this project's own rule — read the
clauses, not the identifiers — is about.

**THE FOURTH REFUSAL IS REAL AND IT IS IN THE SAD.** The brief says *"the four distinct
refusals"* and FR-MED-02 names three conditions — MIME outside the allowed set, declared size over
the per-kind cap, storage quota exceeded. The fourth is `docs/05-sad.md:1062`, the degradation
table: *"Object storage lost … **Upload slots return a specific error**"*.

**And it is the one a client most needs to tell apart.** The other three are permanent: transcode,
compress, or buy more storage. This one is transient, so it is the only refusal for which retrying
is the right advice — and a client that cannot distinguish it either retries three refusals that
will never succeed or gives up on one that would.

**What did hold**: chapter 3.24 shipped the discriminated union this chapter fills.
`attachmentSchema` carries a `{ type: "media" }` arm that refuses today with
`media_not_available`, and `codes.ts:204` says in as many words that *"§4.14 replaces the arm
rather than this code"*. The refusal was built to be replaced, and the replacement is FR-MED-06's
chapter, not this one — this one makes a `media_id` exist for that arm to accept.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tuan asks to send a photo (Priority: P1)

Tuan's client declares a filename, a MIME type and a byte size before it sends anything. The
platform answers with a URL his client can upload to directly and an id for the object that will
exist there. His phone never sends the bytes to Relay.

**Why this priority**: it is the clause's own first sentence and everything else in the chapter
is a refusal of it.

**Acceptance scenarios**

1. **Given** a valid user token and a declared `image/jpeg` of 2 MB, **When** the client requests
   a slot, **Then** it receives a `media_id` in state `pending` and an upload URL, and a record
   exists tying that id to the caller's environment and user.
2. **Given** that URL, **When** the client uploads the bytes directly to the object store,
   **Then** the upload succeeds without any request reaching the api.
3. **Given** the same URL sixteen minutes after it was issued, **When** the client uploads,
   **Then** the store refuses it, and the refusal comes from the store rather than from Relay.
4. **Given** a valid API key rather than a user token, **When** a slot is requested, **Then** it
   is issued and the record carries no user.

### User Story 2 - Three refusals a client can tell apart (Priority: P1)

A client that is refused needs to know which rule it broke, because the remedies are different:
transcode, compress, or contact the account owner.

**Why this priority**: *"each refusal shall use a distinct error code"* is the half of FR-MED-02
that makes the other half usable, and this platform has been caught before shipping one code for
two facts.

**Acceptance scenarios**

1. **Given** a declared MIME type outside the allowed set, **When** a slot is requested, **Then**
   it is refused with a code that names the MIME type as the reason, and no record is created.
2. **Given** an allowed MIME type whose declared size exceeds that kind's cap, **When** a slot is
   requested, **Then** it is refused with a **different** code that names the size and the cap.
3. **Given** an allowed type and size whose bytes would take the environment past its storage
   quota, **When** a slot is requested, **Then** it is refused with a **third** code that names
   the quota.
4. **Given** all three refusals, **When** their codes are compared, **Then** no two are equal and
   each appears in the published error reference.

### User Story 3 - David caps what a tenant may store (Priority: P2)

David sets a storage limit on an environment the way he sets the other three, and a tenant that
reaches it stops being able to start uploads.

**Why this priority**: the quota is the third refusal's precondition. Without it that refusal
cannot be reached, and a refusal that cannot be reached is a test that cannot fail.

**Acceptance scenarios**

1. **Given** an environment with no storage cap configured, **When** slots are requested,
   **Then** the quota refusal never fires and the absent cap stays absent rather than becoming
   zero or infinity.
2. **Given** a configured storage cap, **When** the declared size of a new slot would take the
   environment's committed bytes past it, **Then** the slot is refused.
3. **Given** a configuration naming a dimension the platform does not implement, **When** it is
   saved, **Then** it is refused at parse time rather than ignored.

### Edge Cases

- **A slot is issued and nothing is ever uploaded.** The record stays `pending` and the
  environment's committed bytes include a size no object will ever occupy. What reclaims it, and
  when, is named in this chapter even if the reclaiming is a later one's.
- **The declared size is a lie.** FR-MED-03 verifies the actual object and is not this chapter;
  the chapter states plainly that the quota arithmetic here is over *declarations*.
- **Two slots race the same remaining quota.** Both may be issued against one remaining
  allowance unless the commit is serialised.
- **The object store is down when a slot is requested.** This is the fourth refusal (FR-017), and
  it is the only transient one. A slot cannot be issued because the URL is signed against a store
  that is not answering — and the failure must not read as a quota or a bad MIME type.
- **A MIME type that is allowed but whose kind cannot be derived**, so no per-kind cap applies.
- **An upload URL is shared with someone else.** For fifteen minutes it is a bearer credential.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The platform MUST provide object storage in the local stack, reachable by the api
  and by a client, so that a presigned URL can be issued and used. ADR-13 decided the pattern;
  this provisions it.
- **FR-002**: A caller with a user token or an API key MUST be able to request an upload slot by
  declaring a filename, a MIME type and a byte size.
- **FR-003**: An issued slot MUST carry a `media_id` in state `pending` and an upload URL valid
  for **15 minutes**, and the expiry MUST be enforced by the store rather than by the api.
- **FR-004**: A media record MUST be scoped to the requesting environment, and to the requesting
  user when the caller is a user token.
- **FR-005**: A slot MUST be refused when the declared MIME type is outside the allowed set:
  `image/jpeg`, `image/png`, `image/gif`, `image/webp`; `audio/mpeg`, `audio/mp4`, `audio/ogg`,
  `audio/wav`; `video/mp4`, `video/webm`.
- **FR-006**: A slot MUST be refused when the declared size exceeds the cap for its kind —
  image 10 MB, audio 25 MB, video 100 MB.
- **FR-007**: A slot MUST be refused when issuing it would take the environment's committed
  storage past its configured cap.
- **FR-008**: The four refusals MUST use four distinct error codes, each documented in the
  published error reference, and each MUST say which rule was broken.
- **FR-009**: A refused request MUST create no media record and reserve no bytes.
- **FR-010**: The quota configuration MUST accept a storage dimension, and MUST continue to
  refuse an unimplemented dimension at parse time rather than ignoring it. The parser and the
  migration's constraint MUST agree, for the reason the existing comment gives.
- **FR-011**: FR-RTL-05 MUST be amended to name the storage dimension, or this chapter MUST
  record why it is not amended. Two clauses cite it for a quantity it does not define.
- **FR-012**: An absent storage cap MUST mean no cap and no alert, resolved the same way the
  three existing dimensions resolve an absent cap.
- **FR-013**: Bytes MUST NOT pass through Relay compute on the upload path (ADR-13, and
  NFR-SCL-01's memory budget is the measurable reason).
- **FR-014**: The chapter MUST state what the quota arithmetic is over — declared sizes, not
  verified ones — and what that permits until FR-MED-03 ships.
- **FR-015**: The chapter MUST record what happens to a slot nobody uploads to, and whether the
  bytes it committed are ever released.
- **FR-016**: The `{ type: "media" }` arm MUST continue to refuse with `media_not_available`.
  This chapter makes a `media_id` exist; FR-MED-06's chapter is what starts accepting one.
- **FR-017**: A slot MUST be refused with its own code when the object store cannot be reached,
  and that code MUST be distinguishable from the other three. It is the only transient refusal, so
  it is the only one whose message may tell a client to retry (`docs/05-sad.md:1062`).
- **FR-018**: Every status this chapter introduces MUST have a named code in the error filter's
  ladder, not only in its throwers. The ladder maps 400, 401, 403 and 404 and falls everything
  else through to `internal_error` — which is *"a lie the client cannot act on"* in the filter's
  own words about the 400 chapter 2.2 fixed and the 403 the credentials chapter fixed. Three or
  four new statuses without a ladder entry is three or four more of the same.

### Key Entities

- **Media object** — a row per requested slot: its environment, its user when there is one, the
  declared filename, MIME type and size, its state (`pending` here; `ready` and `rejected` are
  later chapters'), and where the object lives.
- **Upload slot** — not stored. A URL and an expiry, derived from the media object and the
  store's credentials at the moment of the request.
- **Storage commitment** — the environment's declared bytes, which the quota refusal compares
  against the cap. Whether this is a running column or a query over the media rows is the plan's.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A client can obtain a slot and upload a file to the object store without any byte
  of that file reaching the api — verified by the api's own request log showing the slot request
  and nothing else. **The suite spawns the ingester it needs**: the request log is written by
  `services/ingester`, which has no Dockerfile and no compose service, so those rows do not exist
  on a machine where nothing drains the stream. Chapter 4.9 closed `gaps.md` 050-8 by having the
  suite start the process; this criterion is measured the same way or it is measured against an
  empty table.
- **SC-002**: An upload URL is accepted before 15 minutes and refused after, measured against the
  store rather than asserted from the issuing code.
- **SC-003**: The four refusals return four distinct codes, and a test asserts the codes rather
  than the status — this platform has shipped a suite that passed while the body said
  `internal_error`. Distinctness is one assertion and correctness is four; a test that checks only
  distinctness passes when every code is wrong in the same way.
- **SC-004**: Every new code appears in the published error reference, and `check:errors` agrees
  in both directions.
- **SC-005**: A storage cap set on an environment changes whether a slot is issued, measured at
  the boundary: one byte under the cap succeeds and one byte over is refused.
- **SC-006**: A quota configuration naming an unimplemented dimension is refused at parse time,
  and the migration's constraint refuses the same input — checked from both sides, because the
  existing comment says a disagreement makes a cap silently become no cap.
- **SC-007**: The fence chain reports **0** and the delta is stated as an absolute number rather
  than a delta of zero.
- **SC-008**: The chapter's prose is **2,000–4,000 words outside code fences** (`docs/07:67`),
  measured with `relay-tutorial/scripts/prose-words.mjs` — chapter 4.9 came in at 2,826 — and the
  chapter carries **at least one `TRAP` box**, which `docs/07:70` makes a counted class with a
  per-chapter minimum. Its argument's cost is stated as prose or artifacts when the estimate is
  written. **The ten fence hunks do not count**: *"+ code is additive, not counted"*, which is
  what keeps a chapter publishing 1,100 lines of listing inside a 4,000-word bound.
- **SC-009**: The tutorial job in CI succeeds on the chapter's push.
- **SC-010**: Object storage joins the local stack as **one container**, and the **package count
  moves by zero** — measured across every `package.json` in `relay-platform`, which holds no S3
  client of any kind today. `docs/12` carries no dependency count; the "5 → 6" in this project's
  record is chapter 4.5's gateway package count, and a container is not a package.

## Assumptions

- **MinIO is the local object store**, because `docs/05-sad.md:1002` already names it and ADR-13
  already chose the pattern. The plan confirms it rather than re-deciding it.
- **The slot request is a REST route on the api**, following every other tenant-facing surface in
  the series (constitution V).
- **`media_id` is an opaque identifier**, not a path into the store, so the storage layout can
  change without breaking a published contract.
- **The state machine starts at `pending` and this chapter adds no other state.** `ready` and
  `rejected` arrive with the verification and scanning clauses.
- **The storage quota is a monthly cap like the other three**, because FR-RTL-05 says *"monthly
  quotas"* and FR-MED-12 puts storage under it. **This one is worth doubting**: stored bytes are
  a level and messages sent are a flow, and a monthly cap on a level is a different arithmetic
  from a monthly cap on a flow. The plan settles it and the chapter says which it chose.
- **The four-refusals figure in `docs/12` is right**, and analysis found the fourth: the SAD's
  degradation row. It is specified as FR-017 rather than added silently.

## Out of scope

- FR-MED-03's verification of the actual object, and FR-MED-04's virus scan and content probe.
- FR-MED-05's thumbnails and poster frames (P4).
- FR-MED-06's filling of the `{ type: "media" }` arm — chapter 4.11.
- FR-MED-07's `media.updated` event, FR-MED-08's signed delivery, FR-MED-09's rejection marker.
- FR-MED-10's unlinking and hard delete, FR-MED-11's retention, FR-MED-13's webhook types,
  FR-MED-14's SDK helpers.
- FR-MED-12's metering of stored bytes into the analytical store. This chapter needs the cap, not
  the meter.

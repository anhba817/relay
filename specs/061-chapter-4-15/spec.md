# Feature Specification: Chapter 4.15 — "What a thumbnail costs"

**Feature Branch**: `061-chapter-4-15`

**Created**: 2026-09-28

**Status**: Draft

**Input**: User description: "chapter 4.15"

Movement VI, third chapter. `docs/12` §3 row 16: *FR-MED-05: derived objects sharing the
parent's lifecycle.* No open question in §7 is addressed to it.

## What the premise check found

Run before this specification was written. Every recent chapter has had at least one artifact
that agreed with the other artifacts and not with the tree, and the pass that runs the premise
is the one that finds it.

| Claim the brief rests on | Measured | Consequence for scope |
|---|---|---|
| Something generates thumbnails | Across `services/` and `packages/`, word-bounded and with a control: `thumbnail` **2**, `poster` **0**, `derived_from` **0**, `parent_media` **0**. Both `thumbnail` hits are the **same sentence**, in migration `0018` and again in `schema.ts` — a forward reference to this chapter, copied | Nothing exists. Both halves of the clause are unbuilt, and the one comment that anticipates them is already duplicated. |
| The worker can write bytes to the store | `services/media-worker/src/store.ts` exports `headObject`, `bucketPresent`, `getRange`, `streamObject` — **four readers and no writer** | The producer seam has nothing behind it. 4.14's shape, in a different service. |
| The worker could decode an image | Its runtime dependencies are `@relay/protocol` and `@relay/service-kit` — **no third party at all**. `dimensions.ts` reads headers: PNG `IHDR`, GIF screen descriptor, WebP `VP8`, JPEG `SOF0`. It decodes no pixels. | Producing the bytes needs a capability the platform does not have, and acquiring it is the chapter's decision. |
| `media_objects` can express parenthood | No self-reference, no parent column, no column distinguishing an uploaded object from a made one | *"Sharing the parent's lifecycle"* has nothing to attach to. |
| A derived object would be readable | FR-MED-08 authorises through `channelsReferencingMediaIn` — the distinct channels of messages whose `attachments @> [{type:"media", media_id}]`. A thumbnail is named by no message. | **Readable by nobody**, which is FR-MED-08's own stated rule for an object with no referencing message. |
| A derived object would survive | FR-MED-10 hard-deletes unreferenced objects 24 hours after creation | **Destroyed a day after it is made.** `delivery.itest.ts:342` already wrote that sentence, about a different object. |
| The storage quota would ignore it | `coalesce(sum(declared_bytes), 0)` over `media_objects` where `environment_id = ?` and `state <> 'rejected'` — no other predicate | A derived row is charged the moment it exists, against a `declared_bytes` that the column's own comment defines as *"what the caller said"* and that nobody said. |
| A unit test could produce one | Run against `fixtures.ts` with a real decoder: `pngOf(800,600)` decodes and resizes to a 3,618 B thumbnail; **`gifOf(800,600)` decodes and resizes to 198 B**; `jpegOf` fails `Invalid JPEG file` and `webpOf` fails `unable to parse image`, both being headers with no image data | **Two of the four allowed image formats have decodable fixtures.** The first draft of this row said one, from reading the fixture source rather than decoding its output — 4.13's *"every fixture is a header this repository wrote"* is true of two of them, not four. |

**THE CLAUSE'S LAST FIVE WORDS ARE THE CLAUSE.** *"Stored as derived objects sharing the
parent's lifecycle"* reads like a storage note and it is the only part of FR-MED-05 that is
hard. Two clauses already shipped destroy an unreferenced object: FR-MED-08 refuses to serve
it and FR-MED-10 deletes it. A thumbnail is unreferenced by construction — no message names
it, because the message names the parent. So the derived object is not a file that needs a
home; it is **an object the platform must agree to treat as part of another one**, at three
separate doors, and the schema cannot currently say that two rows are related at all.

**AND THE TWO HALVES FAIL FOR DIFFERENT REASONS, WHICH IS WHY THEY ARE SEPARATE STORIES.**
Lifecycle is a question about rows and predicates and can be settled with no image decoder in
the repository: plant a derived row by hand, delete the parent, and read what happened.
Generating the bytes is a question about what this platform is allowed to depend on. The first
is testable today; the second may not be answerable in TypeScript at all.

**THE BYTES CANNOT BE MADE IN TYPESCRIPT, AND ADR-32's LINE DOES NOT OBVIOUSLY REACH THE
ALTERNATIVE.** ADR-32 settled that ClamAV does not engage constitution VII, and its argument is
specific: Relay addresses five programs it is not written in, *"each reached over a socket with
a documented protocol"*. The programs that resize images — ImageMagick, `ffmpeg` — are normally
**subprocesses given argv and a file path**, which is a different relationship from a socket
with a protocol, and the difference is exactly what an ADR has to rule on rather than assume.
The third option is a native Node dependency, which lands in a worker that has **zero**
third-party runtime dependencies today and would be the first native build in the workspace.
This chapter chooses among the three **against a measurement**, which is what the title asks
for.

**THE VIDEO HALF IS STRICTLY HARDER THAN THE ONE 4.13 ALREADY DECLINED.** FR-MED-04 is recorded
PARTLY MET because duration needs four container parsers and MP3 VBR has no header answer. A
poster frame needs a **decoder**, not a container parser: the first keyframe of an MP4 is
H.264, and no amount of byte-walking produces a pixel. If the image half is declined, the video
half is declined a fortiori; if the image half ships, the video half is a separate decision with
its own evidence. The precedent for recording it — SRS 1.18, 1.20 and 1.21 — is *unmet by
decision, and not by oversight, with the reason written down.*

## Vocabulary

Three words for two things, counted across these artifacts before they were fixed: `spec.md`
said *derived object* 36 times and *rendition* 12; `tasks.md` inverted it at 28 and 2. One term
per concept from here on:

- **rendition** — the row and the object. What the platform made from another object.
- **thumbnail** — the one *kind* of rendition this chapter ships. `poster` would be a second.
- **parent** — the uploaded object a rendition was made from.

*Derived object* is FR-MED-05's own phrase and stays where the clause is quoted. Everywhere
else the word is **rendition**, because the clause's phrase names a category and the platform
needs a name for a row.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A derived object belongs to its parent (Priority: P1)

The platform can hold an object that exists because of another object, and the three doors that
act on media agree about it: it is not served on its own, it is not reaped for being
unreferenced, and it goes when its parent goes.

**Why this priority**: it is the only part of FR-MED-05 the clause actually spells out, it is
what the other two stories stand on, and it is testable with no image decoder anywhere in the
repository. If the chapter shipped nothing else, the platform would be able to state what a
derived object is and prove that it survives and dies correctly.

**Independent Test**: plant a derived row against a parent by hand, then exercise each door —
the reaper, the delivery gate, and parent deletion — and assert the outcome for the derived row
and the parent separately.

**Acceptance Scenarios**:

1. **Given** a `ready` parent referenced by a message and a derived object of that parent,
   **When** the unreferenced-object reaper runs past the 24-hour boundary, **Then** the derived
   object survives and the reaper's own count does not include it.
2. **Given** a derived object whose parent is referenced by no message, **When** the reaper
   runs past the boundary, **Then** both are deleted, and the derived object is deleted no later
   than its parent.
3. **Given** a parent deleted for any reason — unlinked and reaped, rejected by the worker, or
   erased — **When** the deletion completes, **Then** no derived object of that parent remains
   in the database or in the store.
4. **Given** a caller not authorised to read any message referencing the parent, **When** it
   requests the derived object directly by id, **Then** it is refused, and the refusal is
   byte-identical to the one for an id no object has.
5. **Given** a derived object, **When** it is requested as if it were an upload slot's object or
   attached to a message, **Then** it is refused: a derived object is not attachable.

---

### User Story 2 - An image gets a thumbnail (Priority: P2)

An image that passes verification gains a smaller rendition, made by the platform, stored beside
it, and recorded with the dimensions it actually has.

**Why this priority**: it is the clause's headline and it is the half that costs a dependency
decision. It is second because it cannot be correct without US1 — a thumbnail that no door
recognises as derived is bytes the platform will delete tomorrow and refuse to serve today.

**Independent Test**: upload a real image, let the worker verify it, and assert that a derived
object exists in the store with the expected kind and bounded dimensions, recorded against the
parent.

**Acceptance Scenarios**:

1. **Given** an uploaded image of an allowed type that passes the scan and the declaration
   check, **When** the worker finishes processing it, **Then** exactly one derived thumbnail
   exists for it, and the parent's own bytes are unchanged.
2. **Given** an image already smaller than the thumbnail bound in both dimensions, **When** it
   is processed, **Then** the recorded outcome is one of the alternatives named before
   implementation begins — no rendition, or a rendition that is a copy — and repeated
   processing of the same image yields that same outcome every time.
3. **Given** an object that is rejected by the scan or the declaration check, **When**
   processing finishes, **Then** no derived object was made and no bytes beyond the parent were
   written.
4. **Given** thumbnail generation fails for an object the verification passed, **When**
   processing finishes, **Then** the parent still reaches `ready`, and the failure is recorded
   rather than retried for ever.
5. **Given** an allowed image type for which this platform cannot produce a thumbnail, **When**
   it is processed, **Then** the parent reaches `ready` with no derived object and the reason is
   a recorded value rather than an absence.

---

### User Story 3 - A client can show the small one (Priority: P3)

A client rendering a message with an image attachment can fetch the thumbnail under the same
authorisation as the full object, without asking for the full object first.

**Why this priority**: it is what a thumbnail is *for*, and it is third because it is the only
one of the three that changes a published contract. A thumbnail nobody can address is an
internal storage detail; this is the story that makes it a feature.

**Independent Test**: as a member of a channel carrying an image message, request the
attachment's thumbnail and receive bytes; as a non-member, receive the same refusal the parent
gives.

**Acceptance Scenarios**:

1. **Given** a delivered message with an image attachment that has a thumbnail, **When** a
   client authorised to read the channel requests the thumbnail, **Then** it receives it under
   the same validity bound as the parent's delivery URL.
2. **Given** the same message, **When** a client not authorised to read any referencing channel
   requests the thumbnail, **Then** it is refused identically to a request for the parent.
3. **Given** a message whose attachment has no thumbnail — audio, or an image that produced
   none — **When** it is delivered, **Then** the payload says so explicitly rather than
   offering an address that answers 404.
4. **Given** an attachment in `pending`, **When** it is delivered, **Then** no thumbnail is
   offered, because none exists yet, and 4.14's `media.updated` is what tells the client to look
   again.

---

### Edge Cases

- A parent referenced by messages in several channels: the derived object follows the parent's
  authorisation, which is a disjunction over all of them, not a single channel.
- Two messages attach the same parent and one is deleted: the parent survives, so the derived
  object must too. Lifecycle follows the parent, never a message.
- The derived object is deleted from the store by something outside the platform: the delivery
  door must refuse rather than hand out an address to bytes that are gone.
- A parent is rejected *after* its thumbnail was made — possible only if the ordering permits
  it, which US2 scenario 3 forbids by construction. If the ordering cannot forbid it, the
  cleanup path must.
- An image whose pixel dimensions are within bounds but whose byte size is not, and the reverse:
  the thumbnail bound is a claim about one of them and the specification must say which.
- The same parent processed twice — a duplicate verdict, a retried sweep — must not produce two
  derived objects or two sets of bytes.
- Erasure (FR-MED-10's second sentence, FR-MOD-04) names derived objects explicitly; whatever
  US1 builds has to be reachable from that path, whose chapter is 4.22.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The platform MUST be able to record that one media object exists because of
  another, such that the relationship is queryable in both directions and cannot name an object
  in another environment.
- **FR-002**: A rendition MUST NOT be treated as unreferenced by the job that hard-deletes
  unreferenced objects. Its reachability is its parent's.
- **FR-003**: Deleting a media object MUST delete its renditions, in the database and in the
  store, with no path that deletes one and leaves the other.
- **FR-004**: A rendition MUST NOT be attachable to a message, and MUST NOT be returned by any
  door that lists or serves a tenant's own uploads as if it were one.
- **FR-005**: Authorisation to read a rendition MUST be exactly the authorisation to read its
  parent, evaluated by the same predicate rather than a second copy of it. A refusal MUST be
  indistinguishable from the refusal for an id no object has.
- **FR-006**: The platform MUST generate a reduced rendition for uploaded images of the allowed
  types it can decode, during processing, and store it as a derived object of the uploaded one.
- **FR-007**: The set of types for which a rendition is produced MUST be derived from the
  platform's own capability rather than restated as a hand-written list, and an allowed type
  that produces no rendition MUST be recorded as a value, not as an absence.
- **FR-008**: Generating a rendition MUST NOT be able to prevent an object that passed
  verification from reaching `ready`, and MUST NOT retry indefinitely.
- **FR-009**: Rejected objects MUST produce no rendition, and MUST leave no rendition bytes in
  the store.
- **FR-010**: Processing the same object more than once MUST leave exactly one rendition of each
  kind it defines.
- **FR-011**: Delivery MUST offer a client the address of an attachment's rendition where one
  exists, and MUST state its absence explicitly where one does not.
- **FR-012**: The bytes held by renditions MUST be accounted in the environment's stored
  total, on the same basis as uploaded bytes, and the specification MUST state what happens when
  a rendition would carry the total past the quota — since no request exists to refuse at that
  moment.
- **FR-013**: The video half of FR-MED-05 MUST be ruled on explicitly — built, or recorded as
  unmet by decision with the reason and the reversal condition written into the SRS.
- **FR-014**: The means of producing the bytes MUST be chosen in an ADR that states the drivers,
  the rejected alternatives and the reversal condition, and that answers whether constitution
  VII's one-language clause is engaged.
- **FR-015**: The chapter MUST publish what a thumbnail costs, as measured numbers rather than
  adjectives: bytes against the parent, time to produce one, and the effect on the stored total
  a tenant is charged for.

### Key Entities

- **Derived object**: a media object the platform made from another, with a kind saying what it
  is, a parent it belongs to, and no independent lifecycle. It has bytes in the store and a row
  in the operational database, like an uploaded object, and differs in every respect that
  governs who may read it and when it dies.
- **Parent object**: an uploaded media object, unchanged by this feature except that deleting it
  now has a consequence and its delivered form may carry an address for a rendition.
- **Rendition kind**: what a derived object is — the thumbnail of an image, and, if the ruling
  goes that way, the poster frame of a video. A closed set, because every door that treats
  derived objects differently must be able to enumerate them.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A derived object survives the unreferenced-object reaper for as long as its parent
  does, demonstrated at the 24-hour boundary from both sides — one run before it and one after,
  with the parent referenced and unreferenced.
- **SC-002**: The cascade is exercised by a direct deletion, with the rendition shown gone from
  **both** the database and the store. Separately, the code paths that delete a media object are
  enumerated from the source rather than listed by hand, and **the enumeration asserts the number
  it found** — which is currently zero, because nothing in the platform deletes a row. A
  criterion of the form *"a test for every path"* over an empty set passes by doing nothing, so
  the count is the part that has to be right.
- **SC-003**: A caller unauthorised for the parent receives byte-identical refusals for the
  parent and for the derived object, differing only in the request identifier.
- **SC-004**: Every arm of the derived-object predicate is probed by deletion: each arm is
  removed individually, both suites are re-run, and each arm is recorded as **tested** or as
  **unnecessary** by name. An arm whose removal turns nothing red is not left unexplained.
- **SC-005**: An uploaded image of each decodable allowed type produces exactly one thumbnail,
  within the stated bound, verified by reading the stored bytes back rather than by trusting the
  row.
- **SC-006**: A rejected object and a failed rendition each leave zero derived bytes in the
  store, verified by listing the store rather than by querying the database.
- **SC-007**: Processing one object twice produces one derived object, asserted after a
  deliberate duplicate.
- **SC-008**: The cost is published as three measurements with their method: thumbnail bytes as
  a fraction of parent bytes over a real sample, wall-clock time to produce one at p50, and the
  change in an environment's stored total. Each is measured, not estimated.
- **SC-009**: The dependency decision is published with the option that was not taken and the
  reason, and the workspace's runtime dependency count is stated before and after.
- **SC-010**: The video half is ruled on in a document, not in a silence: either a poster frame
  is produced for an uploaded video and verified by reading the bytes back, or the SRS carries
  the clause marked unmet by decision with its reason and its reversal condition, and the
  wording is checked against FR-MED-04's own precedent.
- **SC-011**: `pnpm check:fences` reports 0 at the close, and the CI error set is compared per
  error against the pre-chapter baseline, in both directions.
- **SC-012**: The chapter's prose is within the 2,000–4,000 word bound with at least one `TRAP`
  box, and every published fence replays onto `relay-platform`.

## Assumptions

- Row 16 of `docs/12` §3 is chapter 4.15; §3 keeps pre-contraction ordinals in column one, so
  row N is chapter 4.(N−1). This is the convention `CLAUDE.md` records and 4.14 relied on.
- The thumbnail's bound is a pixel bound rather than a byte bound, because the clause says
  "thumbnail" and the consumer is a layout. The exact number is a planning decision and belongs
  in `research.md` with a measurement behind it.
- FR-MED-10's reaper does not exist yet — the sweep built in 4.13 walks `pending` uploads, which
  is a different job. So FR-002 is a constraint this chapter writes down and proves against a
  stand-in, and the chapter that builds the reaper (4.21 or 4.22 by movement, not by number)
  inherits it. Which of the two owns it is settled in planning, not here.
- Derived bytes count toward the stored total. The alternative — a tenant's thumbnails being
  free — is a discount with no clause behind it, which is the argument SRS 1.17 already made
  about tolerance in FR-MED-03.
- No real image exists in the repository to measure against. Producing a sample corpus is part
  of the work, and the sample's provenance is stated wherever a figure derived from it is
  published.
- The chapter ships English prose only; the Vietnamese edition lags and is the user's own pass.

## Open questions carried into planning

1. **Which of the three ways of producing bytes.** A native dependency in the worker, a
   subprocess, or a program addressed over a socket. ADR-32 settled the socket case and said
   nothing about the other two. The answer needs a measurement of each against the same sample,
   and it is FR-014's ADR.
2. **Whether the video half ships at all**, and if not, under which precedent it is recorded.
   FR-013 forces the ruling; it does not presuppose it.
3. **Where the reaper's exclusion lives** while the reaper does not exist. A constraint proven
   against a stand-in is weaker than one proven against the job, and the difference should be
   stated rather than blurred.
4. **Whether a derived object needs a state at all.** Its parent has one; a derived object is
   made only from a `ready` parent and is either there or not. A second state machine that can
   only ever hold one value is the kind of thing 4.13 argued out of migration `0018`.

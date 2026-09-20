# Feature Specification: Chapter 4.13 — the only service that reads the bytes

**Feature branch**: `059-chapter-4-13`
**Created**: 2026-09-20
**Status**: Draft
**Input**: chapter 4.13 — `docs/12` §3 row 14, movement VI

> **Named by its movement and title, not its number.** `docs/12` §3 keeps pre-contraction
> ordinals, so its **row 14** is the chapter that ships as 4.13, exactly as row 13 shipped as
> 4.12 and row 12 as 4.11. **Movement VI opens here.**

---

## The brief, and the event that has no producer

`docs/12` §3 row 14: *"The only service that reads the bytes — the media worker. FR-MED-03/04:
verify against declaration, ClamAV, probe. **Open — see §7.3**."*

FR-MED-03, verbatim: *"The system shall verify actual object size and content type after
upload; objects that contradict their declaration shall be `rejected` and deleted."*

FR-MED-04, verbatim: *"Every uploaded object shall be virus-scanned and content-probed
(dimensions for images; duration for audio/video) asynchronously before transitioning
`pending → ready`. Objects failing the scan shall transition to `rejected` and be deleted,
retaining only the audit record."*

The SAD describes the service in one paragraph (`docs/05-sad.md:199`): *"Consumes
`media.uploaded` events. Fetches the object, verifies size/type against the declaration
(FR-MED-03), virus-scans (ClamAV sidecar), probes dimensions/duration … The only Relay
component that ever reads media bytes."*

**NOTHING PUBLISHES `media.uploaded`, AND THE ARCHITECTURE IS WHY.** Occurrences of
`media.uploaded` across `services/`, `packages/`, `analytics/` and `compose.yaml`: **zero**.
That is not an omission somebody can close with a producer, because ADR-13 put the bytes on a
path Relay is not on. Chapter 4.10 measured the consequence and published it: *"a presigned URL
needs no contact with the store … signing is arithmetic; the api never opens a socket."* The
client PUTs straight to the store. **The only two parties that know the upload finished are the
client and the store**, and neither of them is a Relay service today.

So the chapter's first problem is not *how do we scan* — it is *how does anything learn there
is something to scan*. The specification takes a position on that in Assumptions; it is the one
thing here most likely to be settled against this document.

**AND MOST SLOTS NEVER BECOME OBJECTS.** Measured on the lane before this specification was
written:

    media_objects rows                3,005        every one of them `pending`
    objects in the store                253        8.4%
    slots issued and never uploaded   2,752        91.6%
    rows older than 24 hours          1,538

Those rows are mostly fixtures that ask for a slot and never PUT, so the production ratio will
differ — the figure that survives is the **shape**: a mechanism that sweeps `pending` rows and
asks the store about each one spends most of its work on objects that hold nothing, and a
mechanism that waits to be told spends none.

**AND THE SCHEMA REFUSES EVERY STATE THIS CHAPTER NEEDS.**
`check("media_objects_state_check", sql`${t.state} = 'pending'`)` — one value, written that way
on purpose. Chapter 4.10's comment says why: *"`ready` and `rejected` arrive with the
verification and scanning clauses; a CHECK that accepted them now would be a schema claiming a
state nothing can reach."* This is that chapter. FR-MED-07 was recorded **unmet by decision** at
SRS 1.18 because no attachment had a state; this chapter delivers the first that do.

**AND A SHIPPED ROUTE ALREADY CONTRADICTS AN ACCEPTED ADR.** ADR-14: *"The scan gates byte
delivery (**no signed URL until `ready`**), never message delivery."* Chapter 4.12 shipped
`GET /v1/media/:mediaId` and it signs for a `pending` object — deliberately, and written down:
*"an object is `pending` until movement VI, and a URL for one whose upload never happened is
well-formed."* Every object in the platform is `pending`, so gating on `ready` in 4.12 would
have refused everything. **The conflict is real and it is this chapter's**: either delivery
starts gating, or ADR-14 is amended to say what the platform does.

**AND §7.3 IS THIS CHAPTER'S OPEN QUESTION, WHICH IS ABOUT THE CONSTITUTION.** Constitution VII:
*"One language (TypeScript/Node.js) across services, SDK, and dashboard … Introducing a second
language requires a superseding ADR with profiling evidence."* ClamAV is C and ffprobe is C.
`docs/12` §7.3 states the question rather than answering it: *"VII's subject is the language
services are* implemented in*; a sidecar the worker talks to is arguably not that. Argue it
explicitly rather than by silence, the way the PL/pgSQL guard was argued."*

**And there is a second constitutional question nobody has written down**: VII also says *"new
services require justification against the 'deliberately not a separate service' table (SAD
§4.2)."* This chapter adds the platform's fifth service. The SAD already argues for it — *"the
one service where ADR-01's worker-thread posture matters from day one"* — and the argument has
to be made against that table rather than cited.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An uploaded image becomes readable (Priority: P1)

A customer's client takes an upload slot, PUTs a JPEG, and sends a message referencing it.
Something notices the bytes have arrived, reads them once, confirms they are a JPEG of the size
declared, finds no virus, records the dimensions, and moves the object from `pending` to
`ready`.

**Why this priority**: it is the clause's whole subject. Everything else in this chapter is a
way for this path to refuse.

**Independent test**: upload a real JPEG through the published slot route, wait for the object
to reach `ready`, and read back the recorded width and height. Measured from outside the
worker, so a test that inspects the worker's internals proves nothing about the pipeline.

**Acceptance scenarios**:

1. **Given** a slot issued for `image/jpeg` at *n* bytes and a PUT of exactly those bytes,
   **When** the worker processes the object, **Then** the object's state becomes `ready` and its
   recorded dimensions match the image.
2. **Given** the same object, **When** the state is read again, **Then** it is still `ready` and
   the worker has not read the bytes a second time.
3. **Given** an audio or video object, **When** the worker processes it, **Then** a duration is
   recorded rather than dimensions.

### User Story 2 - An object that contradicts its declaration is rejected (Priority: P2)

A client declares `image/png` at 1,024 bytes and uploads a 4 MB MP4. FR-MED-03: the object is
`rejected` and deleted.

**Why this priority**: it is the half of the brief that needs no scanner, and it is the half a
malicious client reaches first — the declaration is the only thing the upload route could check,
and it checked a claim rather than a fact.

**Independent test**: take a slot for one type and size, upload something else, and assert the
object reaches `rejected`, that the bytes are gone from the store, and that the record of what
happened survives.

**Acceptance scenarios**:

1. **Given** a slot declaring `image/png`, **When** the uploaded bytes are not a PNG, **Then**
   the object is `rejected` and the stored bytes are deleted.
2. **Given** a slot declaring 1,024 bytes, **When** the uploaded object is any other size,
   **Then** the object is `rejected` and the stored bytes are deleted. **The comparison is exact**
   — the quota sums declarations, so any tolerance is storage a client is not billed for.
3. **Given** a rejected object, **When** the record is read afterwards, **Then** it says the
   object was rejected and why, and the quota no longer counts its bytes.

### User Story 3 - An infected object is rejected, and the record survives it (Priority: P3)

A client uploads a file carrying a known virus signature. FR-MED-04: the object is `rejected`
and deleted, *"retaining only the audit record."*

**Why this priority**: it is the clause's own named risk (SAD R9, *"hosted media liability
surface"*), and it is the one path that cannot be exercised without the scanner actually
running. A test that asserts the scan happened by mocking the scanner asserts nothing.

**Independent test**: upload the EICAR test signature — the standard, harmless string every
scanner is required to detect — and assert `rejected`, deleted bytes, and a surviving record.

**Acceptance scenarios**:

1. **Given** an object whose bytes carry the EICAR signature, **When** the worker scans it,
   **Then** the object is `rejected` and the bytes are deleted.
2. **Given** that rejection, **When** the record is read, **Then** it distinguishes *rejected by
   scan* from *rejected by declaration* — they are different facts about the customer.
3. **Given** the scanner is unreachable, **When** the worker processes an object, **Then** the
   object stays `pending` and is retried, rather than being marked `ready` or `rejected`.

### Edge Cases

- **A slot that is never uploaded to.** 91.6% of the lane's rows. The worker must not treat
  "no bytes" as "rejected" — FR-MED-10 reaps unreferenced objects after 24 hours and that is a
  different mechanism with a different clause.
- **The same object processed twice.** Whatever notices the upload can notice it more than once.
  Verification must be idempotent, and a second pass over a `ready` object must not re-read the
  bytes or re-run the scanner.
- **An object that arrives while the worker is down.** The notice has to survive, or the object
  has to be findable afterwards. A mechanism that only works while the worker is running
  silently leaves objects `pending` forever.
- **A message that already references a `pending` object that then gets rejected.** ADR-14 says
  the recipient sees a placeholder that becomes a rejection marker. FR-MED-09's marker is
  movement VI's later chapter; what this one must not do is leave the reference dangling with no
  record of why.
- **An object whose bytes are larger than the worker's memory.** The worker reads bytes for the
  first time in this platform's history, and the size cap is per kind — the largest allowed
  today is the number `KIND_CAPS` holds, not a number this chapter chooses.
- **The scanner's own definitions are stale.** A scanner that has never updated reports clean on
  everything. Its readiness is a different question from its reachability.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Something MUST detect that an object's bytes have arrived, and the mechanism MUST
  survive the worker being down. The chapter MUST publish which mechanism was chosen, what the
  rejected alternatives cost, and what the chosen one cannot do.
- **FR-002**: The worker MUST verify the object's actual size and content type against the
  declaration recorded when the slot was issued (FR-MED-03). **The size comes from the store's
  own count and the type comes from the bytes** — measured at analysis pass 1, the store echoes
  back whatever `Content-Type` the client uploaded with, so reading it verifies the declaration
  against itself.
- **FR-003**: An object contradicting its declaration MUST become `rejected`, and its bytes MUST
  be deleted from the store.
- **FR-004**: Every object MUST be virus-scanned before it can become `ready` (FR-MED-04). An
  object that fails the scan MUST become `rejected` and its bytes MUST be deleted. **The scan
  MUST run before the declaration check**, because *"every uploaded object"* excludes nothing
  and a declaration-first worker never scans the objects that lie — which are the ones worth
  scanning. Where both fail, `scan_failed` is the recorded reason.
- **FR-005**: A rejection MUST retain a record of what happened, and that record MUST
  distinguish a declaration mismatch from a scan failure.
- **FR-006**: Images MUST have dimensions recorded and audio/video MUST have a duration recorded
  (FR-MED-04).
- **FR-007**: The object MUST reach `ready` only after verification, scan and probe have all
  succeeded. No partial success may produce `ready`.
- **FR-008**: Processing MUST be idempotent. An object processed twice MUST end in the same
  state, and the second pass MUST NOT re-read the bytes — **both halves tested**, because the
  second was the one requirement of twenty-six that a mechanical coverage sweep correctly
  flagged as having no task.
- **FR-009**: A transient failure — the store unreachable, the scanner unreachable — MUST leave
  the object `pending` and retryable, and MUST NOT produce either terminal state.
- **FR-010**: The schema MUST accept `pending`, `ready` and `rejected`, and MUST NOT accept a
  state no code can produce.
- **FR-011**: The worker MUST NOT write to Postgres directly (ADR-04). Whatever it uses to
  record a transition MUST be a surface the chapter names.
- **FR-012**: The chapter MUST decide, in writing, whether `GET /v1/media/:mediaId` now refuses
  an object that is not `ready`. ADR-14 says *"no signed URL until `ready`"* and chapter 4.12
  ships the opposite. Either the route gates or the ADR is amended; the chapter MUST NOT leave
  them disagreeing.
- **FR-013**: The chapter MUST argue constitution VII explicitly for both questions it raises —
  the non-TypeScript scanner and probe (`docs/12` §7.3), and the fifth service against SAD
  §4.2's *"deliberately not a separate service"* table. Silence is what §7.3 forbids.
- **FR-014**: The chapter MUST state what the scan does not cover. A scanner detects known
  signatures; *"scanner misses"* is a named risk (SAD R9) and a chapter that implies otherwise
  is worse than one with no scanner.
- **FR-015**: Storage accounting MUST reflect a deletion. A rejected object's bytes stop
  existing, and the tenant's committed bytes are a sum over the media rows (SRS 1.17).

### Key Entities

- **Media object** — `media_objects`, unchanged since chapter 4.10 except for the states it may
  hold and whatever the probe records. Its `state` is the thing this chapter makes mean
  something.
- **The upload notice** — whatever carries *"object X has bytes now"* from wherever that is
  known to the worker. It does not exist yet and FR-001 is about choosing it.
- **The verdict** — verified, rejected-by-declaration, rejected-by-scan, or retry. Four
  outcomes, two of them terminal.
- **The media worker** — the platform's fifth service, and the first Relay component to read
  bytes a customer uploaded.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A real image uploaded through the published slot route reaches `ready` with
  correct dimensions, measured end to end from outside the worker.
- **SC-002**: An object whose bytes contradict its declaration reaches `rejected` and the bytes
  are gone from the store — both halves asserted, because a state change that leaves the bytes
  is the failure this clause exists to prevent.
- **SC-003**: The EICAR signature is rejected by a scanner that is actually running. Asserted
  against the real scanner, not a stub.
- **SC-004**: A scanner that is unreachable leaves the object `pending`, demonstrated by taking
  the scanner away and putting it back.
- **SC-005**: The same object processed twice ends in one state and the bytes are read once.
- **SC-006**: Time from upload to `ready` is measured and published for a representative object,
  with the scan's share of it stated separately. **The start instant is the store's
  `last-modified`, at one-second resolution** — the platform does not observe the upload, and the
  quantisation is published beside the figure rather than rounded away.
- **SC-007**: The chapter's prose is 2,000–4,000 words outside code fences and carries at least
  one `TRAP` box.
- **SC-008**: `check:fences` reports 0, stated as an absolute number.
- **SC-009**: The tutorial job in CI succeeds on the chapter's push.
- **SC-010**: The dependency count across every `package.json` in `relay-platform` is published
  before and after. It is **29** at `part4-ch12`, and this chapter is expected to move it —
  which makes it a figure to explain rather than a figure to hold.
- **SC-011**: `docs/12` §7.3 is closed in writing by the chapter that owns it, and the closure
  is recorded in both the table and §7 — §7.1 was closed by a chapter that did not own it and
  the entry stayed open for two features.

---

## Assumptions

**The flagged one, and it is the chapter's largest.** This specification assumes **the client
tells the platform it has finished uploading**, through a published route, and the platform
publishes `media.uploaded` from there. That is the reading the SAD's paragraph implies — it
names a consumer and an event and leaves the producer unwritten — and it is the cheapest thing
to build: one route, one publish, no vendor configuration, no sweep.

**It is also the reading most likely to be wrong**, and the argument against it is in the
clause: FR-MED-04 says *"every uploaded object shall be virus-scanned"*. A client-driven notice
makes the scan contingent on a client choosing to send it. A client that uploads and stays
silent leaves bytes in the store, unscanned and billed, until FR-MED-10 reaps them 24 hours
later — and *"scanner misses"* is R9's named risk, which an unscanned object does not even
reach. The alternatives are the store telling us (bucket notifications, which is vendor
configuration at the moment ADR-30 chose to keep the store replaceable) and the platform asking
(a sweep over `pending` rows, which the 91.6% figure above prices). `research.md` settles it,
and the specification is left as written rather than edited back — the flag exists to record
what was believed before the work. Three features running have settled a flagged assumption
against the specification.

**The scanner is ClamAV and the probe is ffprobe**, because the SAD names both. That is closer
to implementation than a specification likes, and it stays because §7.3's question is *about
those two programs* — the constitutional argument cannot be made about an unnamed scanner.

**The state machine's transitions belong here and its event does not.** `docs/12` row 15 is
*"Pending, ready, rejected — the state machine and `media.updated`"*, so the boundary is: this
chapter produces the transitions FR-MED-03/04 name, and the next one publishes them to clients
and renders FR-MED-09's marker. A chapter that produced a verdict and could not record it would
be describing a state machine rather than building one.

**The worker reads the bytes once.** Verification, scan and probe are three questions about the
same object, and this platform's rule about round trips (4.10's `storeReachable`, measured at
+24.1%) says a reader that fetches three times should say why.

**Thumbnails are not this chapter's.** FR-MED-05 is `docs/12` row 16 and P4 in the SRS.

---

## Dependencies

- **Chapter 4.10** issued the slot, created `media_objects`, and made `state` a column with one
  legal value. It also established that the api never contacts the store on the signing path,
  which is why FR-001 is a question at all.
- **Chapter 4.11** made the media arm attachable, so an object can be referenced before it is
  verified — which is ADR-14's whole design.
- **Chapter 4.12** ships the delivery route that FR-012 must reconcile with ADR-14, and the GIN
  index that makes *"which messages reference this object"* answerable.
- **ADR-04** keeps workers off Postgres. **ADR-13** keeps bytes off Relay compute. **ADR-14**
  gates bytes and not messages. **ADR-30** chose to sign with `node:crypto` rather than adopt a
  vendor client, which is the precedent any store-side notification mechanism argues against.
- **Constitution VII** is the chapter's own subject twice over, and `docs/12` §7.3 is the entry
  it must close.

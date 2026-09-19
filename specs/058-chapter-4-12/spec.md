# Feature Specification: Chapter 4.12 — a link that expires, and who may hold it

**Feature branch**: `058-chapter-4-12`
**Created**: 2026-09-19
**Status**: Draft
**Input**: chapter 4.12 — `docs/12` §3 row 13, movement V

> **Named by its movement and title, not its number.** `docs/12` §3 keeps pre-contraction
> ordinals, so its **row 13** is the chapter that ships as 4.12, exactly as row 12 shipped as
> 4.11 and row 11 as 4.10.

---

## The brief, and the thing it needs that nothing has

`docs/12` §3 row 13: *"A link that expires, and who may hold it — FR-MED-08: signed delivery,
one hour, authorisation following channel membership rather than a parallel ACL."*

FR-MED-08, verbatim: *"Media objects shall be readable only via signed delivery URLs with a
validity of 1 hour, issued only to callers authorised to read the referencing message (channel
membership or API key). Object storage shall not be publicly readable."*

**HALF OF IT IS ALREADY TRUE AND WAS PROVEN TWO CHAPTERS AGO.** *"Object storage shall not be
publicly readable"* is `presign.itest.ts:53`, whose title names this clause:
*"refuses an unsigned GET of that object — FR-MED-08's precondition"*. 4.10 measured it from
outside the container: signed GET 200, unsigned GET **403**, tampered **403**. Nothing in this
chapter has to build that, and the chapter should say so rather than re-prove it.

**AND THE OTHER HALF NEEDS A LOOKUP NOTHING IN THIS PLATFORM CAN DO.** *"Issued only to callers
authorised to read the referencing message"* means: given a `media_id`, find a message that
references it, and check the caller against that message's channel. Chapter 4.11 created the
first references there have ever been — and filed, as `gaps.md` 057-1, that **nothing counts
them**. `grep -rn media_id` across `services/`, `scripts/` and `analytics/`, filtered for
`count` or `refer`: zero hits. The only way to answer *"which message references this object?"*
is to search `messages.attachments`, a `jsonb` column with **no index on its contents**.

**MEASURED BEFORE THIS SPECIFICATION WAS WRITTEN**, on the lane's 66,516 messages of which
1,580 carry attachments:

    the lookup                          time      buffers   rows filtered
    a hit, sequential scan            2.132 ms       806        53,074
    a MISS, sequential scan           2.886 ms     1,016        66,516
    a hit, GIN jsonb_path_ops         0.082 ms         6             —
    a miss, GIN jsonb_path_ops        0.018 ms         5             —

    the index: 136 kB against an 8,128 kB table — 1.7%

**THE REFUSAL IS THE EXPENSIVE CASE**, because an id nobody references scans the whole table
before it can say no. That is 4.10's shape again — *"a round trip that exists only to produce a
refusal"* — with the cost on the authorisation path rather than the store.

**AND THIS IS THE OPPOSITE ANSWER TO CHAPTER 4.1's.** That chapter measured an index that
*"buys a gap inside the run-to-run spread for +49% storage"* and concluded **you cannot index
your way out of an analytical question when the cost is the aggregation**. Here the cost is a
lookup, and 26× to 160× for 1.7% is what an index does to a lookup. The two findings do not
conflict; the chapter publishes them side by side, because the useful lesson is *which kind of
cost you are looking at*, not *whether indexes help*.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A recipient opens the photo (Priority: P1)

Tuan receives a message carrying a `media_id`. His client asks Relay for a delivery URL, gets
one valid for an hour, and fetches the bytes straight from object storage — the same shape as
the upload, in reverse.

**Why this priority**: it is the whole chapter. Chapter 4.11 shipped an attachment that no
client can turn into an image; both its `research.md` and its contract say so in as many words:
*"a `media_id` in a message is not yet a URL anybody can fetch."*

**Independent test**: send a message carrying a media attachment, ask for a delivery URL as a
member of that channel, and fetch the bytes. The bytes come back and match what was uploaded.

**Acceptance scenarios**:

1. **Given** an object referenced by a message in a channel Tuan belongs to, **when** Tuan asks
   for a delivery URL, **then** he gets one and it fetches the bytes.
2. **Given** that URL, **when** it is used 59 minutes later, **then** it still works; **when**
   it is used after the hour, **then** the store refuses it from its own clock.
3. **Given** the same URL with one character of its signature changed, **then** the store
   refuses it.

### User Story 2 - Somebody who cannot read the message cannot read the file (Priority: P2)

Linh is not a member of the channel the photo was sent to. She has the `media_id` — it is in a
payload she saw, or she guessed it. She asks for a delivery URL and is refused.

**Why this priority**: it is the clause's own sentence and it is constitution I. FR-MED-08 says
authorisation *follows the message*, so a caller who cannot read the message cannot read the
file, and the note under the SRS table says why: *"media access control inherits channel
membership rather than inventing a parallel ACL system."*

**Independent test**: two tenants and two users of one tenant. Ask for a delivery URL as each,
against an object neither may read, and compare the answers.

**Acceptance scenarios**:

1. **Given** an object of another tenant, **then** the request is refused.
2. **Given** an object of this tenant referenced only in a channel the caller does not belong
   to, **then** the request is refused.
3. **Given** a `media_id` no object has, **then** the request is refused **identically** to
   both of the above — the same code, message and field, as 4.11 established for attaching.

### User Story 3 - One object, two channels, two answers (Priority: P3)

The same `media_id` is attached to a message in channel A and to another in channel B. A caller
who belongs to A but not B may read it; a caller who belongs to neither may not.

**Why this priority**: it is the case the clause's singular *"the referencing message"* does not
describe, and 4.11's `gaps.md` 057-1 named it as open. FR-MSG-11 has allowed the same id twice
since 3.24 — *"the same id twice is two attachments"* — so more than one reference is not an
edge case, it is the ordinary consequence of forwarding a photo.

**Independent test**: one object, two messages, two channels, three callers.

**Acceptance scenarios**:

1. **Given** membership of any one referencing channel, **then** the URL is issued.
2. **Given** membership of none of them, **then** the request is refused.
3. **Given** the caller is an application credential of the tenant, **then** the URL is issued
   whatever the memberships are — the clause names *"channel membership **or** API key"*.

### Edge Cases

- **An object with no referencing message at all.** A slot issued, bytes uploaded, never
  attached. FR-MED-08 says authorisation follows the message and there is no message. See
  Assumptions — this is the specification's one flagged assumption.
- **A `pending` object whose bytes were never uploaded.** The row exists, the object does not.
  A signed URL for it is well-formed and fetches a 404 **from the store**, which the caller sees
  and Relay never learns. FR-MED-09's *"explicit rejection marker"* needs a state the schema
  still refuses to hold (4.11's SC-006), so there is nothing better to answer with yet.
- **The URL outlives the authorisation.** A caller removed from the channel one minute after
  being issued a URL holds a working link for another 59. This is inherent to presigned URLs —
  the store checks a signature and knows nothing about membership — and it is the cost of
  ADR-13's whole design rather than a defect this chapter can fix.
- **A deleted message.** Deleting unlinks the attachment (4.11's FR-024), so the reference is
  gone and the object becomes unreadable by this route the moment the tombstone is written,
  while the object itself survives until FR-MED-10's sweep.
- **Fifty images in one channel.** `operationsFor` returns `["rest"]` for every `/v1` path, so
  each delivery URL spends the tenant's REST budget. A client rendering a gallery of fifty spends
  fifty. 4.8 found the same wall from the other side, where reading the request log spends the
  budget the reader is investigating.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A caller authorised to read a referencing message MUST be able to obtain a
  delivery URL for a media object, and that URL MUST fetch the bytes from object storage without
  them passing through Relay.
- **FR-002**: The URL MUST be valid for **one hour**, which is the clause's figure and differs
  from the upload slot's fifteen minutes. Both numbers MUST appear together somewhere a reader
  meets them, because two validities for one object is the kind of thing a reader assumes is a
  mistake.
- **FR-003**: Expiry MUST be enforced by the **store**, from its own clock, and demonstrated
  rather than asserted — the same way 4.10 demonstrated the upload slot's.
- **FR-004**: A caller who cannot read any referencing message MUST be refused.
- **FR-005**: An object of another environment MUST be refused, and the refusal MUST be
  indistinguishable from FR-004's and from a `media_id` no object has. Three conditions, one
  answer, for the reason 4.11 built: a refusal that named the cause reports whether somebody
  else's object exists.
- **FR-006**: An application credential of the environment MUST be issued a URL for any object
  of that environment, matching the clause's *"channel membership **or** API key"* and 4.11's
  reading of the same distinction for attaching.
- **FR-007**: Authorisation MUST be satisfied by **any** referencing message the caller may
  read, not by one chosen arbitrarily.
- **FR-008**: The reference lookup MUST be indexed, and the chapter MUST publish the
  before-and-after with the index's size. The measurements exist already; what the chapter adds
  is the index and the honest comparison against 4.1's opposite conclusion.
- **FR-009**: The chapter MUST state that FR-MED-08's *"object storage shall not be publicly
  readable"* half was already built and proven at 4.10, and cite the test whose title says so.
  Re-proving it would claim work this chapter did not do.
- **FR-010**: The chapter MUST publish that a signed URL **outlives the authorisation that
  produced it**, with the window named, as a cost of ADR-13 rather than a defect.
- **FR-011**: The chapter MUST record what a delivery request costs the tenant's rate budget,
  and MUST NOT route around it with an exemption list — 4.8 left the same loop counted and
  published for the same reason.
- **FR-012**: `gaps.md` 057-1 MUST be re-measured and closed or narrowed in writing. This
  chapter is the first consumer of the reference lookup that entry was filed about.

### Key Entities

- **Media object** — unchanged by this chapter. It gains no column and no state.
- **The reference** — the relationship between a message and a media object, which exists today
  only inside a `jsonb` array and which this chapter is the first thing to query.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A member of a referencing channel obtains a URL and fetches the bytes, and the
  bytes are byte-identical to what was uploaded.
- **SC-002**: Three refusals — another tenant's object, an object referenced only where the
  caller is not a member, and an id no object has — return byte-identical bodies apart from the
  request id.
- **SC-003**: The URL is refused by the store after one hour, demonstrated against the store's
  clock rather than asserted from the signature.
- **SC-004**: The reference lookup is measured before and after the index, with buffers as well
  as milliseconds, and the index's size is reported as a fraction of the table.
- **SC-005**: One object referenced from two channels yields a URL for a member of either and a
  refusal for a member of neither.
- **SC-006**: `check:fences` reports **0**, stated as an absolute number.
- **SC-007**: The chapter's prose is 2,000–4,000 words outside code fences and carries at least
  one `TRAP` box.
- **SC-008**: The tutorial job in CI succeeds on the chapter's push.
- **SC-009**: The dependency count across every `package.json` in `relay-platform` is unchanged,
  measured at the opening and again at the close. It is 29 at `part4-ch11`.
- **SC-010**: The sealed outsider suite fetches a media object's bytes from outside, using
  nothing but a published credential. That suite ran in CI for the first time at 4.11, after a
  one-line fix; a chapter about delivery that did not use it would be leaving the only
  from-outside instrument idle.

---

## Assumptions

- **THE ONE FLAGGED ASSUMPTION: AN OBJECT WITH NO REFERENCING MESSAGE.** FR-MED-08 grants
  access to *"callers authorised to read the referencing message"* and says nothing about an
  object that has none — a slot issued and uploaded but never attached, which is the normal
  state of every object between the upload finishing and the send being made. The strict reading
  refuses everyone, including the uploader, which would mean a client cannot show a preview of
  the file it just uploaded. The permissive reading grants it to the uploader, and to an
  application credential of the environment under FR-006.

  **This specification assumes the permissive reading** and flags it, because the same shape at
  4.11 — a clause silent rather than restrictive about an unrecorded uploader — was settled
  against the specification by `research.md` and produced **SRS 1.18**. The flag exists so
  research can attack it: *a research phase that only ever confirms is a research phase that is
  not reading.*

- **`GET /v1/media/:id` is assumed as the surface**, following `POST /v1/media`. The chapter may
  move it; nothing in the clause names a route.

- **No new dependency.** The signer already produces GET URLs — `presign.ts` has taken
  `"GET" | "PUT" | "HEAD" | "DELETE"` since 4.10 — so this chapter signs with code that exists.
  ADR-30's argument against an S3 SDK is not reopened.

- **The index is assumed to be GIN `jsonb_path_ops`**, because that is what was measured. A
  chapter that ships a different one must re-measure rather than reuse these figures.

---

## Dependencies

- **Chapter 4.11** (`part4-ch11`): the first media references exist. Without them this chapter
  has nothing to authorise against.
- **Chapter 4.10** (`part4-ch10`): the signer, the bucket, and the proof that unsigned reads are
  refused.
- **`gaps.md` 057-1**: the reference lookup, filed as having no mechanism. This chapter is its
  first consumer and owes it an answer.
- **Not blocked on movement VI.** Verification, `media.updated` and the `ready` state are later
  chapters; this one delivers bytes for objects the schema can actually hold, which today is
  `pending` alone.

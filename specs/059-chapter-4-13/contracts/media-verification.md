# Contract — the verdict, the seam it travels on, and what a client can now see

## 1. The internal route

```
POST /internal/media/:mediaId/verdict
```

`@Accepts("platform")`, on the seam `research.md` R8 found already built six times over. The
worker holds `RELAY_INTERNAL_CREDENTIAL` exactly as the dispatcher does; ADR-04 keeps it off
Postgres, so this is how a verdict becomes a row.

**Request — ready:**

```json
{ "verdict": "ready",
  "verified_bytes": 184320,
  "verified_type": "image/jpeg",
  "width": 1920, "height": 1080 }
```

**Request — rejected:**

```json
{ "verdict": "rejected",
  "reason": "declaration_mismatch",
  "verified_bytes": 4194304,
  "verified_type": "video/mp4" }
```

`reason` is one of `declaration_mismatch` or `scan_failed`. FR-005 requires the two to be
distinguishable, and they are distinguishable *to the platform* — whether they are
distinguishable to the customer is §4 below, and the answer is no.

**A transient failure sends nothing.** There is no `"verdict": "retry"`, because a verdict the
platform records as "we could not tell" is a row somebody will later read as a fact. The object
stays `pending` and the next sweep finds it, which is FR-009 expressed as an absence rather than
as a value.

**Idempotent by state, not by key.** A second `ready` for an object already `ready` answers 200
and changes nothing. A `ready` for an object already `rejected` answers **409** — the bytes are
gone, so the verdict is about an object that no longer exists, and answering 200 would let a
stale worker resurrect a rejected row's state while its bytes stay deleted.

## 2. What the worker reads

```
GET /internal/media/pending?limit=50
```

Returns `id`, `object_key`, `mime_type`, `declared_bytes` for objects in `pending`, oldest
first. No environment parameter — **the route takes no tenant as an input**, which is the
isolation property to state rather than a scope to add. A worker that could ask for one tenant's
objects would be a route worth forging.

## 3. What the worker does with the bytes, and it reads them twice for a reason

    HEAD  (signed)   does this object have bytes at all?     1.412 ms measured, 3 KB of headers
    GET   (signed, Range: bytes=0-65535)   the probe          dimensions live in the first 24
                                                              bytes of a PNG
    GET   (signed, streamed)   the scan                       ClamAV INSTREAM, chunked

**Three round trips where one would do, and the chapter has to justify it or collapse it.**
4.10 measured a single extra round trip on the slot path at **+24.1%** and published it, so the
cost of a round trip in this platform is a known number rather than an intuition. What buys the
split here is that **the scan is the only one that needs every byte**, and the largest allowed
object is 100 MB: a design that fetches the whole object to read 24 bytes of header is one that
moves 100 MB to answer a question the first 64 KB contains.

**Whether the scan's stream can feed the probe instead** — one GET, tee'd — is the collapsing
alternative, and it trades the round trip for holding the head of the stream. The tasks phase
measures both rather than arguing.

## 4. What changes for a customer, and it is one thing

`GET /v1/media/:mediaId` starts refusing objects that are not `ready`. That is ADR-14's
*"no signed URL until `ready`"*, which chapter 4.12 shipped the opposite of — deliberately,
because every object was `pending` and gating would have refused everything.

**Measured at `research.md` R4**: adding the gate today turns **10 of 76 tests red**, including
the isolation gauntlet's own control. So it cannot ship before the state machine, and this is
the chapter where both arrive.

**The refusal is the same 404 chapter 4.12 built**, and it stays one answer for what are now
five conditions:

    another environment's object              → 404 not_found
    referenced only where you cannot read     → 404 not_found
    no object has that id                     → 404 not_found
    no message references it                  → 404 not_found
    it is not `ready` yet, or was rejected    → 404 not_found   ← new

**A `rejected` object answers the same 404 as an absent one**, which is the existence-oracle
discipline 4.11 and 4.12 both built — and it is also why FR-MED-09's rejection marker is a
*later* chapter. A client learns that an attachment was rejected from the message payload, not
from the delivery route's refusal; the route's job is to say nothing.

**No new error code.** `check:errors` should read **34 codes, 34 sections** at the close,
unchanged from 4.12 — asserted rather than assumed, because a chapter that changes what a route
refuses usually reaches for new vocabulary.

## 5. Open question 1, decided here: dimensions ship, duration does not

**FR-MED-04 names both** — *"dimensions for images; duration for audio/video"* — and this
chapter ships one of them.

**What dimensions cost**: fixed offsets in four formats, checked against a real 640×480 PNG at
**24 bytes of 4,722**. No dependency, no second binary, no image in `compose.yaml`. The same
shape as ADR-30's *"28 lines of `node:crypto`"*.

**What duration costs**: MP4's `mvhd` atom, WebM's `Segment/Info/Duration`, Ogg's final granule
position, and MP3 — where a VBR stream without a Xing frame has no duration in its header at
all and the honest answer requires decoding. Four unrelated parsers, one of them genuinely hard.
The alternative is ffprobe: **a second non-TypeScript program, a second §7.3 argument, and
ffmpeg in the image.**

**Decision: images get dimensions; audio and video are verified and scanned but not probed, and
FR-MED-04 is recorded PARTLY MET with the missing half named.** The precedent is FR-MED-07 at
SRS 1.18 — *unmet by decision and not by oversight* — and the reason is the same: a chapter that
quietly shipped `duration_ms` as always-null would be worse than one that says which half it
built.

**What this gives up, said rather than hidden**: an audio attachment carries no duration, so a
client cannot render a scrubber length before playing. That is a real gap and it belongs to
whichever chapter decides ffmpeg is worth its image.

**And it makes §7.3's argument narrower and stronger**: the chapter adds exactly **one**
non-TypeScript program, for the one job nobody would write themselves, rather than two because
two were in the same sentence.

## 6. What the scanner does not promise

A signature scanner detects known signatures. SAD R9 names *"scanner misses"* as a residual
risk, and the chapter must say so — FR-014. A reader who finishes this chapter believing scanned
means safe has learned something false, and the clause that would correct them is a risk row
nobody reads.

**And a scanner with no definitions reports clean on everything.** Its readiness is a different
question from its reachability, and a health check that only proves the socket answers is the
shape of every *"a check that cannot fail for the reason you care about"* finding this project
has: chapter 4.2's `/ping`, chapter 4.9's unset credential, chapter 4.10's bucket.

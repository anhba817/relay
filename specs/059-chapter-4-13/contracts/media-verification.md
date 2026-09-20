# Contract — the verdict, the seam it travels on, and what a client can now see

## 1. The internal route

```
POST /internal/media/:mediaId/verdict
```

```ts
@Accepts({ platform: ["media-worker"] })
```

On the seam `research.md` R8 found already built six times over. ADR-04 keeps the worker off
Postgres, so this is how a verdict becomes a row.

**`@Accepts("platform")` DOES NOT COMPILE, AND THE FIRST VERSION OF THIS LINE WROTE EXACTLY
THAT.** `credential.guard.ts:36` types `AcceptSpec` as
`"application" | "user" | { readonly platform: readonly PlatformService[] }`, and its comment
says why in as many words: *"an authorization that can be omitted is one that will be, and the
omission is invisible: the route works, the tests pass, and the blast radius is one leaked
secret wide."* A platform route names **which** internal services may call it, because the
gateway terminates connections from the public internet and the dispatcher does not.

**WITH `RELAY_INTERNAL_CREDENTIAL_WORKER`, NOT THE DISPATCHER'S.** The first version of this
line said the worker holds `RELAY_INTERNAL_CREDENTIAL` *"exactly as the dispatcher does"*, and
so did `research.md` R8 — two artifacts agreeing with each other and neither asking what the
credential **says**. `authenticate.middleware.ts:63` maps that variable to the literal
`"dispatcher"`, and `Principal.service` is what every log line and request-log row reports.

**AND THE DECORATOR IS WHAT FORCES THE THIRD ENTRY, NOT THE UNION.** `PlatformService` is derived
from `PLATFORM_SERVICES`, so `["media-worker"]` is unwriteable until that list has the row —
which is a hard requirement rather than an encouragement. What is **not** true is the thing three
artifacts said next: widening the union does not stop anything compiling. Measured at analysis
pass 2 — a third entry added, `tsc --noEmit` on the api, **exit 0**. The union appears in three
positions and every one is `readonly PlatformService[]`, where a new member is purely additive.

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
and changes nothing. A `ready` for an object already `rejected` is refused — the bytes are gone,
so the verdict is about an object that no longer exists, and answering 200 would let a stale
worker resurrect a rejected row's state while its bytes stay deleted.

**THE REFUSAL IS 422 `unprocessable_request`, NOT A 409, AND THE FIRST VERSION OF THIS LINE SAID
409.** `ProtocolErrorFilter`'s ladder has nine rungs — 400, 401, 402, 403, 404, 413, 415, 422,
503 — and **409 is not one of them**, so a `ConflictException` that names no code answers
`internal_error`. That is not a hypothetical: `connection_environment_conflict` exists in the
registry at 409 precisely because somebody measured it, and its comment carries the failure —
`expected 'internal_error' to be 'connection_environment_conflict'`.

**So the choice was a tenth rung plus a new code, or a code that already fits.** 422 is 4.11's
own addition and its meaning is exactly this one: a well-formed request the platform understood
and cannot carry out. The caller's action is identical either way — a stale worker stops and does
not retry — so the distinction would have bought a word and cost a registry entry.
`check:errors` stays at **34 codes, 34 sections**.

**The rejected alternative, named**: `media_verdict_conflict` at 409, with a tenth rung and a
section in `docs/08-error-reference.md`. It is the more precise answer and it puts vocabulary for
a route no customer can call into the document customers read. `connection_environment_conflict`
is the precedent for doing that, and it is one entry rather than a habit.

## 2. What the worker reads

```
GET /internal/media/pending?limit=50
```

Returns `id`, `object_key`, `mime_type`, `declared_bytes` for objects in `pending`, oldest
first. No environment parameter — **the route takes no tenant as an input**, which is the
isolation property to state rather than a scope to add. A worker that could ask for one tenant's
objects would be a route worth forging.

## 3. What the worker does with the bytes, and it reads them twice for a reason

    HEAD  (signed, the BUCKET)   is the store holding        once per SWEEP, not per object.
                     anything at all?                        A missing bucket answers every
                                                             object's HEAD with 404, which the
                                                             sweep reads as "not yet"
    HEAD  (signed)   does it have bytes, how many, and       1.412 ms measured
                     since when?                             content-length is the store's
                     — the SIZE half of FR-MED-03 is          own count; last-modified is
                       ANSWERED here and ACTED ON later       SC-006's start instant
    GET   (signed, streamed)   the scan                       ClamAV INSTREAM, chunked.
                     FIRST, and unconditionally
    GET   (signed, Range: bytes=0-65535)   the type and       206 · `bytes 0-7/12` measured;
                     the dimensions                           a PNG's are in its first 24 bytes

**A 404 IS AMBIGUOUS AND THE SWEEP CANNOT SEE IT.** Measured at analysis pass 6: `HEAD` on the
real bucket for an absent key and `HEAD` on an absent bucket both answer **404**, because a HEAD
carries no body. The `GET` forms differ — `NoSuchKey` against **`NoSuchBucket`** — and the sweep
issues no GET for an object it believes is empty. So a bucketless store makes the worker inert
and silent, which is 056-10's condition one chapter on. The bucket probe above is the cheap
answer, and `storeReady` is the function that already does it.

**THE ORDER IS SCAN, SIZE, TYPE, AND STATING IT TOOK FIVE PASSES.** Each earlier fix was
pairwise — the size comparison moved onto the `HEAD`, and the scan moved ahead of the *type*
check so EICAR could reach it — which left the size verdict knowable before the scan and nothing
saying whether it short-circuits. **It does not.** FR-MED-04's *"every uploaded object"* is what
ordered the type check, and an object declaring one byte while holding five megabytes is at least
as worth scanning as one whose type is wrong; reading the clause one way and not the other would
be reading it selectively. The cost is streaming up to `KIND_CAPS`'s 100 MB for an object that
will be refused — and a caller who wants 100 MB streamed can upload a valid 100 MB video, so the
worst case is the cap either way.

**AND `last-modified` IS WHERE SC-006's CLOCK STARTS.** *"Time from upload to `ready`"* has a
start instant the platform never observes, because nothing tells it when the PUT finished. The
store does, on the round trip the sweep already makes — `last-modified: Sun, 20 Sep 2026
17:02:53 GMT`, measured at analysis pass 5 — **at one-second resolution**, because an HTTP date
has no sub-second field. That quantisation is a cost of `research.md` R1's decision: the client
notice the sweep replaced would have given an exact instant. Published beside the figure rather
than rounded away.

**THE STORE'S TWO HEADERS ARE NOT EQUALLY TRUSTWORTHY, AND THAT WAS MEASURED.** A presigned PUT
of twelve MP4 bytes sent with `content-type: image/png` answers `HEAD` with **`content-type:
image/png`** — the client's own claim, echoed — and **`content-length: 12`**, which is the
store's count. So the size comparison needs no bytes and the type comparison cannot use the
header. Reading `Content-Type` off the response is verifying the client's claim twice.

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

**AND THE GATE BREAKS THE SEALED SUITE, WHICH R4's FIGURE DID NOT COUNT.**
`packages/outsider/src/integrate.itest.ts:496` fetches the bytes of a **`pending`** object — the
three assertions chapter 4.12 added as SC-010 — and that suite is a third lane the 10-of-76
probe never reached. **Whether it can pass after this chapter depends on plan open question 4**:
only a worker inside the composed profile moves the object to `ready`, and then the assertion
becomes a poll rather than a read. The packaging decision decides whether SC-010 survives.

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

## 5a. `media_events` is specified, and this chapter does not start it

`docs/04-srs.md:827` declares an analytical table this chapter's data would fill:

    media_events | Storage metering, scan-pipeline health (FR-MED-12)
                 | environment_id, ts, event (uploaded/ready/rejected/deleted),
                   kind, bytes, processing_ms

**DR-17** builds on it: *"Stored-bytes-per-tenant shall be maintained as a daily rollup summing
`media_events` deltas (uploaded/deleted), reconciled weekly against an object-storage inventory
listing — the media analogue of FR-ANL-06."* The table has **no `.sql` file**, two live source
files quote DR-17 about it, and no artifact in this feature mentioned it until analysis pass 4.

**Decided: not here, and the reason is the column's own enum rather than scope.** This chapter
produces `ready` and `rejected`. `uploaded` belongs to chapter 4.10's slot, which predates it,
and `deleted` to FR-MED-10's sweep, which does not exist. So a producer built now would emit
**exactly the two values DR-17's sum does not read**, and the first thing anybody did with the
table would be to notice it holds nothing the clause asks for. Chapter 4.6 spent a chapter on
that shape — *"the rollup satisfies DR-10 over a table that receives no events"* — and it is
worth not rebuilding on purpose.

**What is given up**: `processing_ms` is measured at SC-006 and published in `baseline.txt`
rather than stored, so nobody can ask the analytical store how scan latency moved between
chapters. That is the honest cost, and `gaps.md` carries it with the arithmetic so FR-MED-12's
chapter starts from a decision rather than a discovery.

## 6. What the scanner does not promise

A signature scanner detects known signatures. SAD R9 names *"scanner misses"* as a residual
risk, and the chapter must say so — FR-014. A reader who finishes this chapter believing scanned
means safe has learned something false, and the clause that would correct them is a risk row
nobody reads.

**And the EICAR test can only exist because the scan runs first** (`research.md` R5a). ClamAV's
signature matches the file rather than a substring — EICAR plus two hundred trailing spaces is
already `OK` — so no object can both satisfy FR-MED-03's declaration check and trip it. The
order the clause required for its own reason is the order that makes the test possible, which is
a coincidence worth stating rather than relying on.

**And a scanner with no definitions reports clean on everything.** Its readiness is a different
question from its reachability, and a health check that only proves the socket answers is the
shape of every *"a check that cannot fail for the reason you care about"* finding this project
has: chapter 4.2's `/ping`, chapter 4.9's unset credential, chapter 4.10's bucket.

**THE TWO QUESTIONS HAVE TWO COMMANDS, ASKED OF A RUNNING CLAMD AT ANALYSIS PASS 5:**

    zPING\0      ->  PONG
    zVERSION\0   ->  ClamAV 1.5.4/28129/Sun Sep 20 06:26:26 2026

`PING` proves the socket. **`VERSION` proves a signature database is loaded, which version, and
how old** — the three fields are engine, database version and build date. A readiness check that
sends only the first is the 4.2 shape; one that sends the second can refuse a scanner whose
database is older than a stated bound.

**And that is what makes the check runnable red without breaking the scanner.** Manufacturing a
definitionless clamd is awkward; forcing the bound is one constant. The red run asserts the check
refuses when the reported date is too old, which is a test of the check rather than of ClamAV.

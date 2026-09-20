# Research — feature 059, chapter 4.13, "the only service that reads the bytes"

Every row here was checked against the tree, the database or a running container. Where a
figure appears, it is what came back.

---

## R1 · The flagged assumption is wrong, and a measurement is what settles it

**The assumption, as the spec states it**: the client tells the platform it has finished
uploading, through a published route, and the api publishes `media.uploaded` from there. The
argument for it was cost — one route, one publish, no vendor configuration, no sweep — against
an alternative the spec priced at *"91.6% of the work spent on objects that hold nothing."*

**That price is wrong, and the sweep is the cheapest thing in this chapter.** `presign` has
taken `HEAD` since 4.10 and nothing had ever used it. 200 of the lane's 3,005 `pending` rows,
signed and asked serially:

    HEAD per object                    1.412 ms mean · p50 1.094 · p95 1.714
    200 found bytes (200)                 34
    404, never uploaded to               166
    other                                  0
    the whole 3,005-row backlog          4.2 s, serial, one connection

**Four seconds for every unresolved object in the platform.** The 91.6% is real and it is
free: a 404 is the same round trip as a 200, and the wasted work is measured in milliseconds
rather than in anything a sweep interval would notice.

**So the client notice buys latency, not throughput** — seconds against a poll interval — and
it costs the thing FR-MED-04 is written to guarantee. *"Every uploaded object shall be
virus-scanned"*, and a notice the client may simply not send makes the scan contingent on the
client sending it. A client that uploads and stays quiet leaves bytes in the store, unscanned
and billed, until FR-MED-10 reaps them 24 hours later. SAD R9's named risk is *"scanner
misses"*; an object that was never scanned does not even reach it.

**AND THE SWEEP'S OWN SIGNAL IS AMBIGUOUS, FOUND AT PASS 6.** It reads a 404 as *"not uploaded
yet"*, and a missing **bucket** answers the same thing — `HEAD` has no body, so `NoSuchKey` and
`NoSuchBucket` are indistinguishable and only a `GET` tells them apart. So the mechanism below
needs a bucket probe once per sweep or it goes silently inert on the condition 056-10 already hit
in CI. One `storeReady` call an interval, which 4.10 built and measured.

**Decision: the sweep is the mechanism and the notice is an optimisation.** The worker finds
work by asking the database for `pending` rows and the store whether each has bytes. A client
notice may be added on top as a fast path, and if it is, it must be **unable to change the
outcome** — it can only make the same work happen sooner. This project has the sentence for
that already: *an optimisation wearing a branch's clothes* is what 4.11 deleted, and the
distinction that matters is whether removing it changes any answer. Here it does not.

**The third mechanism, priced and rejected.** MinIO publishes bucket notifications and one of
its targets is NATS, which this platform already runs — so the store could tell us directly.
Against it: **ADR-30's direction argument, one layer down.** That decision rejected the `minio`
client *"on the direction (a vendor client at the moment the platform is choosing a replaceable
store)"*, and a bucket subscription is the same commitment expressed in configuration rather
than in `package.json`. It also needs `mc` or the admin API to create the subscription, which is
a second binary for one message. Recorded rather than dismissed: if the store is ever fixed, it
is the lowest-latency answer available.

**What is given up, said rather than hidden.** Time-to-`ready` is bounded below by the sweep
interval rather than by the upload, so a client that uploads a photo and watches for the
placeholder to resolve waits for the next pass. The chapter publishes the interval and the
measured p50 rather than claiming the design is instant.

**AND IT GIVES UP AN EXACT START INSTANT, WHICH THIS ROW DID NOT RECORD UNTIL PASS 5.** The
notice would have told the platform when the upload finished; the sweep does not, so SC-006's
*"time from upload to `ready`"* has to come from the store. It does — `last-modified` on the
`HEAD` the sweep already issues — **at one-second resolution**, because an HTTP date has no
sub-second field. Measurable, and quantised, and the quantisation belongs to this decision.

---

## R2 · Constitution VII and the sidecar — `docs/12` §7.3, argued rather than assumed

**The clause**: *"One language (TypeScript/Node.js) across services, SDK, and dashboard; shared
protocol types between server and SDK eliminate drift bugs (ADR-01). **Introducing a second
language requires a superseding ADR with profiling evidence.**"*

**§7.3 states the question and declines to answer it**: *"VII's subject is the language services
are* implemented in*; a sidecar the worker talks to is arguably not that."*

**The reading that holds, and it is narrower than "a sidecar is fine".** ADR-01's own reasons
are all about *this codebase*: one language across services, the SDK must be JS anyway, and
sharing protocol types eliminates drift. None of the three reaches a program the worker speaks
a wire protocol to. Postgres is C. Redis is C. NATS is Go. MinIO is Go. ClickHouse is C++.
**The platform already talks to five programs written in four languages that are not
TypeScript**, and nobody has ever read VII as forbidding that — because none of them is *a Relay
service*.

**The line, stated so a later chapter can hold it**: a program is inside VII's rule when Relay
compiles, tests and deploys its source. ClamAV is a dependency the worker addresses over a
socket, exactly as the api addresses Postgres. What VII *would* forbid is writing the media
worker itself in Go because the scanning is CPU-bound — and ADR-01 named that trade-off in
advance: *"CPU-bound work needs care."*

**And the precedent is the PL/pgSQL guard**, which §7.3 points at by name. That argument was
made explicitly rather than by silence, and this one is made the same way.

**The chapter writes an ADR** — not because VII is being superseded, but because the
*boundary* is being drawn for the first time and the next chapter to want a binary will cite
it. Recording a line nobody has crossed is cheaper than arguing it again with a worse example.

---

## R3 · Constitution VII's OTHER clause, which no artifact had named

VII also says: *"New services require justification against the 'deliberately not a separate
service' table (SAD §4.2): same datastore + same transactions + same team ⇒ same service."*
This chapter adds the platform's fifth service, and nothing in `docs/12` mentions that clause.

**The media worker fails all three merge criteria, which is what makes it a service:**

| criterion | the four merged candidates | the media worker |
|---|---|---|
| same datastore | Postgres, all of them | **object storage** — and ADR-04 forbids it touching Postgres at all |
| same transactions | local transactions that splitting would distribute | **none** — it reads bytes and reports a verdict |
| same team | yes | yes |

**And the table's own column is *"Revisit when"***, so the argument has a shape to match: each
merge carries a reversal condition. The worker's is the mirror image — it stays separate while
scanning is CPU-bound and off the request path; it would merge if the scan ever became cheap
enough to do inline, which is the thing ADR-14 was written to forbid.

**The ingester is the precedent and it is an awkward one.** `services/ingester` has **no
Dockerfile**, and `api`, `gateway` and `dispatcher` all carry `profiles: ["services"]` in
compose — so the platform's fourth service is one that nothing ever starts except a test suite
spawning a child process (054's finding, re-measured at 057 and still open as `gaps.md` 050-8).
A fifth service packaged the same way would be a fifth thing nobody runs. **Whatever the chapter
decides about the worker's packaging, it should say which of those two shapes it is.**

---

## R4 · ADR-14 and the shipped route disagree, and the gate costs ten tests today

ADR-14: *"The scan gates byte delivery (**no signed URL until `ready`**), never message
delivery."* Chapter 4.12's `GET /v1/media/:mediaId` signs for a `pending` object.

**Measured rather than reasoned about.** One `WHERE state = 'ready'` added to the delivery
lookup, both affected suites run:

    Tests  10 failed | 66 passed (76)

    every grant in delivery.itest.ts        9 tests
    the gauntlet's own control              1 test — the attacker reading its OWN object

**The gate is not a WHERE clause somebody forgot.** It is correct only once something can
produce `ready`, and nothing can: `media_objects_state_check` permits one value. So the
sequencing is fixed rather than chosen — **the transition and the gate ship together, in this
chapter, or the gate ships broken.**

**AND 10 OF 76 IS AN UNDERCOUNT, BECAUSE THE PROBE RAN IN ONE LANE.** It measured
`delivery.itest.ts` and `gauntlet.itest.ts`, which are the api's. **The sealed outsider suite is
a third lane and it fetches the bytes of a `pending` object** — `integrate.itest.ts:496` asks
`GET /v1/media/:mediaId` for the object it uploaded itself, and chapter 4.12 added those three
assertions as SC-010. Under the gate that call answers 404 and the sealed suite goes red, and no
figure above includes it.

**AND THAT IS THE SECOND REASON THE FIGURE UNDERCOUNTS.** The probe also skipped a suite in the
lane it did run: `attach.itest.ts` is the api's, and chapter 4.11's two SC-006 tests assert the
`state` CHECK by name. Measured at analysis pass 3 by applying 0018's widened constraint to the
live database: **2 failed, 15 passed.** So *"10 of 76"* is the cost of the gate in two suites,
and the chapter's true bill is that plus the sealed suite plus 4.11's two — none of which a
single probe over two files could see.

**And whether it can pass afterwards depends on a question the plan left open.** Only a worker
running inside the composed profile moves that object to `ready`, so if plan open question 4
lands on the ingester's unpackaged shape, the sealed suite has no worker and the assertion
cannot be made at all. If it lands on a container, the assertion becomes a **poll** rather than a
read. **Two open questions are coupled and nothing said so**: the packaging decision decides
whether SC-010 survives this chapter.

**And the gauntlet's control is the interesting failure.** That test asserts the attacker can
read its own object, so that the refusal beside it means tenancy rather than a broken feature.
Gating without a state machine makes the control fail, which is the exact shape 4.12 recorded
when it wrote the attack: *"a control that fails for the wrong reason is worse than no control,
because the refusal underneath it then proves nothing."*

---

## R5 · What the scanner costs, and what it is

    clamav/clamav:latest   linux/amd64   7 layers   151 MB compressed
    quay.io/minio/minio    (for scale)              229 MB on disk

Plus definitions: ClamAV downloads its signature database at start (`freshclam`) and the
platform must decide whether the image ships them or fetches them, because **a scanner with no
definitions reports clean on everything** — which is SC-004's sibling and a failure mode no
status code shows.

**The protocol is `INSTREAM` over a socket**, which takes the object in chunks. That matters
against the size caps below: the worker never has to hold an object in memory to scan it.

**AND THE READINESS QUESTION HAS AN ANSWER, ASKED AT PASS 5:**

    zPING\0      ->  PONG
    zVERSION\0   ->  ClamAV 1.5.4/28129/Sun Sep 20 06:26:26 2026

`PING` proves the socket; **`VERSION` proves a signature database is loaded, which version, and
how old.** A check that sends only the first cannot fail for the reason it exists — 4.2's
`/ping`, 4.9's unset credential and 4.10's bucket, for the fourth time. And bounding the reported
date is what lets the check be run red without manufacturing a definitionless scanner.

**Not measured yet and owned by the tasks phase**: scan latency against a real object.

---

## R5a · THE EICAR TEST AND FR-MED-03 ARE MUTUALLY EXCLUSIVE, AND THE CLAUSE DECIDES THE ORDER

**Found at analysis pass 1, by running ClamAV rather than reasoning about it.** The chapter's
scan test is SC-003: *"the EICAR signature is rejected by a scanner that is actually running."*
EICAR is a 68-byte text file. `ALLOWED_TYPES` holds ten image, audio and video types and no text
type, so **whatever a slot is taken for, EICAR's bytes contradict the declaration** — and with
verification before the scan, the object is refused as `declaration_mismatch` and the scanner is
never asked. The test would assert `scan_failed` and get the other one.

**The obvious fix does not work, and that is the measurement worth keeping.** Embed the signature
in a file that IS the declared type. Asked of ClamAV through `INSTREAM`, which is the protocol
the worker will use:

    file                             bytes   verdict

    EICAR alone                         68   Eicar-Test-Signature FOUND
    EICAR + a newline                   69   Eicar-Signature FOUND
    EICAR + 200 spaces                 268   OK
    EICAR + newline + 1 KB of 'A'    1,093   OK
    EICAR prepended to a valid PNG     422   OK
    EICAR appended to a valid PNG      422   OK

**The signature matches the FILE, not a substring inside it.** Two hundred trailing spaces
defeat it, and there are two signature names for the two lengths that match at all. So there is
no object that both passes FR-MED-03's declaration check and trips the scanner — not by
embedding, not by padding, not in either order.

**Decision: THE SCAN RUNS BEFORE THE DECLARATION CHECK, and FR-MED-04's own word decides it.**
*"Every uploaded object shall be virus-scanned."* Refusing on the declaration first means some
uploaded objects are never scanned — and the object that lies about its type is exactly the one
worth scanning. The clause had already made this choice; what surfaced it was a test that could
not be written.

**What it costs, stated rather than hidden**: a mis-declared object pays a full scan before it
is refused, where the old order refused it from the sweep's own `HEAD`. Against that, the old
order left a hole in the word *"every"*, and the platform's own risk row (SAD R9) is about what
it fails to catch rather than what it spends.

**And the rejection precedence has to be written down**, because an object can now fail both.
`scan_failed` wins: it is the more serious fact about the caller, and it is the one an operator
reading `rejected_reason` needs. `data-model.md` §4's table carries the order.

---

## R6 · The probe splits in two, and only one half needs a second program

The allowed set is ten types in three kinds, with caps:

    image  10 MB   image/jpeg  image/png  image/gif  image/webp
    audio  25 MB   audio/mpeg  audio/mp4  audio/ogg  audio/wav
    video 100 MB   video/mp4   video/webm

**Image dimensions need no dependency and almost no bytes.** Checked against a real 640×480
PNG generated for the purpose:

    png magic: true | width 640 height 480
    bytes needed: 24 of 4,722 — 0.51%

PNG's `IHDR` is at a fixed offset; GIF's logical screen descriptor is bytes 6–10; JPEG needs a
short segment walk to the first `SOF` marker; WebP's dimensions are in the `VP8X`/`VP8`/`VP8L`
chunk. Four formats, one small reader — the same shape as ADR-30's *"28 lines of
`node:crypto`"*, and the same argument: a dependency for four fixed offsets is a dependency
whose surface is larger than the problem.

**Audio and video duration is the opposite.** MP4 keeps it in a `mvhd` atom, WebM in a
`Segment/Info/Duration` element, Ogg in the last page's granule position, MP3 in a header that
may not exist at all for a VBR stream without a Xing frame. **Four containers, four unrelated
parsers, and the last one is a known hard case.** That is what ffprobe is for, and it is the
reason FR-MED-04's parenthesis names both quantities rather than one.

**So the second-language question in R2 is not about the scanner alone.** The chapter can ship
image dimensions with no non-TypeScript program at all, and cannot ship duration that way.
Whether it ships both is a scope decision the plan takes below.

**AND THE STORE'S TWO HEADERS ARE NOT EQUALLY TRUSTWORTHY, WHICH WAS MEASURED.** A presigned
PUT of twelve MP4 bytes sent with `content-type: image/png`:

    PUT                      200
    HEAD content-type        image/png      ← the CLIENT's claim, echoed back
    HEAD content-length      12             ← the STORE's own count, correct

**So FR-MED-03 splits.** The size half is answered by the `HEAD` the sweep already issues and
needs no bytes at all; the type half needs the first bytes and nothing the store says. A worker
that reads `Content-Type` off the response has verified the client's claim twice and called the
second one a verification — the plan's top-ranked failure mode, now a measurement rather than a
worry.

**And it removes a round trip from the commonest rejection.** An over-size object is refused
from the sweep's own `HEAD`, before any GET.

**AND THE TWO READS HAVE OPPOSITE SHAPES.** The probe wants the first few kilobytes; the scan
wants every byte. A worker that fetches the object once and uses it twice is one design; a
worker that issues a `Range` request for the header and a streamed full GET for the scan is
another. 4.10's measurement of a single extra round trip — `storeReachable` at **+24.1%** —
is what makes that worth deciding rather than defaulting.

**And the `Range` half is buildable, checked rather than assumed**: a presigned GET carrying
`Range: bytes=0-7` answers **206 · 8 bytes · `bytes 0-7/12`**. SigV4 signs `host` and not
`Range`, so the header rides on an unmodified signature.

---

## R7 · The schema, and the migration this chapter owns

    migration tail                      0017_media_reference_index.sql  → this chapter is 0018
    media_objects_state_check           state = 'pending'      one value, on purpose
    rows on the lane                    3,005, every one pending
    objects in the store                  253 — 8.4%

Chapter 4.10's comment on that constraint: *"`ready` and `rejected` arrive with the
verification and scanning clauses; a CHECK that accepted them now would be a schema claiming a
state nothing can reach."* Widening it is this chapter's, and the widened version must still
refuse a fourth value — the constraint's job is unchanged, only its set.

**What the probe's output is stored as is an open question for `data-model.md`.** Dimensions and
duration are different shapes for different kinds, and the choice is a column pair that is null
for two of three kinds, a `jsonb` blob, or nothing stored at all.

---

## R8 · ADR-04's seam already exists, six times over

*"Never touching Postgres directly, per ADR-04."* The api serves six `internal/` controllers —
`dispatch`, `usage`, `session`, `backfill`, `memberships` and the root one — and the dispatcher
reaches them through one client:

    services/dispatcher/src/api-client.ts:67
      fetch(`${baseUrl}/internal/dispatch/${path}`, …)

So the worker's transition surface is a new route on an existing seam rather than a new
mechanism.

**THE CREDENTIAL IS NOT A FREE REUSE, AND THIS PARAGRAPH SAID IT WAS.** The obvious sentence —
*the worker holds `RELAY_INTERNAL_CREDENTIAL`, as the dispatcher does* — is what the first
version of this row and `contracts/` §1 both wrote, and neither asked what the credential
**says**. `authenticate.middleware.ts:63` maps that variable to the literal `"dispatcher"`:

```ts
const PLATFORM_SERVICES = [
  [PLATFORM_CREDENTIAL_ENV, "dispatcher"],
  [GATEWAY_CREDENTIAL_ENV, "gateway"],
] as const satisfies ReadonlyArray<readonly [string, string]>;
```

`Principal.service` is what every structured log line and every request-log row then reports, so
a worker on the dispatcher's variable is **a fifth service that logs as the fourth**. And the
type was built to force exactly this decision — its own comment reads *"adding a third internal
service widens this union on its own and every route that must now decide about it stops
compiling"*, which is the compiler asking a question that reusing the variable avoids.

**Decision: a third entry, `RELAY_INTERNAL_CREDENTIAL_WORKER`.** The cost is one variable in
`compose.yaml` and in CI. The alternative is a platform whose audit trail attributes the only
component that reads customer bytes to a service that never touched them.

**AND THE FORCING FUNCTION IS NOT THE ONE THAT COMMENT NAMES.** This row said the widened union
would stop routes compiling *"which is the mechanism working rather than a cost"*, copying the
middleware's own sentence. **Measured at analysis pass 2: it does not.** A third entry added,
`tsc --noEmit` on the api, **exit 0**. `PlatformService` occurs in three positions and all three
are `readonly PlatformService[]`; adding a member to a union in array-element position is
additive, and an existing route goes on admitting exactly what it admitted.

**What does force the entry is the guard's type.** `credential.guard.ts:36` makes
`@Accepts("platform")` a compile error — a platform route must name its callers — so
`@Accepts({ platform: ["media-worker"] })` cannot be written until `PLATFORM_SERVICES` holds the
row. That is a hard dependency, and it is a different mechanism from the one three artifacts
cited. **The source comment is wrong as written** and is worth a `gaps.md` entry: a claim about
compiler behaviour that nobody had run.

**The variable this reuses the LESSON of** is `RELAY_INTERNAL_CREDENTIAL` itself, whose absence
4.9 found was silently skipping three isolation attacks at 0 ms apiece.

---

## R7a · The sweep's batch query is a SORT, and §5 reasoned about the predicate

`data-model.md` §5 said no index was needed: *"the predicate is `state = 'pending'` and today
every row matches, so an index on it would select the whole table."* True about the predicate,
and the query also carries `ORDER BY created_at LIMIT 50`. Measured at analysis pass 2, on the
lane's 3,028 rows:

    shape                                          plan                        buffers    time

    no index                        Seq Scan 3,028 rows + top-N heapsort            90   2.370 ms
    partial (created_at) WHERE      Index Scan, stopping at 50                       4   0.029 ms
      state = 'pending'

    index size 88 kB against a 736 kB table — 11.96%

**22× fewer buffers for a 50-row batch**, and the table is the smallest in this movement.

**AND THE STORAGE RATIO RUNS THE OPPOSITE WAY FROM 4.12's.** That chapter's GIN was 1.62% and
stays 1.62% — it indexes every message. This one is **11.96% today because every row is
`pending`**, and it shrinks as objects resolve: a partial index over the unresolved set is
exactly as large as the backlog. The two published side by side say what a partial predicate
buys, which neither says alone.

**Chapter 4.1's sentence is the one that applies**: *the join is 140 ms of a 698 ms plan and the
sort is 656.* The cost here is the ordering, not the filter — and 4.12's complement holds too,
because the index only helps once the query is written so the planner can walk it in order.

---

## R9 · What held, and one premise that would have been cited wrongly

- **`media.uploaded` really is absent.** Zero occurrences across `services/`, `packages/`,
  `analytics/` and `compose.yaml`. The SAD names a consumer and an event and never named a
  producer.
- **NFR-SCL-01 CARRIES NO MEMORY BUDGET, AND IT WOULD HAVE BEEN CITED FOR ONE.** The obvious
  sentence to write is *"a 100 MB video against NFR-SCL-01's 160 MB budget"*. That clause reads
  *"10,000 concurrent WebSocket connections per gateway instance"* and says nothing about
  memory; the 160 MB is `docs/11`'s **measurement of the gateway's RSS**, and 050 already
  recorded this exact mistake — *"cite the source that holds the number"*. The worker's memory
  bound is a thing this chapter would have to measure, not a clause it can quote.
- **ADR-01 named the trade-off in advance**: *"CPU-bound work (HMAC signing at volume) needs
  care."* The media worker is the second instance, and the SAD already calls it *"the one
  service where ADR-01's worker-thread posture matters from day one"*.
- **The sampling in R1 is biased and says so.** The 200 rows were taken newest-first, and 34 of
  them had bytes — 17% against the bucket's 8.4% overall. Recent slots are likelier to have been
  used. The per-object figure is unaffected; the hit rate is not a population estimate.

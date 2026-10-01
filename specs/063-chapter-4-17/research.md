# Research — chapter 4.17, the milestone

Everything below was run against the composed stack on 2026-10-01, not read off a file.
`docker compose --profile services up -d --wait`, `RELAY_POSTGRES_PORT=15432`.

---

## R1 — Is the sealed suite's `pending` a race, or a worker that is not working?

**It is a race, and it wins by a wide margin.** The composed worker is working.

```
media-worker started  interval_ms 5000  scanner "ClamAV 1.5.4/28139/Wed Sep 30 06:24:18 2026"
sweep  seen 616  ready 1  rejected 0  waiting 615
```

Five runs, slot to verdict, against the deployed container — **and this measurement was wrong,
which analysis pass 5 found and which is written out in full below because the error is more
useful than the number**:

```
         slot        PUT       PUT -> verdict
run 1   34.4 ms    6.4 ms      6,123 ms
run 2   10.7 ms    7.1 ms      5,670 ms
run 3    8.5 ms    5.2 ms      5,656 ms
run 4    8.1 ms    4.9 ms      5,756 ms
run 5   10.4 ms    6.3 ms      5,693 ms

min 5,656 · p50 5,693 · max 6,123 ms        ← THE WORST CASE, REPORTED AS THE MEDIAN
```

**A LOOP THAT WAITS FOR THE THING IT IS TIMING SYNCHRONISES WITH IT.** Each trial ended the
moment the sweep processed it, so the next trial's slot was taken a few milliseconds after a
sweep and had to wait almost the whole 5,000 ms interval. Every sample is phase-locked to the
timer it is measuring.

**The tell was in the spread and I read past it**: 467 ms across five samples of a process
gated by a 5,000 ms timer is impossible unless the samples are not independent.

Ten trials, each preceded by a random sleep so the upload lands uniformly in the cycle:

```
1,197 · 1,340 · 1,390 · 1,570 · 2,950 · 3,240 · 3,440 · 4,240 · 5,340 · 5,840 ms

min 1,197 · p50 2,953 · max 5,840 · mean 3,055        over a 5,000 ms sweep interval
```

So an uploaded object is `ready` **between about 1.2 and 5.8 seconds later, p50 2,953 ms** —
the wait is uniform over the interval because nothing tells the platform the upload finished
(ADR-13), plus roughly 0.7 s of work. **The sampled path is the refusal one** (2,048 bytes that
are not a PNG), so it omits the thumbnail's ~15 ms and a store write; the wait dominates either
way and the difference between the two paths is tens of milliseconds.

The sealed suite PUTs, sends and reads within milliseconds of each other, so its expectation of
`pending` holds — and on the corrected figures its margin is **at least 1.2 s** rather than
about five, which is a smaller margin than the original measurement implied and still a wide
one.

**Decision**: the suite's assertion stays correct and its stated reason is replaced. The comment
reads *"this suite runs no media worker, which is what makes the value stable rather than
timing-dependent"*, and CI's own job starts that worker under `--profile services`. It is
timing-dependent and it is stable, which are not the same claim — **a race with a five-second
margin is the kind nothing will ever catch**, and the sentence that would have explained it away
is the one this chapter exists to find.

**Alternative considered and rejected**: shorten the sweep interval for the sealed lane so the
race is visible. That makes a test pass by changing the product's timing, and the interval is a
deployment property rather than a test fixture.

---

## R2 — Does the whole path work today, outside a test?

**Yes, every step, and the join has never been asserted.** One image, published surface only:

```
1  slot + PUT                    201, PUT 200
2  channel                       201
3  send BEFORE the verdict       201   attachment {"type":"media","media_id":…,"state":"pending"}
4  the deployed worker            ready after 6,143 ms   (one sample, high in the cycle)
5  rendition                      created
6  history                        200   state "ready", thumbnail {media_id, 320, 240}
7  link for the parent            200   url issued
8  the bytes                      480,813  IDENTICAL to what was uploaded
9  link for the THUMBNAIL         200   url issued, 30,612 bytes
```

**Decision**: the chapter builds one suite that is this walk, with assertions. It adds no
mechanism, which is what the specification's FR-012 says and what this run makes safe to
promise.

**And the history payload is richer than the spec assumed.** It carries the thumbnail's id and
dimensions beside the state:

```json
{ "type": "media", "media_id": "…", "state": "ready",
  "thumbnail": { "media_id": "…", "width": 320, "height": 240 } }
```

So a recipient never has to guess a rendition id — which is why step 9 is a question a client
would really ask.

---

## R3 — Can a recipient fetch the thumbnail?

**Yes, and it is authorised through the parent.** `GET /v1/media/{rendition_id}` answers **200**
with a signed URL, and the bytes are 30,612 against the parent's 480,813. 4.15's
`readableMediaObjectKey` resolves `parentId ?? mediaId`, so the rendition — named by no message —
inherits the parent's reachability rather than needing a rule of its own.

**Decision**: the journey asserts both fetches. The thumbnail is the only part of this path that
has never been asked for from outside the platform.

**AND EVERY FIGURE IN R2 AND R3 WAS RE-MEASURED IN PHASE 3, BECAUSE THE RECIPE WAS NOT WRITTEN
DOWN.** This walk was taken with an 800×600 PNG of **447,377 bytes** and nothing anywhere
recorded how those bytes were produced — colour type, filter, entropy, seed. A number whose
method is unrecorded cannot be reproduced, so the suite could not be built to hit it and the
figure had to be taken again against the fixture that actually ships: **800×600 greyscale,
xorshift32 noise, filter 0, `deflateSync` at default level — 480,813 bytes, deflating to
480,756.** Its thumbnail is 320×240 and **30,612 bytes**.

The walk is otherwise identical and the published numbers above are now this fixture's. **The
transferable half is that a measurement is a method plus a number**, and a research pass that
records only the number hands the implementation a target it cannot aim at — which is the same
shape as 4.16's quickstart sending the reader to another document for its fixture.

---

## R4 — Where does the journey suite live?

**`packages/outsider`.** Three reasons, and the first is decisive.

1. **It is the only lane that runs the deployed worker.** `packages/e2e` boots services in
   process; the api lane calls `recordMediaVerdict` directly. The sealed suite is the only one
   whose job starts `--profile services`, which is where the container is.
2. **The journey needs no workspace code.** Every step above is a published route plus a signed
   URL — `POST /v1/media`, a `PUT`, `POST /v1/channels/{id}/messages`, `GET …/messages`,
   `GET /v1/media/{id}`. The seal forbids importing workspace code and the walk does not need to.
3. **The media sequence it already has stops exactly where this chapter starts.** Extending it is
   cheaper than a second suite that duplicates its harness, and it keeps one place where the
   question *"what can an outsider do with an image?"* is answered.

**Alternatives considered**: a new `packages/e2e` journey beside `tuan.itest.ts`, which has the
right shape — *"each step names the chapter that made it possible"* — but boots its own services
and so cannot exercise the container. And a new suite in `services/api`, which would have to
call the worker as a function, which is the thing the milestone is for.

**The cost of the choice**: the sealed suite runs in one CI job and nowhere locally, so the
journey is only exercised by CI and by a hand-run. That is already true of its nineteen tests and
is recorded rather than repaired.

---

## R5 — What does the path cost, and how much of it is the timer?

```
slot                     8–34 ms      a signature, no contact with the store (4.10)
PUT                       5–7 ms      480,813 bytes to MinIO on the loopback
waiting for the sweep    0–5,000 ms   the interval, not work — UNIFORM, not a constant
scan + verify + thumbnail  ~700 ms    the floor of the ten independent trials, 1,197 ms,
                                      minus the smallest possible wait
history / link / GET      < 20 ms     each

end to end               1,197–5,840 ms, p50 2,953 over 10 independent trials
```

**Decision**: the chapter publishes the decomposition and names the timer as the dominant term.
Publishing *"5.7 seconds end to end"* without it would describe a platform that is slow at
scanning, when it is a platform that checks every five seconds.

**The 700 ms is a residual, not a measurement**, and the plan says so: it is what is left after
subtracting a bound from a total. The corrected version is a better residual — the minimum of
ten independent trials is the sample that waited least, so what remains after the smallest
possible wait is closer to the work than any figure taken off a phase-locked loop. A direct measurement of the scan belongs to 4.13, which took
it; re-deriving it here by subtraction would publish a worse number for the same quantity.

---

## R6 — What happens when the worker is stopped?

```
PUT 200
state after 20 s          pending
GET /v1/media/{id}        404  not_found  "no such media object"
```

**A stopped worker and an object that does not exist are the same answer from outside.** 4.13
recorded this one layer in — *a correct refusal is indistinguishable from an object nobody
uploaded to* — and from the published surface it is the same 404 that 4.12 built deliberately so
a guessed id tells an attacker nothing.

**Decision**: SC-002 is discharged by the journey waiting on a *condition with a deadline* and
failing with a message that names the worker. The platform's 404 is correct and must not change;
what changes is that one test now depends on the worker, so stopping it turns something red.

---

## R7 — Two instrument notes from running this research

**`date +%s%3N` does not truncate on this machine.** It printed `1790822295522477316` — `%s`
followed by nine digits of nanoseconds — so the first timing harness reported `slot 70934383ms`
and a verdict `5259760396ms`. Numbers that look like milliseconds and are wrong by 10⁶. Timings
here are taken with `time.perf_counter()`.

**And a defaulting accessor turned a wrong key into a platform defect.** The first journey probe
read `hist.get("data")` where the response key is `messages`, and `(items[0].get("attachments")
or [{}])[0]` rendered that as `attachment = {}` — which reads exactly like history dropping the
attachment. The platform was right and the probe was wrong. **A default that supplies an empty
value makes "I asked the wrong question" and "the answer is nothing" print the same line**, which
is this project's instrument rule arriving from the client side.

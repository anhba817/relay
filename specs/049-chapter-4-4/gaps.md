# Gaps — 049, chapter 4.4

Six entries. Each names what it would cost to close.

---

## 049-1 — A NATS restart breaks whichever stream is being written, and this chapter made that constant

048-6 recorded the cause as *"an abrupt `docker compose down` mid-write"*. That is wrong, and
this feature falsified it by accident while running T091's routine restart. Four observations,
including a control and a deliberate reproduction:

    compose stop nats, api writing          -> EVENTS unrecoverable
    compose restart nats, api writing       -> ANALYTICS unrecoverable
    compose restart nats, API STOPPED       -> healthz ok, clean
    compose restart nats under 500-request  -> ANALYTICS unrecoverable
      load, deliberately

**Graceful or not makes no difference; having a writer does.** The third line is the control,
and without it the finding would have been "the broker sometimes fails to recover".

**And chapter 4.4 turned a rare condition into a permanent one.** Before it, the api published
to `ANALYTICS` once per webhook delivery attempt — 36 records in several days. It now publishes
on every request, and Docker polls `/healthz` every five seconds, so the stream is never idle
and every restart from here lands mid-write.

**Cost to close**: unknown, and probably not this project's to pay. It needs the failure
reproduced against a NATS release and reported upstream, or a `compose` arrangement that stops
the writers before the broker. What can be done cheaply is documenting the order — stop `api`,
then `nats` — which is one line in the quickstart and is not the same as fixing it.

---

## 049-2 — The compose api cannot create a stream it does not already have

    NatsError: replicas > 1 not supported in non-clustered mode

`replicaCount()` returns 3 when `NODE_ENV === "production"`, and `services/api/Dockerfile:43`
sets exactly that. `compose.yaml` runs a single-node broker. So the api can *use* a stream it
finds and cannot *create* one it does not — and 474 `request_log.publish_failed` lines
accumulated while that was true, every one a record that never reached the store.

It stayed invisible because the streams pre-existed: they were first created from outside the
container, where `NODE_ENV` is unset and `replicaCount()` returns 1. **048-6's own repair did
the same thing without noticing** — it recreated `EVENTS` with a host script, which is why it
appeared to work.

**Cost to close**: one line — `RELAY_NATS_REPLICAS: 1` on the api, dispatcher and gateway
services in `compose.yaml`. Not taken here because it is a change to the shared development
environment rather than to this chapter's subject, and it wants a moment's thought about
whether the production default of 3 is right to keep.

---

## 049-3 — `check-lane-scope.py` reports zero because it looks at nothing

    controls: 10 of 10 fired
    check-lane-scope: 0 integration files, 0 unscoped read(s) ...      exit 0

Line 28 of `specs/045-part-3-rework/check-lane-scope.py` hardcodes
`/home/dong/work/relay/tmp/part3-refactor` — a worktree 045 deleted when it closed.

**This is the defect the script's own feature wrote the rule about.** 045-81: *"a checker handed
a ref that does not resolve compared nothing and exited 0 — twenty-six times… the zero that
means 'clean' and the zero that means 'never looked' printed the same line."*

**And its ten controls cannot catch it**, because they are synthetic strings checked in memory:
they fire whether or not the corpus is empty. A control that proves the checker WORKS says
nothing about whether it LOOKED.

Retargeted at the real tree it reports `50 integration files, 0 unscoped reads`, so this
chapter's tests are correctly scoped.

**Cost to close**: small — take the root from `argv` with the repository root as the default,
and refuse a run that finds zero files. The second half is the part that matters.

---

## 049-4 — The eviction crossover is 5.5 requests/second and nothing enforces it

`ANALYTICS` is one stream at 1 GiB, seven days, `discard: old`. An API request record occupies
**320 bytes**, so 1 GiB holds 3,355,443 of them: seven-day retention is reached at **5.5
requests/second sustained** and the SAD's 24-hour absorption at **38.8**.

Under `discard: old` the eviction takes the oldest messages regardless of which producer wrote
them, so **a busy tenant's request records evict a quiet tenant's webhook attempts**, with no
error at either end.

R12 was settled as one consumer, one stream — correctly for this volume. The condition under
which that stops being right is the number above.

**Cost to close**: a monitor on stream bytes against `max_bytes`, or the stream split R2 costs
out — narrowing `ANALYTICS` to `analytics.webhook.>` before creating a second stream, on a live
consumer. Neither is this chapter's, and the crossover is recorded so the next chapter does not
have to rediscover it.

---

## 049-5 — `refused_at`'s `handler` arm is an inference from silence

Two of the four values are stamped by the layer that refuses and two are inferred. A guard that
refuses **without** stamping is recorded as `handler`: a plausible value, wrong, in a column
nothing would flag.

`event.test.ts` walks the api's source, finds every class implementing `CanActivate`, and fails
if any lacks the stamp — run red by deleting the stamp before it was trusted green. That covers
guards. It does not cover a future middleware that refuses without stamping, which would be
recorded as `handler` if the router had run and `unmatched` if it had not.

**Cost to close**: extend the same structural test to middleware, which is harder because a
middleware that calls `next()` is the normal case and only a refusing one needs the stamp — the
test would have to recognise `res.end()` without `next()`, and that is a source-shape heuristic
rather than a fact.

---

## 049-6 — The tenantless share is a fact about a workload, and no production workload exists

63% of a stated mix, and the mix was chosen. What is structural is that `platform` is 100%
tenantless by construction and the internal seam is called on every message and every
connection — but the *weight* of that in a real deployment is unknown, and the lane is the
least representative instrument this project has.

**Cost to close**: nothing buildable. It closes when there is production traffic to measure, and
the chapter says so rather than implying the 63% travels.

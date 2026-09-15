# Gaps — 050, chapter 4.5, "the gateway's first stream"

**Eight new entries, and all eleven carried items re-measured.** 049 opened its file
with "Six entries" over 048's five open ones and never mentioned them; this one names
every carried item and says what it is *now*, including the two that changed.

---

## 050-1 — `pnpm coverage`'s "No test files found" DOES NOT REPRODUCE, AND THE RECORD WAS WRONG

Phase 4 recorded the workspace coverage lane as dead:

    RUN  v4.1.10
    No test files found, exiting with code 1
    include: packages/*/src/**/*.test.ts, services/*/src/**/*.itest.ts, …

with a worktree at `part4-ch4` reproducing it, and blocked **T058 and T059** on that.
Re-run at T095 against the same config and the same tree, it **runs** — an explicit
single file passes, and the full lane executes real suites for minutes.

**So the lane is not dead and the pins are enforceable.** What produced that output once
is unknown; the honest statement is that it is intermittent rather than structural, and
the earlier record's conclusion ("either 049's 100/100/100/100 came from a different
invocation or from somewhere else") is withdrawn — `vitest list` finding 108 files while
`run` found none was the tell that the corpus was fine.

**T058 and T059 were then done rather than deferred**: two pins written, both halves of
the threshold probe run, 49 pins swept and 49 binding. So the gap that survives is not the
pins — it is that **one instrument in this repository produced a false "nothing here" and
nobody can yet say why.**

**Cost to close**: run `pnpm coverage` twice at the next chapter's opening and write down
which behaviour appears. If "no test files" returns, it needs a reproduction before it
needs a fix — the one thing now known is that the config is not the cause, because the
config did not change between the two readings.

## 050-2 — THE ANALYTICAL STORE HAS NO LANE GUARD, AND FOUR CHAPTERS NOW WRITE IT

4.2, 4.3, 4.4 and 4.5 all write shared `relay_analytics` tables from integration tests.
Postgres has three defences: feature 030's global-operation trigger, an exemption list
`exempt.test.ts` asserts in **both** directions, and `check-lane-scope.py`. ClickHouse has
none of the three, and `check-lane-scope.py` cannot acquire it — its `SHARED` array is the
lane's Postgres tables and its own last line is *"SQL text only"*.

This chapter runs `SYSTEM STOP MERGES` on a table every later suite reads. T056 handles it
correctly — a `finally` carrying `SYSTEM START MERGES`, a scoped `DELETE`, and both counts
filtered to a dedicated environment id — **by copying 049's shape rather than by anything
enforcing it.** A failed assertion between the stop and the `finally` would leave the table
never collapsing duplicates for every later reader.

**No gaps.md in 046 through 049 records this.**

**Cost to close**: the cheapest honest version is a convention, not a trigger — a per-suite
environment id and a mandatory `finally`, asserted by a checker that greps `.itest.ts`
files for `SYSTEM STOP MERGES` without a `finally` in the same block, and for a bare
`count()` on a `relay_analytics` table. The analytical store has no equivalent of
Postgres's event-trigger hook, so the enforcement has to live in the test corpus.

## 050-3 — THE VIETNAMESE CHAIN IS NEVER COMPARED TO THE TREE, SO THREE STALE BODIES READ AS CLEAN

`check-fence-chain.mjs:265` — *"HEAD: the chain's end state must be the repository, byte
for byte"* — iterates **`en.state`**. The vi chain is replayed at :300 and compared against
the **English chapter's fences** (MIRROR), never against `relay-platform`. So the vi locale
is checked for two properties and neither of them is this one.

Measured directly, comparing each vi whole body against the tree:

    STALE    services/ingester/src/shape.ts        (vi 4.3)
    STALE    services/ingester/src/clickhouse.ts   (vi 4.3)
    STALE    services/ingester/src/main.ts         (vi 4.3)
    MATCHES  services/ingester/package.json        (vi 4.3)
    MATCHES  analytics/0003_webhook_attempts.sql   (vi 4.3)
    MATCHES  analytics/0000_message_events.sql     (vi 4.2)

**Three, and T010c predicted two** — it missed `main.ts`, which this chapter amended for
the three-arm log line. A Vietnamese reader following 4.3 today types a file that no longer
matches the repository, and every gate is green.

MIRROR cannot catch it either: vi 4.3 still carries fences byte-identical to en 4.3's,
which is exactly what MIRROR asks.

**Cost to close**: two things, and they are separable. The *instrument* half is cheap —
run the HEAD comparison over `vi.state` too and report it as its own count, which would
raise the headline by three today. The *content* half is a translated 4.4 and 4.5, which is
not this feature's work. **Or decide once, in writing, that the vi chain lags the English
one by design** and say so on the vi pages, rather than leaving each chapter to discover it.

## 050-4 — ELEVEN OF THE 36 INHERITED HEAD PROBLEMS ARE FENCES WHOSE TITLE NAMES NO FILE

The 36 has been carried as a bare number since 045. Split by what the checker actually
says:

    25   "<path> differs at line N"          a real divergence
    11   "<title> does not exist in relay-platform"

The eleven are fences titled with a **prose phrase** rather than a path — *"who builds a
docs_url"*, *"the ladder against the registry"*, *"the typo, now"*, *"the structural check,
on the first table added after it"*. The checker resolves the title as a path, finds
nothing, and files a permanent HEAD problem. They are not drift and they can never be
repaired by editing `relay-platform`.

This is the mirror of the class 043-1 already owns: an **untitled** fence is never compared
to anything (146 of 904), and a **mis-titled** one is compared against a file that cannot
exist. So the headline 110 is eleven units pessimistic, and the 25 is the number a chapter
should be measured against.

**Cost to close**: an hour. Either retitle the eleven (they are excerpts and want no title
at all, which moves them into 043-1's class and is honest about what they are), or make the
checker distinguish *"this title is not a path"* from *"this file drifted"* and report them
separately. The second is better, because it also names the next one the moment it is
written.

## 050-5 — A CLEAN STOP PUBLISHES A LEDGER THAT SAYS TEN CONNECTIONS ARE STILL OPEN

T035 and T078 together:

    clean stop (SIGTERM)   opened 10 | closed 0     of 20 expected
    kill      (SIGKILL)    opened  0 | closed 0     of 20 expected

`sessions.close()` calls `wss.close()`, which does not close established sockets, so no
per-socket close handler fires and `connectionLog.closed(...)` is never called. **Zero of
twenty is visibly wrong; ten opens with no closes is not.** A dashboard counting live
connections as opens-minus-closes drifts up by a full instance on every deploy, and nothing
in the record says the instance went away.

FR-009a's scoping keeps this out of the *reconciliation*. It does not keep it out of any
other consumer of the table, and this chapter publishes the table.

**NOT A DEFECT TO FIX IN THE GATEWAY.** Closing ten thousand sockets on shutdown to emit
ten thousand close records is the burst this whole chapter exists to avoid, and `session.ts`
argues that at :335 for a different reason.

**Cost to close**: a record the shutdown itself emits — one `instance.stopped` event
carrying the instance id and the count it held — so a reader can subtract a whole instance
instead of inferring it from silence. That is a new record type, a fourth arm on `route()`
and a column, so it is a chapter's worth of work rather than a line, and it belongs wherever
Part 4 does operational events.

## 050-6 — `packages/protocol/src/internal.test.ts` HAS NO BASE IN THE CHAIN

This chapter's five subject-grammar tests are not fenced. The checker's own words:

    diff for packages/protocol/src/internal.test.ts with no earlier fence to amend

No chapter publishes that file as a whole body, so a `diff` fence has nothing to anchor on.
It carries four `diff` fences in earlier chapters, every one of them in the same position —
the file is amended by chapters that never based it.

**Cost to close**: publishing a ~500-line test file as a whole body to support two
assertions, and then owning it for every later chapter. The chapter states the omission in
prose instead.

## 050-7 — `packages/test-harness/src/bound-port.test.ts` DIVERGED BEFORE THIS CHAPTER

    [HEAD] packages/test-harness/src/bound-port.test.ts differs at line 36

The replayed chain state differs from the tree at line 36, so a `-U6` hunk generated against
`part4-ch4` matches its pre-image **0 times**. This chapter adds the `BINDS_NOTHING` entry
for the ingester — the fix that surfaced when `compose.yaml` changed and turbo's cache
stopped hiding a two-chapter-old failure — and cannot fence it.

Same shape as 048-3 and 047-4, and one of the 25 in 050-4.

**Cost to close**: the class, not the instance. See 048-3.

## 050-8 — 4.4's INTEGRATION SUITE NEEDS A PROCESS NO GATE STARTS

`services/api/src/request-log/request-log.itest.ts` polls
`relay_analytics.api_requests` for a row only the **ingester** can write, to a 20-second
deadline. Nothing in the suite starts one, and **there is no ingester service in
`compose.yaml`** — it is run by hand. Measured both ways at T095:

    ingester running     5 passed (5)
    ingester stopped     5 failed (5)

So 4.4's suite — the one discharging its SC-001 — is green only for an operator who
happens to have a process running, and red in any lane that does not. Neither 049's gate
list nor 050's mentions it, and the quickstart does not either.

This chapter's own suites do **not** share the dependency, checked rather than assumed:
`connection-log.itest.ts` reads the stream directly and `ingest.itest.ts` calls
`ingestOnce` itself — 9 passed (9) with no ingester alive.

**Cost to close**: an hour, and there are two honest versions. Add the ingester to
`compose.yaml` as a service, which makes the whole stack match what the chapters describe
and fixes every future suite of this shape; or have the suite call `ingestOnce` the way
`ingest.itest.ts` does, which is smaller and leaves the lane dependent on nothing. The
second is the better test and the first is the better stack.

---

# Carried, re-measured

## 049-1 — A NATS restart breaks whichever stream is being written — **NOW HAS A COUNTER-EXAMPLE**

T068, after the broker-down run:

    ANALYTICS   written continuously   -> RECOVERED, 3,601 messages
    EVENTS      idle                   -> "could not be recovered"

**That is the opposite of the recorded rule**, which says the stream that fails is
whichever is being written. One run against one run, and neither controlled for how much
each stream had recently flushed to disk, so it does not falsify 049-1 — it removes
*"whichever is being written"* as a settled explanation. **The rule now needs a mechanism
rather than another observation.** Repaired from outside the container, as before.

## 049-2 — The compose api cannot create a stream it does not already have — **UNCHANGED**

`replicaCount()` still returns 3 under `NODE_ENV=production`
(`services/api/src/outbox/jetstream.publisher.ts:64`), the Dockerfile still sets it, and
`replicas > 1 not supported in non-clustered mode` is still what the compose api gets. The
streams standing today (3, 12,483 messages) were created and repaired from **outside** the
container, which is the same reason 048-6's repair appeared to work.

## 049-3 — `check-lane-scope.py` reports zero because it looks at nothing — **STILL STALE IN THE TREE**

Line 28 of `specs/045-part-3-rework/check-lane-scope.py` today:

    WT = pathlib.Path("/home/dong/work/relay/tmp/part3-refactor")

— the worktree 045 deleted. T014 measured both readings (0 files and 50 files, same ten
controls firing, same exit 0) **with an override**, and the file itself was never changed.
So the one-line fix has been available for two features and the shipped instrument still
reads nothing. **Cost to close: one line** — default `WT` to the repository root.

## 049-4 — The eviction crossover is 5.5 requests/second — **THE NUMBER MOVED, TWICE**

T083 reconstructed 4.4's figures exactly (5.55 and 38.8 rec/s from 320 B) and then measured
the stream's own accounting over 3,992 real messages: **403.5 B/record, 26.1% heavier**. So
the 7-day crossover is **4.40 rec/s, not 5.55**, and the 24-hour one **30.8, not 38.8** —
and a third producer spends the budget outright: two connection-pairs a second takes the
request allowance from 5.55/s to **0.86/s**.

**Still unenforced.** Nothing alerts on the stream's byte rate; the numbers are in print and
in nothing else.

## 049-5 — `refused_at`'s `handler` arm is an inference from silence — **UNCHANGED**

Untouched by this chapter. The guard that walks the api's source for every `CanActivate` is
still the only thing standing between the inference and a wrong value.

## 049-6 — The tenantless share is a fact about a workload — **UNCHANGED**

34 of 54 requests tenantless is a fact about this lane, and no production workload exists to
compare it against. Nothing in this chapter changes that, and the connection stream has no
tenantless arm at all (FR-006), so it adds no second data point.

## 048-1 — DR-10 and FR-ANL-06 still cannot both hold — **UNCHANGED**

`uniq` is exact to ~60,000 distinct and off by 0.51% at 70,000 against a 0.1% bound, and
047-1's second, worse reason stands: the TTL cuts at a timestamp and a daily rollup's finest
grain is a day, so the oldest day disagrees by 0.49% **at any cardinality**. Filed for
movement IV, untouched here.

## 048-2 — `message_events.delivery_latency_ms` still has no producer — **UNCHANGED**

The column exists (`analytics/0000_message_events.sql:22`) and the only thing that writes it
is `scripts/scale/load-analytics.mjs`. No service produces it. 048-3's neighbour column in
`webhook_attempts` carries a comment saying it is deliberately *not* this one.

## 048-3 — `vitest.coverage.config.mts` cannot take a fence — **UNCHANGED, AND MEASURED AGAIN**

Still a HEAD problem, now reported as `differs at line 29`. This chapter did not add pins
(see 050-1), so it added no new debt — but T010b established that nine of its 23 fences live
in `fences/post-series.md`, the appendix that applies after every chapter, which is the
question 047 asked of `compose.yaml` and nobody had asked of this file.

## 048-4 — The rollup is still unbounded — **UNCHANGED, AND NOW DOCUMENTED**

`daily_usage` still carries no TTL and still grows at `environments × days` forever. What
changed since 048 is that the absence is now **stated as a decision** in the file itself
(FR-003a, 047): *"IT HAS NO TTL AND THAT IS DELIBERATE … message_events expires at 90 days;
this does not."* The gap that survives is the one 047-3 named: **no clause says how long
metering history is kept.** Not this chapter's to decide.

## 048-5 — No gate checks that a chapter's tag matches the chapter — **UNCHANGED**

No script in either repository resolves a tag. `check-fence-chain` replays onto the working
tree and compares against `HEAD`, which is why the three Part 1 tags pointed at a superseded
lineage for months with every gate green. `relay-platform/README.md:8` still promises what
nothing checks. This chapter cuts `part4-ch5` under the same absence.

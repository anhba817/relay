# Research — chapter 4.8, "the log a customer can search"

Ten items. **Eight were measured against the running store or the tree**; two are readings of
published documents checked by opening them. Every figure below is reproducible from the lane
as it stood on 2026-09-16, and the ones that describe the lane rather than the platform say so.

---

## R1 — "end-to-end delivery latency" has three readings and no producer for any of them

**Measured.** `webhook_attempts.latency_ms` is written by `services/dispatcher/src/deliver.ts`:

    const started = Date.now();            // immediately before the fetch
    …
    const latencyMs = Date.now() - started;

It is **the endpoint's response time and nothing else** — it excludes commit, the outbox,
JetStream, the dispatcher's claim and every retry gap before this attempt. The schema file
already said so at `analytics/0003_webhook_attempts.sql:20`: *"How long the ENDPOINT took to
answer. NOT `message_events.delivery_latency_ms`."*

`message_events.delivery_latency_ms` is `Nullable(UInt32)` on a table holding **0 rows** with
**0 writers** under `services/` (`gaps.md` 048-2, re-measured at chapter 4.7's close). Nothing
in the gateway times a frame from commit to socket write — `grep` over `fanout.ts` and
`session.ts` finds the phrase "delivery latency" twice, both in comments about durability.

**Decision**: the chapter defines the quantity before computing anything. The three candidates
and what each would cost:

| reading | instants | what exists | what is missing |
|---|---|---|---|
| socket fan-out | commit → frame written to a subscriber's socket | neither instant is recorded together | a gateway-side producer, and a join across two services |
| webhook | commit → endpoint answered | the last leg only | the first instant, which the dispatcher does not carry |
| REST read | commit → returned by a history page | nothing, and it is pull rather than delivery | the concept — a read nobody made has no latency |

**Alternatives considered**: computing percentiles over `webhook_attempts.latency_ms` and
labelling them FR-ANL-10. Rejected — it would publish a number under a name that means
something else, which is the defect chapter 4.6 avoided by defining a connection-minute before
billing one.

---

## R2 — `quantile()` IS APPROXIMATE AT EVERY SAMPLE SIZE, INCLUDING THE SMALL ONES

**Measured** against the server, uniform values 1–10,000:

    n            p95 quantile()   p95 quantileExact()    error
    100                  95.05                    96    0.9896%
    1,000               950.05                   951    0.0999%
    10,000            9,489.45                 9,501    0.1216%
    100,000           9,472.45                 9,501    0.3005%
    1,000,000         9,521.90                 9,501    0.2200%

**There is no exact regime.** This is the opposite shape from chapter 4.7's `uniq`, which is
exact to 65,536 and wrong above it: `quantile` is wrong everywhere, and **worst at the smallest
sample** — which is exactly the size FR-ANL-10's buckets are, because it asks for percentiles
*per tenant per hour*.

**Decision**: if percentiles are computed at all, they use `quantileExact`, and the reason is
the bucket size rather than a preference. R7 measures that size.

**Alternatives considered**: `quantileTDigest` (same class of approximation, better tails),
and computing in the caller. Both were rejected on the same measurement — at a few hundred rows
an exact quantile is a sort, and the approximation buys nothing it does not also cost.

---

## R3 — THE PAGINATION CONTRACT ALREADY EXISTS, AND THE ANALYTICAL LOG CANNOT KEY A CURSOR THE SAME WAY

**Measured in the tree.** `services/api/src/messages/messages.schema.ts:97`:

    cursor:    z.string().min(1).optional()
    direction: z.enum(["older", "newer"]).default("older")
    limit:     z.coerce.number().int().min(1).max(200).default(50)

Chapter 3.x built it for message history, and its cursor stands on
`(channel_id, sequence)` — a **server-assigned, strictly increasing** number, which
constitution II requires message ordering to use.

**`api_requests` has no such column.** Its key is `(environment_id, ts, request_id)` and `ts` is
`DateTime64(3)`, so it ties. Measured:

    distinct (environment_id, ts) pairs   11,636
    pairs holding more than one row            43
    rows inside a tied pair                    91     0.78% of 11,684
    worst pair                                  3

A `ts`-only cursor skips or repeats those rows. **0.78% is small and it is not zero**, and it
grows with request rate rather than with time.

**Decision**: reuse the existing query shape rather than inventing a second one (FR-019), and
make the cursor composite — `(ts, request_id)` — with the tie behaviour asserted by a test that
plants two rows in one millisecond.

---

## R4 — THE CUSTOMER-FACING READ PATTERN IS ONE GUARD AND ONE DECORATOR

**Measured in the tree.** `WebhooksController`:

    @Controller("v1/webhooks")
    @UseGuards(CredentialGuard)
    @Accepts("application")

`Accepts("application")` carries an argument worth repeating rather than re-deriving: an
end-user token on a tenant-configuration route would let any logged-in person in a customer's
product redirect that customer's events.

**Decision**: the request-log surface follows the same shape. Whether it accepts `"user"` as
well as `"application"` is a scope question the plan must answer, not inherit — a request log
is closer to configuration than to content.

---

## R5 — SIXTY PER CENT OF THE LOG HAS NO TENANT, AND A THIRD OF THE REST IS THE PLATFORM

**Measured.**

    total                       11,684
    environment_id IS NULL       7,063   60.45%    platform 5,916 · none 1,147
    environment_id present       4,621   39.55%

    of the attributed 4,621
      /internal/*                1,656    35.8%
      /v1/*                      1,857    40.2%
      other (/auth/dev-token…)   1,108    24.0%
      endpoint absent                22

And the internal rows carry a **user** principal, not a platform one:

    /internal/session       user          1,423
    /internal/messages      user            115
    /internal/backfill      user             60
    /internal/memberships   user             50
    /internal/session       application       5

So the gateway forwards the end user's principal across the internal seam, and those rows are
attributable to a real person in the customer's product — **made by the platform on their
behalf, not by the customer's server.** The `endpoint` prefix is the only thing that
distinguishes them.

**Decision**: the chapter decides and states whether they appear. Neither answer is free:
hiding them makes the log incomplete against FR-ANL-01's *"every request"*; showing them puts
`/internal/session` at the top of a customer's own log, 1,423 rows of it.

---

## R6 — A 50-ROW PAGE READS 8,194 ROWS, AND THAT IS THE ENGINE'S FLOOR

**Measured**, busiest tenant, with and without a 30-day predicate:

    read_rows 8,194 · read_bytes 402,625 · result_rows 50 · elapsed 2.58–3.66 ms

`index_granularity` is 8192. One granule is the smallest unit a MergeTree reads, so a query
returning 50 rows reads at least 8,192 whatever the filter. The tenant owns 208 rows in total.

**Decision**: publish the number rather than tune it. It is the argument a pagination design has
to be made against — and the reason a page size of 50 and a page size of 500 cost nearly the
same read at this volume.

---

## R7 — THE LANE'S BIGGEST TENANT HOLDS 208 ROWS, SO FR-ANL-08 CANNOT BE EXERCISED HERE

**Measured** across the 152 attributed tenants:

    median rows per tenant     10
    p95                       155
    max                       208

FR-ANL-08 asks that *"analytical queries over 90 days of a single tenant's data return within 2
seconds at p95."* The largest tenant in this store holds 208 rows over two days. **The clause
cannot fail here for its own reason**, which is `docs/12` §2.3's argument about the 0.1% bound
arriving one movement later and one clause over.

**Decision**: the chapter states the bound it is measuring against and either plants a tenant
at a volume where the clause means something, or records the gap as §2.3 does. It does not
publish a p95 from a 208-row tenant and call FR-ANL-08 discharged.

**And it also affects R2**: a per-tenant-per-hour bucket at this scale holds single digits,
which is where `quantile()`'s error is ~1%.

---

## R8 — A WINDOW OUTSIDE RETENTION RETURNS ZERO, WHICH IS THE SAME ANSWER AS "NOTHING HAPPENED"

**Measured**: a query for 120–60 days ago against the busiest tenant returns `0`.
`api_requests`' TTL is `toDateTime(ts) + toIntervalDay(30)` — FR-ANL-07's figure, deliberately
not DR-09's 90, and `analytics/0005_connection_events.sql:4` records the reason: *"one TTL
clause cannot express two."*

**Decision**: the surface distinguishes "no requests in this window" from "this window is
outside retention", the same distinction chapter 4.7 drew between `no-data` and a zero. A
customer investigating an incident three months old needs to be told the log is gone, not that
nothing happened.

---

## R9 — THE WINDOW COMES FROM THE CALLER AND THE STORE TAKES A STRING

**Read in the tree.** `services/api/src/metering/clickhouse.ts` exposes
`query(sql: string): Promise<string[][]>` and chapter 4.7's reconciler builds its SQL by
interpolation — safely, because every value it interpolates is an internal UUID or a
`YYYY-MM-01` string the api produced itself.

**A request-log surface interpolates a caller's window and page size.** That is the first
caller-supplied value this platform has put into a ClickHouse statement.

**Decision**: values are validated before they reach the statement — the same Zod schema shape
R3 names — and the plan states how, because "it is validated upstream" is the sentence that
precedes every injection. A test that sends a hostile window is part of the phase, and it goes
red against the unguarded version first.

---

## R10 — THIS CHAPTER IS INSIDE CONSTITUTION III, WHICH IS WORTH STATING BECAUSE THE LAST ONE WAS NOT

**Read the clause.** *"Analytical queries MUST NEVER execute against the operational database
(PostgreSQL); billing, metering, and **dashboard analytics** read only from the analytical store
(ClickHouse), fed via a durable queue."*

A customer-facing request log is dashboard analytics reading ClickHouse. It is the clause's
central case rather than an exception to it. Chapter 4.7's conflict was about an **auditor**
reading both stores, which `gaps.md` 052-6 still carries; nothing in this chapter reopens it.

**Decision**: the plan's constitution check says PASS on III with the reason, and does not
inherit 4.7's argument.

---

## R11 — THE STORE CLIENT CANNOT RETURN NULL, AND THE CONTRACT PROMISED IT WOULD

**Measured.** `services/api/src/metering/clickhouse.ts` ends its `query` with

    trimmed.split("\n").map((line) => line.split("\t"))

so every cell is a string. ClickHouse writes NULL into a TSV body as the two characters `\N`.
Asked of the server, for one of the 22 rows whose route matched nothing:

    \N<TAB>GET<TAB>200

So a reader that selects `endpoint` alone reports an endpoint of `"\N"` for every unmatched
route — the string, not the absence. This is chapter 4.4's defect one layer up: that chapter
established that `LowCardinality(String)` cannot say "absent", and the transport underneath it
cannot either.

**Decision**: the statement selects `endpoint IS NULL` as a column of its own and the presence
column decides. That is chapter 4.7's `count()` move against the same class of problem — give
absence its own signal rather than a value someone has to interpret.

**Alternatives considered**: translating the literal `\N` in the reader (correct for TSV today,
and wrong the first time a column can legitimately hold those two characters), and switching the
client to `JSONEachRow` (correct, and it changes a file two chapters depend on for a problem one
extra column solves).

---

## R12 — THE GUARD'S DEFAULT IS THE PERMISSIVE ONE

**Read in the tree.** `services/api/src/auth/credential.guard.ts:92`:

    this.reflector.getAllAndOverride<AcceptSpec[]>(ACCEPTS, […]) ?? EITHER

and `EITHER` is `["application", "user"]`. **A route with no `Accepts` decorator accepts
end-user tokens.**

R4 read the decorator as an open decision and it is not: omitting it is the permissive choice,
taken silently. On a route that returns a tenant's entire API history that is the difference
between the customer's software reading its own log and every logged-in person in the
customer's product reading it.

**Decision**: the decorator is written explicitly whichever way the decision goes, and the
contract says which and why.

---

## R13 — THE ENGINE DEDUPLICATES AND THE READ HAS TO ASK FOR IT

**Measured**, before anything was written:

    rows                                       11,684
    distinct (environment_id, ts, request_id)  11,683
    duplicate keys                                  1
    active parts                                    2

`api_requests` is a `ReplacingMergeTree`. Chapter 4.4 chose it because a redelivered batch
writes the same request twice — chapter 4.5 measured `ingestOnce` reporting 16 for a stream
holding 8 — and the engine removes the copy **at merge time**. Until then a read returns both.

So a page of this log can repeat a request, and FR-007's *"no row appears in two consecutive
pages"* would pass on a merged table and fail on an unmerged one.

**Decision**: every read carries `FINAL`, and the chapter says so beside chapter 4.6's sentence
about the other engine — there the read contract was `sum()` with `GROUP BY`, here it is
`FINAL`, and in both **a query whose correctness depends on somebody having run `OPTIMIZE` is
right in a demo and wrong in production.**

**Alternatives considered**: `LIMIT BY (environment_id, ts, request_id)`, which deduplicates
within the read but silently changes what `LIMIT` counts; and documenting the duplicate as
acceptable, which is a contract that says a customer's log may show a request twice and cannot
say when.

**A NOTE ON THE MEASUREMENT.** The probe that found the duplicate then ran `OPTIMIZE TABLE …
FINAL` to test the TTL question in R14, which took the table to **1 part and 0 duplicates**.
The finding is no longer reproducible on this lane, and phase 1's T007a records that rather
than reporting the merged number as the opening state.

---

## R14 — FR-ANL-08's NINETY DAYS CANNOT BE PLANTED, LET ALONE MEASURED

**Measured.** Two rows inserted for a dedicated environment id:

    ts = now() - INTERVAL 60 DAY     ─┐
    ts = now() - INTERVAL  1 DAY     ─┴─ planted 2, surviving 1

The survivor is the one-day-old row. `OPTIMIZE TABLE … FINAL` afterwards changed nothing —
**the 30-day TTL removes rows at INSERT**, which is chapter 4.2's finding reproduced on this
table (120,000 rows over 120 days became 90,000 immediately, silently).

FR-ANL-08 asks that *"analytical queries over 90 days of a single tenant's data return within 2
seconds at p95."* Over `api_requests` there is **no fixture that can make that clause
meaningful**: the data cannot be put there. R7 said the lane is too small; this says the table
is the wrong shape, which is a stronger statement and a different remedy.

**Decision**: the chapter records the measurement and amends the clause rather than building a
fixture the schema refuses. The probe's rows were deleted and the count verified at 0.

---

## R15 — NEITHER CLICKHOUSE CLIENT HAS A TIMEOUT, AND ONE OF THEM IS ABOUT TO SERVE A CUSTOMER

**Read in the tree.** `services/api/src/metering/clickhouse.ts` and
`services/ingester/src/clickhouse.ts` both call `fetch` with no `signal` and no deadline.
`grep` for `timeout`, `signal` and `AbortSignal` over both returns nothing.

Chapter 4.7 put the first of those on a batch reconciler, where an unbounded wait costs a job
that was going to take minutes anyway. **This chapter puts it on a customer request**, where it
holds a Nest worker until the operating system gives up, and constitution III's second sentence
is a MUST: *"Failure or backlog of the analytical pipeline MUST NOT affect message delivery,
API availability, or webhook dispatch."*

The platform already has the pattern one outbound call over — `services/dispatcher/src/deliver.ts`:

    signal: AbortSignal.timeout(timeoutMs)

**Decision**: the deadline is an **option on `createAnalyticalStore`, defaulting to none**, so
4.7's reconciler keeps the behaviour it was measured with and only this route passes one. The
route answers **503** on expiry rather than an empty page: an empty page is a claim about the
tenant, and a refusal is a claim about the platform.

`metering/clickhouse.ts` carries **0 titled fences in either locale**, checked rather than
assumed, so the edit costs the fence chain nothing.

**Alternatives considered**: a hard-coded deadline inside the client (changes 4.7's job without
its consent), and a wrapper in the reader (cannot reach the `fetch` that is actually hanging).

---

## R16 — FOUR PREMISES THAT HELD, AND THE PASS THAT CHECKED THEM

Recorded because a premise that holds is only evidence once somebody has run it.

| premise | measured | result |
|---|---|---|
| Does `FINAL` deduplicate before or after `LIMIT`? | a two-part probe table | **Before.** raw 20 · `FINAL` 10 · `LIMIT 5` returns 5 with and without, so a short page still means the last page |
| Is `request_id` unique, or does the cursor need a third column? | the whole table | **11,683 rows, 11,683 distinct.** `(ts, request_id)` is a total order, and the duplicate R13 found was one request written twice rather than an id collision |
| Does `@Controller("v1/request-log")` serve `/v1/request-log`? | `main.ts` | **Yes** — no `setGlobalPrefix` |
| Can a merge-stop leak between lanes? | the two vitest configs | **Not in the coverage lane** (`fileParallelism: false`). The hazard is the api lane's `maxWorkers: 2`, which is where the duplicate test's `finally` earns its place |

---

## R17 — ABORTING A `fetch` DOES NOT STOP A QUERY, AND THE SERVER HALF IS FREE

**Measured.** A deliberately slow query with a server-side limit:

    SELECT count() FROM (SELECT number, sipHash64(toString(number)) h
                           FROM numbers(300000000) WHERE h % 7 = 0)
    SETTINGS max_execution_time = 1

    → Code: 159. DB::Exception: Timeout exceeded: elapsed 1000.760448 ms, maximum: 1000 ms
    → real 1.023s

R15 put an `AbortSignal.timeout` on the caller. That stops the api waiting; **ClickHouse keeps
executing**, so a tenant retrying a slow page accumulates server-side work — which is the
amplification a deadline is supposed to prevent, arriving one layer down.

`SETTINGS max_execution_time` is the other half and it **needs no interface change**:
`AnalyticalStore.query` takes a SQL string, and a `SETTINGS` clause is part of the statement.

**Decision**: both halves, with the **server limit shorter than the client's**, so the server's
refusal wins the race and the route receives `Code: 159` to map onto `analytics_unavailable`.
The other ordering yields an `AbortError` carrying nothing, and a refusal that names no cause
is the empty page FR-025 exists to prevent.

---

## R18 — THE REFUSAL NEEDS A REGISTERED CODE, AND A GATE COMPARES BOTH DIRECTIONS

**Read in the tree.** `ProtocolErrorFilter` maps a status onto a code from `ERROR_CODES`
(`packages/protocol/src/codes.ts`), and `relay-tutorial/scripts/check-error-codes.mjs` compares
that registry against `docs/08-error-reference.md` **both ways** — a code in the registry and
not the catalogue is red, and so is the reverse. The catalogue holds no 503 and no
service-unavailable entry.

`check:errors` is one of the eleven gates, so an omission here surfaces at phase 7 for work
that belongs in phase 3.

**Decision**: `analytics_unavailable`, added to both in phase 3. The name passes the test the
registry sets on itself — its own comments argue three refusals apart because *"a client acts
on them differently"* — and a client retries this one.

`codes.ts` carries **12 titled fences in each locale and is already a HEAD problem at line
209**, so the edit costs the fence chain nothing visible. That is the third file in this
feature with that property, after `app.module.ts` and `vitest.coverage.config.mts`.

---

## R19 — THE ROUTE COSTS THE TENANT A BUDGET AND RECORDS ITS OWN READS

**Measured in the tree**, two mechanisms nobody chose:

`services/api/src/limits/rate-limit.middleware.ts:79` —

    if (!path.startsWith(PUBLIC_PREFIX)) return [];
    if (method === "POST" && SEND_PATH.test(path)) return ["rest", "send"];
    return ["rest"];

**Every** path under `/v1` spends the REST budget. There is no route list to add to and no
exemption to grant, so this route is counted from the moment it exists.

And `services/api/src/request-log/request-log.middleware.ts:51` records on `res.on("finish")`
for every request including GETs, so **reading the log writes to the log** — each page adds a
row that appears in the next.

**Decisions**: the route stays counted, because an exemption list is a hand-maintained table
and feature 045 deleted one of those rather than correcting it. The self-recording question is
decided in phase 4 with the measurement beside it, on the same argument as `/internal/*`.

**And the loop is published rather than smoothed over**: a customer investigating 429s reads
their request log, the reads spend the budget they are investigating, and the log shows the
429s the reading caused.

---

## R20 — THE CLAUSE THAT GOVERNS WHEN THE LOG IS SEARCHABLE WAS CITED BY NOTHING

**Counted across all seven artifacts of this feature**, before this pass: `FR-ANL-04` **0**,
`60 second` **0**, `freshness` **0**.

The clause: *"Analytical events shall be available for query within 60 seconds of the
originating operation under normal conditions."* It is the one that decides what a customer
sees when they make a request and immediately read their log — the surface's most likely first
experience — and the chapter that builds the log had not named it.

**And in this stack the gap is not 60 seconds, it is unbounded.** `grep ingester
relay-platform/compose.yaml` returns **0**: nothing drains the queue unless an operator starts
a process by hand (`gaps.md` 050-8). Chapter 4.4's own suite over this table fails 5 of 5 at
5,001 ms each for the same reason.

**Decisions**: the contract states the guarantee and **computes no lag** — a per-response lag
needs a second query over the whole table and measures the ingester rather than the tenant. The
chapter measures the real figure once, with an ingester deliberately started, in the shape
chapter 4.5 used for `close -> row readable`.

**And the absence changed a task.** T039c planned to measure the log recording its own reads by
reading a page twice and publishing the difference. With nothing draining, that difference is
**zero**, and zero reads as *"the surface excludes its own reads"* rather than *"nothing filled
the table."* It has a positive control now.

---

## R21 — THE FILTER'S LADDER STOPS AT 404, AND THE STORE CLIENT DISCARDS THE ONE SIGNAL THAT HELPS

Two mechanics, both read in the tree, both changing how the 503 is built.

**`ProtocolErrorFilter`'s status ladder covers 400, 401, 403 and 404 and nothing else.** A 503
falls into the fallback, so registering `analytics_unavailable` in `ERROR_CODES` is necessary
and not sufficient — the code has to be **named on the thrown `HttpException`**, which the
filter supports and then **checks against the registry rather than trusting**, because "a
thrower can put any string in `code`". The same comment records that `docs_url` is derived from
the code, so an undocumented one ships a link to a page that cannot exist.

**And `createAnalyticalStore` keeps `text.trim().split("\n")[0]` and drops the HTTP status.**
Distinguishing a timeout from a malformed query therefore means string-matching `Code: 159` out
of a server message. The server already separates them:

    TIMEOUT_EXCEEDED      → HTTP 408
    unknown identifier    → HTTP 404

**Decision**: carry the status out of the client beside the message, map on the status, and keep
the message for the log and never for the response.

---

## R22 — THE ROUTE IS ATTACKED BY A SUITE THAT DERIVES ITS OWN TARGETS, AND NOTHING PLANNED FOR IT

**Read in the tree.** Constitution I's fourth bullet is a MUST: *"An automated cross-tenant
access test suite MUST attack every endpoint with foreign IDs on every build. A build that
fails this suite MUST NOT ship."*

`services/api/src/isolation/targets.ts` is that suite's classification list, and its own comment
is the mechanism:

> *"A LIST OF CLASSIFICATIONS, NOT A LIST OF TARGETS. The targets themselves are derived from
> the running application — `app.getHttpAdapter().getInstance().router.stack` — because the
> fault this suite exists to prevent is a route that exists and is unattacked … NOTHING MAY BE
> EXEMPT BY OMISSION. A derived target matching no entry fails the suite, and an entry matching
> no derived target fails it too."*

`targets.itest.ts:40` derives; `:71` collects the unclassified and fails. **So the suite turns
red the moment this controller is registered**, in the api lane, in phase 3.

Across all seven artifacts before this pass, every occurrence of "isolation" was about this
feature's own two-tenant assertion. None named the gauntlet, `targets.ts`, `deriveTargets` or
NFR-SEC-09 — and the plan's Principle I row read **PASS** through five analysis passes, marked
on the clause's first three bullets.

**Decision**: `{ method: "GET", path: "/v1/request-log", accepts: "application", shape: "list" }`.
`GET /v1/webhooks` at `targets.ts:134` is the precedent word for word — *"There is no identifier
in the path at all — the tenant comes from the key — so what the attack shows is that a key for
one environment sees none of another's endpoints in a 200."*

`targets.ts` carries 6 titled fences in each locale and is **already a HEAD problem at line
130**, so the edit is invisible to `check:fences` — the fourth such file in this feature.

---

## R23 — THIS API ALREADY HAS A PAGE ENVELOPE, AND THE FIRST DRAFT INVENTED A SECOND

**Read in the tree.** `services/api/src/messages/messages.service.ts:327`:

    Promise<{
      messages: MessageWithSender[];
      next_cursor: string | null;
      prev_cursor: string | null;
    }>

The array is named for the resource and there are **two** cursors. The first draft of this
chapter's contract returned `{ rows, next_cursor, window, retention_edge }` — `rows` is a
storage word, and it carried one cursor while copying `direction: older | newer` from the same
feature's query schema. **Two-way paging with one cursor leaves a caller reading `newer` with
no way back.**

And `repository.ts:3823` already states how the end of a page is known:

> *"ONE ROW MORE THAN ASKED FOR, which is how the caller learns whether there is a next page
> without a second count query. The extra row is dropped before returning and its predecessor
> becomes the cursor."*

**Decision**: `{ requests, next_cursor, prev_cursor, window, retention_edge }`, with the
`limit + 1` derivation named. The two extra fields are this surface's own and have no
counterpart to drift from.

**The pattern worth naming**: the query half of the convention was copied and the response half
was invented, from the same file, in the same task.


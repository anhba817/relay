# Contract — the request-log query surface (FR-ANL-07)

Written before the route. Chapter 4.2's lesson about `contracts/` is that it is the artifact
nothing else reads, so every claim here is one a test can drive.

---

## `GET /v1/request-log`

**Guard**: `CredentialGuard`. The principal must carry an `environmentId`; a `platform`
principal carries none by design and is refused rather than served an empty page (FR-011).

**Accepts**: **`application` only.** A request log is closer to configuration than to content,
which is the reasoning `WebhooksController` already carries: an end-user token on this route
would let any logged-in person in a customer's product read that customer's whole API history —
every endpoint they called, when, and what it answered. The tenant's software may read its own
log; a person signed into the tenant's product may not.

Decided in phase 2 rather than inherited, because there is no neutral option (below).

**And there is no neutral option.** `CredentialGuard` falls back to `EITHER` — application and
user both — when no `Accepts` decorator is present (`credential.guard.ts:92`). Leaving the
decorator off is the permissive choice made silently, which is the shape of defect this project
files against itself: a decision nobody wrote down, taken by a default.

### Query parameters

| name | type | default | bounds |
|---|---|---|---|
| `from` | ISO-8601 instant | `now - 24h` | inclusive; clamped to the retention edge |
| `to` | ISO-8601 instant | `now` | **exclusive** |
| `cursor` | opaque string | — | from a previous response's `next_cursor` |
| `direction` | `older` \| `newer` | `older` | |
| `limit` | integer | `50` | `1..200` |
| `endpoint` | route template, or `unmatched` | — | one of the templates the running router exposes, or `unmatched` for the request that matched none |
| `status` | integer | — | a valid HTTP status |

**`endpoint` also accepts the literal `unmatched`**, which maps to `endpoint IS NULL` — the
request that matched no route. The router contains no route for it, so a set derived from the
router alone cannot express it, and it is the query a 404 investigation opens the log for: 32
rows carry it today.

**And a route retired later becomes unfilterable before it expires.** The accepted set is
derived from the router as it is now; the log holds 30 days. Rows for a removed route are still
returned and can no longer be named. Deriving the set from the data instead would cover them and
costs a query per request; the window is stated here rather than discovered in a support ticket.

**`endpoint` is validated against the live router, not escaped.** `AnalyticalStore.query` takes
a SQL string and has no parameter binding, so this is the sharpest caller-supplied value the
surface handles. The platform already derives the route set —
`deriveTargets(app.getHttpAdapter().getInstance())`, the cross-tenant suite's own mechanism —
and a value from a closed derived set is not text reaching SQL. An unknown endpoint is a **400**,
not an empty page: the same distinction the retention edge draws between "nothing matched" and
"this question cannot be answered".

**Both filters exist because FR-DSH-03 asks for all three** — *"filterable by endpoint, status,
and time range"* — and EIR-DSH-02 permits the dashboard no other source than this API.

A value outside its bounds is **refused with 400**, not clamped — except `from`, which is
clamped to the retention edge and reported in `window`, because a caller asking for 90 days is
asking a reasonable question the data cannot answer.

### 200 response

```json
{
  "requests": [
    {
      "request_id": "…",
      "ts": "2026-09-16T01:02:03.456Z",
      "endpoint": "/v1/channels/:channelId/messages",
      "method": "POST",
      "status": 201,
      "latency_ms": 0.556
    }
  ],
  "next_cursor": "…",
  "prev_cursor": "…",
  "has_more": true,
  "window": { "from": "…", "to": "…" },
  "retention_edge": "…"
}
```

**The envelope matches the one this API already serves.** `messages.service.ts:327` returns
`{ messages, next_cursor, prev_cursor }` — the array named for the resource, and **two**
cursors. A first draft of this contract called the array `rows`, which is a storage word, and
carried `next_cursor` alone while copying `direction: older | newer` from the same schema —
**two-way paging with one cursor, so a caller reading `newer` had no way back.**

- `requests` holds at most `limit` entries, in `direction` order.
- `endpoint` is **null** for an unmatched route — 22 rows in the lane today. Null, not `""`:
  chapter 4.4 paid for the difference between an absent field and an empty one.
  **And the transport cannot carry that distinction on its own.** The store client returns
  `string[][]` split from a TSV body, and ClickHouse writes NULL as the two characters `\N` —
  asked of the server directly:

  ```text
  \N<TAB>GET<TAB>200
  ```

  So the statement selects `endpoint IS NULL` as a column of its own and the presence column
  decides, exactly as chapter 4.7 put `count()` in front of a bare aggregate to tell "holds
  nothing" from "holds zero". A reader that translated the string `\N` would work today and
  break the first time a column can legitimately contain it.

  **This applies to every nullable column the surface returns, not to `endpoint` alone.**
  `system.columns` lists three on this table — `environment_id`, `endpoint` and
  `limited_operation` — and the last is the one chapter 4.4 added so a 429 says which quota
  class it refused on.
- `latency_ms` is fractional. Rounding it to an integer would read `0` for three of four real
  requests (4.4, measured).
- `next_cursor` and `prev_cursor` are null at the respective ends.
- **`has_more` is required by EIR-API-06** — *"List endpoints shall use opaque cursor pagination
  with `limit` and `cursor` parameters, returning `next_cursor` and `has_more`."* It reports the
  direction the query ran, which is the only well-defined reading once `direction` is two-way,
  and the `limit + 1` fetch below already computes it.
  **`grep has_more` over the platform returns nothing**: `messages.service.ts` has not carried it
  since chapter 2.4, so this is the first list endpoint to conform. It is added rather than
  amended away, and the precedent settles which: EIR-API-04's worked example was brought to the
  code in SRS 1.3 **because changing the shape would have been breaking under CON-05's
  URL-versioning rule**. Adding a field is not breaking, so that argument does not reach here.
- **The last page is known by asking for one row more than `limit` and dropping it**, which is
  the convention `repository.ts:3823` already states: *"ONE ROW MORE THAN ASKED FOR, which is
  how the caller learns whether there is a next page without a second count query. The extra
  row is dropped before returning and its predecessor becomes the cursor."* Without it, a page
  that exactly exhausts the window claims a next page that turns out empty.
- `retention_edge` is **the nominal guarantee, `now() - 30 days`**, and it is nominal on
  purpose. A window older than it returns no rows **because the data is gone**, and this field
  is how a caller tells that apart from a quiet period (R8). It is not the oldest surviving
  row: the TTL is a schedule rather than an event — chapter 4.2 measured 121 days and 146,582
  expired rows still present straight after a load — so rows older than this instant can exist
  for a while. **A caller needs the promise, not the leftovers.** Answering with the oldest
  surviving row would hand them a number that moves when a merge runs and that they must not
  build on.

### Refusals

| status | when |
|---|---|
| 400 | `limit` out of bounds, `to` before `from`, malformed `cursor`, unparseable instant |
| 401 | no credential |
| 403 | a credential whose principal carries no `environmentId` |
| 503 `analytics_unavailable` | **the analytical store did not answer within the deadline.** The API is up and this surface is not, which is the distinction constitution III's second clause turns on — and it is why the refusal is explicit rather than an empty page. An empty page would say the tenant made no requests, a claim about them rather than about the platform |

The body carries the five fields **EIR-API-04** names, top-level and not nested: `code`,
`message`, `docs_url`, `request_id`, and `field` where one applies. `ProtocolErrorFilter`
already assembles exactly that — `docs_url: docsUrl(code)` and
`request_id: String(res.getHeader("X-Request-Id") ?? "")` — so the route's work is to throw
with the code named, and the test's work is to assert the five rather than the status alone.

The 503 carries the code **`analytics_unavailable`**, registered in `ERROR_CODES`
(`packages/protocol/src/codes.ts`) and documented in `docs/08-error-reference.md`, because
`scripts/check-error-codes.mjs` compares those two in both directions and a code in one and
not the other is a red gate. The name says what a client does about it — retry — where a bare
`internal_error` would say nothing and `unauthorized` would say something false.

**The body names the subsystem and never the store's answer.** `Code: 159 … elapsed
1000.760448 ms` is infrastructure detail, and a refusal that carries it puts a ClickHouse
error string into a customer's support ticket. That is the argument `codes.ts` already makes
about credentials, one subsystem over.

**The deadline is the route's, not the client's.** Neither ClickHouse client in this repository
sets a timeout — both call `fetch` with no `signal` — which is tolerable for chapter 4.7's
batch reconciler and is not for a customer request: an unbounded read holds a worker until the
operating system gives up, and *"failure or backlog of the analytical pipeline MUST NOT affect
… API availability"* is a MUST. `services/dispatcher/src/deliver.ts` already carries the
pattern with `AbortSignal.timeout(timeoutMs)` on the webhook POST.

**AND IT HAS TWO HALVES, BECAUSE ABORTING A `fetch` DOES NOT STOP A QUERY.** The client stops
waiting; ClickHouse keeps executing, so a tenant retrying a slow page accumulates server-side
work — the amplification the deadline exists to prevent. The second half rides in the SQL and
needs no interface change:

```text
SETTINGS max_execution_time = N
→ Code: 159. DB::Exception: Timeout exceeded: elapsed 1000.760448 ms, maximum: 1000 ms
```

The **server limit is set shorter than the client's**, so the server's refusal wins the race
and the route receives a code it can map. The other ordering yields an `AbortError` carrying
nothing, and a refusal that names no cause is the empty page this contract refuses to send.

### What this log cannot answer

It records **no user and no channel**. The producer stores `principal_kind` — `application`,
`user`, `platform`, `none` — which says what kind of caller made the request and never which
one. So the surface answers *"what did this tenant call, and what happened"*, and it cannot
answer *"what happened to this user"*.

That second question is the one `docs/03-journey-map.md`'s Stage 8 names as the opportunity —
*"per-user and per-channel message tracing for support investigations"*, against a pain point
of *"no way to trace a specific user's reported problem."* FR-ANL-07's six fields never asked
for it, so no clause is broken; a motivating document names a capability no requirement carried.
Closing it needs a column, a producer change and the tenancy argument chapter 4.4 settled by
recording a kind instead of an identity.

### How recent the answer is

**A request made now is not in the log now.** Records reach `api_requests` through a durable
queue and the ingester, and FR-ANL-04 allows *"within 60 seconds of the originating operation
under normal conditions."* So a caller who sends a request and immediately reads their log
finds nothing, and the correct conclusion is "not yet" rather than "never happened".

The surface states the guarantee and **does not compute a lag**. A per-response lag would need
a second query over the whole table on every page, and it would measure the ingester rather
than the tenant — a number that moves for reasons the caller cannot act on.

**And in the development stack there is no ingester at all.** `compose.yaml` runs none
(`gaps.md` 050-8), so the log does not update until somebody starts one. A reader following
this chapter meets an empty log before they meet a wrong one, which the chapter says out loud.

### What it costs the tenant, and what it records about itself

**Reading the log spends the tenant's REST budget.** `operationsFor` returns `["rest"]` for
every path under `/v1` — there is no route list and no exemption — so this route is counted
from the moment it exists. It stays counted: an exemption list is a hand-maintained table, and
feature 045 deleted one of those rather than correcting it after two hand-allocated port bands
turned out to contain services the lane itself runs.

The consequence is worth stating rather than hiding: **a customer investigating 429s reads
their request log, the reads spend the budget they are investigating, and the log then shows
the 429s the reading caused.**

**And reading the log writes to the log.** `RequestLogMiddleware` records on `res.on("finish")`
for every request including GETs, so each page adds a row that appears in the next one. Whether
the surface excludes its own route is decided in phase 4 with the same argument the
`/internal/*` decision gets — excluding makes the log incomplete against FR-ANL-01's *"every
request"*, and including means a reader sees their own reads.

### What the surface never returns

- Request or response bodies. FR-ANL-07 forbids it and the producer never recorded them, so
  the guarantee is a property of the stored columns rather than of a filter (FR-004).
- Another tenant's rows, under any input (constitution I).
- Rows with no tenant — 60.5% of the log. They are not withheld from a particular caller; they
  are unreachable from every tenant's query, because they carry no tenant to match.

### What it does with `/internal/*`

**They are returned.** 1,656 of a tenant's 4,621 attributed rows are the platform calling itself
on that tenant's behalf, with the end user's principal — `/internal/session` alone is 1,423 —
so a customer's own log opens on calls their software did not make.

Three arguments, and the third is the one that decides it:

1. **Hiding them makes the log incomplete** against FR-ANL-01's *"every request"*. The rows
   carry the tenant's environment id because the work was done for that tenant; dropping them
   is a claim that the work did not happen.
2. **Hiding them needs a prefix rule**, which is a hand-maintained table that **fails open**: a
   new internal prefix is returned by default, and this project deleted a nine-row port map
   rather than correct one of those (feature 045).
3. **The caller can already exclude them, and the platform cannot un-hide them.** The
   `endpoint` filter exists on this surface, so a customer who wants only their own calls asks
   for the endpoint they called. A platform that hides rows offers no way back.

What this costs is real and is stated rather than glossed: **the busiest entry in a tenant's
log is a route they have never heard of**, and the chapter says so.

---

## Deduplication, and why every read carries `FINAL`

`api_requests` is a **`ReplacingMergeTree`** keyed `(environment_id, ts, request_id)`. Chapter
4.4 chose that engine for a reason this surface inherits: a redelivered batch writes the same
request twice, and chapter 4.5 measured `ingestOnce` reporting 16 for a stream holding 8.

Measured on the lane before this contract was written: **11,684 rows against 11,683 distinct
keys — one duplicate, across two active parts.** A read without `FINAL` returns it twice, so a
page can repeat a request and the repeat disappears whenever a merge happens to run.

So the read contract is `FINAL`, and it is the same rule chapter 4.6 wrote for the other
engine: there `sum()` with `GROUP BY`, here `FINAL`, and in both cases **a query whose
correctness depends on somebody having run `OPTIMIZE` is right in a demo and wrong in
production.**

What it costs is a function of the number of parts, and the chapter measures it against a table
that has some.

---

## Ordering, and why the cursor is composite

The platform's other cursor stands on `(channel_id, sequence)`, a server-assigned strictly
increasing number that constitution II requires message ordering to use. **`api_requests` has
no such column.** Its key is `(environment_id, ts, request_id)`, and `ts` is
`DateTime64(3)` — 43 `(environment_id, ts)` pairs in the lane hold more than one row, 91 rows
in total, worst case 3.

So the cursor encodes `(ts, request_id)` and the comparison is lexicographic on the pair. A
`ts`-only cursor skips or repeats 0.78% of rows today, and that share grows with request rate
rather than with elapsed time.

---

## What this contract does not cover

- **FR-ANL-10's percentiles.** They are not a page of this log and they do not share its route.
  Phase 5 decides whether they exist at all.
- **Aggregation.** No counts, no group-by, no facets. FR-ANL-07 asks for a queryable log;
  a dashboard is a different chapter, and `docs/12` does not name one here.

# Contract — the request-log query surface (FR-ANL-07)

Written before the route. Chapter 4.2's lesson about `contracts/` is that it is the artifact
nothing else reads, so every claim here is one a test can drive.

---

## `GET /v1/request-log`

**Guard**: `CredentialGuard`. The principal must carry an `environmentId`; a `platform`
principal carries none by design and is refused rather than served an empty page (FR-011).

**Accepts**: decided in phase 3 and stated here with its argument. A request log is closer to
configuration than to content, which argues for `application` only — the same reasoning
`WebhooksController` carries: an end-user token on this route would let any logged-in person in
a customer's product read that customer's whole API history.

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

A value outside its bounds is **refused with 400**, not clamped — except `from`, which is
clamped to the retention edge and reported in `window`, because a caller asking for 90 days is
asking a reasonable question the data cannot answer.

### 200 response

```json
{
  "rows": [
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
  "window": { "from": "…", "to": "…" },
  "retention_edge": "…"
}
```

- `rows` holds at most `limit` entries, in `direction` order.
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
- `next_cursor` is null on the last page.
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
| 503 | **the analytical store did not answer within the deadline.** The API is up and this surface is not, which is the distinction constitution III's second clause turns on — and it is why the refusal is explicit rather than an empty page. An empty page would say the tenant made no requests, a claim about them rather than about the platform |

**The deadline is the route's, not the client's.** Neither ClickHouse client in this repository
sets a timeout — both call `fetch` with no `signal` — which is tolerable for chapter 4.7's
batch reconciler and is not for a customer request: an unbounded read holds a worker until the
operating system gives up, and *"failure or backlog of the analytical pipeline MUST NOT affect
… API availability"* is a MUST. `services/dispatcher/src/deliver.ts` already carries the
pattern with `AbortSignal.timeout(timeoutMs)` on the webhook POST.

### What the surface never returns

- Request or response bodies. FR-ANL-07 forbids it and the producer never recorded them, so
  the guarantee is a property of the stored columns rather than of a filter (FR-004).
- Another tenant's rows, under any input (constitution I).
- Rows with no tenant — 60.5% of the log. They are not withheld from a particular caller; they
  are unreachable from every tenant's query, because they carry no tenant to match.

### What it does with `/internal/*`

**Decided in phase 4 and stated here.** 1,656 of a tenant's 4,621 attributed rows are the
platform calling itself on that tenant's behalf, with the end user's principal —
`/internal/session` alone is 1,423. Whichever way the decision goes, it is asserted by a test,
and this section carries the argument rather than the outcome alone.

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

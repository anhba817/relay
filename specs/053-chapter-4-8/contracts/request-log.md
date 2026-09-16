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
- `latency_ms` is fractional. Rounding it to an integer would read `0` for three of four real
  requests (4.4, measured).
- `next_cursor` is null on the last page.
- `retention_edge` is the oldest instant the log can answer for. A window older than it returns
  no rows **because the data is gone**, and this field is how a caller tells that apart from a
  quiet period (R8).

### Refusals

| status | when |
|---|---|
| 400 | `limit` out of bounds, `to` before `from`, malformed `cursor`, unparseable instant |
| 401 | no credential |
| 403 | a credential whose principal carries no `environmentId` |

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

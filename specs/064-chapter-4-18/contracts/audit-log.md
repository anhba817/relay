# Contract — `GET /v1/audit-log`, and what an entry looks like from outside

Modelled on `GET /v1/request-log` (chapter 4.8), which is the closest thing the platform
already serves. Where this contract differs from that one, it says why.

## The route

| | |
|---|---|
| method and path | `GET /v1/audit-log` |
| credential | **application only** — `@Accepts("application")`, as the request log |
| a principal with no environment | **403 `forbidden`**, not an empty page |
| ordering | newest first |

**403 RATHER THAN AN EMPTY PAGE, AND THE REASON IS CHAPTER 4.8's.** A platform principal
carries `environmentId?: undefined` by design, and that route's comment says it exactly:
*"answering it with `[]` would say that a tenant made no requests when there is no tenant in
the question at all."* An audit log answering `[]` would say that nobody moderated anything,
which is a worse sentence to be wrong about.

**Application only, and a user token is refused** — the same shape as `UsersController`, whose
class-level `@Accepts("application")` carries the reason: these are routes where *the tenant
acts on something it names*, and a user token on them would be a different route shape the SRS
does not ask for. A tenant's moderation history is the tenant's.

## Query parameters

| name | type | default | notes |
|---|---|---|---|
| `from` | timestamp | — | inclusive lower bound on `occurred_at` |
| `to` | timestamp | — | exclusive upper bound |
| `action` | enum | all | **validated against the set as the router serves it now**, not against a list frozen at import time |
| `limit` | integer | 50 | **min 1, max 200**, matching the request log's `z.coerce.number().int().min(1).max(200).default(50)`. A value outside it is a 400 naming the field |
| `cursor` | opaque | — | keyset on the **pair** `(occurred_at, id)`, compared as a row value — see below |

**AND THE ENUM ADMITS WHAT THE COLUMN HOLDS, NOT ONLY WHAT THE SET CURRENTLY CLASSIFIES.** A
route reclassified from `moderation` to `not-moderation` — which rows 20, 21 and 22 may do —
leaves entries carrying an action the current set no longer names, and a filter built from the
set alone would refuse a value that exists in the data. **So an action, once recorded, stays in
the vocabulary.** Chapter 4.8 met the same shape from the other side: *"the repair that made it
safe removed the most diagnostic question it could ask"*, and its answer was to keep
`unmatched` as a member of the set rather than let the filter be narrower than the table.

**THE `action` ENUM IS BUILT PER REQUEST FROM THE INJECTED SET.** Chapter 4.8 built its
`endpoint` filter the same way and the reason transfers exactly: a filter whose vocabulary is
frozen at import time drifts from the router that produces the values, and the drift is silent
in the direction that matters — a real action becomes unfilterable. `buildRequestLogQuerySchema(this.endpoints.get())`
is the shape to copy.

**THE CURSOR IS A PAIR, AND THE PRECEDENT IS WHY.** `occurred_at` is not unique, and
`request-log/reader.ts` carries the measurement that settles it — *"42 `(environment_id, ts)`
pairs in this lane hold more than one row; a `ts`-only comparison skips or repeats all 89 of
them."* The comparison is `(occurred_at, id) < (…, …)` as a row value and the index carries
`id` as its third column so the planner can use it.

**And a filter's promise is that nothing else comes back.** Chapter 4.8's finding, in as many
words: *what a filter promises is that nothing ELSE comes back; the count of what does is the
plant's business.* The tests assert the complement, not the cardinality.

## The response

```json
{
  "entries": [
    {
      "id": "…",
      "occurred_at": "2026-10-02T09:14:22.013Z",
      "actor": { "kind": "application", "id": "key_…" },
      "action": "POST /v1/users/:externalId/ban",
      "target": { "kind": "user", "id": "ana" },
      "request_id": "…"
    }
  ],
  "next_cursor": null,
  "prev_cursor": null,
  "has_more": false,
  "window": { "from": "…", "to": "…" }
}
```

**`has_more` IS REQUIRED BY A PUBLISHED CLAUSE AND AN EARLIER DRAFT OF THIS CONTRACT OMITTED
IT.** EIR-API-06: *"List endpoints shall use opaque cursor pagination with `limit` and `cursor`
parameters, returning `next_cursor` and `has_more`."* The route this contract says it is
modelled on is the one that fixed the platform's long-standing omission, and its comment says
so:

> EIR-API-06 REQUIRES IT AND THIS PLATFORM HAS NEVER HAD IT. `grep has_more` over `services/`
> and `packages/` returns nothing: `messages.service.ts` has been non-conforming since chapter
> 2.4. **Added here rather than the clause amended away** — EIR-API-04's worked example was
> brought to the code because reshaping an error body would have been breaking under CON-05's
> URL-versioning rule, and ADDING a field is not, so that escape does not reach this one.

Shipping a second list endpoint without it would have joined `messages.service.ts` on that
list while citing the chapter that left it.

**`prev_cursor` and `window` come from the same place.** A caller that arrived holding a cursor
cannot otherwise know it can go back, and a caller that sent no `from`/`to` cannot otherwise
know what window it was given.

**AND `retention_edge` IS DELIBERATELY NOT HERE**, which is the one field of the precedent's
envelope this route drops. The request log publishes it because its table has a 30-day TTL and
a caller needs to know where the data stops. **Nothing prunes this table** (research R7), so the
field would publish a boundary that does not exist — and an audit log announcing a retention
edge it does not enforce is a worse sentence than no field at all.

**`entries`, and the key is load-bearing.** The history route's array is keyed `messages` and
chapter 4.17's research spent a probe on assuming otherwise — a defaulting accessor over the
wrong key turned a present attachment into what looked like history dropping it. The key is
named here so the chapter's own tests and its quickstart cannot disagree about it.

**`actor.id` is nullable and the client must handle it.** A platform principal has no actor id
(data-model §3). No `/internal/` route is in the set, so a `null` should not occur in a
tenant's page today — and *should not occur* is not *cannot*, so the contract says the field is
nullable rather than letting the first occurrence be a client's crash.

## No deadline, and that is a decision rather than an omission

**ADR-26 is the chapter that put a customer-facing log route on the request path**, and its
problem statement is *"This chapter puts it on the request path, with a person waiting."* Its
answer was a limit on both sides — `SERVER_DEADLINE_SECONDS = 2` in the client and
`SETTINGS max_execution_time` in the query — after measuring that **aborting a `fetch` stops
the client waiting and ClickHouse keeps executing**, so a tenant retrying a slow page
accumulates server-side work.

This route sets none, and the reason is that the thing ADR-26 was defending against cannot
arise here. The read is a keyset page of at most 200 rows on
`(environment_id, occurred_at DESC, id DESC)`, which is a bounded index range rather than a
scan — there is no query shape a caller can ask for that costs more than the page. And Postgres
is the operational store: constitution III's *"failure or backlog of the analytical pipeline
MUST NOT affect … API availability"* is about a dependency this route does not have.

**If T032a's measurement finds the planner doing anything other than an index range, this
paragraph is wrong and `statement_timeout` is the answer.** It is written here so the next
reader knows the question was asked rather than skipped.

## Refusals

| condition | status | code |
|---|---|---|
| no environment on the principal | 403 | `forbidden` |
| a user token | 403 | the credential guard's existing refusal |
| `limit` outside the bound | 400 | names the field |
| an `action` not in the set | 400 | names the field |
| a malformed cursor | 400 | names the field |

**A malformed cursor is a 400 here and the head of the queue on the worker's internal route**,
and the difference is deliberate: that route's only caller builds the value from a previous
response, so a bad one is a bug and starting over loses nothing. This route's caller is a
customer, and silently answering a different question than the one asked is worse than
refusing.

**And a malformed path parameter is a caller-triggered 500 on sixteen shipped routes**
(`gaps.md` 058-3, still open). This route takes no path parameter, which is the cheap way to
not join that list.

## What this contract does not offer

- **No write route.** An entry is a consequence of an action, never a request. There is no
  `POST /v1/audit-log` and there will not be one: a log a client can write to records what the
  client says happened.
- **No `DELETE`, no `PATCH`.** Refused by the database, not by the absence of a route — FR-004
  is demonstrated by attempting the write at the storage layer, because a route that does not
  exist proves nothing about a table.
- **No cross-tenant read**, by any parameter. The scope is the principal's environment and
  there is no parameter that names an environment, which is the same shape the media
  worker's own route takes: *a route that could be asked for one tenant's objects would be a
  route worth forging.*

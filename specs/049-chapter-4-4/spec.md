# Feature Specification: chapter 4.4 — every request is an event

**Feature**: `specs/049-chapter-4-4/` · **Part 4, movement III, chapter 4 of 22**
**Created**: 2026-09-14
**Status**: specified

## Where this ordinal comes from

`docs/12-part-4-structure.md` §3's table keeps the original 23-chapter ordinals in its first
column and records two contractions on top of them. The movement map at the head of that
section is the amended address: **movement III is chapters 4–5**, so the table's original
ordinal 5 — *"Every request is an event"* — is chapter **4.4**, and original 6, *"The
gateway's first stream"*, is 4.5. 048's own out-of-scope section names it in as many words:
*"API request events (movement III, chapter 4)."*

The title above is §3's, and it is provisional. 4.2 shipped as *the store that was never
listening* against a provisional *ClickHouse from zero*; the published title is drafting's
to choose.

## A finding about the grooming record itself

**§4's cross-references are one ahead of §3's, and §4 is the section that tells a chapter
what it must not re-teach.** Checked against §3's table:

| §4 says | §3's table holds at that ordinal | the chapter §4 means |
|---|---|---|
| the analytics grammar is generalised by **ch 6, 7** | gateway stream, metering | **5, 6** — this chapter and the gateway's |
| the outbox is contrasted by **ch 6** | gateway stream | **5** — this chapter |
| monthly quota counters are reconciled by **ch 9** | the customer-searchable log | **8** — the reconciler |
| the four refusals are **ch 12's** | the refused union arm | **11** — the upload |
| the union arm is filled by **ch 13** | signed delivery | **12** |

Five references, all +1, and they fit the interim 24-chapter numbering that existed for a day
while movement I was two chapters. §7's references (ch 6, 14, 15, 20) match §3's table and are
not affected. **So a writer following §4 literally concludes that this chapter is not the one
that generalises 3.20's pattern** — which is the one thing §4 exists to tell them.

This is the shape CLAUDE.md files under *artifacts that agree with each other and not with the
tree*, one level out: two sections of one document, renumbered on different days. Amending §4
is a task in this feature.

## The premise, run rather than assumed

Three claims this chapter rests on, each checked against the tree at `part4-ch3` rather than
carried from a document.

### 1. The consumer built last chapter will destroy what this chapter publishes

`services/ingester/src/main.ts:128` creates its durable with
`filter_subject: ALL_ANALYTICS_SUBJECT` — `analytics.>`, the widest filter the grammar
admits. Every record on the stream reaches it. `shape()` then requires
`delivery_id`, `endpoint_id`, `event_id`, `attempt`, `latency_ms`, `outcome`,
`environment_id` and `attempted_at`, and returns `null` if any is absent. An API request
record carries none of the first five.

`null` is not a retry. `main.ts:99–102`:

```
malformed += 1;
logger.log("error", "ingester.malformed_record", { stream_sequence: m.seq });
m.term();
```

**`term()` means never redeliver.** So the first API request record published onto
`ANALYTICS` is logged at `error` and permanently dropped — and because the api serves
requests continuously, that is one error line and one destroyed record per request.

The protocol package anticipated a grammar change and predicted the wrong direction of the
failure. `internal.ts:244`: *"a consumer that assembles its own subject filter receives
nothing the day the grammar changes — no error, no warning, just an empty stream position."*
The ingester did not assemble a narrow filter; it took the widest one. The failure is not an
empty position. It is a termination.

### 2. The subject grammar cannot express a request with no tenant, and refuses to try

`analyticsSubjectFor` (`packages/protocol/src/internal.ts:275`) validates the environment id
against a UUID pattern and throws `"an environment id must be a uuid"` at line 283 otherwise. The comment
argues why, and the argument is sound: an environment id becomes a dot-delimited subject
token, so a value carrying `.`, `*` or `>` puts one tenant's records where another tenant's
filter reaches them. Constitution I as a parsing problem.

It also means there is no subject for a request that has no environment.

### 3. The requests with no environment are not the edge case — they include the busiest routes

`services/api/src/auth/principal.ts` defines three principal kinds. Two carry an
`environmentId`. The third does not, and its absence is load-bearing:

```
export interface PlatformPrincipal {
  kind: "platform";
  service: string;
  /** Present and always undefined, so the environment-scoped providers that read
   *  `principal?.environmentId` keep compiling AND keep getting nothing. */
  environmentId?: undefined;
}
```

The file states the reason: an `application` principal is scoped to exactly one environment,
so minting the dispatcher an API key would either stop it serving other tenants or grant it
cross-tenant reach through the credential type whose entire meaning is that it has none.
*"That is not an omission — it is what stops it being usable anywhere a tenant is expected."*

`@Accepts({ platform: [...] })` appears on `internal/dispatch.controller.ts` and
`internal/usage.controller.ts`. Those are the fan-out expand, the delivery material, the
outcome, the replay, and the gateway's connection-minute reporting — **the routes the
platform calls on every message and every connection**, rather than the ones a customer calls
by hand. `RequestWithPrincipal.principal` is additionally optional at the type level, because
signup and `/healthz` are reached with no credential at all.

So FR-ANL-01's *"an analytical event for every API request"* and FR-ANL-07's *"per tenant"*
do not describe the same population, and the gap is widest exactly where the traffic is.

**The share belongs to the chapter, measured at its own tag, not to this document.** The
static inventory is 41 route decorators across 13 controllers; what matters is the share of
*requests*, which needs the lane running.

## FR-ANL-07 asks for something two other clauses forbid

FR-ANL-07 records *"request ID, timestamp, endpoint, method, status, latency, and truncated
payload."*

- **FR-ANL-11**: *"Analytical records containing message content shall store only length and
  metadata, never message text."*
- **Constitution VI**: secrets, tokens and message content never in logs.

`POST /v1/channels/:channelId/messages` has a request body whose whole content is message
text. A truncated payload is still message text, and truncation makes it worse rather than
better: it keeps the beginning, which is the part a person wrote.

Three clauses, one of which cannot hold as written. The precedent is FR-RTM-09, FR-RTM-10 and
043's own FR-016: **when measurement falsifies a clause, amend the clause.** This chapter
amends one of them rather than diverging from it in silence.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every API request leaves a record (Priority: P1)

An operator wants to know what a tenant's integration actually sent: which endpoints, how
often, how fast, and with what status. Today the only trace is one log line per request that
nothing retains and nothing can aggregate.

**Why this priority**: it is FR-ANL-07's producer and the chapter's reason to exist.

**Independent test**: issue a known set of requests across authenticated and unauthenticated
routes, then count records in the analytical store against the number of requests served.

### User Story 2 - The analytics path never costs a response (Priority: P1)

A tenant's requests are served at the same latency and with the same status whether the
broker is healthy, slow, or stopped.

**Why this priority**: constitution III and FR-ANL-03 state it, and this is the first
producer on the *request* path rather than beside it. 3.20's publisher runs after a webhook
outcome has committed, where a delay costs a background job. A publish on the request path
costs a customer.

**Independent test**: measure request latency with the broker healthy and with it stopped,
and publish both distributions.

### User Story 3 - A request that belongs to no tenant is still recorded (Priority: P2)

The dispatcher's calls to the internal seam, the gateway's usage reports, signup and
`/healthz` produce records that can be queried without being visible to, or confusable with,
any tenant's.

**Why this priority**: without it FR-ANL-01's "every" is false for the highest-volume routes,
and the alternative — inventing an environment id for them — is a tenancy violation wearing a
convenience.

**Independent test**: call an internal-seam route and a tenant route, then show that a
tenant-scoped query returns the second and not the first.

### User Story 4 - The ingester stops destroying what it does not recognise (Priority: P2)

A record of a type the ingester does not write is not terminated.

**Why this priority**: it is a defect this chapter would otherwise ship, and it is not
hypothetical — premise 1 measures it.

**Independent test**: publish a well-formed record of an unknown type and show that it is
neither written as an attempt nor terminated.

### Edge Cases

- A request whose principal is resolved *after* the record's fields are captured — the
  middleware chain is `RequestContext → Authenticate → RateLimit`, and the record is assembled
  on `finish`, so the principal exists by then. This is a premise to run, not an assumption.
- A request refused by `AuthenticateMiddleware`'s allowance before any handler runs — served
  as a **429 by `RateLimitMiddleware`, which does not call `next()`**. A producer registered
  after it in the chain never runs, so this edge case is not about the record's contents but
  about whether the record exists at all. It decides where in the chain the producer goes.
- A request whose route did not match any controller — a 404 has a method and a status but no
  route template.
- A request that is still open when the process shuts down. No response finished, so no
  record; the chapter says so rather than implying completeness.
- `/healthz`, polled every few seconds by the container runtime for the life of the stack.
- A response that fails mid-stream: `finish` fires, `close` may not.
- The broker refusing the publish because the stream does not exist — the 503 the webhook
  dispatcher chapter met.

---

## Requirements *(mandatory)*

### Functional Requirements

**The producer**

- **FR-001**: The api shall emit one analytical record per API request whose response
  completed, carrying request id, timestamp, endpoint, method, status and latency
  (FR-ANL-01, FR-ANL-07).
- **FR-002**: The record shall be assembled by naming every field individually. A spread of
  any request, response, principal or header object is refused — the allow-list fails closed
  when a field is added, a spread fails open (NFR-SEC-06, and 3.20's `shape()` made the same
  argument).
- **FR-003**: The publish shall not be awaited on the request path, and its failure shall not
  change the response's status, body, headers or latency (FR-ANL-02, FR-ANL-03, constitution
  III).
- **FR-004**: A publish failure shall be recorded once and shall not be retried on the
  request path.
- **FR-005**: `endpoint` shall be the matched route template, not the request's path. A raw
  path carries channel ids, message ids and user external ids — customer data at unbounded
  cardinality — and FR-ANL-07's word is "endpoint".
- **FR-005a**: A request refused before the router runs shall still be attributable to an
  endpoint where the refusing layer already knows which one it matched. The rate limiter
  resolves the request to a logical operation before it decides; that resolution shall be
  recorded rather than recomputed.
- **FR-005b**: The record shall state **which layer decided the response** — handler, guard,
  middleware, or no match. Without it the api's two sources of 429 are one undifferentiated
  population, and only one of the two can carry an endpoint.
- **FR-006**: No request body, response body, header value or credential shall appear in the
  record (FR-ANL-11, constitution VI, NFR-SEC-06). **This contradicts FR-ANL-07's "truncated
  payload" as written; FR-018 governs.**
- **FR-007**: Latency shall be measured over an interval the chapter names, with the start
  and end points stated rather than implied.

**Tenancy**

- **FR-008**: A request that resolves to an environment shall produce a record attributed to
  it, and to no other (constitution I).
- **FR-009**: A request that resolves to no environment shall still produce a record. This
  covers an absent principal and a `platform` principal, whose `environmentId` is undefined
  by design.
- **FR-010**: A tenantless record shall not be reachable by any tenant-scoped filter or
  query, and no value shall be invented to stand in for the missing environment — not the
  zero UUID, not an empty string, not a sentinel tenant. 047 measured what a zero UUID does
  to a `uniqExact`: one phantom active user per environment.
- **FR-011**: The subject grammar shall express the tenantless case without weakening
  `analyticsSubjectFor`'s UUID refusal, which exists because a subject token containing `.`,
  `*` or `>` crosses tenants.

**The stream and the consumer**

- **FR-012**: The ingester shall distinguish record types and shall not terminate a
  well-formed record of a type it does not write.
- **FR-013**: An API request record shall be written to the analytical store, and the choice
  between extending `analytics-ingester` and adding a second consumer shall be argued rather
  than assumed.
- **FR-014**: The effect of a second, higher-volume producer on a stream shared with
  webhook attempts shall be measured, not asserted. `ANALYTICS` is one stream at
  `max_bytes` 1 GiB with `discard: old` and seven-day retention, sized when its only
  producer was one record per webhook attempt. Under `discard: old` a louder producer
  evicts a quieter one's records **before the ingester reads them, with no error on either
  side**.

**The store**

- **FR-015**: A new analytical table shall hold API request records, applied through 4.2's
  `analytics/apply.mjs` ledger.
- **FR-016**: Its retention shall be **30 days** (FR-ANL-07), not the 90 of
  `webhook_attempts`. Two retentions is the reason it is a second table rather than a column
  on the first.
- **FR-017**: A redelivered record shall not become a second row, by the same mechanism 4.3
  established — the record's own key in the sorting order, not a token derived from a batch.

**The clauses**

- **FR-018**: The conflict between FR-ANL-07's "truncated payload" and FR-ANL-11 /
  constitution VI shall be resolved by amending the SRS, with the revision history entry the
  governance clause requires. Silent divergence is refused.
- **FR-019**: `docs/12-part-4-structure.md` §4's five stale cross-references shall be
  corrected against §3's table.
- **FR-020**: Where a published document is falsified by a measurement in this chapter, it
  shall be amended in the same feature — the SAD's analytical section included.

**The chapter**

- **FR-021**: The chapter shall generalise chapter 3.20's fire-and-forget argument rather
  than re-derive it (`docs/12` §4). A chapter that re-teaches it has not read Part 3.
- **FR-022**: Prose shall stay inside the 2,000–4,000 word bound measured outside code
  fences, or split.
- **FR-023**: `pnpm check:fences` shall be reported as a delta against an opening measured in
  this feature, broken down by kind and locale — APPLY and HEAD, `(en)` and `(vi)` — because
  the Vietnamese chain is under active translation and moves for reasons no chapter caused.

### Key Entities

- **API request record** — request id, timestamp, route template, method, status, latency,
  and an environment when one exists. Its natural broker deduplication key is the request id,
  which `newRequestId()` already mints as a UUID per request.
- **The tenantless record** — the same shape with no environment. Not a defect, not a
  fallback: the dispatcher and the gateway produce them by design.
- **The request log table** — a second analytical table, 30-day retention, sibling to
  `webhook_attempts` rather than an extension of it.
- **`ANALYTICS`** — one stream, seven days, `discard: old`, 1 GiB, now with two producers of
  different volumes.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A known set of requests produces the same number of records in the analytical
  store, and both counts are published side by side. A three-way equality at zero is not a
  result — 047's T023 compared `count()`, `count() FINAL` and `uniqExact` over an empty table
  and called them equal.
- **SC-002**: Request latency is published with the broker healthy and with it stopped, as
  two distributions rather than one assertion, against NFR-PRF-02's 150 ms.
- **SC-003**: The share of requests carrying no environment is **measured at this chapter's
  tag** and published, split by cause — no principal, and a `platform` principal.
- **SC-004**: A tenant-scoped query over the request log returns that tenant's records and no
  tenantless ones, demonstrated rather than asserted.
- **SC-005**: The ingester's behaviour on an unrecognised record type is published as a
  before-and-after pair: what it did at `part4-ch3`, and what it does after.
- **SC-006**: The eviction risk in FR-014 is settled with a number — the record size, the
  rate at which 1 GiB is reached, and what that rate is against the lane's and a stated
  production estimate. If the answer is that it does not bite, that is published too.
- **SC-007**: The new table is applied by `analytics/apply.mjs`, and a second run reports
  that it applied nothing.
- **SC-008**: The producer's automated tests cover the tenancy branch — an environment
  present and absent — and the measured branch coverage is published beside constitution VI's
  100% requirement, met or pinned with the shortfall stated as a number.
- **SC-009**: No test asserts only that a record was published. Idempotence, tenancy and
  redelivery are each asserted on what the store *holds*, because two 204s prove nothing.
- **SC-010**: `check:fences` reported as a delta per SC/FR-023, with the opening measured in
  this feature rather than carried from 048's 110.
- **SC-011**: Prose measured outside code fences against the 2,000–4,000 bound, with the
  figure published whether or not it forced a split.

---

## Assumptions

- **The chapter is the producer, not the query surface.** FR-ANL-07's *"queryable"* half —
  the customer-facing search, filters, and FR-ANL-10's latency percentiles — is movement IV's
  *"The log a customer can search"*. This chapter makes the records exist and retains them for
  30 days.
- **The record is assembled where the request id already is.** `RequestContextMiddleware`
  mints the id, sets `X-Request-Id`, and already logs one structured line on `finish`. Whether
  the producer lives there or beside it is a planning decision; that the two must not disagree
  about a request's identity is not.
- **Latency is not measured today.** The existing line carries request id, method, path and
  status, and no duration. This chapter adds the measurement rather than reading one.
- **The path bug is fixed and stays fixed.** `req.url` was `/` for every request from
  chapter 2.2 until the rate-limiter chapter; `originalUrl` is what the middleware reads now.
  A producer that reintroduces it records one endpoint for the whole api.
- **The 41 route decorators are a static count, not a traffic distribution.** Volume-weighted
  shares come from the lane, and the lane is the least representative instrument here.
- **`discard: old` was the right choice for one producer.** 3.20 argued it: at the bound the
  oldest analytics is the least interesting. That argument is about one producer's records
  being uniformly aged, and FR-014 asks whether it survives two.
- **Constitution VII applies.** Nothing here needs a language that is not TypeScript.

## Dependencies

- Chapter 4.3's ingester and `relay_analytics.webhook_attempts` (`part4-ch3`).
- Chapter 4.2's `analytics/apply.mjs` ledger and the `relay_analytics` database
  (`part4-ch2`).
- Chapter 3.20's `ANALYTICS` stream, `analyticsSubjectFor`, and the fire-and-forget argument
  this chapter generalises.
- `RequestContextMiddleware`, `AuthenticateMiddleware` and the `Principal` union, all
  Part 2 and Part 3.
- The local stack, which was brought down after 048 closed and whose `EVENTS` store had to be
  rebuilt (048-6). It comes up clean; `--no-deps` is no longer needed.

## Out of scope

The customer-facing request-log query surface and its filters; FR-ANL-10's latency
percentiles; connection open and close events, which are chapter 4.5's and need the gateway's
first publisher and ADR-07's second amendment; the daily rollup and the reconciliation job
(movement IV); FR-ANL-12's usage alert, which is P4; and any change to what `webhook_attempts`
holds.

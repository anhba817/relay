# Feature Specification: chapter 4.8, "the log a customer can search"

**Feature branch**: `053-chapter-4-8`
**Created**: 2026-09-16
**Status**: Draft
**Input**: `chapter 4.8`

---

## 1. Which chapter this is

`docs/12-part-4-structure.md` §3, **row 9, movement IV**: *"The log a customer can search —
FR-ANL-07's query surface; FR-ANL-10's latency percentiles."*

**Name the chapter by its movement and title, not by its number.** §3's table keeps
pre-contraction ordinals in column one on purpose; row 9 is the current 4.8, as row 8 was 4.7.

The two clauses:

- **FR-ANL-07**: *"The system shall retain a queryable API request log per tenant for 30 days,
  recording request ID, timestamp, endpoint, method, status, and latency. Request and response
  bodies shall not be recorded."*
- **FR-ANL-10**: *"The system shall compute end-to-end delivery latency percentiles (p50, p95,
  p99) per tenant per hour."*
- And the bound they are read under, **FR-ANL-08**: *"Analytical queries over 90 days of a
  single tenant's data shall return within 2 seconds at p95."*

---

## 2. The brief pairs one clause that can be built with one that cannot, and the second has been blocked since chapter 4.2

Chapter 4.4 built FR-ANL-07's **producer**. `relay_analytics.api_requests` holds 11,684 rows
across 152 environments with a 30-day TTL — the retention the clause names, kept in a separate
table from `webhook_attempts`' 90 because one `TTL` clause cannot express two.

**Nothing reads it.** Every occurrence of `api_requests` outside the tests is the producer or a
comment. So the query surface is real work and the chapter's first half is straightforward.

**The second half is not, and the reason is a column that has never had a producer.**
`delivery_latency_ms` lives on `message_events` — the table chapter 4.6 measured at **0 rows
with no writer anywhere under `services/`** — and the SAD says so in as many words: *"…has no
producer at all until FR-ANL-10, so every row would assert a delivery took 0 ms."* `gaps.md`
048-2 has carried it through four features and it re-measured at **0 files** at chapter 4.7's
close.

**AND THE ONE LATENCY THE STORE ACTUALLY HOLDS IS NOT THAT ONE, BY A COMMENT WRITTEN AT THE
TIME.** `analytics/0003_webhook_attempts.sql:20`: *"How long the ENDPOINT took to answer. NOT
`message_events.delivery_latency_ms`."* 64 rows, p50 2 ms, p95 2,001 ms, p99 4,961 ms — and
those tails are fixtures timing out on purpose.

So FR-ANL-10 asks for percentiles of a quantity **this platform has never defined**, over a
table that has never been written, while the only latency it does record measures something the
schema explicitly says is a different thing.

---

## 2a. Three measurements that decide what the surface can show

Taken at this feature's opening against the lane's store.

**(1) SIXTY PER CENT OF THE REQUEST LOG BELONGS TO NO TENANT.**

    total rows                    11,684
    environment_id IS NULL         7,063     60.4%   platform 5,916 · none 1,147
    environment_id present         4,621     39.6%

That is chapter 4.4's finding arriving as a product constraint. FR-ANL-01 wants an event for
every API request and FR-ANL-07 wants a log **per tenant**; they are not the same population,
and a tenant-scoped surface can show the smaller half by construction.

**(2) A THIRD OF WHAT IS LEFT IS THE PLATFORM CALLING ITSELF ON THE TENANT'S BEHALF.**

    of the 4,621 attributed rows
      /internal/*                  1,656     35.8%
      /v1/*                        1,857     40.2%
      other (/auth/dev-token, …)   1,108     24.0%
      endpoint absent (unmatched)     22

The single busiest endpoint in the attributed set is `/internal/session` at 1,428, with
`/auth/dev-token` at 1,086. **A customer opening "their" request log finds the gateway's
internal calls at the top of it.** Showing them is confusing; hiding them makes the log
incomplete against a clause that says *every* request. The chapter has to decide and say which.

**(3) A 50-ROW PAGE READS 8,194 ROWS, AND THAT IS THE FLOOR RATHER THAN A DEFECT.**

    SELECT … WHERE environment_id = <busiest> ORDER BY ts DESC LIMIT 50
      read_rows 8,194 · read_bytes 402,609 · elapsed 2.58 ms · result_rows 50

`index_granularity` is 8192, so one granule is the smallest unit the engine can read. The
tenant owns 208 rows. The number is worth publishing because it is what a pagination design has
to be argued against, not because anything is wrong with it.

---

## 3. What the requirement asks for that the platform cannot currently answer

**FR-ANL-08 NAMES NINETY DAYS AND FR-ANL-07 RETAINS THIRTY.** A query over 90 days of a
tenant's request log can never return more than 30 days of it. The two clauses are about
different tables — `webhook_attempts` keeps 90 — but read together over the log this chapter
builds, the performance bound is stated over a window the data does not reach. The chapter
measures what it can measure and says which clause it is measuring against.

**AND "DELIVERY" HAS THREE MEANINGS IN A PLATFORM THAT DELIVERS THREE WAYS.** A message
reaches a subscriber as a socket frame, an endpoint as a webhook POST, or a caller as a REST
read. FR-ANL-10 says *"end-to-end delivery latency"* and names none of them. The candidates,
with what exists today:

| reading | instant to instant | what measures it today |
|---|---|---|
| socket fan-out | message committed → frame written to a subscriber's socket | nothing |
| webhook | message committed → endpoint answered | `webhook_attempts.latency_ms` measures only the last leg |
| REST read | message committed → returned by a history page | nothing, and it is pull rather than delivery |

**A percentile of an undefined quantity is a number with no meaning**, which is the failure
mode chapter 4.6 met from the other side when it closed Appendix C question 4 by defining a
connection-minute before billing one.

---

## 4. What this chapter does not decide

- **It does not build a producer for `message_events`.** Chapter 4.6 named that a send-path
  change on the busiest path in the platform and deferred it with its reasons; re-deciding it
  here would be a second chapter's work inside this one.
- **It does not build a dashboard.** FR-ANL-07 asks for a queryable log, not a rendered one.
- **It does not revisit the 0.1% reconciliation bound.** That is chapter 4.7's, amended in SRS
  revision 1.14.
- **It does not resolve constitution III's amendment.** `gaps.md` 052-6 carries it. This
  chapter is squarely inside the clause — a customer-facing analytics read against ClickHouse
  is exactly what III permits — which is worth stating precisely because the last chapter was
  not.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A customer reads their own request log (Priority: P1)

A customer with a credential asks for their recent API requests and receives a page of them,
newest first, carrying request id, timestamp, endpoint, method, status and latency — and
nothing belonging to another tenant.

**Why this priority**: It is the clause's verb. Everything else in the chapter is a qualifier
on what this page may contain.

**Acceptance scenarios**:

1. **Given** a tenant with requests in the log, **when** the surface is asked for that tenant's
   log, **then** it returns rows carrying the six fields FR-ANL-07 names, newest first.
2. **Given** two tenants with requests in the log, **when** tenant A asks, **then** zero of
   tenant B's rows appear, and the assertion is made on a filter rather than on a count.
3. **Given** a request that resolved to no tenant, **when** any tenant asks, **then** that row
   does not appear for any of them.
4. **Given** a tenant with no requests, **when** it asks, **then** the answer is an empty page
   rather than an error.

### User Story 2 - The page is bounded, ordered and resumable (Priority: P1)

A log with 30 days of a busy tenant's traffic cannot be returned in one response. The surface
takes a window and a page size, returns them in a stated order, and lets a caller continue.

**Why this priority**: An unbounded read against an analytical store is the defect this
movement exists to prevent, and a first page that works at lane scale hides it.

**Acceptance scenarios**:

1. **Given** a tenant with more rows than one page holds, **when** the surface is asked twice
   with the continuation the first answer gave, **then** the second page holds different rows
   and no row appears in both.
2. **Given** a page size larger than the surface allows, **when** it is requested, **then** the
   surface refuses or clamps it, and the behaviour is stated rather than discovered.
3. **Given** a time window, **when** the surface is asked, **then** rows outside it do not
   appear, and the window's boundary handling is asserted from both sides.

### User Story 3 - The log says what it contains and what it cannot (Priority: P2)

The surface is honest about the three measurements in §2a: the tenantless majority, the
internal share, and the retention window.

**Why this priority**: A log a customer can search is a product claim, and the difference
between "your requests" and "requests carrying your environment id" is the difference between a
useful answer and a confusing one.

**Acceptance scenarios**:

1. **Given** a tenant whose attributed rows include `/internal/*` routes, **when** the surface
   is asked, **then** the chapter's decision about those rows is visible in the answer and
   asserted by a test, whichever way it went.
2. **Given** the 30-day retention, **when** the surface is asked for a window older than it,
   **then** the answer distinguishes "no requests" from "outside retention".

### User Story 4 - The percentile requirement is resolved rather than approximated (Priority: P2)

FR-ANL-10's quantity is defined, and either computed over a source that exists or recorded as
unbuildable with the measurement that shows it.

**Why this priority**: The alternative is a percentile over `webhook_attempts.latency_ms`
labelled "end-to-end delivery", which would be a published number that means something other
than what it says.

**Acceptance scenarios**:

1. **Given** the three candidate readings of "delivery", **when** the chapter closes, **then**
   one is chosen, written into the SRS, and the other two are recorded with why they were not.
2. **Given** whatever source the chosen reading names, **when** the percentiles are computed,
   **then** they are computed per tenant per hour as the clause says, or the clause is amended
   to what the platform can produce.
3. **Given** a percentile computed over a sketch or an approximation, **when** it is published,
   **then** its error at the cardinalities that matter is measured and stated — chapter 4.7's
   `uniq` cliff at 65,536 is the precedent.

### Edge Cases

- A tenant asks for a window entirely inside the TTL's deleted range.
- A row whose `endpoint` is absent — 22 of them — because a 404 matched no route.
- A row whose `environment_id` is NULL sitting between two of a tenant's rows in key order,
  given `allow_nullable_key = 1`.
- Two requests in the same millisecond, which a `ts`-ordered cursor cannot separate.
- The analytical store is down. FR-ANL-03 and constitution III say the API must keep serving;
  a query surface that cannot answer is different from an API that cannot serve.
- A tenant asks for a page size of zero, or a negative one.
- An hour with no deliveries at all, when percentiles are computed per hour.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A tenant-scoped query surface shall return that tenant's API request log,
  carrying request id, timestamp, endpoint, method, status and latency.
- **FR-002**: Rows belonging to another tenant shall be unreachable from a tenant's query, and
  the isolation shall be shown by a test that asserts on a second tenant's rows rather than on
  a total.
- **FR-003**: Rows with no tenant shall be unreachable from every tenant's query.
- **FR-004**: The surface shall never return request or response bodies (FR-ANL-07), and the
  absence shall be a property of the stored columns rather than of a filter.
- **FR-005**: Results shall be bounded by a page size the surface controls, and the behaviour
  when a caller asks for more shall be stated and tested.
- **FR-006**: Results shall be ordered, and the order shall be stated in the contract rather
  than inherited from the storage engine.
- **FR-007**: A caller shall be able to retrieve the next page without re-reading the previous
  one, and no row shall appear in two consecutive pages.
- **FR-008**: The surface shall accept a time window and exclude rows outside it, with the
  boundary handling asserted from both sides.
- **FR-009**: The chapter shall decide whether `/internal/*` rows appear in a tenant's log, and
  the decision shall be visible in the answer and asserted by a test.
- **FR-010**: The surface shall distinguish "no requests in this window" from "this window is
  outside retention".
- **FR-011**: The surface shall be reachable only with a credential that carries an
  environment, and a request without one shall be refused rather than answered with an empty
  page (constitution I).
- **FR-012**: The chapter shall define "end-to-end delivery latency" for FR-ANL-10, naming the
  two instants it runs between, and shall record the readings it did not choose.
- **FR-013**: If the chosen reading has a source that exists, the percentiles shall be computed
  per tenant per hour. If it does not, the chapter shall record what building the producer
  would cost and amend FR-ANL-10 rather than publish a percentile of something else.
- **FR-014**: No percentile shall be published under a label that names a quantity it does not
  measure.
- **FR-015**: The query cost shall be measured against a stated volume, reported as rows read
  against rows returned, and compared to FR-ANL-08's bound with the clause it is being measured
  against named.
- **FR-016**: Where FR-ANL-08's 90-day window exceeds FR-ANL-07's 30-day retention, the chapter
  shall say so and amend whichever clause the measurement falsifies.
- **FR-017**: Where a measurement falsifies a published document, that document shall be
  amended — SRS, SAD or `docs/12` — following the precedent of revisions 1.12 through 1.14.
- **FR-018**: `docs/12` §3's row 9 shall be amended where this chapter falsifies its one-line
  description. The table's first column shall be left alone.
- **FR-019**: The chapter shall not re-derive 4.2's store mechanics, 4.4's producer, or 4.7's
  verdict arithmetic. It shall cite them.
- **FR-020**: The chapter shall be registered in `relay-tutorial/lib/tutorial.ts` with its
  directory, manifest path and MDX canonical agreeing exactly.
- **FR-021**: Prose shall stay inside the 2,000–4,000 word bound measured outside code fences,
  with at least one `<Trap>`.
- **FR-022**: `pnpm check:fences` shall be reported as a delta against an opening measured in
  this feature, with the two HEAD classes split.
- **FR-023**: All eleven gates shall run, and every red shall be diagnosed against an opening
  measured in this feature by running the suites directly — `pnpm test:integration` runs three
  of its six lanes (`gaps.md` 051-3).
- **FR-024**: Every statement this feature issues against `api_requests`, `webhook_attempts` or
  any rollup shall name its own environment ids. The analytical store has no lane guard
  (`gaps.md` 050-2).

### Key Entities

- **Request log page** — a bounded, ordered slice of one tenant's `api_requests` rows, carrying
  the six fields FR-ANL-07 names and a way to ask for the next one.
- **Delivery latency** — currently undefined. A duration between two named instants, for one of
  three delivery paths, which this chapter has to choose before it can be a percentile.
- **Latency percentile row** — p50, p95 and p99 for one tenant and one hour, over whichever
  source FR-012's decision names.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A tenant's request log is returned with the six fields FR-ANL-07 names, shown by
  a test against the real store.
- **SC-002**: A second tenant's rows are unreachable from the first tenant's query, shown by a
  test that plants rows for both and asserts on the second's.
- **SC-003**: Tenantless rows are unreachable from every tenant's query, shown by a test.
- **SC-004**: Paging through a tenant's log returns every row once, shown by a test that
  collects two consecutive pages and asserts no overlap.
- **SC-005**: A window's boundary is exercised from both sides.
- **SC-006**: The `/internal/*` decision is asserted by a test whichever way it went.
- **SC-007**: Rows read against rows returned is measured and published for a stated volume,
  with FR-ANL-08's bound named and the clause the measurement is made against stated.
- **SC-008**: "End-to-end delivery latency" is defined in the SRS, naming its two instants,
  with the readings not chosen recorded.
- **SC-009**: Either per-tenant per-hour percentiles are computed over a source that exists, or
  FR-ANL-10 is amended and the cost of its producer recorded.
- **SC-010**: The three opening measurements — 60.4% tenantless, 35.8% internal, 8,194 rows for
  50 — are re-taken at the close and published with any movement.
- **SC-011**: `check:fences` reported as a delta against an opening measured in this feature,
  with the two HEAD classes split.
- **SC-012**: Prose measured outside code fences against the 2,000–4,000 bound, with the
  `<Trap>` count.
- **SC-013**: `pnpm build` exits 0 with the chapter rendering.

---

## Assumptions

- **The query surface is an HTTP route on the api**, following `WebhooksController`'s shape —
  `@UseGuards(CredentialGuard)` and a controller scoped by the principal's `environmentId`.
  Nothing else in this platform serves a customer-facing read, and inventing a second shape
  would be a chapter about routing.
- **The api reads ClickHouse directly**, as chapter 4.7's reconciler does through
  `services/api/src/metering/clickhouse.ts`. That file is read-only by construction and its
  argument for not moving the ingester's client into `@relay/service-kit` still holds.
- **This chapter is inside constitution III rather than in tension with it.** The clause permits
  dashboard analytics to read the analytical store; a customer-facing request log is exactly
  that. Chapter 4.7's conflict was about an auditor reading *both* stores, which this is not.
- **The lane's volume cannot exercise FR-ANL-08.** 11,684 rows against a clause about 90 days
  of a single tenant's data; the bound is measured at whatever volume is available and the gap
  is stated, following `docs/12` §2.3's split for the 0.1% figure.
- **`environment_id` stays `Nullable(UUID)`.** Chapter 4.4 argued it and 049 measured it; a
  query surface is not the place to re-open a column type.

---

## Dependencies

- **Chapter 4.4's producer** — `api_requests`, 11,684 rows, 30-day TTL. Its integration suite
  is red without an ingester process (`gaps.md` 050-8), which this feature's opening must
  measure rather than inherit.
- **Chapter 4.7's analytical caller** — `createAnalyticalStore`, read-only, already wired into
  the api's compose environment.
- **`gaps.md` 048-2**, `delivery_latency_ms` has no producer, carried through four features and
  re-measured at 0 files at 4.7's close. This chapter is where it is closed or restated.
- **SRS FR-ANL-07, FR-ANL-08, FR-ANL-10**, and DR-09's retention split.

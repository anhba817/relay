# Traceability — feature 053, chapter 4.8, "the log a customer can search"

Every requirement and success criterion against the tasks that discharge it, and the
artifact that carries the evidence. **Requirements nothing discharged, and requirements
discharged in a weaker form than their words suggest, are named at the foot.**

| id | requirement | tasks |
|---|---|---|
| **FR-001** | A tenant-scoped query surface shall return that tenant's API request log, | — |
| **FR-002** | Rows belonging to another tenant shall be unreachable from a tenant's query, and | T034 |
| **FR-003** | Rows with no tenant shall be unreachable from every tenant's query. | T035, T055 |
| **FR-004** | The surface shall never return request or response bodies (FR-ANL-07), and the | T025 |
| **FR-005** | Results shall be bounded by a page size the surface controls, and the behaviour | T014, T038 |
| **FR-006** | Results shall be ordered, and the order shall be stated in the contract rather | T032 |
| **FR-007** | A caller shall be able to retrieve the next page without re-reading the previous | T024a, T035a, T036 |
| **FR-008** | The surface shall accept a time window and exclude rows outside it, with the | T037 |
| **FR-009** | The chapter shall decide whether `/internal/*` rows appear in a tenant's log, and | T039 |
| **FR-010** | The surface shall distinguish "no requests in this window" from "this window is | T036a, T040 |
| **FR-011** | The surface shall be reachable only with a credential that carries an | T029 |
| **FR-012** | The chapter shall define "end-to-end delivery latency" for FR-ANL-10, naming the | T046 |
| **FR-013** | If the chosen reading has a source that exists, the percentiles shall be computed | T051 |
| **FR-014** | No percentile shall be published under a label that names a quantity it does not | T049, T052 |
| **FR-015** | The query cost shall be measured against a stated volume, reported as rows read | T041 |
| **FR-016** | Where FR-ANL-08's 90-day window exceeds FR-ANL-07's 30-day retention, the chapter | T042, T056 |
| **FR-017** | Where a measurement falsifies a published document, that document shall be | T055 |
| **FR-018** | `docs/12` §3's row 9 shall be amended where this chapter falsifies its one-line | T057 |
| **FR-019** | The chapter shall not re-derive 4.2's store mechanics, 4.4's producer, or 4.7's | T014, T065 |
| **FR-020** | The chapter shall be registered in `relay-tutorial/lib/tutorial.ts` with its | T064 |
| **FR-021** | Prose shall stay inside the 2,000–4,000 word bound measured outside code fences, | T063, T068 |
| **FR-022** | `pnpm check:fences` shall be reported as a delta against an opening measured in | T072 |
| **FR-023** | Every gate shall run, enumerated rather than counted; a gate that reports success | T073 |
| **FR-024** | Every statement this feature issues against `api_requests`, `webhook_attempts` or | T031 |
| **FR-025** | The read against the analytical store shall be bounded by a stated deadline on | T023a, T023c, T040a, T056c |
| **FR-026** | The refusal shall carry a registered error code, documented in the published | T029a |
| **FR-027** | The chapter shall decide and state what reading the log costs the tenant and | T039a |
| **FR-029** | The route shall be classified in the cross-tenant access suite's target list in | T028a |
| **FR-030** | The response envelope shall match the one this API already serves for a paged | T026d |
| **FR-035** | The surface shall filter by endpoint and by status as well as by time range. | T015a, T036a |
| **FR-038** | The route shall appear in the sealed customer's-eye integration suite, which | T035d |
| **FR-037** | The chapter shall state which questions this log can and cannot answer. It | T064a |
| **FR-036** | Where a published clause requires detail this platform deliberately does not | T055a |
| **FR-033** | The integration suite this feature adds shall be runnable by the project's CI, | T001a |
| **FR-034** | The chapter shall carry at least one `<Why>` box linking the code to its | T063 |
| **FR-032** | The surface shall conform to the published REST interface requirements for a list | T026d, T040a |
| **FR-031** | Putting the analytical store on a customer request path shall be recorded as an | T056a |
| **FR-028** | The surface shall state how recent its answer is. A request made now is not in | T035e, T040b |
| **SC-001** | A tenant's request log is returned with the six fields FR-ANL-07 names, shown by | T032 |
| **SC-002** | A second tenant's rows are unreachable from the first tenant's query, shown by a | T034, T040 |
| **SC-003** | Tenantless rows are unreachable from every tenant's query, shown by a test. | T035 |
| **SC-004** | Paging through a tenant's log returns every row once, shown by a test that | T036 |
| **SC-005** | A window's boundary is exercised from both sides. | T037 |
| **SC-006** | The `/internal/*` decision is asserted by a test whichever way it went. | T039 |
| **SC-007** | Rows read against rows returned is measured and published for a stated volume, | T041 |
| **SC-008** | "End-to-end delivery latency" is defined in the SRS, naming its two instants, | T046 |
| **SC-009** | Either per-tenant per-hour percentiles are computed over a source that exists, or | T052 |
| **SC-010** | The three opening measurements — 60.5% tenantless, 35.8% internal, 8,194 rows for | T073a |
| **SC-011** | `check:fences` reported as a delta against an opening measured in this feature, | T072 |
| **SC-012** | Prose measured outside code fences against the 2,000–4,000 bound, with the | T068 |
| **SC-013** | `pnpm build` exits 0 with the chapter rendering. | T064 |
| **SC-014** | A store that does not answer produces the stated refusal rather than a hang or an | T040a |
| **SC-015** | The refusal's code is in the registry and in the error reference, and | T029a |
| **SC-016** | What a read costs the tenant's REST budget, and whether the surface returns its | T039a |
| **SC-018** | The cross-tenant access suite passes with the new route classified, shown by | T028a |
| **SC-022** | Filtering by endpoint and by status is shown by a test, including an unknown | T015a, T036a |
| **SC-025** | The sealed suite exercises the route, and what it finds — including an empty log | T035d |
| **SC-024** | The chapter states what the log cannot answer, and `gaps.md` carries the | T064a |
| **SC-023** | FR-DSH-03 is amended or the conflict is recorded, with FR-ANL-07's own reasoning | T055a |
| **SC-021** | The new integration suite runs in CI, shown by the workflow providing the store | T001a |
| **SC-020** | The response carries `has_more`, and an error response carries the five fields | T036, T040a |
| **SC-019** | The architecture decision is recorded in `docs/05-sad.md` and | T056a |
| **SC-017** | The end-to-end lag between a request and its appearance in the log is measured | T040b |

---

## What nothing discharged, and what was discharged in a weaker form

**FR-001 has no task naming it and is the one every phase served.** Phase 3's heading is
*"FR-001 — a tenant's log, read from the analytical store through the api"*, and the tasks under
it name the parts rather than the whole. It is discharged by `query.itest.ts` and
`route.itest.ts` together. Recorded here because a generated table reports it as uncovered and
the table is right about what it can see.

### Discharged in a weaker form than the words suggest

**FR-012, FR-013 and FR-014 — the percentiles.** The clause is *defined*, not implemented. No
percentile is computed anywhere, and that is the outcome the phase was written to allow: the
chosen reading has no producer, and publishing a percentile over the wrong column would have
been the failure. `grep FR-ANL-10` over the platform returns two comments and nothing that
computes.

**FR-016 — FR-ANL-08's 90-day window.** Not verified; *shown to be unverifiable*. Two rows
planted at `now - 60 days` and `now - 1 day` leave one survivor because the TTL cuts at INSERT,
so no fixture can put the clause's window in front of it at any volume. The clause is amended
where it is read over this table.

**FR-015 and SC-007 — the rows-read figure.** Measured and published, and the number is the
whole table: 11,695 read for a 51-row page, because the part is Compact and holds one granule.
The clause asked for the measurement and got it; what it implies — a bounded read — is not true
of this table at this size, and the chapter says so rather than quoting a favourable window.

**FR-011 — the 403 for a principal carrying no environment.** Asserted by a unit test on the
controller, because no HTTP path can reach it: `@Accepts("application")` refuses every other
credential class at the door and an application credential always carries an environment. Kept
rather than deleted, which is where it differs from chapter 4.6's dead branches — a requirement
asks for this one.

**FR-028 and SC-017 — how far behind the log is.** Measured once, by hand, with an ingester
started for the purpose and stopped afterwards (min 0.29 s, p50 1.60 s, max 1.61 s). **No gate
runs it**, because `compose.yaml` ships no ingester, so the figure is a measurement of one
afternoon rather than a property anything maintains.

**FR-038 and SC-025 — the sealed suite.** The assertion is that a customer's log comes back
**empty**, which is true and weaker than "the log works end to end". It is the stronger
available claim: the platform ships no ingester, and a test showing an empty log for that reason
asserts something, where omitting the endpoint asserts nothing.

**SC-020's `has_more`.** Conforming on this route and on no other. `messages.service.ts` has
been non-conforming with EIR-API-06 since chapter 2.4 and still is (`gaps.md` 053-6).

### Discharged exactly, and worth naming because the evidence is unusual

**FR-029 and SC-018 — the cross-tenant suite.** The route is classified and attacked, and the
attack plants its own rows because an empty log leaks nothing. The derivation named the route
before the classification file did — the seventh time — and the gauntlet then enforced a third
accounting direction the plan had not: *classified but never attacked*.

**FR-024 — every statement names its tenant.** Checked by `check-lane-scope.py`, which had to be
repaired before it could check anything: it reported 0 unscoped reads over **0 files** until this
feature retargeted it (`gaps.md` 053-4).

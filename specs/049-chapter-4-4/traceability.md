# Traceability — 049, chapter 4.4

28 functional requirements, 11 success criteria. Every one is mapped to what discharges it, and
the two that are **not** fully discharged say so.

## Functional requirements

| id | discharged by | evidence |
|---|---|---|
| FR-001 | `request-log.middleware.ts` | 4 of 4 probe requests captured incl. a 429 and a 404 |
| FR-002 | `toRequestEvent` | `event.test.ts` "drops anything it was not asked for" |
| FR-003 | `void publishRequest(...)` in a `finish` listener | broker up 2.61 ms / down 2.45 ms, all 200s |
| FR-004 | `publishRequest`'s catch | 232 log lines for 230 down-requests, one each |
| FR-005 | `req.route.path` with `baseUrl` asserted empty | `/v1/webhooks` recorded on a guard 401 |
| FR-005a | the limiter stamps `refusal.operation` | `limited_operation` = `rest` on a real 429 |
| FR-005a1 | chapter prose, "Which endpoint is being rate-limited" | `operationsFor` quoted; three values |
| FR-005b | `refused_at` column | four values distinguished in the store |
| FR-005b1 | `CredentialGuard` stamps | guard 401 and handler 200 record differently |
| FR-005b2 | `event.test.ts` source scan | run red by deleting the stamp |
| FR-006 | allow-list shaper | no body, header or credential reaches the event |
| FR-007 | both interval ends named | `contracts/api-request-event.md`, baseline T086 |
| FR-008 | `principal?.environmentId` | `application` 20 of 20 attributed |
| FR-009 | `apiRequestSubjectWithoutTenant()` | `platform` and `none` records exist |
| FR-010 | nullable column + exact-match subjects | tenant-scoped read returns 0 tenantless |
| FR-011 | a separate function, validator untouched | `apiRequestSubject("_none")` still throws |
| FR-012 | `route()`'s `unclaimed` arm | unknown record returns on pass 2 |
| FR-013 | `api_requests` + R12 argued in phase 3 | one consumer, with the crossover recorded |
| FR-014 | measured, not asserted | 320 B/record, 5.5 req/s, 38.8 req/s |
| FR-015 | `analytics/0004_api_requests.sql` | `applied 1`, then `applied nothing` |
| FR-016 | `TTL toDateTime(ts) + INTERVAL 30 DAY` | `SHOW CREATE TABLE` |
| FR-017 | `ORDER BY (…, request_id)` | physical 3 / FINAL 1, merges stopped |
| FR-018 | SRS revision 1.11 | FR-ANL-07 amended, "truncated payload" dropped |
| FR-019 | `docs/12` §4's five references | corrected, with the reason recorded |
| FR-020 | SAD revision 1.4 | the 24 h claim amended at both sites |
| FR-021 | chapter prose | 3.20's argument cited, not re-derived |
| FR-022 | 2,393 prose words | inside the 2,000–4,000 bound |
| FR-023 | delta reported by kind and locale | 110 → 110, APPLY 74, HEAD 36 |

## Success criteria

| id | met? | evidence |
|---|---|---|
| SC-001 | yes | 5 requests → 5 rows, against a non-zero floor |
| SC-002 | yes | two distributions, one instrument, status codes beside them |
| SC-003 | yes, **for a stated workload** | 63% tenantless; 049-6 records that no production mix exists |
| SC-004 | yes | tenant-scoped read: own rows, zero tenantless, foreign sees neither |
| SC-005 | yes | before/after pair, both passes |
| SC-006 | yes | 320 B, 5.5 req/s, 38.8 req/s — and it does bite, so it is published |
| SC-007 | yes | `applied 1`, then `applied nothing` |
| SC-008 | **yes, and met rather than pinned** | `event.ts` 100% branches — the clause 048 could not reach |
| SC-009 | yes | 15 tests audited; none asserts only that a publish happened |
| SC-010 | yes | 110 → 110, delta 0, broken down by kind and locale |
| SC-011 | yes | 2,393 words, published whether or not it forced a split |

## What nothing discharged

**Nothing.** All 28 FRs and 11 SCs have evidence above.

Two are discharged with a stated limit rather than fully, and both are in `gaps.md` rather than
hidden in a tick:

- **SC-003** is true of a workload this feature chose. The structural half — `platform` is 100%
  tenantless by construction — travels; the 63% does not (049-6).
- **FR-014** is measured and the answer is that the crossover is low. The requirement asked for
  the measurement, not for the problem to be absent, so it is discharged and 049-4 carries the
  consequence.

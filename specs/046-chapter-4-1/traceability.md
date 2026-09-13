# Traceability — chapter 4.1

Nineteen requirements and eight criteria against the tasks that verify them. The
verification column says the method actually used, not the one the template assumes.

## 1. Functional requirement → tasks

| Requirement | Verified by | How |
|---|---|---|
| FR-001 demonstrate CON-01 by measurement | T027, T028, T036, T037 | A — four numbers, three corpora |
| FR-002 no schema change published | T031, T041 | I — `git status`, migrations end at 0014 |
| FR-003 a seeder with a credential | T011–T013b, T047 | D — three volumes, counts match |
| FR-003a report the corpus created | T018, T047 | D — every field counted from the database |
| FR-003b create and migrate, no DDL | T012a | D — 15 migrations, 23 tables |
| FR-003c a bot sender and its channel | T013b | T — a 403 before, a 201 after |
| FR-004 the query FR-ANL-05/09 asks for | T021 | I — research R2, no `kind` filter |
| FR-005 publish the plan beside the duration | T022, T027 | A — the plan carried the result |
| FR-006 write latency with and without | T024, T028 | A — two control loops, 0.7 ms apart |
| FR-007 counterfactual on a throwaway copy | T033, T034 | I — `create database … template` |
| FR-007a improvement AND cost AND storage | T036, T037, T038 | A — 4.4%, no send effect, +49% |
| FR-008 row counts beside every duration | T025, T027 | I — `subject` block in every result |
| FR-009 the lane's answer beside the corpus | T029 | A — 0.9 ms vs 585.9 ms, factor 651 |
| FR-010 publish a refusal rather than re-run | T030, T039 | A — `hypothesis_send_path_pays` |
| FR-011 do not re-teach fire-and-forget | T056 | I — the ForwardRef cites it, does not derive it |
| FR-012 do not teach ClickHouse | T056 | I — named as the next chapter's |
| FR-013 no artefact of the counterfactual | T031, T041, T047b | I — 0 databases, 0 migrations |
| FR-014 re-derive the index facts | T002 | D — `sed` over `schema.ts`, 2 indexes |
| FR-015 report the fence delta, not the total | T006, T062 | D — 110 → 110, delta **0** |

## 2. Success criterion → tasks

| Criterion | Verified by | Result |
|---|---|---|
| SC-001 a reader reproduces the corpus | T047 | three volumes, all matching |
| SC-002 both durations, factor stated | T027, T029, T054 | 585.9 / 0.9 ms, **651×** |
| SC-003 both p95s, difference as a number | T028 | 20.5 / 13.7 ms, −6.8 ms |
| SC-004 four figures, one worse than before | T036–T038 | storage +49% is the worse one |
| SC-005 every database gone, no schema change | T041, T047b | 0 remain; lane identical to T007 |
| SC-006 interface published, imported by nothing | T048, T049 | no importer outside `scripts/` |
| SC-007 one person, three questions | T066 | **NOT RUN — see gaps.md** |
| SC-008 2,000–4,000 words, a TRAP, two figures | T057, T058, T061 | **2,132 words**, 3 TRAPs, 3 figures |

## 3. What this table cannot say

Every row above was checked by running something, except SC-007, which needs a
person and did not get one. That is the fifteenth record in this project to name
that gap and the fifteenth not to close it.

`check-refs` compares ids. `check-chapter` compares bytes. Neither can say whether
the argument in the prose is the argument the numbers support — and this chapter's
argument changed twice during measurement, which is exactly the case where nobody
would notice if the prose had been left describing the old one.

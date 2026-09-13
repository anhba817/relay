# Traceability — chapter 4.2

Method is the one **actually used**, not the one planned: **T** test, **D** demonstration,
**A** analysis, **I** inspection. Where a requirement was verified by a measurement, the
number is here rather than a pointer to it.

## Functional requirements

| id | verified by | method | what it came back as |
|---|---|---|---|
| FR-001 | T013, T014, T003 | D | Schema created from SAD §6.2 with **six** divergences, each commented in the DDL. The published statement was posted verbatim first and refused: `Code: 450 … BAD_TTL_EXPRESSION`. |
| FR-002 | T013, T026 | I + D | `PARTITION BY toYYYYMM(ts)`, `ORDER BY (environment_id, ts)`. The plan shows the primary key skipping 23 of 154 granules. |
| FR-003 | T013, T021, T024 | D | `TTL toDateTime(ts) + INTERVAL 90 DAY`. 1,654,621 events sent, **413,550 removed**, 1,241,071 held over 91 days. |
| FR-003a | T033a, T030 | D + A | `daily_usage` carries no TTL and holds **121 days** where the raw table holds 91. Stated in the chapter as DR-09 and DR-10 working as a pair. |
| FR-004 | T014, T029 | D | Materialised view; the rollup answers the same question reading **315 rows** against 1,052,655. |
| FR-005 | T033 | D | Three inserts after the view existed were included with no rebuild: raw 3,000, `sum(messages)` 3,000. |
| FR-006 | T020 | I | No text column exists in `message_events`; the load selects lengths only. |
| FR-006a | T013, T051 | I | `delivery_latency_ms` is `Nullable(UInt32)` with no producer, named in the DDL comment and in the chapter's `<ForwardRef>`. |
| FR-007 | T022, T025 | D | FR-ANL-05's question answered: 91 days, 999,962 messages, **13.22 ms** best of three. |
| FR-007a | T018a, T018b | D | The corpus now carries edits, deletions, attachments and non-ASCII text. All four column findings visible as ClickHouse sees them, including `length(attachments)` **78** against `JSONLength` **2**. |
| FR-008 | T030, T029 | D | 91 days compared, **90 agree exactly**, 1 differs by 4,941. Cost published beside it. |
| FR-009 | T032, T034 | D | `uniqMerge` 5,000 against `uniqExact` 5,000, **0.0000%** — published beside the table showing `uniq` is exact only to ~65,000. |
| FR-010 | T023, T026 | D | `EXPLAIN indexes = 1` published with all three stages; two skip nothing, and the chapter says why. |
| FR-011 | T015, T037, T038 | D | Applies 3 on an empty store, **"applied nothing"** on the second run, 1 of 4 after a file is added. |
| FR-012 | T041 | I + D | `schema_migrations` 15 rows, last applied **2026-09-10**, three days before this feature. `services/api/migrations/` unchanged, 0 git changes. No analytical table in Postgres. |
| FR-013 | T051 | I | No ingester, no emission path, no producer. Stated in the `<ForwardRef>`. |
| FR-014 | T025 | A | 4.1's 585.9 ms is **quoted** from `specs/046-chapter-4-1/baseline.txt` with its corpus and machine. No Postgres analytical query was run at this tag. |
| FR-015 | T059, T060 | D | `check:fences` **110 → 110, delta 0**, breakdown matching T004 line for line. Eight gates green. |

## Success criteria

| id | verified by | method | what it came back as |
|---|---|---|---|
| SC-001 | T025 | D | **13.22 ms** against 4.1's **585.9 ms**, both best of three, both 91 days. |
| SC-002 | T030 | D | Rollup read with `sum()` and `GROUP BY`: 90 of 91 days identical; the 91st differs by 4,941 and the chapter explains why it cannot be otherwise. |
| SC-003 | T029, T031 | D | 315 rows against 1,052,655 — 3,342× — for **19%** less time. Both published, including the part that is not flattering. |
| SC-004 | T023, T026 | D | `PrimaryKey … Granules: 131/154`. MinMax and Partition skip nothing, and the TTL is the reason. |
| SC-005 | T037, T038, T040 | D | Applies to an empty store, reports a no-op on the second run, refuses an edited file **by name with both checksums**. |
| SC-006 | T013, T018b | I + D | Every column is filled by the corpus or named as unproduced. `delivery_latency_ms` is the only one with no producer. |
| SC-007 | T041, T043 | I | `schema_migrations` unchanged; no analytical query against Postgres at this tag. |
| SC-008 | T058 | D | **2,580** prose words, inside the 2,000–4,000 bound. |

## Where the plan was wrong

Four task premises were falsified by running them, and all four are recorded in
`baseline.txt` rather than quietly corrected:

1. **T009's `CLICKHOUSE_DB` creates nothing** on a volume that already holds a database —
   the entrypoint skips initialisation. The bootstrap in `apply.mjs` is load-bearing.
2. **T001's falsification clause could not fire.** `default` is refused before and after
   the amendment with the identical error string; the discriminator is whether `relay`
   answers.
3. **T021's TTL is a schedule, not an event.** Nine parts, and only some were cleaned on
   the way in: 121 days immediately after the load, 91 after the merge.
4. **T059 predicted a non-zero fence delta.** It is 0 — the amendment created one HEAD
   problem and the chapter's own hunk closed it.

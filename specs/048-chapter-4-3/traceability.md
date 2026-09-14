# Traceability — chapter 4.3

Method is the one **actually used**: **T** test, **D** demonstration, **A** analysis,
**I** inspection. Where a requirement was verified by measurement the number is here rather
than a pointer to it.

## Functional requirements

| id | verified by | method | what it came back as |
|---|---|---|---|
| FR-001 | T018, T023 | D | One service consumes `ANALYTICS` and writes `relay_analytics`. It is the only consumer: four `ANALYTICS_STREAM` references outside the protocol package, all in the publisher. |
| FR-002 | T019, T044 | D | Bounded by both. Measured: an insert costs 1.5 ms at one row and 1.5 ms at a hundred; per-row cost falls 5,000× by ten thousand. The bounds cross at **5,000 records/second**. |
| FR-003 | T029 | D | With the store stopped: `ingester.batch_failed`, and `ack_pending 5` — delivered, unacknowledged, waiting. |
| FR-004 | T035, T036, T038a | D + T | Ten records replayed under **three different groupings** (5 refused, 3, 10) stay ten rows. |
| FR-005 | T027 | D + A | ClickHouse stopped, 5 webhook walks, **5 succeeded, 0 failed**, 0 walk outputs mentioning the store. |
| FR-006 | T028, T030 | D | Depth 32 → 37 during the outage; drained to 36 rows on recovery. **37 published, 1 terminated, 36 written.** |
| FR-006a | T018, T027a | D | `max_deliver: -1`. Measured at 3: delivered rounds 1–3, **nothing from round 4**, `num_pending 0` with the stream still full. |
| FR-006b | T022, T029 | D | The malformed record at sequence 32 was terminated at the parse, not retried. |
| FR-007 | T011, T014 | D | `0003_webhook_attempts.sql` applied through the ledger; a second run reports `applied nothing`. |
| FR-007a | T011a | D | `CONSTRAINT ts_is_real` → `Code: 469` on an absent `ts`; `skip_unknown_fields=0` → `Code: 117` on a renamed one. |
| FR-008 | T015, T048 | I | SAD revision **1.3** publishes `webhook_attempts`. §6.2 had labelled `message_events` *representative* and named no attempt table. |
| FR-009 | T038 | I | `schema_migrations` 15, unchanged. Zero imports of pg, drizzle or `@relay/api`. Dependencies: `@relay/protocol`, `@relay/service-kit`, `nats`. |
| FR-010 | T022, T029 | D | `ingester.malformed_record · stream_sequence: 32` — the sequence and nothing else. |
| FR-010a | T022 | I + D | No payload in any log line. The record survives in the stream, so the sequence is enough to fetch it deliberately. |
| FR-011 | T031 | D | **`first_seq` is the instrument.** `last_seq - first_seq + 1 == messages`, so nothing was discarded; a consumer's last-acked sequence against `first_seq` gives the loss exactly. |
| FR-012 | T047 | I | No reconciliation job, query surface or percentiles. No producer added for `delivery_latency_ms`. |
| FR-012a | T025a, T038a, T038b | T | 15 tests across two lanes. `shape.ts` **100/100/100**; pins set below measurement with the shortfall named. |
| FR-013 | T055, T056 | D | `check:fences` **110 → 110, delta 0** per line. Eight gates green. |
| FR-014 | T017, T018 | A | The runtime is not reused, and why is the chapter's argument: `claimEvent` is a Postgres transaction. |

## Success criteria

| id | verified by | method | what it came back as |
|---|---|---|---|
| SC-001 | T023 | D | **31 published, 31 written**, and `count()`, `FINAL` and `uniqExact` all 31. |
| SC-002 | T027, T028 | D | 5 walks, 5 successes, depth 32 → 37 and back to drained. |
| SC-003 | T035, T036 | D | Regrouped redelivery: 10 records, 3 groupings, 10 rows. |
| SC-004 | T044 | D | Both bounds measured; the crossover stated at 5,000 records/second. |
| SC-005 | T038 | I | No Postgres write, no Postgres query, no Postgres dependency. |
| SC-005a | T038b | T | `shape.ts` 100% branches; `clickhouse.ts` 84.21%; `main.ts` 37.50%; total **77.19%**, all pinned. |
| SC-006 | T014 | D | `applied 4` then `applied nothing`. |
| SC-007 | T055 | D | Delta 0, reported per line of T007's breakdown. |
| SC-008 | T054 | D | **2,087** prose words, inside 2,000–4,000. |

## Where the plan was wrong

Six task premises were falsified by running them. All six are in `baseline.txt`.

1. **T014 expected `applied 1`.** It applied **4** — 047's close-out dropped the database, so this chapter starts from empty rather than from 4.2's three tables.
2. **T028's signal was wrong twice.** Pass 2 said stream depth against `num_pending` detects a strand; `retention: Limits` makes a clean drain identical to one. The fallback, `num_redelivered`, is a **gauge of outstanding redeliveries** and reads 0 after a drain that definitely redelivered. **The row count against the published count is the only signal.**
3. **T031 expected "it cannot know".** `first_seq` makes the loss computable.
4. **T017a predicted an overrun.** The first draft came in at **1,659 words — below the floor** — and needed two required sections that were simply unwritten.
5. **T051 expected one hunked fence for `compose.yaml`.** The ingester needs no compose entry, so there is none; and `vitest.coverage.config.mts`, which the pins do amend, **cannot take one** — 591 lines divergent before this chapter touched it.
6. **The SQL fence shipped as an excerpt first** and the chain caught it in one run: 111, then 110 once the whole body was published.

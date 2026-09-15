# Traceability — 050, chapter 4.5, "the gateway's first stream"

**32 functional requirements, 11 success criteria.** Each row names the tasks that
discharge it and the artifact a reader can check it against. The last section names
what nothing discharged.

Measurements live in `baseline.txt` under the task id in the second column.

---

## Functional requirements

| FR | Tasks | Discharged by |
|----|-------|---------------|
| FR-001 | T019, T029, T030, T037 | `connection-log/event.ts` `toConnectionEvent()`; `session.ts:980` beside `registry.add` and `:1180` beside `meter.closed`; itest *"puts 2N records on the stream"* |
| FR-002 | T029, T030 | `toConnectionEvent()` names every field off a real `Connection`; `event.test.ts` *"lets no credential, channel list, message content or socket reach the wire"* |
| FR-003 | T021, T030 | The same test, driven by constitution III's **allow-list** — *"only lengths, identifiers, and metadata"*. FR-ANL-11 and NFR-SEC-06 were the original citations and govern message text and application logs; neither reaches the record (pass 12) |
| FR-004 | T023, T031, T032 | The tick publishes; `opened()`/`closed()` enqueue and return. `event.test.ts` *"the TICK publishes, not the hand-over"* and *"neither hand-over throws when the publisher is broken"* |
| FR-004a | T025, T026 | `MAX_BUFFERED = 4_000`, oldest dropped. Test *"drops at the cap, counts the drop, and keeps the records describing the outage"* |
| FR-004b | T026, T067 | One `connection_log.publish_failed` line per flush carrying `attempted`/`failed`/`buffered`; T067 measured it carries no token, no payload and no subject |
| FR-004c | T023, T024 | `FLUSH_INTERVAL_MS = 5_000`, named in the chapter beside the ingester's `BATCH_MS = 2_000` |
| FR-004d | **T028** | **Measured, not derived**: min 2,020 / p50 5,723 / max 5,796 ms over six connections, 9.7% of FR-ANL-04's 60 s **under normal conditions** |
| FR-004e | T033, T065 | Retain-until-accepted: failed records go back in the buffer. T065 measured 139 retained and 0 dropped with the broker stopped |
| FR-004f | T033 | `Promise.allSettled` over the batch, outcomes read per record. Test *"keeps exactly the failed records of a partial flush and drops none of the accepted"* |
| FR-005a | T029 | The open carries `connection.openedAt`, not the moment of shaping. Test 7 |
| FR-005 | T029 | `duration_ms` plus both endpoints; a close preceding its open clamps rather than reporting a negative |
| FR-006 | T036 | **Recorded as impossible rather than handled.** `open()` takes a non-optional `Identity` and is the only builder of a `Connection`; 4001, 1011, 4003, 4008 and 429 all return first. 4.4's `_none` arm is unnecessary here, not declined |
| FR-007 | T071 | `git diff` over `meter.ts` and the quota counters: untouched |
| FR-008 | T087 | The chapter cites `docs/12` §4 rather than re-deriving it, and names both limits: the meter cannot say a connection existed, the records cannot refuse one |
| FR-009 | T073–T075 | Three reconciliation runs agreeing, one crossing a bucket boundary (10 connections → 11 buckets) |
| FR-009a | T073, T078 | Scoped to connections with **both** records. T078 is why: unscoped, run 1 would have compared 8 against 0 |
| FR-009b | T074 | Buckets split by period the way the meter splits them |
| FR-010 | T031, T034 | One lazily-connected client in `publisher.ts` with a shared in-flight connect promise; `main.test.ts`'s fabric list goes 7 → 8 and `shutdown()` closes it second |
| FR-011 | T001, T018 | 5 → 6, counted before and after |
| FR-012 | T049, T054 | The third arm on `route()`; records reach the store through the existing ingester |
| FR-013 | T049, T051 | `connection.opened` / `connection.closed` read off a closed set and renamed to `event`; an unknown type still reaches `unclaimed` |
| FR-014 | T055, T056 | `Nats-Msg-Id` of `{connection_id}:{event}`; three identical inserts, `count()` 3 against `FINAL` 1, under `SYSTEM STOP MERGES` with a `finally`, a scoped `DELETE` and a dedicated environment id |
| FR-015 | T083, T084 | The third producer measured against the shared stream's budget; 049-4's crossover restated |
| FR-016 | T080, T080b | **Both** documents: `docs/05-sad.md`'s summary and `docs/06-adr-deep-dives.md`'s 98-line argument |
| FR-016b | T080b | **Decision** and **Revisit when** left untouched, 3.18's shape |
| FR-016a | T080a | The form chosen out loud: constitution VII says ADRs are immutable, ADR-07 carries both forms, and the missing sentence was the defect rather than either choice |
| FR-017 | T081, T081a | DR-11 given the two figures `docs/05-sad.md:182` chose and credited to it |
| FR-017a | T081b, T081c | The SAD's §6.2 table entry and §4's gateway entry — the *incomplete* rather than *wrong* class |
| FR-018 | T086, T087 | 3.20's fire-and-forget, 4.3's routing and 4.4's tenantless rule are cited, not re-derived |
| FR-019 | T091 | **2,330 prose words** outside code fences, inside the 2,000–4,000 bound |
| FR-020 | T010, T094 | Opening and close both measured by kind and locale in this feature |

## Success criteria

| SC | Tasks | Result |
|----|-------|--------|
| SC-001 | T037, T054 | 6 connections across 6 users → 12 records → 12 rows |
| SC-002 | T064–T066 | **60/60 acked with the broker stopped**, 139 records retained, 0 dropped |
| SC-003 | T071, T077 | The meter suite unchanged and passing; no disagreement to record |
| SC-004 | T073–T076 | Three runs agreeing; the duration/bucket gap published as a number (2 against 0.03 for one connection) so nobody reads it as a defect |
| SC-005 | T001, T018 | 5 before, 6 after |
| SC-006 | T083, T084 | Measured against a length-matched subject, 4.4's 2% lesson applied |
| SC-007 | T056 | Before-and-after counts unchanged by a redelivery |
| SC-008 | T057 | `event.ts` at **100/100/100/100** — constitution VI's 100%-branch clause met rather than merely claimed |
| SC-009 | T080–T080b | The spent argument (the client count, and the cost side going to zero) and the surviving one (Redis alone) both named |
| SC-010 | T010, T094 | 110 → 110, **delta 0 in every cell** |
| SC-011 | T091 | 2,330 words, 2 `<Trap>` boxes, 3 figures |

## What nothing discharged

**Nothing.** Every FR and SC above has a task and an artifact.

Three carry a qualification rather than a gap, each recorded where it was measured:

- **FR-006** is discharged by showing the case cannot arise, not by a branch. That is
  the stronger form and it is why 4.4's `_none` arm has no counterpart here.
- **SC-008**'s figure came from the gateway's own vitest with `--coverage.include`,
  because the workspace coverage lane appeared dead when T057 ran. T095 re-ran that
  lane; see `gaps.md` 050-1 for what the re-run found.
- **FR-004d** is measured under normal conditions, which is the clause's own
  qualifier. A record published during a broker outage is queryable minutes late and
  FR-004e is what makes that legitimate rather than a breach.

# Captured output — chapter 3.3

Everything the chapter quotes comes from here, and everything here came from a
run on 2026-08-08 against the compose stores. No credential and no tenant
message body appears (spec FR-017, quickstart V7).

---

## Lane counts

| Lane | Before (baseline.txt) | After |
|---|---|---|
| `pnpm test` (Docker-free) | 109 | **120** |
| `pnpm test:integration` | 76 | **87** |

New: `event.test.ts` (6), `publisher.test.ts` (5), `outbox.itest.ts` (11).
Every pre-existing suite passes with its assertions unchanged. Both lanes exit 0.

---

## The invariants, as the runner prints them

```text
✓ invariant 1: a committed message leaves exactly one outbox row
✓ invariant 2: a rolled-back write leaves no outbox row
✓ invariant 3: a recognised idempotent retry adds no second event
✓ invariant 4: both doors produce one event each, identical in shape
✓ invariant 7: the relay publishes pending rows, marks them, and does not republish
✓ invariant 8: two concurrent relays publish every row exactly once
✓ invariant 11: a relay log line carries counts, never payloads
✓ invariant 6: publish-after-commit LOSES the event when the process dies in the gap (SC-003)
✓ invariant 5: the outbox SURVIVES the same kill, and invariant 10's id survives with it (SC-002)
✓ invariant 9: the broker can be absent — writes succeed, events accumulate, the backlog drains (SC-007)
✓ a failing publisher leaves the row pending rather than losing it
Tests  11 passed (11)
```

Invariant 12 runs in the unit lane (`publisher.test.ts`); invariant 10's unit
half is in `event.test.ts` and its integration half rides on invariant 5.

---

## The demonstration — same kill, two outcomes

Both runs are `node scripts/dual-write-walk.mjs --mode=…`, `SIGKILL`ed by a
parent the moment the child prints its marker.

```console
$ naive, killed in the gap
environment                0e9d99cb-e8a2-46f5-9e53-3a2729e8ed38
mode                       naive
messages committed         1
outbox rows                0
MARKER kill-me-now
  [process killed with SIGKILL at the marker]

$ outbox, killed in the gap
environment                c0f83026-0e9b-4094-92e4-90ad5c7a7faf
mode                       outbox
messages committed         1
outbox rows waiting        1
MARKER kill-me-now
  [process killed with SIGKILL at the marker]
```

What each left behind:

```text
naive  env 0e9d99cb: messages=1 outbox=0
outbox env c0f83026: messages=1 outbox=1 unpublished=1
```

One message exists in both databases. In the first, nothing anywhere records
that an event was owed — no row, no error, nothing to replay from. In the
second, the event is sitting in the table waiting for a relay.

---

## The walk, run to completion

```console
$ node scripts/dual-write-walk.mjs --mode=outbox
environment                f52b79af-b9c2-4c97-81e1-d8b1400ec193
mode                       outbox
messages committed         1
outbox rows waiting        1
MARKER kill-me-now
events published           1
outbox rows waiting        0

$ node scripts/dual-write-walk.mjs --mode=naive
environment                c2322ed3-0d6b-4029-9ffb-f6ae79cf846e
mode                       naive
messages committed         1
outbox rows                0
MARKER kill-me-now
events published           1
durable record of them     none — the publish WAS the record
```

Nobody killed these. Both publish successfully — which is the honest part: the
naive version is not broken, it is *unlucky*, and only in a window nobody can
see.

---

## Two relays, one table (quickstart V5)

```console
$ node scripts/dual-write-walk.mjs --mode=outbox --messages=200
messages committed         200
outbox rows waiting        200
events published           200
outbox rows waiting        0
```

200 rows, 200 events, no row published twice — `FOR UPDATE SKIP LOCKED` doing
the work a coordination mechanism would otherwise need.

---

## The broker can be absent (quickstart V4, SC-007)

A real container stop, not a simulation:

```console
$ docker compose stop nats
$ node scripts/dual-write-walk.mjs --mode=outbox --messages=3
messages committed         3
outbox rows waiting        3
$ psql -tAc "SELECT count(*) FROM outbox WHERE published_at IS NULL"
3

$ docker compose start nats
$ node scripts/dual-write-walk.mjs --mode=outbox --messages=1
events published           4
outbox rows waiting        0
$ psql -tAc "SELECT count(*) FROM outbox WHERE published_at IS NULL"
0
```

Writes succeeded with the broker down. The backlog drained when it came back —
four events, the three that piled up plus the new one — with nobody
intervening. SAD §7 claims this; this is the claim being run.

---

## The table, as the database has it

```text
                              Table "public.outbox"
    Column    |           Type           | Nullable |              Default
--------------+--------------------------+----------+------------------------------------
 id           | bigint                   | not null | nextval('outbox_id_seq'::regclass)
 subject      | text                     | not null |
 payload      | jsonb                    | not null |
 created_at   | timestamp with time zone | not null | now()
 published_at | timestamp with time zone |          |
Indexes:
    "outbox_pkey" PRIMARY KEY, btree (id)
    "outbox_unpublished" btree (created_at) WHERE published_at IS NULL
```

---

## The NATS client decision (T004, research R11)

Both candidates were installed in a scratch CommonJS package and used to create
a stream and publish one message:

| Candidate | `require()` from CJS | Stream + publish | Packages |
|---|---|---|---|
| `nats@2.29.3` | works | `seq=1` | **1** |
| `@nats-io/jetstream@3.x` | works | `seq=1` | **2** (needs `@nats-io/transport-node`) |

The 2.6-style interop failure did not materialise for either. `nats@2.29.3`
won on Principle VII: one dependency instead of two.

---

## The sabotage check (T025)

With the outbox insert moved outside the transaction:

```text
× invariant 1: a committed message leaves exactly one outbox row
× invariant 3: a recognised idempotent retry adds no second event
× invariant 4: both doors produce one event each, identical in shape
× invariant 7: the relay publishes pending rows, marks them, and does not republish
× invariant 5: the outbox SURVIVES the same kill …
× invariant 9: the broker can be absent …
× a failing publisher leaves the row pending rather than losing it
7 failed
```

Seven of eleven fail. The suite holds the property it claims to hold.

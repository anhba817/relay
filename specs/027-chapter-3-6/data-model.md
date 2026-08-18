# Data model — chapter 3.6

Eight columns across two tables chapter 3.5 created, and one new table. No new
store.

The count started at four. The other four arrived during implementation, when two
requirements turned out to need state nothing was keeping — they are in the
`webhook_deliveries` section below, with the reason each one exists.

---

## `webhook_endpoints` — amended

| Column | Type | Null | Meaning |
|---|---|---|---|
| `failure_run_started_at` | `timestamptz` | yes | When the current unbroken run of failures began. Null when the endpoint is healthy. |
| `failure_run_attempts` | `integer` | yes | How many failed attempts the current run contains. Null when healthy. |
| `disabled_at` | `timestamptz` | yes | When the platform disabled it. Null when the endpoint was never auto-disabled, including when a customer disabled it themselves. |
| `disabled_reason` | `text` | yes | Why. Null unless `disabled_at` is set. |

**`enabled` already exists** and keeps its meaning: whether deliveries are made.
Auto-disable sets `enabled = false` *and* stamps `disabled_at`. A customer
disabling their own endpoint sets `enabled = false` and leaves `disabled_at` null,
which is how FR-009's distinction is drawn — a customer can tell who switched it
off by whether the platform left its fingerprints.

**Transitions.**

```text
healthy ──failure──> run open (started_at set, attempts = 1)
run open ──failure──> run open (attempts + 1)
run open ──success──> healthy (both null)
run open ──hour elapsed AND attempts >= 5──> disabled
                                             (enabled=false, disabled_at, reason,
                                              notification row written)
disabled ──customer re-enables──> healthy   (all four columns null, enabled=true)
disabled ──further failures──> disabled     (no second disable, no second notify)
```

The last line is FR-008. It is enforced by the disable path requiring
`enabled = true` in its predicate, so a second disable updates zero rows rather
than being prevented by a check somebody has to remember to write.

---

## `webhook_deliveries` — amended, and this section was not in the first draft

Four columns the plan did not anticipate. Each is here because a requirement
cannot be met without it, and the reasoning is recorded rather than the columns
merely listed — a data model that grows silently during implementation is one
nobody trusts on the next chapter.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `last_status` | `integer` | yes | What the endpoint answered on the most recent attempt. Null when nothing answered. |
| `last_error` | `text` | yes | What went wrong on the most recent attempt when there was no status. |
| `last_latency_ms` | `integer` | yes | How long that attempt took. Null before the first attempt is reported. |
| `synthetic` | `boolean` | no | True for a test event's delivery (FR-013). Default false. |

**Why the last outcome is persisted at all.** Chapter 3.5 recorded an attempt's
result by moving the delivery — `state`, `attempt`, `next_attempt_at` — and threw
away what the endpoint actually said. That was sufficient while the only consumer
was the retry schedule. Two requirements here need it back:

- **FR-016** — the test event reports what the endpoint answered, to a caller that
  is waiting. The attempt is made by the dispatcher in another process, so the
  answer has to be somewhere the route can read it. It cannot be read off the
  attempt event: that publish is at-most-once by design (R5), and a test whose
  result can be lost is not a test.
- **FR-009 via the sweep** — a disablement records the last observed error. The
  on-outcome trigger has the outcome in hand; **the sweep does not.** It fires
  precisely when no outcome is arriving, which is the whole of research R1. Without
  a persisted last status the sweep can only write null, and a notification that
  says "disabled, cause unknown" is the one a support engineer receives.

`latency_ms` has been crossing the seam since 3.5 and being discarded (R6). This
is the second thing in the chapter to pick it up off the floor.

**Why `synthetic` is a column and not a payload inspection.** The envelope carries
`type: "webhook.test"` and `test: true`, so the fact is already in the `payload`
jsonb and could be read with `payload->>'type'`. It is a column because three
different decisions branch on it — no retry schedule, no failure-run update, and
delivery to a disabled endpoint — and a predicate that expensive to get right
should not be a string comparison against a customer-visible document. It also
keeps the marker for the RECIPIENT (the envelope) separate from the marker for the
PLATFORM (the column), which are two audiences that happen to agree today.

---

## `webhook_disable_notifications` — new

One row per automatic disablement. An outbound obligation the platform has not yet
met.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `id` | `uuid` | no | Primary key |
| `environment_id` | `uuid` | no | Tenant scope (constitution I) |
| `organisation_id` | `uuid` | no | Who is to be told. Resolved at write time through `environments.application_id → applications.organisation_id`. |
| `endpoint_id` | `uuid` | no | Which endpoint |
| `disabled_at` | `timestamptz` | no | When the disablement happened |
| `run_started_at` | `timestamptz` | no | The window that triggered it |
| `run_attempts` | `integer` | no | How many failures were in that window |
| `last_status` | `integer` | yes | What the endpoint last answered, when it answered |
| `last_error` | `text` | yes | What went wrong when it did not |
| `delivered_at` | `timestamptz` | yes | **Always null in this chapter.** Set when a transport exists. |

**Why `organisation_id` is denormalised.** The joins are available, so storing it
looks redundant. It is stored because the notification is a record of an
obligation *as it stood when the endpoint was disabled*, and an application moving
between organisations later must not silently retarget a notification that was
already owed to somebody else.

**`delivered_at` is the honest column.** It exists in this chapter solely to be
null. FR-WHK-07's "and the organisation notified by email" is unmet, and a schema
that recorded only the disablement would let a future reader believe the
requirement was finished.

**No index beyond the primary key and `environment_id`.** Volume is one row per
endpoint per outage.

---

## The attempt record — not a table

Attempts are published to JetStream, not stored (research R4, R5). The shape lives
in [contracts/attempts.md](./contracts/attempts.md). Recorded here so the absence
is deliberate rather than an omission:

- **Not in PostgreSQL.** The SAD calls this an analytical event, and constitution
  III keeps analytical volume out of the operational store.
- **Not queryable in this chapter.** Part 4's ingester consumes the stream into
  ClickHouse and gives it a query surface.
- **Not guaranteed.** Published after the outcome transaction commits, outside it.
  A crash in that gap loses the record and the delivery is unaffected, which is
  the trade constitution III asks for.

Auto-disable therefore reads the two columns above, never the stream. A backlogged
analytics path cannot delay a disablement, and a disablement cannot be blocked by
a broker being unwell.

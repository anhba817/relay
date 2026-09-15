# Data model — 052, chapter 4.7

The job writes nothing. Everything here is a shape it produces or a table it reads.

## The reconciliation report

One row per tenant, per period, per quantity.

| Field | Type | Meaning |
|---|---|---|
| `environmentId` | UUID | the tenant. **Never aggregated away** — R1 measured aggregation turning 19 breaches into one number under the bound |
| `period` | `YYYY-MM-DD` | the first day of a calendar month, UTC, from `periodOf` |
| `quantity` | one of four | `messages`, `activeUsers`, `connectionMinutes`, `storedMessages` |
| `analytical` | number \| null | from `daily_usage_billing`; null when the quantity has no rollup column |
| `operational` | number \| null | from Postgres; null when the quantity has no operational counterpart |
| `operationalSource` | string \| null | **which table**, named in the report — FR-003, because two candidates disagree by 0.2694% |
| `differencePct` | number \| null | null whenever either side is null |
| `verdict` | one of four | below |

## The four verdicts, and why there are four rather than two

| verdict | when | why it is not one of the others |
|---|---|---|
| `pass` | both sides present, difference within the threshold | — |
| `breach` | both sides present, difference over the threshold | — |
| `not-comparable` | the quantity has no operational counterpart at all | Reporting this as a breach would blame the analytical path for a column Postgres never had. R3: the **stored message count** is in this state permanently. |
| `no-data` | neither side has anything for this tenant and period | **Zero against zero is not agreement.** A reconciler that reports 0% here publishes a green number about a tenant it knows nothing about. |

**A tenant with data on exactly one side is a `breach`, not `no-data`.** R4 measured 675
operational tenants against 4 analytical, so 671 are in that state — and the temptation to
call it "missing data" is exactly what would hide the defect this movement exists to expose.

## What each quantity compares

| quantity | analytical | operational | source named in the report |
|---|---|---|---|
| messages | `sum(messages)` | `usage_periods.messages_sent` | `usage_periods` |
| active users | `uniqMerge(active_users_state)` | `count(*)` over `usage_active_users` for that `(environment_id, period)` | `usage_active_users` |
| connection-minutes | `sum(connection_minutes)` | `usage_periods.connection_minutes` | `usage_periods` |
| stored messages | `sum(stored_delta)` up to the period's end | **none** | — |

**`usage_active_users` is `(environment_id, period, user_id, first_seen_at)`** — one row per
user per period, so its total is a count of rows rather than a stored number. **That makes the
active-user comparison the only one comparing two different kinds of thing**: an exact count on
the operational side against `uniqMerge`'s approximate sketch on the analytical one. 047-1's
0.51% lives exactly here, and the report says so rather than presenting the difference as drift.

**`usage_periods.messages_sent` is chosen over a count of `messages`, and the reason is in the
code.** `repository.ts:4325`: *"the alternative is a read over `messages`, which carries no
`environment_id` and no index on `created_at` … proportional to lifetime traffic forever."*
Chapter 4.1 measured that read at 585.9 ms over 1,000,000 rows. **The rejected candidate is
published with its gap AND ITS CAUSE** rather than left unmentioned, because a reconciler that
silently picks one of two disagreeing numbers is asserting the other does not exist.

In this lane the gap is 0.2694% aggregate and 100% for one tenant, and **it is fixtures** —
raw-SQL writers and a sentinel cleanup that deletes counter rows, with every disagreeing tenant
a test application and none anything else. Publishing the number without the cause would make a
lane artifact read as a platform defect, which is 047's pass-9 lesson in a new feature.

## The threshold

`0.1%`, a named constant citing FR-ANL-06, not a literal.

**The verdict is decided before any arithmetic runs.** `no-data` and `not-comparable` are
settled from the presence of each side, and only a row with both sides present reaches a
division — which stops `0 / 0` from being a case anyone has to think about.

For those rows the comparison is
`abs(a − o) / max(a, o)` — **not divided by the operational side**, because the 671 one-sided
tenants have an operational total of zero for some quantities and a denominator of zero is a
crash where a verdict belongs.

## What the job reads, and what it must not touch

- `relay_analytics.daily_usage_billing` — the coarse rollup, keyed `(environment_id, day)`.
  **Not `daily_usage_v2`**: chapter 4.6 measured it at 147,534 rows against 281 for the same
  data, and the reconciler has no use for the channel dimension.
- `usage_periods`, `usage_active_users` — read-only.
- **No writes anywhere.** Two invocations with the same arguments produce the same report, and
  a test asserts it.

## Period boundaries

`periodOf` is the single definition — *"a quota that disagrees with itself about which month it
is counts a tenant twice in one and not at all in the other."* The job takes an **explicit**
period. Reconciling the current month compares a rollup still being written against a counter
still being incremented, which measures the clock.

And a period older than 90 days cannot be checked against raw events at all: the rollups carry
a 25-month TTL and `message_events` 90 days (DR-09, applied in chapter 4.6). That asymmetry is
the design rather than a fault, and it bounds what the job can verify rather than what it can
report.

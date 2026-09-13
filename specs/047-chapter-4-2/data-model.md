# Data model — chapter 4.2

Two tables and a view, all new, all in a store that has been in `compose.yaml` since chapter
1.2 and has never held a row.

---

## 1. `message_events` — the raw table

SAD §6.2's DDL, with **one divergence**, and the divergence is the document's:

| column | type | filled by this chapter? |
|---|---|---|
| `environment_id` | `UUID` | yes — from `channels.environment_id` |
| `channel_id` | `UUID` | yes |
| `user_id` | `UUID` | yes, including the nulls the corpus plants |
| `ts` | `DateTime64(3, 'UTC')` | yes — `messages.created_at` |
| `event` | `LowCardinality(String)` | `'created'` only; `edited` and `deleted` have producers in Part 3 and no analytical writer yet |
| `text_length` | `UInt32` | yes — `length(text)`, **never the text** (FR-ANL-11, DR-08) |
| `attachment_count` | `UInt8` | yes — the corpus writes no attachments, so every row is 0 |
| `delivery_latency_ms` | `UInt32` | **NO PRODUCER.** See below |

    ENGINE = MergeTree
    PARTITION BY toYYYYMM(ts)                     -- DR-07
    ORDER BY (environment_id, ts)                 -- DR-07, and 4.1's whole argument
    TTL toDateTime(ts) + INTERVAL 90 DAY          -- DR-09, and the divergence

**THE DIVERGENCE IS `toDateTime(ts)`, AND SAD §6.2 IS WRONG WITHOUT IT.** Copied verbatim the
statement is refused:

    Code: 450. TTL expression result column should have DateTime or Date type,
    but has DateTime64(3, 'UTC'). (BAD_TTL_EXPRESSION)

That DDL has been published since the SAD's first draft. The chapter amends §6.2 rather than
diverging silently.

**`delivery_latency_ms` HAS NO PRODUCER AND IS CREATED ANYWAY.** Zero matches for
`delivery_latency` or `deliveryLatency` anywhere in `packages/` or `services/`. It is
FR-ANL-10's column and FR-ANL-10 is a later chapter's. **3.23 and 3.24 both found readers with
no writers** — `message_edits` published and unbuilt, `messages.attachments` written only to
null — and this is the same shape one level out. Creating it silently is what makes it a
surprise three chapters from now; creating it and naming it is what makes it a schedule.

### The TTL removes rows at INSERT, not at merge

    inserted 120,000 rows spread over 120 days
    immediately after         90,000 rows · 0 older than 90 days
    after OPTIMIZE … FINAL    90,000 rows · 0 older than 90 days

**A corpus spanning `CORPUS_DAYS` = 120 loses a quarter of itself before anything queries it,
and nothing reports the loss.** The chapter states what the table holds rather than what was
loaded. The comparison against 4.1 is unaffected because 4.1 measured the in-window million —
**unaffected by luck**, and a reader loading a 365-day corpus would lose three quarters in
silence.

---

## 2. `daily_usage` — the rollup

DR-10: *"materialised views shall maintain daily per-tenant rollups for metering, so billing
never scans raw events."* SAD §6.2's view applies verbatim once the raw table exists.

| column | meaning |
|---|---|
| `environment_id` | the tenant |
| `day` | `toDate(ts)` |
| `messages` | `count()` where `event = 'created'` |
| `active_users_state` | `uniqState(user_id)` — an aggregate state, not a number |

    ENGINE = SummingMergeTree
    PARTITION BY toYYYYMM(day)
    ORDER BY (environment_id, day)

**Measured at the corpus's shape: 1,000,000 raw rows become 89 rollup rows.** That ratio is
DR-10's argument in one number.

### And the state is approximate, with a threshold that is a cardinality

| distinct users | `uniqExact` | `uniq` | divergence |
|---|---|---|---|
| 1,000 | 1,000 | 1,000 | exact |
| 60,000 | 60,000 | 60,000 | exact |
| **70,000** | **70,000** | **70,359** | **+0.51%** |
| 200,000 | 200,000 | 199,902 | −0.05% |

At the corpus's 5,000 distinct users, `uniqExact`, `uniq` and `uniqMerge(active_users_state)`
all return **5000**.

**AND THAT PUTS TWO PUBLISHED REQUIREMENTS IN CONFLICT.** FR-ANL-06 wants metered totals to
agree with operational counts **within 0.1%**. Above roughly 65,000 distinct senders in a
period, `uniq`'s own error exceeds that — so a reconciliation reading the rollup cannot satisfy
FR-ANL-06 for a large tenant, and one reading raw events contradicts DR-10.

**This chapter measures it and files it.** Movement IV's reconciliation chapter is where one of
the two clauses has to move; there is no reconciler here to test an amendment against. **The
threshold is a cardinality, not a row count**, which is why volume testing at 5,000 users would
never have found it.

---

## 3. `schema_applied` — the ledger

FR-011 wants schema changes that are idempotent **and report what they applied**. `CREATE …
IF NOT EXISTS` gives the first and not the second: it is silent about whether it did anything,
which is `check-fence-chain`'s zero-that-means-two-things in another costume.

| column | meaning |
|---|---|
| `filename` | the statement file, e.g. `0000_message_events.sql` |
| `applied_at` | when |
| `checksum` | of the file's bytes, so an edited file is visible rather than skipped |

`ENGINE = MergeTree ORDER BY filename`. **It lives in ClickHouse, not in Postgres**, and
nothing writes it to `schema_migrations` (FR-012). `gaps.md` 045-69 is what one runner reading a
version string it has never seen costs: seven byte-identical migrations under different numbers
and a lane that died in 0.6 s, three times.

---

## 4. How the rows get in

**ClickHouse reads Postgres directly**, and it was checked before it was planned:

    SELECT count() FROM postgresql('postgres:5432','relay','messages','relay','relay')
    -> 303885

which is the lane's exact message count. The load is one `INSERT … SELECT` joining `messages`
to `channels` for the tenant — **no client library, no export, no ETL, and no new dependency.**

The ingester will need a client. This chapter does not, and keeping the two decisions apart is
the point: a dependency added here would be justified by a chapter that does not use it.

---

## 5. What this chapter does not create

`webhook_attempt_events`, `api_request_events`, `connection_events` and `emoji_events` are all
named in FR-ANL-01, FR-ANL-07 and DR-14. **The analytics stream carries exactly one action
today** — `WEBHOOK_ATTEMPT_ACTION` — and `internal.ts`'s own comment says the ingester "does
not exist yet". SAD §6.2 calls its table "representative", and this chapter builds the one
4.1's question needs.

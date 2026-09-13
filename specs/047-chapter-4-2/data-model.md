# Data model — chapter 4.2

Two tables and a view, all new, all in a store that has been in `compose.yaml` since chapter
1.2 and has never held a row.

**They live in `relay_analytics`, and every statement says so.** The names below are written
bare for readability; on disk each one is qualified. `CLICKHOUSE_DB` creates that database
without making it the session default, so an unqualified `CREATE TABLE` builds this whole model
in `default` and reports success — see [contracts/schema.md](./contracts/schema.md).

---

## 1. `message_events` — the raw table

SAD §6.2's DDL, with **one divergence**, and the divergence is the document's:

**Every row of this table was checked against what `postgresql()` actually delivers, and three
of eight were wrong before it was.** The source types are not the ones the column names imply.

| column | type | source expression | what was wrong |
|---|---|---|---|
| `environment_id` | `UUID` | `channels.environment_id` | — arrives as `UUID` |
| `channel_id` | `UUID` | `messages.channel_id` | — arrives as `UUID` |
| **`user_id`** | **`Nullable(UUID)`** | `messages.user_id` | **arrives as `Nullable(UUID)`; SAD §6.2 says `UUID` and a NULL inserts as the ZERO UUID, silently** |
| `ts` | `DateTime64(3, 'UTC')` | `messages.created_at` | arrives as `DateTime64(6)`; microseconds truncate to milliseconds, no timezone shift — the server is UTC |
| **`event`** | `LowCardinality(String)` | **three rows per message, not one** | **the load wrote `'created'` for 4,056 deleted and 3,201 edited messages** |
| **`text_length`** | **`Nullable(UInt32)`** | **`lengthUTF8(text)`** | **`length()` is BYTES (FR-EMJ-02 counts code points), and `lengthUTF8(NULL)` inserts 0 into a non-nullable column** |
| **`attachment_count`** | **`Nullable(UInt8)`** | **`JSONLength(attachments)`** | **jsonb arrives as `Nullable(String)`; `length()` gave 151 for a 2-attachment row, and `JSONLength(NULL)` inserts 0** |
| `delivery_latency_ms` | `UInt32` | — | **NO PRODUCER.** See below |

### The three that were wrong, with what each returned

**`attachment_count`.** `attachments` is jsonb and arrives serialised as `Nullable(String)`, so
`length()` counts characters:

    attachments                                          length()   JSONLength()
    [{...first.png...},{...second.png...}]                    151              2
    [{...preview.png...}]                                      77              1

A `UInt8` holds 151 without complaint, so the wrong value would have been stored and charted.

**`text_length`.** ClickHouse's `length` is byte length and `lengthUTF8` is code points:

    'hello'       length 5    lengthUTF8 5
    'héllo 👋🏽'    length 15   lengthUTF8 8

FR-EMJ-02 says *"the message length limit (FR-MSG-01) shall be counted in Unicode code points,
and this shall be documented"*. **A `text_length` in bytes looks exactly like one in code points
until somebody charts it against FR-MSG-01's limit.**

**`user_id`, and this one invents data.** `messages.user_id` is nullable — FR-USR-05 keeps a
deleted user's messages *"as authored by a deleted user"*, and the corpus plants nulls at
`CORPUS_NULL_SENDER_RATIO` for exactly this reason. Inserting a NULL into SAD §6.2's
non-nullable `UUID` column **does not fail**:

    into UUID            10,000 rows in ·  2,928 became 00000000-0000-0000-0000-000000000000
    into Nullable(UUID)  10,000 rows in ·  3,226 stayed NULL

and `uniqExact` counts the zero UUID as **one distinct user**. Every environment holding a
deleted user's messages would gain one phantom active user, in silence.

**With `Nullable(UUID)`, `uniqExact` ignores the NULLs — which is what Postgres's
`count(DISTINCT user_id)` does too**, so the two sides of movement IV's reconciliation agree on
the one input `gaps.md` 046-1 filed as their divergence. The nullable column is not a
concession; it is the only shape under which the two stores can be compared.

**AND `user_id` WAS NOT THE ONLY NULLABLE SOURCE COLUMN.** Analysis pass 1 found this shape,
fixed that column, and did not ask the same question of the two beside it. `text` is NULL for
**4,057 tombstones** and `attachments` for **301,644 of 303,885 rows**, and both
`lengthUTF8(NULL)` and `JSONLength(NULL)` insert **0** into a non-nullable target without
complaint:

    tombstone rows in    text_length [0,0,0,0,0]    attachment_count [0,0,0,0,0]
    rows with content    text_length [3,14,12]      attachment_count [10,2,2]

**A `text_length` of 0 is a claim that a zero-length message was sent.** Both columns are
nullable now, and NULL means *not recoverable* rather than *zero*.

## 1a. The load reconstructs an event log from current state, and it cannot do it completely

**SAD §6.2's `event` column is `created|edited|deleted`, which means one row per EVENT.** The
first version of the load wrote `'created'` for every message row — so **4,056 deleted and
3,201 edited messages were labelled as creations**, and `daily_usage` filters on exactly that
label. FR-ANL-05 meters *messages sent*; the figure would have been over by 4,056.

The load now derives three rows from each message's state:

    created  303,885   at created_at
    edited     3,201   at edited_at, where it is not null
    deleted    4,056   at deleted_at, where it is not null
    total    311,142

**AND 3,282 OF THOSE CREATIONS HAVE NO RECOVERABLE `text_length`.** 4,057 messages are
tombstones and only **775** carry an edit row holding `prior_text`; chapter 3.23's schema says
why in as many words — *"writes no row here, because a tombstone has no text to preserve"*. The
length the message had when it was sent is gone.

**This is the argument for the ingester, arriving three chapters early.** FR-ANL-02 says
analytical events are emitted asynchronously **at the time they happen**, and the reason is
visible here: a store reconstructed from current state cannot recover what the state no longer
holds. **Every NULL `text_length` in this corpus is an artefact of reconstruction, and a real
ingester produces none** — it sees the send.

The chapter publishes the count rather than filling it in.

    ENGINE = MergeTree
    PARTITION BY toYYYYMM(ts)                     -- DR-07
    ORDER BY (environment_id, ts)                 -- DR-07, and 4.1's whole argument
    TTL toDateTime(ts) + INTERVAL 90 DAY          -- DR-09, and the divergence

**THERE ARE TWO DIVERGENCES FROM SAD §6.2, AND THE SECOND IS `user_id`.** The first is
`toDateTime(ts)`; the second is `Nullable(UUID)`, above. **A column that cannot hold what the
operational store holds cannot mirror it**, and the failure mode is silent invention rather
than a refusal.

**THE FIRST DIVERGENCE IS `toDateTime(ts)`, AND SAD §6.2 IS WRONG WITHOUT IT.** Copied verbatim the
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

### How it must be read, because the row count per key is not one

**`SummingMergeTree` holds one row per INSERT per key until a background merge collapses them.**
Three inserts of 1,000 messages on a single day leave **three rows** for that
`(environment_id, day)`:

    SELECT messages                        ->  1000  1000  1000
    SELECT any(messages)                   ->  1000
    SELECT sum(messages)                   ->  3000
    SELECT sum(messages) … GROUP BY day    ->  3000        truth: 3000

**The read contract is `sum()` with `GROUP BY`, and a bare column is wrong until a merge nobody
scheduled has happened.** `OPTIMIZE … FINAL` collapses them, and a query whose correctness
depends on somebody having run it is a query that is right in a demo and wrong in production.

**One shape is caught rather than silent.** Mixing the state column with a bare column —
`SELECT messages, uniqMerge(active_users_state) … LIMIT 1` — is refused with
`NOT_AN_AGGREGATE`, because `uniqMerge` forces an aggregate context. The trap only bites when the
state column is left out entirely.

**And the engine is right.** SAD §6.2's `SummingMergeTree` was expected to be a fifth divergence
and is not: across three parts, `uniqMerge(active_users_state)` returned **1,500** against the
raw table's `uniqExact` of 1,500, before and after `OPTIMIZE … FINAL`.

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

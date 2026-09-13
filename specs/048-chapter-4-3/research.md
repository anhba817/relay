# Research — chapter 4.3

Six questions, all answered by running something. The numbers here are re-measured in
Phase 1 rather than carried; what they settle is the *shape* of the chapter.

## R1 — Can the existing consumer runtime be reused? **In shape, not in its dedup.**

**Decision**: the ingester does not reuse `createConsumerRuntime` unchanged. Either its
claim is parameterised or a second runtime is written; the chapter says which and why.

**Rationale**: `services/api/src/consumer/runtime.ts` is genuinely reusable — it fetches in
batches, it takes a `filterSubject` that already defaults to `events.>`, and its own header
says it exists because *"a future consumer forgets to dedupe → double webhooks / double
metering"*, mitigated by *"a consumer template with dedup built in"*. That is exactly this
consumer's problem.

**And the dedup it has built in is a PostgreSQL transaction.**

    runtime.ts:195   result = await claimEvent(db, durable, parsed!.id, effect);
    repository.ts    db.transaction(... insert(consumedEvents)
                       .onConflictDoNothing({ target: [consumer, eventId] }) ...)

Constitution III keeps the operational and analytical paths apart, and FR-009 forbids this
ingester from writing Postgres on the ingestion path. **The template built to stop a future
consumer double-counting cannot be used by the consumer it was describing.** That is the
chapter's central design argument, and it is worth more than the code it saves.

## R2 — What does the publisher actually send? **Ten fields, two of them deliberately absent rather than null.**

    delivery_id · endpoint_id · environment_id · event_id · attempt
    attempted_at · latency_ms · outcome
    status?   error?          <- spread in only when present

**Rationale**: `shape()` is an allow-list, and its comment says why: *"An allow-list fails
closed when somebody adds a field; a spread fails open."* `exactOptionalPropertyTypes` is
on, so `status` and `error` are **absent keys, not explicit undefined** — *"the difference
is the whole meaning of 'nothing answered'."*

That maps to `Nullable` columns for those two and non-nullable for the rest, which is
chapter 4.2's argument arriving in a new table before anyone can get it wrong again: **zero
is a measurement and NULL is an absence.** A `status` of 0 would claim an endpoint answered
with status zero.

**And `latency_ms` here is not `delivery_latency_ms` there.** This one is how long an
endpoint took to answer a webhook. `message_events.delivery_latency_ms` is how long a
message took to reach a client, still has no producer, and this chapter does not give it
one (047-2 stays open).

## R3 — What are the stream's bounds? **Seven days, 1 GiB, `discard: old`.**

    ANALYTICS_MAX_AGE_NS = 7 * 24 * 60 * 60 * SECOND_NS
    MAX_BYTES            = 1024 * 1024 * 1024
    retention Limits · storage File · discard Old

NFR-REL-08 requires 24 hours; this holds seven days. The stream's own comment explains the
choice as *"long enough for an ingester to be down over a long weekend and short enough that
the stream does not quietly become the analytical database it is supposed to feed."*

**It was chosen while nothing consumed the stream.** FR-011 asks whether it still holds now
that something does — and what `discard: old` at 1 GiB means for the records dropped while
an ingester is down. The stream drops them silently; whether the ingester can even notice is
a question for Phase 4.

## R4 — Does `ReplacingMergeTree` solve the redelivery problem? **Yes, and R7 is why it is the only option that does.**

**This entry was written as a rejection and R7 reversed it.** Read it as the measurement it
is — the read-time cost is real — and read R7 for why that cost is the price of the only
mechanism that works here.

Measured on 25.3, a 1,000-row batch inserted twice with identical sorting keys:

    SELECT count()                 2000     the duplicate is physically present
    SELECT count() FINAL           1000     collapsed at read time
    after OPTIMIZE TABLE ... FINAL 1000     collapsed on disk

**This is chapter 4.2's `SummingMergeTree` finding one engine over.** There, the rollup held
one row per insert per key until a merge, so the read contract became `sum()` with
`GROUP BY`. Here the duplicate survives until a merge, so the read contract becomes `FINAL`
— and a bare `SELECT count()` over an attempt table double-counts every redelivered batch,
by a plausible number, until somebody disputes a bill.

**AND THE FIRST RUN OF THIS PROBE MEASURED NOTHING, FOR A REASON THAT WAS MINE.** It built
both batches with `generateUUIDv4()` in the `env` column, so the two inserts had different
sorting keys and were not duplicates at all. It reported 2,000 rows after `OPTIMIZE FINAL`
and looked like a finding about ClickHouse. **A duplicate test whose rows are not
duplicates measures nothing and says something.**

## R5 — Is there a mechanism built for at-least-once consumers? **There is one, and it cannot be used here. See R7 and R8.**

**Decision, SUPERSEDED**: insert with an `insert_deduplication_token` derived from the
batch's stream sequence range, into a table declared with
`non_replicated_deduplication_window`. **This does not work.** The measurements below are
sound; the inference from them was not, and R7 is the question this entry never asked.

    plain MergeTree, no window
      same token twice                  -> 1000 rows    the token did NOTHING

    MergeTree, non_replicated_deduplication_window = 100
      first insert,   token batch-7     ->  500 rows
      REDELIVERY,     token batch-7     ->  500 rows    the block is refused
      different data, token batch-8     -> 1000 rows

The redelivery is refused **at insert, by the server**, with no read-time cost and no
dependence on anyone running maintenance. That is strictly better than R4 for this shape of
problem.

**The trap is the first line.** Setting the token without the window gives no deduplication
and **no error** — the insert succeeds and the duplicate lands. It is this project's
favourite failure shape: a mechanism that looks configured and does nothing, reporting
success. The window is also **bounded**: a redelivery older than the last *n* blocks slips
through, so *n* is a design parameter to state and size, not a default to inherit.

## R6 — Where does the ingester live, and does anything test it?

`vitest.coverage.config.mts` collects `packages/*/src/**` and `services/*/src/**`. A
consumer written under `analytics/` would be collected by nothing — the same finding 046 and
047 both paid for. Under `services/` it is collected like every other service.

`services/` holds `api`, `dispatcher` and `gateway`. The SAD describes a fourth. Whether it
ships as a service directory or as a mode of an existing one is Phase 1's, but the coverage
globs are an input rather than an afterthought.

## R7 — Can a redelivery be handed back as the same batch? **No, and that kills R5's design.**

**Decision**: dedup on the record's natural key with `ReplacingMergeTree`, never on the
batch. `insert_deduplication_token` is not used.

**Rationale**: R5 proved the token works when you hand the server the same batch twice. It
never asked whether you *can*. Measured against a live JetStream pull consumer:

    original batch, max_messages=5   seqs 1,2,3,4,5              range 1-5
    retry with     max_messages=3    seqs 1,2,3                  range 1-3
    retry with     max_messages=10   seqs 4,5,1,2,3,6,7,8,9,10   range 4-10

**The retry comes back out of order and interleaved with newer messages.** The "sequence
range" is neither contiguous nor the same set, so the token differs and the duplicate is
inserted. DR-11's two-second bound makes it structural rather than incidental: with a time
bound, batch boundaries depend on arrival timing, so even a fixed `max_messages` regroups.

**One case does work**, and it is the one the plan had in mind: a retry with the *same*
`max_messages` returned exactly `1:m1 … 5:m5`, ahead of three newer messages. **A design
tested in one configuration is a design tested nowhere**, and that is the whole finding.

**The replacement was verified against the failure case rather than the happy one.** Three
differently-cut batches over the same 500 records, into a `ReplacingMergeTree` keyed on
`(environment_id, ts, delivery_id, attempt)`:

    batch {1..500}              count   500      FINAL 500
    regrouped retry {1..300}    count   800      FINAL 500
    regrouped retry {101..500}  count 1,200      FINAL 500

It works because **`ts` is `attempted_at`, a field of the record**, not the time it was
consumed — so the same record sorts to the same place however it arrives.

## R8 — What does `insert_deduplication_token` actually key on? **Itself. Not the content.**

    token tok-A, 500 rows 'first-*'    -> table holds 500
    token tok-A, 500 rows 'SECOND-*'   -> table holds 500, and 0 rows start 'SECOND-'

A second insert carrying the same token and **completely different data** was dropped
entirely, with no error. The token is a promise the caller makes, not a fact the server
checks.

**That makes R5's broken derivation dangerous rather than merely useless.** A range token
like `4-10` does not just fail to deduplicate its own batch — it can collide with a
different batch's range and silently discard it. **A token that is not provably unique per
batch is not weak deduplication; it is silent data loss**, and this is the second mechanism
in two features that reports success while doing nothing.

## What research did not resolve

- **How many records `discard: old` has already dropped.** The stream reports depth, not
  what it discarded. If the answer is "you cannot know", that belongs in the prose.
- **Whether seven days is still right** now that something consumes the stream (FR-011).
- **What `FINAL` costs on this table at the corpus's size.** R7 settles that it is the only
  mechanism that works; it does not say what the read is worth. The chapter measures it.

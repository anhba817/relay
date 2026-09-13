# Research — chapter 4.2

Eight questions, every one run against the ClickHouse in `compose.yaml` rather than recalled.
**Three of the eight found a published document wrong**, and one of those three is a conflict
between two requirements that no amount of reading would have produced.

---

## R1 — Can anything outside the container query it? **No, and the health check says otherwise.**

`clickhouse/clickhouse-server:25.3` has been in `compose.yaml` since chapter 1.2 with a
`/ping` health check that has passed on every `docker compose up` since. From the host:

    $ curl -s "http://localhost:8123/ping"                 -> Ok.
    $ curl -s "http://localhost:8123/?query=SELECT+1"
      Code: 194. Authentication failed: password is incorrect, or there is no user
      with such name. (REQUIRED_PASSWORD)

The image ships `/etc/clickhouse-server/users.d/default-user.xml`:

```xml
<default>
  <!-- User default is available only locally -->
  <networks><ip>::1</ip><ip>127.0.0.1</ip></networks>
</default>
```

**The `default` user is loopback-only inside the container.** From inside,
`clickhouse-client` answers `25.3.14.14 default`. Through the published port mapping, every
query is refused — and `/ping` neither authenticates nor is network-restricted, so the health
check is green while the service is unusable.

**Decision**: the chapter gives the container a user it can be reached as, which means
**amending `compose.yaml`** — a file chapter 1.2 fences under an additive-only rule. The
amendment is additive (an `environment:` block and a health check that runs a query), so the
rule holds.

**Rationale**: this is `docs/07`'s own defect class from the other side. CLAUDE.md records
*"a health check that has never passed"* — `membership` and `presence` probed `/health` where
the api serves `/healthz`, and both loops returned success anyway. **Here the probe passes and
the thing behind it cannot be used.** A health check that cannot fail for the reason you care
about is the same defect wearing the opposite sign.

**Alternatives considered**: running every query through `docker exec` — works, and makes the
chapter's commands unrunnable by a reader who deploys ClickHouse anywhere else. Leaving the
health check alone and documenting the exec form — rejected for the same reason.

---

## R2 — Does SAD §6.2's published DDL apply? **No.**

Copied verbatim from the architecture document, where it has sat since the first draft:

    Code: 450. TTL expression result column should have DateTime or Date type,
    but has DateTime64(3, 'UTC'). (BAD_TTL_EXPRESSION)

`TTL ts + INTERVAL 90 DAY` on a `DateTime64(3, 'UTC')` column is rejected. The table creates
with `TTL toDateTime(ts) + INTERVAL 90 DAY`, and the materialised view then creates verbatim.

**Decision**: build from §6.2 and record the one divergence as an amendment, per the
governance rule that a falsified clause is amended rather than silently diverged from.

**Rationale**: `docs/05-sad.md` is a published document a reader can copy from. **Four
chapters have now found a published DDL or clause that does not survive contact** — 3.23's
`message_edits`, 3.24's `attachment_count`, 045's migration identity, and this. The pattern is
that DDL nobody executed is DDL nobody checked.

---

## R3 — When does the 90-day TTL remove rows? **At insert, not at merge.**

The corpus spans 120 days (`CORPUS_DAYS`), and DR-09 retains raw events for 90.

    inserted 120,000 rows spread over 120 days
    immediately after insert:  90,000 rows · 0 older than 90 days
    after OPTIMIZE … FINAL  :  90,000 rows · 0 older than 90 days

**A quarter of the corpus is gone before anything queries it, and nothing reports it.**

**Decision**: the chapter loads and then states what the table holds, rather than asserting
what it loaded. The in-window million is what 4.1 measured, so the comparison is unaffected —
but it is unaffected *by luck*, and a reader loading a 365-day corpus would lose three
quarters of it in silence.

**Rationale**: this is 4.1's own lesson arriving in the second store. Chapter 4.1 spent two
analysis passes on the gap between the volume asked for and the volume the query sees; here
the store itself removes rows between the two.

---

## R4 — Is the rollup's distinct count exact? **Exact to 60,000, and then it is not — and FR-ANL-06's bound is tighter than its error.**

`uniqState`/`uniqMerge` against `uniqExact`, a million rows, varying cardinality:

    distinct     uniqExact      uniq        divergence
       1,000         1,000     1,000        exact
      60,000        60,000    60,000        exact
      70,000        70,000    70,359        +359   (0.51%)
     200,000       200,000   199,902        -98    (0.05%)

At 5,000 distinct users over a million message rows — the corpus's shape —
`uniqExact`, `uniq` and `uniqMerge(active_users_state)` all return **5000**.

**AND THIS IS A CONFLICT BETWEEN TWO PUBLISHED REQUIREMENTS.** DR-10 says materialised views
maintain the rollups **"so billing never scans raw events"**. FR-ANL-06 says metered totals
**"shall agree with counts derived from operational data to within 0.1%"**. Above roughly
65,000 distinct senders in a period, `uniq`'s own error exceeds 0.1% — so a reconciliation
that reads the rollup cannot satisfy FR-ANL-06 for a large tenant, and one that reads raw
events contradicts DR-10.

**Decision**: this chapter measures it, publishes the threshold, and **files the conflict for
movement IV** — the reconciliation chapter is where one of the two clauses has to move. It is
not resolved here, because resolving it means amending a requirement and this chapter has no
reconciler to test the amendment against.

**Rationale**: the threshold is a *cardinality*, not a row count, which is why no amount of
volume testing at 5,000 users would have found it. The corpus's shape hides it exactly.

**Alternatives considered**: `uniqExactState` in the rollup — exact, and stores every
identity, which is a per-tenant unbounded state and a privacy surface FR-ANL-11 exists to
avoid. Not this chapter's to choose.

---

## R5 — How is "skipped" observed? **`EXPLAIN indexes=1`, and it is three stages.**

Three environments of 400,000 rows each, one named in the predicate:

    Condition: (ts in ['…', +Inf))                              Parts: 12/12  Granules: 147/147
    Condition: (toYYYYMM(ts) in [202606, +Inf))                 Parts: 12/12  Granules: 147/147
    Condition: and(ts …, environment_id in ['…02','…02'])       Parts:  4/12  Granules:  49/147

**The MinMax index and the partition key skip nothing; the primary key skips two-thirds.**
That is `ORDER BY (environment_id, ts)` doing the work, and it is the figure FR-010 asks for.

**Decision**: `EXPLAIN indexes=1` is the chapter's instrument, and the parts-and-granules line
is published beside every duration.

**Rationale**: `ProfileEvents['SelectedParts']` in `system.query_log` returned **0** for the
same query, so the obvious instrument reports nothing and reports it silently. **A duration
alone cannot distinguish an ordered store from a fast one**, and at this size ClickHouse
answers a full scan quickly enough to look ordered.

---

## R6 — How does the corpus get in? **ClickHouse reads Postgres directly.**

    SELECT count() FROM postgresql('postgres:5432','relay','messages','relay','relay')
    -> 303885

which is the lane's exact message count. The load is one `INSERT … SELECT`.

**Decision**: no client library, no export, no ETL step. **This chapter adds zero
dependencies.**

**Rationale**: constitution VII asks for the smallest number of moving parts, and the
lockfile contains no ClickHouse client today. A Node client would be a new dependency, a new
DI token and a new failure mode, for a chapter that writes no service. **The ingester will
need one; this chapter does not, and saying so now keeps the two decisions apart.**

**Alternatives considered**: `@clickhouse/client` — correct for movement II's ingester and
premature here. `clickhouse-client` piping a CSV — more moving parts than a table function.

---

## R7 — Is there a column nothing can fill? **Yes, one.**

`delivery_latency_ms` appears in SAD §6.2 and nowhere in `packages/` or `services/` — zero
matches for `delivery_latency` or `deliveryLatency` in the whole tree. It is FR-ANL-10's
column, and FR-ANL-10 is a later chapter's.

**Decision**: create it, and name it in the chapter as having no producer.

**Rationale**: 3.23 and 3.24 both found *readers with no writers* — `message_edits`
published in the SAD since the first draft and never built, `messages.attachments` a column
whose only writer set it to null. **This is the same defect one level out**: a column created
now and filled in three chapters. Creating it silently is what makes it a surprise;
creating it and saying so is what makes it a schedule.

---

## R8 — What does the analytics stream carry today? **One action.**

`packages/protocol/src/internal.ts` defines `analytics.{domain}.{action}.{environment_id}`,
`ANALYTICS_STREAM`, and exactly one action constant — `WEBHOOK_ATTEMPT_ACTION`. Its own
comment says *"Part 4's ingester is that consumer, and it does not exist yet."*

**Decision**: the chapter builds `message_events`, not a webhook-attempt table, and names the
others as later chapters'. The stream is not touched.

**Rationale**: SAD §6.2 calls its table "representative" and FR-ANL-01 names four event kinds.
Building the one 4.1's question needs keeps this chapter to a schema and a comparison.

---

## R9 — What does `postgresql()` actually deliver? **Three of eight columns are not the type the name implies.**

Added by analysis pass 1, which ran the mapping R6 had only proved *reachable*.

    source column      arrives as            the obvious expression, and what it gives
    id, channel_id     UUID                  —
    user_id            Nullable(UUID)        into SAD's `UUID`: the ZERO UUID, silently
    created_at         DateTime64(6)         truncates to (3); no shift, the server is UTC
    text               Nullable(String)      length() = BYTES, not code points
    attachments        Nullable(String)      length() = 151 for a two-attachment row

**Decision**: `lengthUTF8(text)`, `JSONLength(attachments)`, and **`user_id Nullable(UUID)`** —
a second amendment to SAD §6.2.

**Rationale, measured:**

    into UUID            10,000 rows ·  2,928 became 00000000-0000-0000-0000-000000000000
    into Nullable(UUID)  10,000 rows ·  3,226 stayed NULL

`uniqExact` counts the zero UUID as one distinct value, so **every environment holding a
deleted author's messages would gain one phantom active user** with no error anywhere. With the
nullable column, `uniqExact` ignores the NULLs — which is exactly what Postgres's
`count(DISTINCT user_id)` does, so the two sides of movement IV's reconciliation agree on the
one input `gaps.md` 046-1 filed as their divergence.

`length('héllo 👋🏽')` is **15** and `lengthUTF8` is **8**. FR-EMJ-02 requires the message length
limit to be counted in code points, so a byte-valued `text_length` disagrees with the platform's
own definition for every non-ASCII message — **and looks identical to a correct one**.

**How it was found, because the method is the finding**: R6 asked whether `postgresql()` could
*read* Postgres and stopped when it returned the right count. **Reachability is not mapping.**
`data-model.md`, `contracts/schema.md` and `tasks.md` then agreed with each other that
`length()` gave what the column meant, which is three artifacts consistent about a type none of
them had checked.

## R10 — Does the compose fix lift `default`'s restriction? **No. It adds a user.**

    CLICKHOUSE_USER=relay  ->  relay answers from the host
                               default still returns REQUIRED_PASSWORD

**Decision**: the amendment adds `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`, `CLICKHOUSE_DB` and
says so. The shipped `users.d/default-user.xml` is left alone.

**Rationale**: the two are different repairs and only one is ours to make. Someone reading "a
user reachable from outside it" and trying to fix `default` ends up editing a file the image
owns, which the next image tag overwrites.

## R11 — Is the analytical table one row per message, or one per event? **One per event, and the load cannot reconstruct them all.**

Added by analysis pass 2, which asked pass 1's nullable question of the two columns pass 1 had
not asked it about — and found a third thing while counting.

**`user_id` was not the only nullable source column.**

    text NULL (tombstones)      4,057 of 303,885
    attachments NULL          301,644 of 303,885
    user_id NULL               20,541 of 303,885

`lengthUTF8(NULL)` and `JSONLength(NULL)` both insert **0** into a non-nullable target, without
complaint. **A `text_length` of 0 is a claim that a zero-length message was sent.**

**And `event` was a literal.** SAD §6.2's column is `created|edited|deleted` — one row per
event — and the load wrote `'created'` for every message row, including 4,056 deleted and 3,201
edited ones. `daily_usage` filters `WHERE event = 'created'`, so **FR-ANL-05's messages-sent
figure would have been over by 4,056**.

**Decision**: three nullable columns, and three rows per message where the state supports them.

    created  303,885   ·  edited  3,201  ·  deleted  4,056   =   311,142 rows

**AND 3,282 CREATIONS HAVE NO RECOVERABLE `text_length`.** 4,057 messages are tombstones and
only 775 carry an edit row with `prior_text`; `schema.ts:454` says why — *"writes no row here,
because a tombstone has no text to preserve"*.

**Rationale, and it is the ingester's argument arriving three chapters early.** FR-ANL-02 says
analytical events are emitted asynchronously **at the time they happen**. The reason is visible
here: **a store reconstructed from current state cannot recover what the state no longer
holds.** Every NULL `text_length` in this corpus is an artefact of reconstruction; an ingester
that sees the send writes a length every time, and a NULL from one would mean something upstream
lost the event.

**How it was found**: by counting the nulls in every source column rather than the one that had
already broken. Pass 1 found the shape and fixed one instance of it — **the fix is where the
next defect is**, and this is the second feature in a row to demonstrate that.

## What research did not resolve

- **The schema ledger's shape (FR-011/FR-012).** ClickHouse has `CREATE … IF NOT EXISTS`, which
  is idempotent and reports nothing. A ledger that says *what it applied* needs somewhere to
  record it, and where that lives — a ClickHouse table, a file, or the applying script's own
  output — is a Phase 1 decision.
- **Whether DR-10 or FR-ANL-06 moves.** R4's conflict is filed, not settled.

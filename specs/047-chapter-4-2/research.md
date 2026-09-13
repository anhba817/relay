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

## What research did not resolve

- **The schema ledger's shape (FR-011/FR-012).** ClickHouse has `CREATE … IF NOT EXISTS`, which
  is idempotent and reports nothing. A ledger that says *what it applied* needs somewhere to
  record it, and where that lives — a ClickHouse table, a file, or the applying script's own
  output — is a Phase 1 decision.
- **Whether DR-10 or FR-ANL-06 moves.** R4's conflict is filed, not settled.

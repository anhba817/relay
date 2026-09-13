# Contract — `scripts/scale/corpus.mjs`

The seeder outlives the chapter that introduces it. Movement IV's reconciliation milestone will
need a volume at which 0.1% is a real threshold, and this is the thing it would reach for.

**SC-006 used to say that movement IV reuses this unmodified, and it no longer does.** That claim
is about a chapter nobody has written, so it cannot be verified here; it moved to this feature's
`gaps.md` for the chapter that can settle it, and SC-006 now asks only that the interface be
published, that nothing import it, and that it produce what it says at three volumes. **The
interface is written down anyway** — because the last corpus this project built left nothing
behind at all (`specs/034-chapter-3-15/baseline.txt:153`), and a published interface is the
cheapest thing that stops that happening twice.

## Invocation

```
RELAY_POSTGRES_PORT=15432 node scripts/scale/corpus.mjs
```

Configured by environment variable, matching `seed.mjs` and `load.mjs` beside it. **No
`DATABASE_URL`**: the seeder connects to the default database only long enough to
`CREATE DATABASE`, then reconnects to the one it made and migrates that. An earlier version of
this line showed a `DATABASE_URL` and contradicted three rows below it.

| variable | default | meaning |
|---|---|---|
| `CORPUS_DATABASE` | `relay_corpus_<YYYYMMDDHHMMSS>` | **the database it creates**, matching `/^[a-z][a-z0-9_]{0,62}$/` and refused otherwise — the name goes into `create database "…"` and nothing else can escape it. A default nobody passes makes every run a fresh corpus; passing the same value twice is what reaches the refusal below, and is the only way to reach it |
| `CORPUS_MESSAGES` | `1_000_000` | message rows the analytical query **scans**: in the subject environment **and inside the 90-day window**. The seeder writes `CORPUS_DAYS / 90` times that many across the full span — 1,333,334 at the defaults — so the date predicate has a quarter to exclude and the number still means what the query sees. Each non-subject environment receives a tenth of the subject's total |
| `CORPUS_CHANNELS` | `2_000` | channels **in the subject environment**; neighbours get a tenth |
| `CORPUS_USERS` | `5_000` | people **in the subject environment** the seeded messages are authored by; neighbours get a tenth. **Not senders** — a `kind = 'person'` user cannot send through an application credential, and the one row that can is `send_target.bot` |
| `CORPUS_MEMBERSHIPS_PER_USER` | `2` | channels each user belongs to. **Not a term in the analytical query** — that joins `messages` to `channels` and never reads `channel_members`. It is a parameter because the send path needs the bot to be a member and because it sizes a real table, and it was introduced with the opposite reason attached |
| `CORPUS_ENVIRONMENTS` | `3` | environments; the first is the measurement subject. **Refused below 2** — see the bounds below |
| `CORPUS_DAYS` | `120` | days `created_at` spreads across, **ending at seed time** — wider than the 90-day query so the range predicate excludes something. The query anchors on `now()`, so **measure on the day you seed**: a week later the window covers 83 days of corpus and the number moves with the calendar |
| `CORPUS_NULL_SENDER_RATIO` | `0.01` | fraction of messages with `user_id IS NULL`, so R4's divergence is present rather than assumed absent |

### Two bounds, both strict, both refused rather than warned

**`CORPUS_ENVIRONMENTS` must exceed 1 and `CORPUS_DAYS` must exceed `90`.** One environment
leaves `WHERE c.environment_id = $1` nothing to exclude; a span equal to the window leaves
`AND m.created_at >= now() - interval '90 days'` nothing to exclude. **A corpus that satisfies a
predicate vacuously measures its cost at zero and reports a number anyway**, which is the defect
this chapter is about arriving inside its own harness.

Both were implied by this document and stated by neither, until T011 was written and the code had
to decide. The first draft of the guards used `>= 1` and `>= 90` — accepting exactly the two
configurations the rationale forbids — and the boundary probes are what caught it. Refusing is
the right error to make here: a refusal costs somebody a flag, and an acceptance costs a
published figure that looks like a measurement of two predicates and is a measurement of one.

## Output

One JSON object on stdout, and it is the record every measurement quotes:

```json
{
  "database": "relay_corpus_20260912",
  "subject_environment_id": "…",
  "credential": "…",
  "send_target": { "channel": "…", "bot": "corpus-bot" },
  "subject": {
    "messages_in_window": 1000000, "messages": 1333334,
    "channels": 2000, "users": 5000
  },
  "created": {
    "organisations": 1, "applications": 3, "environments": 3,
    "users": 6000, "bot_users": 1, "channels": 2400, "members": 12001,
    "api_keys": 1, "messages": 1600000, "messages_null_sender": 16047
  },
  "created_at_range": ["2026-05-15T…", "2026-09-12T…"],
  "elapsed_ms": 000
}
```

**`credential` and `send_target` are why this is a contract and not a print statement.** The send
loop authenticates with the first and addresses the second, and `scripts/scale/seed.mjs` has
emitted its own equivalents since it was written. A seeder that builds a corpus no client can
reach is a corpus nothing can measure.

**`send_target.bot` is not a convenience.** An application credential may send only as a bot
(FR-MSG-13), so a `kind = 'person'` sender is refused 403 `sender_not_permitted`. The bot is
created with `upsertUser(externalId, { kind: "bot", description })` — `createUser` has no `kind`
parameter — and is a member of `send_target.channel`.

**Three message counts, and the chapter quotes `subject.messages_in_window`.** `created.messages`
is every row in the database. `subject.messages` is the measured environment's. **Only
`messages_in_window` is what the query touches**, because two predicates stand between them:

    created.messages            1,600,000   every row
      └ environment_id = $1     1,333,334   the tenant predicate excludes the neighbours
          └ >= now() - 90d      1,000,000   the date predicate excludes a quarter

**Three things in this block were wrong until the seeder ran.** `applications` was 1:
`unique (application_id, kind)` is FR-TEN-04 — exactly two environments per application —
so three environments need three applications under one organisation, and the first run
died on 23505. `channel_members` was a table that does not exist; it is `members`, and
`memberships` is a different table holding humans in organisations. And
`messages_in_window` is **approximate**: `created_at` is a uniform random offset, so the
count inside the window is binomial around three quarters rather than exactly it — at the
defaults that is ±0.05%, and the seeder reports what landed rather than what was asked for.

**Rounding is `ceil` on the subject and `floor` on each neighbour**, stated because the three
numbers above only add up under that pair — `round` on the subject gives 1,333,333 and the total
misses by one. An unstated rounding rule is how two people implement the same table differently
and neither is wrong.

**A duration published against the first would claim 1.6 million rows and measure 1.** The
tenant half of that was found in analysis pass 7 and the date half in pass 8 — the same defect,
two lines apart in this table, and fixing the first did not prompt anybody to ask the second.

**It reports what it created, not what it was asked for.** A measurement that quotes its
parameters is quoting an intention; one that quotes this block is quoting the corpus. The two
differ whenever rounding spreads rows unevenly, and `messages_null_sender` is counted rather than
derived from the ratio for the same reason.

## Behaviour

| | |
|---|---|
| **Idempotence** | It is **not** idempotent and does not pretend to be. A run naming a `CORPUS_DATABASE` that already holds a corpus **refuses** and names what it found. Adding to a corpus silently would make every published number unattributable. **The default makes this unreachable by accident and passing the same name makes it reachable on purpose**, which is what T047a does — a refusal nobody can trigger is a branch nobody can test. |
| **Failure** | Partial state is left in place and named on stderr — the database, how to drop it, and the cause. A half-built corpus that looks empty is worse than one that says what it is, and dropping on failure would take the evidence with it. A half-built corpus that looks empty is worse than one that says what it is. |
| **Schema** | It creates `CORPUS_DATABASE` **and migrates it**, by running `services/api/dist/db/migrate.js` with `DATABASE_URL` pointed at it — the one place a `DATABASE_URL` appears, set by the script rather than by the caller. It hand-writes no DDL: the corpus carries the schema the platform ships. Requires `pnpm build` first, because the runner is `dist`. |
| **Ordering** | Parents before children, so no FK is ever violated and no constraint is deferred. |
| **Sequences** | `(channel_id, sequence)` is unique (DR-01). Sequences are allocated per channel from 1. |
| **Isolation** | It creates `CORPUS_DATABASE` and refuses if that name is the lane's. The default is date-stamped, so the collision needs somebody to ask for it. |
| **Quotas and outbox** | Untouched. No `usage_periods` row, no outbox row, no event. The corpus is data, not history. |

## What it is not

- Not a fixture. Nothing in `test` or `test:integration` calls it, and a million rows inside the
  lane would break the whole-table assertions 045-74 spent a feature finding.
- Not a demo seeder. `scripts/seed-demo-tenant.mjs` already exists for that and creates a
  coherent tenant a person can log into. This creates volume.
- Not a load generator. `load.mjs` is the socket ladder and `measure.mjs` is the send loop; this
  writes rows and exits.

## The stability the contract actually promises

Movement IV may pass different volumes. It may not need new variables, a different output shape,
or a second mode. **If it does, the finding is that this contract was written by one caller** —
which is 045's deferral lesson one level down: *a deferral justified by a comment is a deferral
justified by one caller's opinion of why the code exists.*

# Research: the fault that only shows up in company

Every finding below was measured, not reasoned about. Two of them changed the
design the spec assumed.

---

## R1 — The developer's database is already adversarial. CI is not.

Measured on the machine that shipped chapters 3.5 through 3.9:

```
outbox unpublished           190
deliveries due             8,364
notifications undelivered     14
endpoints sweepable           35
environments total        17,542
```

The lane passes here. It also passes on a database created and migrated seconds
earlier. Both are true because chapters 3.7 and 3.8 fixed all five reader-shape
instances — so neither condition is currently detecting anything.

That matters for what this feature is *for*. A long-lived developer database
supplies the adversarial condition by accident; a fresh clone and CI do not. So a
**new** reader-shape fault written today passes on CI and on a colleague's fresh
checkout, and fails months later on somebody's aged laptop. The bait's job is to
make fresh behave like aged, which is the reverse of the intuition that a clean
database is the safer place to test.

## R2 — The bait is eaten in a single lane run

Planted 200 unpublished outbox rows, 200 due deliveries, 200 undelivered
notifications and one sweepable endpoint on a fresh database, then ran the api
integration lane once:

```
outbox bait unpublished                0     (200 published)
sentinel notifications undelivered     0     (201 delivered)
sentinel endpoint still enabled        0     (swept)
sentinel deliveries still due        200     (survived)
```

Three of the four baits were gone after one pass. Only the deliveries survived,
and only because most suites run with `RELAY_DELIVERY_RELAY=off`.

**A one-shot `globalSetup` seeder therefore protects whichever suite runs first
and nothing after it.** Planting has to happen per file. This was not in the
spec's assumptions and it is the reason `outbox.itest.ts` failed in the lane and
passed when re-run alone — by then there was no bait left to fail against.

## R3 — Fresh plus bait broke two tests of 177

| Suite | Test | Shape |
|---|---|---|
| `outbox.itest.ts` | invariant 7: the relay publishes pending rows, marks them, and does not republish | reader — the relay's default batch of 100 never reaches this test's own rows |
| `notifications.itest.ts` | sends what the organisation needs | not a reader fault at all — see R4 |

Two, not twenty. The reader shape is better defended than expected, because 3.7
and 3.8 fixed it five times. What the bait protects is the *next* one.

## R4 — The bait changed a suite's workload, not just its arithmetic

`notifications.itest.ts` timed out at 10 seconds. Its relay drains with
`batchSize: 10_000`, so the 200 bait notifications became 200 SMTP sends to the
sentinel address before the test's own row was reached.

That is a different failure from the one the bait is designed to cause. Bait has
to be **cheap to process as well as visible**: the sentinel organisation should
have no addressable member, so each bait notification costs one log line and no
SMTP round trip. Which consumes the bait — looping straight back to R2.

## R5 — Legitimate global operations trip the guard immediately

The sentinel endpoint was disabled by an ordinary lane run. No deliberate fault,
no mutation written for this feature — six suites drive global drains and sweeps
on purpose:

```
services/api/src/outbox/outbox.itest.ts
services/api/src/webhooks/deliveries.itest.ts
services/api/src/webhooks/test-event.itest.ts
services/api/src/webhooks/attempts.itest.ts
services/api/src/notifications/notifications.itest.ts
services/dispatcher/src/dispatcher.itest.ts
```

So the exemption list is a **precondition, not a refinement**. A guard shipped
without it fails the lane on its first run for the right reason and the wrong
suite.

## R6 — THE DESIGN CHANGED: a database trigger attributes; a checksum cannot

The spec assumed a before/after comparison of the sentinel rows around each test,
and conceded in its assumptions that attribution would need serial execution
because integration files run in parallel — a test comparing the sentinel around
itself can observe a mutation another file performed and blame itself.

Combined with R5, that concession is fatal rather than awkward: legitimate global
sweeps happen constantly, so a run-scoped checksum would fire on almost every run
and a test-scoped one would blame bystanders.

A trigger does not have the problem, because it raises **inside the transaction
that did the damage**:

```
NON-EXEMPT session:
  ERROR:  global-operation guard: this statement modified sentinel row
          public.webhook_endpoints (id 00000000-…-000000000005),
          which belongs to no test
  CONTEXT:  PL/pgSQL function __sentinel_guard() line 4 at RAISE

EXEMPT session (SET relay.allow_global = 'on'):
  UPDATE 1
```

Verified against the real schema. The properties this buys:

- **Attribution is exact.** The error surfaces in the offending test's own stack,
  under parallel execution, with no serial diagnosis mode.
- **It catches raw SQL.** A lint rule and a wrapped import both miss a global
  `UPDATE` written by hand; the database does not.
- **Exemption is per session**, set by the lane's setup file from an auditable
  list of files.
- **It makes the bait durable.** A non-exempt suite cannot eat what it cannot
  modify, which softens R2: re-planting is only needed after an exempt suite runs.

The trigger belongs to the test lane, not to the product. It is created by the
lane's setup against a test database, never by a product migration — otherwise
Relay ships a trigger whose only purpose is to break its own test suite.

**Decision**: replace the checksum guard with a trigger. The spec's FR-006 to
FR-011 keep their meaning; the mechanism named in its assumptions is wrong and is
superseded here.

**Alternatives rejected.** Wrapping the repository's exports in the setup file
(catches indirect calls, misses raw SQL, and generic path resolution across test
files is awkward). Making the product functions refuse to run under a test flag
(puts test logic in shipped code — constitution VII). Per-suite databases
(chapter 2.1 chose one deliberately, and all seven findings are real
production-shaped problems isolation would hide).

## R7 — The bait's sizes must come from the constants

The largest default batch in the codebase is 100, in two places:

```
services/api/src/outbox/relay.ts:19          BATCH_SIZE = 100
services/api/src/webhooks/delivery-relay.ts  BATCH_SIZE = 50
services/api/src/notifications/…-relay.ts    BATCH_SIZE = 20
services/api/src/db/repository.ts:1142       limit = 100   ← the last default
```

A literal in the seeder goes stale the first time one of those rises. The seeder
derives its sizes from the exported constants, so a raised default raises the
bait with it.

## R8 — `sweepDisabledEndpoints` is the only remaining default

`drainOutbox`, `drainDueDeliveries` and `drainDisableNotifications` all require a
limit; chapter 3.8's T044 established the rule for the newest of them. The sweep
kept its `limit = 100` and is instance 6's proximate cause — not because 100 was
too small, but because omitting the argument let the author skip the question
"of whose rows?" entirely.

Worth stating plainly: **removing the default would not have prevented instance
6.** `sweepDisabledEndpoints(db, 10_000)` is worse, not better. The required
argument is a prompt to think, not a control. The trigger is the control.

## R9 — The lint restriction has an existing shape to copy

`eslint.config.mjs` already restricts `pg`, `drizzle-orm` and `ioredis` by module
path with an ignores list. `no-restricted-imports` also accepts `importNames`, so
the same block can name the global admin functions without banning the repository
module wholesale. It catches the import line — where the decision is actually
made — and misses indirect calls and raw SQL, which is why it is the third
defence and not the first.


---

# Findings from the first analysis pass

R1 to R9 were written before `tasks.md` existed. The pass that followed it opened
the test harness's runtime mechanics — pooling, parallelism, and the other lanes
sharing the database — which none of R1 to R9 had looked at. It found three
CRITICAL problems in the design R6 declared solved.

## R10 — The trigger works in one session and not in a pool

R6 verified the trigger in `psql`: one connection, one session, one `SET`. That is
the one condition the test lane never provides.

`createPool()` returns a bare `pg.Pool`, and a pool rotates connections. Measured
across five checkouts from a pool of three:

```
plain pool, after one SET on one connection: [null,null,null,null,null]
plain pool, after SET via pool.query:        ["on",null,null,"on",null]
connection-string options, every conn:       ["on","on","on","on","on"]
config-object options, every conn:           ["on","on","on","on","on"]
```

The second line is the bug. `SET relay.allow_global = 'on'` issued through
`pool.query()` lands on whichever connection the pool hands out, so two of five
checkouts carried the exemption and three did not. An exempt suite would fail
intermittently, in a way that looks exactly like the flakiness this feature exists
to remove.

**Decision**: set it as a connection option, so every connection the pool opens
carries it. `options` is honoured both in the connection string and in the config
object; the connection string wins because it needs **no product change** — the
setup file rewrites `process.env.DATABASE_URL` for its own worker before the suite
calls `createPool()`, and `createPool()` reads that variable.

**Alternative rejected**: adding an `options` parameter to `createPool()`. It is a
small passthrough rather than test logic, so it would not violate the
no-test-logic-in-product rule — but it changes a function every service calls in
order to serve a lane, and the environment variable already carries the address.

## R11 — The trigger is database state; the exemption is process state

They have different lifetimes, and the mismatch is the second CRITICAL.

The trigger, once installed, belongs to the database. Every lane pointed at that
database meets it. The exemption is supplied by a vitest hook, and only two lanes
were given one: the api's and the dispatcher's integration configs.

The lanes that share the database and were not given the hook:

| Lane | Config | Touches the database |
|---|---|---|
| coverage | `vitest.coverage.config.mts` | **every `*.itest.ts` in one process**, no `setupFiles`, no `globalSetup` |
| gateway integration | `services/gateway/vitest.integration.config.mts` | `session.itest.ts`, `limits.itest.ts` |
| e2e | `packages/e2e/vitest.integration.config.mts` | `harness.ts`, `webhooks.itest.ts` |

The coverage lane is the sharp one: it runs the six exempt suites with no way to
exempt them, so `pnpm coverage` would fail for the right reason and the wrong
cause.

**Decision**: separate the two concerns the design had fused.

- **Exemption handling goes to every lane** that touches the database — five
  configs, not two. Uniform, so no lane meets a trigger it cannot answer.
- **Bait goes only to the api and dispatcher lanes**, where the reader-shape
  faults live. Planting it in the gateway and e2e lanes would change their
  workload for no return, which is R4's lesson.

The gateway and e2e suites would pass today without any exemption, because none of
them performs a global operation. That is luck rather than design, and luck is
what this feature is about.

## R12 — The seeder has to do the thing the guard forbids

Planting was specified as "delete the sentinel's rows, then re-insert". `DELETE` on
a guarded table for a sentinel row fires the trigger. So the seeder needs the
exemption — and if it takes it on a connection the suite's pool later hands to a
test, the test inherits it and the guard is off for that test. Circular.

Two changes resolve it, and the second also fixes a race the design had not seen.

**The seeder gets its own connection.** A dedicated `pg.Client` created by the
setup file with the exemption in its options, used to plant, then closed. It never
enters the suite's pool, so nothing a test does can inherit it.

**The sentinel becomes per file, not shared.** Files run in parallel — no
integration config overrides `fileParallelism` — so a shared sentinel meant file
A's `beforeAll` deleting and re-inserting rows while file B was mid-test relying on
them. R2's per-file planting requirement and a shared sentinel are incompatible,
and the plan had both.

Per-file sentinels also change the trigger's shape: its `WHEN` clause can no longer
compare against one literal uuid. A small registry table — `__sentinel_environments`
— holds the ids, and the trigger tests membership. One extra lookup per guarded row,
against a table with as many rows as there are test files.

## R13 — A relay swallows the refusal, so the guard is silent where the stakes are highest

`contracts/guard.md` claims the refusal "surfaces in the test that performed the
mutation". That holds for a test. It does not hold for a relay:

```
services/api/src/webhooks/delivery-relay.ts:197   logger.log("error", "deliveries.drain_failed", …)
services/api/src/notifications/notification-relay.ts:148  logger.log("error", "notifications.drain_failed", …)
```

Both catch and log. A relay is the main global operation in the system, so a
trigger firing inside one produces a log line in a background loop and a green
lane.

Today every suite that spawns an api child sets all four relay flags off —
verified in `harness.ts` and `dispatcher.itest.ts`. So the exposure is nil and the
mitigation is a convention repeated in four files rather than a property — `harness.ts`, `dispatcher.itest.ts`, `gateway/limits.itest.ts` and `gateway/session.itest.ts`.

**Decision**: two changes, neither of which tries to make a relay throw.

- The contract's claim is narrowed to say what is true: the refusal surfaces in the
  statement's own transaction, which for a test is that test and for a background
  loop is a log line.
- The setup file asserts that a **non-exempt** file has the relay flags off, and
  fails at startup if not. That turns "we happen to switch them off" into
  something checked, and it is four lines.


---

# Findings from the second analysis pass

The first pass read the harness's *runtime*. This one read the harness's *loading
order*, the workspace layout, and — for the first time in this session — the prose
guide every skill invocation had been instructing us to apply.

## R14 — Where the exemption is written decides whether it works

`setupFiles` gives the test path at **top level**, not only inside a hook, and the
setup file's top-level code runs before the test file is imported. Measured with a
probe:

```
PROBE toplevel testPath  = …/src/__probe/probe.itest.ts
PROBE order so far       = setup-toplevel;testfile-module;
PROBE env visible at test-file module scope = yes
```

That is good news for the per-file sentinel — the path is available where it is
needed — and it comes with a constraint the plan had not stated. **Four suites
create their database pool at module scope**:

```
services/api/src/db/history-drift.itest.ts
services/api/src/db/repository.itest.ts
services/api/src/messages/history.itest.ts
services/api/src/messages/idempotency.itest.ts
```

An exemption written in `beforeAll` arrives after their pool already exists. None
of the six exempt suites is written that way today, so nothing is broken — the same
kind of luck this feature exists to remove. FR-026 states it; the exemption is
applied at module scope and bait planting stays in `beforeAll`, where async
database work belongs.

## R15 — No suite wipes a table, which removes a whole class of worry

Searched every `*.itest.ts` for `TRUNCATE` and for broad `DELETE FROM` against the
guarded tables. **Zero hits.** Had one existed, it would have taken every sentinel's
bait on every run and made the guard useless without anybody writing a fault.

Worth recording as a negative result: it is the kind of thing that would have been
expensive to discover during implementation and cost one grep to rule out.

## R16 — The harness outgrew the service it was going to live in

`services/api/src/testing/` was the plan's home for it. Then the exemption had to
reach every lane, and five configs across four packages ended up importing it —
including the gateway's, which would have meant one service's test lane reaching
into another service's `src/`.

It moves to `packages/test-harness/`. `packages/*` is already a workspace glob, and
`config`, `protocol`, `service-kit` and `e2e` establish that shared code lives
there. The package declares its own `pg` — only `services/api` does today — and it
plants through raw SQL, so it imports nothing from any service.

## R17 — The prose guide had never been opened

Every `/speckit-*` invocation in this session began by instructing us to apply
`.claude/skills/humanizer/PROSE-IN-GENERATED-DOCS.md` before writing prose. It was
read for the first time during this pass, after roughly fourteen thousand words of
specification had been written against it from memory.

Audited afterwards, the documents come out clean on its ranked list: **zero** hits
across all seven files for its twenty-two promotional and AI-vocabulary terms, one
superficial `-ing` tail, and no generic positive conclusions. The four
negative-parallelism hits are all real contrasts.

The exception is the one the guide classes as a *defect* rather than a style
choice. In normative text it asks for one term per concept, and the requirement
block used three for the planted rows — `bait` twice, `planted rows` once,
`sentinel environment's rows` once. Now `bait`, five times, everywhere.

What is worth keeping is not the audit result. It is that a document can be written
correctly against a guide nobody read, and still fail the one rule that guide calls
a defect — because that rule is the one a careful writer would not think to apply
to themselves.


## R18 — Cutting a filler clause found a wrong number inside it

J7 was the smallest finding of the second pass: a superficial `-ing` tail on T022,
", making all five cross-environment functions consistent in requiring one". The
guide asks for such a clause to say what happens or be cut.

Counting before cutting found that **five is four**:

```
drainOutbox                limit=yes   default=-
drainDisableNotifications  limit=yes   default=-
drainDueDeliveries         limit=yes   default=-
sweepDisabledEndpoints     limit=yes   default=100   ← the one losing it
expandEventToDeliveries    limit=NO
replayDeadLetter           limit=NO
pendingDeliveryDepth       limit=NO
outboxDepth                limit=NO
```

Four take a batch size. Two return a global count and have nothing to bound. Two
cross environments but take an id, so they are bounded by construction — a category
none of the documents had, which is why the arithmetic never added up. FR-012b
records it, and SC-006 now says four.

The claim appeared in three places and had survived the first analysis pass, which
quoted it while reporting a *different* problem with the same requirement (M1, the
depth functions). A count carried in prose is a second source of truth, and this one
was wrong in every copy.

**Why the small finding was the productive one.** The filler clause was doing
exactly what filler does: it read as a summary, so nobody checked it. Cutting it
required knowing what it summarised, and knowing that required counting. Three
documents asserted five; the compiler would have caught nothing, because the
sentence was prose.


---

# Findings from the third analysis pass

The first pass read the runtime, the second the loading order. This one read what
the repository requires of a *package*, and re-read the one document whose job is
to say the spec is ready.

## R19 — Growing a package grew four obligations nobody listed

`packages/test-harness/` was decided in R16 on the strength of one argument — five
configs across four packages import it. What a package needs *here* was never
enumerated, and three of the four gaps block a gate:

| Needs | Why | Consequence if missed |
|---|---|---|
| `packages/test-harness/**` in the `pg` ignores list | the harness imports `pg`, which `eslint.config.mjs` restricts to five paths | `pnpm lint` fails on the first run after the package exists |
| a `typecheck` script | `turbo run typecheck` runs per package and **skips** one without the script | the one package built to catch mistakes is never typechecked |
| `tsconfig.json` | `packages/config` and `packages/service-kit` both have one | no typechecking even with the script |
| **no** `test` script | `vitest run` with zero test files exits 1 | `pnpm test` breaks |

`@relay/e2e` is the existing package with exactly this pair — `typecheck` and no
`test` — and is the shape to copy.

The lint one is worth separating from the rest. `eslint.config.mjs` carries **two**
restriction rules with **two** ignores lists: one for the driver (`pg`,
`drizzle-orm`, `ioredis`) and one this feature adds for the global admin functions.
A task existed for the second and none for the first, which is the kind of near-miss
that reads as covered.

## R20 — Referencing the harness by path avoids five manifest edits

By package name would mean adding `@relay/test-harness` to `devDependencies` in the
api, gateway, dispatcher and e2e packages plus the repository root — which has no
workspace dependencies at all today.

By path costs nothing. `setupFiles` and `globalSetup` take paths, and `pg` still
resolves from the harness's own `node_modules`, because Node resolves from the
importing file's location rather than from whichever config loaded it.

## R21 — The checklist had been passing itself for four rounds

`checklists/requirements.md` was written against a 19-requirement spec and never
touched again. The spec has since gained nine requirements, superseded two,
withdrawn an assumption and replaced its central mechanism.

Its Notes described the checksum design in the present tense, and closed with:

> If the plan finds a sound way to attribute under parallelism, that assumption
> should be revisited rather than inherited.

The plan found one. Nobody revisited.

Two things worth keeping. The first is that this is the feature's own subject
matter arriving in the file meant to prevent it: **a check that passes because
nobody re-ran it.** Instance 6 was a test that passed alone; R6 was a design that
worked in one session; this was a validation that passed against a document it had
stopped describing.

The second is smaller and more useful. The stale paragraph was not wrong when
written and did not become wrong by neglect — it became wrong because *the thing it
asked for happened*. A document that names its own condition for revision has done
more than most, and it still needs someone to come back.

## R22 — The highest-stakes claim checked out

`services/api/src/limits/store.ts` says the `rl:` prefix is "the prefix the SAD's
cache-keys table names". That sentence is fenced byte-exact into published chapter
3.8, so a wrong one would be wrong in the book.

`docs/05-sad.md:524`:

```
| `rl:{env}:{bucket}` | Token buckets (FR-RTL-01) | window |
```

True. Recorded because a pass that only lists what it broke gives no sense of what
it checked — and this was the thing most expensive to have got wrong.


---

# Findings from the fourth analysis pass

Three passes had read the runtime, the loading order and the packaging. This one
read the documents the artifacts *assert things about* — and every finding is the
same species: a claim made about a file nobody had opened.

## R23 — `docs/06-adr-deep-dives.md` has no room for a note

The plan's Complexity Tracking said the second-language decision would be recorded
as "a note in `docs/06-adr-deep-dives.md`, not a numbered ADR". Nobody opened the
file.

It is eighteen sections, every one `## ADR-nn — …`, each following a fixed shape:
Problem → Options → Analysis → Decision → Consequences → Revisit when. Its header
declares it "Companion to `05-sad.md` §9", where `### ADR-01` through `### ADR-18`
live. It closes with a heading that counts them:

```
## Reading the eighteen together
```

A note that is not an ADR would be the only section of its kind, and would sit
outside a count baked into a heading. Minting ADR-19 instead would mean editing the
SAD, the deep dives, and that heading — which is exactly the cost the plan had
already declined to pay.

The note goes to `docs/07-tutorial-plan.md`'s "Work that publishes no chapter"
section, which already records this feature, and to the header of `sentinel.sql`,
where a reader meets the PL/pgSQL. Neither pretends to be an ADR.

## R24 — Two more numbers were wrong, in the way the last one was

R18 recorded a filler clause hiding a wrong count. Two more:

**"Seven recorded instances"** in the task list's own deliverable line, and in a
phase checkpoint. The spec is right — six in the table, plus a seventh *precursor*
from chapter 3.3 described in prose and explicitly not one of the six — and the
battery is six: quickstart V3 covers instance 6, V4 covers 1 through 5. FR-017 and
SC-001 both say six. `tasks.md` promised seven reintroductions and contained six.

**"A convention repeated in seven files."** Measured: **four**.

```
packages/e2e/src/harness.ts
services/dispatcher/src/dispatcher.itest.ts
services/gateway/src/limits.itest.ts
services/gateway/src/session.itest.ts
```

Nine files mention the relay flags; three are the modules that *read* them and one
— `outbox.itest.ts` — only names one in a comment. Setters: four.

Three counts wrong across four passes, each in prose, none catchable by a
compiler. The pattern is not carelessness about arithmetic; it is that a number in
a sentence reads as a summary of something already checked, so it never gets
checked. **Every count in these documents is now either measured in the same
commit that states it, or it is a guess wearing a number's clothes.**

## R25 — The trigger needs its table, and nothing guaranteed one

`globalSetup` runs before every suite. Six suites call `migrate(pool)` in their own
`beforeAll` — that is, *after* it. So on an unmigrated database,
`CREATE TRIGGER … ON webhook_endpoints` hits a table that does not exist and the
lane dies before a single test.

The documented paths are safe: CI runs `node services/api/dist/db/migrate.js`
before `pnpm test:integration`, and `fresh-db.sh` migrates. What is exposed is a
developer who creates a database and runs the lane directly — which works today,
because the suites that need a schema build it themselves.

`global-setup.ts` calls `migrate()` first. It is idempotent, keyed on
`schema_migrations`, and it turns the lane from something that assumes a migrated
database into something that guarantees one.

## R26 — The reference that checked out

The prose guide says the house voice is documented at `docs/07-tutorial-plan.md`,
"Voice". Three passes had cited that guide without following the pointer, and it
resolves: line 66, a table row rather than a heading — *"First person plural,
present tense"*.

Recorded because the expectation going in was a dangling reference, and a pass that
lists only what it broke gives no sense of what it checked.


---

# Findings from the fifth analysis pass

Pass four ended by saying the cheapest remaining pass would aim at cross-document
assertions rather than at the design. It did: 72 backticked paths, five numeric
claims about chapter 3.9, and three constitution quotations, checked mechanically.
Two problems, and the first is the largest of the five passes.

## R27 — Four passes inherited a constitutional judgement nobody re-derived

The plan's Complexity Tracking said, from pass zero: **"PL/pgSQL — a second
language, against constitution VII's one-language rule"**, and then, two paragraphs
later, that the decision would be recorded as *a note, not a numbered ADR*.

Constitution VII, line 167:

> Introducing a second language **requires** a superseding ADR with profiling
> evidence.

So the plan declared a MUST violated and declined the one remedy that MUST names.
A justification table is not the escape clause; the ADR **is** the escape clause.
Passes one through four each re-read the Constitution Check, each wrote "one
violation, recorded and justified", and none tested the justification against the
sentence it cited.

**The resolution is that there was never a violation.** VII's clause reads *"One
language (TypeScript/Node.js) across services, SDK, and dashboard; shared protocol
types between server and SDK eliminate drift bugs (ADR-01)"* — its subject is the
language services are **implemented** in, and its stated harm is drift between
server and SDK. The guard is neither a service nor shipped. And the repository
already holds **nine `.sql` files** that the constitution endorses in its own words:
migrations are *"versioned, forward-only, hand-reviewed SQL"*.

The honest wrinkle, which is why the gate stopped here in the first place: those
nine are *declarative* SQL and this one is *procedural*. A `RAISE EXCEPTION` inside
a `plpgsql` function is closer to program logic than an `ALTER TABLE` is. That
difference is real; it is not the difference VII legislates.

**What makes this the sharpest instance of the pattern.** Four wrong counts were
found across passes two to four, each a number in prose that read as a summary and
so never got checked. This is the same failure applied to a judgement instead of a
number — and a judgement carries further, because it decided that a constitutional
remedy would be skipped. Complexity Tracking is now empty, which is what the
template asks for when the gate finds nothing, and the reasoning lives in a section
that does not pretend to be justifying a violation.

## R28 — A baseline measured at a different size

SC-004 promised the integration lane would grow by less than ten seconds "against
the chapter 3.9 baseline of 3m15s". That figure exists in exactly one place —
`specs/029-chapter-3-8/captured-output.md:321`:

```
integration lane    9 tasks, 213 tests passed        3m15s
```

**213 tests.** Chapter 3.9 finished on 223 (029's `battery.txt`, V8), and that run
was never timed. So the ten-second budget was being measured against a lane ten
tests smaller, and part of it was already spent before this feature added anything.

T002 always re-measured the baseline, which made the literal redundant and the two
statements contradictory. SC-004 now measures against T002's number; the `3m15s`
mentions say what they are.

Not a wrong number this time — a right number transplanted from a context where it
meant something else. Same family as R18 and R24, different mechanism.

## R29 — What the sweep confirmed

Recorded because five passes of findings give no sense of what held up.

| Assertion | Verdict |
|---|---|
| 72 distinct backticked paths across seven documents | all resolve |
| Constitution VII, *"a superseding ADR with profiling evidence"* | verbatim, line 167 |
| Constitution VI on 100% branch coverage and the cross-tenant gate | accurate, lines 149 and 151 |
| Coverage floor 89.50% / 82.73% | recorded in 029's `captured-output.md` and `chapter-notes.md` |
| Unit 242 / integration 223 | recorded in 029's `battery.txt` |
| `outboxDepth` and `pendingDeliveryDepth` cross every environment | true — both `count(*)`, no `environment_id` filter |
| api lane = 177 on a fresh database | matches 029's final run |


---

# Findings from the sixth analysis pass

Pass five ended by saying a sixth should aim at whatever pass five asserted
without re-deriving. It did, and pass five's claims held — the interesting
findings came from the last two sections of `spec.md` that no pass had opened.

## R30 — `spec.md` was refuting itself in three places

Every pass read the requirement block, the tasks and the cross-document claims.
None read the narrative sections sitting between them, and both were written in
pass zero.

**Edge case 1** required the design that the Assumptions section, eighty lines
below, strikes through as withdrawn:

> The always-on check **must** therefore be scoped to the run rather than to the
> test, with per-test attribution available in a mode where file execution is
> serial.

**Edge case 4** restated FR-011 — *"Re-planting **must** happen after the verdict"*
— which the same document marks *superseded by research R6*.

**Key Entities** said *"Sentinel environment: **one** named environment"*, which
FR-023 has contradicted since the third pass, and listed a **Verdict** entity that
exists only in the checksum design.

Both sections are phrased normatively. Somebody implementing from Edge Cases and
Key Entities rather than from the FR block would have built the mechanism research
R6 replaced — and would have been reading the spec correctly.

**Why five passes missed it.** Each pass had a target: the runtime, the loading
order, the packaging, the cross-document assertions, its own predecessor. Prose
that was neither a requirement nor a claim about another file fell between every
one of those targets. The checklist failed the same way in pass three, and the
lesson did not generalise, because the fix was "re-validate the checklist" rather
than "re-read what pass zero wrote".

## R31 — The sixth wrong count, and the first that predates the rule

Edge case 2 said *"The outbox relay, the delivery relay and the notification relay
suites"* — **three**. R5 measured **six**, and four other documents say six.

R24 set the rule after the fourth: every count is measured in the commit that
states it, or it is a guess wearing a number's clothes. This one was written before
the rule existed, which is the only reason it survived — and the reason to sweep
for the rest rather than wait for the seventh.

## R32 — Two tasks were justified by a measurement whose conditions are gone

T029 and T030 named specific tests to fix, citing R3. R3 measured them under a
one-shot **shared** sentinel, **no trigger**, and **addressable** bait
notifications. All three have since been replaced by R12, R6 and R4 — and T030's
own expected fix, T008's unaddressable sentinel, removes the cause R3 measured.

T028 exists to produce the real list "before fixing any of them", so T029 and T030
were prejudging it. Both are now hypotheses for T028 to confirm or discard, with
discarding an acceptable outcome that has to be stated rather than quietly skipped.

## R33 — What pass five asserted, re-derived

| Pass-5 claim | Verdict |
|---|---|
| "nine `.sql` files" underpinning the constitution VII reading | **All nine are migrations**, under `services/api/migrations/` — exactly what the constitution endorses as "versioned, forward-only, hand-reviewed SQL". The argument is stronger than it was stated |
| The constitution says nothing about new packages | Confirmed — only *"New services require justification"* |
| `3m15s` was recorded against 213 tests | Confirmed, `029/captured-output.md:321` |
| The superseded checksum is gone from data-model and the contract | Confirmed |

One thing pass five got wrong in its own favour: it reproduced the plan template's
Complexity Tracking instruction as a blockquote and smoothed it — an added article,
a dropped bold, an added period. The prose guide names that exactly: a quote that
has been smoothed is a misquote. Now byte-identical.


---

# Findings from the seventh analysis pass, and the sweep that followed it

Pass six closed by claiming no obvious target remained. That claim was wrong, and
wrong in a way worth recording: pass six swept Edge Cases and Key Entities, and
the conclusion drawn was "the narrative sections are done". **Acceptance scenarios
are neither narrative nor requirements**, so they fell in the same gap that had
hidden the other two for six passes.

## R34 — The third pass-zero section asserting the superseded design

US2's acceptance scenario 3 required a mode the feature deliberately does not have:

> **Given** a lane run where something took the bait, **When** the developer
> re-runs in **diagnosis mode**, **Then** the offending test is named.

FR-008 is marked *superseded by research R6* for exactly that reason — the trigger
names the test in its own stack, on the run that contains the fault. So US2 could
not have been signed off against its own spec.

And the fix for it was itself incomplete. Rewriting the scenario left the story's
own **description** four lines above still saying *"the run that contains the
mutation reports it, and a diagnosis mode names the test"*. The mechanical sweep
caught that; a seventh targeted pass would not have.

## R35 — Two documents, two vocabularies for one sequence

`plan.md` numbered the work Phase A to E; `tasks.md` numbers it 1 to 8. Nothing
mapped them, and the plan's letters had **no counterpart for tasks' Phase 7**,
verification — twenty consecutive lane runs, the SC-004 measurement, quickstart V0
to V11. Two phase vocabularies for one sequence is one too many; until the plan is
renumbered a paragraph carries the mapping and names the phase the letters skipped.

Also in the plan: **Phase D still stated research R3's two failures as fact**, six
passes after they became hypotheses and one pass after `tasks.md` was corrected to
say so. A remediation that changes one document and leaves another asserting the
opposite is worse than the original error, because it looks settled.

## R36 — What a mechanical sweep found that seven targeted passes did not

Instead of an eighth targeted pass, every document was grepped for the vocabulary
the design abandoned — `diagnosis mode`, `checksum`, `run-scoped`, `verdict`,
`serial`, `SET relay.allow_global`, `shared sentinel`, `setup hook` — and for every
count that has been wrong once: `seven instances`, `seven files`, `five global`,
`five cross-environment`, plus the two paths that moved.

**80 hits across 8 documents. Three were real:**

| | |
|---|---|
| `spec.md` US2's story description | still promised a diagnosis mode — R34 |
| `plan.md`, twice | *"the seven recorded instances"*, where the battery is six. Pass four corrected this in `tasks.md` and never looked at `plan.md` |
| `data-model.md` | its entity section was still headed **Verdict**, the checksum's name for it, while `spec.md`'s Key Entities had been renamed **Refusal** in pass six |

The other 77 are `research.md`'s chronology — which must contain the old words,
because it records what was believed and when — and explanatory notes of the form
*"an earlier version said X"*. Those are not drift; they are the audit trail.

**The lesson is about method, not about any of the three.** Seven passes each
picked a target and swept it: the runtime, the loading order, the packaging, the
cross-document claims, the predecessor's assertions, the narrative sections, the
acceptance scenarios. Every pass found something, and every pass left a surface
unswept, because a target is a guess about where the problem is. A grep for
abandoned vocabulary needs no guess. It found in one command what the sixth and
seventh passes each found one instance of, and it will keep working when nobody
remembers which mechanism was replaced.

Two of the three had already been fixed **elsewhere** — pass four in `tasks.md`,
pass six in `spec.md` — and survived in a second document. That is the strongest
argument for the sweep: a remediation is not done when the file you were reading
is correct.


---

# Findings from implementation

## R37 — A trigger's WHEN condition may not contain a subquery

The design said the trigger fires `WHEN (OLD.environment_id IN (SELECT
environment_id FROM __sentinel_environments))`. Postgres rejects that at
`CREATE TRIGGER`:

```
ERROR:  cannot use subquery in trigger WHEN condition
```

Every document describing the per-file sentinel — data-model, the contract, the
tasks — assumed the registry could be consulted from the `WHEN` clause. None of the
eight analysis passes caught it, because none of them tried to create the trigger.

Two ways out, and the difference matters for SC-004. Dropping `WHEN` entirely means
the function body runs for **every** UPDATE and DELETE on five tables across the
whole lane. Keeping `WHEN` and putting the lookup behind a `STABLE` function keeps
the cheap path cheap: a subquery is forbidden, a function call is not.

```sql
CREATE OR REPLACE FUNCTION __is_sentinel(env uuid) RETURNS boolean
LANGUAGE sql STABLE AS $$
  SELECT EXISTS (SELECT 1 FROM __sentinel_environments WHERE environment_id = env)
$$;
```

Verified end to end against a fresh database, with the trigger installed and one
sentinel registered:

```
NON-EXEMPT refused: global-operation guard: this statement modified sentinel row
                    public.webhook_endpoints (id a1ec0d8b-…) …
bystander insert:   allowed
EXEMPT allowed:     1 row(s)
```

The exempt connection carried `options=-c relay.allow_global=on`, which is the
mechanism R10 measured and the reason it is a connection option rather than a
statement.


---

# Findings from implementation

The eight analysis passes read the documents. These came from running the thing.

## R38 — The exemption did not permit the write, it discarded it

`sentinel.sql` answered an exempt connection with `RETURN OLD`. On a `BEFORE
DELETE` trigger that is correct and the only option. On a `BEFORE UPDATE` trigger
it does not mean "allow the update" — it means "perform the update, writing these
values", and those values are the row as it was. The write happens, one row is
reported modified, and nothing changes.

R37's verification is what makes this worth writing down. It ended:

```
EXEMPT allowed:     1 row(s)
```

That line is true and proves nothing. `rowCount` was 1 because a row *was*
written — the old one. The measurement asked whether the statement was refused,
and the statement was not refused, so it passed.

What surfaced it was the api lane, in the file with the most reason to notice:

```
FAIL src/webhooks/deliveries.itest.ts > logs nothing when there is nothing to disable
AssertionError: expected 17 to be +0
```

Seventeen is the number of files in the lane, each having planted one sentinel
endpoint with an open failure run past the cutoff. The relay swept, disabled
none of them because the trigger reverted every disable, and found all seventeen
again on the next pass. An endless supply of eligible work, and no error anywhere.

**Decision**: return `OLD` on `DELETE` and `NEW` otherwise, and add
`packages/test-harness/src/guard.itest.ts` — the guard's own lane, six tests. The
one that matters reads the row back after an exempt update:

```
✓ a connection without the exemption > cannot update a sentinel row …
✓ a connection without the exemption > cannot delete one either
✓ a connection without the exemption > may still write rows that belong to no sentinel
× a connection carrying the exemption > UPDATES THE ROW, and the new value is what the next reader sees
```

With the bug restored, that is the only one of the six that fails. Every
refusal-side test passes, which is why no amount of testing the refusal would have
found it: the guard was wrong on the path where it was supposed to do nothing.

## R39 — R13 measured the wrong nine files

R13 concluded the relay exposure was "nil" because "every suite that spawns an api
child sets all four relay flags off", and named four files. That is accurate about
child processes. It does not cover the suites that boot the app **in process**:

```
$ grep -l "AppModule" services/api/src/**/*.itest.ts | wc -l
9
$ grep -l "RELAY_OUTBOX_RELAY" $(grep -l "AppModule" services/api/src/**/*.itest.ts)
(nothing)
```

Nine suites import `AppModule`, and each relay defaults to on when its flag is
unset — `process.env.RELAY_OUTBOX_RELAY ?? "on"`. So nine of the seventeen files
in the lane were running four background loops that sweep the whole database,
while the other suites' fixtures sat in it. A relay catches and logs its own
errors, so the guard's refusal inside one of them is a log line and a green lane —
the hole R13 identified, in nine more places than R13 counted.

**Decision**: set the four flags off in the lane's config rather than in nine
files, so a quiet database is a property of the lane. FR-025's startup check stays,
now as the thing that catches a lane whose config drifts rather than the thing
carrying the whole guarantee.

## R40 — The bait found instance 7 before any deliberate fault was reintroduced

Against the bait and the fixed trigger, the api lane fails two tests, both in
`outbox.itest.ts`, both scoped correctly and both wrong anyway:

```
FAIL invariant 7: the relay publishes pending rows, marks them, and does not republish
AssertionError: expected 4 to be +0     (unpublishedFor(db, env.id).length)

FAIL invariant 8: two concurrent relays publish every row exactly once
AssertionError: expected 24 to be +0    (outboxDepthFor(db, env.id))
```

Every read in both is filtered to `env.id`. The fault is not in the assertion, it
is in the loop above it: `drainUntilClear(relay, db, environmentId, passes = 20)`
gives a **global, oldest-first** relay a fixed budget of twenty passes and then
asserts a local fact. Twenty passes of the default batch move 2,000 rows; the
backlog is 3,400. Invariant 8 uses `batchSize: 7`, so its budget is 140 rows.

This is the reader shape in the form the spec did not anticipate: not "the
assertion reads globally" but "the drive loop is bounded in units of batches while
the work is bounded in units of the whole table". It is also a real
production-shaped problem — a tenant's events wait behind every older tenant's —
which is the argument for a shared database restated by the thing it was arguing
about.

R3 hypothesised invariant 7 would fail and could not reproduce it. It reproduces
now, deterministically, because the bait is re-planted per file instead of once.

## R41 — A file-wide exemption could not catch the fault the feature was built for

T017 says: reintroduce instance 6 into `notifications.itest.ts`, run that file
alone against a fresh database, confirm the refusal appears in its own stack.
Reintroduced, it passed:

```
Test Files  1 passed (1)
      Tests  9 passed (9)
```

`notifications/notifications.itest.ts` is on the exemption list, because it drives
the notification relay. It is on that list *because of instance 6* — an ordinary
lane run disabled `deliveries.itest.ts`'s fixture, and exempting the file was how
the lane went green. So the guard had excused the exact file the guard was built
for, and nothing in eight analysis passes noticed, because the list and the
instance were written down in different documents.

The distinction the design was missing: **instance 6 is global over
`webhook_endpoints`; the notification relay is global over
`webhook_disable_notifications`.** Different tables, one boolean.

**Decision**: `relay.allow_global` carries a comma-separated list of table names
(`all` only for the planting connection), each exempt entry names its tables, and
the trigger checks `TG_TABLE_NAME = ANY (string_to_array(allowed, ','))`. The same
reasoning that made this a list of paths rather than a pattern makes each path a
list of tables rather than a blanket.

Reintroduced under the per-table exemption, in one run of one file on a fresh
database:

```
× sends what the organisation needs, and Mailpit confirms the contents  363ms
… 9 of 9
Caused by: error: global-operation guard: this statement modified sentinel row
public.webhook_endpoints (id 6ba2cc2e-…), which belongs to no test — the bait
planted by services/api/src/notifications/notifications.itest.ts
```

Reverted with `git checkout --`; `md5sum` matches the committed file.

Two tests in `guard.itest.ts` hold the property: a connection exempt for
`webhook_disable_notifications` writes that table and is refused on
`webhook_endpoints`.

## R42 — One bait endpoint cannot fill a batch of a hundred

Instance 1 is `sweepDisabledEndpoints` at the product's own limit: the sweep takes
the hundred oldest eligible endpoints, older ones fill the batch, and the test's
own endpoint is never reached. Reintroduced and run alone on a freshly migrated
database:

```
Test Files  1 passed (1)
      Tests  49 passed (49)
```

The bait planted **one** endpoint with an open failure run. One older endpoint does
not fill a batch of a hundred. The other three baits were sized at `BAIT_ROWS`
(200, twice `MAX_PRODUCT_BATCH`) and the endpoint was not, because the spec
described it in the singular — "a sentinel environment holding an endpoint with an
open failure run" — and nothing checked the singular against the arithmetic.

**Decision**: plant `BAIT_ROWS` endpoints, the first keeping `s.endpointId` so the
deliveries and notifications still hang off a stable, nameable row, each stamped
`now() - interval '4 hours' - (i * interval '1 second')` so they sort ahead of
anything a test mints. Re-run:

```
Test Files  1 failed (1)
      Tests  1 failed | 48 passed (49)
FAIL invariant 12: the SWEEP disables the quiet endpoint no outcome ever revisits
AssertionError: expected true to be false
```

One test, the right one, and the other 48 unaffected. T019's idempotency assertion
said "each sentinel holds exactly one endpoint" and is now wrong; it was a
restatement of the design, not a measurement of it.

## R43 — Four of the six, and the two the seeder cannot reach

SC-001 promises all six recorded instances fail alone on a fresh database. Measured,
one reintroduction at a time, each reverted and `md5sum`-checked:

| # | file | alone, fresh db | what failed |
|---|------|-----------------|-------------|
| 1 | `deliveries.itest.ts` | **fails** | `invariant 12` — `expected true to be false` |
| 2 | `deliveries.itest.ts` | passes | see below |
| 3 | `consumer.itest.ts` | passes | see below |
| 4 | `signup.itest.ts` | **fails** | `invariant 7` — the global `count(*)` moved |
| 5 | `dispatcher.itest.ts` | **fails** | 10 tests, `expected 0 to be greater than 0` |
| 6 | `notifications.itest.ts` | **fails** | 9 tests, the guard's refusal (R41) |

Instance 5's message is the one chapter 3.8's baseline recorded, character for
character, which is the strongest evidence that the bait reproduces the original
conditions rather than merely breaking something.

**Instance 2 cannot fail alone, by construction.** Its content is *this suite leaves
leftovers that starve a later one* — the fix was cleanup, and the victim is
instance 5's site. A cause whose only symptom appears in another file has no
alone-failure to produce. What the bait changes is that the victim now fails alone:
the leftovers are permanent and planted, so instance 5's reintroduction is the
observable form of the same fault. SC-001's "all six" is wrong about this one, and
the criterion is amended rather than the result reported as five.

**Instance 3 is out of the seeder's reach.** Its shared growing resource is the
JetStream stream, not the database — a consumer with no subject filter replays
every event earlier chapters left behind, on a fixed budget of polls. Unfiltered
and run alone on a fresh database it passes, because a fresh CI stream is small.
Seeding it would mean a NATS connection inside `plant()`, which every suite's
`beforeAll` would then depend on — including the several that never touch NATS.

**Decision**: do not seed the stream. The mechanism for instance 3 is the lint rule
(US3), extended to the consumer: a runtime constructed in a test without a subject
filter is the call site to object to, and unlike the bait the linter can see it
before anything runs. Recorded in `eslint.config.mjs` beside the rule, and in
`contracts/guard.md` under what the seeder does not cover.

## R44 — Bait in the dispatcher lane fails the suite either way

T016b sent bait to the api and dispatcher lanes, because instance 5 lives in
`dispatcher.itest.ts`. Measured on a freshly migrated database with nothing else
running:

```
with bait     Tests  10 failed | 6 passed (16)   Duration 155.74s
without bait  Tests  16 passed (16)              Duration  73.70s
```

Instance 5's fix — `batchSize: 10_000` — is in place in both runs. So the bait
fails the suite whether or not the fault is present, and an instrument that always
reads "broken" carries no information.

The cause is not the batch. `deliverEvent` publishes everything due to the stream
and then waits eight seconds for the **dispatcher process** to deliver its own row;
the dispatcher consumes a shared FIFO stream, so 200 bait jobs sit ahead of it,
each costing an api `material()` call and a delivery attempt. Two hundred rows at
roughly forty milliseconds is the eight seconds exactly.

Nothing cheaper works. `https://sentinel.invalid` resolves in about 1ms after the
first attempt, so the URL is not the cost; a disabled bait endpoint would still
cost the api round-trip per job, because the skip decision is made after the
claim. And the bait cannot be made unclaimable without ceasing to be bait — the
drain's claim predicate is exactly its eligibility predicate.

**Decision**: bait in the **api lane only**. The dispatcher lane keeps exemption
handling — the trigger is database state and outlives whichever lane installed it.
Instance 5's protection becomes the required batch size (`drainDueDeliveries` takes
no default) plus a reintroduction verified by hand and recorded, rather than a
standing property. That is weaker, and saying so is the point.

This is the same boundary as instance 3: the seeder seeds a database, and both of
these faults ride a broker.

## R45 — Bait has to look like the work it stands in for

With `outbox.itest.ts`'s drive loop fixed, invariant 7 failed differently:

```
AssertionError: expected 5 to be 204
```

The relay publishes `payload.id` as the deduplication key, and the test asserts the
ids it sent are distinct. The bait's outbox rows carried `'{}'`, so two hundred
messages published with `id: undefined` collapsed to one entry in a `Set` and a
correct assertion failed. Fixed by giving each bait row
`jsonb_build_object('id', gen_random_uuid())`.

Worth noting what this was not: the assertion was right, the scoping was right, and
the loop was right by then. The bait was wrong, in a way that only surfaced after
two other things were fixed.

## R46 — Instance 8, in the file that already had instance 3 fixed

T032 says grep for the class while the first instance is on screen, and it found
one in `consumer.itest.ts` — forty lines from the test chapter 3.7 fixed:

```
services/api/src/consumer/consumer.itest.ts:361
    const a = runtimeFor(db, durable, async (e) => void byA.push(e.id));
    const b = runtimeFor(db, durable, async (e) => void byB.push(e.id));
    for (let i = 0; i < 400; i++) { … }
```

`runtimeFor`'s fifth parameter is the environment filter and it is optional, so
both runtimes start at the head of the whole stream. The test publishes three
events to three different environments — `ENV()` called three times, which is the
same detail that made instance 3 unfilterable — and then polls 400 times.

It has never failed. That is the property of this class rather than a defence of
it: a fixed budget against a growing shared resource passes until the resource
outgrows the budget. Chapter 3.7 fixed the test above this one and did not look
down.

The environments were incidental to what the test is about — two runtimes sharing
one durable, each message handled once — so one environment and a filter on both
runtimes leaves the subject intact. Eight instances now, in six files, across
chapters 3.3 to 3.9.

## R47 — Three attempts at delivery bait, and the one that works gives something up

R44 removed bait from the dispatcher lane. That was not enough, because bait is
database state and the coverage lane shares the database: `pnpm coverage` runs
every `*.itest.ts` in one process against whatever the api lane last planted, and
the dispatcher suite failed there for the same reason it had failed in its own
lane.

Three shapes measured, each on a freshly migrated database:

| bait deliveries | dispatcher lane | duration |
|---|---|---|
| 200 due, on the enabled endpoint | 10 of 16 failed | 155.7s |
| 200 due, on a **disabled** endpoint | 2 of 16 failed | 71.9s |
| 200 **not due**, on a disabled endpoint | 16 passed | 73.6s |

The middle row is the interesting one. `deliveryMaterial` returns null for a
disabled endpoint, so the dispatcher logs `delivery.skipped` and acks without
signing or sending — and it still cost eight seconds for two hundred rows, because
the api round-trip per job *is* the forty milliseconds. Only the first two tests
failed; after that the bait was consumed. A warm-up cost is still a cost.

**Decision**: `next_attempt_at` an hour in the future. The rows stay in the table
for anything that counts them, and no drain claims them. The endpoint stays
disabled anyway, so that if one ever does come due through a path not anticipated
here, a skip is the cheapest thing it can cost.

What this gives up, plainly: the due-delivery drain has no bait, so its reader
shape is not caught by the seeder. It is covered by the required batch size and
by the lint rule. This is the third boundary of the same kind — instance 3's
stream, instance 5's broker latency, and now the drain's own work — and they share
a cause: **bait for a reader that performs work IS that work.**

## R48 — The ratchet was already failing, and the baseline said otherwise

`pnpm coverage` ended:

```
ERROR: Coverage for functions (98.7%) does not meet
       "services/api/src/db/repository.ts" threshold (100%)
```

The natural suspect was T022, which removed `sweepDisabledEndpoints`'s default
parameter. Measured both ways, with the harness's own tests excluded so the two
runs are comparable:

```
limit = 100   repository.ts  97.27 | 90.44 | 98.7 | 99.24
limit: number repository.ts  97.27 | 90.39 | 98.7 | 99.24
```

Identical. The relay flags were the second suspect — the coverage lane now runs
with all four off — and turning them back on produced 98.7 as well.

The uncovered function is `drainDisableNotifications`'s `onError` default,
`= () => {}`. At the pre-feature commit the only caller in the tree already passed
a handler:

```
$ git grep -n "drainDisableNotifications(" fb97056 -- 'services/**/*.ts'
notification-relay.ts:122:    return drainDisableNotifications(db, batchSize, deliver, (row, error) => {
```

So it was uncovered then too, and `baseline.txt`'s "every per-file ratchet still
passes" was a sentence about ratchets nobody had run. That is this feature's own
recurring failure — a summary that reads as a measurement — recorded here rather
than quietly corrected.

**Decision**: remove the default and require the handler, for the same reason
T022 required the batch size and a sharper one. A default `onError` discards a
row's failure with no log line, which is the swallowed-refusal shape R13 and R39
are both about, in the file that holds the platform's admin surface. Nothing used
it.

```
repository.ts  97.27 | 90.90 | 100 | 99.24
Test Files  53 passed (53)      Tests  472 passed (472)
```

## R49 — The same law, a third time, found by run 1 of twenty

The twenty-run battery was restarted on a frozen tree and failed on run 1:

```
FAIL src/notifications/notifications.itest.ts >
     sends twice for an endpoint disabled, re-enabled and disabled again
Error: Test timed out in 5000ms.
```

`drainDisableNotifications` claims on `delivered_at IS NULL` and then does per-row
work: look up the organisation's recipients, decide, mark. The sentinel's
organisation has no addressable member — T008's design, which removed the 200 SMTP
sends R4 measured — so every bait row takes the cheapest branch available. Cheapest
is about 1.4 milliseconds, and seventeen files' worth of bait is 3,400 rows, which
is a little under five seconds. Vitest's default test budget is five seconds.

It is exactly the "passes on headroom" signature: the same lane had run green
several times before, including a full `pnpm test:integration` twenty minutes
earlier. Nothing about the tree changed between the green run and the red one.

**Decision**: plant these rows with `delivered_at` set. They stay in the table for
anything that counts rows and leave every claim window.

That is the third measurement of one law, so it is worth stating as a law rather
than as three incidents:

> **Bait may be claimable only where draining it is database work.**

The endpoints (a sweep: one statement) and the outbox rows (a publish to whatever
publisher the test supplies) qualify, and both stay claimable — instances 1 and 7
were caught by exactly those two. The deliveries (an api round-trip and an HTTP
send per row) and these notifications (a recipient lookup and a mark per row) do
I/O, and both are now out of reach of a claim.

The cost is stated rather than hidden: two of the four global drains have no bait,
so their reader shape is caught by the required batch size and the lint rule and
not by the seeder.

**What the battery is for.** This is the fault the twenty runs exist to catch, and
it was caught on the first one — after three separate full-lane runs had passed.
Chapter 3.7 spent four hours on its twenty and found four faults; this one found a
fault the moment it was pointed at a tree nobody was editing.

## R50 — The harness was the only task in the repository that required `DATABASE_URL`

Reported from a plain `pnpm test:integration` on a clean shell:

```
@relay/test-harness:test:integration: No test files found, exiting with code 1
@relay/test-harness:test:integration: Error: the global-operation guard needs
    DATABASE_URL — the integration lane cannot install it against a database it
    cannot name
  ❯ Object.globalSetup [as setup] src/global-setup.ts:27:11
```

The message was written to be helpful and the check was wrong. Every other package
in the workspace falls back:

```ts
services/api/src/db/client.ts:13
export const DEFAULT_DATABASE_URL = "postgres://relay:relay@localhost:15432/relay";
export function createPool(): pg.Pool {
  return new pg.Pool({ connectionString: process.env.DATABASE_URL ?? DEFAULT_DATABASE_URL });
}
```

So `pnpm test:integration` has always worked from a shell with nothing exported,
against the compose stack. The harness made itself the single exception, and
because `globalSetup` runs before collection, vitest also reported "No test files
found" — two confusing lines for one cause.

Every measurement in this feature was taken in a shell that had sourced the
environment, which is precisely why it went unnoticed: **the condition the check
broke is the one the author never ran in.** That is the feature's own subject
pointed at the feature. Instance 6 passed alone; R6 worked in one session; this
worked in one shell.

**Decision**: `packages/test-harness/src/db-url.ts` exports the same fallback, and
the three entry points — `global-setup.ts`, `setup.ts` and `guard.itest.ts` — go
through it. The literal is duplicated rather than imported, because a workspace
package importing service source is the wrong direction, and `db-url.test.ts` reads
`client.ts` and fails if the two disagree. Same shape as `bait-size.test.ts` and
`lists-agree.test.ts`: a duplicated constant is fine, an unwatched one is not.

With the stack deliberately down and nothing exported, the harness lane now fails
the way any lane does:

```
Error: connect ECONNREFUSED 127.0.0.1:15432
```

An address it could only have got from the fallback.

## R51 — The bait's bill arrived in a different suite

Run 4 of twenty, having passed runs 1 to 3 on the same tree:

```
FAIL src/notifications/notifications.itest.ts >
     sends twice for an endpoint disabled, re-enabled and disabled again
Error: Test timed out in 5000ms.
```

The same test R49 fixed, and R49's fix was not wrong — it was incomplete. The
planted notification rows were `delivered_at`-set and out of every claim window, as
intended. The rows the drain was working through had been written by the product:

```
select e.enabled, n.delivered_at is null, count(*)
  from webhook_disable_notifications n
  join __sentinel_environments s using (environment_id)
  join webhook_endpoints e on e.id = n.endpoint_id
 group by 1,2;

 f | f | 4000     <- planted, delivered, inert
 f | t | 3799     <- written by the sweep, undelivered, work
```

Every file planted `BAIT_ROWS` endpoints with an open failure run.
`deliveries.itest.ts` sweeps globally with a limit of 10,000, disables all of them,
and **each disablement writes a notification row**. Nineteen files' worth is 3,799
rows, and `notifications.itest.ts`'s first global drain has to work through them at
about 1.3ms each. Five seconds is vitest's default budget. Runs 1 to 3 passed
because the total sat just under it.

So R49's law needs its second clause:

> Bait may be claimable only where draining it is database work — **and draining
> it must not create work for a different reader.**

**The design error underneath.** Sweep bait is a GLOBAL property and the trigger's
attribution is a PER-FILE one, and `plant()` served both with the same rows. To
defeat `sweepDisabledEndpoints`'s batch you need more than `MAX_PRODUCT_BATCH`
eligible endpoints *in the database*; it does not matter who planted them. To have
a refusal name a file you need one guarded row per file. Planting 200 per file
satisfied both and bought nineteen times what the first needs.

**Decision**: split them. Each file plants one endpoint — the trigger's target.
`plantReaderBait()` maintains a single shared sentinel holding `BAIT_ROWS`, and
every file calls it, because any file may be the one running alone. It is
idempotent **by UPDATE rather than by delete-and-reinsert**: a sweep disables these
by design, so they have to go back, and re-creating them would delete rows another
file may be mid-sweep against (research R12). It also clears the notifications the
last sweep wrote, which is the whole point.

Measured after a full lane, from a cleaned database:

```
bait endpoints                     239
undelivered sentinel notifications   0      (was 3,799)
undelivered total                   48      (real product rows)
Tests  8 + 177 + 21 + 16 + 9 = 231 passed
```

And the mechanism still works — instance 1 reintroduced, run alone on a freshly
migrated database:

```
FAIL invariant 12: the SWEEP disables the quiet endpoint no outcome ever revisits
AssertionError: expected true to be false
Tests  1 failed | 48 passed (49)
```

**An unplanned proof, from trying to clean up by hand.** A `DELETE` issued straight
from `psql` to tidy the debris was refused:

```
ERROR:  global-operation guard: this statement modified sentinel row
        public.webhook_disable_notifications (id 7ab2b88c-…), which belongs to no
        test — the bait planted by packages/test-harness/src/guard.itest.ts
CONTEXT:  PL/pgSQL function __sentinel_guard() line 41 at RAISE
```

No import to lint and no test to attribute to — exactly the case R6 argued only a
database-side check can see. The cleanup succeeded once reissued through a
connection carrying `options=-c relay.allow_global=all`.

## R52 — The only drain-driving suite on vitest's default budget

Run 9 of twenty, after eight green:

```
FAIL src/notifications/notifications.itest.ts >
     does not let ONE undeliverable row block every row behind it
Error: Test timed out in 5000ms.
```

A **different** test from run 4's, in the same file, at the same 5,000ms. The
backlog theory does not explain this one — the database held 58 undelivered
notifications at the time and none of them belonged to a sentinel, so R51's fix was
holding.

What the file actually is:

| suite | explicit test timeouts |
|---|---|
| `deliveries.itest.ts` | 60_000, 120_000, 180_000 |
| `test-event.itest.ts` | 60_000, 90_000 |
| `attempts.itest.ts` | 30_000, 60_000 |
| `outbox.itest.ts` | 30_000, 60_000 |
| **`notifications.itest.ts`** | **none — only its `beforeAll` declares one** |

All nine of its tests drive a global relay drain and then wait on a real SMTP
round-trip to Mailpit, and all nine ran on the 5,000ms default. Their measured
cost, with the lane running seventeen files in parallel:

```
✓ sends what the organisation needs, and Mailpit confirms the contents   653ms
✓ sets delivered_at only AFTER the send returns                         1953ms
✓ does not send a delivered row twice                                   1957ms
✓ sends twice for an endpoint disabled, re-enabled and disabled again    1446ms
✓ handles an organisation nobody can be written to                       861ms
✓ sends to EVERY member with an address, one message each               1014ms
✓ does not take anything else down with it when the mail server is gone   482ms
```

Half a second to two seconds, against a budget of five. That is not a margin, and
two different tests have now used it up on two different runs.

**Decision**: 30 seconds on every test in the file — the budget its siblings have
always declared, not a concession extracted by a red run.

**This is not a twelfth instance of the recurring fault**, and it is worth being
precise about the difference rather than adding it to a count. The class is a test
asserting a local fact about a *global operation*; this is a test whose *wall-clock
budget* was set below its own measured cost. The shared growing resource is the
machine, not the table.

Feature 030 exposed it rather than caused it. The seeder makes the lane busier and
thinned an excursion headroom that was always this thin — which is also why the
file passed for four chapters and fails now. `notifications.itest.ts` is fenced by
no chapter, so there is no post-series amendment for it.

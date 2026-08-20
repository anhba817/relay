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

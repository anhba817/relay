# Contract: the global-operation guard

Three interfaces, all internal to the test lane. None is public API; all three
are things a developer will meet while a test fails, so their shape is a contract
rather than an implementation detail.

---

## 1. The refusal

**When it fires.** A statement modifies or deletes a row belonging to the
sentinel environment, in a session that has not declared itself exempt.

**What it raises.** A Postgres exception, inside the offending transaction:

```
ERROR:  global-operation guard: this statement modified sentinel row
        public.webhook_endpoints (id 00000000-0000-4000-8000-000000000005),
        which belongs to no test
```

Verified against the real schema during research (R6).

**Required elements**, each earning its place:

| Element | Why |
|---|---|
| the prefix `global-operation guard:` | greppable, and says which of the lane's mechanisms fired |
| schema and table | says *what kind* of global operation it was — a sweep, a drain, a delete |
| the row id | lets the developer confirm against `data-model.md` that the row is the sentinel's |
| `which belongs to no test` | the diagnosis, not just the fact. A developer meeting this for the first time needs to know the row is not theirs |

**What it must not contain**: a suggested fix. The right scoped alternative
depends on what the test was trying to do, and a guess printed as advice is worse
than silence. That guidance belongs in the lint message, where the call site is
known.

**Where it surfaces.** In the **statement's own transaction**. For a statement
issued by a test, that is the test, with its own stack — the property the whole
design turns on, and the reason parallel file execution needs no serial diagnosis
mode and no bystander is ever blamed.

**For a statement issued by a background relay, it is a log line.** Both
`delivery-relay.ts` and `notification-relay.ts` catch their own errors and log
`*_drain_failed`, so a refusal raised inside one produces a log entry and a green
lane. A relay is the largest global operation in the system, which makes this the
guard's sharpest limitation rather than a footnote (research R13).

Today no suite is exposed to it: every file that spawns an api child sets all four
relay flags off. That is a convention repeated in seven files, so the setup hook
checks it — a non-exempt file with a relay enabled fails at startup rather than
running unguarded (FR-025).

## 2. The exemption

A **connection option**, carried by every connection a pool opens:

```
DATABASE_URL=…?options=-c%20relay.allow_global%3Don
```

**Not a statement.** `SET relay.allow_global = 'on'` through a pool sets it on
whichever connection the pool hands out. Measured across five checkouts from a
pool of three: `["on", null, null, "on", null]` (research R10). An earlier draft of
this contract specified the statement, and it would have produced an exempt suite
that failed two times in five.

**Who sets it.** The lane's setup hook, by rewriting `process.env.DATABASE_URL`
for its own worker before the suite calls `createPool()`, and only when the file
under test appears on the exempt list. No test sets it — a test that could exempt
itself is not guarded.

**Scope.** The worker, and therefore the file. Each test file runs in its own
worker, so exemption cannot leak between files.

**The seeder is the one exception, and it is bounded.** Planting deletes sentinel
rows, which the trigger forbids, so the seeder uses a dedicated `pg.Client` with
the option set and closes it before the first test. That connection never enters
the suite's pool (FR-024).

**Default.** Refusal. `current_setting('relay.allow_global', true)` returns null in
a connection that never carried the option, and null is not `'on'`.

**Reversal.** Nothing un-exempts a worker mid-run. A file is exempt or it is not,
decided once, from a list.

## 3. The lint refusal

**When it fires.** A `*.itest.ts` file not on the exempt list imports a function
that reads or writes across environments.

**The restricted names**, all from `services/api/src/db/repository`:

```
drainOutbox              drainDueDeliveries       drainDisableNotifications
sweepDisabledEndpoints   outboxDepth              pendingDeliveryDepth
```

The two `*Depth` functions are included because they return counts across every
environment — the shape of instance 4, where a global `count(*)` was compared
against itself.

**What the message must say**, unlike the trigger's: the alternative. The lint
rule knows the call site, so it can be specific.

```
drainOutbox reads across every environment. A test that needs its own rows
drained should bound the batch and assert on its own row, not on the count —
see specs/030-global-operation-guard/data-model.md. Files that legitimately
drive a global drain are listed in services/api/src/testing/exempt.ts.
```

**What it does not catch**, stated so nobody trusts it further than it goes:
indirect calls through a helper, and raw SQL. The trigger covers both. This rule
exists because the import line is where the decision is actually made — instance
6 was a deliberate choice at an import, by an author who had read about the other
five.

---

## Composition

The three defences overlap on purpose, and the overlap is not redundancy — each
catches something the others cannot:

| | writer via named import | writer via raw SQL | writer via helper | writer via a background relay | reader shape |
|---|---|---|---|---|---|
| **trigger** | ✅ | ✅ | ✅ | logged, not failed | — |
| **bait** | — | — | — | — | ✅ |
| **lint** | ✅ | — | — | — | partial (the `*Depth` names) |
| **relay-flag check** | — | — | — | ✅ at startup | — |

The fourth column is the one an earlier draft of this table did not have, and the
row that answers it is four lines of setup code rather than anything clever.

The trigger is the control. The lint rule is the prompt that arrives earliest. The
bait is the only one of the three that addresses the reader shape at all, and it
is the only one whose absence is silent.

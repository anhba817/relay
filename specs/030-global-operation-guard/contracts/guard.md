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

**Where it surfaces.** In the test that performed the mutation, with that test's
own stack. This is the property the whole design turns on: the exception is raised
in the culprit's transaction, so parallel file execution needs no serial diagnosis
mode and no bystander is ever blamed.

## 2. The exemption

```
SET relay.allow_global = 'on'
```

**Who may set it.** The lane's setup hook, and only when the file under test
appears on the exempt list. No test sets it directly — a test that could exempt
itself is not guarded.

**Scope.** The session. Each test file runs in its own worker with its own
connections, so exemption does not leak between files.

**Default.** Refusal. `current_setting('relay.allow_global', true)` returns null
in a session that never set it, and null is not `'on'`.

**Reversal.** Nothing un-exempts a session mid-run. A file is exempt or it is not,
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

| | writer via named import | writer via raw SQL | writer via helper | reader shape |
|---|---|---|---|---|
| **trigger** | ✅ | ✅ | ✅ | — |
| **bait** | — | — | — | ✅ |
| **lint** | ✅ | — | — | partial (the `*Depth` names) |

The trigger is the control. The lint rule is the prompt that arrives earliest. The
bait is the only one of the three that addresses the reader shape at all, and it
is the only one whose absence is silent.

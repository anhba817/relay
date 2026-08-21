# Chapter 3.10 — notes

Written from what happened, which is not what the plan said would happen.

## What shipped

Monthly usage quotas for two dimensions, in three tables and one column that was
already there.

- **Usage is a roll-up**, incremented by the transaction that writes the message.
  `usage_periods` for the count, `usage_active_users` for the distinct senders,
  both keyed on `(environment_id, period)` where the period is a stored `date` and
  not a computed one.
- **The caps live in `environments.quota_config`**, the jsonb column chapter 2.1
  declared and nothing read for eighteen chapters.
- **Enforced in `Repository.sendMessage`**, because chapter 3.8's limiter never
  sees `/internal/messages` and that is how a WebSocket send arrives. One throw,
  `402 quota_exceeded`, from the one service method both routes call.
- **The outbox a fourth time** in `quota_notifications`, drained by a fourth relay,
  with the at-most-one-email guarantee carried by a unique constraint rather than
  by the code that writes the rows.
- **No periodic job.** Nothing in this chapter performs a global operation.

## Did the design survive?

Mostly, and the two places it did not are the interesting ones.

**R5 held.** The plan's central prediction was that a quota needs no sweep,
because usage rises only on a send and the send transaction knows the value before
and after. Three phases of writing to three new tables later, the whole
integration lane against a freshly baited database produces fifteen refusals from
feature 030's trigger and not one names a quota table. No file joined the
exemption list. The instrument built by the previous feature changed this
chapter's design rather than only its tests, which is what that feature's SC-008
hoped for and could not measure.

**R4 was wrong twice over.** It proposed extending `environmentLimits` — the
per-request policy read — to return the caps and the usage as well, so the request
path would gain no query. Pass 2 of the analysis found the second caller,
`internal/session.controller.ts`, which hands the gateway its limits on every
WebSocket connect and would have paid for a usage join it never reads. And the
read would have been advisory anyway, because only the transaction's read decides
anything. Removing it made the design smaller.

**R8's lock could not exist.** The plan specified `FOR UPDATE` on the usage row to
bound cap overshoot to one message. Once the caps and the usage became one joined
read — which is a separate improvement — Postgres refused:

```
ERROR:  FOR UPDATE cannot be applied to the nullable side of an outer join
```

The specification had already said the overshoot is "bounded by concurrency, not
unbounded, and this is stated rather than defended against". R8 defended against
it; the defence turned out to be unavailable, and the spec's position is the one
that shipped.

## What the plan did not predict

**The column was already there, and a published chapter said so.** Chapter 3.8 was
offered `environments.quota_config` for rate-limit policy and refused it in print —
*"the column is named for quotas, quotas are a later chapter"*. This is that
chapter, and the plan added four typed columns beside it. **Three analysis passes
missed this**, because none of them read the artifacts against the published
series: pass 1 read the documents against each other, pass 2 against the code,
pass 3 against the build gates. That is a fourth surface, and it produced the
single largest design change in the chapter.

**The publication gate needed its own tasks.** Ten already-fenced files changed,
carrying 47 fences between them, and `check:fences` compares byte for byte. Pass 3
caught that nothing was scheduled to write them; the task it added said seven
files, and the answer was ten. `turbo.json`, `main.ts` and `app.module.ts` were
missing from the list, and `harness.ts` joined during Phase 4 — the list had been
written from the plan rather than from `check:fences`, which is the only thing that
knows.

**`app.module.ts` had to change and nothing said so.** The relay would have been
written, unit-tested, and never started.

## What went badly

**T033, in four acts.** An uncontrolled benchmark reported the quota path costing
273%, then 341%, then 303%, then 411% of the unconfigured path. Each time a
different cause looked obvious, and each time it was acted on: a `FOR UPDATE`
serialising the environment, an organisation lookup running on every send, two
round-trips holding a pooled connection above the pool size. None of them was it.
The cause was the benchmark — one environment per case, run in a fixed order, so
each measurement carried its own warm-up and table growth. Toggling the
configuration on a single environment with the phases instrumented gave **0.56ms
per send**, and the crossing block gave 0.000ms.

Two of the three changes are better code and stayed. The third was impossible to
undo. But three changes were made to a number that was never real, and this
project's whole subject is not reasoning where a measurement is cheap. The
measurement was cheap the entire time.

I also committed the flawed figures into a source comment and had to amend, which
matters because that comment is fenced into a published page.

**The traceability pass caught a leak I had just written, and the fix broke six
things.** Sixteen feature-local `FR-0xx` and `SC-0xx` ids had gone into this
chapter's comments — the same class feature 030 leaked fourteen of, in the chapter
whose own task list warns about it. Replacing them with `FR-RTL-*` rewrote **six
pre-existing comments** belonging to chapters 3.5, 3.6 and 3.9, whose bare
`FR-0xx` ids are part of the sixty-occurrence backlog feature 030 explicitly
scoped out. Restored by checking each altered line against the tag: if reversing
the substitution produced a line the tag had, the line was not mine.

A blunt search-and-replace across a file with eighteen chapters of history in it
is not a safe operation, and it took a second pass to notice.

**The battery was started on a tree that was still moving.** Twelve runs in, the
traceability pass changed source that the lane rebuilds from. Feature 030 made
exactly this mistake on its first attempt and recorded it; the record did not stop
it happening again. Restarted on a frozen tree.

## Two test expectations I got wrong

Both in the Mailpit tests, both arithmetic rather than code. A cap of 4 over four
sends crosses **three** thresholds, not two — 80% of 4 is 3.2, so nothing lands on
it and the fourth message clears 80 and 100 together; the test's own name said
three while its assertion said two. And sorting email subjects as strings puts
"100%" before "50%", so the assertion now extracts the percentages and compares
numbers.

Neither was an implementation defect. Both would have gone unnoticed with rounder
numbers.

## The numbers

| | baseline | after |
|---|---|---|
| unit | 251 | 286 |
| integration | 231 | 255 |
| coverage | 473 | 532 |
| statements | 89.08 | 89.51 |
| branches | 82.35 | 82.73 |
| functions | 89.25 | 88.94 |
| lines | 90.58 | 90.92 |
| fenced files in the chain | 165 | 173 |
| chapters in the chain | 26 | 27 |

Statements and branches now read the figures chapter 3.8 recorded and feature
030's baseline corrected downward as unreachable. They were reachable; two test
gaps were holding them down — an export nothing called, and the `start`/`stop`/`run`
hole that every relay in this codebase has. The fourth relay does not have it.

The chapter measures 2,548 prose words against a 2,000–4,000 gate, and 31 fences.

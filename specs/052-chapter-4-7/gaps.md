# Gaps — chapter 4.7

Filed rather than fixed. Each entry says what was measured, why it is not this chapter's
work, and what would close it.

---

## 047-1 / 048-1 — DR-10 AND FR-ANL-06 CANNOT BOTH HOLD — **CLOSED BY AMENDMENT, AND BOTH NUMBERS MOVED**

Filed at chapter 4.2 *for movement IV, where FR-ANL-06's job is built*, carried unchanged
through 048, 049, 050 and 051. This is that chapter, and both reasons were re-measured
rather than copied.

**REASON TWO, `uniq`, IS SHARPER THAN THE FILING.** 047-1 recorded *"exact to ~65,000,
0.5129% at 70,000"* from a corpus. Measured here with no corpus at all —
`reinterpretAsUUID(toUInt128(number))` over `numbers(n)`, because the error is a property of
the sketch at a cardinality and nothing else:

    cardinality       uniq    uniqExact   uniqMerge      error
        65,000      65,000      65,000      65,000     0.0000%
        65,536      65,536      65,536      65,536     0.0000%
        65,537      65,909      65,537      65,909     0.5676%
        70,000      70,449      70,000      70,449     0.6414%
     1,000,000   1,005,409   1,000,000   1,005,409     0.5409%

**The cliff is at 2^16 and it is one distinct value wide.** One user past 65,536 the error
is 5.7x the bound it has to sit under. `uniqMerge` over the rollup's
`AggregateFunction(uniq, …)` returns `uniq`'s figure at every point, so the rollup inherits
the error rather than smoothing it. **047 loaded a corpus for this and did not have to.**

**REASON ONE, THE TTL BOUNDARY, WAS NEVER A SINGLE NUMBER.** 047-1 published 0.49%. Measured
against a probe table with the same 90-day TTL, 92,000 rows at 1,000 a calendar day: the cut
removed the oldest day whole and **53 of the next day's 1,000** — exactly the rows lying
before the server's wall clock, which read 01:16:07 against 86-second row spacing. A rollup
computed before the cut therefore disagrees with its source by **53 / 90,947 = 0.0583%** at
that hour, **0% just after midnight**, and **1,000 / 91,000 = 1.0989%** just before the next
one. 047's 0.49% is one point on that curve — 45% of a day, a run at about 10:48.

**AND THE TTL IS A SCHEDULE, NOT AN EVENT**, which the probe reproduced as its control: all
92 days were present straight after the insert and 1,053 rows vanished only when a merge was
forced.

**WHY IT CLOSES HERE, AND NOT BY ANY OF THE FOUR OPTIONS 047 LISTED.** 047-1 offered: widen
the tolerance, exempt the boundary day, keep a second exact-distinct column, or let metering
read raw events and amend DR-10. **None was taken.** The clause now states where its own
bound is unreachable (SRS revision 1.14) and the chapter publishes no percentage that implies
otherwise. That is constitution VII's *"resolved explicitly by amendment rather than silent
divergence"* — the arithmetic is unchanged and it is written down where the requirement is,
instead of in a gaps file five features deep.

---

## 052-1 — `pnpm coverage` REPORTED NOTHING AT ALL ON A RED LANE, AND HAD SINCE CHAPTER 4.4

**Fixed here rather than filed**, but the shape is worth the entry. `coverage.reportOnFailure`
defaults to false, so one failing test suppresses the entire report: no table, no per-file
threshold errors, no `coverage/` directory, and the single line `Coverage enabled with v8`.
Run both ways over the same three files — green printed the table and every threshold error,
one red test printed neither.

The api's `request-log.itest.ts` has been red on any machine with no ingester process since
4.4 shipped it (050-8), so **the gate that measures constitution VI has been answering with
silence, and silence is indistinguishable from a pass at a glance.** Set to `true` in
`vitest.coverage.config.mts`.

**What stays open**: nothing checks that a gate produced output. Every `check:*` script in
this project refuses a run that compares nothing (045-81); the coverage lane does not.

---

## 052-2 — `services/ingester/src/shape.ts` IS PINNED AT 100 AND MEASURES 95.12

The first reporting run after 052-1 found it immediately:

    ERROR: Coverage for statements (95.12%) does not meet
           "services/ingester/src/shape.ts" threshold (100%)

39 of 41 statements and 78 of 82 branches, at **100% lines and 100% functions** — so every
function runs and two statements inside them do not. The uncovered arms are
`shapeConnection`'s: `shape.test.ts` imports `route`, `shape` and `shapeRequest` and never
constructs a `connection.opened` or `connection.closed` record, so that path is reached only
through the ingester's integration suite.

**Left at 100 rather than lowered.** This chapter did not measure it down, it made it
visible, and lowering another chapter's ratchet is the move this project's own notes call the
failure mode. Closes when `shape.test.ts` gains two cases — one connection record routed,
one with a missing field called malformed.

---

## 052-3 — A CLEANUP ENUMERATES TABLES BY HAND, AND THE NEXT CHAPTER'S TABLE IS NOT ON THE LIST

`services/ingester/src/metering.itest.ts:65`'s `clean()` deletes its environment's rows from
`connection_events`, `message_events`, `daily_usage_v2` and every `.inner_id.*` table. It does
**not** delete from `daily_usage_billing`, which chapter 4.6 added after that suite was
written. So every run removes the source rows and leaves the rollup rows.

Measured: the backfill expansion run against `connection_events` today yields **8 rows, 56
minutes, 8 environments**; `daily_usage_billing` holds **7 rows, 144 minutes, 4
environments**, and the four are the ingester's own fixture ids, which appear in
`connection_events` for none of them. **The rollup and its source hold disjoint tenant sets.**

Closes when the cleanup reads the table list from the store rather than from memory — the
`.inner_id.*` half already does exactly that, three lines below.

---

## 052-4 — `reset-lane.itest.ts` COUNTS ORGANISATIONS A NEIGHBOUR DELETES (045-74's CLASS, NINTH)

    AssertionError: the reset removed an organisation: expected 3092 to be 3094

Reproduces with the harness lane run alone, twice. It is not the script: `scripts/reset-lane.mjs`
deletes from `webhook_deliveries` and JetStream consumers and nothing else. The deletion is
`guard.itest.ts:292` — `DELETE FROM organisations WHERE id = $1` — in the other file of the
same two-file lane.

**The scope looks like a scope, which is why the class keeps recurring.** The assertion counts
`organisations WHERE created_at <= pinned`, which is feature 044's own rule — *"pin one
instant before the script runs"* — applied to the creation side only. A neighbour deleting a
fixture it created before that pin moves the number, and no predicate about this test's own
rows was ever written. `check-lane-scope.py` reports it clean because the query carries a
predicate.

Closes with one predicate naming this test's organisation.

---

## 052-5 — "RAISES AN ALERT" HAS NO MECHANISM, AND THE EXIT CODE IS NOT ONE

FR-ANL-06 requires *"a daily reconciliation job that raises an alert on breach"*. There is no
alerting integration in these three repositories. What exists is two mail paths —
`quotas/quota-email.ts` for a quota crossing and `notifications/notification-relay.ts` for a
disabled endpoint — sharing one transport, `notifications/mailer.ts`, whose default is
`smtp://localhost:1025`: the lane's own catcher. Their failure mode is already visible as
`quotas.unaddressable` / `notifications.unaddressable` — *no member has an email address*.

The job exits non-zero, and `exitCodeFor` makes that testable. **A notification with no
recipient is not an alert, and neither is an exit code.** A real one needs a delivery target
that is not a person's inbox, a deduplication key so a job breaching for thirty days sends one
alert rather than thirty, and a severity that distinguishes 0.2% from 100%. The platform has
none of the three anywhere.

---

## 052-6 — CONSTITUTION III's AMENDMENT IS STILL OWED (carried from 051-2, AND THE ARCHITECTURE ALREADY ASSUMED THE ANSWER)

051-2 recorded that the only way to demonstrate DR-10's rollup was to run the cross-path read
constitution III's first sentence forbids. This chapter met the same clause from the other
side: FR-ANL-06 requires comparing the analytical store against PostgreSQL, and III says
billing, metering and dashboard analytics read only from ClickHouse.

The reading that makes both true — **the reconciler is none of those three roles, and an
auditor confined to one side of a fence cannot check the fence** — is recorded in SRS revision
1.14 and in `docs/05-sad.md` §6.2. **It is still not in the constitution**, which is the only
document that can ratify it, and constitution VII requires an amendment rather than silent
divergence.

**What is new**: `docs/05-sad.md`'s ADR-06 has said it all along. Its accepted trade-off reads
*"mitigated because the only strict consumer (metering) reconciles daily against Postgres
(FR-ANL-06)"* — so the cross-path read is the mitigation that makes choosing NATS over Kafka
acceptable. Removing it costs that ADR its argument. **The conflict was written into an
accepted decision and nobody had read the two documents beside each other.**

---

## 052-7 — A FEATURE-LOCAL ID WAS CITED AS A PUBLISHED CLAUSE IN TWO DOCUMENTS

`docs/04-srs.md`'s DR-09 and `docs/05-sad.md:879` both cited **`FR-003a`** as though it were a
clause. **There is no `FR-003` in the SRS**, and `FR-003a` is a feature-local id that four
features use to mean four different things — a refusal message in 042, a channel read in 034,
a rollup TTL in 047, a corpus report in 046.

Both citations are corrected. The class is open: nothing checks that an id cited in a
published document resolves in that document. `check-srs-ids.sh` checks the reverse direction.
It is how 044 shipped four artifacts agreeing on two clauses that do not exist, and how this
chapter found a sentence — *"the rollups carry no TTL"* — that chapter 4.6 had falsified in
the same feature that wrote it.

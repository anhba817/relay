# Contract — the reconciliation job

**What it takes, what it returns, and what it may not touch.** This is the artifact nothing
else reads, which is where 046 and 047 each hid a defect for six and four passes, and where
4.6 left the implementation unnamed until analysis pass 1. Every invocation below is one
somebody can paste.

## Called in isolation

`docs/12` row 8 says so in as many words: *"built to be callable in isolation (§2.3)."*

```ts
import { reconcile } from "./reconcile.js";

const report = await reconcile({
  environmentId: "…",   // one tenant; the job never sweeps
  period: "2026-08-01", // periodOf's shape: the first day of a calendar month, UTC
});
```

**It returns its report as a value.** Not a log line a test greps, not a side effect: §2.3's CI
half plants a drift and asserts the raise, and that assertion needs something to hold.

**It takes an explicit period.** No clock. Reconciling the current month compares a rollup
still being written against a counter still being incremented — see `data-model.md`.

**It is one tenant per call.** R1 measured why: aggregating across tenants turned 19 breaches
into 0.2694%, a number below any threshold a reader would question. A sweep is a loop over
this function in the caller, and the caller is where a summary belongs.

## The thin caller

```bash
node scripts/reconcile-usage.mjs --environment <uuid> --period 2026-08-01
```

Exits non-zero on any breach. That is the whole of "raises an alert" this platform can
currently do: **there is no alerting integration**, and the one notification path that exists
is `quotas/quota-email.ts`, whose failure mode is already visible in the lane as
`quotas.unaddressable: no member has an email address`. **A notification with no recipient is
not an alert**, and the chapter says what a real one would cost rather than implying the exit
code is one.

## What comes back

Four rows, one per FR-ANL-05 quantity, each carrying both totals, the named operational source,
the percentage, and one of four verdicts — `pass`, `breach`, `not-comparable`, `no-data`. Their
definitions and the reason there are four are in `data-model.md`.

**The percentage is null whenever either side is null.** A number computed against an absent
counterpart is the failure this contract exists to prevent: it would read as a measurement.

## What it may not touch

- **No writes.** The job is a comparison. Two invocations with the same arguments return the
  same report, asserted by a test.
- **No `daily_usage_v2`.** The channel-keyed rollup holds 147,534 rows where the billing one
  holds 281 for the same data (chapter 4.6). The reconciler has no use for the dimension and
  every reason to avoid its cost.
- **No raw event tables.** DR-10: *"billing never scans raw events"*, and a checker that scans
  what the thing it checks may not scan is checking something else.

## What it reads across the boundary, and why that needs saying

**The job reads Postgres and ClickHouse in one process.** Constitution III says *"billing,
metering, and dashboard analytics read only from the analytical store"* — and the same
constitution requires this reconciliation. The reading that makes both true: **the reconciler
is none of those three roles.** It audits the boundary, and an auditor confined to one side of
a fence cannot check the fence.

That reading is available in the clause's own words and **is written down nowhere**. The
chapter states it; `gaps.md` 051-2 already carries one conflict in this family that the
constitution must settle, and this is the second.

## What this contract does not cover

- **Making the numbers agree.** `docs/12` §2.3 gives agreement to the milestone at chapter 4.9
  and gives this chapter detection.
- **A sweep across all tenants.** A loop in the caller, and the summary shape it needs is not
  specified here because no requirement asks for one.
- **A schedule.** FR-ANL-06 says *"daily"*; nothing in this platform schedules anything, and
  inventing a scheduler to satisfy an adverb would be the kind of scope this project refuses.

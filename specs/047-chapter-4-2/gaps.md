# Gaps — chapter 4.2

Filed rather than fixed. Each entry says what was measured, why it is not this chapter's
work, and what would close it.

---

## 047-1 — DR-10 AND FR-ANL-06 CANNOT BOTH HOLD, AND THERE ARE **TWO** REASONS

FR-ANL-06: *"Metered totals shall agree with counts derived from operational data to
within 0.1%."* DR-10: metering never scans raw events. So the reconciliation has to run
against the rollup, and the rollup disagrees with the raw table in two independent ways.

**REASON ONE — THE TTL BOUNDARY, AND IT BITES AT ANY CARDINALITY.**

Comparing the busiest tenant day by day over the same ninety days, both sides day-aligned:

    days compared   91
    days agreeing   90
    days differing   1     2026-06-15: raw 6,220, rollup 11,161, difference 4,941

The differing day is the **oldest day in the window**, every time. The raw table's TTL cuts
at a timestamp — `ts + 90 days < now()` — and the rollup's finest grain is a day. The view
counted that day whole at insert; the merge then removed the rows whose ninety days had
passed. **The boundary day can never reconcile**, and the gap moves continuously as `now()`
advances through it.

    4,941 / 1,004,877 = **0.49%**, against FR-ANL-06's 0.1%.

This is not a cardinality effect and no corpus size hides it.

**REASON TWO — `uniq` IS APPROXIMATE ABOVE ~65,000 DISTINCT.**

    distinct     uniq        error
      10,000     10,000      0%
      50,000     50,000      0%
      60,000     60,000      0%
      65,000     65,000      0%
      70,000     70,359      0.5129%
     100,000    100,315      0.315%
     500,000    502,646      0.5292%

**The threshold is a cardinality, not a row count.** This corpus holds 5,000 users, so
`uniqMerge` against `uniqExact` came back **5,000 against 5,000, 0.0000%** — a perfect
agreement that proves only that the corpus is too small to show the problem. A reader who
tested at this size and shipped would meet it at 65,001 distinct senders.

**Why it is not closed here**: there is no reconciler to test an amendment against, and
amending a published clause without one is deciding before measuring. Filed for movement
IV, where FR-ANL-06's job is built. Closing it means choosing: widen the tolerance, exempt
the boundary day, keep a second exact-distinct column, or let metering read raw events for
reconciliation only and amend DR-10.

---

## 047-2 — `delivery_latency_ms` HAS NO PRODUCER

SAD §6.2 publishes it; nothing writes it until FR-ANL-10's chapter. It is
`Nullable(UInt32)` here rather than SAD's `UInt32` — left non-nullable, every row would
read **0 ms**, a measured claim about a delivery nobody timed (FR-006a). Closes when the
ingester lands.

---

## 047-3 — THE ROLLUP IS UNBOUNDED

`daily_usage` carries no TTL and that is deliberate (FR-003a): metering must not lose
history when raw events expire. It is also a table that grows forever at
`environments × days`. At this corpus, 363 rows for 1,241,029 raw — but nothing in the
platform ever removes a row from it, and no clause says how long metering history is kept.
Not this chapter's to decide.

---

## 047-4 — THE THREE PART 1 TAGS (carried from 046-8)

`part1-ch1`, `part1-ch2`, `part1-ch3` are on neither `main` nor
`backup/pre-main-move-20260911`, and are the only thing keeping those commits reachable.
Unchanged by this chapter, restated so it is not lost.

---

## 047-5 — TWO GATES PART 4 NEEDS AND STILL DOES NOT HAVE

`docs/12` §6: a standing `check:redirects`, and a gate refusing chapter ordinals in
platform source. Neither exists. This chapter added no ordinal to platform source, which
is the condition the second gate would enforce and nothing checks.

# Feature Specification: Chapter 4.16 — "Storage on the bill"

**Feature Branch**: `062-chapter-4-16`

**Created**: 2026-09-29

**Status**: Draft

**Input**: User description: "chapter 4.16"

Movement VI, fourth chapter. `docs/12` §3 row 17: *FR-MED-12: stored bytes metered per tenant
per day, into the store movement IV built.* No open question in §7 is addressed to it.

## Vocabulary

Two words this chapter has to keep apart, because one of them is already taken:

- **a level** — how many bytes a tenant is storing *right now*. The quota reads this.
- **a delta** — how many bytes a tenant's storage changed by, on one day. A rollup sums these.
- **`stored_delta`** — an existing column that counts neither. See the premise table.

## What the premise check found

Run before this specification was written.

| Claim the brief rests on | Measured | Consequence for scope |
|---|---|---|
| Nothing meters stored bytes | Correct. `stored_bytes` appears only in `0016_storage_quota.sql`, as a **quota configuration key**. No producer, no rollup, no reader. | The whole clause is unbuilt. |
| `daily_usage_billing.stored_delta` is the column for this | **It is not.** It is `sum(multiIf(event = 'created', 1, event = 'deleted', -1, 0))` over `message_events` — a net count of **stored messages**, not bytes. | **A name collision a planner would read as "already built".** This chapter adds a column; it does not fill that one. |
| The technique is undecided | **DR-17 already states it**: *"a daily rollup summing `media_events` deltas (uploaded/deleted)"* — and `ingester/src/metering.ts` names it in a comment, calling its own `storedMessages` *"the same shape one table over."* | The mechanism is specified. What is missing is every part of it. |
| FR-MED-12 is the whole requirement | **DR-17 adds one FR-MED-12 never mentions**: *"reconciled weekly against an object-storage inventory listing — the media analogue of FR-ANL-06."* | Two deliverables, and the second needs a bucket listing nothing in this platform can do. |
| The precedent works | `storedMessages` is a correct query over `daily_usage_v2`, and **`message_events` holds 0 rows and has no producer** — 4.6's finding, still true. | **The pattern this chapter is told to copy has never carried data.** |
| A daily figure needs a scheduler | For the rollup, no: a materialised view fires on insert, which is why DR-17 says *summing deltas* rather than *sampling a level*. **For DR-17's weekly reconciliation, yes** — and ADR-28 records that this platform has no runner for a recurring job, no `schedule:` trigger, and one hand-run script. | The daily half is reachable. The weekly half meets ADR-28. |
| The quota half is outstanding | **Built at 4.10.** `reserveMediaSlot` sums `declared_bytes` over the environment's non-`rejected` rows, and 4.15 added that renditions count. | FR-MED-12's *"enforced as FR-RTL-05's storage quota"* is already met. This chapter does not rebuild it. |
| *"Visible in the dashboard"* is in scope | **There is no dashboard.** No service, no app, and FR-DSH-04/05 are unbuilt. | That clause cannot be discharged here and the chapter must say so rather than quietly drop it. |
| The lane has something to meter | **8,120 objects, 4,255 MB declared across 1,576 environments** — and `api_requests` holds 118,238 rows, so the analytical path itself is live. | Unlike 4.15, the corpus is real. |

**A DELTA IS NOT A LEVEL, AND THE DIFFERENCE IS WHERE THIS CHAPTER'S RISK LIVES.** Summing
deltas gives a level only if no event is ever lost. A sampled level is self-correcting: get it
wrong on Tuesday and Wednesday's sample is right anyway. A delta-summed level is not — one
dropped `media_events` row makes every subsequent day wrong, permanently and silently, and the
error compounds in the direction of whichever event went missing. **That is exactly why DR-17
pairs the rollup with a weekly reconciliation**, and it is why the two halves of that clause are
one feature rather than two.

**AND THE RECONCILIATION CANNOT FAIL IN THE DIRECTION THAT MATTERS YET.** The `deleted` delta
needs something that deletes, and chapter 4.15 established that **nothing in this platform
deletes a `media_objects` row** — the rejection path removes bytes and keeps the row on purpose.
So until the erasure chapter ships, the level only ever rises, and a reconciliation against the
store would agree for a reason that will stop being true. This is 4.7's shape — a clause whose
verification is unreachable for reasons that are not defects — and the chapter's job is to say
which part is verified, which is vacuous, and what would make it real.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A tenant's stored bytes have a daily history (Priority: P1)

The platform records every change to a tenant's stored bytes as it happens, and a day's net
change is available per tenant without scanning raw events.

**Why this priority**: it is FR-MED-12's headline and DR-17's stated technique, and it is the
half that is reachable without a scheduler. Everything else in this chapter reads it.

**Independent Test**: upload objects, let them resolve, and read the day's delta for that tenant
from the rollup; the number matches what the operational store says changed.

**Acceptance Scenarios**:

1. **Given** a tenant with no media, **When** an object reaches a state that makes its bytes
   count toward the quota, **Then** that day's delta for that tenant increases by exactly the
   bytes the quota counts.
2. **Given** an object that is refused or rejected, **When** its lifecycle completes, **Then**
   the tenant's delta does not include its bytes, and the rollup agrees with the quota's own sum.
3. **Given** objects belonging to two tenants, **When** either is read, **Then** the figure is
   that tenant's alone.
4. **Given** a day with no media activity for a tenant, **When** the rollup is read, **Then** the
   answer is zero rather than absent, and a caller cannot tell "no change" from "no tenant".
5. **Given** a rendition, **When** it is created, **Then** its bytes appear in the same delta as
   an upload's, because 4.15 settled that derived bytes are charged.

---

### User Story 2 - The bill can be checked against the store (Priority: P2)

Someone can ask whether the metered level matches what the object store actually holds, and get
an answer per tenant rather than one number for the platform.

**Why this priority**: DR-17 requires it, and it is the only thing that makes a delta-summed
level trustworthy. Second because it needs US1 to have produced something to check.

**Independent Test**: plant a deliberate disagreement between the metered level and the store's
contents, and confirm the comparison reports it, per tenant, with the direction of the drift.

**Acceptance Scenarios**:

1. **Given** a metered level and a store whose contents agree, **When** the comparison runs,
   **Then** it reports agreement for each tenant compared.
2. **Given** a tenant whose store holds bytes the meter does not know about, **When** the
   comparison runs, **Then** it reports that tenant and the direction of the difference.
3. **Given** a tenant present on one side only, **When** the comparison runs, **Then** it
   reports a verdict distinguishable from agreement and from a breach.
4. **Given** the comparison, **When** it is invoked, **Then** it reports what it compared and how
   many tenants it looked at, so a zero cannot mean "nothing was checked".

---

### User Story 3 - Uploads are counted by kind (Priority: P3)

The platform records how many objects a tenant uploaded, broken down by the kind of media.

**Why this priority**: it is the clause's second sentence, it is cheap once US1's event exists,
and nothing downstream depends on it yet.

**Independent Test**: upload objects of two kinds and read the per-kind counts for that tenant
and day.

**Acceptance Scenarios**:

1. **Given** uploads of more than one kind on one day, **When** the counts are read, **Then**
   each kind's count is separate and their total is the day's uploads.
2. **Given** a rendition, **When** the counts are read, **Then** the specification states
   whether it is an upload, and the answer is the same everywhere it is asked.

---

### Edge Cases

- An object whose bytes are counted at one moment and recounted at another: the delta must be
  emitted once, or the level drifts by the size of the object.
- A verdict delivered twice: 4.15's compare-and-set means the second changes nothing, so no
  second delta may be emitted either.
- An object whose declared size and verified size differ: the quota counts one of them, and the
  meter must count the same one or the two disagree by construction.
- The analytical store unreachable when a delta would be emitted: constitution III forbids the
  operational path depending on it, so the delta must survive the outage or be lost knowingly.
- A tenant deleted: the operational rows go and the analytical history does not, which is
  DR-09/DR-10's intent and worth stating rather than discovering.
- The reconciliation on a bucket holding objects from tenants the rollup has never seen —
  including objects written by tests.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The platform MUST record a change in a tenant's stored bytes at the moment the
  change becomes true, as a signed quantity, attributed to the tenant and the day.
- **FR-002**: The quantity recorded MUST be the same quantity the storage quota enforces, so the
  two cannot disagree about what a byte is.
- **FR-003**: A tenant's stored level MUST be derivable without reading raw events (DR-10) and
  MUST be that tenant's alone, **for any day within the rollup's retention horizon**. The
  rollup's TTL is 25 months, and a level accumulated from deltas is understated by everything
  the TTL has removed — so *"any day"* is bounded, and the bound is stated rather than implied.
- **FR-003a**: The specification MUST state what re-bases a level the retention boundary has
  truncated, and the mechanism MUST be one this chapter builds or one it names.
- **FR-004**: Emitting the record MUST NOT be able to fail a caller's request, and MUST NOT make
  the operational path depend on the analytical store (constitution III).
- **FR-005**: A change MUST be recorded exactly once, including when the operation that caused it
  is retried or delivered twice.
- **FR-006**: The platform MUST provide a comparison of the metered level against the object
  store's own contents, per tenant, reporting the direction of any disagreement (DR-17).
- **FR-007**: The comparison MUST report how many tenants it examined, so an empty result is
  distinguishable from an unexamined one.
- **FR-008**: The comparison MUST have a verdict for a tenant present on one side only, distinct
  from both agreement and breach.
- **FR-009**: The platform MUST count uploads per tenant per day, separated by kind.
- **FR-010**: The specification MUST state whether a rendition is an upload for FR-009's purpose,
  and every reader MUST give the same answer.
- **FR-011**: Where a clause of FR-MED-12 or DR-17 cannot be discharged in this chapter, it MUST
  be recorded in the SRS as unmet with the reason, rather than left to look built.
- **FR-012**: The chapter MUST state what the delta-summed level costs in reliability against a
  sampled one, and what the reconciliation does about it.

### Key Entities

- **Storage event**: a signed change to a tenant's stored bytes, with the tenant, the moment, the
  kind of media, and what caused it. The unit the rollup sums.
- **Daily storage rollup**: per tenant, per day — the net byte change and the uploads by kind.
  Read for a level by accumulating; read for a chart by the day.
- **Store inventory**: what the object store reports it holds for a tenant, which is the only
  thing that can contradict the meter.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a tenant exercised end to end, the level derived from the rollup equals the
  quota's own sum, asserted as an equality rather than a tolerance.
- **SC-002**: The rollup is read without touching raw events, demonstrated by the read's own cost
  against the raw table's, both measured.
- **SC-003**: A tenant's figure contains no other tenant's bytes, probed by deleting the scope
  predicate and observing which tests fail — and each arm recorded as tested or unnecessary.
- **SC-004**: A repeated verdict produces exactly one delta, asserted after a deliberate
  duplicate.
- **SC-005**: With the analytical store stopped, the operation that would emit a delta still
  succeeds, **and the record is on the stream during the outage and in the rollup after the
  restart.** The ANALYTICS stream's `max_age` is 7 days, so this is a confirmation rather than
  a discovery — an earlier draft asked the chapter to report "whichever of the two it is",
  which is a criterion that passes on either answer.
- **SC-006**: The reconciliation reports, for a planted disagreement, the tenant and the
  direction, and for an agreeing tenant reports agreement; the count of tenants examined is part
  of the output in both cases.
- **SC-007**: Uploads by kind sum to the day's total uploads for every tenant in the sample.
- **SC-008**: Every clause of FR-MED-12 and DR-17 is marked met, unmet-by-decision with a reason,
  or unreachable with the reason — and the count of each appears in the chapter.
- **SC-009**: The chapter publishes what the delta approach costs: the drift from one lost event,
  measured rather than asserted, and how long it would persist.
- **SC-010**: `pnpm check:fences` reports 0 at the close; `pnpm lint`, `pnpm exec turbo run
  typecheck` and the full lane set are green; and the CI error set is compared per error against
  the pre-chapter baseline in both directions.
- **SC-011**: The chapter's prose is within the 2,000–4,000 word bound with at least one `TRAP`
  box, and every published fence replays onto `relay-platform`.

## Assumptions

- Row 17 of `docs/12` §3 is chapter 4.16; §3 keeps pre-contraction ordinals, so row N is chapter
  4.(N−1).
- The quantity metered is `declared_bytes`, because that is what the quota sums (4.10) and
  FR-002 requires the two to agree. Where a verified size differs, the quota's choice wins and
  the divergence is recorded rather than reconciled.
- A rendition is **not** an upload for FR-009's count — nobody uploaded it — but its bytes **are**
  in the level, which 4.15 settled. FR-010 exists to stop those two answers drifting apart.
- DR-17's *"weekly"* is a cadence this platform cannot run (ADR-28). The comparison ships as an
  invokable command with the cadence recorded as unmet, on ADR-28's own precedent.
- *"Visible in the dashboard"* is out of scope: no dashboard exists, and FR-DSH-04/05 are
  unbuilt. Recorded under FR-011 rather than dropped.
- The chapter ships English prose only.

## Open questions carried into planning

1. **Whether the delta is emitted on the operational path or derived from what already flows.**
   The platform already has an analytical producer per request (4.4) and per connection (4.5);
   a third is a known cost. Deriving from existing records instead would avoid it and may not be
   possible.
2. **What the reconciliation lists.** The store has no listing call in either service, and the
   bucket holds objects from every tenant plus test debris. Whether it lists by prefix, or reads
   the operational rows and heads each object, is a measurement.
3. **Whether `daily_usage_billing` gains a column or storage takes its own rollup.** DR-10 was
   amended after 4.6 measured a rollup whose key made billing reads more expensive than the raw
   table; the same question applies to widening a table that is already read per tenant per day.
4. **What happens to the level when the erasure chapter starts deleting rows.** This chapter's
   `deleted` delta has no producer, so the design must be one the reaper can emit into without
   rework.

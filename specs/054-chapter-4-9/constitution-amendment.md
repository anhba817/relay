# Constitution amendment proposal — Principle III, fourth bullet

**Proposed by**: feature 054, chapter 4.9, "Milestone: the meter agrees" · 2026-09-17
**Status**: **proposed, not applied.** See "Why this is not committed" below.
**Version bump**: **MINOR**, 1.1.0 → 1.2.0 — materially expanded guidance; no principle removed
or redefined.
**Supporting ADR**: **ADR-28** (`docs/05-sad.md`, argument in `docs/06-adr-deep-dives.md`). The
governance section requires one: *"Amendments that alter Principles I–IV (correctness
properties) additionally require an updated or superseding ADR in `docs/` demonstrating the
drivers changed."*

---

## The conflict, quoted from both documents

**`.specify/memory/constitution.md`, Principle III, fourth bullet** (unchanged since ratification):

> Metered totals MUST reconcile against operational counts to within 0.1%, verified by
> a daily job that alerts on breach.

**`docs/04-srs.md` FR-ANL-06, as amended at revision 1.14** (feature 052, chapter 4.7), in part:

> **AND THE 0.1% BOUND IS UNREACHABLE FOR THREE OF THE FOUR QUANTITIES, FOR REASONS THAT ARE NOT
> DEFECTS.** Unique active users: `uniq` is exact to **65,536** distinct and off by **0.5676%**
> at 65,537. Any quantity read at the raw retention boundary: a daily rollup's finest grain is a
> day and the TTL cuts at a timestamp, so the oldest day in the window disagrees by **0% at
> midnight rising to 1.0989% just before it**, on the same data. Connection-minutes: the meter
> bills every calendar minute a connection was open and the records bill only connections that
> **closed** […]
>
> **AND "RAISES AN ALERT" HAS NO MECHANISM HERE.** This platform has no alerting integration;
> the job exits non-zero […]

The governance section is why this cannot be left alone:

> Where it conflicts with the SRS or SAD, the conflict MUST be resolved explicitly by amendment
> rather than ignored.

## The sentence is three requirements, and the platform has one

Nobody had written this down before feature 054's phase 1 went looking for the runner.

| part of the sentence | mechanism | recorded where, before this proposal |
|---|---|---|
| *"reconcile … to within 0.1%"* | chapter 4.7's reconciler, `services/api/src/metering/reconcile.ts` | SRS 1.14, and measured in `docs/13-metering-measurement-2026-09-17.md` |
| *"verified by a **daily job**"* | **none** | **nowhere** |
| *"that **alerts on breach**"* | **none** — the job exits non-zero | SRS 1.14 |

**The daily job has no runner of any kind.** Measured, with the corpora named because a zero from
a grep is a claim about the corpus only if the corpus is named:

    reconcile-usage in relay-platform/package.json     0 occurrences
                       relay-platform/turbo.json        0
                       .github/workflows/ci.yml         0
                       relay-tutorial/package.json      0
                       any *.sh in either repository    0
    ci.yml triggers    push, pull_request — no `schedule:`

The platform runs five background loops — `RELAY_OUTBOX_RELAY`, `RELAY_DELIVERY_RELAY`,
`RELAY_QUOTA_RELAY`, `RELAY_NOTIFICATION_RELAY`, `RELAY_EVENT_CONSUMER` — so the pattern for
recurring work exists and the reconciler is the one recurring job built as a hand-run script.
**ADR-28 decides that, and its decision is to record the absence rather than build a sixth
loop**: what a daily sweep would buy today is a `no-data` verdict for every tenant on the
platform, because no environment has both sides of the comparison.

## What does not change

**The bound itself, for the quantity that can meet it.** Measured at 121,057 messages in one
tenant-period — a volume where the smallest expressible drift is 122 messages, 0.1008% — metered
messages and operational messages agree to **0.0000%**. 0.1% is a real threshold there and it is
met.

## The proposed replacement

Replace the fourth bullet of Principle III with:

> - Metered totals MUST reconcile against operational counts to within 0.1% **for the quantities
>   whose two sides can express that bound**, verified by a reconciliation job. **The clause is
>   three obligations and the platform currently meets one**: the comparison exists
>   (SRS FR-ANL-06, chapter 4.7) and is exercised on every push by a planted-drift test; the
>   **schedule** is recorded as absent (ADR-28) rather than implied; and **"alerts on breach"
>   has no mechanism in this platform** (SRS 1.14) — the job's exit code is what it can currently
>   mean. **Three of the four metered quantities cannot meet the bound for reasons that are not
>   defects** and are named in FR-ANL-06: `uniq`'s exactness cliff at 65,536 distinct, the
>   retention boundary a daily rollup cannot align with, and connection-minutes counting a
>   different population on each side. A figure published against this clause states its
>   quantity, its volume, and the smallest drift that volume can express.

## Migration impact on in-flight specs and plans

**None blocking.** No in-flight spec depends on the flat 0.1%:

- Feature 054's own measurement is taken against FR-ANL-06 as amended at 1.14 either way, and
  says so in `docs/13`'s first paragraph.
- `docs/12` §2.3's milestone claim is scoped to the planted-drift test and the recorded figure,
  both of which survive the amendment unchanged.
- Movement V's chapters (hosted media) touch DR-17, *"the media analogue of FR-ANL-06"*, which
  inherits the same three-obligation reading and is better served by it than by the original.

Plans already merged that ran a Constitution Check against the old wording do not become wrong:
the bound is unchanged where it is reachable, and the added guidance is about what else the
sentence was asking for.

## Why this is not committed

The governance section specifies a procedure with a human in it — *"Amendments are proposed as a
PR modifying this file"* — and this project has no separate PR flow: a chapter commits to `main`.
Applying a change to the document that governs every other decision, inside a tutorial chapter
that the same author wrote, would be the constitution amending itself.

So the amendment is written out in full, ready to apply as one edit plus a version line, and the
decision to apply it belongs to whoever ratifies the constitution. **This is the third
constitution III item this movement has produced** — `gaps.md` 051-2 and 052-6 carry the other
two, both about the cross-store read — and it is the first about the clause a chapter was written
to verify.

**What this feature did instead of waiting**: measured the figure the clause asks for, at a volume
where it means something; made the planted-drift test reachable by a gate whose colour can change;
and recorded, in ADR-28 and here, which of the sentence's three obligations the platform actually
meets.

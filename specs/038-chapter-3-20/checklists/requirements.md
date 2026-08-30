# Specification Quality Checklist: chapter 3.20 — the membership that changed under a live socket

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-29
**Last re-run**: analysis pass 11 — and **not once in the ten passes before it**, which is the
fault this file's own Notes describe in its predecessor
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) — *read as the series' register; see Notes*
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders — *read as "written for its actual audience"; see Notes*
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details) — *five exceptions, named below*
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [~] All functional requirements have clear acceptance criteria — *five have no user scenario; see Notes*
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

**Three ticks above are deliberate readings rather than plain passes, and saying so is the point.**
Chapter 3.19's checklist was a fossil for four analysis passes — it claimed every item passed while
the spec grew from 31 requirements to 38 under two CRITICAL remediations, and two of its ticks were
false when pass 2 read them. A checklist that is easier to tick than to re-run is worse than none.

- **"No implementation details" and "no implementation details leak"** are read as *the series'
  register*. This spec names `chan:{channel_id}`, `presence:{channel_id}`, ADR-07, four route paths
  and two file paths, on purpose: its audience is building the thing and the identifiers are what
  make a requirement checkable. `docs/07-tutorial-plan.md` defines that voice. What the items are
  really guarding against — a spec that decides the design — is checked separately: FR-014, FR-017
  and FR-025 each require a decision to be *made and recorded* rather than making it here.
- **"Written for non-technical stakeholders"** is false as literally worded and true as intended.
  There is no non-technical stakeholder on this project.
- **"Success criteria are technology-agnostic"** has **five** exceptions, all named rather than
  hidden: SC-013 cites the fence chain, SC-014 the gateway package's wall clock, SC-015 the
  connection's `buffering` phase, SC-016 three log-name strings, and SC-017 *"four subject shapes on
  one Redis"*. Each is a property of this repository's own instruments, and a criterion that avoided
  them would not be checkable. **The note said "two" until pass 11**, having been written when there
  were fourteen criteria and not re-read when there were seventeen.

### What re-running at pass 11 found — one tick was false

**Item 13 was ticked for ten passes and is not true.** The acceptance-scenario list stayed at
twenty from `/speckit-specify` while the requirements went from 31 to 36, and **all five late
requirements had no scenario**: FR-029, FR-030, FR-031, FR-032, FR-033.

    pass 3   FR-029  the resume buffer flushes to a removed member      CRITICAL
    pass 7   FR-030  the notice must not join that buffer
    pass 8   FR-031  a successful publish is logged
    pass 8   FR-032  three log names and no fourth
    pass 8   FR-033  no frame arrives as the wrong kind

**Two of the five now have one.** US1 scenario 7 is the journey FR-029 and FR-030 always had — a
member removed mid-resume — and writing it took two minutes once the question was asked.

**Three of the five never will, and the tick is `[~]` rather than `[x]` for that reason.**
FR-031, FR-032 and FR-033 are system properties with no user journey behind them: nobody *does*
anything to make a log line appear or a frame arrive under the wrong `type`. Their verification is
SC-016 and SC-017 plus both directions of `traceability.md`, which is a real answer and not the
one this item asks for. Forcing a Given/When/Then onto them would make the tick true and the
document worse.

**Why it went unnoticed.** Pass 3 mapped scenarios → tasks. Pass 9 mapped requirements →
criteria. Neither is the mapping this item is about, and the one it *is* about — new requirements
→ scenarios — was nobody's question until this file was re-read.

### What authoring found, before any analysis pass

Two requirements had no acceptance scenario and were caught by running this checklist rather than
reading it:

- **FR-006** — a role change publishes nothing — lived only in Edge Cases. Now US2 scenario 6.
- **FR-016** — a publish must not be able to fail the write it follows — was in no story at all.
  Now US1 scenario 6, together with FR-015's log line.

### The two decisions the author made, before the spec was written

- **Scope is FR-RTM-10 plus `membership.changed`**, built as one mechanism. Typing (FR-RTM-08) and
  the five-connection cap (FR-RTM-09) are named as out, with reasons, in FR-018 and FR-019.
- **A removed user is told, and told last.** The channel's remaining members receive the frame and
  the removed user receives it as their final frame for that channel. The ordering became FR-008
  and is a requirement rather than an implementation note: cut-then-send would make the notice
  itself violate FR-RTM-10.

### The one thing this spec asks the plan to decide rather than deciding here

**FR-014.** ADR-07 makes the fan-out fabric explicitly lossy, and chapter 3.19's presence path was
authorised to degrade because a green circle self-heals. A dropped revocation does not self-heal.
What carries it, and what a dropped one costs, is a research question with a real answer, and
FR-014a says what happens if the honest answer is "nothing affordable": record the clause as met on
the happy path and unmet under fabric loss, rather than narrow it until it passes. Chapter 3.18
faced the same temptation with this same clause and refused it.

### What no checklist item covers

**FR-026 is a claim about published prose, and no checker in this repository reads prose.** Chapter
3.19 turned its version into a command with a per-claim, per-locale fragment list, which proves a
sentence is gone and never that its replacement is right. The remainder is a person:
chapter 3.18's `gaps.md` item 6, on its seventh chapter here.

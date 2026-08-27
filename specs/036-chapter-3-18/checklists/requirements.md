# Specification Quality Checklist: chapter 3.18 — the message that never arrived

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-26
**Feature**: [spec.md](../spec.md)

## Content Quality

- [X] No implementation details (languages, frameworks, APIs)
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders
- [X] All mandatory sections completed

## Requirement Completeness

- [X] No [NEEDS CLARIFICATION] markers remain
- [X] Requirements are testable and unambiguous
- [X] Success criteria are measurable
- [X] Success criteria are technology-agnostic (no implementation details)
- [X] All acceptance scenarios are defined
- [X] Edge cases are identified
- [X] Scope is clearly bounded
- [X] Dependencies and assumptions identified

## Feature Readiness

- [X] All functional requirements have clear acceptance criteria
- [X] User scenarios cover primary flows
- [X] Feature meets measurable outcomes defined in Success Criteria
- [X] No implementation details leak into specification

## Notes

**Where the two content-quality items are strained, and why they pass.** "No implementation
details" and "written for non-technical stakeholders" are awkward for a tutorial series about
building a platform: the reader IS the developer, and a subject like a fan-out subject cannot be
described without naming one. The line drawn here is that requirements state WHAT must be true
(a connected member receives the message; a refused send delivers nothing) and the assumptions
section carries the HOW, marked as a default the plan may revisit.

**Seven premises checked against the repository before a requirement was written**, which is the
practice chapter 3.17's five wrong task premises earned:

    the api publishes to no fan-out            read, services/gateway/src/session.ts:651 is
                                               the only publisher outside tests
    the api already reaches Redis              read, services/api/src/limits/store.ts
    the SAD draws api -> redis for fan-out     read, docs/05-sad.md:138
    the SAD specifies the ordering vs the ack  read, docs/05-sad.md:254
    only message.created is ever delivered     read, session.ts — the other frame types
                                               exist and nothing sends them
    message.updated / membership.changed       counted, ZERO producers outside tests
    nothing writes edited_at or deleted_at     counted, 0 writers on messages

**And the clause the plan named is not the clause this chapter satisfies.** The tutorial plan's
3.18 row cites FR-RTM-05. The unmet clause is **FR-RTM-01** — *"A connected client shall receive
messages for every channel of which it is a member"* — P1, and violated today for any REST send.
FR-RTM-05 is about which event KINDS exist; FR-RTM-01 is about delivery, which is the subject.

This is the same shape chapter 3.17 met with FR-MSG-13: a plan naming one clause while a
different one is more directly on point. Found by reading §4.6's clauses rather than its
identifiers — the practice that produced two of that feature's twenty CRITICALs, applied before
the spec was written rather than at analysis pass 13.

**The difference from 3.17 worth stating: there is no amendment to make.** Chapter 3.17's gate
was an SRS amendment, because the SRS had no bot concept. Here both the requirement and the
architecture already exist and are unbuilt. Principle VI is satisfied by citation rather than by
amendment, and FR-002 requires the chapter to say so — a reader who has just finished 3.17 will
expect a gate that is not there.

Checklist 16/16 at first validation, no iterations required.

## Re-validation, 2026-08-26, after two amendments

**A complete checklist certifying an older spec is worse than an incomplete one**, because
`/speckit-implement` halts on incomplete and proceeds on complete. This one read 16/16 while the
spec had changed twice since it was written — FR-005 amended in `dd9a1a1`, FR-002a added in
`69bcd6a` — so it was re-run rather than trusted. Found in analysis pass 5.

**Fourteen items survived unchanged. Two did not, and both for the same reason:**

- **"Scope is clearly bounded"** — FR-002a widened the work into a governing document and its
  mirror, and neither the Summary nor Out of scope said so. Fixed by adding an *In scope beyond
  the publisher* section naming the SAD amendment, its re-sync, and the registry entry.
- **"Dependencies and assumptions identified"** — the same amendment introduced two dependencies
  that were not listed: `docs/05-sad.md` with its `pnpm sync:docs` step, and
  `relay-tutorial/lib/tutorial.ts`. Both added.

**Two items are strained further than at first validation and still pass.** "No implementation
details" and "written for non-technical stakeholders" now have to absorb FR-005's transport
ordering (commit/publish/respond), two NFR identifiers, and FR-002a's mermaid arrow `G->>G`. The
line drawn in the note above still holds — requirements state what must be true, the assumptions
carry how — but it is holding more weight than it was.

**The weakest clause in the spec is FR-002a's "MUST not conflate".** It is a prose requirement
about the chapter, which is the same category as FR-002, FR-003 and FR-012, so it is consistent
rather than anomalous — but it is the one clause whose acceptance criterion is a reader's judgment.
Recorded rather than reworded, because narrowing it would lose what it is for.

Checklist 16/16 after two spec edits.

## One of pass 5's own remediations did not apply, and the count said so

Pass 5 added three tasks — T000, an MDX warning, and the traceability builder. **Only two landed.**
The MDX task used a `.replace()` with no assertion, anchored on a task number that had moved two
passes earlier, and silently matched nothing. Pass 6 found it while editing the same region.

**The evidence was on screen and misread.** The validation printed `tasks: 73` where three
additions to 71 should have given 74. The check counted tasks, checked `[P]` collisions, checked
story labels and checked coverage — and none of those asks *did the thing I just wrote exist*. A
count is not an outcome, and 30/30 coverage was true of a task list missing a task, because the
missing one carried no requirement id.

**And in passes 1 through 4 this analysis reported an extension hook that does not exist.**
`.specify/extensions.yml` declares hooks under `after_specify` and `after_plan` only; there is no
`after_analyze` key, and the skill's instruction for that case is to *"skip silently"*. Four reports
carried an `after_analyze` agent-context block anyway — pattern-matched from the hook legitimately
read during `/speckit-plan`. Passes 5 onward omitted it. Recorded because a fabricated hook is the
same class of defect as a fabricated citation, and this document is where this feature keeps its
process failures.

Every subsequent edit asserts its anchor and then verifies each new task **by name**. That is the
same rule the repository's checkers already learned: write the class list explicitly and fail on an
unknown member.


## The sweep, and its own three bugs

`sweep.py` encodes one check per CRITICAL/HIGH class the sixteen passes found — 32 checks:
artifact structure (ids, labels, `[P]` collisions, dependency order, placeholders, coverage),
cross-artifact (the fence column against the task list), **twenty repository premises** that earlier
passes established, **eleven cited line numbers read rather than trusted**, the five static gates
with a skip-detector, and `dist` staleness. It was tested red three ways before being believed
(`--self-test`), per 3.17's rule.

**It failed twice on its first real run and both were the checker.** Diagnosing them is the whole
value of writing it down:

    check 7   demanded a file path from `git tag part3-ch18` and fifteen others
              -> now an EXPLICIT exemption list of sixteen ids with reasons, which fails
                 on an unknown pathless task rather than letting one join a silent majority
    check 10  counted DEFAULT_REDIS_URL in 5 files, not 3
              -> `grep -rl` without `--include=*.ts` was reading `services/gateway/dist/*.js`,
                 the compiled copies. C2's finding of three source declarations is intact

Both are the same failure this feature has now found eleven times: **a pattern matching a broader
or narrower set than the rule names.** A sweep is not immune to it; a sweep tested red three ways
and diagnosed on failure is how it stops being fatal.

Final: **32/32**.

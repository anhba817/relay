# Feature Specification: repair the fence chain — 110 to 0

**Feature Branch**: `055-fence-chain-repair`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "Go with option D, Repair the 110"

---

## Context

`pnpm check:fences` replays every titled code fence in every published chapter, in order, and
requires the result to land byte-for-byte on `relay-platform`. It has reported **110 problems**
since feature 045 rebuilt Part 3, and `ci.yml`'s tutorial job ends with that command and no
`continue-on-error` — so **the workflow has been red on every push for nine chapters**, and every
chapter since 4.1 has closed by reporting `110 → 110, delta 0` **by hand**.

Feature 054 weighed five ways out and this feature is the one chosen: **repair the chain rather
than change what the checker accepts.** The alternatives — a recorded baseline, `continue-on-error`,
splitting the job — are in `docs/06-adr-deep-dives.md` (ADR-27) and `specs/054-chapter-4-9/gaps.md`
054-1. Each of them makes the number tolerable; only this one makes it true.

**Every one of the 110 is in `relay-tutorial`.** Measured, by the file each problem is reported
against:

    36  HEAD   app/(en)/…/page.mdx            the English chapters
    30  APPLY  app/(en)/…/page.mdx
    30  APPLY  app/(vi)/vi/…/page.mdx         the Vietnamese mirrors
    14  APPLY  fences/post-series.md          the appendix

`relay-platform` is the reference the chain is measured against and is not the thing measured —
`docs/07` §6's third defense, *"the repo at tag N is the truth; prose describes it"*. No
requirement here changes platform code to satisfy a chapter.

### What the 110 actually are

Four failure classes, measured 2026-09-17:

| class | count | what it means |
|---|---|---|
| `hunk pre-image matched 0 times` | **42** | a `diff` fence written against a state the chain does not have |
| `diff … with no earlier fence to amend` | **32** | a `diff` fence for a file the chain has never seen whole |
| `<path> differs at line N` | **25** | the replayed end state is not the file on disk |
| `<title> does not exist in relay-platform` | **11** | the fence's title is a prose phrase, not a path |

**The Vietnamese chain contributes no independent defects.** All 30 vi problems mirror an en
problem exactly — same chapter, same line, same message — and there are **zero vi-only** entries.
The `MIRROR` rule requires each vi fence to be byte-identical to its English twin, so a broken
hunk in en is necessarily broken in vi, and there are 0 MIRROR failures today.

**And the 110 is not 110 independent repairs.** Attributed to the file each problem is about:
**47 distinct targets** — 36 platform files and 11 prose-titled fences — and the top eleven
account for 64 of the 110:

    vitest.coverage.config.mts                        16   15 bad-hunk, 1 differs
    services/gateway/src/session.itest.ts             10   10 no-intro  (5 chapters × 2 locales)
    turbo.json                                         6    6 bad-hunk
    services/api/src/app.module.ts                     5    4 bad-hunk, 1 differs
    packages/protocol/src/codes.ts                     5    4 bad-hunk, 1 differs
    services/api/src/outbox/event.test.ts              4    4 no-intro
    packages/test-harness/src/driver-exempt.test.ts    4    4 no-intro
    packages/protocol/src/internal.test.ts             4    4 no-intro
    eslint.config.mjs                                  4    3 bad-hunk, 1 differs
    services/api/src/webhooks/test-event.itest.ts      3    2 bad-hunk, 1 differs
    packages/test-harness/src/sentinel.sql             3    2 bad-hunk, 1 differs

**`vitest.coverage.config.mts` alone is 16 of the 110, and one hunk explains nine of them.** The
appendix hunk that would create that file's `env` block fails, so the block does not exist in the
chain's state, so every later hunk anchored inside it fails too. Feature 054 proved this by
dumping the checker's own replayed state. **The class is a cascade, and the first failure per file
is the only one that has to be diagnosed.**

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader can copy any fence and get the file (Priority: P1)

Somebody following the series copies a fenced listing into their own repository. Today, for 47
distinct targets, what the chapters build up to is not what `relay-platform` holds — a hunk that
never applied, a file the chapters amend without ever showing, a listing whose title claims to be
a file it is not. The reader has no way to know which.

**Why this priority**: This is the property the fence chain exists to guarantee and the only one a
reader depends on. Every other outcome here is downstream of it.

**Independent Test**: Pick any chapter that fences a file, replay the chain to that chapter, and
compare against the repository at that chapter's tag. Delivers value at any count below 110,
because each repaired file is a listing a reader can now trust.

**Acceptance Scenarios**:

1. **Given** a file the chapters amend with `diff` fences, **When** the chain is replayed, **Then**
   the file has been published whole at least once before the first amendment.
2. **Given** any titled fence, **When** the chain is replayed to the end, **Then** the resulting
   file is byte-identical to `relay-platform`.
3. **Given** a listing that is an excerpt rather than a whole file, **When** the checker reads it,
   **Then** the excerpt is distinguishable from a whole-file claim without being silently exempt
   from every gate.

---

### User Story 2 - The build's colour means something again (Priority: P1)

A push to any of the three repositories produces a workflow whose result says whether that push
broke anything. Today it is red before the push and red after it.

**Why this priority**: Equal-first with US1 and for a different reason — it is the defect chapter
4.9 is about, one level up, and it is what the nine hand-written `delta 0` reports have been
standing in for.

**Independent Test**: Run `pnpm check:fences` on a clean tree and read the exit code. Testable the
moment the count reaches 0, and not before: at 1 problem the step is as red as at 110.

**Acceptance Scenarios**:

1. **Given** a clean tree, **When** `pnpm check:fences` runs, **Then** it exits 0.
2. **Given** a change to a fenced platform file with no corresponding chapter hunk, **When**
   `pnpm check:fences` runs, **Then** it exits non-zero and names the file.
3. **Given** the repaired chain, **When** the tutorial job runs in CI, **Then** its result reflects
   that push rather than the 2026 baseline.

---

### User Story 3 - A chapter's repair does not cost the reader a wrong chapter (Priority: P2)

A repair edits a published chapter. The chapter must still describe the code it shows, and must
not acquire a listing it never discusses.

**Why this priority**: The repair is worthless if it buys a green number with prose that has
stopped being true. Feature 045 recorded the shape: *"putting those into the last chapter that
happened to fence the file would make that chapter show a reader code it never discusses."*

**Independent Test**: Read each repaired chapter's prose beside its new or changed fence and
confirm the prose describes what the fence shows.

**Acceptance Scenarios**:

1. **Given** a file that needs a whole-body introduction, **When** the introduction is placed,
   **Then** it lands in a chapter that discusses that file, at or before the first amendment, with
   the content taken from that chapter's tag — and where no chapter does, the path leaves the
   chain as excerpts with a recorded exception rather than going to the appendix, which applies
   too late to introduce anything.
2. **Given** a repaired fence, **When** its chapter is read, **Then** the surrounding prose is
   still accurate about what the listing contains.

---

### Edge Cases

- **A repair that increases the count.** Regenerating one foundation fence took the chain from
  **111 to 203** by unanchoring ninety-two downstream hunks (045-81). Any repair can do this, so
  the count is measured after each file rather than at the end.
- **A repair that fixes the checker and breaks the reader.** Retitling a prose-titled excerpt to
  its real path turns an excerpt into a whole-body claim, which is false in a different direction.
  Removing the title instead moves it into the 360 fences that are outside every gate —
  a silent exemption rather than a repair.
- **The count reaching 0 and then moving.** Every later chapter pays for the files it edits; 054
  took the chain 110 → 113 with three platform edits and back with five hunks. Zero is a state to
  be held, not a milestone to be passed.
- **A file whose chain state cannot be reached from any hunk.** `vitest.coverage.config.mts`'s
  replayed state has no `env` block at all, so no two-line hunk can anchor inside one. Some files
  need their chain rebuilt from an earlier point rather than amended.
- **A `differs at line N` where the chapter was right when written.** The platform moved
  afterwards. The repair is still in the chapter, because authority runs one way.
- **The Vietnamese chapters are under active translation.** Repairs there are fence bodies only,
  which `MIRROR` already requires to be byte-identical copies of the English ones — no translated
  prose is touched.

---

## Requirements *(mandatory)*

### Functional Requirements

**The count**

- **FR-001**: `pnpm check:fences` MUST report **0 problems** on a clean tree, and the run MUST
  exit 0 without any change to what the checker accepts.
- **FR-002**: The checker's pass/fail semantics MUST NOT be weakened to reach FR-001. No baseline
  file, no `continue-on-error`, no problem class newly exempted, no threshold. If a problem cannot
  be repaired, it is **converted and recorded** under FR-012 rather than tolerated by the
  instrument — and converted is the load-bearing half, because the instrument cannot tell a
  recorded problem from any other kind.
- **FR-003**: The count MUST be measured after each file's repair, not only at the end, and every
  measurement recorded with the file that preceded it.
- **FR-004**: A repair that raises the count MUST be reverted or completed within the same file's
  work, and the excursion recorded with both numbers.

**The four classes**

- **FR-005**: Every file the chapters amend with a `diff` fence MUST be published as a whole body
  at or before its first amendment — 32 problems over 9 distinct files.
- **FR-006**: Every `diff` fence whose pre-image the chain cannot find MUST be regenerated against
  **the chain's own replayed state**, not against the repository tree — 42 problems over 12
  distinct files. The generator MUST be the checker's own replay (fence-chain rule 1a), because a
  generator that replays differently produces hunks the checker rejects for reasons neither
  explains.
- **FR-007**: Every file whose replayed end state differs from `relay-platform` MUST be brought to
  the repository's current content by a fence in a chapter that discusses it — 25 problems.
- **FR-008**: The 11 fences whose titles name no file MUST be resolved so that each listing is
  either a verified whole-file claim or an excerpt the checker can recognise as one. The
  resolution MUST NOT increase the number of fences that no gate reads.

**How a repair may be made**

- **FR-009**: No platform file may be edited to make a chapter's fence correct. Where a chapter and
  the repository disagree, the repository is the truth (`docs/07` §6).
- **FR-010**: A whole-body introduction MUST be placed in a chapter that discusses the file, at or
  before the first amendment, and its content MUST be the file at that chapter's tag rather than
  at the working tree. **`fences/post-series.md` is not available for this class**: it applies
  after every chapter, so it can amend a path and can never introduce one — this requirement said
  the opposite until research measured the checker's ordering (R2). Where no chapter honestly
  introduces the file, the path leaves the chain as excerpts and the exception is recorded under
  FR-012 — leaving the chain is the conversion FR-012 requires, and the record is the other half.
- **FR-011**: Vietnamese repairs MUST change fence bodies only, copied byte-identically from their
  English twins, and MUST NOT alter translated prose. `MIRROR` MUST remain at 0 failures
  throughout.

**What cannot be repaired**

- **FR-012**: Any problem this feature cannot repair MUST be **converted and recorded**, not
  recorded alone. Converted: the fence is declared `(excerpt)` so it stops claiming a file the
  chain cannot verify, which is the same mechanism as FR-008 and is what takes the problem out of
  the count. Recorded: the reason, the measurement that establishes it, and what a real repair
  would cost.
  **Recording alone does not reach FR-001, because nothing reads `gaps.md`.** The checker counts a
  documented problem exactly as it counts an undocumented one, so "record and leave it" ends at a
  residual number — which is the baseline file this feature refused to write, reached by a
  different door. A feature that reports "0 except for these" without the arithmetic has moved
  that baseline; a feature that reports "0" and hides an exception inside an excerpt without the
  arithmetic has done the same thing more quietly, which is why both halves are required.

**The record**

- **FR-013**: The inventory MUST be re-measured at the start rather than copied from this
  specification, and any divergence from the 110/47 recorded here MUST be reported. This
  document's numbers are dated 2026-09-17 and the chain moves whenever a chapter or the platform
  does.
- **FR-014**: The 109-versus-110 discrepancy MUST be resolved or recorded: feature 045 closed
  reporting **109** and every chapter since 4.1 has reported **110**, and no document explains the
  extra one.
- **FR-015**: The feature MUST record which of the 110 were single defects and which were cascades,
  so the next reader of the number knows what it counts. Measured here: one hunk explains nine of
  `vitest.coverage.config.mts`'s sixteen.
- **FR-016**: Where a repair reveals that a published fence was wrong rather than stale — for
  example `packages/test-harness/src/sentinel.sql`, whose chapter publishes `END $;` where the
  repository has `END $$;` — the finding MUST be recorded separately from the count, because a
  reader copying that listing gets a syntax error and the count never said so.

### Key Entities

- **A fence**: a titled code block in a published chapter. A plain fence states a file's whole
  content at that chapter; a `diff` fence amends the previous state with `@@` hunks.
- **The chain**: every fence for one path, in chapter order, replayed from the first whole body
  through every amendment, with `fences/post-series.md` applied last.
- **The replayed state**: what the chain produces for a file at a given point. It is not the
  repository tree, and the difference is where 42 of the 110 come from.
- **A problem**: one `[APPLY]`, `[HEAD]` or `[MIRROR]` line. The checker reports the first failure
  per file, so a file with three divergences counts once.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `pnpm check:fences` reports **0 problems**, from 110, **evidenced by its success line**
  — `N fenced files replay onto relay-platform across M chapters` — and not by the exit code alone.
  The wrapper exits 0 when `relay-platform` is absent, having replayed nothing, so an exit code
  cannot tell a repaired chain from an unread one (045-81).
- **SC-002**: The tutorial job in CI succeeds on a push that changes nothing, for the first time
  since feature 045.
- **SC-003**: A deliberate regression — one line changed in a fenced platform file, with no
  chapter hunk — makes the run exit non-zero and names that file. Run red, not reasoned about.
- **SC-004**: `MIRROR` failures remain **0** throughout, measured after each locale's repair.
- **SC-005**: Each of the four classes reaches 0, reported separately: 42 bad hunks, 32 missing
  introductions, 25 divergences, 11 prose titles.
- **SC-006**: The count never exceeds 110 at any measured point in the work, and any excursion is
  reported with the file that caused it and the number it reached.
- **SC-007**: Every repaired chapter's prose still describes the listing beside it, checked by
  reading, with the count of chapters read recorded.
- **SC-008**: The number of fences that no gate reads — untitled, or titled with a prose phrase —
  is measured before and after, and does not increase. Measured 2026-09-17: **360 untitled of
  2,109 opening fences** (1,071 `app/(en)`, 1,005 `app/(vi)`, 33 `fences/`), with 222 titles
  already declared `(excerpt)` — **111 in each locale** — and one further `.naive.` pair the
  checker also skips, for 224 in all. **Every figure here spans both locales**; counted on one
  side each is roughly half. `gaps.md` 043-1's *"146 of
  904"* is a 2026-08 figure this feature re-measures rather than repeats.
- **SC-009**: The repair is reproducible: the commands that regenerate each hunk are recorded and
  run as written.
- **SC-010**: Zero platform files are edited to satisfy a chapter.

---

## Assumptions

- **The target is the whole 110, both locales.** The vi chapters' fences are byte-identical copies
  the `MIRROR` rule already enforces, so repairing them is mechanical and touches no translated
  prose. The user's in-flight translation work is in the prose around the fences, not in the fence
  bodies.
- **`relay-platform` is not modified.** Its current content is the target the chain must reach.
  This follows `docs/07` §6 and is stated as a requirement (FR-009) rather than left implicit.
- **No chapter is renumbered or moved.** Part 3's rework is closed; this feature edits fences and
  the prose immediately around them.
- **The 11 prose-titled fences need a decision, not a mechanical fix.** The three candidate
  resolutions — retitle to the real path, remove the title, or give the checker an explicit
  excerpt form — differ in what they cost the reader and the gate. The specification states the
  constraint (FR-008, SC-008); the choice belongs to the plan and is an architecture decision
  under constitution VII.
- **Repairs are ordered from the most concentrated file down.** Eleven files account for 64 of the
  110, and cascades mean the first failure per file is the only one that has to be diagnosed.
- **The count is expected to move during the work** and the checker is the instrument for saying
  by how much, which is why FR-003 measures per file.
- **This feature publishes no chapter.** It repairs published ones. Whether the work is described
  to readers anywhere is out of scope and noted for the series.

---

## Out of scope

- Changing `check-fence-chain.mjs`'s exit semantics, adding a baseline file, or any form of
  tolerance. That was option A and this feature exists because it was not chosen.
- The 360 untitled fences that no gate reads (`gaps.md` 043-1, which recorded 146 of 904 in
  2026-08 and is re-measured here). They are measured (SC-008) and
  not closed; closing them is a decision about what a fence means, not a repair of the chain.
- `relay-platform` behaviour, tests, or coverage.
- The 3 Part 1 tags on neither `main` nor the backup (`gaps.md` 046-8) and the absence of any gate
  checking that a chapter's tag matches the chapter (048-5, 054-4). Adjacent, and each its own
  feature.

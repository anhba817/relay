# Feature Specification: Part 2 Chapter Drafts — The Core Loop, Written Ahead

**Feature Branch**: `020-part2-chapter-drafts`

**Created**: 2026-08-02

**Status**: Draft

**Input**: User description: "Write the content for all chapter in phase 2 in relay-tutorial, only English, do not do the coding of relay-platform"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The seven core-loop chapters exist as complete English drafts (Priority: P1)

As the series' author (and its first reader), I open the drafts of chapters
2.2 through 2.8 — the entire remainder of Part 2, the part docs/07 stars as
"where the tutorial earns its premise" — and each one is a complete chapter,
not an outline: the cold open, the failure-first structure (docs/07 §4 Rule
1: the reader must *see the bug the design prevents*), the derivation from
the documents, the code the chapter builds, the boxes, the figures, the
exercises, the takeaways, the closing checkpoint. The seven chapters teach
exactly what docs/07 §3's Part 2 table assigns them: the write path under a
row lock (2.2), idempotency keys (2.3), cursor pagination (2.4), the
gateway's socket (2.5), Redis fan-out across two servers (2.6), the resume
protocol and the series' flagship bug (2.7), and the Tuan test milestone
that IS the SRS Phase 1 exit criterion (2.8). Everything is written against
the re-founded stack the revised 1.1–2.1 established (ADR-15/16/17): the
API service grows NestJS endpoints, queries go through the Drizzle
repository, the gate runs through the task graph.

**Why this priority**: The chapters are the deliverable; drafting the whole
part in one sustained pass is what keeps its arc coherent — every chapter
here leans on its predecessors, and 2.8's milestone defines "done" for all
of them (docs/07 §5's own production rule: draft the part's test story
before the part's chapters harden).

**Independent Test**: A reviewer can read the seven drafts in sequence and
follow the entire core loop — from the first POST under concurrency to the
mid-send tunnel reconnect — without consulting docs/04/05/06, and can trace
every factual claim back to those documents when they do.

**Acceptance Scenarios**:

1. **Given** the seven drafts, **When** read in order, **Then** each opens
   from the state its predecessor left (2.2 assumes only 2.1's spine; 2.8
   assumes 2.2–2.7), teaches its docs/07 row, and pairs its capability with
   the named failure it prevents — demonstrated before it is fixed.
2. **Given** any draft, **Then** it meets the code-chapter format at draft
   level: 2,000–4,000 canonical words; ≥2 `WHY` boxes citing requirement
   IDs/ADRs; ≥1 `TRAP`; 1 `SKIP AHEAD`; ≥1 forward reference; 2–4 captioned
   figures (with figure source alongside); takeaways; exactly one closing
   `CHECKPOINT`.
3. **Given** the chapters' code, **Then** it is consistent with the
   re-founded stack and the published 1.1–2.1 state (the NestJS api, the
   Drizzle repository, the two-lane gate, the protocol package's frames),
   and consistent across chapters — 2.4 pages over what 2.2 wrote, 2.7
   resumes what 2.5 connected.
4. **Given** 2.7, **Then** the duplicate/gap race from SAD §5.2 is staged
   as the tutorial's flagship bug-then-fix; **given** 2.8, **Then** the
   milestone suite scripts journey 4 end-to-end (kill the socket mid-send,
   reconnect, assert exactly-once and order) and states its role as the
   Phase 1 exit criterion.

---

### User Story 2 - The drafts are honest about being drafts (Priority: P2)

As a reader of the live site — and as the series' own honesty rules
(docs/07 §6) demand — nothing changes until the code exists. These chapters
show code the canonical repository does not yet contain; the fence contract
(every fence byte-matches the repo at the chapter's tag) is therefore
*unsatisfiable* today, and the series does not publish what it cannot
verify. The drafts live in the tutorial repository **outside the routable
site tree**, each carrying a draft header that names its verification debt:
the tag it will pin (`part2-ch2` … `part2-ch8`), the files its fences must
eventually byte-match, the commands that must replay, and the numbers left
as to-be-verified markers (test counts, command output) that only running
code can supply.

**Why this priority**: The fence discipline is the series' trust mechanism,
re-affirmed at cost in feature 019; a Part 2 published ahead of its code
would spend that trust for speed. Draft-but-unpublished is the only state
consistent with the rules the series set for itself.

**Independent Test**: The live site's surface is bit-for-bit unchanged
(sitemap, manifest, navigation, allowlist — 2.2–2.8 still render as
"forthcoming"); every draft's header lists its tag, fence inventory, and
TBV markers; no file under relay-platform is touched.

**Acceptance Scenarios**:

1. **Given** the tutorial repository after this feature, **Then** the only
   additions are draft files in a non-routable location; the manifest,
   sitemap URL set, navigation, and suggestions allowlist are unchanged;
   `pnpm build` output is identical in page count.
2. **Given** any draft, **Then** its header records: intended tag, the
   fence inventory (paths the chapter will pin), amendment expectations
   (which previously fenced files it must diff-fence), the gate/lane
   commands it will claim, and every TBV marker in the body.
3. **Given** relay-platform, **Then** `git status` shows zero changes from
   this feature — the coding is explicitly out of scope, deferred to the
   per-chapter implementation features.

---

### User Story 3 - The part reads as one arc, traceable to the paperwork (Priority: P3)

As the tutorial's future implementer (and reviewer), each draft is not just
individually correct but load-bearing for its neighbors: the sequence
machinery 2.2 builds is what 2.3's idempotency protects and what 2.4 pages
over; 2.5's connection registry is what 2.6 fans out across and what 2.7
resumes through; 2.8 exercises all of it in one scripted journey. Every
mechanism cites its source (ADR-03 for sequences, DR-03 for the partial
index, ADR-07 for the lossy fabric, SAD §5.2 for the resume protocol,
journey 4 and the SRS Phase 1 exit criterion for the milestone), and no
invented requirement or ADR identifiers appear anywhere.

**Why this priority**: Cross-chapter coherence is the reason to draft the
part as one feature instead of seven; it is cheaper to keep the arc
straight now than to retrofit it during seven implementation features.

**Independent Test**: The invented-ID detector passes over all seven
drafts; a continuity read finds no chapter using a mechanism its
predecessors have not built; the forward references form a connected chain
through the part and into Part 3.

**Acceptance Scenarios**:

1. **Given** the seven drafts, **Then** 100% of cited IDs (FR-*, DR-*,
   NFR-*, EIR-*, ADR-*, D1–D8) exist in docs/04/05/06 or the constitution,
   and quoted passages are faithful to the current documents.
2. **Given** the part's arc, **Then** each draft's `SKIP AHEAD` and
   `CHECKPOINT` describe states that build strictly on prior chapters, and
   2.8's checkpoint closes Part 2 explicitly as the Phase 1 exit.

---

### Edge Cases

- **Code that has never run**: draft code is design-stage — it can be
  plausible and stack-consistent yet wrong in detail (an API signature, an
  import path, an output string). The drafts must confine unverifiable
  specifics behind TBV markers where they matter (exact outputs, counts)
  and the draft header's verification debt; the per-chapter implementation
  features own making the code real and correcting the prose to match.
- **Tags that don't exist yet**: `SKIP AHEAD` boxes name `part2-chN` tags
  as the format requires; the draft header flags that the tag is intended,
  not cut — publishing without the tag is what US2 forbids.
- **The 2.8-first tension**: docs/07 §5 says the milestone's test story
  defines done-ness for the part. Drafting order inside this feature must
  honor that: 2.8's journey script is settled (at least in skeleton) before
  2.2–2.7's checkpoints finalize, so the part is written toward its exit
  criterion rather than patched to it.
- **The flagship bug must actually be stageable**: 2.7's duplicate/gap race
  (SAD §5.2) is the series' marquee moment; the draft must stage it as a
  concrete, reproducible sequence of events (subscribe/backfill
  interleaving), not a hand-wave — this is the chapter most damaged by
  vague drafting.
- **Stack drift between draft and implementation**: the re-foundation
  (019) is in the working tree but not yet committed/tagged by Dong. The
  drafts assume 019's state; if review changes 019, the drafts inherit the
  delta as part of their verification debt.
- **Scope boundary with SRS phases**: "Phase 2" in the request is read as
  tutorial Part 2 (the current part, seeded 2.2–2.8 forthcoming) — not SRS
  Phase 2 (which is tutorial Part 3). The assumption is recorded below.
- **English only**: no Vietnamese editions in this feature; translation
  happens per chapter at publish time with the byte-identical fence flow,
  as established.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Seven complete English chapter drafts MUST exist — 2.2 "The
  write path", 2.3 "Send it twice", 2.4 "History that pages", 2.5 "The
  socket", 2.6 "Two servers, one conversation", 2.7 "The tunnel", 2.8
  "Milestone: the Tuan test" — each teaching its docs/07 §3 row with the
  failure-first structure of docs/07 §4 Rule 1, read through the row
  itself: 2.5's row names no prevented failure ("—"), so its chapter is
  structural — its `TRAP` still satisfies the battery without a staged-bug
  centerpiece.
- **FR-002**: The drafts MUST live in the relay-tutorial repository in a
  location that is not routable and not reachable from any navigation
  surface; the live site's manifest, sitemap URL set, navigation, and
  suggestions allowlist MUST be unchanged.
- **FR-003**: Each draft MUST meet the code-chapter format at draft level:
  2,000–4,000 canonical words, ≥2 `WHY` (source-cited), ≥1 `TRAP`, 1
  `SKIP AHEAD` naming its intended tag, ≥1 forward reference, 2–4 captioned
  figures with figure sources authored alongside, takeaways, exactly one
  closing `CHECKPOINT`.
- **FR-004**: All chapter code MUST be consistent with the re-founded stack
  (ADR-15/16/17) and with the published 1.1–2.1 state, and mutually
  consistent across the seven drafts (shared names, shared shapes, one
  continuous codebase story); mechanisms MUST implement what their sources
  define (ADR-03 sequences and row lock, DR-03 partial unique index, cursor
  pagination per SAD §6.3's index, gateway per SAD §5.1/5.2 and the
  protocol package's frames, fan-out per ADR-07, resume per SAD §5.2,
  journey 4 for the milestone).
- **FR-005**: Each draft MUST open with a draft header recording its
  verification debt: intended tag, fence inventory (files to pin),
  expected amendments to previously fenced files, gate and integration-lane
  commands to be claimed, an enumerated list of TBV
  (to-be-verified) markers used in the body for outputs and counts that
  only running code can supply, and the platform baseline the draft was
  written against (the 019 re-foundation state) — six keys total, exact
  format plan-level.
- **FR-006**: relay-platform MUST be untouched by this feature — zero file
  changes; all coding is deferred to per-chapter implementation features.
- **FR-007**: The drafts MUST be English-only; no Vietnamese files are
  created or modified.
- **FR-008**: 100% of cited requirement/decision identifiers MUST exist in
  the current docs/04/05/06/constitution (invented-ID detector clean over
  all drafts and figure sources); quoted passages MUST be faithful.
- **FR-009**: 2.8's journey script (the Tuan test's staged sequence) MUST
  be drafted before 2.2–2.7's checkpoints are finalized, and each of
  2.2–2.7 MUST be consistent with what that script will demand of it
  (docs/07 §5's part-level test-first rule).
- **FR-010**: 2.7 MUST stage the SAD §5.2 duplicate/gap race as a concrete
  reproducible event sequence (the bug shown, then the
  subscribe-before-backfill buffer fixing it), not as an abstract
  description.

### Key Entities

- **The seven drafts**: Complete English chapters for 2.2–2.8, format-true,
  stack-true, unpublished; sources: docs/04 (FR-MSG, FR-RTM, FR-CHN
  slices), docs/05 (§5.1/5.2, §6.1/6.3, ADR-03/05/07, S-scenarios), docs/06
  deep dives, docs/07 §3–5, journey 4, constitution I/II.
- **The draft header**: Per-draft verification-debt record — intended tag,
  fence inventory, amendment expectations, lane commands, TBV markers — the
  contract each implementation feature will discharge.
- **The part arc**: The dependency chain 2.2→2.8 (sequences → idempotency →
  pagination → socket → fan-out → resume → milestone) that this feature
  keeps coherent by drafting as one unit, toward 2.8's exit criterion.
- **The unchanged surfaces**: relay-platform (zero diffs) and the live
  site's manifest/sitemap/navigation/allowlist (bit-for-bit unchanged).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Exactly seven draft chapters exist, each 2,000–4,000
  canonical words, each passing the box/figure battery at draft level
  (≥2 WHY, ≥1 TRAP, 1 SKIP AHEAD, ≥1 forward ref, 2–4 figures, exactly one
  closing CHECKPOINT).
- **SC-002**: The live site is unchanged: sitemap URL set identical (34),
  manifest byte-identical, `pnpm build` green with the same page count,
  2.2–2.8 still rendered as forthcoming.
- **SC-003**: relay-platform shows zero changes from this feature.
- **SC-004**: The invented-ID detector passes over all seven drafts and
  their figure sources; spot-checked quotes match the current documents.
- **SC-005**: Every draft carries a complete draft header; every
  unverifiable output/count in any body is a listed TBV marker (zero
  unmarked invented outputs on review).
- **SC-006**: A continuity review of the seven drafts in sequence finds
  zero uses of a mechanism before the chapter that builds it, and 2.8's
  script exercises capabilities from every one of 2.2–2.7.

## Assumptions

- **"Phase 2" means tutorial Part 2** (chapters 2.2–2.8, currently seeded
  as forthcoming) — not SRS Phase 2 (which is tutorial Part 3). This
  follows directly from the conversation's context (Part 2 was just opened
  by 2.1) and the request's "all chapters".
- **Drafts are unpublished by rule, not by preference**: the fence contract
  cannot be satisfied without platform code, and docs/07 §6 makes
  fence-equals-repo the series' non-negotiable honesty mechanism (restated
  at cost in feature 019). Publishing follows per chapter, with its
  implementation feature: code built → fences verified/corrected → TBVs
  resolved → Vietnamese edition → manifest flip → tag.
- **The drafts assume the 019 re-foundation state** (NestJS api, Drizzle
  repository, turbo gate) as the platform baseline, including its
  not-yet-cut tags; any 019 review changes become draft verification debt.
- **Draft location and header format are plan-level decisions**, bounded by
  FR-002 (non-routable) and FR-005 (verification debt recorded).
- **Commits and pushes are Dong's**, on explicit go-ahead only; this
  feature leaves working-tree changes in relay-tutorial and the parent's
  spec artifacts.

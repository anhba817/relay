# Feature Specification: Part 3, reorganised by subject

**Feature Branch**: `045-part-3-rework`
**Created**: 2026-09-07
**Status**: Draft
**Input**: "rework chapter 3 with English only, for vietnamese, use a placeholder content, I will provide translation later"

## Context

Part 3 is 447,394 words across 24 chapters that `docs/07-tutorial-plan.md` says were **planned as
seven**. Its own header records the cause: *"a chapter that reached its word ceiling and split
rather than compress."* Every split was a local decision, so the boundaries between subjects were
never redrawn. What the reader gets is the order the work was done in, not an order anybody chose.

Four things were measured before this specification was written:

- **Five of eight subject clusters are discontiguous.** The event backbone is chapters 3, 4 and 7,
  interrupted by two webhook chapters. Webhooks are 5, 6 and 9, interrupted by deduplication and
  rate limits. Commercial controls are 8, 10 and 11, interrupted by email. The two milestones are
  12 and 14, interrupted by a domain chapter — which exists to repair the instruments the first
  milestone exposed, and references it ten times.
- **The webhook chapters teach delivery for events that do not exist yet.** 70,558 words across
  chapters 5 and 6 build a delivery system whose event types get their first producers in chapter
  20. Feature 043 later measured 838 stored subscriptions to types the platform still does not
  emit.
- **Cross-cutting patterns are re-derived rather than taught.** The outbox is explained four times
  — one section is titled *"The outbox, a fourth time"* — and mentioned in 21 of 24 chapters. The
  subject-grammar rule is derived five times, and the plan admits it: *"which three prior chapters
  reached independently."* Nine architecture decisions are raised mid-chapter.
- **The dependency order is nevertheless sound.** 54 forward references against 522 backward. The
  chapters build on what came before; it is the grouping that is wrong, which is why this can be
  fixed by moving chapters rather than rewriting their arguments.

**Chapter 3.7 already published the rule this feature finishes.** Its section *"A chapter number is
a reference that ages"* records that inserting one chapter invalidated three source comments, one of
which had been wrong since a previous insertion: *"A chapter number in a source comment is a
reference that ages every time the plan changes, and this file is fenced byte-exact into a published
chapter, so correcting it costs a fence amendment. The subject does not move; the ordinal does."*
That rule was applied to three comments. **1,429 more remain, across 166 fenced files and 49
unfenced ones.**

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader follows one subject to its end (Priority: P1)

A developer reading Part 3 in order encounters each subject as an unbroken run of chapters. When
they finish the event backbone they have the whole backbone; when they start webhooks they do not
put it down after two chapters to learn rate limiting and come back four chapters later.

**Why this priority**: this is the defect. Everything else in this specification is either a
consequence of fixing it or a cost of doing so.

**Independent test**: derive the cluster of every chapter from its subject, then confirm each
cluster occupies a contiguous run. Eight of eight, against five of eight today.

**Acceptance Scenarios**

1. **Given** the published Part 3, **When** the chapters are grouped by subject, **Then** every
   group occupies consecutive positions.
2. **Given** a reader at the first webhook chapter, **When** they read forward, **Then** every
   webhook chapter follows without another subject intervening.
3. **Given** a reader who has finished a movement, **When** the next movement begins, **Then** it
   does not depend on a chapter later than itself.

### User Story 2 - A reader is never asked to build for an absence (Priority: P1)

The reader builds a mechanism only after the thing it operates on exists. Webhook delivery comes
after the events have producers. Quotas and metering come after there is a product to meter.
A verification milestone comes after the surface it verifies.

**Why this priority**: it is the sharpest reader-visible symptom, it accounts for the largest single
block of misplaced material (70,558 words), and it is the one an outside reader would notice first.

**Independent test**: for each event type a webhook chapter delivers, confirm a producer exists in
an earlier chapter. For the isolation milestone, confirm every route it attacks was built earlier.

**Acceptance Scenarios**

1. **Given** the webhook chapters, **When** each declared event type is traced, **Then** its
   producer appears in an earlier chapter.
2. **Given** the isolation milestone, **When** its derived target list is taken, **Then** every
   target's route was built in an earlier chapter.
3. **Given** the outsider milestone, **Then** no chapter follows it.

### User Story 3 - A chapter can move without ageing a reference (Priority: P2)

References to a chapter name its subject rather than its position. Moving, inserting or splitting a
chapter does not silently invalidate a comment in the platform's source.

**Why this priority**: it is what makes this the last reorganisation that costs this much. It is P2
rather than P1 because the reader does not see it directly — but the next person to insert a chapter
does.

**Independent test**: count Part-3 chapter-number references in `relay-platform` source. It is 1,171
today; the target is zero in fenced files.

**Acceptance Scenarios**

1. **Given** a source comment that referred to a chapter, **When** it is read after this feature,
   **Then** it names the subject and no ordinal.
2. **Given** a chapter is moved after this feature, **When** the gates run, **Then** no source
   comment needs amending because of the move.

### Edge Cases

- **A reference whose subject has no name.** Some comments cite a chapter for a decision that was
  never given a title. The comment must be rewritten to state the decision, not to point at it.
- **A reference to a chapter outside Part 3.** Parts 0, 1, 2 and 4 are not reordered, so their
  ordinals are stable. They stay numbered, and the rule is stated so a reader knows why the two
  cases differ.
- **A Vietnamese page whose fences no longer match.** The mirror check compares the Vietnamese fence
  list and every fence body against the English chapter. A placeholder page that drops its fences
  fails; a placeholder page that keeps them byte-identical passes.
- **A chapter that both moves and has its comments rewritten.** Its fences change for two reasons at
  once; the amendment must be generated after both changes, not between them.
- **An excerpt-only file.** Thirteen files are published only as `(excerpt)` and no gate compares
  them to anything. Comment renames inside them are invisible to `check:fences` and must be verified
  another way.
- **The chapter that splits.** The error-registry material and the outsider verdict currently share
  one chapter and belong at opposite ends of Part 3. Splitting it changes the chapter count.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every subject cluster in Part 3 MUST occupy a contiguous run of chapters.
- **FR-002**: A chapter MUST NOT teach a mechanism whose subject is introduced in a later chapter.
  This covers webhook delivery against event producers, commercial controls against the product they
  meter, and each verification milestone against the surface it verifies.
- **FR-003**: The chapter that teaches a cross-cutting pattern in full MUST precede every chapter
  that reuses it. This applies to the transactional outbox and to the subject-grammar rule.
  **This clause was narrowed during task generation, because it contradicted FR-009.** It read
  "taught once … and referred to thereafter", which means deleting three of the four outbox
  explanations and four of the five grammar derivations — and that is compression, which FR-009
  preserves against and Out of Scope excludes by name. A reorder can guarantee the ordering and
  cannot collapse the repetition. **Consolidating them is deferred to the compression feature**, and
  is recorded in Out of Scope rather than left as a requirement no task could satisfy.
- **FR-004**: A verification milestone MUST appear after all the work it verifies.
- **FR-005**: The error registry MUST appear before the first chapter that adds a code to it.
- **FR-006**: The final state of every file the book publishes MUST be byte-identical before and
  after this feature, except where a source comment is rewritten under FR-008. **The platform's
  behaviour does not change.**
- **FR-007**: Chapters MUST be renumbered to their new reading order, with no gaps and no
  reordering of the numbers relative to the sequence.
- **FR-008**: A reference to a Part 3 chapter from `relay-platform` source MUST name the subject
  rather than the ordinal. **1,429 such references exist across all `.ts` under `services/` and
  `packages/`; 1,298 of them sit inside 183 fenced paths.** Both numbers are stated with the pattern
  that produced them — `[Cc]hapter 3.N`, `(3.N)`, `3.N's` — because a count whose reach is unstated
  is a count nobody can check, which is SC-002's own rule.
  **This clause has carried three wrong numbers.** It read 985 references until research widened the
  pattern; the count was corrected to 1,429 and **the file count was left at 166, which came from the
  same lowercase-only pattern that produced the 985**. Analysis pass 3 found the survivor: with
  `Chapter` capitalised the fenced-path count is **183**, seventeen more files than planned for.
  A correction applied to one number and not to its neighbour is how a measurement stays wrong.
- **FR-009**: Every English chapter's prose MUST be preserved. This feature moves and renumbers; it
  does not compress, merge or rewrite arguments.
- **FR-010**: **Every English chapter MUST have a Vietnamese page**, carrying a fence list and
  fence bodies byte-identical to its English counterpart, and placeholder prose. **This clause read
  "every Vietnamese chapter page MUST continue to exist" and analysis found the hole**: the split
  creates a Vietnamese page that has never existed, and "continue to exist" is satisfied without
  creating it. Stated per English chapter so the count follows the map rather than the past.
- **FR-011**: A Vietnamese placeholder page MUST be visibly marked as awaiting translation, so a
  reader is never shown a page that appears translated and is not.
- **FR-016**: The appendix MUST be treated as part of the chain. `relay-tutorial/fences/post-series.md`
  amends **49** fenced paths after the last chapter — **41** of them also have comment rewrites and
  **21** also change chain order, carrying **48** hunks between them. Three things follow, and none
  was stated before analysis pass 3: the replay tooling MUST apply the appendix or the chain never
  reaches the platform file; for the 21, the target for a *chapter* fence is the state **before** the
  appendix applies, not the platform file; and the 48 existing hunks were generated against the
  current chain's end state, so they MUST be re-verified and regenerated where the reorder moves what
  they apply to.
- **FR-015**: The published navigation MUST follow the renumbering. `relay-tutorial/lib/tutorial.ts`
  declares every chapter's number, path, title and reading time by hand, and it is read by the
  sitemap and by six components — the sidebar, the chapter shell's previous and next links, the site
  header, the landing page and the language switcher. **No requirement named it until analysis went
  looking for what else knows a chapter number**, and nothing compares it to the filesystem, so a
  renumbering that skipped it would leave every gate green and every link dead.
- **FR-012**: `docs/07-tutorial-plan.md` MUST be amended to the new structure, and the amendment
  MUST state the chapter count derived from its own rows rather than carried in a heading — a number
  that section records as having been wrong three times running.
- **FR-013**: Every gate MUST be green at close-out, including the fence chain replaying byte-exact
  across all chapters in the new order.
- **FR-014**: The mapping from old chapter number to new MUST be recorded where a reader of the
  published book can find it, because external links and existing readers' notes cite the old
  numbers.

### Key Entities

- **Chapter**: a published unit with a subject, an ordinal, a slug and a route. This feature changes
  the ordinal and the position; the subject and the prose are preserved.
- **Movement**: a contiguous run of chapters sharing a subject. Eight of them. Not a published
  heading level necessarily, but the unit FR-001 is measured against.
- **Fence chain**: the sequence of code fences for one file path across chapters, replayed in
  chapter order and required to land byte-exact on the platform. Reordering changes the sequence;
  rewriting comments changes the content. **169 of 242 fenced files are affected by one or both.**
- **Reference**: a mention of a chapter from prose, a source comment or a record. After FR-008 a
  reference from source names a subject.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Eight of eight subject clusters are contiguous, against five of eight today.
- **SC-002**: Zero Part-3 chapter-number references remain in `relay-platform` source, against
  **1,429** today across all `.ts` under `services/` and `packages/` — **1,298** of them within the
  **183** fenced paths. **Report the pattern and the corpus alongside the count.** This criterion
  said "report the pattern" and the specification then quoted two numbers measured with different
  patterns over different corpora, which is the failure the rule exists to prevent, committed by the
  document that states it.
- **SC-003**: Every **emitted** webhook event type has a producer introduced in an earlier chapter —
  five of the eight declared, and today none of the five does. **This criterion said "every event type
  the book teaches delivery for" and could never be satisfied**: `channel.created`, `user.connected`
  and `user.disconnected` are declared and have no producer anywhere, and building them is out of
  scope, so "every" was unreachable by construction. **Its baseline was also inverted** — it read
  "three of eight today" where `event.ts` marks five emitted and three not. Both corrected in analysis
  pass 2; the three unbuilt types are recorded rather than counted.
- **SC-004**: Every chapter that reuses the transactional outbox or the subject-grammar rule appears
  after the chapter that teaches it in full. **Not "exactly one chapter", which this criterion read
  until it was matched against FR-009** — counting explanations measures compression, and this
  feature does not compress.
- **SC-005**: Every fenced file replays byte-exact onto `relay-platform` in the new chapter order,
  and the platform's final state is unchanged except for rewritten comments.
- **SC-006**: Every Vietnamese chapter carries a fence list and bodies byte-identical to its English
  counterpart, and the mirror check passes with 24 or more Vietnamese chapters present.
- **SC-007**: The full test battery is green and its duration stays within 10% of the 225.45 s mean
  measured over twenty runs at feature 044's close-out. **The platform is not supposed to change**,
  so a moved duration is a signal that something did.
- **SC-008**: All 24 old chapter numbers resolve to their new position from a single published
  page, and every entry names a chapter that exists.
- **SC-009**: The chapter registry and the filesystem agree in **both directions** — every declared
  path exists and every chapter page is declared — checked by an instrument rather than by reading.
  They agree today at 41 and 41, which is what makes silent drift possible rather than unlikely.
- **SC-010**: Every existing appendix hunk still applies after the reorder, and the chain including
  the appendix lands byte-exact on `relay-platform`. **The chain does not end at the last chapter**,
  and a tool that stops there reaches a state that is not the platform's — measured: 70
  reference-bearing lines appear in no chapter snapshot at all, because the appendix put them there.

## Assumptions

**This is a reorganisation, not a rewrite.** The user's words were *"I mean reorganize the
content"*. Chapter prose is preserved verbatim wherever a chapter moves unchanged. Compression —
which the 6× size variance and the four outbox explanations would justify — is deliberately excluded
so that a mechanically verifiable change is not mixed with an unverifiable one. **No gate can tell
you which of the two broke a chapter, so they are not done together.** A later feature can compress
against a structure that is already right.

**Renumbering was chosen over the two alternatives, and the third option was rejected on the
reader's behalf.** Keeping numbers bound to subjects — so the book runs 1, 2, 14, 3, 4, 7, 13 — costs
almost no reference churn and asks every reader to carry the mapping. Renumbering while rewriting
the ordinals in place is scriptable and re-creates the liability at the next insertion. Naming the
subject instead is the rule chapter 3.7 published in print after paying for it twice, and this is
the moment it stops being expensive to finish.

**The Vietnamese pages stay in place rather than being deleted.** The mirror check skips a chapter
that has no Vietnamese page, which would make deletion the cheapest option — and would remove
published translated content from the site. Keeping the pages with placeholder prose and identical
fences preserves the routes, keeps the mirror honest, and leaves a translator a file to work in.

**Non-Part-3 chapters keep their ordinals.** Parts 0, 1, 2 and 4 are not reordered, so their numbers
do not age in this feature. The named-reference rule is applied to Part 3 references because those
are the ones this feature invalidates; extending it to the rest of the book is a separate decision
and is out of scope here.

**The platform's git history is not load-bearing for the fence chain.** The checker replays fences
onto the working tree and never reads git history, so reordering chapters does not require rebuilding
`relay-platform`'s commits. The user has said the repository may be reset and re-tagged; this feature
does not need it, and says so rather than doing it because it was permitted.

**Reordering does not let the existing fences be reused, and the first draft of this specification
assumed it did.** Research replayed the per-chapter deltas of all 39 order-changing paths in the new
order: **3 land correctly, 31 conflict, and 5 merge cleanly onto a different file.** The fences on
those paths are re-derived from the final file by attribution, not re-hunked — 278 of them. The
correction is recorded here because the assumption is what made the feature look small.

**The 39-path reorder estimate is a floor, not the scope.** Reordering alone changes the chain order
of 42 of 207 Part-3 fenced paths. Rewriting comments changes the content of 183. The union is
**184** of 242 fenced files repository-wide, and feature 043 changed 58 files against an estimate of 17. **A
plan counts the fix and not what the fix drags with it**, so the number above is stated as measured
today and expected to grow.

## Out of Scope

- Compressing chapters, merging them, or reducing the 6× size variance between the smallest and
  largest. **This now explicitly includes collapsing the four outbox explanations into one and the
  five subject-grammar derivations into one** — both are real defects, both were in FR-003's first
  draft, and both need prose rewritten rather than moved.
- Translating the Vietnamese pages. The user has said they will supply translations later.
- Reordering Parts 0, 1, 2 or 4, or renaming their chapter references.
- Any change to platform behaviour. Comments are rewritten; code is not.
- The open items in `specs/044-revision-watermark/gaps.md`, except where a chapter move forces one.

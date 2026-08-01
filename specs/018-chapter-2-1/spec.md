# Feature Specification: Tutorial Chapter 2.1 — Schema with a Spine

**Feature Branch**: `018-chapter-2-1`

**Created**: 2026-08-01

**Status**: Draft

**Input**: User description: "Start chapter 2.1"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 2.1 and build the schema + repository layer alongside it (Priority: P1)

As the tutorial's reader, I open Part 2's first chapter — "Schema with a
spine" (docs/07 §3) — and the series reaches its heart: the core loop begins,
and it begins with the single most important requirement in the system.
FR-TEN-05 (no operation may touch another tenant's data) and driver D4 say
tenant isolation is a *correctness property*; this chapter makes it one — by
construction, not by vigilance. I write the first migrations (the SAD's own
tables: environments, users, channels, members, messages), connect the API
service to 1.2's Postgres for the first time, and build the repository layer
whose constructors *require* an `environment_id` — so that a cross-tenant
query is not a bug someone must catch in review, but a shape the code cannot
express. Docs/07's framing is the chapter's spine: cross-tenant leaks
"designed out, not tested out."

**Why this priority**: The chapter is the deliverable; it opens the part
docs/07 marks ★ ("where the tutorial earns its premise"), and every write,
read, and resume built in 2.2–2.8 flows through this layer.

**Independent Test**: A reader with the Part-1 checkpoint state can, using
only the chapter: run the migrations against the compose Postgres, build the
repository layer, watch the isolation tests attack it with foreign tenant IDs
and fail to leak, and explain why isolation lives in data access rather than
in handlers — without consulting docs/04/05/06.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** read end to end, **Then** it
   derives the schema from the SAD's data view (the tables the docs/07 row
   names, with their tenant columns and DR-cited constraints), builds
   versioned forward-only migrations, brings up the repository layer with
   mandatory tenant scoping, and closes in the runnable, tested state.
2. **Given** the format rules (docs/07 §2, code-chapter battery), **Then**
   the chapter passes: 2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, 1
   `SKIP AHEAD` naming tag `part2-ch1`, ≥1 forward reference, 2–4 captioned
   figures, takeaways, exactly one closing `CHECKPOINT`.
3. **Given** the chapter's factual claims, **Then** 100% trace to docs/04
   (FR-TEN, DR-01/02/03, NFR-SEC-09, CON-01), docs/05 (§6.1's SQL, D4,
   ADR-03/04, §8's repository-layer clause), the constitution (Principle I),
   or earlier chapters; SQL shown matches the SAD's own definitions where the
   SAD defines them; gaps are recorded chapter decisions.
4. **Given** the code the chapter builds, **Then** every file-content fence
   byte-matches the repository at `part2-ch1` — and where this chapter must
   CHANGE a file an earlier chapter fenced, the change is shown as an
   explicit diff in the chapter (the fence discipline's amendment mechanism,
   debuting here — see US2).

---

### User Story 2 - The canonical code advances to tag `part2-ch1`, and the fence discipline learns to amend (Priority: P2)

As a reader (or a stuck reader), the schema and repository layer exist in
`relay-platform` as the diff from `part1-ch4` to `part2-ch1`. This is the
first chapter that cannot be purely additive: the API service — whose
package manifest and entry files chapter 1.4 fenced — must gain its store
dependency and its wiring. The series' promised escape hatch therefore
debuts: **edits to previously fenced files appear in the chapter as explicit
diffs**, the earlier chapter's fence checks re-pin to its own tag, and
nothing changes silently. The gate also grows an honestly named second lane:
isolation tests run against the real compose Postgres.

**Why this priority**: The tag discipline continues, and the two mechanisms
this increment establishes — diff-fences and the integration test lane —
govern every core-loop chapter after it.

**Independent Test**: Checking out `part2-ch1` yields a workspace where the
Docker-free gate still passes; with the compose stack up, the migration
command and the isolation suite pass; the `part1-ch4..part2-ch1` diff
contains exactly the chapter's changes, and every changed-previously-fenced
file's edit corresponds to a diff shown in the chapter.

**Acceptance Scenarios**:

1. **Given** the repository at `part2-ch1`, **When** the established gate
   runs (lint, typecheck, test) with Docker stopped, **Then** it passes —
   unit-level tests never require stores.
2. **Given** the compose stack up, **When** the chapter's migration command
   and the new isolation suite run, **Then** migrations apply versioned and
   forward-only (constitution workflow clause), and the suite demonstrably
   attacks repository operations with foreign `environment_id`s and proves
   the leak inexpressible (constitution Principle I's suite, at the layer
   that exists today — its endpoint form arrives with endpoints).
3. **Given** the diff from `part1-ch4`, **Then** new code is additive where
   possible; every edit to a fenced file (at minimum the API service's
   manifest) is shown as an explicit diff in the chapter; 1.1–1.3's fences
   still byte-match; 1.4's fence battery re-pins to tag `part1-ch4` with the
   re-pinning recorded in the feature's verification artifacts.

---

### User Story 3 - Part 2 opens across the bilingual series (Priority: P3)

As a reader of either language, chapter 2.1 appears everywhere — and with it
**Part 2 comes alive**: the manifest gains all eight docs/07 chapters (2.1
published and translated; 2.2–2.8 forthcoming with draft Vietnamese titles),
Part 2 leaves the landing's road-ahead list and becomes the second chapter
section, the sidebar shows the new part in its mixed state, 1.4's footer
gains the next-chapter card its empty state was waiting for, the sitemap
grows by exactly two pages, the suggestions allowlist admits the new paths,
and the Vietnamese edition ships at the settled register.

**Why this priority**: Structural integration after content exists; the
Part 1 → Part 2 boundary crossing is this feature's unique navigation moment
(the second part-opening the series has performed, first since 013).

**Independent Test**: From either landing, reach 2.1 in ≤2 steps; Part 2
renders as a chapter section (1 link + 7 forthcoming) on both landings and
the sidebar; 1.4's footers show the next card in both locales; sitemap
32 → exactly 34; vi parity incl. byte-identical fences; suggestion POSTs
accepted for both new paths.

**Acceptance Scenarios**:

1. **Given** the series manifest, **When** the chapter ships, **Then** Part 2
   carries its eight docs/07 chapters with reserved paths and draft vi titles
   (Dong-reviewable), and every navigation surface updates with zero manual
   edits.
2. **Given** 1.4's footers (both locales), **Then** the next card appears,
   linking 2.1 — the part-boundary empty-next state retires exactly as
   designed, for the second time.
3. **Given** the Vietnamese chapter, **Then** box/figure/fence counts match
   en, fences are byte-identical, and the prose follows the naturalized
   register and settled glossary ("package", "cửa ải"/"vượt qua", "bản giao
   kèo", "tin nhắn", "thêm chi tiết"; SQL/identifiers/table names English; no
   calques or hyphenated compounds; naturalization self-review before
   presenting).

---

### Edge Cases

- **The additive-only rule's first real amendment**: the API service's
  `package.json`, and possibly its entry files, are 1.4 fences that must
  change. The diff-fence mechanism (edits shown as explicit diffs in the
  chapter; the amended chapter's fence battery re-pins to its own tag) debuts
  and must be defined precisely enough to govern all future amendments —
  including how en/vi keep diff content byte-identical.
- **The gate meets the database**: isolation is proven against a real
  Postgres, but the established three-command gate has been Docker-free for
  four chapters and must stay so. The split (unit lane vs. integration lane
  needing the compose stack) must be explicit, named, and taught — and the
  constitution's "suite runs on every build" is a recorded trajectory note
  until CI exists.
- **Schema scope discipline**: the docs/07 row names users, channels,
  members, messages (+ the environments table they all reference); the SAD's
  §6.1 defines more (edits, outbox, emoji, media). The chapter takes exactly
  the row's slice and names where the rest arrive.
- **The SAD's SQL is quotable source**: where the chapter's migrations
  reproduce SAD tables, they must match the SAD's definitions (columns,
  constraints, DR citations); divergence is either a recorded decision or a
  defect.
- **Isolation must be structural, not decorative**: "constructors require an
  `environment_id`" (constitution I / SAD §8) is the load-bearing clause —
  the chapter must show what becomes *inexpressible*, and the TRAP territory
  is the tempting alternative (filtering in handlers / trusting WHERE
  clauses sprinkled at call sites).
- **Test data and teardown**: integration tests against the compose Postgres
  must not depend on `down -v` hygiene between runs (deterministic seeding /
  cleanup), and must not touch Dong's Neon (that database belongs to the
  tutorial site's suggestions, not the product).
- **Seeding eight chapters bilingually**: draft vi titles ship for Dong's
  review (the 013 precedent); the established glossary applies ("đường hầm
  của Tuan" already exists for 2.7's subject).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chapter 2.1 MUST exist as a published chapter titled per
  docs/07 ("Schema with a spine") at a Part 2 path following the established
  URL convention, in both locales, rendered through the existing shell with
  all established chrome.
- **FR-002**: The chapter MUST teach tenant isolation as a correctness
  property designed out, not tested out (docs/07's row, D4, FR-TEN-05,
  constitution Principle I), pairing the capability with the failure it
  prevents per Part 2's chapter formula.
- **FR-003**: The chapter MUST build versioned, forward-only migrations for
  the row's tables (environments, users, channels, members, messages),
  matching the SAD §6.1 definitions where the SAD defines them (constraints
  and DR citations included) and recording as decisions whatever it leaves
  open.
- **FR-004**: The chapter MUST build the repository layer per the SAD §8 /
  constitution I clause — constructors require an `environment_id`, every
  operation is tenant-scoped by construction, raw connection access outside
  the layer is lint-forbidden (the enforcement mechanism itself is
  plan-level) — and MUST end in the runnable, tested state with a closing
  `CHECKPOINT`.
- **FR-005**: The chapter MUST pass the code-chapter battery: 2,000–4,000
  canonical words; ≥2 `WHY`; ≥1 `TRAP`; 1 `SKIP AHEAD` naming `part2-ch1`;
  ≥1 forward reference; 2–4 captioned figures; takeaways; exactly one closing
  `CHECKPOINT`.
- **FR-006**: The canonical repository MUST advance by exactly this chapter's
  content and be tagged `part2-ch1` (Dong's tag); new dependencies MUST be
  pinned, package-local, and reasoned in the chapter; an automated isolation
  suite MUST attack repository operations with foreign tenant IDs against a
  real database and pass.
- **FR-007**: The fence contract MUST hold with its new amendment mechanism:
  unchanged prior fences (1.1–1.3) still byte-match; every edit this chapter
  makes to a previously fenced file is shown as an explicit diff in the
  chapter (en/vi byte-identical); 1.4's fence checks re-pin to `part1-ch4`;
  2.1's own file fences byte-match at `part2-ch1`; commands replay — with
  the documented split between Docker-free and compose-required lanes.
- **FR-008**: Publishing MUST be manifest-plus-seed: Part 2's eight chapters
  enter the manifest (2.1 published + translated; 2.2–2.8 forthcoming with
  reserved paths and draft vi titles); all navigation surfaces update
  automatically; the sitemap grows from 32 to exactly 34; the suggestions
  allowlist admits the two new paths with zero edits.
- **FR-009**: The Vietnamese chapter MUST be structurally identical at the
  naturalized register per the settled glossary; SQL, table/column names,
  identifiers, and commands stay English; naturalization self-review before
  presenting.
- **FR-010**: 100% of quoted content MUST be faithful to current
  docs/04/05/06 and the constitution; the invented-ID detector passes over
  both page.mdx and both figures.ts; table/column names are SAD-derived or
  explicitly recorded decisions.

### Key Entities

- **Chapter 2.1**: Part 2's opener; sources docs/04 (FR-TEN-01..06, DR-01/02,
  NFR-SEC-09), docs/05 (§6.1, §8, D4, ADR-03/04), docs/06, constitution I,
  docs/07 §2–3; reader produces a migrated schema and a tenant-scoped
  repository layer with a passing isolation suite.
- **The schema**: The SAD §6.1 slice the row names — the operational tables
  every core-loop chapter builds on, each carrying its tenant column.
- **The repository layer**: The one place data access lives (ADR-04's
  single-writer discipline made code); constructors demand a tenant; the
  layer every later endpoint calls.
- **The fence amendment mechanism**: Explicit in-chapter diffs for edits to
  previously fenced files + per-chapter re-pinning — the discipline that
  lets the series modify its own published code honestly.
- **Chapter tag `part2-ch1`** and **the Part 2 manifest seed** (eight
  entries, the 013 pattern).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chapter body is 2,000–4,000 canonical words and passes the
  full battery in both locales with structural parity and byte-identical
  fences (including diff-fences).
- **SC-002**: At `part2-ch1`: the Docker-free gate passes; with the compose
  stack up, migrations apply cleanly to a fresh database AND re-running them
  is a no-op (forward-only, versioned), and the isolation suite passes while
  demonstrably attacking with foreign tenant IDs — machine-verified.
- **SC-003**: 100% of fence checks pass under the amended discipline:
  1.1–1.3 byte-match at `part2-ch1`; 1.4 byte-matches at `part1-ch4`
  (re-pinned); 2.1's fences and diff-fences match; the ID detector is clean.
- **SC-004**: From either landing, 2.1 is reachable in ≤2 steps; Part 2
  renders as a section with exactly 1 link + 7 forthcoming; 1.4's footers
  show the next card both locales; the sitemap holds exactly 34 URLs;
  suggestion submissions against both new paths succeed.
- **SC-005**: A test reader can go from the Part-1 checkpoint to the passing
  2.1 checkpoint within the chapter's stated time budget, using only the
  chapter.
- **SC-006**: Publishing changes only the manifest (the seed) and adds
  content files — every surface, including the allowlist, updates by itself.

## Assumptions

- **Chapter scope is docs/07's row**: migrations for the named tables + the
  repository layer + the isolation proof. The write path (row locks,
  sequences in anger) is 2.2; idempotency enforcement is 2.3; endpoints
  arrive with their chapters — the layer exists before its callers, like the
  protocol did.
- **Technology within the fixed stack**: Postgres via 1.2's compose; the
  driver, migration tooling, and lint-enforcement mechanism are plan-level
  decisions bounded by boring-by-design and the constitution.
- **The repository conventions continue, amended**: fence-equals-repo with
  the new diff-fence + re-pin mechanism; tag per docs/07 §2 (`part2-ch1`);
  the three-command gate stays Docker-free with a named integration lane
  beside it; commits/tags/pushes are Dong's.
- **Part 2's seed follows the 013 precedent**: eight entries, reserved
  paths, draft vi titles for Dong's review; Part 3+ stays road-ahead.
- **The isolation suite at this stage attacks the repository layer**; its
  endpoint-level form (constitution I's full "every endpoint" clause) grows
  with endpoints, and CI enforcement is a recorded trajectory item.
- **Integration tests use the local compose Postgres only** — never the
  tutorial site's Neon database.
- **Dong reviews the Vietnamese translation and the eight draft vi titles
  before committing; commits, pushes, and tags are Dong's.**

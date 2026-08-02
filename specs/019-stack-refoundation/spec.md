# Feature Specification: Stack Re-foundation — Turborepo, NestJS, Drizzle

**Feature Branch**: `019-stack-refoundation`

**Created**: 2026-08-01

**Status**: Draft

**Input**: User description: "Implement The re-foundation feature scope"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Re-read the three revised chapters and build the production-shaped stack (Priority: P1)

As the tutorial's reader, I follow chapters 1.1, 1.4, and 2.1 and what I
build is the stack the series has decided to be judged on — the one recorded
as ADR-15, ADR-16, and ADR-17 and bound by the constitution's Technology &
Platform Constraints (v1.1.0). Chapter 1.1 now raises the pnpm workspace
*and* the task graph over it: a gate whose cost scales with the change, not
the workspace (ADR-17). Chapter 1.4's walking skeleton builds the API
service as a real application-framework service (ADR-15) while the gateway
stays deliberately frameworkless — the chapter's new teaching beat is
exactly that boundary: the framework serves the wide surface and stops at
the gateway's door. Chapter 2.1 builds the repository layer on the typed
data layer ADR-16 chose, with migrations still versioned, forward-only,
hand-reviewed SQL — the write path's invariants stay visible. Because the
series was started with the promise of being "close to a production
application as much as possible," these chapters are revised honestly: the
prose describes the new truth, and the revision is announced, not hidden.

**Why this priority**: The chapters are the deliverable, and this is the
series' declared premise (docs/07 §1.1: "how a production-shaped system is
actually brought into existence") catching up with three accepted ADRs.
Every unwritten chapter from 2.2 onward will be authored on this
foundation; revising three chapters now is cheaper than contradicting
seventeen ADRs for forty more.

**Independent Test**: A new reader starting from an empty directory can
follow 1.1 → 1.2 → 1.3 → 1.4 → 2.1 in sequence, using only the chapters,
and arrive at the passing 2.1 checkpoint on the new stack — with every
intermediate chapter checkpoint green — without noticing a seam between
revised and untouched chapters.

**Acceptance Scenarios**:

1. **Given** the revised 1.1, **When** read end to end, **Then** it raises
   the workspace with the task runner ADR-17 records, teaches why the gate
   caches (and what a false green would mean), keeps its ADR-01 spine, and
   closes in the runnable, tested state its tag pins.
2. **Given** the revised 1.4, **When** read end to end, **Then** the API
   service comes up as an application-framework service per ADR-15, the
   gateway comes up frameworkless with the contrast taught explicitly, the
   chapter's compiler-strictness teaching is rescoped honestly (the flag
   that forbids framework idioms is kept where it still holds and released
   where ADR-15's trade-off spends it), and health checks, request IDs, and
   structured logs survive as the chapter's spine.
3. **Given** the revised 2.1, **When** read end to end, **Then** the
   repository layer is built on ADR-16's data layer with tenant scoping
   still required by construction, migrations remain versioned forward-only
   SQL generated-then-reviewed against SAD §6.1, and the isolation suite
   still attacks with foreign tenant IDs and fails to leak.
4. **Given** all three revised chapters, **Then** each passes the
   code-chapter battery (2,000–4,000 canonical words; ≥2 `WHY`; ≥1 `TRAP`;
   1 `SKIP AHEAD` naming its tag; ≥1 forward reference; 2–4 captioned
   figures; takeaways; exactly one closing `CHECKPOINT`), and each cites
   its governing ADR (17, 15, 16 respectively) in a `WHY` box.

---

### User Story 2 - The canonical repository is re-founded and the tag lineage is rebased honestly (Priority: P2)

As a reader (or a stuck reader), checking out any chapter tag still yields
exactly the state that chapter describes. This feature performs the
maneuver docs/07 §6 rule 3 reserved for this day: a later decision forces a
change to earlier code, so the tag lineage is rebased, every checkpoint
re-runs, and the affected chapters say so. The five published tags
(`part1-ch1` through `part2-ch1`) are re-cut under their existing names on
the re-founded history; chapters 1.2 and 1.3 — whose content does not
change — still byte-match their fences at the re-cut tags, and their
checkpoints still pass because the re-founded workspace flows through them.

**Why this priority**: The fence-equals-repo discipline is the series'
honesty mechanism; a re-foundation that broke it would cost more trust than
the new stack earns. This story is what makes User Story 1's revision
*checkable* rather than claimed.

**Independent Test**: At each of the five re-cut tags, the three-command
gate passes Docker-free; at `part2-ch1`, the compose stack up, migrations
apply cleanly and idempotently and the isolation suite passes; every fence
in every published chapter byte-matches its own chapter's tag; 2.1's
diff-fences reconstruct exactly (pre-image equals revised 1.4's published
fences, post-image equals the file at the re-cut `part2-ch1`).

**Acceptance Scenarios**:

1. **Given** any re-cut tag, **When** the established gate runs with Docker
   stopped, **Then** it passes — and from the revised 1.1 onward the gate
   runs through the task graph, warm or cold.
2. **Given** the re-cut `part2-ch1` with the compose stack up, **When** the
   migration command and isolation suite run, **Then** migrations are
   versioned and forward-only, re-running them is a no-op, and the suite
   demonstrably attacks repository operations with foreign tenant IDs.
3. **Given** the full published series, **Then** 100% of fence checks pass:
   1.2's and 1.3's fences unchanged and byte-matching their re-cut tags;
   1.1's, 1.4's, and 2.1's fences byte-matching their revised content at
   their re-cut tags; 2.1's diff-fences re-derived against revised 1.4.
4. **Given** the platform repository's "deliberately not yet" record for
   the task runner, **Then** it is resolved in place — the recorded revisit
   trigger is superseded by ADR-17's adoption, stated, not deleted
   silently.

---

### User Story 3 - The revision is visible, bilingual, and measured (Priority: P3)

As a reader of either language — including one who read the original
chapters — the revision is announced and complete. Each revised chapter
carries a reader-visible revision note (the docs/07 §6 rule 3 `REVISED`
note, debuting as a series mechanism) naming what changed and which ADR
drove it. The Vietnamese editions of all three chapters are revised to full
structural parity at the settled register, with fences byte-identical to
English. The word-count battery is re-baselined for the three revised
chapters while every untouched chapter's row stays byte-identical —
the measurement discipline survives its first revision.

**Why this priority**: Transparency and parity after content exists; the
revision-note mechanism established here governs every future revision the
series performs.

**Independent Test**: Both locales of every chapter in the final revision
set (1.1, 1.4, 2.1, plus any chapter added via FR-004's escape hatch)
display a revision note naming the driving ADRs; no other chapter displays
one; vi
box/figure/fence counts match en with byte-identical fences; the feature's
battery baseline shows exactly three changed rows per locale against 018's
baseline; no navigation surface, sitemap entry, or allowlist entry changes.

**Acceptance Scenarios**:

1. **Given** the revised chapters in both locales, **Then** each opens with
   (or prominently carries) a revision note stating the chapter was revised
   to adopt the re-founded stack, citing ADR-17/15/16 respectively — and
   the note's mechanism is reusable, not bespoke.
2. **Given** the Vietnamese editions, **Then** structure matches en
   (boxes, figures, fences, counts), fences are byte-identical, and prose
   follows the naturalized register and settled glossary ("package",
   "cửa ải"/"vượt qua", "bản giao kèo", "tin nhắn", "thêm chi tiết";
   identifiers/commands English; no calques; naturalization self-review
   before presenting).
3. **Given** the tutorial site, **Then** the sitemap URL set is unchanged,
   the manifest gains no entries, navigation renders identically, and the
   suggestions allowlist is untouched — this feature changes chapter
   content, not chapter existence.

---

### Edge Cases

- **The rebase's blast radius must be exact**: 1.1's revision changes root
  workspace files that every later tag contains, so all five tags re-cut
  even though only three chapters change prose. Chapters 1.2 and 1.3 are
  the control group: their prose and fences must survive untouched, their
  `SKIP AHEAD` boxes keep naming the same tag names, and their checkpoints
  must pass on the re-founded lineage. If the plan discovers an unavoidable
  touch to a 1.2/1.3-fenced file (e.g., the protocol package needing a
  build script for the new build order), that chapter joins the revision
  set explicitly — minimal edit, revision note, recorded decision — rather
  than drifting silently.
- **The compiler-strictness rescope**: 1.4 currently teaches a
  strictness flag as a workspace-wide guarantee, and 2.1's code comments
  cite "chapter 1.4's guarantee". ADR-15's framework spends that guarantee
  for the API service only. Both chapters must tell one consistent story
  about where the flag still holds (gateway, shared packages) and why it is
  released where it is — the trade-off is taught, not papered over.
- **The old tags' fate**: re-cutting reuses the five existing tag names so
  published prose stays true. Whether the prior states survive under
  archived names is Dong's call at tag time; the feature must leave the
  repository in a state where either choice is a tag operation, not a
  rework.
- **2.1's diff-fences are derived artifacts**: their pre-images are 1.4's
  *published fences*. Revised 1.4 changes those fences, so every 2.1
  diff-fence must be re-derived and re-verified — a stale pre-image is a
  broken fence check, not a cosmetic issue.
- **The revision note must not distort the battery**: the note is chrome
  (like boxes), not canonical prose; whether its words count toward the
  2,000–4,000 bound must be decided once, recorded, and applied identically
  in both locales.
- **The teaching beats that die must die on purpose**: 1.4's current
  runner-workaround narrative and 2.1's constructor-property teaching
  moment are casualties of the new stack. Each revised chapter replaces
  lost beats with the new stack's own failure-first material (e.g., the
  false-green cache, the framework-at-the-socket temptation) so the
  chapters don't thin out pedagogically.
- **Isolation survives the re-foundation**: the repository layer's
  "constructor requires a tenant" clause (constitution I) must hold in the
  framework's idiom — however request scoping is realized (plan-level), a
  handler must still be unable to express a query without a tenant, and
  the raw-driver lint ban must extend to the new data layer's client.
- **Never the tutorial site's database**: integration tests attack the
  local compose Postgres only; Dong's Neon belongs to the suggestions
  feature and is out of bounds.
- **Word counts move honestly**: three chapters' canonical word counts
  change (within bounds); the feature's baseline records the new values;
  every other row must be byte-identical to 018's baseline — the revision
  must not smuggle drift into untouched chapters.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chapter 1.1 MUST be revised in both locales to raise the
  workspace with ADR-17's task runner over the unchanged pnpm workspace:
  the three-command gate is preserved as the reader's contract, now taught
  as a cached task graph (including the false-green trade-off and its
  discipline), with the chapter's ADR-01 material intact.
- **FR-002**: Chapter 1.4 MUST be rewritten in both locales so the walking
  skeleton's API service is an application-framework service per ADR-15
  (module/DI/validation conventions, uniform error shaping, health
  endpoint, request IDs, structured logs) while the gateway remains
  frameworkless with the ADR-15 boundary taught explicitly; the
  compiler-strictness teaching is rescoped consistently with the framework
  idioms ADR-15 accepts.
- **FR-003**: Chapter 2.1 MUST be revised in both locales so the repository
  layer is built on ADR-16's data layer: tenant scoping required by
  construction in the framework's idiom, migrations remaining versioned
  forward-only SQL generated-then-reviewed against SAD §6.1 with drift
  checked, raw data-layer access outside the repository lint-forbidden,
  and the isolation suite passing against the compose database.
- **FR-004**: Chapters 1.2, 1.3, and all Part 0 chapters MUST remain
  unchanged in prose and fences; if the plan proves a 1.2/1.3-fenced file
  must change, that chapter enters the revision set explicitly with a
  minimal edit, its own revision note, and a recorded decision.
- **FR-005**: The canonical repository MUST be re-founded so that the five
  published tags (`part1-ch1`, `part1-ch2`, `part1-ch3`, `part1-ch4`,
  `part2-ch1`) are re-cut under their existing names, each pinning exactly
  the state its chapter describes; at every tag the three-command gate
  passes Docker-free, and at `part2-ch1` the integration lane passes
  against the compose database. Tag operations themselves are Dong's.
- **FR-006**: The fence contract MUST hold across the entire published
  series after the rebase: every file fence byte-matches its own chapter's
  re-cut tag; 2.1's diff-fences are re-derived (pre-image = revised 1.4's
  published fences; post-image = the file at re-cut `part2-ch1`); en/vi
  fences stay byte-identical; all chapter commands replay.
- **FR-007**: Each revised chapter MUST carry a reader-visible revision
  note in both locales — the docs/07 §6 rule 3 `REVISED` note, established
  here as a reusable series mechanism — naming what changed and the
  driving ADR; no unrevised chapter carries one.
- **FR-008**: All three revised chapters MUST pass the code-chapter
  battery in both locales; the feature MUST ship a battery baseline where
  exactly the revised chapters' rows change relative to 018's baseline and
  every other row is byte-identical.
- **FR-009**: The Vietnamese editions MUST be revised to full structural
  parity at the naturalized register per the settled glossary;
  identifiers, commands, table/column names, and code stay English;
  naturalization self-review before presenting.
- **FR-010**: 100% of quoted content and factual claims MUST trace to the
  current docs/04/05/06/07 (including ADR-15/16/17 and their deep dives)
  and constitution v1.1.0; the invented-ID detector passes over all
  revised page.mdx and figures.ts files; the platform repository's
  "deliberately not yet" task-runner record is resolved in place, citing
  ADR-17.
- **FR-011**: The tutorial site's navigation, manifest, sitemap, and
  suggestions allowlist MUST be unchanged by this feature — content is
  revised, no page is added, removed, or moved.

### Key Entities

- **The revision set**: Chapters 1.1, 1.4, 2.1 in both locales — prose,
  boxes, figures, and fences revised to teach the ADR-15/16/17 stack;
  sources: docs/05 (ADR-15/16/17, §6.1, §8), docs/06 (three new deep
  dives), docs/07 §2–3 (amended rows), constitution v1.1.0.
- **The control set**: Chapters 1.2, 1.3, and Part 0 — must pass through
  the re-foundation byte-unchanged, proving the revision's blast radius
  was exactly as declared.
- **The re-founded canonical repository**: The platform workspace rebuilt
  on the accepted stack; five tags re-cut under existing names; the state
  every fence check and checkpoint verifies against.
- **The revision note**: The reader-visible `REVISED` marker (docs/07 §6
  rule 3) debuting as a reusable mechanism — the series' way of changing
  its mind in public.
- **The re-derived diff-fences**: 2.1's amendment fences rebuilt against
  revised 1.4 — the proof the amendment mechanism survives revision of its
  own pre-images.
- **The 019 battery baseline**: The measurement artifact in which exactly
  six rows (three chapters × two locales) may differ from 018's.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three revised chapters pass the full code-chapter battery
  in both locales (word bounds, box minima, figure counts, structural
  parity, byte-identical fences), and the 019 baseline differs from 018's
  in exactly the revised chapters' rows.
- **SC-002**: At each of the five re-cut tags the three-command gate passes
  with Docker stopped; at `part2-ch1` with the compose stack up, migrations
  apply cleanly to a fresh database, re-running them is a no-op, and the
  isolation suite passes while demonstrably attacking with foreign tenant
  IDs — machine-verified.
- **SC-003**: 100% of fence checks across all published chapters pass after
  the rebase, including 1.2/1.3 unchanged fences and 2.1's re-derived
  diff-fences; the invented-ID detector is clean over all revised files.
- **SC-004**: The sitemap URL set, manifest entries, navigation surfaces,
  and suggestions allowlist are bit-for-bit unchanged by the feature.
- **SC-005**: A test reader can follow the published series from an empty
  directory to the passing 2.1 checkpoint using only the chapters, with
  every intermediate checkpoint green on the re-founded lineage.
- **SC-006**: Exactly the revision set's chapters per locale display a
  revision note (1.1, 1.4, 2.1, plus any chapter added via FR-004); each
  names its driving ADR; zero unrevised chapters display one.

## Assumptions

- **The stack is decided, not re-litigated**: ADR-15 (framework, API
  service only), ADR-16 (data layer inside the repository), and ADR-17
  (task runner over the pnpm workspace) are accepted and constitution
  v1.1.0 binds them; this feature implements, it does not re-argue.
  Specific versions, config shapes, and the request-scoping idiom are
  plan-level decisions bounded by boring-by-design.
- **Revision, not addition**: no new chapters, pages, or manifest entries;
  chapters 2.2–2.8 remain forthcoming and will be authored on the new
  foundation.
- **The tag lineage is rebased under existing names** (docs/07 §6 rule 3);
  whether prior states are archived under other names is Dong's decision
  at tag time; commits, tags, and pushes are Dong's, on Dong's explicit
  go-ahead only.
- **The gateway and the protocol package keep their teaching intent**:
  frameworkless gateway (ADR-15's scope clause), contract-first protocol
  package (1.3); any mechanical touch their files need is surfaced
  explicitly per FR-004, not assumed.
- **Integration tests use the local compose Postgres only** — never the
  tutorial site's Neon database.
- **Dong reviews the Vietnamese revisions before committing.**

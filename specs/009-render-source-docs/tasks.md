# Tasks: Chapter 0 Improvement — Render the Source Documents

**Input**: Design documents from `/specs/009-render-source-docs/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/reference-docs-contract.md, quickstart.md

**Tests**: Not requested — verification is contract C4's scripted battery (drift,
routes, sentinels, chapter links, hreflang, **battery freeze**), quickstart V1–V5,
and `pnpm lint && pnpm build`. Diagram/theme legibility is a named manual check (V3).

**Organization**: First infrastructure feature since 004. Distinctive obligations:
**verbatim mirrors** (byte-identical to parent `docs/`, drift-checked), **MDX is
forbidden for the docs** (JSX-hostile prose — research R2; render raw strings with
react-markdown + remark-gfm), **theme-aware mermaid** (6 diagrams, both themes), and
the **battery freeze** — all ten existing chapter `page.mdx` files stay
byte-identical, proven against a baseline recorded BEFORE any change (V0).

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` (Dong commits
personally). Consult `node_modules/next/dist/docs/` before writing route/component
code (AGENTS.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = read the rendered document, US2 = navigate without getting lost, US3 = documents stay truthful

## Path Conventions

- App paths relative to `/home/dong/work/relay/relay-tutorial/`
- Canonical sources: `/home/dong/work/relay/docs/0{1..6}-*.md` (parent repo — never edited by this feature)
- Mirrors (NEW): `content/docs/0{1..6}-*.md` — written only by the sync script
- Registry slugs: `product-vision`, `personas`, `journey-map`, `srs`, `sad`, `adr-deep-dives`

---

## Phase 1: Setup

**Purpose**: The freeze baseline (must precede all changes) and the new dependencies

- [X] T001 Record the battery baseline per quickstart V0 for all ten existing chapter files (`app/{,vi/}part-0/chapter-0[1-5]/*/page.mdx`: canonical words, Why/SkipAhead/ForwardRef/Checkpoint counts, fence lines) and save it to /home/dong/work/relay/specs/009-render-source-docs/battery-baseline.txt — this is SC-004's before-picture; do it before touching anything
- [X] T002 Add dependencies in relay-tutorial/package.json via `pnpm add react-markdown remark-gfm mermaid` (research R2/R3); `pnpm lint && pnpm build` still green before any feature code

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The verbatim mirrors and the registry every story reads from

- [X] T003 Create relay-tutorial/scripts/sync-docs.sh (copy `../docs/0[1-6]-*.md` → `content/docs/`, fail if parent missing) and relay-tutorial/scripts/check-docs-drift.sh (per data-model E2: diff each mirror against `../docs/`; non-zero exit naming the diverged file; warning + exit 0 when parent absent); wire `"sync:docs"` and `"check:docs"` into relay-tutorial/package.json; run the sync to populate content/docs/ with all six files and confirm `pnpm check:docs` exits 0 (FR-005/009)
- [X] T004 [P] Create the six-entry registry in relay-tutorial/lib/docs.ts per data-model E1: `{slug, sourceDoc, file, title, titleVi}` with `sourceDoc` values matching the manifest verbatim (`docs/01-product-vision.md` … `docs/06-adr-deep-dives.md`); helpers `getDoc(slug)`, `docsForSourceDoc(field)` (split on comma, trim, resolve; unresolved segments returned as plain-text labels — the 002 no-dead-link rule), and `chaptersCiting(slug)` (reverse lookup over the manifest's published chapters — data-model E1)

---

## Phase 3: User Story 1 - Open a chapter's source document and read it correctly rendered (Priority: P1) 🎯 MVP

**Goal**: All six documents readable at `/docs/[slug]` with full GFM + diagram fidelity, linked from every chapter header.

**Independent Test**: From chapter 0.5, open the SAD reference: drivers table renders as a table, all six diagrams render as diagrams, ADR-13 reads verbatim (quickstart V2 sentinels + V3.1/V3.5).

### Implementation for User Story 1

- [X] T005 [P] [US1] Create the theme-aware diagram component in relay-tutorial/components/docs/mermaid-diagram.tsx per data-model E3: client component; lazy `import("mermaid")` on mount; `securityLevel: "strict"`; mermaid theme `"default"`/`"dark"` from next-themes `resolvedTheme`; re-render on theme change; pre-hydration fallback renders the diagram source in a `<pre>` fence (FR-004, research R3)
- [X] T006 [US1] Create the renderer in relay-tutorial/components/docs/doc-article.tsx per research R2 (consult node_modules/next/dist/docs/ first): server component taking the mirrored file's raw string; react-markdown + remark-gfm; component overrides — every `<table>` wrapped in an `overflow-x-auto` container (C3 overflow bound), fenced ` ```mermaid ` blocks routed to MermaidDiagram, other fences as styled code blocks, headings h2/h3 given stable slugified ids; typography via existing prose/token styling; NO raw-HTML plugin (all raw HTML in the docs sits inside mermaid fences)
- [X] T007 [US1] Create relay-tutorial/app/docs/[slug]/page.tsx: `generateStaticParams` over the registry; read `content/docs/<file>` via fs at build; metadata title from registry + " — Building Relay" with hreflang alternates (`/docs/[slug]` ↔ `/vi/docs/[slug]`, 004 C4 pattern); site chrome + back-to-contents link + the "referenced by" line linking each citing chapter via `chaptersCiting` (US2-AS1, contract C2); render DocArticle; unknown slug → 404; then `pnpm build` (6 en routes appear) and run the V2 sentinel greps (srs: `FR-TEN-05`; sad: `last_sequence`; adr-deep-dives: `Revisit when`; `<table` ≥1 on table-bearing pages, zero `^|` lines in served HTML)
- [X] T008 [US1] Add the chapter-header affordance per data-model E4: i18n keys in relay-tutorial/lib/i18n.ts (`shell.sourceDocs`: "Source" / "Tài liệu gốc"; `badges.englishDoc`: "English" / "tiếng Anh"); in relay-tutorial/components/tutorial/chapter-shell.tsx, `ChapterHeader` resolves `chapter.sourceDoc` via `docsForSourceDoc` and renders the labeled links line (locale-prefixed hrefs, locale titles, English hint on vi) under the reader-produces line; verify every published chapter (×2 locales) links its doc(s) — 0.5 shows BOTH sad and adr-deep-dives; **battery freeze**: re-run the V0 measurement and diff against specs/009-render-source-docs/battery-baseline.txt — must be identical (FR-001/007/008, SC-004)

**Checkpoint**: US1 delivers the feature's core value — documents readable, chapters linking to them

---

## Phase 4: User Story 2 - Move between chapter and document without getting lost (Priority: P2)

**Goal**: In-document navigation and the full Vietnamese counterpart surface.

**Independent Test**: From vi chapter 0.4, open the SRS, jump to a top-level section in ≤2 actions, return; switcher maps `/docs/x` ↔ `/vi/docs/x` (quickstart V3.3–V3.4).

### Implementation for User Story 2

- [X] T009 [US2] Add the "Contents" outline to relay-tutorial/components/docs/doc-article.tsx per research R4: extract the document's h2 sections server-side and render an anchor-link outline block above the article (any top-level section = 1 click from top, SC-005); verify anchors land on the slugified heading ids from T006 (FR-006)
- [X] T010 [US2] Create relay-tutorial/app/vi/docs/[slug]/page.tsx per research R6: same registry/`generateStaticParams` + fs read; vi chrome (renders inside the existing `app/vi` `lang="vi"` layout); the article wrapped in `lang="en"` with the one-line note "Tài liệu gốc — được giữ nguyên tiếng Anh"; vi metadata title (registry `titleVi` + " — Building Relay") + hreflang pair; the "referenced by" line with `/vi/…` chapter hrefs and vi titles; verify with dev server: all 12 doc routes 200 with hreflang ≥2; `lang="en"` wrapper present on vi doc pages only; language switcher maps both directions; vi chapter headers link to `/vi/docs/…` (FR-008)

**Checkpoint**: Both locales navigate chapter ↔ document ↔ section cleanly

---

## Phase 5: User Story 3 - The documents stay truthful over time (Priority: P3)

**Goal**: The refresh path proven end to end and documented.

**Independent Test**: A deliberate 1-line divergence is caught by `pnpm check:docs`; the sync script propagates a parent edit to the page (quickstart V2 drift drill + V5).

### Implementation for User Story 3

- [X] T011 [US3] Prove and document the truth loop: run the V2 drift drill (append a line to content/docs/01-product-vision.md → `pnpm check:docs` fails naming the file → restore) and the V5 refresh drill (edit one line in /home/dong/work/relay/docs/02-personas.md → `scripts/sync-docs.sh` → page reflects it → `git checkout` both copies); then document the workflow in relay-tutorial/README.md ("Updating the mirrored docs": mirrors live in content/docs/, written only by `pnpm sync:docs`, checked by `pnpm check:docs`, never hand-edited) (FR-009, SC-006)

**Checkpoint**: All three user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation and the no-commit handoff

- [X] T012 Run the complete quickstart V1–V3 for specs/009-render-source-docs/quickstart.md and record results: route table (V1 — exactly 12 new routes, chapter routes unchanged), full scripted battery (V2 — drift, sentinels, tables, chapter links incl. 0.5's two, hreflang, lang wrappers, battery freeze vs specs/009-render-source-docs/battery-baseline.txt), manual pass (V3 — all six mermaid diagrams in BOTH themes on /docs/sad and /vi/docs/sad, /docs/srs tables at 375 px with no page overflow, outline jump to SAD §9, the chapter→doc→switcher walk both locales, drivers-table + ADR-13 fidelity spot-check); flag V4 (Dong's skim of the six pages, both themes) prominently
- [X] T013 Handoff (NO commits — standing instruction): report ready-to-commit files for relay-tutorial (new: content/docs/ ×6, scripts/ ×2, lib/docs.ts, components/docs/ ×2, app/docs/[slug]/page.tsx, app/vi/docs/[slug]/page.tsx; modified: package.json + lockfile, lib/i18n.ts, components/tutorial/chapter-shell.tsx, README.md) with a suggested commit message; note parent-repo follow-ups (spec artifacts incl. battery-baseline.txt, CLAUDE.md pointer, feature.json, submodule pin); request Dong's V4 pass before committing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 strictly first (the before-picture); T002 after T001
- **Foundational (Phase 2)**: T003 and T004 [P] after T002
- **US1 (Phase 3)**: T005 [P] anytime after T002; T006 after T005 (routes fences to it); T007 after T003+T004+T006; T008 after T004+T007 (links need live routes)
- **US2 (Phase 4)**: T009 after T006; T010 after T007 (shares the renderer; hreflang pairs need both routes → verify after)
- **US3 (Phase 5)**: T011 after T003 (any time later; placed after US2 for the settled serial habit)
- **Polish (Phase 6)**: T012 after all; T013 last

### User Story Dependencies

- **US1 (P1)**: Setup + Foundational only — the MVP
- **US2 (P2)**: builds on US1's renderer and en routes
- **US3 (P3)**: only needs Foundational's scripts; independent of US1/US2

### Parallel Opportunities

- T004 (registry) ∥ T003 (scripts/mirrors) — different files
- T005 (mermaid component) ∥ T003/T004 — different files
- T011 (US3) could run any time after T003 if resequencing is ever useful

## Parallel Example

```bash
# After T002:
#   lane A: T003 (scripts + mirrors)
#   lane B: T004 (lib/docs.ts) and T005 (mermaid-diagram.tsx)
# Then serial: T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001–T008 — six documents rendered correctly at /docs/[slug], linked from every chapter header, battery frozen
2. **STOP and VALIDATE**: tables + diagrams + verbatim sentinels + chapter links

### Incremental Delivery

1. US1 → the primary sources readable and one action away
2. US2 → outline navigation + the full /vi mirror
3. US3 → the truth loop proven and documented
4. Polish → full battery; request Dong's pass; handoff

---

## Notes

- NEVER convert the docs to MDX — `{channel_id: seq}` in ADR-03's prose is a JSX
  expression to MDX and kills the build (research R2)
- content/docs/ files are machine-written only; any hand edit is a drift-check
  failure by design
- GFM stays isolated to DocArticle; the chapter MDX pipeline config is untouched
- The battery baseline (T001) is the feature's before-picture — if T008's diff is
  not empty, the affordance leaked into chapter files and must be reworked, not
  re-baselined
- NO git commit / git push — Dong commits personally

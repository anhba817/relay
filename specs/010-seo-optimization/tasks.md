# Tasks: SEO Optimization for the Existing Pages

**Input**: Design documents from `/specs/010-seo-optimization/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/seo-contract.md, quickstart.md

**Tests**: Not requested — verification is the seo-contract's scripted battery
(quickstart V1–V3, V5) plus deploy-time validators (V4, Dong). No new dependencies
anywhere.

**Organization**: Infrastructure feature. Distinctive obligations: **the ten
chapter files move but MUST NOT change** (route-group restructure — pure renames,
proven by the path-normalized battery diff); **chapter OG/JSON-LD flows through
ChapterHeader** (React 19 hoisting — layout-level openGraph inherits wholesale and
would show the wrong og:title, and chapter metadata blocks are word-counted by the
battery, so chapter files get zero edits); **exactly one og:image source**
(the /og route declared once in shared metadata — nothing else may emit image tags).

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` (Dong commits
personally). Consult `node_modules/next/dist/docs/` before route-group and
metadata-route code (AGENTS.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = discover/crawl/index, US2 = rich link previews, US3 = structured data

## Path Conventions

- App paths relative to `/home/dong/work/relay/relay-tutorial/`
- After the restructure: en pages under `app/(en)/…`, vi pages under
  `app/(vi)/vi/…` — URLs unchanged
- The 24 indexable pages: `/`, `/vi`, 5+5 chapters, 6+6 reference docs

---

## Phase 1: Setup

**Purpose**: The freeze baseline (before any file moves)

- [X] T001 Copy the current battery baseline (already current as of the 0.5 polish) from specs/009-render-source-docs/battery-baseline.txt to /home/dong/work/relay/specs/010-seo-optimization/battery-baseline.txt per quickstart V0 — the count columns are the SC-007 before-picture; V2's diff normalizes the new paths against it

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The helper module every story reads from

- [X] T002 Create relay-tutorial/lib/seo.ts per data-model E1: `siteUrl()` (from `NEXT_PUBLIC_SITE_URL`, same source as metadataBase — FR-008), `ogLocale(locale)` (`en_US`/`vi_VN`), `chapterArticleJsonLd(chapter, locale)` (TechArticle: headline = locale title, description = locale reader-produces, inLanguage, absolute url, position = chapter id, isPartOf WebSite "Building Relay"), `websiteJsonLd(locale)` (WebSite naming both language URLs); `pnpm lint` green

---

## Phase 3: User Story 1 - Search engines can discover, crawl, and index every page (Priority: P1) 🎯 MVP

**Goal**: Sitemap + robots live; every page correctly language-labeled; canonicals/hreflang proven intact.

**Independent Test**: A crawl of /sitemap.xml reaches 100% of pages (24/24, all 200); `<html lang>` correct on all 24; 24/24 self-canonical with bidirectional alternates (quickstart V2 C1–C2).

### Implementation for User Story 1

- [X] T003 [US1] Restructure app/ into per-locale root layouts per data-model E2 (consult node_modules/next/dist/docs/ route-groups + layout conventions first): create relay-tutorial/components/root-shell.tsx (fonts, ThemeProvider, SiteHeader, globals.css import — extracted from the current app/layout.tsx); create app/(en)/layout.tsx (`<html lang="en">`, RootShell, shared metadata: metadataBase, default title/description, `openGraph.siteName: "Building Relay"`, `twitter.card: "summary_large_image"`) and app/(vi)/layout.tsx (`<html lang="vi">`, RootShell, vi default description, same shared fields); `git mv` app/page.tsx, app/part-0/, app/docs/ into app/(en)/ and app/vi/ into app/(vi)/vi/; delete the old app/layout.tsx and the `<div lang="vi">` wrapper layout (app/(vi)/vi/layout.tsx keeps nothing unless other duties exist — the doc pages' `lang="en"` article wrapper stays untouched); app/icon.jpg stays at app/ root — verify the icon still serves (fallback: place it in both groups); then `pnpm build` (identical 24 URLs), spot `<html lang>` on /, /vi, a vi chapter, and run quickstart V2's C5 normalized battery diff — MUST be empty (FR-003/009)
- [X] T004 [P] [US1] Create relay-tutorial/app/sitemap.ts per data-model E3: entries for `/` and `/vi`, every published chapter path (+ `/vi` counterpart only when `translatedIn` includes "vi"), and every doc-registry slug ×2 — absolute URLs via `siteUrl()`, `alternates.languages` per entry; nothing unpublished, no parts 1–8 (FR-001)
- [X] T005 [P] [US1] Create relay-tutorial/app/robots.ts per data-model E3: allow all user agents, `sitemap: <siteUrl>/sitemap.xml` (FR-002)
- [X] T006 [US1] Run the C1–C2 battery per quickstart V2 with the dev server: sitemap has exactly 24 `<loc>` and every listed URL serves 200; robots.txt names the sitemap; `<html lang>` matrix (en on 12, vi on 12 — loop all 24); vi doc pages keep the `lang="en"` article wrapper; the `div lang="vi"` wrapper is gone; canonical == 1 and hreflang ≥ 2 on the six-page spot matrix; fix findings

**Checkpoint**: US1 delivers indexability — crawlable, complete, correctly labeled

---

## Phase 4: User Story 2 - Shared links unfurl into rich previews (Priority: P2)

**Goal**: Every page produces a complete, language-correct social-preview card with the series image.

**Independent Test**: OG matrix (contract C3) passes on all page classes: og:title equals each page's own title (vi chapters show vi titles), og:locale correct, exactly one og:image everywhere (quickstart V2 C3).

### Implementation for User Story 2

- [X] T007 [P] [US2] Create the series preview image per data-model E5 (as implemented: relay-tutorial/app/(en)/og/route.tsx serving URL /og — the file convention does not attach without a top-level root layout and per-group copies would collide): `ImageResponse` from next/og (built-in — no new deps); 1200×630 PNG; "Building Relay" + series tagline on static Violet Bloom hex colors; declared once as `openGraph.images` in lib/seo.ts sharedMetadata/baseOpenGraph; verify /og serves the card (FR-006)
- [X] T008 [P] [US2] Add chapter preview tags in relay-tutorial/components/tutorial/chapter-shell.tsx per research R3 (as implemented): `ChapterHeader` renders hoisted `<meta>` elements for `og:url` (absolute via `siteUrl()` + localePath), `og:type` "article", `og:locale` via `ogLocale` — ONLY these; og/twitter title+description come from each page's own metadata via the API fallback, and og:image from the shared metadata declaration; zero edits to any chapter page.mdx (FR-005/009)
- [X] T009 [US2] Add `openGraph` to the editable pages per data-model E4: relay-tutorial/app/(en)/page.tsx and app/(vi)/vi/page.tsx metadata (title, description, url, `type: "website"`, locale) and both docs routes' `generateMetadata` (app/(en)/docs/[slug]/page.tsx, app/(vi)/vi/docs/[slug]/page.tsx — locale-appropriate titles/descriptions, canonical url, locale); no image fields anywhere (FR-005)
- [X] T010 [US2] Run the C3 battery per quickstart V2 (as implemented): exactly ONE og:title per page on 24/24, equal to the page's own title via the metadata API fallback (spot-check 0.5 en and vi verbatim); exactly one og:description each (the page's own); og:locale en_US/vi_VN split; og:type article on chapters, website elsewhere; exactly one og:image and one twitter:card per page across the six-page matrix; fix findings

**Checkpoint**: Any page shared anywhere unfurls correctly in its own language

---

## Phase 5: User Story 3 - Chapters qualify for rich search results (Priority: P3)

**Goal**: Valid TechArticle on all ten chapter pages; WebSite on both landings; nothing on doc pages.

**Independent Test**: JSON-LD extraction shows ['TechArticle'] on chapters, ['WebSite'] on landings, [] on docs, every block parsing as valid JSON (quickstart V2 C4).

### Implementation for User Story 3

- [X] T011 [US3] Emit structured data per data-model E6: `ChapterHeader` (relay-tutorial/components/tutorial/chapter-shell.tsx) renders one `<script type="application/ld+json">` with `chapterArticleJsonLd(chapter, locale)`; both landing page.tsx files render `websiteJsonLd(locale)`; doc pages get none; then run the C4 extraction loop (quickstart V2) — 10× TechArticle, 2× WebSite, 0 on docs, all blocks `json.loads`-clean (FR-007)

**Checkpoint**: All three user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation, the publish-flow proof, and the no-commit handoff

- [X] T012 Run the complete quickstart V1–V3 + V5 for specs/010-seo-optimization/quickstart.md and record results: build/route table (V1 — 24 page routes + sitemap/robots/opengraph-image), full scripted battery (V2 — C1 sitemap completeness incl. the dead-link loop, C2 lang/canonical/hreflang matrices, C3 OG matrix, C4 JSON-LD, C5 normalized battery freeze), manual local pass (V3 — the 1200×630 card renders, hoisted tags in head, no duplicate og:image, zero visible content change), publish-flow proof (V5 — temporarily flip 0.5 to "forthcoming": the sitemap shrinks by exactly its 2 URLs with zero other edits, then revert — no forthcoming chapter exists to flip the other way); flag V4 prominently: link-preview validators, rich-results test, and Lighthouse SEO = Dong, against the deployed URL
- [X] T013 Handoff (NO commits — standing instruction): report ready-to-commit files for relay-tutorial (new: lib/seo.ts, components/root-shell.tsx, app/(en)/layout.tsx, app/(vi)/layout.tsx, app/sitemap.ts, app/robots.ts, app/opengraph-image.tsx; moved: all page routes into the two groups; modified: components/tutorial/chapter-shell.tsx, both landing page.tsx, both docs [slug] routes; deleted: app/layout.tsx, the old vi lang-wrapper layout) with a suggested commit message; note parent-repo follow-ups (spec artifacts incl. battery-baseline.txt, CLAUDE.md pointer, feature.json, submodule pin); list the V4 deploy-time checks awaiting Dong

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 strictly first
- **Foundational (Phase 2)**: T002 after T001
- **US1 (Phase 3)**: T003 after T002; T004 ∥ T005 after T002 (independent of T003 — different files); T006 after T003+T004+T005
- **US2 (Phase 4)**: T007 ∥ T008 after T002 (independent files); T009 after T003 (edits files at their post-move paths); T010 after T007+T008+T009
- **US3 (Phase 5)**: T011 after T008 (same shell file — serialize); landings part after T003
- **Polish (Phase 6)**: T012 after all; T013 last

### User Story Dependencies

- **US1 (P1)**: Foundational only — the MVP
- **US2 (P2)**: T009 needs US1's T003 (post-move paths); T007/T008 independent
- **US3 (P3)**: shares the shell with US2's T008 — runs after it

### Parallel Opportunities

- T004 ∥ T005 (sitemap / robots)
- T007 ∥ T008 (image route / shell tags) — and both ∥ T004/T005
- The restructure T003 is deliberately serial and alone: file moves + two new root layouts, verified before anything builds on the new paths

## Parallel Example

```bash
# After T002:
#   lane A: T003 (restructure — the sensitive one, alone)
#   lane B: T004 + T005 (sitemap, robots)
#   lane C: T007 (og image) + T008 (shell tags)
# Then: T006 → T009 → T010 → T011 → T012 → T013
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001–T006 — indexable: sitemap, robots, correct languages, canonicals proven
2. **STOP and VALIDATE**: the C1–C2 matrices pass 24/24

### Incremental Delivery

1. US1 → discoverable and correctly labeled
2. US2 → every shared link unfurls in its own language
3. US3 → chapters carry valid article structured data
4. Polish → full battery + publish-flow proof; deploy-time validators to Dong

---

## Notes

- The ten chapter page.mdx files are moved with `git mv` and never edited — if the
  normalized battery diff (V2 C5) is non-empty, the restructure leaked into
  content and must be reworked, not re-baselined
- Only app/opengraph-image.tsx may emit og:image/twitter:image — duplicates are a
  validator failure (contract C3)
- og:title for chapters comes from the shell (React 19 hoisting), NEVER from
  layout-level openGraph — the inheritance rule makes layout og:title wrong
  (research header)
- All absolute URLs via lib/seo.ts `siteUrl()` — zero hardcoded domains (FR-008)
- NO git commit / git push — Dong commits personally

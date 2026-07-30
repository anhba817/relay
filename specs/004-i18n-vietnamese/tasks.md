# Tasks: Internationalization with Vietnamese Chapter 0.1

**Input**: Design documents from `/specs/004-i18n-vietnamese/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/i18n-contract.md, quickstart.md

**Tests**: Not requested — verification is the quickstart's scripted checks (contract C6), its manual scenarios, and the `pnpm lint && pnpm build` gate. Translation quality (quickstart V5) is reviewed by Dong, not by script.

**Organization**: Tasks grouped by user story. The Foundational phase carries the locale plumbing (dictionaries, manifest fields, component props) because all three stories consume it. The iron rule throughout: **no existing English route changes address or body content** (contract C1); the single permitted en edit is additive hreflang metadata (US3).

**⚠ Standing instruction**: Do NOT run `git commit` or `git push` — Dong commits personally. The final task is a handoff report with suggested commit messages.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = switcher + localized chrome, US2 = Vietnamese chapter 0.1, US3 = coherent bilingual structure

## Path Conventions

- All paths relative to `/home/dong/work/relay/relay-tutorial/` (the submodule)
- EN chapter: `app/part-0/chapter-01/from-app-to-infrastructure/page.mdx` (source of the translation)
- VI mirror root: `app/vi/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: None — zero new dependencies (research R1); the codebase from features 001–003 is the baseline.

*(no tasks)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The locale plumbing every story renders through

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T001 Create the i18n module in relay-tutorial/lib/i18n.ts per data-model E1/E2 and contract C3: `type Locale = "en" | "vi"`; a shared `Dictionary` type and `dictionaries: Record<Locale, Dictionary>` covering ALL reader-facing chrome strings (landing pitch + section labels + "forthcoming"/"the road ahead", chapter-shell strings — breadcrumb aria, "You will produce", minutes note, Previous/Next, back-to-contents, forthcoming badge, "available in English only" badge — box labels Why/Trap/Checkpoint/Skip ahead/Revised/Forward reference, locale-hint texts, switcher accessible labels); helpers `t(locale)`, `localeFromPath(path)` (`/vi` prefix ⇒ vi), `counterpartPath(path)` (pure prefix add/strip)
- [x] T002 [P] Extend the series manifest in relay-tutorial/lib/tutorial.ts per data-model E3: add optional `titleVi`, `readerProducesVi`, `translatedIn?: Locale[]` to `Chapter` (0.1 gets `translatedIn: ["vi"]` plus Vietnamese title/readerProduces; 0.2–0.5 get `titleVi`/`readerProducesVi` only) and `titleVi` per part; add accessors `chapterTitle(ch, locale)` / `chapterReaderProduces(ch, locale)` / `partTitle(part, locale)` with English fallback; body availability derives ONLY from `translatedIn` (FR-009)
- [x] T003 [P] Add the `locale` prop (default `"en"`) to all six box components in relay-tutorial/components/tutorial/boxes.tsx: labels come from `t(locale)` instead of hardcoded strings (`Why — {source}` composition preserved); zero visual changes for existing English call sites (contract C3)
- [x] T004 [P] Add the `locale` prop (default `"en"`) to ChapterHeader/ChapterFooter in relay-tutorial/components/tutorial/chapter-shell.tsx: all labels via `t(locale)`, chapter/part names via the T002 localized accessors, internal links locale-aware (breadcrumb + back-to-contents → `/vi` when locale is vi; prev/next hrefs prefixed via `localePath`); in vi locale, prev/next link cards MUST gate on `translatedIn`: a chapter published in English but not Vietnamese renders as a non-link card with the localized "available in English only" badge — never a dead `/vi` link (FR-009, analysis U1); forthcoming badge text localized

**Checkpoint**: `pnpm lint && pnpm build` pass; English pages render byte-identically *at this point* (default props). Note: after T008 adds the dormant `<LocaleHint />`, the enduring guarantee is the real contract — no reader-visible change, no address change (SC-003, analysis I1) — so do not byte-diff at T017

---

## Phase 3: User Story 1 - Switch the site language (Priority: P1) 🎯 MVP

**Goal**: EN/VI switcher in the header on every page; the `/vi` landing with fully Vietnamese chrome; cookie persistence with the no-redirect hint.

**Independent Test**: From any page, switch to Tiếng Việt → land on the counterpart page with 100% Vietnamese chrome; choice persists (cookie); `/` shows the hint on return; keyboard-operable (quickstart V3/V4).

### Implementation for User Story 1

- [x] T005 [US1] Create the language switcher in relay-tutorial/components/language-switcher.tsx per contract C2: `"use client"`; derives current locale via `localeFromPath(usePathname())`; renders the two locales (EN / VI) as links to `counterpartPath(pathname)` with the active one visually and semantically marked (e.g. `aria-current`); when the counterpart page does not exist (determinable from the manifest for chapter routes — a future en-only chapter), link to the target locale's landing instead of a dead mirror path (analysis U1); on activation writes cookie `locale=<value>; max-age=31536000; path=/; SameSite=Lax`; accessible labels from the dictionary; keyboard-operable; token classes only
- [x] T006 [US1] Make the site header locale-aware in relay-tutorial/components/site-header.tsx: derive locale from the pathname — the locale-dependent parts must live in a client boundary (`usePathname`; a server component rendered once from the root layout cannot know the route), kept as small as practical (analysis A1); brand link targets `/` or `/vi` per locale, add `<LanguageSwitcher />` beside `<ThemeToggle />`; verify no overlap at supported widths
- [x] T007 [P] [US1] Create the locale hint in relay-tutorial/components/locale-hint.tsx per research R3: `"use client"`; reads the `locale` cookie; on the en landing shows a dismissible inline hint "Đọc bằng tiếng Việt →" (link to `/vi`) when cookie=vi, and the mirror hint on the vi landing when cookie=en; dismiss stores nothing permanent (session-scoped state); NEVER redirects; token classes only
- [x] T008 [US1] Extract the landing UI into relay-tutorial/components/landing.tsx per research R6: move the current app/page.tsx rendering into `<Landing locale>`; all strings from `t(locale)`, titles via localized accessors; chapter links per locale — vi listing links 0.1 to `/vi/...` (it is in `translatedIn`) and shows 0.2–0.5 with Vietnamese titles + localized forthcoming badge; include `<LocaleHint />`; English output must remain visually identical to today
- [x] T009 [US1] Rewrite relay-tutorial/app/page.tsx as a thin wrapper: render `<Landing locale="en" />`, keep existing metadata (alternates arrive in US3); confirm rendered English landing is unchanged (SC-003)
- [x] T010 [US1] Create relay-tutorial/app/vi/layout.tsx per research R4: wraps children in `<div lang="vi">` — nothing else; fully static
- [x] T011 [US1] Create relay-tutorial/app/vi/page.tsx: `<Landing locale="vi" />` with Vietnamese `metadata` (title, description from the dictionary/pitch translation)
- [x] T012 [US1] Verify US1 per quickstart V3 (scripted parts) + C6 subset: `/vi` renders with zero English chrome strings (grep the rendered HTML for known en strings → 0); switcher present on `/`, `/vi`, en chapter; counterpart hrefs correct (`/` ↔ `/vi`); `pnpm lint && pnpm build` pass; fix gaps

**Checkpoint**: US1 fully functional — the MVP (Vietnamese chrome everywhere the site exists today, minus the chapter body)

---

## Phase 4: User Story 2 - Read chapter 0.1 in Vietnamese (Priority: P2)

**Goal**: The complete, faithful Vietnamese translation of chapter 0.1 at `/vi/part-0/chapter-01/from-app-to-infrastructure`.

**Independent Test**: The vi chapter reads end-to-end in natural Vietnamese with full structural parity (box counts, exercise, takeaways, checkpoint); the switcher maps chapter ↔ chapter both ways (quickstart V2 parity block + V5 review).

### Implementation for User Story 2

- [x] T013 [US2] Create relay-tutorial/app/vi/part-0/layout.tsx mirroring app/part-0/layout.tsx (the same `prose` container — one line of duplication accepted over premature abstraction)
- [x] T014 [US2] Author the Vietnamese chapter in relay-tutorial/app/vi/part-0/chapter-01/from-app-to-infrastructure/page.mdx per data-model E5 and contract C5: translate the ENGLISH chapter (its file is the source; docs/01 stays the source of facts — add no claims) with the same section arc; `<ChapterHeader id="0.1" locale="vi" />` / `<ChapterFooter id="0.1" locale="vi" />`; every box carries `locale="vi"`; box counts ≥ English per type (Why ≥2, SkipAhead ≥1, ForwardRef ≥2, Checkpoint exactly 1); the exercise preserves the for/who/that/unlike template slots in the translated Relay worked example (FR-007); established technical terms stay English (WebSocket, API, SDK; idempotency introduced with a Vietnamese gloss); natural Vietnamese prose (first-person plural equivalent: "chúng ta"), NOT literal machine-translation phrasing; Vietnamese `metadata` title "Từ ứng dụng đến hạ tầng — Building Relay" + description
- [x] T015 [US2] Verify US2 scripted parity per quickstart V2: box-count comparison en vs vi (vi ≥ en per type, Checkpoint =1 both); switcher on each chapter page links to the other (`href` check both directions, SC-004); `pnpm build` compiles the vi chapter route; flag the chapter for Dong's V5 quality review in the handoff

**Checkpoint**: US1 AND US2 — the Vietnamese reading path is complete

---

## Phase 5: User Story 3 - Coherent bilingual structure (Priority: P3)

**Goal**: hreflang counterpart metadata everywhere; proof that English pages are untouched and untranslated content is gated.

**Independent Test**: All four pages emit hreflang en/vi pairs; en pages carry no `lang="vi"`; pre-existing English URLs render unchanged (quickstart V2 regression block).

### Implementation for User Story 3

- [x] T016 [US3] Add counterpart metadata per contract C4: `metadata.alternates` (canonical + `languages: { en, vi }`) on relay-tutorial/app/page.tsx, app/vi/page.tsx, the EN chapter page.mdx (metadata export edit ONLY — body untouched), and the VI chapter page.mdx; verify each of the four rendered pages emits both hreflang links (SC-006)
- [x] T017 [US3] Run the full English-regression + gating verification per quickstart V2: en landing and en chapter render with unchanged body markers and zero `lang="vi"` / zero Vietnamese chrome; `div lang="vi"` present on both vi pages; vi landing renders 0.2–0.5 as non-links with Vietnamese forthcoming badges (translatedIn gating, FR-009); fix any regression found

**Checkpoint**: All three user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation and handoff

- [x] T018 Run the complete quickstart V1–V6 for specs/004-i18n-vietnamese/quickstart.md: route table (V1), full scripted block (V2), manual switching/chrome sweep incl. keyboard (V3), persistence semantics — cookie set only on explicit switch, hint on landings, no redirects, private-window vi link (V4), theme/favicon interplay on vi pages (V6); record results; V5 (translation quality) is Dong's — include the review request prominently in the handoff
- [x] T019 Handoff (NO commits — standing instruction): report ready-to-commit files for relay-tutorial (new: lib/i18n.ts, components/language-switcher.tsx, components/locale-hint.tsx, components/landing.tsx, app/vi/** ; modified: lib/tutorial.ts, components/site-header.tsx, components/tutorial/boxes.tsx, components/tutorial/chapter-shell.tsx, app/page.tsx, en chapter page.mdx metadata) with a suggested commit message; request Dong's V5 Vietnamese read-through before committing; note parent-repo follow-ups (spec artifacts + submodule pin)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: empty
- **Foundational (Phase 2)**: T001 first (T002 parallel to it — different file, no import of i18n needed for data fields; T003/T004 import T001's `t()` so they follow it; T003 ∥ T004)
- **US1 (Phase 3)**: T005 → T006 (header imports switcher); T007 [P] anytime after T001; T008 needs T001/T002/T007; T009 after T008; T010 independent after nothing; T011 after T008 + T010; T012 last
- **US2 (Phase 4)**: T013 independent; T014 needs Phase 2 (locale props) + T010 (vi layout) + T013; T015 after T014
- **US3 (Phase 5)**: T016 needs the four pages to exist (after T009/T011/T014); T017 after T016
- **Polish (Phase 6)**: T018 after all; T019 last

### User Story Dependencies

- **US1 (P1)**: Foundational only — the MVP
- **US2 (P2)**: Foundational + T010 from US1 (the `div lang="vi"` layout); otherwise independent of US1's landing/switcher work
- **US3 (P3)**: needs US1/US2's pages to exist (metadata attaches to them)

### Parallel Opportunities

- **T002 ∥ T001**, then **T003 ∥ T004** (four foundational files, two waves)
- **T007 (locale-hint)** parallel with T005/T006
- **US2's translation authoring (T014)** can start as soon as Phase 2 + T010/T013 exist — in parallel with US1's landing work (T008–T011); different files entirely
- The translation (T014) is the wall-clock-dominant task; starting it early is the biggest scheduling win

## Parallel Example

```bash
# Wave 1: T001 ∥ T002
# Wave 2: T003 ∥ T004
# Then two tracks:
#   Track A (US1): T005 → T006, T007 ∥, T008 → T009, T010, T011 → T012
#   Track B (US2): T010(shared) → T013 → T014 → T015
# Join: T016 → T017 → T018 → T019
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 2 (T001–T004): plumbing, English rendering provably unchanged
2. Phase 3 (T005–T012): switcher + Vietnamese chrome + `/vi` landing
3. **STOP and VALIDATE**: a Vietnamese reader can inhabit the site in Vietnamese (minus the chapter body) — demonstrable MVP

### Incremental Delivery

1. US1 → bilingual site shell live
2. US2 → chapter 0.1 readable in Vietnamese; switcher maps counterparts
3. US3 → hreflang + regression proof
4. Polish → full quickstart; hand the Vietnamese chapter to Dong for the V5 read-through; handoff for commits

---

## Notes

- The wall-clock-dominant and quality-dominant task is T014 (the translation). The bar is FR-007's: natural Vietnamese carrying the argument, established terms in English — nothing that "reads as machine translation" (quickstart V5). Dong is the named reviewer; the handoff must request that review explicitly
- The single edit to any pre-existing English file's rendered output is T016's hreflang metadata (head links only). If any task finds itself wanting to touch en body content, it is wrong — stop and re-read contract C1
- Cookie has exactly one writer (the switcher, T005) and one reader (the hint, T007) — keep it that way (data-model E4)
- NO git commit / git push anywhere — Dong commits personally

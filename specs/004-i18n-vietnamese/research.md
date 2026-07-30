# Research: Internationalization with Vietnamese Chapter 0.1

**Feature**: `specs/004-i18n-vietnamese` · **Date**: 2026-07-29

Grounded in the existing codebase (features 001–003), the bundled Next.js 16.2.12
docs, and the constitution's boring-by-design principle.

## R1 — Routing: a manual `/vi` mirror, no i18n framework

- **Decision**: Vietnamese lives under a literal **`/vi/...`** route subtree that
  mirrors the English structure (`/vi` landing, `/vi/part-0/chapter-01/
  from-app-to-infrastructure` chapter). English routes are **not touched, not moved,
  not prefixed** — no middleware, no locale negotiation, no i18n library.
- **Rationale**: The spec's hardest constraint (FR-005/SC-003: every existing English
  URL unchanged) is satisfied trivially by not touching English routes. With exactly
  2 locales, ~4 pages, and ~20 chrome strings, an i18n framework is machinery without
  a problem (constitution VII). File-based MDX stays the chapter contract: a
  translation is just a second `page.mdx` under `/vi` — the same "add a chapter"
  workflow feature 002 promised.
- **Alternatives considered**: `next-intl` (the standard choice at scale — but it
  wants an `app/[locale]/` restructure that moves the English chapter files feature
  002 contracted, plus middleware for a site with two locales); Next's Pages-router
  i18n config (App Router doesn't support it); `[locale]` dynamic segment with
  `generateStaticParams` (same restructuring cost, and MDX-per-route stops being
  plain files).

## R2 — Locale model and chrome strings: one dictionary module

- **Decision**: `lib/i18n.ts` exports `type Locale = "en" | "vi"`, a `dictionaries`
  object holding every reader-facing chrome string (landing pitch/labels, header,
  chapter-shell strings, box labels, forthcoming/available-in-English badges) in both
  locales, a `t(locale)` accessor, and `localePath(locale, path)` /
  `counterpartPath(path)` helpers (pure prefix add/strip). The series manifest
  (`lib/tutorial.ts`) gains optional `titleVi` and `readerProducesVi` per chapter and
  `titleVi` per part; accessors fall back to English when absent (FR-009's explicit
  marking uses the badge, never silent English body content).
- **Rationale**: One string source per locale (constitution IV in spirit; spec's
  "Localized string set" entity). Extending the manifest keeps series data in the
  single place feature 002 established, and the English-fallback-plus-badge rule
  makes untranslated future chapters safe by construction.
- **Alternatives considered**: per-component inline ternaries (scatters the
  vocabulary); JSON message catalogs with ICU formatting (no plurals/interpolation
  needs exist yet); duplicating the manifest per locale (two sources of truth for
  one series — rejected outright).

## R3 — Language switcher and persistence: header control + cookie + root hint

- **Decision**: `components/language-switcher.tsx` (client) sits in the site header
  next to the theme toggle: two options (EN / VI, Tiếng Việt labeled), active locale
  discernible, rendered as links to `counterpartPath(usePathname())` so switching
  lands on the same logical page (FR-003/SC-004). Choosing a language sets a
  `locale` cookie (1-year, SameSite=Lax). Persistence semantics:
  1. **In-session**: all internal links on `/vi` pages are locale-aware (brand link
     → `/vi`, chapter links → `/vi/...`), so navigation naturally stays in-language.
  2. **Cross-session**: the English landing (`/`) shows a small dismissible inline
     hint — "Đọc bằng tiếng Việt →" — when the cookie says `vi` (and the mirror
     hint on `/vi` when it says `en`). **No automatic redirect anywhere.**
- **Rationale**: SC-003/US3-AC1 ("English URLs render as before, no redirect") and
  SC-005 ("preference survives a restart") are in genuine tension — an auto-redirect
  honoring the cookie would break the former. The hint resolves it: content and
  addresses are untouched, yet a returning reader recovers their language in one
  click from the entry point. The spec's shared-link edge case holds automatically:
  a `/vi` address renders Vietnamese and visiting alone never writes the cookie —
  only an explicit switch does.
- **Alternatives considered**: middleware auto-redirect from `/` based on cookie
  (violates SC-003 as written); browser-locale detection (spec assumption explicitly
  rejects it); localStorage instead of a cookie (invisible to any future server
  logic and no expiry semantics; cookie is the conventional locale store).

## R4 — Language declaration and counterpart discovery

- **Decision**: The root layout keeps `<html lang="en">`. `app/vi/layout.tsx` wraps
  its subtree in `<div lang="vi">` — a valid, fully static language declaration for
  all Vietnamese content, no JavaScript involved. Every page in a language pair
  exports `metadata.alternates`: `canonical` plus `languages: { en: <en path>, vi:
  <vi path> }`, which Next renders as hreflang link tags (SC-006/FR-008). Vietnamese
  pages also set their own `<title>`/description in Vietnamese.
- **Rationale**: `lang` is valid on any element, so scoping it to the `/vi` subtree
  sidesteps the App Router limitation that only the root layout owns `<html>` —
  without client-side attribute mutation. hreflang alternates are the standard
  counterpart-relationship mechanism search engines and tools read.
- **Alternatives considered**: mutating `document.documentElement.lang` from a
  client effect (works but JS-dependent and flickers in translation tools); moving
  `<html>` into per-locale layouts (the `[locale]` restructure R1 rejected).

## R5 — The Vietnamese chapter: a parallel MDX file with locale-aware shell

- **Decision**: `app/vi/part-0/chapter-01/from-app-to-infrastructure/page.mdx` — the
  English slug is kept (parallel structure, so counterpart mapping is a pure prefix
  operation and the feature-002 slug rule stays single). The translation is authored
  from the English chapter as source (faithful section arc, ≥ same box counts,
  exercise structure preserved per FR-006/007), with established technical terms kept
  in English (WebSocket, API, idempotency introduced with Vietnamese gloss).
  Components grow a `locale` prop with default `"en"`: `ChapterHeader`/`ChapterFooter
  ({ id, locale })` pull `titleVi` etc. from the manifest and localize their labels;
  boxes (`Why`, `SkipAhead`, `Checkpoint`, `ForwardRef`, …) localize their **labels**
  via the same prop (`<Why locale="vi" …>`). `app/vi/part-0/layout.tsx` reuses the
  prose container.
- **Rationale**: Explicit props over context because these are server components and
  the repo's stated style is visible mechanics (feature 002 R4 precedent). Default
  `"en"` keeps every existing English file untouched (SC-003). Keeping the English
  slug under `/vi` trades URL purism for a switcher that can never mis-map — and the
  spec only requires the address be "recognizably Vietnamese" (the `/vi` prefix) and
  structurally parallel.
- **Alternatives considered**: translated slugs (`/vi/phan-0/chuong-01/...` — reads
  better in Vietnamese but requires a slug-mapping table and breaks the pure prefix
  counterpart rule; revisit if Vietnamese SEO becomes a goal); React context for
  locale (unavailable in server components without client boundaries).

## R6 — Landing pages: shared component, two thin routes

- **Decision**: Extract the landing UI into `components/landing.tsx` taking a
  `locale` prop (rendering from the manifest + dictionary); `app/page.tsx` and
  `app/vi/page.tsx` become thin wrappers passing `"en"` / `"vi"` and exporting their
  own metadata (incl. alternates). The `/vi` landing lists chapters with Vietnamese
  titles; 0.1 links to the `/vi` chapter; 0.2–0.5 show the Vietnamese forthcoming
  badge.
- **Rationale**: One landing implementation, two locales (single source of truth);
  metadata stays per-route where Next wants it.
- **Alternatives considered**: duplicating page.tsx into /vi (immediate drift risk);
  making `/` itself locale-dynamic (breaks SC-003's "renders exactly as before").

## R7 — Verification approach

- **Decision**: Scripted: English-URL regression (fetch `/` and the en chapter,
  assert unchanged markers + `lang="en"` only); parallel-structure comparison
  (box-type counts en vs vi via grep); hreflang presence on all four pages;
  `div lang="vi"` present on vi pages; switcher present and pointing at counterpart
  paths; `pnpm lint && pnpm build`. Manual: translation quality read-through (Dong is
  the reviewing authority per spec), switcher keyboard pass, cookie persistence and
  root-hint behavior.
- **Rationale**: Matches the feature-002/003 verification style; the one thing
  scripts cannot judge — Vietnamese prose quality — is explicitly assigned to the
  human who can.

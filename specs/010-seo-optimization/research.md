# Research: SEO Optimization for the Existing Pages

**Feature**: `specs/010-seo-optimization` · **Date**: 2026-07-30

Pre-spec audit: no sitemap, no robots policy, zero social-preview metadata,
`<html lang="en">` global (Vietnamese pages mislabeled at page level). Strengths to
preserve: unique per-page titles/descriptions, self-canonicals, bidirectional
hreflang, metadataBase from `NEXT_PUBLIC_SITE_URL`, fully static output.

Framework facts verified in `node_modules/next/dist/docs/` (16.2.12):
- Metadata `openGraph` fields inherit from a layout **wholesale** when a page sets
  none — the inherited `og:title` is the layout's, NOT the page's title
  (generate-metadata.md L1416). So layout-level OG cannot produce per-page titles.
- Multiple root layouts via route groups are the sanctioned pattern for per-locale
  `<html lang>`; caveats: full page reload when navigating across groups, no
  conflicting paths, home route must live inside a group (route-groups.md L28–32).
- `opengraph-image` file conventions apply per segment and cascade to children.

## R1 — Per-locale `<html lang>`: two root layouts via route groups

- **Decision**: Restructure `app/` into two route groups with their own root
  layouts: `app/(en)/layout.tsx` (`<html lang="en">`) holding `page.tsx`,
  `part-0/`, `docs/`; and `app/(vi)/layout.tsx` (`<html lang="vi">`) holding the
  existing `vi/` segment. URLs are unchanged (groups don't affect paths). Shared
  chrome (fonts, ThemeProvider, SiteHeader, globals.css, metadataBase) extracted
  into one shared `RootShell` component + shared metadata constants used by both
  root layouts. The old `app/vi/layout.tsx` `<div lang="vi">` wrapper is retired —
  the html element now carries the truth; the reference-doc pages' `lang="en"`
  article wrapper stays (spec edge case).
- **Rationale**: FR-003. Layouts cannot know the pathname, and hoisting can't set
  html attributes — route groups are the framework's answer. Locale switches
  become full page loads (documented caveat) — acceptable for a rare action.
- **Alternatives considered**: client-side `document.documentElement.lang`
  mutation (initial HTML still wrong — crawler-hostile); keeping `div lang` only
  (fails FR-003's page-level requirement).
- **Consequences**: all ten chapter files MOVE (`app/part-0/…` → `app/(en)/part-0/…`,
  `app/vi/…` → `app/(vi)/vi/…`) with byte-identical content — battery counts prove
  it (baseline paths normalized, count columns identical). `app/icon.jpg` stays at
  the root segment; verify the icon convention still resolves without a root
  layout (fallback: place it in both groups).

## R2 — Sitemap and robots: manifest-derived metadata routes

- **Decision**: `app/sitemap.ts` (`MetadataRoute.Sitemap`) enumerating: both
  landings, every published chapter's path ×2 locales (vi only when
  `translatedIn` includes it — the manifest gate), and the six doc-registry slugs
  ×2 — 24 URLs today — each entry carrying its language alternates; absolute URLs
  from `NEXT_PUBLIC_SITE_URL`. `app/robots.ts` allowing all user agents and
  pointing at the sitemap.
- **Rationale**: FR-001/002; deriving from the manifest + registry keeps
  publishing manifest-only (SC-001) and honors constitution IV (no second list of
  pages).
- **Alternatives considered**: static XML files (manual drift on every publish);
  crawling-based generation (machinery).

## R3 — Social preview metadata: metadata API where files are editable, shell-hoisted tags for chapters

- **Decision**: Two mechanisms, one per file class:
  1. **Landings (2 files) and doc routes (2 route files → 12 pages)**: extend
     their `metadata`/`generateMetadata` with `openGraph` (title, description,
     url, type, locale, siteName) — these files are not battery-protected.
  2. **Chapter pages (10 battery-frozen files)**: zero edits. IMPLEMENTATION
     FINDING (supersedes the planning-time assumption): once a layout-level
     `openGraph` object exists, the metadata API fills `og:title`,
     `og:description`, `twitter:title`, and `twitter:description` from each
     page's OWN title/description — exactly the per-page values wanted. So the
     shell (`ChapterHeader`) emits only what the API cannot know for these
     files: `og:url`, `og:type=article`, `og:locale` — as hoisted `<meta>`
     elements (React 19 document metadata). No title/description tags from the
     shell, or they duplicate the API's.
  Shared site-wide bits set once in both root layouts' metadata: `twitter.card =
  summary_large_image`, `openGraph.siteName`. The shell must NOT emit `og:image`
  (R4's file convention already injects it everywhere) — no duplicate tags.
- **Rationale**: FR-005 + FR-009. The verified inheritance rule makes layout-level
  OG wrong for per-page titles, and editing chapter metadata blocks would change
  battery word counts (metadata lines are counted). The shell is already the
  manifest-driven chrome channel (features 002–009); this extends it.
- **Alternatives considered**: editing all ten chapter metadata blocks +
  re-baselining the battery (breaks SC-007 as written; erodes the freeze
  discipline); no per-page OG relying on unfurler `<title>` fallback (fails
  validator-based SC-004).

## R4 — The series preview image: generated at build, no binary asset

- **Decision**: `app/opengraph-image.tsx` using `ImageResponse` from `next/og`
  (built into Next — zero new dependencies): 1200×630, Violet Bloom palette,
  series title + tagline; plus the exported `alt`/`size`/`contentType`. The file
  convention injects `og:image`/`twitter:image` with absolute URLs on every route.
- **Rationale**: FR-006; code-generated means no binary in git, theme-consistent
  colors, and the convention handles the tags (nothing else may emit og:image).
- **Alternatives considered**: hand-made static PNG (binary asset, design tooling
  outside the repo); per-page dynamic images (explicitly out of scope).

## R5 — Structured data: JSON-LD from the shell and the landings

- **Decision**: `ChapterHeader` also renders one
  `<script type="application/ld+json">` per chapter — `TechArticle` with
  `headline` (locale title), `description` (reader-produces), `inLanguage`,
  `isPartOf` the series (`name: "Building Relay"`), `position` (chapter id), and
  `url` — all from the manifest. Landings render a `WebSite` record naming the
  site and both language URLs (2 editable files, inline). Reference-doc pages get
  none (spec allows "if any"; their authorship/dates belong to the documents).
  JSON-LD is consumed from anywhere in the DOM; no hoisting subtleties.
- **Rationale**: FR-007 with zero chapter edits; the manifest is already the
  single source for every field used.
- **Alternatives considered**: per-page schema in MDX (battery); `CreativeWork`
  only (TechArticle is the accurate, richer type).

## R6 — Verification: scripted assertions + deploy-time validators

- **Decision**: Scripted (local): sitemap contains exactly the expected 24 URLs
  and nothing else; robots serves and names the sitemap; `<html lang>` correct on
  all 24 pages; `og:title` on every page equals that page's own title (spot-check
  matrix incl. vi chapters); `og:locale` correct; exactly one `og:image` per
  page; every JSON-LD block parses and has the expected `@type` (10 TechArticle +
  2 WebSite); canonicals/hreflang regression 24/24; **battery counts identical
  after path normalization** (`app/(en)/`→`app/`, `app/(vi)/vi/`→`app/vi/`).
  Deploy-time/manual: platform link-preview validators and the rich-results test
  need a public URL — run against the deployed site (Dong); a Lighthouse SEO run
  is environment-dependent (needs Chrome — via Docker if convenient, else against
  the deployment).
- **Rationale**: SC-001..007 split by what can be proven locally vs what
  inherently requires the public deployment.

## R7 — What explicitly does not change

- No new dependencies (next/og is built in). No chapter prose or metadata edits.
  No visible-content changes on any page (meta/JSON-LD/head only — the retired
  `div lang` wrapper has no visual effect). The 009 reference-doc contract
  (mirrors, drift, anchors) is untouched; doc pages only gain OG fields in their
  existing `generateMetadata`.

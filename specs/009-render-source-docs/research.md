# Research: Chapter 0 Improvement — Render the Source Documents

**Feature**: `specs/009-render-source-docs` · **Date**: 2026-07-30

Survey of the six documents (docs/01–06): 232–924 lines each, ~3,570 lines total;
~590 pipe-table lines (409 in the SRS alone); 6 mermaid diagrams (all in the SAD);
all raw HTML (`<br/>` ×33) occurs **inside** mermaid fences only; prose contains
JSX-hostile sequences (`{channel_id: seq}`, `conn:{env}:{user}`, `<` comparisons).

## R1 — Content location: a committed mirror inside the submodule

- **Decision**: Mirror the six files verbatim into `relay-tutorial/content/docs/`
  (same filenames), committed to the submodule. A sync script
  (`scripts/sync-docs.sh`) copies from the parent repo's `docs/` and fails if the
  parent is absent (a sync without its source is an error — only the drift check
  degrades gracefully);
  a drift check (`scripts/check-docs-drift.sh`, plus `pnpm check:docs`) diffs each
  mirrored file against its parent source and fails loudly on divergence, skipping
  with a warning when the parent is absent (standalone clones, CI).
- **Rationale**: relay-tutorial is an independent repo deployed standalone — it
  cannot read `../docs` at build time in every environment. FR-009's refresh step
  = run the sync script and commit; SC-006's detection = the drift check. The
  parent `docs/` remains canonical (constitution IV concern addressed head-on:
  the mirror is a build input, never edited by hand — the scripts enforce it).
- **Alternatives considered**: reading `../docs` directly at build (breaks
  standalone builds); git submodule/subtree of docs into the app (heavy machinery
  for six files); fetching at runtime (violates the static-site property).

## R2 — Rendering path: a markdown renderer on raw strings, NOT MDX

- **Decision**: A dynamic route `app/docs/[slug]/page.tsx` (mirrored at
  `app/vi/docs/[slug]/page.tsx`) with `generateStaticParams` over the six-entry
  registry (R5); the page reads the mirrored `.md` via `fs` at build time and
  renders it with **react-markdown + remark-gfm** in a server component, styled by
  the existing typography/token system. Custom component overrides: tables wrapped
  in an `overflow-x-auto` container; fenced `mermaid` blocks routed to the diagram
  component (R3); headings get stable ids (R4).
- **Rationale**: The chapters' MDX pipeline is unusable here twice over — MDX
  parses `{…}`/`<…>` as JSX (the docs contain both in prose, e.g. ADR-03's
  `{channel_id: seq}` → build error), and the chapter pipeline deliberately has no
  GFM while the docs are ~590 lines of pipe tables. A renderer over raw strings
  keeps the documents byte-verbatim (FR-005) and isolates GFM to reference pages —
  the chapters' no-GFM rule stays intact.
- **Alternatives considered**: converting docs to `.mdx` pages (verbatim fidelity
  lost the moment content must be escaped; fragile forever); enabling remark-gfm
  globally in the MDX pipeline (touches every chapter's pipeline for zero chapter
  benefit); an iframe/static-HTML export (loses theme/chrome integration).

## R3 — Diagrams: client-side mermaid, theme-aware, loaded only where needed

- **Decision**: A `MermaidDiagram` client component: dynamic `import("mermaid")`,
  render on mount, `securityLevel: "antiscript"` (the docs' diagram labels use
  `<br/>` line breaks, which "strict" would encode into visible literal text;
  antiscript keeps them working while still stripping script content — the input
  is our own repo's docs); theme follows next-themes'
  `resolvedTheme` (mermaid theme `"default"` for light, `"dark"` for dark) and
  re-renders on theme change. Until hydration it shows the diagram source in a
  normal `<pre>` fence (honest fallback, also the no-JS story). Only reference
  pages containing mermaid fences load the library.
- **Rationale**: FR-004's both-themes legibility needs runtime theme awareness;
  build-time SVG (rehype-mermaid) requires a headless browser in the build and
  bakes one theme in. The library is heavy, so it loads lazily and only on the one
  page that has diagrams (the SAD).
- **Alternatives considered**: rehype-mermaid/Playwright at build (heavy CI dep,
  single-theme output); pre-rendering two SVG sets per diagram (build tooling +
  drift risk with doc edits); ASCII-art fallback (fails "must display correctly").

## R4 — Long-document navigation: heading ids + a top outline

- **Decision**: Stable, slugified ids on every rendered `h2`/`h3`; a "Contents"
  outline at the top of each reference page listing the document's top-level
  sections as anchor links. One click from page top = any top-level section
  (SC-005's ≤2 actions met with margin).
- **Rationale**: FR-006; the SRS/SAD are 780–924 lines — citations like "SAD §9"
  must be one jump away.
- **Alternatives considered**: sticky sidebar TOC (nicer, heavier; the outline
  block reuses existing prose styling — an enhancement candidate for later);
  no TOC with browser-find (fails FR-006 on mobile).

## R5 — The registry and the chapter affordance: manifest-driven chrome

- **Decision**: New `lib/docs.ts`: six entries `{slug, file, title, sourceDoc}` —
  slugs `product-vision`, `personas`, `journey-map`, `srs`, `sad`,
  `adr-deep-dives`; `sourceDoc` holds the exact path string the series manifest
  already records (`docs/04-srs.md`, …), which is the join key. `ChapterHeader`
  splits the manifest's comma-separated `sourceDoc`, resolves each through the
  registry, and renders a "Source documents" line of links under the existing
  reader-produces line — labels from the i18n dictionary (`Source:` /
  `Tài liệu gốc:`), with an "(English)" hint on the Vietnamese side (FR-008).
  Zero chapter `page.mdx` files change (FR-007); unresolvable `sourceDoc` values
  render as plain text, never a dead link (the 002 rule).
- **Rationale**: The manifest already owns the chapter→doc mapping (spec Key
  Entities); the shell already renders exclusively from the manifest — this is the
  same pattern that made publishing manifest-only in features 002–008.
- **Alternatives considered**: per-chapter links written into MDX (touches all ten
  battery-verified files — exactly what FR-007 forbids); footer placement (the
  header is where the reader is told what the chapter is based on — `sourceDoc`
  already displays nothing today, this is its debut).

## R6 — Locale mirror: full `/vi/docs/[slug]` counterpart pages

- **Decision**: Reference pages exist in both locale trees with identical English
  article content: `/docs/[slug]` (en chrome) and `/vi/docs/[slug]` (vi chrome,
  the article wrapped in `lang="en"` inside the vi layout's `lang="vi"`, with a
  one-line note "Tài liệu gốc — được giữ nguyên tiếng Anh"). hreflang pairs both
  directions; the language switcher maps them mechanically via the existing
  `counterpartPath`.
- **Rationale**: The 004 i18n contract gives every page a counterpart and a
  working switcher; a single en-only route would break the switcher and hreflang
  invariants on 12 surfaces. Content stays English per the spec assumption — only
  chrome localizes.
- **Alternatives considered**: en-only routes linked cross-locale (breaks the 004
  invariants; vi readers lose their chrome); translating the documents (out of
  scope per spec).

## R7 — Verification: extend the settled battery with doc-page checks

- **Decision**: Scripted (quickstart V2): drift check green; 12 routes in the
  build; per-page greps prove verbatim presence of sentinel content (e.g.,
  `FR-TEN-05` in srs, `last_sequence` in sad, D1 row text); `<table` present on
  table-bearing pages; every published chapter page (×2 locales) contains hrefs to
  its mapped doc route(s); hreflang ≥2 on all 12 pages; **battery-freeze check**:
  word/box/fence counts of all ten existing chapter files identical to their
  recorded values (SC-004). Manual (V3): six diagrams in both themes; SRS tables
  at phone width; TOC jumps; chapter→doc→back walks in both locales.
- **Rationale**: Diagrams render client-side, so their visual correctness is a
  browser check; everything else scripts.

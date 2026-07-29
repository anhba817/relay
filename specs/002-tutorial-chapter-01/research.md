# Research: Tutorial Chapter 0.1 — From App to Infrastructure

**Feature**: `specs/002-tutorial-chapter-01` · **Date**: 2026-07-29

Verified against the Next.js 16.2.12 docs bundled in the repo
(`node_modules/next/dist/docs`, per relay-tutorial's AGENTS.md instruction), the npm
registry, and the existing relay-tutorial codebase.

## R1 — Chapter content format: MDX via @next/mdx

- **Decision**: Author chapters as **MDX pages** using `@next/mdx` (matches Next
  16.2.12) with file-based routing — a chapter is a `page.mdx` under `app/`.
  Dependencies: `@next/mdx`, `@mdx-js/loader`, `@mdx-js/react`, `@types/mdx` (dev).
  A root `mdx-components.tsx` is **required** for App Router (v16 docs, MDX guide).
  `next.config.ts` gains `pageExtensions` + `withMDX` wrapping.
- **Rationale**: Chapters are prose with embedded interactive conventions
  (`WHY`/`CHECKPOINT` boxes). MDX keeps authoring as markdown (docs/07 §2's chosen
  medium) while making the box conventions real components. File-as-route means zero
  content-loading machinery — the boring choice (constitution VII).
- **Alternatives considered**: plain `.md` + `react-markdown` at runtime (loses
  compile-time components, adds a renderer dependency for no gain); Contentlayer
  (unmaintained); a full docs framework like Nextra/Fumadocs (heavy opinionated shells
  that would fight the Violet Bloom theme and hide the mechanics a tutorial repo
  should keep visible).

## R2 — Routes and entry point

- **Decision**: The app's home page (`app/page.tsx`) becomes the **series landing /
  table of contents**. Chapter URLs follow the canonical pattern
  **`/part-<n>/chapter-<nn>/<slug>`** (spec clarification 2026-07-29): chapter 0.1
  lives at **`/part-0/chapter-01/from-app-to-infrastructure`**
  (`app/part-0/chapter-01/from-app-to-infrastructure/page.mdx`). The slug is the
  kebab-case of the title's main clause (subtitle dropped). Chapter pages export
  Next `metadata` from the MDX file.
- **Rationale**: The app *is* the tutorial site (feature-002 user decision); making
  `/` the ToC satisfies SC-005 (chapter reachable in ≤2 steps: land → click chapter).
  The numeric `part/chapter` segments sort naturally and match docs/07's numbering,
  while the trailing slug makes the address self-describing (user requirement).
- **Alternatives considered**: a `/relay-chat-service-tutorial/...` site prefix
  (proposed then withdrawn by the user in the same clarification session); numeric
  segments without a slug (originally planned — superseded); title-only slugs
  (lose the stable numeric ordering docs/07 refers to).

## R3 — Series structure: a typed manifest as single source of truth

- **Decision**: `lib/tutorial.ts` exports a typed series manifest: parts 0–8 with
  titles (from docs/07 §3), and for Part 0 all five chapters with `id`, `path` (the
  full route; its final segment is the slug), `title`, `status` (`published` |
  `forthcoming`), `readerProduces`, `sourceDoc`, and `readerMinutes`.
  Helper functions: `getChapter(id)`, `nextChapter(id)`, `prevChapter(id)`. The
  landing ToC and every chapter's header/footer render exclusively from this manifest.
- **Rationale**: Next/previous links, "forthcoming" markers, and series identity must
  never be hand-duplicated per chapter (FR-007, SC-006's zero-per-chapter-work
  companion). One manifest, many consumers — the single-source-of-truth discipline in
  miniature.
- **Alternatives considered**: filesystem introspection of `app/part-*` (can't
  represent forthcoming chapters that have no files yet); per-chapter frontmatter as
  the source (scatters series data across files).

## R4 — Box conventions: explicit components imported in MDX

- **Decision**: `components/tutorial/boxes.tsx` exports `<Why>`, `<Trap>`,
  `<Checkpoint>`, `<SkipAhead>`, `<Revised>`, and `<ForwardRef part="...">` —
  callout-style blocks styled entirely with Violet Bloom tokens (e.g. `accent` family
  for WHY, `destructive` tints for TRAP, `primary` for CHECKPOINT, `muted` for SKIP
  AHEAD). Chapters import them explicitly at the top of the MDX file.
  `mdx-components.tsx` handles only base HTML element styling.
- **Rationale**: Explicit imports keep each chapter file self-describing (a tutorial
  repo should show its mechanics), and token-only styling satisfies SC-006 (both
  modes, zero per-chapter styling). Implements FR-004/FR-008.
- **Alternatives considered**: injecting the boxes globally via `useMDXComponents`
  (magic — components appear from nowhere in a repo meant to be read); directive
  syntax via remark plugins (`:::why`) (extra plugin machinery, non-standard syntax).

## R5 — Long-form typography: @tailwindcss/typography

- **Decision**: Add `@tailwindcss/typography` (0.5.20, latest — verified) via Tailwind
  v4's CSS `@plugin` directive in `globals.css`, and map the `prose` palette to the
  Violet Bloom variables (body/foreground, links/primary, code/accent-foreground,
  `.dark` handled by the same tokens). Chapter body renders inside a
  width-constrained `prose` container in the chapter shell.
- **Rationale**: 2,000–4,000 words of prose (SC-001) needs real typographic defaults —
  headings scale, list rhythm, blockquotes, code. The plugin is the boring standard;
  mapping it to theme tokens keeps SC-006 (both modes) automatic. The theme's serif
  (Lora) is available for chapter epigraphs via existing `font-serif` tokens.
- **Alternatives considered**: hand-styling every element in `mdx-components.tsx`
  (reinvents the plugin, endless drift); no typographic treatment (fails the reading
  experience the shell exists to provide).

## R6 — Chapter shell: header/footer components fed by the manifest

- **Decision**: `components/tutorial/chapter-shell.tsx` exports `<ChapterHeader
  id="0.1" />` (series identity: part, chapter number, title, reading-time note,
  breadcrumb to ToC) and `<ChapterFooter id="0.1" />` (next/previous from the
  manifest, forthcoming chapters rendered as non-links with a "forthcoming" badge).
  Each chapter MDX file includes both, passing only its id.
- **Rationale**: Satisfies FR-007/US3 with one line per chapter. Data flows from the
  R3 manifest, so adding chapter 0.2 later automatically fixes 0.1's footer.
- **Alternatives considered**: per-chapter `layout.tsx` files (boilerplate per
  chapter); a route-group layout deriving the chapter from `usePathname` (client
  component for what is static content; implicit where explicit is clearer).

## R7 — Chapter content derivation and verification

- **Decision**: The chapter prose is authored at implement time with
  `docs/01-product-vision.md` as the sole factual source (SC-002), structured as:
  (1) the naïve chat-app premise; (2) the underestimation table walked as a
  derivation (docs/01 §2); (3) the alternatives and the gap (§2); (4) finding the
  wedge (§4); (5) writing the positioning statement — worked example (§1); (6)
  non-goals as commitments (§6); (7) exercise; (8) takeaways + CHECKPOINT.
  Format compliance is checked by script: word count via `wc -w` on the MDX body
  (target 2,000–4,000), box presence via `grep -c` per component (SC-004).
- **Rationale**: The section arc mirrors docs/01's own §2→§3→§4→§6 argument, which is
  what "watch the reasoning unfold" (FR-002) requires. Scripted checks make SC-001/
  SC-004 verifiable rather than asserted.
- **Alternatives considered**: reproducing docs/01 verbatim (fails FR-002 — the
  chapter derives, the vision document concludes); inventing new market claims
  (violates SC-002).

## R8 — Landing page replaces the feature-001 placeholder

- **Decision**: Rewrite `app/page.tsx` as the series landing: series title ("Building
  Relay"), the one-sentence pitch (docs/07 §1.1), the nine-part arc as a compact list
  (parts 1–8 collapsed/forthcoming), Part 0 expanded with its five chapters — 0.1
  linked, 0.2–0.5 marked forthcoming. Rendered from the R3 manifest. Violet Bloom
  styling; both modes.
- **Rationale**: The feature-001 placeholder page has served its purpose (it proved
  the theme); the spec (FR-007, SC-005) makes `/` the tutorial entry point. Feature
  002's spec explicitly retires 001's scaffold-purity boundary.
- **Alternatives considered**: keeping the placeholder and adding `/tutorial` (two
  competing home pages; extra navigation step against SC-005).

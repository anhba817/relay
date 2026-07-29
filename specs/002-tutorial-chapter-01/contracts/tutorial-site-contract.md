# Contract: Tutorial Site — Routes, Manifest, and Chapter Conventions

**Feature**: `specs/002-tutorial-chapter-01` · **Date**: 2026-07-29

What readers and future chapters may rely on. Breaking these breaks the series.

## C1 — Routes

| Route | Guarantee |
|---|---|
| `/` | Series landing: series title, pitch, nine-part outline, Part 0 expanded with all five chapters; published chapters are links, forthcoming ones visibly marked and not links (SC-005: any published chapter reachable in ≤2 steps) |
| `/part-0/chapter-01/from-app-to-infrastructure` | Chapter 0.1, statically rendered, with metadata (title = the chapter title's main clause + series name, e.g. "From app to infrastructure — Building Relay"; main-clause convention matches the slug rule) |
| Future chapters | `/part-<n>/chapter-<nn>/<slug>` — numeric segments for stable ordering, slug = kebab-case of the title's main clause (subtitle dropped) |

## C2 — Series manifest (`lib/tutorial.ts`)

| Export | Guarantee |
|---|---|
| `series` | Parts 0–8 with titles per docs/07 §3; Part 0 lists chapters 0.1–0.5 with id/path/title/status/readerProduces/sourceDoc/readerMinutes (the field is `path` — the full route; "slug" refers only to its final segment) |
| `getChapter(id)` | Returns the chapter or throws on unknown id (fail loud at build time) |
| `nextChapter(id)` / `prevChapter(id)` | Adjacent chapter within the whole series order, or null at the ends |
| Single source of truth | Landing ToC, ChapterHeader, and ChapterFooter render only from this manifest — no duplicated series data anywhere |

## C3 — Chapter authoring contract (every future chapter)

A chapter is `app/part-<n>/chapter-<nn>/<slug>/page.mdx` that:

1. exports `metadata` (title, description);
2. imports the boxes it uses from `@/components/tutorial/boxes` and the shell from
   `@/components/tutorial/chapter-shell`;
3. opens with `<ChapterHeader id="…" />` and closes with `<ChapterFooter id="…" />`;
4. keeps body prose inside the shell's `prose` treatment with zero per-chapter styling;
5. adds its manifest entry (or flips `forthcoming → published`).

Nothing else is required to add a chapter — that is the FR-008 reusability guarantee.

## C4 — Box component API (`components/tutorial/boxes.tsx`)

| Component | Props | Rendering guarantee |
|---|---|---|
| `<Why>` | `children`, optional `source` (e.g. "vision §2") | Labeled callout, accent family, cites its source |
| `<Trap>` | `children` | Labeled callout, destructive-tinted |
| `<Checkpoint>` | `children` | Labeled callout, primary family |
| `<SkipAhead>` | `children` | Labeled callout, muted family |
| `<Revised>` | `children`, `note` | Labeled callout, secondary family |
| `<ForwardRef>` | `children`, `part` (e.g. "Part 2") | Inline-or-block callout naming the future part |

All: server components, theme-token styling only, distinct in light and dark (SC-006).

## C5 — Format verification (scripted, quickstart V2)

| Check | Bound |
|---|---|
| Body word count (`page.mdx`, prose only) | 2,000 ≤ n ≤ 4,000 |
| `<Why` occurrences | ≥ 2 |
| `<Checkpoint` occurrences | exactly 1 |
| `<ForwardRef` occurrences | ≥ 1 |
| Takeaways block present | 1 |

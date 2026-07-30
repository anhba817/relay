# Data Model: Chapter 0 Improvement — Render the Source Documents

**Feature**: `specs/009-render-source-docs` · **Date**: 2026-07-30

## E1 — Doc registry entry (lib/docs.ts, six entries)

| Field | Rule | Source |
|---|---|---|
| `slug` | Route segment, stable: `product-vision`, `personas`, `journey-map`, `srs`, `sad`, `adr-deep-dives` | FR-002 |
| `sourceDoc` | The exact path string the series manifest records (`docs/01-product-vision.md`, …) — the join key for chapter links; MUST match manifest values verbatim | FR-001, R5 |
| `file` | Mirrored file under `content/docs/` (same basename as `sourceDoc`) | R1 |
| `title` | Display title (`Product vision`, `Personas`, `Journey map`, `SRS — Software Requirements Specification`, `SAD — Software Architecture Document`, `ADR deep dives`) | FR-002 |
| `titleVi` | Vietnamese display title for links/chrome (content stays English) | FR-008 |

Helpers: `getDoc(slug)`, `docsForSourceDoc(sourceDocField)` — splits the manifest's
comma-separated `sourceDoc` string, trims, resolves each through the registry;
unresolved segments are returned as plain-text labels (rendered without a link —
the 002 no-dead-link rule); `chaptersCiting(slug)` — the reverse lookup: published
chapters whose manifest `sourceDoc` includes the doc's path (US2-AS1's "way back to
the citing context").

## E2 — Mirrored document (content/docs/*.md, six files)

| Property | Rule | Source |
|---|---|---|
| Content | Byte-identical to the parent repo's `docs/<same name>` at ship time | FR-005, R1 |
| Lifecycle | Written only by `scripts/sync-docs.sh`; never hand-edited | R1, constitution IV |
| Drift | `scripts/check-docs-drift.sh` (and `pnpm check:docs`) diffs each file against `../docs/`; non-zero exit + named file on divergence; warning + exit 0 when the parent is absent (standalone clone) | FR-009, SC-006 |

## E3 — Reference page (both locale routes over one shared renderer)

| Element | Rule | Source |
|---|---|---|
| Routes | `/docs/[slug]` and `/vi/docs/[slug]`, `generateStaticParams` over the registry — 12 static pages | FR-002, R6 |
| Metadata | Title from registry (locale-appropriate) + " — Building Relay"; hreflang alternates both directions | FR-008, 004 C4 |
| Chrome | Site header (theme + language switcher functional); breadcrumb-style back link to the contents; a "referenced by" line linking each citing chapter (`chaptersCiting`, locale-prefixed hrefs and locale titles); vi article wrapped `lang="en"` inside the vi layout with the one-line English-material note | FR-006/008, US2-AS1, R6 |
| Body | `DocArticle`: react-markdown + remark-gfm over the mirrored file (read via fs at build); headings get stable slug ids; tables wrapped in `overflow-x-auto`; ```mermaid fences → `MermaidDiagram`; all other fences render as code blocks | FR-003, R2 |
| Outline | "Contents" block above the article listing top-level (h2) sections as anchor links — any section 1 click from top | FR-006, R4, SC-005 |
| Diagrams | `MermaidDiagram` (client): lazy `import("mermaid")`, `securityLevel: "antiscript"` (keeps the docs' `<br/>` labels working; see R3), theme `default`/`dark` from next-themes `resolvedTheme`, re-render on theme change, `<pre>` source fallback pre-hydration | FR-004, R3 |

## E4 — Chapter header affordance (chapter-shell.tsx + i18n.ts)

| Element | Rule | Source |
|---|---|---|
| Placement | New line in `ChapterHeader` under the reader-produces/minutes line | R5 |
| Content | `{d.shell.sourceDocs}:` + one link per resolved doc (locale-prefixed route, locale-appropriate title); vi adds the English hint (e.g. `(tiếng Anh)`) | FR-001/008 |
| Data | `chapter.sourceDoc` (manifest, unchanged) → `docsForSourceDoc` | R5 |
| i18n keys | `shell.sourceDocs` ("Source" / "Tài liệu gốc"), `badges.englishDoc` ("English" / "tiếng Anh") | FR-008 |
| Invariant | Zero edits to any `page.mdx`; battery counts of all ten chapter files identical before/after | FR-007, SC-004 |

## E5 — Chapter→document mapping (existing — unchanged)

The series manifest's `sourceDoc` field (features 002–008) remains the single
mapping: 0.1 → docs/01, 0.2 → docs/02, 0.3 → docs/03, 0.4 → docs/04,
0.5 → `"docs/05-sad.md, docs/06-adr-deep-dives.md"` (two links). No manifest
field changes in this feature.

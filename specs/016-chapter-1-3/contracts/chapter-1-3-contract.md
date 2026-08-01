# Contract: Chapter 1.3 — The Protocol Package

Externally observable promises; verification in [quickstart.md](../quickstart.md).

## C1 — Pages exist and render

- `GET /part-1/chapter-03/the-protocol-package` and
  `GET /vi/part-1/chapter-03/the-protocol-package` prerender with the full
  reading shell (sidebars, rail, footers, code-block titles/copy, figures,
  suggestion capture, vi banner on the vi page).
- Canonical/hreflang alternates, OG metadata, TechArticle JSON-LD via the
  established shell.

## C2 — Battery (per locale)

| Check | Bound |
|---|---|
| Canonical words | 2,000 ≤ w ≤ 4,000 |
| WHY | ≥ 2 |
| TRAP | ≥ 1 |
| SKIP AHEAD | = 1, names `part1-ch3` |
| FORWARD REF | ≥ 1 |
| CHECKPOINT | = 1, closing |
| Figures | 2–4, captioned |
| Baseline | 16 rows; 14 prior rows byte-identical to 014's baseline |

## C3 — Fence ↔ repository (three chapters now)

- Every `title=""` file fence in 1.3 (en AND vi) byte-matches the named
  relay-platform file at HEAD (Dong's `part1-ch3` pins it).
- 1.1's ten and 1.2's three file fences still byte-match at the same state
  (additive-only).
- en/vi fence lists index-aligned and byte-identical; command fences replay.
- Test-file fences: full-file fences carry `title=""` and byte-match; if the
  chapter shows excerpts instead, the excerpt fences carry NO title and the
  prose says the tag holds the full file — one or the other, no gray zone.

## C4 — The package and the gate

- `pnpm install && pnpm lint && pnpm typecheck && pnpm test` green at the
  chapter-end state with ≥12 total tests; the new suites demonstrably reject
  malformed frames (wrong type, missing/extra/wrong-typed payload fields,
  invalid seq/idem_key) and verify code-registry integrity.
- zod appears ONLY in `packages/protocol/package.json` (pinned); root
  manifest and all fenced files from 1.1/1.2 are byte-unchanged
  (`git status` additive check).
- Every exported static type is inferred from a schema (no duplicate
  hand-written frame interfaces — R3 spot-check).
- `@relay/protocol` is importable from a sibling workspace package (checked
  via a scratch consumer or pnpm resolution, not committed).

## C5 — Vocabulary fidelity (the R2 table is the law)

- Document-sourced rows quote/cite correctly (EIR-WS-02/03/05, SAD §5.1
  frame lines, FR-RTM-04/05/06/08, FR-MSG-04, ADR-03, SAD §7's 4009).
- Every DECISION row's item appears in the chapter WITH its explicit
  recorded-decision marker sentence.
- The ID detector passes over page.mdx + figures.ts; zero frame names outside
  the R2 table.

## C6 — Navigation & publishing (manifest-only)

- The ONLY tutorial-side source edit outside the two new chapter directories
  is the 1.3 manifest entry flip.
- After the flip: 1.2's footers gain the 1.3 next card (both locales); 1.3's
  footers show 1.2 prev and no next; sidebar Part 1 = exactly 3 linked + 1
  forthcoming; both landings link 1.3; sitemap = exactly 30 URLs.
- **Suggestions integration**: POST /api/suggestions accepts pagePath
  `/part-1/chapter-03/the-protocol-package` (locale en) and the `/vi/…`
  variant (locale vi) — the 015 allowlist derived the new pages with zero
  edits.

## C7 — Vietnamese parity & register

- Box/figure/fence counts match en; fences byte-identical incl. titles.
- Settled register and glossary ("package", "cửa ải"/"vượt qua", "bản giao
  kèo", "quả ngọt", "tin nhắn"; frame names/codes English; no calques or
  hyphenated compounds); naturalization self-review done before presenting.
- Dong's read-through precedes the commit (handoff item).

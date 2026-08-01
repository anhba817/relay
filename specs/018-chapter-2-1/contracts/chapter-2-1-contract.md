# Contract: Chapter 2.1 — Schema with a Spine

Externally observable promises; verification in [quickstart.md](../quickstart.md).

## C1 — Pages exist and render

- `GET /part-2/chapter-01/schema-with-a-spine` (+ `/vi/…`) prerender with the
  full reading shell and all established chrome.
- Canonical/hreflang, OG, TechArticle JSON-LD via the shell.

## C2 — Battery (per locale)

| Check | Bound |
|---|---|
| Canonical words | 2,000 ≤ w ≤ 4,000 |
| WHY / TRAP / SKIP / FWD / CHK | ≥2 / ≥1 / =1 (`part2-ch1`) / ≥1 / =1 |
| Figures | 2–4, captioned |
| Baseline | 20 rows; 18 prior rows byte-identical to 017's |

## C3 — Fence contract, AMENDED discipline (the debut)

- 2.1's file fences byte-match the repo at HEAD (Dong's `part2-ch1` pins).
- **Diff-fences** (exactly two: `services/api/package.json`,
  `eslint.config.mjs`): applying each diff to the predecessor chapter's
  published fence text yields the current repo file byte-exactly.
- Predecessor re-pinning recorded: 1.4's package.json fence and 1.1's eslint
  fence are valid at their own tags; ALL other prior fences (1.1×9, 1.2×3,
  1.3×7, 1.4×9) still byte-match HEAD.
- en/vi fence AND diff-fence lists index-aligned, byte-identical.
- Command fences replay under the documented lane split.

## C4 — The gate, two lanes

- **Unit lane (unchanged, Docker-free)**: `pnpm lint && pnpm typecheck &&
  pnpm test` green with the daemon irrelevant; `*.itest.ts` files are
  provably invisible to it (root vitest include unmatched).
- **Integration lane**: with the compose stack up —
  `pnpm --filter @relay/api migrate` applies migration 001 to a fresh
  database AND re-runs as a no-op; `pnpm --filter @relay/api
  test:integration` passes, demonstrably attacking with foreign
  environment_ids (cross-tenant reads null/empty, lists exclude, DR-02
  uniqueness per-tenant).
- The integration suite fails fast on a non-local DATABASE_URL host (the
  never-Neon guardrail, mechanical).
- Lint enforces the constitution clause: importing `pg` outside
  `services/api/src/db/**` is a lint error (verified by a scratch violation).

## C5 — Schema & derivation fidelity

- Migration SQL is column-exact against SAD §6.1 for environments, users,
  channels, messages (constraints, CHECKs, DR comments included,
  wrap-tolerant); `applications` and `members` carry recorded-decision
  comments citing their anchors (environments' FK; §6.3's index).
- Both SAD §6.3 hot-path indexes exist with citation comments.
- The ID detector passes; every R-table DECISION appears in the chapter with
  its marker sentence.

## C6 — Navigation & publishing (Part 2 opens)

- The ONLY tutorial-side source edit outside the two new chapter dirs is the
  Part 2 seed in `lib/tutorial.ts`.
- After the seed: both landings render Part 2 as a chapter section (exactly
  1 link + 7 forthcoming badges) and drop it from road-ahead; sidebar shows
  Part 2 mixed; 1.4's footers gain the 2.1 next card (both locales); 2.1's
  footers show 1.4 prev + no next; sitemap = exactly 34 URLs.
- Suggestions: POSTs accepted for both new paths (allowlist derived); 2.2's
  forthcoming path still rejects with `invalid_page`.

## C7 — Vietnamese parity & register

- Structural parity; fences + diff-fences byte-identical; settled register
  and glossary (SQL/table names English; "thêm chi tiết" et al.); the eight
  seeded vi titles flagged for Dong's review; naturalization self-review
  done before presenting.

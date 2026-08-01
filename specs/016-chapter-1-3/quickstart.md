# Quickstart: Verifying Chapter 1.3

Contract references (C1–C7) from
[contracts/chapter-1-3-contract.md](./contracts/chapter-1-3-contract.md).

## Prerequisites

- Node 22+, pnpm 10. No Docker needed for this chapter's gate.
- For V5's live allowlist check: the 015 verification database (or any
  `DATABASE_URL` in relay-tutorial/.env) and the dev server. If absent,
  run the unit-level fallback in V5 and flag the live POST for Dong.

## V1 — The package and the gate (C4)

```bash
cd relay-platform
pnpm install
pnpm lint && pnpm typecheck && pnpm test
```

**Expect**: green; total tests ≥ 12; the protocol suites visibly include
reject cases. Then the additive check:
`git -C relay-platform status --porcelain` shows ONLY `packages/protocol/`
(+ never-fenced files if any); zod present only in
`packages/protocol/package.json`, pinned.

## V2 — Vocabulary fidelity (C5)

Walk research R2's table against the chapter: each document-sourced row's
quote spot-checked (wrap-tolerant) against docs/04/05; each DECISION row's
marker sentence present; ID detector clean over both page.mdx + figures.ts;
grep the chapter for frame names and confirm the set equals the R2 table's.

## V3 — Fence ↔ repo, three chapters (C3)

Extract every title'd fence from BOTH locales' 1.3 page.mdx → byte-diff
against relay-platform files; re-run 1.1's ten and 1.2's three diffs; assert
en/vi fence lists byte-identical; replay command fences on the workspace.

**Expect**: zero diffs; the three-chapter battery is now the standing set.

## V4 — Battery v3 (C2)

Regenerate `specs/016-chapter-1-3/battery-baseline.txt` (16 rows, established
formula). Diff the 14 pre-existing rows against 014's baseline —
byte-identical or defect. 1.3 rows within all bounds.

## V5 — Navigation + suggestions integration (C1, C6)

`pnpm build` in relay-tutorial, then against the output:

- sitemap.xml = exactly 30 URLs incl. both 1.3 pages;
- 1.2 footers (en+vi) show the 1.3 next card; 1.3 footers show 1.2 prev, no
  next; sidebar Part 1 = 3 links + 1 forthcoming; landings link 1.3;
- OG/JSON-LD present on both new pages; vi page carries the translation
  banner with the suggest invitation;
- `git diff` shows the manifest flip as the only source edit outside the two
  chapter directories;
- **allowlist admission**: with the dev server + database up, POST a valid
  suggestion against `/part-1/chapter-03/the-protocol-package` (en) and
  `/vi/part-1/chapter-03/the-protocol-package` (vi) → 201 each, rows land.
  Fallback without a database: unit-check `validateSuggestion` accepts the
  two paths (allowlist membership) and flag the live POST for Dong.

## V6 — Vietnamese parity (C7)

Structural-parity counts en vs vi; fence byte-identity (V3 covers); glossary
sweep over the new chapter ("gói", "cánh cổng", "trình biên dịch", "trình
chạy test", calque hyphens all absent; "cửa ải" pairs with "vượt qua";
"package"/"bản giao kèo" used as settled).

## V7 — Dong's manual checks (handoff, not build gates)

1. vi read-through of 1.3 (register) — suggestions channel is live as backstop.
2. Reader-path walk vs the 75-minute budget; figures both themes / 375 px.
3. Commit sequence: relay-platform (`git add -A && git commit && git tag
   part1-ch3 && git push origin main --tags`), then relay-tutorial, then
   parent (pins + spec artifacts). Post-push: fresh-clone gate replay at the
   tag.
4. Redeploy the site (compose rebuild on the VPS — or the Vercel import, if
   the migration discussed on 2026-08-01 happens first).

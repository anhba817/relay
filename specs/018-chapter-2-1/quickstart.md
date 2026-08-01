# Quickstart: Verifying Chapter 2.1

Contract references (C1–C7) from
[contracts/chapter-2-1-contract.md](./contracts/chapter-2-1-contract.md).

## Prerequisites

- Node 22+, pnpm 10, Docker + Compose v2 (the 1.2 stack is the test
  database).
- On the reference machine the compose Postgres runs remapped:
  `RELAY_POSTGRES_PORT=15432` — export
  `DATABASE_URL=postgres://relay:relay@localhost:15432/relay` for the
  integration lane. **Never** the tutorial site's Neon.

## V1 — Unit lane, Docker-free (C4)

```bash
cd relay-platform
pnpm install
pnpm lint && pnpm typecheck && pnpm test
```

**Expect**: green with Docker stopped/irrelevant; test count unchanged from
1.4's 40 unless unit tests were added; `*.itest.ts` demonstrably NOT
collected (vitest list or run output).

## V2 — Migrations + isolation suite on compose (C4)

```bash
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait postgres
export DATABASE_URL=postgres://relay:relay@localhost:15432/relay
pnpm --filter @relay/api migrate        # applies 001
pnpm --filter @relay/api migrate        # second run: no-op (idempotence)
pnpm --filter @relay/api test:integration
```

**Expect**: fresh apply lists 001; re-run reports nothing to do; the itest
suite passes with visible foreign-tenant attack cases; suite refuses to run
if DATABASE_URL points at a non-local host (spot-check with a fake remote
URL → fast failure, nothing executed).

## V3 — Enforcement spot-checks (C4)

- Scratch violation: add a temporary `import pg from "pg"` to
  `services/api/src/main.ts` → `pnpm lint` fails with the
  no-restricted-imports message; remove it.
- Constructor discipline: `new Repository(pool)` without an environment id
  is a TYPE error (tsc spot-check in a scratch file; delete after).

## V4 — Fence battery under the amended discipline (C3)

- 2.1's title'd fences byte-match the repo (both locales).
- **Diff-chain**: extract the package.json fence from 1.4's page.mdx and
  the eslint fence from 1.1's page.mdx; apply this chapter's diff-fences;
  results must byte-equal the current files.
- All other prior fences (1.1×9, 1.2×3, 1.3×7, 1.4×9) still byte-match HEAD.
- en/vi fence + diff-fence identity; command replay per lanes.

## V5 — Battery v3 (C2)

Regenerate `specs/018-chapter-2-1/battery-baseline.txt` (20 rows,
established formula); 18 prior rows byte-identical to 017's; 2.1 rows in
bounds.

## V6 — Navigation: Part 2 opens (C1, C6)

`pnpm build` in relay-tutorial, then:

- sitemap = exactly 34 URLs incl. both 2.1 pages;
- both landings: Part 2 is a chapter section (1 link + 7 forthcoming),
  gone from road-ahead; sidebar mixed state;
- 1.4 footers show the 2.1 next card (both locales); 2.1 footers show 1.4
  prev + no next;
- OG/JSON-LD on the new pages; vi banner + suggest invitation;
- `git diff`: the Part 2 seed is the only source edit outside the chapter
  dirs;
- allowlist: POST per new path → 201 (flag rows for Dong); 2.2's path →
  400 invalid_page.

## V7 — Vietnamese parity (C7)

Structural parity counts; fence identity (V4); glossary sweep (no "gói",
"cánh cổng", "trình biên dịch/trình chạy test", "hình hài", "thành tiếng",
"đắp cơ bắp/da thịt", hyphenated compounds); "cửa ải"+"vượt qua"; the eight
seeded vi titles listed for Dong.

## V8 — Dong's manual checks (handoff, not build gates)

1. vi read-through of 2.1 + the eight seeded vi titles.
2. The 90-minute walk; figures both themes/375 px.
3. Neon cleanup of flagged verification rows.
4. Commit sequence: relay-platform (`git add -A && git commit && git tag
   part2-ch1 && git push origin main --tags`), then relay-tutorial, then
   parent. Post-push: fresh-clone replay of BOTH lanes at the tag; site
   redeploy.

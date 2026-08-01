# Quickstart: Verifying Chapter 1.4

Contract references (C1–C7) from
[contracts/chapter-1-4-contract.md](./contracts/chapter-1-4-contract.md).

## Prerequisites

- Node ≥ 22.18 (`node --version` — type stripping; reference machine 22.20),
  pnpm 10. No Docker anywhere in this chapter.
- For V5's allowlist POSTs: a `DATABASE_URL` in relay-tutorial/.env (Dong's
  Neon is currently configured — flag any test rows for deletion in the
  handoff, as in 016).

## V1 — The gate and the additive check (C4)

```bash
cd relay-platform
pnpm install
pnpm lint && pnpm typecheck && pnpm test
```

**Expect**: green, ≥40 tests, no fixed ports in any suite. Then:
`git status --porcelain` shows only `packages/service-kit/`, `services/api/`,
`services/gateway/` (+ lockfile/README); zero new external dependencies in
any new package.json; the three new tsconfigs carry `erasableSyntaxOnly`.

## V2 — The living skeleton (C4)

```bash
pnpm --filter @relay/api dev &      # then the same for @relay/gateway
curl -i localhost:4000/healthz
curl -s localhost:4001/healthz | python3 -m json.tool   # inspect .protocol (jq works too, if present)
curl -i localhost:4000/nope         # EIR-API-04-shaped 404
```

**Expect**: 200s with `X-Request-Id` headers (unique per request); api shape
`{status:"ok",service:"api",uptime_s}`; gateway payload advertises 10 frame
names + close codes [4001,4002,4008,4009] matching `@relay/protocol`; the 404
carries `{code:"not_found",message,docs_url}`; each request produces exactly
one JSON log line whose `request_id` equals the response header. PORT
override spot-check (`PORT=4100 pnpm --filter @relay/api dev`). Stop both.

## V3 — Fence ↔ repo, four chapters (C3)

Extract every title'd fence from BOTH locales' 1.4 page.mdx → byte-diff
against relay-platform; re-run ALL prior chapters' fence diffs (10+3+7);
diff the two service tsconfigs against the fenced kit tsconfig (the
identical-in-prose claim); en/vi fence identity; command-fence replay.

## V4 — Battery v3 (C2)

Regenerate `specs/017-chapter-1-4/battery-baseline.txt` (18 rows, established
formula); 16 prior rows byte-identical to 016's; 1.4 rows in bounds.

## V5 — Navigation: Part 1 completes (C1, C6)

`pnpm build` in relay-tutorial, then:

- sitemap = exactly 32 URLs incl. both 1.4 pages;
- sidebar Part 1 = 4 links, **0 forthcoming** (grep the built HTML for the
  forthcoming badge inside Part 1's section — must be absent);
- 1.3 footers show 1.4 next (both locales); 1.4 footers show 1.3 prev and no
  next; landings: Part 1 fully linked, Part 2 still road-ahead;
- OG/JSON-LD on both new pages; vi banner with suggest invitation;
- `git diff`: manifest flip is the only source edit outside the chapter dirs;
- allowlist: POST a suggestion for each new path → 201 (note rows for Dong's
  cleanup); confirm 016's old "forthcoming 1.4 → invalid_page" case now
  correctly returns 201 instead.

## V6 — Vietnamese parity (C7)

Structural-parity counts; fence identity (V3); glossary sweep (no "gói",
"cánh cổng", "trình biên dịch/trình chạy test", "hình hài", "thành tiếng",
hyphenated compounds; "cửa ải"+"vượt qua"; "bộ khung biết đi" present).

## V7 — Dong's manual checks (handoff, not build gates)

1. vi read-through of 1.4; the 90-minute walk; figures both themes/375 px.
2. Delete my verification suggestion rows from Neon (`WHERE suggestion LIKE
   'allowlist check%'` or as reported).
3. Commit sequence: relay-platform (`git add -A && git commit && git tag
   part1-ch4 && git push origin main --tags`), then relay-tutorial, then
   parent — the **Part 1 milestone** commits (docs/07 §5).
4. Post-push: fresh-clone gate replay at the tag; redeploy the site (VPS
   rebuild or Vercel).

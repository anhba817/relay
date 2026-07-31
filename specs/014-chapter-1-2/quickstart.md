# Quickstart: Verifying Chapter 1.2

Validation scenarios proving the feature end-to-end. Contract references
(C1–C7) from [contracts/chapter-1-2-contract.md](./contracts/chapter-1-2-contract.md).

## Prerequisites

- Node 22+, pnpm 10 (via corepack), Docker Engine + Compose v2 (`docker
  compose version` — needs `--wait` support) on the verification machine.
- Working tree: parent repo with both submodules at the feature's end state.

## V1 — The gate, Docker-free (C4)

```bash
# Docker daemon stopped (or: sudo systemctl stop docker)
cd relay-platform
pnpm install
pnpm lint && pnpm typecheck && pnpm test
```

**Expect**: all green; test output includes the infra suite (service names,
healthcheck count, volume assertions) with zero containers running.

## V2 — One command, whole world (C3, C4)

```bash
cd relay-platform
docker compose up -d --wait          # exits 0 only when all healthchecks pass
docker compose ps                    # four services, each "(healthy)"
docker compose down                  # clean teardown, volumes kept
docker compose up -d --wait && docker compose down -v   # reset path also clean
```

**Expect**: `--wait` returns success; `ps` shows exactly `postgres`, `redis`,
`nats`, `clickhouse` healthy on 5432/6379/4222/8123; both teardown modes exit 0.

## V3 — Fence ↔ repo diffs, both chapters (C3)

Extract each `title=""`-named fence from **both locales'** 1.2 page.mdx and
byte-diff against the relay-platform file it names (`compose.yaml`, `infra.ts`,
`infra.test.ts`). Then re-run 1.1's ten fence diffs unchanged — the
additive-only rule means they must still pass. Also assert en/vi fence lists
byte-identical (the established extraction script).

**Expect**: zero diffs anywhere.

## V4 — Battery v3 (C2)

Run the battery over all published chapters, regenerate
`specs/014-chapter-1-2/battery-baseline.txt` (14 rows). Diff the 12 pre-existing
rows against `specs/013-chapter-1-1/battery-baseline.txt`.

**Expect**: 1.2 rows within bounds (words 2,000–4,000; WHY ≥2, TRAP ≥1, SKIP =1,
FWD ≥1, CHK =1, figures 2–4); 12 prior rows identical.

## V5 — Navigation battery (C1, C5)

```bash
cd relay-tutorial && pnpm build
```

Then against the built output:

- sitemap.xml holds exactly 28 URLs, including both 1.2 pages;
- 1.1's footers (en+vi) show the 1.2 next card; 1.2's footers show 1.1 prev and
  no next;
- sidebar Part 1: exactly 2 linked chapters + 2 forthcoming (unlinked);
- both landings link 1.2; `git diff` on relay-tutorial shows the manifest flip
  as the only source edit outside the two new chapter directories;
- 1.2 pages carry canonical/hreflang/OG/JSON-LD (grep the prerendered HTML).

## V6 — Facts and IDs (C6)

Run the invented-ID detector over both page.mdx + figures.ts; spot-check the
verbatim quotes (NFR-MNT-03 sentence; ADR-02/07 phrases) against docs/04/05.

**Expect**: detector clean; quotes byte-faithful.

## V7 — Vietnamese parity (C7)

Structural-parity script (box/figure/fence counts en vs vi) + fence
byte-identity (covered in V3) + glossary sweep: no "gói"/"cánh cổng"/"trình
biên dịch"/"trình chạy test"/calque hyphens in the new chapter; "cửa ải"
pairs with "vượt qua".

## V8 — Dong's manual checks (handoff, not build gates)

1. vi read-through of 1.2 (register).
2. Reader-path walk vs the 60-minute budget.
3. Figures at both themes / 375 px.
4. Commit sequence: relay-platform first (`git add -A && git commit && git tag
   part1-ch2 && git push --tags`), then relay-tutorial, then parent (pins +
   spec artifacts). After push: fresh-clone replay of V1+V2 at the tag.

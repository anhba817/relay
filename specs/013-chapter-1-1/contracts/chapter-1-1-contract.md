# Contract: Chapter 1.1 — Scaffold, Chapter, and the Code-Chapter Battery

**Feature**: `specs/013-chapter-1-1` · **Date**: 2026-07-31

## C1 — The scaffold (relay-platform)

| Check | Bound |
|---|---|
| Fresh-clone replay | clone → `pnpm install` → `pnpm lint` → `pnpm typecheck` → `pnpm test` all exit 0 (at HEAD now; at `part1-ch1` once Dong tags) |
| Shape | workspace globs `packages/*`,`services/*`; strict base tsconfig; flat ESLint; Vitest; `@relay/config` with ≥1 passing test |
| Discipline | `packageManager` pinned; no orchestrator (Turborepo/Nx) — plain pnpm scripts; own git history (submodule) |

## C2 — Routes and navigation

| Surface | Guarantee |
|---|---|
| `/part-1/chapter-01/the-monorepo-and-the-toolchain` (+ `/vi/…`) | Both live, static, hreflang pair, shell identity "Part 1 · Chapter 1.1", header source links, sidebars |
| 0.5 footers (both locales) | Next card appears for the first time, linking 1.1 |
| Sidebar/landing | Part 1 mixed: exactly 1 link + 3 forthcoming entries (unlinked); Part 0 untouched |
| Sitemap | Exactly 26 `<loc>`; forthcoming chapters absent |
| SEO | New pages: canonical=1, og:title=1, og:image=1, one TechArticle each; existing pages unchanged |

## C3 — Chapter content (battery v3)

| Item | Bound |
|---|---|
| Canonical words (prose outside fences) | 2,000–4,000 per locale's own measure (en bound authoritative) |
| Boxes | Why ≥2 · **Trap ≥1** · SkipAhead =1 (names `part1-ch1`) · ForwardRef ≥1 · Checkpoint =1; en == vi per class |
| Figures | 3 per locale, captioned, ≥1 per half, en == vi |
| Decisions summary | Present as the opening section — Part 0's binding artifacts as a lookup |
| ADR-01 fidelity | Deep-dive quotes verbatim (wrap-tolerant spot-checks); ID detector clean over page.mdx + figures.ts |
| Fences | File-content fences diff clean against the repo (C4); en/vi code fences byte-identical |

## C4 — Chapter↔code no-drift (enumerated)

| Check | Bound |
|---|---|
| File fences | Every enumerated fence ↔ repo file diff is empty at the verified ref |
| Command fences | Replay clean on a fresh clone in order |
| SKIP AHEAD | Names `part1-ch1` exactly (the tag Dong creates at commit) |

## C5 — Freeze and regressions

| Check | Bound |
|---|---|
| Part 0 content | Byte-untouched; under the v3 formula only the words column may differ from the v2 baseline (fence-strip); boxes/fences/figures columns identical |
| New baseline | specs/013-chapter-1-1/battery-baseline.txt covers all 12 chapter files under v3 |
| docs/07 | §2 carries the code-chapter battery note; drift check (docs mirror) still green |
| Build gate | `pnpm lint && pnpm build` (tutorial) exit 0; zero new tutorial dependencies |

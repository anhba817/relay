# Implementation Plan: Tutorial Chapter 1.4 — Walking Skeleton

**Branch**: `main` (no feature branch — consistent with features 001–016) | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/017-chapter-1-4/spec.md`

## Summary

Close Part 1: stand up the first two of Relay's six services — `services/api`
and `services/gateway`, deliberately empty of business logic but real
processes with docs/07's four properties (health checks, request IDs,
structured JSON logs, skeleton-before-muscles). The operational plumbing the
two services share — logger, request-id middleware, a tiny node:http serve
helper — gets ONE home in a new `packages/service-kit` (the chapter's TRAP is
copying it twice; 1.1's copies-drift lesson applied to behavior). Services run
with **zero new runtime dependencies**: Node 22.18+ type-stripping executes
TypeScript directly (`node --watch src/main.ts`), enforced per-package via
`erasableSyntaxOnly` — so the additive-only rule survives its hardest test
(no root-script edits, no compose edits; start via `pnpm --filter`). The
gateway's health payload advertises the protocol vocabulary it speaks by
importing `@relay/protocol` — 1.3's promise made visible. Tutorial side:
chapter en+vi, the flip that completes Part 1 (sitemap 30 → 32, sidebar
4 links + 0 forthcoming), allowlist admission for the new pages. Decisions in
[research.md](./research.md).

## Technical Context

**Language/Version**: relay-platform — TypeScript ~5.9 / Node 22 / pnpm 10;
services REQUIRE Node ≥ 22.18 at runtime (native type-stripping, R3) —
verified reality: the reference machine runs 22.20; relay-tutorial —
unchanged stack

**Primary Dependencies**: relay-platform: **none new** — `@relay/protocol`
and `@relay/service-kit` are workspace-internal (`workspace:*`); the services
use `node:http` and `node:crypto` only (R1, R3). Tutorial side: none new

**Storage**: None touched — the skeleton deliberately connects to no store
(that is Part 2's muscle); the 1.2 compose stack is unused by this chapter's
gate and demonstrations

**Testing**: relay-platform: gate green at `part1-ch4`, Docker-free; new
suites boot each service's exported server on an ephemeral port (port 0),
fetch `/healthz`, assert response shape + `X-Request-Id` + structured log
lines via an injectable sink (R4); test count grows 32 → ≥40. Tutorial:
battery v3 (baseline 16 → 18 rows), fence diffs across FOUR chapters
(10+3+7+1.4's), ID detector, nav battery (sidebar 4+0, sitemap 32, 1.4
empty-next), vi parity, allowlist admission (R6)

**Target Platform**: any Node ≥ 22.18 machine; no Docker anywhere in this
chapter's gate or demos; tutorial: static prerendered pages

**Project Type**: Two-artifact content feature (code increment + teaching
chapter) — fourth and final Part 1 iteration

**Performance Goals**: None — the skeleton serves health checks; NFR-PRF
targets arrive with Part 2's real paths

**Constraints**: NO file fenced by 1.1/1.2/1.3 may be modified (root
package.json, compose.yaml, and all of packages/{config,protocol} are now
read-only); observability honesty — NFR-OBS-01's tenant/correlation IDs are
recorded deferrals, request ID is real (R2); frame vocabulary from
`@relay/protocol` only; commits, pushes, AND the `part1-ch4` tag are Dong's

**Scale/Scope**: relay-platform: 3 new workspace members (~12 files, ~350
lines): `packages/service-kit`, `services/api`, `services/gateway`; tutorial:
2 page.mdx (~2,400 prose words each) + 2 figures.ts (3 figures/locale),
manifest flip (1 entry), battery baseline regenerated (18 rows)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I. Tenant isolation | ✅ N/A (recorded) | No data access exists; the log schema reserves the tenant field as a documented deferral (R2), so Principle I's observability hooks have a named landing slot. |
| II. No acknowledged loss | ✅ N/A | No write paths yet; the chapter reiterates that the gateway never writes (ADR-05) as the *reason* the skeleton API/gateway split looks the way it does. |
| III. Two data paths | ✅ N/A | No analytics. |
| IV. Single source of truth | ✅ Pass | The shared plumbing gets one home (`service-kit`) instead of two copies — the chapter's TRAP; services consume the one protocol package; ADR-04's single-writer division is taught as the skeleton's shape. |
| V. Developer/reader-first | ✅ Pass | Request IDs on every response (EIR-API-05) from the first line of the first service — the "traceable within 5 minutes" promise (NFR-OBS-06) starts here. |
| VI. Requirement-driven, test-verified | ✅ Pass | Every property traces (EIR-API-05, NFR-OBS-01/06, SAD §4.1, ADR-04/05); tests assert response shape, header presence, and log structure — not placeholders. |
| VII. Boring by design | ✅ Pass | node:http, node:crypto, native type-stripping — ZERO new dependencies; two services because the SAD's Phase-1 service view names exactly these two; no framework until a requirement demands one. |
| Tech & platform constraints | ✅ Pass | TypeScript/Node per ADR-01; structured JSON logs with request ID per the constitution's observability clause (tenant/correlation IDs: recorded deferrals with named arrival points). |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — three additive workspace members, a chapter
pair, one flip.

## Project Structure

### Documentation (this feature)

```text
specs/017-chapter-1-4/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chapter-1-4-contract.md
├── battery-baseline.txt # regenerated (18 rows) at implementation
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code

```text
relay-platform/ (submodule — advances part1-ch3 → part1-ch4, ADDITIVE ONLY)
├── packages/service-kit/             # NEW — @relay/service-kit (R1): the shared plumbing
│   ├── package.json                  # no external deps
│   ├── tsconfig.json                 # extends base + erasableSyntaxOnly (R3)
│   └── src/
│       ├── index.ts                  # structured logger, request-id, serve() helper (R2)
│       └── index.test.ts             # log shape + request-id format tests (R4)
├── services/api/                     # NEW — @relay/api (SAD §4.1's API service, empty)
│   ├── package.json                  # deps: @relay/{protocol,service-kit} workspace:*
│   ├── tsconfig.json
│   └── src/
│       ├── main.ts                   # serve(): /healthz + EIR-API-04-shaped 404 (R2)
│       └── main.test.ts              # ephemeral-port boot test (R4)
└── services/gateway/                 # NEW — @relay/gateway (SAD §4.1's gateway, empty)
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── main.ts                   # serve(): /healthz advertising the protocol vocabulary (R5)
        └── main.test.ts

relay-tutorial/ (existing submodule)
├── lib/tutorial.ts                                   # MODIFIED — 1.4 flips; Part 1 completes (R6)
└── app/{(en),(vi)/vi}/part-1/chapter-04/walking-skeleton/
    ├── page.mdx                                      # NEW ×2 (R7, R8)
    └── figures.ts                                    # NEW ×2

/home/dong/work/relay/ (parent)
└── specs/017-chapter-1-4/battery-baseline.txt        # NEW — 18 rows
```

**Structure Decision**: The 013 pattern, fourth pass, with the additive-only
escape hatch never needed: per-package `dev` scripts + `pnpm --filter` start
the services, so no fenced file changes. `services/*` was already in the
workspace glob and the vitest include pattern since 1.1 — the map drawn three
chapters ago finally gets buildings.

## Implementation Flow (input to /speckit-tasks)

1. **service-kit** (FR-003, R1/R2/R4): the shared logger/request-id/serve
   home with its tests; verify `node src/…` type-stripping reality (R3).
2. **The two services** (FR-002..004): api + gateway with health endpoints,
   request IDs, structured logs, protocol advertisement; ephemeral-port
   tests; gate green Docker-free; additive check.
3. **Manifest flip** (FR-008, R6): 1.4 published+translated; Part 1 complete.
4. **English chapter** (FR-001..005, 007, R7): the beats; fences byte-match;
   three figures; derivation + deferral honesty.
5. **Vietnamese chapter** (FR-009, R8): settled register; byte-identical
   fences; naturalization self-review.
6. **Verify** ([quickstart.md](./quickstart.md)): gate, live service walk
   (start → curl → log line → stop), four-chapter fence battery, battery v3
   (18 rows), nav battery incl. Part-1-complete states + allowlist POSTs, vi
   parity.
7. **Handoff**: no commits — per-repo report incl. Dong's `part1-ch4` tag
   sequence and the Part 1 milestone note.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The Node ≥ 22.18 runtime floor (type stripping) is real and must be stated
  in the chapter and README — the fenced root `engines: >=22` cannot change,
  so prose carries the precision (verified: reference machine is 22.20).
- `erasableSyntaxOnly` goes in the three NEW tsconfigs only — the base
  tsconfig is a 1.1 fence and stays untouched.
- The gateway's protocol advertisement must derive frame names from
  `@relay/protocol`'s actual exports at implementation time (no hardcoded
  list that could drift) — verify zod 4's discriminated-union introspection
  API against the installed package first.
- Service tests must never bind fixed ports (port 0 only) — parallel vitest
  workers and CI both punish fixed ports.
- Commits/pushes/tags remain Dong's; vi read-through before the milestone
  commit; Part 2 is NOT seeded.

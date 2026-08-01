# Contract: Chapter 1.4 — Walking Skeleton

Externally observable promises; verification in [quickstart.md](../quickstart.md).

## C1 — Pages exist and render

- `GET /part-1/chapter-04/walking-skeleton` and the `/vi/…` twin prerender
  with the full reading shell (sidebars, rail, footers, code-block
  titles/copy, figures, suggestion capture, vi banner).
- Canonical/hreflang, OG, TechArticle JSON-LD via the established shell.

## C2 — Battery (per locale)

| Check | Bound |
|---|---|
| Canonical words | 2,000 ≤ w ≤ 4,000 |
| WHY | ≥ 2 |
| TRAP | ≥ 1 |
| SKIP AHEAD | = 1, names `part1-ch4` |
| FORWARD REF | ≥ 1 |
| CHECKPOINT | = 1, closing |
| Figures | 2–4, captioned |
| Baseline | 18 rows; 16 prior rows byte-identical to 016's baseline |

## C3 — Fence ↔ repository (four chapters now)

- Every `title=""` file fence in 1.4 (en AND vi) byte-matches the named
  relay-platform file at HEAD (Dong's `part1-ch4` pins it).
- ALL twenty prior file fences (1.1×10, 1.2×3, 1.3×7) still byte-match at
  the same state (additive-only).
- en/vi fence lists index-aligned and byte-identical; command fences replay
  (`pnpm --filter … dev` starts; curls answer; gate passes).
- The services' tsconfig.json files are identical to the fenced service-kit
  one — stated in prose, verified by diff even though not re-fenced.

## C4 — The skeleton and the gate

- `pnpm install && pnpm lint && pnpm typecheck && pnpm test` green at the
  chapter-end state, ≥40 total tests, no Docker; no fixed ports in tests.
- Started via `pnpm --filter @relay/api dev` and `…/gateway dev` on Node
  ≥22.18: each answers `GET /healthz` with 200, correct JSON shape, and a
  unique `X-Request-Id` per response; unknown routes return the
  EIR-API-04-shaped 404 carrying the request id; every request logs exactly
  one structured JSON line to stdout containing that request_id.
- The gateway's health payload advertises `protocol.frames` and
  `protocol.close_codes` computed from `@relay/protocol` at runtime — the
  lists match the package's actual exports (spot-check: 10 frames, 4 codes).
- The API service's 404 body parses against `@relay/protocol`'s error-frame
  payload schema, asserted in its suite — BOTH services' protocol
  dependencies are exercised, none unused (H1; 1.3's ForwardRef stays true).
- Zero new external RUNTIME dependencies (`node:` builtins + `workspace:*`
  links only); the sole new devDependency is `tsx` (pinned, package-local to
  each service — the surfaced R3 amendment: Node's type stripping cannot
  resolve @relay/protocol's fenced `.js`-convention specifiers); `git status`
  shows only the three new members (+ lockfile/README — never fenced).

## C5 — Derivation fidelity (research R2 is the law)

- Document-sourced properties quote/cite correctly (EIR-API-05, EIR-API-04,
  NFR-OBS-01/06, SAD §4.1's responsibility sentences, ADR-04/05).
- Every DECISION row appears in the chapter WITH its recorded-decision
  marker (request-id format, /healthz path+shape, ports, protocol
  advertisement, `not_found` code placement, log-field deferrals).
- The ID detector passes; no invented requirement/service/endpoint names.

## C6 — Navigation & publishing (Part 1 completes)

- The ONLY tutorial-side source edit outside the two new chapter dirs is the
  1.4 manifest flip.
- After the flip: sidebar Part 1 = exactly 4 linked chapters, 0 forthcoming;
  1.3 footers gain the 1.4 next card (both locales); 1.4 footers show 1.3
  prev and NO next; landings render Part 1 fully linked, Part 2 still in the
  road-ahead list; sitemap = exactly 32 URLs.
- Suggestions: POSTs against both new page paths are accepted (allowlist
  derived, zero edits); the 1.4-forthcoming rejection case from 016's battery
  now inverts — worth one explicit re-check.

## C7 — Vietnamese parity & register

- Box/figure/fence counts match en; fences byte-identical incl. titles.
- Settled register and glossary ("bộ khung biết đi" as the title term,
  "package"/"service" English, "cửa ải"/"vượt qua", "bản giao kèo", no
  calques/hyphenated compounds/"hình hài"); naturalization self-review done
  before presenting; Dong's read-through precedes the commit.

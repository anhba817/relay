# Research: Tutorial Chapter 1.4 — Walking Skeleton

All Technical Context unknowns resolved.

## R1 — Three additive workspace members, one shared home

**Decision**: `packages/service-kit` (`@relay/service-kit`) holds the
operational plumbing both services need — the structured logger, request-id
generation/propagation, and a minimal `serve()` wrapper over `node:http` —
with `services/api` (`@relay/api`) and `services/gateway` (`@relay/gateway`)
as thin consumers (~40 lines each). All three are private workspace packages
mirroring the established shape (type module, exports → src/index.ts or a
main.ts entry, typecheck script, tsconfig extending the base). Services
depend on `@relay/protocol` and `@relay/service-kit` via `workspace:*`.

**Rationale**: The plumbing is needed twice on day one — duplicating it is
exactly the copies-drift disease 1.1's TRAP taught, which makes the kit
package the chapter's narrative gift (the TRAP writes itself). Naming: the
SAD §4.1 fixes the *service* names (API service, gateway); `service-kit` is a
recorded decision. Package-local dependency discipline continues — though
this chapter needs none: node builtins only.

**Alternatives considered**: duplicating logger/request-id into each service
(the TRAP, rejected by the series' own rule); putting the plumbing in
`@relay/config` (that package's charter is constants and tool fragments —
editing its fenced files is also forbidden); a third-party framework
(Fastify/Express — a dependency for routing two paths; boring-by-design says
node:http until a requirement demands more); shipping the gateway as the only
service (SAD §4.1 marks both Phase 1, and ADR-04/05's division is the
teaching).

## R2 — The observable-skeleton derivation table

Same derive-or-mark discipline as 1.3. Every property cites its source;
**DECISION** rows are recorded chapter decisions.

| Item | Content | Source |
|---|---|---|
| Request ID on every response | `X-Request-Id` header, unique per request | EIR-API-05 |
| Request ID format | `crypto.randomUUID()` | **DECISION** (EIR-API-05 fixes uniqueness, not format) |
| Structured logs | one JSON object per line to stdout: `time`, `level`, `service`, `msg`, `request_id` where a request exists | NFR-OBS-01 + constitution ("structured JSON logs with request ID…") |
| Log fields deferred | `tenant_id` (no tenants until Part 2's data paths), `trace/correlation` (OpenTelemetry is NFR-OBS-02, later) — named deferrals, logged schema leaves room | **DECISION** recording the deferral, mirroring 1.3's `request_id` precedent |
| Health endpoint | `GET /healthz` → 200 JSON `{ status: "ok", service, uptime_s }` | **DECISION** (the compose healthchecks of 1.2 set the /healthz precedent; no doc fixes service paths) |
| Gateway health extra | the protocol vocabulary it speaks: frame-type names + close codes, derived at runtime from `@relay/protocol` exports | **DECISION** — makes 1.3's "the skeleton speaks nothing else" visible (R5) |
| Unknown-route response | EIR-API-04's error shape `{ code, message, docs_url }` with `code: "not_found"` + the request id via header | EIR-API-04 (shape); `not_found` joins the registry story (**DECISION**: REST codes live with services until an API chapter owns them — the protocol package's fenced files cannot be edited) |
| Service names | `api`, `gateway` | SAD §4.1 |
| Division of labor taught | API owns REST semantics and is the only Postgres writer; gateway terminates WebSockets and never writes | SAD §4.1, ADR-04, ADR-05 |
| Local ports | API 4000, gateway 4001, each overridable via `PORT` | **DECISION** (no doc fixes local ports; 3000 belongs to the tutorial site) |
| Traceability promise | request ID → logs within 5 minutes | NFR-OBS-06 (quoted as the *why*) |

**Scope boundary (stated in the chapter)**: no store connections, no JWT, no
WebSocket sessions, no real endpoints — Part 2 grows each muscle onto this
skeleton and extends the log schema as the deferred fields become real.

## R3 — Running TypeScript services (amended at implementation, surfaced)

**Decision (as implemented)**: Services run via **tsx** (`^4.23.1`, a
devDependency of each service — package-local, pinned within the major):
`"dev": "tsx watch src/main.ts"`, started with `pnpm --filter @relay/api dev`
(gateway likewise). The three new tsconfigs still add
`"erasableSyntaxOnly": true` — hygiene that keeps the sources compatible with
Node's native stripping for the day it suffices.

**Why the original zero-dependency decision fell**: the plan was plain
`node --watch src/main.ts` (Node ≥ 22.18 type stripping). It works for leaf
files — verified — but **Node does not rewrite import specifiers**, and
`@relay/protocol`'s internals use the standard TS ESM convention
(`export * from "./frames.js"` resolving to `frames.ts` under tsc/vitest).
The gateway's very first cross-package import crashed with
`ERR_MODULE_NOT_FOUND` (empirically confirmed, with and without
`--experimental-transform-types`). The protocol package's files are 1.3
fences — rewriting their specifiers is forbidden — so the smallest tool that
resolves the TS convention wins: tsx, R3's own named fallback. The chapter
teaches this arc honestly (platform-native attempted, resolver wall hit,
smallest dependency taken) — a better lesson than the clean story.

**Alternatives considered**: plain node type stripping (fell as above);
editing @relay/protocol's specifiers to `.ts` (fence violation + would need
`allowImportingTsExtensions` in a fenced tsconfig); tsc build + node dist
(a build step against the base's noEmit — machinery); deep relative imports
bypassing the package boundary (worse than any dependency); adding root
convenience scripts (1.1 fence — still declined; `--filter` suffices).

## R4 — Tests without daemons or fixed ports

**Decision**: Each service exports its server factory (`createServer()`
separated from the `main.ts` listen call); tests boot it on **port 0**, hit
`/healthz` with `fetch`, and assert: 200, response shape, `X-Request-Id`
present and UUID-shaped, distinct across two requests. The kit's logger takes
an injectable sink (defaults to stdout) so tests capture and assert log
structure (valid JSON, required fields, request_id propagation) without
scraping process output. Kit suite covers logger shape + request-id
uniqueness; per-service suites cover the boot + health + 404-shape behavior.
Target ≥8 new tests (gate 32 → ≥40).

**Rationale**: Real behavior (a served HTTP response), no Docker, no fixed
ports (parallel vitest workers), no snapshotting stdout. The injectable sink
is the smallest seam that makes logging testable — and it is itself a
teaching beat (observability you can't test rots).

**Alternatives considered**: supertest (a dependency; `fetch` against port 0
does the job); pure handler unit tests without listening (misses the header/
listen wiring the chapter demonstrates); spawning real processes in tests
(slow, flaky, port collisions).

## R5 — The gateway advertises its contract

**Decision**: The gateway's `/healthz` payload includes
`protocol: { frames: [...], close_codes: [...] }`, derived at runtime from
`@relay/protocol`'s exports — frame type names introspected from the
discriminated union (zod 4 API verified against the installed package at
implementation; fallback: a `FRAME_TYPES` derivation via the union's options),
close codes from `CLOSE_CODES` keys. The API service's consumption is equally
real (H1 remediation): its REST error envelope is **asserted to parse against
the protocol package's error-frame payload schema** — `main.test.ts` imports
`errorFrameSchema` from `@relay/protocol` and validates the live 404 body
with it, making the EIR-API-04 alignment between REST errors and WS error
frames executable rather than claimed (constitution IV: one error shape, one
home). Both services therefore import `@relay/protocol` meaningfully — which
keeps 1.3's ForwardRef sentence ("the walking skeleton's gateway and API
service import @relay/protocol") true without any prose churn.

**Rationale**: 1.3 promised the skeleton "speaks nothing else"; an empty
skeleton can't speak frames over sessions yet, but it can *declare* its
vocabulary from the single source — visible, meaningful, zero drift (the list
is computed, never typed). It also gives the health endpoint honest content
beyond `ok`.

**Alternatives considered**: a hardcoded frame list (drift by construction —
rejected); a stub WebSocket endpoint speaking `connection.ack` (requires
session/auth decisions that belong to Part 2; the spec's "empty must still be
honest" edge case cuts against faking it).

## R6 — The manifest flip that completes Part 1

**Decision**: `lib/tutorial.ts` 1.4 entry: `status: "published"`,
`translatedIn: ["vi"]`, settle placeholders — `readerProduces` "Two running
skeleton services — health-checked, request-ID'd, logging structured JSON" +
`readerProducesVi` "Hai service bộ khung chạy được — có health check, request
ID, log JSON có cấu trúc", `sourceDoc` "docs/04-srs.md, docs/05-sad.md",
`readerMinutes` → 90. Title/titleVi ("Bộ khung biết đi")/path unchanged. This
flip completes Part 1: sidebar renders 4 links + 0 forthcoming, 1.4 gets the
empty next card (the 0.5 state at a new boundary), the landing shows a fully
linked Part 1, sitemap 30 → 32, and the suggestions allowlist admits both new
paths. Part 2 is NOT seeded.

**Rationale**: The 014/016 pattern; 90 minutes for three packages' worth of
typing. Part-completion states all exist in code (built across 004–013) but
render together for the first time — verification treats them as first-run,
not regression.

**Alternatives considered**: seeding Part 2's chapters in the same flip
(spec assumption explicitly defers it — part boundaries are feature
boundaries).

## R7 — English chapter narrative (the beats)

**Decision**: ~2,400 prose words, nine beats:

1. **Cold open — Part 1's last brick**: three chapters built ground no user
   can see; this one stands something up that answers. Walking skeleton
   defined (docs/07's row): deploy the skeleton before the muscles.
2. **SKIP AHEAD**: tag `part1-ch4`; start commands + gate.
3. **WHY #1 (SAD §4.1 · ADR-04/05)**: why THESE two services first — the
   Phase-1 pair; the division of labor quoted (API owns REST and is the only
   Postgres writer; the gateway terminates WebSockets and never writes) —
   the skeleton's shape IS the architecture's shape.
4. **The observability derivation**: EIR-API-05's X-Request-Id, NFR-OBS-01's
   log fields with the honest deferral of tenant/correlation IDs,
   NFR-OBS-06 as the why ("traceable within 5 minutes" starts at line one).
   Figure 1: six services with two solid, health/request-id/log properties
   annotated.
5. **TRAP — the second copy**: the logger is needed by both services; the
   naive move is paste. 1.1's drift lesson replayed on behavior; the fix is
   the kit package. `service-kit` fences (package.json, tsconfig with
   erasableSyntaxOnly explained, src/index.ts).
6. **The two services**: api + gateway fences (package.json ×2, main.ts ×2);
   the gateway's protocol advertisement (R5) with the 1.3 callback; the
   EIR-API-04-shaped 404. WHY #2 (the run-pattern story, amended R3): we
   tried the platform-native path — Node ≥22.18 strips types and runs a leaf
   file beautifully — and hit the resolver wall on the first cross-package
   import (Node doesn't rewrite the TS `.js` convention @relay/protocol's
   fenced internals use). The smallest tool that resolves it is tsx, taken
   deliberately, package-local, pinned; `erasableSyntaxOnly` stays as the
   forward-compatible guarantee. Teach the failed attempt honestly.
7. **Run it**: `pnpm --filter @relay/api dev`, curl /healthz (both), the
   response header and the log line shown side by side — one request ID
   threading through. Figure 2: the request-id thread (request → header →
   log line → grep).
8. **Tests + gate**: ephemeral-port pattern, injectable sink; suite fences;
   the gate run (≥40 tests). Figure 3: Part 1 complete — the four-chapter
   gate flow ending at `part1-ch4`.
9. **FORWARD REF** (Part 2 grows the muscles: JWT + sessions + stores + the
   real send path; tenant/correlation log fields arrive with their features;
   containers in Part 6) + your-turn exercises (kill a service and watch the
   other keep answering; grep a request id across interleaved logs; add a
   temporary route and watch the 404 test object) + takeaways + CHECKPOINT
   (both services answering, gate ≥40 green — Part 1 done) + footer.

Battery: WHY 2, TRAP 1, SKIP 1, FWD 1, CHK 1, figures 3.

**Rationale**: The proven arc; the Part-1-finale framing gives the cold open
and checkpoint real weight.

**Alternatives considered**: teaching HTTP-server mechanics (node:http is
deliberately beneath the chapter's attention — the subject is operational
discipline, not routing).

## R8 — Vietnamese chapter conventions

**Decision**: Naturalized register per the settled glossary and all standing
corrections: **package**/**service** English, "cửa ải"+"vượt qua", "bản giao
kèo", "quả ngọt", "tin nhắn", "bộ khung biết đi" (the seeded title term);
meaning-first, no calques or hyphenated compounds, no "hình hài"; fences
byte-identical incl. titles; figure labels translated; naturalization
self-review before presenting; Dong reads before committing (suggestions
channel live as backstop).

**Rationale**: Settled feedback, fourth application.

**Alternatives considered**: none.

## R9 — What stays out (and where it's promised)

**Decision**: Out: JWT verification and WS sessions (Part 2), store
connections and real endpoints (Part 2), tenant/correlation log fields (with
their features), OpenTelemetry + metrics + alerts (NFR-OBS-02/03/04, later),
compose entries and Dockerfiles for services (Part 6 / docs/07 §6.1), a
process manager (two terminal tabs are honest at this scale — noted in
prose), Part 2 manifest seeding (its own feature).

**Rationale**: docs/07's row scope; each exclusion named in the chapter.

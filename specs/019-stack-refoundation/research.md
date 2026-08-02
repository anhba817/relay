# Research — Stack Re-foundation (Turborepo, NestJS, Drizzle)

All versions below were read from the registry on 2026-08-01 (`pnpm view`).
Per AGENTS.md discipline, every behavioral claim about a library is
re-verified against the *installed* package at implement time; decisions
below record the intended shape and the named fallback if verification
fails.

## R1 — Turborepo adoption shape (chapter 1.1)

**Decision**: `turbo` ^2.10 (registry: 2.10.8), pinned as a root
devDependency. A root `turbo.json` declares four tasks:

- `typecheck` — per-package (`tsc --noEmit` scripts already exist in every
  package), `dependsOn: ["^build"]` so declaration-consuming packages wait
  for their dependencies' dist once builds exist.
- `test` — per-package `vitest run`, `dependsOn: ["^build"]`.
- `build` — per-package where a package has one (none at part1-ch1; the
  protocol/service-kit builds arrive with revised 1.4), `outputs:
  ["dist/**"]`, `dependsOn: ["^build"]`.
- lint — remains ONE whole-repo ESLint invocation (the 1.1 "one lint
  config" story is kept literally), registered as a turbo **root task**
  (`//#`-style) so it is cached like everything else; its cache unit is
  the repo, which is honest — ESLint's config graph is repo-global. Exact
  root-task script naming is settled at implement against installed turbo.

The root gate scripts keep their names — `pnpm lint && pnpm typecheck &&
pnpm test` remains the reader's contract — but each now delegates to
`turbo run`. The root `vitest.config.ts` (one include for the whole
workspace) retires; each package owns `"test": "vitest run"` and vitest's
default include (`**/*.{test,spec}.*`) picks up its own `src` tests.
`.turbo/` joins `.gitignore`.

**Why the `*.itest.ts` trick survives**: vitest's default include requires
the literal `.test.` / `.spec.` segment; `repository.itest.ts` matches
neither, so the integration lane stays invisible to per-package unit runs
exactly as it was invisible to the root include. Verified at implement
with the installed vitest 4.

**Rationale**: ADR-17 verbatim — task graph + content-hash caching over
unchanged pnpm; every turbo target stays an ordinary package script;
deleting `turbo.json` degrades to `pnpm -r`.

**Alternatives considered**: running `test` as a single root task
(preserves the old root vitest config and 1.3's fence untouched) —
rejected because it forfeits per-package caching for the gate's slowest
lane and leaves 1.1's turbo teaching hollow; Nx and plain `pnpm -r` were
rejected in ADR-17 itself.

**Consequence (FR-004 exercised)**: per-package `test` scripts mean
`@relay/protocol`'s `package.json` — a 1.3 fence — gains two lines
(`"test": "vitest run"` under scripts). Chapter 1.3 therefore joins the
revision set **minimally**: fence updated in place, zero-word revision
note (R6), prose otherwise untouched. The *build* script and dist exports
for the protocol package are NOT part of 1.3 — they arrive as a
**diff-fence in revised 1.4** (the chapter whose `nest build` need causes
them), so each amendment lives where its need arises. `@relay/config`'s
`package.json` is a 1.1 fence (revised anyway) and gains its test script
there.

## R2 — NestJS service shape (chapter 1.4)

**Decision**: `@nestjs/core`, `@nestjs/common`, `@nestjs/platform-express`
^11.1 (registry: 11.1.28), `reflect-metadata`, `rxjs`; `@nestjs/cli` ^11
as devDependency. Express platform — the boring default; ADR-15 already
names Fastify as the fallback, and the skeleton exercises no
platform-specific surface.

**Module system**: the API service's `package.json` flips to
`"type": "commonjs"` (a package-local override in the ESM workspace) and
`nest build` emits CommonJS via tsc — the framework's native module
system. Workspace deps (`@relay/protocol`, `@relay/service-kit`) build
**ESM dist + d.ts**; Node ≥22.12's stable `require(esm)` bridges the two.
The engines floor moves to `">=22.12"` **in revised 1.1's root
package.json** (the fence carries it from birth — deciding it at S4 would
force a needless amendment chain to a root 1.1 fence), with 1.4 teaching
why the floor exists. This is itself a teaching beat: the workspace stays
ESM, the framework keeps its native dialect, Node's bridge is named and
dated. **Verify at
implement** (boot `nest build && node dist/main.js` importing protocol
dist); **fallback**: dual-emit protocol/service-kit (tsup) if the bridge
trips on anything.

**tsconfig rescope**: `services/api/tsconfig.json` drops
`erasableSyntaxOnly` and gains `experimentalDecorators` +
`emitDecoratorMetadata` (ADR-15's stated trade-off, taught); gateway,
service-kit, protocol, config keep `erasableSyntaxOnly` — the guarantee is
rescoped, not abandoned, and revised 1.4 + 2.1 tell one consistent story.

**Dev runner**: api `"dev": "nest start --watch"` (tsc watch → node
dist); tsx remains the gateway's runner (its 1.4 story about the
`.js`-specifier resolution stays true for the gateway half). The api's
tsx devDependency retires.

**Unit tests under decorators**: esbuild (vitest's default transform)
does not emit decorator metadata; the documented NestJS+Vitest pairing is
`unplugin-swc` + `@swc/core` in the api's own `vitest.config.ts`. Adopted
for the api package only. Verify at implement; fallback: keep api unit
tests DI-free (construct controllers by hand), which the walking
skeleton's surface permits.

**Skeleton content**: root `AppModule`, health controller (same
endpoint/shape as today), request-id + structured-log wiring reusing
`@relay/service-kit` (rewritten in 1.4 as before, now also consumed
through Nest middleware/interceptor idiom). Boundary validation pipes are
named as trajectory (bodies arrive with 2.2's write path) — the skeleton
has no request bodies to validate.

## R3 — Drizzle data layer shape (chapter 2.1)

**Decision**: `drizzle-orm` ^0.45 (registry: 0.45.2) over the existing
`pg` Pool via `drizzle-orm/node-postgres`; `drizzle-kit` ^0.31 (0.31.10)
as devDependency with `drizzle.config.ts`.

- `src/db/schema.ts` — the TS schema mirroring SAD §6.1 (tables, FKs,
  CHECKs, the DR-03 partial unique index via Drizzle's
  `uniqueIndex(...).where(...)`, hot-path indexes).
- **Migrations**: drizzle-kit `generate` produces the SQL; the SQL is
  reviewed and diffed against §6.1 (ADR-16's drift check, performed in
  the chapter); the existing ~50-line hand-rolled runner **stays** and
  applies plain SQL files exactly as before — forward-only, versioned,
  `schema_migrations` ledger. drizzle-kit's own migrator/journal is not
  used (one applier, ours). The 018 migration file is regenerated through
  this flow so the chapter's story and the repo's history agree.
- **Repository**: stays a plain class beneath the framework —
  `new Repository(db, environmentId)` with `db: NodePgDatabase<schema>`;
  the constructor still *requires* the tenant. The NestJS request-scoped
  provider idiom is explicitly deferred to 2.2, when endpoints exist to
  inject into — the layer exists before its callers, as before. Queries
  move to Drizzle; raw-SQL islands permitted per ADR-16.
- **Lint ban extended**: `no-restricted-imports` outside
  `services/api/src/db/**` now bans `pg`, `drizzle-orm`, and
  `drizzle-orm/*` (patterns entry) — the re-derived 2.1 diff-fence.
- The isolation suite (`*.itest.ts`) keeps its four attacks and its
  localhost-only guard; assertions move to Drizzle query results.

**Alternatives considered**: drizzle-kit `migrate` as the applier —
rejected (two migration ledgers, and the hand-rolled runner is a retained
teaching artifact ADR-16 explicitly preserves); rewriting migrations by
hand and skipping `generate` — rejected (the generate→review→diff flow IS
the chapter's ADR-16 beat).

## R4 — The rebase and tag mechanics

**Decision**: relay-platform's history is rebuilt as five clean states
(S1..S5 = part1-ch1, part1-ch2, part1-ch3, part1-ch4, part2-ch1), each
state passing its gate before the next is layered on:

- **S1** (1.1 revised): workspace + turbo + `@relay/config` (with test
  script) + root gate through turbo. No build targets yet — `turbo run
  build` is an empty, declared task.
- **S2** (1.2 unchanged): compose stack + infra test — byte-identical
  files to today's tag except inherited S1 root files.
- **S3** (1.3 minimally revised): protocol package with `test` script;
  everything else byte-identical.
- **S4** (1.4 rewritten): NestJS api + frameworkless gateway +
  service-kit (now with build) + protocol build/dist-exports via the
  1.4 diff-fences.
- **S5** (2.1 revised): Drizzle schema/repository/migrations + extended
  eslint ban via re-derived diff-fences + integration lane.

Dong performs all commits and re-tags the five names; whether the current
states survive under archive names (e.g. `part1-ch1-v1`) is Dong's call
at tag time — the working tree this feature produces makes either choice
a pure tag operation. Verification (quickstart) checks out each tag and
runs its gate; `part2-ch1` additionally runs the integration lane against
the compose Postgres. Never Dong's Neon.

## R5 — The revision-note mechanism

**Decision**: a new tutorial component, `<RevisionNote>` — props-only and
self-closing (`<RevisionNote locale="vi" date="2026-08" adr="ADR-15"
summary="..." />`-shaped; exact props at implement), rendered directly
under the chapter header. Because the battery's word counter skips lines
starting with `<`, a props-only component contributes **zero canonical
words** — but ONLY if the usage is a **single line**: continuation lines
of a prettier-wrapped call don't start with `<` and would leak prop words
into the count (Figure caption lines demonstrably count this way today).
The single-line rule is therefore part of the mechanism, documented in
the component and enforced by 1.3's word-count-unchanged check — the
"decided once, recorded" answer to the spec's battery edge case, applied
identically in both locales. Exactly
the revision set's chapters (1.1, 1.3, 1.4, 2.1 × 2 locales) carry one;
each names its driving ADR (1.3's names ADR-17, whose task graph caused
its two-line touch).

## R6 — Battery baselines and measurement

**Decision**: the 019 baseline regenerates all 20 rows. Expected deltas:
1.1 en/vi, 1.4 en/vi, 2.1 en/vi (six rows) change word counts within
2,000–4,000; **1.3's rows stay byte-identical** (its only changes are
fence content — excluded from the word measure — and a zero-word note);
all Part 0, 1.2 rows byte-identical. Any other delta is a defect.

## R7 — Vietnamese editions

**Decision**: unchanged flow — vi fences built by «Fn» marker
substitution from en for byte-identity; prose at the naturalized register
per the settled glossary ("package", "cửa ải"/"vượt qua", "bản giao kèo",
"tin nhắn", "thêm chi tiết", "bộ khung biết đi" for the walking skeleton);
naturalization self-review before presenting; Dong reviews before commit.

## R8 — Teaching-beat ledger (what dies, what replaces it)

| Chapter | Beat that dies | Replacement (failure-first) |
|---|---|---|
| 1.1 | `pnpm -r` as the whole gate story | The false-green cache: an undeclared input demonstrated, then the input declared — ADR-17's trade-off on camera |
| 1.4 | tsx-vs-type-stripping workaround as the *api's* runner story | The framework boundary: why the gateway refuses the framework (ADR-15's scope clause), plus the ESM/CJS bridge as a named production reality; the tsx story survives gateway-side |
| 1.4 | `erasableSyntaxOnly` as workspace-wide guarantee | The rescope taught as ADR-15's explicit trade-off: what the flag still protects (gateway, packages) and what buys its release (DI metadata) |
| 2.1 | Constructor-parameter-property trap under `erasableSyntaxOnly` | The schema-twice drift risk: TS schema vs §6.1 SQL, and the generate→review→diff discipline that checks it (ADR-16's mitigation) |

## R9 — Tutorial-site surface

**Decision**: no manifest, sitemap, navigation, or allowlist changes
(FR-011); the only site-code addition is the `RevisionNote` component and
the revised chapter/figure files. relay-platform's README "Deliberately
not yet" Turborepo entry is rewritten in place to record adoption via
ADR-17 (FR-010), preserving the original trigger text as history rather
than deleting it.

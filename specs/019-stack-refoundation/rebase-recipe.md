# Rebase recipe — feature 019 (for Dong)

The working tree of `relay-platform` currently holds **S5** (the final
state). The five chapter tags must be re-cut on a rebuilt history whose five
commits are S1..S5. Per-state file trees were verified green (see
`scratchpad/019-states/GATE-MATRIX.md` in the session scratchpad, and the
DERIVATIONS.md beside it); this recipe reconstructs each commit from the
final tree using git only — no content is retyped.

> All commands are yours to run; nothing here has been committed, tagged, or
> pushed. Decide first whether to archive the current tags
> (`git tag part1-ch1-v1 part1-ch1` … before moving them) — both options
> below work either way.

## The five states, as file sets

Every state = the FINAL content of the listed files (later states never
rewrite earlier files except the ones listed under "amended"):

- **S1 → `part1-ch1`**: `.gitignore .nvmrc .prettierrc README.md
  package.json pnpm-workspace.yaml tsconfig.base.json turbo.json
  eslint.config.mjs@PRE-BAN packages/config/{package.json,tsconfig.json,
  src/index.ts,src/index.test.ts}` + `services/.gitkeep` + lockfile.
  ⚠ Two files are NOT at final content at this state:
  `eslint.config.mjs` (pre-ban — the text of revised 1.1's fence) and no
  `infra.*` in packages/config yet.
- **S2 → `part1-ch2`**: + `compose.yaml`,
  `packages/config/src/infra.{ts,test.ts}`.
- **S3 → `part1-ch3`**: + `packages/protocol/{package.json@S3,tsconfig.json,
  src/*}` — package.json at S3 has the `test` script but NOT the build
  script/dist exports (that is revised 1.3's fence text; the build arrives
  as revised 1.4's diff-fence).
- **S4 → `part1-ch4`**: + `packages/service-kit/*` (with build),
  `packages/protocol/{package.json,tsconfig.build.json}@final`,
  `services/api/*` WITHOUT `src/db/`, `drizzle.config.ts`, `migrations/`,
  `vitest.integration.config.mts`; + `services/gateway/*`.
- **S5 → `part2-ch1`**: everything else (the db layer, migrations+meta,
  drizzle config, integration config, `eslint.config.mjs@final`,
  api `package.json@final`).

The three content-versioned files and where their intermediate texts live:

| File | S-intermediate text is in |
|---|---|
| `eslint.config.mjs` (S1–S4) | revised 1.1's fence (en or vi — byte-identical) |
| `packages/protocol/package.json` (S3) | revised 1.3's fence |
| `services/api/package.json` (S4) | revised 1.4's fence |

## Suggested command sequence (orphan rebuild)

```bash
cd relay-platform
git checkout --detach                       # keep main untouched until the end
git checkout --orphan refound
git rm -rf --cached . && git clean -fdx -e node_modules -e .env   # careful: review first
# ...restore the working tree from main:
git checkout main -- .                      # full S5 content, staged fresh
```

Then per state: `git reset` everything, `git add` the state's file set (with
the three intermediate files temporarily set to their fence text for
S1/S3/S4 — copy from the chapter fences, then restore), commit, and continue
adding. Suggested commit messages:

1. `feat: workspace + toolchain on a Turborepo task graph (chapter 1.1, ADR-17)`
2. `feat: one-command local infrastructure (chapter 1.2)`
3. `feat: @relay/protocol — the wire contract (chapter 1.3)`
4. `feat: walking skeleton — NestJS api, frameworkless gateway (chapter 1.4, ADR-15)`
5. `feat: schema with a spine — Drizzle repository layer (chapter 2.1, ADR-16)`

Run `pnpm install` before each commit so the lockfile matches that state,
and run the gate at each commit (`pnpm lint && pnpm typecheck && pnpm test`;
at 5 also the integration lane). Then re-point the tags and main:

```bash
git tag -f part1-ch1 <sha1>   # or delete+recreate; -f moves them
git tag -f part1-ch2 <sha2>
git tag -f part1-ch3 <sha3>
git tag -f part1-ch4 <sha4>
git tag -f part2-ch1 <sha5>
git branch -f main refound && git checkout main
git push --force-with-lease origin main
git push --force origin part1-ch1 part1-ch2 part1-ch3 part1-ch4 part2-ch1
```

(Archive variant: before the `-f` re-tags, `git tag part1-chN-v1 part1-chN`
for each and `git push origin 'refs/tags/*-v1'`.)

## Push order across the three repos

1. `relay-platform` (commits + tags as above)
2. `relay-tutorial` (single commit; suggested:
   `feat: stack re-foundation — revise 1.1/1.3/1.4/2.1 for ADR-15/16/17, add RevisionNote`)
3. Parent repo: pin both submodules + spec artifacts (suggested:
   `docs: spec artifacts for 019-stack-refoundation; ADR-15/16/17 docs; constitution v1.1.0; pin submodules`)

## Review list before committing

- vi read-throughs: 1.1, 1.4, 2.1 (revised prose), 1.3 (note only)
- The RevisionNote copy in both locales (component:
  `components/tutorial/revision-note.tsx`)
- The 1.3 two-line fence change
- Tag strategy: move-in-place vs archive `-v1` names

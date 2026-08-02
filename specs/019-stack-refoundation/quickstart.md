# Quickstart — validating the re-foundation

Prerequisites: Node ≥22.12, pnpm 10, Docker (integration lane only),
both submodules checked out at the feature's final state.

## 1. The five-tag gate sweep (contract C1)

For each tag T in part1-ch1 part1-ch2 part1-ch3 part1-ch4 part2-ch1:

```bash
cd relay-platform && git checkout T && pnpm install
pnpm lint && pnpm typecheck && pnpm test          # green, Docker stopped
```

Expect: from part1-ch1 onward the runs go through turbo (task summary
visible); repeat a command to see a cache hit; `pnpm turbo run test --force`
stays green (cold correctness). Before Dong re-tags, run the same sweep on
the five prepared states by commit.

## 2. Services boot (at part1-ch4)

```bash
docker compose up -d --wait                        # 1.2's stack
pnpm --filter @relay/api build && pnpm --filter @relay/api dev &   # nest
pnpm --filter @relay/gateway dev &                 # tsx, frameworkless
curl -s localhost:<api-port>/health                # ok + request id in logs
```

## 3. Migrations + isolation (at part2-ch1, contract C1/C6)

```bash
docker compose up -d --wait postgres
pnpm --filter @relay/api migrate                   # applies; re-run = no-op
pnpm --filter @relay/api test:integration          # 4 attacks pass, localhost only
```

Also: add a temporary `import pg from "pg"` in a non-db file → `pnpm lint`
fails naming constitution I; same for `drizzle-orm`. Remove it.

## 4. Fence + battery sweep (contracts C2/C3/C4/C8)

Run the feature's verification script(s) (established pattern from
016–018, extended for amendment chain B):

- every plain fence vs its chapter's tag (per-chapter pinning);
- 2.1 diff-fences vs revised 1.4 text and part2-ch1 files;
- 1.4 diff-fences vs 1.3 text and part1-ch4 files;
- en/vi fence byte-identity; invented-ID detector;
- battery v3 vs `battery-baseline.txt` — exactly six rows differ from
  018's baseline.

## 5. Site surface frozen (contract C7)

```bash
cd relay-tutorial && pnpm lint && pnpm build       # green
```

Diff the built sitemap URL set against the pre-feature one (identical);
spot-check both landings and a Part-1 sidebar (no rendering change);
confirm `<RevisionNote>` renders on exactly the eight revised pages and
nowhere else (`grep -rl RevisionNote app/` matches the revision set only).

## 6. README + docs cross-check (contract C5)

relay-platform README's "Deliberately not yet" section records Turborepo
as adopted per ADR-17 (original trigger preserved as history); chapters
cite ADR-15/16/17 where the plan says; no chapter still claims
`erasableSyntaxOnly` is workspace-wide.

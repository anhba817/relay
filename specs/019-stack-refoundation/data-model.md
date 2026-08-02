# Data Model — Stack Re-foundation

A content-revision feature's "data" is the chapter/fence/tag structure it
must keep consistent. (The *database* schema is content-identical to
018's — see research R3; only its expression changes.)

## Entities

### Tag lineage (the five states)

| State | Tag | Chapter | Status this feature | Gate at tag |
|---|---|---|---|---|
| S1 | `part1-ch1` | 1.1 | REVISED — turbo over pnpm | 3 commands, Docker-free, via turbo |
| S2 | `part1-ch2` | 1.2 | CONTROL — byte-unchanged files | same + compose demo replays |
| S3 | `part1-ch3` | 1.3 | MINIMAL — protocol test script (FR-004) | same |
| S4 | `part1-ch4` | 1.4 | REWRITTEN — NestJS api, frameworkless gateway | same; services boot |
| S5 | `part2-ch1` | 2.1 | REVISED — Drizzle repository | same + integration lane vs compose |

Invariants: each state passes its own gate before the next is layered;
each chapter's fences byte-match its own state; tag names are reused;
re-tagging is Dong's operation (archive names optional, Dong's call).

### The revision set

`{1.1, 1.3, 1.4, 2.1} × {en, vi}` — eight page.mdx files; figures.ts
expected touched for 1.1, 1.4, 2.1 (both locales). Every member carries
exactly one `<RevisionNote>` naming its driving ADR (1.1→ADR-17,
1.3→ADR-17, 1.4→ADR-15, 2.1→ADR-16). No non-member carries one (SC-006).

### The control set

`{Part 0 (0.1–0.5), 1.2} × {en, vi}` — zero byte changes to pages,
figures, or battery rows. 1.2's fences byte-match at re-cut `part1-ch2`.

### Fence inventory and amendment chains

- **Plain fences**: every `title=""` file fence byte-matches the file at
  its own chapter's re-cut tag.
- **Amendment chain A (existing, re-derived)**: 2.1's diff-fences —
  pre-image = revised 1.4's published fence text (at S4), post-image =
  file at S5. Members: `services/api/package.json`, `eslint.config.mjs`
  (ban now includes drizzle-orm).
- **Amendment chain B (new)**: 1.4's diff-fences against 1.3 —
  pre-image = 1.3's published fence text (at S3), post-image = file at
  S4. Members: `packages/protocol/package.json` (build script +
  dist exports), protocol build tsconfig if expressed as a diff (or as a
  new-file plain fence — implement decides; new-file fences need no
  pre-image).
- **Re-pin rule**: an amended chapter's own fence battery pins to its own
  tag (1.3's checks run at S3), exactly as 018 established for 1.4.

### RevisionNote (tutorial component)

Props-only, self-closing, zero canonical words (R5) — usage is strictly
ONE line (`<RevisionNote … />`; wrapped prop lines would count as prose,
per R5). Fields: locale, revision date (2026-08), driving ADR id(s),
short summary string (rendered by the component, not counted).
Placement: directly below `<ChapterHeader>`. State: exists on
revision-set members only. 1.3's word-count-unchanged baseline check is
the rule's mechanical backstop.

### Battery baseline (019)

20 rows. Allowed deltas vs 018's baseline: exactly the six rows for
1.1/1.4/2.1 × en/vi; the fourteen others (including both 1.3 rows —
zero-word note, fence-only edits) byte-identical. Word counts stay in
2,000–4,000.

### Platform workspace (post-S5 shape)

- Root: gate scripts delegate to turbo; `turbo.json` declares
  lint(root-task)/typecheck/test/build; no root vitest config.
- Packages `config`, `protocol`, `service-kit`: own `test` scripts;
  `protocol` + `service-kit` own `build` → ESM dist + d.ts, exports →
  dist (from S4).
- `services/api`: CJS NestJS app (`nest build`/`nest start`), SWC-backed
  vitest unit config, drizzle schema + retained SQL runner, itest lane.
- `services/gateway`: unchanged shape — ESM, tsx, frameworkless.
- eslint: one root flat config; restricted imports outside
  `services/api/src/db/**`: `pg`, `drizzle-orm`, `drizzle-orm/*`.

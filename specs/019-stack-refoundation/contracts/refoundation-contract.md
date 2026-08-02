# Contract — Stack Re-foundation (feature 019)

Binding checks. Each is machine-verifiable at implementation's end;
violation of any is a defect, not a judgment call.

## C1 — Per-tag gate matrix

At every re-cut tag (`part1-ch1`, `part1-ch2`, `part1-ch3`, `part1-ch4`,
`part2-ch1`), with Docker stopped:

```
pnpm install && pnpm lint && pnpm typecheck && pnpm test   # all green
```

From `part1-ch1` onward these run through `turbo run`; a second
invocation may be cache-hot but MUST also be green cold
(`--force` / fresh clone). At `part1-ch4`: both services boot (api via
nest, gateway via tsx) and health checks answer. At `part2-ch1`, with the
compose stack up: `pnpm --filter @relay/api migrate` applies cleanly to a
fresh database AND re-runs as a no-op; `pnpm --filter @relay/api
test:integration` passes while attacking with foreign environment_ids
against localhost only.

## C2 — Fence contract (series-wide)

- Every `title=""` file fence in every published chapter byte-matches the
  file at that chapter's own re-cut tag.
- 2.1 diff-fences: strip-`+` == revised 1.4's published fence text;
  strip-`-` == file at `part2-ch1`.
- 1.4 diff-fences (new chain): strip-`+` == 1.3's published fence text;
  strip-`-` == file at `part1-ch4`.
- en/vi fences byte-identical, including diff-fences.
- Every fenced command replays with the output the prose claims.

## C3 — Control set is byte-frozen

`git diff` over the tutorial repo for this feature touches NO file under
Part 0 or chapter 1.2 (either locale), and 1.2's platform-side fences
byte-match at `part1-ch2`. The 019 battery baseline differs from 018's in
exactly the six rows of 1.1/1.4/2.1 × en/vi.

## C4 — Revision notes

Rendered notes appear on exactly {1.1, 1.3, 1.4, 2.1} × {en, vi}, each
naming its driving ADR (17, 17, 15, 16); zero other pages render one; the
component contributes zero words to the battery's canonical count.

## C5 — ADR fidelity

The implemented shapes match the accepted records: framework in
services/api only (gateway package.json has NO framework dependency);
migrations remain versioned forward-only `.sql` applied by the retained
runner, with the drizzle-kit-generated SQL diffed against SAD §6.1 and
the diff's disposition recorded in the chapter; turbo targets are
ordinary package scripts (deleting turbo.json leaves `pnpm -r` able to
run the same scripts); `erasableSyntaxOnly` remains ON everywhere except
`services/api`.

## C6 — Isolation machinery survives

Repository construction without an `environment_id` is a compile error;
the eslint restriction forbids `pg` AND `drizzle-orm` imports outside
`services/api/src/db/**` (verified by a deliberate violation failing
lint); the isolation suite's foreign-tenant attacks pass; the
localhost-only DATABASE_URL guard is intact. Dong's Neon is never
touched by anything in this feature.

## C7 — Site surface frozen

Sitemap URL set, manifest entries, nav rendering, and the suggestions
allowlist are unchanged. The only site-code addition is
`components/tutorial/revision-note.tsx` (plus chapter/figure revisions).
`pnpm build` green.

## C8 — Bilingual parity

For each revision-set chapter: vi structure (boxes, figures, fences,
headings count) matches en; vi register per the settled glossary with
naturalization self-review; battery passes in both locales.

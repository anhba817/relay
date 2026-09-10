# The carry of features 043 and 044 onto the rebuilt chain

Twenty-four commits. Each row records what was decided and why. **A carried commit is a
carried ledger item: measured against the tree, not copied.**

| # | commit | decision | reason |
|---|---|---|---|
| 1 | 89f4109f | SKIP — already applied | The chain retired the port map entirely and binds `PORT=0`, reading the assignment from the child's own `listening` line, in `packages/e2e/src/harness.ts`, `services/gateway/main.ts` and `limits.itest.ts:142`. 043 was still adding the e2e lane TO the map; the chain has no map. Taking it would reintroduce a comment describing a mechanism that no longer exists. |
| 2 | 2c11c79e | APPLIED cleanly | `test(043): the teardown assertion, and the durables the dispatcher left behind`. One new file, no overlap with the rebuild. On the branch as `acdf10d`. |
| 3 | e5c1f19c | SPLIT — skip two thirds, carry one | Three separable concerns. **The reset-lane script and its itest: SKIP.** The chain has its own, and it is stronger — it PLANTS the stale delivery it asserts on (the rebuild found that assertion vacuous against a no-op DELETE and falsified it red), where main's plants nothing and still counts rows "due now". **The eslint exemption: already present** — the chain added `reset-lane.itest.ts` to `DRIVER_EXEMPT` at new 19. **The `connections.test.ts` split: CARRY.** It is the fix for this feature's own open item 045-26: the chain's unit test is 366 lines and opens `redis://localhost:6399`, so the UNIT gate needs a live broker and its failure reads as a defect; main's is 139 lines with the Redis half in `connections.itest.ts`. |

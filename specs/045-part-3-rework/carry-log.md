# The carry of features 043 and 044 onto the rebuilt chain

Twenty-four commits. Each row records what was decided and why. **A carried commit is a
carried ledger item: measured against the tree, not copied.**

| # | commit | decision | reason |
|---|---|---|---|
| 1 | 89f4109f | SKIP — already applied | The chain retired the port map entirely and binds `PORT=0`, reading the assignment from the child's own `listening` line, in `packages/e2e/src/harness.ts`, `services/gateway/main.ts` and `limits.itest.ts:142`. 043 was still adding the e2e lane TO the map; the chain has no map. Taking it would reintroduce a comment describing a mechanism that no longer exists. |
| 2 | 2c11c79e | APPLIED cleanly | `test(043): the teardown assertion, and the durables the dispatcher left behind`. One new file, no overlap with the rebuild. On the branch as `acdf10d`. |
| 3 | e5c1f19c | SPLIT — two thirds skipped, one third FILED | Three separable concerns. **The reset-lane script and its itest: SKIP.** The chain has its own and it is stronger — it PLANTS the stale delivery it asserts on (the rebuild found that assertion vacuous against a no-op DELETE and falsified it red), where main's plants nothing and still counts rows "due now". **The eslint exemption: already present** — the chain added `reset-lane.itest.ts` to `DRIVER_EXEMPT` at new 19. **The `connections.test.ts` split: FILED, not carried.** It is 045-26's fix and is measured on `main` — `12 failed \| 5 passed` against a dead broker, so twelve move and five stay. Its home is the connection-cap chapter, new 16: a fourth mid-chain insertion, outside the set that was authorised. |
| 4 | a8b2b317 | CARRIED into chapter 17 | `a concurrent edit could overwrite a tombstone`. The edit's tombstone check was a READ taken earlier in the same transaction while its write filtered on id alone. Carried WITH its test, and the pairing is the finding: I had taken the test first and it failed one run in three, which read as a flake and was a missing fix. |
| 12 | b3488b87 | SKIP — already present | `max(8000)` is in `messages.schema.ts` from chapter 1, because it arrives with the base; the avatar scheme rule is in `users.schema.ts` and is taught in chapters 10 and 18. 043 consolidated duplicates the rebuild never created. See 045-72 for what this uncovered instead. |
| 13, 14 | a6f63b57, 091447bb | SKIP — already present | The chain registers all six named webhook refusals and has **zero** bare `UnprocessableEntityException`s, and `WEBHOOK_EVENT_TYPES` declares the eight with their `emitted` flags. What was missing was the PROSE, and chapter 19 now has it. |
| 18, 19 | a16e83b9, 0c2f7a13 | CARRIED into chapter 17 | The counter cherry-picked with two deliberate calls; the ack half REIMPLEMENTED against chapter 17's own code rather than cherry-picked, because 043's patch reaches into eight files belonging to chapters 15 and 22. The carry's purpose is the behaviour, not the literal diff. |
| 20, 21 | d4dfed43, 4e3c9fb0 | CARRIED with 18 | 044's counter tests arrived inside commit 18's test block; kept, with chapter 18's five attachment blocks dropped as that chapter's material. |
| 10 | afee4872 | ABSENT, not carried | `drizzle.config.ts` and the `drizzle-kit` dependency are still in the chain, so the generator was never retired there. Tooling: appendix material, no chapter teaches it. |
| 17 | c427e3bf | ABSENT, not carried | `scripts/scale/` does not exist in the chain. A load harness for NFR-SCL-01 is Part 7's subject (load, chaos), not Part 3's. |

**WHERE THE TWENTY-FOUR STAND.** Six decided above by artifact — two carried into chapter 17,
four already present in the chain because the rebuild re-derived them. Two are absent and belong
in the appendix or a later part rather than here. The remaining sixteen are modification-only:
test-lane fixes, coverage pins and title corrections whose substance cannot be tested for by
looking for a file or a symbol, and which need the same read-then-decide each. **None of them
publishes a chapter**, so none changes Part 3's count of 26.

**AND THE PATTERN ACROSS THE SIX IS THE RESULT WORTH KEEPING.** Four of six were already in the
chain, arrived at independently during the rebuild, and in three cases in a stronger form — the
lane reset plants the row it asserts on, the port map is deleted rather than extended, the
exemption list is read from the rule rather than restated. **Cherry-picking them blindly would
have downgraded the chain in every one of those three.** That is the carried-ledger rule applied
to commits, and it has now paid for itself six times out of six.

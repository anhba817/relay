# The carry of features 043 and 044 onto the rebuilt chain

Twenty-four commits. Each row records what was decided and why. **A carried commit is a
carried ledger item: measured against the tree, not copied.**

| # | commit | decision | reason |
|---|---|---|---|
| 1 | 89f4109f | **SPLIT — half already applied, half MISSED and now carried** | Originally logged as SKIP, and that was wrong. The PORT half is genuinely already applied: the chain retired the port map entirely and binds `PORT=0`, reading the assignment from the child's own `listening` line, in `packages/e2e/src/harness.ts`, `services/gateway/main.ts` and `limits.itest.ts:142`. **The TEARDOWN half was not.** This commit also rewrites `stop()` to wait for each child with a measured one-second grace before `SIGKILL`; the chain kept `SIGTERM` then a flat 200 ms sleep. **The subject says both halves — *"binds port 0 AND WAITS FOR ITS CHILDREN"* — and it was read as one.** Carried, with the leak the assertion could not see; see 045-76. |
| 2 | 2c11c79e | APPLIED — **and it was the test without its fix** | `test(043): the teardown assertion, and the durables the dispatcher left behind`. Logged as "one new file, no overlap with the rebuild"; the file count was right and the conclusion was not. The assertion it adds is the assertion for commit 1's `stop()` rewrite, which had been skipped — so the e2e lane was red **3 of 3 runs**, deterministically. **Third instance in this carry of taking a `test(` commit without the `fix(` it proves**, after 043's tombstone and 044's race. Both halves now sit in one commit at the tip. |
| 3 | e5c1f19c | SPLIT — two thirds skipped, one third FILED | Three separable concerns. **The reset-lane script and its itest: SKIP.** The chain has its own and it is stronger — it PLANTS the stale delivery it asserts on (the rebuild found that assertion vacuous against a no-op DELETE and falsified it red), where main's plants nothing and still counts rows "due now". **The eslint exemption: already present** — the chain added `reset-lane.itest.ts` to `DRIVER_EXEMPT` at new 19. **The `connections.test.ts` split: FILED, not carried.** It is 045-26's fix and is measured on `main` — `12 failed \| 5 passed` against a dead broker, so twelve move and five stay. Its home is the connection-cap chapter, new 16: a fourth mid-chain insertion, outside the set that was authorised. |
| 4 | a8b2b317 | CARRIED into chapter 17 | `a concurrent edit could overwrite a tombstone`. The edit's tombstone check was a READ taken earlier in the same transaction while its write filtered on id alone. Carried WITH its test, and the pairing is the finding: I had taken the test first and it failed one run in three, which read as a flake and was a missing fix. |
| 12 | b3488b87 | SKIP — already present | `max(8000)` is in `messages.schema.ts` from chapter 1, because it arrives with the base; the avatar scheme rule is in `users.schema.ts` and is taught in chapters 10 and 18. 043 consolidated duplicates the rebuild never created. See 045-72 for what this uncovered instead. |
| 13, 14 | a6f63b57, 091447bb | SKIP — already present | The chain registers all six named webhook refusals and has **zero** bare `UnprocessableEntityException`s, and `WEBHOOK_EVENT_TYPES` declares the eight with their `emitted` flags. What was missing was the PROSE, and chapter 19 now has it. |
| 18, 19 | a16e83b9, 0c2f7a13 | CARRIED into chapter 17 | The counter cherry-picked with two deliberate calls; the ack half REIMPLEMENTED against chapter 17's own code rather than cherry-picked, because 043's patch reaches into eight files belonging to chapters 15 and 22. The carry's purpose is the behaviour, not the literal diff. |
| 20, 21 | d4dfed43, 4e3c9fb0 | CARRIED with 18 | 044's counter tests arrived inside commit 18's test block; kept, with chapter 18's five attachment blocks dropped as that chapter's material. |
| 5 | cf0b3293 | CARRIED into chapter 13 | `scope presence's outbox count to its own environment`. A whole-table `select count(*) from outbox` asserted unchanged while a neighbour wrote to it — `expected 614255 to be 614250`, naming no neighbour. Gated at chapter 13, where the suite is born. One of the three that were known before the lane was ever run unserialised. |
| 6, 7 | 09c658bf, 6d081a79 | CARRIED into chapter 22 | `sum the budget across windows instead of sleeping` and `stop the budget test straddling a wall-clock minute`. Ten sends across a `floor(now / 60_000)` boundary write two keys and read one: `expected 7 to be 10`, which reads exactly like a limiter dropping increments. Both gated at chapter 22, arriving with the file. |
| 8 | — | THE CONFIG CHANGE THE THREE ABOVE WERE FOR | Dropping `fileParallelism: false` from the api and gateway lanes, gated at chapter 16 and measured at that tag against a fresh database. **The three carried fixes were not enough**: three more places held the lane and two of them are not assertions. 045-74 has the six and the numbers; chapter 16 publishes it. |
| 10 | afee4872 | ABSENT, not carried | `drizzle.config.ts` and the `drizzle-kit` dependency are still in the chain, so the generator was never retired there. Tooling: appendix material, no chapter teaches it. |
| 17 | c427e3bf | ABSENT, not carried | `scripts/scale/` does not exist in the chain. A load harness for NFR-SCL-01 is Part 7's subject (load, chaos), not Part 3's. |

**WHERE THE TWENTY-FOUR STAND.** Ten decided above by artifact — five carried into chapters 13,
17 and 22, one split half-and-half, four already present in the chain because the rebuild
re-derived them. Two are absent and belong in the appendix or a later part rather than here.
The remaining twelve are modification-only: coverage pins and title corrections whose substance
cannot be tested for by looking for a file or a symbol, and which need the same read-then-decide
each. **None of them publishes a chapter**, so none changes Part 3's count of 26.

**AND THE PATTERN ACROSS THE SIX IS THE RESULT WORTH KEEPING.** Four of six were already in the
chain, arrived at independently during the rebuild, and in three cases in a stronger form — the
lane reset plants the row it asserts on, the port map is deleted rather than extended, the
exemption list is read from the rule rather than restated. **Cherry-picking them blindly would
have downgraded the chain in every one of those three.** That is the carried-ledger rule applied
to commits, and it has now paid for itself six times out of six.

**AND THE FAILURE MODE OF THIS LOG IS NOW MEASURED.** Two of its first four rows were wrong, in
opposite directions and for the same reason: **a commit was classified by one of the things it
does.** Row 1 did two things and was skipped for the half already present. Row 2 was accepted as
complete because its file count was right. The carried-ledger rule says measure rather than copy;
the sharper version is **measure every clause of the subject line**, because a commit that does
two things says so there and nowhere else.

**THE `test(` / `fix(` PAIRING IS THE SPECIFIC TRAP.** Three times in this carry — 043's
tombstone, 044's race, 043's teardown — the test was taken and its fix was not, and every time
the symptom was a suite that failed some or all of the time and read as flaky. **A red test is
the visible half, so it gets carried first and alone.** Before taking a `test(` commit, find the
`fix(` it was written to prove.

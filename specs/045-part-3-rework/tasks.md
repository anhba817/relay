# Tasks: Part 3, reorganised by subject

**Feature**: `specs/045-part-3-rework/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

**Format**: `- [ ] TNNN [P?] [USn?] description with a file path`. `[P]` means parallelisable —
different files, no dependency on an incomplete task. Story labels appear only in story phases.

**THE STORY ORDER AND THE EXECUTION ORDER DIFFER, ON PURPOSE.** US3 is P2 and runs before the two
P1 stories. Once no source comment names an ordinal, moving a chapter cannot invalidate one — so
doing the references first keeps two large changes separately verifiable. The other order entangles
them, and no gate could then say which one broke a chapter. Stated here rather than left for somebody
to discover by reading the phase numbers.

**Tests are the fence chain.** This feature writes no test code. `check:fences` replays 240 fenced
files byte-exact across 42 chapters after the split — 41 today — and is the acceptance test for almost every task below. The two
places it cannot see are named where they occur: the thirteen excerpt-only files, and prose that
walks through a diff.

---

## Phase 1: Setup — and proving the instrument before trusting it

- [X] T001 Pin the starting state in `specs/045-part-3-rework/baseline.txt`: all fourteen gates with each exit code captured **outside any pipeline**, plus the numbers this feature is measured against — 24 chapters, 447,394 words, 242 fenced files, 904 fences, 1,429 source references, and the battery's 225.45 s mean with stdev 1.15. **`fail=1` inside a `for … | sort` runs in a subshell and dies with it**, which has printed "ALL GATES: GREEN" over a red one three times in feature 043. (SC-007)
  All fourteen green, every exit code written to a file and counted from the file. The nine measured
  numbers are pinned in `baseline.txt` and **all nine match the artifacts** — 24 chapters, 447,394
  words, 623 titled and 99 untitled fences, 242 fenced paths, 183 comment-changed, 1,429 references,
  49 appendix-amended.

- [X] T002 Build the snapshot tool at `specs/045-part-3-rework/snapshot.mjs`: replay the published chain and dump each path's state **after every chapter and again after `relay-tutorial/fences/post-series.md`**. **The appendix is part of the chain and the first tooling forgot it** — the omission showed as 70 reference-bearing lines present in the platform file and in no snapshot, concentrated in `eslint.config.mjs` and `vitest.coverage.config.mts`. (FR-016) **Copy `check-fence-chain.mjs` and truncate it rather than reimplementing the replay** — a generator that replays differently from the checker produces output the checker rejects for reasons neither explains.
  **240 of 240 paths in the post-appendix snapshot are byte-identical to `relay-platform`**, which is
  the proof pass 3's finding demanded: the chain does not end at the last chapter, and a tool that
  stops there reaches a state that is not the platform's. The script patches
  `check-fence-chain.mjs` in place and deletes the copy, so there is one replay implementation in
  this repository rather than two — and it **asserts both injection points match exactly once**,
  because a silent no-op would produce an empty dump and a control that passes for the wrong reason.

- [X] T003 Build the replay tool at `specs/045-part-3-rework/replay.mjs`: for each path, commit the snapshots as a git history, cherry-pick them onto the new order, and emit each resulting state plus the fence between consecutive states. Conflicts stop and are reported by path, for hand resolution in T021.
  Built as a three-way merge, per the mechanism analysis pass 2 substituted for line attribution.

  **AND THE CONTROL IMMEDIATELY FOUND A BUG IN IT.** `snapshot.mjs` dumps the whole chain state after
  every chapter, so a path appears in every chapter directory from its introduction onward — including
  chapters that never touch it. The first version read "present in the directory" as "fenced by that
  chapter", which produced empty commits, and **`git cherry-pick` refuses an empty commit**: the
  forced control came back with a conflict on nearly every path, at chapters as early as 1.04. A key
  now counts only where its snapshot differs from the previous key's. The state count fell from 5,020
  to **644**, which is the real number — the first figure was inflated by unchanged repeats.


  **THIS IS NOT THE MECHANISM THE PLAN FIRST SPECIFIED, AND THE REPLACEMENT WAS MEASURED.** The first
  design filtered the final file by line attribution — *the final file minus every line owned by a
  later cluster*. Analysis pass 2 built it: **52 parse errors on `repository.ts`, 59 on `session.ts`,
  4 on `schema.ts`**, because line-level ownership cuts through syntax. Three-way merge instead gives
  **56 intermediate states with 0 parse failures**. A merge of two real files is a real file; a
  filtered subset of one is not.

  **AND THE TARGET IS NOT ALWAYS THE PLATFORM FILE.** For the **21** order-changing paths the
  appendix also amends, a chapter fence must land on the state the appendix then amends — targeting
  the platform file overshoots by exactly those hunks, and `check:fences` reports the failure at the
  wrong place. (FR-016)
- [X] T004 **The control, and the reason Phase 1 exists.** Run `replay.mjs --order current` and require byte-exact reproduction of today's `app/(en)/part-3` fences. **A generator that cannot rebuild what already exists cannot be trusted to build what does not**, and every later phase reads its output. **This control has already caught one mechanism**: the attribution design reproduced **17 of 96** states under it, which is how T003's approach came to be replaced before a line of the book moved. (SC-005)
  **644 states reproduced byte-exact through the merge machinery.**

  **THE FIRST VERSION OF THIS CONTROL PROVED NOTHING, TWICE.** `--order current` leaves every path's
  sequence untouched, so all 242 took the fast path and the control compared snapshots against copies
  of themselves: 5,020 green states and not one line of merge machinery exercised. `--force-replay`
  now runs the merge regardless, and cherry-picking a history onto itself must reproduce it exactly.

  **Then the target was wrong.** The drift check compared against `SNAP/<last chapter>/<path>` —
  replay's own input — so a corrupted snapshot was reproduced faithfully and the comparison passed.
  For the 193 paths the appendix does not amend, the target is now **the platform file**, which is
  independent of the input. For the 49 it does amend, the chapter chain must stop short of the
  platform and the snapshot is the only target there is; those are counted separately rather than
  silently trusted.

- [X] T005 Prove T004's control can fail: perturb one fence body in a Part 3 `page.mdx`, confirm the comparison names that file and that fence, restore. **A control that has never been red is a control nobody has tested** — feature 044 shipped two probes that could not fail, one of them written by the audit that exists to find them.
  **Red, and it took four attempts to write a probe that could make it red.** Each failure is a fact
  about what this control detects:

  | Probe | Result | Why |
  |---|---|---|
  | perturb one mid-chain snapshot | green | the next delta is computed from the perturbed state back to the unperturbed one, so it cancels |
  | perturb an appendix-amended path | green | its target is the snapshot by design — the chapter chain must stop short of the platform |
  | perturb only the last-changing chapter | green | `snapshot.mjs` writes the state into every later directory, so a later copy registers as a change back |
  | **perturb from that chapter onward** | **exit 1, `DRIFT packages/config/src/infra.test.ts`** | the final state no longer equals the platform |

  **So the control detects a wrong END state, not a wrong intermediate one** — and an intermediate
  corruption that is later corrected is invisible to it. That is defensible, since the chain's
  contract is the end state plus every hunk applying, but it is a limit and it is now written down
  rather than assumed away. **Two probes in feature 044 failed to go red while appearing to test
  something; here four did, and the four are the finding.**


**Checkpoint**: the tool reproduces the present. Nothing has moved.

---

## Phase 2: Foundational — the three tables

**Blocking.** Every later phase reads one of these.

- [X] T006 Write the subject-name table at `specs/045-part-3-rework/subjects.json`: one entry per Part 3 chapter, keyed by slug, giving the phrase a source comment should use — `webhooks-that-survive-the-customer` → "the webhook dispatcher chapter". **Keyed by slug and not by number**, because the number is the thing being retired. **It serves ~605 references, not 923** — the other ~757 are tags that delete and consult no table.
  **Drafted, not settled**, and flagged for revision inside the file: 25 phrases that land in platform
  source comments permanently. Each is a definite noun phrase that reads mid-sentence — "the
  membership-revocation chapter's finding", "the rate-limit chapter built" — because a title would
  not: *"The words somebody wants back's finding"* is not English. Two entries deliberately do not
  end in "chapter" (both milestones already have names the book uses in prose), and 3.13 and 3.15
  take "channel-endpoints" and "channel-control" rather than colliding on "the channel chapter".

- [X] T007 Write the chapter map at `specs/045-part-3-rework/chapter-map.json` from `contracts/chapter-map.md`. **One record, two consumers** — the published mapping page and the redirects. A hand-maintained pair is the defect the port bands taught this project, and it cost chapter 3.24 an unexplainable eleventh red. (FR-014, SC-008)
  25 chapters, 8 movements, ordinals 1..25 with no gaps. The split is recorded with its boundary —
  `## The outsider` at line 961 of 1,565, 14 fences above and 7 below — because the scope estimate
  turns on it and nothing else in the tree records it.

- [X] T008 [P] Write `specs/045-part-3-rework/classify-refs.py`: emit every one of the 1,429 source references with its file, line, class and proposed rewrite. Three classes, measured in research R5 by **the rewrite each needs** — ~757 delete, ~605 substitute, ~70 read. **Classifying by appearance instead gave 416 / 923 / 90 and was half wrong in the middle column.** **Report the pattern and the corpus with every count**: 1,429 is all `.ts` under `services/` and `packages/`, 1,298 is the subset inside the 183 fenced paths, and the 985 this feature planned against came from a pattern missing a capital `C`. **Give the pattern a positive control and report a pattern that fails its own example as BROKEN rather than as zero**: `grep` here is ugrep 7.8.4, and a grouped alternation followed by two negated classes matches nothing under it. (FR-008, SC-002)
  **1,429 references in 203 files, and the classifier disagrees with the estimate it was built from.**
  Analysis pass 5 estimated ~757 delete / ~605 substitute / ~70 read. The classifier measures
  **791 / 523 / 115**. It is now the authority, being the thing that will drive the work, and its
  heuristic for "subject of a verb" is looser than the hand estimate's — the read class is 115 rather
  than 70, which is the class that decides how long Phase 3 takes.

  **THE CONTROLS FAILED TWO DESIGNS BEFORE THEY WORKED, AND BOTH FAILURES ARE THE SAME MISTAKE.**
  `REF` is a three-branch alternation:

  | Design | Probe | Result |
  |---|---|---|
  | one control for the whole pattern | break `[Cc]hapter` | **exit 0** — the control string `chapter 3.20's` still matched via the possessive branch |
  | a separate compiled pattern per branch | break `REF`'s paren branch | **exit 0** — the controls tested those patterns, not the one doing the scanning |
  | **`REF` built by joining named branches**, one control string per branch | all five | **all exit 1** |

  **A control another branch can satisfy is not a control for the branch it names.** Found by
  probing, not by reading — the first two designs both looked correct.

- [X] T009a [P] Write `specs/045-part-3-rework/check-registry.py`: `relay-tutorial/lib/tutorial.ts` declares every chapter's number, path, title, `titleVi` and reading time **by hand**, and the sitemap plus six components read it — the sidebar, the chapter shell's previous and next links, the site header, the landing page and the language switcher. Compare it against the filesystem **in both directions** and test it red each way. **Nothing checks this file today**, and it agrees at 41 and 41, which is what makes silent drift possible rather than unlikely. (FR-015, SC-009)
  **41 declared, 41 on disk, agreeing in both directions** — unguarded rather than broken, which is
  the condition analysis pass 1 found and the harder one to notice. Tested red three ways: an entry
  dropped (caught as "on disk and not declared — invisible to the sitemap and sidebar"), a path
  pointed at a chapter that does not exist, and the `path:` key renamed, which the checker reports as
  a parse of zero rather than as agreement with everything.

- [X] T009b [P] Write `specs/045-part-3-rework/check-fence-parity.py`: count **every** fence in each chapter, titled and untitled, and require the English and Vietnamese pages to agree per chapter. **`check:fences` cannot do this** — `check-fence-chain.mjs:77` collects a fence only when it matches `title="…"`, so it compares 623 per locale in Part 3 and never sees the other **99**. Test it red by deleting one untitled fence from a Vietnamese page. (FR-010, SC-006)
  **758 titled and 146 untitled fences compared across 41 chapters, 0 problems.** And the probe is the
  proof of pass 4's finding, run side by side with the gate it supplements:

  | Damage to a Vietnamese page | `check-fence-parity.py` | `pnpm check:fences` |
  |---|---|---|
  | drop all 4 untitled fences | **exit 1** | **exit 0** |
  | change one untitled fence's language | **exit 1** | **exit 0** |
  | drop one titled fence | exit 1 | exit 1 |

  **The mirror is blind to exactly the damage the Vietnamese task is most likely to do**, since T032
  is an instruction to replace everything that is not a fence. Untitled bodies are compared by count
  and language rather than byte-for-byte, and the file says why: an untitled fence has no title to
  pair on, so position is the only key and the language sequence already checks it.

- [X] T009 [P] Write `specs/045-part-3-rework/check-map.py`: the map is a bijection over 24 old and 25 new chapters, every slug exists on disk, and **every new ordinal is used exactly once**. Test it red on a duplicate and on a missing slug. (FR-007, FR-014)
  25 chapters, 8 movements, 0 problems. Tested red five ways: a duplicated ordinal, a slug with no
  page, an undeclared movement, a dropped chapter, and a second chapter appearing twice where only
  the split may.


**Checkpoint**: the three tables exist and disagree with nothing.

---

## Phase 3: User Story 3 — a chapter can move without ageing a reference (Priority: P2, runs first)

**Goal**: no source comment names a Part 3 ordinal.

**Independent test**: count Part-3 chapter-number references in `relay-platform`. 1,429 today; zero in fenced files after.

- [X] T010 [US3] **DELETE the tag** — the ~757 references that are a parenthetical provenance note or a sentence-initial marker, across the `.ts` files of `relay-platform`. `(chapter 3.21, FR-RTM-08)` becomes `(FR-RTM-08)`; `(chapter 3.2)` at the end of a sentence goes; `// Chapter 3.8: nor the notification relay` loses its prefix. **No name is needed and `subjects.json` is not consulted** — the sentence stands without the tag, and where it carried a requirement id that id was always the durable half. (FR-008)
  **687 tags deleted, then 25 more once one shape was widened — 712 in 182 files.** Zero
  delete-class references remain and `typecheck`, `lint` and `build` are green.

  **THE RULE TOOK FIVE ORDERINGS AND EACH WAS FOUND BY READING THE OUTPUT, NOT THE CODE:**

  | Ordering | What it did to the tree |
  |---|---|
  | proximity to a requirement id | called `Chapter 3.8 needed the` a tag because an `ADR-05:` sat earlier on the line |
  | parentheses before possessives | stripped a possessive inside brackets to a hole, leaving the noun it modified stranded — 32 of them, possessives and plurals inside brackets |
  | possessives first, verbs later | stripped `(chapter 3.11 added it)` to a hole; treated `it("… as chapter 3.10 shipped them")` as a tag, because `it(` opens a bracket |
  | a last-resort strip for anything left | **applied to the tree**: 16 dangling prepositions and 36 orphaned possessives — `narrowed by's` where a requirement id had followed |
  | shape order, no last resort, quotes excluded | 712 rewritten, 0 unmatched |

  **The fourth was caught by scanning the applied diff for damage signatures**, not by
  reading the rule — 141 flagged lines, reverted, rule fixed, re-applied at 45 flagged of
  which 44 were false positives. **The one true positive was pre-existing**: the source
  already read `(chapter 3.11, , NFR-PERF-01)` with a double comma, and the scan found it.

  **AND THE PATTERN ITSELF WAS WRONG A THIRD TIME.** `[Cc]hapter` misses `CHAPTER` — this
  codebase writes ALL-CAPS for emphasis — so 75 references were invisible, and 117 bare
  `3.N` more. **1,428 became 1,614 in 207 files.** The count read 985 until it gained a
  capital `C`, the file count kept the lowercase pattern until analysis pass 3, and this is
  the same word in caps. The spec and plan need amending.

- [X] T011 [US3] **SUBSTITUTE a name** in `relay-platform/packages/`, from `subjects.json`, and record found against rewritten. (FR-008)
  **578 substituted across five batches** — packages 71, api/src/db 109, the rest of the api
  237, gateway 145, dispatcher 16 — with `typecheck`, `lint` and `build` green.

  **CAPITALISATION FOLLOWS SENTENCE POSITION, NOT THE REFERENCE'S OWN CASE**, and it took a
  revert to see why. The rule read `if ref[0].isupper()`, which in a codebase that writes
  ALL-CAPS for emphasis is the wrong signal:

      **THIS LINE IS THE ONE CHAPTER 3.21 FORGOT.**
      -> **THIS LINE IS THE ONE The typing chapter FORGOT.**

  Now a capital is added only where the reference opens a sentence — nothing before it, a
  comment opener, or a full stop. Both damaged lines read lower-case and correct.

  **AND TEMPORAL PREPOSITIONS MOVED TO THE READ CLASS.** `ADR-16 has said it since chapter
  3.9` became `since the mail-transport chapter`, which is understandable and wrong about
  why — the mail chapter has nothing to do with migrations. "Since" means a point in the
  series, so 35 of these take a rewritten sentence instead of a name.

- [X] T011a [US3] Substitute in `relay-platform/services/api/src/db/` — `repository.ts` alone holds 129 references, the largest concentration in the tree. (FR-008)
  109 in `services/api/src/db/`; `repository.ts` alone held the largest concentration.

- [X] T011b [US3] Substitute in the rest of `relay-platform/services/api/`, outside `src/db/repository.ts`, located with `grep -rn`. (FR-008)
  237 in the rest of `services/api/`.

- [X] T011c [US3] Substitute in `relay-platform/services/gateway/` and `services/dispatcher/`, located with `grep -rn`. (FR-008)
  161 across `services/gateway/` (145) and `services/dispatcher/` (16).


  **~605 substitutions split four ways, because one task of that size cannot be told part-done from
  done.** Each batch reports found against rewritten. **Read each one; do not run a blind
  substitution** — the table gives the phrase and the sentence decides whether it fits.

- [X] T012 [US3] **READ and rewrite** the ~70 in `relay-platform` that neither rule fits, located with `grep -rn`: section rules like `// ── chapter 3.18: two instances, one fabric ──`, and temporal claims where "since the rate-limit chapter" reads worse than restating the fact. **Re-measure this class before starting it.** Its size came from reading twelve sentences after two classifiers disagreed by 4.5× — 90 against 407 — and twelve is thin. It is the class that decides how long this phase takes. (FR-008)
  **All 293 done, and only nine needed a person.** The read class was not one job — it was five
  sub-classes plus a residue, and four of the five were uniform enough for a rule and a damage scan:

  | Sub-class | Count | Rewrite |
  |---|---|---|
  | section rules | 32 | the ordinal is navigation; the words after the colon already say what the section is |
  | a bare `3.N` | 100 | a name reads — `stranded a user online for ever in the presence chapter` |
  | temporal | 33 | a name reads too. They were routed here because `since chapter 3.9` → `since the mail-transport chapter` implies the mail chapter caused a migrations rule; re-read across all 33, **that one is the outlier** |
  | the split chapter | 16 | decided per sentence — a mention of the sealed package, the outsider or the exit criterion means the milestone, everything else the registry |
  | ends the line | 16 | the verb is on the next line, which the single-line test could not see |
  | **by hand** | 9 | test titles, a `gaps.md` item that was never a chapter reference, and sentences where no rule fits |

  **THE ESTIMATE WAS ~70 AND THE TRUTH WAS 293, THEN 9.** Both numbers are wrong in the useful
  direction: analysis pass 5 read twelve sentences and inferred the expensive class was small;
  the classifier said 318; and the answer is that **almost none of it was expensive once the
  sub-classes were named.** The lesson is not that the estimate was bad — it is that "needs a
  person" was never one category.

  **FOUR MORE MECHANICAL CLASSES SURFACED WHILE WORKING THROUGH THE RESIDUE**, each found by
  reading what was left rather than by planning: a parenthetical that spans lines (12), `---` as
  a section rule alongside `──` (2), `'S` uppercase failing a case-sensitive possessive test (5),
  and `gaps.md 3.23-4` which is an item id and never was a chapter reference (1).

  **AND THE CLASSIFIER CRASHED ON ITS OWN SUCCESS.** `counts[k]*100//tot` divided by zero the
  moment the last reference was rewritten — a script that could not report the condition it
  existed to reach.

- [X] T013 [P] [US3] Confirm the 49 **unfenced** `.ts` files under `relay-platform` were covered by T010–T012 and need no fence amendment, with `grep -rn`. They carry 210 of the 1,429 and are the only ones where a rewrite costs nothing downstream. (FR-008)
  **The 49 unfenced files were covered by T010–T012 along with everything else.** The rewriters
  walk `services/` and `packages/` whole and never consulted the fence list, so no separate pass
  was needed — and `classify-refs.py` reporting **zero references in zero files** is the proof
  that covers fenced and unfenced alike.

  **AND THE WALK WAS EDITING BUILD OUTPUT.** `rglob("*.ts")` matches `packages/protocol/dist/
  frames.d.ts`, so the rewriters were rewriting generated declaration files. `dist/` is
  gitignored and `pnpm build` regenerates it, so nothing was lost — but the three scripts now
  skip it, and the classifier's count of 1 remaining reference was a `dist/` file until it did.


  **THE THREE RULES ARE THE SPLIT, NOT THE DIRECTORIES**, and this ordering was the other way round
  until analysis pass 5. Classifying by what a reference *looks like* gave 416 delete / 923 substitute
  / 90 read; classifying by the rewrite it *needs* gives **~757 / ~605 / ~70**. Nearly half of what
  was called a substitution is a deletion that consults no table. Batches sized by directory mixed all
  three, so neither the cost nor the reviewer was predictable per batch.

- [X] T014 [US3] Regenerate the fences for the **183** fenced files whose comments changed, and append amendment hunks to `relay-tutorial/fences/post-series.md`. **`-U6` is a default, not a rule**: regenerate wider when a pre-image matches twice, and verify the hunks apply clean before pasting, not after. `-U8` was worse than `-U6` once and `-U10` fixed it, because widening context merges adjacent hunks. (FR-006, FR-013)

  **THE PROPAGATION WAS MEASURED AND IT IS MECHANICAL.** Of 1,221 reference-bearing lines in fenced
  source, **94% are byte-identical from the chapter that introduced them to the final file and 0%
  changed between chapters** — so rewriting a comment is a replace across snapshots rather than 1,429
  separate decisions. The remaining **5% appear in no chapter snapshot at all**: those are the
  appendix's, and they are T021a's. **This premise was untested until analysis pass 3**, and it is the
  one headline check in this feature that passed.
  **THE TASK LINE AND ITS OWN NOTE DISAGREED, AND THE NOTE WAS RIGHT.** The line said to
  append amendment hunks to `fences/post-series.md`; the note said a comment rewrite "is a
  replace across snapshots". The appendix applies AFTER the last chapter, so amending 154
  files there leaves every Part 3 chapter PUBLISHING `(chapter 3.8, research R1)` in its own
  fence and stripping it once the reader has finished the book. The convention that every
  platform change carries an appendix hunk is feature 044's, and **044 published no chapter**.
  The fence bodies were rewritten instead. `check:fences` is green at **240 files**.

  **THE MAP CAME FROM THE COMMITS, NOT FROM RE-RUNNING THE RULES.** The rewriters made
  contextual decisions; re-deriving them against a fence's context could disagree by one
  word, and a chain that disagrees by one word lands on a file that is not the platform's.
  1,626 line mappings and 21 reflowed runs, read out of the nine rewrite commits — plus
  **228 lines the platform never held at HEAD**, which no commit can describe: a comment
  introduced in 3.2 and replaced by 3.9's hunk is published, typed by readers, and absent
  from the final file. T014's note measured 94% of reference-bearing lines as byte-stable to
  HEAD. True — and the other 6% is that.

  **SIX DEFECTS, FOUR OF THEM INVISIBLE TO EVERY GATE HERE.**

      five two-line tags joined wrongly     `(chapter 3.14,` / `// FR-024)` -> `(  // FR-024)`
      24 references split over a line break `... which is chapter` / `* 3.12 found` — the
                                            ordinal substituted, the word left dangling
      19 deleted markers that were subjects  `// Chapter 3.22, and NOT for ...` -> `// And NOT ...`
      11 lower-case names amid capitals      `* THE LOCK the quota chapter WANTED`
      1 quotation a substitution made false  `used to say "the deduplication chapter's"` —
                                            it never said that; the numbers ARE the evidence
      154 references in 34 non-.ts files     `rglob("*.ts")` matches neither `.mts`, `.mjs`,
                                            `.sql` nor `compose.yaml`; the Dockerfile has no
                                            extension at all

  **AND THE CLASSIFIER HAD THE SAME BLIND SPOT AS THE REWRITERS**, so "0 references in 0
  files, every Part-3 ordinal in platform source now names its subject" was a claim about a
  corpus that excluded 34 files. **A CHECKER WHOSE CORPUS IS NARROWER THAN ITS CLAIM says
  nothing, and it says it in the language of a pass.** The corpus is now the union of source
  suffixes and the paths titled fences name — 300 files — and reads 0, with 1 ordinal kept on
  purpose in `refrules.DELIBERATE`.

  **FOUR COPIES OF ONE RULE.** The comment-opener set lived in `classify`, in `delete_one`,
  in the read class and in the re-capitaliser. Teaching three of them that `--` and `#` open a
  comment left the fourth deciding the capital, so `-- Chapter 3.1 — the tenancy hierarchy`
  was correctly recognised, correctly stripped, and came out `-- the tenancy hierarchy`.

  **A REMOVED SQL COMMENT LINE READS `--- ` IN A DIFF**, which is also the file-header
  prefix, so the map silently dropped every removed line in all fifteen migrations. Position
  tells them apart: the headers sit between `diff --git` and the first `@@`.

  **AND AN ORACLE THAT CAN BE WRONG IS NOT AN ORACLE.** A repair pass re-derived every
  rewritten line from its pre-image and called any difference damage: 104 lines in 57 files,
  and reading them showed the TREE was right — the "repair" put `(3.24)` back. The original
  work was a pipeline of two rule passes, six read kinds and nine hand edits, and one
  function is not equivalent to it. Rewritten to detect each damage class by its own
  signature in the tree, where no oracle is needed.

- [~] T015 [US3] Verify: zero ordinals in fenced source, `check:fences` green at 240 files, and `pnpm typecheck`, `lint`, `build` green in `relay-platform`. **A comment edit that breaks a build is still a broken build.** (SC-002, FR-013)
  **PARTLY DONE, AND THE HELD PART IS NAMED.** Zero ordinals in fenced source (300-file
  corpus, 1 kept on purpose) and `check:fences` green at 240 files are both confirmed.
  `pnpm typecheck`, `lint` and `build` were green at commit `42cd22b`; the two commits after
  it — `ba7b8aa` restoring the quotation and `309ffdd` the Dockerfile — are comment-only and
  **NOT re-verified**, because the machine hard-locked twice during this task and turbo
  spawning `tsc` per package is the heaviest thing this feature runs. `T015`'s own line says a
  comment edit that breaks a build is still a broken build, so this is recorded open rather
  than assumed. Neither lock-up was memory: **0 OOM events in both boots**, the kernel log
  stopping mid-sentence, `i915_hpd_poll_init_work hogged CPU for >10000us` escalating 7 -> 259
  times, and a hybrid Intel + NVIDIA open-module 595.84 stack reporting `Cannot find any crtc
  or sizes` on every boot. The rewriters' own footprint was measured at **15.7 MB and 0.12 s**
  after pruning a walk that had been materialising 34,620 paths including `node_modules`.

- [X] T016 [US3] Check the **ten excerpt-only platform files** separately with `check-excerpt-files.py` — they carry **99 ordinals**, 43 of them in `session.itest.ts` alone. The other three of the thirteen are `docs/04-srs.md`, `docs/05-sad.md` and a predecessor's `baseline.txt`, which are not `relay-platform` source and so fall outside FR-008. **`check:fences` compares them to nothing**, so T015's green says nothing about them — and one of them, `session.itest.ts`, holds the only end-to-end proof of feature 044's signal.
  **THIRTEEN, TEN OF THEM PLATFORM, AND THE COUNT IS PARSED BEFORE IT IS COUNTED.** 112
  excerpt fences, 68 distinct titles, of which **13 name no file at all** — `the naive
  version`, `the grep that changed the chapter`. Two more carry a prose suffix over a path
  that IS chained elsewhere: `frames.ts, chapter 1.3` and `session.ts before this chapter`.
  Counting those makes fifteen, which is the error this project has made four times in five.
  `check-excerpt-files.py` asserts all four title shapes as controls before counting.

  **THE 99 ORDINALS WERE ALREADY GONE** — these ten are `.ts` and `.sql` under `services/`
  and `packages/`, so T010-T012's corpus covered them. The re-measurement reads **0**.

  **THE QUESTION NOBODY ASKS IS THE SECOND ONE**, and its first form was wrong. Comparing
  each excerpt body against its file reported **38 of 99 fences drifted**, nearly all
  legitimately: an excerpt elides with `{ … }`, annotates (`path: req.originalUrl,   // was:
  req.url`), simplifies a signature, and **above all often shows the file as it stood at that
  chapter**. Comparing a chapter-5 excerpt to HEAD is the same mistake as pointing the
  chain's replay at the platform file for the 49 paths the appendix amends — the target is
  wrong, so the failure lands in the wrong place. Narrowed to the answerable question — a
  line carrying a chapter SUBJECT NAME is a line this feature wrote, and it must read the
  same in the fence and in the source — it reports **0 naming a different subject** and 4
  with no counterpart in HEAD, each of which received the same substitution the identical
  sentence got elsewhere in the platform.

- [X] T017 [US3] Commit all three repositories. `git checkout` on a file with uncommitted work has destroyed it twice in this project.

**Checkpoint**: US3 is independently shippable. Nothing has moved, and nothing can be aged by moving it.

---

## Phase 4: User Story 1 — a reader follows one subject to its end (Priority: P1) 🎯 MVP

**Goal**: eight of eight subject clusters contiguous.

**Independent test**: group every chapter by subject, confirm each group occupies consecutive positions.

- [ ] T018 [US1] Split the milestone chapter per `contracts/chapter-map.md`: the error-registry half becomes new 3.3 under its own slug, the outsider half becomes new 3.25 keeping `errors-that-resolve-and-an-outsider`. **Its 21 fences divide 14 to the registry and 7 to the outsider**, at the chapter's own `## The outsider` heading on line 961 of 1,565 — nothing straddles it, and the assignment is in `contracts/chapter-map.md` because the scope estimate turns on it. **This is the only chapter whose prose is divided**, and the division is where FR-009's "prose is preserved" is most at risk. (FR-005, FR-007)
- [ ] T019 [US1] Rename the 24 English chapter directories under `relay-tutorial/app/(en)/part-3/` per `chapter-map.json`. **The slug travels with the chapter; only the numeric segment moves.** (FR-007)
- [ ] T020 [US1] Update `metadata.alternates.canonical` and the `languages` pair in each moved **English** `page.mdx` — **61 hard-coded chapter paths** across the 24 — which name their own path and do not follow a directory rename.
- [ ] T021 [US1] Run `replay.mjs --order new` for the **42** order-changing paths, **resolve the 31 merge conflicts by hand**, and write the **289** regenerated fences into their chapters. **Give the 5 paths that merge cleanly onto a *different* file their own reading** — they pass every mechanical check until the final byte comparison, which is the worst way for this to fail. **These counts moved during analysis**: 39 and 278 assumed the milestone chapter moved whole, and the answer is 39/278 if its fences land early against 44/300 if late. The split is now decided fence by fence in `contracts/chapter-map.md`. **3 of 39 would replay from the old deltas and 36 would not** — 31 conflict and 5 land on a different file, which is the outcome that passes every check but the last. (FR-006, SC-005)
- [ ] T021a [US1] Re-verify the **48 existing appendix hunks** on the 21 order-changing paths they amend, in `relay-tutorial/fences/post-series.md`, and regenerate any whose pre-image no longer matches. **They were generated against today's chain end state**, and R2 measured 5 paths where reordering lands on a different file — where that intersects these 21, the appendix's own pre-images stop matching. T014 only *appends* new hunks and would leave these silently stale. (FR-016, SC-010)
- [ ] T021b [US1] Confirm the chain **including the appendix** lands byte-exact on `relay-platform` with `pnpm check:fences`. **The chain does not end at the last chapter**, and a tool that stops there reaches a state that is not the platform's. (SC-010)
- [ ] T022 [US1] Rewrite the 54 forward references in Part 3 prose, across the English `page.mdx` files. A sentence that says "chapter 3.19 will build this" is wrong when 3.19 now precedes it; some become backward references and some become nothing.
- [ ] T023 [US1] Read every moved chapter's prose against its regenerated diffs. **This is the task no gate can do.** A chapter that walks a reader through a hunk now shows a different hunk, and `check:fences` is satisfied either way. Budget for it: 289 fences across 42 paths, concentrated in `repository.ts` (23 fences), `schema.ts` and `session.ts` (16 each). (FR-009)
- [ ] T023a [US1] Rewrite the 24 Part 3 entries in `relay-tutorial/lib/tutorial.ts` from `chapter-map.json` — number, path and order — and add the 25th for the split chapter, deriving its `readerMinutes` and `readerProduces` from the halves. **No requirement named this file until analysis went looking for what else knows a chapter number**, and skipping it leaves every gate green with a broken sitemap, a broken sidebar and dead previous-and-next links on all 25 chapters. (FR-015)
- [ ] T023b [US1] Run `check-registry.py` and confirm both directions agree at 42 chapters. (SC-009)
- [ ] T024 [US1] Verify SC-001 with `check-movements.py`: eight of eight, against five of eight today. Then `check:fences` green at 240 files across **42** chapters — 41 today, plus the one the split adds. (FR-001, SC-001, FR-013)
- [ ] T025 [US1] Commit all three repositories with `git commit`, `relay-tutorial` and `relay-platform` before the root pointer.

**Checkpoint**: Part 3 reads as eight movements. This is the MVP — the defect is closed.

---

## Phase 5: User Story 2 — a reader is never asked to build for an absence (Priority: P1)

**Goal**: nothing is taught before the thing it operates on exists.

**Independent test**: every synthesised intermediate state compiles, and every webhook event type has a producer in an earlier chapter.

**This phase is mostly verification of Phase 4's arrangement**, and saying so is honest: FR-002 is satisfied by the order chosen in `contracts/chapter-map.md`, not by code written here. What this phase adds is the proof, and the proof can fail.

- [ ] T026 [US2] Typecheck every intermediate state: `replay.mjs --order new --typecheck-each`. **A state that does not compile is a finding about the order, not a bug in the tool** — it means a chapter teaches code calling something a later chapter introduces. Record which pair and move one of them. (FR-002, FR-003, SC-004)
- [ ] T027 [US2] Trace each **emitted** event type in `relay-platform/services/api/src/outbox/event.ts` to a producer in an earlier chapter — **five of the eight declared**, measured from the `emitted` flags. Record the other three, `channel.created`, `user.connected` and `user.disconnected`, as declared and unbuilt. Feature 043 measured **838 stored subscriptions to types the platform does not emit**; this feature builds none of them, which is why SC-003 is scoped to the emitted set rather than to all eight. (FR-002, SC-003)
- [ ] T028 [US2] Confirm the isolation milestone at new 3.24 attacks every route built before it, from `relay-platform/services/api/src/isolation/gauntlet.itest.ts`, using its own derived target list rather than a hand-written one. The list extends itself from the running router, so this is a check that the derivation still runs, not that somebody remembered to add rows. (FR-004)
- [ ] T029 [US2] Confirm the outsider milestone at new 3.25 has nothing after it — no later `page.mdx` under Part 3 — and that the SRS Phase 2 exit criterion it renders a verdict on is still the last word in Part 3. (FR-004)
- [ ] T030 [US2] Commit all three repositories with `git commit`, root pointer last.

**Checkpoint**: both P1 stories are done and proved.

---

## Phase 6: The Vietnamese placeholders

- [ ] T031 Rename the 24 Vietnamese directories under `relay-tutorial/app/(vi)/vi/part-3/chapter-NN/` per `chapter-map.json`, and split the milestone chapter to match, giving **25**. (FR-010)
- [ ] T032 Replace the prose in each `relay-tutorial/app/(vi)/vi/part-3/chapter-NN/*/page.mdx` with a placeholder, **keeping every import, every `metadata` field, every figure, every JSX box — `<Why>`, `<Trap>`, `<SkipAhead>`, `<ForwardRef>`, `<Checkpoint>` — and every code fence byte-identical to its English counterpart**.

  **THE MIRROR PROTECTS ONLY 623 OF THE 722 FENCES.** It compares titled fences and is blind to the
  **99 untitled** ones per locale, which hold console transcripts and worked diagrams. Dropping them
  passes every gate and deletes real content from 24 published pages. `check-fence-parity.py` is what
  catches it.

  **AND 41 OF THE 623 SIT INSIDE A JSX BOX.** Strip the prose without keeping the wrapper and the MDX
  stops balancing — which fails at `pnpm build`, not at a gate, so it surfaces after the work rather
  than during it. (FR-010, FR-011, SC-006) (FR-010, SC-006)
- [ ] T032a Update `metadata.alternates.canonical` and the `languages` pair in each Vietnamese `page.mdx` — **72 hard-coded chapter paths** across the 24, more than the English side because each names both locales. **No task owned these until analysis pass 4**: T020 sits in the English reorder phase and Phase 6 never mentioned metadata. **The mirror cannot see metadata at all**, so wrong canonicals ship green — and they are what `hreflang` and the sitemap resolve against. (FR-007, SC-008)
- [ ] T033 Mark each Vietnamese `page.mdx` placeholder visibly as awaiting translation, so a reader is never shown a page that looks translated and is not (FR-011). (FR-011)
- [ ] T034 Verify the mirror with `pnpm check:fences` **and count the pages** under `relay-tutorial/app/(vi)/vi/part-3/` — **25**, one per English chapter. A deleted Vietnamese page passes `check:fences` silently, because the checker skips chapters that do not exist — so absence is invisible to the gate that is supposed to catch it. (SC-006)
- [ ] T035 Commit `relay-tutorial` with `git -C relay-tutorial commit`, then the root repository's submodule pointer.

---

## Phase 7: The published surfaces

- [ ] T036 Amend Part 3's rows in `docs/07-tutorial-plan.md` to the new structure, and **derive the chapter count from the rows rather than carrying it in the heading**. That heading said seven, then sixteen, then twenty-one through three chapters that each added a row without moving it — in a paragraph whose own last sentence says the count comes from the rows. (FR-012)
- [ ] T037 [P] Publish the mapping page from `chapter-map.json` as its own route under `relay-tutorial/app/`, naming all 24 old numbers, and link it from the series sidebar in `components/reading/series-sidebar.tsx`. **There is no Part 3 index page** — an earlier draft of this task assumed one; navigation is rendered from the registry. **Four chapters keep their number and change meaning** — 3.13, 3.14, 3.15 and 3.16 all exist before and after and name different chapters, which is the sharpest thing a returning reader needs told. (FR-014, SC-008)
- [ ] T038 [P] Generate the 48 redirects into `relay-tutorial/next.config.ts` from the same `chapter-map.json`, permanent rather than temporary. The split chapter's old URL has to choose a target; `contracts/chapter-map.md` records that it goes to the outsider half and why. (FR-014, SC-008)
- [ ] T039 Rewrite the references into Part 3 found in every `page.mdx` outside Part 3, English and Vietnamese, with `grep -rn` over `relay-tutorial`. Those parts are not reordered, so their own ordinals are stable — but a Part 2 chapter that says "chapter 3.18 builds this" is now wrong.
- [ ] T040 Verify every old URL resolves: `pnpm build` then `check-redirects.py`, 48 redirects each landing on one of the 50 pages that exist. **Check `app/sitemap.ts` in the same pass** — it is the map's third consumer, it is generated from the registry, and the plan called it two consumers until analysis counted them. **And check the 133 metadata paths**, 61 English and 72 Vietnamese: nothing in the gate set reads them. (SC-008)

---

## Phase 8: Polish and close-out

- [ ] T041 [P] Run the coverage lane as a **control**. The platform's behaviour does not change in this feature, so coverage should not move; read `coverage/coverage-summary.json` rather than the text table, which omits any file at 100% on all four metrics. Re-pin nothing unless a number moved, and if one did, find out why before pinning it.
- [ ] T042 [P] Run the credential scan over this feature's diff across all three repositories, recording every pattern searched and every hit classified in `baseline.txt`. **Never report only "clean"** — and give each pattern a positive control, because two of sixteen silently reported zero on material that was present the last time this was run.
- [ ] T043 Run the twenty-run battery of `pnpm test:integration` from a cleared lane with all seven sequencer caches removed, **including the root `node_modules/.vite/vitest`** which a `packages/*` and `services/*` glob misses. SC-007 is a tripwire: 225.45 s ± 10%, and a moved duration means the platform changed when it was not supposed to. (SC-007)
- [ ] T044 Write `specs/045-part-3-rework/gaps.md`, carrying feature 044's ledger **re-measured against the tree rather than copied**. Two items — 044-2 and 3.23-4 — were closed after 044's close-out and must not be re-opened by a copy. Note whether this feature closes `043-1`: renumbering touches every chapter, so the 146 untitled fences are as findable now as they will ever be.
- [ ] T045 Run all fourteen gates last — `pnpm typecheck`, `pnpm lint`, `pnpm build` in `relay-platform`; `pnpm check:fences`, `check:docs`, `check:figures`, `check:srs`, `check:errors` in `relay-tutorial`; and the six instruments in `specs/045-part-3-rework/` — with every exit code written to a file outside any pipeline. (FR-013)
- [ ] T046 Commit the close-out records, then trim `CLAUDE.md` and point the `SPECKIT` block past this feature.

---

## Dependencies

    Phase 1 (T001-T005)  ──▶ Phase 2 (T006-T009)  ──▶ Phase 3 / US3 (T010-T017)
                                                            │
                                                            ▼
                                              Phase 4 / US1 (T018-T025)  P1, MVP
                                                            │
                                                            ▼
                                              Phase 5 / US2 (T026-T030)  P1
                                                            │
                                       ┌────────────────────┼────────────────────┐
                                       ▼                    ▼                    ▼
                              Phase 6 (T031-T035)   Phase 7 (T036-T040)          │
                                       └────────────────────┴──────────▶ Phase 8 (T041-T046)

**US3 blocks US1, which is the inversion worth reading twice.** A P2 story runs before a P1 one
because doing it second would mean rewriting references the reorder had already invalidated, twice.

**US2 depends on US1** and cannot be tested before it: it verifies the arrangement US1 builds. This is
the one story pair that is not independent, and saying so is better than claiming an independence the
tasks do not have.

**Phases 6 and 7 are independent of each other** and both depend on US1's numbering being final.

## Parallel opportunities

- **T008 and T009** are different files and different questions.
- **T013** parallelises with T010–T012 **only after** the file sets are confirmed disjoint. Check it;
  an assumption of disjointness is how two edits land on one file.
- **T037 and T038** read the same map and write different files.
- **T041 and T042** are a lane run and a text scan.
- **Within Phase 3 and Phase 4, almost nothing is parallel.** T014 depends on every comment edit
  before it, and T021 depends on the directory renames. The chain is the bottleneck by design.

## Implementation strategy

**MVP is Phase 1 + Phase 2 + Phase 3 + Phase 4.** That is the defect closed: Part 3 reads as eight
movements and no reference ages when a chapter moves. Phase 5 proves it, Phases 6 and 7 publish it.

**Phase 1 is not optional and not setup.** It is the control. If `replay.mjs` cannot rebuild today's
chain byte-exact, every fence it writes later is unverifiable, and the feature has no test at all.
**The control has already rejected one mechanism at 17 of 96 states**, which is the argument for
running it before anything moves rather than after.

**Commit each phase.**

**Expect the file count to be wrong.** The plan estimates **184** fenced files and 289 fences across 42 paths. It has already read 169/39/278, then 169/42/289, and now 184 — the last move because a pattern correction was applied to the reference count and not to the file count beside it. Feature 043
estimated 17 files and changed 58; feature 044 estimated 12, then 15, then 17. Every unplanned file in
043 came from **running** something rather than reading it, and T023 — reading prose against
regenerated diffs — is the task most likely to find work no instrument here can see.

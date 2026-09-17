# Gaps — feature 054, chapter 4.9, "Milestone: the meter agrees"

Every carried item was re-measured rather than copied. Where a re-measurement contradicts the
item's own wording, the correction is in the entry — a ledger goes stale in two ways, and only
one of them is about time passing.

**Closed this feature: 050-8, 051-3, and half of 053-3.** New: 054-1 through 054-8.

---

## 054-1 — THE WORKFLOW IS RED AT THE TOP, AND THE FIX WAS WRITTEN AND NOT APPLIED

**OPEN, AND IT IS THIS MILESTONE'S OWN SUBJECT ONE LEVEL UP.** `check-fence-chain.mjs:337` exits
1 whenever the problem count is non-zero; `ci.yml:205` runs `pnpm check:fences` as the tutorial
job's last step with no `continue-on-error`; the standing count is **110** and has been since
feature 045. **Every push since then has produced a red workflow**, and every chapter since 4.1
has closed by reporting `110 → 110, delta 0` **by hand**, because the machine could not say it.

Nothing is stranded behind it — it is the last step of its job. What is lost is the workflow's
colour, which is exactly the property this chapter spent a phase restoring one level down.

**The 110 are mostly not repairable by editing anything.** Eleven are fences whose titles name a
prose phrase rather than a path, so *"does not exist in relay-platform"* is true by construction
(050-4); thirty live in the Vietnamese chain, under active translation; and bringing one
foundation fence up to date takes the chain from 110 to 203 by unanchoring ninety-two downstream
hunks (045-81). **A gate demanding zero here is demanding a rewrite of the series.**

**The design, written and not applied.** A recorded baseline in `fences/baseline.json`, compared
**per kind as well as in total** — APPLY 75 with HEAD 35 sums to the same 110 while hiding a new
broken hunk behind a repaired one, which is the half a hand-written report has never checked —
exiting 1 above the baseline and printing the line that lowers it below. **The edit was refused
by this environment's own guard as a CI bypass**, which is the correct reflex for a change that
makes a failing checker exit 0: it is the user's call, not a chapter's. ADR-27 records the fact
and the three options; this entry carries the design so whoever takes it does not start from
nothing.

File beside **050-4**, which is the arithmetic, not a complaint about the checker.

---

## 054-2 — FR-ANL-06's DAILY JOB HAS NO RUNNER, AND ITS ALERT HAS NO MECHANISM

**OPEN, AND BOTH HALVES ARE NOW RECORDED RATHER THAN ONE.** The clause is three obligations:

    the comparison   reconcile.ts, chapter 4.7      exercised on every push, and measured
    the daily job    NO RUNNER OF ANY KIND          recorded nowhere until this feature
    the alert        NO MECHANISM                   recorded at SRS 1.14

Measured, corpora named because a zero from a grep is a claim about the corpus only if the corpus
is named: zero occurrences of `reconcile-usage` in `relay-platform/package.json`, `turbo.json`,
`.github/workflows/ci.yml`, `relay-tutorial/package.json` or any `*.sh`; `ci.yml` triggers on
`push` and `pull_request` with no `schedule:`.

**ADR-28 decides it as a recorded absence rather than a sixth background relay**, and states the
reversal condition: build the job when a tenant exists whose two sides are populated by the
platform rather than by a harness. Today a daily sweep would report `no-data` for every tenant —
2,440 `usage_periods` rows over 2,330 environments, 7 rollup rows over 4 environment ids, **zero
environments in both** — and a check that always fires stops being read.

---

## 054-3 — CONSTITUTION III'S AMENDMENT IS PROPOSED AND NOT APPLIED — THREE ITEMS, ONE PRINCIPLE

**OPEN.** `specs/054-chapter-4-9/constitution-amendment.md` is the full text, the MINOR bump, the
migration impact and the supporting ADR the governance section requires for a change to
Principles I–IV. It is not committed to `.specify/memory/constitution.md`, and the reason is in
the proposal: the procedure names a PR, this project has no PR flow, and **a chapter amending the
document that governs it, written by the same author, is the constitution amending itself.**

**Three open items now stand against one principle**, which is worth stating as a number:

    051-2   the cross-store read — `load-analytics.mjs` runs an analytical query against Postgres
    052-6   the auditor reading both stores — an auditor confined to one side cannot check the fence
    054-3   the 0.1% bound, the daily job and the alert — this feature's

The first two are about the same sentence from different angles; this one is about the bullet
below it. All three have been carried rather than resolved, and the procedure for resolving them
is the same one.

---

## 054-4 — `docs/07` §6's DEFENSE 1 IS NOT WHAT EXISTS, AND 048-5 IS ITS OTHER HALF

**OPEN.** §6 specifies *"a checkpoint script per tag"* — `tutorial/checkpoints/part2-chN.sh`, each
chapter's tag checked out and verified. Measured: **`tutorial/checkpoints/` exists in none of the
three repositories**, and `ci.yml` contains zero occurrences of `tag` or `checkpoint`.

What feature 024 closed defense 1 on is a workflow against the **tip** — three jobs that build and
test `main`. That is useful and it is not what §6 describes: it says nothing about whether chapter
3.12's tag still typechecks. The per-tag sweep has been run by hand, twice, by the features that
needed it (045 over Part 3's 26 tags, 047 over Part 1's).

**048-5 is the adjacent half** — *no gate checks that a chapter's tag matches the chapter* — and
this is its reason. Filed together, because the missing mechanism is one mechanism.

§6's contradictory pair is fixed this feature: it said *"Defense 1 does **not** exist"* and
*"Defense 1 now exists"* ten lines apart, both dated 2026-08-08, and chapter 4.8 corrected the
second without reading the first.

---

## 054-5 — TWO MILESTONE CHAPTERS ARE BELOW BOTH OF `docs/07` §2's FLOORS

**OPEN, AND NOT THIS CHAPTER'S TO FIX.** §2 states 2,000–4,000 prose words and 2–4 captioned
figures for every chapter. Measured:

    milestone-the-tuan-test                3,151 words   0 figures   below the figure floor
    milestone-the-isolation-gauntlet       1,873 words   1 figure    below both
    errors-that-resolve-and-an-outsider    1,683 words   2 figures   below the word floor
    the-log-a-customer-can-search          3,606 words   3 figures   inside both
    milestone-the-meter-agrees             2,666 words   3 figures   inside both

**The same two chapters fail both floors**, which makes it one decision rather than two.

**T059a's decision: the floors are read as applying to milestones, and the two published ones are
a gap rather than a category `docs/07` never covered.** §2's length row states one range for
every chapter and its entire rationale concerns the upper bound — the only enforcement story in
the document is a split, chapter 3.8 at 4,700 words. Nothing contemplates a chapter being too
short. Chapter 4.9 meets both bounds either way, so **exempting a chapter class on this evidence
would be an amendment made to avoid a measurement**, and amendments belong in a phase of their
own.

**And the gate has a blind spot that let a zero-figure chapter ship green.** `check:figures`
verifies that every diagram is passed as `code=` and that every import binding resolves. It
reports a series-wide count and enforces no per-chapter one. A prose or figure addition costs the
fence chain nothing — measured at 4.8 — so extending those two chapters is cheap, and it is
somebody's chapter to extend rather than this one's.

---

## 054-6 — A TEST HELPER'S DEADLINE IS TWICE ITS TEST'S TIMEOUT

**OPEN.** `services/gateway/src/typing.itest.ts`'s `arrived()` polls to a **10,000 ms** deadline;
the gateway's integration config sets no `testTimeout`, so vitest's default **5,000 ms** kills the
test first. A genuine absence therefore reports *"Test timed out in 5000ms"* and **the assertion
that would have named the missing frame never runs**.

That is how this feature's first look at the four-kind failure spent a pass on the wrong
hypothesis: the message said timeout, the cause was a discarded frame. Raising the timeout to 20 s
made the real assertion reachable — `presence: expected [] to have a length of 1 but got 0` — and
the file has been 12 of 12 green since the real defect was fixed, at either timeout.

**Recorded rather than changed**, because the lane is green at the default and raising a timeout
to make a message reachable is worth doing on evidence rather than on a hypothesis. The class is
wider than one file: any helper whose deadline exceeds its caller's timeout is a diagnostic that
cannot print.

---

## 054-7 — `scripts/` HAS NO TESTS, AND A COVERAGE PIN THERE IS SILENT

**OPEN.** `scripts/scale/corpus.mjs:167` says *"Everything above is arithmetic and testable
without one"* and exports `readConfig` and `planFor`. **Nothing imports them.** No vitest project
includes `scripts/`; `pnpm test` is turbo over packages, and `scripts/` is not a package.

Both halves of the threshold probe were run, in one coverage run:

    scripts/scale/corpus.mjs pinned at an impossible lines: 101   SILENT — no ERROR line
    services/api/src/metering/reconcile.ts, the control         FIRED at 68.18% against 100

So **a pin on a real file that no lane includes is as silent as feature 045's pin on a path that
does not exist.** A pin for `scripts/` would be a decoration rather than a ratchet.

This feature's decision was to put the arithmetic where the ratchet reaches it —
`smallestExpressibleDrift` lives in `services/api/src/metering/reconcile.ts`, which chapter 4.7's
own precedent established when it moved `exitCodeFor` out of a script *"so a test can ask it
directly"*. **Making `scripts/` measurable is a lane change and a feature of its own**, and
inheriting the absence without saying which of the two it is is what this entry prevents.

---

## 054-8 — THE EARLY-RETURN PATTERN SURVIVES THE VARIABLE THAT EXPOSED IT

**OPEN AS A CLASS.** Three attacks in `isolation/gauntlet.itest.ts` read
`if (dispatcher === undefined) return; // not configured in this lane` and reported green without
running: 1ms, 0ms and 1ms against 27ms, 6ms and 33ms once the credential was configured.

Configuring the credential fixes today's instance in both lanes. **The pattern is untouched**:
any future environment variable a suite guards this way produces the same silent skip, and the
suite's own accounting test cannot catch it because `attacked.add(...)` runs before the early
return — **the check written to find unattacked routes is satisfied by the route that was
skipped.**

Two cheap mechanisms exist and neither is built: make the guard `expect(x).toBeDefined()` so an
unconfigured lane is red rather than quiet, or move `attacked.add(...)` after the return so the
accounting test notices. Filed rather than taken, because it is a change to the cross-tenant
suite's own conventions and constitution VI names that suite as gating releases.

---

## 050-8 — 4.4's INTEGRATION SUITE NEEDS A PROCESS NO GATE STARTS — **CLOSED**

**CLOSED at chapter 4.9, five features after it was filed.** `request-log.itest.ts` spawns the
ingester it needs in `beforeAll` and kills it in `afterAll`, which is what `consumer.itest.ts`
and `outbox.itest.ts` already do for a Node child. 5 of 5 red became 5 of 5 green, and the api
lane is 33 of 33 for the first time since chapter 4.4.

**Both obvious fixes were wrong, which is why it stayed open for five features.**
`services/ingester` has no Dockerfile, and `api`, `gateway` and `dispatcher` carry
`profiles: ["services"]` — so a compose service would be a new image that is not running when the
lane runs, and one in the default profile would drain the analytics stream on every machine
continuously. `--filter` could not separate the suites either: it selects packages, and these
five live inside `@relay/api` beside the reconciler's own suite.

**What it drains is reported rather than assumed**: 8 batches and 1,038 records on the first run —
the backlog the stream had been holding because nothing had ever consumed it — and 12 on the
second.

---

## 051-3 — `pnpm test:integration` RUNS A SUBSET — **CLOSED, AND THE ITEM UNDERSTATED IT**

**CLOSED at chapter 4.9.** The gate runs `scripts/integration-gate.mjs`, which derives the lane
list and suite count from the tree, passes `--continue` so every lane runs, and reads each lane's
own vitest summary back. Measured green: **54 suites of 54, six lanes, exit 0** — and measured red
with a planted drift: 54 of 54 still executed while the api lane failed.

**The item said the command "runs a subset" and the sharper statement is that its summary line
cannot be read at all.** `Tasks: 8 successful, 10 total` counts turbo tasks: nine builds, nine
test tasks, three of them packages with no integration script. And the total does not reproduce —
`7 of 9`, `8 of 10`, `7 of 11` and now `12 of 12` across four runs of the same tree, because
which tasks were in flight when a failure arrived decides it.

---

## 053-3 — THE SEALED SUITE — **CORRECTED TWICE, FROM TWO ADJACENT LINES OF ONE FILE**

**HALF CLOSED, HALF RE-STATED.** The item read: *"no local command runs the sealed suite, and
`pnpm test:integration` does not reach it."*

**The first half is false.** `package.json:16` is
`"test:outsider": "turbo run test:integration --filter=@relay/outsider"` — one command, and it
has existed since the appendix published it. The item was written at chapter 4.8's close after
running that suite by hand in six commands, and this feature's own research repeated the claim
through four analysis passes before anybody opened the file.

**The second half is true for a reason the item does not give.** `pnpm test:integration` does not
reach it because **line 15 excludes it by name** — `--filter=!@relay/outsider` — not because
turbo stops early. The distinction matters: an early stop is a bug and an exclusion is a
decision, and the sealed suite's exclusion is the right one (it integrates against a platform it
does not start).

**A carried item can be wrong about its mechanism while right about its symptom, and wrong about
its symptom while right about its category.** Two ways a ledger goes stale beyond going out of
date, both in one entry, both fixed by reading two adjacent lines of the file the item is about.

---

## 048-2 — `message_events.delivery_latency_ms` HAS NO PRODUCER — **UNCHANGED, SEVENTH FEATURE**

**OPEN.** Re-measured: `message_events` held **0 rows** at this feature's opening, and the only
thing that writes the table — `scripts/scale/load-analytics.mjs` — supplies `CAST(NULL AS
Nullable(UInt32))` for that column in both halves of its `UNION ALL`, on purpose.

**This feature filled the table for the first time and did not touch the column.** The corpus load
wrote 397,978 rows of `created`, `edited` and `deleted` events, every one with a NULL latency. So
the table now has data and the clause still has no producer, which is a sharper statement of the
same gap: **the absence is not for want of rows.**

---

## 050-2 — THE ANALYTICAL STORE HAS NO LANE GUARD — **UNCHANGED, AND THIS FEATURE MEASURED THE COST**

**OPEN.** Feature 030's sentinel guard covers PostgreSQL. `relay_analytics` has nothing
equivalent: any test or script may write it, and the only cleanup shipped before this chapter was
`apply.mjs --drop-all`, which is `DROP DATABASE`.

**Measured this feature, which is new.** One corpus load leaves **571,333 rows across four
tables** in the lane's own store:

    .inner_id.3f6e34d9-…  (chapter 4.2's daily_usage)        184
    daily_usage_billing                                      184
    daily_usage_v2                                       172,965
    message_events                                       398,000

The scoped cleanup this feature added removes exactly those, by environment id, and verifies by
count — **but it is a convention in a script rather than a guard in the store.** The next thing
that writes `relay_analytics` without cleaning up leaves rows nobody attributes.

---

## 050-3 — THE VI CHAIN IS NEVER COMPARED TO THE TREE — **UNCHANGED, AND THIS FEATURE RELIED ON IT**

**OPEN.** `check-fence-chain.mjs` replays the Vietnamese chain and compares it against the
**English chapter's fences** (MIRROR), never against `relay-platform`. This feature relied on that
twice: the Vietnamese Part 4 stops at `chapter-03`, so every file chapters 4.4 through 4.9 fence
is en-only, and no vi mirror is owed for this chapter.

That is the translation frontier rather than a shape needing handling — which is what phase 1
established, after three artifacts had treated *"1 en, 0 vi"* as a special case.

---

## 050-4 — ELEVEN HEAD PROBLEMS ARE FENCES WHOSE TITLE NAMES NO FILE — **UNCHANGED, AND USED AGAIN**

**OPEN.** The standing 110 splits APPLY 74 / HEAD 36, and the HEAD half splits **25 `differs at
line`** and **11 `does not exist in relay-platform`**. The eleven are fences titled with a prose
phrase; they can never be repaired by editing the platform.

**The APPLY half's third bucket has a name now**, which four chapters reported without giving:
74 is 30 `(en)` + 30 `(vi)` + **14 in `fences/post-series.md`** — the appendix, one file, and the
one this feature had to edit.

---

## 048-3 — `vitest.coverage.config.mts` CANNOT TAKE A FENCE — **UNCHANGED, AND IT HID AN EDIT AGAIN**

**OPEN.** The file has diverged from the chain at line 29 since before Part 4, and a checker
reports the first failure per file — so every later edit to it is invisible to the HEAD
comparison. This feature added two environment variables to it and the delta did not move.

**The APPLY side is separate and is where the appendix's nine hunks live**, which is why the edit
still had to be published there: a file can be free on one half of the checker and expensive on
the other.

---

## 048-5 — NO GATE CHECKS THAT A CHAPTER'S TAG MATCHES THE CHAPTER — **UNCHANGED**

**OPEN**, and see **054-4**, which is its cause rather than a second instance of it.

---

## 052-2 — `services/ingester/src/shape.ts` IS PINNED AT 100 AND MEASURES 95.12 — **UNCHANGED**

**OPEN.** Reported by `pnpm coverage` every run, which is what chapter 4.7's `reportOnFailure`
bought. Left at 100 rather than lowered, for that chapter's reason: it was made visible rather
than measured down.

---

## 052-3 — A CLEANUP ENUMERATES TABLES BY HAND — **UNCHANGED THERE, AND THIS FEATURE DID THE OPPOSITE**

**OPEN.** `services/ingester/src/ingest.itest.ts` still issues per-table `DELETE`s naming
`webhook_attempts`, `api_requests` and `connection_events` at five call sites.

**This feature's own cleanup is the counter-example rather than the fix.**
`load-analytics.mjs --clean` asks `system.columns` which tables carry an `environment_id` and
`system.tables` which of those are not views, then deletes from the ones holding rows. **A
hand-written list would have missed `.inner_id.3f6e34d9-…`** — chapter 4.2's `daily_usage`, a
materialised view with no `TO`, whose rows live in a table named after a UUID that no document
mentions. The item's own sentence, demonstrated rather than restated.

---

## 052-6 — CONSTITUTION III's AMENDMENT IS STILL OWED — **UNCHANGED**, and see **054-3**

**OPEN, AND NOT THIS FEATURE'S TO CLOSE.** See 054-3 for the count: three items now stand against
this principle.

---

## 052-7 — A FEATURE-LOCAL ID CITED AS A PUBLISHED CLAUSE — **CHECKED, AND CLEAN THIS TIME**

**OPEN AS A CLASS, NOT INSTANTIATED HERE.** The check was run over every document this feature
touched: `docs/13`, `docs/06-adr-deep-dives.md` — **no bare-numbered ids**. `docs/05-sad.md`,
`docs/12` and `docs/07` carry five between them and every one is pre-existing and *qualified*
("FR-013 of chapter 3.23", "043's own FR-016"), which is the acceptable form.

**Still nothing runs it.** `check-srs-ids.sh` checks the SRS's own rows for duplicates and never
looks at what other documents cite. The check is one `grep` and would have caught 4.8's instance.

---

## 053-1, 053-2, 053-4 through 053-9 — CARRIED, NOT RE-MEASURED

**OPEN, AND SAID PLAINLY RATHER THAN IMPLIED BY A SHORT LIST.** This feature touched none of the
surfaces those items are about — the clamp this series publishes (053-1), the sealed suite's
assertions (053-2), `check-lane-scope.py` (053-4), the journey map's question (053-5),
`has_more` on one list endpoint of two (053-6), EIR-API-07 (053-7), the `/internal/*` decision
(053-8), or the dashboard immediacy gap (053-9).

**A carried item re-measured by a feature that did not touch its subject is a re-measurement of
nothing**, and copying last feature's sentence forward under a new heading would make the ledger
look worked on. They carry unchanged, from chapter 4.8's measurements, with that said out loud.

---

## What this milestone could not establish

In the same terms as what it could, because a milestone that lists only successes is the document
nobody trusts.

- **That the platform's own two counters agree.** The measured 0.0000% is over a corpus whose two
  sides are derived from one set of rows. What establishes the platform's agreement is a
  mechanism — `sendMessage` writing both in one transaction — and chapter 4.7's 0 of 1,385
  tenant-periods disagreeing for a non-fixture reason. **This chapter's figure is about the
  reconciler's arithmetic and the bound's resolution.**
- **That the bound holds at production volume.** The largest tenant-period measured is 121,057
  messages in a corpus built for the purpose. No real tenant on this platform has both sides.
- **That a drift would be noticed outside a test run.** No daily job exists (054-2), the alert
  has no mechanism, and the workflow's own colour has been red for nine chapters (054-1).
- **That the fence chain is clean.** It is 110 problems and was 110 before, which is a delta of
  zero rather than a verdict.

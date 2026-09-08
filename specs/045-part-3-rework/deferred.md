# Changes a chapter cannot make yet, and the chapter that must make them

The rebuild moves whole subjects. A chapter that used to touch a file now sometimes runs
BEFORE the chapter that creates it — and the change is not lost, it is owed. This is the
ledger. Every entry names the original commit, the file, and the chapter that inherits it.

Without this the rebuild silently drops work: a cherry-pick that cannot apply is reported
once, on a terminal, and then never again.

| original commit | file | belongs to | what it did |
|---|---|---|---|
| `b638242` | `services/api/src/webhooks/deliveries.itest.ts` | new 19 (webhooks) | settle the drain before asserting a delivery was published |
| `5015cc8` | `services/api/src/webhooks/deliveries.itest.ts` | new 19 (webhooks) | give the sweep tests a limit that reaches their own endpoint |
| `aed5af8` | `scripts/webhook-walk.mjs`, the webhook block of `services/api/src/db/schema.ts` | new 19 (webhooks) | name the subject instead of the chapter number in three comments |

**Three of old 3.7's eight commits are webhook work.** In the old order webhooks came two
chapters earlier, so a chapter about the resume high-water mark could freely fix a webhook
test in passing. Moving webhooks to 19 unpicks that: the resume work applies cleanly and
the webhook fixes have nothing to apply to. Neither is a merge problem — the file does not
exist — and neither is lost, because they are here.
| `6c1c90b` (part) | six `/v1/webhooks*` rows in `isolation/targets.ts`, their gauntlet attacks | new 19 (webhooks) | classify and attack the webhook routes |
| `6c1c90b` (part) | the webhook block and `get environment()` in `db/repository.ts` | new 19 (webhooks) | endpoint/delivery/dead-letter repository methods |

## OLD 3.10 IS LOAD-BEARING INFRASTRUCTURE THE MAP MOVES THIRTEEN CHAPTERS LATER

Measured while porting new 9. `chapter-map.json` sends **old 10 → new 23**
("quotas-and-what-they-cost") because quotas are its *subject*. But old 3.10's span carries
`packages/test-harness` — the integration lane's own infrastructure and the global-operation
guard — and three separate things in front of it depend on that:

    new 8  `.mdx` fences `sentinel.sql`, `sentinel.ts`, `guard.itest.ts`   lines 1385/1416/1454
    new 10 `.mdx` fences `sentinel.sql`                                    line  4079
    new 9  `b8d8bb7`'s own test asserts a 16-code registry; the branch
           has 10, and `quota_exceeded` is old 3.10's

**None of it is visible to a gate.** All four fences carry `(excerpt)` titles, so
`check-fence-chain.mjs` compares them to nothing and `check-chapter.py` skips them — which is
why new 8 reported *0 problems* while fencing three files that do not exist at its own tag.

**THE SPAN SPLITS CLEANLY.** Sixteen commits are harness-and-guard with no quota content
(`fb97056`..`d365817`); seven are quotas (`aa236de`..`b21a87c`). The boundary is exact.

### AND THE PROSE CARRIES A CAUSAL CLAIM ABOUT CHAPTER ORDER

New 8 §"Nine guarded tables, not five" is not a forward reference — it is an **audit of two
earlier chapters**:

> Feature 030's guard … watched five tables. **Chapters 3.10 and 3.11 added four more** that
> carry `environment_id` — `usage_periods`, `usage_active_users`, `quota_notifications`,
> `usage_connections` — **and neither added them here.**

Old 10 → new 23 and old 11 → new 24. At new 8 the four tables do not exist, the guard does not
exist, and the section has nothing to audit. **A chapter that audits earlier chapters cannot be
reordered ahead of them**, and no instrument in either repository reads that sentence.

The retrofit story only existed because the original forgot. The re-narration is therefore not
"move the section" but **delete it and have each chapter add its own table to the guard array as
it creates it** — which also disposes of the sentinel's running count (`sentinel.sql` says "TEN
AS OF CHAPTER 3.16"), a number the reorder scrambles and nothing checks.

## AND THE COVERAGE THRESHOLDS HAVE A THIRD SILENT MODE

Re-running the silent-key probe at new 8's re-pin confirmed both halves under
vitest 4.1.10 — a real key demanding 101% names itself, a key naming no file says
nothing at all — and turned up one more:

    "services/api/src/auth/user-token.ts": { lines: 101 },   <- overwritten
    ...
    "services/api/src/auth/user-token.ts": { branches: …, lines: … },

**A DUPLICATE KEY IN THE THRESHOLDS OBJECT IS AN ORDINARY JS OVERWRITE.** The first
probe demanded 101% of a file that was *already pinned* forty lines down, got no
error, and read as the instrument being broken. It was the probe. A pin added above
an existing one is discarded in silence, which is the same failure as the
non-matching key with a worse tell: the key *looks* effective because the file
exists and the number is visible in the config.

`gaps.md` should carry it with the other two. It is one more reason the probe has to
be run on a key nothing else names.

## THE PUBLISHED TREE HAS 21 TAGS FOR 24 CHAPTERS

`part3-ch13`, `part3-ch14` and `part3-ch15` were never cut. `relay-platform/README.md:8`
says:

> **One git tag per chapter** (`part1-ch1`, `part1-ch2`, …). Every tag is a runnable,
> tested state: check it out and the toolchain checks pass. Each chapter's SKIP AHEAD
> box names the tag to check out if you get stuck.

Three chapters' SKIP AHEAD boxes name a tag that does not exist. **This is the contract
that made every snapshot re-derivation the wrong question**, and it turns out to have
three holes in it.

**AND THE INSTRUMENT HID IT.** `git merge-base --is-ancestor <commit> part3-ch13` exits
non-zero for a ref that does not exist, which is byte-identical to "not an ancestor". A
probe over ch12→ch13→ch14→ch15 returned `NO`, `NO`, `NO` and read as a structural claim
about the repository's shape — that the published tags were not one chain. They are; the
refs were absent. **A ref-existence control is the positive control this probe needed**,
the same rule the credential scan bought at a higher price.

The span `part3-ch12..part3-ch16` is **16 commits covering four old chapters** (3.13
through 3.16) and **not one of them carries a `(3.N)` subject prefix**, unlike every
other chapter's commits. So the boundaries between old 13, 14, 15 and 16 exist in
`.mdx` fences and nowhere else — which is what `check-chapter.py` reads, and the reason
the rebuild's chapter 8 and 9 spans had to be derived from prose rather than from tags.

**A CONSEQUENCE WORTH STATING PLAINLY:** old 3.13's content sits *inside* `part3-ch12`'s
span (`6c1c90b feat(3.12): a channel and its members over the public API` creates
`channels.controller.ts`, which new 8's page fences). The tag names chapter 12 and holds
chapter 13's work. Any measurement that attributes commits to chapters by tag boundary
is wrong in this region, in a direction no gate reports.

## TWO MIGRATIONS RE-CUT ALONG CHAPTER LINES

`b8d8bb7 feat: the schema chapters 3.15 and 3.16 stand on` says in its own subject that
it serves two chapters, and the reorder keeps them adjacent (old 15 → new 9, old 16 →
new 10) — so nothing forces a split. What forces it is that the two migrations are
**numbered sequentially and split by subject, not by chapter**:

    0011_activity_and_read_positions   channels.last_activity_at + index   -> new 10
                                       read_positions table                -> new 10
    0012_member_roles_and_user_deletion  members.role + CHECK              -> new 9
                                         users.deleted_at                  -> new 10

New 9 cannot add `0012` without `0011` existing, and `0011` holds nothing it uses. Its
page is 109 mentions of `role` against three of `deleted_at`, one of
`last_activity_at` and three of `read_positions` — the prose already knows which
chapter it is.

So new 9 takes `members.role` alone, as this branch's `0006`, and new 10 takes
`last_activity_at`, `read_positions` and `users.deleted_at` as `0007`. **A migration's
number should follow the chapter that introduces it**, which is only true if no
migration serves two.

Deferred to new 10 with it: `scripts/backfill-channel-activity.mjs` (the
`last_activity_at` backfill, outside the migration because a scan is not
downtime-free), and `read_positions`' entry in the guard's table array — which under
the per-chapter rule belongs to the chapter that creates the table, not to this one.

## `PORT=0` WAS SAFE FOR ONE OF TWO SERVICES, AND THE ASYMMETRY WAS INVISIBLE

The e2e journey failed twice with **all eight tests skipped**, immediately after a
lane that spawns api children, and green on its own. The obvious cause was
`packages/e2e/src/harness.ts`'s fixed `4100` with gateways at `apiPort + 1 + i` — a
band, of the class the port fix was meant to have retired. Replacing it with `PORT=0`
did not fix it.

**The real cause was one service short of a two-service fix.** `services/api/src/main.ts`
has read its bound address back since the isolation harness — `PORT=0` prints `0` if
you log the value you were handed. `services/gateway/src/main.ts` logged `{ port }`
straight from the environment. So:

    api up on 37763
    gateway 1 never became healthy      <- a health probe against port zero

**AND NOTHING NOTICED BECAUSE NOTHING ASKED.** Every suite that spawned a gateway
handed it a fixed port, so the logged value was the value passed in and correct by
accident. The property only becomes observable the first time a parent needs the
answer — which is the same shape as an exemption that never fires and a bait row no
drain can claim.

`packages/test-harness/src/bound-port.test.ts` derives every `services/*/src/main.ts`
from the tree and asserts each calls `address()` and does not log the name it bound
from `process.env`. Red-tested by reverting the gateway.

Four fixed ports are now gone: `public-surface.itest.ts`'s 4800-5000 band,
`session.itest.ts`'s 4123, and the e2e harness's 4100 plus the gateway band derived
from it. `RELAY_E2E_API_PORT` and `RELAY_SESSION_ITEST_API_PORT` are out of
`turbo.json`'s env allowlist. The only remaining literals are the two services' own
production defaults.

## AND AN ASSERTION ON TWO CHARACTERS READ AS A LEAKED SECRET

`credentials.itest.ts` invariant 1 proves a minted secret is unrecoverable from the
row it leaves behind. It took the secret as `credential.split("_").at(-1)` — and the
secret is **base64url, whose alphabet includes `_`**. So the assertion was on whatever
followed the secret's own last underscore: usually a long tail, occasionally two
characters.

    AssertionError: expected '[{"public_id":"cbd76832…' not to contain 'WA'
    salt: 7XKYdYc_ottu61KbLY4dWA

Two characters that appear inside the stored salt — which reads exactly like the api
returning a secret it had just hashed. `minted.prefix` was already on the returned
object. **The first repair used `lastIndexOf("_")` and was the same fault again**; the
prefix is the only exact answer. A length guard now refuses to assert on a short
string at all, and twenty consecutive runs are green.

## A FAITHFUL REWRITE OF A WRONG REFERENCE IS WORSE THAN THE WRONG REFERENCE

Two of the references swept in the prose pass were wrong before anything touched them,
and the substitution carried each one faithfully into something less checkable:

    chapter 3.1   "3.7's isolation gauntlet"
                  -> "the deduplication chapter's isolation gauntlet"
                  The gauntlet is the isolation harness's. Old 3.7 is fan-out and
                  resume, and has no gauntlet in it.

    chapter 3.9   "(chapter 3.16, FR-022a)" on a test its OWN chapter's page carries
                  -> would have pointed a reader fourteen chapters away

**A WRONG NUMBER IS CHECKABLE AND A WRONG NAME IS NOT.** A reader who sees "3.7's
isolation gauntlet" can open chapter 3.7 and find no gauntlet in about four seconds.
"The deduplication chapter's isolation gauntlet" reads like a fact about a chapter
whose subject the sentence has just told them, and there is nothing to check it
against.

So the rewrite is only as good as its input, and the class it cannot see is a reference
that resolves to a real chapter and names the wrong one. Neither `check-refs` nor the
damage scan can find these: both compare shapes. Two found by reading, out of roughly
four hundred substitutions — which is a rate, not a clean bill.

## AND CHAPTER 3.7 HAD ALREADY MADE THE ARGUMENT, WITH THE REASON HALF WRONG

Written one chapter before the reorder was planned:

> The distinction worth keeping is between a **provenance stamp** and a **forward
> promise**. "Chapter 3.7 added this field" stays true for ever — **chapters do not
> renumber backwards.** "Chapter 3.7 will build the transport for quotas" goes stale
> the moment anything is inserted ahead of it.

The premise is the thing this feature falsified: twenty-four chapters renumbered, and
3.7 kept its number by coincidence while both its neighbours moved. **An ordinal is
stale in both directions**, which collapses the rule into the one this pass applies —
name the subject, because a name encodes no position.

The page now says so where the argument was made rather than in a later chapter's
retrospective, since that is where a reader meets it.

## THE REFERENCE REWRITE IS A STEP IN THE PER-CHAPTER LOOP, NOT A PHASE

Measured at chapter 3.9's first tag: **81 explicit ordinals and 84 bare**, against zero
at 3.8's. A chapter's port cherry-picks commits from the published history, and every
one of them carries the references the convention removed. The full-branch replay
established the convention; it cannot keep it.

So `replay-range.sh` runs per chapter — the same tree-by-tree mechanism over one
chapter's commits, onto a parallel branch, with the tag repointed after. Two traps in
building it, both already recorded elsewhere in this file and both hit again:

**`git rev-parse` ON AN ANNOTATED TAG RETURNS THE TAG OBJECT.** `commit-tree -p
<tag object>` fails with *"is not a valid 'commit' object"* naming a sha the script
never printed. The rework tags are annotated because a tag should carry the chapter
title a reader checking it out wants — which made every bare `rev-parse` in this
repository a trap. `^{commit}` everywhere.

**AND `--require-all` ASKED THE WRONG QUESTION ON THE SECOND RUN.** It was written for
the one tree where every replacement in `read-class.json` is still unrewritten. Run
against a later tree it reported 24 replacements matching nothing — every one of them
already applied, which is indistinguishable in its output from 24 typos. It takes
`--group` now, so a chapter's own group is checked against that chapter's tree.

## A REWRAP DROPS WORDS AND NOTHING COULD SEE IT

A two-line read-class replacement has to fit the same text into different line breaks,
and trimming to fit is silent — both sides are the right shape:

    - // 3.13 chose" as *named outcomes* and dropped *bulk*. Every pass compared
    + // endpoints chapter chose" as *named outcomes* and dropped *bulk*. Every pass
      // requirements to tasks, both said "removal", …

`Every pass compared` became `Every pass`, and the next line went on `requirements to
tasks`. `apply-read-class.py` counts words now: a replacement may lose the reference's
own words, function words and verb inflections, and nothing else.

**IT CAUGHT THREE MORE OF MINE ON ITS FIRST RUN** — `first two` dropped from "the first
two endpoints", `for a whole` dropped from a sentence whose next line began "chapter
and then turned nine of fifteen tests red", and `table` dropped from a clause I had
reworded to avoid repeating a noun. Two were real losses; the third I restored rather
than widen the rule, because a guard with an exemption per rewording is a guard nobody
trusts.

## THE FOURTH ATTACK SHAPE, AND THE TWO IT TURNED OUT NOT TO COVER

The isolation harness left a note where a `list` shape would go: *"nothing this api
serves returns a collection, so a list attack would be a function with no target — and
a shape with no member is a vocabulary entry that drifts. The chapter that adds the
first list route adds the shape and the attack together."* Chapter 3.10 is that
chapter, and the prediction held — but adding the member found two more distinctions
the taxonomy did not have:

**A LISTING CANNOT ASSERT THE PAIR.** Every other attack compares the foreign
identifier against one that exists nowhere and requires them indistinguishable. `GET
/v1/users/:externalId/channels` names the user in the path, so a foreign id is
correctly a 404 while a user who owns nothing is a 200 with no rows. Comparing those
says nothing. The property is that no identifier from another environment appears in
any answer — which a status code cannot express, so `ListVerdict` carries the rows and
what leaked into them.

**AND A ROUTE THAT ECHOES ITS INPUT HAS NO PAIR EITHER.** `POST /v1/users` and
`DELETE /v1/users/:externalId` were written as `writeAttack` and both failed
correctly:

    body {"data":[{"external_id":"victim-…-user","status":"created",…}]}  (foreign)
    vs   {"data":[{"external_id":"absent-0000…","status":"created",…}]}  (absent)

The answers differ by construction, in the one field the request chose. `POST
/v1/users` also takes its identifiers in the BODY, so there is no foreign id in a URL
to compare. Both check the victim's state alone.

**THE TYPE CAUGHT ONE SITE AND NOT THE ARITHMETIC BESIDE IT.** `Record<Shape, number>`
stopped compiling the moment `Shape` gained a member and named the tally. Four lines
below, `counts.read + counts.write + counts.credential` quietly stopped totalling
everything: `expected 17 to be 18`, for a route classified, attacked, and counted as
neither. Both derive from the record now.

## AND IMPLICIT USER CREATION STOPPED 404 BEING A SIGNAL

A user row is minted on first authentication (FR-039a/b), and the gauntlet's credential
attack mints a token for the victim's external id with the attacker's key — so it
**creates that name in the attacker's environment**. Nothing leaks: the row is the
attacker's own, with a name the attacker chose.

But the two ban attacks asserted 404 and got 200. After this chapter a foreign
identifier no longer reliably answers not-found on any user route, because presenting
it may have created it. Both assert the victim's row instead, with `banned_at` named
beside the deep equality — a field added later would otherwise fail the comparison for
a reason unrelated to a ban.

## A COMMIT THE CONVENTION DELETED

`b8f278a docs: twenty-two citations point at the chapter that taught the change` was
skipped, and its content is the argument: twenty-two comments renumbered from
`chapter 3.12` to `chapter 3.14`, because the work they cited had moved and the number
encoded a position. Named, none would have needed correcting. **A whole commit of
maintenance, deleted by a naming rule** — which is the clearest measurement of what
the rule is worth.

## TWO ORDINALS SURVIVE AT `rework/part3-ch2`, AND BOTH ARE SELF-REFERENCES

`internal.ts` and `messages.module.ts` say "chapter 3.2" inside chapter 3.2.
`rework/base-convention` removes them one commit later — the convention was
established after the first two chapters were written, which the tag's own message
records. Redundant rather than wrong, and not worth rewriting two chapters' history
for.

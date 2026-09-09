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
| `6c1c90b` (part) | the webhook block in `db/repository.ts` | new 19 (webhooks) | endpoint/delivery/dead-letter repository methods |

**AND `get environment()` CAME OUT OF THAT ROW, because the membership chapter needed it first.** It was deferred with the webhook block on the strength of its own comment, which attributes it to the test event: "an UNSCOPED operation … must still be told which environment is asking". New 14 publishes a membership change from two controllers and needs the same id for a different reason — `req.principal?.environmentId ?? "unknown"` reads it too and carries a branch the guard makes unreachable, which is a coverage failure with no fix but a comment. So the accessor lands there, with that reason, and new 19 inherits a smaller row.

**THE LESSON IS ABOUT THE LEDGER RATHER THAN THE ACCESSOR.** A row here was written by reading what a thing's comment SAID it was for. Three lines of it turned out to be load-bearing for a chapter five earlier, and nothing found that until `tsc` said `Property 'environment' does not exist`. **A deferral justified by a comment is a deferral justified by one caller's opinion of why the code exists.**

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

## A CHAPTER'S FENCES GO STALE WHEN ITS OWN TAG MOVES

Chapter 3.9's page verified clean, then reported **16 problems** with nothing touching
it. The reference replay had moved `rework/part3-ch9`, and `regen-fences` had run
against the tag before the move.

**So the per-chapter loop has an order, and it is not the obvious one.** The reference
rewrite has to run BEFORE the fences are regenerated, because it changes the code the
fences quote:

    port the commits  →  gates  →  reference replay  →  retag
                      →  regen-fences  →  check-chapter  →  vi-placeholder  →  page

Run the other way round, every fence in the chapter is regenerated against a tree that
is about to change, and the only thing that notices is `check-chapter` on the next
chapter's pass — which is how this was found, one chapter late.

## AND THE MDX PASS WAS MISSING A CLAUSE THE SOURCE PASS HAD

`refrules.AMBIGUOUS` routes a reference to a split old chapter away from automatic
substitution, because old 12 is new 4 *or* new 25 and only the sentence knows. The
source pass consults it. `rewrite-mdx-refs.py` did not — it substituted every ordinal
whose chapter `subjects.json` names, and old 12's name there is `the isolation
gauntlet`, which is new 25's half.

So a sentence about the harness would have sent a reader to the milestone twenty-one
chapters later. **Two copies of a rule are two rules**, and the second was missing a
clause — the same finding this feature already recorded about `place_name`, arrived at
from the other direction. It reports what it leaves for a reader now: six on chapter
3.10's page, four of them deliberate quotations.

## THREE PROSE SHAPES THE SUBSTITUTION CANNOT HANDLE

Found by reading its output rather than by any check:

**A TABLE COLUMN KEYED BY THE ORDINAL.** `3.15   20 files taught, 2,947 prose words`
became `The channel-control chapter   20 files taught…`, and the alignment the block
depends on is gone. A name is longer than a number and a monospace column is not
prose.

**A QUOTATION OF THE ORDINAL ITSELF.** A passage discussing what a citation *said*
needs the citation verbatim: `31 files cited "chapter 3.12"` is a fact about the text,
not a pointer. Substituting it makes the sentence describe something that never
happened.

**AND A PASSAGE WHOSE SUBJECT THE CONVENTION DELETED.** Chapter 3.10 carried 30 lines
on matching citing files to the pages that fence them, a distribution of 25 / 9 / 13
against a shortcut's 15 / 14 / 10, and one file the exercise could not reach. All of it
accurate, and none of it arising once a chapter is named by its subject. **Telling
"accurate" from "necessary" apart is only possible after the convention exists** — which
is the argument for reading a page after the rules have run over it, and the reason no
checker will ever do this pass.

## CHAPTER 11 DEFERS FOUR FILES, AND ONE OF THEM IS PROSE

`75d8c33` ("every send site names a sender") is the widest commit in old 3.17: FR-MSG-15 made
every send name a sender, so every *existing* send site in the tree had to be given one. Three
of its nine files do not exist yet.

| original commit | file | belongs to | what it did |
|---|---|---|---|
| `75d8c33` (part) | `packages/outsider/src/integrate.itest.ts` | new 26 (the outsider) | give the sealed suite's sends a bot, and assert the three refusals |
| `75d8c33` (part) | `services/api/src/limits/limits.itest.ts` | new 22 (limits) | name a sender in the rate-limit suite's sends |
| `75d8c33` (part) | `services/gateway/src/limits.itest.ts` | new 22 (limits) | name a sender in the socket-limit suite's sends |
| `75d8c33` (part) | `README.md`, "Sending a message: name who is sending" | new 26 (the outsider) | document the bot sender in the quickstart of record |

**THE README ROW IS A DIFFERENT KIND OF DEFERRAL, AND THE DIFFERENCE IS THE POINT.** The other
three are files that do not exist: the cherry-pick says so, loudly, and the only decision is
which chapter inherits them. The README exists. Its hunk conflicts on *context* and resolving
that conflict is easy — which is exactly the trap, because the section applies cleanly to a
document that cannot support it.

Every prerequisite of that section is deferred. It opens `CHANNEL=$(curl … -H "authorization:
Bearer $RELAY_DEMO_CREDENTIAL" …)`, and `RELAY_DEMO_CREDENTIAL` comes from
`scripts/seed-demo-tenant.mjs`, which new 26 creates; this tree's README is 79 lines and has no
demo tenant, no credential and no API example of any kind. It closes by calling itself "the
quickstart of record", whose claim — "the suite below is that execution — it is sealed from
workspace code and follows this file" — names `packages/outsider`, also new 26's.

**So the section would have told a reader to export a variable nothing defines, and cited a
suite nothing runs, and no gate could have said so.** `check:fences` compares fenced bytes
against a chapter's diff; a bash fence in the README that references an unset variable is
byte-perfect. The section is correct prose about a platform that will exist eleven chapters
later, which is the same defect as a comment citing `quota_exceeded` — a code this tree does
not define, cited twice in `packages/protocol/src/codes.ts` as though it did.

**A DROPPED FILE ANNOUNCES ITSELF AND A DROPPED PARAGRAPH DOES NOT.** Three of these four rows
were written because `git cherry-pick` printed `CONFLICT (modify/delete)` and named the path.
The fourth was written because somebody read the hunk. That asymmetry is the argument for this
ledger existing at all, and it is worth re-reading whenever a chapter's port ends with "it
applied cleanly".

## AND A WHOLE SECTION OF THE SENDER CHAPTER'S PAGE IS THE QUOTA CHAPTER'S

`## Billed, and exempt` — 38 lines, one `<Figure>`, one `<Trap>` — argues that a bot must be
metered and exempt from the ceiling: `usage_active_users` answers two questions, FR-ANL-05
*meters* unique active users and FR-RTL-05 *enforces* a quota on them, and only the second is
narrowed to persons. It is the sharpest argument in the chapter and none of it is true here yet.

| original commit | artefact | belongs to | what it did |
|---|---|---|---|
| old 3.17's page | `## Billed, and exempt`, and `figTwoCounters` in `figures.ts` | new 23 (quotas) | the bot is billed and exempt, and the exemption's second half |

**MEASURED BEFORE REMOVING IT, because the section reads as though it describes this chapter's
code.** In `rework/part3-ch11`: `usage_active_users` occurs 4 times and every one is a comment;
the table is in no migration; `assertWithinQuota`, `usageActiveUsers` and `max_active_users` do
not occur at all; and no file the chapter changes is quota-shaped. The 18 occurrences of
"ceiling" are FR-CHN-07's **channel member** limit, which is a different ceiling in a different
family — the one trap in checking this by name.

**ITS `<Trap>` NAMED A NUMBER THAT CANNOT EXIST HERE**: "verified by removing the other half and
watching all 26 quota tests stay green". `quotas.itest.ts`, `period.itest.ts` and
`connections.itest.ts` are all deferred; there are no quota tests to stay green. That sentence is
the reason this was found — a count is checkable and a claim about an argument is not.

The section text and the figure are kept verbatim in the record so new 23 inherits the argument
rather than re-deriving it. **The exemption's second half is the part worth carrying**: returning
early so a bot is not refused is visible, and excluding bots from the count the ceiling compares
against is the half that decides whether it works — with a test that sends as a *person* after a
bot, never as the bot itself.

## A DEFERRAL THAT RUNS THE OTHER WAY: A RULE THAT ARRIVES AFTER THE FILE IT MUST EXEMPT

Every other row in this ledger is a change that cannot apply because its file does not exist yet.
This one is the inverse, and it is the shape that goes wrong silently.

`eslint.config.mjs` restricts `ioredis` to the two limits files, and the fan-out chapter adds
`services/api/src/fanout/**` to that exemption with a reason: the restriction exists because
rate-limit counters are keyed `rl:{environment_id}:…` and an unrestricted client can read another
tenant's counter, whereas the publisher touches no keys — it calls PUBLISH onto `chan:{channel_id}`
and nothing else.

**In this order the rule does not exist yet.** `ioredis` is restricted by the rate-limit chapter,
which is new 22; the fan-out chapter is new 12. So the exemption hunk has nothing to apply to, the
api's publisher imports `ioredis` and lints clean, and **nothing is wrong until new 22 lands the
rule** — at which point a file ten chapters old starts failing a rule it has never seen.

| original commit | artefact | belongs to | what it did |
|---|---|---|---|
| `eeafe8a` (part) | the `services/api/src/fanout/**` entry in the `ioredis` exemption | new 22 (limits) | exempt the publisher from a rule that does not exist yet |

**THE FAILURE MODE IS THE OPPOSITE OF A MISSING FILE.** A cherry-pick that cannot apply prints
`CONFLICT` and names the path. A rule that has not arrived prints nothing, because there is nothing
to print — the exemption is for a rule with no members, and an exemption list is only checked
against the rule it belongs to. New 22 must add `services/api/src/fanout/**` in the same commit
that adds the `ioredis` restriction, or its own gate goes red on a chapter nobody is editing.

## THE `ioredis` EXEMPTION IS NOW OWED TWICE, AND THE TWO REASONS ARE DIFFERENT

The fan-out chapter's entry is recorded above. The presence chapter adds two more, and the
distinction between them is the rule's own reason rather than a formality:

| original commit | artefact | belongs to | what it did |
|---|---|---|---|
| `60e7f03` (part) | `services/gateway/src/presence.ts` in the `ioredis` exemption | new 22 (limits) | exempt a client that composes environment-scoped keys |
| `d38f415` (part) | `services/gateway/src/presence.itest.ts` in `DRIVER_EXEMPT_TESTS` | new 22 (limits) | exempt a suite that publishes arbitrary bytes onto the fabric |

**AND THE PRESENCE ENTRY IS THE ONE THAT MATTERS.** The fan-out publisher is justified by
"this client touches no keys" — it publishes onto `chan:{channel_id}`, a channel UUID, and a
subject is not readable at all. **Presence's client touches keys and they are
environment-scoped**: `presence:{env}:{user}`, which is exactly the shape the restriction
exists to guard. Its justification is the rate limiter's instead — every key is composed from
the environment id on the authenticated connection's own identity, nothing takes an environment
id from a client, and there is no scan, `KEYS` or pattern read that could reach another
tenant's key.

So new 22 cannot add one blanket exemption for "the gateway's Redis files". It has to carry
both arguments, and the presence one is a claim about how keys are composed that somebody has
to re-check against the code as it then stands.

**A LIST THAT CAN ONLY GROW HAS ALREADY BEEN A GAP IN THIS PROJECT ONCE.** 044 found the
driver-exemption linter checking one direction only: an unlisted file importing `pg` fails
loudly, a listed file importing nothing restricted passes forever. Both directions are asserted
now — which means new 22 must add the rule and all three exemptions in ONE commit, or the
assertion fires on the rule's own arrival.

## AND TWICE MORE FOR MEMBERSHIP — WITH THE MISTAKE THAT WAS MADE WRITING IT

| original commit | artefact | belongs to | what it did |
|---|---|---|---|
| `576b316` (part) | `services/gateway/src/membership.itest.ts` in `DRIVER_EXEMPT_TESTS` | new 22 (limits) | exempt a suite that publishes arbitrary bytes onto the fabric |
| `576b316` (part) | `services/gateway/src/membership.ts` in the `ioredis` exemption | new 22 (limits) | exempt a publisher that composes no key |

**THE COMMENT ON THE FIRST ONE RECORDS A MISTAKE WORTH INHERITING.** The entry was written first
on the `**/*.ts` block's `ignores` list, where an `.itest.ts` entry does nothing: the
`**/*.itest.ts` block below REPLACES `no-restricted-imports` for every integration test not on one
of the two exemption lists, so an exemption placed above it is overwritten in silence. The file's
own header states that hazard — it is the bug the isolation harness found (R23, FR-043) — and the
entry still went to the wrong list.

That is a fact about `eslint.config.mjs`'s structure, not about membership, and it is true of this
tree today. New 22 will be adding four entries across two lists in one commit; this is the note
that says which list each belongs on and why putting one in the wrong place produces no error.

**FOUR EXEMPTIONS NOW, THREE ARGUMENTS:**

    fanout/**                 no key is touched at all — a publish onto a channel UUID
    membership.ts             the same: PUBLISH only, onto member:{channel_id}
    presence.ts               keys ARE composed, and environment-scoped — the limiter's argument
    presence.itest.ts         \ suites publishing arbitrary bytes with a client
    membership.itest.ts       / belonging to neither module

## THE TYPING CHAPTER OWES ONE TEST TO THE LIMITS CHAPTER, AND IT IS THE SHARPEST ONE

| original commit | artefact | belongs to | what it did |
|---|---|---|---|
| `3412851` (part) | `typing.itest.ts`'s T048b, `GatewayLimits` plumbing, the session stub's `limits` | new 22 (limits) | assert a typing signal spends no message quota (FR-014) |
| `3412851` (part) | `packages/outsider/src/integrate.itest.ts` | new 26 (the outsider) | the sealed exercise's typing leg |
| `3412851` (part) | `services/api/src/internal/usage.itest.ts` | new 24 (metering) | the usage suite's typing case |
| `0ecb21f` | `services/gateway/src/meter.itest.ts` | new 24 (metering) | keep the meter fixture's child output |

**T048b IS THE ONE THAT MATTERS AND ITS OWN COMMENT SAYS WHY.** *"Moved out of US3 by analysis
pass 1, and the reason is worth keeping: leaving it in a P2 story meant stopping after the MVP
could ship a cosmetic feature able to exhaust a customer's message budget."* A typing indicator
that spends a send's budget is a denial of service a client controls by holding a key down.

**AND THE ASSERTION'S SHAPE IS THE PART TO CARRY, NOT THE TEST.** It asserts on the LIMITER
rather than on a counter in Redis: a recording double proves the typing branch never *reaches*
`limits.spend`, where a counter reading would also pass if the branch spent and then refunded.
Two implementations satisfy "the count did not move" and only one satisfies "the call was never
made".

**IN THIS ORDER THE PROPERTY IS TRUE BY CONSTRUCTION AND UNTESTABLE.** `session.ts` returns from
the `typing.send` branch before it reaches anything that could spend — there is no limiter below
it to reach. So new 22 does not merely port a test: it adds a limiter *underneath* an early
return that has been there for nine chapters, and the test that says the early return still comes
first is the one thing standing between a typing indicator and a customer's message budget.

## A FIFTH `ioredis` EXEMPTION, AND A FIFTH REASON — WHICH IS THE POINT NOW

| original commit | artefact | belongs to | what it did |
|---|---|---|---|
| `a7ebbb1` (part) | `services/gateway/src/connections.itest.ts` in `DRIVER_EXEMPT_TESTS` | new 22 (limits) | exempt a suite whose raw client is the STIMULUS |

**THE REASON IS NEW AND THE RULE CANNOT EXPRESS IT.** The four before it are about what the
client reads or writes: three touch no key at all, one composes environment-scoped keys and
argues how. This suite needs a raw client for neither — its subject is delivery and it asserts
on sockets. It needs one to **cause** a membership change, because `Membership` exposes
`onChange`, `subscribeChannel` and `watch` and no `publish`: the api publishes and the gateway
only ever subscribes. So the client is the stimulus rather than the oracle.

    fanout/**                 no key is touched at all — a publish onto a channel UUID
    membership.ts             the same: PUBLISH only, onto member:{channel_id}
    presence.ts               keys ARE composed, and environment-scoped — the limiter's argument
    connections.ts            keys put the ENVIRONMENT FIRST: conn:{env}:{user}:{slot}
    presence.itest.ts         \ suites publishing arbitrary bytes with a client
    membership.itest.ts       / belonging to neither module
    connections.itest.ts      the client is the STIMULUS, not the oracle
    connections.test.ts       a unit test that reads the module's own source from disk

**EIGHT ENTRIES, FIVE ARGUMENTS, AND NEW 22 HAS TO CARRY ALL OF THEM IN ONE COMMIT** — the
both-directions check fires on the rule's own arrival if any is missing, and a blanket "the
gateway's Redis files" would erase five distinctions the rule exists to make.

| original commit | artefact | belongs to | what it did |
|---|---|---|---|
| `83309e5` (part) | `services/gateway/src/connections.ts` in the `ioredis` exemption | new 22 (limits) | exempt a client whose keys put the environment first |
| `23a85c5` (part) | `services/gateway/src/connections.test.ts` in `DRIVER_EXEMPT_TESTS` | new 22 (limits) | exempt a unit test that reads the module's source |

**`connections.ts` IS THE STRONGEST CASE ON THE LIST, NOT THE WEAKEST**, and the reason is
structural rather than argued: `conn:{env}:{user}:{slot}` puts the environment id FIRST, so a
cross-tenant read needs a caller to hand the module another environment's id — which the
session layer takes from the api's verified identity and never from a payload. The other seven
argue about what they touch; this one cannot reach across a tenant without being lied to.

**AND ITS COMMENT REPEATS THE LIST-PLACEMENT TRAP.** The `.itest.ts` sibling is deliberately
NOT on the `**/*.ts` block's `ignores`, because the later `**/*.itest.ts` block would override
it in silence. Two chapters have now written that note; new 22 gets it in writing twice.

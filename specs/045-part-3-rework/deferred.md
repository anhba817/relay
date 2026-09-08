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

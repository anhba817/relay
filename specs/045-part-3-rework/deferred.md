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

# Gaps — 045, Part 3's rework

Things this feature found and has not closed. Each names what is wrong, how it was
measured, and what closing it costs. A gap with no measurement is an opinion.

## 045-1 · EIGHT PART-3 ORDINALS SURVIVE IN TAGGED CHAPTERS' COMMIT MESSAGES

`replay-range.sh` rewrote file contents and passed `%B` through untouched, so every
chapter ported before the sender chapter kept the published messages. Measured on
`rework/base-convention..rework/part3-ch10`:

    3 subjects   feat(3.12): a channel and its members over the public API …
                 feat: JetStream and the first consumer - chapter 3.4
                 feat: The outbox - chapter 3.3
    5 bodies     "chapter 3.5's precedent", "the margin 3.12 declined",
                 "renumbered from `chapter 3.12` to `chapter 3.14`",
                 "3.16 fills it", "run 11 of chapter 3.7's twenty lane runs"

**WHY IT MATTERS MORE THAN A COMMENT DOES.** A subject is the part read detached from
its tree — `git log --oneline` has no repository to grep, and a reader who sees
"chapter 3.4" in a subject cannot check it against anything. This project already made
that argument about task ids in test titles and removed seven of them.

**IT IS FIXED FOR CHAPTER 11 ONWARD AND NOT BEHIND IT.** `rewrite-message.py` now
rewrites bodies through `refrules` and takes a person's table for subjects and for the
ambiguous bodies a rule may not touch. `rework/part3-ch11` carries zero.

**WHAT CLOSING IT COSTS — AND THE FIRST ESTIMATE HERE WAS WRONG.** It was written as
"the trees do not change, only messages, so no fence and no page is affected". That is
false, and what falsified it was reading chapter 11's own published diff: it contains

    -   * 3.15, FR-013, FR-CHN-08).
    +   * channel-control chapter, FR-013, FR-CHN-08).

which is chapter 10's comment being rewritten inside chapter 11's fence, because the
read-class decision covering it was added while porting chapter 11 and chapter 10 was
tagged before it. **Every read-class pair added after a chapter is tagged leaves that
chapter's tree carrying the ordinal and the next one appearing to fix it.** So the
replay changes ten trees, not ten messages, and each affected chapter's fences must be
regenerated and its page re-verified.

Measured on chapter 11: **one line out of 1,800 changed**, in one fence. That is the
whole present cost, which is why it is still deferred — but the ratio is a property of
this chapter's decisions, not a constant, and the next chapter that decides a reference
an earlier tree also carries will add its own. Re-check this number per chapter rather
than assuming it stays at one.

A probe that said "no earlier tree is affected" was run and was WRONG — it reported zero
against a tree where `git show rework/part3-ch10:services/api/src/db/repository.ts`
plainly shows the line. Two minutes with `git show` settled what the probe could not.
**A zero from an instrument with no positive control is not a measurement.**

## 045-2 · THREE FORWARD REFERENCES TO DEFERRED MATERIAL, IN PROSE NO GATE READS

The reorder moves subjects, and a comment written when its subject was two chapters back
now runs ahead of it. Three found while porting the sender chapter, all in shipped
source:

    packages/protocol/src/codes.ts:15    "the argument this file already makes for
                                        `wrong_credential_type` and `quota_exceeded`"
    packages/protocol/src/codes.ts:44    "`wrong_credential_service` the wrong SERVICE"
                                        — named as a sibling "directly above"
    services/api/src/db/repository.ts    FR-029's "every `usage_active_users` row"

`quota_exceeded` is the quota chapter's (new 23), `wrong_credential_service` is a code
this tree does not define at all, and `usage_active_users` is a table the quota chapter
creates. **The honest form already exists in this tree** and is the model for fixing
these: `users.itest.ts:1014` says outright "there is no `usage_active_users` yet".

**Measured by sweeping every deferred symbol against the tree**, `dist` excluded. Not
closed here because the sweep belongs to whichever chapter lands quotas, when the same
pass can turn each of them from a forward reference into a true one.

## 045-3 · A STALE READ-CLASS PAIR IS SILENT

`apply-read-class.py` reports "N matched nothing" as ordinary output, because on any
given tree most pairs legitimately do not apply — the reference is not there yet.
`--require-all` exists for the one tree where all of them should fire, and `--group`
narrows it to a chapter. **Between those two, a mistyped left-hand side in a pair that
never fires anywhere is invisible.**

Measured: 80 pairs, of which 15 fired on the sender chapter's tree and 65 did not, and
nothing distinguishes "not yet" from "never". Closing it means recording, per pair, the
chapter whose tree it is expected to fire on, and failing when that tree passes without
it — which is a table of 80 entries somebody must fill in and keep true.

## 045-4 · A REFERENCE REWRITE DAMAGED FIVE LINES AND SIX TAGS SHIPPED WITH IT — CLOSED

`_orphaned_punctuation` rebuilt its line from two match groups, and `(\S.*)$` stops before
a trailing newline: `.` does not match one and `$` sits in front of it. **Every line that
function touched came back without its terminator and welded to the line beneath it.** A
second defect in the same replay capitalised a subject name at the start of a
*continuation* line, because all three of `place_name`'s sentence-start tests are
line-local and a comment sentence routinely spans lines.

    scripts/stream-info.mjs          "— a" + "// configuration"  ->  "— a// configuration"
    users/users.itest.ts             two comment lines welded
    fanout/fanout.itest.ts           a comment welded to a CODE line
    users/users.itest.ts             "the mechanism The isolation harness built"
    packages/e2e/src/harness.ts      "while The outbox chapter's own suite"

**FOUR OF THE FIVE WERE INVISIBLE TO EVERY GATE.** Joining two comment lines is valid
TypeScript; so is a capital letter mid-sentence. `check:fences` compared the damaged bytes
against the damaged tree and they matched, because a comment that says the wrong thing is
still byte-identical to itself. The fifth welded a comment to a *statement*, and `tsc`
said `';' expected` at a column in the middle of a comment — which is how the whole class
was found. **One instrument out of six saw one instance out of five.**

**THE REPAIR COULD NOT BE A RE-REPLAY.** The reference rules remove ordinals, and the
damaged trees have none left, so running them again finds nothing. `replay-repair.sh`
walks the range applying `repair-welds.py` — a table of exact pairs that **fails on a weld
it does not recognise**, because a pattern loose enough to find these also splits the
fifty aligned tables this repository writes inside comments.

Closed: tags ch5–ch12 re-cut, chapters 1, 2, 5, 6, 10 and 11's fences regenerated, their
mirrors rebuilt, and all eleven ported chapters verify at 0 problems.

**THREE THINGS THIS COST THAT ARE WORTH THE PRICE:**

**The replay range was wrong twice, in the same direction.** First run started at ch5 and
ch5's own tree kept its capital; the fix has to start at the chapter BEFORE the earliest
damage, and finding the earliest damage means asking each tag, not reasoning about it.

**The weld detector had the same blind spot as the weld.** It looked for a second comment
opener, which a comment-welded-to-code does not have. Widened to "sentence-ending
punctuation, then alignment whitespace, then content" — checked against the whole tree,
where it fires on the weld and on none of the tables.

**AND RUNNING `check-chapter` ACROSS ALL ELEVEN PORTED CHAPTERS FOR THE FIRST TIME FOUND
ELEVEN PROBLEMS THAT HAD NOTHING TO DO WITH THIS.** Chapters 1 and 2's fences had never
been regenerated after `rework/base-convention` rewrote their trees. **A per-chapter check
is only a per-chapter check if somebody runs it on the chapters that are already done.**

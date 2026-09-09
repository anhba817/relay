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

**WHAT CLOSING IT COSTS.** A replay of `rework/part3-ch1..rework/part3-ch10` with a
subject map of three lines and five body decisions, then re-cutting ten annotated tags
and re-cutting `rework/part3-ch11` on top. The TREES do not change — only messages — so
no fence, no page and no gate is affected, and each chapter's verification stands.
Deferred because it rewrites ten tags mid-rebuild for a defect that costs nothing while
the rebuild is still running, and the same replay will be cheaper once every chapter is
in and the tags are cut once.

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

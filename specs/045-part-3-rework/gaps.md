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

## 045-5 · THE MDX PASS COMPARED TWO NUMBERING SYSTEMS — CLOSED

`own_id` read `<ChapterHeader id="3.N" />` and the pass skipped every reference whose
chapter number equalled N, as "the chapter's own id". **The header carries the NEW number
and every reference in the prose is an OLD one**, so inside new chapter N the pass silently
skipped references to old chapter N — a different chapter with a different subject.

    new 3.3  is old 3.14      new 3.8  is old 3.13      new 3.12 is old 3.18
    new 3.4  is old 3.12      new 3.10 is old 3.16      new 3.25 is old 3.12

It is a hazard for all twenty-three ported chapters and **it bit two**. Chapter 7 — old 3.7
and new 7, the one coincidence in the renumbering — kept a table row reading `| **3.7** |`
among rows that name their subject. Chapter 8 kept *"Part 3 ends at 3.14"*, which was true
of the published order and is false of this one: the endpoints chapter is now eighteen
chapters ahead of the criterion it unblocks, not two, and the whole near-miss the paragraph
was about is gone. **Both are ordinals in prose, which is bytes like any other to every
gate this repository has.**

Resolved through `chapter-map.json`, so the comparison is old-to-old, and both sentences
rewritten for the order they now sit in.

**AND A QUOTED ORDINAL IS NOT A POINTER.** Chapter 7 argues the convention by exhibiting
the thing it replaces — "`the outbox chapter` encodes no position; `chapter 3.3` encodes one
and nothing checks it" — and the pass substituted inside the quotation, inverting the
sentence it was illustrating. A reference inside a single-backtick code span is skipped now,
counted by backticks before the position rather than matched as a span: a pattern for
"backtick, anything, ordinal, anything, backtick" also matches the GAP between two adjacent
code spans, which is prose. Four of the six candidates in these pages are that shape.

**THE REPORTING LOOP HAD TO LEARN THE SAME FILTER.** It listed the one quoted ordinal as
"left for a reader" when nothing was left. The selector and the report must ask the same
question or the count is about neither.

## 045-6 · A COMMIT THIS ORDER MADE OBSOLETE, AND THE NUMBER IN IT IS WORTH KEEPING

`b285b47` — *"the port map was wrong, not 78% complete"* — is skipped entirely. It touches only
`services/gateway/src/limits.itest.ts`, which arrives with new 22, and its subject is a
hand-maintained table of port bands that **this order deleted three chapters ago**: new 14
retired all of them for `PORT=0` with the port read from each child's own `listening` line.

**ITS ANALYSIS IS THE PART THAT SURVIVES ITS OBSOLESCENCE.** The commit's finding is not "two
entries are missing" but that the map was *wrong*:

    presence.itest.ts   4700 + %200   →  4700-4900
    meter.itest.ts api  4710 +  %60   →  4710-4770   ← strictly inside the range above

**One unregistered range strictly contains a registered one**, and the gateway's integration
config sets no `fileParallelism`, so both files run at once. P = 1/200 per run against an
observed 2.5–5% failure rate for those two files — a contributor rather than the cause, and the
first hypothesis in that ledger item with a number attached.

And it names why the earlier chapter's elimination could not see it: that chapter ruled out "a
port collision" because *"the failing ports are in each file's own range"* — **the colliding
port IS in each file's own range.** An elimination is only as good as the property it tests, and
that one tested the wrong property.

**WHAT THIS ORDER SHOWS THAT THE PUBLISHED ONE COULD NOT.** The commit ends *"left as it is
rather than fixed here, because moving a range is another chapter's change to another chapter's
file"* — which is true of a table and false of the mechanism. Rebuilding by subject put the two
suites that owned the worst bands in the same chapter, so the fix was one chapter's change to
its own files, and the table went rather than gaining two rows. **A defect that is nobody's to
fix is a defect the ordering created**, and this is the clearest instance of it in the rework so
far.

## 045-7 · THE REORDER LEFT THREE SENTENCES FALSE FOR SIX CHAPTERS, AND PUBLISHED FIXED THEM LATE TOO

Measured while porting new 17. Three comments in three files said, in the PRESENT tense,
that `MessagesController` declares no `@Accepts` and the guard therefore falls back to
`EITHER`:

    services/api/src/db/repository.ts:2131
    services/api/src/messages/messages.controller.ts:95
    services/api/src/messages/messages.itest.ts:153

`@Accepts(` arrived on that controller in `rework/part3-ch11` (`560bd5c`, old 3.17, the
sender chapter), so all three were false from new 11 onward. They were corrected in new
17, which is where old 3.23 corrected them — six chapters after this order made them
wrong, and the port carried that lateness in rather than fixing it in place.

**THE REORDER DID NOT CAUSE THIS, IT LENGTHENED IT.** Published was wrong for six
chapters too — 3.17 through 3.23 — which is why old 3.23 is the commit that carries the
fix at all. What the reorder changes is only which chapter numbers the staleness spans.
So this is not a rework defect to be repaired quietly; it is a published one whose
correction the rework should arguably move EARLIER, to new 11.

**WHY IT WAS NOT MOVED.** The correction is one clause in each of three comments and it
would be free to move. What is not free is the precedent: this feature's rule is that a
chapter ports what its published commit did, and a chapter that also fixes prose its
predecessor left stale becomes a chapter whose diff no published fence matches. Two
fenced files are involved (`repository.ts`, `messages.controller.ts`), so moving the
clause means regenerating new 11's hunks for a change new 11's published commit never
made.

**WHAT CLOSING IT COSTS.** Three one-clause edits in new 11's port, `regen-fences` on new
11 and new 17, and a sentence in each chapter's prose explaining a correction the reader
cannot see a cause for — because the cause is in the chapter they are about to read. That
last cost is the real one, and it is why this is filed rather than done.

**AND THE CLASS IS THE ONE THIS PROJECT KEEPS RECORDING.** Two more copies of the same
sentence (`users/users.controller.ts:48`, `messages/messages.controller.ts:65`) were
already past tense before this chapter, so the tree held five copies of one fact in two
tenses. A grep for the claim found all five in one command; nothing else would have.

## 045-8 · THREE ROUTES WERE CLASSIFIED AND NEVER ATTACKED, AND PUBLISHED PART 3 COULD NOT SEE IT — CLOSED

Measured while porting new 17. The revisions chapter classifies three routes in
`isolation/targets.ts` — `GET …/:messageId/edits`, `PATCH …/:messageId`,
`DELETE …/:messageId` — and old 3.23 wrote no gauntlet attack for any of them. Ten
commits, none touching `gauntlet.itest.ts`.

**PUBLISHED HAD NO TEST THAT COULD ASK.** `git show part3-ch24:…/gauntlet.itest.ts` has no
`attacked` set and no accounting test; the file's own header says there was *"nothing
anywhere that knew which endpoints had been attacked and which had merely been
classified."* The rework's new 4 wrote that accounting test, and it fired on this chapter
with all three routes named by path:

    classified but never attacked: GET /v1/channels/:channelId/messages/:messageId/edits,
    PATCH /v1/channels/:channelId/messages/:messageId,
    DELETE /v1/channels/:channelId/messages/:messageId

**IT ONLY FIRED IN THE COVERAGE RUN.** `targets.itest.ts` and `gauntlet.itest.ts` are
different files, and the accounting test lives in the second one — so the three
per-commit itest runs this chapter's port made were all green. The full battery is what
asked, 258 seconds in.

**FOUR ATTACKS WERE WRITTEN, AND THE FOURTH IS THE ONE NO PAIR CAN EXPRESS.** Every
helper in `attack.ts` forges BOTH identifiers, which a nested route can satisfy while
checking only the outer one. The added case presents the attacker's OWN channel with the
victim's message id, against all three verbs. Falsified by dropping
`eq(messages.channelId, channelId)` and `eq(channels.environmentId, …)` from
`messageExistsIn`: the history route answered **200 to a cross-tenant read** and the other
44 attacks stayed green. `send` is now exported from `attack.ts` for that one caller,
with the reason written at the export.

**THE EDIT AND THE DELETION WERE NOT REACHABLE THAT WAY**, which is worth recording
because it is the half the probe did NOT show: `editMessage` and `deleteMessage` each
join the channel and the environment inside their own transaction, so the unscoped
`messageExistsIn` could not be used against a write. One read-only hole, and the test that
finds it also covers the two writes that were already closed.

## 045-9 · THIRTY-SIX SPAN CLAIMS COUNTED IN CHAPTERS, AND THE REORDER MOVED MOST OF THEM

Measured while porting new 17, across the seventeen ported English pages. Prose says how
long a thing has been true by COUNTING CHAPTERS — *"for twenty-two chapters"*, *"eleven
chapters later"* — and a reorder changes every one of those numbers without touching a
single ordinal. `rewrite-mdx-refs.py` cannot see them: there is no `3.` in them.

    36  numeric span claims          "for twenty-two chapters", "twenty-four chapters later"
    34  relative-position phrases    "the previous chapter", "two chapters ago"
    12  of the 17 ported pages carry at least one

**THE SHARPEST INSTANCE IS TWO SENTENCES APART.** New 11 reads:

    For fourteen chapters that was fine. Nothing read the sender.

    Then the channel-control chapter made the sender decide whether a private channel is
    visible, the user-surface chapter made it decide what a channel listing renders …

The second paragraph carries substituted subject names — the port rewrote it. The first
carries a published count and was left. **One passage, one pass, two treatments**, because
the tool that did the rewriting only looks for digits after a `3.`.

**AND THE CHECKABLE ONES ARE FINE, WHICH IS THE SIGNAL.** New 13 says `session.ts` *"is
fenced by eight chapters before this one — four in Part 2 and four in Part 3"*. One command
answers it:

    grep -rln 'title="services/gateway/src/session.ts"' 'app/(en)'
    → part-2: 05, 06, 07, 08         four
    → part-3 before 13: 02, 03, 07, 10   four

Still exactly true. The claims that survived are the ones a command can answer; the ones
carrying stale numbers are the ones where the anchor is a sentence rather than a file.

**WHAT IS PROVABLY STALE, BY ARITHMETIC ALONE.** A claim of the form "for N chapters" whose
anchor is the start of Part 3 is stale by exactly the renumber delta:

    new 16  "for twenty-one chapters"   old 22, 21 before it   →  fifteen
    new 17  "for twenty-two chapters"   old 23, 22 before it   →  sixteen   (fixed in new 17)
    new 15  "for twenty chapters"       old 21, 20 before it   →  fourteen
    new 11  "for fourteen chapters"     old 17                 →  needs its anchor read
    new 09  "for twenty-three chapters" old 15, cross-part     →  needs its anchor read

**ONLY NEW 17's IS FIXED.** Every other page is already committed to the tutorial
repository, and the fix is not mechanical: each number's anchor is a chapter named in prose
somewhere else, so closing this means reading 36 passages and computing 36 spans. Two of
them (new 07's "seven chapters", new 13's "eight chapters") are already correct and would
be broken by a blanket adjustment, which is why a delta applied everywhere is worse than
the gap.

**AND THE RELATIVE PHRASES ARE THE WORSE HALF.** "The previous chapter" is not a number and
cannot be checked at all — it is right when the reorder happens to preserve adjacency and
silently wrong otherwise. New 17's one instance (*"the previous chapter learned that"*, of
the connection-cap chapter) is still correct because old 22 → new 16 sits directly before
old 23 → new 17. That is luck, and 33 more sit on the same luck.

**WHAT CLOSING IT COSTS.** For each of the 70: find the anchor, decide whether the span is
within Part 3 or crosses into Part 2, recount, and edit both locales. Roughly a chapter's
worth of work with no gate to confirm it afterwards — which is the same shape as this
feature's own SC-006 problem. A cheaper partial: a checker that FAILS on any "for N
chapters" in a Part-3 page, forcing each one to be either recounted or rewritten to name a
chapter instead of counting to it. Naming is the better prose anyway, and it is what the
reference convention already decided for ordinals.

## 045-10 · A POSSESSIVE THAT DID NOT SHOUT WITH ITS OWN CLAUSE, IN FIVE TAGGED CHAPTERS

Measured while porting new 17. `place_name` upper-cases the substituted name when the
clause around it is all-caps, and the `chapter` branch's pattern —
`(?i:chapter) 3\.\d{1,2}`, with no `(?:'s)?`, which only `bare` has — stops before the
possessive. So the case conversion could not reach it:

    // CHAPTER 3.23's EDIT HISTORY  ->  // THE REVISIONS CHAPTER's EDIT HISTORY

Eight instances across seven files. **Nothing in this feature could see them**: the ordinal
IS gone, so `classify-refs` reports zero and `check-chapter` compares the same bytes on both
sides; a lower-case apostrophe-s is valid TypeScript and valid prose.

    rework/part3-ch10   services/api/src/isolation/gauntlet.itest.ts:472
    rework/part3-ch11   services/api/src/db/schema.ts:250
    rework/part3-ch14   services/gateway/src/membership.ts:20
    rework/part3-ch14   services/api/src/membership/publisher.ts:99
    rework/part3-ch15   services/gateway/src/typing.itest.ts:880

**FIXED IN THE TOOL AND IN NEW 17.** `refrules.place_name` now upper-cases a possessive it
finds immediately after the match, with four cases run against it — the all-caps possessive,
the all-caps non-possessive, the lower-case possessive, and a mixed line that must stay
lower. `repair-welds.py` gained the three exact pairs for this chapter's `targets.ts`, and
`replay-repair.sh` re-cut the chapter over its whole range rather than from the first damaged
commit, which is the mistake this feature made twice in the other direction.

**WIDENING THE BRANCH PATTERN WAS THE WRONG FIX AND THAT IS THE INTERESTING PART.** Adding
`(?:'s)?` to the `chapter` branch would put the possessive inside the match — and then the
DELETE rule swallows it, and `classify-refs`' published counts change eight chapters into a
feature that has stated 1,614 references in 207 files as a measured figure. A case bug fixed
where case is decided costs one function; fixed in the pattern it costs the feature's own
arithmetic.

**WHAT CLOSING THE FIVE COSTS.** `replay-repair.sh` over `rework/part3-ch9..rework/part3-ch15`
with five more exact pairs, re-pointing six tags, then `regen-fences` and `check-chapter` on
chapters 10, 11, 14 and 15 — because a tag's tree changing changes every fence downstream of
it in those chapters. That is the same operation this feature already ran once for the weld
damage, where the defect changed what a line MEANT. Here it changes one apostrophe's case, so
it is filed rather than done, and it is filed with the command that would do it.

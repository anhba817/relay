# Gaps — 045, Part 3's rework

Things this feature found and has not closed. Each names what is wrong, how it was
measured, and what closing it costs. A gap with no measurement is an opinion.

## 045-1 · EIGHT PART-3 ORDINALS SURVIVE IN TAGGED CHAPTERS' COMMIT MESSAGES — CLOSED

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

## 045-7 · THE REORDER LEFT THREE SENTENCES FALSE FOR SIX CHAPTERS, AND PUBLISHED FIXED THEM LATE TOO — CLOSED

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

## 045-11 · NEW 3 PORTED THE TYPED THROWER AND DROPPED TWO OF ITS THREE HUNKS — CLOSED

Measured while porting new 18, phase 6. Published `89fd038` — *"thirteen codes, one URL
rule, and a typed thrower so a typo cannot ship a dead link"* — did three things. The
rework's new 3 (`3fd9db5`, "errors that resolve") ported one:

    ported      ERROR_CODES, protocol-error.ts, the filter, session.ts's ErrorCode
    NOT ported  docsUrl's anchor form and its per-call env base
    NOT ported  zod-validation.pipe.ts's switch to protocolError

**THE URL RULE IS THE SERIOUS HALF, AND IT IS A DEAD LINK PER CODE.**
`docs/08-error-reference.md` is ONE document with `## <code>` headings — one `### ` and
eleven `## `. Published's rule resolves against it:

    published    `${base}#${code}`      -> …/errors#media_not_available   an anchor that exists
    this tree    `${BASE}/${code}`      -> …/docs/errors/media_not_available   a page that does not

New 3 did not invent the path form: **Parts 1 and 2 publish it** (`docs/errors/not_found` in
`part-1/chapter-04` and `part-2/chapter-05`), and they were never renumbered. Published's
answer was to teach the path form early and CORRECT it in Part 3, at old 3.12. The rework
kept the early form and never ran the correction — so the whole tree now ships the URL that
89fd038 exists to prevent, and it does so consistently: new 3 also wrote
`it("appends the code VERBATIM — no slug transform, no case change")` asserting
`` `${ERROR_DOCS_BASE}/${code}` ``, so the test agrees with the defect. **Nothing could
catch this**, because the function and its test were written together.

**AND THE ENV BASE WENT WITH IT.** Published reads `RELAY_DOCS_BASE_URL` per call with a
test named *"reads the base URL per call, not at import"*; this tree has a `const`. A
preview deployment cannot point its error links at its own docs.

**THE PIPE'S HALF SURFACED ON ITS OWN AND IS FIXED IN NEW 18.** `media_not_available` is a
422, and a `BadRequestException` cannot carry a code that is not 400 — so phase 6 could not
be ported without the switch. It is made there with the reason written at the top of the
file, naming the chapter that owed it. **The one call site that never needed typing is the
one that proved it was needed**, which is the same shape as the SRS clauses this feature
found by opening the file to make an edit.

**WHAT NEW 18 DID NOT DO.** Change `docsUrl`. That is one line and it rewrites every
`docs_url` the platform emits, in five production call sites and in the fences of four
already-paged chapters plus Parts 1 and 2 — inside a chapter about attachments. Chapter
18's own route test was written to survive either rule instead: it asserts
`body.docs_url === docsUrl("media_not_available")`, deriving the URL from the package that
builds it rather than restating a separator. `codes.test.ts` owns the rule, and one place
should.

**WHAT CLOSING IT COSTS.** `docsUrl` and `ERROR_DOCS_BASE` in new 3, its two URL tests,
then `regen-fences` and `check-chapter` on new 3 and on every later chapter whose fences
show an error envelope — and a decision about Parts 1 and 2, which are outside this
feature's scope and currently publish the form new 3 would be leaving behind. That last
point is why this is filed with a question rather than a patch: published answered it by
correcting mid-book, and whether the rework should correct in new 3 or teach the anchor form
from Part 1 is not a renumbering decision.

## 045-12 · THE REWORK TREE HAS NO LANE RESET, SO ITS BROKER ACCUMULATES AND ONE SUITE HANGS — CLOSED

Measured while porting new 18. `consumer.itest.ts` was run alone to reproduce the chapter's
"six red tests" claim and produced no output for six minutes before being stopped. Both
node processes showed ~0 seconds of CPU against 5:49 elapsed — which is what a suite waiting
on JetStream deliveries looks like either way, so the CPU reading is NOT evidence of a hang.
What the broker said is:

    curl -s 'localhost:8222/jsz?consumers=1&streams=1'

    EVENTS msgs 8520
        recorder            pending 14
        itest-basic-…       pending 0
        walk-c7b02d3f       pending 0
        itest-shared-…      pending 0
        itest-poison-…      pending 0
        itest-garbage-…     pending 0
        itest-catchup-…     pending 0

**EACH TEST LEAKS A DURABLE CONSUMER AND EACH ONE PAYS A FULL STREAM SCAN.** Six durables
from earlier runs, all caught up, on a stream of 8,520 messages nothing drains — so every
new durable the suite creates walks the whole backlog before it reaches its own messages.

**THE SELF-CLEANING THIS LANE RELIES ON DOES NOT EXIST HERE.** CLAUDE.md records that
`reset-lane.itest.ts` runs the real purge script and `@relay/test-harness` sorts first, so a
full integration run begins by purging. That script is 043/044 work on `main` — AFTER Part 3
— and `find . -name 'reset-lane*'` in this tree returns nothing. **The rework's lane
degrades run by run and there is no floor under it**, which also means the "no two batteries
are comparable" rule is back in force for every timing this feature reports.

**WORKED AROUND, NOT FIXED.** Purging `EVENTS` and dropping the six leaked durables took the
stream to zero and the suite ran. That is a hand operation performed from a scratch script,
not a checked-in one, and it purges lane debris rather than data — the same distinction
`reset-lane.mjs` makes.

**WHAT CLOSING IT COSTS.** The purge script and its test are one file each and they are
`main`'s, not this feature's; porting them into the rework tree would put post-Part-3 work
inside a Part-3 chapter, which is the thing `deferred.md` exists to prevent in the other
direction. The honest options are to run the full integration lane rather than one suite
(the sort order then purges first — but only once `reset-lane` exists), or to keep purging
by hand and say so beside every number. **This gap is why every duration in new 18's
close-out is reported with the broker's message count next to it.**

### RE-MEASURED AT NEW 25, ON A DIFFERENT SUITE, AND THE NUMBER IS WORSE

New 25's coverage battery went red on `dispatcher.itest.ts` — *"Test timed out in 60000ms"* on
one case. The suite passes alone, three times for three: **16/16 in 126s, 73s and 73s.** A suite
whose whole run takes 73 seconds has a case that cannot afford a loaded lane, and the lane said
what it was carrying:

    ANALYTICS   msgs=  84   consumers= 0
    EVENTS      msgs= 293   consumers=15
    DELIVERIES  msgs= 660   consumers=14

**THIRTY-ONE DURABLE CONSUMERS AND THREE THOUSAND FOUR HUNDRED AND FORTY-EIGHT STALE ROWS.**
Borrowing `main`'s own `scripts/reset-lane.mjs` — copied in, run once, deleted again, never
committed — cleared:

    ANALYTICS:   137 -> 0 messages,  0/0  consumers deleted
    DELIVERIES:  706 -> 0 messages, 15/15 consumers deleted
    EVENTS:      303 -> 0 messages, 16/16 consumers deleted
    webhook_deliveries: 3,448 stale pending rows deleted

The original entry measured six leaked durables on one stream. This is thirty-one across two,
plus a table of pending deliveries nothing was ever going to drain. **The curve has a known
endpoint**: that script's own header records the state it was written for — *"216 durable
consumers on DELIVERIES, with 27,847 webhook deliveries due."*

**AND THE SAME BATTERY, TWENTY MINUTES APART, PRICES IT:** 457.02s on the accumulated lane,
**399.68s on the reset one** — 57 seconds, 12.5%, for no change to a line of code. That is four
times SC-005's 10% threshold and the same order as the noise CLAUDE.md measured on `session.ts`,
which is the reason a duration is quoted with its lane state or not at all.

**AND IT CHANGES WHAT A GREEN BATTERY MEANS.** Chapters 22, 23, 24 and 25 were all measured on a
lane nobody had reset, so their durations include whatever the broker had accumulated by then —
which is a monotonic quantity. `check:fences` and the test counts are unaffected; the TIMINGS are
comparable only in the way CLAUDE.md already qualifies, and now for a second reason it names.

**THE FIX IS NEW 8'S, NOT THIS CHAPTER'S.** `scripts/reset-lane.mjs` and
`packages/test-harness/src/reset-lane.itest.ts` belong to the harness, which is new 8. Porting
them into new 25 would put the lane's own infrastructure into the gauntlet milestone's diff.

## 045-13 · A DOCUMENTED CODE WITH NO PRODUCER, AND THE GATE THAT COUNTS CANNOT SEE IT — CLOSED

Measured while porting new 19. `docs/08-error-reference.md` publishes six webhook
refusals; `webhooks.service.ts` throws five. The sixth,
`webhook_event_type_unknown`, has a section — status, retryability, field — and nothing
anywhere emits it: `create` accepts any string in `event_types`.

**`check:errors` PASSES AND IS RIGHT TO.** It reads the built `dist` against the docs and
reports *"27 codes, 27 sections, each with a cause and a client action"*. Both directions
it checks are satisfied because it compares the REGISTRY with the SECTIONS — and a code
can be in both while no code path constructs it. What it cannot ask is whether anything
produces the refusal, which is the same shape as the producer test the revisions chapter
had to write by reading `session.ts` as text.

**THE OTHER FIVE WERE THE OPPOSITE DEFECT AND ARE FIXED IN NEW 19.** They were documented,
unregistered, and thrown as bare 422s that shipped `code: "internal_error"` — measured on
this tree with the exact body. So this one file held both directions of the same hole at
once: five codes the registry lacked, and one the registry has with nothing to emit it.

**WHY IT IS NOT FIXED HERE.** Refusing an unknown event type is new product behaviour that
published's chapter 3.5 did not have, and the set to validate against is a decision:
`OUTBOX_EVENT_TYPES` holds five names in this tree and FR-WHK-02 spells eight, three of
which have no producer yet. Validating against the five would refuse a subscription to an
event the contract publishes — which is the mistake feature 044's FR-016 made and had to
amend, recorded in CLAUDE.md as *"a design in which a case cannot arise beats a branch
that handles it"* inverted.

**WHAT CLOSING IT COSTS.** One decision — which set — then one refusal, one code
registration, one row in `webhooks.itest.ts`'s vocabulary test, and a paragraph in the
chapter that makes it. Cheap; the decision is the part that needs a person.

## 045-14 · THE REWRITER IMPORTED THE PROTECTION AND NEVER CALLED IT — CLOSED

Found while porting new 19, by reading the replayed file rather than the tool's report.

`refrules.DELIBERATE` names the three lines of one comment whose SUBJECT is an ordinal —
`schema.ts`'s NAMED-NOT-NUMBERED paragraph, the origin of this feature's convention and
quoted in `subjects.json`'s own `_why`. `classify-refs.py` honours it and prints
*"3 kept ON PURPOSE (refrules.DELIBERATE) — a comment whose subject IS an ordinal"*.

**`rewrite-refs.py` IMPORTS `is_deliberate` ON LINE 31 AND NEVER CALLS IT.** So the
counter reported a protection the rewriter did not enforce, for nineteen chapters, and the
substitution ran:

    - // NAMED, NOT NUMBERED. This line used to say "chapter 3.7's cross-tenant
    + // NAMED, NOT NUMBERED. This line used to say "the deduplication chapter's cross-tenant

The sentence now claims the line used to say the thing it says now. **The ordinal WAS the
evidence**, and the tool that exists to remove ordinals removed the one that was being
quoted as a specimen.

**AN INSTRUMENT REPORTING A PROTECTION IT DOES NOT ENFORCE IS WORSE THAN ONE WITH NO
PROTECTION**, because the report is the thing a reader checks. Two tools, one definition,
and only one of them applied it — the same shape as `check-fence-chain`'s corpus being
narrower than its claim, and as the three classifiers that disagreed 4.5×.

**FIXED AND CONTROLLED IN BOTH DIRECTIONS.** The rewriter now skips a deliberate line, with
the cost written at the check. Falsified by disabling the guard: `found 1 rewritten 1`,
naming `schema.ts:597`. Re-enabled: `found 0`. The paragraph was restored in the tree
before the chapter's replay, and `classify-refs` reports 3 kept on purpose after it.

**WHAT IT MEANS FOR THE EIGHTEEN TAGGED CHAPTERS.** Nothing to repair: the paragraph
arrives with new 19, so no earlier tag ever contained a deliberate line for the rewriter to
damage. This gap was a loaded gun rather than a wound, and it fired on the first chapter
that handed it something.

## 045-15 · THE WELD DETECTOR FIRED ON A NESTED BULLET, AND EXITED 1 — CLOSED

Found while porting new 20, by running `repair-welds.py` in the per-chapter loop.

    3 UNRECOGNISED weld(s) — the bug is back, or the detector is:
      services/api/src/db/repository.ts:812  *   * ONE ENDPOINT, named by the caller, …
      services/api/src/db/repository.ts:815  *   * DELIVERED EVEN WHEN DISABLED — …
      services/api/src/db/repository.ts:819  *   * NO CLAIM LEDGER. Expansion claims …

All three are a two-level JSDoc list. The clause searched `s.lstrip()` for
`\S\s{2,}\* ` — content, alignment whitespace, a second comment opener — and in
`*   * ONE ENDPOINT…` the `\S` it matched was **the opener's own asterisk**. So the
detector reported three legitimate bullets as damage and the script exited 1.

**A DETECTOR WITH FALSE POSITIVES TEACHES ITS READER TO IGNORE IT**, which costs more than
the check is worth — and this one was written precisely because "a checker's blind spot is
worse than its absence". A false alarm is the same failure wearing the other face.

**THE DISTINCTION IS WHAT COMES BEFORE THE SECOND OPENER.** A weld has PROSE there; a
nested bullet has only whitespace. So the opener run is stripped before the search and the
`\S` has to be real content. Verified in both directions: the three bullets stop firing,
and a line of the shape the `REPAIRS` table records —
`* So a REST send needs one to exist — and \`createUser\`     * makes a person.` — is still
reported as unrecognised.

**THIS IS THE THIRD FAULT FOUND IN THIS FEATURE'S OWN TOOLING IN THREE CHAPTERS**, after
the read rule listing eight of nineteen and the rewriter never calling `is_deliberate`. All
three were found by RUNNING the tool on new input rather than by reading it, and none was
visible to any test: the tooling has no tests of its own, which is the oldest item on this
ledger and now has three instances behind it.

## 045-16 · A DEFAULT PARAMETER THAT IS NEVER CONSTRUCTED, AND ONLY ONE INSTRUMENT COULD SEE IT — CLOSED

Measured while porting new 21. Every test passed — 1,120 across 74 files, both lanes green
— and the battery exited 1 on one line:

    ERROR: Coverage for functions (99.12%) does not meet
           "services/api/src/db/repository.ts" threshold (100%)

The uncovered function was not a branch nobody tested. It was a **default parameter**:

    onError: (row: DisableNotificationRow, error: unknown) => void = () => {},

`() => {}` is a function that exists and never runs, because the one caller —
`notification-relay.ts`'s `drainOnce` — has always passed a logging callback. v8 counts it,
and 113 of 114 is 99.12%.

**NOTHING ELSE IN THE REPOSITORY COULD HAVE ASKED.** Not the typecheck: a default is
well-typed. Not lint: the parameter is used. Not either test lane: they were green. Not the
statement or branch thresholds: one arrow body is one function and no statements. Only a
per-file FUNCTION threshold pinned at 100 — rather than at whatever the file happened to
measure — can produce this failure, which is the argument for pinning at the requirement
instead of at the reading.

**DELETED RATHER THAN COVERED, THE SIXTH TIME THIS FILE'S RATCHET HAS DONE THAT.** And the
deletion is right on its own terms, not merely convenient: `onError` is how a caller learns
a row was CLAIMED AND NOT SENT, so a default that swallows the failure silently is the
wrong default. Required means the compiler asks the question instead of a reviewer. Battery
re-run: 1,120 tests, exit 0, `repository.ts` functions back to 100.

**AND A THIRD FILE JOINED THE LIST THAT READS LOW FOR WHERE ITS CODE RUNS.**
`notifications/notification-relay.ts` measures 58.06/50/62.5/62.06 because its loop is
started by `main.ts` in a spawned api; what this process reaches is `drainOnce`, called
directly by the suite. It sits beside `internal/dispatch.controller.ts` (9.09%) and
`webhooks/delivery-relay.ts` (28.12%) — three files now, all unpinned, and the fact is
recorded in the config rather than in three lowered pins that would describe a test
topology instead of the code.

## 045-17 · THE LEDGER OWED EIGHT `ioredis` EXEMPTIONS AND THE TREE NEEDED TWELVE, ONE OF THE EIGHT WRONG

`deferred.md` recorded the inverted deferral carefully — a rule that arrives after the files it
must exempt — and it recorded the count wrong in both directions. Its headline is **"EIGHT
ENTRIES, FIVE ARGUMENTS, AND NEW 22 HAS TO CARRY ALL OF THEM IN ONE COMMIT"**, built up one
chapter at a time across four separate notes as each porting session found the next one.

**MEASURED BY ASKING THE TREE INSTEAD OF READING THE LEDGER.** One grep for the importers:

    grep -rln 'from "ioredis"' --include=*.ts .   →   13 files

Thirteen, of which `services/api/src/limits/store.ts` is the rule's own home and covered by the
`services/api/src/limits/**` carve-out. **Twelve need an entry**, not eight. The four the ledger
never recorded:

    services/api/src/fanout/fanout.itest.ts     the fan-out chapter — the suite, not just `fanout/**`
    services/api/src/membership/publisher.ts    the api's half of the membership fabric
    services/gateway/src/typing.ts              the typing chapter, publish AND subscribe
    services/gateway/src/typing.itest.ts        its suite

The typing chapter is the sharp one: `deferred.md` has a whole section titled **"THE TYPING
CHAPTER OWES ONE TEST TO THE LIMITS CHAPTER, AND IT IS THE SHARPEST ONE"** — T048b, a real
finding — and while writing it nobody noticed that the same chapter's two files import `ioredis`
and would go red on the rule's arrival. **A ledger entry written about one artefact does not
sweep the commit it came from.**

**AND THE EIGHTH ENTRY WAS AN EXEMPTION OVER NOTHING.** `services/gateway/src/connections.test.ts`
is recorded as owed, with a reason — *"a unit test that reads the module's own source from
disk"*. It reads the source and imports nothing restricted, so the rule has nothing to say about
it. Adding it fails `driver-exempt.test.ts`'s stale-entry check, and that is how it was caught:

    AssertionError: services/gateway/src/connections.test.ts is exempt from the driver
    rule and imports none of pg, drizzle-orm, ioredis: expected [] to not deeply equal []

The published tree does not list it either. The ledger row came from reading a chapter's diff
rather than the file it names.

**WHAT ACTUALLY HELD THE LINE WAS THE CHECK, NOT THE LEDGER.** Both halves of
`driver-exempt.test.ts` were falsified against this commit — a removed exemption gives the
rule's own error on `presence.ts`, a stale entry gives the assertion above, a third glob gives
`expected [ 'db/**', …(2) ] to deeply equal [ 'db/**', …(1) ]`. **The ledger is a reminder; the
both-directions test is the instrument.** 044 filed that asymmetry as a gap and closing it is
what made an eight-versus-twelve error a red test rather than a chapter reddened months later.

**ONE DIVERGENCE FROM PUBLISHED, DELIBERATE.** Published exempts `services/api/src/fanout/**`
and `services/api/src/membership/**` as directory patterns. This tree lists their two files by
path, because its own comment says a pattern *"would silently absorb the next file added
there"* and `driver-exempt.test.ts` asserts exactly which entries may be globs. Two are:
`db/**` and `limits/**`, the two data-access LAYERS the rule carves out.

## 045-18 · A PARAMETER INSERTED BEFORE AN OPTIONAL ONE RENAMED EVERY LATER ARGUMENT, AND THE TYPECHECK AGREED

`sendError` in `services/gateway/src/session.ts` took `(socket, code, message, field?)` in this
tree. The limits chapter's `request_id` commit adds a fourth parameter — and published put it
**before** `field`, because in the published order `field` did not exist yet and was appended two
chapters later:

    function sendError(socket, code: ErrorCode, message: string,
                       requestId: string = newRequestId(),
                       field?: string)

**IN THIS ORDER `field` IS ALREADY THERE, SO THE INSERT IS A RENAME.** One call passed a fourth
argument — the invalid-frame refusal, handing over `frame.error.issues[0]?.path.join(".")` — and
after the merge that string was the `request_id`, with `field` gone. **Both parameters are
`string`, so nothing could complain**: `pnpm typecheck` green over twelve packages, `pnpm lint`
green, `pnpm test` green over 11 packages. The frame then carries a zod path where a support
ticket expects an id, and carries no `field` at all.

**WHAT DID SEE IT WAS ONE INTEGRATION ASSERTION**, and it was written three chapters earlier for
its own reason (T041a, `session.itest.ts:403`). Falsified by reintroducing the swap:

    AssertionError: expected undefined to be 'payload.attachments'
      services/gateway/src/session.itest.ts:403

So this is not "nothing could have caught it" — it is **nothing in the per-commit gate could**.
The loop for this rework runs typecheck/lint/test per commit and the battery per chapter, which
means a defect of this shape lives inside the chapter until its end. Fixed by passing an explicit
`undefined`, with the reason at the call, matching what published's later state does anyway.

**THE GENERAL RULE THIS EARNS.** When a port inserts a parameter, the question is not whether the
signature compiles — it is **which existing call sites pass an argument at or after that
position**. Two `string` parameters make the compiler useless for it, and a positional API of
four-plus arguments makes it likely. Read the call sites; there were nine and only one mattered.

## 045-19 · TWO COMMENTS ARGUED FOR OMITTING A FIELD, AND THE ARGUMENT INVERTED WHEN THE FIELD BECAME REQUIRED

Both gateway suites that forge one frame per union member carried a note on the `error` sample:

    // NO `request_id`. The payload is a `strictObject`, so an extra field is refused
    // as `invalid_frame` — and this loop asserts `unknown_frame_type`, which is a
    // claim about DIRECTION. A sample that fails validation tests the validator
    // instead, and the assertion then passes or fails for the wrong reason.

Every clause of that is true, and the conclusion inverts the moment `request_id` goes from
absent to required: the same `strictObject` that refused the extra field now refuses its
absence. `session.itest.ts` came back

    AssertionError: direction refusal for error: expected { code: 'invalid_frame', …(4) }
    to match object { code: 'unknown_frame_type' }

which is exactly the failure the builder's own header warns about — *"a frame that fails
`safeParse` is answered `invalid_frame` and never reaches the direction check"* — arriving from
the other side. `isolation.itest.ts` held the same comment, was not run by the per-commit gate,
and would have failed the same way.

**THE REASON SURVIVES AND THE INSTRUCTION DOES NOT.** The durable half is *"the sample must be
exactly what the schema accepts, or this loop tests the validator instead"*. The perishable half
is the list of fields that satisfies it. Both comments now say which half is which, so the next
field to arrive reads as an update rather than a contradiction.

**AND THIS IS THE PRODUCER/READER INVERSION IN A THIRD PLACE.** `CLAUDE.md` keeps chapter 3.24's
lesson — an argument right about a schema the platform BUILDS inverts about one that READS off a
durable queue. A test fixture is a producer for a schema it does not own, which makes it the same
shape of mistake: **a claim about what a schema refuses is a claim with a date on it.**

## 045-20 · A HELPER ARRIVED THIRTEEN CHAPTERS BEFORE THE FIELD IT STRIPS, AND ITS DOCBLOCK SAYS OTHERWISE — CLOSED

`services/api/src/isolation/compare.ts` holds `withoutRequestId`, the indistinguishability
oracle three isolation assertions compare bodies through. Its docblock states:

> *"Chapter 2.2's suite needed to prove that a foreign channel answers exactly as an absent one;
> **the rate limiter added `request_id` to every error body and forced this helper into
> existence**; and there it stayed…"*

**IT ARRIVED AT NEW 9 AND THE LIMITER IS NEW 22.** Measured — the file's first commit is
`d6aa3ef` (*"feat: the private type decides something, on every read"*), whose earliest chapter
tag is `rework/part3-ch9`. Asked the tree what produced the field at that point:

    git grep -ln 'request_id' rework/part3-ch9^{commit} -- services packages

Eleven files, and **not one of them puts `request_id` in an error body**. `service-kit`'s
`serve()` has it in the LOG line beside the 404 body, not in it; `zod-validation.pipe.ts` and
`repository.ts` only mention it in comments — the pipe's saying, correctly, that the field *"was
declared in 1.3 and first sent by the rate limiter"*. So from new 9 until new 22's
`request_id` commit, `withoutRequestId` deleted a key no body had: **a no-op wrapped around
three assertions that were passing for a reason unrelated to it.**

**THIS IS NOT A DEFECT IN THE ASSERTIONS AND THAT IS THE POINT.** The three comparisons are
right, and they were right without the helper. What is wrong is a docblock that explains the
file by an event thirteen chapters ahead, so a reader at new 9 is told the code answers a
pressure that does not exist yet — and cannot check the claim, because the thing it cites has
not been written. `gaps.md` 045-2 filed three forward references of this shape; this is a fourth
and the strongest, because the others are citations and this one is the file's whole reason.

**THE REPAIR IS A SENTENCE AND ITS COST IS A REPLAY.** New 9 is tagged and paged, so the fix
goes through `replay-repair.sh` the way 045-10's possessives did: change the middle clause to
say the field is *declared* in the frame contract and not yet sent by anything, and that the
helper is here because this chapter's assertions will need it the moment it is. Left open rather
than executed inside new 22, because a chapter's own port must not quietly rewrite a tagged
predecessor — and recorded now, while the measurement is in hand.

**AND IT SHARPENS 045-2's CLASS.** A forward reference in prose is a citation somebody can
follow late. A forward reference in a *rationale* is different: it makes the code look
already-justified, so nobody asks the question the helper's own arrival should have raised —
**what does this strip today?**

## 045-21 · THE LEDGER SAID "BOTH" AND ONE OF THE TWO CHAPTERS DID NOT COLLECT

`deferred.md`'s split table for the interleaved rate-limit/mail range marks one commit
`31e9cce` as **"BOTH — see below"**, and the row below it names only the halves new 22 owes:

| original commit | artefact | belongs to |
|---|---|---|
| `31e9cce` (part) | the `credentials.itest.ts` and `signup.itest.ts` halves | new 22 (limits) |

**THE THIRD HALF HAS NO ROW, AND NEW 21 SHIPPED WITHOUT IT.** `31e9cce` also rewrites
`services/api/src/notifications/notifications.itest.ts` — 42 lines, adding an `undelivered(endpointId)`
helper and replacing `expect(await broken.drainOnce()).toBe(0)` with a question asked of ONE
row. Measured in the tree at new 22: the helper is absent and `notifications.itest.ts:259` still
reads `expect(await broken.drainOnce()).toBe(0)`.

**AND THE MISSING HALF IS THE ONE THIS PROJECT HAS PAID FOR REPEATEDLY.** `drainDisableNotifications`
is global, the integration lane runs files in parallel, and the assertion counts the batch rather
than the row — which is `CLAUDE.md`'s *"AN ASSERTION SCOPED WIDER THAN THE THING IT TESTS FAILS
FOR SOMEBODY ELSE'S REASON"*, the fault four suites carried at 043 and the reason published wrote
this hunk at all. Its own comment says so: *"which this file walked into on its first full-lane
run."*

**WHY "BOTH" WAS ENOUGH TO LOSE IT.** Every other row in that ledger names a file. This one named
a decision — that the commit divides — and left the second side to whoever read the table. The
chapter porting the FIRST side reads the row addressed to it, finds its two files, and has no
reason to look for a third; the chapter that owed the third side had already gone. **A ledger row
addressed to one chapter cannot record an obligation of another one.** Split rows need one row
per destination, both written when the split is found.

**NOT CARRIED INTO NEW 22, DELIBERATELY.** The hunk lands in a suite whose subject is the mail
transport, and carrying it here would put a mail-chapter diff on the limits chapter's page — the
exact thing this ledger exists to prevent. The repair is a `replay-repair.sh` pass over new 21,
the way 045-10's possessives were repaired, and it is filed rather than executed inside another
chapter's port. **The risk while it is open is a flake attributed to the wrong chapter**: new 22's
battery runs this suite, and if the lane leaves a claimable row the failure will read as new 22's.
Recorded here so it does not.

**AND IT IS NOT THE ONLY ONE THE MAIL CHAPTER LEFT.** The same interleaved range holds four
cleanup commits, and new 21 collected none of them:

    31e9cce (part)   notifications.itest.ts — ask ONE row, not the batch count
    b060056          notifications.itest.ts — the suite must not run a global sweep
    14816fa (part)   the mail files' feature-local ids: mailer.ts, mailer.test.ts,
                     notification-relay.ts, notifications.itest.ts, and two lines of
                     repository.ts
    14816fa (part)   `packages/config/src/infra.ts` — the Mailpit line's `FR-021`
    1144655          n/a — a prettier revert this tree never needed

Measured in the worktree at new 22: `notifications.itest.ts:259` still counts the batch, no
`undelivered()` helper exists, and `mailer.ts:1` still reads `(FR-021, FR-WHK-07)`. **Three of
the four are the SAME shape of miss** — a feature commit was collected and the range's tidy-up
commits were not — which makes this a rule rather than an accident: **the last commits of an
interleaved range are the ones a split loses**, because the chapter that owns the feature has
already stopped reading by the time they appear.

## 045-22 · A MECHANICAL ID SWEEP PRINTED ONE ID TWICE, AND CITED A WEBHOOK CLAUSE FOR A RATE LIMIT

`14816fa` ("cite identifiers that resolve, not feature-local ones") replaced fifty-nine
feature-local `FR-0xx` citations with SRS, SAD and ADR ids. Most of them are right. Eight are
not, and published's HEAD still carries them:

    services/api/src/db/schema.ts:148     (FR-RTL-04, FR-RTL-04)
    services/api/src/limits/policy.ts:19  (FR-RTL-04, FR-RTL-04)
    services/api/migrations/0008…sql:1    (FR-RTL-04, FR-RTL-04)
    gateway/src/limits.itest.ts:433       "the gateway's internal call … is exempt (FR-WHK-05)"
    gateway/src/limits.itest.ts:530       a test TITLE ending "(FR-WHK-05)"
    api/src/limits/limits.itest.ts:268    "the failure FR-WHK-05 forbids"
    api/src/limits/limits.itest.ts:294    "the half constitution I needed"
    api/src/limits/rate-limit.middleware  "Account creation (FR-AUT-12)"

**THE TWO FAILURE SHAPES ARE DIFFERENT AND BOTH COME FROM THE SAME MECHANISM.** A substitution
table maps many-to-one, so **a range collapses**: `(FR-018 to FR-020)` becomes
`(FR-WHK-07 to FR-WHK-07)` and `(FR-RTL-04, FR-007)` becomes `(FR-RTL-04, FR-RTL-04)` — a
citation that has lost its second half while looking complete. And where no real id fits, the
table supplies **the nearest one it has**: FR-WHK-05 is *"webhook delivery shall be asynchronous
and shall never delay or block message delivery"*, cited here for the gateway's internal routes
being exempt from the tenant rate limit. Those are unrelated clauses, and one of the two
citations is in a test title — the part read detached from its file, where nobody has the source
to notice.

`FR-AUT-12` is *"failed authentication attempts shall be rate limited per source IP"*, and the
signup limiter is not an authentication at all. Same key shape, same threshold, no clause of its
own — which is worth saying rather than papering over with the neighbouring id.

**AND `constitution I` LANDED IN THE MIDDLE OF A SENTENCE.** *"FR-RTL-04's configurability, and
the half constitution I needed"* — the replaced token was `SC-003`, a success criterion, and the
substitution was made without reading the clause it sat in. **An id inside a sentence has a
grammatical role**, and a table cannot see it.

All eight are corrected in this tree rather than copied, with the reason recorded at two of them.

**THE GENERAL RULE.** A sweep that replaces identifiers needs the same treatment as a checker: a
positive control (does the new id resolve?) and a **collision check** (did two distinct ids
become one?). The second is the one nobody runs, and it is the one that silently deletes a
citation.

## 045-23 · THIRTY-FIVE OF ONE HUNDRED AND THIRTY-SEVEN CITED IDS RESOLVE NOWHERE, AFTER THE SWEEP THAT WAS ABOUT THAT

Measured over the seventeen source files new 22 touched, after `14816fa`'s sweep was ported:

    ids cited (FR/EIR/NFR/DR/CON/SC/ADR)                137
    resolving nowhere in docs/ (word-boundary grep)       35

    FR-002a FR-002b FR-002d FR-003 FR-003a FR-004 FR-004a FR-004b FR-005 FR-005c
    FR-007a FR-010 FR-011a FR-011b FR-013a FR-015 FR-017a FR-019a FR-019b FR-020a
    FR-021a FR-026 FR-027 FR-028 FR-029 FR-030 FR-031 FR-032
    SC-001 SC-002 SC-003 SC-003a SC-005 SC-008 SC-013

**TWO CONTROLS, BOTH BEHAVING.** A fabricated `FR-ZZZ-99` is reported missing; `FR-RTL-01` is
reported found. Without both, a `0` and a `35` are equally meaningless — the lesson `CLAUDE.md`
records under *"give every pattern a positive control"*.

**THESE ARE FEATURE-LOCAL IDS FROM EACH CHAPTER'S OWN SPEC**, and they resolve nowhere a reader
of the published tutorial can follow: the spec directories are not published. `14816fa` fixed the
subset its author's grep found in the files that chapter touched. The rest are spread over
chapters that had already shipped, which is why a sweep run inside one chapter cannot close this
— **the leak is tree-wide and the fix was chapter-local.**

Not fixed here, for the reason 045-20 gives: rewriting citations in files fenced byte-exact into
already-tagged chapters is a `replay-repair.sh` pass, not a line in another chapter's port. Filed
with the measurement so the pass has a target list and a way to check itself.

## 045-24 · A FIELD ARRIVED AFTER THE SUITES THAT COMPARE WHOLE BODIES, AND THE FILE HAD WRITTEN DOWN WHAT TO DO

`deferred.md` records one **inverted** deferral — a lint rule that arrives after the files it
must exempt — and calls it *"the shape that goes wrong silently."* This is the same shape with a
data field instead of a rule, it was not in the ledger, and it is louder: twenty-three tests in
two files, all at once.

    Test Files  2 failed | 21 passed (23)
    Tests      23 failed | 489 passed (512)

Every failure the same:

    AssertionError: expected { code: 'not_found', …(3) } to deeply equal { code: 'not_found', …(3) }
    -   "request_id": "6bca7578-0461-4274-804a-22a71f0c195d"
    +   "request_id": "6d5517e3-baf6-48ad-a935-4a535ce80d68"

**THE MECHANISM.** Constitution I's oracle is a PAIR: a foreign identifier must answer exactly
as an identifier that exists nowhere, so the gauntlet compares status and **whole body**. Add a
field that is unique per request and every pair differs — twenty-two attacks in
`isolation/attack.ts`'s `comparePair`, plus `channels.itest.ts`'s membership case. In the
published order those suites came AFTER the limiter and were written knowing; here the isolation
harness is new 4, the channel surface new 8, and the limiter is new 22.

**WHAT MADE IT A ONE-LINE FIX INSTEAD OF A DEBUGGING SESSION**, and it is the finding worth
keeping. `attack.ts`'s own docblock said:

> *"So status and whole body are compared. There is nothing to exclude from the comparison yet:
> the error envelope is `code`, `message` and `docs_url`, all three of which must match. **When a
> per-request field joins it, the chapter that adds it owns the decision to drop it here** — and
> it will have to argue that the field reveals nothing about the resource."*

`channels.itest.ts:205` carried the same sentence in miniature: *"Nothing here is per-request
yet, so nothing is excluded."* **Both notes are in the exact place a reader lands from the
failure**, they name the chapter that owns the decision, and they state the argument that
decision has to make. The argument, made: `request_id` is the only field in the envelope not
derived from the resource — `code`, `message` and `docs_url` answer what was asked for, the id
answers the asking — so dropping it removes no leak.

**THIS IS THE COUNTEREXAMPLE TO 045-20 AND THE PAIR IS THE LESSON.** There, `compare.ts`'s
docblock explained itself by an event thirteen chapters ahead, and the reader could not check
it. Here, a comment states what is true TODAY, names the condition that will change it, and
says who decides — and it cost one line to act on. **A forward-looking comment works when it
records the trigger and the owner, and fails when it records the outcome.**

**AND THE LEDGER COULD NOT HAVE FOUND THIS BY ITS OWN METHOD.** Every `deferred.md` row comes
from a cherry-pick that would not apply. Nothing failed to apply here: the field's commit
touched six files and none of them was `attack.ts`. What found it was **running the battery** —
which is why the per-chapter loop runs one, and why a chapter is not finished when its commits
are green.

## 045-25 · THE CHECK AGAINST AN UNINJECTED MODULE COULD NOT SEE A MODULE BUILT WITHOUT OPTIONS — CLOSED

`services/gateway/src/main.test.ts` holds one of this project's better instruments. Its comment
states the defect it exists for: *"A MODULE BUILT, CLOSED, AND NEVER PASSED IN IS INERT AND
GREEN … That happened to `typing` in the order this book was first written and was found by the
sealed client, which is eleven chapters away."* It reads `main.ts` as text, derives the fabrics
rather than listing them, and asserts each one appears in the `attachSessions` call.

**IT DERIVED FIVE OF SIX.** The pattern was

    /\bconst (\w+) = create[A-Z]\w*\(\{/g

— a call with an OBJECT ARGUMENT. `createGatewayLimits()` takes none: it reads its url from the
environment. Measured on the tree at new 22:

    old pattern   fanout presence membership typing connections
    widened       fanout presence membership typing connections limits

So the ninth Redis client in that file was outside the check, and outside it **in the direction
that passes** — the same asymmetry 044 found in the driver-exemption linter and closed there.
A `limits` line deleted from the call left the suite green; the limiter would have been inert,
every socket unlimited, and `**/main.ts` is excluded from coverage so no figure could show it.

**AND THE POSITIVE CONTROL WAS SATISFIED BY THE HOLE.** The control asserted
`built().length > 1` — five names pass that as easily as six. It is now an assertion on the
list by name, which goes red when a fabric is added without a thought about this file. **"More
than one" is a control against a parse that found NOTHING; it is not a control against a parse
that found MOST.**

**THE FIX HAD A TRAP OF ITS OWN AND THAT IS WHY IT IS RECORDED.** Dropping the `{` widens the
match to `createLogger` and `createServer` in the `import.meta.main` block below the
function — neither is a fabric. Both happen to satisfy the injection test (`logger: log,` and
`server,` both match), so the widened check would have passed for the wrong reason. It is
scoped to the text between `export function createServer` and the `attachSessions({` call
instead, which is what the describe's title always claimed. **An exclusion list would have been
the thing this file exists instead of.**

Falsified: with `limits,` removed from the call, `built by createServer and never injected:
limits`. Closed in new 22.

## 045-26 · THE UNIT GATE NEEDS A LIVE REDIS, AND ITS FAILURE READS AS A DEFECT

Measured while re-verifying new 22 after the lane had gone down: `pnpm run test` — the cheap
gate, the one that runs before every commit in this rework's loop — came back with twelve
failures.

    AssertionError: expected { kind: 'unenforced' } to deeply equal
                    { kind: 'claimed', slot: +0, held: +0 }

**NOTHING WAS WRONG WITH THE TREE.** `relay-redis-1` was not running, and `unenforced` is the
connection registry's fail-open arm — the correct answer to "the store is gone". The suite is
`services/gateway/src/connections.test.ts`, named `.test.ts`, so it runs in the UNIT lane; with
Redis down it contributes 12 of its 17 tests as failures, and every message is about slots and
claims rather than about a connection refused. Measured directly through vitest, bypassing
turbo: `src/connections.test.ts (17 tests | 12 failed)`, every other unit suite green.

Eight `.test.ts` files reach for a store or a client at all — the two api publishers, five
gateway modules and `main.test.ts` — and seven of them get away with it because they only
construct or read source. One actually issues commands.

**AND THE CACHE MAKES IT WORSE IN THE OTHER DIRECTION.** `test` is a cacheable turbo task, so
after a green run the same command reports

    Tasks: 11 successful, 11 total   Cached: 11 cached, 11 total   Time: 10ms >>> FULL TURBO

with no store running at all. So the unit gate can say green with the lane down and red with the
lane down, from the same tree, depending only on whether the cache was warm. **A gate whose
answer depends on a cache and a container is not a gate about the code**, and neither reading
names the reason.

**WHAT IS ACTUALLY FILED HERE IS A NAMING DEFECT.** The tree's convention is
`.itest.ts` for a suite that needs the lane, and it is what the integration config globs. This
suite needs the lane and does not say so, so nothing routes it correctly and no one running the
cheap gate is told what the failure means. Two fixes, and they are not equivalent: rename it
`connections.itest.ts` (which moves 17 tests into a 6-minute lane), or keep it in the unit lane
behind a store probe that skips with a stated reason. **The second is worse than it sounds** —
this project has already recorded that *"a security test that skips itself is worse than no
test"* — so the rename is the honest one, and it should be measured before it is made: five of
the seventeen do not need Redis at all and belong where they are.

Not fixed in new 22: the file is the connection-cap chapter's, it is fenced into that chapter's
page, and the change is a rename plus a split — a `replay-repair.sh` pass, not a line in another
chapter's port.

## 045-27 · THE GUARD'S THREE PARTS WENT TOGETHER AND ONLY TWO WERE CHECKED — AND THE FIRST FIX WAS VACUOUS — CLOSED

`packages/test-harness/src/sentinel.sql` names the tables the global-operation guard watches,
and its comment states the discipline plainly:

> *"A name added here without bait planted in `sentinel.ts` installs a trigger that can never
> match, and it reads exactly like protection. That is why the three go together: the name, the
> bait, and the case that turns red when the name is removed."*

**TWO OF THE THREE WERE CHECKED AGAINST EACH OTHER AND THE BAIT AGAINST NOTHING.**
`guard.itest.ts` compares the array to its own `SHAPES` in both directions, and to `pg_trigger`
in both directions. Measured while adding the quota chapter's three tables: deleting the
`usage_periods` insert from `plant()` left the suite at **32 of 32 green**, and deleting
`read_positions`' — an older chapter's — did too.

**WHAT THAT COSTS IS NOT THAT SUITE.** Every case in it plants its own row through `SHAPES`, so
it is unaffected. `plant()` is what `setup.ts` runs **once per test FILE**, and the row it leaves
is what makes an unscoped `DELETE FROM usage_periods` in somebody else's suite meet a trigger at
all. A name added with a shape and no bait leaves that table with no canary in any lane run.

**AND THE FIRST FIX WAS VACUOUS, WHICH IS THE PART WORTH KEEPING.** The new assertion counted
rows for `VICTIM.environmentId` — and `beforeAll` plants the victim's rows through `SHAPES`, so
every count was nonzero for a reason unrelated to `plant()`. It passed with the insert deleted,
twice. `CLAUDE.md` records this exact shape from 044 — *"a test written by the audit that finds
vacuous tests was vacuous"* — and the question that finds it is the same one: **what would have
to be false for this to fail?** Here: nothing, because two different mechanisms could satisfy it
and only one was the subject.

Fixed by planting a THIRD sentinel that only `plant()` ever touches and counting against its
environment. Falsified three ways, each naming the right table:

    guarded, and plant() leaves no row to guard: usage_periods
    guarded, and plant() leaves no row to guard: read_positions
    guarded, and plant() leaves no row to guard: quota_notifications

**AND IT IS ASKED OF THE DATABASE, NOT OF THE SOURCE.** A scan of `sentinel.ts` would pass on an
insert that runs and inserts nothing — an `ON CONFLICT DO NOTHING` against a row the fixture does
not own — which is the shape a fixture fails in. Closed in new 23.

## 045-28 · "THE FIVE TEST LANES", AND FOUR OF THEM WERE WIRED — CLOSED

Published's harness half carries a commit named `02993b1 feat: wire the guard into the five test
lanes`. That half went to new 8. Measured at new 23, before this chapter touched anything:

    services/api/vitest.integration.config.mts             globalSetup ✓  setupFiles ✓
    services/gateway/vitest.integration.config.mts         globalSetup ✓  setupFiles ✓
    packages/e2e/vitest.integration.config.mts             globalSetup ✓  setupFiles ✓
    packages/test-harness/vitest.integration.config.mts    globalSetup ✓  setupFiles ✓
    services/dispatcher/vitest.integration.config.mts      —              —

**AND NOTHING COULD SAY SO**, which is the property worth naming. An unwired lane does not fail;
it simply never installs the guard, never plants a sentinel, and never refuses anything. The
missing lane is invisible in exactly the direction that passes — the third instance of that
asymmetry in this feature after the driver-exemption list (045-17) and the derived fabric check
(045-25).

**A SIXTH SURFACE WAS UNWIRED TOO, AND IT IS THE ONE THIS REWORK RUNS MOST.**
`vitest.coverage.config.mts` had `setupFiles` and no `env`, so the coverage battery — 1,183
tests, run once per chapter — booted every relay, each defaulting to on when its flag is unset.
Published set the flags there at old 3.10 and this port takes that change; before it, every
per-chapter coverage run swept the whole database with four background loops while every other
suite's fixtures sat in it.

Both are fixed here rather than filed, because the quota relay is the FOURTH such loop and this
chapter is what starts it — leaving the flags unset would have been shipping the problem the
flags exist for. The new-8 wiring is carried with it: splitting one `test: {}` block across two
chapters would have been an artefact of the ledger rather than of the code.

**WHAT THE LEDGER COULD NOT HAVE CAUGHT.** No cherry-pick failed. `02993b1` is a harness commit
and went to new 8 whole; new 8 applied it and the dispatcher's hunk is simply not in the tree,
which means the commit was ported partially and reported as ported. **A commit that touches five
files and lands four is indistinguishable, afterwards, from a commit that touches four** — unless
somebody counts, and the only reason anybody counted here is that this chapter needed to add a
fifth flag to the same block.

## 045-29 · THE FOURTH MEASUREMENT OF ONE LAW, AND THE FIRST WITH TEETH

`sentinel.ts` records a rule the project has now paid for four times:

> *"bait may be claimable only where draining it is DATABASE work. The endpoints (a sweep) and
> the outbox rows (a publish to whatever the test hands it) qualify and are left claimable …
> The deliveries and these notifications do I/O per row, so they stay in the table as rows a
> global count would see and out of every claim window."*

`drainQuotaNotifications` claims on `delivered_at IS NULL` and then calls `deliver(row)` — a mail
send. So the quota chapter's bait had to be planted already delivered, like the two before it.

**THE THREE EARLIER INSTANCES COST SECONDS; THIS ONE IS A HARD FAILURE**, because the same
chapter puts `quota_notifications` under the global-operation guard. The relay claims the
sentinel's row on a connection carrying no exemption, the trigger refuses the UPDATE, and the
transaction is poisoned:

    Failed query: UPDATE quota_notifications SET delivered_at = now(), last_error = NULL
    → 25P02 in_failed_sql_transaction on the next statement
    six tests red, and the message names neither the bait nor the guard

**AND `ON CONFLICT DO NOTHING` MADE IT UNFIXABLE FROM SOURCE.** A sentinel's ids are derived from
its owner, so the bait's id is the same on every run for ever. Planting it delivered fixed
nothing on a lane that had already planted it undelivered: the row persisted, the failure
persisted, and the diff looked correct. The insert now uses `DO UPDATE SET delivered_at`, because
**this row's STATE is part of the fixture's contract and not merely its existence** — and a
fixture that only guarantees existence guarantees whatever the first run happened to write.

The lane's own debris was cleaned by hand, which needed the exemption — and the guard refusing
that cleanup, naming the owning test file, is the clearest demonstration of it working that this
feature has produced.

## 045-30 · A TWO-HALF EXEMPTION WHOSE OBVIOUS TEST COVERS ONE HALF, AND THE SECOND CASE FOUND BY FALSIFYING — CLOSED

`deferred.md` deferred old 3.17's `## Billed, and exempt` section to new 23 and said which part
mattered:

> *"The exemption's second half is the part worth carrying: returning early so a bot is not
> refused is visible, and excluding bots from the count the ceiling compares against is the half
> that decides whether it works — with a test that sends as a person after a bot, never as the
> bot itself."*

That instruction is right and it is not sufficient, which is the finding. Written as directed —
bot sends, then a person must still get through — and falsified both ways:

    drop the COUNT's `kind = 'person'` filter   → red: QuotaExceededError, 1 of 1
    drop the `!senderIsPerson` early return     → GREEN

**THE EARLY RETURN IS UNREACHED BY THE TEST WRITTEN TO PROTECT IT.** With the count filtered to
persons, a bot sending first sees zero of one and passes the ceiling check on its way through, so
the return it would have taken is never needed. The early return only bites once the PERSONS have
filled the ceiling — which is the state a customer meets on the day their team grows, and the one
where refusing their own software is worst.

A second case covers it: cap of one, a person sends, then a bot must still send. Falsified: with
the early return deleted, `QuotaExceededError: active_users quota exhausted: 1 of 1`.

**THE GENERAL SHAPE.** Two mechanisms that implement one rule can each be sufficient for the
obvious case, and a single test then pins whichever runs first. The ledger's warning caught the
half that is easy to forget; only running the probe caught the half that is easy to *cover by
accident*. **"Which half does this test fail without?" has to be asked once per half**, and the
answer is not derivable from the requirement — both halves cite the same clause.

Closed in new 23, with both cases and both falsifications recorded at the code.



## 045-31 · A DESTRUCTIVE STEP RAN FOR THREE SESSIONS WITH ITS QUESTION UNANSWERED — AND THE ANSWER WAS "KEEP RUNNING IT"

The per-chapter loop ends with `vi-placeholder.py`, which replaces a chapter's Vietnamese page
with a three-line notice. Applied to new 17 through new 22 it overwrote 1.2 MB of Vietnamese
prose, and this session's records show the question being put three times and never blocked on:
*should the placeholder step keep running when real prose exists?*

**BOTH ANSWERS I GUESSED WERE WRONG, AND IN OPPOSITE DIRECTIONS.** Running the step for six
chapters assumed the prose was disposable. Then, told *"I'm doing the translation to Vietnamese
for the first chapters, so do not clean up my work"*, I restored all six — assuming the prose was
the author's. It was neither: **chapters 1 to 9 are the author's translations and chapters 10
onward are machine edits**, so the six I restored were exactly the ones that should have stayed
placeholders, and the nine I never touched were the ones at risk.

The restore was reverted; chapters 17 to 22 hold placeholders again and chapters 1 to 9 have
never been touched by this loop.

**THE FINDING IS NOT ABOUT VIETNAMESE.** A step that overwrites human-authored content ran for
three sessions on an instruction given before the content existed, and when the instruction was
finally clarified my correction was wrong too — because I inferred the boundary rather than
asking where it was. The question I asked three times was *"should I keep doing this?"*. The
question that would have settled it in one exchange is **"which files are yours?"** — a question
whose answer is a list rather than a judgement.

**WHAT WOULD HAVE CAUGHT IT.** Not a gate: no instrument in either repository knows who wrote a
paragraph. What was available and unused is the target itself — `vi-placeholder.py` never reads
what it is about to replace, and its own docstring frames the choice as "placeholder or delete
the page", which hides the third state that was already on disk. A destructive step should print
what it is overwriting, and a loop should not contain one whose premise is unverified.

**THE RULE.** A step that overwrites human-authored content is not a step in a loop. It needs the
same treatment this project gives a migration or a lane reset: look at the target first, and stop
if what is there is not what the step assumes — and when the boundary is somebody else's to draw,
ask for the list, not for permission.

## 045-32 · THE RE-PIN PROBE THIS PROJECT REQUIRES CANNOT RUN ON ONE FILE, AND IT FAILS SILENT

`CLAUDE.md` records a rule from 044 and asks for it on every re-pin:

> *"A PER-FILE COVERAGE THRESHOLD WHOSE KEY MATCHES NO FILE IS SILENT. Demanding 101% of
> `this-file-does-not-exist.ts` produced no error, no warning, nothing. Demanding 101% of a real
> file names the key. **Run both halves of that probe every time the ratchet is re-pinned.**"*

Run against a single test file, as anyone would to keep it cheap, **both halves are silent and
for two different reasons**. Measured while pinning the quota chapter's six files:

    npx vitest run --config vitest.coverage.config.mts <one>.test.ts
      → exit 0. No coverage table, no "Coverage enabled" line: without `--coverage`
        the thresholds are not evaluated at all, so a 101% key on a REAL file passes.

    npx vitest run --config vitest.coverage.config.mts --coverage <one>.test.ts
      → exit 1, and the message is
        `ERROR: Coverage for lines (0.28%) does not meet global threshold (70%)`
        The global floor fires first and the per-file key is never reported.

So the cheap form of the probe reports "nothing happened" in exactly the case it exists to
distinguish from "nothing happened", and the form that does fire reports the wrong thing. **A
probe whose negative result is indistinguishable from a broken probe is the defect it was written
to find**, one level up — the same shape as 043's grep that matched nothing under one engine.

**THE PROBE IS ONLY VALID IN THE FULL RUN**, where the global floor is met and the per-file keys
are the only thing left to fail. That costs six minutes, which is why nobody would reach for it
by hand, which is why the cheap form is the one that gets run.

Not closed. Two shapes would fix it and both are work: run the probe as part of the close-out
battery rather than by hand, or give the config a mode where the global floor is relaxed so a
single-file run can exercise one key. Recorded here with the measurements so the next re-pin does
not spend the same twenty minutes discovering it, and the config now says which half of the
ritual each pin was validated by.

## 045-33 · THE FENCE GENERATOR ATE EVERY REMOVED SQL COMMENT, AND THE CHECKER CAUGHT IT THE SAME DAY — CLOSED

`regen-fences.py` strips `git diff`'s header before storing a fence body, and it did so by prefix:

    if not l.startswith(("diff --git", "index ", "--- ", "+++ ", "new file mode"))

`--- ` is the header's old-file line. It is also **a removed SQL comment**: `-- a trigger that
can never match` is emitted by `git diff` as `--- a trigger that can never match` — one `-` for
the removal, two for the comment. So every such line was deleted from the fence.

The result is a fence carrying the ADDITIONS of a rewritten comment block and none of the
REMOVALS. Measured on new 23's `sentinel.sql`: git's diff has 2 hunks and 4 removals; the
generated fence had 1 hunk and 1 removal, and the three lost lines were exactly the three
comment lines the chapter replaced.

**THE CHECKER CAUGHT IT IMMEDIATELY AND SAID SOMETHING TRUE BUT UNHELPFUL:**

    packages/test-harness/src/sentinel.sql: hunk pre-image matched 0 times (need 1)
      — starts '  -- so a table with no `id` raises `record "old" has no fie'

Every individual line of the pre-image was present in the base file; only the SEQUENCE was wrong,
which is why the message names a line that is not the problem. Finding it took aligning the
pre-image against the base line by line and reading the first divergence — the fence had context
where the base had text.

**BOUNDED, AND THE BOUND IS THE INTERESTING PART.** Two chapters fence a `.sql` file as a diff
rather than whole: new 10 and new 23. New 10 removes no comment line, so it is undamaged and
`check-chapter` confirms it at 0 problems. **New 23 is the first chapter in this rework to delete
a line of SQL commentary**, which is why a bug that has been in the generator since it was written
surfaced now.

Fixed by stripping the header **by position** rather than by prefix — everything before the first
`@@` is header and nothing after it is, and `git diff` always emits hunks last. That is exact
where a prefix match is a guess, and it needs no list of the languages whose comments collide with
diff syntax (SQL, Lua, Haskell, Ada all use `--`).

**AND IT IS THE FILE'S OWN WARNING COMING TRUE.** `regen-fences.py`'s header says a generator that
replays differently from the checker "produces hunks the checker rejects for reasons neither of
them explains". This is that, from the one direction nobody looked: not the widening, but the
line filter that runs after it.

## 045-34 · A PROSPECTIVE RULE WHOSE ARRIVAL WOULD SWITCH OFF THE ONE ALREADY THERE — MEASURED, THEN CLOSED IN NEW 25

New 24's phase-7 port (`f605840`) adds `drainQuotaNotifications` to a `no-restricted-imports`
rule **this tree does not have**. The cherry-pick therefore offered the whole feature-030 block
instead of a three-line addition, and the block is the one every `ioredis` note in
`eslint.config.mjs` has warned about twice without ever meeting.

**REPRODUCED RATHER THAN ASSERTED.** `services/api/src/channels/channels.itest.ts` is on no
exemption list. With `import { sql } from "drizzle-orm";` prepended:

    control (this tree's config)         eslint exit 1, `no-restricted-imports` fires
    published's block appended verbatim  eslint exit 1, and the ONLY error left is
                                         `'sql' is defined but never used`

The driver-and-engine ban is gone for **all 33 non-exempt `.itest.ts` files** in the workspace,
silently, because in flat config a later block REPLACES a rule rather than merging it. The
hazard is R23/FR-043 and the file's own header states it.

**AND THE BLOCK RESTRICTS NOTHING HERE TODAY.** Exactly six `.itest.ts` files import a drain
function — `outbox`, `deliveries`, `test-event`, `attempts`, `notifications`, `dispatcher` — and
those six are precisely published's exemption list. Published's own comment says as much: *"It
protects a future DIRECT importer."*

**THE DECIDING MEASUREMENT IS THE SIBLING LIST.** `packages/test-harness/src/exempt.ts` names
**one** file, and its comment says the two lists "must agree. A file exempt from one and not the
other is a trap for whoever adds the next one." A six-entry block would make the tree's own
comment false on arrival. So the hunk is **not taken**, and the port says so in its message
rather than leaving a reader to wonder which side won.

**WHAT THE CHAPTER THAT DOES TAKE IT HAS TO DO**, since published's final tree solved this and
its Part-3 commits do not: four blocks, not two. Hoist `DRIVER_AND_ENGINE`, `DRIVER_EXEMPT_TESTS`,
`DRAIN_EXEMPT_TESTS` and `GLOBAL_DRAINS`; the `**/*.itest.ts` block composes the **union**
(`paths: [...DRIVER_AND_ENGINE.paths, ...GLOBAL_DRAINS.paths]`) and ignores both lists; two
trailing blocks give each list back its own single rule.

**AND ONE TEST BREAKS ON THE HOISTING, WHICH IS THE PART A PLAN WOULD MISS.**
`driver-exempt.test.ts` parses the rule with

    /"no-restricted-imports":[\s\S]*?paths:\s*\[([\s\S]*?)\],\s*patterns:/

With the consts hoisted, the first `"no-restricted-imports"` is followed by
`["error", DRIVER_AND_ENGINE]` and the regex then captures
`...DRIVER_AND_ENGINE.paths, ...GLOBAL_DRAINS.paths` — no `name:` in it, so `restricted()`
returns `[]` and every check reading it goes vacuous. Its own first assertion catches that, which
is the only reason this is a nuisance rather than a silent hole. Published's tree parses
`const DRIVER_AND_ENGINE = {` … `\n};` by position instead; that is the change this test needs
in the same commit.

## 045-35 · THE DERIVED TARGET LIST NAMED A ROUTE THE CHAPTER FORGOT, AND ITS HAND-KEPT SIBLING HAS FIVE HOLES — CLOSED

New 24 adds `POST /internal/usage/connections` and classified it nowhere, so three tests in
`services/api/src/isolation/targets.itest.ts` went red in a file the chapter was not editing:

    classifies every derived target exactly once   unclassified: ["POST /internal/usage/connections"]
    accounts for every derived target …            expected 41 to be 42
    leaves nothing exempt by omission (FR-033a)    CLASSIFICATIONS.length !== derived.length

**THIS IS THE DERIVATION PAYING FOR ITSELF, for the sixth recorded time.** The list is read off
the running router rather than typed, so a route nobody classified cannot hide — and the failure
names the route rather than printing two integers.

Classified `write`, for `expand`'s reason: it names an environment ALONGSIDE a connection id, so
a caller can claim one tenant's connection for another's bill. The attack is in
`gauntlet.itest.ts` and asserts both directions — the attacker gained nothing, and the victim did
not LOSE the minutes it had, which a refusal that moved the row and then failed would still
satisfy.

**AND THE ONE-DIRECTIONAL LIST BESIDE IT IS FIVE ENTRIES SHORT.** `targets.itest.ts`'s `ADDED`
list — "each chapter that adds a route adds its key here" — holds only `/v1/…` routes. The four
`/internal/dispatch/*` routes and `/internal/memberships` are on the router and not on it. That
direction catches *a route classified and never built*, so the holes cost nothing today and the
list is weaker than it reads. This chapter added its own key and filed the rest rather than
sweeping them.

## 045-36 · A BATTERY RUN WITHOUT THE PINNED LANE READS AS TWENTY-TWO DEFECTS, AND ONE OF THEM WAS REAL

New 24's first integration battery: **22 failed / 583 passed across 29 files, 16m33s**. It was run
with `RELAY_POSTGRES_PORT=15432` and nothing else, and `baseline.txt` pins **nine** variables.

    18 failures   `inbox` in notifications (7), connections (6) and quotas (5) —
                  Mailpit defaults to `http://localhost:8025`; the lane runs 18025
     1 failure    "the lane must configure a platform credential: expected undefined
                  to be truthy" — `RELAY_INTERNAL_CREDENTIAL` unset, in a message
                  that names its own cause
     3 failures   REAL, and 045-35 is them

**THE SUITE SAID SO IN ITS OWN HEADER.** `notifications.itest.ts` carries the full command —
`RELAY_MAILPIT_HTTP_PORT=… RELAY_SMTP_URL=… RELAY_MAILPIT_URL=…` — twelve lines above the
`?? "http://localhost:8025"` it falls back to. The instrument was documented and the run was
not read against the document.

**AND THE DURATION IS NOT A MEASUREMENT.** 16m33s red against **6m39s green** on the same tree
twenty minutes later — 45 files, 882 tests, exit 0, nine variables set. A battery with 22
failures spends its time on retries, teardown and mail polling that never arrives. **A red
battery has no timing.** Record the environment beside the duration or neither number means
anything.

    new 22   37 files   759 tests   6m10s
    new 23   40 files   802 tests   6m22s
    new 24   45 files   882 tests   6m39s

Three chapters that can be compared, which is what 043's port fix bought and what this run
would have thrown away.

## 045-37 · TWO LEDGER ROWS WERE ALREADY PAID, ONE OF THEM BETTER THAN PUBLISHED, AND A THIRD NAMED THE WRONG THING

`acf0695` — "invariant 1 took the api key secret as `split("_").at(-1)`" — is **entirely carried**.
The tree already fixed it, and differently: it slices by `minted.prefix.length`, where published's
version restates the credential's shape in the test as
`/^rk_(?:dev|live)_[0-9a-f]{32}_(.+)$/`. A second copy of a production rule is a second rule;
the prefix is returned by the minting call and cannot disagree with the row. Cherry-picked to a
zero-byte diff, and dropped.

`3412851`'s row read **"the usage suite's typing case"**. There is no typing case in
`services/api/src/internal/usage.itest.ts` and never was: what that commit did to the file was
replace a hard-coded `AUGUST` with `periodOf(new Date())`, already ported in this chapter's cap
phase. **The row named the chapter the change was FOUND in, not the change** — the same shape as
044's four artifacts agreeing on two clauses that do not exist.

**AND PUBLISHED'S OWN ID SWEEP LEFT A COMMA.** `d7e5354` rewrites
`session.perf.itest.ts`'s header from `(chapter 3.11, SC-012, FR-025)` to
`(chapter 3.11, , NFR-PERF-01)`. The sweep was right — the id it removed is gone from the test
title below too — and its edit was not. A mechanical rewrite that leaves punctuation behind is
invisible to every gate in both repositories, which is 045-22 in a third shape.

## 045-38 · A SUITE THAT FAILS HALF THE TIME, AND ITS OWN COMMENT PRESCRIBES A MITIGATION THAT CANNOT WORK

New 24's coverage battery came back **1 failed / 1404 passed, 95 files, 400.78s** — one test in
`services/gateway/src/typing.itest.ts`:

    Error: only 0 of 1 typing frames for dc16e82c-…; saw connection.ack

**FORCED RATHER THAN WAVED AWAY**, which took two minutes against a battery that would have shown
it once in six. Four runs of that one suite at HEAD and four at `rework/part3-ch23`:

    HEAD   pass, FAIL, pass, FAIL      2 of 4
    ch23   pass, FAIL, pass, FAIL      2 of 4   ← so this chapter did not introduce it

Three distinct tests have failed across the eight runs — "sends nothing at all after the signal",
"sends the signaller nothing while another member receives", and "keeps four kinds apart over one
channel" (that one on `presence`, not on typing at all). **One cause, three symptoms**, which is
why each one alone reads as its own flake.

**THE FILE ALREADY NAMES THE CAUSE, IN A COMMENT WRITTEN WHEN IT WAS FOUND:**

> *"A connection is acked before its Redis SUBSCRIBE has necessarily landed: the non-resume
> branch of `open()` acks without awaiting `subscribing`. So a test that acks a watcher and
> immediately signals can miss the frame, and a fixed `settle()` after the signal only makes that
> unlikely rather than impossible."*

**AND THE MITIGATION IT THEN CHOSE CANNOT FIX THAT.** It replaced the sleep with
`untilTyping`, a 4-second poll for the frame — *"POLL FOR AN ARRIVAL, NEVER SLEEP FOR ONE"*.
A publish that reaches Redis before the SUBSCRIBE lands is **discarded by Redis**: there is no
frame to arrive, so polling for four seconds is a slower way to fail. The comment diagnosed a
lost message and prescribed a longer wait for it.

**THE FIX IS TO WAIT FOR THE SUBSCRIPTION, NOT FOR THE FRAME.** The suite already imports
`Redis` from `ioredis` — it is on `DRIVER_EXEMPT` — and already imports `subjectForTyping`,
`subjectForChannel`, `subjectForChannelMembership`, `subjectForPresence`. `PUBSUB NUMSUB
<subject>` polled after `acked()` and before the send is exact where the current poll is a
guess. The alternative is to make `open()` await `subscribing` before acking, which is a
platform change and a published design decision: an early ack is deliberate.

**NOT FIXED INSIDE NEW 24, AND THE REASON IS THE FENCE CHAIN.** `typing.itest.ts` is the typing
chapter's file and that chapter is tagged. An edit to it inside this chapter's tag makes the
chapter's diff carry a file belonging to a subject twelve chapters back, and the chain would then
want a hunk for it on this chapter's page. This belongs in
`relay-tutorial/fences/post-series.md`, which is the mechanism for a platform change that
publishes no chapter.

**AND UNTIL IT IS FIXED THE COVERAGE GATE NEEDS A STATED POLICY.** New 24's figure below is a
re-run. Record which run a coverage number came from, because "1 failed" in this suite is not
evidence about the tree.

## 045-39 · A DIAGNOSTIC CHECKOUT LEFT THE BUILD AT ANOTHER TAG, AND SEVENTEEN FAILURES FOLLOWED — THE TELL WAS A UNIT TEST

045-38 was measured by checking the worktree out at `rework/part3-ch23`, building, running the
suite four times, and returning to `part3-rework`. **The return did not rebuild.** The next
coverage battery came back **17 failed / 1388 passed across 5 files**, every one of them about
the usage report:

    usage.itest.ts        8   the whole controller suite
    session.itest.ts      3   the cap at the door
    api-client.test.ts    3   reportUsage's credential and body
    meter.itest.ts        2   SIGKILL and SIGTERM
    gauntlet.itest.ts     1   this chapter's own new attack

Read as a chapter, that is a feature that does not work. Read once, it is one mistake.

**THE TELL IS THAT THREE OF THEM ARE IN A `.test.ts`.** A unit test spawns nothing, reads no
database and cannot be affected by the lane, so a unit failure alongside integration failures is
not interference — it is the code under test being different from the code on disk. And the
message says which:

    TypeError: Cannot read properties of undefined (reading 'safeParse')
      ❯ parse services/gateway/src/api-client.ts:156:27

`schema` is `undefined` because `@relay/protocol` is consumed as its BUILT `dist`, and that dist
was chapter 23's — where `internalUsageReportResponseSchema` does not exist yet. Every other
failure is the same fact one layer out: `session.itest.ts`, `meter.itest.ts` and `usage.itest.ts`
spawn `services/api/dist/main.js`, which at that tag serves no
`POST /internal/usage/connections` at all.

**AND TURBO MADE THE WRONG BUILD FREE AND SILENT.** `turbo run build` at ch23 printed
`5 cached, FULL TURBO` in 16ms, and printed exactly the same thing at HEAD afterwards. The cache
is keyed on inputs, so it is *right* both times — which means **nothing in the output
distinguishes "your dist is now at the tag you asked for" from "your dist is already correct"**.
A checkout for measurement has to be followed by a build before anything is believed, and
`FULL TURBO` is not evidence that the build is the one you want; it is evidence that turbo did
not have to work.

**THIS IS CLAUDE.md's OWN RULE IN A THIRD SHAPE.** *"`check:errors` reads the BUILT `dist`.
Build before believing it."* That was written about one gate. It is true of every suite in this
repository that spawns a service or imports a workspace package, which is most of them.

## 045-40 · THE RATCHET FIRED ON THE CHAPTER THAT MOVED THE READING, WHICH IS THE ONE TIME IT IS SUPPOSED TO — CLOSED

New 24's coverage battery: **95 files, 1405 tests, all passing, exit 1.**

    ERROR: Coverage for branches (70%) does not meet
           "services/api/src/quotas/quota-email.ts" threshold (75%)

New 23 pinned that file at 75 and wrote the fraction down: **6/8, the uncovered pair being
`months[Number(m) - 1] ?? m`**. This chapter added a third guard —
`STOPPAGE[facts.dimension] ?? DEFAULT_STOPPAGE`, the sentence that says a connection-minutes cap
refuses connects rather than sends — taking the file to **7/10**. Ten arms, three uncovered, 70%.

**A PIN SET AT THE PREVIOUS READING IS WHAT MADE THAT VISIBLE**, and 044's warning about pins
set at readings is the other half of the same rule: pin at what the requirement is, and then a
chapter that adds an uncovered arm goes red rather than diluting a percentage. An eight-branch
file at 75 leaves room for exactly two arms. The third one was refused.

**AND THE ANSWER WAS NOT 70.** *"A ratchet that teaches people to lower ratchets"* is the failure
mode; the question is whether the arm is reachable. Two of the three are:

    NOUN[facts.dimension] ?? facts.dimension        reachable
    STOPPAGE[facts.dimension] ?? DEFAULT_STOPPAGE   reachable
    months[Number(m) - 1] ?? m                      NOT — a `date` column has no month 13

**A DIMENSION IS A STRING OFF A ROW, NOT A MEMBER OF A UNION.** `quota-relay.ts` reads it out of
`usage_periods`, so a fourth dimension added to the database and not to those two maps arrives at
this function — and what the customer then reads in an email about their own bill is the word
`undefined`. One test reaches both fallbacks and asserts exactly that, in both the subject and
the body. **9/10, pinned at 90** — the file ends this chapter better covered than it started it.

**AND THE NOTE BESIDE THE PIN POINTED AT THE WRONG LINE.** It cited `quota-email.ts:31` for a
guard that now sits at 51: the file grew by twenty lines and the comment did not. A line number
in a comment is the same class of artefact as a task id in a test title — read detached from the
thing it names, and wrong in silence.

## 045-41 · THE DELETE RULE TOOK A TAG THAT OPENED A PARENTHETICAL AND LEFT THE `(` BEHIND — TEN TIMES

`rewrite-refs.py --rule delete` has a pattern for `"(chapter 3.21, FR-…)" -> "(FR-…)"`. It is
right about that line and blind to the sentence:

    /** Everything the connect path needs, in ONE round trip (chapter 3.11,
     * FR-RTL-05, FR-RTL-06).

`H` is horizontal whitespace **by design** — a deliberate fix, recorded in the file, for a
`\s*` that once ate a newline and joined two comment lines. So the substitution stops at the
line break and leaves `(` orphaned at the end of the line, with its contents on the next.

**TEN IN THE TREE, AND EIGHT OF THEM PREDATE THIS CHAPTER:**

    at rework/part3-ch23   8    in files no chapter since has opened
    at rework/part3-ch24  10    the two new ones are both `repository.ts`

Nothing looked, because the property has no checker. It is trivially checkable: after the rule
runs, **no comment line may end in a bare `(`** — a positive-controllable, corpus-wide assertion
in one grep.

**FIXED BY REFUSING RATHER THAN BY WIDENING.** `delete_one` now skips a substitution whose result
ends in `(` when the input did not, which routes the reference to `read` — where a person joins
the two lines. That is the answer the mirror-image case already gets: `\b[Cc]hapters?$` one
function up catches the tag split across the break the OTHER way, and it was written for the same
reason. The two new instances are decided in `read-class.json`; **the eight older ones are a
repair, not this chapter's**, and they go with 045-21's repair-replay list.

**AND THE SAME PASS FOUND AN ID LIST PUBLISHED COLLAPSED.** Four comments in this range read
`(FR-RTL-05/FR-RTL-05/FR-RTL-05)` and `(FR-RTL-07/FR-RTL-07)`. Published's own text had
`FR-005/FR-006/FR-009` and `FR-022/FR-023` — three distinct clauses and two, renamed to one id
each by a later feature and left printed three times and twice. `main` carries them still.
Collapsed to a single id here, in the commit that first brings the line into this tree.

## 045-42 · THE FENCED HALF OF THE REFERENCE CORPUS HAS BEEN EMPTY FOR THE WHOLE REBUILD

`refrules.platform_files` is the union of two definitions — files with a source suffix, and files
a titled fence names — and its own docstring says why the second is needed: `services/api/Dockerfile`
has no extension, is fenced, and carries `# The api (chapter 3.5).`

`platform_files(root, tutorial=None)` defaults `tutorial` to `root.parent / "relay-tutorial"`.
**Every script the rebuild runs passes the WORKTREE as the root** — `replay-range.sh` does
`RELAY_PLATFORM=$WT`, and `$WT` is `/home/dong/work/relay/tmp/part3-refactor`, whose parent is
`tmp`. There is no tutorial there. `Path.glob` on a missing directory yields nothing and
`post-series.md` was skipped by its own `exists()` check, so the fenced set came back **empty**,
the corpus silently collapsed to `SOURCE_SUFFIXES`, and every reference scan of the rebuild has
been running on the narrower half.

**MEASURED AT THIS CHAPTER'S TAG, BOTH WAYS:**

    RELAY_PLATFORM=<worktree>                        1 reference in 1 file
    RELAY_PLATFORM=<worktree> RELAY_TUTORIAL=<...>   2 references in 2 files, one `delete`

The one that appears is the fenced Dockerfile the docstring was written about. `git grep` finds
`chapter 3.5` in three Dockerfiles; only one is fenced, and the other two are outside the
corpus **by the corpus's own definition** — which is a scope, not a hole, and is now the
difference between the two numbers rather than an accident.

**THE FIX IS TO FAIL, NOT TO DEFAULT.** `fenced_paths` now raises on an absent tutorial rather
than returning an empty set, and `platform_files` reads `RELAY_TUTORIAL` before falling back to
the sibling. The three replay scripts pass it. **A default path is a claim about the filesystem**,
and an unchecked one turns a checker into a checker of half its corpus that reports in the
language of a pass — which is 044-1's lesson about a broken pattern filing a zero, one layer up.

**THE REPAIR RAN BEFORE NEW 25, AND IT HAD TO.** With the corpus complete, a replay rewrites
`services/api/Dockerfile` in every tree that contains it — so porting new 25 first would have
put a file belonging to **new 19** into new 25's diff, and the chain would then want a hunk for
it on the wrong chapter's page.

Measured first, then done. The reference sits in the tags for **ch19 through ch24** and nowhere
earlier, which is exactly where old 3.5's Dockerfile lands in the new order, so the repair range
is `ch18..ch24` — 68 commits — and not the whole rebuild.

    tip-to-tip diff after the replay   1 file, 1 line: `# The api (chapter 3.5).` -> `# The api.`
    the commit it lands in             `feat: containerise the api, gateway and dispatcher`
    tags re-pointed                    ch19 … ch24, messages preserved
    references at the new tip          0, over the COMPLETE corpus, all 7 controls firing
    check-chapter ch19..ch24           0 problems each, after the fence body moved with it
    check:fences HEAD mismatches       157 -> 156, and no Dockerfile in the remainder

**THE LINE LANDS IN THE COMMIT THAT CREATES THE FILE**, so no chapter shows the Dockerfile as a
modification and no other chapter's fences move. That is the property a repair replay is for, and
it is only available because the reference rules are idempotent: re-running them over trees with
no ordinals left finds nothing and changes nothing.

**AND `main` HAS THE SAME TWO STRAGGLERS.** `services/dispatcher/Dockerfile` and
`services/gateway/Dockerfile` still read `(chapter 3.5)` in both trees, because neither is fenced
and neither has a source suffix — outside the corpus **by the corpus's own definition**, which is
a scope rather than a hole. The convention's REASON reaches them (an ordinal ages every time the
plan changes, and a person reads these files) and its INSTRUMENT does not. Left as measured, said
out loud here, rather than fixed by a scan that would then be claiming a corpus it does not have.

**ONE COUNT CHECKED AND FOUND RIGHT.** `refrules.py` says "24 fenced paths sit outside the suffix
list". Re-counted with the corpus working: 37 such titles, of which 13 name nothing here — 11 are
PROSE titles (`the check`, `42P01`, `run 11 of 20`) and two are `packages/outsider/`, which does
not exist until new 26. **24 real paths.** The number was right; this ledger's usual finding is
the other kind, so a confirmation is worth its line.

## 045-43 · THE DRAIN EXEMPTION ARRIVED HALF STALE, AND THE TEST THAT SAYS SO FOUND IT ON ITS FIRST DAY — CLOSED

045-34 deferred published's global-drain rule out of new 24 and named the chapter that would owe
it. That chapter is **new 25**, because published fixes R23 in `f2e4a37` — old 3.12's own commit —
and the fix is the four-block composed shape that ledger entry described from published's final
tree.

**TAKEN HERE, AND THE OBJECTION THAT HELD IT BACK IS GONE.** New 24 refused it because the rule
would have arrived without the matching `exempt.ts` entries and made that file's "the two lists
MUST AGREE" comment false. `f2e4a37` carries both halves.

**SIX PROBES, EACH RED WHERE IT SHOULD BE RED**, run against the composed config:

    a plain `.itest.ts` importing `drizzle-orm`          banned   (R23 closed)
    a DRAIN-exempt suite importing `drizzle-orm`         banned   (excused from one rule, not two)
    a DRIVER-exempt suite importing `drainOutbox`        banned   (likewise, the other way)
    a plain `.itest.ts` importing `outboxDepth`          banned   (the union's drain half)
    a drain-exempt suite importing its own drain         allowed  (the exemption works)
    the tree as it stands                                clean

**AND THE EXEMPTION LIST IS THREE, WHERE PUBLISHED'S IS SIX.** `drain-exempt.test.ts` reads the
restricted names out of `DRAIN_NAMES` and asserts both directions against the TREE — every listed
suite still imports one, and every suite that imports one is listed. It went red immediately:

    test-event.itest.ts      names `drainDueDeliveries` only in prose about why it does NOT call one
    notifications.itest.ts   names two drains in comments arguing for scoped assertions instead
    dispatcher.itest.ts      declares `drainDueDeliveries` as a PROPERTY on a stub it builds

Three standing exemptions over nothing, on the list's first day — **the exact failure mode
`exempt.ts`'s own header warns about, arriving by inheritance rather than by drift.** A list
copied from another tree is a list nobody has checked against this one.

**`lists-agree.test.ts` IS DELIBERATELY NOT TAKEN**, and the reason is the sharper half of this
entry. It asserts `DRAIN_EXEMPT_TESTS` and `exempt.ts` name the same files. That holds in a tree
whose guard array has nine tables including the webhook ones; **this rebuild's guard grew per
chapter by SUBJECT** — the reassignment's own instruction — so it holds seven, none of them
touched by these drains, and `EXEMPT_FILES` names one file. Asserting the agreement would mean
widening a guard array to satisfy a test. **Two lists agreeing is a proxy; each list agreeing with
the tree is the thing itself**, which is 044's finding about this very file read one step further.

## 045-44 · A "IS THIS ALREADY PORTED?" PROBE ANSWERED THE OPPOSITE ON THE ONE COMMIT THAT MATTERED

Scoping new 25 meant asking, of sixteen commits in old 3.12's span, which were already in the
tree. The cheap probe is to reverse-apply each patch and see whether it fits:

    git show <c> | git apply --check -R --3way -

It reported **`08e9dbf` — FR-044, authorize a platform credential by SERVICE — as already in.**
It is not. `AcceptSpec` did not exist, `PlatformService` did not exist, and both controllers still
read `@Accepts("platform")`. The ledger had named that commit as new 25's in writing, one line of
`deferred.md` above where the probe's answer was being read.

    with --3way   1 of 16 wrong in the direction that SKIPS work
    strict        15 of 16 wrong in the direction that REDOES it

Neither is usable: `--3way` falls back to blob matching and reports success for a patch it did
nothing with, and strict mode fails on any file the rebuild has touched — which is most of them.

**WHAT ANSWERED IT WAS READING THE TREE.** `grep AcceptSpec` and `grep @Accepts` in the two
controllers, five seconds, unambiguous. That is mechanism 1 in CLAUDE.md's ranking — ask the
repository a question with a yes-or-no answer — and the probe above is what it looks like when a
question that HAS a yes-or-no answer is asked of the wrong oracle.

**AND THE COST OF BELIEVING IT WAS SPECIFIC.** The chapter would have shipped without the
narrowing it is about: two platform credentials resolving to one class, the gateway's reaching
`POST /internal/dispatch/replay`, which takes a dead-letter id and no environment.

## 045-45 · FR-044 WENT RED IN A NEIGHBOUR'S POSITIVE CONTROL, WHICH IS THE ONLY REASON IT WAS NOTICED — CLOSED

New 25 narrowed `/internal/usage/connections` to `@Accepts({ platform: ["gateway"] })`. New 24's
gauntlet attack — the one 045-35 added — reports usage through
`process.env["RELAY_INTERNAL_CREDENTIAL"]`, which is **the dispatcher's**. The battery said:

    FAIL  the platform routes > a connection billed to one environment cannot be re-billed
    AssertionError: expected 403 to be 200

**ON THE SETUP CALL, BEFORE ANY ATTACK WAS MADE.** The line that failed is the positive control
written into that test one chapter earlier — *"a legitimate call: the platform may report the
victim's own connection. Without it the refusal below would also arrive from a route that credits
nothing at all."* Without that line, the test would have gone GREEN: the attack expects a refusal,
and a route refusing everything refuses the attack too.

**THAT IS THE WHOLE ARGUMENT FOR A POSITIVE CONTROL, PAID BACK ACROSS A CHAPTER BOUNDARY.** The
control was written to guard against the route being broken; what it caught was the route being
correctly narrowed and the test not knowing. Same shape, one chapter's distance, and no other
assertion in either chapter could have seen it — `usage.itest.ts` sets both credentials itself.

Fixed by presenting the gateway's credential, which is what the route now requires. **A narrowing
its own suite does not notice is a narrowing nobody has measured.**

## 045-46 · A REINTRODUCTION NAMED ITS TARGET BY MEMORY, AND THE TARGET HAD MOVED

New 25's opening section is three deliberate defect reintroductions, and its whole point is
that the first one did not fire. Re-run in this tree:

    1.  unscope `listMessages`' scoping helper       71/71 passed   (as published: 21/21)
    1b. ALSO unscope `channelExists`                 71/71 passed   (published: 2 fired)
    1c. unscope `channelVisibleTo`                   5 fired
    2.  unscoped UPDATE, every read still scoped     1 fired, `differences` EMPTY
    3.  a 403 that needs an unscoped read to make    2 fired

**STEP 1b IS THE NEW FINDING.** Published's correction — the move that took its first
reintroduction from green to red — **is green here.** `channelExists` is not on the history
path any more: the channel-control chapter replaced existence with VISIBILITY, because an
absent channel answered 404 while a private channel a non-member read answered 200 with an
empty page, and one predicate now produces both refusals.

So the probe was right about the shape of the fault and wrong about the function, and a probe
aimed at a function nothing calls **passes without testing anything** — which is the same
sentence this chapter spends four hundred lines making about test suites, arriving one level up
in the thing that verifies them. *Which check is outermost is itself a thing that changes.*

**AND FIVE REDS ARE NOT FIVE FAULTS.** `channelVisibleTo` sits under the message read, the edit,
the deletion and the edit history; the fifth is the credential attack, whose ORACLE is a message
read. One unscoped SELECT, five assertions. A suite of independent attacks is not independent
where two of them share a target, and a count of red assertions is a count of assertions.

**REINTRODUCTION 3 FIRED TWICE WHERE PUBLISHED REPORTS ONCE**, for a duller reason worth one
line: `setEnabled(id, enabled)` serves both the enable and the disable route here, so a fault
planted in it is visible from either door.

All three were reverted against a committed tree and the tree was verified pristine — `git
status` empty, `git diff` empty, zero occurrences of the probe's own helper name, isolation
suites back to 71/71. The lane keeps the rows: the gauntlet seeds fresh disposable environments
per run, so reintroduction 2's cross-tenant write damaged a fixture that no later run reads.

## 045-47 · THE CHAPTER'S OWN LINT FIX HAD NO FENCE AND NO PROSE IN ANY CHAPTER — CLOSED

`regen-fences` reported `eslint.config.mjs` under **changed but NOT fenced** for new 25 — and
that file is where this chapter closes R23, in 260 added lines. Four chapters fence that file
(new 8, 11, 22, 23) and none of them is this one, so a reader typing along would have reached
the end of Part 3 with a config that silently exempts every integration test from the driver
rule, and no page would have mentioned it.

**THE UNFENCED LIST IS NOT A DEFECT BY ITSELF** — a milestone chapter publishes instruments
rather than an appendix, and new 24 left 27 of 52 unfenced with reasons. What made this one
different is that the unfenced file carried the chapter's own headline change.

A section was added: the rule, the replacement mechanism stated plainly, the two-line
measurement that proves it, the four hoisted sets, the six probes as a table, and the
three-entries-stale exemption list. `check-chapter` goes 6 fences / 4 compared / 0 problems to
**7 / 5 / 0**.

**AND `regen-fences`' SECOND LIST IS THE ONE TO READ EVERY TIME.** Its "changed but NOT fenced"
line is the only instrument in either repository that answers "did this chapter change something
it never explains", and it answers by listing rather than counting — which is what made one file
out of thirteen stand out at all.

## 045-48 · THE SEAL'S LAST BLOCK CARRIED HALF A RULE, IN THE ONE PACKAGE THAT MOST NEEDS THE OTHER HALF — CLOSED

`packages/outsider` is sealed in three levels so that "an integration built from published
documentation alone" is a mechanical claim rather than a promise. Level 2 is a
`no-restricted-imports` block, and published's version sets **only the outsider's own
patterns**:

    rules: { "no-restricted-imports": ["error", { patterns: [ @relay/*, ../* ] }] }

No `paths`. And that block is LAST, which the file's own comment says is deliberate — one
winner per file, the last matching block. So `pg`, `drizzle-orm` and `ioredis` were unrestricted
in `packages/outsider`, **and they resolve there**: the parent walk reaches the workspace root's
`node_modules` even though `@relay/*` does not, which is the whole mechanism level 1 depends on.

That is 045-34's replacement fault again, in the package where the ban matters most — the one
whose entire purpose is to have no privileged access. Published's own final tree fixes it
(`paths: DRIVER_AND_ENGINE.paths`); its Part-3 commit does not.

**TAKEN HERE COMPOSED, AND ALL THREE LEVELS MEASURED RATHER THAN ASSERTED:**

    level 1  node -e "import('@relay/protocol')" from the package   ERR_MODULE_NOT_FOUND
    level 2  `@relay/protocol`                                      red
    level 2  `../../protocol/src/codes.js`                          red
    level 3  `join(HERE, "..", "dist")`                             red
    level 3  `node:module` / `createRequire`                        red
    level 3  `import … from "/etc/passwd"`                          red
    the union `import { sql } from "drizzle-orm"`                   red   <- published: allowed
    the package as written                                          clean

**LEVEL 1 IS THE ONE WORTH MEASURING AT ALL**, because it is the only level that is not a rule.
The comment says the module "is not there"; `ERR_MODULE_NOT_FOUND` from inside the package is the
difference between that sentence and a belief about pnpm's layout.

## 045-49 · A COMMENT COUNTED ITS OWN FILE AND THE COUNT WAS TRUE OF ONE COMMIT — CLOSED

The sealed suite's typing test opens: *"the first `socket.send` in this file's history"*, with a
measured `grep -c` of **0** beside it. Counted across published's own history:

    30fb8f1  (the commit that CREATES the file)   1
    3412851^ (three chapters later)               0
    3412851  (the commit making the claim)        3
    main                                          3

**The file had an inbound `socket.send` on the day it was written.** A later chapter removed it
and retitled that test "sent over REST", which is the state the claim was measured against — so
"in this file's history" was already false when it was written, and the grep that proved it was
run on a file the sentence was not describing.

**AND THIS REBUILD NEVER APPLIED THE REMOVAL**, so the premise fails twice here: the suite has
sent over the socket since it arrived. The typing leg is still worth porting — every other check
on `typing.send` is in-workspace, using the `ws` package this file refuses to import, so the
frame genuinely had never been driven from outside — but the sentence had to be rewritten to say
that instead.

**FOUND ONLY BY RUNNING THE COMMENT'S OWN COMMAND.** Nothing else would have: a `grep -c` in a
docblock is prose to every instrument in both repositories. **A count in a comment is a claim
about one commit**, and this one outlived its commit by three chapters and a whole reorder.

## 045-50 · A TURBO ENV DECLARATION THAT NO TASK READS IS A CACHE KEY THAT CANNOT CHANGE — CLOSED

`f33beee` adds four variables to turbo's global env list. This tree reads three —
`RELAY_API_URL`, `RELAY_WS_URL`, `RELAY_DEMO_CREDENTIAL`, all by the sealed suite. The fourth,
`RELAY_DOCS_BASE_URL`, is read by `docsUrl` on published's FINAL tree, where `ERROR_DOCS_BASE`
became `DEFAULT_DOCS_BASE_URL` behind an env lookup. In this tree it is still a constant.

A turbo `env` entry is a cache key: turbo hashes the variable's value into the task hash. One
that no task reads can never change a hash, and **nothing reports it** — not turbo, not lint,
not any `check:*`. Dropped rather than kept against a reader that may or may not arrive.

**THE READER BELONGS TO THE ERROR-REGISTRY CHAPTER**, which is new 3 and tagged. Making
`ERROR_DOCS_BASE` configurable is the change that turns `docs_url` from a placeholder into
something a deployment can point at a real host — the debt new 3 opens and puts in Part 4. It
goes with that debt rather than into the last chapter of this part.

## 045-51 · THE SEALED SUITE IS FILTERED OUT OF THREE LANES AND THE THIRD LANE GLOBS THE FILESYSTEM — CLOSED

`packages/outsider` integrates against a platform it does not start. Without `RELAY_API_URL`,
`RELAY_WS_URL` and `RELAY_DEMO_CREDENTIAL` it throws on purpose and prints the five commands that
would satisfy it — a good failure, and the right one.

Three lanes have to be told not to run it, and each is told differently:

    the unit lane          the package declares no `test` script — nothing to find
    `test:integration`     `turbo run test:integration --filter=!@relay/outsider`
    `pnpm coverage`        globs `packages/*/src/**/*.itest.ts` and found it anyway

**MEASURED: one failed file, ten skipped tests, every coverage run.** The exclusion went into a
`package.json` SCRIPT, and the third lane's membership is decided by a glob in
`vitest.coverage.config.mts` — so being filtered out of the lane a chapter was thinking about
says nothing about the lane it was not.

**PUBLISHED SHIPPED IT AND FIXED IT TWO CHAPTERS LATER**, at eight skipped tests; its config
carries the story in the comment that fixes it. It is ten here because the typing leg above added
two. **A count in a filter is a count of what somebody remembered to filter**, and the number
grows with the suite while the filter does not.

**THE GENERAL SHAPE, WHICH IS THE PART TO KEEP.** A suite's membership in a lane is declared in
as many places as there are lanes, in as many languages: a missing script, a turbo filter, a
vitest glob. Nothing cross-checks them, and this rebuild has now been bitten by the same class
twice in two chapters — 045-47's unfenced config was a file changed and never explained, and this
is a file excluded and never excluded. **Ask of every lane, separately, whether it can see the
thing you just told one lane to ignore.**

## 045-52 · THE SEALED SUITE PORTED AT ITS BIRTH COMMIT WAS RED ON THREE OF TEN, AND PUBLISHED TOOK TWO CHAPTERS TO NOTICE THE SAME THING — CLOSED

`packages/outsider` arrives at new 26 from `30fb8f1` — the commit that creates it, fourteen
chapters earlier in published's order than this chapter sits in the rebuild's. Run against a live
stack:

    refuses a private channel, naming the field    expected 400, got 201
    sends a message over REST and reads it back    expected 201, got 400
    docs_url on a foreign channel                  expected "#not_found", got ".../not_found"

Each is the platform having moved: the channel-control chapter widened the create route's enum to
`["public","private"]` and that chapter is now BEHIND this one; a send must name a bot since
FR-MSG-15; and `docsUrl` is a path per code here where published later made it an anchor on one
page.

**PUBLISHED'S OWN COMMENT ON THE FIRST ONE IS THE ENTRY:**

> *"THIS TEST WAS RED FOR TWO CHAPTERS AND NOBODY SAW IT (T065). It asserted `400` with
> `field: "type"`, which was true when it was written… this suite was not run at that chapter's
> close — `pnpm test:outsider` is its own lane, outside `pnpm test:integration`, so nothing in the
> twenty-run battery touches it. The one suite that stands for an external developer was wrong
> about the API for two chapters."*

**THE LANE ISOLATION IS RIGHT AND IT IS THE CAUSE.** The suite needs a compose profile no
developer should be forced into, so keeping it out of the default lane is correct — and it means
the suite is only ever as true as the last time somebody deliberately ran it. That is the same
class as 045-51 one turn earlier, from the other side: **a suite kept out of the lanes everybody
runs is a suite nobody runs.**

**SO IT WAS RUN, WHICH IS THE POINT OF THE CHAPTER.** Taken in the form written against a complete
platform and adapted where this tree differs: **16 of 16**, against a stack built with `--build`
(the chapter's own `<Trap>` is about stale images), seeded through `scripts/seed-demo-tenant.mjs`,
with the seal re-verified after the swap — level 1 `ERR_MODULE_NOT_FOUND`, a `drizzle-orm` import
still red.

**AND THE ADAPTATION IS ONE LINE, NAMED.** `docs_url` is asserted as a path per code. The anchor
form needs `ERROR_DOCS_BASE` to become configurable, which is the error-registry chapter's change
and Part 4's debt — 045-50 is the same boundary seen from turbo's env list.

## 045-53 · THE LAST CHAPTER'S VERDICT IMPROVED BECAUSE OF THE REORDER, WHICH IS THE FEATURE'S OWN THESIS ARRIVING AS A MEASUREMENT

New 26 is the outsider milestone, and its verdict is the SRS Phase 2 exit criterion. Published
reports **MET IN PART** with two things missing, "different in kind":

    1  a REST-sent message reaches no live socket, and no document says so
    2  content sufficiency is not comprehensibility — no test can reach it

**THE FIRST IS CLOSED HERE, AND NOT BY ANY WORK THIS CHAPTER DID.** That symptom had two causes.
The sender chapter removed one — a public send attributes a sender, so the row survives a resume.
The message-delivery chapter removed the other, which was the whole of what remained: the api
published to no fan-out at all. **In published's order both fixes came AFTER the exercise that
recorded the gap. In this order both are behind it.**

Measured, not argued: the suite's own test used to be titled "receives a message on a socket —
SENT over the socket", in capitals, because a REST send could not work. It sends over REST now
and passes — the send an integrating developer's backend actually makes.

So the verdict goes from two missing things to **one**, and the closing hand-forward loses two of
its three items: the publish is done, and so is the public surface a customer drives, including
the `type: "private"` this part used to refuse at the door.

**THIS IS FR-007's CLAIM WITH A NUMBER ON IT.** The feature's premise is that grouping by subject
is better than grouping by the order the work happened in. The strongest evidence available for
that was always going to be a milestone whose verdict changes — same suite, same platform, and a
chapter that measures a gap no longer running before the chapters that close it. **Nothing in the
plan predicted this**; it fell out of running the suite the chapter is about.

**AND THE WEAKER HALF IS WORTH SAYING TOO.** The remaining gap is the one no reorder can help and
no instrument can reach, and it is the same sentence CLAUDE.md has carried for thirteen records:
*use a person.* Part 3 now ends on it rather than on a scheduling note.

## THE CLOSE-OUT PASS — FIFTY-THREE ITEMS RE-MEASURED, TWENTY-TWO CLOSED, AND THE ESTIMATES WERE WRONG IN BOTH DIRECTIONS

Part 3 is rebuilt, so the ledger was read against the tree rather than against itself — the rule
CLAUDE.md states as **measure the carried ledger; do not copy it**. Every open item was given a
yes-or-no question and asked it of the repository.

**SIX WERE ALREADY DISCHARGED AND SAID SO, AND FIVE OF THE SIX CHECKED OUT:**

    045-25  `built by createServer and never injected: limits` is in `main.test.ts`
    045-27  guard.itest.ts carries the third direction — bait in every guarded table
    045-30  both cases and both falsifications are at the code, in new 23
    045-33  regen-fences.py:81-85 strips the header BY POSITION; the prefix filter is gone
    045-35  all five `/internal` keys are in `ADDED`
    045-40  `quota-email.ts` is pinned at `branches: 90`

**ONE CLOSED WITH NOBODY WORKING ON IT**, which is 043's shape and worth the line. **045-28**
said the dispatcher's integration config was the unwired one of five lanes. Re-measured: all five
carry `globalSetup` and `setupFiles`. It was wired by a later chapter's port and the ledger never
heard.

**AND 045-1's OWN COST ESTIMATE WAS PESSIMISTIC BY A FACTOR OF FIVE.** It warned that closing it
"changes ten trees, not ten messages", because a read-class pair added after a chapter is tagged
leaves that chapter's tree carrying the ordinal — and it said to *re-check the number per chapter
rather than assuming it stays at one*. Re-checked, all 26:

    ch1, ch3..ch18   0 ordinals in source
    ch2              2   (both `chapter 3.2` — self-references, and NOT covered by any rule)
    ch19..ch26       3   the deliberate `schema.ts` quotation, and two unfenced Dockerfiles

So the tree cost was **two files in two chapters**, not ten trees. The replay over
`part2-ch8..part3-rework` — 221 commits — changed:

    messages         8 ordinals -> 1        the one that stays is a QUOTATION (below)
    trees            ch9..ch16, 1-2 files   `(chapter 3.15…)` and a span recount
    the tip tree     BYTE-IDENTICAL         `git diff` between old and new heads: empty
    26 tags          re-pointed, messages preserved, chain re-verified
    check-chapter    0 problems on all 26, after four chapters' fences regenerated

**THE ONE ORDINAL THAT STAYS IS THE EVIDENCE FOR THE CONVENTION.** `56292d8` reads *"twenty-two
comments renumbered from `chapter 3.12` to `chapter 3.14`, because the work they cited had moved
and the number encoded a position"*, and its next paragraph is this feature's whole argument. The
ordinals are the SUBJECT of that sentence, not citations in it — the same exemption
`schema.ts`'s "This line used to say" carries in source. Rewriting it would delete the evidence,
so the subject map says so in a comment beside the decision.

**AND THE MIRROR CAUGHT WHAT check-chapter COULD NOT.** Regenerating four chapters' fences moved
four fence BODIES, and their Vietnamese pages hold byte-identical copies. `check-chapter` is
tag-to-tag and stayed at 0; `check:fences` went **296 -> 300 with a new MIRROR 4 category naming
exactly those four chapters**, and back to 296 once the bodies followed. Two instruments, two
scopes, and only one of them can see a mirror.

Three of the four Vietnamese pages hold LIVE translation work, so `vi-placeholder.py` was the
wrong tool — it replaces prose by design. `sync-vi-fences.py` is the new one: it copies fence
bodies by title and occurrence, refuses a per-title count mismatch, and touches nothing else.
Its guard fired immediately, on two chapters that fence one path twice.

**WHAT IS STILL OPEN, AND WHY** — thirty-one items, and none of them is a chapter's:

    a repair replay with pairs      045-7 (three sentences false for six chapters),
                                    045-10 (five possessives), 045-20 (a docblock),
                                    045-23 (35 of 137 cited ids), 045-26 (a rename),
                                    045-41 (eight dangling `(`)
    a chapter that no longer exists 045-12 — the lane reset belongs to new 8 and Part 3 is closed
    a decision that is a person's   045-13 (which set), 045-2 and 045-11 (scope),
                                    045-3 (an 80-entry expectation table)
    recorded lessons, no action     045-6, 045-9's residue, 045-17..045-19, 045-21, 045-22,
                                    045-24, 045-29, 045-31, 045-32, 045-36..045-39, 045-42's
                                    two Dockerfiles, 045-44, 045-46, 045-53
    the post-series amendment       045-38 (the typing flake)

**THE SIX REPAIR-REPLAY ITEMS ARE ONE PASS NOW, NOT SIX.** Each is a table of exact pairs applied
to every tree, which is what this pass just proved costs: one replay, four chapters' fences, one
mirror sync. They were filed separately because each was found in a different chapter; they close
together.

## 045-54 · A SUBJECT MAP IS KEYED BY SHA, AND A REPLAY IS THE THING THAT CHANGES SHAS

The close-out pass closed 045-1 by replaying the rebuild with a subject map — `<sha>|<subject>`
for the five published titles that carried their position. It worked. The NEXT replay, twenty
minutes later, refused:

    subject map names e4bc665, which is not in part2-ch8..part3-rework

**THE CHECK IS RIGHT AND THE MAP WAS RIGHT WHEN IT WAS WRITTEN.** `replay-range.sh` asserts that
every mapped sha is an ancestor of the head, because *"a stale line is a subject that silently
keeps its ordinal, which is the failure this map exists to prevent."* And the first replay is
exactly what made those five shas non-ancestors: it rewrote them.

So a subject map is **single-use by construction** — good for the replay that consumes it and
invalid for every replay after, including a re-run of the same one. Nothing said so, and the
mode it fails in is the good one: it stops rather than passing over a name it cannot find.

**THE SECOND REPLAY NEEDED NO MAP AT ALL**, which is the other half of the point. The messages
were already rewritten and committed; only the file table had grown. A map is a record of a
decision, and once the decision is in the history the map is spent.

Written down because the next repair pass will reach for the same file: **check whether the map's
shas are still in the range before adding a line to it, and delete a map whose decisions have
landed.** The alternative — re-keying five shas after every replay — is a table that has to be
maintained against a moving history, which is the shape this whole feature exists to remove.

## 045-55 · AN ORDINAL WITH AN ITEM NUMBER HANGING OFF IT, ELEVEN TIMES IN THIS FEATURE'S OWN COMMIT — CLOSED
Found while repairing a `post-series.md` hunk. The amendment chain carried:

    the two-lists-that-must-agree defect `gaps.md` the revisions chapter-4 records about

**AND THE FIRST DIAGNOSIS WAS WRONG, WHICH IS WHY IT IS WRITTEN DOWN TWICE.** It was filed as a
FEATURE id read as a chapter ordinal — `044-4` matched because 044's subject name is *the
revisions chapter*. That reading is tidy and false. `git show` on the commit that did it settled
it in one line:

    - * subscriptions name `channel.created`**. The review and `gaps.md` 3.23-1 both recommend
    + * subscriptions name `channel.created`**. The review and `gaps.md` the revisions chapter-1 both

The original is **`3.23-1`** — a gaps ITEM id, `<chapter>-<item>`. The rule matched the right
thing: `3.23` IS a chapter ordinal, and *the revisions chapter* is its name. What it could not
know is that the ordinal was part of a larger identifier, so the substitution left `-1` hanging
off a chapter name.

**ELEVEN IN THE PLATFORM, NINE OF THEM ALSO IN THE AMENDMENT** — and the two counts are the same
defect seen twice, because `post-series.md`'s `+` lines are what put them in the tree. The
rebuild's own trees carry **zero**: these are 044's files, after Part 3, so the Part-3 rebuild
never touched them.

**A CITATION INTO A DOCUMENT IS AN ID.** Renaming a chapter does not renumber that chapter's own
`gaps.md`, which is exactly why `FR-RTL-05`, `T121a` and `R7` pass through untouched. Reverted to
`3.23-N` and `3.22-6` in both places at once, because the amendment and the tree have to agree or
the chain HEAD-mismatches. `check:fences` before and after: **296, APPLY 139, HEAD 157.**

**AND THE GUARD'S FIRST VERSION WAS WRONG, CAUGHT BY ITS OWN NEGATIVE CONTROL.** `(?!-\d)` on the
ordinal branches looked sufficient and is not: `\d{1,2}` backtracks, so `chapter 3.23-4` still
matched — as `chapter 3.2`, with `3-4` left over. `(?!\d)(?!-\d)` is the pair that holds.

`refrules.py` declares three refused strings beside its three positive controls now. **A positive
control proves a pattern still fires; only a negative control proves it stopped firing where it
should not** — and this one found the fix incomplete before a line of source was touched, which is
the whole argument for having written it.


## THE DECIDED PASS — SIX ITEMS CLOSED ON A PERSON'S ANSWER, AND TWO ESTIMATES CORRECTED BY THE TOOLS

Four decisions were put to a person because each changed what the work would be, and two more
were taken with a stated recommendation. What came back closed **045-7, 045-11, 045-12, 045-13,
045-20 and 045-50**, through three history splices and one replay.

**045-12 SPLIT THE WAY THE CHAPTERS DO, WHICH THE DECISION DID NOT ANTICIPATE.** "Port it into
new 8 properly" could not be done: the script purges `webhook_deliveries`, and that table is
created at **new 19**. A script deleting from a table the tree does not have is a script nobody
can run. So the broker half is new 8's — where the harness is — and the deliveries half arrives
in the chapter that creates the table, each with its own half of the test. 192 commits rebased
for the first, 70 for the second, one conflict each.

**AND ITS SECOND ASSERTION WAS VACUOUS UNTIL IT WAS FALSIFIED.** Written as "run the script,
count stale rows, expect zero", it PASSED with the DELETE replaced by a no-op — a lane that was
just reset has no stale rows either way, so the test was green in exactly the case it exists to
catch. It plants the row it is about to have deleted now. The stream half was written with its
planting from the start and went red on the same probe: `messages survived the purge: expected 3
to be +0`.

**045-13 LANDED IN THE SHAPE MAIN INDEPENDENTLY REACHED.** `WEBHOOK_EVENT_TYPES` carries an
`emitted` flag per type, and `satisfies Record<string, { emitted: boolean }>` makes adding a type
without deciding a compile error — so "declared but unbuilt" stops being a comment. Validated
against FR-WHK-02's declared eight, not the emitted five, because refusing a subscription to a
published-but-unbuilt type is 044's FR-016 defect, which was amended rather than shipped.
`event.test.ts` compares the two sets in both directions **with a positive control**: if they
were ever identical the agreement test would pass against a declared set whose flag was dead
weight.

**045-11's DEFECT WAS A TITLE AND AN ASSERTION DISAGREEING FOR TWENTY-TWO CHAPTERS.** The
`describe` said *"the docs URL is built in one place, with the code as the anchor"* and the
assertion under it checked `` `${base}/${code}` `` — a path. `docs/08-error-reference.md` is one
document with `## <code>` headings, so all 27 `docs_url` values named pages that do not exist.
Nothing could catch it: the function and its test were written together, and **the reference
document is the only artefact that disagreed — no instrument reads it.** Corrected at new 25,
where published corrected it; Parts 1 and 2 keep teaching the path form, as published does.

**AND CLOSING IT FALSIFIED 045-50.** That entry says a turbo env declaration no task reads is a
cache key that cannot change, and it was right — `RELAY_DOCS_BASE_URL` was declared and unread.
Making `docsUrl` read it per call gives the declaration a reader, so the commit that removed it
was replayed out of the history. **An item can be closed by making its premise false rather than
by fixing what it describes.**

## 045-56 · THE TOOLS CORRECTED TWO OF MY ESTIMATES BEFORE EITHER COST ANYTHING

**"SIX ITEMS ARE ONE PASS NOW, NOT SIX" WAS WRONG, AND `apply-read-class.py` SAID SO.** Its
word-count guard refused 045-7 (`WORDS DROPPED {'falls': 1}`) and 045-20 (`{'rate', 'limiter',
'added'}`) — a tense and a rationale, neither of which is a reference. Two of six, not six.

**AND THE ANSWER WAS NOT TO TURN THE GUARD OFF**, which is what the decision offered and what I
would have built. The tool already had the sharper mechanism: a per-group `drops` list naming the
words the group may lose, declared beside its reason, with an undeclared drop still failing. The
prose group declares four words. **A guard with an exemption per declared word beats a guard with
a switch.**

**AND SEVEN OF EIGHT PAREN PAIRS MISSED**, hand-typed from `sed 's/^/    /'` display output and
carrying four spaces the files do not have. One of the eight happened to sit at column zero, so
the first attempt looked like partial success. Regenerated from the files: all eight.

## 045-57 · `pnpm install` AT A MID-HISTORY CHECKOUT PRUNES THE DEPENDENCIES LATER CHAPTERS DECLARE

Splicing a commit into new 8 meant checking the worktree out there and installing. Chapter 8's
`services/api/package.json` does not declare `ioredis`; the rate-limit chapter is new 22. pnpm
pruned it, and the next typecheck at new 19 said:

    src/fanout/publisher.ts(9,23): error TS2307: Cannot find module 'ioredis'

**IN FILES THAT LEGITIMATELY IMPORT IT**, which is why it reads as a broken tree rather than a
pruned `node_modules`. The rule: install at the tree you are about to gate, and install again at
the tip when the splicing is done. `node_modules` is state the checkout does not carry.

## 045-58 · AN EARLY CHAPTER'S INTEGRATION SUITE CANNOT RUN AGAINST THE FINAL SCHEMA

Running new 19's webhook suite to check the new refusal:

    error: update or delete on table "users" violates foreign key constraint
           "usage_active_users_user_id_fkey" on table "usage_active_users"

The harness's `plant()` deletes the tables **that chapter knows about**, and the lane's database
is migrated to the LAST chapter's schema. `usage_active_users` arrives at new 23 with a foreign
key to `users`, and chapter 19's harness has never heard of it.

**THE PER-CHAPTER LOOP NEVER MET THIS BECAUSE IT ALWAYS RAN FORWARD** — each chapter's battery
ran at that chapter's tip, where the schema and the harness agree by construction. Going
backwards breaks that, and it is not a defect in either: a chapter's harness is correct for its
own tree. What it means practically is that a spliced change is verified at the TIP, not at the
chapter it lands in.

## 045-59 · A DERIVATION FOR 045-3 WAS ATTEMPTED TWICE AND FAILED TWICE — WHICH IS THE ANSWER

045-3 asks for a table recording which chapter's tree each read-class pair should fire on. It was
measured at 80 pairs; there are now **252 in 29 groups**, so the proposal was to record the
chapter per GROUP — 29 entries, catching a mistyped left-hand side, with no maintenance as pairs
join an existing group.

Deriving those 29 mechanically failed twice:

    from the group's own `why`      17 of 30 name a chapter in the first line
    from the commit that added it   `docs\((?:3\.)?(\d+)\)` matched `docs(045)` and returned
                                    chapter 45 for everything
    name-first, feature excluded    8 of 30 — the messages name their chapter in PROSE, and
                                    only two-thirds of them do

**SO IT IS NOT DERIVABLE, WHICH IS WHAT 045-3 SAID.** *"A table of 80 entries somebody must fill
in and keep true."* The estimate was right and the shape was wrong; it is 29 entries, and they
still need a person.

**AND THE HALF-POPULATED VERSION WAS REFUSED DELIBERATELY.** A `chapter` key on 8 groups with a
check over it passes the other 21 in silence — the "list checked one way can only grow" defect
this feature has recorded four times. Either every group declares one and the check can fail, or
neither exists. Left open with the attempt written down so the next person does not spend it
again.

## 045-60 · `docker compose up` WITH A PARTIAL ENV RECREATES CONTAINERS THE COMMAND WAS NOT ABOUT

045-36 records a battery reading as twenty-two defects because Mailpit answered on 8025 while the
lane runs 18025. It happened again in the same session, from a different direction, and the
second cause is worse than the first.

Bringing the services profile up for the outsider suite:

    RELAY_POSTGRES_PORT=15432 RELAY_WEBHOOK_SECRET_KEY=… \
      docker compose --profile services up -d --wait --build

That command is about `api`, `gateway` and `dispatcher`. It passed no
`RELAY_MAILPIT_HTTP_PORT`, so compose resolved `${RELAY_MAILPIT_HTTP_PORT:-8025}` to the
DEFAULT, found the running container's published ports no longer matched the resolved config,
and **recreated Mailpit on 1025/8025** — a container the command never named.

Eighteen failures across three suites, and the two shapes it produced are not equally readable:

    quotas, connections   TypeError: fetch failed        in `inbox` — honest and traceable
    notifications         expected 0 to be greater than 0 on a DRAIN — the relay sends mail,
                          SMTP refuses, the drain reports nothing drained, and the failure
                          names neither mail nor a port

**THE SECOND SHAPE IS THE DANGEROUS ONE.** A drain returning zero reads as a defect in the
disablement logic. Nothing in it mentions Mailpit, and the suite that says `fetch failed` is a
different file — so a reader who opens the first failure alphabetically starts in the wrong
place.

**THE RULE, AND IT IS NARROWER THAN "SET THE ENVIRONMENT".** `baseline.txt` pins nine variables
for the TEST command; this was a compose command, and the two were treated as different
concerns. They are not: **every `docker compose up` needs the full port environment, whichever
services it names**, because compose reconciles the whole file and a variable it cannot see reads
as a changed configuration. Checking `docker ps` for the published ports after a bring-up costs
one line and would have caught both instances.


## 045-61 · A PLACEHOLDER DELETED TEN TRANSLATED FILES AND THE BUILD COULD NOT SAY SO

`vi-placeholder.py` unlinked the sibling `figures.ts` whenever the placeholder it generated
imported no figures. That is correct in isolation — a placeholder renders no diagrams — and it
is wrong the moment somebody translates the page, because a translated page imports figures the
way the English one does and the file is gone.

Ten chapters, one per port: **01, 02, 05, 06, 07, 08, 09, 10, 11, 12**. Seven of the ten are
broken at HEAD, not only in the working tree, so **the site has not built since chapter 3.1's
port** — the whole of the rebuild.

**WHAT MADE IT INVISIBLE IS NOT THE SCRIPT.** Three instruments passed over it:

    check:figures       reads the PROP NAME — `code={figThing}` vs `chart={figThing}` — and
                        never asks whether `figThing` resolves. One step outside its own header.
    check:fences        reads fences; a JSX import is not a fence
    pnpm run build      the only thing that could see it, and the tutorial checkout had
                        NO `node_modules` for the entire feature

The third is the finding. Every `pnpm` invocation printed *"Local package.json exists, but
node_modules missing"* and the five `check:*` gates ran anyway, because they are plain Node
scripts reading files. **A gate that does not need the install cannot tell you the install is
missing**, and the one gate that would have failed was the one nobody could run.

**RECOVERY IS NOT REGENERATION.** The ten files hold Vietnamese somebody wrote — figure labels,
not identifiers. Copying the English siblings would have compiled and silently replaced ten
translations with English. Each was recovered from the parent of its own deleting commit
(`git log --diff-filter=D`), verified export-for-export against what its page imports: nine
matched exactly, chapter 11's carried one extra export from a state that no longer exists.

Fixed three ways: the `unlink()` is gone and reports instead; `check-figures.mjs` now resolves
every imported binding in both directions and is red-tested three ways (absent file, renamed
export, used-but-unimported); and the whole corpus scans clean for the two MDX parse faults that
the same absent build had been hiding — `\"` inside a JSX attribute, and a `</ForwardRef>`
closing a `<Why>`. Both were unique. 209 figures, 211 bindings, all resolving.

## 045-62 · `pnpm run build` IS NOT ONE OF THE FOURTEEN GATES

Falling out of 045-61 and worth its own entry, because the close-out gate task checks that list
and the list is missing the only instrument that compiles the pages.

The fourteen gates are typecheck, lint, unit, integration, coverage, and the five `check:*`
scripts, plus the platform's own. **None of them parses MDX.** A page can be syntactically
invalid, import a module that does not exist, or close a component with the wrong tag, and every
gate stays green. Two of those three shapes were live in this feature simultaneously.

`pnpm run build` in `relay-tutorial` takes about four minutes, fails on the FIRST bad page and
names no other, and needs `node_modules` — which is the argument for running it once per chapter
rather than once per feature. Ten faults would otherwise cost ten builds.

## 045-63 · THE CONVENTION COMMIT LANDED TWO CHAPTERS LATE, AND ITS OWN MESSAGE SAYS WHERE IT BELONGS — CLOSED IN THE CHAIN

`0317d83 refactor: a source comment names its subject, not an ordinal` — 74 references across 44
files — carries this in its body:

> Establishing the convention on the base so the rebuilt history does not mix the two.

It is not on the base. It sits **between `rework/part3-ch2` and `rework/part3-ch3`**, so the two
chapters ahead of it are on the wrong side of their own convention. Counted over every source
file in every chapter tree, unexempted:

    ch1     2      environment-context.guard.ts:9, signup.controller.ts:34
    ch2     9      internal.ts, user-token.ts, schema.ts, internal.controller.ts,
                   messages.module.ts, request-with-tenant.ts, signup.controller.ts ×2, auth.ts
    ch3–ch8 0
    ch9     1      repository.ts:928 — `3.13's addMembers shape`, removed again at ch10
    ch10+   0      (ch19/ch20's two are 045-64, a false positive)

**Twelve references, and the tip is clean** — 0 over 301 platform files. **A per-chapter contract
needs a per-chapter measurement**: the reader checks out `rework/part3-ch2` and reads `chapter 3.2`
in a comment, naming a chapter this feature deleted.

**AND THE CORRECTION TO THIS ENTRY IS THE PART WORTH KEEPING.** It first said no instrument could
see this, because every instrument looked at the tip. That is false. `check-fence-ordinals.py`
reads fence BODIES across both locales, it reports these same references — **38 hits in 12 files,
19 per locale, the twelve real ones plus the provenance tag's continuations of 045-64** — and it
has been exiting 1 for the whole feature. Nothing was hidden. What happened is smaller and more
familiar: **its output was a bare count with no locations.**

    ordinals still inside a fence body   38  in 12 files
    distinct texts                       12
    files                                12

Twelve files, unnamed. To find out WHICH twelve the scan had to be written a second time by hand,
and the hand-written one disagreed — 18, because it covered one locale — which is how a
disagreement between two measurements of the same thing became the way in. **A red gate that
names nothing is a red gate somebody learns to step over**, and it stayed red beside a fence
chain sitting at a 296-problem baseline, which is the cover a second unexplained red needs.
`--list` now prints every location and its class; that costs eight lines and is the difference
between a number and a finding. What no instrument does is scan the chapter TREES rather than the
pages, which is how the ch1/ch2 split from the ch9 miss was established.

Chapter 9's one is a different miss from the other eleven — it is inside a chapter's own ported
diff rather than on the base, so the reference replay had it in range and did not rewrite it.
Both halves of chapter 9/10's `repository.ts` fence show it, `+` then `-`.

**THE REPAIR IS A CHAIN REWRITE AND IS NOT FREE.** Moving `0317d83` ahead of chapter 1 re-points
all 26 tags; because it changes only comment text and no line counts, chapters 3 onward keep
their trees exactly, and the commit itself becomes empty and drops. Chapters 1, 2 and 3's fences
and chapter 9/10's `repository.ts` fence need regenerating from the moved tags. Not attempted
under this entry; measured, scoped, and left for a decision.

## 045-64 · `DELIBERATE` EXEMPTS THE FIRST LINE OF A PROVENANCE TAG AND NOT ITS CONTINUATION — CLOSED

The tag `refrules` was built to protect is three lines of prose:

    // NAMED, NOT NUMBERED. This line used to say "chapter 3.7's cross-tenant
    // gauntlet". The gauntlet was 3.7 when that was written, became 3.8 when a chapter
    // was inserted ahead of it, and is now 3.9 after a second insertion — and the

`DELIBERATE` is a set of whole lines and holds the first one. Lines two and three each carry
ordinals and are matched, so `schema.ts` reports two references at ch19 and two at ch20 — four
hits that are the exemption's own subject matter. Harmless today because the corpus scan runs at
the tip where the wording differs, which is exactly why it went unnoticed.

The fix is not more lines in a set: an exemption for a *tag* should be scoped to the tag, not to
each sentence in it. Filed rather than patched, because the set-of-lines design is what 045-55
also strained against.

## 045-65 · THE CONVENTION COMMIT INTRODUCED A DOUBLED ARTICLE ONTO A LINE THAT HAD NO ORDINAL — CLOSED IN THE CHAIN

`scripts/credential-walk.mjs:1`, live at the tip and in every tag from ch3 on:

    parent   // The credentials chapter walk, as a script (so the transcript in the chapter is
    0317d83  // The the credentials chapter walk, as a script (so the transcript in the chapter is

The pre-image contains no digits. Whatever produced it — the substitution running on a line
somebody had already fixed by hand, or a hand edit among the 74 — the line was not a reference
and was changed anyway.

**AND THE MEASUREMENT THAT SAID THE CORPUS WAS CLEAN CANNOT SEE IT.** `refrules` looks for
ordinals; zero ordinals over 301 files is a true statement that says nothing about whether the
replacements read correctly. **A rewrite needs a check on its OUTPUT, not only on the absence of
its input** — one `grep -niE '\b(the the|a a|the a|an the)\b'` over the same corpus finds this
one and finds nothing else, and it costs a second.

The file is fenced in chapter 2 (both locales), so the typo is published text. It is one line in
the same commit as 045-63 and is fixed by the same repair, which is why it is filed beside it
rather than patched at the tip: a tip-only fix would be a platform change no chapter documents
and would need a `fences/post-series.md` amendment for a doubled article.

## 045-66 · THE 296 FENCE PROBLEMS DECOMPOSE INTO THREE CAUSES, AND ONLY ONE OF THEM IS ABOUT WHICH TREE

`check:fences` has sat at "296 problem(s) — APPLY 139, HEAD 157" for the whole rebuild, carried
in the record as a baseline. A baseline is a number somebody decided to accept, and nobody
decided this one: it was measured once and repeated. FR-013 says every gate is green at
close-out, so it has to be decomposed before it can be argued about.

`check-fence-chain.mjs:38` reads the platform from `../relay-platform` — a hardcoded path to the
submodule's working tree, which is `main`. The rebuilt chapters' fences replay onto the REWORK
tip. So the gate has been comparing a rebuilt chain against a tree that does not contain it.
Running a copy of the checker with that one line repointed at `tmp/part3-refactor` answers the
question:

                        vs main   vs the rework tip
    HEAD  en chapters       138                  41
    HEAD  post-series.md     19                  24
    APPLY en chapters        42                  42
    APPLY vi chapters        42                  42
    APPLY post-series.md     55                  55
                        ───────   ─────────────────
                            296                 204

**THREE CAUSES, AND THE MIDDLE ONE IS THE ONLY ONE ANYBODY GUESSED.**

**1. Ninety-two are "main is not the rebuilt history" (296 → 204).** The HEAD category is the one
sensitive to which tree; it drops from 157 to 65. This is not a defect in anything — it is the
gate correctly reporting that the published platform does not carry the chapters the tutorial now
describes. **It cannot be fixed inside the tutorial**, and it cannot be fixed at all without
deciding to make `part3-rework` the published history. That decision is not a gate's to make.

**2. The APPLY count is 139 either way — completely insensitive to the platform tree.** 42 in the
English chapters, 42 in the Vietnamese ones, 55 in the appendix. The 42/42 symmetry says these are
the same fences in both locales, which is what a mirrored body does: `sync-vi-fences.py` copies EN
bodies into vi by title and occurrence, so a bad EN body is a bad vi body. **One repair fixes
both**, and the count halves the work rather than doubling it.

**3. The appendix accounts for 79 of the 204 and was never in scope.** `fences/post-series.md`
amends 49 paths with 48 hunks, and analysis pass 3 recorded that "the chain does not end at the
last chapter". Every one of those hunks was written against published 3.24's end state. The
rework changed the end state, so the appendix's pre-images no longer match — **not because the
appendix is wrong, but because it is an amendment to a history that was replaced underneath it.**
No task in this feature touches it. It is the single largest contiguous block of the 204.

**WHAT THIS MEANS FOR FR-013.** "Every gate green" is reachable for twelve of the fourteen. For
`check:fences` it requires, in order: the platform decision (92), 42 fence bodies regenerated in
both locales (84), and the appendix rewritten against the new end state (79). The first is a
person's call, the second is `regen-fences.py` plus reading, and the third is a chapter-sized
piece of work that no task in this feature planned for. **Recording the decomposition is the
useful act here**; quoting 296 as a baseline hid a person's decision inside a number.

## 045-67 · THE REBUILT CHAIN IS A PARALLEL HISTORY, AND PUBLISHING IT AS-IS DELETES FEATURES 043 AND 044

`main` and `part3-rework` diverge at **`6b3423d feat: milestone the tuan test - chapter 2.8`** —
the end of Part 2, which is where the rebuild was told to start. They are not ancestor and
descendant:

    commits on main not in part3-rework    228
    commits on part3-rework not in main    225
    files differing                        177

The raw counts are alarming and mostly meaningless: 193 of main's 228 are published Part 3, which
the rebuild re-ports. **The number that matters is 35** — main's commits after published Part 3's
tip (`8829881 fix(3.24): delete the key instead of destructuring it away`):

    feature 043     16     port bands retired, message-length bound, webhook refusals named
    feature 044      6     `channels.revision_sequence` and the ack that reports it
    feature 045     11     the reference campaign, whose effect the chain already carries
    unlabelled       2

**SO THE REWORK TIP DOES NOT CONTAIN 043 OR 044.** `revision_sequence` appears 10 times in main's
source and **zero** times at the rework tip. Publishing `part3-rework` as the platform's history,
as a branch replacement, would delete a shipped column, the ack that reports it, the
message-length bound, the named webhook refusals and two features' worth of coverage pins.

**NOTHING IN THE RECORD PLANS FOR THIS.** `plan.md`, `tasks.md`, `spec.md`, `deferred.md` and
`baseline.txt` between them mention 043 and 044 only in passing — a credential value "unchanged
from 043 and 044". There is no task to replay them, no note that the chain must be rebased before
it can be published, and no acknowledgement that the two histories cannot be fast-forwarded. It
is the largest hole in the plan and it sits directly under the decision the fence chain's 92 HEAD
problems are waiting on (045-66).

**THE GOOD NEWS IS THE SIZE.** Twenty-two commits of real work plus two unlabelled, onto a chain
whose tip is already green on typecheck, lint and build. That is a replay, not a rewrite — and
`replay-range.sh` and `replay-repair.sh` are the mechanism, already used twenty-six times.

**AND IT ALREADY MISLED A MEASUREMENT, WHICH IS HOW IT WAS FOUND.** The carry task takes feature 044's
ledger "re-measured against the tree rather than copied", and the tree I reached for first was the
rework worktree — the one tree that **cannot** contain 044's fixes. Item C6 ("files that discard
their child's output", closed at zero) came back as **14** and read as a reopening.

Two errors, stacked, and each is one of this project's recorded classes:

    the corpus    measured against a tree that predates the fix
    the pattern   `stdio: ["ignore"` matches `["ignore","pipe","pipe"]`, which discards only
                  STDIN and is the CORRECT form — the child's log line is readable. The
                  positive control for the good form found 15 of them and made the false
                  positive obvious in one line

**C6 re-measured properly, with a control per pattern: one instance in code, in both trees** —
`scripts/webhook-walk.mjs`, `stdio: ["ignore", "ignore", "inherit"]`, which discards stdout and
keeps stderr, in a walk script that drives its loops by hand and needs no port from a log line.
044's "still zero" was measured over test files and is still true of test files. **The item stays
closed, and the ledger now says which corpus the zero belongs to.**

**THE RULE FOR THE REST OF THE CARRY.** Every carried item is a claim about a tree, and this
feature has three: `main`, the rebuilt chain, and the tutorial. An item about the platform's
present state is measured on `main`; an item about the rebuilt series is measured on the chain.
Saying which is not pedantry — it is the difference between a closed item and a false reopening.

## FEATURE 044's LEDGER, CARRIED AND RE-MEASURED — THIRTEEN ITEMS AND THE UNNUMBERED ONE

Re-measured against the tree, not copied. **Every row names the tree it was measured on**, which
045-67 is the reason for: this feature has three trees, and one of them predates the fixes half
these items are about.

    id        state            measured on        then      now
    3.22-3    OPEN, MOVED      tutorial             13         6   excerpt-only files
    3.22-6    CLOSED           main + chain          0         0   in tests (1 in a walk script)
    3.23-4    CLOSED, TWICE    main + chain          —         —   by different means; see below
    043-1     OPEN             tutorial       146/904   151/981   untitled fences
    3.23-2    OPEN             —                     —         —   Part 4.7's, out of scope by name
    3.23-7    OPEN, MEASURED   chain             —         —   comment-only, no trigger
    3.22-4    OPEN             main                  —         —   assertion re-read, unchanged
    3.22-5    OPEN, PREMISE?   main                  5         4   modules naming the bound
    3.22-7    OPEN, WORSE      —                     —         —   045 added its own case
    3.22-8    OPEN, 9th time   feature dir           6        39   instruments with no owner
    044-1     OPEN             this machine    ugrep 7.8.4      confirmed, and paid forward
    044-2     CLOSED           main                  0         0   ids in test titles
    044-3     OPEN             main            330/46    314/45   ids elsewhere in tests

**3.22-3 IS THE ONE THIS FEATURE IMPROVED, AND IT DID NOT MEAN TO.** Excerpt-only files — the
class no gate can verify — went from **thirteen to six**, three of them platform source.
Regenerating every Part-3 fence from the chapter's own two tags replaced excerpts with full
chained bodies wherever the diff had one. **Seven files left a class that had been stuck for four
features, as a side effect of a renumbering.** The count has been wrong four times out of five in
this project's history and every error was in parsing the title; this instrument declares four
title controls and fires them, which is why the number is trustworthy this time.

**043-1 IS NOT CLOSED, AND THIS WAS ITS BEST CHANCE.** The carry task says so in its own text: renumbering
touches every chapter, so the untitled fences "are as findable now as they will ever be". They
were findable and nobody titled them. **151 untitled against 830 titled**, 15.4% — the share fell
from 16.1% because the corpus grew from 904 fences to 981, and the absolute number ROSE by five.
This feature added untitled fences while holding the one opportunity to retire them.

**3.23-4 IS CLOSED IN BOTH TREES BY DIFFERENT MEANS, WHICH IS WORTH MORE THAN EITHER FIX.** On
`main`, 044 added `describe("the driver exemption list")` to `lists-agree.test.ts` — three `it`s,
one of which asserts the list "is reading a real list, a real rule, and a wired-in one". On the
rebuilt chain the same problem produced `driver-exempt.test.ts` and `drain-exempt.test.ts`, which
read the restricted module names **out of the rule** and assert both directions against the tree.
Neither knew about the other. **The chain's version is stronger and proved it: it found three of
published's six drain exemptions stale**, which a test asserting only "an unlisted file fails"
can never see.

**3.22-8 IS THE ONE THAT GOT MEASURABLY WORSE.** 044 recorded "six Python instruments … copied
from 043, which copied them from 042. They will be copied into 045 and drift there." They were,
and there are now **thirty-nine** files in this feature's directory. Two of them drifted exactly
as predicted — `check-refs.py`'s `FOREIGN` set and its docstring both arrived stale from 044's
copy, and the file says so in a comment. **The prediction was precise and nobody acted on it for
the eighth feature running; this is the ninth.**

**3.22-5's PREMISE MAY HAVE EXPIRED.** The item calls the retry-log bound "a five-module
decision"; four modules on `main` name it today. Whether a module left or the count was always
four needs the five identified by name, which the item does not give. **Filed as a premise to
check rather than as a number that moved** — checking a task's premise before executing it is the
third of this project's three mechanisms, and an item is a task.

**3.22-7 GOT ITS 045 INSTANCE, AND IT IS THE PLAINEST ONE YET.** The item is that coverage cannot
see an omission. This feature wrote `reset-lane.itest.ts`'s deliveries assertion, which **passed
against a no-op DELETE** — the row it was meant to prove had been removed was never planted, so
the assertion compared zero to zero. Fixed by planting the row and watching it go red first.
Coverage saw a green file both times.

**3.23-7 IS MEASURED, AND MY REASON FOR DEFERRING IT WAS A MISREADING.** I recorded it as needing
a coverage run and waiting on the battery. It needs no run: "the guard's coverage" in that title
means **which tables the guard reaches**, not line coverage, and the item's own body says so —
`db/catalogue.ts` classifies by `has_environment_id` then `via`, `message_edits` is a `hop`, and
no check asks whether a `hop` table is append-only. Four greps, no lane.

**OPEN, unchanged, and now measured rather than carried:**

    catalogue.ts:195-196   `direct` if has_environment_id, then `hop` if via.length > 0 —
                           the classifier is the one 3.23 left
    message_edits          still two links away, still a `hop` (catalogue.ts:135)
    the append-only claim  lives in TWO COMMENTS citing FR-004 —
                           `0009_message_edits.sql:25` and `schema.ts:421`, both saying
                           "Nothing updates or deletes a row here"
    enforcement            NO trigger, in any migration
    assertion              four integration suites name `message_edits` and not one
                           attempts an UPDATE or DELETE against it

**So the property is stated twice, enforced nowhere, and asserted nowhere** — which is a sharper
statement of the item than the one it carried, and it is the shape this project keeps finding: a
claim in a comment reads like a guarantee to everybody except the database. **Reading the item's
body rather than its title is what turned a blocked measurement into a four-grep one.**

**AND THE UNNUMBERED ONE, FOR THE FOURTEENTH FEATURE.** Use a person. This feature's own
instruments say it in their last lines — `check-movements: contiguity only — whether the ORDER
teaches anything needs a person` is a new instrument written this week whose closing sentence is
that it cannot answer the question the feature exists to answer. Eight contiguous movements are
measurable. Whether they teach anybody anything is not, and `reader-protocol.md` has been sitting
there since chapter 3.18.

## 045-68 · THE BATTERY IS 79% SLOWER BECAUSE THE CHAIN MUST SERIALISE A LANE THAT MAIN RUNS IN PARALLEL

SC-007 is a tripwire: 225.45 s ± 10%, and a moved duration means the platform changed when it was
not supposed to. Twenty runs at the rework tip measure **~404 s**, +79%. It tripped, and the cause
is not the platform.

**EVERY SIZE MEASURE POINTS THE OTHER WAY**, which is what made the number worth chasing rather
than explaining away:

    integration files in the battery   47 at 044's tree      46 at the rework tip
    static `it`/`test` calls           859                   832
    packages the battery runs          api gw disp harness   identical
    lane rows, outbox / messages       791,520 / 392,517     238,643 / 179,666

Fewer files, fewer cases, a third of the rows — and 179 s longer.

**`fileParallelism: false`, AND THE REBUILD PUT IT THERE.**

    rework tip    api ✓   gateway ✓   e2e ✓   test-harness ✓
    main          api ✗   gateway ✗   e2e ✓   test-harness ✗
    published 3.24 tip (8829881)      nowhere

The only two commits that ever add the string live on rework branches alone, dated 2026-09-08:
*"fix: what the outbox's new table and migration forced"*. Nine suites call `migrate(pool)` in
their own `beforeAll`; with a migration PENDING several issue `CREATE TYPE` against one schema at
once and Postgres answers `duplicate key value violates unique constraint
"pg_type_typname_nsp_index"` — an error about its own catalogue that reads like a driver fault.
Serialising the files closed it.

**THE COST, FROM THE RUN'S OWN LOG.** The gateway runs eleven files one at a time for 135.66 s
against a longest single file of 34.1 s; the api takes 174.04 s of which `consumer.itest.ts` is
101 s on its own — and 101 s is this project's recorded CLEAN-broker figure, so the broker is not
dirty. Parallel execution collapses each lane toward its longest file: **roughly 160–170 s of the
179 s gap.**

**AND IT IS LOAD-BEARING, WHICH IS THE PART THAT MAKES THIS 045-67 AGAIN.** The line cannot simply
be deleted, because the chain is at a pre-043 state and still holds the assertions parallel
execution breaks:

    chain    select count(*)::int as n from outbox
    main     select count(*)::int as n from outbox where subject like '%' || $1 || '%'

Main's version carries a comment naming the exact failure — *"`membership.itest.ts` sending a
message next door moved the number and the test reported `expected 614255 to be 614250`. Nothing
in that failure suggests a neighbour."* `limits.itest.ts`'s wall-clock minute bucket is the same
story. **Main runs in parallel because 043 scoped those assertions; the chain serialises because
it has not got 043 yet.**

**SO THE TWO NUMBERS ARE NOT THE SAME QUANTITY.** 225.45 s is a parallel lane with scoped
assertions; 404 s is a serial lane with global ones. The old rule was "no two batteries are
comparable"; 043 and 044 earned the newer one — "two batteries are comparable once the lane stops
colliding with itself". **This is the third case: a lane that is not colliding because it has been
forbidden to, which is comparable to nothing until the forbidding is lifted.**

**THE ORDER OF OPERATIONS.** Replay 043 and 044 onto the chain (045-67, ~22 commits) — the scoped
assertions arrive with them — then drop `fileParallelism: false` from api, gateway and
test-harness, then re-measure. Only then does SC-007 mean anything. **Measuring it before that
order is complete produces a number that trips a tripwire nobody can act on**, which is what this
battery did, and the twenty runs were still worth it: 20 of 20 green with a cv near 1% is the
evidence that the lane itself is sound.

## 045-69 · THE REORDER RENUMBERED THE MIGRATIONS, AND `schema_migrations` KEYS ON THE FILENAME

Found by trying to run the control for 045-68 — the same battery command on `main`, same machine,
same lane, to prove the serialisation is the whole of the 79%. It failed in 0.6 s, three times:

    error: relation "webhook_dead_letters" already exists     SQLSTATE 42P07
      ❯ migrate services/api/dist/db/migrate.js:37
      ❯ Object.globalSetup src/global-setup.ts:37

The lane's database was migrated by the rebuilt chain. `main`'s `migrate` read its own directory,
found a version string `schema_migrations` had never seen, and re-ran a migration whose tables
already exist. **Comparing the two migration sets by their SQL with comments stripped:**

    6   identical name and SQL          0000–0005, the Part-2 base
    7   RENUMBERED, SQL identical       webhooks        0006 → 0010
                                        attempts        0007 → 0011
                                        limit_policy    0008 → 0012
                                        quotas          0009 → 0013
                                        conn_minutes    0010 → 0014
                                        bot_users       0013 → 0008
                                        message_edits   0014 → 0009
    2   RE-PARTITIONED                  main's 0011_activity_and_read_positions +
                                        0012_member_roles_and_user_deletion  ↔  the chain's
                                        0006_member_roles + 0007_user_surface
    1   absent from the chain           0015_channel_revision_sequence — feature 044's

**THE SQL IS THE SAME. THE IDENTITY IS NOT.** No schema differs; seven files carry byte-identical
DDL under a different number, because a migration belongs to the chapter that introduces it and
seven chapters moved. That is correct behaviour for a series read from scratch and it is a
migration-ledger rewrite for anything already migrated.

**WHAT IT COSTS.** A database migrated in published order records `0006_webhooks.sql`. Handed the
rebuilt chain it is told to apply `0010_webhooks.sql` — and nine of them in turn, every one
failing on "already exists". **The re-partitioned pair is worse than the renames**: main's two
files and the chain's two files divide the same DDL differently, so there is no 1:1 rewrite of
`schema_migrations` rows that fixes it. This lane is the proof, and this lane is the easy case —
it can be dropped and recreated. A reader's cannot, and neither can a deployment's.

**THE CHAIN ALREADY DOCUMENTS THE PROBLEM FROM THE INSIDE.** `0010_webhooks.sql`'s own header:

> NUMBERED 0010 AND GENERATED AS 0006 … `drizzle-kit` numbers from its own snapshot count and
> this directory's snapshots stop at 0005 … `migrate.ts` reads the DIRECTORY and sorts by
> filename, so a 0006 here would run before the four migrations it must follow.

Somebody worked out the intra-chain numbering carefully and wrote it down. **Nobody asked what the
number means to a database that was migrated under the other order** — the same shape as this
project's oldest lesson: required is a claim about what you WRITE, and a reader of durable state
cannot be handed a new name for work it has already done.

**THIS IS THE SECOND HALF OF THE PUBLISH DECISION, AND IT IS HARDER THAN THE FIRST.** 045-67's
replay of 043 and 044 is twenty-two commits of mechanical work. This one needs a decision about
what a migration's identity IS, and the three options are not equally available:

    keep published numbering    BROKEN, and it is the option that looks safest. `migrate.ts`
                                sorts by FILENAME, so webhooks keeping `0006` while its chapter
                                sits at 19 applies it eleven chapters early for a reader
                                working through the book from scratch.
    rewrite schema_migrations   works for the seven pure renames; the re-partitioned pair
                                divides the same DDL across differently-named files, so there
                                is no 1:1 row mapping — only "mark all four applied", which is
                                sound because the schema is the union, and delicate.
    a fresh start               no existing database upgrades into the rebuilt series.

**DECIDED: THE FRESH START.** A reader working through the reworked series builds the database
from scratch, which is what a reader does; the only people inconvenienced are those who finished
the published Part 3 and want to continue, and they recreate a DEVELOPMENT database. The mapping
page carries the instruction, because that page is where a returning reader already goes to find
out what moved — the same page that tells them 21 of 26 numbers changed meaning.

**AND THE DECISION IS WHY THE 045-68 CONTROL STAYS UNMEASURED.** A fresh start means this lane's
database belongs to the rebuilt chain; measuring `main`'s battery against it would need a second
database, which is now a deliberate consequence rather than an obstacle.

**AND THE 045-68 CONTROL IS BLOCKED BY IT.** Measuring `main`'s battery needs a database migrated
in published order; measuring the chain's needs one migrated in subject order; the lane holds one
database. The 79% gap therefore rests on the config and assertion diffs — which are conclusive on
their own — and not on a same-day measured control. **Recorded as unmeasured rather than assumed
measured**, and the way to get it is a second database, not a second run.

## 045-70 · THE CHAIN REWRITE LANDED, AND IT FOUND SEVEN COMMITS THAT CLAIM WORK AND CONTAIN NONE

045-63 and 045-65 are **CLOSED in the chain.** `repair-base-refs.py` applies twelve exact-string
replacements extracted from `0317d83` itself, and `replay-publish.sh` replays the 225 commits
tree-by-tree applying only that. Result, on branch `part3-published`:

    ordinals in chapter trees      ch1 2 → 0    ch2 9 → 0    ch9 1 → 0
    remaining across all 26        4, and all four are 045-64's provenance continuations
    tip vs the old tip             ONE line — the doubled article of 045-65
    commits dropped                1, `0317d83`, empty once the convention is in the trees
    tags re-pointed                26 of 26, all ancestors of the new tip, 0 unmapped

**THE FIRST RUN DROPPED SEVEN COMMITS AND ITS RULE WAS WRONG.** The driver skipped any commit
whose repaired tree matched its parent's. Seven were skipped, none of them the convention commit,
all with substantive subjects — *"the last fixed ports, and the service that never reported the
one it bound"*, *"the fourth attack shape"*, *"a route that echoes its input has no
indistinguishable pair"*. Measured: **all seven change zero files and their trees already equal
their parents' in the ORIGINAL chain.** They were empty before this replay touched them.

    a tree-by-tree rebuild emits a commit even when its rewrite leaves nothing to commit

That is where they come from, and one of the seven says so in its own subject — *"the citation
commit this convention makes unnecessary"*. **Six do not**, and `git log` is read as the record of
what happened. They are preserved rather than swept, because they are somebody's record and not
this replay's business; the driver now drops only a commit that was non-empty BEFORE and is empty
AFTER, which is the convention commit and nothing else.

**AND MY OWN PATCH TABLE HAD A NO-OP IN IT, WHICH THE FIRST RUN ALSO REVEALED.** The
`credential-walk.mjs` entry was built by diffing `0317d83`'s pre- and post-images and then
applying the 045-65 correction to the post-image — which made `new` identical to `old`, because
that commit's ONLY change to that file was inserting the second "the". An entry whose replacement
equals its pre-image matches everywhere and changes nothing, so **the doubled article survived the
replay untouched and the tip diff was zero lines.** Found by asking why `0317d83` had not been
dropped when the whole point of the table was to empty it. The entry now runs the other way — it
finds the damage and removes it — and the table asserts no entry is a no-op before it runs.

**THE CARRY IS NOT A CHERRY-PICK SEQUENCE, AND THE FIRST CONFLICT SAID SO.** Feature 043's first
commit conflicts on three files, and in two of them **the chain already implements the same fix,
independently and better documented**: `packages/e2e/src/harness.ts` reads the port out of the
child's own `listening` line, and `services/gateway/src/main.ts` logs `server.address()` rather
than the port it asked for. Resolving those in favour of the incoming commit would DOWNGRADE the
chain. Audited by what each commit creates rather than by how many of its lines already appear:

    likely PRESENT   1   the lane reset with a real guard — both new files are in the chain,
                         because the rebuild built them
    clearly ABSENT   6   the teardown assertion, the retired generator, the message-length
                         maximum, the scale harness, the revision counter, the ack's report
    needs a reading 17   modification-only; no new file or symbol to test for

**A CARRIED COMMIT IS A CARRIED LEDGER ITEM.** Measure it against the tree, do not copy it — the
same rule the carry task applies to gaps entries, and the same failure mode: the overlap percentages said
27% and 36% and meant almost nothing, because most of what two versions of a fix share is braces
and prose.

## 045-64's FIX, AND WHAT IT COST TO GET THE BOUNDARY RIGHT

`refrules.deliberate_lines()` covers a deliberate tag's comment PARAGRAPH — the entry's line plus
every following comment line until a bare `//`, a rule line, or the first non-comment line. Not the
comment block, which would exempt a genuine ordinal sitting further down the same comment; not three
more entries in the set, which would fix these two tags and nothing about the next one somebody
writes. `check-fence-ordinals.py` now runs two passes, because **a paragraph is not visible from one
line** and the first pass is what builds the spans.

    before the chain rewrite    38 ordinals in 12 files
    after regenerating fences   12 in 4 — every one a tag continuation
    after the paragraph span     0 in 0, 28 lines kept on purpose in 4 files, exit 0

**RED-TESTED BOTH WAYS, AND THE FIRST PROBE WAS WRONG.** I inserted `chapter 3.11` after the tag's
last sentence and the checker stayed green — which looked like a hole and was the design: that line
is still inside the tag's paragraph, because the paragraph ends at the rule line BELOW it. Inserting
past the rule line is caught, exit 1, one ordinal in one file. **A probe that lands inside the
exemption tests the exemption, not the boundary**, and the difference is one line of the file.
`deliberate_controls()` asserts the span is the tag's three lines and not the seven-line block, and
runs on every invocation.

## 045-71 · THE TWO FENCE CHECKERS CANNOT BOTH BE SATISFIED BY EDITING A BODY, AND ONE OF THEM IS THE ARTIFACT

`check-chapter.py` verifies a fence against the diff between the chapter's own two tags.
`check-fence-chain.mjs` verifies it against the cumulative replay of every fence from Part 1.
**Where those two states differ, no fence body satisfies both** — and the difference is not
hypothetical, it is 68 of this feature's remaining fence problems.

**I BUILT THE REPLAY-SOURCED GENERATOR AND IT MADE THE ARTIFACT WRONG.** CLAUDE.md's rule 1a says
to generate hunks from the checker's own replay — copy `check-fence-chain.mjs`, make it dump its
state, generate from that. Done: `regen-from-replay.py`, eleven fences regenerated from the
predecessor state the chain actually holds.

    check-fence-chain    APPLY 137 → 132     the chain went greener
    check-chapter        0 → 4, 4, 2, 1      chapters 22, 23, 24 and 25 went RED

Every new pre-image was absent from the chapter's real starting tree, so a reader typing along
would find nothing to match. **Green instrument, false artifact**, and the eleven were reverted to
tag-correct bodies. Rule 1a is right about generating hunks the CHAIN will accept; it does not say
that accepting them is worth a fence a reader cannot apply, and this is the case where those
diverge.

**WHY THE STATES DIVERGE, WHICH IS THE FINDING UNDER THE FINDING.** The chain replays only what it
can see: a fence with a `title="…"`. Content that reaches a file through an untitled fence, an
excerpt-only file, or no fence at all never enters the replayed state — so the state the chain
holds at chapter N is the real tree minus everything invisible to it. **The remaining APPLY
failures are not fence-body bugs; they are 043-1's 151 untitled fences, measured from the other
end.** Editing bodies to accommodate that is repairing the symptom into the published text.

**THE DECOMPOSITION, RE-MEASURED** (045-66's numbers were taken before the chain rewrite):

                            vs main    vs the rework tip
    HEAD  en chapters          137                   36
    HEAD  post-series.md        19                   24
    APPLY post-series.md        55                   55
    APPLY en chapters           34                   34
    APPLY vi chapters           34                   34
                            ───────    ─────────────────
                                279                  183

**101 of the 279 are "main is not the rebuilt history"** and go when the publish decision lands.
**79 are the appendix**, unchanged either way, and no task in this feature touches it. **68 are the
untitled-fence divergence**, mirrored across two locales, and the honest repair is upstream —
title the fences that carry content — not downstream in the bodies that fail because of them.
**Seven were fences describing changes the reorder had already made elsewhere**, and those are
gone: chapter 10's five citation-only edits, chapter 7's provenance tag, chapter 25's assertion.

**AND `check-chapter` IS THE ONE TO KEEP GREEN.** It tests the property a reader depends on — this
chapter's diff applies to this chapter's starting point. The chain tests a property the *book*
depends on, and it is currently measuring its own blind spot as well as the text. Both are worth
having; when they disagree, the artifact wins.

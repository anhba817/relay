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

## 045-11 · NEW 3 PORTED THE TYPED THROWER AND DROPPED TWO OF ITS THREE HUNKS

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

## 045-12 · THE REWORK TREE HAS NO LANE RESET, SO ITS BROKER ACCUMULATES AND ONE SUITE HANGS

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

## 045-13 · A DOCUMENTED CODE WITH NO PRODUCER, AND THE GATE THAT COUNTS CANNOT SEE IT

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

## 045-20 · A HELPER ARRIVED THIRTEEN CHAPTERS BEFORE THE FIELD IT STRIPS, AND ITS DOCBLOCK SAYS OTHERWISE

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

## 045-25 · THE CHECK AGAINST AN UNINJECTED MODULE COULD NOT SEE A MODULE BUILT WITHOUT OPTIONS

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

# Chapter 3.18 — the plan against what shipped

*Written as the work happens, not at the end. Sections are filled by the tasks that
name them; anything still angle-bracketed has not been done.*

## What shipped

    3.18 "the message that never arrived"     9 files taught, 2,836 words, 36 fences
                                              19 files changed, re-derived from git diff
                                              4 figures, 2 locales, reader minutes 70

    607 integration tests across 41 files (3.17: 589 across 40)
    20 of 22 full-lane runs green, mean 194.74 s, stdev 1.49, budget 240
    the sealed outsider 11 of 11 through the README's own procedure

    36 titled fences: 20 excerpt-or-prose, 12 diff, 4 whole-file
    216 fenced files across 35 chapters, 35 translated, fences mirrored

    coverage  services/api/src/fanout/publisher.ts    100 / 100 / 100 / 100
              packages/protocol/src/fanout.ts         100 / 100 / 100 / 100
              statements 2360/2572 — 3.17 closed at 2552, so this adds 20
              expand.ts's pin needs the dispatcher container stopped: gaps.md item 7

    NO SRS CLAUSE CHANGED. Principle VI satisfied by citing FR-RTM-01.
    docs/05-sad.md amended (it disagreed with itself), docs/06-adr-deep-dives.md
    amended (ADR-07's exception, dated to 3.8), docs/07-tutorial-plan.md corrected
    (the row cited FR-RTM-05 from 3.14 to 3.18, and a publisher claim at :215).

    traceability.md  134 lines, both directions. Running it the second way found
                     FR-007 — a MUST — with no test at all. Written, and proven red.
    gaps.md          8 items, each with an owner. Item 6 is T058, not closed.
    FR-013 / SC-006  pinned as UNMET rather than narrowed until they passed.

## The two file counts (T042)

    9    what the chapter TEACHES     -> drove the word estimate
    19   what the chapter must FENCE  -> drives the chain
    19   files changed, re-derived from `git diff 8166941..HEAD` at the end

Kept in two columns from `plan.md` to here, and **neither number was ever asked to do the
other's job**. The taught column is the nine files a reader follows; the fenced column is
every platform path whose end state this chapter is now responsible for.

**THE RE-DERIVATION DISAGREED WITH THE PREDICTION, AND THAT IS THE POINT.** `plan.md`'s
column — itself rebuilt in analysis pass 11 after the pre-task version missed five files —
predicted 17. `git diff` says 19. The difference:

    NOT PREDICTED, CHANGED   services/api/src/auth/principal.ts
                             services/api/src/request-context.middleware.ts
    PREDICTED, NOT CHANGED   (none — isolation.itest.ts was predicted and DID change,
                             once T025a was noticed)

The two unpredicted files are the request-id plumbing. Analysis pass 6 found that
NFR-OBS-01 wants a request id in every structured line, and the publish logs from inside a
handler — but nobody traced that requirement to the files it would touch. The id existed
only as a generated local and a response header; a handler could not read it. One line in
the middleware and one field on an interface, invisible until something needed them.

**And the reconciliation caught a missed task.** `isolation.itest.ts` was in the column and
showed no diff, which is how T025a — retire the comments this feature falsifies — was found
unstarted after Phase 3 had been marked complete. A count that only ever agrees with itself
would not have said so.

## The word estimate (T043)

`plan.md` estimated **2,650–3,350** from six arguments, after analysis pass 7 cut two of the
eight that had accumulated. The chapter is written against that and measured at close-out
by T052a, which counts rather than estimates and re-counts 3.15, 3.16 and 3.17 with the
same instrument — because the figures those chapters recorded came from a tool that no
longer exists.

## The grammar could not move verbatim (T004, T007)

`plan.md` and T004 both said the subject grammar moves **verbatim**. It could not: the
package already exports a `subjectFor` — `internal.ts:112`, the event spine's
`(type, environmentId)` — and TypeScript refused the second one.

    src/index.ts(12,1): error TS2308: Module "./internal.js" has already exported
    a member named 'subjectFor'.

The spine's name is chapter 3.4's, published and fenced, so the new one moved:
**`subjectForChannel(channelId)`**. Nineteen analysis passes read both files and neither
noticed the collision; the compiler found it in four seconds.

It is also the same asymmetry pass 6 found and T044b records — the spine's subject carries
the tenant, the fan-out's carries only a channel id. Putting them in one package is what
made it a compile error instead of a paragraph.

## T014a — session.itest.ts stays outside the fence chain

**Decided: `(excerpt)` in the chapter; the file does not join the chain.**

It is fenced by no chapter today, which puts it with `sentinel.ts`, `sentinel.sql` and
`guard.itest.ts` in `gaps.md` item 7 — files the chain never verifies. This chapter adds a
third describe block to it (T014) and will put its end-to-end delivery test there (T022),
so the question had to be answered rather than discovered at close-out.

Three options were real:

    titled fence          the chapter carries the whole file — now 582 lines, of which
                          ~150 are this chapter's. A tutorial does not print 582 lines of
                          test harness, and a titled fence binds every later chapter that
                          edits the file.
    a new file            services/gateway/src/rest-delivery.itest.ts, ~150 lines and
                          fenceable. Rejected: the expensive part is `startApi`, which
                          SPAWNS the api from dist/main.js, and a second file either
                          duplicates it or needs a shared harness module that would itself
                          be unfenced. The cure has the disease.
    (excerpt) + no chain  CHOSEN. The chapter shows the new describe block, the reader sees
                          the test that proves the claim, and the chain does not silently
                          grow by 600 lines no chapter teaches.

The cost, stated plainly: **the chapter's end-to-end test is not verified against the
repository by `check:fences`.** That is one more file in item 7's set and it is recorded
there, not left implicit.

## An existing test's title over-promises (found while writing T014)

`session.itest.ts`'s first delivery test is titled *"opens for a token the api minted, and
knows the user's channels"* and asserts only `payload.user`. Its type annotation declares
`channels?: string[]` on the ack payload — a field `connectionAckSchema` does not have
(`{ user, cursor, resume_ok, truncated }`). The first version of T014's test read that
field and got an empty array.

Not this chapter's to fix, and worth knowing: the gateway learns the channel list from
`POST /internal/session` and never tells the client. A test whose title promises more than
it checks is how the annotation survived.

## The lint rule that nineteen analysis passes missed

`pnpm lint` failed the moment the publisher existed:

    'ioredis' import is restricted from being used. The counter store lives in
    services/api/src/limits and services/gateway/src/limits.ts only
    (constitution I, chapter 3.8). Its keys are per environment; an
    unrestricted client is a cross-tenant read.

**Nineteen analysis passes read `eslint.config.mjs` twice — pass 4 for appendix ownership,
pass 11 for the fence column — and neither noticed that the file this feature adds could
not import the driver it is built on.** The rule cites constitution I, which is the
NON-NEGOTIABLE principle, so this was not a style nit.

Two exemptions added, each with the reason the doctrine demands (`a LIST WITH REASONS, not
a directory pattern`):

    services/api/src/fanout/**            product code. The rule's reason is that counters
                                          are keyed `rl:{environment_id}:…`, so a loose
                                          client can read another tenant's. This client
                                          touches no keys — PUBLISH onto `chan:{uuid}`, and
                                          a subject is not readable at all.
    .../fanout/fanout.itest.ts            the two limits suites' argument exactly: the
                                          subject is what reaches the fabric, and only a
                                          subscriber using neither service's code can see it.

**And it grows the fence column again.** `eslint.config.mjs` was not in `plan.md`'s
sixteen-file table, and it is appendix-owned — `fences/post-series.md` holds a hunk
anchored just after the `services/gateway/src/fanout.ts` line this change sits beside.
Chapter 3.17 hit that same collision. Recorded for T047/T050.

## T030 — SC-002 is a composition, and no fixture does both halves

**Stated because the pair of suites would otherwise imply more than either proves.**

    services/gateway/src/resume.itest.ts     TWO gateway instances, real sockets, one
                                            fabric — and a STUBBED api. Three tests:
                                            the member's instance receives, the
                                            bystander's does not, and a channel neither
                                            holds reaches neither.
    services/gateway/src/session.itest.ts    a REAL api spawned from dist/main.js, a real
                                            socket, a real POST — and ONE gateway.

So "a REST send from a real api reaches a socket on another instance" is assembled from
two measurements rather than taken in one. The gateway has no database (ADR-05), which is
why its suites stub the api; giving `resume.itest.ts` a real one means giving it a Postgres
handle and the fixture stops being about the fabric.

**What makes the composition sound rather than convenient**: the api publishes to
`chan:{id}` and nothing else (asserted in `services/api/src/fanout/fanout.itest.ts`, on a
real subscriber), and an instance holding a member of that channel delivers while one that
does not stays silent (asserted here, on real sockets). The join is the subject string, and
it is one function in `@relay/protocol` with its own test.

**What would close it properly**: a fixture that spawns an api and two gateways. That is
the same shared-harness feature `gaps.md` item 2 wants for `session.itest.ts`, and it is
not this chapter's.

## The largest risk resolved as a gap, not as a pass (T031-T034)

`plan.md` named FR-RTM-10 the chapter's largest open risk and said: *"If neither path meets
FR-RTM-10, the outcome is a recorded gap and a sentence in the chapter, not a quiet claim."*
Neither path meets it. `gaps.md` item 4 has the measurement and the mechanism.

The chapter has to say this, and the honest framing is narrow: **this chapter did not break
FR-RTM-10 and does not fix it.** It adds a second door onto a room whose lock was already
missing. What it does contribute is the measurement — nobody had run it before, and the
clause has been P1 since v1.

## T044b — the subject grammars' asymmetry, and a deviation from where it was to go

    events.msg.created.{environment_id}     the spine   — carries the tenant
    chan:{channel_id}                       the fan-out — carries a channel

Defensible: a channel id is a UUID, and an instance subscribes only to channels a
tenant-scoped session named at connect. Nothing leaks. But the two grammars now sit in one
package, so a reader meets both signatures at once and neither states the difference.

**T044b said to record this in chapter-notes and NOT in the chapter**, on analysis pass 7's
reasoning that it was a sidebar and the word budget was tight. It is in the chapter as well,
and the reason it changed is that the implementation changed what kind of thing it is:

    src/index.ts(12,1): error TS2308: Module "./internal.js" has already exported a
    member named 'subjectFor'.

Pass 7 was cutting a speculative aside. What actually happened is that the two grammars
could not share a name, the compiler said so, and the rename to `subjectForChannel` is a
line of the chapter's own narrative — the grammar-move section has to explain the name
regardless. Two sentences of asymmetry attached to a compile error costs less than a
paragraph of sidebar, and it lands where a reader is already looking.

Recorded as a deviation rather than done quietly, because "the plan said elsewhere" is
exactly the kind of thing a close-out should not have to reconstruct.

## The fence chain took five wrong answers, same as 3.17 (T050, T051)

`check:fences` went from **16 problems to 0**, and every step of the descent was the checker
naming a file and a line. Recorded because 3.17 reported exactly five and the shapes repeat.

    16  the starting state. Three of my own fence titles named no file and were read as
        paths — a title that is a prose label needs `(excerpt)`, which is the same
        `NOT_A_FILE` hatch that keeps `gaps.md` item 7's files out of the chain.
        Thirteen files were [HEAD]-drifted: their last titled fence no longer matched
        the repository.

     4  after ten `diff` fences went into the chapter. The mechanism, read in
        `check-fence-chain.mjs` rather than guessed: `lang === "diff"` AMENDS by hunk,
        any other lang RESTATES the whole file, and a `post-series.md` fence "must be a
        diff — a post-series fence amends, it never restates". Ten hunked diffs of ~500
        lines total, against printing ten whole files.

     3  after the Vietnamese twin got the same fence list. [MIRROR] is a LIST check:
        the two locales must carry the same titles in the same order, and adding a fence
        to one locale alone is an error in its own right.

     1  after `eslint.config.mjs` came OUT of the chapter. A chapter fence for it gave
        `hunk pre-image matched 0 times` — that file's exemption list is appendix
        territory, and CLAUDE.md's lesson 3 is exactly this: a chapter cannot do the
        appendix's work. The change moved to `fences/post-series.md`.

     1  still, at line 83 — and this one is the instructive one. My entry was in the
        appendix, in the right fence, with correct hunk headers. It was in the WRONG
        ORDER: the repository has it before `history.itest.ts` because Phase 2 anchored
        on `backfill.itest.ts`, and the appendix had it after. Same content, and the
        replay diverges at the first line where the sequence differs.

     0  after the second eslint change — the `ignores` entry — went into the fence that
        owns that region. Three appendix fences touch `eslint.config.mjs`; the one that
        matters is the one whose hunk covers the lines you are changing, and finding it
        meant grepping for the anchor rather than assuming the last fence wins.

**212 fenced files across 35 chapters, 35 translated, fences mirrored.**

The generalisable part: **every one of the five was diagnosed from the checker's own output**,
which names the file, the line, and both sides of the mismatch. None needed reasoning about
the chain. The one that took longest — the ordering — is the one whose two sides looked
identical until you read them as sequences instead of sets.

## The prose sweep, and the two sites the class list did not name (T056a)

Twelve phrases over `app/(en)/**/page.mdx`, `app/(vi)/**/page.mdx` and the parent's `docs/`.
Eight from FR-018's own list — *"reaches no socket"*, *"no live socket"*, *"does not reach"*,
*"never arrives"*, *"cannot succeed"*, *"the gateway publishes"*, *"instance that handled"*,
*"only publisher"* — and four architectural: *"clean mapping"*, *"gateway to Redis"*,
*"publish once per message"*, *"two broker clients"*.

    phrase                      en   vi   docs        phrase                     en   vi   docs
    reaches no socket            5    4     0         clean mapping               1    0     1
    no live socket               1    0     0         gateway to Redis            1    0     1
    does not reach               3    2     1         publish once per message    0    0     1
    never arrives                2    0     0         two broker clients          1    0     2
    cannot succeed               3    0     1
    the gateway publishes        2    2     1
    instance that handled        2    2     0
    only publisher               1    1     0

**FR-018's four classes are all corrected, both locales.** 3.13's Trap now reads *"A message
sent over REST reached no socket — closed in 3.17 and 3.18"*, past tense, and its twin carries
`đã không tới được socket — đóng lại ở 3.17 và 3.18`. 3.16's closing paragraph names 3.18 and
cites FR-RTM-01 in both. The outsider test records its own old title at
`integrate.itest.ts:247`. Every remaining hit in 3.17 is an attributed record — *"Chương 3.12
ghi lại rằng…"* — or a `<ForwardRef>` that names 3.18.

**Two sites were defects, and neither was on the list.**

`part-3/chapter-14`'s closing `<ForwardRef>` read *"a REST-sent message reaches no socket and
FR-RTM-05's chapter owns the choice"* — present tense, no chapter named, and the FR-RTM-05
misattribution FR-001 corrects to FR-RTM-01. FR-018 named 3.16's closing paragraph and
explicitly exempted *"3.14's verdict"* as a gap record. This is a third thing in 3.14: not the
verdict, and not the paragraph the class list named. Corrected in both locales to *"chapter
3.18 owns the publish — FR-RTM-01, not FR-RTM-05"*, following 3.16's precedent.

`docs/07-tutorial-plan.md:215` read *"the gateway publishes to the fabric after the api has
committed"* — the same defect as `docs/05-sad.md:254`, which stated the ordering
unconditionally for three analysis passes, in a different file. Now qualified by transport:
the gateway's publish for a socket send, the api's own for a REST send. The passage still says
*"four instances of one seam"* and there is now a fifth; the enumeration was left alone.

`docs/07-tutorial-plan.md:167` is still *(planned)* and still cites FR-RTM-05. That is T061's,
and the sweep confirms it open.

**An English phrase list cannot sweep a Vietnamese chapter.** The eight FR-018 phrases score 4
hits in `(vi)`, all in code-adjacent text, and 0 in vi prose making the claims that matter.
Six Vietnamese phrasings were needed to sweep the twin at all — `không tới được socket`,
`không bao giờ tới`, `không có gì publish`, `chỉ gateway`, `instance xử lý`,
`chỉ có gateway` — and they are what confirmed 3.13's and 3.16's twins were corrected. A
mirrored corpus needs a mirrored word list; this is the same failure as a checker whose
pattern matches the examples in front of it.

## Chapter 3.14's Phase 2 verdict, re-examined (T060, FR-016)

3.14 recorded the SRS Phase 2 exit criterion — *an external developer integrates using only
public documentation, with no assistance* — as **met in part, with the missing part named**.
Two things were not met, and 3.12's `gaps.md` says they *"are different in kind"*.

    G1: REST send, socket receive, cannot succeed        MET as of this chapter
    comprehensibility is not content sufficiency         NOT MET, and no test reaches it

**The first is now met, on the condition that paragraph itself set.** It read *"until the
platform delivers a REST-sent message or the documentation says it does not, the criterion is
not met for that path"* — two ways out, and this chapter took the first. The sealed outsider's
REST-send / socket-receive test passes with no correction to the suite, which is what the
criterion actually asks: 3.12's suite passed only because a failing test had corrected it,
*"precisely the assistance the criterion forbids"*.

**The second is untouched, and this is the fifth chapter to say so.** 3.14, 3.15, 3.16 and
3.17 each named it; so does this one. Every check in this repository compares bytes, and none
of them can tell whether a chapter is comprehensible to somebody who has not read the plan
that produced it. See T058 — it is recorded there with an owner and a protocol rather than as
an aspiration, which is the only thing that has changed about it in five chapters.

## T058 — use a person: NOT CLOSED, for the fifth time

Chapters 3.14, 3.15, 3.16 and 3.17 each named this and none closed it. Neither did this one,
and the task is left unchecked rather than reported done.

The reason it keeps not happening is that it is the only task in the cycle that no command can
discharge. Everything else here ends in an exit code. This ends in somebody saying "I could not
tell from the chapter why the api publishes instead of the gateway", and there is no way to
fake that from inside the loop that wrote the chapter.

What changed: `reader-protocol.md`. Six questions, the expected answers, the two that carry the
most weight (FR-RTM-01 against a reader arriving from 3.17 expecting an SRS amendment; and a
201 with Redis down whose only evidence is a log line), a 45-minute box, and a place to write
down what the reader could not answer. It is `gaps.md` item 6 with the author's name on it.

Whether that is progress or a more elaborate way of deferring is a fair question. The honest
answer is that four sentences of intent produced nothing four times, and this is the first
version somebody could actually be handed.

## Decisions recorded during the work

Each of these is written into the source or a section above, not only here.

**T009c — no off-switch, and that is a decision.** Four api modules carry one
(`RELAY_OUTBOX_RELAY` and its three siblings) and CI sets them off because *"a background
daemon draining the table two suites are asserting on is a race between test files, not a
property"*. Every one of those is a daemon polling shared state; this is a synchronous
publish to `chan:{uuid}` that a suite which did not create the channel cannot observe. The
stronger reason is in `publisher.ts:30`: **a switch would let the lane run green with the
publish disabled, which is the false-green shape the whole feature exists to remove.**

**The DI token lives beside the interface, not in the module.** A controller importing it
from the module closes an import loop, and Nest reports it as a missing dependency rather
than as a cycle — *"Nest can't resolve dependencies of the MessagesController
(MessagesService, Repository, ?)"*. Recorded at `publisher.ts:33` because the error message
does not name the cause.

**T014a — `session.itest.ts` stays outside the fence chain**, and the new delivery block is a
third `describe` rather than a fourth argument to the existing ones, so suites that want no
broker keep none. `isolation.itest.ts` records the same decision from the other side.

**T030 — SC-002 is a composition** and no fixture did both halves; `resume.itest.ts` got the
delivery half because it is the suite that already runs two instances on one Redis.

**T044b — the subject grammars are asymmetric** and the deviation is recorded rather than
smoothed: `subjectForChannel` in `@relay/protocol`, while the gateway's event-subject helper
stays where it is. The rename was forced — `internal.ts:112` already exports `subjectFor`,
and `index.ts` would not compile (`TS2308`).

## The phases that went badly

**Phase 2 — T003 failed twice for reasons that were not the feature.** First a 400 because an
application credential may only send as a bot (chapter 3.17's rule, working). Then a second
400 because the REST route types `idempotency_key` as `z.string().uuid()` while the socket
frame takes any string — `gaps.md` item 1, found by a test that was trying to do something
else.

**Phase 2 also committed against a database that was not idempotent from cold volumes.**
After `docker compose down -v` the first lane run failed all 16 dispatcher tests and the
second and third were green. Five hypotheses were eliminated before the sixth: service
containers, 149 Mailpit messages, my own code via `git stash`, the ports, the demo seed.
`gaps.md` item 3, deliberately unfixed.

**Phase 3 was marked complete with T025a unstarted.** The file-count reconciliation caught it:
`isolation.itest.ts` was in the fenced column and showed no diff. A count that only agrees
with itself would not have said so.

**Phase 4's timeouts were `afterEach`, not the tests.** `server.close()` waits for open
connections and the tests never closed their sockets. The failure looked like the feature and
was the fixture.

**Phase 7 — the fence chain went 16 → 0 through five wrong answers**, the same count as 3.17:
prose titles read as paths, whole-file versus `diff` fences, `[MIRROR]` being a list check
rather than a content one, `eslint.config.mjs` turning out to be appendix territory
(`hunk pre-image matched 0 times`), and finally **ordering** — the right entry in the right
appendix fence, placed after `history.itest.ts` where the repository has it before.

**And my own instruments failed about thirteen times, in one shape**: a pattern matching the
examples in front of me rather than the set the rule names. The `[P]` collision check omitted
a file class; a `grep -rl` read `dist/*.js`; a `--verbose` parse gave 194 for 212; a lookahead
for `16379` matched a port nothing uses; an awk matched a cross-reference; and one pass-5
remediation silently did not apply, which the count caught by reading 73 where 74 was due.
`gaps.md` item 5's section was in the file **twice**, verbatim, until T061 read it.

## The fence chain reads the working tree, not git (T063)

**460 lines of chapter 3.18 were never committed, and every gate was green the whole time.**

The chapter's four closing whole-file fences — `protocol/fanout.ts`,
`protocol/fanout.test.ts`, `fanout/publisher.ts`, `fanout/publisher.test.ts` — and their
prose were written while landing the fence chain in Phase 7, *after* `9d20932` had already
committed the chapter. `pnpm check:fences` reported 216 fenced files and mirrored locales
against a working tree that git did not have.

It surfaced at the close-out commit, from a line count that did not add up: 472 insertions on
a page where 56 were due. The four fences show up in a marker-sequence diff as an append,
which is what sent me looking.

Nothing was lost, and that is luck rather than process. 3.12 destroyed uncommitted work twice
with `git checkout`, and the rule written down after it — **commit each phase** — is about
exactly this window. The rule held for the platform, whose close-out commit is 90 lines and
all of them mine; it did not hold for the tutorial, because Phase 7's commit came before
Phase 7's last edits.

The check that would have caught it is one line, and it belongs at the end of every phase:

    git status --short        # in every repository, not just the one being edited

## What the next feature should do differently

**Build the traceability map both ways in the PLANNING phase, not at close-out.** Running it
the second way here found FR-007 — a MUST — with no test at all, at T058a, after eight phases
and nineteen analysis passes had all read `requirement -> test` and believed it. The map cost
an hour and found something nineteen passes of reading did not. It belongs before the tests
are written, where its answer changes what gets built.

**Stop the compose app containers before ANY lane, coverage included.** `baseline.txt` said it
for `test:integration` and not for `pnpm coverage`, and a live `relay-dispatcher-1` moved a
pin on a file this feature never touched — half an hour spent proving innocence. The symptom
was not a failing test. It was a percentage.

**A phrase sweep needs one word list per locale.** Eight English phrases scored zero against
the Vietnamese prose making the claims they were written to find. Six Vietnamese phrasings
found them. A mirrored corpus needs a mirrored instrument, which is the checker lesson one
level up.

**When a requirement enumerates a class, check the class rather than the enumeration.**
FR-018 listed four classes of stale published claim and named the chapters they were in. Two
defects sat outside the list — 3.14's closing `<ForwardRef>`, which the clause explicitly
exempted as *"3.14's verdict"* when it is a third thing in that chapter, and a second file
carrying `05-sad.md:254`'s exact defect. The sweep found both in five minutes; the list had
had nineteen passes.

**And run the reader protocol.** It is written now (`reader-protocol.md`, `gaps.md` item 6).
Five chapters have named this gap. The sixth should be the one that hands the document to
somebody.

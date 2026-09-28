# gaps.md — feature 060, chapter 4.14 "Pending, ready, rejected"

**16 entries: 10 new, 6 carried and re-measured.** Every carried item was re-measured rather
than copied; four of 043's twenty-three were wrong when somebody finally checked, and three had
closed with nobody working on them.

---

## New

**060-1 · The first sentence of FR-MED-07 was unmet and no artifact said so.**
Three chapters cited this clause for the event it names and recorded the state machine as the
gap. The sentence before it — *"real-time and history delivery shall include each attachment's
state"* — had nowhere to put a state: `attachmentSchema`'s media arm was `{ type, media_id }` on
every door. **CLOSED** by `deliveredAttachmentSchema` and SRS 1.21.

**060-2 · One schema was serving a door that must refuse a state and a payload that must always
carry one.** `attachmentSchema` is embedded by `messages.schema.ts:40`, `messageSendSchema`,
`internal.ts:35` — and `messageSchema` at `frames.ts:46`, which is what the api BUILDS. **CLOSED**
by a third shape. The file already argued the same split for a different field at `frames.ts:89`.

**060-3 · Three hand lists of doors, all wrong.** The spec named three; analysis pass 2 replaced
that with six; `tsc` named two, plus one it is structurally unable to see because that handler's
return type is inferred. **CLOSED** by deriving the set and pinning it in `doors.txt`, and by
FR-003 deleting its own list. The general form is in CLAUDE.md already and this is its fourth
instance in five features.

**060-4 · Reusing a subject means reusing its publisher, which research priced at zero.**
`publishRevision` derived its subject from `revision.message.channel`. Eight production sites
across two services reached through `.message` for the subject, the routing key or a log field;
five more in tests, including a HARNESS that would have left every downstream test unable to
exercise the media path while staying green. **CLOSED** by `channelOfRevision` in the module that
owns the grammar, with an exhaustive `switch`.

**060-5 · The verdict seam had four things missing and none of them was the producer.** No
tenant (`recordMediaVerdict` returned none, and a worker's principal carries none by design), no
publisher (`MessagesModule` withholds the token), a publisher that assumed one arm shape, and no
lifecycle for the second Redis client. **CLOSED**. The second is invisible to lint, typecheck and
every unit test — `Nest can't resolve dependencies` on the first request, which is 4.10's finding.

**060-6 · Five places count frames, and all five fired.** The protocol union's own length; the
gateway's advertised vocabulary; `isolation.itest.ts`'s derived count; its classified-exactly-once
check; and `session.itest.ts`'s non-inbound refusal loop. **CLOSED** — every count updated with
its reason. The last two are not counts for their own sake: a server-to-client frame with no
DIRECTIONS entry is one a client could forge.

**060-7 · And the forged-sample trap fired for the third time in the same file.**
`session.itest.ts` carries its own sample builder, deliberately not shared, whose comment records
paying this bill twice before: a frame whose sample is malformed is refused `invalid_frame` — the
phase *before* the direction check the loop exists for. A new frame does it by having no case.
**CLOSED**; the comment now records the third.

**060-8 · `echo "EXIT=$?"` after a pipeline reads `sed`'s status. Fifth time.**
`pnpm coverage 2>&1 | sed … > f; echo "EXIT=$?"` printed EXIT=0 on a run that had failed a
threshold. **CLOSED** for this feature by re-running without the pipe; the class is CLAUDE.md's
and this is the fifth occurrence, committed in the same session that quotes the rule.

**060-9 · A statement that no test can reach, and a pin that is not the branch pin's problem.**
`media.controller.ts` statements 92.59 against 93. One statement is the `ready`/`rejected` guard
the per-arm probe proved unreachable. **CLOSED** at 92 with the reason in the config — and
explicitly distinguished from the branch pin two lines above it, which is a denominator that
differs between machines (059-20). Both present as a red pin.

**060-10 · A rolling deploy drops transitions on un-upgraded gateways.**
`revisionFabricSchema.safeParse` refuses an unknown arm and `fanout.ts` logs the subject, not the
reason. **OPEN by decision, not by oversight.** FR-009's floor repairs it on the client's next
read, which is the argument for having a floor. Recorded in the chapter and in T039b rather than
left for somebody to report as a bug. Closing it would need a version negotiation this platform
has deliberately never built.

---

## Carried, re-measured

**055-3 · `check:errors` still has no CI job.** Re-measured: five `check:*` scripts, four steps
in `ci.yml`, zero running that one. Run by hand in both directions this feature — **34 codes, 34
sections, 6 close codes** — which is the only reason a discrepancy would have been caught. This
chapter adds no code and the figure is unchanged. **STILL OPEN.**

**059-20 · `media.controller.ts`'s branch denominator differs between machines.** Not
re-measurable from here (see 060-11). The pin stays at 83 and this feature added a statements
figure beside it that is a different kind of number, said so in the config.

**043 · The wall-clock minute bucket.** Untouched by this chapter; `limits/bucket.ts` is still a
fixed 60-second window and 4.13's `pinWindow` is still the mitigation rather than the fix.
**STILL OPEN.**

**059-11 · `media_events` has no producer.** Unchanged and still correct to defer: DR-17's sum
reads `uploaded` and `deleted`, and `deleted` arrives with FR-MED-10 in the erasure chapter,
which can then build producer and consumer together — the lesson 4.6 paid for.

**050-8 · Two test files spawning an ingester is not a deployment.** Unchanged.

**060-11 · CI is not visible from this machine, so three tasks could not run.**
`gh run list -R anhba817/relay-platform` returns empty on every branch; `gh` is authenticated as
a different account. T007's opening error set was never taken, so T079's per-error comparison and
T080's is-it-ours triage have nothing to compare against. **OPEN**, and recorded rather than
worked around: an instrument that cannot see its corpus reports nothing, and reading that as "no
errors" is the mistake 055-4 and 049-3 both name.

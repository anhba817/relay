# Chapter 3.24 — gaps

*Every item has an owner. Every reference names its chapter, because the numbers collide.*

**Labels.** `3.24-n` is this chapter's own. `3.23-n` carries chapter 3.23's nine, re-measured
against the tree rather than copied. `3.22-n` carries the eight 3.23 labelled `C1`–`C8`, in the
same order, so a reader following a `C6` reference from that file lands on `3.22-6` here.

**Opened where they were found, not at close-out.** Three of this chapter's five new items are
findings of the analysis passes; the fourth is what fell out of reading a pipe that nine files
discard, and the fifth is what the close-out's own coverage run hit on its first attempt.
Writing them down where they are found is the only version of this that has ever worked.

---

## 3.24-1. `avatar_url` ACCEPTS `javascript:` — NEW, OPEN

`services/api/src/users/users.schema.ts:54` and `:92`:

    avatar_url: z.string().url().max(2048).nullable().optional(),

**Measured, not read.** Research R7 ran the validator rather than its documentation, and
`javascript:`, `data:`, `file:` and `vbscript:` all pass — zod's `.url()` asks whether the string
parses as a URL, not whether its scheme is one anybody should follow. The file's own comment two
lines up says *"`avatar_url` IS VALIDATED AS A URL AND NOT AS A STRING"*, which is true and is not
the same claim.

**This chapter is the reason it was measured.** FR-MSG-11 needed a url on an attachment, the
obvious spelling was the one already in the tree, and R7 ran it before copying it.
`packages/protocol/src/attachments.ts` therefore parses with `new URL(value).protocol` and
compares against a two-member allowlist, and that decision has a test with `javascript:` in it.

**What it costs.** The platform ships no client, so nothing here renders an avatar. A customer's
does. A `javascript:` value in an `<img src>` is inert in every current browser; the same value
behind an `<a href>` is stored XSS with the platform's name on the storage. The gap is that the
API accepts a value it has no use for and cannot make safe downstream.

**Owner: whoever next touches the user profile routes.** The remedy is the three lines
`attachments.ts` already carries, and it goes red for any environment already storing one — which
is why it is a decision rather than a drive-by.

## 3.24-2. THE SOCKET DOOR'S `text` CARRIES NO BOUND AT ALL — NEW, OPEN

Found by putting the three send doors beside each other rather than reading one:

    services/api/src/messages/messages.schema.ts:18   sendMessageBodySchema.text      z.string().max(8000)
    packages/protocol/src/internal.ts:32              internalSendRequestSchema.text  z.string().max(8000)
    packages/protocol/src/frames.ts:34                messageSendSchema.payload.text  z.string()

Two doors bound it. The third — the frame a browser puts on a socket, which is the only one of
the three an untrusted client reaches directly — bounds nothing. `services/gateway/src/session.ts`
has no length check either; `grep` for `8000`, `MAX_TEXT` and `text.length` in that file returns
nothing.

**It is not a hole, and calling it one would be wrong.** The gateway forwards every socket send to
`internal.controller.ts`, whose schema is the second row above, so an over-long text is refused —
by the api, after the gateway has parsed the frame, held it in memory and paid for an HTTP
request. `session.ts:1602` maps a 4xx carrying a registered code onto an error frame, so the
client does learn. **The bound is enforced one hop late, on the far side of the network boundary
from the client that broke it.**

**What actually bites is the asymmetry a reader cannot see.** `frames.ts` is the file that
publishes the contract. Someone reading it to find out how long a message may be finds no answer
there, and the two files that hold the answer are not the ones a client author reads.

**This chapter removed the floor from two of the three deliberately** (FR-019: a message may be
attachments with no text) and it is the reason all three were read side by side. The ceiling was
never on the third, in any chapter.

**Owner: the chapter that next changes `messageSendSchema`.** The remedy is
`.max(MESSAGE_TEXT_MAX)` exported once and imported by all three — the shape
`attachments.ts` uses for `MAX_ATTACHMENTS`, chosen there for exactly this reason. It changes
which code a client sees for an over-long text, from the api's derived refusal to the gateway's
own `invalid_frame`, and that is a wire-visible change rather than a tightening nobody notices.

## 3.24-3. FIVE BARE 422s IN `webhooks.service.ts` ANSWER `internal_error` — NEW, OPEN

`services/api/src/webhooks/webhooks.service.ts` lines 88, 193, 196, 202 and 210 throw
`UnprocessableEntityException` with a message and no code. `ProtocolErrorFilter` derives a code
from 400, 401, 403 and 404 and answers `internal_error` for everything else, so each of those five
puts this on the wire:

    422  {"code": "internal_error", "docs_url": ".../08-error-reference.md#internal_error"}

— for a refusal the customer caused, can read, and can fix. The message is right and the code
says the platform broke.

**Measured against the filter's ladder, not inferred from it.** The same reading is why this
chapter's own 422 names `media_not_available` through `protocolError(code, message, 422)` instead
of throwing the bare exception.

**Nothing catches it.** `services/api/src/webhooks/webhooks.itest.ts:90` asserts `422` and then
that the body contains the limit — never the code. A test that asserted the code would have been
red since chapter 3.5.

**Not this chapter's file, and the remedy is small**: `protocolError` at five call sites plus one
new code in `codes.ts` and one section in `docs/08-error-reference.md`. **Owner: a webhooks
chapter.**

## 3.24-4. THE e2e HARNESS RELEASES ITS PORTS ON A TIMER — NEW, OPEN

This is the item the pipe was hiding.

    packages/e2e/src/harness.ts:411   const apiPort = Number(process.env.RELAY_E2E_API_PORT ?? 4100)
    packages/e2e/src/harness.ts:427   const port = apiPort + 1 + i          // gateways: 4101, 4102
    packages/e2e/src/harness.ts:534   async stop() {
                                        for (const child of children) child.kill("SIGTERM");
                                        await new Promise((r) => setTimeout(r, 200));
                                      }

`stop()` signals and sleeps. It never waits for `exit`. The lane's three suites — `quotas`,
`tuan`, `webhooks` — each `boot()` and each `stop()`, and `vitest.integration.config.mts` sets
`fileParallelism: false`, so they run one after another **on the same three fixed ports**. An api
child that needs more than 200 ms to close its listeners — a slow pool drain, a machine under
coverage instrumentation — is still holding 4100 when the next file's child tries to bind it.

**The evidence is a line that exists and nobody reads:**

    Error: listen EADDRINUSE: address already in use :::4100

It was found this chapter by reading the harness's captured child output — the thing
`harness.ts:342` collects, `:352` formats and `:486` offers as `serviceOutput()`. **Exactly one
of the three suites calls it** (`tuan.itest.ts:60`). The other two report the second error, which
is a health-check timeout or an `ECONNREFUSED` against a port whose owner died before it ever
listened.

**This is not the cause of chapter 3.23's two red battery runs** — those were in
`session.itest.ts`'s own 4400–4599 range, in a different lane — but it is the same shape, found
in the one place where somebody had already written the capture and only one caller used it.
`3.22-6` below is the item that says why the shape stays invisible.

**Owner: whoever next has a red e2e run.** The first line of the fix is to await `exit` in
`stop()` with a timeout instead of sleeping 200 ms. **The second is not "do what the gateway lane
does"** — `session.itest.ts:133` draws `4400 + Math.floor(Math.random() * 200)`, four times a run,
which chapter 3.23's `baseline.txt` measured as self-colliding 2.96% of the time. A fixed port
collides always under contention and a random one collides sometimes; **only binding port 0 and
reading the assignment back cannot collide at all**, which is what `main.test.ts:19` does and what
`3.22-2` below says nothing tests. The reason nobody has fixed either is the item after that one.

## 3.24-5. THE INTEGRATION LANE ACCUMULATES STATE UNTIL IT CANNOT PASS — NEW, OPEN

Found by running the close-out's coverage lane and getting fifteen failures, every one of them a
delivery that never arrived. **Fifteen failures, two causes** — and the first hypothesis explained
both, which is why it had to be tested rather than believed. The nine in
`services/dispatcher/src/dispatcher.itest.ts` are this item. The six in
`services/api/src/consumer/consumer.itest.ts` are a defect this chapter introduced, and clearing
the broker reproduced them **identically** — the same six tests, 484189 ms against 484245 ms —
which is what said they were not environmental. `baseline.txt` carries that half.

**This half was not broken by this chapter; it had been filling up for nine days.**

    DELIVERIES stream          56,193 messages       216 consumers
    EVENTS stream              18,778 messages         1 consumer
    dispatcher-deliver         38,599 pending    100 ack_pending  = MAX_ACK_PENDING
    itest-deliver-<8 hex>      ~56,000 pending each, 215 of them
    webhook_deliveries         28,650 pending · 27,563 dead · 7,091 delivered
                               27,847 due now, oldest 2026-08-27

Three mechanisms, and each one on its own is survivable:

1. **`services/dispatcher/src/main.ts:86` creates durables with `DeliverPolicy.All`.** A
   consumer added to a stream holding 56,193 messages starts at the first one. Every test that
   publishes an event and polls for its arrival is polling for message 56,194.
2. **`dispatcher-deliver` is pinned at `MAX_ACK_PENDING`** (`main.ts:64`, 100). Its hundred
   unacked messages are deliveries whose rows were deleted by test runs that have since ended,
   so nothing will ever ack them and JetStream will never hand it a hundred-and-first.
3. **`publishDue()` in `dispatcher.itest.ts:252` calls the PRODUCTION delivery relay's
   `drainOnce()`**, which drains every due delivery in the database rather than the seeded
   environment's. So purging the stream is not enough: 27,847 stale rows put it straight back.

**Nothing here reports any of it.** The test says `expected 0 to be greater than 0`. The
dispatcher logs nothing, because from its side there is no error — it asked for messages and got
the ones it was owed. The only way to see it is to ask the broker, which is what
`scripts/stream-info.mjs` exists for and what no failure message suggests doing.

**Cleared by hand this chapter, with the user's approval**, and the numbers are in `baseline.txt`:
three streams purged, 216 consumers deleted, 28,650 stale `pending` rows removed under feature
030's `relay.allow_global` exemption — which refused the first attempt, correctly, because the
DELETE touched a sentinel row left behind by `messages.itest.ts`. **That refusal is the guard
working, and it is also a fourth kind of debris**: bait planted per file and outliving the run
that planted it.

**Why it matters to the next close-out and not just this one.** The close-out battery is twenty
consecutive integration runs. Each one adds deliveries and durables, so the lane the twentieth run
measures is not the lane the first one measured. A mean taken across a battery that degrades as it
proceeds is a mean over a moving instrument.

**The fix for the biggest half is already written, in the file next door.**
`services/api/src/consumer/consumer.itest.ts:201` deletes its durables in `afterAll`, and its own
comment says why: *"without this, every run of this suite left another handful behind on a shared
broker, and `stream-info.mjs` found twelve of them the first time it looked."* Chapter 3.4 learned
that at twelve. `services/dispatcher/src/dispatcher.itest.ts:407`'s `afterAll` stops the
dispatcher, drains the connection, kills the child and closes two endpoints — and deletes neither
`itest-expand-${run}` nor `itest-deliver-${run}`. **That is where 215 of the 216 came from**, and
the lesson was available in a sibling file for twenty chapters.

**Owner: whoever owns the lane, which is nobody.** Three fixes, cheapest first: delete the two
durables in `dispatcher.itest.ts`'s `afterAll`, the way `consumer.itest.ts` already does; give
that suite's durables `DeliverPolicy.New`, so a dirty stream cannot starve a fresh run; and add
the reset the repository does not have — `scripts/` can read this state (`stream-info.mjs`) and
cannot clear it.

---

# CARRIED FROM CHAPTER 3.23, RE-MEASURED AGAINST THE TREE

Nine items closed with `part3-ch23`. **Each was re-run here rather than copied.** Two of the nine
came back with a different number than the record carries, and one of those two was already wrong
on the day it was written.

## 3.23-1 — a customer can subscribe to an event type that does not exist — **OPEN, unchanged.**

`webhooks.service.ts:208`'s `assertEventTypes` still checks only `Array.isArray(types) &&
types.length > 0`. Membership against `OUTBOX_EVENT_TYPES` is still never checked.
`OUTBOX_EVENT_TYPES` still holds five members, because **this chapter added no event type** — it
changed what `message.created` carries, not which types exist. So the ratio 3.23 recorded, five
of FR-WHK-02's eight emitted, holds exactly.

## 3.23-2 — FR-MOD-03's audit log — **OPEN, unchanged, and untouched here.**

This chapter adds no moderation action and no read path over `metadata.deleted_by`.

## 3.23-3 — a concurrent edit and deletion of one message is not tested — **OPEN, and this chapter widened the subject without widening the item.**

Neither write took a row lock before and neither takes one now. What changed is what an edit
carries: `editMessage` reads `attachments` as of FR-015, so the interleaving 3.23 described in
text now has a second column in it. **The conclusion is unchanged** — both orderings still end in
a tombstone — and the attachment column follows the text column through every ordering, because
it is written by the same UPDATE.

## 3.23-4 — one authorization fact lives in two places and nothing compares them — **OPEN, and this chapter did not widen it.**

`grep` for `.accepts` outside `targets.ts` still returns nothing: the field still has no consumer.
**This chapter added no route** — attachments ride `POST /v1/channels/:id/messages`, `PATCH
/v1/messages/:id` and the existing internal send — so the declared list did not grow. 3.23 widened
it by three; this one by zero.

## 3.23-5 — a closed chapter's two records disagree — **CLOSED, and the convention held.**

`specs/040-chapter-3-22/baseline.txt:1201` carries the bracketed amendment, naming chapter 3.23 as
the amender and preserving what the line said before. Re-read this chapter; it is still there and
still legible as an annotation rather than an overwrite.

## 3.23-6 — drizzle-kit's snapshot is behind the directory — **OPEN, and the number was wrong when it was written.**

    services/api/migrations/meta/     snapshots through 0007_snapshot.json
    services/api/migrations/          0014_message_edits.sql

**Seven, not six.** 3.23 measured the gap before adding its own migration and recorded the
measurement it took: `0013_bot_users.sql` was the last file at the time. `0014_message_edits.sql`
is that same chapter's, renumbered by hand from the colliding `0008` drizzle-kit generated — so
the item was one behind by the time the chapter it belongs to was tagged.

**This chapter did not move it, and the reason is worth recording**: `messages.attachments jsonb`
has existed since `0000_core_tables.sql:54`. FR-MSG-11's column was in the schema before the
feature that uses it, so **this chapter ran no migration and generated no SQL** — which is also
why it never met the collision.

The two ways to close it are 3.23's and unchanged. **Owner: whichever chapter next adds a table.**

## 3.23-7 — the tenancy catalogue's reach was fixed; the guard's coverage was not — **OPEN, unchanged.**

`db/catalogue.ts:216-217` still classifies by `has_environment_id` then `via`, `message_edits` is
still `hop`, and no check yet asks whether a `hop` table is append-only or trigger-protected. This
chapter added no table, so the population is what 3.23 left.

## 3.23-8 — EIR-WS-06 is still met by two close codes of six — **OPEN, re-measured, identical.**

Re-counted across `docs/` rather than carried:

    4001  invalid or expired token      docs/04-srs.md              x1
    4002  protocol violation            docs/08-error-reference.md  x2
    4003  banned in this environment    nowhere at all
    4004  connection limit reached      docs/08-error-reference.md  x1
                                        docs/05-sad.md              x1
                                        docs/07-tutorial-plan.md    x1
    4008  quota exhausted               docs/07-tutorial-plan.md    x2
    4009  server shutdown (drain)       docs/05-sad.md              x1

Every count is the one 3.23 recorded. `CLOSE_CODES` still holds exactly these six
(`packages/protocol/src/codes.ts`), the error reference still documents two of them, and the
clause's four classes are still met by one.

**This chapter added an ERROR code and no close code** — `media_not_available`, which is a 422 on
a REST body — so the work remains entirely somebody else's clause. **Owner: the next chapter that
adds or renames a close code.**

## 3.23-9 — a `.test.ts` in the docker-free lane needs a running Redis — **OPEN, unchanged, and re-measured.**

`services/gateway/src/connections.test.ts` still calls `createConnections({ url: REDIS, … })` at
**six** call sites, and `REDIS` is still `process.env["RELAY_REDIS_URL"] ?? "redis://localhost:6379"`.
The file's own comment at line 18 states the argument for it — *"AGAINST A REAL REDIS, NOT A STUB"*
— which is a defensible test design and is not an argument about which lane it belongs in.

**One thing the 3.23 item did not say, and it makes the fix cheaper**: `connections.itest.ts`
already exists beside it, 1,115 lines to this file's 366. The lane the six call sites belong in is
not hypothetical.

**Owner: unchanged** — chapter 3.22 wrote the file; this chapter changed `connections.itest.ts`
and not `connections.test.ts`.

---

# CARRIED FROM CHAPTER 3.22 VIA 3.23, RE-MEASURED

3.23 labelled these `C1`–`C8`. Same order, same meaning, re-run here.

## 3.22-1 (`C1`) — EIR-WS-06 — **carried, and it is `3.23-8` above with the same numbers.**

Nothing moved in either direction this chapter.

## 3.22-2 (`C2`) — the port collision a test could not see — **OPEN, and this chapter found one it CAN see.**

`main.test.ts:19` still binds `server.listen(0, …)` and reads the assigned port back, which is
what makes it structurally unable to see a collision on the configured one. Unchanged.

**What is new is that the collision it was written about is no longer hypothetical.**
`3.24-4` above holds an `EADDRINUSE` on a fixed port, captured, in this repository, with the file
and line that produces it. That item and this one are the same defect at two scales: a port that
a process cannot fail to get is a port whose loss nothing tests.

## 3.22-3 (`C3`) — an excerpt-only file is never verified — **OPEN, and the count is TEN, not two.**

`check-fence-chain.mjs:42` still skips a title containing `(excerpt)` or `.naive.`. **This chapter
added no excerpt fence** — `grep` over its page returns zero — so it did not widen the rule.

It did widen the exposure, and re-measuring the population is what showed it. Every fence title
across the English chapters, split into real chains and excerpt-only ones, leaves **ten real
repository paths that no chapter has ever fenced whole**:

    packages/test-harness/src/guard.itest.ts        services/api/src/messages/idempotency.itest.ts
    packages/test-harness/src/sentinel.sql          services/api/src/notifications/mailer.test.ts
    packages/test-harness/src/sentinel.ts           services/api/src/quotas/quotas.itest.ts
    services/api/src/fanout/fanout.itest.ts         services/gateway/src/limits.itest.ts
    services/api/src/internal/usage.itest.ts        services/gateway/src/session.itest.ts

3.22 named two and 3.23 carried two. **Two was the gateway's count, not the repository's** — the
same error `3.22-6` made about child output, in the same place, one chapter apart.

**This chapter edited three of the ten**: `fanout.itest.ts`, `idempotency.itest.ts` and
`session.itest.ts`. Every fence a chapter shows from those files is an excerpt, so nothing
compared the edits with what any chapter published about them.

**Owner: unchanged, and the number is the argument.** The remedy 3.22 recorded — verify an excerpt
as a substring rather than skipping it — costs the same for ten files as for two.

## 3.22-4 (`C4`) — `main.test.ts` checks that a module is CLOSED, not that it is PASSED — **OPEN, and this chapter used the instrument 3.23 pointed at.**

The check at `main.test.ts:109` is still `shutdown.includes(\`await ${String(name)}.close()\`)`.
A module built and never handed to `attachSessions` still passes it.

`packages/outsider/src/integrate.itest.ts` — the only instrument that boots the shipped binary —
gained this chapter's end-to-end assertion, and the title audit found that the task list
had scheduled an audit over that file while no task wrote a test into it. **It does now.** A
structural check would still be better, for the reason 3.23 gave: the outsider suite catches this
chapter's wiring, not the next chapter's.

## 3.22-5 (`C5`) — the retry-log bound is a five-module decision — **OPEN, unchanged, untouched here.**

## 3.22-6 (`C6`) — files that discard their child's output — **OPEN, re-measured, and the number is ELEVEN.**

3.22 said five. 3.23 re-counted nine. Re-run here over every file that calls `spawn(`:

    output discarded entirely        services/dispatcher/src/dispatcher.itest.ts
                                     services/gateway/src/isolation.itest.ts
                                     services/gateway/src/limits.itest.ts
                                     services/gateway/src/membership.itest.ts
                                     services/gateway/src/presence.itest.ts
                                     services/gateway/src/public-surface.itest.ts

    captured, surfaced on ONE path   packages/e2e/src/harness.ts        1 of 3 callers use it
                                     services/gateway/src/meter.itest.ts        health check
                                     services/gateway/src/session.itest.ts      health check

    captured and parsed              services/api/src/consumer/consumer.itest.ts
                                     services/api/src/outbox/outbox.itest.ts

**Eleven files, and the three-way split is the finding.** 3.23 counted files that spawn and
discard. Counting what each one does with what it captures separates the two that read their
child's output as data from the three that hold it and show it for exactly one failure — which is
the state that produced `3.24-4`: the line was captured, it was in memory, and two of three
callers threw it away.

`session.itest.ts`'s and `meter.itest.ts`'s ring buffers and `[child exited code=…]` lines are
chapter 3.21's (`7ec7c6e`), not this chapter's. Nothing here changed any of the eleven.

**Owner: unchanged — whoever next has a red run they cannot explain.** This chapter was that
person, on the e2e lane, and the fix it needed was one caller passing `serviceOutput()` into an
error. The other two callers still do not.

## 3.22-7 (`C7`) — coverage cannot see an omission — **OPEN in the same partial way.**

`**/main.ts` is still in `vitest.coverage.config.mts`'s exclude list, so the shape of 3.21's
defect is still invisible to the ratchet. The outsider suite is still the instrument that can see
it, and this chapter is the second to use it for a feature: `integrate.itest.ts` drives an
attachment through the shipped binary.

## 3.22-8 (`C8`) — the per-chapter instruments have no owner — **OPEN for the SIXTH chapter, and this chapter DOUBLED it while choosing not to.**

**3.23's own count is wrong and re-measuring it was in the task.** That item says this chapter's
predecessor added *"a fourth instrument"* and that *"all four were improved"*, then names three;
`specs/041-chapter-3-23/` holds exactly three `.py` files. The fourth was counted twice: the three
per-chapter *copies* (`039-`, `040-`, `041-`) are directories, not instruments.

`specs/042-chapter-3-24/` holds **six**, 933 lines:

    check-refs.py            319      sweep.py                303
    check-quickstart.py       92      check-checklist.py       84
    regen-traceability.py     72      check-prose.py           63

`check-quickstart.py` was written in analysis pass 13, `check-checklist.py` in pass 14, and
`regen-traceability.py` during planning. **The copy-forward is now twice the size it was**, and
the three that were inherited all diverged from the copies they came from — differing lines,
counting both sides:

    check-refs.py    50        sweep.py    65        check-prose.py    110

**And two of those three numbers moved after they were written down.** This chapter's own task list recorded
`sweep.py` at 2 differing lines, measured during analysis; the tree says 65, because a 58-line
rule was added to it during implementation. A copy-forward gap is not a fixed quantity measured
once — **it grows for the whole chapter, so any number taken before close-out understates it.**

**The decision this chapter made, and made silently until now.** 3.23's recommendation was to move
the instruments into a shared `specs/_instruments/` with per-feature configuration passed in, or
to accept that each chapter re-derives what it happens to need. This chapter took the second
option — by copying three files forward and writing three more — and never wrote down that it was
choosing. **That is the part no other task records**, and it is why the item is here rather than
one line longer.

**Owner: still nobody.** The honest recommendation is unchanged and the cost of not taking it has
doubled.

---

## THE ONE THAT IS NOT NUMBERED, BECAUSE ELEVEN CHAPTERS HAVE NUMBERED IT

`specs/036-chapter-3-18/reader-protocol.md` — 45 minutes, six questions, one person who has not
read the chapter. **Chapters 3.14 through 3.24 have each named it and none has closed it**, and
this chapter is the eleventh.

It cannot be closed from inside a session. Every check in this repository compares bytes, and this
chapter added two more of them: `check-quickstart.py` compares a command in prose with a command
in a file, `check-checklist.py` compares a checklist item with a requirement id. **Six instruments
now, and not one of them can answer whether a paragraph is understandable to somebody who does not
already know the answer.**

What this chapter would most want asked, if somebody did run it:

    1  Read the section on the two doors and say, without scrolling back, why the same rule is
       written twice. If the answer is "so both endpoints validate", the section buried its
       point — that is what the rule DOES, and the reason it is written twice rather than
       shared is a different and harder claim about layers.
    2  Look at the attachment figure and say what a message with no attachments carries on the
       wire. If the answer is "nothing" or "the field is missing", FR-007 did not land: it is
       an empty array, always, and the whole reason the field is required rather than optional
       is that a reader should never need to ask this.
    3  Say what happens if you send text and no attachments, then edit it to no text and no
       attachments. The answer is a refusal, and finding it should not require reading the
       schema — if it does, the pair rule is explained in the wrong place.

**An instrument that is easy to run tells you what it measures, not what you wanted to know**, and
eleven chapters of that sentence have not produced the forty-five minutes.

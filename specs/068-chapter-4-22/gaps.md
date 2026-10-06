# Gaps — feature 068, chapter 4.22, "The identifier the customer gave it"

Numbered. The carried ledger is re-measured rather than copied, which is the only
way four of 043's twenty-three were found to be wrong.

## NEW

### 068-1 · The real-time surface still addresses channels by uuid

Thirteen REST routes take the customer's identifier. **Every gateway frame still
carries `channel: <uuid>`**, the session response hands a connecting client a
list of channel uuids, and a socket `message.send` is forwarded to a door typed
`z.string().uuid()` (`packages/protocol/src/internal.ts:28`).

So a customer holding a WebSocket keeps the lookup table REST no longer needs —
on **Journey 3's Stage 5**, in the same journey whose Stage 1 promises zero of
them.

**The evidence that it is an oversight rather than a decision is in the contract
itself.** Two lines above the field that carries those uuids, `internal.ts` says
*"`user` is the EXTERNAL id, as everywhere else on this contract: internal uuids
are the api's business."* The principle is stated there and applied to one field
of two.

**OPEN.** Fixing it is the gateway, `subjectForChannel`, the resume cursors and
the internal contract — a chapter, not a paragraph. Named in FR-CHN-11, ADR-38,
`contracts/addressing.md`, the quickstart and the chapter's own closing section.

### 068-2 · A pipe answers before every check the handler makes

Nest runs pipes after guards and before the handler. So a pipe that refuses
preempts refusals the handler makes first on purpose:

    a BANNED user, real channel        403 user_banned      the ban check
    a BANNED user, invented channel    404 not_found        a refusing pipe

`gauntlet.itest.ts` asserts those two are byte-identical once `request_id` is
stripped, and caught it. `messages.itest.ts` caught the same shape one check
over — a token for a user with no row answers `400 unknown user` before the
channel is read.

**CLOSED by design**: the pipe resolves and never refuses, and an unresolved
segment becomes a fresh `randomUUID()` so every handler refuses in its own
order. **Recorded because the next enhancer will look as right as this one did**
— it threw the same exception class with the same constant message that
`channels.service.ts` chose deliberately, and it passed ninety-two assertions
before the gauntlet found it.

### 068-3 · `members[].user_id` handed out a key no route accepted

`POST /v1/channels/{channelId}/members` returned the row's `users.id` on every
member added, for every user. `GET /v1/users/{a users.id}` is 404 while
`GET /v1/users/{external_id}` is 200, so a caller storing it held a key to
nothing — and **ADR-37's opening sentence said the platform exposed `users.id`
nowhere a caller can act on.**

Nothing asserted the field, no clause documented it, no tutorial page showed it.
**CLOSED**: removed, and ADR-37 amended in both homes.

**The method is the part worth keeping.** The chapter went looking for the
`GET /v1/users` listing cursor ADR-37 names, found the route does not exist, and
enumerated every v1 response shape instead, asking of each uuid *does a route
accept this?* Reading produced a phantom; enumerating produced the real one.

### 068-4 · The 500's cause is still unlogged, and that is every route

A 500 is logged as `{"level":"info","msg":"request","status":500}` and nothing
else — no `22P02`, no constraint name, nothing an operator can act on.
`ProtocolErrorFilter` has no rung for a driver error.

**This is NOT 058-3's population**, which six of this feature's artifacts said it
was. That gap counted sixteen routes where a malformed uuid *causes* a 500 and
is now closed, 16 to 0. How the remaining 500s are *logged* is every route on
the platform and has never been counted.

**OPEN**, and deliberately: repairing the logging for one route and leaving the
rest is worse than naming the class.

### 068-5 · The clamav healthcheck has a seven-day bound against a seven-day tag

`clamav/clamav:1.5` is a moving tag republished every seven days, each build
bundling that week's signature database:

    sha256:0e31ce…   built 2026-09-21   bundles Sep 21
    sha256:ebec5bc…  built 2026-09-28   bundles Sep 28
    bound <= 7 days · Sep 28 + 7 = Oct 5 green · Oct 6 red

**Zero margin.** The check passes for exactly one week after each rebuild and
fails from the eighth day until the next lands. It has been true since 4.13 and
nobody had pushed on a day eight.

Underneath it, `freshclam` downloads the database and cannot notify `clamd` —
the socket is not up yet — and its daemon then sleeps for hours. So the check
measured *the age of whatever clamd loaded at container start*.

**PARTLY CLOSED, AND THE DEBT IS WRITTEN INTO THE CHAPTER.** The healthcheck now
reloads the daemon when the answer is stale, measured both ways: a daemon at
`28143` with `28145` on disk reloaded to `28144` in about eight seconds, and a
simulated stale version takes the branch. **Reloading from a healthcheck is the
wrong place for it** — a probe that repairs what it measures — and the real fix
is upstream: the image's entrypoint should order freshclam after clamd's socket
exists, or freshclam should retry its notification.

**AND A GREEN JOB DOES NOT PROVE THE RELOAD FIRED.** CI's download may simply
have won the race, as it does on this machine, where a fresh container had
today's database 45 seconds in. The clamav log that would distinguish them is
captured only on failure.

### 068-6 · Two lanes on one broker steal each other's messages

On this machine, api and dispatcher run together and one of them loses:

    api alone          998 of 998, three times    (1,001 after the new attacks)
    dispatcher alone    16 of 16, twice
    together           one fails, either one

The losing assertions are always exactly-once or nothing-is-there claims over a
shared stream; `EVENTS` carries seven consumers. **Not reproducible in CI** —
the dispatcher lane ran there, uncached, and passed — so this is local broker
state rather than a property of the code.

**OPEN, LOCAL.** The revert-and-measure that would have dated it was refused as
an irreversible local operation.

### 068-7 · A fence bill cannot see the work that has not happened yet

The bill predicted 8 files and the chapter charged 9, 23 hunks:

    predicted, NOT TOUCHED   users.schema.ts
    NOT PREDICTED            channels.service.ts · compose.yaml
                             vitest.coverage.config.mts

Every surprise arrived from RUNNING something rather than reading it — the
sweep's removal landing elsewhere, the NATS fix, the pins. **Three files needed
their FIRST appendix block**, which a count of existing blocks cannot show.

**CLOSED as a measurement**, open as a lesson: 4.15's rule holds, and it holds
in one direction.

### 068-8 · ADR-37 sits alone, 1,700 lines from the other ADRs

    docs/05-sad.md:730    ADR-37    was `##`, INSIDE section 6 "Data view"
    docs/05-sad.md:2350   ADR-34    `###`
    docs/05-sad.md:2429   ADR-35    `###`, inside section 10 "Risks"
    docs/05-sad.md:2466   ADR-36    `###`, inside section 10 "Risks"
    docs/05-sad.md:2513   ADR-38    `###`, placed with the run

At `##` the ADR-37 heading **closed section 6** while the data view's own content
continued below it. Demoted to `###` so it stops doing that.

**OPEN.** The SAD has no ADR section; three chapters put theirs in three places.
Moving ADR-37 is 1,700 lines of published document for no behavioural reason.

### 068-9 · The sealed suite and the api lane want opposite machine states

`packages/outsider` needs the composed services UP and three environment
variables; the api lane needs them DOWN or a second relay drains rows its tests
are counting. `turbo run test:integration` with `--concurrency=1` stops at the
first failure, so run as one command they answered `Tasks: 1 successful, 4
total` in 1.044 s.

**OPEN.** Nothing enforces either state and nothing documents the split. I broke
the rule myself an hour after recording it, because the response-shape sweep
needed the api up.

## CARRIED, RE-MEASURED

| | |
|---|---|
| **058-3** malformed uuid in a path is a 500 on sixteen routes | **CLOSED, 16 to 0.** Thirteen by never casting, three by `UuidParamPipe`, one `mediaId` already done at 4.12 |
| **067-1** two exceptions three chapters apart is a list | holds; this chapter added none to ADR-35 |
| **067-2** the edit path still writes a `Date` | untouched, unverified here |
| **067-3** `git diff <tag>..HEAD` reads committed state | **paid again.** T041's one-dot form found four `FR-006`s in published documents that `..HEAD` would have missed |
| **066-1** a comment still accurate must be left alone | paid the other half: `media.controller.ts`'s comment was falsified by this chapter and repaired |
| **065-2** `message_edits.edited_at` writes a `Date` on the edit path | untouched |
| **065-4** a single-mutation probe measures the defence, not the arm | **third chapter running.** Deleting the tenancy scope turned 18 addressing tests red and 0 gauntlet tests |
| **063-4** feature-local ids in `docs/` | **22 distinct, unchanged, and I added four more before T041 caught them** |
| **062-12** unpinned files a re-measure cannot see | **paid.** Two of this chapter's files had no pin; 66 pins now, from 62 |
| **050-8** the ingester has no runner | untouched |
| **043-1** an untitled fence is never compared | untouched; this chapter contributed 0 titled fences |

## WHAT THIS FEATURE PAID FOR TWICE

**An explanation that fits one observation is a hypothesis.** The dispatcher
failures were explained as a volume reset and the next run falsified it; the
clamav failure was explained as a slow download and the next line of the same
log falsified it. Both wrong readings are in `baseline.txt` with what killed
them, because in both cases the thing that settled it was running something
again rather than thinking harder.

**And four times, the same refusal.** An application credential may send only as
a bot. It cost two runs in the test fixtures, two more in the response-shape
sweep, and it is now written into the quickstart.

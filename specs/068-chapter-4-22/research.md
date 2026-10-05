# Research — chapter 4.22, "The identifier the customer gave it"

Every figure measured against the development lane on 2026-10-05, before the plan
was written.

---

## R1 — The 500 is a failed cast, and that is a better fact than "the route takes a uuid"

```sql
select id from channels where external_id = 'order-not-a-uuid'
                           or id = 'order-not-a-uuid'::uuid;

ERROR:  invalid input syntax for type uuid: "order-not-a-uuid"
```

**POSTGRES RAISES BEFORE THE `OR` CAN SHORT-CIRCUIT**, which is both the cause of the
500 and the reason a single query cannot resolve both forms. The route hands a path
segment to a uuid-typed column, the driver sends it as a uuid, and the database
refuses it — surfacing to the caller as `internal_error`.

**AND THE API LOGS THE STATUS WITHOUT THE CAUSE.** Measured against the composed
container:

```
{"level":"info","msg":"request","method":"GET",
 "path":"/v1/channels/order-xyz-not-uuid","status":500}
```

That is the whole of it. No error line, no `22P02`, no constraint name — an operator
reading the log sees a 500 and nothing that explains it. **Recorded as a gap rather
than fixed here**: the swallowed cause is every 500's problem on this platform, not
this chapter's, and 058-3 already counts 22 routes that can produce one.

## R2 — The resolution order is a correctness question, because the cost is a tie

Both lookups are single index hits, measured with `EXPLAIN (ANALYZE, BUFFERS)`:

```
WHERE environment_id = $1 AND id = $2
  Index Scan using channels_pkey            2 shared hit + 1 read   1.475 ms
WHERE environment_id = $1 AND external_id = $2
  Index Scan using channels_environment_id_external_id_unique
                                            3 shared hit + 1 read   1.094 ms
```

**THE IDENTITY LOOKUP IS MARGINALLY CHEAPER THAN THE KEY LOOKUP**, which is the
opposite of what a reader expects from a primary key. The composite index carries the
environment, so it answers the scoped question in one search where the primary key
answers an unscoped one and then filters. The difference is inside the run-to-run
spread and **the point is that there is no performance argument either way.**

**SO THE ORDER IS DECIDED BY WHICH COLLISION IS WORSE.** An `external_id` may itself
be a uuid — `z.string().min(1).max(255)` permits it — and measured, **0 of 41,768
channels have a uuid-shaped identifier and 0 have one equal to their own row id.**

| | order | the collision case | consequence |
|---|---|---|---|
| **A** | key first, then identity | a customer names a channel with another channel's uuid | **they can never reach their own channel** — the key always wins |
| **B** | identity first, then key | the same | the customer reaches their own; the other is still reachable by its uuid from a caller who has it |
| **C** | shape-based: a value that cannot parse as a uuid is resolved as an identity and never cast | — the collision needs a uuid-shaped value | one query on the identity path |

**DECISION, IN TWO PARTS, BECAUSE THE FIRST VERSION OF THIS SECTION RAN THEM
TOGETHER AND CONTRADICTED ITSELF.**

**The outcome is settled: the IDENTITY wins a true tie.** A customer who named a
channel must reach the channel they named; the other channel stays reachable by its
uuid from any caller holding it, and the alternative strands somebody permanently
with no error they can act on. That is B's tie-break and it is the half with an
argument behind it.

**The shape test is settled too**, and it is independent of the tie-break: a value
that cannot parse as a uuid can only be an identity, so it costs one query and **the
cast never happens — which is what removes the 500.**

**THE PROCEDURE FOR A UUID-SHAPED VALUE IS NOT SETTLED, AND T009 OWNS IT.** Two
candidates deliver identity-wins:

```
one query, explicit preference
  where environment_id = $1 and (external_id = $2 or id = $2::uuid)
  order by (external_id = $2) desc limit 1
     one round trip. 4.18 found an `OR` can land in a `Filter:` instead of an
     `Index Cond`, so this needs EXPLAIN before it is chosen, not after

identity first, then the key
  two round trips on every uuid-shaped value, which is all 157 existing call
  sites — the cost R2 rejected "B everywhere" for
```

**What this section said before.** It tabled C as *"parse as a uuid → try key then
identity"*, gave its collision consequence as *"the same as A"* — and A is *"they can
never reach their own channel"* — and then decided for the identity six lines later.
Key-then-identity-if-nothing-found means the **key** wins a true tie. The same
contradiction reached `data-model.md`, `contracts/addressing.md`, and tasks T013 and
T021, where the implementing task encoded one order and its asserting task the other.
**An outcome and a procedure are different decisions, and writing them in one
sentence is how the artifacts stopped disagreeing with the tree and started
disagreeing with themselves.**

**Alternatives considered.** *A* — simplest to describe and it is the one that
strands a customer. *Refuse ambiguity with a 409* — honest, and it turns a working
call into a broken one for a customer who did nothing wrong.

## R3 — 157 existing call sites, and the design must not touch any of them

```
/v1/channels/${channelId}        55        /v1/channels/${privateChannelId}   8
/v1/channels/${channel}          24        /v1/channels/${t.victim.channelId} 7
/v1/channels/${api.channelId}    11        /v1/channels/${rejectId}           7
/v1/channels/${c}                10        … and the rest
                                 ---
                                 157 across the test corpus
```

Every one passes a uuid. **FR-002 is not politeness, it is 157 assertions**, and any
design that changes what a uuid does breaks the suite that proves the chapter did no
harm. Under R2's decision they all take the same path they take today.

## R4 — Where the resolution belongs, and the cheapest place cannot work

**Thirteen `@Param("channelId")` sites, counted from the decorators rather than from
the route list: 7 on `channels.controller.ts`, 5 under `messages.controller.ts`'s
`v1/channels/:channelId/messages` prefix, and 1 on `users.controller.ts`'s read
position route.** A first version of this section said *"8 on channels.controller …
plus the read position route"*, which totals fourteen while calling it thirteen — the
total was right by accident and the breakdown was wrong. **A task saying "all 8 sites"
either leaves one unedited or hunts for one that does not exist.**

**There is no chokepoint**: `channelId` is passed into ten different repository
methods. **And all five messages routes do take `@Param("channelId")`**, checked per
route — one that read the channel from elsewhere would never run the pipe.

| | design | fence cost | verdict |
|---|---|---|---|
| middleware | one registration in `app.module.ts` | 75 pages | **cannot work** |
| **pipe** | `@Param("channelId", ChannelIdPipe)` | **101 pages · 17 blocks · 7 files** (R6) | **chosen** |
| service layer | resolve at the top of each method | 91 pages, ~13 sites | rejected |
| repository | each method accepts either | spreads the ambiguity into ten queries | rejected |

**THE MIDDLEWARE IS CHEAPEST AND NEST RUNS IT BEFORE GUARDS**, so it has no principal
and cannot scope the lookup to an environment. That is disqualifying rather than
inconvenient: an unscoped resolution is a cross-tenant read.

**AND IT NEEDS NO MODULE REGISTRATION, WHICH ANALYSIS PASS 1 GOT WRONG AND PASS 2
MEASURED.** Three Nest apps booted, one HTTP request each:

```
A  pipe AND dependency in `providers`     200  {"id":"x|scoped"}
B  dependency only, PIPE NOT A PROVIDER   200  {"id":"x|scoped"}
C  neither                                Nest can't resolve dependencies of
                                          the ResolvingPipe (?)
```

**Nest instantiates a param-level pipe class from the module's injector without it
being in `providers`. What must be resolvable is its DEPENDENCY** — and `Repository`
already is one in all three modules.

**CASE `C` IS WHAT MAKES `B` TRUSTWORTHY.** `B` alone is a green that proves nothing:
it could have passed because Nest silently skipped the pipe. `C` failing by name shows
the pipe really ran and really needed its dependency.

**HOW PASS 1 GOT IT WRONG IS THE PART WORTH KEEPING.** It asked how Nest finds the
class, reasoned from the module-visibility rule `internal.module.ts` states and 4.21
paid four times, and cited 4.10's `MediaModule`. **That rule is real and it governs
dependencies, not enhancers** — and the analogy carried the conclusion past the
evidence. The remedy it prescribed was three module edits and 19 fence pages of work
that does nothing. **A reasoned premise is still a premise.**

**AND A SECOND PROBE, BECAUSE THE FIRST ONE'S LESSON WAS NOT TO ASSUME TWICE.** A
param-level pipe that throws and a body pipe that throws, in one app, both parameter
orders, one real request each:

```
A  @Param(pipe) idx0, @Body(pipe) idx1   400 bad body            ran: body, param
B  @Body(pipe) idx0, @Param(pipe) idx1   404 channel not found   ran: param, body
C  guard + @Param(pipe)                  403 guard               ran: guard
```

**The HIGHER parameter index runs first, and both pipes run even after one throws.**
All thirteen real signatures put `@Param("channelId")` at index 0 with any
`@Body`/`@Query` validation above it, so **body validation keeps winning and a 400
stays a 400** — which is what FR-002 and FR-009 rest on. Case `C` confirms guards
still precede pipes, which is what disqualifies the middleware.

**The clean result is the one nobody writes down.** It is here because the
alternative was finding out at T023 that a refusal moved.

**AND "BOTH PIPES RUN" IS NOT FREE** — the resolution query fires on requests already
refused for a bad body. See the cost note at the end of this section.

**There is no injectable pipe anywhere in this codebase**: `ZodValidationPipe` is
`new`-ed at 21 call sites and carries no `@Injectable()`. So the design has no
precedent here, which is why it was worth probing rather than assuming in either
direction.

**THE PIPE GETS THE SCOPE BY CONSTRUCTION.** An injectable pipe can take the
request-scoped `Repository`, whose constructor already requires an `environment_id` —
the same mechanism chapter 4.21 found had kept six of seven stores correct without
anyone remembering. Everything downstream keeps receiving a uuid, so the ten
repository methods are untouched.

**AND THAT IS THE COST, NOT ONLY THE SELLING POINT.** The handlers still call
`getChannelById`, `channelExists` or `channelVisibleTo` with the resolved uuid, so
**the resolution is a second scoped `SELECT` on every one of the thirteen routes
rather than a relocated one** — at R2's own figures, +1.094 to +1.475 ms and one
round trip per request, plus the refused-body requests the ordering probe showed it
runs on anyway.

Three ways out, none free: let the pipe hand the row downstream and delete the
handler's read (touches the ten methods the design exists to leave alone); cache the
resolution on the request object (state nobody can see); or **pay it and say so.**
Paying it is the default here — the chapter's subject is correctness, and a doubled
read on a route that was answering 500 is not the expensive part. **It is measured at
T023a and published**, because every other chapter in Part 4 priced its instrument.

## R5 — The users side, and the leak that is not there

All eight user routes take the identity and the upsert returns no uuid, measured:

```
POST /v1/users   -> external_id, status, display_name, avatar_url, metadata, kind, description
POST /v1/channels -> id, external_id, type, name, metadata            <- uuid first
```

**AND THE ONE LEAK THIS SECTION PUBLISHED DOES NOT EXIST.** It said the single leak
was the `GET /v1/users` listing cursor, base64 of `{a: last_activity_at, id:
users.id}`. Analysis pass 3 opened the controller:

```
users.controller.ts routes      POST /v1/users · GET/PATCH/DELETE :externalId
                                GET :externalId/channels · PUT …/channels/:channelId/read
                                DELETE :externalId/data · POST/DELETE :externalId/ban
                                — THERE IS NO GET /v1/users
listingQuerySchema, consumers   one: users.controller.ts:70, @Get(":externalId/channels")
listChannelsForUser keyset      (channels.lastActivityAt, channels.id)   repository.ts:4878
nextCursor                      { activityAt: last.lastActivityAt, id: last.id }  :4915
targets.ts, derived from a boot no GET /v1/users row
```

**The route is `GET /v1/users/{externalId}/channels` and the cursor carries a CHANNEL
uuid.** The row it points at already returns that uuid as a top-level `id`, and after
this chapter all thirteen routes accept it — so FR-006's own test, *an identifier
that is Relay's alone **and that no route accepts***, does not flag it even once.

**THE CLAIM CAME FROM A PUBLISHED DOCUMENT, WHICH IS WHY TWO PASSES READING THIS
DIRECTORY COULD NOT CATCH IT.** `docs/05-sad.md`'s ADR-37, shipped by 4.21:

> **Reversal condition.** If `users.id` ever becomes resolvable to a person by a
> party outside the platform, this rule fails […] **One live edge is already known
> and bounded**: the `GET /v1/users` listing cursor is base64 of `{a, id}` […] so a
> customer who paged before an erasure holds the uuid.

Six artifacts in this feature inherited it — spec, this section, `data-model.md`,
`contracts/addressing.md`, the plan's complexity table and four tasks — and so did
`CLAUDE.md`. **It is not a case of artifacts agreeing with each other and not with
the tree; they agreed with a document, and the document was wrong.**

**ADR-37 IS STRONGER THAN IT WAS PUBLISHED, NOT WEAKER.** Its conclusion — a key into
an erased row names nobody — stands, and its one bounded exception turns out not to
exist. The reversal condition holds with **zero known live edges**. FR-010 makes the
amendment this chapter's work, in both homes.

**WHAT IS NOW OPEN.** *Where, if anywhere, does `users.id` reach a caller?* The
sweep this pass started is not an answer: `users.id` is selected at eight sites in
`repository.ts` and every one read so far is internal, with the services stripping it
before the wire — consistent with the upsert response above, and **a reading rather
than a measurement**, taken while the lane was down. Two near misses worth recording
because each looked like the leak for a minute:

```
channel listing, last_message.user.id   = user_external_id, not users.id   :4908
upsertUser's returned row carries id    stripped by the service before the wire
```

SC-006 asks for the count. It was a formality while the leak was known; it is the
question now, and T026 is where US2 finds out whether it has a subject at all.

## R6 — What the fence chain charges, counted now, with the method written down

**The method, because the number has moved three times and nobody could reproduce
it.** `pages` is pages whose titled fence ends with that path; `blocks` is titled
fences for it in `fences/post-series.md`; `hunks` is `@@` lines inside those blocks.

```
                                 pages  blocks  hunks
channel-id.pipe.ts                   0   0        0   NEW FILE
users.schema.ts                      4   0        0   the cursor payload, if US2 keeps one
channels.controller.ts               8   0        0   7 @Param edits
users.controller.ts                  5   1        1   1 @Param edit
messages.controller.ts              19   1        1   5 @Param edits
repository.ts                       52   7       50   one resolution read
gauntlet.itest.ts                   13   8       14   T031's new-form attack
                                 -----  --      ---
                                   101  17       66   across 7 files
```

**THE BILL OMITTED A FILE A TASK EDITS.** T031 adds the new-form attack to
`gauntlet.itest.ts`, which is fenced on **13 pages and 8 appendix blocks**. This is
066's finding reproduced on the chapter after it — *the fence bill named all six
files at ANALYSIS, including `gauntlet.itest.ts`* — and the point of 4.15's rule is
that the count happens early enough to change the sequencing.

**`targets.ts` IS 13 PAGES AND NEEDS NO ROW**, checked rather than assumed: it keys
on method and path, and this chapter adds no route and renames no token.

**AND `users.controller.ts` WAS 2 AND IS 1.** One titled block in the appendix, not
two. The earlier column was never derived from the tree.

**THE FIGURE HAS NOW MOVED THREE TIMES**: the milestone's plan said 84 (omitting
`users.schema.ts`), analysis pass 1 said 107 across 9 (adding three module files the
pipe does not need), pass 2 said 88 across 6, and pass 3 measures **101 across 7**.
Only the last two came from running anything, and this is the first with its method
written down. **A count nobody can reproduce is a count that moves.**

## R7 — What this chapter must not do

**It must not remove the uuid.** 157 call sites and every published client depend on
it, and a deprecation needs a window, a warning and a version — none of which belongs
in a chapter whose subject is making the identity work.

**It must not touch the other four nouns.** Messages, media objects, webhooks and
environments have no `external_id` column, measured against `information_schema`, so
a Relay identifier is the only identifier they have.

**And it must not fix the swallowed 500 cause.** R1 found it; 058-3 counts 22 routes
that can produce one. A chapter that fixes the logging for one route and leaves 21 is
worse than one that records the class.

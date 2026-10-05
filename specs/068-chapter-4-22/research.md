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
| **C** | shape-based: parse as a uuid → try key then identity; otherwise identity only | the same as A for uuid-shaped input | one query in both common cases |

**DECISION: C, WITH B's TIE-BREAK.** A value that cannot parse as a uuid can only be
an identity, so it costs one query and the cast never happens — **which is what
removes the 500.** A value that does parse is ambiguous in principle, and the
tie-break goes to the **identity**, because a customer who named a channel should
reach the channel they named. The alternative strands them permanently with no error
they can act on.

**Alternatives considered.** *A* — simplest to describe and it is the one that
strands a customer. *B everywhere* — correct and costs a failed identity lookup on
every one of the 157 existing uuid call sites. *Refuse ambiguity with a 409* —
honest, and it turns a working call into a broken one for a customer who did nothing
wrong.

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

Thirteen routes name a channel — 8 on `channels.controller.ts`, 5 under
`messages.controller.ts`'s `v1/channels/:channelId/messages` prefix — plus the read
position route on `users.controller.ts`. **There is no chokepoint**: `channelId` is
passed into ten different repository methods.

| | design | fence cost | verdict |
|---|---|---|---|
| middleware | one registration in `app.module.ts` | 75 pages | **cannot work** |
| **pipe** | `@Param("channelId", ChannelIdPipe)` | **84 pages · 10 hunks · 5 files** | **chosen** |
| service layer | resolve at the top of each method | 91 pages, ~13 sites | rejected |
| repository | each method accepts either | spreads the ambiguity into ten queries | rejected |

**THE MIDDLEWARE IS CHEAPEST AND NEST RUNS IT BEFORE GUARDS**, so it has no principal
and cannot scope the lookup to an environment. That is disqualifying rather than
inconvenient: an unscoped resolution is a cross-tenant read.

**THE PIPE GETS THE SCOPE BY CONSTRUCTION.** An injectable pipe can take the
request-scoped `Repository`, whose constructor already requires an `environment_id` —
the same mechanism chapter 4.21 found had kept six of seven stores correct without
anyone remembering. Everything downstream keeps receiving a uuid, so the ten
repository methods are untouched.

## R5 — The users side is one line, and it is where 4.23's ADR rests

All eight user routes take the identity and the upsert returns no uuid, measured:

```
POST /v1/users   -> external_id, status, display_name, avatar_url, metadata, kind, description
POST /v1/channels -> id, external_id, type, name, metadata            <- uuid first
```

The single leak is the listing cursor — `users.schema.ts:194`, base64 of
`{a: last_activity_at, id: users.id}` — whose own comment reads *"OPAQUE IS NOT
SECURITY. Base64 of JSON is readable by anyone who wants to read it."*

**AND IT IS LOAD-BEARING FOR THE CHAPTER AFTER THIS ONE.** ADR-37's reversal
condition is *"if `users.id` ever becomes resolvable to a person by a party outside
the platform"*, and names this cursor as the one live edge. Closing it narrows that
condition from a known exception to none.

**WHAT REPLACES IT IS THE PLAN'S QUESTION, NOT THIS SECTION'S.** A keyset cursor
needs a tiebreak that is unique and ordered; `users.id` was chosen because it is
both. An `external_id` is unique per environment and the cursor is already
environment-scoped, so it is a candidate — and FR-007 requires that a cursor issued
before this chapter keeps working or is refused by name, which is a version field or
a dual-read.

## R6 — What the fence chain charges, counted now

```
                                 pages   appendix   touched
channel-id.pipe.ts                   0   0          NEW FILE
channels.controller.ts               8   0          8 @Param edits
messages.controller.ts              19   1          5 @Param edits
users.controller.ts                  5   2          1 @Param edit + the cursor
users.schema.ts                      4   0          the cursor payload
repository.ts                       52   7          one resolution read
                                 -----   --
                                    88  10          across 6 files
```

**88 pages, not the 84 the milestone's plan estimated** — that figure omitted
`users.schema.ts`, which the users half needs. 4.15's rule earns its place again:
count the bill before the work, and expect it to grow by whatever the first count
forgot.

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

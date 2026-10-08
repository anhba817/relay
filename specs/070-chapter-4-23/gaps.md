# Gaps — feature 070, chapter 4.23, "The channel a socket names"

Numbered. The carried ledger is re-measured rather than copied, which is the only
way four of 043's twenty-three were found to be wrong.

## NEW

### 070-1 · Webhooks are the third surface, and nobody's chapter

`services/api/src/outbox/event.ts` carries `channel_id` as a Relay identifier in
three payload types — `MessageCreatedData` (:20), `MessageDeletedData` (:66),
`MembershipChangedData` (:83) — **8 occurrences, 6 emitted event types**, delivered
to the customer's own endpoint by `dispatcher/deliver.ts:79`.

**And the comment above the first states the rule the field below it breaks**, more
plainly than `internal.ts` did for the socket: *"A message as the PUBLIC api returns
it. Consumers are customers: they get external ids and the field names the REST
surface uses. `user_id` does not cross this boundary."* `MembershipChangedData` goes
further — its `user` is annotated *"The EXTERNAL id. Never `users.id`"* and sits
beside a channel's internal one. **Third time in three chapters for that shape.**

**It is a lookup-table burden, not a dead key.** Since 4.22 thirteen REST routes
take either form, so a customer CAN act on the uuid — unlike 068-3's
`members[].user_id`, which no route accepted. What fails is Journey 3 Stage 1's
*zero lookup tables*, on the surface a customer's backend integrates with.

**OPEN, and recorded rather than built.** Named in SRS 1.30, ADR-38 in both homes,
`docs/03` Stage 2 and the chapter's closing section. Widening this chapter to cover
it is what the plan's complexity table warns against — and a third surface arriving
is the same warning by a different road.

### 070-2 · `typing.itest.ts` is not a flake in the dismissible sense

Five observations, **four different test names, one signature every time**:
`untilTyping` (:469) timing out with *"only 0 of 1 typing frames for <uuid>; saw
connection.ack"*.

    CI 37482921334          "delivers one frame to a member on another instance"
    local, full lane        "sends nothing at all after the signal, until another"
    local, file alone, run 1    23 of 23 PASSED
    local, file alone, run 2    "sends nothing to the signaller's OTHER connection"
    local, full lane again  "delivers one frame to a member on another instance"

068 met it twice and recorded a flake both times. **Three failures in five runs
across two environments, on four different assertions that share one wait**, makes
that reading unsafe. The shape — a typing frame that never arrives while the ack
does — points at the subscription not being established before the signal is
published.

**OPEN.** Not this chapter's subject, and the whole gateway lane went 238 of 238 at
the end of Phase 5 — **which is one green run and not evidence the flake is gone**
(045: *"8 of 8 green was not evidence"*).

### 070-3 · The coverage lane fails 18 tests that pass in their own lanes

`pnpm coverage` runs 156 files serially in one process and reported **18 failed of
2,312** across eight suites. Every one of those suites, run in its own lane against
the same tree: **88, 16, 24, 32 and 46 — all EXIT 0.**

So the failures belong to the lane, not to the tree, and none is in a file this
chapter changed. 063-4's family with evidence on both sides rather than a
resemblance.

**OPEN.** The consequence is that three coverage thresholds cannot be read:
`services/ingester/shape.ts` and `clickhouse.ts` (062's child-process blindness,
made worse by `ingest.itest.ts` failing in the lane) and
`services/gateway/src/presence.ts` at functions 96.96 against a pin of 100. **No pin
was moved** — lowering a ratchet to fit a number from a red lane is the failure the
ratchet exists to prevent.

### 070-4 · A hand-written cast is a hole in the type instrument

Changing `channel_ids` to pairs made the compiler name thirteen construction sites.
It named none of the two in `internal.itest.ts` that read the response as
`(await res.json()) as { channel_ids: string[] }` — **a shape asserted rather than
read**. Both failed at runtime in the api lane instead.

**CLOSED as a measurement** (they parse the schema now), **open as a lesson**: the
reach of a type change is the set of places that obtain the type, and a cast leaves
that set silently.

### 070-5 · The fence bill cannot see what the compiler will find

Predicted ~50 pages across 7 files at specification, 83 across 9 at research, 83+
across 11 at analysis pass 1, 98 across 12 at T005 — and the chain charged for
**20 files**. The eight it missed are TESTS: the type change named every stub that
constructs a session response, and eight of those are published.

**CLOSED as a measurement.** 4.15's rule, fifth time in one feature, and the first
time the extra files came from the compiler rather than from reading.

### 070-6 · A derived-target suite is green by construction against a value change

`services/gateway/src/isolation.itest.ts` derives its attack list from
`frameSchema`'s members (`:165`, `:877–910`), so a frame type added and forgotten is
attacked automatically. **This chapter adds no frame type** — it changes what a field
carries, and three of the structures it changes are not frame types at all.

Three attacks were written by hand (T042a). **OPEN as a property**: the next chapter
that changes a value rather than a shape inherits the same blind spot, and nothing
in the suite announces it.

### 070-7 · A stale `dist` makes a cross-version comparison look like a catastrophe

To classify 070-3 the platform was checked out at `part4-ch22` and the coverage lane
re-run: **123 failed of 2,302**, all in suites that spawn an api. The api's `dist`
was built from THIS chapter's source; the gateway was at the tag; the old gateway
read `session.channel_ids` from a new api and got `undefined`.

**`isolation-fixtures.ts:150` spawns the api from `dist`** — the hazard analysis pass
15 found, here from the other side. **CLOSED as a measurement** (the comparison was
withdrawn, the tree restored and rebuilt), open as a rule: a source checkout without
a rebuild compares two different platforms.

### 070-8 · The uuid-shaped identifier stopped being theoretical

4.22 measured **0 of 41,772** channels with a uuid-shaped `external_id` and published
the tie-break as a precaution. Four days later:

    uuid-shaped external_id                          19 of 44,574
    of those, equal to ANOTHER channel's id          19

So nineteen strings are simultaneously one channel's identity and another's key.
**CLOSED as a decision** — it settles T011 by measurement: no shape test separates
the forms in a resume cursor, so both are accepted and the identity wins.

### 070-9 · `git add -A <submodule>` from the superproject stages a gitlink

The commit meant to carry the chapter carried `baseline.txt` alone; the tutorial's
seven changed files sat uncommitted while every gate passed **against the working
tree**. **CLOSED** by committing inside each submodule first. Worth keeping because
a green gate is a claim about what is on disk, and the push order (submodules, then
the superproject) only protects a state that was committed in the first place.

## CARRIED, RE-MEASURED

| | |
|---|---|
| **068-1** the real-time surface addresses channels by uuid | **CLOSED. This chapter.** FR-RTM-11, the map at the client edge, and a socket that never says a uuid |
| **068-2** a pipe answers before every check the handler makes | holds, and the mirror was built: `send` translates and **never refuses** — a value it cannot name is passed through so the api refuses it in its own order |
| **068-4** the 500's cause is unlogged on every route | untouched |
| **068-5** clamav's seven-day bound against a seven-day tag | **re-measured: `daily.cld` is dated today, 10:27, against an image still tagged `clamav/clamav:1.5`.** The healthcheck's reload is working; the debt 068 wrote down — a probe repairing what it measures — is unchanged |
| **068-6** two lanes on one broker steal each other's messages | not reproduced: every lane was run alone this feature, which is 068-9's rule followed rather than a measurement |
| **068-7** a fence bill cannot see work that has not happened | **paid again, and see 070-5**: the bill moved four times and was still short by eight files |
| **068-8** ADR-37 sits alone, 1,700 lines from the other ADRs | untouched |
| **068-9** the sealed suite and the api lane want opposite machine states | **paid**: the battery needs the composed services DOWN and the quickstart needs them UP, so they ran in sequence rather than together |
| **067-3** `git diff <tag>..HEAD` reads committed state | **paid, and it found one**: the one-dot form caught `FR-029` in a published revision row |
| **065-4** a single-mutation probe measures the defence, not the arm | **fourth chapter running.** Deleting the scope turned **0 of 35** gauntlet tests red and **1 of 85** in the suite built for the question |
| **063-4** feature-local ids in `docs/` | **re-measured: 30 distinct `FR-0NN` ids, every one resolving to no SRS clause** — 22 at 4.17, so eight more have arrived since. This feature added one and removed it |
| **062-12** unpinned files a re-measure cannot see | no pin added or moved; see 070-3 |
| **050-8** the ingester has no runner | untouched, and it is why `ingest.itest.ts` spawns its own |
| **043-1** an untitled fence is never compared | **paid**: the two Part 2 transcript lines this chapter makes historical sit in an untitled fence, outside every gate, and are left deliberately (T049a) |

## WHAT THIS FEATURE PAID FOR TWICE

**Counting the wrong thing, twice in one premise.** Seven `channel` fields missed
three structures that name channels without the word; twenty-one `channel:` writes
counted eleven log lines, six publishes and a comment as if they were frames, and
missed the one frame the gateway forwards without writing. Both numbers were right.
Both conclusions were wrong. **The fix was to open the sites, not to grep harder.**

**And the record kept being the thing that was wrong.** `FR-029` reached a published
document out of a code comment; the fence bill was short four times; a MEASURED
label survived seven analysis passes on a quickstart section that could not connect.
Every one was found by running something rather than by reading it again.

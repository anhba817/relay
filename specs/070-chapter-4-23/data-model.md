# Data model — chapter 4.23, "The channel a socket names"

No table changes, no migration. One service learns something the one beside it
already knew.

## The two spaces, one service further out

Chapter 4.22 drew this line at the request boundary. This chapter draws the same
line at the gateway's client edge.

```
                    IDENTITY                     KEY
                    what the customer named      what Relay minted

REST       after 4.22   13 routes take either    accepted, 173 call sites
socket     today        nothing                  every frame, every send
socket     after this   every frame, every send  accepted inbound (R4)

behind the edge, unchanged either way
  subjectForChannel · subjectForChannelRevision · subjectForPresence
  subjectForTyping  · subjectForChannelMembership            keys
  the resume cursor's storage and comparison                 keys
  internalSendRequestSchema.channel_id                       z.string().uuid()
  registry.subscribersOf(channelId)                          keys
  connection.channelIds                                      keys
  marks, built from the backfill response                    keys
  lastPublished, the typing debounce                         keys
```

**AND ONE STRUCTURE IS ON BOTH SIDES OF THE EDGE, WHICH PASS 3 FOUND.**
`connection.buffer` holds `Message[]` — the frames a resuming client is about to
receive — and two internal comparisons index them by channel:

```
resume.ts:111   flushable  marks[frame.channel] ?? 0
                a lost mark means every buffered frame is re-delivered
session.ts:662  the revocation filter  m.channel !== change.channel
                a lost match means a revoked channel's backlog is flushed (FR-029)
```

**Both are silent and both are user-visible**, so *where* the translation happens
decides whether they survive. Translating at the outermost `send` leaves every frame
in the buffer keyed and both comparisons intact; translating where the frame is
built does not.

## The map, which is two maps

**ONE DIRECTION IS NOT ENOUGH, AND ANALYSIS PASS 2 IS WHERE THAT SURFACED.** The
first version of this section specified `Map<key, identity>` and FR-002 asks for the
other direction: a client that may SAY the identity means three sites have to turn an
identity back into a key.

```
key -> identity    the 21 outbound sites, the ack's three structures      READ
identity -> key    session.ts:1620  channel_id into internalSendRequestSchema
                   session.ts:1571  signalTyping, before subjectForTyping
                   resume.ts:80     the cursor filter, against a key set
```

**The key→identity map is authoritative** — it is built from the session response,
one row per channel — and the inverse is derived from it at the same moment. Two
identities colliding on one key is impossible; **two keys colliding on one identity
is impossible too, because of `unique("channels_environment_id_external_id_unique")`
in `schema.ts`** — unconditional, not partial, checked at analysis pass 19. That is
what makes the inverse safe to derive rather than a lossy second source.

```
input:  the session response at connect, scoped by `users.environmentId` in
        `channelsForUser` — NOT by `channels.environmentId`; the query reaches
        channels through `members`, and a member row cannot cross environments
        [{ key, identity }, …] for the channels this user may hear

held:   on the registry's Connection, beside the `channelIds: Set<string>` at
        registry.ts:25 and the channel-keyed `revisions` at registry.ts:21
        — NOT auth.ts:103, which is `string[]` one hop earlier (auth.ts:42)

read:   at the 21 sites that write `channel:` onto a client frame
        18 session.ts · 1 fanout.ts · 1 resume.ts · 1 typing.ts
        at the 22nd, one call away in the revocation backstop (session.ts:741)
        and at the three ack structures that name channels without a field

write:  at connect, and on whatever Phase 2 decides for a mid-session join
```

**AND `connection.channelIds` STAYS A SET OF KEYS.** Three membership tests read it
and all three invert silently if it ever holds identities:

```
session.ts:1493   signalTyping's guard — returns with no frame and no log
session.ts:729    reread's set difference against api.memberships()
resume.ts:80      the cursor filter
```

The second is the loudest failure of the three: a `channelIds` holding identities
and an `api.memberships()` returning keys makes **every channel look both removed
and added on every timer tick**, and the client is told so.

**SCOPED BY ARRIVAL, NOT BY A PREDICATE.** The session response is built for one
principal by an api that already knows the environment, so nothing in the gateway
applies a scope and nothing in the gateway could forget to. That is the property —
and it is also why **no test in this service would notice if the scope were dropped
upstream**, which FR-006's probe exists to measure rather than assume.

## The miss

A key the map cannot name. Three sources:

```
a channel joined mid-session           R3's hole, and Phase 2's decision
ALL_CHANNELS, the ban sentinel "*"     not a channel; special-cased BEFORE the map
a bug                                  which is why the fallback matters
```

**THE FALLBACK MUST NOT BE THE KEY.** Emitting it would hand a client the uuid this
chapter exists to stop handing them, on exactly the channels they most recently
joined — the worst case wearing the shape of a safe default. What it should be
instead is Phase 2's to decide and the chapter's to publish.

## What a client sees change

```
at connect       the channel list is identities
every frame      `channel` is the identity
a send           takes the identity, and still takes a key (R4)
a resume cursor  keyed by identity going out; both forms accepted coming in,
                 because every connected client across the deployment holds one
                 keyed by uuid and `cursorSchema` is z.record(z.string(), …)

and the ack's other two structures, which a count of `channel` fields missed
  revisions      z.record(channel, number) — on EVERY ack, zeros included
  truncated      string[] of channel ids, built at session.ts:1354 as
                 [...connection.channelIds]
```

**THE INBOUND CURSOR IS FILTERED, NOT PARSED.** `resume.ts:80` is
`Object.entries(cursors).filter(([channelId]) => channelIds.has(channelId))`, so a
key the set does not hold is **dropped silently** — no error, no refusal, no log. An
identity-keyed cursor meeting a key-holding set resumes nothing and says nothing,
which is the one outcome FR-003 forbids, reached by a filter rather than by a parse
failure. Whatever Phase 2 decides about telling the two forms apart has to be
decided at that line.

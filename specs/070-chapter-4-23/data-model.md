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
```

## The map

```
input:  the session response at connect, already scoped to this principal
        [{ key, identity }, …] for the channels this user may hear

held:   on the connection, beside the `channelIds: Set<string>` that
        auth.ts:103 already builds from the same response

read:   at the 21 sites that write `channel:` onto a client frame
        18 session.ts · 1 fanout.ts · 1 resume.ts · 1 typing.ts

write:  at connect, and on whatever Phase 2 decides for a mid-session join
```

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
```

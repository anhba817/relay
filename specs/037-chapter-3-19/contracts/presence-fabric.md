# Contract — the presence fabric

**Scope:** the subject grammar and the payload that crosses Redis between gateway instances.
Nothing in this contract is visible to a client.

---

## 1. Subject grammar

    presence:{channel_id}

Built in `packages/protocol/src/fanout.ts` and nowhere else, beside the existing
`subjectForChannel`. The package's own comment already records why this rule exists: a consumer
that assembles its own subject filter receives nothing the day the grammar changes.

    export function subjectForPresence(channelId: string): string

**Naming.** Not `subjectFor` — that name is taken by `internal.ts`'s event-spine helper, and
chapter 3.18 recorded the collision when it moved `subjectFor` into this package and got
`Module '"@relay/protocol"' has already exported a member named 'subjectFor'`. The two grammars
are genuinely different: the spine's subject carries the tenant, the fan-out's carries only a
channel.

**One presence subject per channel, subscribed in lockstep with the message subject.** A channel
becomes interesting to an instance when its first local member connects and stops being
interesting when the last leaves. That reference count already exists in the fan-out and is not
shared: `presence.ts` keeps its own, over the same channel ids.

**Declared cost:** a user in N channels now issues 2N subscriptions at connect rather than N.
Phase 3 measures it. `ioredis` takes a variadic `subscribe(...)`, so the round trips do not
double even though the subscriptions do.

## 2. Payload

    {
      "user": "<external user id>",
      "state": "online" | "offline",
      "transition": "<uuid>"
    }

Validated with a `z.strictObject` in `packages/protocol/src/presence.ts`, exported as
`presenceFabricSchema`.

**Validated on receipt, not only on publish.** The fabric is inside the trust boundary and frames
are still parsed — `services/gateway/src/fanout.ts:77-79` states the reason and it applies unchanged: *"inside" is one
compromised dependency away from "outside", and a malformed payload must not reach a client.* A
payload that fails to parse is one log line and no frame.

**`strictObject`, so an unknown field is a rejection.** Constitution VI asks for unknown fields
rejected on write; this is the internal equivalent, and it means a future field cannot be added on
one side of a rolling deploy and silently ignored on the other — it fails loudly instead.

## 3. What must not happen

| Rule | Why it holds structurally |
|---|---|
| A presence payload is never delivered as `message.created` | It is published on a subject no message subscriber subscribes to |
| A message is never delivered as `presence.changed` | Same, in reverse |
| `transition` never reaches a client | The delivery path constructs the wire frame from `user` and `state` only |
| A presence frame is never buffered by the resume path | Presence delivery does not consult `connection.phase` or `connection.marks`; both are message-only (research R10) |

The first two are the reason for a second subject rather than an envelope. Under an envelope they
would be properties a test has to defend; here they are properties of the topology.

## 4. Mixed-version deploys

An old gateway instance never subscribes to `presence:{channel_id}`, so it receives nothing it
cannot parse and logs nothing. A new instance publishing during a rolling deploy simply reaches
fewer watchers until the old instances drain.

The enveloped-subject alternative behaves worse here and it is worth recording why: an old
instance subscribed to `chan:{id}` would receive presence payloads, fail
`messageCreatedSchema.shape.payload`, and emit `fanout.invalid_payload` for every transition on
every channel for the length of the deploy.

## 5. At-most-once, and no resume

Redis pub/sub delivers to whoever is subscribed at the moment of publish and to nobody else.
A presence frame that misses a subscriber is gone.

For messages this is recoverable — sequences live in Postgres, cursors live with the client, and
chapter 2.7's resume turns any gap into a backfill. **Presence has none of that and must not be
given any** (FR-026). There is no sequence to compare, no cursor to resume from, and no snapshot
on connect (spec, out of scope). A client's roster is empty until the next transition it hears.

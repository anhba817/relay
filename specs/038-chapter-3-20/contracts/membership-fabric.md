# Contract — the membership fabric

*What crosses between gateway instances, what crosses to a client, and what crosses to the event
spine. Three shapes for one state change, and the differences are the contract.*

---

## The subject grammar

```ts
// services/gateway/src/membership.ts — the factory's options
export interface MembershipOptions {
  url?: string;
  logger: Logger;
  /** The backstop's re-read period. Defaults to production's; a test injects a
   *  short one, because sixty seconds does not fit in a 45 s package. */
  rereadIntervalMs?: number;
}
```

```ts
// packages/protocol/src/membership.ts
export function subjectForChannelMembership(channelId: string): string;   // member:{channel_id}
export function subjectForUserMembership(
  environmentId: string,
  user: string,
): string;                                                                // member:{env}:{user}
```

**Named for what they address, not for what they carry.** `subjectForChannel` and
`subjectForPresence` already exist in this package and `internal.ts` exports a bare `subjectFor`;
chapter 3.18 paid for one collision in that family with
`Module "./internal.js" has already exported a member named 'subjectFor'`.

**Invariant to assert in a unit test**: for any id, all four of `subjectForChannel`,
`subjectForPresence`, `subjectForChannelMembership` and `subjectForUserMembership` are pairwise
distinct. Cross-kind mis-delivery is a property of the topology here, not something tests defend,
and the test exists to prove the topology holds.

---

## The fabric payload

```ts
export const membershipFabricSchema = z.strictObject({
  environment: z.string().min(1),
  channel: z.string().min(1),
  user: z.string().min(1),
  change: z.enum(["added", "removed"]),
});
```

`strictObject`, for chapter 3.19's reason repeated: an unknown field is a rejection rather than a
silent ignore, so a field added on one side of a rolling deploy fails loudly on the other instead
of being dropped.

**`environment` is on the fabric and not on the wire.** A receiving gateway checks it against the
connection it is about to act on and refuses a mismatch (FR-007). A client already knows its own
environment, and putting it on a socket frame would be the first time this platform sent a tenant
identifier to a client for no purpose.

**A ban carries `channel: "*"` — or a separate payload shape, and this is the one open question in
this contract.** The phase that builds US4 decides it. For `"*"`: one schema, one parse, one code
path. Against: `channel` is `z.string().min(1)` and a sentinel inside a string is the kind of
thing that reads as a channel id in a log line for a year.

---

## The wire frame — unchanged since chapter 1.3

```ts
{ type: "membership.changed", payload: { channel, user, change } }
```

`packages/protocol/src/frames.ts` is **not edited**. `frames.test.ts` already asserts this shape
and chapter 3.12's gauntlet already classifies it outbound. What this feature changes is that the
frame is produced.

---

## The outbox event — FR-WHK-02's spelling, not this chapter's

```ts
{ id, type: "channel.member_added" | "channel.member_removed",
  environment_id, occurred_at, data: { channel_id, user } }   // user: the EXTERNAL id
```

Written inside the transaction that wrote the membership row, by the repository, complete —
*"the relay moves bytes, it does not author them"* (`services/api/src/outbox/event.ts`).

**`user` is the external id, and the repository does not have one.** `MessageCreatedData`'s
comment fixes the boundary — *"Consumers are customers: they get external ids and the field names
the REST surface uses. `user_id` does not cross this boundary"* — while `addMember`,
`removeMembers` and `banUser` all take `users.id`. The message path solved this by having its
caller pass `userExternalId` down (`repository.ts:3710`), and this path takes the same shape: the
service already builds the external→internal map, so it passes both.

The alternative implementations are both wrong and both easy: **build the event outside the
transaction** and constitution II is violated, or **put the uuid in `data.user`** and a customer's
webhook carries an identifier this platform has never exposed.

**This widens a literal type.** `OutboxEvent["type"]` is `"message.created"` today, not a union.
Widening it is visible to every consumer that narrows on it, which is the shape of change a
typecheck catches and an integration lane does not.

---

## Who subscribes to what

| Subject | Subscriber | Reference-counted by |
|---|---|---|
| `member:{channel_id}` | every gateway instance holding a member of that channel | channel |
| `member:{env}:{user}` | every gateway instance holding a connection for that user | user |

**The subscription count this adds, to be measured and not predicted.** Chapter 3.19 measured its
own with `CONFIG RESETSTAT` then `INFO commandstats` and read `cmdstat_subscribe calls=12` for two
instances over three channels — six fan-out, six presence. The prediction here is 18 plus one per
distinct connected user per instance. Record the reading; a prediction that agrees with a
measurement is worth having and a prediction quoted as one is not.

---

## The api side

The publisher lives in `services/api/src/membership/` and is shaped like
`services/api/src/fanout/publisher.ts` — chapter 3.18's, which already solved the problems this
one has. **It is called from the controllers, not the services**, for the same reason the message
publish is at `services/api/src/messages/messages.controller.ts:199`: `ChannelsService`'s
constructor takes only the `Repository`, so it holds no request id and no logger, and the failure
event needs both. Four call sites — bulk add, join, bulk remove, ban — behind one helper:

- it swallows its own errors and resolves, so a failed publish cannot fail the write it follows
  (FR-016)
- **and therefore the log line is the requirement's evidence** (FR-015). Chapter 3.18's own trap:
  *"the send returned 201 while Redis was down"* is true of a publisher that does nothing at all.
- **and it logs its successes too** (FR-031, FR-032). Three names, and no fourth:

      membership.published        a change went onto the fabric — channel, external id,
                                  no content, no token (constitution VI)
      membership.failed           the publish threw and was swallowed — op, error
      membership.invalid_payload  a body that is not JSON, or JSON the schema rejects

  Every log requirement this chapter had until analysis pass 8 was about failure, because every
  argument it inherited was about failure. An operator who can only see the mechanism breaking
  cannot tell a quiet system from a dead one.
- it fails fast rather than queueing. Default `ioredis` retries forever and queues, so against a
  dead store a publish neither succeeds nor rejects and the documented failure path is never
  taken — measured twice now, in 3.18 and again in 3.19.

**One client, one close owner, one module.** The publisher is not a bare factory: it needs an
injection token, a provider, and a `Lifecycle implements OnModuleDestroy` — `limits.module.ts:10`
states the rule and six modules follow it, because *"a `close()` nothing calls is a leaked handle
in a service that boots once per integration suite"*. Two controllers need it, so it lives in one
module both import rather than being registered twice, which would open two connections for one
job. **It is not exported beyond that**, for the reason `MESSAGE_PUBLISHER` is not: a module that
reuses another's providers wholesale would make the publisher injectable somewhere it must not be.

`ioredis` is a lint-restricted import (constitution I). The exemption for the api's publisher
already exists; the gateway's new module needs its own, and **the justification is presence's
rather than the fan-out's**: this client composes keys and subjects from the authenticated
connection's own environment id. Chapter 3.19's entry states the distinction and it transfers.

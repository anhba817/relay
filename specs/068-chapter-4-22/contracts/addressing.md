# Contract — what each route accepts

The chapter adds no route and no field. It widens what thirteen existing path
parameters accept, and the contract is the list plus the refusals.

## The thirteen

```
GET    /v1/channels/{channel}
POST   /v1/channels/{channel}/archive
DELETE /v1/channels/{channel}/archive
POST   /v1/channels/{channel}/join
POST   /v1/channels/{channel}/members
POST   /v1/channels/{channel}/members/remove
PATCH  /v1/channels/{channel}/members/{userExternalId}
POST   /v1/channels/{channel}/messages
GET    /v1/channels/{channel}/messages
PATCH  /v1/channels/{channel}/messages/{messageId}
DELETE /v1/channels/{channel}/messages/{messageId}
GET    /v1/channels/{channel}/messages/{messageId}/edits
PUT    /v1/users/{externalId}/channels/{channel}/read
```

`{channel}` accepts **the customer's identifier or Relay's**. Everything else on
these paths is unchanged: `{userExternalId}` was already an identity and
`{messageId}` is a key with no identity to offer.

**THE PATH PARAMETER IS RENAMED IN THE DOCUMENTATION AND NOT IN THE CODE.**
`:channelId` stays as the route token because renaming it would touch every
`@Param` string twice; what changes is what the documentation calls it, because
`channelId` is now a misleading name for something that is usually not an id.

## Refusals

| condition | status | code |
|---|---|---|
| an identifier no channel in this environment has | 404 | `not_found` |
| *(the message is constant across all four — FR-TEN-05)* | | |
| a uuid no channel in this environment has | 404 | `not_found` — unchanged |
| a channel belonging to another tenant, by either form | 404 | `not_found`, **indistinguishable from absent** |
| a malformed value of any shape | 404 | `not_found` — **this is the 500 today** |

**NO INPUT TO THESE ROUTES MAY PRODUCE A 5xx.** Today `GET /v1/channels/order-88412`
is `500 internal_error`, because the value reaches a uuid-typed column and Postgres
raises `invalid input syntax for type uuid` — which the api does not log. After this
chapter a value that cannot be a uuid is never cast, so the error cannot arise.

## What a client sees that is new

**Nothing, unless it chooses to.** The 157 existing call sites that pass a uuid take
the same path they take today, by construction (R2's shape test). No response shape
changes, no header, no status for any input that works now.

## The ambiguous input

An `external_id` may itself be a uuid — legal, and **0 of 41,768 channels have one**.
When a path segment parses as a uuid and both spaces could answer:

**The identity wins a true tie**, because a customer who named a channel must be able
to reach the channel they named; the other channel stays reachable by its uuid from
any caller holding it. The alternative strands a customer permanently with no error
they can act on. **That is the contract.** Which procedure delivers it — one query
with an explicit preference, or the identity looked up before the key — is an
implementation choice T009 makes and R2 prices; a caller cannot tell them apart.

A value that **cannot** parse as a uuid is an identity, costs one query, and is never
cast. That is the clause that removes the 500, and it is independent of the
tie-break.

## The cursor

**There is no `GET /v1/users` listing.** The opaque cursor belongs to `GET
/v1/users/{externalId}/channels` and encodes `(last_activity_at, channels.id)` — a
**channel** uuid, which every route in the table above accepts. ADR-37 names it as
the one live edge on its reversal condition; that is the thing this chapter amends
rather than closes.

| condition | behaviour |
|---|---|
| the cursor as it is today | unchanged, unless the sweep gives a reason |
| a cursor issued before this chapter | **works, or is refused with a named cause** — if anything changes at all |
| a cursor a caller constructed | outside the contract, as its own comment already says |

**A silently wrong page is the one outcome forbidden**, and the cheapest way to
guarantee it is to change nothing here. Whether anything changes is FR-006's sweep
to decide.

## What this contract does not offer

- **No deprecation of the uuid.** 157 call sites and every published client hold
  one. A window, a warning and a version belong to a later chapter.
- **No change to the other four nouns.** Messages, media objects, webhooks and
  environments have no customer identifier to honour.
- **No new error code.** `not_found` is in `codes.ts` and in
  `docs/08-error-reference.md` already.
- **No fix for the unlogged 500 cause.** R1 found it; 058-3 counts 22 routes that can
  produce one, and repairing one of 22 is worse than recording the class.

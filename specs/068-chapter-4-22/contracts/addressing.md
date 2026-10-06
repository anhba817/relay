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

**AND THIS LIST IS THE WHOLE OF IT, WHICH IS NARROWER THAN FR-001's FIRST WORDING.**
Three internal doors also name a channel and are deliberately excluded:

| route | names a channel in | stays a uuid because |
|---|---|---|
| `POST /internal/messages` | body `channel_id` | the gateway's send door; `internal.ts:28` types it `z.string().uuid()` |
| `POST /internal/backfill` | body `channel` | the same contract, the same reason |
| `POST /internal/dispatch/expand` | body `channel` | the dispatcher's, not a customer's |

`packages/protocol/src/internal.ts` states the rule for that contract itself —
*"internal uuids are the api's business"* — so this is the published position rather
than an omission.

**AND THE REAL-TIME SURFACE IS NOT IN THIS CONTRACT AT ALL.** Every client frame
carries `channel: <uuid>`, and the session response hands a connecting client a list
of channel uuids. A customer on the socket still keeps the mapping this chapter
removes from REST. That is published as a limitation (T050) and handed to 4.23, not
fixed here.

**THE PATH PARAMETER IS RENAMED IN THE DOCUMENTATION AND NOT IN THE CODE.**
`:channelId` stays as the route token because renaming it would touch every
`@Param` string twice; what changes is what the documentation calls it, because
`channelId` is now a misleading name for something that is usually not an id.

## The clause behind it

**There is none today, and that is a finding rather than an oversight by this
contract.** FR-CHN-01 covers creating a channel with a customer-supplied identifier
and FR-CHN-02 covers that creation being idempotent on it. **Nothing in FR-CHN-01
through 10 says the identifier may then be used to name the channel.** `docs/03`
Journey 3 Stage 2 asserts *"channel retrieval by external ID"* and cites no clause,
which is the same gap seen from the journey's side.

**FR-CHN-11 is what this contract is the contract for** (T027), written before the
pipe, because constitution VI's first bullet says new behaviour gets a requirement
first.

## Refusals

| condition | status | code |
|---|---|---|
| an identifier no channel in this environment has | 404 | `not_found` |
| *(the message is constant across all four — FR-TEN-05)* | | |
| a uuid no channel in this environment has | 404 | `not_found` — unchanged |
| a channel belonging to another tenant, by either form | 404 | `not_found`, **indistinguishable from absent** |
| a malformed value of any shape | 404 | `not_found` — **this is the 500 today** |
| a malformed `:messageId` on the three routes that take one | 400 | `invalid_request`, `field: "messageId"` |

**THE LAST ROW CLOSES A GAP RATHER THAN RECORDING ONE.** `PATCH` and `DELETE
…/messages/{messageId}` and `GET …/messages/{messageId}/edits` hand their second path
parameter to `messages.id`, a uuid column with no shape check, so
`…/messages/not-a-uuid` raises `22P02` exactly as the channel cast does. Gap **058-3**
counts sixteen routes with that defect — **thirteen taking `channelId`, three taking
`messageId`, one `mediaId` validated at 4.12**. The pipe closes the thirteen by never
casting; three lines of `z.uuid()` in a file this chapter already opens close the
rest. **16 to 0.**

**NO INPUT TO THESE ROUTES MAY PRODUCE A 5xx, IN ANY PATH PARAMETER.** Today `GET /v1/channels/order-88412`
is `500 internal_error`, because the value reaches a uuid-typed column and Postgres
raises `invalid input syntax for type uuid` — which the api does not log. After this
chapter a value that cannot be a uuid is never cast, so the error cannot arise.

## What a client sees that is new

**Nothing, unless it chooses to.** The 173 existing call sites that pass a uuid take
the same path they take today, by construction (R2's shape test). No response shape
changes, no header, no status for any input that works now.

## The ambiguous input

An `external_id` may itself be a uuid — legal, and **0 of 41,772 channels have one**.
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

- **No deprecation of the uuid.** 173 call sites and every published client hold
  one. A window, a warning and a version belong to a later chapter.
- **No change to the other four nouns.** Messages, media objects, webhooks and
  environments have no customer identifier to honour.
- **No new error code.** `not_found` is in `codes.ts` and in
  `docs/08-error-reference.md` already.
- **No fix for the unlogged 500 cause.** R1 found it: a 500 is logged as a status
  with no `22P02` and nothing an operator can act on. **That is a different
  population from 058-3** — this contract closes every route where a malformed path
  parameter *causes* a 500, and says nothing about how the remaining 500s are
  *logged*, which is every route and has never been counted.

# Contract — `/internal/session`, extended

The private half. Gateway to api, on the one call the gateway already makes at connect.

---

## Response, with the new field

    {
      "environment_id": "…",
      "user": "…",
      "channel_ids": ["<channel_id>", …],
      "channel_revisions": { "<channel_id>": 7 },
      "banned": false,
      "limits": { … }
    }

`channel_revisions` is a map from channel id to the channel's current revision count. Its keys
are the channels in `channel_ids`.

**`channel_ids` is unchanged.** Eleven chapters publish that field; widening it into an array of
objects would edit all of them for a field they do not read.

**`.default({})`**, following `banned`'s precedent in this same schema — an api built before
this feature satisfies the schema during a rolling deploy, and the gateway treats a missing map
as all-zero, which is today's behaviour.

## Why this route

The gateway holds no database and must not gain one. `registry.ts` states it as a design
property: *"no pg, no drizzle-orm, no repository import."* The counts are a column in Postgres
and the api is the only service that reads Postgres.

Two fields already took this seat for the same reason. `banned`'s comment:

> IT RIDES THIS RESPONSE FOR THE REASON THE LIMITS DO: the gateway has no database and must not
> gain one … So the ban travels on the one call the gateway already makes at connect — no new
> table reaches the gateway and no new round trip is added.

**FR-014 is satisfied by this route existing**, not by making a new one cheap. At 10,000
connections a second call per handshake is 10,000 calls, and the measurement that produced
SC-004's baseline is what makes that concrete rather than theoretical.

## The api's side

The counts are resolved in the statement that already resolves memberships — a join to
`channels` on a row that query already reaches. No second query, no N+1 per channel.

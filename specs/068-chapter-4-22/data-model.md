# Data model — chapter 4.22, "The identifier the customer gave it"

**No new table, no new column, no migration.** What changes is which of two existing
columns a route accepts.

## The two spaces, and which belongs on the wire

```
IDENTITY                              KEY
the customer supplied it              Relay minted it
unique per environment                unique globally
users.external_id  text               users.id    uuid
channels.external_id  text            channels.id uuid
                                      messages.id, media_objects.id, …

FR-USR-01  "Relay shall not generate end-user identities"
ADR-18     "their identity is whatever external_id the customer already had"
```

**EXACTLY TWO TABLES CARRY AN IDENTITY**, from `information_schema`: `users` and
`channels`. Messages, media objects, webhooks and environments have a key and no
identity, so the key is the only thing that could address them and they are out of
scope by construction rather than by preference.

## What each noun accepts today, and after

| noun | routes | today | after |
|---|---|---|---|
| `users` | 8 | identity | unchanged |
| `channels` | 13 | **key only** | **identity or key** |
| messages, media, webhooks, environments | — | key | unchanged |

## The resolution

One function, called once per request, at the boundary.

```
input: the path segment, and the caller's environment

  parses as a uuid?
    no   ->  look up the identity.  one query. THE CAST NEVER HAPPENS,
             which is what removes the 500
    yes  ->  look up the key, then the identity if the key found nothing
             the identity wins a true tie — a customer who named a channel
             reaches the channel they named

  found     -> the key, handed downstream unchanged
  not found -> a refusal naming the cause. NEVER a 5xx
```

**SCOPED BY CONSTRUCTION, NOT BY A PREDICATE SOMEBODY WROTE.** The resolution runs
inside the request-scoped `Repository`, whose constructor requires an
`environment_id`. That is the mechanism chapter 4.21 found had kept six of seven
stores correct without anyone remembering — and the one store it did not mediate was
the only one that got the scope wrong.

**BOTH LOOKUPS ARE INDEX HITS AND THE IDENTITY IS THE CHEAPER ONE** —
`channels_environment_id_external_id_unique` answers the scoped question in one
search at 3 buffers and 1.094 ms, against the primary key's 2 buffers and 1.475 ms
plus an environment filter. There is no performance argument for either order.

## The collision, which is legal and has never happened

An `external_id` is `z.string().min(1).max(255)` and may be a uuid. Measured:

```
channels                                           41,768
with a uuid-shaped external_id                          0
with an external_id equal to their own row id           0
```

So the tie-break is a case the chapter constructs rather than waits for, and the
order is decided by which failure is worse: under key-first a customer who named a
channel with another channel's uuid **can never reach their own**, with no error they
can act on.

## The cursor

`GET /v1/users` paginates on `(last_activity_at, users.id)`, encoded as base64 of
`{a, id}`. The tiebreak must be unique and ordered, which is why the key was chosen.

**The identity is also unique and ordered within an environment, and the cursor is
already environment-scoped** — so it is a candidate. What it is not yet is a
decision, because FR-007 requires a cursor issued before this chapter to keep working
or be refused by name, and that is a version field or a dual-read.

## Entities this feature adds

None to the platform. One to the vocabulary: **a resolution** — turning what arrived
in a path into a key, once, inside the calling tenant.

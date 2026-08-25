# Contract — bot users

**No new route.** Bots are created through `POST /v1/users`, chapter 3.16's upsert, so the
gauntlet's derived target list stays at 38 and no classification is added.

Paths below are written with the customer's external id in place; the router names the
parameter `:externalId`. A classification entry copied from this file verbatim will not match
a derived target — the same note `membership.md` and `listing.md` carry.

## `POST /v1/users` — two fields on an entry

```json
{
  "users": [
    { "external_id": "ana", "display_name": "Ana" },
    {
      "external_id": "support-bot",
      "kind": "bot",
      "display_name": "Support Bot",
      "description": "Posts ticket updates from the helpdesk. Never reads."
    }
  ]
}
```

| Field | Rule |
|---|---|
| `kind` | `"person"` or `"bot"`, optional. **The default applies only on creation.** An entry that omits `kind` for a row that already exists asks for no change — it does not ask for `"person"` |
| `description` | required when `kind` is `"bot"`, at most 500 characters; refused when `kind` is `"person"` |

| Outcome | Status |
|---|---|
| created, updated or revived | 200, per-entry result array as chapter 3.16 defined it |
| an entry changing an existing row's `kind` | **200**, and that entry's status is `kind_conflict` |
| `kind: "bot"` with no `description` | 400 `invalid_request`, `field: "users.N.description"` |
| `description` on a `"person"` | 400 `invalid_request`, `field: "users.N.description"` |

### The two failure shapes, and which one a rule gets

**What zod can see fails the whole batch. What only the database knows is reported per
entry.** Chapter 3.16 built both and this contract has one of each:

    kind: "bot" with no description     zod sees it inside the entry        400, users.N.description
    a kind change                       needs the EXISTING row's kind       200, status kind_conflict

A kind change cannot be a 400. zod cannot know what the row already holds, and answering 400
would fail a batch of 100 because of entry 7 — which is the outcome chapter 3.16's per-entry
array exists to prevent: *"a partial outcome is reported per entry rather than collapsed into
one status code."*

`kind_conflict` joins `created`, `updated` and `revived` as a fourth status.

**ABSENT IS NOT `"person"`, and getting that wrong makes a bot uneditable.** `kind` defaults
to `"person"` on creation. Apply that default before comparing against an existing row and
every upsert that updates a bot's description without restating `kind: "bot"` reads as a
request to demote it — so FR-004's "a bot supports profile update" would be unreachable through
this route.

The distinction is the one chapters 3.15 and 3.16 built into the profile patch — *absent keeps
its value, present-and-null clears it* — and the reason `exactOptionalPropertyTypes` is on.

**The kind-change refusal is the one to read twice.** Person → bot silently revokes the
ability to authenticate for an identifier whose users may hold live tokens; bot → person hands
out a credential for an identity nobody meant to issue one for. Both are refused, and the
per-entry status reports which entry failed — a batch of 100 that fails on entry 7 must say 7.

## `GET /v1/users/:externalId` — the profile carries both

```json
{
  "external_id": "support-bot",
  "kind": "bot",
  "display_name": "Support Bot",
  "description": "Posts ticket updates from the helpdesk. Never reads.",
  "avatar_url": null,
  "metadata": {}
}
```

`kind` is present for every user, `description` is `null` for a person. **A client must be able
to tell a bot from a person without parsing the identifier** — that is FR-003, and returning
`kind` on every profile is what satisfies it.

## `PATCH /v1/users/:externalId` — the description is editable, the kind is not

| Outcome | Status |
|---|---|
| `description` updated on a bot | 200 |
| `description` set to null on a bot | 400 `invalid_request`, `field: "description"` — **refused by validation**, and the CHECK would reject it too if validation were ever relaxed |
| `kind` present at all | 400 `invalid_request`, `field: "kind"` |

## `POST /auth/dev-token` — a bot cannot be minted for

| Outcome | Status |
|---|---|
| the identifier has no row | 200, a **person** is created and a token minted (FR-USR-02) |
| the identifier is a person | 200 |
| the identifier is a bot | **404** |

**404 and not 403, and the message must not say "this is a bot."** Chapter 3.16 established
that this route's response must not distinguish created from existed, because that would let a
caller enumerate a tenant's external ids by minting tokens. The same argument applies here: a
refusal that names bot-ness is an oracle for which identifiers are bots. The refusal is the one
a non-existent user gets.

## What a bot inherits, unchanged

Membership, roles, the channel listing, the ban, the deletion and every isolation guarantee —
all keyed on the user row, all working without a new rule. `data-model.md` lists them.

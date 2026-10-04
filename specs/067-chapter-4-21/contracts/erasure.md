# Contract — erasing an end user, and the receipt that says what it could not

One surface, and the receipt is the part worth specifying. FR-MOD-04's
*completion receipt* is its least defined phrase: a 204 satisfies the grammar
and tells a compliance officer nothing.

## `DELETE /v1/users/{externalId}/data`

| | |
|---|---|
| credential | **application only** — class-level `@Accepts("application")`, the decision rather than a branch |
| scope | the caller's environment. An external id is unique per environment, not globally |
| body | none |

**THE ROUTE LIVES IN `users.controller.ts`, BESIDE THE DELETION IT MUST NOT BE
CONFUSED WITH.** That controller already carries `@Controller("v1/users")`,
`@UseGuards(CredentialGuard)` and `@Accepts("application")` at class level, so the
erasure inherits all three. A separate module was the first plan and it would have cost
19 extra fence pages to duplicate those decorators — and put the two verbs in different
files, which is the opposite of what the paragraph below argues for.

**WHY NOT `DELETE /v1/users/{externalId}`.** That is FR-USR-05's deletion and it
already exists with the opposite semantics — it keeps the row, the messages and
the billing rows on purpose. Two verbs that differ only in what they preserve
must not differ only in a query parameter either: a mistyped flag would be an
irreversible erasure. **The path says which one you asked for.**

## The receipt

```json
{
  "user_external_id": "u-4821",
  "requested_at": "2026-10-04T11:52:00.000Z",
  "completed_at": "2026-10-04T11:52:00.412Z",
  "stores": [
    { "store": "profile",            "outcome": "erased",        "rows": 1 },
    { "store": "memberships",        "outcome": "erased",        "rows": 7 },
    { "store": "read_positions",     "outcome": "erased",        "rows": 7 },
    { "store": "media_objects",      "outcome": "erased",        "rows": 2,
      "note": "attributed uploads only; 73% of objects platform-wide record no uploader" },
    { "store": "connection_events",  "outcome": "erased",        "rows": 31 },
    { "store": "api_requests",       "outcome": "nothing_to_erase",
      "note": "this table records no user identifier" },
    { "store": "daily_usage",        "outcome": "cannot_erase",  "rows": 0,
      "note": "a uniq sketch has no subtract operation; recomputation needs message_events" }
  ]
}
```

**FOUR OUTCOMES AND THE FOURTH IS THE ONE THAT MATTERS.**

| outcome | means |
|---|---|
| `erased` | rows named this user and no longer do |
| `nothing_to_erase` | this store never named them |
| `cannot_erase` | this store names them and **no operation removes one user** |
| `not_reached` | the store was unavailable; the erasure is incomplete and says so |

**`nothing_to_erase` AND `cannot_erase` MUST NOT COLLAPSE.** `api_requests`
holds 205,697 rows and no user column — that is chapter 4.4's design paying off
and there is genuinely nothing to do. `daily_usage` holds 880 rows that name
users in a form from which no single user can be removed. A receipt that
reported both as "0 rows erased" would be true and would hide the only thing a
compliance officer needs to see.

**AND `not_reached` IS WHY THE RECEIPT IS LOAD-BEARING.** Constitution III keeps
the analytical path independent of the operational one, so a ClickHouse outage
must not roll back an erasure that has already removed a person's profile and
messages. The operational half commits; the analytical half is attempted and
reported. Without a `not_reached` outcome the only honest alternative is to fail
the whole request, which is the design failure III names.

### Refusals

| condition | status | code |
|---|---|---|
| an external id no user in this environment has | 404 | `not_found` — and **indistinguishable from another tenant's**, apart from `request_id` |
| a user token | 403 | `wrong_credential_type` |
| an unknown field in the body | 400 | `invalid_request` — the schema is `z.strictObject` (constitution VI's fifth bullet) |
| a second erasure of the same user | **200** | a receipt reporting zero erased. **Not a 404** — idempotence is about what the second call DID |

**No new error code.** `not_found`, `wrong_credential_type` and
`invalid_request` are all in `codes.ts` and `docs/08-error-reference.md`
already — checked, because `codes.ts` is published by 27 pages with an appendix
that amends it twice.

## What this contract does not offer

- **No asynchronous mode and no job id.** FR-MOD-04 bounds completion at thirty
  days and nothing in this platform schedules anything; a synchronous erasure
  satisfies the bound trivially and the chapter says the bound is unexercised
  rather than implying a timer. The fifth clause bounded by ADR-28's absence.
- **No undo.** FR-MOD-05's tenant export — two rows above FR-MOD-06, still
  unbuilt — is the clause that would let a tenant hold a copy first.
- **No erasure across environments.** An external id is unique per environment.
  A person who exists in two of a customer's environments is two users here, and
  the receipt names the one it erased.
- **No `audit_log` deletion.** It is append-only (ADR-35), and an erasure
  **writes** an entry rather than removing them (FR-013). The 1,324 entries that
  name a user target stay, and the chapter says why.

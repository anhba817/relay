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
    { "store": "profile",            "outcome": "erased",             "rows": 1,
      "note": "display_name, avatar_url, metadata AND external_id" },
    { "store": "memberships",        "outcome": "erased",             "rows": 7 },
    { "store": "read_positions",     "outcome": "erased",             "rows": 7 },
    { "store": "media_objects",      "outcome": "erased",             "rows": 2,
      "note": "attributed uploads only; 73% of objects platform-wide record no uploader" },
    { "store": "connection_events",  "outcome": "erased",             "rows": 31 },
    // scoped by environment_id AND user_external_id, BOTH AS BOUND PARAMETERS.
    // An id alone spans up to 111 environments on the development lane, and an
    // interpolated hostile id matches all 1,109 rows (R8, R9). The count is a
    // separate SELECT: the DELETE answers 200 with an empty body.
    { "store": "messages",           "outcome": "retained_anonymous", "rows": 143,
      "note": "FR-028: a channel's history must not lose one participant's half" },
    { "store": "usage_active_users", "outcome": "retained_anonymous", "rows": 22,
      "note": "FR-029: a customer who deleted a user in March still owes for March" },
    { "store": "daily_usage",        "outcome": "retained_anonymous", "rows": 0,
      "note": "uniq sketches keyed on the uuid; nothing to subtract and nothing identifying" },
    { "store": "api_requests",       "outcome": "nothing_to_erase",
      "note": "this table records no user identifier" },
    { "store": "audit_log",          "outcome": "cannot_erase",       "rows": 12,
      "note": "target_id holds the EXTERNAL id and the log is append-only (ADR-35)" }
  ]
}
```

**FIVE OUTCOMES, AND THE LAST TWO ARE WHY THE RECEIPT EXISTS.**

| outcome | means |
|---|---|
| `erased` | rows named this user and no longer exist, or no longer name them |
| `nothing_to_erase` | this store never named them |
| `retained_anonymous` | rows reference this user **by key**, are kept under a named clause, and the key now resolves to an erased row |
| `cannot_erase` | this store holds their **identity** and **no operation removes one user** |
| `not_reached` | the store was unavailable; the erasure is incomplete and says so |

**`retained_anonymous` IS NOT CALLED `anonymised`, AND THE NAMING IS THE
DECISION.** *Anonymised* is a claim with a statutory bar behind it. The receipt
states the mechanism — the rows stay, the key is dead — and lets the reader draw
the conclusion.

**`nothing_to_erase` AND `cannot_erase` MUST NOT COLLAPSE.** `api_requests`
holds 205,697 rows and no user column — that is chapter 4.4's design paying off
and there is genuinely nothing to do. `audit_log` holds **1,357 rows whose
`target_id` is the person's external id — 1,357 of 1,357, not one a uuid** — in
a table ADR-35 made append-only. A receipt that reported both as "0 rows erased"
would be true and would hide the only thing a compliance officer needs to see.

**AND `retained_anonymous` MUST NOT COLLAPSE INTO `erased`**, for the same
reason one turn further out. *"7 membership rows removed"* and *"22 billing rows
left standing, naming nobody"* are different facts, and a compliance officer who
reads the second as the first will be wrong about why March's invoice still
counts this person.

**THE LINE BETWEEN THEM IS KEYS AGAINST CONTENTS.** A uuid pointing at an erased
row names nobody — that is what makes `usage_active_users` and the `uniq`
sketches `retained_anonymous` at no cost. It says nothing about the VALUE on the
row: a photo is personal data whatever key it hangs from, and so is message
text. `messages` and `media_objects` are therefore decided on their own clauses
and **they go opposite ways**, which is the test that the line is real.

**AND `not_reached` IS WHY THE RECEIPT IS LOAD-BEARING.** Constitution III keeps
the analytical path independent of the operational one, so a ClickHouse outage
must not roll back an erasure that has already destroyed a person's profile,
their external id and their uploads — none of which can be put back. The operational half commits; the analytical half is attempted and
reported. Without a `not_reached` outcome the only honest alternative is to fail
the whole request, which is the design failure III names.

### Refusals

| condition | status | code |
|---|---|---|
| an external id no user in this environment has | 404 | `not_found` — and **indistinguishable from another tenant's**, apart from `request_id` |
| a user token | 403 | `wrong_credential_type` |
| ~~an unknown field in the body~~ | — | **No body, so no refusal.** The route takes one path parameter and declares no `@Body()`; a junk body answers exactly as an empty one does. Constitution VI's fifth bullet governs endpoints that take input and is **not engaged** here, which is a different thing from unmet |
| a second erasure of the same user | **404** | `not_found`, and this INVERTS the obvious answer. Erasure clears `external_id`, so the resolve step genuinely finds no user. The cost is real: a support tool retrying after a timeout cannot tell *already erased* from *never existed*. **A hash of the external id on the tombstone would answer it and is refused** — `u-4821` and an email address are both brute-forceable, so a hash is the identity wearing a disguise. **The operator's proof is the audit entry**, which is append-only by design |

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
- **No confirmation step, and the adjacent clause has one.** FR-TEN-08 requires an
  application deletion to be *"confirmed by typing the application name"*; FR-MOD-04
  requires nothing, and this erasure is equally irreversible. **The asymmetry is in the
  caller, not the consequence**: FR-TEN-08's ritual is a human in a dashboard, and this
  endpoint's caller is a support tool holding an API key — `docs/03`'s Journey 3 opens
  *"Priya never touches Relay directly."* A typed confirmation cannot be asked of a
  machine. **What takes its place is the path**: `/data` on the end of the URL is the
  thing a reader of the call site sees, which is why the route is not a flag.
- **No erasure across environments.** An external id is unique per environment.
  A person who exists in two of a customer's environments is two users here, and
  the receipt names the one it erased.
- **No `audit_log` deletion**, which is now a receipt row rather than an
  omission — see `cannot_erase` above. It is append-only (ADR-35), and an
  erasure **writes** an entry rather than removing them (FR-013).
  **AND THE ENTRY IT WRITES CARRIES THE NAME IT JUST ERASED.** `deleteUser`
  records `targetId: userExternalId`; recording the uuid instead was considered
  and refused, because the entry is the operator's only proof the erasure
  happened and FR-MOD-03's log exists to demonstrate exactly that. **The one
  place the name survives is the record that the name was erased.**

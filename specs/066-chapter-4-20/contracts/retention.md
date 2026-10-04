# Contract — setting a retention policy, and what running the sweep does

Two surfaces, and only one of them is an HTTP route. The second is a command, because this
platform has no scheduler and pretending otherwise would put a compliance promise behind a
mechanism that does not exist (research R3).

## `PATCH /v1/environments/{environmentId}` — the policy

| | |
|---|---|
| credential | **application only**, consistent with every other environment-level setting |
| field | `retention_days` |
| values | `30`, `90`, `365`, or `null` |

```json
{ "retention_days": 90 }
```

```json
{ "id": "…", "name": "production", "retention_days": 90 }
```

**`null` IS INDEFINITE AND IS NOT A MISSING FIELD.** FR-MOD-06's fourth option is *indefinite*,
and the column's absence of a value is how this schema already spells it. A client clearing a
policy sends `null` explicitly; a client omitting the field changes nothing. **The two are
different requests** and the schema distinguishes them, which is chapter 4.14's lesson about an
absent key and a null value being the same to a truthiness check and different to a contract.

### Refusals

| condition | status | code |
|---|---|---|
| `retention_days` not in {30, 90, 365, null} | 400 | `invalid_request` — the clause enumerates four options and a fifth is not a stricter policy somebody chose |
| a user token | 403 | `wrong_credential_type` |
| an unknown field in the body | 400 | `invalid_request` — the schema is `z.strictObject`, because constitution VI's fifth bullet says *unknown fields are rejected on write endpoints* and this is one |
| another tenant's environment | 404 | indistinguishable from one that does not exist |
| a malformed id in the path | **500** | `internal_error`, **and this chapter does not fix it** — `gaps.md` 058-3, live across **twenty-two** routes and twenty-three with this one, carried with its bill for the reason chapter 4.19 gave: one validating route among twenty-two makes the remaining twenty-one harder to sweep |

**058-3 SAYS SIXTEEN AND THE NUMBER IS TWENTY-TWO**, re-measured at analysis pass 11. That entry counted `@Param("channelId")` 13 and `@Param("messageId")` 3 across `messages.controller.ts` and `channels.controller.ts`, and **never opened `webhooks.controller.ts`** — six routes taking `@Param("id") id: string` with no validation, passed straight to the repository, where `webhook_endpoints.id` is `uuid PRIMARY KEY`. The number has been carried verbatim since chapter 4.12. **The carry-rather-than-fix argument gets stronger with the real figure, not weaker**, which is the only reason it is safe to correct it here rather than act on it.

**No new error code.** `invalid_request`, `wrong_credential_type` and `not_found` are all in
`codes.ts` and `docs/08-error-reference.md` already — checked, because `codes.ts` is published
by 24 pages with an appendix that amends it three times, so adding one is a bill to check
before incurring rather than after.

## The sweep — a command, not a timer

```
pnpm --filter @relay/api exec node dist/retention/sweep.js [--environment <id>] [--dry-run]
```

| | |
|---|---|
| what invokes it | **an operator, or whatever an operator wires up.** Nothing in this platform does |
| what it prints | a counted line per environment: messages destroyed, objects destroyed, objects kept because they were shared |
| `--dry-run` | counts and prints, destroys nothing |

**THE COUNTED LINE IS THE OUTPUT, NOT THE EXIT CODE.** 055-4: five of seven gate scripts exit 0
when their corpus is absent, and the rule the entry produced is to assert the line. A sweep
that found no environments with a policy and a sweep that found nothing expired both exit 0 and
must not print the same thing.

### What the sweep promises, and the sentence it must not say

It promises that **when it runs**, every message past its environment's policy is destroyed. It
promises nothing about when it runs, because nothing runs it.

**So no surface publishes a `retention_edge`, an `expires_at`, or anything a client could read
as a bound.** Chapter 4.18 refused exactly that for the audit log's retention year; the request
log publishes one only because its table has a real TTL enforced by ClickHouse. A field naming
a deadline this platform does not keep is worse than no field, because a compliance team reads
it.

## What this contract does not offer

- **No per-channel or per-user policy.** FR-MOD-06 says per environment.
- **No undo.** Expiry is destruction; there is nothing to restore and the chapter says so
  rather than letting somebody ask. **And the clause that would have been the undo sits two
  rows above FR-MOD-06 and is unbuilt**: FR-MOD-05, *"exporting all data for a tenant as
  newline-delimited JSON, generated asynchronously with a notification on completion."* A
  tenant who wants to keep what a policy destroys has no supported way to take a copy first.
  Naming it is the honest version of *no undo*.
- **No notification.** A tenant is not told what expired. That is a different clause and a
  larger table — and the audit log is deliberately not it: FR-MOD-03's population is
  *moderation actions*, which are things a credential did, and a sweep is not one.
- **No bound on a single run.** Whether a sweep that would destroy a million rows should stop
  and resume is a real question, and the lane cannot inform it: nothing here is 30 days old
  (research R5). Recorded as a known shape rather than solved on a guess.

# Data model — Chapter 3.12

**No product migration.** This is the first chapter since 3.7 with none, and the reason
is worth stating: the two new endpoints wrap repository functions that already exist
against tables chapter 2.1 created, and the constraints their idempotency needs were
created with them. What follows is therefore mostly *derived* shapes — the things the
suite computes at run time — plus three shapes that are new code and no new storage.

## 1. Existing storage this chapter relies on and does not change

| Table | What this chapter needs from it |
|---|---|
| `channels` | `channels_environment_id_external_id_unique` — the customer-supplied identifier is the idempotency key for `POST /v1/channels`. Already there, unused by any public route until now |
| `users` | `users_environment_id_external_id_unique` — same property, for the user identifiers a member request names |
| `members` | primary key `(channel_id, user_id)` — makes a repeated member add a no-op rather than a second row, once the insert says so (R14a) |
| `usage_periods`, `usage_active_users`, `usage_connections`, `quota_notifications` | the four tables the guard starts watching. Three have composite primary keys and no `id` column |
| `outbox` | `id, subject, payload, created_at, published_at`. No tenant column, zero foreign keys; infrastructure, beside `consumed_events` (R7). Its payload is a full copy of the message and nothing prunes it, which is a retention finding rather than a tenancy one (R7a) |

## 2. `Target` — derived, never written down

One per routable endpoint, computed at suite start from the express router.

| Field | Source | Notes |
|---|---|---|
| `method` | `route.methods` | uppercased; a route may carry more than one |
| `path` | `route.path` | as express normalised it: `/v1/webhooks/:id` |
| `shape` | the classification list | one of `read`, `list`, `write`, `credential`, `exempt` |
| `because` | the classification list | required when `shape` is `exempt`; a sentence, not a tag |

**Invariants.**

1. The derived count is non-zero, and `POST /v1/channels/:channelId/messages` is
   present. A derivation that silently returns nothing must fail, not pass (R2).
2. Every derived target matches exactly one classification entry. An unmatched target
   fails the suite; a classification entry matching no target also fails it, because a
   stale exemption is how a route becomes unattacked after a rename.
3. `exempt` requires `because`. Nothing may be exempt by omission (FR-003).

**The five shapes**, and the fifth is the one the specification did not anticipate. The
five rows sum to 22, which is the check that caught the webhook **create** route missing
from an earlier draft of this table — 21 named against a derived 22:

| Shape | Members today | The attack |
|---|---|---|
| `read` | `GET /v1/webhooks/:id`, `GET /v1/channels/:channelId/messages` | another tenant's id, paired with an id that exists nowhere |
| `list` | `GET /v1/webhooks` | the caller's own credential against an empty tenant |
| `write` | the eight `/internal/*` routes, **`POST /v1/webhooks`**, `POST` and `DELETE` on `/v1/webhooks/:id/*`, `POST /v1/channels/:channelId/messages` — fifteen | a foreign id, plus a state read before and after |
| `credential` | `POST /auth/dev-token` | a key from environment A must not mint a token that works in B. No identifier is involved (R4) |
| `exempt` | `GET /healthz`, `GET /auth/:provider/start`, `GET /auth/:provider/callback` | none, with a reason |

## 3. `AttackPair` — the unit of assertion

A single response proves nothing about indistinguishability, so the unit is two.

| Field | Meaning |
|---|---|
| `foreign` | the response to another tenant's identifier |
| `absent` | the response to a well-formed identifier that exists nowhere |
| `before` / `after` | for `write` shapes, the target tenant's rows read directly |

**Comparison rule.** Bodies are compared whole with `request_id` removed — the field
chapter 3.8 added and the only one that reveals nothing about the resource. Status and
error code are part of the comparison, not a substitute for it. The helper is lifted
from `messages.itest.ts`, where it and its reasoning already exist (R3).

## 4. `TenantPath` — the structural check's model

Computed from `information_schema` for every base table in `public` — **by a function in
`services/api/src/db/catalogue.ts`, not inline in the test.** That directory is where the
query engine is permitted; the restored lint ban (R23) forbids it elsewhere, and a
classification written into the test file would need an exemption for as long as it lived.

**Three classes, not four.** An earlier draft had a fourth, `unscoped`, holding
`outbox` alone — on the reading that Principle I's second clause was violated. R7
reversed that: the outbox is infrastructure, so the class had exactly one member and
then none.

| Value | Meaning | Count today |
|---|---|---|
| `direct` | the table has `environment_id` | 12 on a database the lane has run against, 11 on a fresh one — `__sentinel_environments` is the harness's, so the counts are recorded rather than asserted (SC-007) |
| `hop` | at least one foreign key reaches a `direct` table | 2 — `members` and `messages`. Each reaches **two** (`channels` and `users`), so the rule is existence and not uniqueness; an earlier draft of this table said "exactly one", which would have classified neither and failed totality on both |
| `spine` | the tenancy tables themselves, plus infrastructure | 8 — `organisations`, `applications`, `environments`, `humans`, `memberships`, `consumed_events`, `schema_migrations`, `outbox` |

`spine` is an explicit list with a reason each, not a pattern. A new table lands in none
of the three and fails the check until somebody classifies it, which is the property
FR-012 asks for. **A fourth class is not kept open for future violations**: a table that
belongs in none of these is a finding, and an empty bucket waiting to receive it is how a
finding becomes a classification.

## 5. `ErrorCode` — the registry becomes the set

Today the emittable set is eleven and `ERROR_CODES` holds six. This chapter adds a
twelfth and a thirteenth — `wrong_credential_service`, for a platform credential refused
on a route declared for another service (R24), and `channel_member_limit_exceeded`, which
FR-CHN-07 requires and the SRS's own EIR-API-04 example names — so the registry ends at
**thirteen** and the type system keeps it that way.

| Code | Emitted from | In the registry today |
|---|---|---|
| `invalid_frame` | frame validation | yes |
| `unknown_frame_type` | frame validation | yes |
| `unauthorized` | the 401 ladder, guards | yes |
| `rate_limited` | the limiter, the guard, the gateway | yes |
| `wrong_credential_type` | `credential.guard.ts` | yes |
| `quota_exceeded` | `messages.service.ts`, `session.controller.ts` | yes |
| `invalid_request` | the 400 ladder | **no** |
| `forbidden` | the 403 ladder | **no** |
| `not_found` | the 404 ladder, `service-kit` | **no** |
| `internal_error` | the ladder's fallback | **no** |
| `connection_environment_conflict` | `usage.controller.ts` | **no** |
| `wrong_credential_service` | `credential.guard.ts` — new in this chapter | **new** |
| `channel_member_limit_exceeded` | `channels.service.ts` — new in this chapter (FR-CHN-07) | **new** |

**Shape.** Each entry keeps its one-line meaning, as the six do now. The ladder in
`protocol-error.filter.ts` is typed `ErrorCode`, so an unregistered code stops
compiling rather than reaching the wire undocumented.

**Derivation.** `Object.keys(ERROR_CODES)` is the set. The reference document's
completeness test compares two lists; nothing greps source (R8).

## 6. The reference entry

One `h2` per code in `docs/08-error-reference.md`, the heading being the code verbatim.

| Part | Rule |
|---|---|
| heading | `## <code>` — the anchor is the code, once the slugifier keeps underscores (R10) |
| meaning | what the platform is saying |
| cause | what the client did, or what state it met |
| remedy | what to do. For a retryable condition, what makes it retryable; for one that is not, that it is not |

`docs_url` = the reference's published URL + `#` + the code. No transform on either
side, which is the point of R10's one-character change.

## 7. The two endpoints

### `POST /v1/channels`

```
request   { external_id, type: "public", name?, metadata? }   metadata ≤ 8 KB
201       { id, external_id, type, name, metadata }   created
200       { id, external_id, type, name, metadata }   already existed (FR-CHN-02)
400       invalid_request, field: "type"             "private" — see below
```

**All four of FR-CHN-01's elements**, including the 8 KB metadata an earlier draft omitted.
`channels.metadata` is a `jsonb` column with a default, present since chapter 2.1, so this
costs a schema field and a bound rather than a migration.

**`private` is refused, and the reason is that nothing enforces it.** `channels.type` has
been a `"public" | "private"` column with a CHECK constraint since 2.1 and no code reads
it: history and send scope by `environment_id` alone, with no membership check anywhere. So
FR-CHN-05 — a P1 clause — is unimplemented, and a public create endpoint accepting
`private` would sell a guarantee the platform does not keep. The documented enum has one
member until chapter 3.13 builds the other (R14, FR-047).

`external_id` is the idempotency key, enforced by the unique constraint rather than by a
read-then-write. The two statuses are the distinction chapter 2.3 drew for a duplicate
send, and an integrating developer can act on it.

### `POST /v1/channels/:channelId/members`

```
request   { user_ids: string[] }                 ≤ 100 per request (FR-CHN-06)
200       { added: string[], already_members: string[] }
404       channel not found — identical for a foreign channel and an absent one
422       channel_member_limit_exceeded — would exceed 1,000 members (FR-CHN-07)
```

**Two limits, and they are different requirements.** 100 is the batch size FR-CHN-06
allows in one request; 1,000 is the channel's ceiling from FR-CHN-07, which also specifies
the `422` and requires a code of its own. The SRS names that code in its worked example for
EIR-API-04: `channel_member_limit_exceeded`. An earlier draft of this document had neither
the ceiling nor the code.

Users named and not yet present are created — **FR-USR-01**'s rule that identifiers come
from the customer and "Relay shall not generate end-user identities", together with
FR-CHN-06, which does not require members to pre-exist. Not FR-USR-02, which describes
creation on first *authentication* and is a different moment. The cap is stated rather than unbounded because
FR-CHN-06 names 100 and an endpoint that takes one identifier would have to be replaced
instead of extended.

**Why this is not `addMember` with a controller on top (R14a).** The existing helper
returns one boolean for three different outcomes — added, channel not in this
environment, user not in this environment — and has no `ON CONFLICT`, so a repeat
raises against `members`' primary key and the filter renders it `internal_error`. The
conflation is correct for isolation and wrong for an endpoint: the response must be the
same for a foreign channel and an absent one, and *different* for "already a member",
which is a success. So the service does a scoped channel read first, then an upsert.

## 8. `AcceptSpec` — the decorator that stops under-specifying

New code, no new storage. Today `Accepts` takes `...kinds: PrincipalKind[]`, so a route
can say which credential *class* may call it and not which internal *service* — and both
platform credentials resolve to `{ kind: "platform", service }` with `service` documented
"for logs" (R24).

```ts
type PlatformService = (typeof PLATFORM_SERVICES)[number][1];   // "dispatcher" | "gateway"
type AcceptSpec = "application" | "user" | { platform: readonly PlatformService[] };
```

| Route | Spec after this chapter |
|---|---|
| `POST /internal/messages`, `/internal/session`, `/internal/backfill` | `"user"` |
| `POST /internal/usage/connections` | `{ platform: ["gateway"] }` |
| `POST /internal/dispatch/expand`, `/material`, `/outcome`, `/replay` | `{ platform: ["dispatcher"] }` |
| `POST /auth/dev-token`, `/v1/*` | `"application"`, or `"application" \| "user"` as today |

**The property worth having is that `@Accepts("platform")` stops compiling.** An
authorization that can be omitted is one that will be, and the platform has more than one
internal caller with unequal exposure — the gateway terminates connections from the public
internet and the dispatcher does not. `PlatformService` is derived from `PLATFORM_SERVICES`
rather than retyped, so a third internal service widens the type on its own. Chapter 3.11
learned the same lesson from `Dimension`: the config key widened the type and the ternary
underneath it was what the compiler could not see.

## 9. The guard's table array

```
webhook_endpoints  webhook_deliveries  webhook_disable_notifications  channels  users
+ usage_periods  + usage_active_users  + quota_notifications  + usage_connections
```

Nine, and the refusal message changes with them:

```sql
key_text := coalesce(to_jsonb(OLD) ->> 'id', to_jsonb(OLD)::text);
```

Measured on both shapes (R15). The fallback prints the row, and these four carry
counters, dates and identifiers — no message text, which is why the same fallback would
be wrong on `messages` (NFR-SEC-06).

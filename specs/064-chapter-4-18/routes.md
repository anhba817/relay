# T010 — every mutating route the router serves, derived

**Derived from a booted application, not parsed from source.** `targets.itest.ts` printed
`gauntlet targets: 47 derived, 39 attacked, 8 exempt` and passed 9 of 9 — and its
both-directions assertion is what licenses this table: every derived target matches an entry
in `targets.ts` and every entry matches a derived target, so the file and the router are the
same list, proven on this run rather than assumed.

    47 routes derived
    33 mutating (POST · PATCH · PUT · DELETE)
     9 of those /internal/
    24 tenant-reachable mutating  ← the population owed a decision

**THE POPULATION IS 24, AND SIX DOCUMENTS SAID 25.** Research R3 published two estimates —
a regex over the source giving 47 entries, `grep -c "method:"` giving 51 — and said only the
router could settle it. It settled 47, which vindicates the parse. But the 25 came from a
*different*, stricter regex that missed one `/internal/` route, and it reached the spec, the
plan, the data model, the tasks, the checklist and the research note. Corrected everywhere by
sweep; the rule that found it is the one analysis pass 16 produced — *after correcting a
number, grep the feature directory for the old one* — applied in the other direction, to a
number that was wrong from the start.

## The population: 24 tenant-reachable mutating routes

`accepts` is from the derivation. The decision and its reason are T012's.

| method | path | accepts | classification | reason |
|---|---|---|---|---|
| `POST` | `/auth/dev-token` | `application` | | |
| `POST` | `/v1/channels` | `application` | | |
| `POST` | `/v1/channels/:channelId/archive` | `application` | | |
| `DELETE` | `/v1/channels/:channelId/archive` | `application` | | |
| `POST` | `/v1/channels/:channelId/join` | `user` | | |
| `POST` | `/v1/channels/:channelId/members` | `application` | | |
| `PATCH` | `/v1/channels/:channelId/members/:userExternalId` | `application` | | |
| `POST` | `/v1/channels/:channelId/members/remove` | `application` | | |
| `POST` | `/v1/channels/:channelId/messages` | `either` | | |
| `PATCH` | `/v1/channels/:channelId/messages/:messageId` | `user` | | |
| `DELETE` | `/v1/channels/:channelId/messages/:messageId` | `either` | | |
| `POST` | `/v1/media` | `either` | | |
| `POST` | `/v1/users` | `application` | | |
| `DELETE` | `/v1/users/:externalId` | `application` | | |
| `PATCH` | `/v1/users/:externalId` | `application` | | |
| `POST` | `/v1/users/:externalId/ban` | `application` | | |
| `DELETE` | `/v1/users/:externalId/ban` | `application` | | |
| `PUT` | `/v1/users/:externalId/channels/:channelId/read` | `either` | | |
| `POST` | `/v1/webhooks` | `application` | | |
| `DELETE` | `/v1/webhooks/:id` | `application` | | |
| `POST` | `/v1/webhooks/:id/disable` | `application` | | |
| `POST` | `/v1/webhooks/:id/enable` | `application` | | |
| `POST` | `/v1/webhooks/:id/rotate-secret` | `application` | | |
| `POST` | `/v1/webhooks/:id/test` | `application` | | |

## Outside the set by construction: 9 internal routes

Not decided — **not decidable**. A platform principal carries `environmentId?: undefined`
(chapter 4.4), so its action cannot be scoped to a tenant and cannot appear in a tenant's
read. *Outside by construction* and *decided to be outside* are different claims and only one
of them needs a reason.

| method | path |
|---|---|
| `POST` | `/internal/backfill` |
| `POST` | `/internal/dispatch/expand` |
| `POST` | `/internal/dispatch/material` |
| `POST` | `/internal/dispatch/outcome` |
| `POST` | `/internal/dispatch/replay` |
| `POST` | `/internal/media/:mediaId/verdict` |
| `POST` | `/internal/messages` |
| `POST` | `/internal/session` |
| `POST` | `/internal/usage/connections` |

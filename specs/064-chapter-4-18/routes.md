# T010 / T012 / T013 — every mutating route, derived and classified

**Derived from a booted application, not parsed from source.** `targets.itest.ts` printed
`gauntlet targets: 47 derived, 39 attacked, 8 exempt` and passed 9 of 9 — and its
both-directions assertion is what licenses this table: every derived target matches an entry
in `targets.ts` and every entry matches a derived target, so the file and the router are the
same list, proven on this run rather than assumed.

    47 routes derived
    33 mutating (POST · PATCH · PUT · DELETE)
     9 of those /internal/
    24 tenant-reachable mutating  ← the population owed a decision

**THE POPULATION IS 24, AND SIX DOCUMENTS SAID 25.** The 25 came from a regex that missed a
ninth `/internal/` route and reached the spec, the plan, the data model, the tasks, the
checklist and the research note. Corrected everywhere by sweep.

## T012 — the classification

The rule: **mutating, tenant-reachable, and acting on something other than the caller — and
where the caller decides, the credential decides.** `accepts` is the derivation's own.

| method | path | accepts | classification | reason |
|---|---|---|---|---|
| `POST` | `/auth/dev-token` | `application` | **not-moderation** | minting a credential is authentication plumbing; it changes nobody's standing and no content |
| `POST` | `/v1/channels` | `application` | **not-moderation** | creating a space is provisioning |
| `DELETE` | `/v1/channels/:channelId/archive` | `application` | **moderation** | the reversal is as much an action as the action — the ban pair's precedent |
| `POST` | `/v1/channels/:channelId/archive` | `application` | **moderation** | removes a shared space from use for everyone in it |
| `POST` | `/v1/channels/:channelId/join` | `user` | **not-moderation** | `accepts: user`; the caller acts on themselves |
| `POST` | `/v1/channels/:channelId/members` | `application` | **not-moderation** | **provisioning, and this is the rule's hardest call.** Adding members is what a tenant's onboarding does all day; a log that records it is a request log with extra columns |
| `PATCH` | `/v1/channels/:channelId/members/:userExternalId` | `application` | **moderation** | granting or revoking moderator powers is the thing an audit log exists for |
| `POST` | `/v1/channels/:channelId/members/remove` | `application` | **moderation** | removing a person from a space is an action against a person |
| `POST` | `/v1/channels/:channelId/messages` | `either` | **not-moderation** | the product's main verb, under either credential |
| `DELETE` | `/v1/channels/:channelId/messages/:messageId` | `either` | **moderation-when-application** | FR-002a's one route. Under a key it is FR-MOD-02; under a user token deleting their own message it is FR-013 of chapter 3.23 |
| `PATCH` | `/v1/channels/:channelId/messages/:messageId` | `user` | **not-moderation** | **`accepts: user` — a tenant key cannot reach it at all.** FR-MOD-02 grants deletion of any message and is silent on editing; FR-013a reads silence as absence of permission |
| `POST` | `/v1/media` | `either` | **not-moderation** | taking an upload slot is the product's verb |
| `POST` | `/v1/users` | `application` | **not-moderation** | upserting users is provisioning |
| `DELETE` | `/v1/users/:externalId` | `application` | **moderation** | removes a person's profile and memberships |
| `PATCH` | `/v1/users/:externalId` | `application` | **not-moderation** | profile maintenance. **The line the set draws is STANDING, not data**: ban, delete, role and removal change what a person may do; a display name does not |
| `DELETE` | `/v1/users/:externalId/ban` | `application` | **moderation** | and its reversal, which today leaves no trace at all |
| `POST` | `/v1/users/:externalId/ban` | `application` | **moderation** | the chapter's opening demonstration |
| `PUT` | `/v1/users/:externalId/channels/:channelId/read` | `either` | **not-moderation** | a read position is the reader's own state |
| `POST` | `/v1/webhooks` | `application` | **not-moderation** | integration configuration, not moderation |
| `DELETE` | `/v1/webhooks/:id` | `application` | **not-moderation** | integration configuration |
| `POST` | `/v1/webhooks/:id/disable` | `application` | **not-moderation** | integration configuration |
| `POST` | `/v1/webhooks/:id/enable` | `application` | **not-moderation** | integration configuration |
| `POST` | `/v1/webhooks/:id/rotate-secret` | `application` | **not-moderation** | security-sensitive and **not moderation**; a configuration audit is a clause that does not exist |
| `POST` | `/v1/webhooks/:id/test` | `application` | **not-moderation** | integration configuration |

**7 moderation · 1 moderation-when-application · 16 not-moderation = 24.**

### What the rule got wrong, and it is the ninth expected inclusion

The spec expected **nine**: ban, unban, delete a user, delete another author's message, **edit
another author's message**, remove a member, change a member's role, archive, unarchive. The
set is **eight**, and the one missing is *edit another author's message* — because
`PATCH /v1/channels/:channelId/messages/:messageId` is **`accepts: "user"`**. A tenant key
cannot reach it. FR-MOD-02 grants a key deletion of any message and is silent on editing, and
FR-013a reads that silence as absence of permission, which the repository states in its own
comment: *"this route accepts both credential classes and the edit accepts one."*

**So the ninth action is not excluded by the rule — it does not exist.** The spec predicted
*"the routes it classifies wrongly are the chapter's findings"*; this one was classified right
and the expectation was wrong, which is the same prediction coming true from the other side.

### The two calls that could have gone the other way

**`POST …/members`** — adding members to a channel — is the rule's hardest call and is
excluded. The rule admits it: a tenant adding somebody else is acting on another. It is
excluded because a tenant's onboarding does it all day, and a log that records provisioning is
a request log with extra columns. **`PATCH /v1/users/:externalId`** is excluded for the same
reason, and together they draw the line the set actually uses: **standing, not data.** Ban,
delete, role and removal change what a person may do; a display name and a membership row do
not.

## T013 — outside the set by construction: 9 internal routes

Not decided — **not decidable**. A platform principal carries `environmentId?: undefined`
(chapter 4.4), so its action cannot be scoped to a tenant and cannot appear in a tenant's read.
*Outside by construction* and *decided to be outside* are different claims and only one of
them needs a reason.

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

# Research — chapter 3.17, the sender a message never had

Every number here was measured against the repository at planning time, not carried from an
earlier document. The two chapters before this one were re-planned eight times because a
count was carried; the convention now is that a plan states where each figure came from.

---

## R1 — THE BLAST RADIUS, measured first because it decides the chapter's shape

Requiring a sender breaks a route shipped in chapter 2.2. Counted by grep over every send site
in the workspace:

    46 send sites across 12 files

    services/api/src/isolation/gauntlet.itest.ts        14
    services/api/src/messages/messages.itest.ts          8
    services/api/src/limits/limits.itest.ts              4
    services/api/src/users/users.itest.ts                3
    services/api/src/auth/credentials.itest.ts           3
    services/api/src/channels/channels.itest.ts          3
    packages/outsider/src/integrate.itest.ts             3   ← the sealed integration
    services/gateway/src/public-surface.itest.ts          2
    services/gateway/src/isolation-fixtures.ts            2
    packages/e2e/src/tuan.itest.ts                        2
    services/api/src/internal/internal.itest.ts           1
    services/gateway/src/limits.itest.ts                  1

**Three of them are in `packages/outsider`**, the package chapter 3.14 sealed so it cannot
import workspace code — the artifact that stands for an external developer. Its send is
`post(/v1/channels/${channelId}/messages, { text }, credential)` with an **API key**, and CI
runs it as its own job. So this chapter does not merely break tests: **it breaks the
integration the previous milestone built to prove an outsider can integrate**, and that break
is the honest signal that a published contract changed.

**Decision**: accept the break and make the outsider demonstrate the new flow — create a bot,
send as it. The alternative is a compatibility shim, and a shim is how an anonymous send
survives.

### AND THE COUNT ABOVE IS ONE OF TWO — corrected at `/speckit-tasks`

46 counts **HTTP send sites**. Making `repository.sendMessage`'s `userId` required (R5) breaks
a different set: in-process calls that omit it, in files the first count never looked at.

    27 repository calls with no userId, across 8 files

    services/api/src/messages/idempotency.itest.ts       11
    services/api/src/db/repository.itest.ts               6
    services/api/src/db/history-drift.itest.ts            3
    services/api/src/messages/history.itest.ts            2
    services/api/src/channels/channels.itest.ts           2
    services/api/src/quotas/quotas.itest.ts               1
    services/api/src/outbox/outbox.itest.ts               1
    services/api/src/internal/backfill.itest.ts           1

**Five of those eight files are not in the 46's twelve.** `idempotency.itest.ts`,
`history.itest.ts`, `quotas.itest.ts`, `outbox.itest.ts` and `backfill.itest.ts` never send
over HTTP, so a count of HTTP sites cannot see them — and `idempotency.itest.ts` alone holds
eleven, more than any HTTP file but the gauntlet.

**This is the previous feature's eight-revisions lesson arriving on schedule.** Chapters 3.15
and 3.16 revised one file count eight times, and the eighth revision was the one that split it
in two. This count split in two at the first re-derivation, because "how many places send" and
"how many places break" are different questions and the first one was asked first.

**The union is 17 files**, not 12: three files appear in both lists
(`channels.itest.ts`, `repository.itest.ts` is HTTP-free but in the repository list,
`messages.itest.ts` is HTTP-only). The enumeration lives in `tasks.md`, and the number to trust
at implementation time is `git diff --name-only`, not either list.

## R2 — HOW A BOT IS DISTINGUISHED: a column, `users.kind`

**Decision**: `kind text NOT NULL DEFAULT 'person'` with `CHECK (kind IN ('person','bot'))`,
in migration `0013`.

**Rationale.** The platform already answers "what kind of thing is this row" with a checked
column three times — `channels.type`, `members.role`, `memberships.role` — and chapter 3.15
spent a section on why `members.role` is a column with its own CHECK rather than a convention:
*a request that gets past the enum still cannot write a value the database rejects*.

**Alternatives considered.**

- **A flag in `users.metadata`.** Rejected on chapter 3.15's own argument, one level up: a
  convention inside 4 KB of free-form JSON is not a property anything can require, validate,
  index or render. It would also make "is this a bot" a jsonb read on the send path.
- **A separate `bots` table.** Rejected because membership, read positions, roles, the
  listing, the ban, `toFrame` and every isolation guarantee are keyed on `users.id`. A parallel
  table forks all of them and would have to be attacked separately by the gauntlet — the
  catalogue would gain a table and the derived target list a second surface.

**The cost, stated:** `users` now holds two kinds of thing, and every query that means "a
person" has to say so. The chapter has to find those queries rather than assume there are none.

## R3 — THE DESCRIPTION: a column, and the database requires it for bots

**Decision**: `description text` with
`CHECK (kind <> 'bot' OR description IS NOT NULL)`, bounded at 500 characters in the schema
layer.

**Rationale.** The requirement is that a tenant is *forced* to describe a bot. A nullable
column with validation only in zod is a requirement the application enforces and the database
does not — and this platform's convention is that a constraint the database can hold, it
holds. The CHECK makes "a bot without a description" unrepresentable rather than merely
refused.

500 characters because the field answers "what is this and why did it message me" for a human
reading a conversation — a sentence or two. `display_name` is 255 and this needs more; 4 KB is
`metadata`'s budget and this is not a document.

**A person's description is null**, and the CHECK permits that. Whether people may also carry
a description is left open deliberately: nothing asks for it, and a column that both kinds may
use is harder to remove than one only bots use.

## R4 — HOW A SEND NAMES ITS SENDER: a `user` field, required for one credential class

**Decision**: `POST /v1/channels/:channelId/messages` takes `user` — a customer-supplied
external id — **required** when the credential is an application key and **refused** when it
is a user token.

**Rationale for the name.** `/auth/dev-token` already takes `{ "user": "tuan" }`, and the
listing routes name a user `:externalId` in the path. `user` matches the closest precedent and
carries the same kind of value.

**Rationale for "refused" rather than "ignored" on a user token.** One rule, testable, and it
cannot drift: a user token speaks as its subject, so a body naming anyone is either redundant
or an attempt to impersonate, and the platform should not have to tell those apart at runtime.
The cost is that a client library sending `user` unconditionally must branch on credential
class — which it already does, because the two credentials come from different places.

**Alternatives considered.**

- **A per-environment default bot**, so a send with no `user` uses it and the shipped route
  keeps working. Rejected: it keeps every existing caller working and reintroduces exactly the
  thing this chapter removes — a message whose sender nobody chose. It also hides the concept
  from the quickstart, where an integrator most needs to meet it.
- **A separate route for system messages.** Rejected: two routes writing one table, and the
  isolation gauntlet gains a target for a distinction that is about the credential rather than
  the operation.

## R5 — WHERE THE TWO CHECKS LIVE, and they are two

Chapter 3.15's lesson was that a check on the caller needs three places — the handler resolves,
the service threads, the repository accepts — and that a check gated on a parameter nobody fills
in never fires. This chapter has **two different checks** and they belong in different layers,
because they are checks about different things.

**"A message has a sender" is a data property → the repository.** `sendMessage`'s `userId`
becomes **required** rather than optional. That is the strongest available form: SC-003 asks
that no write path can produce a senderless message, and a required parameter makes every
would-be violation a **compile error** rather than a test that has to be written and remembered.

**"An application credential may only send as a bot" is a credential property → the service.**
The repository cannot see the credential class and should not learn it; the guard resolves the
principal and the service is the first layer that holds both the principal and the user row.

**What this predicts, and the chapter should check it:** making `userId` required will break
every in-process caller that omits it, including test fixtures that construct legacy rows. That
is the same shape as chapter 3.16's tombstone test, which had to write its state by raw SQL
because no route could produce it.

## R6 — A BOT CANNOT AUTHENTICATE, and the mint path is where that is enforced

`POST /auth/dev-token` calls chapter 3.16's idempotent `createUser` so a token can be minted
for an identifier with no row (FR-USR-02). Three cases now:

    identifier has no row        create a PERSON and mint
    identifier is a person       mint
    identifier is a bot          REFUSE

**Decision**: refuse, and name the reason. A bot is an identity messages are sent *as*; a token
for one would be a credential nobody issued, usable to open a socket and to send as that bot
from anywhere.

**And the refusal must not leak.** A refusal that distinguishes "this is a bot" from "this user
does not exist" tells an attacker which identifiers are bots. Chapter 3.16 already established
the rule for the mint path — the response must not distinguish created from existed, because it
would be a membership oracle — and the same argument applies here with the same answer.

## R7 — NO NEW ROUTES, and the derived target list should not move

**Decision**: bots are created through `POST /v1/users`, chapter 3.16's upsert, with `kind` and
`description` on the entry. No new route, so the gauntlet's derived list stays at **38 targets**
and no classification is added.

**The upsert MUST refuse a kind change.** Turning a person into a bot would silently revoke
their ability to authenticate; turning a bot into a person would hand out a credential for an
identity that was never meant to have one. Both are refused, and FR-005a's "must not turn an
existing bot into an authenticating user" is that rule in one direction.

**Verification note.** The derived target list fails the build on any route it has not been
told about — five separate times in the last feature. If it moves, a route was added that this
plan did not intend, which is the check working.

## R8 — WHAT CHAPTER 3.16 LEAVES THAT THIS CHAPTER MUST REVISIT

- **`last_message.user: null`** in the listing, and the repository test that exercises it. The
  arm now covers **legacy rows only**. The test constructs its row with an unattributed
  `repo.sendMessage`, which becomes a compile error under R5 — so it must construct the row
  the way the tombstone test does, by raw SQL, and say why.
- **`toFrame` drops a senderless row.** After this chapter no new row can be senderless, so the
  drop covers legacy rows only. Whether those become renderable is FR-013's decision.
- **The frame-shape assertion** written in chapter 3.16, which refuses a `message.created`
  whose `user` is not a non-empty string, **keeps passing** — and that is the point of choosing
  a bot over a nullable sender. It is worth an explicit assertion that it still passes, because
  a chapter that changes the sender model and leaves the frame contract alone is making a claim
  a reader will not believe without one.

## R9 — THE SRS AMENDMENT

The SRS has no bot, system or service-account concept: FR-USR-01 to FR-USR-06 describe end
users supplied by the customer, and the SAD mentions none. The constitution's Governance
section requires an explicit amendment.

**Proposed, and corrected in analysis pass 13**: additive where nothing conflicts, and an
in-place edit where something does. The original proposal was *"one new clause in each affected
family, rather than editing existing ones, so the amendment is additive and the diff shows what
changed"* — a good default that had not been tested against §4.5's existing rows.

    FR-USR-07   NEW.       Customers shall be able to create bot users representing their
                           own software, carrying a description, which cannot authenticate.
    FR-MSG-13   AMENDED.   "on behalf of any user via API key" -> "on behalf of a bot user
                           of that tenant via API key". P2 and verification T unchanged.
    FR-MSG-15   NEW.       Every message shall carry a sender.

**FR-MSG-13 is why the split matters.** It has said since v1 that *"The system shall support
sending a message on behalf of any user via API key, for backend-originated messages"*, and it
says **any user** where this chapter permits only a bot. An additive amendment would leave both
statements standing. It has also never been delivered as written: chapter 3.3 satisfied it by
sending unattributed, and `messages.controller.ts` cites it for exactly that. So FR-MSG-15 carries
only the genuinely new half — that every message has a sender at all — and FR-MSG-13 carries the
narrowing.

**An additive-only policy is a decision per clause, not a policy.** Deciding it once, at the top,
is what let thirteen passes read FR-015's claim that the SRS lacked this requirement.

**And FR-MSG-01 needs a note, not an edit.** It describes what a message contains and does not
mention a sender; the amendment record should say the sender requirement is FR-MSG-15's and
that FR-MSG-01 is unchanged, so a later reader does not look for it there.

# What the integration needed that the documentation did not contain

Kept while `packages/outsider/src/integrate.itest.ts` was being written, not
reconstructed afterwards (FR-033). Each entry is a fact the suite could not have
had from the published series, the reference documents, or `relay-platform`'s
README — found by a test failing, an assertion guessed wrong, or a command that
did nothing useful.

**A list of zero would have been a result only with a stated method.** The method
was: write the suite against the documentation, run it, and record every place the
documentation ran out. Six places did.

---

## G1 — a message sent over REST reaches no socket, ever  **[CLOSED — chapter 3.18]**

**CLOSED. Both mechanisms are gone, and the clause is FR-RTM-01.**

    the sender    FR-MSG-15, chapter 3.17     every REST send names a bot user
    the publish   FR-RTM-01, chapter 3.18     the api publishes to chan:{channel_id}

The api now holds its own Redis client for the fan-out
(`services/api/src/fanout/publisher.ts`) and `messages.controller.ts` publishes the
committed message after the transaction, for non-duplicate sends only.
`services/gateway/src/public-surface.itest.ts` asserts arrival on **both** legs now — live
and on resume — where it once asserted `[]` on both. The sealed outsider sends over REST
and receives on a socket without reading platform source, which is the criterion this gap
was blocking.

**The clause cited below is wrong and was wrong for six chapters.** This gap is
FR-RTM-01's, not FR-RTM-05's; chapter 3.18's FR-001 corrects the attribution and
`docs/07-tutorial-plan.md`'s row carried the same error from 3.14 to 3.18.

Everything from here down is the record as it stood, kept rather than rewritten.


**Found by:** the socket test failing with `never received the message; saw
connection.ack` after a `POST /v1/channels/:id/messages` returned 201.

Two independent mechanisms, either sufficient. Nothing in the api publishes to the
gateway's fan-out — `session.ts` publishes when a SOCKET sends, and the api's send
path writes the row and the outbox and stops, with the event consumer's handler
being `createRecorder`, which records rather than delivers. And the public send
route passes no user, so every row it writes has `user_id` NULL, which
`backfill.controller.ts`'s `toFrame` drops on purpose because `messageSchema`
requires `user` and there is no truthful value to invent.

**AMENDED BY CHAPTER 3.17 — ONE OF THE TWO MECHANISMS IS GONE.**

The second cause is closed. FR-MSG-15 makes every message carry a sender, so the public
send route no longer writes `user_id NULL` and `toFrame` has no reason to drop the row.
Measured on `public-surface.itest.ts`: **a REST-sent message now arrives on a resume.** The
test that pinned both mechanisms at once began failing on the half that changed, which is
how the change was noticed at all.

The FIRST cause stands, unchanged: nothing in the api publishes to the gateway's fan-out.
`session.ts` publishes when a socket sends; the api's send path writes the row and the
outbox and stops. So **live** delivery still reaches nothing, and the sentence that is now
true is narrower than this heading:

    live delivery      still nothing        chapter 3.18 owns it
    on resume          NOW ARRIVES          closed by chapter 3.17

A two-mechanism gap became a one-mechanism gap. Recorded here rather than in 3.17's own
`gaps.md` alone, because a reader who finds this heading needs to know it is half true —
and because this project has now corrected a "delivered" claim three times by reading the
record next to the code.

So "send a message and receive it on a socket" was only true over the socket. An
integrating developer following the obvious path — REST to send, socket to
receive — waited for ever, and nothing told them why. That was the state through
chapter 3.17.

**Disposition: CLOSED by chapter 3.18.** Recorded when scheduled as: Two candidate fixes and both
are product decisions rather than corrections. Attributing a public send to an
end-user token changes what `user` means on the wire for every existing caller
(FR-MSG-13's territory); a live fan-out from the api is a new coupling between the
api and Redis that ADR-05 and constitution III would each want an argument for.
Owned by whoever owns FR-RTM-05. **Documented here and pinned by a test** — and the test changed when the gap closed.
`services/gateway/src/public-surface.itest.ts` asserted both halves: a socket send
between two members added over the public API is delivered, and a REST send is delivered
neither live nor on resume. Chapter 3.18 rewrote the second half and the test's own name,
which had said "does NOT deliver". Both legs now assert arrival.

## G2 — `docker compose --profile services up` serves whatever was last built

**Found by:** six of eight tests failing against a stack that was up and healthy.
`POST /v1/channels` answered 404 for a route that exists, and `docs_url` came back
as `https://relay.example/docs/errors/not_found` — the pre-chapter host.

The README's compose block had no `--build`, and none of the failures named a
stale image. A developer's first day ends here.

**Disposition: fixed in this chapter.** `relay-platform/README.md` now shows the
build as its own line with the measurement beside it, and the CI job runs
`docker compose --profile services build` before `up`.

## G3 — `RELAY_POSTGRES_PORT=15432` is required on every compose invocation

**Found by:** `docker compose up -d --wait` bringing up four healthy containers
and failing on Postgres alone with `bind: address already in use`.

`compose.yaml:22` defaults the host port to 5432; `client.ts` and `db-url.ts`
default to 15432; the published series documents 15432 in four chapters and 5432 in
one. Three sources, three answers, and on a machine already running Postgres the
symptom points at compose rather than at a default.

**Disposition: fixed for the commands this chapter owns, and named for the rest.**
Every compose call in the README, the quickstart, research R25 and the CI job now
carries the variable. The series' own port drift — two documented ports for each of
Postgres, NATS and Redis, sometimes inside one chapter — is out of scope here and
recorded in `baseline.txt`: rewriting port references across ten published chapters
in two locales is a documentation pass with a fence chain behind it, not a line in
an isolation chapter.

## G4 — there is no public way to obtain a credential

**Found by:** having nothing to put in `Authorization` before writing a line of
the suite.

Sign-up ends at an OAuth consent screen no automated integration can complete
(chapter 3.4), and key management was deferred to "the dashboard's chapter"
(chapter 3.2). Both facts are documented; the consequence — that an outsider
cannot start — is not stated anywhere.

**Disposition: fixed here, as a script rather than an endpoint.**
`scripts/seed-demo-tenant.mjs` creates the tenancy tree and prints one key, and
the README says which half of the constitution's "seeded demo tenant" clause that
closes: the intent, not the letter, because compose starts stores rather than
services and no invocation of it can seed anything.

## G5 — `POST /auth/dev-token` answers 200, not 201

**Found by:** `expected 200 to be 201`, written on the assumption that minting is
creation.

It is defensible either way — a token is not a resource with a URL — and it is
written down nowhere. Small, and exactly the kind of thing that costs an
integrating developer twenty minutes.

**Disposition: scheduled with the rest of the public surface, chapter 3.15.** The
error reference this chapter added documents failures; there is no endpoint
reference yet, and inventing half of one for a single status code would be worse
than the gap. Recorded so 3.15 inherits it.

## G6 — the series' socket examples predate Node's own WebSocket

**Found by:** `ws` resolving at runtime by the ordinary parent walk while its
TYPES did not, which forced a choice the suite had not planned to make.

Every socket example in the series uses the `ws` package. Node has shipped a
standards-compliant global `WebSocket` since 22.4, and the platform requires Node
22 — so an integration in 2026 needs no library at all, and the constructor call
in the series' examples is identical either way.

**Disposition: not a defect, and it improved the suite.** `packages/outsider` now
imports nothing but vitest, which is a stronger seal than one whose dependency list
is empty because three things were reached for sideways. Worth a sentence in the
chapter; worth nothing in the SRS.

---

# The Phase 2 exit criterion — verdict

> "an external developer integrates using only public documentation, with no
> assistance"

**MET IN PART**, and the part that is missing is not the part this chapter set out
to fix.

**What is met, and how it was checked.** `packages/outsider` completes a full
integration against a platform it did not start: it creates a channel, repeats the
call and gets the existing one, has a private channel refused with the field named,
adds two members who did not exist, mints a token for one of them, sends over REST
and reads history back, sends over a socket and receives the event, and confirms
that a foreign resource and an absent one answer identically. **Eight tests, all
passing**, against `docker compose --profile services`, in CI as its own job.

It is sealed in three levels and each was demonstrated failing, one at a time:
`@relay/protocol` by package name does not resolve at all; the same import by
relative path is refused by `no-restricted-imports`; a path built from `".."`
string literals, and `createRequire`, are refused by `no-restricted-syntax`.

**What is not met.** Two things, and they are different in kind.

The first is G1. An integration that sends over REST and waits on a socket cannot
succeed, and no document says so. The suite passes because it was CORRECTED by a
failing test — which is precisely the assistance the criterion forbids. A real
outsider would have filed a bug or given up. Until the platform delivers a
REST-sent message or the documentation says it does not, the criterion is not met
for that path.

> **Met as of chapter 3.18.** The platform delivers a REST-sent message: the api
> publishes to `chan:{channel_id}` after commit, and the sealed outsider's REST-send /
> socket-receive test passes with no correction to the suite. The condition this
> paragraph set — *"until the platform delivers a REST-sent message"* — is the one that
> was satisfied, rather than the documentation alternative.

The second is the criterion's harder half, and no test can reach it. **Content
sufficiency is not comprehensibility.** This chapter measured whether the
documentation CONTAINS what an integration needs. Whether a person reading it
without help can build one is a different question, and a person is the only
instrument for it — this chapter does not use one, and says so rather than letting
eight passing tests stand in for a reader (FR-034).

The same distinction applies to the seal. The dependency rules are mechanical:
workspace code is unimportable, provably, three ways. Not READING the repository's
source is a discipline, and no configuration can enforce it. Three rules must not
be left to imply a fourth.

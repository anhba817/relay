# Quickstart — validating chapters 3.15 and 3.16

Eighteen checks. Run in order; several depend on earlier ones. Every command is one a
maintainer runs, verbatim.

**This is a validation guide, not the published quickstart.** Constitution VI's clause
— "the quickstart MUST run unmodified, verified by automated execution in CI against
the published documentation" — is met by the `outsider` job, which runs the README's
documented sequence verbatim: compose up, migrate, seed a demo tenant, run the sealed
suite. Chapter 3.14 built that. The file you are reading is the Spec Kit artifact a
maintainer walks by hand, and every check below carries the command that runs it.

**Six of the checks are negative**: they require breaking something on purpose and
watching a test fail — V2's guard array, V6's suite removals, and one removal per column
that began this feature dead, at V3, V10, V14 and V15. FR-035 exists because of them: a test that
passes with and without the code it covers is measuring nothing, and the only way to know
which kind you have is to remove the code. The count said three until analysis pass two
counted the tasks and found five removals and a guard break.

## Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm install
pnpm build
node services/api/dist/db/migrate.js
```

The four variables only CI sets. Without them 11 tests fail in a way that reads as
regression — a missing platform credential fails `limits.itest.ts` and cascades into
the dispatcher, and NATS comes back `CONNECTION_REFUSED`:

```bash
export RELAY_REDIS_URL=redis://localhost:6379
export RELAY_NATS_URL=nats://localhost:4222
export RELAY_INTERNAL_CREDENTIAL=rk_svc_ci_0123456789abcdef0123456789abcdef
export RELAY_WEBHOOK_SECRET_KEY="BpDal75yBZp7Fc2GtGS3D1vh7qOKgCWJkF6/d0XWxBU="
export RELAY_DB=postgres://relay:relay@localhost:15432/relay
```

`RELAY_DB` is for the `psql` checks below and nothing else. V1 and V11 used it before it
was defined anywhere — two commands that could not run, in the file whose first line
says every command is one a maintainer runs verbatim. Found by analysis pass two.

`DATABASE_URL` stays unset — every package falls back to 15432, this project's
documented port, and this machine's own Postgres holds 5432.

---

## V0 — the lanes and the dead-column count, before anything changes

```bash
pnpm lint && pnpm typecheck && pnpm turbo run test
pnpm test:integration
pnpm coverage
```

**Expect** the numbers chapter 3.12 closed on: 379 unit, 407 integration in 10 tasks,
771 under coverage with every ratchet met.

Then the count this feature is about. Five columns exist and are read by nothing —
`channels.type`, `channels.archived_at`, `users.avatar_url`, `users.metadata`,
`users.banned_at`. Record it now (SC-016). A count taken after Phase 2 measures the
edit, not the starting position.

## V1 — the migrations apply, and apply twice

```bash
node services/api/dist/db/migrate.js
node services/api/dist/db/migrate.js   # again
psql "$RELAY_DB" -c '\d read_positions' -c '\d+ members' -c '\d+ channels'
```

**Expect** `read_positions` with primary key `(channel_id, user_id)` and no `id`
column; `members.role` defaulting to `'member'`; `channels.last_activity_at` with the
`(environment_id, last_activity_at desc)` index. The second run is a no-op.

**And check the CHECK is the right one.** `members_role_check` names
`owner, moderator, member`. If it names `admin`, the migration reused
`memberships.role`'s constraint — R8's trap, which looks correct in review.

## V2 — the guard's tenth table

```bash
pnpm vitest run packages/test-harness/src/guard --config packages/test-harness/vitest.integration.config.mts
```

**Expect** the sentinel refusal for `read_positions`, naming the composite key rather
than `undefined`. That is the `coalesce(to_jsonb(OLD) ->> 'id', to_jsonb(OLD)::text)`
expression chapter 3.13 installed, working for a table with no `id`.

**Then break it**: drop `read_positions` from `sentinel.sql`'s array, re-run. The suite
must fail. Restore it. Chapter 3.13 learned that a table in the array is not the same
as a table the guard watches.

## V3 — the membership check, and it fails when removed

```bash
pnpm vitest run services/api/src/db/repository --config services/api/vitest.integration.config.mts
```

**Expect** a send to a private channel by a non-member refused **with the not-found
envelope** — not a `403` naming the membership — and the channel's message count unchanged
afterwards (FR-001, SC-003). A refusal that still writes a row is not a refusal, and a
refusal that names what it is refusing is not indistinguishable: SC-002 covers send along
with the three reads, so this answer has to match a channel that does not exist.

**And the same refusal on the public route with a user token** —
`POST /v1/channels/:channelId/messages` is the only one of the three send paths a
customer's client calls, and until analysis pass seven it was the one no check reached:
`MessagesController` declares no `@Accepts`, so a user token is accepted, and the
controller passed no user, so the `userId`-gated check never fired.

**Then remove the check** from `repository.sendMessage` and re-run. The test must fail.
This is FR-035's gate; the column table lists every removal this feature owes.

## V4 — the six callers inherit it

```bash
grep -rn "sendMessage(" services/api/src --include=*.ts | grep -v itest | grep -v "\.test\."
```

**Expect** six call sites, none of them passing a check of its own. The check is in one
function because the signature already says who is acting — `userId` present means a
user, absent means the tenant — and that is what constitution I means by data access
rather than handlers.

## V5 — a private channel is indistinguishable from absent

```bash
pnpm vitest run services/api/src/isolation --config services/api/vitest.integration.config.mts
```

**Expect** for each of **SC-001's four verbs — send, resume, subscribe and read by id**:
the private channel the caller cannot see and a channel that exists nowhere give the same
status and the same body, `request_id` excepted (SC-002). Chapter 3.12 built the oracle;
this is the first use of it inside a single tenant.

**Read by id is a route this feature adds** (FR-003a). It did not exist —
`channels.controller.ts` had a create and a member-add and no read — while this check,
SC-001 and the authorization table all assumed it. Analysis pass three found it by asking
whether each verb had a handler.

## V6 — the same-tenant attack exists and is new

```bash
pnpm vitest run services/api/src/isolation/gauntlet --config services/api/vitest.integration.config.mts
```

**Expect** at least one same-tenant, non-member attack per verb (SC-015), on a fixture
that is not `seedTwoTenants` — one environment, two users, one channel, one of them not
a member. All four pre-existing attack shapes take another tenant's identifiers, so
this is new work rather than a reuse.

**Then remove each new check in turn** and confirm the matching attack goes red — the
suite's own removals, T086. Chapter 3.12 found that a scoped `channelExists` running
first hides an unscoped read below it, so record which of these attacks are masked that
way rather than reshaping them.

## V7 — the derived target count moves by exactly the routes added

```bash
pnpm vitest run services/api/src/isolation/targets --config services/api/vitest.integration.config.mts
```

**Expect** the count from V0 plus **14** — the routes the two contracts describe, plus
FR-003a's read-by-id — each matched to exactly one classification entry (SC-014). **The
classification entries use the router's parameter names**, `:channelId` and not the
contracts' `:externalId`: `targets.ts` compares literal path strings. An unclassified route fails the
suite on the build that adds it, which is the point of deriving the list rather than
writing it.

## V8 — the private type accepted, and the repeat that must not change it

```bash
pnpm vitest run services/api/src/channels --config services/api/vitest.integration.config.mts
```

**Expect** `POST /v1/channels` with `type: "private"` returns 201 and the row reads
back `private` (SC-006) — read back **through `GET /v1/channels/:channelId`**, which is
what FR-003a adds and the only way a customer can see the four fields at all; a second
creation naming `public` returns 200 with the existing channel, still `private` (FR-010).

## V9 — removal, and the messages that survive it

```bash
pnpm vitest run services/api/src/channels --config services/api/vitest.integration.config.mts
pnpm vitest run services/gateway/src/isolation --config services/gateway/vitest.integration.config.mts
```

**Expect** a removed member's send refused; their reconnection carrying no history for
the channel (SC-004); their existing messages still in history, still attributed to
them (SC-005). Removing a non-member and removing a user who does not exist both give
200 `not_a_member` — see `contracts/membership.md` for why the second is not a 404.

## V10 — the archive refuses with its own code

```bash
pnpm vitest run services/api/src/channels --config services/api/vitest.integration.config.mts
```

**Expect** a send to an archived channel **the caller can see** refused with
`channel_archived`, distinct from not-found and from `user_banned` (SC-010); history still
readable; archiving an archived channel a 200 no-op.

**And the order, tested with the oracle rather than read from the code** (FR-021a): an
archived *private* channel the caller cannot see answers exactly as an absent one, and a
banned user gets `user_banned` for a channel id that exists and for one that does not. Ban,
then membership and visibility, then archive — reversed, the archive refusal becomes the
existence oracle the membership refusal is not allowed to be.

**Then remove the `archived_at` read** and confirm the refusal test goes red.

## V11 — roles round-trip, and the fourth value is refused

```bash
pnpm vitest run services/api/src/channels --config services/api/vitest.integration.config.mts
psql "$RELAY_DB" -c "insert into members (channel_id, user_id, role) values ('…','…','admin')"
```

**Expect** `owner`, `moderator` and `member` accepted; a fourth value refused 400 with
`field: "role"` (SC-009). The field name in the envelope is only there because chapter
3.14 made `ZodValidationPipe` carry `issues[0].path`.

**And the raw insert refused by `members_role_check`.** That second command is the one
that matters: a schema at the edge rejecting `admin` says nothing about the constraint
underneath it, and R8's trap is a constraint that accepts the organisation vocabulary.

## V12 — the listing orders, pages and excludes

**Expect** a user's channels most-recently-active first; a cursor that pages without
overlap or gap; a channel the caller is not a member of absent (SC-007, FR-015). Two
channels sharing a `last_activity_at` must page correctly — that is what `id` is doing
in the keyset.

**Then remove the `last_activity_at` ordering** and confirm the order test goes red.

**And measure it.** The index has to be used:

```sql
EXPLAIN ANALYZE SELECT … ORDER BY last_activity_at DESC, id DESC LIMIT 50;
```

**Expect** an index scan. A sequential scan here means the index is not being used and
R4's 145× is not being collected.

## V13 — the unread count, including the tombstone

```bash
pnpm vitest run services/api/src/users --config services/api/vitest.integration.config.mts
```

**Expect** the count rises with each message and falls to zero when a position is set
to `last_sequence` (SC-008). Then delete a message and check the count again: it stays
the same, because a tombstone keeps its sequence. That is the approximation FR-019
requires be stated, and this is where a reader sees it.

A position past `last_sequence` is refused 400 with `field: "sequence"`; a replayed
lower position is a 200 no-op.

**Then remove the read-position read** from the unread count and confirm the count test
goes red.

## V14 — the user surface

```bash
pnpm vitest run services/api/src/users --config services/api/vitest.integration.config.mts
pnpm vitest run services/gateway/src/isolation --config services/gateway/vitest.integration.config.mts
```

**Expect** all three profile fields round-trip; metadata over 4 KB and a malformed
`avatar_url` refused 400, each naming its field (SC-011); 100 users upsert in one
request and 101 refused (SC-012); a deleted user's messages still readable and still
attributed, their memberships gone, their `usage_active_users` rows untouched.

Then present the deleted user's external id again: the same row comes back with
`deleted_at` cleared and empty profile fields (FR-030).

**Then remove the `avatar_url` and `metadata` reads** and confirm the round-trip goes
red. **And the `deleted_at` read**, confirming the 404-for-a-deleted-user test goes red —
pass five found that column written, cleared and never read.

## V15 — the ban, and the token that creates

**Expect** a banned user refused at connect and on send with `user_banned`; their
history still readable by others (SC-013). The already-open connection behaves the way
the chapter says it does — whichever answer FR-032 takes, this check is where it is
verified rather than asserted.

```bash
pnpm vitest run services/api/src/auth --config services/api/vitest.integration.config.mts
```

**Expect** a token minted for an identifier with no user row, then a message sent
through `POST /internal/messages` and accepted (SC-020). Before this feature that
sequence answers `400 "unknown user"`.

**Then remove the `banned_at` read** and confirm the ban test goes red.

## V15a — the chapter citations, classified

```bash
cd relay-platform
grep -rn "chapter 3\.1[2-6]" --include=*.ts --include=*.sql --include=*.mjs . \
  | grep -v node_modules
```

**Expect** every hit to name the chapter its change was taught in. The starting position
is 31 files and 40 `chapter 3.12` citations, of which 12 files are fenced in chapter
3.12's page — 9 are taught in 3.13, 9 in 3.14, and `exempt.ts` only in the post-series
appendix. Classify all 40 and record the wrong count before correcting any of them
(SC-021).

**Two things not to correct.** The `FR-` and `R` identifiers stay: they name
`specs/033-chapter-3-12/`, and a feature directory is named once (FR-038b). And a
citation naming a chapter for something other than its own file's change — chapter 2.2
for `last_sequence` — is already right; rewriting it is the correction making things
worse.

A comment inside a titled fence moves three files at once, so run `pnpm check:fences`
after this one and not only at V16.

## V16 — the gates, the battery, and the prose

```bash
pnpm lint && pnpm typecheck && pnpm build
pnpm turbo run test && pnpm test:integration && pnpm coverage
pnpm test:outsider
cd ../relay-tutorial && pnpm check:docs && pnpm check:errors && pnpm check:fences
```

**Expect** the error registry at 16 codes and 16 reference sections, checked in both
directions. `check:fences` green — 203 files at the last tag, and every file either
chapter touches has to replay.

Then the dead-column count again. **Five before, and the after-count is not zero:** all
five named columns get readers, and this feature leaves two behind that have none —
`members.role`, which FR-012 and T069 establish nothing reads, and
`read_positions.updated_at`, written by every position write and read by nothing. Name
each survivor beside the requirement it stands for (SC-016, FR-036). A feature about
columns nothing reads, adding two, is worth a sentence on the page rather than a zero
that does not hold.

Then the battery. Twenty consecutive runs of the integration lane, on a machine running
nothing else:

```bash
for i in $(seq 1 20); do … done   # the loop from specs/032-chapter-3-11/
```

**Expect** 20 green, and record the mean. Chapter 3.12 closed at 193.25 s. Run 11 of
that battery failed with `api never became healthy` at 135 s against a 193 s mean, and
the cause was two Next.js dev servers on the same machine compiling an MDX page — the
evidence was the wall-clock timeline, not the error message. A battery is only a
measurement if nothing else is running.

Last, the prose (SC-018, SC-019): each page's word count inside 2,000–4,000 by the
counter the series uses, and the split recorded with the file count that produced it —
**25 as R12 measured it, corrected to 29 by R18 before any prose was written**, and the
sentence that the correction removed the floor argument the split was decided on.

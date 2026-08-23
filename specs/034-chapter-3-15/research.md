# Research — chapter 3.15's feature

**18 items, R1 to R18.** Twelve were measured against a running database or the code
rather than reasoned about. Two measurements pointed the wrong way at first, and both are
recorded with the number that misled and the number that settled it — as is one worry the
measurement refuted outright (R18).

R1 appeared **twice** in this file from analysis pass seven to pass twelve: the pass that
appended the caller-count correction re-emitted the whole section instead of extending it,
and five passes read past a duplicated header. Removed in pass twelve.

---

## R1 — the membership check has a home, and the signature already says so

**Decision**: the check goes inside `repository.sendMessage`, gated on `userId`
being present.

`sendMessage` already takes `userId?: string`. That optionality is not an accident of
the API — it is the distinction the whole clause turns on:

    userId present    a USER is sending. Membership applies.
    userId absent     the TENANT is sending through an application key.
                      There is no member to check.

So FR-005 — what a private channel means for an application credential — is answered
by a type that already exists rather than by a new decision. And putting the check in
the repository rather than a service satisfies constitution I directly: *isolation
lives in data access*. Every caller inherits it. **The list below said six and is wrong** —
it counted files that mention a send anywhere, not call sites; the corrected graph is at the
end of this item:

    packages/e2e/src/harness.ts            services/api/src/isolation/fixtures.ts
    services/api/src/messages/…service.ts  services/gateway/src/api-client.ts
    services/gateway/src/isolation-…ts     services/gateway/src/session.ts

The socket path reaches it through `api-client` → `POST /internal/messages` →
`messages.service.send` → `repository.sendMessage`, so one edit covers the socket and
the internal route together.

**Alternatives considered**: a guard on `/internal/messages` (misses `sendMessage`'s
other callers and puts a tenancy rule in a controller); a check in
`messages.service` (two controllers call it, and the fixtures do not).

**AND THE CALLER COUNT WAS WRONG, WHICH HID A HOLE.** This item said six callers inherit
the check. Counted in analysis pass seven:

    repo.sendMessage        messages.service.ts:47        (+ isolation/fixtures.ts, a test helper)
    MessagesService.send    messages.controller.ts:40     the PUBLIC route
                            internal.controller.ts:65     the socket's route

Three call sites, not six — and the important one supplies nothing.
`messages.controller.ts:40` calls `this.messages.send(channelId, body)` with **no user**,
and `MessagesController` declares no `@Accepts`, so `credential.guard.ts` falls back to
`EITHER = ["application","user"]` and a user token is accepted there. So a user sends to a
private channel they are not a member of through the route a customer's client actually
calls, `userId` is absent, and the gate opens.

**The decision survives; the argument for it did not.** "The signature already encodes who
is acting" is true of the signature and false of that caller: a parameter nobody fills in
encodes nothing. The check stays in the repository — constitution I is explicit that
isolation lives in data access — and T031a makes the public route say who is acting, which
is what the argument assumed all along. Six passes read the number and none counted it.

## R2 — reading is already membership-scoped; only sending is not

**Measured**, by reading both paths:

    repository.backfill      joins `members` on the caller's user id — membership
    session.controller       builds its list from `channelsForUser` — membership
    listMessages             `environment_id` only
    channelExists            `environment_id` only
    /internal/messages send  resolves the user, checks nothing

The two that scope by environment alone are reached from the **public** history route,
which is application-authenticated and has no user — so they are correctly unscoped by
membership.

The gap is one line's worth of behaviour in one function, and chapter 3.12's shipped
comment claiming "no membership check on any read path" is wrong. That comment is
inside a titled fence in chapter 3.13's page in two locales; FR-037 owns the
correction and it is fence work, not a source edit.

## R3 — `channels.type` gets a reader, and FR-CHN-03's word "join" is the hard part

**Decision**: `private` requires membership on every verb. `public` permits a
tenant user to **read** without membership, to **send** without membership, and to
**join**, where joining is a new user-initiated operation.

**Send was missing from this decision until the first analysis pass**, which found
`contracts/membership.md` granting it while this paragraph listed only read and join.
FR-CHN-03's words are "read and join", so the clause does not settle it and FR-004 is
what asks for an answer. The answer is send, for one reason: a channel a tenant user can
read and join but not post in is a channel where the platform refuses a write it will
accept one request later, after a join that cannot be refused. That is a refusal with no
meaning behind it. The cost is that `public` is a weaker word than it looks — it means
"open to this tenant", not "readable by this tenant" — and the chapter has to say so.

FR-CHN-03's exact words are that any authenticated user of the tenant "may read and
join" a public channel. If membership were required for both types, `channels.type`
would still have no reader and FR-CHN-03 would still be unimplemented — the column
becomes live only because the two types differ.

**The subscription set is not the read set**, and keeping them apart is what makes
this affordable. A public channel is readable on demand by id; it is *subscribed*
only if the caller is a member. Putting every public channel into every user's session
would make the session unbounded in a tenant with many channels.

**Alternatives considered**: membership for both types (leaves the column dead and the
clause unmet); public channels auto-subscribed for every tenant user (unbounded
session, and a socket that delivers channels a user never asked for); read-and-join
without send (a refusal a join makes disappear).

## R4 — `last_sequence` cannot order channels by activity, and the test lane says otherwise

**Decision**: a `channels.last_activity_at` timestamp with an index on
`(environment_id, last_activity_at DESC)`.

**And this is the measurement that pointed the wrong way.** Ordering by
`max(messages.created_at)` against the test lane looked free:

    the test lane, busiest environment by messages: 579 messages, 32 channels
    aggregate ordering, three runs:  1.942 ms   0.630 ms   0.870 ms

Reporting 0.87 ms would have settled the question in favour of adding no column. The
test lane's largest environment holds 579 messages, so the number measures nothing a
real tenant would do. Measured again in a scratch database with **2,000 channels and
1,000,000 messages**, one member in every channel:

    aggregate over messages   159.737 ms   158.103 ms   158.842 ms
                              → Seq Scan on messages, 1,000,000 rows, every call
    indexed column              1.102 ms     1.496 ms     2.210 ms

**145× apart, and the aggregate scans every message in the environment on every
listing.** The cost grows with message volume, which is the one thing a chat platform
guarantees will grow.

**Alternatives considered**: the aggregate (above); ordering by `last_sequence`
(a per-channel counter — two channels at sequence 50 say nothing about which was
active more recently, so it cannot order channels against each other at all).

## R5 — the unread count needs no counter, because `last_sequence` already counts

**Decision**: unread is `greatest(channels.last_sequence − read_position, 0)`.

Three shapes measured on the same 1,000,000-row dataset, for one page of 50 channels:

    count rows past the read position    9.807 ms   11.109 ms   13.431 ms
    a cached counter on the position     2.129 ms    1.928 ms    1.226 ms
    last_sequence − read position        1.122 ms    4.426 ms    4.497 ms

The third needs no counter and has nothing to invalidate: `channels.last_sequence` is
already maintained by the write path, and chapter 2.2 made it the sequencing authority.
The cached counter is no faster and adds a value that can go stale.

**The approximation this accepts, and FR-019 asks for it to be stated**: a tombstoned
message still occupies a sequence, so a deleted message counts as one unread. The
alternative is counting rows, which is 10× the cost to make a deleted message stop
being unread.

**Alternatives considered**: both of the above.

## R6 — a read position is one table with two columns and no counter

**Decision**: `read_positions (channel_id, user_id, sequence)`, primary key on the
first two, `environment_id` for the guard.

It is the only entity in this feature with no storage today — measured: no `last_read`,
`read_at` or equivalent anywhere in the schema. It needs `environment_id` because
feature 030's guard watches tables that carry one, and a table without it is a table
the guard cannot see (chapter 3.13 extended the guard to nine tables for exactly this
reason).

Positions advance forwards only, and a position past `last_sequence` is refused —
FR-018 — because a position nothing can reach makes every later count wrong.

## R7 — deleting a user keeps the row

**Decision**: clear the profile fields, delete the memberships, keep the `users` row
with a deletion marker.

Three tables reference `users.id` — `messages`, `members`, `usage_active_users` —
verified in the schema. FR-USR-05 asks that messages be preserved "as authored by a
deleted user", and chapters 3.13 and 3.14 established that a NULL author makes a
message **invisible to sockets**: `backfill.controller`'s `toFrame` drops senderless
rows because `messageSchema` requires `user`. So `ON DELETE SET NULL` would satisfy
the letter of "preserved" while making those messages undeliverable.

`usage_active_users` is billing history and is not touched — FR-029.

**Alternatives considered**: `ON DELETE SET NULL` (breaks delivery); `ON DELETE
CASCADE` (deletes the messages the clause says to keep); a separate
`deleted_users` table (a second identity space for one flag).

## R8 — two role vocabularies, and neither may borrow the other

**Measured**: `memberships` already has a `role` column with
`CHECK (role IN ('owner','admin','member'))` — that is FR-TEN-07, a human's role in an
organisation. FR-CHN-04's channel roles are `owner`, `moderator`, `member`.

Different tables, different subjects, and one word different. A migration that reused
the organisation constraint would accept `admin` on a channel member and refuse
`moderator`, and the CHECK would look correct in review.

**Decision**: `members.role` with its own CHECK naming the SRS's three, and a comment
on each constraint pointing at the other.

## R9 — FR-USR-02 is unmet, and its absence is already a bad error message

**Measured**: `createUser` is called from exactly one non-test place —
`channels.service.ts`, on first membership. `POST /auth/dev-token` mints a token for
an identifier that need not exist, and creates nothing.

`POST /internal/messages` then looks the user up and throws
`BadRequestException("unknown user")`. So the sequence *mint a token, send a message*
fails with a `400` that names the caller rather than the cause — which is precisely
what implicit creation on authentication exists to prevent.

**Decision**: the token route creates the user if absent, using chapter 3.13's
idempotent `createUser`, so authentication and membership converge on one row for one
external identifier.

## R10 — the gauntlet needs a fixture it does not have

**Measured**: `services/api/src/isolation/fixtures.ts` seeds **two tenants**, and all
four attack shapes take another tenant's identifiers. A non-member of the caller's
*own* tenant is a different fixture — one environment, two users, one channel, one of
them not a member — and nothing in the suite has it.

**Decision**: a second fixture beside `seedTwoTenants`, and one attack per verb. This
is new work rather than a reuse, and FR-034 says so.

## R11 — which error codes this feature adds

**Measured**: the registry holds thirteen after chapter 3.14. Three refusals in this
feature have no code:

    not_a_member          a user acting on a channel they do not belong to
    channel_archived      a send to an archived channel
    user_banned           a banned user connecting or sending

Each is a distinct fact a client acts on differently, which is the test chapter 3.14's
registry comment sets: `channel_member_limit_exceeded` is separate from
`quota_exceeded` because one resets on a date and the other never does. Sixteen codes
after this feature, and `docs/08-error-reference.md` gains three sections — checked
in both directions by the existing `check:errors`.

**Alternatives considered**: reusing `forbidden` for all three (a client cannot tell
"join the channel" from "wait for the archive to lift" from "contact support").

## R12 — the split, measured before any prose exists

FR-040 requires this, and chapter 3.12's close-out is why: it estimated 37 fenced
files, shipped **61**, and took the split at Phase 12 — after prose for the discarded
sections had been written.

Counted by enumerating the files each clause group must touch and verifying every one
exists (a design that names a file that is not there is a design that has not been
checked):

| Group | changed | new | total |
|---|---|---|---|
| A — membership, private type, removal (FR-CHN-03, 05, 06) | 11 | 1 | 12 |
| B — listing, unread, archiving (FR-CHN-08, 09, 10) | 10 | 2 | 12 |
| C — users and roles (FR-USR-02→06, FR-CHN-04) | 10 | 6 | 16 |
| corrections (FR-037, FR-038) | 1 | 0 | 1 + 2 locale pages |

**Union: 16 existing files changed, 9 new, 25 platform files.** **Superseded by R18's
enumeration: 34.** This count was revised twice, and the second revision found a file no
task named.

At chapter 3.11's measured ratio — 21 files, 31 fences, 3,316 prose words, so ~1.5
fences per file and ~107 words per fence:

    A          12 files ≈ 18 fences ≈ 1,926 words
    B          12 files ≈ 18 fences ≈ 1,926 words
    C          16 files ≈ 24 fences ≈ 2,568 words
    A+B+C      25 files ≈ 38 fences ≈ 4,000+ words

**The three-way split fails, and it fails at the floor rather than the ceiling.** The
bound in `docs/07-tutorial-plan.md` is 2,000–4,000 prose words; A and B each land at
about 1,900. Chapter 3.12's split only had to avoid the ceiling, so this is the first
time the other end of the bound has decided anything.

**One chapter also fails**: 25 files lands at the ceiling before any allowance for the
estimate running low, and it has run low twice — chapter 3.5 estimated 22 fences and
shipped 39, chapter 3.12 estimated 37 files and shipped 61. Chapter 3.11's was exact.
An estimate at 4,000 with a known upward bias is an estimate that breaks the bound.

**Decision: two chapters, grouped by subject rather than by arithmetic.**

| Chapter | Carries | Files | ≈ words |
|---|---|---|---|
| **3.15** the channel a customer controls (R18 supersedes these counts: 19 and 20 files against a 34-file union) | membership enforcement, the private type, removal, member roles, archiving — who is in a channel, what kind it is, and whether it is open | 17 | ≈ 2,730 |
| **3.16** what a user sees | listing with cursor pagination, activity ordering, unread counts, and the whole user surface — profile, bulk upsert, deletion, banning, and implicit creation on authentication | 20 | ≈ 3,210 |

Both inside the band with room for the estimate to run low, and each has one subject a
reader can hold. Roles move to 3.15 because a role is a property of membership;
archiving moves to 3.15 because "can anyone write here" belongs with "who may write
here".

## R13 — where each of the five dead columns comes alive

| Column | Read by, after this feature | Chapter |
|---|---|---|
| `channels.type` | the membership check in `sendMessage`, and the by-id read check | 3.15 |
| `channels.archived_at` | the same check, refusing with `channel_archived` | 3.15 |
| `users.avatar_url` | the profile route's read and write | 3.16 |
| `users.metadata` | the same | 3.16 |
| `users.banned_at` | the socket's connect path and the send check | 3.16 |

FR-035 requires each to be shown read by a test that fails when the read is removed.
Being written is not being read — chapter 3.13 recorded the same distinction when it
found that adding a table to the guard's trigger array is not the same as the guard
watching it.

## R14 — no ADR is required, and one candidate was weighed

Nothing here chooses between architectures. The read position is a new table in the
existing store on the existing writer; the activity column is a denormalisation inside
one table; the membership check is a predicate in the layer constitution I already
assigns it to.

**The candidate was the activity column.** Denormalising a derivable value is the kind
of decision an ADR exists for, and R4's numbers are what make it not one: 159 ms
against 1.1 ms with a sequential scan over every message, on a query a client runs to
render its first screen. A decision with a 145× measurement behind it and no rejected
architecture is a recorded rationale, not an architecture decision.

## R15 — the guard, and the two new tables

`read_positions` carries `environment_id` and therefore belongs in feature 030's
trigger array, taking it from nine tables to ten. Chapter 3.13 recorded what that
costs: the refusal message needs a key expression that works for a composite primary
key, and the bait must be planted in a state no global drain can claim — a lesson that
cost thirteen failing tests in two unrelated files when it was got wrong.

`read_positions` has a composite primary key `(channel_id, user_id)` and no `id`, so
it needs the `coalesce(to_jsonb(OLD) ->> 'id', to_jsonb(OLD)::text)` expression chapter
3.13 already installed. Nothing drains read positions globally, so its bait is not
claimable by construction.

## R16 — what this feature does not do, named rather than implied

- **Presence in a private channel — and there is nothing to defer yet.** FR-CHN-05 names
  presence alongside read and send, and `presenceChangedSchema` is in the protocol's frame
  union (`packages/protocol/src/frames.ts:87`). **Nothing emits it**: the gateway sends no
  presence frame anywhere, so a non-member receives none because nobody receives any. The
  earlier wording here — "in scope only as far as: a non-member's socket is not subscribed,
  so it receives no presence for it" — read as though presence flowed, and analysis pass
  twelve found the claim vacuously true. When FR-RTM-07 gives the frame an emitter, the
  subscription set is what will scope it. A declared frame with no sender, in a feature about
  five declared columns with no reader, is worth a sentence on the page.
- **A REST-sent message reaching a socket — half of it.** Chapter 3.14's gap G1 has **two
  independent causes**: the api publishes to no fan-out, and the public send attributes no
  user. This feature must fix the second, because FR-001 cannot hold without it — a
  membership check gated on `userId` never fires on a route that supplies none (R1, T031a).
  It does **not** touch the fan-out, which stays with FR-RTM-05. So G1 closes halfway here,
  and the half that closes is the half this feature's own central requirement depends on.
  Stated this way because analysis pass seven found R16 declaring the whole gap out of
  scope while FR-001 required part of it.
- **The outbox's message-text retention.** Chapter 3.12's finding, owner FR-MOD-06.
- **A human reading the documentation.** Chapter 3.14's verdict on the Phase 2 exit
  criterion said content sufficiency is not comprehensibility, and that a person is
  the only instrument for the second. This feature does not use one either.

## R17 — nineteen files point a reader at the wrong chapter

**Found while checking a citation for R15**, which is the only reason it was found:
`exempt.ts` says "NINE GUARDED TABLES AS OF CHAPTER 3.12", and the guard's ninth table
is taught in chapter 3.13.

The previous feature was specified as one chapter and shipped as three. Its record
directory is still `specs/033-chapter-3-12/`, which is correct — a feature directory is
named once. What moved is the *chapter number a reader is sent to*, and the comments
written during that feature were not revisited after the split.

Measured against the three published pages, matching each cited file against the page
that fences it:

    files citing "chapter 3.12" in a comment        31   (40 citations)
      fenced in chapter 3.12's page                 12   correct
      fenced in chapter 3.13's page                  9   wrong page
      fenced in chapter 3.14's page                  9   wrong page
      fenced in no chapter page                      1   exempt.ts, in the post-series appendix

**Nineteen files send a reader to a page that does not contain them.** Four examples,
each pointing somewhere different from where its subject is taught:

    zod-validation.pipe.ts:18   "chapter 3.12 is where that stopped being optional"   → 3.14
    codes.ts:71                 "(chapter 3.12, FR-046)"                              → 3.14
    session.ts:94               "(chapter 3.12, FR-025)"                              → 3.14
    repository.ts:2698          "THREE OUTCOMES, NOT A BOOLEAN (chapter 3.12, R14a)"  → 3.13

**The requirement identifiers in those comments stay as they are.** `FR-025` and `R14a`
belong to the feature, and the feature is `specs/033-chapter-3-12/`. Only the chapter
number is wrong, and only where the citation points a reader at a page.

**Decision**: classify all 40 citations and correct the chapter number where the cited
page does not carry the file. This is the same shape as FR-037 — a stale sentence in a
source file that is also inside a published fence — so a corrected comment in a fenced
file is three files moving together, and `pnpm check:fences` fails if they do not.

**This now has its own requirement.** FR-037 covers one sentence in
`channels.schema.ts` and FR-038 covers one row in a traceability map; neither reached
this, so it is **FR-038a** — the rule, with the measurement above as its starting
count — and **FR-038b**, which says what must not change: the `FR-` and `R` identifiers
inside those comments name the feature record, and a feature directory is named once.
Verified by **SC-021**: all 40 citations classified, the wrong count recorded, and that
count reaching zero.

**And the rule needed a boundary.** "Every citation must name the chapter that fences
the file" is the wrong rule — `last_sequence` is cited to chapter 2.2 in files taught
much later, and that citation is correct. The rule is about the chapter a *change* was
taught in, which is why FR-038a says so and the edge case beside it names the case that
would otherwise be corrected into a mistake.

**Alternatives considered**: leaving them (a code comment that names a chapter is a
reference, and a wrong reference is worse than none — the series' own argument for
fixing `docs_url`, which chapter 3.14 made); rewriting the citations to name the
feature directory instead of a chapter (correct and useless to a reader, who is holding
a chapter and not a spec directory).

## R18 — the split's arithmetic, re-derived after the task list existed

The first analysis pass raised three things about R12's numbers. Two are real, one is
refuted by its own measurement, and the third changes what the split rests on.

### The file count was low, twice, and the enumeration is why

R12 counted **25** platform files from the clause list. The task list named **29**
(analysis pass one). Enumerating properly — every path a task line names, basenames
canonicalised, plus three files the tasks imply and never name — gives **34**.

    24 changed  +  7 new   =  31 files the tasks name
     3 more the tasks imply and never name:
         services/api/src/app.module.ts        UsersModule has to be registered
         services/api/src/users/users.module.ts    "module, controller, service" — T109
         services/api/src/users/users.service.ts
    ── 34 platform files, of which:
        32 are taught by one chapter or both
         2 are conditional and taught by neither — packages/test-harness/src/exempt.ts
           and eslint.config.mjs, touched only if T011 finds a file needing an entry
         1 is read, not changed — services/api/src/isolation/compare.ts (T043 uses it)

**Each revision was found by a mechanism, not by rereading.** 25 → 29 came from the task
list naming files a clause list cannot reach. 29 → 34 came from asking which chapter
fences each file, which is the question that finds a file nothing registers: `app.module.ts`
appeared in **no task at all**, and without it none of the eight user routes mount.

**The lesson is the same one three times: a count without an enumeration cannot be
checked, and every check found more.** So the enumeration is below, and it is what the
split rests on now.

### Which chapter teaches which file — the canonical table

Derived from the phases that touch each file, not assigned by path: assigning by path
guessed wrong five times in chapter 3.12.

**Every count below is read off this table. Nothing recomputes it.** Three analysis
passes produced three wrong overlap figures — pass one carried 12 from a 25-file base,
pass two wrote 5 where 2 followed, and both were hand-arithmetic on quantities the table
already holds. So the table is the authority and every other document quotes it.

| | count | files |
|---|---|---|
| **3.15 only** | 13 | `channels.controller.ts`, `channels.itest.ts`, `channels.schema.ts`, `channels.service.ts`, `internal.itest.ts`, `fixtures.ts`, `gauntlet.itest.ts`, `targets.itest.ts`, `targets.ts`, `tenant-scope.itest.ts`, `isolation-fixtures.ts`, **`messages.controller.ts`**, **`messages.service.ts`** |
| **3.16 only** | 13 | `credentials.itest.ts`, `dev-token.controller.ts`, `users.controller.ts`, `users.service.ts`, `users.module.ts`, `users.schema.ts`, `users.itest.ts`, `app.module.ts`, `session.ts`, `0011_*.sql`, `sentinel.sql`, `guard.itest.ts`, `vitest.coverage.config.mts` |
| **both** | 7 | `repository.ts`, `repository.itest.ts`, `isolation.itest.ts`, `schema.ts`, `0012_*.sql`, `codes.ts`, `codes.test.ts` |
| **neither** | 3 | `compare.ts` (read by T043, not changed), `exempt.ts` and `eslint.config.mjs` (touched only if T011 finds a file needing an entry) |

    union            36 files
    taught           33
    3.15 teaches     13 + 7 = 20
    3.16 teaches     13 + 7 = 20
    instances        40   = 33 taught + 7 counted twice   ✓

**36, from 34, from 29, from 25.** Four revisions, each found by a different question:
the task list (29), the chapter assignment (34), and the send call graph (36) —
`messages.controller.ts` and `messages.service.ts` arrived in analysis pass seven with
T031a, because the public send had to be made to say who is acting before a membership
check could fire on it. Every revision has come from asking a new question rather than
rereading, which is the argument for the enumeration existing at all.

The seven shared files are fenced **whole in 3.15 and diffed in 3.16**, 3.15 coming
first. `schema.ts` and `0012` straddle because each carries columns from both chapters:
`members.role` is 3.15's subject and `users.deleted_at` is 3.16's, in one migration. The
alternative is regrouping the migrations by chapter — 0011 for the role column, 0012 for
activity, read positions and the deletion marker — which costs nothing except that Phase
2 runs both before either chapter is written. Not taken; the straddle costs one diff.

`sentinel.sql` and `guard.itest.ts` belong to **3.16**, because `read_positions` is its
subject. Both are amended by `fences/post-series.md`, which the checker applies after
every chapter, so the chapter excerpts and the appendix amends — a chapter is upstream of
its own amendment.

### What the enumeration does to the word estimate

At chapter 3.11's measured 160 words per file — 1.5 fences per file, 107 words per fence:

    3.15    20 files  ≈ 3,200 words
    3.16    20 files  ≈ 3,200 words

Both inside 2,000–4,000 with 800 words of headroom, and seven of 3.16's twenty are diffs
of files 3.15 already fenced, which run shorter than a whole file. **Three chapters would
be 40 ÷ 3 × 160 ≈ 2,133 each**, which clears the floor by 133 words — still the wrong side
of comfortable against an estimate that has run low three times, and the reason two
chapters holds is now subject coherence with the arithmetic no longer arguing either way.

So the two-chapter split is supported by arithmetic again, and by better arithmetic than
R12's: a real per-file assignment rather than a group sum scaled by a ratio. Analysis
pass one had reported the floor argument gone, on a scaled estimate of ~2,290 a page for
three chapters; the scaling was the wrong instrument and the assignment is the right one.

### The diff-heavy worry is refuted by measurement

The pass suggested that because **23 of the 29 files are already fenced in earlier
chapters** — `repository.ts` in twelve of them, `schema.ts` in ten, `session.ts` in
seven, `codes.ts` in five — most fences here are diffs, and that a diff-heavy chapter
should run lighter in prose than R12's 107 words per fence.

Measured over the four most recent chapters:

    chapter   titled fences   diffs   diff share   prose words   words/fence
    3.11             31         22        71%          3,316         107
    3.12             37          7        19%          3,440          93
    3.13             25          6        24%          2,452          98
    3.14             31         13        42%          2,228          72

**The opposite of the prediction.** 3.11 has the highest diff share of the four and the
highest words per fence; 3.14 has more diffs than 3.12 or 3.13 and the lowest. Words per
fence does not track diff share at all — and R12's base chapter was already 71% diffs,
so "these chapters will be diff-heavy" is not new information about the estimate.

Recorded because a plausible worry with a cheap measurement behind it should not survive
to a second analysis pass, and this one would have.

### What the corrected count does to the decision

Superseded by the assignment above, and recorded rather than deleted because the wrong
instrument is worth naming.

Analysis pass one scaled R12's 37 file-instances by 29/25 to get ~43, divided by three,
and reported that three chapters now fits inside the band at ~2,290 words a page — so
the floor argument that killed three was gone. **The scaling was the error.** Instances
do not grow with the union; they grow with how many chapters teach each file, which is a
question the enumeration answers directly. The real count is 38 instances, giving ~2,027
a page for three chapters — still against the floor, by 27 words.

Two chapters holds on all three grounds now: arithmetic, subject coherence, and headroom
against an estimate that has run low three times (3.5 by 77%, 3.12 by 65%, this feature's
own first count by 26%).

# Research — the revision watermark

Five questions, each answered by running a command or reading the clause rather than by
judgement. Two answers changed the design and one found a gap in the specification.

---

## R1 — How do the counts reach the gateway without a per-handshake query? (FR-014)

**Decision: they ride `internalSessionResponseSchema`, the call the gateway already makes at
connect.**

**Rationale.** `/internal/session` already answers `channel_ids` for the connecting user, and
the route has taken exactly this kind of passenger twice before. `banned` rides it, and its
comment states the rule:

> IT RIDES THIS RESPONSE FOR THE REASON THE LIMITS DO: the gateway has no database and must not
> gain one, `banned_at` is a column in Postgres, and the api is the only service that reads
> Postgres. So the ban travels on the one call the gateway already makes at connect — no new
> table reaches the gateway and no new round trip is added.

The counts are a column in Postgres and the gateway must not read Postgres. Same seat, third
passenger. **FR-014 is met by an existing route, not by optimising a new one**, and the api
resolves the counts in the statement that already resolves the memberships.

**Alternatives considered.** A second internal call at handshake — rejected: it is the round
trip FR-014 exists to forbid, and at 10,000 connections it is 10,000 extra calls. A count
fetched lazily when a client asks — rejected: the client cannot know to ask, which is the
defect.

**And the shape is a map, not a widened array.** `channel_ids: string[]` stays as it is;
`channel_revisions` is a parallel `Record<channel_id, count>`. Widening the array into objects
would change a field eleven chapters publish, for no gain.

---

## R2 — Can the resume cursor carry the count as a third field?

**Decision: no — and in the end the client presents no count at all.**

**Rationale.** `resume.ts:60-63` splits each cursor on the LAST colon, and says why:

> rsplit: channel ids are opaque to the gateway and a colon inside one must not silently
> truncate it.

A `<channel_id>:<seq>:<rev>` entry would rsplit into channel `"<channel_id>:<seq>"` and sequence
`rev`. **Every resume would silently resume from the wrong place** — the worst kind of failure,
because it produces plausible numbers rather than an error.

**THIS ANSWER WAS REVISED AFTER IT WAS BUILT.** The original read: *"So counts ride
`?rev=<channel_id>:<count>`, repeated, parsed by the same rsplit."* That was implemented —
`parseRevisions` was written — and then removed, because the question above is the wrong one.
The cursor cannot carry the count, but neither can anything else the client sends, for a reason
that has nothing to do with parsing: **the ack already carries every count, so a client can
compare against its own without telling the platform anything.**

Once the client compares, the parameter buys nothing and costs a contract clause. A parameter
the server parses and never acts on can never be removed, and one the server DOES act on hands
the client a number the platform will make decisions with — which is how a fabricated count
becomes a denial of service the client controls.

**So the cursor format is untouched and the upgrade URL gains nothing.** The rsplit rule stays
intact by not being tested rather than by being extended, which is the stronger outcome: there is
no second parser to keep in agreement with the first.

**Alternatives considered.** Changing the cursor format to a JSON blob — rejected: it breaks
every existing client for a field they do not use. A first-colon split — rejected: it is the
bug the current comment exists to prevent.

---

## R3 — What does a client that presents a cursor but no counts get told?

**Decision: report the counts, signal no repair. And this is a gap in the specification, not a
reading of it.**

**Rationale.** FR-007 covers "no count" as a **first connection** — nothing held, nothing
stale, no repair. It does not cover a client that presents a **cursor** and no counts, which is
every existing client during the deploy window and for as long after as a client goes
un-upgraded.

Reading FR-007's "treated as presenting zero" literally would tell that client that every
channel with any revision ever needs repair. For a busy channel that is every channel, on every
reconnect, for every un-upgraded client — the thundering herd US2 exists to prevent, arriving
during a deploy, which is when the platform is already at its most loaded.

So the two cases are distinguished:

    cursor absent, rev absent    a first connection      no repair signalled   (FR-007)
    cursor present, rev absent   a pre-upgrade client    no repair signalled
    cursor present, rev present  an upgraded client      compare per channel   (FR-006)

**An upgraded client's first reconnect establishes its baseline** — it receives counts, stores
them, and the reconnect after that can compare. One reconnect of latency before the signal
works, and no herd.

**This needs FR-007 amended rather than interpreted.** A requirement that has to be read
generously is one the next person reads differently. Recorded here and carried into the task
list as a specification change, not a design note.

---

## R4 — Can the ack reuse `cursorSchema` for the counts?

**Decision: no. A new record type that admits zero.**

**Rationale.** `cursorSchema` is `z.record(z.string(), z.number().int().positive())`.
`.positive()` excludes zero, and **every channel that has never been revised has a count of
zero**. Reusing it would make an unrevised channel unrepresentable — the api would have to omit
it, and the gateway could not tell "no revisions" from "not reported", which is precisely the
distinction FR-007 and R3 turn on.

A sibling `revisionCountSchema` with `.nonnegative()`, beside `cursorSchema` in `frames.ts`.

**Alternatives considered.** Omitting zero-count channels and treating absence as zero —
rejected for the reason above: it collapses two states the feature needs apart. Starting counts
at 1 so `.positive()` fits — rejected: it makes the number mean "revisions plus one", which is
the kind of off-by-one nobody remembers in a year.

---

## R5 — Where does the counter rise, and what does it cost?

**Decision: `channels.revision_sequence`, a `bigint not null default 0`, raised by one UPDATE
inside each of the two transactions that already exist.**

**Rationale.** Both revision paths are already transactions and both already write to
`messages`:

    editMessage    tx.update(messages).set({ text, editedAt })      + messageEdits insert
    deleteMessage  tx.update(messages).set({ deletedAt, … })

Neither touches `channels`. The send path does, and its comment records what that buys:

> ONE STATEMENT AND NO NEW TRANSACTION. The write path already updates this row here, so the
> column costs an extra assignment rather than an extra round trip.

**Here it is an extra round trip**, one per revision, inside a transaction that exists. That is
the right side of the trade: revisions are rare and reconnects are not, and the alternative
puts the cost on the read.

`bigint` and not `integer`, matching `channels.last_sequence`. `not null default 0` so every
existing channel starts at zero, which the spec's Assumptions record as deliberate — a count
reconstructed from history would tell every client to repair every channel once.

**Alternatives considered.** Deriving the count from `MAX(messages.edited_at)` — rejected: zero
writes, but it needs an index on `(channel_id, edited_at)` and puts a scan on the handshake,
which FR-014 forbids. A timestamp instead of a counter — rejected by FR-010: a clock the client
and platform disagree about produces wrong repairs in both directions, and a counter answers
"how many" for free.

**The migration is `0015`, hand-written.** Feature 043 retired `drizzle-kit` and
`migrations.test.ts` fails if the generator, its config or its snapshots return.

---

## What this research did not settle

**Which changed files are fenced.** Feature 043 measured thirteen files published only as
`(excerpt)`, including `session.itest.ts` — edits to those are invisible to `check:fences` and
carry no amendment hunk, while `repository.ts` is fenced by 23 chapters and `internal.ts` by 11.
The task list resolves this per file by running the checker, because the answer is not
derivable from the path.

**What the battery will find.** Feature 043 estimated 17 files and changed 58, and every
unplanned one came from running something rather than reading it. This plan's twelve is the
same kind of estimate.

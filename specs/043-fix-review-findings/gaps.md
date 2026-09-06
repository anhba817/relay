# Feature 043 — gaps

**Twenty-four items: twenty-three carried and one new.** Chapter 3.24's five, the seventeen
numbered before them, the one that has never been numbered, and one this feature's own
analysis found.

**The arithmetic matters here.** Chapter 3.24's ledger carried "five items and the seventeen
before them", and that phrasing excluded the unnumbered one by counting rather than by
deciding — which is how an item with no owner disappears without anybody closing it. It is
below, with the same title its predecessor gave it.

**Every carried item was re-measured against the tree, not copied.** Three of chapter 3.24's
were wrong on the day they were written, so the numbers below come from commands run during
this close-out. Where a number moved, both are shown.

    closed by this feature            9
    closed earlier, still closed      2
    closed on re-measurement          3     none of them on purpose
    open                             10
                                     --
                                     24

**Three closed because somebody measured them, not because anybody worked on them.** The
port-collision item, the discarded-output item, and the appendix's inability to retire a file
were all resolved as side effects — which is an argument for re-measuring a carried ledger
rather than copying it forward, and the reason this one was.

---

## CLOSED BY THIS FEATURE — NINE

### 3.24-1. `avatar_url` accepts `javascript:` — **CLOSED**

`users.schema.ts` now parses with `new URL` and checks `AVATAR_URL_SCHEMES`, on both the
PATCH and the bulk upsert, from one fragment.

Re-measured on zod 4.4.3, 2026-09-06: `z.string().url()` still accepts `javascript:`,
`data:`, `file:`, `vbscript:` and `ftp:`. The validator has not changed; the field's rule has.

Stored rows the new rule would reject: **0** of 443,263 (442,589 null, 670 https, 4 http).
The four `http` rows are why the rule is a list of two schemes rather than `https` alone.

### 3.24-2. The socket door's `text` carries no bound at all — **CLOSED**

`MESSAGE_TEXT_MAX` in `frames.ts`, imported by four doors: the socket send frame, the
internal hop, the REST send body and the edit body. Grep for a length literal outside the
definition returns nothing.

**Not applied to `messageSchema`**, which is the outbound message read off stored rows. A
test asserts it stays unbounded, because the task for this item named that schema by line
number and bounding it would be chapter 3.24's `outboxEventSchema` defect repeated.

### 3.24-3. Five bare 422s answer `internal_error` — **CLOSED**

All five now `protocolError(code, message, 422, field?)`. **Six codes, not five** — validating
the event-type set created a refusal that did not exist to be counted, and
`codes.test.ts`'s exact-count assertion moved 21 → 27 deliberately.

Reverting one reproduces the finding: `expected 'internal_error' to be 'webhook_url_insecure'`.

### 3.24-4. The e2e harness releases its ports on a timer — **CLOSED, AND IT WAS NINE HARNESSES**

`stop()` awaits every child's `exit` with a SIGKILL fallback. But the item named one harness
and there were **nine hand-allocated port bands across eight more files**, two of them
containing a service the lane itself runs: `membership.itest.ts` drew 5400-5599, which holds
Postgres's 5432, and `limits.itest.ts` drew 4100-4299, which holds NATS's 4222.

All nine retired. Every child spawns with `PORT=0` and reports the port the OS gave it.

**This closes chapter 3.24's eleventh red, which its own record calls unexplainable** —
`limits.itest.ts` reporting "api never became healthy" with the child's `EADDRINUSE` written
to a pipe nobody read. 4222 is in its band.

### 3.24-5. The integration lane accumulates state until it cannot pass — **CLOSED**

`scripts/reset-lane.mjs`, guarded by `--yes-this-is-my-test-lane`, purges every stream,
deletes every durable, and removes webhook deliveries left pending by runs that ended. The
seeded demo tenant survives, because the constitution names `docker compose up` by title.

Twenty-run battery from a cleared lane: **zero durable consumers outlived any run**.

### 3.23-1. A customer can subscribe to an event type that does not exist — **CLOSED, REMEDY RE-POINTED**

Validated against FR-WHK-02's **declared eight**, not the emitted five. The item's own
recommended fix — one `includes` against `OUTBOX_EVENT_TYPES` — would have refused **838**
stored subscriptions naming `channel.created`, which is declared and unbuilt.

The item predicted this without identifying the cause: *"it goes red for any customer already
storing a bad value"*. The values were not bad. Annotated in place in both predecessors'
ledgers.

### 3.23-6. drizzle-kit's snapshot is behind the directory — **CLOSED BY RETIREMENT**

Re-measured at deletion: **15 SQL files against 8 snapshots, seven behind.** Chapter 3.23
recorded six and chapter 3.24 seven, so the number moved again exactly as its predecessors
predicted.

Not fixed by regenerating. ADR-16 has said since chapter 3.9 that migrations are
*"versioned, forward-only, hand-reviewed SQL"*, which a generator's output is not — so the
tooling had contradicted the constitution the whole time. `migrations/meta/`,
`drizzle.config.ts` and `drizzle-kit` are gone, held down by `migrations.test.ts`, tested red
four ways.

### 3.23-8. EIR-WS-06 is met by two close codes of six — **CLOSED**

All six documented in a close-code table with cause and remedy, including **4009, which is
declared and never emitted** — the table says so rather than describing behaviour the
platform does not have.

`check-error-codes.mjs` now compares `CLOSE_CODES` with the reference in both directions.
Tested red three ways: text removed, code renamed, code added with no text. The rename fires
both directions at once.

### 3.23-9. A `.test.ts` in the docker-free lane needs a running Redis — **CLOSED**

Split per assertion rather than moved or stubbed: **6 tests stay container-free, 34 moved to
`connections.itest.ts`**. Verified with every container stopped — the whole unit lane runs
**512 tests across 56 files, exit 0**.

---

## CLOSED EARLIER, AND STILL CLOSED — TWO

### 3.23-3. A concurrent edit and deletion is not tested — **CLOSED, AND THE CLAIM IT RESTED ON WAS FALSE**

Chapter 3.23's ledger said both orderings already end in a tombstone. Forced races disproved
it: **3 of 5 runs left four rows with `deleted_at` set and `text` present**. Closed with a
compare-and-set on `deleted_at` in the edit path, then 5 runs × 50 races with no incoherent
row.

### 3.23-5. A closed chapter's two records disagree — **CLOSED, and the convention held.**

Used twice more this feature, to annotate a factual error in a closed ledger without
rewriting the original claim.

---

## CARRIED FROM 3.22 AND 3.23 — ELEVEN, AND THREE OF THEM CLOSED ON RE-MEASUREMENT

### 3.23-2. FR-MOD-03's audit log — **OPEN, unchanged, untouched here.**

Chapter 4.7's, and named out of scope in this feature's assumptions.

### 3.23-4. One authorization fact lives in two places — **OPEN, unchanged.**

`eslint.config.mjs`'s `DRIVER_EXEMPT_TESTS` and the harness's own list still agree by
somebody remembering. This feature added no exemption, so it did not widen the item — but it
is the same shape as the two-lists defect it closed in `WEBHOOK_EVENT_TYPES`, and that fix is
the template if anyone wants it.

### 3.23-7. The tenancy catalogue's reach was fixed; the guard's coverage was not — **OPEN, unchanged.**

### 3.22-2 (`C2`). The port collision a test could not see — **CLOSED, and it was worse than recorded.**

Promoted out of the open list. A test can see it now: `harness.itest.ts` boots, stops, and
probes the first system's port, which fails under a timed teardown and cannot fail under one
that awaits `exit`. And the class the item described turned out to have **nine instances, not
one** — see 3.24-4.

### 3.22-3 (`C3`). An excerpt-only file is never verified — **OPEN, AND THE COUNT IS THIRTEEN.**

Chapter 3.22 recorded two, chapter 3.24 corrected it to TEN, and the measured count today is
**13** path-shaped files that appear only as `(excerpt)` and never with a full chain:

    docs/04-srs.md                              services/api/src/messages/idempotency.itest.ts
    docs/05-sad.md                              services/api/src/notifications/mailer.test.ts
    packages/test-harness/src/guard.itest.ts    services/api/src/quotas/quotas.itest.ts
    packages/test-harness/src/sentinel.sql      services/gateway/src/limits.itest.ts
    packages/test-harness/src/sentinel.ts       services/gateway/src/session.itest.ts
    services/api/src/fanout/fanout.itest.ts     specs/036-chapter-3-18/baseline.txt
    services/api/src/internal/usage.itest.ts

**This feature edited three of them** — `limits.itest.ts`, `session.itest.ts` and
`guard.itest.ts` — and no gate could see any of those edits. `check:fences` never listed
them, which is how the port-map rewrite in `limits.itest.ts` shipped with no amendment hunk
and no complaint.

### 3.22-4 (`C4`). `main.test.ts` checks that a module is CLOSED, not PASSED — **OPEN, unchanged.**

### 3.22-5 (`C5`). The retry-log bound is a five-module decision — **OPEN, unchanged, untouched here.**

### 3.22-6 (`C6`). Files that discard their child's output — **CLOSED. The count is ZERO.**

Chapter 3.22 counted nine, chapter 3.24 re-measured eleven. Measured today: **no file in
`packages/` or `services/` passes `stdio: "ignore"` to a spawn.** The two remaining matches
are both in comments explaining why the practice was abandoned.

Closed as a side effect rather than as a goal: retiring the port bands required reading each
child's `listening` line, and a child whose output is discarded cannot report one. **The
diagnostic value was the argument for years and the mechanical need is what actually did it.**

### 3.22-7 (`C7`). Coverage cannot see an omission — **OPEN in the same partial way.**

And re-confirmed by this feature's own experience: v8 records a `&&` operand as covered when
it was *evaluated*, not when it went both ways.

### 3.22-8 (`C8`). The per-chapter instruments have no owner — **OPEN for the SEVENTH feature.**

Six Python instruments in this directory, carried from a predecessor and edited again here:
`check-refs.py` gained the success-criteria ordering rule. Every one of them will be copied
into the next feature's directory and drift there, exactly as this copy's three stale fields
did.

**And this feature demonstrated the cost three times in one session.** `sweep.py` caught
the checklist carrying a task count six behind the list; `check-refs.py` caught the checklist
citing task ids that belong only in `tasks.md`; and both then caught the same two faults in
THIS FILE, one paragraph after it was written. Every one was a defect in a document this
feature wrote, caught by instruments this feature inherited and will abandon.

### 3.24 CARRIED: `check-fence-chain.mjs` could amend a published file but never retire one — **CLOSED**

Found by the task that retired the migration generator: its `drizzle.config.ts` deletion
was answered with "must be a diff" — true of an amendment and not of a deletion. `replay` has understood `(deleted)` since
chapter 3.2; the appendix loop never did. Since Part 3 closed, the appendix is the only place
a change can land, so the gap made retirement impossible. Tested red both ways.

---

## NEW — ONE

### 043-1. AN UNTITLED FENCE IS NEVER COMPARED TO ANYTHING — **NEW, OPEN**

`check-fence-chain.mjs:77` collects a fence only when it matches
`/^```(\w+) title="([^"]+)"\s*$/`. A fence with no `title=` is skipped silently, so its
content is never replayed and never compared with the repository.

Measured across the 41 English chapter pages:

    titled fences      758
    untitled fences    146     16% of every opening code fence
                       ---
    total              904

**This is one step further out than 3.22-3.** An excerpt-only file is skipped *by* its title,
which is a decision somebody made and wrote down. An untitled fence is skipped because the
pattern does not match it, which nobody decided and nothing reports.

This feature repaired one of the 146 — the `tuan` transcript in chapter 2.8, still showing
ports 4100-4102 after the lane made them ephemeral — and it was found because an analysis
pass happened to grep for a port number, not because any instrument pointed at it.

**The class needs an owner.** The cheap version is a report rather than a gate: count them,
list them, and let a chapter decide which deserve titles.

---

## THE ONE THAT IS NOT NUMBERED, BECAUSE TWELVE CHAPTERS HAVE NUMBERED IT

**USE A PERSON.** Chapters 3.14 through 3.24 each named this gap and none closed it. This
feature is the twelfth, and it did not close it either.

`specs/036-chapter-3-18/reader-protocol.md` describes the whole thing: 45 minutes, six
questions, one person who has not read the work.

Every check in these three repositories compares bytes. Six Python instruments, five
`check:*` scripts, and a compile-time assertion added this week — and not one of them can
answer whether a paragraph is understandable to somebody who does not already know the
answer. Each of them says so in its own last line, which is the honest version of the same
admission:

    check-refs: ids only — this says nothing about whether the prose around them is true
    sweep: this says nothing about whether the prose is TRUE
    check-checklist: presence only — it cannot tell whether a ticked box is true
    check-quickstart: names only — it cannot tell whether a scenario's expectation is true

**An instrument that is easy to run tells you what it measures, not what you wanted to know.**

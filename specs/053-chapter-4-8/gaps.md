# Gaps — feature 053, chapter 4.8, "the log a customer can search"

**Every carried item is re-measured rather than copied.** Four of 043's twenty-three were wrong
when re-measured and three closed with nobody working on them; 052's own re-measurement of
048-2 recorded *"0 occurrences under `services/`"* and this feature found **3**. Measure the
ledger.

---

## 053-1 — THE CLAMP THIS SERIES PUBLISHED FOR TWO PARTS, AND THE CODE HAS NEVER DONE IT

**CLOSED IN THIS FEATURE, and recorded because of how it was found.** Chapter 2.4 published,
in prose and in a code comment inside its `diff` fence, that `limit` *"CLAMPS rather than
rejects — a client asking for 500 gets 200 and a next_cursor"*. `.max(200)` on a zod number is
a validation, not a transform. Measured:

    {}                OK   {direction:"older", limit:50}
    {limit:"500"}     REFUSED  too_big
    {limit:"0"}       REFUSED  too_small
    {limt:"200"}      REFUSED  unrecognized_keys

Nothing in the tree asserted either behaviour, so the refusal has been unpinned and
undocumented since 2.4. **Found by executing a task that said "mirror `historyQuerySchema`'s
form and bounds"** — the mirror was of the code, and the code disagreed with its own comment.

The repair touched **five chapters in two locales plus the platform**: 2.4 adds the comment and
3.11, 3.17 and 3.18 carry it as `diff` CONTEXT, so changing the tree alone unanchors six hunks.
Two of the four carried only the comment's first two lines, because a `-U6` window ended
mid-comment — so a block replacement caught four occurrences and missed four, and the fix had
to go line by line. `check:fences` 110 before and 110 after.

The words were fixed rather than the code: the refusal is what customers' clients have been
written against for two parts, and this chapter's own surface refuses `limit` for a stated
reason. **The Vietnamese paragraph was rewritten by this feature and its wording is not a
translator's** — worth a pass by someone who writes the language.

---

## 053-2 — THE SEALED SUITE HAD NEVER PASSED, AND NOTHING COULD HAVE SAID SO

**CLOSED IN THIS FEATURE.** `packages/outsider/src/integrate.itest.ts` asserted that `docs_url`
contains `/not_found` — a path per code — under a comment ending *"Asserted as this platform
actually answers."* `docsUrl` returns `${base}#${code}`, and `git merge-base --is-ancestor`
puts the commit that made it an anchor **before** the commit that wrote the suite. Both on
2026-09-10.

So the suite has been red since it was written, and nothing reported it, because **it needs a
running platform that no lane starts**: `compose --profile services`, a built image, a migrated
database and a seeded tenant. Chapter 4.8 stood that up to run its own new tests in the file
and met the failure on the way past. 18 of 18 green afterwards, the first time.

**The general form is still open (see 053-3).** A suite that only runs in CI's third job, and
whose failure nobody sees locally, is one deploy away from being red for a month.

---

## 053-3 — NO LOCAL COMMAND RUNS THE SEALED SUITE, AND `pnpm test:integration` DOES NOT REACH IT

**OPEN.** `packages/outsider` has a `test:integration` script and `pnpm test:integration` stops
before it: turbo plans 18 tasks, attempts **10**, and prints `Tasks: 8 successful, 10 total`
(051-3, re-measured — the numbers were 7 of 9 at 4.7). Running the suite takes six commands and
about four minutes of image building, which is why nobody does it.

What would close it: a `pnpm test:sealed` that brings the stack up, seeds, runs and tears down,
so the cost is one command rather than six remembered ones.

---

## 053-4 — `check-lane-scope.py` HAD STILL NEVER LOOKED, AND 049 MEASURED THE FIX WITHOUT LANDING IT

**CLOSED IN THIS FEATURE.** Line 28 read `/home/dong/work/relay/tmp/part3-refactor` — the
worktree feature 045 deleted — so the glob matched nothing and the script exited 0 with all ten
of its own controls firing:

    before   controls: 10 of 10 fired ·  0 integration files, 0 unscoped read(s)
    after    controls: 10 of 10 fired · 55 integration files, 0 unscoped read(s)

049-3 recorded the retarget as done — *"Retargeted: 50 files, 0 unscoped reads"* — and the
retarget was a command somebody ran, not an edit anybody committed. **A measurement is not a
repair**, and this is the second time in this feature that a re-measurement caught a carried
item's own wording (see 048-2 below).

Retargeted off the file's own location, and given 045-81's rule: a run that reads no files now
**refuses with exit 2**. Both halves checked — exit 2 on a dead path, exit 0 on the real tree.

---

## 053-5 — THE JOURNEY MAP ASKS A QUESTION THIS LOG CANNOT ANSWER

**OPEN, AND NOT THIS CHAPTER'S TO BUILD.** `docs/03-journey-map.md`'s Stage 8 — Operate lists
the pain point as *"no way to trace a specific user's reported problem"* and the opportunity as
*"per-user and per-channel message tracing for support investigations."*

`api_requests` carries no user and no channel. The producer stores `principal_kind` —
`application`, `user`, `platform`, `none` — which says what KIND of caller made the request and
never which one. So the surface answers *"what did this tenant call and what happened"* and the
journey asks *"what happened to this user"*.

FR-ANL-07's six fields never asked for the second, so **no clause is broken**: a motivating
document names a capability no requirement carried. Closing it costs a column on
`api_requests`, a change to chapter 4.4's `event.ts`, a migration, and the tenancy question 4.4
settled by recording a kind instead of an identity.

---

## 053-6 — EIR-API-06's `has_more` EXISTS ON ONE LIST ENDPOINT OUT OF TWO

**OPEN.** *"List endpoints shall use opaque cursor pagination with `limit` and `cursor`
parameters, returning `next_cursor` and `has_more`."* `grep has_more` over `services/` and
`packages/` returned **nothing** before this chapter; `messages.service.ts` has been
non-conforming since chapter 2.4 and still is.

Not fixed here: that file carries six titled fences in each locale, and adding a field to a
response shape is a change to a published chapter's output rather than to a comment. **Adding a
field is not breaking under CON-05**, so the clause is satisfiable without a version bump
whenever a chapter touches that service.

---

## 053-7 — EIR-API-07 HAS NO IMPLEMENTATION, AND THIS CHAPTER GREW ITS SURFACE

**OPEN.** *"An OpenAPI 3.1 specification shall be published, machine-readable and complete for
every public endpoint"* (P4). There is no specification anywhere in the tree and no generator.
This chapter adds `GET /v1/request-log` to the set it would have to cover. Recorded rather than
claimed, because a P4 clause with no implementation and no chapter is the shape that becomes a
surprise at a launch review.

---

## 053-8 — THE `/internal/*` DECISION SERVES FR-ANL-07 LESS WELL THAN FR-ANL-01

**RECORDED, NOT A DEFECT.** The surface returns the platform's internal calls, so FR-ANL-01's
*"every request"* is served exactly. FR-ANL-07's *"per tenant"* is served less well than it
could be: **1,676 of a tenant's 4,762 attributed rows are calls their software did not make**,
`/internal/session` being the busiest single route in the log. A customer's first page is a
route they have never heard of.

One of the two had to give. What makes this the right way round is that it is reversible by the
caller and not by the platform: the `endpoint` filter excludes them, and a platform that hid
them offers no way back.

---

## 048-2 — `message_events.delivery_latency_ms` HAS NO PRODUCER — **UNCHANGED, AND THE ITEM'S OWN WORDING WAS WRONG**

**OPEN, SIXTH FEATURE.** Re-measured from the server: `message_events` holds **0 rows** and **0
rows carrying a latency**.

**4.7's re-measurement said "0 occurrences under `services/`" and it is 3.** All three are in
`services/ingester/src/metering.itest.ts` — a comment saying the table has no producer, a
cleanup `DELETE`, and a test's own `INSERT`. The item holds and its wording did not: *"0
producers"* is what was always meant, and *"0 occurrences"* is checkable and false.

**AND THE ONE THING THAT WRITES THE TABLE WRITES NULL INTO THAT COLUMN ON PURPOSE.**
`scripts/scale/load-analytics.mjs` names the column in its list and supplies `CAST(NULL AS
Nullable(UInt32))` in both halves of its `UNION ALL`. That is stronger than an absence: the
loader had the chance and declined.

What changed this feature: **FR-ANL-10 now names the quantity** (commit to the frame written to
a subscriber's socket) and records the two readings not chosen. The producer is still absent,
and building it means carrying both instants across a service boundary — the commit is the
api's and the socket write is the gateway's — on the busiest path in the platform.

---

## 050-8 — 4.4's INTEGRATION SUITE NEEDS A PROCESS NO GATE STARTS — **UNCHANGED, AND IT COST THIS FEATURE A TEST**

**OPEN.** `request-log.itest.ts` is 5 of 5 red in every run of this feature, for the reason it
has been since 4.4: it polls for a row only an ingester can write and `compose.yaml` runs none.

**This feature paid for it twice more.** The cross-tenant gauntlet's attack on the new route has
to plant its own rows, because both tenants' logs are empty on a fresh lane and an empty log
passes a leak check for the same reason an empty page does. And the sealed suite asserts the log
comes back **empty** in front of a customer — which is the honest assertion and not a skip.

Measured once with an ingester running (T040b): the log is **1.60 s behind at p50**, 2.7% of
FR-ANL-04's 60 seconds. Starting one drained 188 rows over 15 batches, the first alone writing a
137-row backlog off the stream.

---

## 051-3 — `pnpm test:integration` RUNS A SUBSET — **UNCHANGED, AND THE NUMBER MOVED**

**OPEN.** `turbo run … --concurrency=1` stops scheduling at the first failure. Measured here:
plans 18 tasks, attempts **10**, prints `Tasks: 8 successful, 10 total`. At 4.7 it was 7 of 9.
Provisioning CI's ClickHouse (T001b) does not touch this; the lanes ordered after the api are
still not executed by that command, in CI exactly as locally.

---

## 052-2 — `services/ingester/src/shape.ts` IS PINNED AT 100 AND MEASURES 95.12 — **UNCHANGED**

**OPEN.** `pnpm coverage` reports it every run, which is what 4.7's `reportOnFailure` bought.
Left at 100 rather than lowered, for 4.7's reason: the chapter made it visible rather than
measuring it down.

---

## 052-3 — A CLEANUP ENUMERATES TABLES BY HAND — **UNCHANGED, AND THIS FEATURE DID NOT TOUCH IT**

**OPEN.** `services/ingester/src/ingest.itest.ts` issues per-table `DELETE`s naming
`webhook_attempts`, `api_requests` and `connection_events` at five call sites. This feature's
suites clean up their own environments and do not share that helper, so the item gets its second
reading unchanged: a hand-maintained list of tables in a cleanup is a list that goes stale the
next time a chapter adds one.

---

## 052-6 — CONSTITUTION III's AMENDMENT IS STILL OWED — **UNCHANGED, AND THIS CHAPTER IS INSIDE THE CLAUSE RATHER THAN BESIDE IT**

**OPEN, AND NOT THIS FEATURE'S TO CLOSE.** 4.7's conflict was an auditor reading both stores.
This chapter is constitution III's **central case**: *"dashboard analytics read only from the
analytical store"* is what a customer-facing request log is, and nothing here reopens the
auditor question. The amendment is still the constitution's own, under VII's *"resolved
explicitly by amendment rather than silent divergence"*.

---

## 052-7 — A FEATURE-LOCAL ID CITED AS A PUBLISHED CLAUSE — **RECURRED IN THIS FEATURE, BY ME**

**OPEN AS A CLASS.** Two paragraphs of this chapter's ADR-26 were drafted citing `FR-025`, and
one cited `FR-007` — feature-local ids, in published documents, three commits after this feature
read 1.14's correction of `FR-003a` for the same reason.

**The mechanism was copying the task line.** A task is a feature-local document and uses the
local id correctly; a published document is not. Caught by diffing `docs/` for `FR-0\d\d` added
by this feature, not by re-reading — and the check is cheap enough to be a gate. **Nothing runs
it.** `check-srs-ids.sh` checks the SRS's own rows for duplicates and does not look at what
other documents cite.

---

## 053-9 — IMMEDIACY AND A QUEUE CANNOT BOTH HOLD, AND THE GAP IS 30x RATHER THAN RHETORICAL

**OPEN, FILED FORWARD FOR THE NEXT CHAPTER THAT READS THIS STORE.** Constitution V says *"every
metered unit is visible in the dashboard the moment it is counted"*. Constitution III says
billing, metering and dashboard analytics *"read only from the analytical store … fed via a
durable queue"*. **FR-DSH-02 puts a number on the first** — *"API calls as they occur, with a
latency under 2 seconds"* — against **FR-ANL-04's 60**, and EIR-DSH-02 binds the dashboard to
this API, so the 2 seconds is a claim about the route this chapter built.

Measured here with an ingester running: **p50 1.60 s, max 1.61 s** — inside both. So the lane
does not show the contradiction, which makes this a question about production scale rather than
something anyone can see today, and that is the honest form of it. The clustering is the
ingester's two-second batch window; a deployment that widens the window to save inserts spends
FR-DSH-02's whole budget on the batch.

**Not this route's problem.** A request log is not a metered unit. It is filed forward because
this chapter is the first customer-facing read of the store and the usage dashboard is the next
one — so that chapter inherits a question rather than discovering one, the way 047-1 was filed
for movement IV.

---

## 050-2 — THE ANALYTICAL STORE HAS NO LANE GUARD — **UNCHANGED, AND THIS FEATURE LEANED ON THE CONVENTION AGAIN**

**OPEN.** Feature 030's sentinel trigger covers Postgres. ClickHouse has nothing: an unscoped
`DELETE` in any suite would take another suite's rows with it. Every statement in
`query.itest.ts` and `route.itest.ts` names its own environment id, and the dedup probe's
`finally` restores merges and deletes its own rows — all of it convention.

---

## 050-3 — THE VI CHAIN IS NEVER COMPARED TO THE TREE — **UNCHANGED, AND THIS FEATURE RELIED ON IT**

**OPEN.** `check-fence-chain.mjs:265` iterates `en.state` only. This feature edited four
Vietnamese chapters' fences (053-1) to keep them consistent with the English ones, and **no gate
would have reported it either way**. The consistency is a habit, not a check.

---

## 050-4 — ELEVEN HEAD PROBLEMS ARE FENCES WHOSE TITLE NAMES NO FILE — **UNCHANGED, AND USED AGAIN**

**OPEN.** Re-measured at this close: **36 HEAD problems, 25 `differs at line` and 11 `does not
exist in relay-platform`.** The eleven can never be repaired by editing the platform. The
headline 110 is eleven units pessimistic and 25 is the number a chapter should be measured
against.

---

## 048-3 — `vitest.coverage.config.mts` CANNOT TAKE A FENCE — **UNCHANGED, AND IT HID FOUR MORE EDITS**

**OPEN.** The file has diverged at line 29 since before Part 4, and a checker reports the first
failure per file. This feature added four per-file pins and lowered one; the chain's count did
not move for any of them.

---

## 048-5 — NO GATE CHECKS THAT A CHAPTER'S TAG MATCHES THE CHAPTER — **UNCHANGED**

**OPEN.** `README.md:8` promises it. `check-fence-chain` replays onto the working tree and
compares against `HEAD`; it never resolves a tag. 047 found three Part 1 tags on a superseded
lineage and the chain was green throughout.

# 062 — gaps

Started at phase 4, because T040 asks for an entry here rather than only in the chapter.
T077 completes it with the carried ledger **re-measured**, not copied.

---

## 062-1 — the metered level cannot fall for a deletion, so the reconciliation cannot fail in that direction

**New.** `StorageCause` has four members and `deleted` has no producer: chapter 4.15
established that no code path removes a `media_objects` row — the rejection path subtracts the
bytes and keeps the row on purpose (`0018`: *"a rejected object's row is all that survives
it"*) — and the reaper that will is `docs/12` row 22's, the erasure chapter.

So the failure mode a delta-summed level is most exposed to — a **lost `deleted` record**,
leaving the meter permanently over — cannot arise, because no such record is ever sent. A run
of green verdicts is evidence about the three causes that do exist and about nothing else.

Recorded in `services/api/src/metering/storage-reconcile.ts` and in
`services/api/src/metering/storage-event.ts`, which already carried the producer half of it.
**Closes when the erasure chapter ships a reaper**, at which point the signature this feature
wrote is the one it calls.

---

## 062-2 — DR-17's *"weekly"* has no runner, exactly as FR-ANL-06's *"daily"* has none

**Carried from 054-3 / ADR-28, re-measured.** Zero `schedule:` triggers in `ci.yml`, no cron,
no job runner of any kind in these three repositories. `scripts/reconcile-usage.mjs` has been
invokable and uninvoked since chapter 4.9; `scripts/reconcile-storage.mjs` joins it.

ADR-28's precedent is followed rather than re-argued: the absence is recorded, the exit code is
what *"raises an alert"* can currently mean, and the clause is marked unmet in the SRS (FR-011)
rather than left to look built. **Two weekly/daily jobs and no scheduler is a class now, not an
instance** — the next clause that names a cadence should expect the same answer.

---

## 062-3 — a probe that did not alter anything reported green, and prettier is why

**New, and it is 4.10's tamper probe at a different address.** T039's first arm — deleting the
uuid test inside `partitionByTenant` — ran **15 of 15 unit and 8 of 8 integration green**, which
I was one keystroke from recording as *"this arm is uncovered."*

The mutation had not been applied. `prettier` had wrapped that `if` across five lines when the
file was last formatted, so the single-line pattern the probe replaced matched nothing and the
script wrote the file back unchanged. Re-run with `assert old in s` and a `diff` against the
saved original, the same arm is **1 unit red and 1 integration red**.

**The rule this project already had**: *a probe that may not have altered anything has to assert
that it did* (4.10, 056). The new half is the mechanism — **a source file that a formatter owns
cannot be mutated by matching its text as you last wrote it**, and the cheap control is to diff
against the pre-mutation copy rather than to trust the replacement.

---

## 062-4 — three stores in one function, and constitution III's question is wider than 4.7 left it

**Carried from 051-2 / 052-6 / 054-3, widened.** `reconcile.ts` reads Postgres and ClickHouse;
`reconcileStorage` reads Postgres, ClickHouse **and the object store**, in one function, inside
the service that IS the operational path.

And the third side is not optional. The analytical store records a `reserved` event and no
`uploaded` event, so **nothing in it can tell an outstanding slot from a delivered object** —
measured, because 267 of the lane's 6,580 pending rows name a key the bucket holds. The term
that explains a gap has to come from the operational side, and which reservations are still
outstanding can only be answered by the inventory. Three sides, because the question has three.

The constitution III amendment written in full at 054 and not applied
(`specs/054-chapter-4-9/constitution-amendment.md`) now has a **fourth** item standing against
it.

---

## 062-5 — a column with one writer and no reader, three commits after it was added

**New, and it is 4.6's finding one movement later.** That chapter is called *"the rollup
nobody read"*: it found a rollup that had existed for two chapters, satisfied DR-10, and was
read by nothing — `grep` gave a comment and a file referenced by no script, service or config.

`uploads_by_kind` was in exactly that state at the start of phase 5. `grep` over all three
repositories gave `0017`, which declares it, and `0018`, which writes it. Nothing read it.
`storedBytes` was one step better — a reader with no test and no caller.

**CLOSED IN THIS FEATURE RATHER THAN RECORDED.** `uploadsByKind()` joins `storedBytes` and
`storedMessages` in `services/ingester/src/metering.ts`, and both have tests. The entry stays
because the *interval* is the finding: a clause that says the platform MUST count something
is not discharged by a column that holds the count, and three commits is how long it took
anyone to ask.

---

## 062-6 — the amended migration needs a manual step on any lane that applied the old one

**New, operational.** `0018_mv_billing_storage.sql` was amended in place after it had been
applied — `sumMap(map(kind, if(…)))` to `sumMapIf(…)` — because the migration is this
chapter's own and has shipped nowhere, and an `0019` that repairs `0018` publishes a mistake
as history (4.13's argument when it rewrote the MinIO image in all 25 commits).

`analytics/apply.mjs` keys its ledger on filename AND checksum and refuses a file that changed
after it was applied, which is the gate working. A developer holding such a lane needs two
commands before `node analytics/apply.mjs` will run:

    DROP TABLE IF EXISTS relay_analytics.mv_billing_storage
    ALTER TABLE relay_analytics.schema_applied DELETE WHERE filename = '0018_mv_billing_storage.sql'

**CI AND A FRESH CLONE NEVER MEET IT**, which is the same asymmetry 4.10's MinIO UID had and
the reason it is written down rather than assumed harmless. `quickstart.md` carries it.

**AND THE OLD VIEW'S ROWS ARE STILL IN THE ROLLUP** on any such lane, carrying zero-valued
keys a merge will never remove. Harmless to the level and to every count that reads a value;
misleading only to a reader that treats the key set as the list of kinds uploaded — which is
the defect the amendment was for.

---

## 062-7 — coverage cannot see a service its own suite runs in a child process

**New, and it is the sharpest instrument finding of the feature.** `shapeMediaStored`,
`route()`'s fourth arm and `insertMediaEvents` are executed on **every** run of
`services/api/src/media/storage-metering.itest.ts`, which drives the whole path end to end.
`pnpm coverage` reported them at 78.57%, 81.37% and 83.78% against pins of 100 and 84.

Both readings are true. That suite **spawns the ingester as a child process**, because the
ingester is not a compose service (4.9 — it has no Dockerfile), so none of the code under
test is instrumented. *A green lane is a claim about what was re-run* (050); **a coverage
number is a claim about what ran in this process.**

**CLOSED BY A SUITE, NOT BY A PIN.** `ingest.itest.ts` now drains `media.stored` records in
process against the same real broker and store. The entry stays because the class is open:
**050-8 is the same shape** (*"two test files starting a process is not a deployment"*), and
any future code whose only exercise is through that child process will measure as dead.

---

## 062-8 — the gauntlet reports nothing about a reconciliation, and cannot

**Carried from 4.12, third occurrence, and this time it is structural rather than a defect.**
Eleven scope arms deleted one at a time; `isolation/gauntlet.itest.ts` answered **61 of 61
green for every one of them.**

Constitution VI names that suite as gating releases, and it is an attack surface over HTTP
routes. A reconciliation is read-only, runs in no request and is reachable from no route, so
there is nothing for the gauntlet to attack. **The tenancy of a batch job is outside the
instrument the constitution points at** — recorded rather than repaired, because adding a
route to make it attackable would be inventing product to satisfy a checker.

What does hold the arms is `storage-reconcile.itest.ts`: nine of the eleven turn it red.

---

## 062-9 — a pin whose key names no file is still silent, four features on

**Carried from 049, re-measured, unchanged.** 71 per-file coverage pins, **0 unbindable**;
and a pin demanding **101% of `this-file-does-not-exist.ts`** produces no error, no warning
and no line, exiting 0.

Both halves run, the config restored and diffed afterwards. The ratchet binds today; the
blind spot that would let it stop binding is exactly as open as 049 found it.

---

## 062-10 — the SRS's data dictionary described a `media_events` table nobody built

**New.** The DR section's table row read:

    | `media_events` | Storage metering, scan-pipeline health (FR-MED-12)
    | `environment_id`, `ts`, `event` (uploaded/ready/rejected/deleted), `kind`, `bytes`, `processing_ms` |

Against what `0016` creates: the events are `reserved`/`rejected`/`rendition`/`deleted`, the
column is `bytes_delta`, there is a `media_id`, and there is no `processing_ms` at all —
`scan-pipeline health` was a second purpose the table never took on. **Four columns' worth of
divergence, in the document the table implements.**

Found by opening the DR section to edit DR-17, two rows below it. `check:srs` cannot see this:
it checks that identifiers are unique and ordered, and **no checker in these repositories
reads a clause against the schema it describes**. Corrected in revision 1.23.

---

## 062-11 — a feature-local id reached the SRS again, in the row announcing a clause fix

**Carried from 052-7, re-offended.** `git diff HEAD -- docs/ | grep '^+' | grep -oE 'FR-0[0-9][0-9]'`
returned **`FR-010`** — this feature's own spec-local id, written into revision 1.23 as though
it were a clause of the SRS.

052-7 recorded the mechanism as *copying the task line*, and that is what happened again: the
task for this work is phrased with the feature-local id and the id came along. **The
self-referential part is the finding** — it was committed inside the sentence correcting
somebody else's clause citation.

**AND NOTHING RUNS THIS CHECK.** It is one line, it has caught something in two of the four
features that have run it by hand, and it is in no `check:*` script and no workflow. That is
the same shape as 055-3 (`check:errors` has no CI job) with one fewer step: here there is no
script to leave unrun.

---

## 062-12 — this chapter shipped three source files and the ratchet held none of them

**New, and the config's own notes already name the class.** `vitest.coverage.config.mts` records
it about the quota chapter: *"this one shipped seven and left the ratchet nothing to hold, which
is visible only by comparing two chapters."* It happened again here —
`metering/storage-reconcile.ts`, `db/storage-reads.ts` and `metering/storage-event.ts` were all
unpinned, and `storage-event.ts` measured **66.66% statements** with nothing to notice.

The global floor is 70% **in aggregate**, so an unpinned file passes as long as the rest carry
it: **68 of the 139 files the run sees are unpinned and the lowest is at 20.00%.**

**CLOSED FOR THIS CHAPTER'S THREE**, with `storage-event.ts` pinned at 100 rather than at what it
first measured — a test now drives the `catch`, which is not a defensive branch but the whole of
what *"a lost record is the accepted cost"* means in code. The class stays open: nothing makes a
new file's absence from the ratchet visible, and both instances were found by a human comparing
one chapter to another.

---

## 062-13 — the carried ledger, re-measured

**050-8 — the ingester is not a deployment. WIDENED.** Still no Dockerfile, still zero mentions
in `compose.yaml`, and **three** test files now spawn it rather than two: `media.itest.ts`,
`request-log.itest.ts` and this chapter's `storage-metering.itest.ts`. Every analytical figure
this chapter publishes is on the far side of a process no deployment starts.

**055-3 / 061-4 — `check:errors` has no CI job, and `check:refs` does not exist.** Re-measured:
`check:errors` is 1 hit in `package.json` and **0 in `ci.yml`**, unchanged across four features.
`check:refs` is 0 in both — it has never existed and 061's task list still named it.

**059-20 — a per-file branch pin is a claim about the machine.** `media.controller.ts` now reads
**86.15% over 65 branch points locally** against a pin of 83 set from CI's 84.61. The
denominator has moved again — 33 at 4.13, 65 now — which is the entry's own point rather than a
new one: the two figures are not two samples of one quantity.

**043 — task ids in test titles.** **279 across 47 files**, from 330 across 46 at 045's close.
Fewer ids, one more file; still filed rather than swept.

---

## 062-14 — a restart left two streams unrecoverable, one at a time, and the second could not be cleared

**Carried from 048-6 / 049-1 / 058, reproduced exactly.** The host suspended and every container
exited; on restart NATS answered `JetStream stream '$G > ANALYTICS' could not be recovered`.
049-1's cause holds — the stream that fails to recover is whichever was being written — and the
api writes on every request while Docker polls `/healthz` every five seconds, so a restart always
lands mid-write.

058's shape held too: **the health check names one unrecoverable stream at a time.** Clearing
`ANALYTICS` and restarting produced `EVENTS`, and N corrupt streams cost N restarts with each one
looking like the last.

**AND THE SERVER OFFERS NO WAY OUT.** `jsm.streams.delete("EVENTS")` answers `stream not found`:
the server cannot see a stream it failed to recover, so the only repair is removing the directory
from the JetStream volume. **This environment's guard permitted that for the first stream and
refused it for the second**, which is 058's *"the bulk form of a permitted operation is not
automatically permitted"* at one instance rather than a loop.

**AND THEN IT REPAIRED ITSELF, WHICH IS THE PART WORTH KEEPING.** Starting the composed api
brought the health check to `{"status":"ok"}` with all three streams present — `ANALYTICS` 333
messages, `EVENTS` 816, `DELIVERIES` 17. The api creates its streams on first publish, and a
fresh `streams.add` over a directory the server never loaded succeeds where `streams.delete`
answered `stream not found`.

So the repair is **start the thing that owns the stream**, not reach into the volume — and the
refusal that blocked the second removal blocked a step that was not needed. Recorded in full
because the intermediate state is convincing and wrong: two restarts, two different stream
names, a server that cannot see what it is complaining about, and an obvious conclusion
(*"the files have to go"*) that the first removal appeared to confirm.

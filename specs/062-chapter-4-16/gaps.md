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

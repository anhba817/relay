# Gaps — chapter 4.21, "Erasure, and every path it must find"

Numbered. The carried ledger is re-measured at T064 rather than copied.

---

## 067-1 — the audit log holds the name of everyone it says was erased

**MEASURED, AND IT GREW BY ONE PER ERASURE DURING THIS FEATURE.**

```
audit_log.target_id                        text
user-target rows                           1,357      (the spec said 1,324)
of those, NOT a uuid                       1,357 of 1,357 — every one an EXTERNAL id
actor_kind on every row                    application — a user is never the actor
actions on user targets   ban 936 · unban 235 · delete 186 · ERASE, from this chapter
```

An entry recording that somebody was banned is itself a record of that person. The
log is append-only (ADR-35), so no operation removes one, and **the erasure writes a
new entry naming the person it just erased** — which is deliberate, because that
entry is the operator's only proof the erasure happened and FR-MOD-03's log exists to
demonstrate exactly that. The receipt reports it as `cannot_erase`.

**THE REPAIR WOULD BE NARROWING ADR-35 A SECOND TIME IN TWO CHAPTERS**, which is why
it is a gap and not this chapter's work. Chapter 4.20 opened the first exception —
one verb, one table, one named deleter — and a second one, three chapters later, for
a different reason, is how a guarantee becomes a list of exceptions. If it is ever
taken, the shape is not a delete: it is a `target_id` that holds the internal uuid
for FUTURE entries, with the 1,357 already written left where they are, because no
migration can recover an identity that was never stored anywhere else.

**AND A HASH IS NOT THE ANSWER HERE EITHER**, for the reason `contracts/erasure.md`
gives about the tombstone: `u-4821` and an email address are both brute-forceable, so
a hashed `target_id` is the identity wearing a disguise and would make the log
useless to the operator as well.

Seen during this feature at full force: the injection test's user has external id
`' OR 1=1 --`, and that string is now in the audit log in plaintext, for ever,
written by the erasure of that very user.

---

## 067-2 — `research.md`'s injection payload is a syntax error, not an injection

**The mechanism is real and the string published beside it does not produce it.**
R9 named `ev'il OR 1=1 --` and reported a count going from 0 to 1,081. Asked of the
server directly, both interpolated into the same scoped statement:

```
ev'il OR 1=1 --    Code: 62. Syntax error: failed at position 144 (il)
' OR 1=1 --        1,116 — the whole table
```

The leading quote has to **close** the literal cleanly. `'ev'il …` parses as the
string `'ev'` followed by an identifier and dies — which an interpolating
implementation survives as a caught error and a `not_reached` line on the receipt.
**That is a safe failure.** The 1,081 is a real table total from a real
measurement, so the number was not invented; the string was transcribed wrong, or
the measurement used a different one.

**WHAT IT COST, AND IT IS THE REASON THIS IS AN ENTRY.** The red probe was run
against the published payload first and the test went red — on the wrong
assertion, `expected 1 to be +0`, the hostile user's own row rather than the
bystander's. **A red that looks like proof is worse than a green**, and only
reading which assertion failed caught it.

**A payload that errors tests the error path; only one that parses tests the
predicate.** Fixed in `research.md`, in the test and in the chapter's TRAP box.

---

## 067-3 — a feature-local id reached the API response body

`FR-028` and `FR-029` are feature-local to the chapter that built `deleteUser`.
**There is no `FR-028` in `docs/04-srs.md`**: the messages clause is FR-USR-05, and
for the billing argument there is no clause at all — it is a comment in that
method. Both were copied out of `deleteUser`'s docstring into this feature's
record, into `repository.ts`, and into **the receipt's `note` fields**.

**THE RECEIPT IS A NEW CLASS AND IT IS WORSE THAN THE DOCUMENT CASE.** 053 found a
feature-local id reaching two published documents. This one reaches **a compliance
officer at a customer**, who has no access to this platform's specification by any
means — the string is unresolvable by construction, for the one reader least able
to come and ask. Every receipt note is plain prose now.

**AND THE SWEEP THAT WAS SUPPOSED TO CATCH IT RETURNED A CONFIDENT ZERO.**
`git diff part4-ch20..HEAD -- docs/` reads **committed** state and the `docs/` edits
were in the working tree:

```
git diff part4-ch20..HEAD -- docs/     0 feature-local ids added     WRONG
git diff part4-ch20     -- docs/       2 — `FR-014`, twice, both mine
```

`..HEAD` is how a diff quietly stops looking. 063-4's defect committed by the
person who had just read the rule, hidden by an instrument reporting zero.

**Nothing runs either form of this check.** 063-4 is still open and this is a
second way for it to be missed.

---

## The carried ledger, re-measured

| id | what it said | re-measured 2026-10-05 |
|---|---|---|
| **066-1** | an audit entry outlives its target — 1,435 rows name a message | **the hazard stands and the instance count is now 0.** No foreign key exists, so nothing prevents it; today every message target still resolves. **A property with no instances is still a property** — and this chapter made the shape worse, not better: `audit_log` now also holds 1,781 user targets whose rows will outlive erasure by design |
| **065-2** | the edit path still writes a millisecond `Date` | **OPEN, and the split is sharper.** `ended_by='edit'`: **5,929 of 5,929** millisecond-exact. `ended_by='deletion'`: **51 of 1,472** — about 3.5%, which is chance, so 4.19's `sql\`now()\`` fix is holding on the path it was applied to and the edit path was never fixed |
| **058-3** | a malformed path parameter is a caller-triggered 500 — "23 routes, not sixteen" | **22 uuid-shaped path params across three controllers**: 13 `channelId`, 6 `id`, 3 `messageId`. **This chapter's route is NOT a member** — `externalId` is text and reaches no uuid cast — which is the first thing to check before adding a route to that count |
| **063-4** | the feature-local id check is diff-scoped and nothing runs it | **OPEN, and 067-3 is a second way to miss it.** `..HEAD` excludes the working tree, so even the diff-scoped form reports zero on uncommitted work |
| **062-12** | 68 of 139 files unpinned under a global floor | **OPEN. `services/api/src/users/` has ZERO pins** — not one of its five files, including the two this chapter wrote. T065 adds them |
| **050-8** | the ingester is not a deployment; two test files start a process | **OPEN, unchanged.** `message_events` still holds 0 rows and has no producer, which is why FR-MOD-04's third analytical store is met vacuously |
| **043-1** | 146 of 904 fences are untitled and outside every gate | **OPEN.** This chapter contributed 0 titled fences and six untitled ones, so it widened the population it did not close |
| **064-1 · 065-3 · 065-5 · 066-2 · 066-4** | carried | not re-measured this feature; none was touched by its edits, and saying so is better than copying a number |

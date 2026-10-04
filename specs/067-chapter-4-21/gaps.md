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

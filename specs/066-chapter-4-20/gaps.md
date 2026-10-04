# Gaps — chapter 4.20, "The messages that expire" (feature 066)

Numbered, with what was measured rather than what was suspected. The carried
ledger is re-measured rather than copied: four of 043's twenty-three carried
items were wrong when re-measured and three had closed with nobody working on
them.

## 066-1 · An audit entry outlives the message it names, and nothing refuses it

**Measured at the open and unchanged by this chapter:**

    audit_log rows naming a message target          1,435
    audit_log rows in total                         3,477
    foreign key from audit_log to messages          NONE

An entry records that an action happened, not the thing it happened to — so
there is no constraint between the two tables and nothing in the database stops
a message being destroyed while an entry still names its id. After this chapter
the sweep destroys messages, so **an entry whose `target_id` resolves to nothing
is a state the platform now reaches on purpose rather than by accident.**

**STATED RATHER THAN FIXED, AND THE REASON IS THE OTHER CLAUSE.** Repairing it
means one of two things and both are worse than the gap:

- **Add the foreign key.** Then an audit entry refuses the deletion FR-MOD-06
  requires, and the two clauses deadlock.
- **Delete the entries whose target is gone.** That is a DELETE against
  `audit_log`, which `0021`'s `BEFORE UPDATE OR DELETE` trigger refuses — and
  the refusal is ADR-35's published guarantee, which chapter 4.18 wrote and this
  chapter has already narrowed once. Narrowing it twice in two chapters for a
  cosmetic repair is not a trade worth making.

So a reader of the audit log may find an entry naming a message that no longer
exists, and the honest answer is that the entry is the record and the message
was not. The log says what a moderator did; it was never a copy of what they did
it to.

**WHAT WOULD CHANGE THIS.** FR-MOD-05's export — unbuilt, two rows above
FR-MOD-06 — is the clause that would let a tenant hold the message beside the
entry. Until it exists, the audit log is the only durable record of a moderation
action and it carries an id rather than a payload.

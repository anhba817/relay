# Traceability — chapters 3.15 and 3.16 against the governing documents

**Generated rather than grown**, for chapter 3.12's reason: editing citations into 58
bullets is what chapter 3.11's traceability pass attempted with a regex, and it broke 36
files. A map in one file can be wrong in one place.

Two directions, because only one of them catches an omission:

- **§1** every requirement these chapters make → the clause it implements
- **§2** every governing clause they touch → the requirement covering it

Chapter 3.12's map found four clauses touched and unclaimed, and one row recording a clause
as delivered when it was not — **found only because this feature's spec read that map for a
purpose other than writing it.** That is the reason §2 exists and the reason it is checked
by reading it against something else.

---

## §1 — requirement → governing clause

### The private channel type, and the four doors (FR-001 to FR-010)

| Requirement | Implements |
|---|---|
| FR-001 | FR-CHN-05 (a private channel's messages are visible only to its members) |
| FR-002 | FR-CHN-05; SC-002's byte-identical refusal, which is FR-TEN-05's rule applied inside a tenant |
| FR-003 | FR-CHN-05; FR-MSG-09 (history's own shape is what "answers as absent" means on that route) |
| FR-003a | FR-CHN-01 (a channel has four fields and nothing could read them back) |
| FR-004 | FR-CHN-03 (any authenticated user of the tenant may read and join a public channel) |
| FR-005 | FR-CHN-05; chapter 3.3's unattributed REST send — the tenant acts for the customer and sees private channels |
| FR-006 | FR-CHN-06, second half (removal; 3.13 delivered adding) |
| FR-007 | FR-CHN-06; chapter 3.13's per-entry result shape |
| FR-008 | FR-CHN-03 (a user joining on their own behalf) |
| FR-009 | FR-CHN-01's `type`; constitution V (do not sell a guarantee before keeping it) |
| FR-010 | FR-CHN-07 (a channel holds at most 1,000 members) |

### Roles (FR-011 to FR-012)

| Requirement | Implements |
|---|---|
| FR-011 | **FR-CHN-04** (member roles), recorded as delivered by chapter 3.12's map and not delivered until now |
| FR-011a | FR-CHN-04's vocabulary — `owner`, `moderator`, `member`, and NOT `memberships`' `admin` (FR-TEN-07) |
| FR-011b | FR-CHN-04 with FR-CHN-06 (a member creatable with a role, in the add's shipped shape) |
| FR-012 | NFR-MNT-02 — a column whose reader nobody can name is a column nobody maintains |

### The listing, the count, the last message (FR-013 to FR-022a)

| Requirement | Implements |
|---|---|
| FR-013 | FR-CHN-08 (channel listing, cursor-paginated) |
| FR-014 | FR-CHN-08's "most recent activity"; DR-05 (an ordering key is indexed) |
| FR-015 | FR-CHN-08 with FR-CHN-05 — the listing set is the membership set |
| FR-016 | FR-CHN-09 (unread counts) |
| FR-017 | FR-CHN-09's read position; FR-MSG-05 (a sequence is the acknowledgement) |
| FR-017a | FR-CHN-09 — absence of a position is a state, and it is zero |
| FR-018 | FR-CHN-09; DR-01 (`last_sequence` is the sequencing authority, chapter 2.2) |
| FR-019 | FR-CHN-09 with **FR-MSG-08** (a tombstone retains its sequence) |
| FR-020 | FR-CHN-10 (archiving) |
| FR-020a | FR-CHN-10 — archiving preserves history, which is a property to assert not assume |
| FR-021 | FR-CHN-10's refusal |
| FR-021a | FR-TEN-05 applied to refusal ORDER — a refusal must not reveal what it refuses |
| FR-022 | FR-CHN-10 with FR-CHN-08 (an archived channel is still listed) |
| FR-022a | FR-CHN-10 with FR-RTM-03 (an archived channel's resume cursor is still accepted) |

### The user surface (FR-023 to FR-032)

| Requirement | Implements |
|---|---|
| FR-023 | FR-USR-03 (display name, avatar URL, metadata) |
| FR-024 | FR-USR-03's 4 KB bound; constitution VI (a bound is refused by field name) |
| FR-025 | FR-USR-04 (bulk upsert, up to 100) |
| FR-025a | FR-USR-04's bound, and the same 100 as FR-CHN-06's |
| FR-026 | FR-USR-04 — an entry naming an existing user updates it |
| FR-027 | FR-USR-05 (deletion) |
| FR-028 | FR-USR-05's "preserving their messages as authored by a deleted user" |
| FR-028a | FR-USR-05; FR-RTM-03 — `toFrame` drops a senderless row, so the two states must differ |
| FR-029 | FR-USR-05 with FR-TEN-08 (billing history is not profile data) |
| FR-030 | FR-USR-05 with DR-02 (`(environment_id, external_id)` is unique, so the row is reused) |
| FR-031 | FR-USR-06 (banning) |
| FR-031a | FR-USR-06 — a ban lifts, and lifting restores what it took |
| FR-032 | FR-USR-06 with FR-AUT-11 (what a credential change does to an open socket) |

### The suite, the corrections, the chapters (FR-033 to FR-040a)

| Requirement | Implements |
|---|---|
| FR-033 | NFR-SEC-09; constitution I (the isolation suite runs on every build) |
| FR-033a | NFR-SEC-09; feature 030's list-with-reasons doctrine — nothing exempt by omission |
| FR-034 | NFR-SEC-09 extended inside a tenant: authorization, not tenant isolation |
| FR-034a | FR-TEN-05 — the same string in two tenants resolves to two rows |
| FR-035 | constitution VI (a check with no failing test is a check nobody has seen fail) |
| FR-036 | NFR-MNT-02 — the count of columns nothing reads, before and after |
| FR-037 | constitution IV (a false comment in published prose is a defect) |
| FR-038 | constitution IV; chapter 3.12's traceability row |
| FR-038a | constitution IV — a citation that names the wrong chapter sends a reader nowhere |
| FR-038b | NFR-MNT-02 — a feature directory is named once |
| FR-039 | constitution VI (a documented status per route) |
| FR-039a | **FR-USR-02** (implicit creation on first authentication) |
| FR-039b | FR-USR-02 with DR-02 — authentication and membership converge on one row |
| FR-039c | FR-USR-02 — the response must not distinguish created from existed |
| FR-040 | `docs/07-tutorial-plan.md`'s 2,000–4,000 word bound |
| FR-040a | The same bound, per chapter, against a measured file count |

---

## §2 — governing clause → the requirement covering it

### The twelve clauses this feature was specified to deliver

| Clause | Covered by | Delivered |
|---|---|---|
| FR-CHN-03 | FR-004, FR-008 | yes — public read and join, and a private channel answers as absent |
| FR-CHN-04 | FR-011, FR-011a, FR-011b, FR-012 | yes — `members.role` with its own CHECK, and no operation authorized by it |
| FR-CHN-05 | FR-001, FR-002, FR-003, FR-005 | yes — all four doors |
| FR-CHN-06 | FR-006, FR-007 | yes — removal, up to 100, reported per user |
| FR-CHN-08 | FR-013, FR-014, FR-015 | yes — keyset on `(last_activity_at, id)` |
| FR-CHN-09 | FR-016 to FR-019 | yes — `greatest(last_sequence − position, 0)`, no counter |
| FR-CHN-10 | FR-020, FR-021, FR-022 | yes — archiving, below membership in the order |
| FR-USR-02 | FR-039a, FR-039b, FR-039c | yes — on the mint path |
| FR-USR-03 | FR-023, FR-024 | yes — the first writer `avatar_url` and `metadata` ever had |
| FR-USR-04 | FR-025, FR-025a, FR-026 | yes — 100 per request, per-entry results |
| FR-USR-05 | FR-027 to FR-030 | yes — the row survives, the messages keep their author |
| FR-USR-06 | FR-031, FR-031a, FR-032 | yes — at the door and on the send path |

### Clauses this feature TOUCHES without being asked to, and what covers them

The direction chapter 3.12's pass five added, because it is the one that finds an omission.

| Clause | How this feature touches it | Covered by |
|---|---|---|
| FR-TEN-05 | Every refusal in the feature is byte-identical to an absent identifier, and FR-021a fixes the ORDER so no refusal reveals what it refuses | FR-002, FR-021a, FR-034a |
| FR-MSG-08 | The listing reports a tombstoned last message with `text: null`. **The clause itself is unimplemented** — nothing in the platform writes `messages.deleted_at` — so the rule is tested against a state constructed by raw SQL | FR-019, and the clause stays open |
| FR-MSG-05 | A read position is a sequence, and the sequence is the acknowledgement | FR-017 |
| FR-RTM-03 | A deleted user's message must still reach a resuming client, and an archived channel's cursor is still accepted | FR-028a, FR-022a |
| FR-AUT-11 | A ban does not terminate an open socket; it stops the socket writing. Same shape the clause already required for an expired token | FR-032 |
| FR-TEN-08 | `usage_active_users` survives a user deletion | FR-029 |
| DR-05 | `channels.last_activity_at` gains an index, and `EXPLAIN ANALYZE` shows it used at 50,000 memberships | FR-014 |
| EIR-WS-06 | A fifth close code, `4003`, for a class the clause does not name | FR-031 |
| **FR-027 (SRS)** | `docs_url` — the gateway was discarding every api refusal code but 401, so `user_banned` and `channel_archived` reached socket clients as `internal_error` and their `docs_url` never existed. **Touched and unclaimed by any requirement in this spec** | nothing — found in Phase 15, recorded here |

**One clause touched and unclaimed**, which is the same shape pass five found in chapter
3.12 and one fewer instance. The gateway's discarded refusal codes are a defect against
the SRS's own `docs_url` clause, found by implementation rather than by reading, and no
requirement in this spec asked for the fix. Recorded rather than back-filled into a
requirement: a requirement written after the work to describe the work is not a
requirement, and the next feature to touch `api-client.ts` should know why it looks the
way it does.

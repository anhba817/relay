# Traceability — chapter 3.23

**Built in phase 1, both ways, before a line of production code exists.** That placement is
the predecessor's lesson with a number on it: chapter 3.18 ran the map only at close-out and
found FR-007 — a MUST — with no test at all, after eight phases and nineteen analysis passes
had each read `requirement → test` and believed it. Chapter 3.22 ran it during planning and
found two orphans immediately.

**Generated from `spec.md` and `tasks.md` rather than typed.** Every row's id and every task
in it was read out of those two files by a script, so the map cannot be incomplete in the one
way a hand-written map always is. What a script cannot do is judge whether the named task
verifies the thing — that is the reader's job and section 4 says so.

**No task ids in prose elsewhere; here they are the subject.** `check-refs.py` forbids a task
id in any other artifact because ids go stale when tasks are renumbered. This file is the
map, so it carries them — and it is regenerated in phase 12 rather than edited.

**Methods are the constitution's four**: **T**est, **D**emonstration, **I**nspection,
**A**nalysis.

---

## 1. SRS clause → feature requirements → verification

| SRS clause | Pri · method | Feature requirements | Verified by |
|---|---|---|---|
| **FR-MSG-07** — editing preserves the sequence number and records an immutable edit history with timestamps | P2 · T | FR-001 … FR-005, FR-021, FR-023, FR-023a | unit and route tests; the history is read through a route, not the database |
| **FR-MSG-08** — deletion replaces content with a tombstone retaining sequence number, author, timestamps and deletion metadata | P2 · T | FR-006, FR-006a, FR-007, FR-009 | integration; **FR-006a is the clause's "deletion metadata" read as more than a timestamp** |
| **FR-MSG-10** — history responses include tombstones so clients render deletions without gaps | P2 · T | FR-011, FR-017, FR-017a | **T009, against unchanged code, before any writer** |
| **FR-RTM-05** — real-time events for creation, edit, deletion, membership, presence, typing | P1 · T | FR-005, FR-007, FR-008, FR-008a | the two frames, and SC-008's six-producers check |
| **FR-MOD-01** — retrieving a channel's complete history including tombstones and edit history, via API key | P2 · T | FR-023, FR-023a | **the per-message half only**; the channel-level read stays that clause's chapter |
| **FR-MOD-02** — deleting any message via API key irrespective of author | P2 · T | FR-012, FR-013, FR-013a | integration, both refusals and the permitted case |
| **FR-WHK-02** — the eight event types | P2 · T | FR-019, FR-020 | the fourth and fifth of eight; three existed |
| **FR-RTM-03** — resume delivers everything past the cursor | P1 · T | FR-016, FR-016a, FR-016b | integration, and **the documented bound for what a cursor cannot see** |
| **CON-02 / Principle I** — no sticky routing; isolation is a correctness property | — · I | FR-014 | the isolation gauntlet, three declared targets |
| **FR-MOD-03** — the moderation audit log | P3 · T | — | **not built, and widened by this chapter** — chapter 3.23's `gaps.md` item 2 |

## 2. Feature requirement → method → the tasks that verify it

| Requirement | M | What it asks | Verified by |
|---|---|---|---|
| FR-001 | T | The system MUST allow the author of a message to change its text. | T026 |
| FR-002 | T | An edit MUST preserve the message's sequence number, its channel, its author and its… | T026, T027 |
| FR-003 | T | An edit MUST record when it happened, distinguishably from when the message was created. | T026 |
| FR-004 | T | Every edit MUST append the superseded text to an immutable history with its own timestamp.… | T026, T028 |
| FR-005 | T | An edit MUST be announced to every connected member of the channel as `message.updated`,… | T031, T033 |
| FR-006 | T | The system MUST allow a message to be deleted, replacing its text and its attachments with… | T039, T040, T041 |
| FR-006a | T | The deletion's metadata MUST record **who performed it** as well as when. FR-MSG-08 itemises… | T039a, T040, T073 |
| FR-007 | T | A deletion MUST be announced to every connected member of the channel as `message.deleted`,… | T045, T046 |
| FR-008 | T | The deletion event MUST identify the message, its channel, its position in the channel's… | T013 |
| FR-008a | I | The message payload used by creation and edit events MUST be left unchanged. It has been… | T013 |
| FR-009 | T | Deleting an already-deleted message MUST succeed without changing the row and without… | T042, T043 |
| FR-010 | T | Editing a deleted message MUST be refused. | T022, T044 |
| FR-011 | T | History responses MUST include deleted messages in their original position, so a reader sees… | T009, T047 |
| FR-012 | T | A tenant API key MUST be permitted to delete any message in its environment irrespective of… | T041a, T051, T052 |
| FR-013 | T | An end user MUST NOT be permitted to edit or delete a message they did not author. | T030, T054 |
| FR-013a | T | A tenant API key MUST NOT be permitted to edit a message. FR-MOD-02 grants it deletion of… | T030, T053 |
| FR-014 | T | A message in another tenant's environment MUST be indistinguishable from one that does not… | T029, T055 |
| FR-015 | T | Neither an edit nor a deletion MUST change a channel's position in the activity ordering by… | T034 |
| FR-016 | T | A resuming client MUST NOT be sent the superseded text of a message that was edited while it… | T058, T059 |
| FR-016a | T | Resume MUST stay ordered by the channel sequence alone. A message older than the client's… | T060 |
| FR-016b | T | The limit in FR-016a MUST be documented as a property of a cursor rather than left to be… | T075a |
| FR-017 | I | The behaviour of **every** read path with respect to tombstones MUST be stated in one place… | T076a |
| FR-017a | I | The statement required by FR-017 MUST be derived from the code at the time it is written… | T076a |
| FR-018 | T | An edit or deletion MUST be refused for a message whose author cannot be established, rather… | T036, T042a |
| FR-019 | T | An edit MUST be emitted to subscribed webhook endpoints as `message.updated`, and a deletion… | T065 |
| FR-020 | T | The deletion webhook event MUST NOT carry the message's text, for the same reason the… | T067 |
| FR-023 | T | A message's edit history MUST be readable, oldest entry first, by a tenant API key.… | T033b, T033c |
| FR-023a | T | The edit-history read MUST be refused to an end user, including the message's own author.… | T033c, T033e |
| FR-021 | T | An edit whose text equals the current text MUST be treated as an edit — an edit time, a… | T036a |
| FR-022 | T | A refusal because the caller did not write the message MUST carry a code of its own rather… | T017a, T075 |

## 3. Success criterion → method → the tasks that verify it

| Criterion | M | What it asks | Verified by |
|---|---|---|---|
| SC-001 | T | An author can correct a message and every other member watching the channel sees the… | T033 |
| SC-002 | T | After three edits, an operator can retrieve all three superseded texts in order, through a… | T001a, T033d |
| SC-002a | T | An end user cannot retrieve what a message used to say. | T033e |
| SC-003 | T | A deleted message leaves no gap: a reader paging through the channel's history sees an… | T009, T047 |
| SC-004 | T | A deletion removes the content from every path a reader can reach it by, in the same request… | T001a, T051 |
| SC-005 | T | An operator can remove any message in their environment without acting as a person. | T052 |
| SC-006 | T | A client that was disconnected across an edit and a deletion, and follows the documented… | T061 |
| SC-006a | T | The one case the repair is needed for — a change to a message older than the client's cursor… | T001a, T075a |
| SC-007 | T | Repeating a deletion produces no additional events and no additional history. | T043 |
| SC-008 | T | FR-RTM-05's six event kinds all have producers, with none of the six emitted by nothing. | T049a |
| SC-009 | I | Every read path's tombstone behaviour is documented — four of them — and each documented… | T076a |
| SC-010 | A | The full integration lane's mean stays inside its 240-second budget. | T098 |
| SC-011 | T | A customer subscribed to message events is told about an edit and a deletion, not only about… | T069 |

## 4. The reverse direction — deliberately empty

It maps every test this chapter adds back to a named requirement, across the eleven files
that gain tests, and **one of those tests exists**: T009's tombstone read. Phase 12 fills the
rest.

**Recording the direction now, empty, is what stops it being forgotten** — the failure
chapter 3.18 shipped, and the reason chapter 3.22's close-out found four of six files missing
from its own first list.

## What this file does not establish

Every row names the tasks that cite a requirement. **None says the task verifies it**, and
the difference is not academic:

- **A citation can be a mention.** SC-002, SC-004 and SC-006a each list the task that added
  the coverage rule to `check-refs.py`, because that task's text names them while explaining
  what the rule found. Each also lists a genuine verifier. The rule counts a mention in a
  working task, which is stricter than counting a commit line and looser than counting a
  test.
- **A test can pass while proving nothing.** T009 passed its first falsification because it
  read one of `listMessages`' two query branches; the filter went into the other. The test now
  reads both and both turn it red.
- **Four rows cannot have a test at all.** FR-008a, FR-017, FR-017a and SC-009 are inspection;
  SC-010 is analysis, measured by the battery.

The close-out re-derivation maps the same requirements against the **shipped tree** rather
than against this plan, and that is the pass that can say whether any of it is true.

---

## 5. Re-derived at close-out, against the shipped tree

**Both directions, and every quoted test title checked as an exact string** rather than by
eye. The generator that built sections 1 to 4 reads `spec.md` and `tasks.md`; this section
reads the **repository**, which is the only thing that can say whether a task that claims to
verify a requirement produced a test that exists.

Every requirement's named task is done, and the tests those tasks wrote are in the tree:

    84 new tests across 14 files, counted from `git diff` against part3-ch22^{commit}

    packages/protocol/src/frames.test.ts               3
    packages/protocol/src/codes.test.ts                1
    packages/protocol/src/revision.test.ts             7
    services/api/src/db/repository.itest.ts           19
    services/api/src/messages/messages.itest.ts       26
    services/api/src/outbox/event.test.ts              8
    services/api/src/webhooks/deliveries.itest.ts      1
    services/api/src/internal/backfill.itest.ts        5
    services/api/src/fanout/publisher.test.ts          3
    services/gateway/src/session.test.ts               4
    services/gateway/src/session.itest.ts              2
    services/gateway/src/resume.itest.ts               1
    services/gateway/src/fanout.itest.ts               4
    packages/outsider/src/integrate.itest.ts           1

**THE MAP NAMED ELEVEN FILES AND THE TREE HAS FOURTEEN.** Section 2's task list was written
during planning, and three files it never mentions carry tests: `revision.test.ts` (the fifth
grammar did not exist when the map was written), `backfill.itest.ts` (US4's tests moved there
from the gateway, which has no database) and `publisher.test.ts`. One file the map DOES name —
`packages/protocol/src/fanout.test.ts` — gained no test at all, because the subject function
went into a module of its own.

**Four rows point at tasks whose file moved**, and the map is left as generated rather than
edited, with the moves recorded here:

    FR-016, FR-016a   T058-T061 name `services/gateway/src/resume.itest.ts`.
                      Five of the six tests are in
                      `services/api/src/internal/backfill.itest.ts`; one is in the
                      gateway file, and it is the only half that file can answer.
    FR-019            T065-T067 name phase 9. The types, the union branches and both
                      builders shipped in phase 6, because ADR-06 puts the outbox
                      insert inside the transaction that writes the tombstone.
    FR-023, FR-023a   T033b-T033h name `messages.controller.ts` and they are there,
                      but the read they call — `listMessageEdits` — is in the
                      repository, which no row names.
    SC-008            T049a names `session.test.ts` and is there. Its FIRST home in
                      the task list was `frames.test.ts`, where it cannot be written.

**What is still not established by this file**, unchanged from what section 4 says: that a
named test verifies the thing it is named against. Section 5 adds only that the test exists
and that its title says what its assertion checks — 84 read one at a time, six retitled.

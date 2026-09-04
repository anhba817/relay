# Traceability — chapter 3.24, attachments

**Generated from `spec.md` and `tasks.md` rather than typed.** Every row's id and every task
in it was read out of those two files by a script, so the map cannot be incomplete in the one
way a hand-written map always is. What a script cannot do is judge whether the named task
verifies the thing — section 3 says so.

**Built in phase 1, both ways, before a line of production code exists.** Chapter 3.18 ran
the map only at close-out and found FR-007 — a MUST — with no test at all, after eight phases
and nineteen analysis passes had each read `requirement → test` and believed it.

**No task ids in prose elsewhere; here they are the subject.** `check-refs.py` forbids a task
id in any other artifact because ids go stale when tasks are renumbered. This file is the map,
so it carries them — and it is regenerated in phase 12 rather than edited.

---

## 1. Feature requirement → the tasks that verify it

| Requirement | What it asks | Verified by |
|---|---|---|
| FR-001 | The system MUST accept up to 10 attachments on a message send. | T019, T021, T022, T023, T025, T026, T029, T034 |
| FR-002 | An attachment MUST declare a kind of `image`, `audio` or `video`, and a kind outside that set… | T009, T013, T037, T042 |
| FR-003 | An attachment MUST carry an external URL. A `media_id` attachment MUST be refused with a code… | T009, T013, T039, T042 |
| FR-003a | The refusal in FR-003 MUST say that hosted media is not available rather than that the field … | T039, T040, T042 |
| FR-003b | The attachment shape MUST be a discriminated union on a kind field from the first version, so… | T009, T013 |
| FR-004 | An attachment URL MUST be refused unless its scheme is `http` or `https`. | T011, T013, T038, T042 |
| FR-005 | A send carrying more than 10 attachments MUST be refused, and MUST write no message row. | T019, T025, T035, T036, T041, T042 |
| FR-006 | Attachments MUST be returned in the order they were submitted, on every path that returns a m… | T022, T023, T025 |
| FR-007 | A message with no attachments MUST be returned with an empty list rather than an absent field… | T028, T031, T034 |
| FR-008 | Attachments MUST be delivered to connected members in the same frame as the message they belo… | T014, T018, T027, T030, T034 |
| FR-009 | History responses MUST include each message's attachments. | T028, T029, T034 |
| FR-010 | The resume backfill MUST include attachments, so a client that was away and a client that sta… | T051, T052, T054 |
| FR-011 | A recognised idempotent retry MUST return the original message's attachments and MUST NOT wri… | T049, T050, T054 |
| FR-012 | Deleting a message MUST unlink its attachments, and the tombstone MUST be returned with an em… | T043, T048 |
| FR-013 | The deletion event MUST NOT carry attachment data, for the same reason it carries no text. | T016, T044, T048 |
| FR-014 | An attachment MUST NOT be readable by a caller who cannot read the message it belongs to. | T032a |
| FR-015 | The message payload used by creation and edit events MUST carry attachments identically, so a… | T014, T018, T057, T060 |
| FR-016 | Whether an edit may change attachments MUST be decided and stated. If it may not, an edit MUS… | T045, T047, T048 |
| FR-017 | The number of attachments on a message MUST be derivable from what this chapter writes, so §4… | T058, T060 |
| FR-018 | The comment at `packages/protocol/src/frames.ts:14` scheduling attachments for Part 4 MUST be… | T002, T061, T067 |
| FR-019 | A message whose text is empty MUST be accepted when it carries at least one attachment, and M… | T004, T020, T024, T025 |
| FR-019a | An attachments-only message MUST stay distinguishable from a tombstone on every read path. `t… | T024, T025 |
| FR-019b | A message with no text and no attachments MUST still be refused. Relaxing the bound is condit… | T020, T025 |
| FR-020 | The attachment shape MUST leave room for §4.14's `media_id` arm without a breaking change to … | T009 |

## 2. Success criterion → the tasks that verify it

| Criterion | What it asks | Verified by |
|---|---|---|
| SC-001 | A member connected when a message with attachments is sent, and a member who reads it from hi… | T029, T030, T033, T034 |
| SC-002 | A send with eleven attachments is refused, and the channel's message count is unchanged after… | T035, T042 |
| SC-003 | A deleted message's attachments are unreachable through every read path the platform exposes,… | T043, T048 |
| SC-004 | An attachment whose URL uses a scheme other than `http` or `https` never reaches a client. | T038, T042 |
| SC-005 | A client that was disconnected across a send with attachments, and follows the documented rep… | T052, T054 |
| SC-006 | Every read path's behaviour with respect to attachments is stated in the architecture documen… | T063, T067 |

## 3. What this file does not establish

**That a named task verifies the thing it is named against.** The script matched an
identifier in a task line; it did not read the assertion under it. Chapter 3.23's close-out
read eighty-four test titles against their assertions one at a time and corrected six, all in
one direction — a title describing the data where the assertion described the promise.

**That the tasks are in the right phase.** Nothing compares a task's content with the heading
above it. Chapter 3.23 found three tasks under a heading about subject grammars that belonged
to the phase before, and eight analysis passes had not caught it.

## 4. The reverse direction

**Every task that names an id appears above.** A task naming none is setup, a commit, a gate
run or a record — and those are the tasks a coverage map cannot speak about, which is why
this section says so rather than leaving the difference to look like an omission.

    93 tasks · 24 requirements · 6 criteria
    0 ids with no verifying task

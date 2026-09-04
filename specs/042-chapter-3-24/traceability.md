# Traceability — chapter 3.24, attachments

**Generated from `spec.md` and `tasks.md` rather than typed**, and regenerated after each
analysis pass. Two passes have now moved the counts at the bottom of this file, and `sweep.py`
caught both — a count in a generated file is a claim like any other.

**It also caught the sentence that described it.** A rewrite of this paragraph quoted the
sweep's own failure message, and the sweep read the quoted figure as a fresh claim and failed
again. Reworded rather than exempted: a checker cannot tell a claim from a quotation of one,
and teaching it the difference mid-pass is how a checker learns to accept what it was pointed
at.

**Built in phase 1, both ways, before a line of production code exists.** Chapter 3.18 ran the
map only at close-out and found FR-007 — a MUST — with no test at all, after eight phases and
nineteen analysis passes had each read `requirement → test` and believed it.

**No task ids in prose elsewhere; here they are the subject.** This file is the map, so it
carries them, and it is regenerated rather than edited.

---

## 1. Feature requirement → the tasks that verify it

| Requirement | What it asks | Verified by |
|---|---|---|
| FR-001 | The system MUST accept up to 10 attachments on a message send. | T015a, T019, T021, T022, T023, T022a, T022b, T022c, T025, T026, T029, T034 |
| FR-002 | An attachment MUST declare a kind of `image`, `audio` or `video`, and a kind outside that set… | T009, T013, T037, T042 |
| FR-003 | An attachment MUST carry an external URL. A `media_id` attachment MUST be refused with a code… | T009, T013, T039, T042 |
| FR-003a | The refusal in FR-003 MUST say that hosted media is not available rather than that the field … | T039, T039a, T040, T042 |
| FR-003b | The attachment shape MUST be a discriminated union on a kind field from the first version, so… | T009, T013 |
| FR-004 | An attachment URL MUST be refused unless its scheme is `http` or `https`. | T011, T013, T038, T042 |
| FR-005 | A send carrying more than 10 attachments MUST be refused, and MUST write no message row. | T019, T022c, T025, T035, T036, T041, T042 |
| FR-006 | Attachments MUST be returned in the order they were submitted, on every path that returns a m… | T022, T023, T022c, T025, T028b, T030a, T052 |
| FR-007 | A message with no attachments MUST be returned with an empty list rather than an absent field… | T028, T031, T034 |
| FR-008 | Attachments MUST be delivered to connected members in the same frame as the message they belo… | T014, T018, T027, T028a, T028b, T030, T029a, T034 |
| FR-009 | History responses MUST include each message's attachments. | T028, T029, T030a, T034 |
| FR-010 | The resume backfill MUST include attachments, so a client that was away and a client that sta… | T051, T052, T054 |
| FR-011 | A recognised idempotent retry MUST return the original message's attachments and MUST NOT wri… | T049, T050, T050a, T054 |
| FR-012 | Deleting a message MUST unlink its attachments, and the tombstone MUST be returned with an em… | T043, T048, T050a, T054 |
| FR-013 | The deletion event MUST NOT carry attachment data, for the same reason it carries no text. | T016, T044, T048 |
| FR-014 | An attachment MUST NOT be readable by a caller who cannot read the message it belongs to. | T032a |
| FR-015 | The message payload used by creation and edit events MUST carry attachments identically, so a… | T014, T018, T057, T060 |
| FR-016 | Whether an edit may change attachments MUST be decided and stated. If it may not, an edit MUS… | T045, T047, T048 |
| FR-017 | The number of attachments on a message MUST be derivable from what this chapter writes, so §4… | T023, T058, T060 |
| FR-018 | The comment at `packages/protocol/src/frames.ts:14` scheduling attachments for Part 4 MUST be… | T002, T061, T067 |
| FR-019 | A message whose text is empty MUST be accepted when it carries at least one attachment, and M… | T004, T017b, T020, T020a, T024, T025 |
| FR-019a | An attachments-only message MUST stay distinguishable from a tombstone on every read path. `t… | T024, T025 |
| FR-019b | A message with no text and no attachments MUST still be refused. Relaxing the bound is condit… | T020, T020c, T025 |
| FR-020 | The attachment shape MUST leave room for §4.14's `media_id` arm without a breaking change to … | T009 |
| FR-021 | The same URL attached twice to one message MUST be stored and returned twice. The platform MU… | T036a |
| FR-022 | The attachments field on a message payload MUST be present on every payload that carries a me… | T014, T014a, T027 |

## 2. Success criterion → the tasks that verify it

| Criterion | What it asks | Verified by |
|---|---|---|
| SC-001 | A member connected when a message with attachments is sent, and a member who reads it from hi… | T028b, T029, T030, T033, T034 |
| SC-002 | A send with eleven attachments is refused, and the channel's message count is unchanged after… | T035, T042 |
| SC-003 | A deleted message's attachments are unreachable through **each of the six read shapes** `data… | T043, T048 |
| SC-004 | An attachment whose URL uses a scheme other than `http` or `https` never reaches a client. | T038, T042 |
| SC-005 | A client that was disconnected across a send with attachments, and follows the documented rep… | T052, T054 |
| SC-006 | Every read path's behaviour with respect to attachments is stated in the architecture documen… | T063, T067 |

## 3. What the analysis passes changed here

**Pass 1 — the socket door.** FR-001 (3.24) gained four verifiers and FR-008 (3.24) two, all
on the path a socket send takes. The task list had traced the field through the REST door and
treated the socket as a schema change; three named constructions between the two schemas
dropped it, and one strict response schema would have broken every socket send. **Coverage read
100% before that pass and 100% after** — the ids all matched and the tasks named the wrong
files.

**Pass 2 — the edge cases and the frame.** Two of the spec's seven edge cases had no task at
all, which an id-matching instrument cannot see because edge cases carry no identifiers. Both
became requirements with tests: FR-021 (3.24) for a duplicate URL, and the recovered-tombstone
case as an assertion on two guards this chapter changes the meaning of. FR-022 (3.24) settled
whether the frame's field is optional — it is not — and FR-006 (3.24) gained order assertions
on the resume and socket paths, where it had said only "with attachments".

**Pass 3 — the scenarios and the protocol's own limits.** One acceptance scenario asked for
something the protocol cannot do: the sender's acknowledgement carrying attachments, on a
`message.ack` whose payload has been `{ seq }` since chapter 2.2. Narrowed to the REST door and
given a test that keeps the narrowing honest. Seven of eight scenarios had a task; scenarios
carry no identifiers either.

**FR-017 (3.24) moved from a record task to a test** in pass 1. It had been cited by a task
that writes a paragraph, which is the shape `check-refs.py` refuses for commit tasks and did
not catch one step to the left.

## 4. What this file does not establish

**That a named task verifies the thing it is named against.** The script matched an identifier
in a task line; it did not read the assertion under it. Chapter 3.23's close-out read
eighty-four test titles against their assertions and corrected six.

**That the tasks are in the right phase.** Nothing compares a task's content with the heading
above it. Chapter 3.23 found three tasks under a heading that belonged to the phase before.

## 5. The reverse direction

**Every task that names an id appears above.** A task naming none is setup, a commit, a gate
run or a record — the tasks a coverage map cannot speak about.

    109 tasks · 26 requirements · 6 criteria
    0 ids with no verifying task

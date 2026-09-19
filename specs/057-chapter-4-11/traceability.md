# Traceability — feature 057, chapter 4.11, "the half of the union that was refused"

Every requirement and criterion to the tasks and artifacts that discharged it, and **anything
discharged in a weaker form than its words suggest**, said here rather than implied.

**Built by enumerating the ids and grepping, not from memory.** Analysis pass 10 ran that sweep
and found **14 of 51 requirements carrying no id anywhere in `tasks.md`** — all 14 covered in
substance, so the sweep produced fourteen alarms and every one was false. That is the argument
for doing it this way and also its limit: a literal match cannot build this table and neither
can recall. Each row below was read.

## Functional requirements

| id | discharged by | evidence |
|---|---|---|
| FR-001 | T013, T018–T032 | the `.refine(() => false)` deleted; `attach.itest.ts` accepts a user's own slot, an API key's, and a tenant-uploaded one |
| FR-001a | T032b | a `message.send` frame carrying a `media_id` commits — `message.ack` with `seq > 0` |
| FR-001b | T032a | `session.itest.ts:415` **converted, not deleted**; it now asserts the refusal is a UUID complaint and explicitly **not** the old sentence |
| FR-002 | T018, T033 | `eq(mediaObjects.environmentId, this.environmentId)`; the three-refusal test, and the gauntlet's forged-id attack |
| FR-003 | T019, T020, T034 | the uploader clause with its NULL arm; two users of one tenant in `attach.itest.ts` |
| FR-004 | T035 | an id no object has, in the three-refusal test |
| FR-005 | T036, T037 | one class in the repository, one code at the wire; **three bodies compared whole, byte-identical apart from `request_id`** |
| FR-006 | T023, T027 | `["url", "media"]` in order, no de-duplication |
| FR-007 | T039 | nine good attachments and one foreign store **nothing** — 0 rows with that text |
| FR-008 | T008, T010 | `media_not_available` gone from `codes.ts` and from the reference; `codes.test.ts` asserts the **absence** |
| FR-008a | T012, T042 | `z.uuid()`; a 400 naming `attachments.0.media_id`, asserted **not** to be `internal_error` |
| FR-009 | T022 | 422, `media_not_attachable`, `field` carrying the index |
| FR-009a | T011a, T011b | the 422 rung; run red by deleting it — *"expected 'internal_error' not to be 'internal_error'"* |
| FR-009b | T011a0, T010 | `unprocessable_request`, with a reference section saying what a client does |
| FR-010 | T019, T044, T046 | **WEAKER THAN ITS WORDS, AND SAID SO.** The predicate admits `pending` and `ready`; only `pending` can exist. The `ready` arm is built and cannot be exercised — the database refuses the row, and that refusal is the published evidence |
| FR-011 | T018 | the read is inside `sendMessage`'s transaction; SC-003's three figures are what prove it |
| FR-012 | T027a | ten mixed attachments accepted, eleven refused — the cap is over the union |
| FR-013 | T028a | the array read back unchanged at **two** doors (send response, history) and a third in `session.itest.ts` |
| FR-014 | T052, T053, T054 | the gauntlet attack, planting a row per tenant, with a control; run red it commits the victim's object |
| FR-015 | T055 | `gaps.md` 057-1 — nothing counts references, verified by grep returning zero |
| FR-016 | T067 | **0**, absolute: 290 files across 54 chapters, EXIT 0 |
| FR-017 | T070, T070a, T070b | SRS 1.18, `docs/12` row 12, and `docs/07`'s copy — **the second copy had received none of the four own-row amendments 4.7–4.10 wrote** |
| FR-018 | T017a | both outbox arms take the permissive element |
| FR-018a | T017b | red-first: strict, the envelope is **terminated** — `expected [] to include '<event id>'` |
| FR-018b | T017d, T017e | the send response; red-first against the strict schema |
| FR-018c | T004a | ten validators, re-verified against the tree; `data-model.md` §4b in two tables |
| FR-018d | T017f, T017g | the three readers reaching the union through `messageSchema`; all three red when strict |
| FR-019 | T055a | `gaps.md` 057-3 — `attachment_count` changes meaning at `load-analytics.mjs:178,187,200` |
| FR-020 | T028b | an edit leaves the attachment unchanged |
| FR-021 | T032e, T073a | the sealed suite uploads and attaches from outside — 19 of 19 |
| FR-023 | T050a | constitution VI answered **per arm, by deletion**, because the pin cannot carry it |
| FR-024 | T028c | delete nulls the column and the media row survives |
| FR-026 | T001a, T001b | 503 measured with its control, then 201 with a PUT from outside the network |
| FR-027 | T073b | the quickstart, run |

## Success criteria

| id | met? | evidence |
|---|---|---|
| SC-001 | yes | slot → upload → send → read back, in `attach.itest.ts` and again from outside |
| SC-002 | yes | three bodies, `toEqual` over the whole body with `request_id` removed |
| SC-002a | yes | the socket commits; `message.ack` |
| SC-002b | yes | red-first against the strict arm |
| SC-002c | yes | red-first |
| SC-002d | yes | the sealed suite, both arms delivered in order over a socket |
| SC-002e | yes | three tests, all red when their reader is strict |
| SC-003 | yes | rows, sequence **and outbox**, scoped to the test's own channel |
| SC-004 | yes | `check:errors` — 34 codes, 34 sections, both directions, by hand |
| SC-005 | yes | derivation 9 of 9; gauntlet 59 of 59; the new attack red without the predicate |
| SC-006 | yes | `violates check constraint "media_objects_state_check"`, quoted |
| SC-007 | yes | **0**, absolute |
| SC-008 | yes | 2,396 words, one TRAP |
| SC-009 | pending | T076 — after the push |
| SC-010 | yes | 29 at T003 and 29 at T068a, **measured twice** |
| SC-011 | yes | the four arms, each deleted and the suite re-run |
| SC-012 | yes | a slot from the **composed** api, and its URL used from outside the network |

## Discharged in a weaker form than the words suggest

**FR-010 is the headline one.** *"A message may attach a `media_id` in state `pending` or
`ready`"* — the predicate is built for both and only one half can run, because the column's
CHECK admits `pending` alone. The chapter publishes the database's refusal rather than a
skipped test, and does **not** widen the constraint so a fixture could plant `ready`: that
would buy a green assertion about a transition no code performs.

**FR-018c says ten validators and the number is a floor, not a ceiling.** It is what four
analysis passes found, and pass 6 found three of them only by asking what the union is
*embedded in* rather than who names it. The enumeration is better than it was; nothing proves
it is complete.

**FR-021's outsider test runs in a lane no local artifact named before this chapter.**
`pnpm test:outsider` is excluded from `pnpm test:integration` by name, deliberately, and CI
gives it a job of its own. A chapter adding a test there and running only the integration gate
would see it pass by never running.

**And SC-009 is the only one still open at the time of writing**, because a CI result cannot
exist before a push.

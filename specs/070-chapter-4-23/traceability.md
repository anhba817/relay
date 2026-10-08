# Traceability — chapter 4.23, "The channel a socket names"

Every requirement and criterion to the thing that discharges it, and to the
measurement that says so. Where a figure is quoted it is in `baseline.txt` with the
command that produced it.

## Functional requirements

| | discharged by | the evidence |
|---|---|---|
| **FR-001** every outbound field names the identifier | `send` at `session.ts:119`, one place | `channel-naming.itest.ts` — the ack's three structures, a delivered `message.created`, and a whole session with no key in any frame |
| **FR-002** every inbound field accepts it | `session.ts:1620` (send), `:1571` (typing), `resume.ts:74` (cursor) | a send by identifier hands the api the KEY; a typing frame by identifier is delivered; a cursor keyed by identity resumes |
| **FR-003** the Relay identifier is not lost | the same three sites, each trying the identity first | asserted SEPARATELY from FR-002, because the promise and the compatibility claim fail for different reasons |
| **FR-004** confined to the client edge | the wrapper, and nothing behind it | `git diff part4-ch22 --`: 0 lines in four subject files, 0 changed `subjectFor*` lines in the fifth, and no change to `internalSendRequestSchema.channel_id` |
| **FR-005** refused exactly as today | a value the map does not hold passes through verbatim | the api receives `order-nobody-has` unchanged; 068-2 is why the gateway does not refuse it itself |
| **FR-006** scoped, and demonstrated by deletion | `eq(users.environmentId, this.environmentId)` in `channelsForUser` | deleting it turns **1 of 85** red in the suite built for the question and **0 of 35** in the socket gauntlet — 065-4, fourth chapter running |
| **FR-007** mid-session membership | the fabric payload carries `channel_identity`; the map is filled before the send | `membership.itest.ts`'s add tests; the backstop's additions carry it too, which is how the defect was found |
| **FR-008** a clause says which | **FR-RTM-11**, written in Phase 3 before any code | `check:srs` 246 → 247, predicted at T003a |
| **FR-009** nothing else changes | — | SC-008's diff, at the close |
| **FR-010** amend what is falsified | SRS 1.30, ADR-38 in both homes, `docs/12`, `docs/07`, `docs/03` | and the two Part 2 transcript lines left deliberately (T049a) |

## Success criteria

| | met by | the number |
|---|---|---|
| **SC-001** every frame kind, per frame | `channel-naming.itest.ts` + the suites that own each kind | 7 fields and 3 structures; where each is asserted is in `baseline.txt`, Phase 4 |
| **SC-002** send both ways, typing both ways | two tests, deliberately separate | the api is handed `KEY` in both |
| **SC-003** the ack carries no Relay identifier | the wrapper re-keys `revisions`, `cursor`, `truncated` | `JSON.stringify(payload)` does not contain the key |
| **SC-004** nothing over a whole session | the sweep test | 3 kinds received, 0 keys |
| **SC-005** removing the scope turns a named test red | the probe | `repository.itest.ts > membership writes with foreign ids affect zero rows` |
| **SC-006** subjects and the send door unchanged | demonstrated, not asserted | T037's diffs |
| **SC-007** Journey 3 Stage 5 reachable by order number | the chapter, and 4.24 asserts it end to end | handed over at T071, with the webhook surface named |
| **SC-008** nothing outside the subject | — | at the close |
| **SC-009** the tutorial job's six steps | — | at the close |
| **SC-010** the CI error set, per error, both ways | — | at the close, against a baseline that is RED in `typing.itest.ts` |

## What is not discharged, and is written down instead

- **The webhook surface.** Three payload types in `outbox/event.ts` still carry
  `channel_id` as a Relay identifier. Named in SRS 1.30, ADR-38 in both homes,
  `docs/03` Stage 2 and `gaps.md`; it is nobody's chapter.
- **`typing.itest.ts`'s intermittent failure.** Five observations, four distinct
  test names, one signature. Pre-existing, measured in Phase 2, untouched here.
- **The coverage pins.** Not moved: the lane was red in eight suites unrelated to
  this chapter when the numbers were taken.

# Traceability — chapter 4.22, "The identifier the customer gave it"

Written by reading, not by grep. The last two sections are the ones a grep
cannot produce: what is in the feature with no requirement behind it, and what
was deliberately not amended.

---

## Requirements to evidence

| | where it is met | how it is verified |
|---|---|---|
| **FR-001** every public path route takes the identity | `channel-id.pipe.ts` at 13 `@Param` sites | `addressing.itest.ts`, per route rather than in aggregate |
| **FR-002** the Relay identifier still works | the same pipe; `resolveChannelId`'s uuid arm | the same 13 assertions with a uuid, and 998 api tests unedited |
| **FR-003** the order is defined, documented, tested | `resolveChannelId`'s `order by (external_id = $2) desc` | the constructed collision — 0 of 41,772 channels have a uuid-shaped identifier, so it is built or never tested |
| **FR-004** a refusal names the cause, no 5xx | the shape test; `UuidParamPipe` | 52 hostile inputs across 13 routes, plus the three `:messageId` routes |
| **FR-005** scoped, and demonstrated by removal | `this.environmentId` in `resolveChannelId` | T030: 18 red when deleted, restored byte-exact |
| **FR-006** sweep, count, dispose | `members[].user_id` removed | the sweep's table in `baseline.txt`; the assertion that the field is gone |
| **FR-007** old tokens keep working | nothing changed | no opaque token was altered, so the clause does not engage |
| **FR-008** the rule is written | **FR-CHN-11**, **ADR-38** in both homes | `check:srs` 245 → 246; the clause answers for a noun with and without an identifier |
| **FR-009** nothing else changes | — | 998 of 998 unedited; `git diff` reviewed at T059 |
| **FR-010** amend what measurement falsifies | SRS 1.29, ADR-37 ×2, Journey Stage 2, both Part 4 tables, two SAD schema comments, `media.controller.ts`'s comment | the gates, and the sweep that found ADR-37 wrong |

| | asserted by |
|---|---|
| **SC-001 / SC-002** 13 routes × 2 forms | `addressing.itest.ts`, one test per route per form |
| **SC-003** no 5xx in any path parameter | the hostile matrix, and the three `:messageId` routes |
| **SC-004** two tenants, same identifier | the foreign-channel pair, and the gauntlet's three new attacks |
| **SC-005** removing the scope turns a named test red | 18 of them |
| **SC-006** the count, stated | one removed, three kept with reasons |
| **SC-007** Journey 3 **Stage 2** | the `GET` that was a 500 and is a 200 |
| **SC-008 / SC-009 / SC-010** | T059, T054, T065 |
| **SC-011** the added cost, published | +0.615 ms, +12.8%, three runs a side |

## In the feature with no requirement behind it

**`UuidParamPipe` and the three `:messageId` sites.** No clause in this feature
asked for them. They are gap **058-3**'s remaining three routes, and the chapter
took them because it was already closing thirteen of the same sixteen and
editing the file all three live in. FR-004 and SC-003 were widened afterwards to
match what was built — **the requirement followed the work here, and saying so
is the point of this section.**

**`media/media.controller.ts`'s comment.** Repaired because this chapter made it
false, not because anything required it.

**`compose.yaml`'s `RELAY_NATS_REPLICAS: "1"`.** Outside the subject entirely and
FR-009 says there should be no such change. Without it the composed api cannot
create a stream, so the quickstart — NFR-USE-03's whole verification — cannot
run. 049-2 diagnosed this and set the override nowhere; the streams survived on
a volume for nineteen features and a `docker volume rm` exposed it.

**Three gauntlet attacks and a control.** Constitution I's cross-tenant suite is
named by constitution VI's third bullet as gating releases, which is a standing
obligation rather than this feature's requirement.

## Deliberately not amended

**FR-CHN-01 and FR-CHN-02.** Widening either to cover addressing would make a
creation clause carry a retrieval rule. FR-CHN-11 is new for that reason.

**ADR-18.** Still correct about users. ADR-38 extends rather than supersedes it,
because constitution VII makes an accepted ADR immutable.

**ADR-35, ADR-36.** Untouched; nothing here is about the audit log or retention.

**The internal doors.** `POST /internal/messages`, `/internal/backfill`,
`/internal/dispatch/*` name a channel in a body and keep the uuid.
`packages/protocol/src/internal.ts` states the position already.

**`docs/08-error-reference.md`.** `not_found` and `invalid_request` are both
registered with sections; no new code.

**ADR-37's placement.** Its heading was `##` inside section 6 and structurally
closed the Data view; demoted to `###` so it stops doing that. **Moving it to
sit with ADR-34, -35, -36 and -38 is 1,700 lines of published document for no
behavioural reason** and belongs to whoever next needs the ADR section to exist.

**The real-time surface.** Every gateway frame carries `channel: <uuid>`. Named
in FR-CHN-11, ADR-38, the contract, the quickstart and T050, and fixed nowhere.

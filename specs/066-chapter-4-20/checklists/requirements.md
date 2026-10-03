# Specification Quality Checklist: Chapter 4.20 — The messages that expire

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-03
**Feature**: [spec.md](../spec.md)

## Content Quality

- [X] No implementation details (languages, frameworks, APIs)
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders
- [X] All mandatory sections completed

## Requirement Completeness

- [X] No [NEEDS CLARIFICATION] markers remain
- [X] Requirements are testable and unambiguous
- [X] Success criteria are measurable
- [X] Success criteria are technology-agnostic (no implementation details)
- [X] All acceptance scenarios are defined
- [X] Edge cases are identified
- [X] Scope is clearly bounded
- [X] Dependencies and assumptions identified

## Feature Readiness

- [X] All functional requirements have clear acceptance criteria
- [X] User scenarios cover primary flows
- [X] Feature meets measurable outcomes defined in Success Criteria
- [X] No implementation details leak into specification

## What the premise check found, before a word of the spec was written

`docs/12` §7.5 asked chapter 4.19 to check its premise and four of five obligations turned
out already met. The habit transferred, and here it inverted: **none of FR-MOD-06's three
obligations is met, and the interesting one is refused by the database.**

| measured | |
|---|---|
| `environments.retention_days` | exists since chapter 2.1 — *"DECLARED IN 2.1 AND STILL EMPTY … read by nothing in seventeen chapters"* — and set on **0 of 33,051** environments |
| a scheduler | **none.** 0 `schedule:` triggers, no cron, no timer. ADR-28's precedent, and this would be the **fourth** clause bounded by the same absence |
| a hard delete of a message | **refused**, with a control: a message *with* a version row gives `message_edits_message_id_fkey`; a message *without* one gives `DELETE 1` |
| what references `messages` | **exactly one table**, `message_edits`, `NO ACTION`. So the FK is the only obstacle rather than one of several |
| messages blocked today | **5,495**, where chapter 4.19 measured 4,565 at its close and handed the number to row 22 |
| `media_objects` → `messages` | **no foreign key at all.** FR-MED-11's link is a `media_id` inside jsonb, so nothing in the database will cascade it and nothing will notice if it is wrong |
| the lane's oldest message | **19 days.** 0 messages older than 30, 90 or 365 days — the clause cannot be exercised at any of its four settings without a backdated fixture |

**THE CHAPTER IS THE OBSTACLE, NOT THE JOB.** Chapter 4.19 wrote the FK collision down,
declined to pre-solve it, and named row 22 as the chapter that would meet it. **Row 21 meets
it first** — and resolving it here means erasure inherits the resolution rather than repeating
the discovery.

## Analysis pass 1 — four findings, none CRITICAL, all fixed

**The question**: *do the files the artifacts cite say what they are cited as saying?* — the
mechanism with the best record as a first pass.

- **A1 HIGH — the ADR had no number.** `ADR-35` is the last in both homes, so this chapter's is
  **ADR-36**, and the plan said *"a new ADR"* six times without naming it. T045 could have been
  executed and produced a record the SRS, the SAD and `docs/12` have nothing to cite. Chapter
  4.18 named ADR-35 in its plan before writing a line of it. **Fixed in plan, tasks and
  research** — and the post-correction sweep found three more mentions after the first edit,
  which is the third feature running that the sweep has paid.
- **A2 MEDIUM — `api_keys.credential_hash` does not exist.** The columns are `id,
  environment_id, public_id, secret_hash, salt, prefix, name, created_at, last_used_at,
  revoked_at`. `quickstart.md` §2 queried it and would have failed before the chapter did
  anything. **Fixed** by taking the environment id from the seeder's own stderr line, which is
  the right source anyway, and the correction is in the preamble's list.
- **A3 MEDIUM — SC-012 had two halves and one task.** *"…published, **and re-measured at the
  close**."* T007 measures the refused count at the open and nothing re-measured it, on a
  number that moves **by one per deletion by construction** — the clearest case of 4.17's rule
  there has been. **Fixed** as T063a, publishing the pair rather than the later figure alone.
- **A4 LOW — the fence bill left one file uncounted.** `targets.ts` is **13 pages**, and the
  appendix already carries **4 hunks** for it, so the bill is five files. Counting it at
  analysis is what counting in phase 1 is for. **And it is the file where 4.12's rule bites**:
  its entries neighbour rows the appendix itself adds, so T026's hunk likely extends an
  existing one rather than adding one.

### Checked, and clean

```
no environments surface anywhere          the route is genuinely new
docs/07's Part 4 row 21                   exists — "The messages that expire"
src/retention/sweep.ts -> dist/retention/ the layout migrate.js already proves
nothing parses an environment response    no route, so no reader to break
```

**The last one is the risk 065 was bitten by, checked by type rather than assumed.** A required
field reaching a strict schema one seam away cost that chapter three red tests. Here the new
route creates a response shape **nothing yet parses** — `createEnvironment` is a fixture helper,
not a parsed contract — so the class does not apply.

**AND THE MECHANICAL COVERAGE MAP RAISED 18 ALARMS OF WHICH 17 WERE FALSE**, which is 4.11's
finding reproduced almost exactly (14 of 51 there). Every FR and SC except SC-012 is discharged
by a task that does not cite its number — FR-001 by T025, FR-006 by T028–T030, FR-009 by T035,
FR-012 by T042–T047. Recorded so a later pass does not re-walk them, and it is why
`traceability.md` is built by reading.

## Analysis pass 2 — four findings, none CRITICAL, all fixed

**The question**: *what do the queries nobody has written yet actually cost?* The sweep's
predicate and the media reverse-lookup were both described in prose and neither had been run.

- **B1 HIGH — there is no index on `messages.created_at`.** The table carries
  `messages_pkey`, `messages_channel_id_sequence_unique`, `messages_idem` and
  `messages_attachments_gin` — nothing for an age predicate, nothing for the order T020
  demands. **T020 said *keyset, not offset* with nothing to keyset on.** Fixed as a phase-2
  decision (T013a) with 4.1's treatment attached: measure the index before adding it, because
  that chapter added the one its query obviously needed and bought a gap inside the run-to-run
  spread for +49% storage.
- **B2 HIGH — the plan sketched the slow shape.** As a join across all environments the age
  bound lands in a `Join Filter`: **`Rows Removed by Join Filter: 1018`, 604 buffers** — every
  message in a policied environment fetched and discarded, each pass. Per environment with the
  bound as a constant it is **74 buffers** and reaches `channels_environment_last_activity`.
  **8×.** Fixed in `plan.md`'s Performance Goals, `data-model.md`'s sweep sketch, T013a and
  T020.
- **B3 MEDIUM — selecting the policied environments is a seq scan every pass**: 33,051 rows,
  **546 buffers, `Rows Removed by Filter: 33050`**. A partial index on `WHERE retention_days IS
  NOT NULL` would be nearly empty, because the column is 0-populated. Named in the risks and in
  T013a, with the same measure-first rule.
- **B4 MEDIUM — the two scales do not coincide on this lane.** The busiest *message*
  environment holds **1,018 messages and 0 media objects**; the busiest *media* environment
  holds **531 objects and 843 messages**. So an end-to-end sweep cost cannot be observed here
  even with backdated fixtures — it is a sum of two measurements, and T038 now says which half
  each figure came from.

### What this changed about the plan's own framing

The Performance Goals cited **883 against 94,132 buffers** for the media check and called it
*"the shape the sweep is written in rather than a figure to beat"*. That was a real measurement
of a real query — **and it is the second query the sweep runs.** The first one, the predicate
that decides which messages expire at all, had no measurement, and the shape the plan sketched
was the slow one.

**It is 4.12's error, caught earlier than 4.12 caught it.** That chapter published 26x-160x for
an index measured on a query its route did not send, and three analysis passes went by before
anybody asked what the planner would do with the shipped version. Here it was pass 2, before a
line of code.

### Checked, and clean

```
channels_environment_last_activity   exists, and the fast form reaches it
messages_attachments_gin             exists (4.12's), and R2's 883 figure uses it
the cascade's cost                   not separately measurable — the trigger refuses
                                     it today, so it is phase-3 work
```

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`
- **No `[NEEDS CLARIFICATION]` markers were raised.** The three decisions a reader might expect
  to be open — which column, whether to build a scheduler, and how to resolve the foreign key —
  are each settled by something already written down: the column exists and is named in two
  published documents; ADR-28 declined a scheduler for the same reason three times; and the FK
  resolution is a design question for `/speckit-plan` with the measurement already in hand.
  Recording them as assumptions with their evidence is more useful than asking.

# Traceability — chapter 4.21, "Erasure, and every path it must find"

Built by reading each requirement and finding the thing that discharges it, not by
grepping for identifiers. Chapter 4.11's pass 10 ran the mechanical version and got
**fourteen alarms, fourteen false**, which is why this file is written this way.

The ids below are **this feature's own**, local to `spec.md`. They are not SRS
clauses, and none of them reaches `docs/` — checked both ways at T048.

---

## The fourteen requirements

| # | what it asks | discharged by | evidence |
|---|---|---|---|
| FR-001 | an endpoint that erases an end user | `@Delete(":externalId/data")`, `users.controller.ts` | suite, 14 of 14 |
| FR-002 | profile, memberships, read positions | `Repository.eraseUser` | *"removes the user from every store that can remove them, counted absolutely"* |
| FR-003 | the user's unreferenced media objects | `destroyMediaObjects` + `deleteObjectWithRenditions` + a negative storage delta | receipt row, and `rendition.itest.ts`'s caller assertion |
| FR-004 | rows naming the user in every analytical store | `eraseFromAnalyticalStore` | the same test counts `connection_events` to 0 |
| FR-005 | say so where one user cannot be removed | `cannot_erase`, and `audit_log` is its member | *"tells the three silences apart"* |
| FR-006 | a receipt, per store | ten rows, five outcomes | `contracts/erasure.md`; the ClickHouse-stopped run in `baseline.txt` |
| FR-007 | re-runnable | **404 on the second call, and that is the finding** | *"answers 404 on the second erasure, which inverts the obvious answer"* |
| FR-008 | act only within the calling tenant | three arms, two of them tested after the probe | *"erases one tenant's user when two environments share the external id"*; the gauntlet attack |
| FR-009 | application credential only | `@Accepts("application")` at class level | *"refuses a user token"* — **written because the probe found nothing red** |
| FR-010 | distinguish *nothing to erase* from *cannot* | a set of three outcomes, asserted to have size 3 | *"tells the three silences apart"* |
| FR-011 | nothing outside the subject changes | T026's unedited suites, 223 + 39 | and T068's `git diff --name-only` at close |
| FR-012 | amend what measurement falsifies | SRS 1.28 · three clauses · three SAD sites · ADR-37 | `clauses.md` |
| FR-013 | an erasure writes an audit entry | `recordAction(ACTION.eraseUser)` | rows verified in Postgres: `target_kind = user`, no migration needed |
| FR-014 | caller-supplied values bound, not interpolated | `AnalyticalStore.query(sql, params)` | **red interpolated, green bound**, with the payload corrected |

---

## What is in the feature with no requirement behind it

A grep cannot produce this section.

- **The `retained_anonymous` outcome.** `spec.md` has fourteen requirements and none
  of them asks for a fifth receipt word. It exists because T010 and T011 were decided
  after the spec was written and the four existing outcomes could not say what happens
  to `messages` and `usage_active_users`.
- **ADR-37.** `plan.md` predicted *probably no ADR*. The decision it records did not
  exist when the plan was written.
- **`deleteUserRowRaw`.** A test helper with no requirement; it exists so a probe can
  demonstrate the foreign-key wall that the whole design rests on.
- **The `not_reached` note's two sentences.** A receipt saying *"the analytical store
  answered 0"* satisfies FR-006 and tells a compliance officer nothing. Found by
  running with the container stopped, not by reading the clause.
- **The deadline on the analytical client.** 3,000 ms, `reader.ts`'s value. No
  requirement asks for it; constitution III does.

## The clauses deliberately NOT amended, and why

- **FR-USR-05's *unless message deletion is explicitly requested*.** It would have been
  easy to read FR-MOD-04 as that request and amend nothing. The reading taken is the
  opposite one and both clauses now name the trade, so the decision is findable from
  either side rather than hidden in whichever clause somebody opens first.
- **There is no clause requiring usage history to survive a deletion**, and the receipt
  no longer pretends there is. `FR-029` is feature-local to the chapter that built
  `deleteUser` and resolves to nothing in `docs/04-srs.md`; the argument is a comment in
  that method, which is where it stays.
- **ADR-35 is not narrowed a second time.** `audit_log` could be made erasable the way
  `message_edits` was in chapter 4.20. A guarantee with two exceptions three chapters
  apart is a list, and `gaps.md` 067-1 carries the design if it is ever wanted.
- **FR-MOD-03 is not amended**, though it is the clause in tension with FR-MOD-04. Its
  `target` obligation is correct and the conflict is real; naming it in FR-MOD-04 and in
  the SAD puts it where a reader of either will meet it, without weakening the log.

## Requirements this chapter did NOT move, named rather than implied

- **FR-MOD-05**, the tenant export. Unbuilt, and it is the clause that would make an
  erasure survivable, because there is no undo. Third chapter running.
- **FR-MED-10's 24-hour orphan reaper.** Still has no caller; ADR-28's absence.
- **The 30-day bound.** Met at 53 ms and therefore unexercisable.

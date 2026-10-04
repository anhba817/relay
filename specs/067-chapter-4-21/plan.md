# Implementation Plan — chapter 4.21, "Erasure, and every path it must find"

**Feature**: 067 · **Spec**: [spec.md](./spec.md) · **Research**: [research.md](./research.md)
**Chapter**: 4.21, movement VII's fourth · `docs/12` row 22 · FR-MOD-04, FR-MED-10

## Summary

An endpoint that erases one end user, and a receipt that says what it could not
erase. The premise check came out mixed — FR-MED-10's unlink is already met,
FR-MOD-04's endpoint does not exist, and the phrase *analytical records* turns
out to be four stores with four different answers.

**The chapter's product is a receipt, not an endpoint.** The deletion itself is
ordinary. What is not ordinary is that one of the stores named in the clause
**cannot** remove one user by construction, another needs no erasure because the
column was never collected, and a third is kept on purpose by a built behaviour
with a billing argument behind it. A 204 would satisfy the clause's grammar and
tell a compliance officer nothing.

## Technical Context

**Language / runtime**: TypeScript, Node 22, NestJS api (unchanged)
**Stores touched**: Postgres (`users`, `members`, `read_positions`, `messages`,
`media_objects`, `usage_active_users`), ClickHouse (`connection_events`), the
object store (per-object `DELETE`)
**New surface**: one route, one repository path, one receipt shape. **No new module** —
`@Controller("v1/users")` already exists with the three decorators this route needs and
already holds FR-USR-05's deletion. Analysis pass 1 measured the alternative at 19 extra
fence pages, and colocation also puts the two `DELETE`s where a reader meets both at once
**No new dependency, no new service, no new table.**

**Performance**: the media half dominates, as chapter 4.20 measured — 2.05 ms an
object against 0.04 ms a message, because the object store has no foreign keys
and DR-15's prefix is tenant-scoped rather than user-scoped (R7).

**Constraints**: no breaking change to a published response (CON-05). The
erasure adds a route and changes no existing one.

## Constitution Check

| principle | verdict |
|---|---|
| **I — tenant isolation** | **engaged, and the failure mode is a LOSS rather than a leak** — the third chapter running where that inversion holds. An erasure scoped wrong destroys another tenant's user. The route resolves the external id within the caller's environment and the repository is constructed per environment; the probe must ask what SURVIVED, which is the form chapter 4.20 had to learn |
| **II — no acknowledged message is lost** | **ENGAGED, AND ADR-36 ALREADY DECIDED IT.** Bullet four reserves hard deletion for *the compliance path*, and FR-MOD-04's endpoint is the path that clause was written about — the one ADR-36 named first when it listed two. **No new ADR is needed for this half**, and saying so is the point: chapter 4.20 did the work |
| **III — two data paths** | **ENGAGED, AND THIS IS THE ONE THAT NEEDS AN ARGUMENT.** The principle keeps the operational and analytical paths independent, and an erasure must reach into both. See below |
| **IV — single writer** | satisfied by the predicate being self-clearing, as 4.20's sweep was: an erased user cannot match the next call, so a re-run needs no ledger |
| **V — API-first** | the erasure is a route, which is what the clause asks for. Unlike 4.20's sweep there is nothing here that cannot be a request |
| **VI — test-verified** | five bullets, answered below |
| **VII — boring by design** | no new service, no new dependency, no new table. **Whether it needs an ADR is the open question of this plan** — see below |

### Principle III in full, because an erasure crosses the fence the principle draws

III keeps two data paths independent so that a sick analytical pipeline cannot
stop a customer's messages. An erasure has to write to both, which looks like a
violation and is not — but the reason matters and is not obvious.

**The principle governs the SERVING path, not every write.** Chapter 4.7's
reconciler was the first thing to read both stores and ADR-06 records that the
cross-store read is *the mitigation that makes choosing NATS over Kafka
acceptable*. What III forbids is an operational request depending on the
analytical store being healthy.

**So the shape has to be: the operational erasure commits, and the analytical
erasure is attempted and REPORTED.** If ClickHouse is down, the user's profile,
memberships, messages and media are still erased and the receipt says the
analytical store was not reached. The alternative — rolling back a compliance
erasure because a metering pipeline is unwell — is the design failure III names
in as many words.

**THAT MAKES THE RECEIPT LOAD-BEARING RATHER THAN DECORATIVE**, which is the
argument for R5's shape and the reason this plan treats it as the product.

### Principle VI in full, because a row that answers one bullet reads as answering five

| bullet | verdict |
|---|---|
| stable identifiers, priority, verification method | met. 13 FR and 13 SC, `traceability.md` built by reading |
| **70% coverage; ordering, idempotency and tenant isolation at 100% branches** | **two of the three are this chapter's.** Tenant isolation is the external-id resolution and every per-store predicate, probed per arm. **Idempotency is FR-007** — the second erasure reports zero, counted absolutely |
| **the cross-tenant suite, dependency vulnerability scans AND the OWASP Top 10 scan gate releases** | **one of three met, and the other two do not exist** — `gaps.md` carries it from chapter 4.20, re-measured rather than copied. The gauntlet runs, and an erasure route is a new shape for it: the worst outcome on this surface is not a read |
| the quickstart runs unmodified, verified in CI | **UNMET, and not this chapter's.** No quickstart executes in `ci.yml`; the phase-9 task runs this one by hand |
| **input validated against a schema; UNKNOWN FIELDS REJECTED on write endpoints** | **NOT ENGAGED, and measured rather than assumed.** The route is a `DELETE` with one path parameter and **no body**, so there is nothing to validate and nothing for `z.strictObject` to be strict about — a bodyless `DELETE` answers identically with a junk body and with none. Chapter 4.20's route was a `PATCH` with a body and that sentence was carried across. **And `gaps.md` 058-3 is not engaged either**: its population is routes taking a **uuid-typed** path parameter, and this one takes a string external id. `DELETE /v1/users/no-such-xyz` answers 404, not 500, so the count stays at **twenty-three** |

### Does this need an ADR?

**Probably not, and the reason is worth stating rather than assuming.**
Constitution VII requires an ADR for *every architecture decision*, and this
chapter takes three that look like candidates:

- **Hard deletion on the compliance endpoint** — already licensed. ADR-36's
  first decision named two compliance paths and this is the one the clause was
  written about. Re-deciding it would be the mistake chapter 4.19's ninth
  analysis pass caught: editing an accepted ADR, which VII forbids.
- **Reaching into ClickHouse from an operational request** — argued above from
  III and ADR-06 rather than decided afresh. If the argument does not hold under
  analysis, this becomes an ADR.
- **What erasure means for a store that cannot erase** — this is the live one.
  If the answer is *report it*, that is a receipt design and belongs in the
  contract. **If the answer turns out to require amending FR-MOD-04**, it is an
  SRS amendment like chapter 4.20's, not an ADR.

**RECORDED AS OPEN.** Chapter 4.20's plan said *"Yes — ADR-36, with TWO
decisions"* and was right; saying *probably not* here without the analysis
passes having run is a prediction, and the one thing this project's record is
clear about is that predictions about what analysis will find are usually wrong.

## Phases

1. **Setup and measurement.** The lane and CI baselines with `Cached:` and
   elapsed beside each (chapter 4.20's finding), the six tutorial gates by name,
   the fence bill against the tree, and research R1–R7 re-read against the code.
2. **The decisions.** What the receipt attests, which stores are in scope, and
   whether `usage_active_users` is erased or kept — settled before any route
   exists.
3. **US1 — the erasure.** The route in the existing users controller, the per-store
   deletions, and
   the red probe first: assert what a user leaves behind today.
4. **US2 — the receipt.** Per store, per outcome, with the un-erasable one
   named. Asserted by reading the receipt alone.
5. **US3 — the bounds.** The thirty days, the 24-hour reaper, and a verdict per
   obligation.
6. **The probes.** Each tenancy arm alone and in combination; the receipt's
   claim against each store; the second erasure.
7. **The documents.** FR-MOD-04 and FR-MED-10 read before being edited, the SRS
   revision, `docs/12` row 22, both Part 4 tables.
8. **The chapter.** 2,000–4,000 prose words, the hunks, `check:fences` to zero.
9. **The record and the close.** Coverage pins after the chain is zeroed, and
   `check:fences` re-run after the pins go in.

## Complexity Tracking

| the simpler thing | why it is not taken | what it would cost |
|---|---|---|
| Return 204 and call it a receipt | the clause's least defined word, and the one store that cannot comply would be invisible | a compliance officer files a document that does not record the gap |
| `ON DELETE SET NULL` on `messages.user_id` | **measured and refused already**: the resume path drops a senderless row, so every message the user sent vanishes from every reconnecting client | a silent delivery defect, and reaching for a thing the platform rejected with evidence |
| Reuse `deleteUser` | it keeps the row, the messages and `usage_active_users` **on purpose** (FR-027/028/029), which is the opposite answer on three of them | the chapter's central conflict papered over by a function name |
| Erase the rollup sketches | a `uniq` state has no subtract operation; the only repair is recomputation from a source with 0 rows and a 90-day TTL | a claim the receipt cannot support |
| Skip ClickHouse when it is down | III's independence cuts the other way here: the operational erasure must not be rolled back, and the receipt is what carries the gap | either a blocked compliance erasure or a silent one |

## Risks

- **The receipt could become the chapter's whole subject and crowd out the
  erasure.** Mitigated by US1 shipping first and being independently testable.
- **`usage_active_users` is a decision with money on one side.** If it is kept,
  FR-MOD-04 is partly unmet and the SRS needs amending; if it is erased, a
  customer's March invoice loses its basis. Phase 2 decides it and the argument
  goes in `baseline.txt` either way.
- **The analytical half may be vacuous on this lane** — 0 rows in
  `message_events`, 0 distinct users in the sketches — so a green test proves
  less than it looks. Both numbers get published, which is chapter 4.19's rule
  about a boundary being two numbers.

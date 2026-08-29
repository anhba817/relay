# Traceability — chapter 3.19

**Built during planning, both ways, before any test is written.** Chapter 3.18's own instruction:
it ran the map the second way at close-out and found FR-007 — a MUST — with no test at all, after
eight phases and nineteen analysis passes had each read `requirement -> test` and believed it. The
map cost an hour and found something reading did not. Its answer changes what gets built, so it
belongs here.

**It already earned its place.** Three requirements did not exist until this map was built:

| Added | Because |
|---|---|
| **FR-027** | A presence frame must bypass the resume buffer and the backfill marks. Decided in research R10, carried by no requirement. |
| **FR-028** | Several closes inside one grace window must leave one decision. Listed as an edge case, carried by no requirement. |
| **FR-029** | No cross-kind mis-delivery. In the edge cases and in the fabric contract, and in no requirement. |

**And analysis pass 1 added two more, for the same reason in the other direction** — behaviour that
existed in the design and in no requirement:

| Added | Because |
|---|---|
| **FR-030** | The log vocabulary. `presence.suppressed` and `presence.invalid_payload` were in the lifecycle contract, implemented by tasks, mandated by nothing and asserted nowhere. |
| **FR-031** | The self-healing duplicate `online` after a lost key. Described in R11 and in the state machine, permitted by ADR-10, required or forbidden by no clause — so a later reader would delete it as a bug. |

---

## 1. SRS clause → feature requirement → verification

| SRS clause | Pri | Feature requirements | Verified by |
|---|---|---|---|
| **FR-RTM-05** (presence-change kind) | P1 | FR-001, FR-003, FR-004, FR-022 | integration: a `presence.changed` frame arrives. FR-022 by a task that **names** the five producer-less kinds in the chapter and the notes — chapter 3.18's spec claimed `typing` had no frame, which is what an unnamed list costs. |
| **FR-RTM-06** (`online`/`offline`, 30 s grace) | P1 | FR-003–FR-008, FR-027, FR-028 | integration for each transition; **unit for the 30_000 default**, so the number in the clause is asserted somewhere other than a constant. |
| **FR-RTM-07** (only users sharing a channel) | P1 | FR-010, FR-011, FR-012 (FR-013 retired) | integration, must-receive and must-not-receive in one run; the three-shared-channels case asserted **by count**. |
| **FR-CHN-05** (third verb: observe presence) | P1 | FR-014, FR-015 | integration: private non-member and cross-tenant receive nothing. FR-015 by the **existing** `isolation.itest.ts`. |
| **FR-RTM-10** | P1 | FR-020, FR-020a, FR-020b, FR-021 | **NOT MET, deliberately.** The gateway test that asserts the violation keeps asserting it. Decision and reason in `plan.md`. |
| **FR-RTM-09** | P2 | — | Untouched. This chapter counts connections per user and enforces no cap. `docs/05-sad.md:574`'s key is not built (research R6). |
| **NFR-OBS-01** | — | FR-024, FR-025 | integration: the log events exist, with the named fields and no content. |
| **NFR-MNT-02** | — | FR-032 | `pnpm coverage`. Presence is the tenant-isolation class; the pin is 100% branches and the classification is recorded in `plan.md`, not left to the run. |
| **ADR-05** (gateway has no database) | — | FR-009 | chapter 2.1's lint ban — a violation is a build failure, not a review comment. |
| **ADR-10** | — | FR-016, FR-016a, FR-016b, FR-026 | inspection + grep. FR-026 by a test: a transition adds no outbox row. |

---

## 2. Feature requirement → verification (the direction everybody reads)

| FR | Verification | Kind |
|---|---|---|
| FR-001 | the chapter and this map cite four clauses | inspection |
| FR-002 | `git diff docs/04-srs.md` touches Appendix C and no clause row | **command** |
| FR-002a | same diff shows the appendix row changed | **command** |
| FR-003 | first connection anywhere → one `online` | integration |
| FR-004 | last close → one `offline`, not before `graceMs`; the default is 30_000; **and the check is armed after the re-pin resolves, at `graceMs + marginMs`** — equal deadlines strand the user online permanently (R2b) | integration + unit |
| FR-005 | a connection open on another instance suppresses it | integration, two instances |
| FR-006 | second connection → nothing; one of two closes → nothing | integration, **by count** |
| FR-007 | reconnect inside the window → nothing at all | integration |
| FR-008 | `targets.ts` gains no route, and FR-015's refusal holds | **derived route list** + integration |
| FR-009 | the gateway imports no pg/drizzle/repository | **lint, build failure** |
| FR-010 | co-member receives, non-sharer does not, **in the same run** — absorbed FR-013's method in pass 11 | integration |
| FR-011 | the subject's own socket receives its own transition | integration |
| FR-012 | three shared channels → exactly one frame | integration, **by count** |
| FR-013 | **retired in pass 11** — one constraint in two polarities; folded into FR-010, id not reused | — |
| FR-014 | private non-member and cross-tenant receive nothing | integration |
| FR-015 | **already tested** — `isolation.itest.ts`, nine sockets, one per outbound frame | existing integration |
| FR-016 | all five positions agree — `docs/04-srs.md:903`, `docs/05-sad.md:899`, `docs/05-sad.md:210`, **`docs/06-adr-deep-dives.md:633` and `:651`** | grep |
| FR-016a | the closure names ADR-10 and the undischarged trigger, in the SRS row and in the deep dive | inspection |
| FR-016c | the closure names NFR-SCL-01, the other clause Appendix C row 3 blocks | grep |
| FR-016b | `docs/05-sad.md:210` no longer points at an open question | grep |
| FR-034 | ADR-19 exists and supersedes; ADR-10's decision text is byte-identical except its `**Status:**` line | **`git diff docs/05-sad.md`** |
| FR-017 | the SAD records the fabric that ships, in ADR-19 — **in `docs/05-sad.md` and in `docs/06-adr-deep-dives.md`'s Decision paragraph, which carries the same sentence** | inspection |
| FR-018 | the 3.19 row names FR-RTM-07 and FR-CHN-05 | grep |
| FR-019 | `pnpm check:docs` green after `pnpm sync:docs`, for the three published documents this feature amends | **command** |
| FR-019a | `docs/07-tutorial-plan.md` absent from `sync-docs.sh`'s list and from `content/docs/` | **command** |
| FR-020 | `gaps.md` records FR-RTM-10 unmet with the corrected premise | inspection |
| FR-020a | `plan.md` states the decision and its reason | inspection |
| FR-020b | the default was not silently exercised — the reason is written | inspection |
| FR-021 | the join-while-connected staleness is a sentence in the chapter | **inspection only — no checker reads prose** |
| FR-022 | the five producer-less kinds named; the union still has ten members | inspection + existing totality test |
| FR-023 | Redis down: socket opens, messages deliver | integration |
| FR-024 | Redis down: one `presence.failed` event, **and the next transition publishes after restore** | integration |
| FR-025 | each publish logged with `user`, `state`, `channels` count; no content, no token | integration |
| FR-026 | a transition adds no outbox row and no JetStream publish | integration |
| FR-027 | a transition during a resume arrives, and is not in the buffer | integration |
| FR-028 | close/reopen/close inside one window → one `offline`, once | integration |
| FR-029 | no message arrives as presence and no presence as a message | integration + topology (R1) |
| FR-030 | `presence.suppressed` and `presence.invalid_payload` fire and are asserted; the other two are FR-024's and FR-025's | integration |
| FR-031 | the duplicate `online` after a lost key is permitted and bounded to that cause | inspection + the implementation's own comment |
| FR-032 | both `presence.ts` files at 100/100/100/100 — NFR-MNT-02's tenant-isolation class | **`pnpm coverage`** |
| FR-033 | the four published claims no longer say what this design contradicts, in both locales | **`check-prose.py`** + a reader for the replacements |
| FR-033a | one fragment per claim per locale, and the checker green | **`check-prose.py`** |

**Every FR has a verification. Three have one that no command can run** — FR-001, FR-021 and the
inspection rows. FR-021 is the sharp one: it is a claim in prose, and no checker in this repository
reads prose. A published Trap contradicted chapter 3.17's own chapter through fifteen analysis
passes for exactly this reason.

---

## 2a. Success criterion → requirement

**Added in analysis pass 11.** All 41 requirements were traced and **none of the 14 success criteria
were** — and `check-refs.py` enforced the requirement half only, because requirements were what this
map already held. Passes 1 through 9 mapped the criteria to tasks by hand in analysis reports, which
is not a place a mapping survives a task being renamed.

**Mapped to requirements, not to tasks, and that was the checker's doing.** The first version of this
section was an SC → task table, and `check-refs.py` rejected it: fourteen task ids outside
`tasks.md`, which is the rule pass 4 added after three renumbers left stale references behind — one
of them citing, as evidence, the very test that disproved its paragraph. Requirements are stable
identifiers; task numbers are positions. So the criteria attach to requirements, and the requirement
rows above carry the tasks.

| SC | Rests on | Where no requirement carries it |
|---|---|---|
| SC-001 | FR-003, FR-010 | — |
| SC-002 | FR-003, FR-005 | — |
| SC-003 | FR-012 | — |
| SC-004 | FR-006 | — |
| SC-005 | FR-004 | the **measured** upper bound: an observed close-to-`offline` delay recorded in `baseline.txt`, which no requirement asks for |
| SC-006 | FR-005, FR-007 | — |
| SC-007 | FR-010, FR-014 | — |
| SC-008 | FR-015, FR-022 | — |
| SC-009 | FR-023, FR-024 | — |
| SC-010 | FR-016, FR-016a, FR-016b, FR-016c | — |
| SC-011 | FR-001, FR-018 | the map itself, re-derived both ways from the shipped tree |
| SC-012 | FR-020, FR-020a, FR-020b | running the gateway's FR-RTM-10 test rather than asserting its state |
| SC-013 | FR-021, FR-033 | the 2,000–4,000 prose-word bound, the fence chain replaying from `caeabc9`, and both locales routing with the static-page count at 93 |
| SC-014 | — | the lane green inside its 240 s budget, with the count read after the ANSI codes are stripped |

**Four criteria carry obligations no requirement states**, and SC-014 carries nothing else. That is
worth seeing rather than hiding behind a task number: a success criterion with no requirement behind
it is a promise the traceability map cannot check, and the right of the table is the honest list of
them.

---

## 3. Planned test → requirement (the direction that finds things)

Read this column first and ask of each row: **what would have to be false for this to fail?**

| Planned test | Requirement | What its failure would mean |
|---|---|---|
| a watcher receives `online` when a co-member connects | FR-003, FR-010 | the producer does not exist — this is phase 1's red test |
| the same across two gateway instances | FR-003, FR-005 | presence is instance-local, the split brain of chapter 2.6 |
| a second connection produces no frame | FR-006 | the NX guard is not doing the guarding |
| three shared channels produce one frame | FR-012 | the transition id is not deduplicating |
| `offline` arrives after `graceMs`, not before | FR-004 | the grace period is not a grace period |
| **the production default is 30_000** | FR-004 | somebody changed the clause's number in a constant |
| reconnect at half the window → nothing, to anybody | FR-007 | the check reads the wrong state, or reads it too early |
| reconnect to a **different** instance → nothing | FR-005, FR-007 | the TTL is not the cross-instance signal it is claimed to be |
| close/reopen/close in one window → one `offline` | FR-028 | two timers were left pending |
| **swapping `registry.remove` and `presence.disconnected` fails** | FR-004, FR-005 | the ordering is a comment and not a property. With the order reversed the local count is 1, no check is scheduled, and the user never goes offline |
| non-sharer receives nothing while co-member receives | FR-010 | the scoping is absent, or the producer is dead and the test cannot tell |
| private non-member, cross-tenant | FR-014 | principle I |
| a client uttering `presence.changed` is refused | FR-015 | *(already green — cited, not written)* |
| a transition during a resume arrives and is not buffered | FR-027 | presence went through the message path's buffer |
| Redis down: socket opens, messages deliver | FR-023 | presence is load-bearing, which it must not be |
| Redis down: `presence.failed` logged; **restored: next transition publishes** | FR-024 | the path does nothing and every other failure test passes anyway |
| a transition writes no outbox row | FR-026 | presence acquired durability |
| the re-pin is awaited and the check armed at `graceMs + marginMs` | FR-004 | the two deadlines are equal and a prompt timer suppresses the only `offline` there will ever be |
| twenty sockets close in one tick, twenty `offline` frames | FR-004, FR-028 | the `pending` map does not survive a deploy drain |
| five connections close one by one | FR-005, FR-006 | the reference count works at two and not at five |
| the union still has ten members, each classified once | FR-022 | a frame was added or reclassified without a decision |

**Three rows exist only because the reverse reading demanded them** — the swap test, the resume
test and the close/reopen/close test. None appears in the spec's user stories; all three defend a
mechanism the design depends on.

---

## 4. Requirements with no test, listed rather than absent

| FR | Why not | Who could |
|---|---|---|
| FR-001, FR-016a, FR-017, FR-020–FR-020b | claims about documents and records | a reader |
| ~~FR-033~~ | **left this list in analysis pass 9** — `check-prose.py` turned it from inspection into a command, and only the quality of the replacement prose still needs a reader | a command, plus a reader |
| **FR-021** | a claim in chapter prose | **a person; chapter 3.18's `gaps.md` item 6, now on its sixth chapter** |

Nothing on this list is a MUST about platform behaviour. That was the check worth running, and it
is the check chapter 3.18 could not pass at this stage.

**Two entries left this list in analysis pass 1**, having been on it wrongly: **FR-009** (the
gateway reads no database) was recorded as verified by chapter 2.1's lint ban with no task running
it, and **FR-022** (the producer-less kinds named) had no task at all. Both now have one. A
requirement verified by "a rule exists somewhere" is a requirement nobody checked.

---

## 5. Re-derived from the shipped tree at close-out — both directions again

**The second run is the one that catches a test renamed or deleted**, and it caught three
things the planning map could not have.

### Shipped

    packages/protocol/src/presence.test.ts        6 unit
    services/gateway/src/presence.test.ts         8 unit
    services/gateway/src/presence.itest.ts       38 integration   (31 + 7 added at close-out)
    services/gateway/src/isolation.itest.ts       1 cited, not written
                                                 -----
                                                 53 tests carrying this feature

### Every planned row, checked against a title in the tree

Twenty-one planned rows in §3. **Nineteen exist. One shipped at a different size. One does
not exist and is named rather than quietly dropped.**

| Planned | Shipped as |
|---|---|
| a watcher receives `online` when a co-member connects | *delivers presence.changed online to a connected co-member* |
| the same across two instances | *delivers it when the subject is on another instance* |
| a second connection produces no frame | *publishes nothing for a second connection of a user already online* |
| three shared channels produce one frame | *delivers ONE frame to a watcher sharing three channels* |
| `offline` after `graceMs`, not before | *publishes one offline after the window and nothing before it* |
| the production default is 30_000 | *keeps FR-RTM-06's thirty seconds somewhere a reader can find it* |
| reconnect at half the window → nothing | *publishes nothing at all for a reconnection inside the window* |
| reconnect to a different instance → nothing | *publishes nothing when the reconnection lands on another instance* |
| close/reopen/close → one `offline` | *leaves one decision for two closes inside one window* |
| non-sharer receives nothing while co-member receives | *delivers to a co-member and not to a user sharing no channel* |
| private non-member, cross-tenant | *does not let a non-member observe presence in a private channel*, *delivers nothing to a user of another tenant* |
| a client uttering `presence.changed` is refused | `isolation.itest.ts`'s `DIRECTIONS` row — cited, unchanged |
| a transition during a resume | *delivers a transition to a connection that is resuming* |
| Redis down: socket opens, messages deliver | *opens the socket and completes the handshake anyway*, *does not stop messages reaching a connected member* |
| Redis down then restored | *logs presence.failed with an op and an error*, *publishes the next transition after the connection is restored* |
| no outbox row | *writes no outbox row for a transition* |
| the re-pin awaited, check at `graceMs + marginMs` | *is the grace plus the margin, never the grace alone* (unit) and *holds the key for the grace, not for the TTL* (integration) |
| five connections close one by one | *publishes nothing until the fifth of five connections closes* |
| the union still has ten members | `isolation.itest.ts`'s `DIRECTIONS`, ten rows |

**The one that shipped smaller.** The planned row reads *"twenty sockets close in one tick,
twenty `offline` frames"*; the shipped test is *"publishes one offline per user when six
close in the same tick"*. Six, not twenty — trimmed while cutting the file from 65.4 s to
32.6 s. The mechanism it defends is the `pending` map surviving a deploy drain, and six
users across two instances exercises it; twenty exercised the same thing more slowly. The
number in the plan was never a requirement, and this row is here so that nobody reads the
plan later and believes twenty ran.

**The one that does not exist.** *"Swapping `registry.remove` and `presence.disconnected`
fails"* has no test and never will in this form: a test cannot swap two lines of production
code. What ships in its place is the ordering assertion — the grace check IS scheduled on
the last close — plus a comment at the call site stating the constraint and its cost. The
task was left open deliberately rather than marked done, and this row is its record.

### Shipped tests with no planned row — the direction that found the most

Twelve of the 38 integration tests answer to no row in §3. Two classes:

**Behaviour the design had and the plan did not enumerate.** *Delivers the subject's own
transition to the subject's own socket* (FR-011); *publishes to nobody for a subject who is
a member of no channel* — FR-RTM-07's degenerate case, and the one that explained an
`INFO commandstats` reading of seven election wins against six publishes; *publishes
nothing while another connection remains open*, and its cross-instance twin; *publishes no
second online when the reconnect lands past the TTL* (FR-007, research R2a); *closes a
socket without throwing or leaving a rejection*; and the three log-vocabulary assertions
that FR-030 was written in analysis pass 1 to require.

**Seven written at close-out for coverage**, listed in `baseline.txt` with the arm each
closes. They are not scenarios a user performs, and one of them replaced a test whose title
claimed an arm it never touched.

### What the second pass changed in this map

Nothing about requirement coverage — every FR still has a verification and the four
inspection-only rows are the same four. What it changed is the honesty of §3: two of its
twenty-one rows described a test that is not in the tree, and both were readable as done.

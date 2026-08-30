# Traceability — chapter 3.20

**Built during planning, both ways, before any test is written.** Chapter 3.18's own
instruction: it ran the map the second way at close-out and found FR-007 — a MUST — with no
test at all, after eight phases and nineteen analysis passes had each read
`requirement → test` and believed it.

**It earned its place before the file was finished.** Mapping the requirements against the
task list found **five with no task at all**, and every one of them is a requirement whose
verification is a sentence rather than a test:

| Orphan | What was missing | Now carried by |
|---|---|---|
| **FR-002a** | the Appendix C decision. A task verified no *clause* changed and nothing recorded the appendix answer either way | the SRS-diff task, widened |
| **FR-003** | *"name the remaining three kinds"*. The chapter task named FR-WHK-02's gap and not FR-RTM-05's | the chapter's discoveries task |
| **FR-018** | typing named as out, with the reason it can reuse the fan-out | the same |
| **FR-019** | FR-RTM-09's cap named as out, with `conn:{env}:{user}`'s defect as the reason | the same |
| **FR-020** | `message.updated` and `message.deleted` named as out | the same |
| **FR-017** | *"state which and why"*. A task revived the schema; none recorded the reason | the revival task, widened |

Six requirements, one pass, before any code. The common shape is worth naming: **a
requirement satisfied by prose is the kind a task list forgets**, because a task list is
written by thinking about what to build.

---

## 1. SRS clause → feature requirement → verification

| SRS clause | Pri | Feature requirements | Verified by |
|---|---|---|---|
| **FR-RTM-10** (5-second revocation) | P1 | FR-008, FR-012, FR-013, FR-014, FR-014a, FR-021, **FR-029**, **FR-030** | integration, waiting the clause's own budget; **and the inverted test in `session.itest.ts`**, which is the one a reader will check |
| **FR-RTM-05** (membership change, of six kinds) | P1 | FR-003, FR-004, FR-005, FR-006, FR-009, FR-010 | integration for the producer; FR-003 by a task that **names** the three kinds still without one |
| **FR-RTM-01** (a member receives their channels' messages) | P1 | FR-010 | integration: a channel joined mid-connection delivers |
| **FR-WHK-02** (event type vocabulary) | P2 | — | **not met, and not claimed.** Two of eight names gain outbox rows; five are missing and no endpoint subscribes. The rows exist because constitution II requires them for the publish this chapter makes |
| **FR-RTM-08** (typing) | P2 | FR-018 | **out**, named in the chapter with its reason |
| **FR-RTM-09** (5 concurrent connections) | P2 | FR-019 | **out**, named with `conn:{env}:{user}`'s defect as the reason |
| **NFR-MNT-02** (100% branches for isolation code) | — | FR-027 | `pnpm coverage`. Membership decides who may hear what; the classification is in `plan.md`, not left to the run |
| **NFR-OBS-01** (structured observability) | — | FR-015, **FR-031**, **FR-032** | integration: three log names, each reached by a test. FR-031 is the one the first eight passes had no counterpart for — every log requirement here was about failure |
| **NFR-SCL-01** (10k connections/instance) | — | — | **undischarged.** The backstop's interval is priced against it and nothing here measures at that scale |
| **Constitution II** | — | FR-016 | the outbox row inside the transaction, proven by a test that fails the write after the insert |
| **Constitution IV** | — | FR-014, FR-014a | the backstop, and an honest verdict if no interval is affordable |
| **ADR-05** (gateway has no database) | — | — | chapter 2.1's lint ban. The re-read is an HTTP call, not a query |

---

## 2. Feature requirement → verification

| FR | Verification | Kind |
|---|---|---|
| FR-001 | the chapter and this map cite four clauses | inspection |
| FR-002 | `git diff docs/04-srs.md` touches no clause row | **command** |
| FR-002a | the Appendix C answer is recorded either way | inspection |
| FR-003 | three of six kinds have producers; the other three named | integration + inspection |
| FR-004 | every writer publishes — add, remove, join, ban | integration, one per path |
| FR-005 | an idempotent no-op writes no row and publishes nothing | integration, **by count** |
| FR-006 | a role change produces no row and no frame | integration, both halves |
| FR-007 | a change whose environment does not match is refused and logged | integration |
| FR-008 | the frame precedes the cut-off, asserted **in arrival order** | integration + a swap that must fail |
| FR-009 | a remaining member gets one frame per removed user | integration, **by count** |
| FR-010 | an added user receives, and their presence is observed | integration |
| FR-011 | non-sharer and cross-tenant receive nothing **in a run where a member does** | integration |
| FR-012 | cross-instance, and two sockets for one user | integration, two instances |
| FR-013 | the socket stays open, no close code, no error frame | integration |
| FR-029 | a removal mid-resume drops that channel's buffered frames, so the flush cannot deliver them | integration, **the assertion that fails against an implementation passing FR-008's** |
| FR-030 | the notice arrives during a resume rather than after it — the frame's own path reads neither `phase` nor `marks` | integration, and the mirror of FR-029: one stops the messages, the other stops the notice joining them |
| FR-014 | the fabric decision and the cost of a drop are recorded | inspection |
| FR-014a | the backstop corrects a severed publish within one interval | integration, TCP proxy |
| FR-015 | one `membership.failed` event with an op | integration |
| FR-016 | a failed publish cannot fail the write; the row survives | integration |
| FR-031 | a successful publish is logged with channel, external id, no content, no token | unit + integration |
| FR-032 | all three log names reached by a test; nothing else emitted from this path | integration |
| FR-033 | no frame arrives as the wrong kind, across all four subject shapes | integration + topology |
| FR-017 | the schema is revived or deleted, and the reason recorded | inspection |
| FR-017a | the signup fixture's **assertion** is read before the route lands | inspection + the api lane |
| FR-018, FR-019, FR-020 | each named in the chapter with its reason | **inspection only — no checker reads prose** |
| FR-021 | the FR-RTM-10 test asserts the clause, keeping its 5,500 ms wait | **command** |
| FR-022 | chapter 3.19's `gaps.md` item 2 closed by name, and the presence half tested | integration + inspection |
| FR-023 | the 3.20 row exists and the Part 3 header is re-derived | grep |
| FR-024 | `pnpm check:docs` green after `pnpm sync:docs` | **command** |
| FR-025 | the architecture decision is recorded either way | inspection |
| FR-026 | the contradicted claims are gone from both locales | **`check-prose.py`** + a reader |
| FR-027 | every new production file at 100/100/100/100 | **`pnpm coverage`** |
| FR-028 | chapter 3.19's items carried with status, each naming its chapter | **`check-refs.py`** + inspection |

**Six requirements have a verification no command can run** — FR-001, FR-002a, FR-014,
FR-017, FR-025 and the FR-018/019/020 group. Five of the six are *decisions recorded*,
which is the shape this chapter has more of than its predecessors, because two
constitutional gates pass conditionally.

---

## 2a. Success criterion → requirement

| SC | Rests on | Where no requirement carries it |
|---|---|---|
| SC-001 | FR-008, FR-012 | — |
| SC-002 | FR-008 | — |
| SC-003 | FR-010 | — |
| SC-004 | FR-010, FR-022 | — |
| SC-005 | FR-008 | the **ordering**, asserted in arrival order, which FR-008 states and no test would check by default |
| SC-006 | FR-009 | — |
| SC-007 | FR-011 | — |
| SC-008 | FR-004 | — |
| SC-009 | FR-014a, FR-015, FR-016 | — |
| SC-010 | FR-021 | — |
| SC-011 | FR-003 | — |
| SC-012 | — | **the map itself**, re-derived both ways from the shipped tree |
| SC-013 | FR-026 | the 2,000–4,000 word bound, the fence chain from `d38f415`, and both locales routing |
| SC-014 | — | the lane inside 240 s, counted with the colour codes stripped, **and the gateway package's own clock** |
| SC-015 | FR-029, FR-030 | — (US1 scenario 7 is the journey behind it, added at pass 11) |
| SC-016 | FR-031, FR-032 | — |
| SC-017 | FR-033 | — |

**Three criteria carry obligations no requirement states**, and SC-012 and SC-014 carry
nothing else. The last three carry the opposite problem, resolved: **they exist because four
requirements did not** — the list was frozen at spec time and eight passes of requirement growth
went past it. That is worth seeing rather than hiding: a success criterion with no
requirement behind it is a promise this map cannot check.

---

## 3. Planned test → requirement (the direction that finds things)

Read this column first and ask of each row: **what would have to be false for this to
fail?**

| Planned test | Requirement | What its failure would mean |
|---|---|---|
| a removed member gets one frame and then nothing | FR-008 | the revocation does not happen — the clause is still unmet |
| **a removal mid-resume flushes nothing for that channel** | FR-029 | the buffer is a second delivery path nobody filtered, and FR-RTM-10 is violated by a flush rather than by a subscription |
| **the notice arrives during the resume, not after it** | FR-030 | the frame went into the buffer it was announcing the filtering of — so it lands after the cut-off, or FR-029 drops it and it never lands |
| **a second local member of the same channel still receives** | FR-009 | the unsubscribe released a channel instead of decrementing it. **The obvious test passes against that bug** |
| the frame precedes the last message, in arrival order | FR-008 | cut-then-send, and the notice itself violates the clause it announces |
| the removed user's other channel still delivers | FR-008 | the socket broke rather than the membership |
| the socket stays open, no close code | FR-013 | a revocation became a disconnection |
| both sockets of a two-instance user stop | FR-012 | the fabric is instance-local, chapter 2.6's split brain again |
| a remaining member gets one frame per removed user | FR-009 | bulk removals coalesce, or the dedup is missing |
| a member sharing three channels gets one frame | FR-009 | delivery is per subscription rather than per connection |
| a non-sharer and a cross-tenant user get nothing **in a run where a member does** | FR-011 | scoping is absent — or the producer is dead and the test cannot tell |
| **a message, a presence transition and a membership change over three channels each arrive once, under their own type** | FR-033 | four subject shapes share one Redis and the topology stopped keeping them apart |
| **a working change logs `membership.published`** | FR-031 | the mechanism can be seen failing and never seen working |
| a role change produces no row and no frame | FR-006 | the enum grew a third meaning nobody decided |
| an added user receives the channel's next message | FR-010 | the user-addressed subject is not reaching a non-subscribed instance |
| the added user's presence is observed by that channel | FR-022 | chapter 3.19's staleness is not closed, only claimed |
| an idempotent re-add publishes nothing | FR-005 | every retry fires a frame and a webhook |
| the write fails after the outbox insert; **neither survives** | FR-016 | the row is written beside the transaction, not inside it, and every other outbox test still passes |
| Redis down: the route answers, the row is written, one line logged | FR-015 | the publisher does nothing and two of the three assertions cannot tell |
| the backstop corrects a severed publish within one interval | FR-014a | constitution IV's recovery property is not preserved |
| the re-read is a no-op when nothing changed, **by request count** | FR-014a | the backstop is re-applying a diff it should not have |
| swapping send-and-delete makes a test fail | FR-008 | the ordering is a comment, not a property |
| swapping subscribe-and-insert makes a test fail | FR-010 | the window is open and the loss is silent |

**Five rows exist only because a reading demanded them** — the second-local-member test, the
arrival-order assertion, the transaction-failure test, the two swaps, and the mid-resume flush.
None appears in the spec's user stories; each defends a mechanism the design depends on.

**The two mid-resume rows came last and from two different questions.** FR-029's came from
reading the edge cases against the tasks (pass 3); FR-030's from asking what chapter 3.19's FR-027
corresponds to here (pass 7). **3.19 needed both halves and wrote both**; this map had one for four
passes, and the missing half is the kind that only shows up when a predecessor's requirement list
is read as a checklist rather than as prose.

 Passes 1 and 2 read the tasks
against the code. Pass 3 read the *scenarios and edge cases* against the tasks, and found the one
path all five documents mention exactly once: `session.ts:632` flushes
`flushable(connection.buffer, marks)`, which filters on `frame.seq` and not on membership. The
edge-case list asked the question in one line and nothing followed it up.

---

## 4. Requirements with no test, listed rather than absent

| FR | Why not | Who could |
|---|---|---|
| FR-001, FR-002a, FR-014, FR-017, FR-025 | claims about documents and decisions | a reader |
| **FR-018, FR-019, FR-020** | claims in chapter prose about what was *not* built | **a person; chapter 3.18's `gaps.md` item 6, on its seventh chapter** |
| FR-026 | half a command — `check-prose.py` proves a sentence is gone, never that its replacement is right | a command, plus a reader |

Nothing on this list is a MUST about platform behaviour. That was the check worth running.

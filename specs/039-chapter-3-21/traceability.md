# Traceability — chapter 3.21

**Built during planning, both ways, before any test is written.** Chapter 3.18 ran the map
the second way at close-out and found FR-007 — a MUST — with no test at all, after eight
phases and nineteen analysis passes had each read `requirement → test` and believed it.
Chapter 3.20 did the same and found a requirement whose planned test was not in the tree.

**It earned its place before this file was finished.** Mapping requirements against the
task list found **three with no task**, and all three are the shape a task list forgets: a
requirement whose verification is a sentence rather than a test.

| Orphan | What was missing | Now carried by |
|---|---|---|
| **FR-019** | *no SRS clause may change* — a task verified the diff, none said what to do if it were non-empty | the SRS-diff task, widened to record the mismatch rather than edit |
| **FR-020** | *state which of the six kinds have producers* — the chapter task named the grammar decision and not the count | the chapter's discoveries task |
| **FR-021** | *state that the fourth grammar was taken rather than avoided* — nothing recorded that the plan assumed the opposite | the same |

---

## 1. SRS clause → feature requirement → verification

| SRS clause | Pri | Feature requirements | Verified by |
|---|---|---|---|
| FR-RTM-08 | P2 | FR-009, FR-009a, FR-009b, FR-009c, FR-010, FR-011, FR-012, FR-013 | integration + arithmetic, **and a recorded verdict**: the platform's half is met, the expiry itself is the client's, and the clause says the system *shall* |
| FR-RTM-05 | P1 | FR-001, FR-004, FR-008, FR-020 | integration, and a count stated in prose |
| FR-RTM-01 | P1 | FR-004, FR-007 | integration, cross-instance |
| FR-RTL-01 | P1 | FR-011, FR-012, FR-013, FR-014 | integration, **by count** |
| NFR-SCL-01 | — | FR-011 | arithmetic, not a measurement — the lane cannot see 10,000 connections |
| NFR-OBS-01 | — | FR-015, FR-016 | integration, asserting the emitted set |
| NFR-MNT-02 | — | the coverage pins | `pnpm coverage`, 100/100/100/100 |
| EIR-WS-06 | — | FR-002, FR-003 | integration, driven from the union |

**No SRS clause changes** (FR-019). Research R10 read them rather than enumerating them;
`git diff docs/04-srs.md` verifies it at the end, because expected is not verified.

---

## 2. Feature requirement → verification

| FR | Verification | Kind |
|---|---|---|
| FR-001 | a client's signal is accepted and the socket stays open | integration |
| FR-002 | the inbound type differs from `typing`; the gauntlet still calls `typing` outbound | integration + inspection |
| FR-003 | `INBOUND_FRAME_TYPES` has exactly two members, asserted as a set and a size | unit |
| FR-004 | a member on another instance receives one frame | integration, cross-instance |
| FR-004a | a member added mid-connection receives a typing frame without reconnecting | integration |
| FR-005 | the signaller receives none, in a run where another member does — **and their own second connection receives none either**, in the two-connection topology FR-011a already requires | integration |
| FR-006 | the delivered `user` is the connection's identity, never the payload's | integration + a schema with no `user` |
| FR-007 | a foreign channel publishes nothing, asserted on a **subscriber** | integration |
| FR-008 | `git diff` on `frames.ts` shows additions only, no `typingSchema` removal | **command** |
| FR-009 | no frame is sent to end an indicator | integration, by absence + inspection |
| FR-009a | **no frame of any kind** follows a signal until the next one | integration, on the watcher's whole frame list |
| FR-009b | the client's five seconds is stated in the chapter | inspection |
| FR-009c | the verdict on FR-RTM-08 is recorded, not asserted — **in a published document as well as in the notes** | inspection |
| FR-010 | no table, no key, no outbox row | inspection + `INFO commandstats` |
| FR-011 | 2 s against 5 s, with the arithmetic recorded | inspection |
| FR-011a | two connections in one channel both publish; one connection in two channels publishes twice | integration |
| FR-012 | repeated signals in one window produce one publish | integration, **by count** |
| FR-013 | a dropped signal produces no frame, no close **and no log line** | integration |
| FR-013a | `limits.ts` is not edited and no `"typing"` operation exists | **command** — `git diff` |
| FR-014 | the send budget is unchanged across typing signals | integration |
| FR-015 | fabric severed: socket open, one logged event | integration |
| FR-016 | the SET of names an instance emitted is the closed set | integration |
| FR-017 | four kinds over shared channels, each once, under its own type | integration |
| FR-018 | nothing buffered, nothing replayed on reconnect | integration + a proof it bites |
| FR-019 | `git diff docs/04-srs.md` is empty | **command** |
| FR-019a | five claims, ten fragments, none still published | **command** — `check-prose.py` across `docs/` and both locales |
| FR-020 | four of six kinds have producers, the other two named | inspection |
| FR-021 | the chapter says the fourth grammar was taken and why the plan assumed otherwise | inspection |

**Six of twenty-one are verified by inspection or by a command rather than by a test**, and
that is the number worth watching. Chapter 3.20 had five, and its close-out found the one
requirement whose test did not exist by reading this column the other way.

---

## 2a. Success criterion → requirement

| SC | Requirements | How it is checked |
|---|---|---|
| SC-001 | FR-004 | integration, two instances, a shared channel |
| SC-002 | FR-009, FR-010 | inspection — no frame ends an indicator, because none exists to send |
| SC-003 | FR-011, FR-012 | integration, **by publish count** on a subscriber |
| SC-004 | FR-006 | integration, plus a schema that has no `user` to send |
| SC-005 | FR-007 | integration, the negative and the positive in one run |
| SC-006 | FR-002, FR-003 | integration, driven from the union rather than a list — **and once from the sealed client**, which had sent no frame in its history |
| SC-007 | FR-014 | integration, a send after typing signals |
| SC-008 | FR-015, FR-016 | integration, fabric severed by a TCP proxy |
| SC-009 | FR-018 | integration, reconnect after signals |
| SC-010 | FR-020 | prose, and the count re-derived at close-out |

**SC-002 is the one to look at twice.** It says an indicator disappears with no message
crossing the network — a criterion satisfied by doing nothing, which is the hardest kind to
test and the easiest to believe. What backs it is structural: `typingSchema` has no state
field, so there is no frame the server could send to end one. If that changes, this
criterion needs a different check.

---

## 3. Planned test → requirement (the direction that finds things)

Read this column first and ask of each row: **what would have to be false for this to
fail?**

| Planned test | Requirement | What its failure would mean |
|---|---|---|
| a client's typing signal is accepted | FR-001 | the seam did not widen; the feature has no entrance |
| **every other type is still refused, driven from the union** | FR-002, FR-003 | the seam widened too far — a client can utter an outbound frame |
| a payload carrying a `user` is refused | FR-006 | a client can type as anybody, which is the gauntlet's stated attack |
| a foreign channel publishes nothing, **on a subscriber** | FR-007 | scoping is absent, or the publisher is dead and the socket cannot tell |
| a member on another instance receives one frame | FR-004 | the fabric is instance-local |
| **a member added mid-connection receives one** | FR-004a | chapter 3.20's `added` branch subscribes three grammars and not the fourth — messages and presence arrive, typing does not, and the obvious test passes against that bug |
| **the signaller receives none while another member does** | FR-005 | the self-filter is missing, or the collector is unfiltered — chapter 3.19 got this wrong three phases running |
| **the signaller's SECOND connection receives none** | FR-005 | the filter is by socket rather than by identity. One connection per user cannot tell the two apart, and the wrong one shows a user their own indicator on their own second device |
| **the sealed client sends a typing frame and gets it delivered** | FR-001, FR-004 | the inbound seam works only for a client that imports this workspace's `ws` package |
| **the sealed client sends an unknown type and reads `unknown_frame_type`** | SC-006 | the refusal is asserted eleven times in-workspace and never once from outside it |
| a non-member receives nothing **in a run where a member receives** | FR-007 | a must-not-receive test passing because nothing was produced |
| a cross-tenant user receives nothing, same run | FR-007 | principle I, structurally |
| repeated signals produce one publish | FR-012 | a publish per keystroke at 10,000 connections per instance |
| **nothing at all follows a signal** | FR-009a | the server is ending indicators, which the frame cannot express — or the test proves nothing because the server sends nothing ever |
| two connections in one channel both publish | FR-011a | the interval is per user or per tenant, and one chatty client silences everybody else |
| an over-limit signal is silent | FR-013 | a cosmetic feature disconnects a client |
| **the send budget is unchanged** | FR-014 | typing exhausts a customer's message quota |
| a mid-resume frame is sent, not buffered | FR-018 | it lands after the cut-off or is dropped by the buffer's seq filter |
| a reconnecting client gets no replay | FR-018 | a claim about the present that was true five seconds ago |
| fabric severed: socket open, one line | FR-015 | the socket dies for a cosmetic feature |
| **the emitted name SET is the closed set** | FR-016 | the vocabulary grew and nobody decided — chapter 3.20's FR-032 said three while the code emitted six |
| four kinds, each once, under its own type | FR-017 | five subject shapes share one Redis and the topology stopped keeping them apart |
| **swapping in a third inbound type fails a test** | FR-003 | the set is a comment rather than a property |
| **setting the interval to zero fails a test** | FR-012 | the interval is decoration rather than a property |
| **routing typing through the buffer fails a test** | FR-018 | the separate path is decoration |

**The last three rows are proof techniques rather than tests, and this project has learned
to distrust them.** Chapter 3.20 wrote two and **neither produced a failure** — both
orderings turned out to be unobservable. A row here is a prediction; if it does not fail,
the finding is the row, not the code.

---

## 4. Requirements with no test, listed rather than absent

| FR | Why no test | What stands in |
|---|---|---|
| FR-008 | "this file is not edited" is not a runtime property | `git diff` on `frames.ts`, and the fence chain, which compares the file byte for byte |
| FR-009b | the client's timer is the half no test in this repository can reach | the chapter states it; FR-009a covers the server's half with a test |
| FR-009c | a verdict is a judgement, not a behaviour | `chapter-notes.md` in the shape chapter 3.20 used for FR-RTM-10, **and ADR-22 in `docs/05-sad.md`, which a customer can read** |
| FR-010 | "nothing is persisted" cannot be asserted by a test that does not know where to look | `INFO commandstats` shows no key written, and the schema has no table |
| FR-011 | a number and its argument | recorded in `baseline.txt` and read at close-out |
| FR-019 | a diff, not a behaviour | `git diff docs/04-srs.md` |
| FR-019a | prose in two trees | `check-prose.py`, run red before the corrections |
| FR-020, FR-021 | prose | the chapter, and `check-prose.py` for the claims they replace |

**Six requirements whose only verification is a sentence or a command.** That is the class
chapter 3.20 found a task list forgetting — a task list is written by thinking about what to
build, and nobody builds a paragraph.

# Traceability — chapter 3.22

**Built during planning, both ways, before any test is written.** That placement is not a
preference. The previous chapter's file records why: chapter 3.18 ran the map the second
way at close-out and found FR-007 — a MUST — with no test at all, after eight phases and
nineteen analysis passes had each read `requirement → test` and believed it. Chapter 3.20
did the same and found a requirement whose planned test was not in the tree. **This
chapter's own close-out re-derivation sat in the last phase until analysis pass 15 read
that paragraph.**

**No task ids below, and that is the predecessor's convention rather than an oversight.**
Chapter 3.21's traceability file carries none: a task id in another document goes stale the
moment tasks are renumbered, and what a reader needs is *how* a requirement is verified,
not *which* line of the task list happens to say so. The chapter's own `check-refs.py`
enforces this and reported fifty-six violations against the first draft of this file.

**It earned its place before it was finished.** Mapping the twenty-one requirements and
fourteen criteria against the task list found **two orphans**, both the shape a task list
forgets — and the shape the previous chapter named in the same words: *a requirement whose
verification is a sentence rather than a test.*

| Orphan | What was missing | Now carried by |
|---|---|---|
| **FR-011a / SC-013** | the shutdown release was **implemented and untested**. One task writes `releaseAll()`, another asserts `connections.close()` is *registered* in `main.ts` — which is wiring, not release. **The crash test covers the opposite path**: an instance destroyed without closing its sockets, slots freeing at the bound. A shutdown frees them **immediately**, so a reconnect must not wait the bound out, and nothing asserted that. | a clean-shutdown integration test, added to the task list by this file |
| **FR-002** | *"the maximum MUST be five, stated in exactly one place"* was named only by a commit task. The module defines the constants and a premise check covers `policy.ts`'s derivation; **nothing checked the single-statement property itself**, which is the point of the requirement — a second literal five is how two figures come apart, which is exactly what `policy.ts` did. | a unit assertion, added to the task list by this file |

**One requirement is satisfied by construction and is recorded as that rather than as an
orphan.** FR-004 — *"MUST NOT instruct the client to retry after an interval"* — needs no
test: `errorFrameSchema` is a `z.strictObject` of `code`, `message`, `docs_url`,
`request_id` and an optional `field`, so the payload **cannot** carry a retry hint, and the
refusal declines the HTTP path where `Retry-After` would live. Verified by inspection of
the schema, which is stronger than a test asserting a field's absence.

---

## 1. SRS clause → feature requirements → verification

`Pri` and the method are the SRS's own. The method column uses the constitution's four:
**T**est, **D**emonstration, **I**nspection, **A**nalysis.

| SRS clause | Pri · method | Feature requirements | Verified by |
|---|---|---|---|
| **FR-RTM-09** — up to 5 concurrent connections; each receives all events independently | P2 · T | FR-001 … FR-016b (the cap), FR-014 (the second clause) | integration, both halves |
| **CON-02** — no sticky routing for correctness | — · I | FR-006 | integration across two instances |
| **NFR-REL-03** — a deployment costs no more than one reconnection cycle | P2 · A | FR-011a | integration, the clean shutdown |
| **EIR-WS-05 / EIR-WS-06** — close codes documented, distinguishing their classes | P1 · T / P2 · I | FR-003 | unit (the pinned set) + inspection (the reference) |
| **NFR-SEC-06** — no credential in an error surface | — · I | FR-015 | integration, the log assertion |
| **NFR-MNT-02** — coverage floors | P2 · T | — | the ratchet, pinned at 100 on the new module |
| **NFR-PRF-04** — handshake to `connection.ack` p95 < 1 s | — · A | — | analysis: 1–5 local round trips against a 1 s budget |
| **NFR-SCL-01** — 10,000 connections per instance | P1 · A | — | **undischarged**, and this chapter does not discharge it (research R12) |
| **FR-RTL-01** — per-tenant rate limits including connection establishment | P2 · T | — | already shipped; unchanged here (research R6 hands on its arithmetic) |

## 2. Feature requirement → how it is verified

| Requirement | Method | Verified by |
|---|---|---|
| FR-001 | T | integration — five accepted, the sixth refused |
| FR-002 | I | **unit — the literal five appears exactly once** |
| FR-003 | T | integration — the close code and error code asserted, not the fact of closing |
| FR-004 | I | **by construction**: `errorFrameSchema` cannot carry a retry hint |
| FR-005 | T | integration — all five receive the next message after a refusal |
| FR-006 | T | integration, two instances — three on A, two on B, refused on either |
| FR-007 | T | integration — a dead instance's slots free after the bound |
| FR-008 | T | integration — a renewing connection survives three bounds |
| FR-009 | T | unit — the ratio, not the values |
| FR-010 | T | integration — a closed slot is reusable with no waiting period |
| FR-011 | T | integration — the expired slot and the hijack, two distinct states |
| FR-011a | T | **integration — a clean shutdown frees slots immediately** |
| FR-011b | T | integration — the re-claim succeeds, and the cap genuinely full |
| FR-012 | T | integration — one identifier, two environments, two counts |
| FR-013 | T | integration, after a falsification decides the test's shape |
| FR-014 | T | integration — three tests written against unchanged code |
| FR-015 | T | integration — the log line, and no credential in it |
| FR-016 | T | integration — the **log line**, not the acceptance |
| FR-016a | T | integration — the two log states told apart |
| FR-016b | T | integration — no fallback to the local count |
| FR-017 | I | inspection — the two SAD rows reconciled; SC-009 is the criterion |

## 3. Success criterion → how it is verified

| Criterion | Method | Verified by |
|---|---|---|
| SC-001 | T | integration — the delivery and the cap together |
| SC-002 | T | integration — the five undisturbed |
| SC-003 | T | integration — no waiting period |
| SC-004 | T | integration — two instances |
| SC-005 | T | integration — after the bound **and** before it, both halves |
| SC-006 | T | integration — three consecutive bounds |
| SC-007 | T + I | integration asserts the code pair; `contracts/refusal.md` states what a client does |
| SC-008 | T | integration — the log line |
| SC-009 | I | three documents read against each other, no contradiction left |
| SC-010 | A | the battery's mean against the 240-second budget |
| SC-011 | T | integration — the unenforced log line |
| SC-012 | T | integration — nothing closed by an opening |
| SC-013 | T | **integration — the clean shutdown** |
| SC-014 | T | integration — both branches |

---

## What this file does not establish

Every row says which kind of check verifies a requirement. **None says the check passes** —
that is the close-out re-derivation's job, which maps the same requirements against the
shipped tree rather than against the plan.

**And the reverse direction is deliberately empty.** It maps every test this chapter adds
back to a named requirement, across the six files that gain tests, and there are no tests
yet. The close-out fills it. Recording the direction now, empty, is what stops it being
forgotten — the failure chapter 3.18 shipped.

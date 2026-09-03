# Traceability — chapter 3.22

**Built during planning, both ways, and RE-DERIVED here against the shipped tree.** The
planning version is what found two orphans before a line of code existed; this version is
the check that what was planned is what exists. Chapter 3.18 ran the map only at the end and
found FR-007 — a MUST — with no test at all, after eight phases and nineteen analysis passes
had each read `requirement → test` and believed it.

**Methods are the constitution's four**: **T**est, **D**emonstration, **I**nspection,
**A**nalysis. Four rows here cannot have a test title at all and say so: FR-017 and SC-009
are inspection, because nothing executable reads `docs/05-sad.md`; SC-010 is analysis, the
battery's mean against a budget; FR-002 is a test that reads source, which is inspection
wearing a test's clothes and is recorded as **I** with the title beside it.

**No task ids, which is the predecessor's convention.** A task id in another document goes
stale the moment tasks are renumbered, and what a reader needs is how a requirement is
verified. The chapter's own `check-refs.py` enforces it.

**Every title below is an exact string from the tree**, checked by script rather than by
eye. Chapter 3.21's first re-derivation reported 28 gaps and every one was false: it matched
the first two long words of a proof phrase against test titles, and a proof phrase is a
description while a title is a sentence.

---

## The two orphans planning found, and where they landed

| Orphan | What was missing | Shipped as |
|---|---|---|
| **FR-011a / SC-013** | the shutdown release was implemented and untested. One task wrote `releaseAll()`, another asserted `connections.close()` was *registered* in `main.ts` — which is wiring, not release. The crash test covers the opposite path. | `frees the slots IMMEDIATELY on a clean shutdown (FR-011a (3.22), SC-013)`, plus two unit tests |
| **FR-002** | *"the maximum MUST be five, stated in exactly one place"* was named only by a commit task; nothing checked the single-statement property, which is the point of the requirement. | `states the maximum in exactly one place (FR-002 (3.22))`, which reads the module from disk and counts bare fives outside comments |

---

## 1. SRS clause → feature requirements → verification

| SRS clause | Pri · method | Feature requirements | Verified by |
|---|---|---|---|
| **FR-RTM-09** — up to 5 concurrent connections; each receives all events independently | P2 · T | FR-001 … FR-016b (the cap), FR-014 (the second clause) | integration, both halves; and the sealed outsider against built images |
| **CON-02** — no sticky routing for correctness | — · I | FR-006 | integration across two in-process instances |
| **NFR-REL-03** — a deployment costs no more than one reconnection cycle | P2 · A | FR-011a | integration, the clean shutdown, against the default 60 s bound |
| **EIR-WS-05 / EIR-WS-06** — close codes documented, distinguishing their classes | P1 · T / P2 · I | FR-003 | unit (the exact set, the exact count) + inspection (`docs/08-error-reference.md`). **EIR-WS-06 is met by two of six close codes** — chapter 3.22's `gaps.md` item 1 |
| **NFR-SEC-06** — no credential in an error surface | — · I | FR-015 | integration, the log assertion; plus the chapter-wide credential scan |
| **NFR-MNT-02** — coverage floors | P2 · T | — | the ratchet, `services/gateway/src/connections.ts` pinned 100/100/100/100 |
| **NFR-PRF-04** — handshake to `connection.ack` p95 < 1 s | — · A | — | analysis: 1–10 local round trips against a 1 s budget, and an unreachable registry bounded at 1 s by `connectTimeout` |
| **NFR-SCL-01** — 10,000 connections per instance | P1 · A | — | **undischarged, and this chapter does not discharge it** — ADR-23's reversal condition depends on it |
| **FR-RTL-01** — per-tenant rate limits including connection establishment | P2 · T | — | already shipped; unchanged here |

## 2. Feature requirement → method → the exact shipped titles

| Requirement | M | Verified by |
|---|---|---|
| FR-001 | T | `refuses when every slot is held, and says five (FR-001 (3.22))` · `accepts five and refuses the sixth with 4004 (FR-001 (3.22), FR-003, SC-002)` · `refuses a sixth connection for one user (FR-RTM-09 (3.22))` · `holds five connections and is refused a sixth with 4004 (FR-RTM-09 (3.22))` |
| FR-002 | I | `states the maximum in exactly one place (FR-002 (3.22))` |
| FR-003 | T | `accepts five and refuses the sixth with 4004 (FR-001 (3.22), FR-003, SC-002)` · `contains exactly 4001, 4002, 4003, 4004, 4008, 4009` · `holds eighteen codes` |
| FR-004 | I | **by construction**: `errorFrameSchema` is a `z.strictObject` of `code`, `message`, `docs_url`, `request_id` and an optional `field`, so the payload cannot carry a retry hint, and the refusal declines the HTTP path where `Retry-After` would live |
| FR-005 | T | `accepts five and refuses the sixth with 4004 (FR-001 (3.22), FR-003, SC-002)` — its second half publishes to all five after the refusal |
| FR-006 | T | `counts five across two instances and refuses the sixth on either (FR-006 (3.22), SC-004)` |
| FR-007 | T | `frees a dead instance's slots after the bound (FR-007 (3.22), SC-005)` · `still refuses BEFORE the bound elapses (FR-007 (3.22), SC-005)` |
| FR-008 | T | `renews a slot it still holds (FR-008 (3.22))` · `keeps a heartbeating connection's slot across three bounds (FR-008 (3.22), SC-006)` |
| FR-009 | T | `keeps the heartbeat strictly inside the bound, three to one (FR-009 (3.22))` |
| FR-010 | T | `frees a slot it holds, and the slot is reusable at once (FR-010 (3.22))` · `claims a slot whose tombstone has NOT expired (FR-010 (3.22))` · `does NOT free a slot another connection now holds (FR-010 (3.22))` · `frees a slot on close, reusable with NO waiting period (FR-010 (3.22), SC-003)` |
| FR-011 | T | `refuses to renew a slot ANOTHER connection now holds (FR-011 (3.22))` · `does not resurrect an expired slot on renewal (FR-011 (3.22))` · `refuses to renew a slot another connection took, rather than overwriting it (FR-011 (3.22))` |
| FR-011a | T | `releases every slot this instance holds (FR-011a (3.22))` · `accepts a claim immediately after releaseAll frees all five (FR-011a (3.22))` · `frees the slots IMMEDIATELY on a clean shutdown (FR-011a (3.22), SC-013)` · `closes every module it builds (chapter 3.22)` |
| FR-011b | T | `re-claims when its slot is GONE and nothing else took it (FR-011b (3.22))` · `keeps the connection working on a NEW slot after a re-claim (FR-011b (3.22), SC-014)` · `closes the connection when the cap is genuinely full at renewal (FR-011b (3.22), SC-014)` |
| FR-012 | T | `counts each environment separately for one user identifier (FR-012 (3.22))` · `counts each environment separately for one user (FR-012 (3.22))` |
| FR-013 | T | `never admits a sixth under many simultaneous claims (FR-013 (3.22))` |
| FR-014 | T | `delivers a message to both of one user's connections, each exactly once (FR-014 (3.22), SC-001)` · `delivers a membership change to both of one user's connections (FR-014 (3.22))` · `keeps delivering to a live connection when an EARLIER one is gone (FR-014 (3.22))` |
| FR-015 | T | `logs the refusal with the user, the environment and the count, and no credential (FR-015 (3.22), SC-008)` |
| FR-016 | T | `returns unenforced rather than zero when Redis is unreachable (FR-016 (3.22))` · `logs that the cap was not enforced when the registry is unreachable (FR-016 (3.22), SC-011)` |
| FR-016a | T | `tells 'not enforced' apart from 'enforced and under the limit' (FR-016a (3.22), SC-014)` |
| FR-016b | T | `does NOT fall back to counting this instance's own connections (FR-016b (3.22))` |
| FR-017 | I | the two `conn:` rows in `docs/05-sad.md` reconciled against ADR-23 and against `connections.ts`; no test reads a document |

## 3. Success criterion → method → the exact shipped titles

| Criterion | M | Verified by |
|---|---|---|
| SC-001 | T | `delivers a message to both of one user's connections, each exactly once (FR-014 (3.22), SC-001)` |
| SC-002 | T | `accepts five and refuses the sixth with 4004 (FR-001 (3.22), FR-003, SC-002)` |
| SC-003 | T | `frees a slot on close, reusable with NO waiting period (FR-010 (3.22), SC-003)` |
| SC-004 | T | `counts five across two instances and refuses the sixth on either (FR-006 (3.22), SC-004)` |
| SC-005 | T | `frees a dead instance's slots after the bound (FR-007 (3.22), SC-005)` · `still refuses BEFORE the bound elapses (FR-007 (3.22), SC-005)` |
| SC-006 | T | `keeps a heartbeating connection's slot across three bounds (FR-008 (3.22), SC-006)` |
| SC-007 | T + I | the close code and the error code asserted together in `accepts five and refuses the sixth with 4004 (FR-001 (3.22), FR-003, SC-002)`; `contracts/refusal.md` and `docs/08-error-reference.md` state what a client does |
| SC-008 | T | `logs the refusal with the user, the environment and the count, and no credential (FR-015 (3.22), SC-008)` |
| SC-009 | I | `docs/05-sad.md` §4.1, §6.3 and ADR-23 read against each other; no contradiction left |
| SC-010 | A | the twenty-run battery's mean against the 240-second budget |
| SC-011 | T | `logs that the cap was not enforced when the registry is unreachable (FR-016 (3.22), SC-011)` |
| SC-012 | T | `accepts five and refuses the sixth with 4004 (FR-001 (3.22), FR-003, SC-002)` — nothing is closed by an opening |
| SC-013 | T | `frees the slots IMMEDIATELY on a clean shutdown (FR-011a (3.22), SC-013)` |
| SC-014 | T | `keeps the connection working on a NEW slot after a re-claim (FR-011b (3.22), SC-014)` · `closes the connection when the cap is genuinely full at renewal (FR-011b (3.22), SC-014)` · `tells 'not enforced' apart from 'enforced and under the limit' (FR-016a (3.22), SC-014)` |

## 4. The reverse direction — every test this chapter adds, to a requirement

Six files gain tests, and the first version of this list said "the three new files", which
missed four of the six — including the sealed outsider, the chapter's only proof the feature
is not inert in the product.

| File | New tests | Every one mapped above |
|---|---|---|
| `services/gateway/src/connections.test.ts` | 17 | yes |
| `services/gateway/src/connections.itest.ts` | 20 | yes |
| `services/gateway/src/session.itest.ts` | 1 | FR-001 |
| `packages/protocol/src/codes.test.ts` | 2 changed | FR-003 |
| `services/gateway/src/main.test.ts` | 1 | FR-011a |
| `packages/outsider/src/integrate.itest.ts` | 1 | FR-001 |

**Two tests carry no requirement id and that is deliberate**: `does not throw for a slot the
connection never held` and `does not throw when it holds nothing` are the module's two empty
arms. Both were renamed at close-out — they used to say "is a no-op" and "releases nothing",
which describe the keys, while the assertion describes the promise.

---

## What this file does not establish

Every row says which check verifies a requirement and names it exactly. **None says the
check is a good one.** The eight falsification mechanisms in `baseline.txt` are the closest
this chapter comes to that, and they cover the cap's own tests rather than all thirty-seven.

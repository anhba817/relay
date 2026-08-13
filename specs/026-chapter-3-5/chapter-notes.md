# Chapter 3.5 — notes, written from what happened

Not a summary of the plan. The plan is in `plan.md` and it was wrong in places;
this is the record of what the work actually did, including the parts that were
discovered rather than designed.

---

## What R1's measurement changed

The chapter was planned twice. The first plan put the retry schedule in the
broker: `nak` with a delay, let NATS hold the message, let it come back. No new
table, no new loop, and chapter 3.4 had already built the consumer that would
receive it. It was the smaller design by every measure that was available before
anything was measured.

Two questions were then put to the actual broker:

```text
Q1  delayed redelivery survives a restart?           YES — 3 ms late
Q2  do delayed messages hold the ack-pending budget?  YES — and that is the problem
```

Q1 passed better than the design needed. Q2 disqualified it: three sleeping
messages against `max_ack_pending: 3` made two available messages **unfetchable**,
which at scale is one customer's dead endpoint consuming delivery capacity that
belongs to every other customer. FR-WHK-05 says that must not happen.

**The instruction was to stop and re-plan rather than adapt in place, and that is
what happened.** The replacement is a `next_attempt_at` column drained by chapter
3.3's relay loop with one extra predicate — a mechanism the reader already owns.
It also removed a dual write the first plan had accepted: expansion writes N rows
inside the claim transaction instead of publishing N messages after it.

The re-plan made the chapter bigger. That was the honest trade and it was written
down at the time (research R13), not discovered afterwards.

---

## The fence budget: 22 → 25 → 37–41, shipped 39

| Estimate | When | Why it moved |
|---|---|---|
| 22–26 | original plan | — |
| 25–29 | after R1's re-plan | the delivery relay and the schedule column |
| 37–41 | after counting properly | **test files** (7) and **container files** (4) had never been counted |
| **39** | shipped | inside the revised budget |

The first two numbers were not estimates that drifted; they were estimates that
omitted whole categories. Chapter 3.4 fenced one test file inside its budget and
left two unfenced, which is *why* spec FR-029 exists — and the first two budgets
for this chapter still forgot to count the seven test files FR-029 requires.

R11 said to treat the budget as a warning rather than an estimate, and that if
implementation approached the ceiling it was a signal to check whether the
narrowing decision held. It approached the ceiling. The narrowing decision was
checked, and it moved: FR-WHK-06 and FR-WHK-07 went to a new chapter 3.6.

Four changed files are deliberately unfenced — `pnpm-lock.yaml`, the drizzle
snapshot and journal, and the dispatcher's two tsconfigs. The chapter does not
teach them and fencing them would show a reader code it never discusses.

---

## Defects this chapter found in its own work

Every one of these was found by running something, and none by reading.

**1. The retry schedule never ran.** The delivery relay deduplicated its
JetStream publishes on `row.id` — identical across all seven attempts — so the
broker collapsed every retry into the first attempt's message. The publish
reported success, no message reached the dispatcher, and the row kept the
`dispatched_at` its claim had set, which only an outcome report clears. **Every
failing webhook was retried exactly zero times.**

Found by the walk script, against `--mode=fail`, on its first real run. Not found
by the test suite, because the delivery suite drives the claim query with no
broker in the path and the dispatcher suite used a fresh delivery for every case
— so nothing had ever published the same delivery twice, which is the exact
situation every retry produces. Key is now `{delivery_id}:{attempt}`; the
regression test was verified to fail against the old key.

**2. A security test that skipped itself.** The assertion standing between a
platform credential and a public route read `RELAY_INTERNAL_CREDENTIAL` from the
environment and returned early when absent — and CI never set it. It reported
success on every build without asking its question. Introduced in this chapter
(commit `d3b8fe9`), not inherited; the fix sets the value rather than reading it,
and CI now sets both new variables.

**3. `expand.ts` at 0% coverage.** The dispatcher's own suite reached expansion by
calling the repository against the database directly, so the consumer under test
was bypassed entirely. Research R12 predicted a new deployable would escape the
instrument; what it did not predict is that the instrument needed **no change at
all** — the globs already covered it, and no CI job was needed because every
workflow command runs at the workspace root. The task was to read the instrument,
not extend it.

**4. `repository.ts` fell below its ratchet** — 86.30% branches to 78.22%, four
thresholds red. `deliveryMaterial` and `pendingDeliveryDepth` are called only by
the dispatcher, whose suite runs the api as a child process whose coverage is not
attributable. The one function that returns a customer's signing secret in
plaintext was untested by the only measure the constitution names. Eleven tests
later it is 97.28 / 89.51 / 100 / 98.99, and the ratchet was **raised**, not
lowered to meet the code.

**5. Two vacuous assertions.** The "terminated, not retried" test could not fail:
`ack_wait` was 30 s and the test waited 2. Making it real required splitting
`ackWaitMs` per consumer — one knob had also shortened the deliver consumer, and
under the coverage lane's slower clock the broker redelivered attempts that were
still in flight, breaking two unrelated tests. And `deliver.ts`'s `skipped` branch
was covered only *incidentally*, by leftover deliveries other suites had left
pointing at deleted endpoints, which made a ratchet pinned on it move on its own.

**6. The walk signed a rendering that never went on the wire.**
`--print-signing-material` signed the payload object as the script built it, while
the platform signs what comes back out of `jsonb` — and PostgreSQL does not
preserve key order. A reader following V5 would have computed a signature that
never matched and blamed the platform.

**7. The figures rendered nothing.** `<Figure chart={…}>` — the prop is `code`.
MDX does not type-check props, so lint and build both passed while all three
diagrams were blank. Caught by T074's headless-browser check, which is the only
reason that check is worth running: a page that returns 200 is not a page that is
laid out.

---

## What it exposed in earlier work (spec FR-032)

**No earlier chapter's prose was found to be wrong.** The fence chain shows each
chapter's state at its own time, so a file amended here does not make an earlier
chapter a liar. What this chapter did expose were two latent gaps and one standing
debt.

- **The gateway had no build or start script.** It had run through `tsx` since
  Part 2 and nobody had needed otherwise. Containerisation made that impossible to
  defer. Amended and fenced here.
- **3.3's publisher assumed one stream.** `ensureStream` was hardcoded because in
  3.3 `EVENTS` was the only stream there was. A second stream turned "which stream
  do I guarantee" into a parameter. Not a defect — a correct assumption that
  needed widening, and the first delivery published to `deliveries.*` returned
  `503` until it was.
- **STANDING DEBT, still unfixed: the two Redis knobs.** `RELAY_REDIS_URL` is read
  by production code, `RELAY_REDIS_PORT` by the integration tests, which build
  their own URL. Setting only one produces timeouts that look like a broken
  fabric. Chapter 3.4's notes recorded this; it cost time again in this chapter,
  in exactly the way those notes predicted. **Recording it a third time is not the
  fix.** Reconciling the two names is a small change that touches files fenced in
  Part 2, and it belongs in a chapter that can explain it rather than in a
  footnote here.

---

## Corrections made to this feature's own artifacts

- **Quickstart V3's sabotage table was wrong.** Dropping the `next_attempt_at`
  predicate fails invariant 10 only, not "9 and 10" — invariant 9 is about claim
  exclusivity, which does not depend on dueness. The table conflated two
  properties that share a query.
- **Quickstart V3's first mutation would have passed.** Nothing verified that the
  delivery path signs the bytes it sends; the unit tests prove `signDelivery` is
  correct, which is a different claim. An integration test now verifies the
  signature against the raw body as received.
- **Quickstart V4 said six attempts.** FR-WHK-03 settled at seven.
- **Quickstart V6 could not be run as written.** A containerised dispatcher
  resolves `127.0.0.1` to its own loopback, so a hostile endpoint on the host was
  unreachable. Fixed with `extra_hosts` and a `--host` flag.
- **The chapter registry advertised auto-disable.** Rewritten in both languages to
  describe what 3.5 actually builds.

---

## Final state

```text
lint · typecheck · build            exit 0
unit                                156   (config 6 · service-kit 3 · protocol 31 ·
                                           api 74 · dispatcher 8 · gateway 34)
integration                         149   (api 111 · dispatcher 16 · gateway 13 · e2e 9)
coverage                            296 passed, every ratchet green
sabotage                            5 mutations, 5 caught, files byte-identical after
tutorial: lint · build · docs · fences   exit 0
fence chain                         145 files across 22 chapters, 22 translated
```

Part 3 gained a chapter. 3.6 is "When to stop trying" — the attempt log and
auto-disable together, because switching off a paying customer's endpoint is a
decision somebody has to explain afterwards, and the log is the explanation.

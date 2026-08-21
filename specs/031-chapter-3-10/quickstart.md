# Chapter 3.10 — validation

Every step reports an exit code. Run from `relay-platform/` with the compose stack
up and `DATABASE_URL` set, or unset — every package in this workspace falls back
to the compose address, a property feature 030's R50 had to restore.

## V0 — Baseline, before anything changes

```bash
pnpm turbo run test --force
pnpm test:integration
pnpm coverage
```

Record the three test counts, the integration lane's wall-clock, and the coverage
figures in `baseline.txt`. The current numbers are 251 unit, 231 integration and
473 coverage at 89.08 / 82.35 / 89.25 / 90.58 — but record what *this* machine
measures, because SC-006 compares against it.

## V1 — The month is counted

```bash
pnpm --filter @relay/api test:integration src/quotas
```

Expected: green, and the roll-up figures equal to the messages sent. This is the
step that proves the count exists before anything is enforced on it.

## V2 — The count survives a flush

```bash
docker compose exec redis redis-cli FLUSHALL
pnpm --filter @relay/api test:integration src/quotas
```

Expected: identical figures (SC-001). This is FR-002, and it is the one property
that separates a quota from chapter 3.8's limiter. If it passes trivially, check
that the test is reading the roll-up and not recomputing from `messages`.

## V3 — Running out refuses sends and nothing else

```bash
pnpm --filter @relay/api test:integration src/quotas src/messages
```

Expected: one refused send, one successful history read, against the same
environment in the same test (SC-002). Read the refusal body and confirm it names
the dimension, the usage, the quota and the resume date, and that its status is
`402` rather than `429`.

## V4 — Both doors

```bash
pnpm --filter @relay/gateway test:integration
pnpm --filter @relay/e2e test:integration
```

Expected: a WebSocket send is refused by the same cap as a REST send, and the
socket stays open (SC-003). Chapter 3.8's limiter never saw `/internal/messages`;
this chapter's enforcement point does, and this is the step that proves it rather
than assuming it (research R3).

## V5 — Nobody is surprised

```bash
pnpm --filter @relay/api test:integration src/quotas
open http://localhost:18025          # Mailpit
```

Expected: exactly three emails per quota per period, read out of Mailpit rather
than asserted on a send call (SC-004). Then drive usage across the same thresholds
again and confirm no fourth email (SC-005).

## V6 — The unaddressable organisation

Expected: the crossing is recorded, the cap still applies, and the failure to
notify appears in the log (FR-018). Chapter 3.9 built this branch; this step
confirms the fourth table uses it rather than reinventing it.

## V7 — Raising the cap

Expected: the next send succeeds, with no restart and no cache to clear (SC-007).
If this needs a restart, the cap is being read somewhere it should not be cached.

## V8 — The guard's prediction

```bash
pnpm test:integration
```

Expected: green, with no new entry in `packages/test-harness/src/exempt.ts`
(SC-008). Research R5 predicts this design engages feature 030's guard nowhere,
because it performs no cross-environment mutation. **This step exists to find out
that the prediction is wrong.** A refusal here names the table and the row, which
is a cheaper way to learn it than a suite failing after this one.

## V9 — Nothing was lost

```bash
pnpm turbo run test --force
pnpm coverage
```

Expected: unit and coverage counts at or above V0's, every per-file ratchet
green. The send path gains a `FOR UPDATE` on one row; if `repository.ts`'s ratchet
moves, that is the branch that moved it.

## V10 — Twenty runs

```bash
for i in $(seq 1 20); do pnpm test:integration || break; done
```

Expected: twenty green. Feature 030's battery took five attempts and each red run
was a real defect, so budget for the possibility rather than treating a red run as
noise.

## V11 — The size gate

Count the finished page's prose words, excluding fences, front matter and figure
captions. Expected: 2,000 to 4,000 (SC-009).

**Over 4,000 and the notification story moves to its own chapter** — it is the
phase with its own table, relay and test surface, which is why the phase order
puts it last. Counted on the page, not estimated: three of Part 3's four splits
were discovered mid-chapter, and this is the instrument that catches the fourth.

## V12 — The paperwork

```bash
cd ../relay-tutorial
pnpm check:fences && pnpm check:docs && pnpm lint && pnpm build
```

Expected: four exit codes of zero, and the fence chain reporting the new chapter's
files replaying onto `relay-platform`.

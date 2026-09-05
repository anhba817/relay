# A plan for `docs/09-platform-implementation-review-2026-09-03.md`

**Written:** 2026-09-05, against `part3-ch24` / `main`.
**Source review:** 10 current findings (2 High, 8 Medium), 3 roadmap items, 8 amendment
concerns.

---

## 0. What I checked before planning, and one finding that does not survive

Three of the review's claims are load-bearing for the ordering, and were asserted rather
than cited. I ran them.

| Claim | Verdict |
|---|---|
| ADR-20 lets revocation land 55 s beyond FR-RTM-10 | **Confirmed, verbatim in the ADR.** `06-adr-deep-dives.md` says *"exceeding the clause by 55 seconds"* and gives the arithmetic: 10,000 connections at one re-read each is 167 req/s at sixty seconds, 2,000 at five. |
| Close-code documentation covers two of six | **Confirmed.** `08-error-reference.md` names 4002 (x2) and 4004 (x1); 4003 appears in no document at all. |
| **Bot sends bypass quota exhaustion** | **WRONG AS STATED.** |

### The correction

`repository.ts:assertWithinQuota` throws `QuotaExceededError` on the **message** hard cap
*before* it ever consults `senderIsPerson`:

    if (messages_.hard !== null && sent >= messages_.hard) { … throw … }   // no bot branch
    …
    if (!senderIsPerson) return { … }                                       // 45 lines later
    if (users_.hard === null) return { … }                                  // active-users only

A bot send is refused exactly like a person's when the message quota is exhausted. What a
bot is exempt from is the **unique-active-persons** ceiling — which is what FR-RTL-05 says
after chapter 3.17 narrowed it, deliberately, with the reasoning in the code and the SRS.
And the bot is still **metered**: `usage_active_users` gets its row either way, because
FR-ANL-05 meters "users" while FR-RTL-05 caps "persons".

**The residual concern is real but much narrower than the review states**: a customer who
creates many bots pays nothing in the active-users dimension. Messages still count and
still hit the wall. So FR-RTL-06/08's cost control is not defeated; one of its two
dimensions is deliberately human-scoped. Worth a decision, not a fix.

---

## 1. The constraint the review omits, and it sets the price of everything

**Part 3 is closed. Every file these fixes touch is fenced by a published chapter.**

    users.schema.ts        2 chapters      webhooks.service.ts     2 chapters
    frames.ts              5               codes.ts               10
    internal.ts           11               messages.schema.ts      6
    repository.ts         23 (+appendix)   harness.ts              7 (+appendix)
    dispatcher.itest.ts    3 (+appendix)   connections.test.ts     1

A fence is a claim that the file in the repository looks exactly like the listing, and
`check:fences` replays all 241 of them. So **every code change below also costs an
amendment hunk in `relay-tutorial/fences/post-series.md`** — the appendix, not a chapter,
because no chapter teaches these fixes and a chapter cannot do the appendix's work.

Two consequences for sequencing:

- **Batch by file, not by finding.** Three fixes touching `frames.ts` cost one appendix
  hunk if done together and three if done apart.
- **`connections.test.ts` is the expensive one and the review calls it a move.** The fix is
  a *rename*, which retires a path. The chain convention for that is a `(deleted)` title,
  and the destination `connections.itest.ts` already has its own chain from chapters 3.22
  and 3.24. Renaming merges two chains. Budget this as a small project, not a `git mv`.

---

## 2. Workstreams

### A — Restore trustworthy verification (do this FIRST, not third)

The review puts this third. It belongs first, and its own text says why: *"these are
test-system defects, but they undermine the evidence used to claim product correctness."*
Every fix in B and C is validated by the lane. Fixing product code while the lane's exit
code means "and tuan didn't run last" is measuring with a broken instrument.

| # | Work | Where | Risk |
|---|---|---|---|
| A1 | `stop()` awaits child `exit` with a timeout instead of sleeping 200 ms | `packages/e2e/src/harness.ts:534` | Low. Two lines. Fixes 10 of this chapter's 11 red battery runs. |
| A2 | Give the e2e lane non-fixed ports — bind 0 and read back, the way `main.test.ts:19` does | `harness.ts:411` | Low, but touches the health-check plumbing. **Do not copy the gateway lane**: `session.itest.ts:133` draws a random port from a 200-slot range and self-collides 2.96% of runs. |
| A3 | Delete `itest-expand-*` / `itest-deliver-*` durables in `afterAll`, the way `consumer.itest.ts:201` already does | `services/dispatcher/src/dispatcher.itest.ts:407` | Low. The fix is written in the file next door. |
| A4 | `DeliverPolicy.New` for the dispatcher suite's own durables, so a dirty stream cannot starve a fresh run | `dispatcher.itest.ts` | Low. |
| A5 | Add the lane reset the repository does not have — `scripts/` can *read* this state (`stream-info.mjs`) and cannot clear it | new script | Low, and it retires a hand-run procedure that currently needs a human to approve two destructive statements. |
| A6 | Move `connections.test.ts`'s six real-Redis call sites out of the docker-free lane | see §1 | **Medium-high, because of the chain.** |

**Exit criterion:** twenty consecutive `pnpm test:integration` runs, from a cleared lane,
with the vitest sequencer cache deleted before the first — and the failure count reported
with the mechanism, not the fraction.

### B — Public-boundary defects (the review's #1, and it is right that they group)

| # | Work | Where | Risk |
|---|---|---|---|
| B1 | One exported `MESSAGE_TEXT_MAX`, applied to all three send doors | `frames.ts:34`, `internal.ts:32`, `messages.schema.ts:18` | Low code, **wire-visible**: an over-long socket send changes from the api's derived refusal to the gateway's own `invalid_frame`. Decide whether that is acceptable before shipping. |
| B2 | Restrict `avatar_url` to `http:`/`https:` by parsing the scheme, not by `z.url()` | `users.schema.ts:54,92` | Low code, **goes red for any environment already storing a bad value**. Needs a decision on existing rows. |
| B3 | `protocolError(code, …)` at the five bare 422s, one new code, one error-reference section | `webhooks.service.ts:88,193,196,202,210` | Low. Follow chapter 3.24's `media_not_available` precedent exactly. |

B1 and B2 both re-use the parsed-scheme and shared-bound patterns `attachments.ts` already
carries, so they are consistent with published material rather than new invention.

### C — Make webhook configuration trustworthy

| # | Work | Where | Risk |
|---|---|---|---|
| C1 | Validate `event_types` against `OUTBOX_EVENT_TYPES` at create and update | `webhooks.service.ts:208` | Low code, **needs a decision**: it goes red for any customer already storing a bad value, and today five of FR-WHK-02's eight named types are emitted, so some "invalid" subscriptions are subscriptions to unbuilt events. |
| C2 | Document 4001, 4003, 4008, 4009 and teach `check-error-codes.mjs` to compare `CLOSE_CODES` with the reference | `docs/08-error-reference.md`, `scripts/check-error-codes.mjs` | Low, **with a trap**: that script's orphan check fails on any `## ` heading not in `ERROR_CODES`. Chapter 3.21's convention is that a close code lives inside the `**Status:**` line of the error code carrying it — do not add a `## 4001` heading. |

### D — Decisions that are yours, not mine

Each of these is a recorded, argued decision. The review is right that each is open; none
should be overturned by a drive-by edit.

| Question | What the record says | What is actually being asked |
|---|---|---|
| **ADR-20's 55-second revocation gap** | The ADR states the overshoot and its arithmetic | Amend FR-RTM-10 with a degraded-mode bound, or make revocation durable and fail closed. **The clause and the code disagree today and one of them must move.** |
| **ADR-23's fail-open connection cap** | Deliberate, logged on every occurrence | Is the cap contractual/abuse-prevention (then fail closed) or best-effort availability (then say so in FR-RTM-09)? |
| **ADR-22's client-side typing expiry** | Technically argued; FR-RTM-08 reads as a server obligation | Needs a published client contract before it is true. Blocked behind the protocol reference. |
| **Missed revisions have no repair trigger** | SAD §resume amendment says history is the repair | A client has no reason to start it. Revision watermark, revisions in resume, or a bounded reconciliation pull. |
| **Migration metadata seven behind** | `gaps.md` 3.23-6 records both options | Regenerate snapshots from 0008, or delete `meta/` and retire `drizzle-kit generate` — which is what the last five chapters have actually done. **Decide before the next schema change**, which is Part 4's first migration. |
| **A subject grammar per real-time kind** | ADR-19→24, each argued individually | Define the threshold at which this consolidates. NFR-SCL-01 is still unmeasured, so there is no number to test against. |
| **Bot exemption from the active-users cap** | FR-RTL-05 as amended by 3.17, reasoning in code | See §0 — narrower than the review states. Options: an org-wide bot cap, or accept and document. |
| **ADRs live in two hand-maintained documents** | Convention since ADR-01 | Generate the SAD index from the ADR source, or accept the drift risk. `check:docs` does not compare them. |

### E — Cheap and unambiguous

| # | Work | Risk |
|---|---|---|
| E1 | Reorder the SRS revision ledger — 1.7, 1.6, 1.5 appear in reverse | Trivial edit in a published doc. |
| E2 | Add a checker for ordered revision entries | Small, and it is the only one of these findings that no existing instrument could ever have caught, because no checker reads prose. |

### F — Not fixes, and should not be planned as fixes

The three Roadmap rows — dashboard and self-service tenancy, analytics/compliance/hosted
media/emoji/SDK/reference client, and the public protocol reference and OpenAPI — are
**Part 4 and later scope**, already scheduled in `docs/07-tutorial-plan.md`: 4.1–4.4
analytics, 4.5–4.6 hosted media, 4.7 the audit log and compliance lifecycle, Part 5
developer experience. FR-MOD-03's audit log is the review's own Medium finding and it is
chapter 4.7's row. Listing them as findings is fair; scheduling them as remediation would
double-book work the plan already owns.

---

## 3. Recommended order, and why it differs from the review's

    1. A1–A5   the lane, minus the rename          evidence for everything below
    2. B1–B3   public-boundary defects             one appendix hunk if batched
    3. E1–E2   the revision ledger                 trivial, unblocks nothing, costs nothing
    4. D        the decision set                    needs you; several block Part 4
    5. C1–C2   webhook trust                       C1 needs D's "existing bad rows" answer
    6. A6      the connections.test.ts rename      most chain work, least urgency
    7. F        Part 4, as chapters

The review's order puts public-boundary defects first and verification third. I would swap
them: A1–A5 are low-risk, they are the reason the current battery reads 9 of 20, and every
claim that B and C are *done* rests on the lane they repair.

**A6 moves last, against the review's grouping.** It is the only item whose cost is
dominated by the fence chain rather than the code, and nothing else waits on it.

---

## 4. How this ships

Part 3 is closed and tagged. These are not a chapter — no chapter teaches them — so they
land as ordinary commits plus amendment hunks in `relay-tutorial/fences/post-series.md`,
which is exactly what that file is for.

Two rules from this chapter's close-out apply directly:

- **Run the full gate set, and it is fourteen, not eleven**: `typecheck`, `lint` and
  `build` from `relay-platform` belong in it. Chapter 3.24 tagged a tree that failed
  `pnpm lint` because they were missing from the list.
- **Run `check:fences` after every source edit**, not once at the end. Three separate
  edits broke fences during 3.24's close-out, and the checker reports only the first
  difference per file.

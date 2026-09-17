# Implementation Plan: chapter 4.9 — "Milestone: the meter agrees"

**Feature directory**: `specs/054-chapter-4-9`
**Spec**: [spec.md](./spec.md) · **Research**: [research.md](./research.md) — **read it first,
two of `docs/12` §2.3's four premises are falsified there**
**Created**: 2026-09-17

## Summary

Movement IV's closing milestone makes two claims (`docs/12` §2.3): a CI gate that catches a
planted drift on every run, and the 0.1% figure recorded once at a volume where 0.1% is a real
threshold. Most of the parts exist and **neither claim is true today**.

The gate's test was written at chapter 4.7 and the gate never reaches it: `pnpm
test:integration` stops at the first failure and the api lane carries six, none of them the
reconciler's. **And its summary line counts tasks rather than suites** — 18 planned is 9 builds
and 9 test tasks, three of which are packages with no integration script — so the number four
chapters have read as lanes has never been one. The figure has no resolution anywhere in this lane: the largest operational
tenant-period holds 1,017 messages, where the smallest expressible drift is 0.197% — twice the
bound — and no tenant has both sides of the comparison at all.

So the work is a harness, a gate that can go red for its own reason, one measurement published
in its own document, and an amendment: **constitution III still says 0.1% flat while SRS 1.14
says three of four quantities cannot meet it.**

## Technical Context

**Language / runtime**: TypeScript / Node 22, unchanged (constitution VII).
**New dependencies**: none expected. The harness extends `scripts/scale/`, which is plain
Node and `pg`.
**Stores**: PostgreSQL 18 (operational counters), ClickHouse 25.3 (`daily_usage_billing`, fed
from `message_events`).
**Volume**: 1.6M messages build in 92.4 s and load into ClickHouse in 1.2 s (R3), so the volume
is not a constraint. The measurement needs ≥100,000 in one tenant-month, and three facts about
`corpus.mjs` decide the shape — **all three were read only after an artifact had published a
number that ignored them**: `CORPUS_DAYS` must exceed 90 (`:88`), `CORPUS_ENVIRONMENTS` must be
at least 2 (`:82`), and **`CORPUS_MESSAGES` is the subject environment's ninety-day window, not
a total** (`planFor`). The rule that falls out: a month is a third of `CORPUS_MESSAGES`, so
350,000 gives the subject ≈116,700. The figure the measurement publishes is **read off the
harness's report**, because the split across channels is floor division with a remainder.

**Lane hygiene**: the corpus's analytical side loads into `relay_analytics` — the lane's own
store — so a run deposits ≈389,000 rows beside four chapters' data, and the only cleanup this
repository ships is `DROP DATABASE` (R6a). A scoped cleanup is part of the work, not an
afterthought.
**Test strategy**: the planted-drift suite already exists; this feature makes it reachable,
shows it red, and adds the harness's own tests.
**What is NOT in scope**: the ingester `compose.yaml` does not ship (050-8) is resolved or
recorded, not redesigned; movement V's hosted media; and the two carried constitution III items
about the cross-store read.

## Constitution Check

Read the clauses, not the identifiers — chapter 4.7 found a citation pointing at nothing and
4.8 wrote two feature-local ids into published documents. Each row below quotes what it checked.

| principle | verdict | what was read, and why |
|---|---|---|
| **I — tenant isolation** | **PASS** | The harness creates environments and writes rows scoped to them; `usage_periods.environment_id` is a foreign key to `environments.id`, so nothing can be written for a tenant that does not exist. The cross-tenant suite derives its targets from the router and this feature adds **no route**, so the suite's target count does not move. Checked: the fourth bullet's *"automated cross-tenant access test suite MUST attack every endpoint"* is about endpoints, and there are none. |
| **II — no acknowledged message is lost** | **NOT ENGAGED** | The harness writes `messages` rows directly, which is what `corpus.mjs` has always done and is not a send. No write endpoint, no ack, no sequence assignment. The bulk-insert trap chapter 4.1 recorded — `channels.last_sequence` left at 0 makes every later send collide — is the one thing here that could touch this principle, and `corpus.mjs` already maintains it. **Verify rather than assume.** |
| **III — two data paths, never crossed** | **CONFLICT, NAMED, AND LARGER THAN THE FIGURE** | The fourth bullet is this milestone's own clause: *"Metered totals MUST reconcile against operational counts to within 0.1%, verified by a daily job that alerts on breach."* **SRS FR-ANL-06 was amended at 1.14 and this bullet was not.** And the sentence asks for three things: **two of the three have no mechanism here**, not one. The bound is unreachable for three of four quantities (1.14); *"alerts on breach"* has no path (1.14); and **the *"daily job"* has no runner at all** — nothing invokes `scripts/reconcile-usage.mjs`, and `ci.yml` has no `schedule:` trigger (R7a). Only the alert was ever recorded. The governance section requires the conflict be *"resolved explicitly by amendment rather than ignored"*. See R7, R7a and the Complexity table. |
| **IV — single writer** | **PASS, WITH ONE THING TO CHECK** | *"Only the API service writes to PostgreSQL."* `corpus.mjs` writes to its own `relay_corpus_*` database and is refused the lane's `relay` — it is a measurement harness against a disposable database, not a second writer to the product's store. **What to check**: the harness must not gain a path that writes `usage_periods` in `relay`, which would be a second writer to a live table. |
| **V — API-first** | **NOT ENGAGED** | No API surface, no error codes, no dashboard. The fifth bullet — *"every metered unit is visible in the dashboard the moment it is counted"* — is the tension `gaps.md` 053-9 files forward and is not reopened here. |
| **VI — requirement-driven, test-verified** | **PASS, AND ONE CLAUSE IS THE FEATURE** | *"The cross-tenant suite, dependency vulnerability scans, and the OWASP Top 10 scan gate releases"* and *"The quickstart MUST run unmodified, verified by automated execution in CI"*. The second is what the gate half is about: a gate that cannot be reached does not verify anything. Coverage: the harness is a script, and `scripts/` carries no per-file pins today — **decide, do not inherit** (see Complexity). |
| **VII — boring by design** | **PASS** | No new service, no new language, no new dependency. **An ADR is owed if the gate's shape changes** — moving a suite out of the integration gate, or changing `--concurrency=1`, is an architecture decision with a reversal condition, and VII says every one is recorded. |

### Constitution III, stated as the thing it is

This is the first feature whose **subject** is a constitution clause rather than a requirement
that happens to touch one. Three readings were considered:

1. **The constitution's 0.1% is the binding one and the SRS amendment is a divergence.** Then
   the milestone cannot pass and the platform is out of compliance on three quantities for
   reasons that are not defects — which is what the amendment exists to say.
2. **The SRS is the operative document.** The governance section forbids this reading in as
   many words: a conflict is resolved by amendment, not by precedence.
3. **The constitution bullet is amended to carry what 1.14 established.** The bound holds for
   the quantity whose two counters are written in one transaction, and the clause names the
   three it cannot hold for and why.

**The third is the one the governance section describes**, and the amendment is a MINOR bump
under the stated versioning policy — materially expanded guidance, no principle removed. It is
the constitution's own amendment procedure and therefore a proposal this feature writes rather
than a change it makes unilaterally.

## Phases

### Phase 1 — Premises and openings

Take every figure this feature will be measured against, before anything changes. The gate's
current behaviour, the six reds by name and cause, both sides of the reconciler on the lane,
the resolution table re-derived, and the fence-chain opening by kind and locale.

**Run the quickstart as written before trusting it** — chapter 4.8's step 2 caught step 1 the
first time it was run.

### Phase 2 — The harness's arithmetic, with no store in sight

The parts a unit test can drive: the volume-to-smallest-drift function, the counter derivation,
and the argument parsing for the reconciler script's two new addresses. Chapter 4.7 separated
its verdict for this reason and 4.8 separated its query contract; the same split applies.

### Phase 3 — Both sides, for one tenant, at volume

Extend `scripts/scale/` to write `usage_periods` and `usage_active_users` for the environments
it creates, and teach `scripts/reconcile-usage.mjs` to take both addresses. Then run the
reconciler against a corpus and get a verdict that is `pass` or `breach` rather than `no-data`.

**The order matters and the quickstart fixes it** (R6): apply the analytical schema first so
the views fire on the load. The wrong order reports an analytical zero — and **the backfill is
not the recovery**, because `daily_usage_billing` is a `SummingMergeTree` that doubles on a
second run while `apply.mjs`'s ledger makes re-applying a silent no-op.

### Phase 4 — The gate that can go red 🎯 MVP

Make the integration gate reach the reconciler and report which suites ran. Resolve or record
each of the six reds. **Show the gate red by breaking the drift comparison, then green again.**

**And the workflow's colour is not a signal to change** (R1b). `ci.yml`'s tutorial job ends with
`pnpm check:fences`, which exits 1 at the standing 110 and has on every push since feature 045 —
so a planted drift is measurable at the step and invisible at the workflow. **That is this
milestone's own defect one level up**, and the phase decides what to do about the arrangement
rather than claiming a build signal it does not have.

**And decide the schedule, which is a different claim from the gate** (R7a). §2.3 substituted
*"the lane, every run"* for the clause's *"daily job"* without saying so, and a per-push check on
a planted fixture reads no real tenant. The decision — a sixth background relay, or a recorded
absence — is an architecture decision with a reversal condition, not an implementation detail.

This is the MVP: after this phase a planted drift fails the build, which is the half §2.3 calls
falsifiable.

### Phase 5 — The measurement

Build the corpus at ≥100,000 in one tenant-month, run the real reconciler, plant a drift at the
bound and one past it, and publish `docs/13-metering-measurement-<date>.md` on `docs/11`'s
model. **Say what the figure does not prove** (R10): both sides derive from one source, so the
figure is about the reconciler's arithmetic and the bound's resolution, not about the platform
agreeing with itself.

### Phase 6 — The amendments

Propose the constitution III amendment with its version bump and migration impact. Amend
`docs/12` §2.3 where this feature falsified it — the harness claim is stale and the gate claim
was never true. Re-check every clause by opening the SRS, and **diff `docs/` for bare-numbered
ids**, which is the check that caught chapter 4.8 reproducing 1.14's defect.

### Phase 7 — The chapter

The milestone chapter, registration, figures, fences, every gate, `gaps.md`, `traceability.md`,
`CLAUDE.md`, the tag, the push. **Movement IV's close**: what shipped, what was amended, what
was defined and left unbuilt.

## Complexity tracking

| decision | why it is not simpler | what it costs |
|---|---|---|
| **A constitution amendment proposal** | The governance section requires it and the milestone's own clause is the one in conflict. Leaving it is the silent divergence the section names. | A document, a version bump, and a decision that is not this feature's to make alone. |
| **Extending `corpus.mjs` rather than writing a second harness** | 045 deleted a hand-maintained port map rather than correct it; a second corpus builder is the same shape. And `corpus.mjs` already runs the platform's migrations against its own database, so the counter tables exist there. | The file grows, and it carries no titled fence in either locale — checked, not assumed, before the plan committed to it. |
| **One new argument on `reconcile-usage.mjs`** | Without it the script reads the lane from the environment and cannot be pointed at a corpus. **It was two until analysis pass 1**: `--analytics-database` cannot work, because `DB_ANALYTICS` is a constant at `reconcile.ts:110` rather than a parameter and `apply.mjs` hardcodes the same name, so nothing here can build a second analytical database to point at. | One flag, defaulting to today's behaviour; it is also the change that would let an operator reconcile a staging tenant. And the validation moves to the value that **does** reach a ClickHouse statement — the environment id, interpolated as `toUUID('…')` from a command-line argument. |
| **Coverage pins for a `scripts/` file** | `scripts/` carries no per-file pins today. A harness whose arithmetic decides a published figure is not the same as a one-off. | Decide in phase 2 and record the decision either way, rather than inheriting the absence. |
| **Changing the integration gate's shape** | Six reds block the reconciler and four chapters have read them as somebody else's problem. | If the shape changes — `--continue`, a separated lane — it is an architecture decision and VII wants an ADR with a reversal condition. |
| **Deciding whether `docs/07` §2's chapter floors cover a milestone** | §2 states 2,000–4,000 words and 2–4 figures for every chapter, and **the same two published milestones fail both** — 1,873 words / 1 figure, and 1,683 words / 2 figures, against 2.8's 3,151 words and **0 figures** (R7c). A feature that imposes those floors on 4.9 whose closest precedents fail them has to say which reading it is using, and it is one question rather than two. | A decision and two recorded measurements. Chapter 4.9 meets both either way; exempting a chapter class would be an amendment to `docs/07` and is not taken on this evidence alone. **And the figure floor is enforced by nothing** — `check:figures` checks the `code=` prop and the bindings, not the count. |
| **Deciding what to do about a permanently-red workflow** | `check:fences` exits 1 at 110 as its job's terminal step, so no gate in this workflow has a legible verdict at the workflow level (R1b). A milestone about a gate that cannot fail for its own reason cannot leave that unnamed. | A decision and an ADR. The options — a recorded baseline the checker compares against, `continue-on-error` with the count published, or its own job — are the series', not this chapter's, so **deciding and recording is required and building is not**. |
| **Deciding the schedule rather than only the gate** | FR-ANL-06 asks for a *daily* job and nothing runs the reconciler: no script, no CI step, no `schedule:`, no relay (R7a). A milestone that claims the clause is verified by a per-push fixture check would be claiming the weaker of two different things. | A decision, an ADR, and possibly a **sixth** background relay — whose cost feature 030 already measured for the other five: another loop sweeping the database while other suites' fixtures sit in it, and another flag every analytical suite has to set. Not building it is allowed; not deciding is not. |

## Files this feature is expected to touch

Named because chapter 4.5 found a remembered list wrong in both directions, and 4.8 found three
clean fenced files it had not counted. **Fence counts are checked at phase 1, not assumed.**

    file                                    fences en/vi  HEAD problem?  in the APPENDIX?
    scripts/scale/corpus.mjs                    0 / 0        —              no    free
    scripts/reconcile-usage.mjs                 1 / 0        no             no    chapter hunk
    services/api/src/metering/reconcile.ts      1 / 0        no             no    chapter hunk
    compose.yaml                                8 / 6        no             no    chapter hunk
    services/api/src/limits/limits.itest.ts     1 / 1        no             no    chapter hunk
    package.json                                4 / 4        YES, line 15   YES   APPENDIX ONLY
    turbo.json                                 10 / 10       no             YES   APPENDIX ONLY
    .github/workflows/ci.yml                    —            not chained
    docs/13-metering-measurement-<date>.md          new
    .specify/memory/constitution.md                 the amendment proposal
    docs/12-part-4-structure.md                     §2.3, falsified in two places
    relay-tutorial/app/(en)/part-4/chapter-09/…     the chapter
    relay-tutorial/lib/tutorial.ts                  registration

**Counted, not remembered, and the last column is the one that decides where an edit goes.**
`corpus.mjs` is free, which is why the harness extends it.

**`services/api/src/metering/reconcile.ts` was added to this table at phase 2**, when the
arithmetic landed there rather than in `scripts/`: a per-file coverage pin on a file no lane
includes is silent — probed, both halves — so a harness function in `scripts/` would be
unmeasured and unpinnable. It is chapter 4.7's own precedent, which moved `exitCodeFor` out of
that script for the same reason.

**THE GATE'S DEFINITION IS PUBLISHED IN THE APPENDIX AND NOWHERE ELSE** (R1a).
`fences/post-series.md` carries a `package.json` hunk whose `-`/`+` pair **is the
`test:integration` line**, and the appendix applies after every chapter — so a 4.9 chapter hunk
for that file would anchor on a pre-appendix state and then be **overwritten** by the appendix.
Chapter 4.8 hit the adjacent case and it reported (`hunk pre-image matched 0 times`) because the
two edits did not overlap; **an overlapping edit does not report, it disappears.** Any change to
`test:integration` goes in the appendix's hunk.

**And "already a HEAD problem, therefore invisible" is about the wrong half of the checker.**
That makes an edit invisible to the HEAD comparison. The APPLY side is separate and is where an
overwritten hunk lives. A file can be free on one half and expensive on the other.

**`reconcile-usage.mjs` at 1 en and 0 vi is not special**: the Vietnamese Part 4 stops at
`chapter-03`, so every file chapters 4.4 through 4.8 fenced is en-only. That is the translation
frontier rather than a shape needing handling.

## Open questions for `/speckit-analyze`

1. Whether the ingester belongs in `compose.yaml` or the five suites belong outside the gate.
   Both are decisions with reversal conditions; neither is obviously right, **and they are not
   the same price**. `package.json:15` already carries `--filter=!@relay/outsider` for a suite
   that needs a running platform no lane starts, so the shape has a precedent — but `--filter`
   selects **packages**, and the five `request-log.itest.ts` reds sit inside `@relay/api` beside
   the reconciler's suite. Separating them needs a vitest `exclude`, a second config, or moving
   the file, each changing what the api's integration lane means for everyone (R1). Against that,
   an ingester in `compose.yaml` is a service definition and 8/6 fences.
2. Whether the measurement's corpus is built once and recorded, or rebuilt by the quickstart.
   `docs/11`'s precedent is the former; constitution VI's *"quickstart MUST run unmodified"* is
   an argument for the latter.
3. Whether the constitution amendment ships in this feature or is proposed and left open. The
   procedure says a PR modifying the file; this project has no separate PR for it.
4. Whether the reconciler becomes a sixth background relay. Answered by phase 4's ADR either
   way, and the answer decides what the milestone's one sentence is allowed to say.

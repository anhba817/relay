# Specification Quality Checklist: Tutorial Chapter 3.8 — "Limits you can see coming"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-19
**Feature**: [spec.md](../spec.md)

## Content Quality

- [X] No implementation details (languages, frameworks, APIs)
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders
- [X] All mandatory sections completed

## Requirement Completeness

- [X] No [NEEDS CLARIFICATION] markers remain
- [X] Requirements are testable and unambiguous
- [X] Success criteria are measurable
- [X] Success criteria are technology-agnostic (no implementation details)
- [X] All acceptance scenarios are defined
- [X] Edge cases are identified
- [X] Scope is clearly bounded
- [X] Dependencies and assumptions identified

## Feature Readiness

- [X] All functional requirements have clear acceptance criteria
- [X] User scenarios cover primary flows
- [X] Feature meets measurable outcomes defined in Success Criteria
- [X] No implementation details leak into specification

## Notes

### On the two "no implementation details" items

Both are marked pass, and the reasoning needs stating rather than assuming,
because the spec names Redis, Postgres, `429`, `X-RateLimit-*` and a container in
`compose.yaml`.

The item exists to catch a spec that over-constrains the solution — one that picks
a technology the requirement did not ask for. Everything named here is **already
decided in a document this spec is downstream of**:

- Redis as the counter store and the `rl:` key prefix are specified in SAD §6.3's
  key table against FR-RTL-01. The spec cites that choice; it does not make it.
  (The SAD's row also says "Token buckets", which research R1 later found
  contradicts the same row's TTL column — see R1 for why the chapter builds a fixed
  window and why that is not an ADR.)
- `X-RateLimit-Limit`, `-Remaining`, `-Reset`, `429` and `Retry-After` are the
  literal text of FR-RTL-02 and FR-RTL-03. Paraphrasing them would lose the
  requirement.
- `rate_limited` and close code 4008 are existing constants in
  `packages/protocol/src/codes.ts`, declared in chapter 1.3.

Naming a decision made upstream is citation, not leakage. Where this spec does
make a technology choice — a mail container in `compose.yaml` — it is recorded in
Assumptions with a justification against constitution VII, which is where a new
piece of infrastructure is supposed to be argued.

The "non-technical stakeholders" item is the weakest of the four. This is a
specification for a chapter of a technical tutorial; its reader is a developer.
It is marked pass on the same basis every previous chapter spec in this repository
was, and the standard applied is that a reader who has not seen the code can
follow what is being built and why.

### Two requirements were rewritten during validation

**FR-008** first read "MUST count a documented unit … and the implementation MUST
match", which is a requirement to be consistent rather than a requirement to be
correct. A test over single-message traffic passes whether the limiter counts
requests or messages, so the original wording was satisfiable by an untested
choice. It now requires a test that distinguishes the two.

**FR-014** first read "MUST NOT assert a remaining count the platform cannot
substantiate". Untestable as written: it forbids a state of mind. It now requires
that a client be able to tell "you have N left" from "we are not counting", and
requires the chapter to say which the platform sends. The matching acceptance
scenario in User Story 2 was rewritten with it.

### Decisions deliberately left to the plan

These are not gaps in the spec; they are questions the spec is right to pose and
wrong to answer.

- **The default limit numbers.** The SRS specifies none for FR-RTL-01. FR-007
  requires a documented default and configurability; what the number is belongs in
  research, with its reasoning recorded, because any number chosen here would look
  authoritative and be arbitrary.
- **What a degraded response sends** — headers omitted, or headers with an explicit
  "not counting" signal. FR-014 requires the distinction be possible and the
  chapter state the choice; which choice is a design question.
- **How the auth limiter avoids failing open** without failing closed into an
  outage. FR-011 states the property; whether it is a local in-process fallback, a
  stricter threshold, or something else is research's to answer. This is the
  chapter's sharpest decision and the spec should not pre-empt it.
- **Whether the mail transport is a section or a split.** Recorded as a size risk
  in Assumptions. Three of the last four Part 3 chapters exceeded the word bound;
  the plan should estimate the fence budget before the prose is written.

### What `/speckit-analyze` found that this checklist did not

Recorded because a validation pass that only reports itself passing is one nobody
trusts. Four findings, and the first two are the ones this checklist should have
caught.

**A1 — the biggest, and it was a hole rather than a wording problem.** Three
buckets were defined (`rest`, `send`, `connect`) and a `POST …/messages` is both a
REST request and a message send. Nothing said whether it decrements one, the other,
or both — and FR-002 describes **one** set of headers, so a client reading
`Remaining: 599` could not tell which allowance it had read. The "requirements are
testable and unambiguous" item was marked pass over it. Resolved by research R11 and
FR-036: both are counted, the headers report whichever has fewer remaining, and the
refusal names which limit was reached.

**C1 — the spec said "token buckets" and research had chosen a fixed window.** Two
of the four places carrying the stale word were *published* artifacts, the tutorial
plan's table row and the site registry in both locales. This is the failure chapter
3.7 spent itself on: a document promising something the code does not do.

**C3 — the fixed-window decision contradicted a mechanism the SAD names, with no
reversal condition and no answer to whether it needed an ADR.** Chapter 3.2's
research had set the precedent of addressing that question explicitly; R1 did not.
Both are now in R1.

**G1 and G2 — two requirements that got built and never checked.** FR-007 had tasks
creating three nullable columns and no task asserting an override changes anything;
FR-014 had an implementation task and no assertion. Both are the shape this project
keeps finding at the sabotage battery, and both now have tasks (T011a, T025a).

Four of the eight edge cases also had no task. Three now sit in T006a; the
disable/re-enable/disable case went into T049.

### What the SECOND analyse pass found, which was worse

Three findings, two of them architectural, and both architectural ones came from
the same place: **the gateway's deliberate poverty.**

**D1 — the gateway cannot read the limit policy.** It lives in three Postgres
columns and `services/gateway/src/registry.ts` states the gateway's position as a
design statement: *"no pg, no drizzle-orm, no repository import."* FR-007 required
per-environment configurability and carved out no exception for the socket, so one
of the three limits was specified as configurable and had no way to be. Resolved by
R12: the limits ride the authentication response the gateway already requests, and
sit on the `Connection` beside chapter 3.7's `marks`. The accepted cost — a limit
changed mid-connection does not apply until reconnect — is now a stated property
with a test.

**D2 — research R5 asserted something false about the platform.** It said "a gateway
exists, it mints request ids" as the argument for requiring `request_id` everywhere.
The gateway mints none: zero occurrences, and its `sendError` builds three fields.
The requirement would have surfaced as a compile error in T022 with no value
available to supply — which is exactly when a chapter takes the expedient answer and
makes the field optional. R13 rejects that explicitly, because an optional fourth
field would be the fourth instance of the habit this chapter is *about*.

**D3 — the api counts the wrong IP.** FR-AUT-12 limits failed authentication per
source address, and a handshake authenticated through the gateway arrives from the
gateway. Every customer's failures shared one counter, so one attacker would exhaust
a threshold that then refused everybody. This was not a wording problem; it was a
security requirement that did not do what it said. R14 forwards the client address on
the internal contract, and names the interaction it creates: the same call is trusted
enough not to be throttled and not trusted to be the origin.

**What both passes have in common.** Neither found a bad sentence. Both found a
requirement that was satisfiable on paper and unbuildable, or buildable and wrong.
The first pass's A1 and this pass's D1 and D3 are all the same shape — a spec written
from the API's point of view, applied to a service with different capabilities.

### What the THIRD pass found: the same shape, now in the tests

**E1 — the auth limiter would have refused this project's own test suite.** The
threshold is 10 failed authentications per minute per source address; the api
integration lane asserts `401`/`403` twenty-six times from `127.0.0.1` in about 110
seconds. And FR-028 makes the rate-limit refusal *deliberately* indistinguishable
from a wrong-credential refusal, so the break would have arrived as a `401` carrying
the wrong `code` and no local cause.

Resolved by R15: the threshold becomes configuration with an **enforcing** default,
and T004a measures what the lane actually produces before anything is chosen — a
count of assertions is not a count of requests, which is the difference chapter 3.7's
sweep fault turned on.

**Three passes, one shape.** Pass 1 found a spec written from the api's point of view
applied to a socket. Pass 2 found two more of the same. Pass 3 found the feature
written without asking what it does to the suite that already exists. None of the
twelve findings was a badly written sentence; every one was a requirement that was
satisfiable on paper and either unbuildable or wrong in practice.

**And the size estimate moved the wrong way.** R10 said 23 fences for the limiter
half; remediation across three passes took it to **28**, above chapter 3.6's entire
21, every addition a consequence of the gateway not being the api. Estimates usually
shrink under scrutiny. This one grew, which is the strongest argument yet for T059
splitting the transport out.

### The fourth pass found a defect the third pass introduced

**F1 — an instruction written from memory instead of from the script.** Pass 3 added
T061a saying "an amendment diff's base is the chain's end state, not the latest
tag", generalising from a debugging session during chapter 3.7. Reading
`check-fence-chain.mjs` shows it is true of **post-series** diffs and false of
**chapter** fences: `replay()` applies all chapter fences first and post-series
afterwards, so for a chapter fence the chain's end state *is* `part3-ch7` — and
`check:fences` passing is the proof. The instruction would have sent an implementer
hunting a Part 1 base for `frames.ts` that they did not need.

**F2 — and the fourth pass's own first instance was also wrong.** It reported
`package.json` as a live collision because this chapter adds two dependencies to
`services/api/package.json`. The post-series entry is for the **root** `package.json`.
Same basename, different file. Corrected before remediation by checking the title
rather than trusting the match.

**The one real collision is `credentials.itest.ts`** — post-series amended by chapter
3.6's baseline, and T025d has to raise the auth threshold in it. It goes to
post-series rather than a chapter fence, because 3.8 teaches rate limiting and not
credential testing (T025e).

**What this says about the process.** Three of the sixteen findings across four
passes were about the fence mechanism, and two of those three were mistakes made
*while fixing* the first. An analysis pass can add defects as well as remove them,
and the ones it adds arrive with the same confident tone as the ones it removes. The
rule that came out of it is in R16: read the script, not the memory of the last time
the script complained.

### The fifth pass, which found something no earlier pass could have

**G1 and G2 — a fifth container, unregistered and unwatched.** `@relay/config`
exports `INFRA_SERVICES` above a comment saying it *names* the local infrastructure
so the workspace need not parse YAML. T041 added Mailpit to `compose.yaml` and
nothing added it to the list, so the constant would have become false. It would also
have had no healthcheck, and `infra.test.ts`'s own comment states the cost: *"if a
healthcheck disappears … `docker compose up -d --wait` would silently stop meaning
ready."* V9 reads Mailpit's API immediately after `--wait`.

**The gate could not have caught either.** `infra.test.ts` asserts that compose
declares every `INFRA_SERVICES` entry — one direction only. A container present in
compose and absent from the list is invisible to it. The reverse assertion is added
with the service (T041c), so the next chapter to add a store is caught by a test
rather than by a fifth analysis pass.

**Where this came from matters more than what it was.** It is in a file — 
`packages/config/src/infra.test.ts` — that none of the four earlier passes had
opened. Passes 1 to 3 read the spec against itself, pass 4 read the previous pass's
remediation, and this one read a package the chapter touches only sideways.

**On when to stop.** Five passes produced 20 findings at a flat rate: 7, 5, 4, 4, 4.
They did not run out; they moved outward, and the last one came from the edge of what
the chapter touches rather than its centre. Stopping here is a judgement about cost —
96 tasks are waiting — and not a claim that the artifacts are clean.

### The sixth pass found the worst defect of all six, and it was self-inflicted

**H1 — R11 invented a capability and built four documents on it.** Pass 1 found a
real ambiguity: which bucket does a REST send decrement? The answer R11 gave justified
two buckets on the grounds that they count different things, with the worked example
*"a batch of ten messages in one request decrements `rest` by 1 and `send` by 10"*.

`sendMessageBodySchema` is a `strictObject` with one `text` field. `messageSendSchema`
on the socket is the same. **There is no batch send on either transport.** So both
counters moved by one together, both defaults were 600, they would have exhausted in
the same instant, and the header rule chose between two identical numbers.

It propagated into FR-008's "distinguishing test" (unwritable), FR-036, SC-002, the
contract's worked example, the quickstart's V1 and T018a — a requirement, a contract,
a verification step and a task, all resting on a request nobody can make.

**The answer that survives.** The send limit counts messages *wherever they enter*: a
REST send decrements both budgets, a socket frame decrements only `send`. That keeps
R11's one real insight — a limit a client can lift by switching transport is not a
limit — and drops the fiction. The two counters now genuinely diverge, so the header
rule has work to do, and the distinguishing test is buildable: five REST sends plus
five socket frames leave `send` at 10 and `rest` at 5.

It also made the design better in a way the first version missed. A socket send is
counted by the **gateway**, against the same key the api uses, because the gateway's
internal call is exempt from customer limits (FR-009). Two services incrementing one
bucket is precisely why that counter belongs in Redis and not in either process — a
justification the first answer never needed to make.

**The lesson, and it is the lesson of all six passes.** Every pass that opened a
source file none of its predecessors had read found something. The spec, plan,
research, contract and quickstart were all written by a process that had never opened
`messages.schema.ts` — the schema for the operation the send limit limits. Reasoning
about a platform from its documents produces text that is internally consistent and
externally false, and the reviews that only read documents cannot tell the difference.

### The seventh pass, and the rule that finally predicted its own findings

The sixth pass ended with an instruction: *read the source of every operation the spec
constrains*, and named three unread files. Reading them produced three findings in the
places predicted — the first time in seven passes a prediction held.

**I1 — `AuthenticateMiddleware` never throws, and T027 asked it to.** Its comment says
so with its reason: *"pre-credential routes (signup, health) are reached that way on
purpose."* R18 moves the refusal to `CredentialGuard`, which already owns the `401` that
FR-028 wants the `429` indistinguishable from, and already throws the object form that
carries a `code`. The invariant survives verbatim.

**J1 — FR-009 exempted something it could not recognise.** The gateway forwards the
**end user's** token on all three of its api calls; `/internal/session`,
`/internal/backfill` and `/internal/messages` are `@Accepts("user")`. Only the
dispatcher carries the platform credential. So a principal-based exemption would have
refused the gateway, a socket send would have cost two slots, and a reconnect storm
would have eaten a customer's request budget — none of it described anywhere. R17
replaces "the internal seam is exempt" with *count each operation once, at the door it
entered*, which is the chapter's own theme rather than a special case.

**I3 — and the routes with no tenant.** `/healthz` must never be limited, because
Docker polls it and `up -d --wait` depends on the answer. Signup is limited per source
IP on the same counter family as failed authentication: no tenant to key on, and an
unlimited account-creation route is not acceptable in a platform that limits everything
else.

**One finding was retracted.** The seventh pass had claimed the gateway presents the
platform credential and receives a hard-coded `service: "dispatcher"`. It does not. That
claim was made by reasoning about `authenticate.middleware.ts` without opening
`api-client.ts`, which is the same error as R11's batch send one pass earlier.

**The rule, stated as narrowly as it deserves.** Findings live wherever the spec
constrains an operation whose source nobody opened, and that set is enumerable — it is
the list of files the tasks touch. The corollary cost one false finding to learn: do not
report a finding about code you have not opened, even when the surrounding code seems to
imply it.

### The eighth pass: an escape hatch that would not have opened

**K1 — Turborepo runs in strict env mode, and this chapter's new variables would have
arrived as `undefined`.** Confirmed by probe rather than by reading documentation: a
task declaring only `RELAY_NATS_URL`, run with that and an undeclared variable set,
printed `nats://declared` and `(undefined)`. R15's whole design — an enforcing default
with a test-visible override — depends on the override reaching the child. It would
not have. T025d would have raised a threshold nothing read, and the suite would have
broken exactly as R15 predicted while appearing to have been fixed.

**K2 — and the same hazard has a second home this project has already been bitten
by.** `packages/e2e/src/harness.ts` forwards an explicit allowlist, above a comment
naming the incident: *"turbo runs tasks in strict env mode, the port variable was
filtered out, and the harness confidently passed `localhost:5432` to an api that would
have found the right store on its own."* Nine variables, each tagged with the chapter
that added it. This chapter adds three.

**Neither list is a gate.** Nothing fails loudly when somebody forgets to extend them;
a missing variable is `undefined` and the `??` behind it wins. R19 names that as a
defect in the test harness rather than in this chapter, and declines to fix it here —
a chapter about rate limits is not where a test-infrastructure gate belongs.

**The method mattered more than the finding.** Two earlier findings were retracted
because they were reasoned from surrounding code rather than read. This one was a
three-line probe task, run and then reverted. The difference between K1 and those two
is about four minutes of work.

### The ninth pass: the first genuine constitution finding, and it was in a config file

Nothing was wrong with the documents. What the pass found was two mechanisms the **code**
uses to enforce its own rules, neither mentioned in any spec, and a new component that
sidesteps both.

**L1 — the driver boundary is four lines of eslint config.** `pg` and `drizzle-orm` are
restricted everywhere except `services/api/src/db/**`, above a comment citing the
principle: *"Isolation lives in data access, not in handlers (constitution I)."* This
chapter gives the api a second per-tenant store keyed `rl:{environment_id}:…`, and left
`ioredis` unrestricted — so any controller could have read or written any environment's
counter. **Constitution I is non-negotiable**, and this is the first finding in nine
passes that engages it directly. FR-042 and T012a.

**L2 — every long-lived resource closes through `OnModuleDestroy`.** Three api modules
implement it and every api suite ends `await app.close()`. An `ioredis` client holds the
event loop open, so without a hook the suites would hang **after their assertions
pass** — green tests, and a lane that never returns, in a project that spent three
chapters clearing one. FR-043 and T012b.

**L3 — and the gateway cannot borrow fanout's clients.** `Fanout` is a closed interface
exposing neither; one of the two is a subscriber and a connection in subscribe mode
cannot run `INCR`; and `fanout` is optional in the session server, so a limiter riding
its lifecycle would vanish in every chapter-2.5 configuration. Its own client, its own
`close()`.

**What this changes about where to look.** The first eight passes found things by reading
source files. This one found things by reading **self-enforcing conventions** — a lint
rule and an interface — that no requirement mentions and that a component can violate
while satisfying every document in the feature. The remaining quiet enforcers are the
coverage ratchets, `check:docs`, and whatever `scripts/` the lane runs. None has been read
for what it would demand of a new component.

### The tenth pass: the fifth instance of one shape, and a gate I over-cited

**M1 — two vitest configs disagree, and the difference was the finding.** The coverage
config sets `fileParallelism: false` above a comment naming the incident it came from;
`services/api/vitest.integration.config.mts` sets only `include`, so **the lane runs
files in parallel**. Every suite asserting a `401` increments one
`rlauth:127.0.0.1:{window}` bucket, concurrently, from different workers.

Raising a threshold survives that — a high ceiling never refuses however polluted the
count. **Lowering one does not**, and R15's plan lowered it in `limits.itest.ts`, which
would have compared a count filled by other workers against a deliberately small number
and refused requests that had nothing to do with it. Intermittently, depending on which
worker ran first.

**This chapter would have created the fifth instance of a shape it already knows.**
Chapter 3.7's baseline found four — a sweep with a batch limit, a drain holding a lock, a
consumer draining a growing stream on a fixed budget, a global `count(*)` compared against
itself — all tests asserting a local fact about a global operation. The fifth would have
been in the test for the very mechanism this chapter is about. The fix is a private key
rather than a private threshold, and it is already in the codebase twice: `attempts.itest.ts`
carries `const SUITE = "itest-attempts"` for the same reason.

**M3 — and a note about this feature's own reporting.** `pnpm check:docs` globs
`0[1-6]-*.md`. This chapter edits `docs/07-tutorial-plan.md`, which is not in the mirror
set. Ten consecutive reports cited that gate passing as evidence; it was never a false
claim, and it was thinner than repeating it implied. T069a now says to read the plan
rather than cite the gate.

**The enforcer sweep is finished.** Both vitest configs, `check-docs-drift.sh`, and the
ten `scripts/*.mjs` walks — none of which this chapter touches. The one that mattered was
a single line present in one config and absent from the other.

### One requirement carries a claim that may be wrong, on purpose

The Assumptions say this renumbering should be cheap because chapter 3.7 removed
every forward chapter reference from live source, so no fenced file should need
amending. FR-035 and SC-009 test that claim rather than trusting it. If a fence
amendment turns out to be needed anyway, that is a finding about whether 3.7's
rule actually paid for itself — which is worth more than a renumbering that went
smoothly.

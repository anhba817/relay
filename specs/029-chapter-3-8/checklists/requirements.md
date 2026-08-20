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
keeps finding at the sabotage battery, and both now have tasks (T018c, T025a).

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

### The eleventh pass found only damage from the previous ten

Nothing about the platform. Three findings, all self-inflicted by remediation.

**N1 and N3 — two hand-written counts, stale for the third time each.** R10's fence
estimate went 23 → 28 → 33 as later passes added files earlier chapters had already
fenced; T061's "eight are worth naming" became eleven. Each went stale the same way: a
remediation added an item *below* the sentence stating how many there were.

Both are now fixed as a class rather than as instances. T058 **derives** the fence count
from the page instead of comparing against a written total, and T061 states no number at
all. A written total describing something a document also enumerates is a second source
of truth — which is the fault this feature has diagnosed in five other places and had
twice committed itself.

**N2 — a task that could not pass where it sat.** T011a asserted that a lowered limit
*refuses* a request, from Phase 2, whose checkpoint reads *"nothing has been limited
yet"*. The refusal needs the middleware Phase 3 builds. Pass 1 had placed it beside the
policy tasks it related to rather than after the mechanism it needed. Now T018c.

**E5 was already closed and did not need remediation.** The sixth pass's rewrite of
FR-036 covers the socket case explicitly — *"a `message.send` frame on an open socket
decrements the send limit only"* — so the item carried on three reports as open had been
resolved by work done for a different finding. Checked before editing rather than after.

**Where eleven passes ended.** 42 findings, 2 retracted. The productive question changed
three times — read the spec against itself, read the source of every constrained
operation, read the conventions the code enforces on itself — and then ran out. This pass
had no fourth question and found only accretion, which is the signal to stop.

### The twelfth pass: the constitution had a half nobody had read

Eleven passes checked this feature against the constitution's **seven principles**. None
opened the eighty lines after them — Technology & Platform Constraints, Development
Workflow & Quality Gates, Governance. Reading them produced the first genuine conflict in
twelve passes and a gap in the one command the constitution insists must work.

**P1 — the connect limit contradicts a deployment gate.** *"Deploys cause no message loss
and at most one client reconnection cycle."* A connect limit of 60/min/environment
refuses the surplus when a deploy reconnects every client at once, and refused clients
come back — a second cycle. (**The fourteenth pass raised the default to 3,000/min** and
found the requirement's own id, NFR-REL-03; the residual conflict is smaller and still
recorded.)

**And the gate has no implementation.** `CLOSE_CODES[4009]` reads "server shutdown
(drain)" and nothing emits it. So the conflict is with a promise nothing yet keeps, which
makes **4009 the fourth code declared in chapter 1.3 and never wired**, beside
`rate_limited`, 4008 and `request_id`. Three of the four are in one file. This chapter
enforces one, closes one, and can now say exactly what the other two wait for: 4008 needs
a quota, 4009 needs a drain.

Handled the way the constitution prescribes for itself — recorded in the plan's
Complexity Tracking table with its justification, and FR-045 states the requirement for
whichever chapter builds a drain. Not papered over, and not fixed by shipping a
drain-grace *reader* for a flag nothing writes, which would be the fifth instance of the
habit this chapter is about.

**P2 — `docker compose up` would have started a limiter that enforces nothing.** The
compose `api` service has no Redis, because until now the api needed none. With
`RELAY_REDIS_URL` falling through to `localhost`, and FR-010 failing open by design, the
composed stack would serve everything unlimited **while reporting a limit**. Not a crash;
the chapter's own degraded mode, permanently.

**I got half of P2 wrong when I reported it** and corrected it before acting: the report
claimed the `gateway` service had the same gap. It does not — chapter 2.6 gave it
`RELAY_REDIS_URL` and `depends_on: redis` for fan-out. Checked the file rather than
assuming symmetry, which is the habit the two earlier retractions bought.

**On having recommended stopping.** The eleventh pass ended with "the artifacts are now
wrong about nothing I can find". That conclusion rested on having read the constitution's
principles eleven times and its gates never. The lesson is the one passes 6 and 7 taught
about source files, applied to a document: **I had been reasoning about the constitution
from the part of it I had read.**

### The thirteenth pass: the persona document had this chapter's user in it

`docs/03-journey-map.md` is cited by the SRS as the source of FR-RTL-06's reasoning and is
one of six documents `check:docs` mirrors. Thirteen passes never opened it. Its **Test
phase** is four lines describing this chapter's user doing this chapter's thing — *"load
testing, verifying rate limit behaviour"*, touchpoint *"rate limit headers"* — and two of
its four pain points are this chapter's subject.

**Q2 — the spec understated FR-RTL-04.** The journey map asks for *"fully isolated dev and
production environments with separate keys and **separate quotas**"*, against the pain
*"shared dev and production quotas, so load testing risks her live environment"*. FR-006
and SC-003 covered independent **counters**; the policy is three nullable columns per
environment and nothing tested that two environments could carry **different configured
limits**. The capability existed; the requirement stopped one step short of what the
persona needs, which is to raise her dev ceiling without moving production's. T017a.

**Q3 — and the default was reasoned about the wrong user.** R4 justified 600/min as
"generous for the integration this platform is sold for". The journey map says the one
user who will drive a limit deliberately is a developer load-testing a dev environment.
Not a reason to raise the default — a reason for the chapter to say the number is hers
(FR-046).

**Q1 — the error page that does not exist, and stays that way.** Constitution V requires
every error code have a reachable documentation page. This chapter ships `rate_limited` as
the first code a developer receives routinely and looks up, pointing at a placeholder
`docs_url` that has been a placeholder since chapter 1.4. **The placeholder is kept by
decision** — a docs site is not this chapter's to build — and FR-047 records the gap so
the URL does not imply otherwise. A fifth thing declared and not enforced, except this one
is a promise in the constitution rather than a constant in `codes.ts`.

**What thirteen passes have established about where findings live.** Four times now the
productive move has been to open a document or file that every previous pass had reasoned
about without reading: the send schema (pass 6), the gateway's api client (7), the
constitution's gates (12), the journey map (13). Each time the artifacts were internally
consistent and wrong about something outside them. The set of unread things is finite and
enumerable, and it has been the whole answer since pass 6.

### The fourteenth pass: three numbers were fine and one was not, for the same reason

Reading the SRS's **NFR tables** — repeatedly read FR tables, never once the NFRs — found
that R4's connect default made a P1 requirement unreachable.

**R1.** NFR-SCL-01: *"10,000 concurrent WebSocket connections per gateway instance"*, and
FR-RTM-09 allows five per user. At 60 establishments a minute, filling one instance takes
**167 minutes**; an environment of 5,000 users at five connections each takes over six
hours. Pass 12 had found the same default conflicting with a deployment gate and I
recorded it as a one-off. It was the first symptom: **R4 chose all four numbers by
reasoning about a client, and the limit is per tenant.**

So all four were re-derived (R26) rather than the broken one patched. Sends are 1% of
NFR-SCL-03's stated 1,000/s aggregate; connect became **3,000/min**, sized from
NFR-SCL-01 ÷ FR-RTM-09; failed auth stays 10/min per IP by judgement, now with its
shared-NAT cost named. **The REST limit has no anchor at all**, and R26 says so instead of
inventing one.

The fix is not the new number. It is that each default now states what it rests on,
including the one that rests on nothing.

**R2 and R3 — two requirements cited by paraphrase.** FR-045 quoted the constitution's
Quality Gates and never NFR-REL-03, the numbered P2 requirement that says the same thing;
FR-013 quoted the constitution's observability line and missed that **NFR-OBS-01** asks
for a third field, a correlation id, which the platform does not mint. T063 checks that
every identifier the chapter *cites* resolves. Neither of these was a citation — they were
paraphrases of requirements that exist.

### The fifteenth pass: the error envelope had the wrong shape in the document

Reading the SRS's **§3, External Interface Requirements** — skipped by fourteen passes
that read §4 and §5 repeatedly — found EIR-API-04's worked example nesting the error
body's fields under an `error` key. `ProtocolErrorFilter` has emitted them flat since the
walking skeleton, and `service-kit`'s 404 does the same. A P1 requirement verified by
Test, disagreeing with the code for fourteen chapters, and nothing had resolved it.

**This chapter would have made it worse**, adding `request_id` as a fourth field to a
shape already structurally wrong and publishing the flat form in a contract document.

**Resolved by amending the SRS to 1.3**, which is the route the constitution's Governance
names: *"where it conflicts with the SRS or SAD, the conflict MUST be resolved explicitly
by amendment rather than ignored."* Wrapping the body would have been a breaking change,
and CON-05 makes breaking changes a URL-versioning event — far outside a rate-limiting
chapter.

Flat is also the better shape rather than merely the shipped one. The same five fields
travel on the socket inside a frame's `payload`, and the filter's own comment gives the
reason: *"one error shape, one home … so the REST surface and the WebSocket surface
cannot drift apart."* Nesting the REST body would make them differ in two ways instead of
one.

**Two smaller things fell out.** The SRS's version line still read 1.0 after two prior
amendments recorded in Appendix D — now 1.3. And the mirror had to be re-synced, because
`docs/04-srs.md` is one of six documents `check:docs` compares; amending the source alone
would have broken a gate that had passed for fifteen passes.

### The sixteenth pass: a stale count this feature walked past twice

**T1 — the tutorial plan's summary said Part 3 was 7 chapters and the series 51.** It is
10 and 54. Three insertions moved it — 3.6, 3.7, and this feature's quotas split — and
each edited the chapter *table* twelve lines below while leaving the summary alone. **Two
of the three were this feature's own commits.**

It is the exact class the eleventh pass diagnosed and fixed twice: a hand-written total
describing something the same document enumerates. R10's fence estimate was made to derive
itself and T061's count was deleted — while this one sat above a table the same commits
were editing. `check:docs` does not cover `07-tutorial-plan.md` either (R22), so nothing
caught it for three chapters.

Corrected and then **verified by counting rows** rather than by re-reading the summary:
all nine part counts and the total now agree.

**T2 — this chapter completes SRS Phase 2, and nothing said so.** §7.3 lists Phase 2 as
FR-TEN, FR-AUT, FR-WHK and FR-RTL at P2; the other three groups landed in 3.1, 3.2 and
3.5, so FR-RTL-01…04 is the last of them. The plan already had the convention — 2.8's row
reads *"This chapter **is** the SRS Phase 1 exit criterion"* — and no row named Phase 2's.
Both now do: 3.8 completes the set, 3.10 runs the test.

**T3 — and the two collide.** Phase 2 exits on *"an external developer integrates using
only public documentation, with no assistance"*. This chapter ships `rate_limited` as the
first error code an integrating developer will receive and look up, pointing at a
`docs_url` that resolves to nothing. FR-047 already recorded the placeholder; §7.3 is what
makes it expensive rather than untidy — **the phase whose exit criterion is public
documentation is completed by a chapter that documents an error code nowhere.**

Recorded, not solved. A docs site is not a chapter of this series and half of one would be
Part 3's fifth unfinished mechanism.

### The seventeenth pass: an open question the chapter's own design forecloses

**SRS Appendix C question 5**, never opened before: *"Should the dev-mode token endpoint
(FR-AUT-09) be rate limited more aggressively to prevent production misuse?"* — **Blocks
FR-AUT-12**, which is one of this chapter's requirements.

The interesting half is not the question. It is that **this chapter cannot answer it, for
a reason nobody noticed while choosing the design.** The policy is three nullable columns
on `environments`, so it has a slot for an environment and none for a route. "More
aggressive on one route" is unrepresentable.

The shape is still right — FR-RTL-04's isolation is per environment, one row per
environment, and a separate table would be a join on every request. What was missing is
that the choice foreclosed an open question the SRS lists as blocked on this requirement.

What the chapter *does* change: the route had no limit at all and now carries its
environment's REST limit. So the baseline moved and the remaining work is priced — a
fourth policy dimension — which is more than the question had before. Recorded and left
to Security, which the SRS names as its owner.

**Appendices B and C otherwise clear.** The exclusions bear on nothing here; the other
five open questions block FR-MSG, FR-RTM, FR-ANL and FR-EMJ.

### One requirement carries a claim that may be wrong, on purpose

The Assumptions say this renumbering should be cheap because chapter 3.7 removed
every forward chapter reference from live source, so no fenced file should need
amending. FR-035 and SC-009 test that claim rather than trusting it. If a fence
amendment turns out to be needed anyway, that is a finding about whether 3.7's
rule actually paid for itself — which is worth more than a renumbering that went
smoothly.

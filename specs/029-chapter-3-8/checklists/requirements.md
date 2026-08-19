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
3.6's baseline, and T025c has to raise the auth threshold in it. It goes to
post-series rather than a chapter fence, because 3.8 teaches rate limiting and not
credential testing (T025d).

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

### One requirement carries a claim that may be wrong, on purpose

The Assumptions say this renumbering should be cheap because chapter 3.7 removed
every forward chapter reference from live source, so no fenced file should need
amending. FR-035 and SC-009 test that claim rather than trusting it. If a fence
amendment turns out to be needed anyway, that is a finding about whether 3.7's
rule actually paid for itself — which is worth more than a renumbering that went
smoothly.

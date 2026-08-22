# Specification Quality Checklist: Chapter 3.11 — Counting a connection

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-22
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

**Two scope decisions were taken before the spec was written, not assumed.**
Both were put to the author and both are recorded in Assumptions with what the
alternative would have cost:

- **A connection-minute is a wall-clock minute bucket, charged per connection.**
  A five-second socket costs one minute; a socket open from 00:00:59 to 00:01:01
  costs two. The alternatives were accumulating seconds and rounding per
  connection, or accumulating seconds and rounding once at read. The bucket model
  charges reconnect churn, which the third does not, and the identity of a minute
  is the natural key for deduplicating a repeated report.
- **A connection-minutes hard cap refuses new connections, not sends.** FR-RTL-08
  literally says quota exhaustion rejects sends, and a defensible reading is that
  every dimension degrades that one way. It was rejected because a cap that only
  refuses sends leaves an idle listener burning the metered resource with no brake,
  so the cap would not bound the thing it meters.

**This also answers a question `docs/04-srs.md` records as open** — number 4,
"does connection-minute metering need per-second precision", addressed to Product
and Billing. FR-028 requires the chapter to answer it in print rather than to
answer it silently in code.

**Five requirements had no measurable outcome on the first pass** and got one:
FR-004 (the observing service gains no database) → SC-018, FR-010 (accounting
state bounded by connections, not minutes) → SC-017, FR-012 (a metering failure
cannot break traffic) → SC-019, FR-021 (a soft threshold refuses nothing) →
SC-020, and FR-026 (the figure survives a counter-store flush) → SC-016. FR-026
is chapter 3.10's central criterion and it had been carried into this spec as a
requirement with nothing checking it, which is how a durability claim becomes
decoration.

**Four items sit close to the "no implementation details" line** and are kept,
because deleting them would delete the constraint rather than the detail:

- **SC-012** names `EXPLAIN (ANALYZE, BUFFERS)`. It is an instrument, and it is
  the only instrument that can show the absence of a scan; a clock cannot. Chapter
  3.10's SC-006 was corrected mid-cycle for exactly that confusion.
- **SC-018** names a lint rule. The rule is the whole subject of the chapter
  expressed as a build gate, and the temptation this chapter creates — give the
  gateway a database, it is the only thing that can see a connection — is
  precisely what the rule exists to refuse.
- **FR-027** names feature 030's exemption list. A property of the test lane the
  chapter must satisfy, not a design choice it makes.
- **FR-003** requires the definition of "which minute" to be usable from tests
  without waiting in real time. That reads as a testability constraint and is one;
  it is also the difference between a suite that runs in three minutes and one
  that cannot express its own acceptance scenarios.

**Where the spec is weakest.** Three requirements — FR-019, FR-024 and FR-028 —
require the chapter to *state* something rather than to *do* something. They are
checkable by reading and they are how this series records a cost instead of
discovering it later. FR-024 in particular asks the chapter to compare what the
third dimension actually cost against chapter 3.10's written prediction of "a new
key plus a one-line constraint change", and says a higher number is a result. A
prediction nobody checks is not a prediction.

**What the spec cannot settle and hands to the plan.** Whether a report naming a
connection the api has never seen is accepted or refused; the reporting interval;
what the gateway does with reports it cannot deliver; and the bound on clock skew
between instances. All four are in Edge Cases as decisions the plan must make and
state, not as gaps.

**SC-015 cannot be evaluated until the chapter is written.** It is the size gate,
counted on the finished page. Three of Part 3's four splits were discovered
mid-chapter; chapter 3.10's estimate ran 18% high against the page it produced.


## First analysis pass, 2026-08-22

Nineteen findings — one CRITICAL, six HIGH, nine MEDIUM, three LOW — no
constitution violation. All nineteen applied.

**This pass read the documents against each other AND against the published
series, which is the surface chapter 3.10 discovered last.** That ordering was
deliberate and it paid: two of the nineteen are shipped chapters asserting facts
this one falsifies, and one of them names a file that appeared in none of my
inventories.

**C1 was a correctness gap, not a wording one, and it is the reason to run this
pass at all.** `session.ts` removes a connection from the registry on the line
after its `close` handler opens, and the meter walks the registry — so a socket
that opened and closed between two reports was counted **zero**. FR-002 says a
five-second socket costs one minute. Worse, it failed at the one thing R2 chose
the bucket model *for*: the comparison table there argues the model charges
reconnect churn where summing seconds does not, and under a registry-only meter a
thousand five-second sockets would have cost nothing. Fixing it forced R3 to be
narrowed in print — "reports carry totals so nothing is queued" is true of open
connections and false of closed ones, because a closed connection has no next
report to repair a lost one.

**Three HIGH findings were one file nobody had opened.** `quotas/quota.error.ts`
holds a two-way ternary — `dimension === "messages" ? "message" : "active user"` —
so a connection-minutes breach would have rendered "monthly **active user** quota
exhausted", and `Dimension` is `keyof QuotaConfig`, so it widens on its own and
the compiler catches nothing. The same file says "sends resume on" twice, and what
resumes for this dimension is connecting. And `contracts/metering.md` had
paraphrased the message format from memory rather than quoting it. Chapter 3.10's
second pass found this class and called it "a claim the plan made confidently
about architecture nobody had opened"; the difference is that this pass opened it.

**H1 is the expensive one.** Chapter 3.8 fenced
`services/api/src/limits/rate-limit.middleware.ts` with a comment saying the
gateway "forwards the END USER's token on all three of its api calls" and that
"Only the dispatcher carries the platform credential". This chapter adds a fourth
call and a second holder. The middleware's behaviour is unaffected —
`operationsFor` returns `[]` for anything outside `/v1/` — but the sentence stops
being true, and the file was in neither the plan's structure tree nor R16's fence
table. Twelve files at 62 fences became thirteen at 66.

**Two findings were my own numbers being wrong**, which is worth recording
because this series claims to say the number instead of the adjective. The plan
called `usage_connections` "a fifth usage table" when it is the fourth, and three
of the phase-to-requirement mappings pointed at phases that do not contain the
work.

**One finding was a task that pre-answered its own measurement.** T066 said "count
the six places", which is the prediction FR-024 asks to be tested, not the result.

The counts moved: 28 requirements to 29, 20 success criteria to 21, 95 tasks to
103, and research grew R19 and R20 — the close path, and the unseen-connection
decision the specification had asked the plan to make and the plan had not made.

## Second analysis pass, 2026-08-22

Thirteen findings — one CRITICAL, five HIGH, five MEDIUM, two LOW — no
constitution violation. All thirteen applied.

**Pass 1 read the documents against each other and against the published prose.
This pass read them against the code, systematically: every file the plan claims
to touch, opened, and every claim checked against what is in it.** The two passes
found different classes of thing, and the second class could not have been found
by reading.

**C2 is the one worth the pass on its own, and it is a gap no test could have
caught.** Four documents said the gateway flushes a final report on shutdown —
R11, FR-008, `contracts/metering.md` §5, and the task that wires it. They agreed
with each other, which is what reading them against each other proves. `serve()`
returns a bare `node:http` Server, nothing in the gateway ever calls
`server.close()`, and only the dispatcher installs signal handlers. On
`docker stop` the process exits and the handler the flush was hung on never runs.
The guarantee had no mechanism, and no test would have failed, because no test
sends a signal.

**Four findings were one decision the plan made without consulting the protocol.**
`CLOSE_CODES` has held `4008: "quota exhausted"` since chapter 1.3 and nothing
emits it. `docs/04-srs.md:226` — EIR-WS-06 — requires close codes to distinguish
quota exhaustion. `session.test.ts:929` is a live test asserting nothing emits it,
whose comment reads "quotas are a later chapter". And chapter 3.8's own comment
says its refusal is raw HTTP *because* it needs a `Retry-After`, which this
chapter's contract explicitly declines while keeping the shape.

The plan had written one refusal where there are two hops. The api speaks HTTP and
answers 402; the client speaks WebSocket and now gets an error frame and close
4008. That reaches a browser, where the raw refusal the contract itself admitted
was invisible does not.

**Two findings were my own numbers, again.** R16's fence table said thirteen files
at 66 — and the row pass 1 added for `rate-limit.middleware.ts` asserted four
fences without counting. It has one. Counted properly, with the four files this
pass added, it is **seventeen files and 77 fences**. A table of numbers assembled
from memory is the thing this series says not to do, and it has now been wrong
twice in two passes.

**One finding was a test resting on infrastructure that does not exist.** T041
verifies SC-005 by killing the gateway. Both gateway integration suites spawn *the
api* as a child and run the gateway in-process, so there was no gateway process to
kill. The spawn pattern to copy exists; nothing pointed it at the gateway.

The counts moved: 29 requirements to 31, 21 success criteria to 23, 103 tasks to
110, and research gained R21 while R11 was rewritten around the handler it assumed.

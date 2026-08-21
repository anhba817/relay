<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/032-chapter-3-11/plan.md` (chapter 3.11, "Counting a connection" — the
third dimension of FR-RTL-05, a PUBLISHED chapter, so its fences belong in the
chapter that teaches them and NOT in `fences/post-series.md`).

THE CHAPTER'S SPINE: messages and users were already rows, so counting them was
an aggregation question. A CONNECTION IS NOT A ROW ANYWHERE, and the only process
that can see one is the gateway, WHICH OWNS NO TABLES (ADR-05, and the chapter
2.1 lint ban makes a database import a build failure). So the subject is not
counting — it is metering from a service that cannot write: what it has to say,
how often, and what happens to the number when the thing saying it dies
mid-sentence.

TWO SCOPE DECISIONS TAKEN BY THE AUTHOR BEFORE A WORD WAS WRITTEN:
(1) A connection-minute is a WALL-CLOCK MINUTE BUCKET, CHARGED PER CONNECTION. A
five-second socket costs one minute; 00:00:59 to 00:01:01 costs two; a hundred
concurrent sockets for one minute cost a hundred. This answers `docs/04-srs.md`'s
OPEN QUESTION 4 in print (FR-028), charges reconnect churn, and makes the dedup
key fall out of the unit.
(2) A hard cap REFUSES NEW CONNECTIONS, not sends. Each dimension refuses the
operation that consumes it. Open sockets stay open, keep delivering AND KEEP
ACCRUING — so FR-019 owes a stated overshoot bound whose right-hand side has no
numeric ceiling, and saying that beats inventing a number.

SEVEN MEASURED DECISIONS, all in `research.md`:
(R1) THE GATEWAY HAS NEVER SPOKEN FOR ITSELF. Every internal call forwards the
END USER'S token — `api-client.ts` says it "holds no secret that could" verify
one. A report is nobody's user action, and reporting per connection with that
connection's token fails hardest on the long-lived socket whose token expired,
which is the one with the most minutes on it. Chapter 3.5 already built the class:
`PlatformPrincipal`, `@Accepts("platform")`, `rk_svc_`. The gateway becomes its
SECOND holder — one compose line, one turbo env entry, one config read.
(R1a) `resolvePlatformCredential` returns a HARDCODED `service: "dispatcher"`,
and that field is documented as "which internal service presented it". A second
caller makes it a lie. ONE CREDENTIAL PER SERVICE — a caller-asserted header is
the pattern 3.2 spent itself removing.
(R3) REPORTS CARRY TOTALS, NOT DELTAS, and that DELETES THE RETRY BUFFER. Lost
report → repaired by the next. Repeated → credits max(0, reported − credited) = 0.
Undeliverable → DROPPED, not queued. The gateway keeps no outbox, which is the
right amount of durable state for a service designed to hold none.
(R4) IDEMPOTENCY STATE IS ONE ROW PER CONNECTION PER PERIOD, NOT PER MINUTE. The
naive key is 43.2M rows/month at 1,000 concurrent sockets — 3.10's R1 argument in
a new costume. `usage_connections` PK `(connection_id, period)`.
(R5) STILL NO SWEEP, for the second chapter running. Usage rises only on a
report; the report transaction knows before and after, so it writes its own
crossings. V7 exists to falsify this.
(R5a) AND 3.10 LEFT A GAP: it added three environment-scoped tables and extended
feature 030's guard to NONE. Its SC-008 read "no new file joins the exemption
list", which passed, is true, and is quieter than it sounds. Extending the guard
is NOT a one-line array change — the refusal interpolates `OLD.id` and
`usage_periods` has no `id` column. Recorded, not fixed here.
(R6/R7) ENFORCED AT THE DOOR, in `POST /internal/session` — which adds a usage
read to THE EXACT PATH 3.10's H2 protected from one, and makes `Authentication`
grow a FOURTH OUTCOME: a 402 today becomes `ApiError` → `unavailable` → close
1011, "we are broken, retry", wrong twice.
(R8) `Repository` IS ENVIRONMENT-SCOPED BY CONSTRUCTION and a platform principal
carries no environment, so `recordCrossings` and `organisationOf` come out as
standalone functions. ~40 lines moved, no behaviour changed.

THE PREDICTION THIS CHAPTER CHECKS (R15, FR-024, SC-013): 3.10 wrote — twice, in
`0009_quotas.sql` and `quotas/config.ts` — that a third dimension costs "a new
key plus a one-line constraint change". It is SIX PLACES. Count what it really
costs and write the number down; a higher number is the RESULT, not a failure.

FENCE SURFACE COUNTED UP FRONT (R16): twelve files this chapter touches already
carry 62 titled fences. The chain applies HUNKED DIFFS, so the cost is one diff
fence per changed region — but 3.10's third pass found NO TASK WROTE THE FENCES
and called it the most expensive finding of three passes, because it surfaces
after the chapter is written AND TRANSLATED.

PHASE ORDER PUTS THE NOTIFICATION STORY LAST (Phase 7) because it is the seam and
is almost entirely reuse. PHASE 3 IS EARLY on purpose — the credential gates every
integration test in Phases 4 to 7. Estimate is 3,000-3,600 prose words against a
2,000-4,000 gate COUNTED ON THE FINISHED PAGE; 3.10's estimate ran 18% high.
<!-- SPECKIT END -->

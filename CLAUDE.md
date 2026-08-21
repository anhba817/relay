<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/031-chapter-3-10/plan.md` (chapter 3.10, "Quotas and what they cost" —
FR-RTL-05 to FR-RTL-08, a PUBLISHED chapter, so its fences belong in the chapter
that teaches them and NOT in `fences/post-series.md`).

THE CHAPTER'S SPINE: a rate limit is about THIS SECOND and forgets; a quota is
about THIS MONTH and must not. Chapter 3.8 built the limiter; this is the other
half of FR-RTL and the two are different problems wearing the same word.

SCOPE, decided before a word was written: messages sent and distinct active users.
CONNECTION-MINUTES IS CHAPTER 3.11 — scheduled with a number, not deferred to a
promise, and the isolation gauntlet moved to 3.12 to make room. Messages and users
are already rows (`messages.user_id` has been in `0000_core_tables.sql` since Part
2); a connection-minute is a duration nothing records, and the service that would
record it is the gateway, WHICH OWNS NO TABLES. THE CAP IS DENOMINATED IN METERED
UNITS, NOT MONEY: no price, unit cost or currency appears in the SRS or SAD, and
inventing a pricing primitive is scope constitution VII would ask to justify.

FOUR MEASURED DECISIONS, all in `research.md`:
(R1) Usage is a ROLL-UP, not derived on read. `select count(*), count(distinct
user_id)` scoped to one environment measures 1.189ms today — and `messages` carries
NO `environment_id` (it hangs off `channels`) and NO index on `created_at`, so the
work is proportional to the tenant's LIFETIME traffic. That is this project's
eleven-times-recorded fault written into the product instead of into a test.
(R3) Enforced in `Repository.sendMessage`, NOT in middleware. `operationsFor`
returns [] for anything outside `/v1`, so chapter 3.8's limiter NEVER SEES
`/internal/messages` — the route a WebSocket send arrives on. `sendMessage` is the
one point both doors pass through and it already owns the write transaction, so the
check and the increment commit together. Cost: the refusal is raised in the
repository layer and mapped in two controllers.
(R5) THERE IS NO SWEEP, and that is the interesting result. Usage rises only on a
send, and the send transaction knows the value before and after — so it knows which
thresholds it crossed and writes the notification rows itself. Feature 030's guard
is engaged NOWHERE and no file joins its exemption list. The first chapter written
after that feature turns out not to need a global operation, which is the outcome
its SC-008 hoped for and could not measure. V8 of the quickstart exists to find out
this prediction is wrong.
(R2) The distinct-user count CANNOT be an increment — it needs to know whether this
user already sent this period. A membership row per user per period, `ON CONFLICT
DO NOTHING`, bounded by the tenant's user count rather than their traffic.
HyperLogLog in Redis is refused by FR-002: a flush would erase the month.

THE OUTBOX PATTERN A FOURTH TIME (R6), in `quota_notifications` —
`webhook_disable_notifications` cannot be reused because `endpoint_id` is NOT NULL.
Four concrete tables that look alike is a pattern; one abstract table serving four
purposes is a framework. Say the number out loud in the chapter.

The refusal is `402`, NOT `429` (contracts/quota.md): a client that retries after
`Retry-After` is right for a rate limit and wrong for a quota, which will still be
exceeded in an hour. No `Retry-After` header — the resume date is in the message.
Its `docs_url` resolves to nothing, exactly as `rate_limited`'s does; inherited
deliberately, recorded in R10, and chapter 3.12's problem.

PHASE ORDER PUTS THE NOTIFICATION STORY LAST because it is the seam. Estimate is
3,000-3,600 prose words against a 2,000-4,000 gate COUNTED ON THE FINISHED PAGE —
three of Part 3's four splits were discovered mid-chapter and this sequencing is
what catches the fourth.
<!-- SPECKIT END -->

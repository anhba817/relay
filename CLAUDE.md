<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/026-chapter-3-5/plan.md` (feature: Tutorial Chapter 3.5 — "Webhooks
that survive the customer": webhook endpoints with envelope-encrypted,
rotatable signing secrets, and a NEW deployable dispatcher service —
frameworkless per ADR-15, zero new dependencies — that consumes the event
stream, signs with HMAC-SHA256, posts, and dead-letters what never succeeds.
R1 was RE-PLANNED after measurement: a broker-held delay survives a restart to
3 ms but holds an acknowledgement slot while it waits, so dead endpoints starve
healthy ones. The six-tier retry schedule is therefore a `next_attempt_at`
column on `webhook_deliveries`, drained by a second relay in the api —
chapter 3.3's `SELECT … FOR UPDATE SKIP LOCKED` loop with one more predicate.
Expansion writes N delivery rows in the claim transaction rather than N stream
publishes, which removes a dual write the first plan had accepted. Chapter 3.4's claim-and-effect-
in-one-transaction pattern stops applying twice over: the effect is on a
machine the platform does not own, and constitution IV reserves PostgreSQL
writes to the API service, so the dispatcher reaches state only over the
internal seam. At-least-once at the customer hop, stated, with the
deduplication identifier handed over. Both locales; spec, research, data
model, two contracts, and quickstart live alongside it. Attempt log
(FR-WHK-06) and auto-disable (FR-WHK-07) are deliberately deferred to a
follow-on chapter).
Project principles: `.specify/memory/constitution.md`.
<!-- SPECKIT END -->

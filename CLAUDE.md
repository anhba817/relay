<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/029-chapter-3-8/plan.md` (feature: Tutorial Chapter 3.8 — "Limits you can
see coming": per-environment FIXED-WINDOW counters in Redis (`rl:{env}:{op}:{window}`,
INCR + EXPIRE, no Lua) on REST requests, message sends and connection
establishment, with `X-RateLimit-Limit/-Remaining/-Reset` on 2xx AS WELL AS 429 —
that is FR-RTL-02 and the requirement an afterthought passes. Fixed window, not a
token bucket, because `Reset` must name one moment and a refilling bucket's honest
answer is a curve; the cost is up to 2x the limit across a window boundary and the
chapter states it. Policy lives in Postgres as three NULLABLE columns on
`environments` (null = use default; null is NOT zero, because refuse-everything
must stay expressible). Defaults 600/600/60 per minute, 10 failed auths per IP.
THE CHAPTER'S ARGUMENT IS THE FAILURE DIRECTION: the tenant limiter FAILS OPEN
(Redis is not a source of truth, SAD §6.3 — a cache outage must not refuse paid
traffic) and the auth limiter MUST NOT (failing open there is a hole, not a
degradation). Research R3 settled the third answer: an in-process fallback counter,
same threshold, so the guarantee weakens from N/window/fleet to N/window/instance —
bounded, capped, and it STOPS ADMITTING new keys rather than evicting, because
eviction is what an attacker drives. Two middleware positions, forced: the tenant
limiter after `AuthenticateMiddleware` (needs the principal), the auth counter
inside it (must work when there is none). RESEARCH R5 FOUND A SECOND UNENFORCED
CONTRACT: constitution V's error envelope has been THREE fields since chapter 1.3,
above a comment promising `request_id` "joins in Part 2, when a gateway exists to
mint one" — it never did. Added to EVERY error response, not just the 429
(`frames.ts`, `protocol-error.filter.ts`, `service-kit`). So `rate_limited`, close
code 4008 and `request_id` are all vocabulary declared and never wired; this
chapter enforces two and explains why 4008 STAYS UNUSED (it means quota exhausted;
quota is 3.9). WS handshake refusal is an HTTP 429 BEFORE the handshake (Retry-After
has nowhere to live on a close frame) — deliberately unlike 4001, which completes
the handshake by design. A limited frame gets an `error` frame and the connection
STAYS OPEN. The internal service seam is exempt (FR-009): throttling the dispatcher
stalls every customer. Second half: the EMAIL TRANSPORT chapter 3.6 deferred, which
is the OUTBOX A THIRD TIME over `webhook_disable_notifications` — it already has
`delivered_at`, so claim/send/mark needs no migration and no new column, and 3.6's
backlog drains as ordinary undelivered work. Mailpit in `compose.yaml` + nodemailer;
tests read what was RECEIVED, because FR-021 forbids a secret in an email and only
the received message can prove it. `humans.email` is NULLABLE so the unaddressable
recipient is a real branch. RESEARCH R10 IS A WARNING: ~30 fences against a
2,000-4,000 word bound (3.5 shipped 39 on an estimate of 22; 3.6 ran 5,273 words).
The transport is the separable 7 and the phase order puts it LAST so it can lift
into its own chapter with the word count in hand. Part 3 renumbered again: quotas
3.9, gauntlet 3.10 — and it cost ZERO fence amendments, which is the first evidence
3.7's stop-citing-movable-numbers rule paid for itself).
<!-- SPECKIT END -->

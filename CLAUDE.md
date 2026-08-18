<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/028-chapter-3-7/plan.md` (feature: Tutorial Chapter 3.7 — "Commit and
publish are two instants": the resume duplicate chapter 2.7 did not close. A
message is durable at one instant and announced at another — the gateway commits
through the api, then publishes to Redis — and a resuming client whose backfill
lands between them is delivered the same message twice, once from the backfill and
once from the fabric after the dedup window has shut. The fix keeps the backfill's
high-water mark on the Connection instead of discarding it at `phase = "live"`,
and consults it in `deliver()`. RESEARCH R3 OVERTURNED THE SPEC: the mark must
NEVER be retired, because two gateway instances can publish out of order and a
higher sequence arriving first would retire the mark before the delayed lower one
lands; no retirement is needed because the mark set is already capped at 200 by
`MAX_RESUME_CHANNELS`. The failure mode of this change is a GAP, which is worse
than the duplicate it replaces (constitution II), so a degraded resume retains
nothing. The existing `resume.itest.ts` covers three of four quadrants and the
missing one IS the bug — one number apart from a test already there, which is why
the deterministic test needs no api and no timing luck. No migration, no column,
no new dependency, no api change. Part 3 renumbers: quotas 3.8, gauntlet 3.9, and
three source comments citing chapter numbers are rewritten to stop citing numbers
that move — one of them has been stale since 3.6's insertion).
<!-- SPECKIT END -->

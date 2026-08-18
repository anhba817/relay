<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/027-chapter-3-6/plan.md` (feature: Tutorial Chapter 3.6 — "When to stop
trying": the attempt log and auto-disable, the two requirements deliberately
deferred out of chapter 3.5. Attempts are PUBLISHED to a new ANALYTICS stream,
not stored and not queryable — Part 4's ingester makes them queryable, and the
publish is at-most-once on purpose so a backlogged analytics path cannot stall
webhook dispatch (constitution III). Auto-disable reads two operational columns
on `webhook_endpoints`, never the stream. Research R1 measured that an
outcome-only check never fires for a low-traffic endpoint — one failing delivery
attempts at +35m36s then not again until +2h35m36s, and never at all if it
dead-letters with no further events — so there are TWO triggers: on a recorded
outcome, and a sweep riding the delivery relay's existing loop. The notification
is RECORDED, not sent; this platform has no email transport and chapter 3.7
needs one for quotas too, so `delivered_at` exists in order to be null. A
synthetic test event (FR-WHK-09) closes the disable-repair-re-enable loop; its
outcome never touches the failure run. No new dependency, no new service, no new
loop. Fence budget 15-19, and `repository.ts` has half a point of ratchet
headroom before this chapter adds five operations to it).
Project principles: `.specify/memory/constitution.md`.
<!-- SPECKIT END -->

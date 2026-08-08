<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/023-chapter-3-3/plan.md` (feature: Tutorial Chapter 3.3 — "The
outbox": an event row committed inside the same transaction as the message
that caused it, a relay that drains it to JetStream with SELECT … FOR UPDATE
SKIP LOCKED, and the dual-write failure demonstrated by killing the process
between the commit and the publish. At-least-once, stated; ordering, not
promised. English only; spec, research, data model, contracts, and quickstart
live alongside it).
Project principles: `.specify/memory/constitution.md`.
<!-- SPECKIT END -->

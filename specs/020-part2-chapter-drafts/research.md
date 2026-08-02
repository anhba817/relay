# Research — Part 2 Chapter Drafts (020)

## R1 — Draft location and shape

**Decision**: drafts live at `relay-tutorial/drafts/part-2/chapter-0N-<slug>/`
(slugs exactly as the manifest seeds them: `the-write-path`,
`send-it-twice`, `history-that-pages`, `the-socket`,
`two-servers-one-conversation`, `the-tunnel`,
`milestone-the-tuan-test`), each containing `page.mdx` + `figures.ts` in
the **final page shape** — same imports, metadata, `ChapterHeader`, boxes,
`Figure` usage as a published chapter. Publishing later is then a move into
`app/(en)/part-2/chapter-0N/<slug>/` plus verification, not a rewrite.

**Rationale**: `drafts/` is outside `app/`, so Next.js routes nothing —
FR-002 holds by construction; `figures.ts` files remain real TypeScript
(typechecked/linted by the site toolchain, so figure sources can't rot);
`page.mdx` outside `app/` is not compiled, so unresolved-at-drafting
concerns don't block the build.

**Alternatives considered**: pages under `app/` behind a "draft" flag —
rejected (routable by URL, sitemap/manifest pressure, violates US2);
plain `.md` in specs/ — rejected (loses the final-shape property that
makes publishing cheap and format checks meaningful).

## R2 — The draft header

**Decision**: each `page.mdx` opens (before the imports) with one MDX
comment block delimited by literal marker lines:

```
{/* DRAFT-HEADER (feature 020 — not published; strip at publish time)
tag: part2-chN (intended, not cut)
fences: <repo paths this chapter will pin>
amendments: <previously fenced files this chapter must diff-fence>
commands: <gate/lane commands the prose claims>
tbv: <numbered list of every «TBV: …» marker in the body>
019-baseline: drafted against the uncommitted re-foundation state
DRAFT-HEADER-END */}
```

The draft battery's word counter strips everything between the marker
lines before counting (draft-level measurement only; the published battery
never sees a header because publishing strips it).

**Rationale**: renders nothing even if previewed; trivially strippable;
machine-checkable (header presence, required keys, TBV list ↔ body markers
cross-check).

## R3 — TBV marker syntax

**Decision**: inline `«TBV: short description»` in prose/output blocks
wherever a value only running code can supply (test counts, command
output, durations, generated identifiers). Guillemets are already the
house marker convention and cannot collide with real content. The header
enumerates every marker; the contract requires the sets to match.

**Alternatives**: HTML comments (invisible → too easy to lose at publish);
TODO (collides with ordinary prose usage; not greppable-unique).

## R4 — Source map per chapter

| Draft | Primary sources (verify anchors while drafting) |
|---|---|
| 2.2 The write path | ADR-03 (+deep dive), SAD §5.1, §6.1 (`last_sequence`, DR-01), FR-MSG send/ordering rows, constitution II |
| 2.3 Send it twice | DR-03, SAD §5.1's idempotent-retry leg, FR-MSG idempotency rows, journey 4's duplicate "B2, north ramp" moment, constitution II |
| 2.4 History that pages | Cursor pagination requirement (FR-MSG history rows, constitution V's cursor clause), `messages_channel_seq` index (anchor as published 2.1 cites it), FR-MSG-09 |
| 2.5 The socket | SAD §5.1/§5.2 gateway legs, EIR-WS rows, @relay/protocol frames/close codes (1.3), FR-RTM connection/auth rows, ADR-05 |
| 2.6 Two servers, one conversation | ADR-07 (+deep dive), SAD §5.2, §6.3 (Redis ephemeral-only), CON-02/NFR-SCL (no sticky sessions), constitution IV |
| 2.7 The tunnel | SAD §5.2 resume walk (the duplicate/gap race), FR-RTM resume rows, FR-MSG-04, journey 4, ADR-03/07 interplay |
| 2.8 The Tuan test | Journey 4 end-to-end (docs/03), SRS §7.3 Phase 1 exit criterion, docs/07 §4 Rule 2, everything 2.2–2.7 built |

**Rule**: every anchor above is re-verified against the current documents
during drafting (FR-008); where the published 2.1 already cites an anchor
(e.g. the hot-path index), drafts cite it the same way for consistency.

## R5 — Drafting order (FR-009)

**Decision**: (1) 2.8's journey script skeleton first — the staged
sequence of the Tuan test (connect, converse, kill mid-send, tunnel,
reconnect, resume, assert exactly-once + order) written as the suite's
outline; (2) 2.2 → 2.7 drafted against it; (3) 2.8 completed in full;
(4) a continuity pass over all seven (SC-006) checking
no-mechanism-before-its-chapter and forward-reference chaining.

## R6 — Design-stage code discipline

**Decision**: draft code is written against knowledge already verified in
this workspace (NestJS 11 / Drizzle 0.45 / vitest 4 / turbo 2 — probed in
feature 019) plus registry checks for libraries Part 2 introduces
(`pnpm view` for intended versions of the WebSocket library `ws`, the
Redis client, and the JWT verifier — recorded in draft headers as intended
pins, still TBV until an implementation feature installs them). Exact
outputs, counts, and generated values are never invented — they are
`«TBV: …»` markers. API shapes for endpoints follow SAD §5.1/EIR-API and
the established repository surface; where the SAD is silent the draft
records a DECISION sentence exactly as 2.1 did for schema gaps.

**Rationale**: keeps the inevitable draft-vs-reality delta small,
enumerated, and honest — the implementation features correct code and
resolve TBVs rather than discovering silent fiction.

## R7 — Draft-level battery

**Decision**: measure drafts with the established formula (words, Why,
Skip, Fwd, Chk, Trap, tick-lines, Figures) after stripping the draft
header; record results in `specs/020-part2-chapter-drafts/draft-battery.txt`
(7 rows). This file is a feature artifact, NOT the series baseline —
`battery-baseline.txt` remains 019's 20 published rows and is untouched.
Fence checks are explicitly NOT run (nothing to check against — that is
the verification debt by design).

# Implementation Plan: Part 2 Chapter Drafts — The Core Loop, Written Ahead

**Branch**: `main` (no feature branches) | **Date**: 2026-08-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/020-part2-chapter-drafts/spec.md`


> **Post-feature note (2026-08-04).** `relay-tutorial/drafts/part-2/` no longer
> exists. All seven chapters were published, at which point the drafts became
> byte-identical duplicates that nothing tracked and nothing checked, and the
> directory was removed. The per-chapter metadata its `DRAFT-HEADER` blocks
> carried now lives in `chapter-notes.md` beside this file. References to the
> draft paths below are left as written: they record what this feature actually
> did, and research R1's reasoning about keeping drafts outside `app/` only
> makes sense in those terms.

## Summary

Seven complete English chapter drafts for 2.2–2.8 — the rest of Part 2 —
written ahead of their platform code, in the final page shape, under
`relay-tutorial/drafts/part-2/` where nothing routes. Each draft opens
with a verification-debt header (intended tag, fence inventory, expected
amendments, lane commands, enumerated `«TBV: …»` markers) so writing ahead
stays honest under the series' fence discipline instead of quietly
violating it. Drafting runs test-first at the part level (2.8's journey
script skeleton before 2.2–2.7 finalize, per docs/07 §5), against the 019
re-founded stack. The live site and relay-platform are untouched. All
decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: relay-tutorial's existing toolchain only (Next
16.2.x, TS 5.9, pnpm 10) — used for lint/typecheck of `figures.ts` and the
unchanged site build. NO new dependencies anywhere; NO platform changes.

**Primary Dependencies**: none added. Registry version checks (`pnpm
view`) for libraries Part 2 *intends* to introduce (ws, Redis client, JWT
verifier) are recorded in draft headers as intended pins (R6) — nothing is
installed.

**Storage**: n/a (prose feature). Draft code *describes* the compose
Postgres/Redis from 1.2 and the Drizzle layer from 2.1; it runs nothing.

**Testing**: draft battery (established formula, header-stripped, 7 rows
→ `draft-battery.txt` — series baseline untouched, R7); invented-ID
detector over 7×(page.mdx+figures.ts); header-completeness check (required
keys present; header TBV list ↔ body `«TBV»` markers match exactly);
continuity review per SC-006; surface freeze (sitemap 34, manifest
byte-identical, `pnpm build` green, same page count); relay-platform
zero-diff check. Fence checks deliberately NOT run — they are the recorded
verification debt.

**Target Platform**: files in the relay-tutorial repo; site build only as
a no-change regression check.

**Project Type**: single-artifact content feature — seven unpublished
chapter drafts + spec artifacts. The series' first write-ahead feature.

**Performance Goals**: none.

**Constraints**: drafts non-routable (FR-002); relay-platform zero diffs
(FR-006); English only (FR-007); 2.8-script-first ordering (FR-009);
docs/07 §4 Rule 1 failure-first structure in every chapter; SAD §5.2 race
staged concretely in 2.7 (FR-010); commits/pushes are Dong's.

**Scale/Scope**: 14 new files under `relay-tutorial/drafts/part-2/`
(7 × page.mdx + figures.ts; ~2,000–4,000 canonical words each, 2–4
figures each) + `draft-battery.txt` in the feature dir. Zero changes to
app/, lib/, components/, relay-platform, or docs/.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I. Tenant isolation (NON-NEGOTIABLE) | ✅ Pass | No data access is built. Draft content TEACHES the machinery (2.2–2.4 queries go through the tenant-scoped repository; 2.8 attacks with foreign ids as part of the journey) — drafts must not depict any query bypassing the layer. |
| II. No acknowledged loss | ✅ Pass — this part IS the principle | 2.2 (ack after commit, server-assigned sequences), 2.3 (storage-layer idempotency), 2.7 (resume without loss or duplicates) are the principle's chapters; drafts derive their mechanisms from ADR-03/DR-03/§5.2 verbatim. |
| III. Two data paths | ✅ Pass | Part 2 is operational-path only; no analytical anything appears. |
| IV. Single writer | ✅ Pass | 2.5/2.6 keep the gateway store-free (sends forwarded to the api per ADR-05; Redis is fan-out only per §6.3) — the drafts teach exactly this boundary. |
| V. Developer/reader-first | ✅ Pass | Cursor pagination (2.4) per the constitution's own clause; error envelopes stay on the 1.4 filter; nothing published that can't be verified (US2). |
| VI. Requirement-driven, test-verified | ✅ Pass with an honest caveat | Every chapter cites its requirements (FR-008); the *code* is design-stage and unverified BY DESIGN — recorded per draft as verification debt, discharged by the per-chapter implementation features. Nothing ships: the constitution's test gates bind shipping, and nothing here ships. |
| VII. Boring by design | ✅ Pass | No stack choices are made beyond the accepted ADRs; libraries Part 2 will need are noted as intended pins, decided properly in their implementation features. |
| Tech & platform constraints (v1.1.0) | ✅ Pass | Drafts depict the bound stack (NestJS api-only, Drizzle in-repository, turbo gate) and nothing else. |
| Workflow & quality gates | ✅ Pass | Spec-first observed; the fence gate is not waived but *deferred with a written debt record* — the same honesty mechanism 019's REVISED notes used, applied forward. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — no service, no dependency, no surface
change; one new directory of prose.

## Project Structure

### Documentation (this feature)

```text
specs/020-part2-chapter-drafts/
├── plan.md              # This file
├── research.md          # Phase 0 output (R1–R7)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── part2-drafts-contract.md
├── arc-sheet.md         # generated at implementation — the part-level design memo (2.8 script skeleton + shared codebase story)
├── draft-battery.txt    # generated at implementation (7 rows; NOT the series baseline)
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code

```text
relay-tutorial/ (submodule — additions only, all non-routable)
└── drafts/
    └── part-2/
        ├── chapter-02-the-write-path/{page.mdx,figures.ts}
        ├── chapter-03-send-it-twice/{page.mdx,figures.ts}
        ├── chapter-04-history-that-pages/{page.mdx,figures.ts}
        ├── chapter-05-the-socket/{page.mdx,figures.ts}
        ├── chapter-06-two-servers-one-conversation/{page.mdx,figures.ts}
        ├── chapter-07-the-tunnel/{page.mdx,figures.ts}
        └── chapter-08-milestone-the-tuan-test/{page.mdx,figures.ts}

relay-platform/  — UNTOUCHED (FR-006)
app/, lib/, components/, docs/ — UNTOUCHED (FR-002)
```

**Structure Decision**: `drafts/` at the tutorial repo root — outside
`app/` so Next routes nothing; `figures.ts` stays inside the toolchain's
typecheck/lint net; each draft is in final page shape so publishing is a
move + verification, not a rewrite (R1).

## Complexity Tracking

> No constitution violations. The one unusual posture — chapters ahead of
> code — is docs/07 §5's own sanctioned production order, made auditable
> by the draft-header debt mechanism (R2) instead of left implicit.

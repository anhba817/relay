# Tasks: Part 2 Chapter Drafts — The Core Loop, Written Ahead

**Input**: Design documents from `/specs/020-part2-chapter-drafts/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/part2-drafts-contract.md, quickstart.md

**Tests**: Not requested as separate tasks — verification is the contract
battery (C1 draft battery, C2 headers/TBVs, C3 frozen surfaces, C4 source
fidelity, C5 arc continuity, C6 marquee moments, C7 stack fidelity).

**Organization**: The series' first write-ahead feature. Non-negotiables:
**drafts are UNPUBLISHED** (everything under `relay-tutorial/drafts/part-2/`
— never under `app/`; manifest/sitemap/nav/allowlist untouched);
**relay-platform gets ZERO changes**; **English only**; **no invented
outputs** — every value only running code can supply is a `«TBV: …»` marker
enumerated in the draft header (R2/R3); **2.8's script skeleton before
2.2–2.7 finalize** (FR-009, docs/07 §5); **fence checks are deliberately
NOT run** — they are the recorded verification debt; **series
battery-baseline.txt untouched** (draft metrics go to this feature's
draft-battery.txt).

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` /
`git tag` (Dong does all three). Drafts assume the 019 re-foundation
working-tree state (uncommitted; its tags not yet cut).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = the seven drafts, US2 = draft honesty (headers + frozen surfaces), US3 = arc + traceability

## Path Conventions

- Drafts: `relay-tutorial/drafts/part-2/chapter-0N-<slug>/{page.mdx,figures.ts}` (slugs per data-model's table)
- Sources: docs/03 (journey 4), docs/04 (FR-MSG, FR-RTM, FR-CHN, EIR-WS, EIR-API, SRS §7.3 exit criteria), docs/05 (§5.1 L224+, §5.2 L265+, §6.1, §6.3, ADR-03/05/07), docs/06 deep dives, docs/07 §3–5, constitution I/II/IV/V
- Platform baseline (read-only!): relay-platform working tree = 019's S5 (NestJS api, Drizzle repository, turbo gate, protocol frames)
- Header format: research R2; TBV syntax: research R3; arc chain: data-model

---

## Phase 1: Setup

**Purpose**: Load the sources, pin intentions, snapshot the frozen surfaces

- [X] T001 Source study + reality snapshots: read the drafting sources end to end and extract working notes into `/tmp/claude-1000/.../scratchpad/020-sources.md` — docs/03 journey 4 (the tunnel narrative, "B2, north ramp"), docs/04 FR-MSG/FR-RTM/FR-CHN/EIR-WS/EIR-API slices + SRS §7.3 Phase 1 exit criterion (quote it verbatim), docs/05 §5.1/§5.2 walk-throughs (capture the §5.2 duplicate/gap race steps EXACTLY), §6.1/§6.3, ADR-03/05/07 + their docs/06 deep dives, docs/07 §3 Part 2 table + §4 rules + §5 production order; record intended pins via `pnpm view <pkg> version` for the libraries Part 2 will name (`ws`, Redis client — check both `ioredis` and `redis` and pick per SAD/boring-by-design with one-line rationale, JWT verifier — check `jose`; intended, NOT installed); snapshot the current sitemap URL set and `pnpm build` page count for C3's freeze check; re-read the published 2.1 + revised 1.4 (en) so draft code continues their exact surfaces (Repository methods, protocol exports, controller/filter idioms) (R4/R6, C3/C7)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The part-level design that keeps seven drafts telling one story

- [X] T002 Write the arc sheet at specs/020-part2-chapter-drafts/arc-sheet.md (feature artifact, not published): (a) **the 2.8 journey script skeleton FIRST** (FR-009) — the staged Tuan-test sequence with numbered steps (two users converse across two gateway instances; kill the socket mid-send; drive through the tunnel window; reconnect; resume from cursor; assert exactly-once, order, and zero reveals of loss) and, for each step, which chapter (2.2–2.7) must supply the capability it exercises; (b) the shared codebase story all drafts draw from: endpoint shapes (the POST message route and history route per SAD §5.1/EIR-API, NestJS module layout continuing 1.4's AppModule idiom), repository method additions per chapter (continuing 2.1's surface, Drizzle idiom, raw-SQL islands only where the builder falls short), DTO/validation posture (zod from @relay/protocol at the boundary — trajectory named in 1.4), the gateway session/registry design (frameworkless, ws library, JWT verify, per SAD §5.2 + EIR-WS), Redis channel naming + payload shape for fan-out (ADR-07), the cursor format (channel_id+seq per SAD §6.1's index), and the migration/lane conventions each chapter claims; (c) per-chapter fence inventories + expected amendments (which chapter diff-fences api package.json for `ws`/redis deps, etc.) feeding the R2 headers (C5/C7)

---

## Phase 3: User Story 1 - The seven core-loop chapters exist as complete English drafts (Priority: P1) 🎯 MVP

**Goal**: Seven complete, format-true, failure-first drafts telling one continuous story on the 019 stack.

**Independent Test**: A reviewer reads 2.2→2.8 in sequence and follows the whole core loop without the source documents (spec US1).

### Implementation for User Story 1

- [X] T003 [US1] Draft 2.2 "The write path" in relay-tutorial/drafts/part-2/chapter-02-the-write-path/{page.mdx,figures.ts}: R2 header (tag part2-ch2; fences per arc sheet; amendments: api module wiring); failure FIRST — the naive endpoint (no lock) demonstrated interleaving sequences under concurrent sends (a two-writer race narrated concretely, output as «TBV»), THEN ADR-03's `SELECT … FOR UPDATE` on the channel row + server-assigned sequence + ack-after-commit (constitution II quoted); the first real NestJS endpoint (controller/DTO/pipe continuing 1.4's idioms; repository gains the write method in Drizzle with the row lock — `.for("update")` per ADR-16's first-class claim); figures: the send walk (§5.1 slice) + the race timeline; battery-true (FR-001/003/004, C1/C6/C7)
- [X] T004 [US1] Draft 2.3 "Send it twice" in relay-tutorial/drafts/part-2/chapter-03-send-it-twice/{page.mdx,figures.ts}: R2 header (tag part2-ch3); failure FIRST — Tuan's duplicate "B2, north ramp" (journey 4 quoted; a retry after ack-loss duplicates the message), THEN DR-03's partial unique index doing its planted work (2.1 forward-ref harvested): idempotency key on the write path, `ON CONFLICT` returning the original row, enforced at storage not memory (constitution II verbatim); the §5.1 idempotent-retry leg walked; figures: retry timeline before/after; battery-true (FR-001/003/004, C1/C7)
- [X] T005 [US1] Draft 2.4 "History that pages" in relay-tutorial/drafts/part-2/chapter-04-history-that-pages/{page.mdx,figures.ts}: R2 header (tag part2-ch4); failure FIRST — offset pagination drifting under live inserts (a page-2 request skipping/duplicating rows while messages arrive, staged concretely), THEN cursor pagination on (channel_id, seq) riding `messages_channel_seq` as a pure index-order scan (FR-MSG-09; cite the index anchor exactly as published 2.1 does); opaque cursor per constitution V's clause (quoted); the history endpoint + repository read method; figures: offset drift vs cursor stability; battery-true (FR-001/003/004, C1/C7)
- [X] T006 [US1] Draft 2.5 "The socket" in relay-tutorial/drafts/part-2/chapter-05-the-socket/{page.mdx,figures.ts}: R2 header (tag part2-ch5; amendments: gateway package.json gains `ws` + JWT verifier as intended pins); the gateway grows its real job — WS termination (frameworkless, per ADR-15's scope clause taught in 1.4), JWT verify at connect (delegated trust, constitution V; close code 4001 from the protocol package), connection registry (in-memory this chapter; its Redis future named per §6.3), frames from @relay/protocol over the wire at last (1.3's payoff harvested); sends forwarded to the api over internal HTTP (ADR-05 — the gateway writes NOTHING, constitution IV); TRAP: the temptation to let the gateway touch the store "just for reads"; figures: connect/auth/frame walk + the two-service send path; battery-true (FR-001/003/004, C1/C7)
- [X] T007 [US1] Draft 2.6 "Two servers, one conversation" in relay-tutorial/drafts/part-2/chapter-06-two-servers-one-conversation/{page.mdx,figures.ts}: R2 header (tag part2-ch6; amendments: api gains the Redis publisher, gateway the subscriber — intended pins from T001); failure FIRST — the sticky-session trap (two gateway instances, users split across them, messages don't cross; CON-02 forbids the "easy" fix), THEN ADR-07's Redis pub/sub fan-out with the lossy-fabric argument told honestly (at-most-once is FINE because durability lives in Postgres sequences — constitution IV quoted; the deep dive's argument); Redis stays ephemeral (§6.3 — total loss costs nothing durable); figures: the two-instance topology + the fan-out walk (§5.2 first half); battery-true (FR-001/003/004, C1/C6/C7)
- [X] T008 [US1] Draft 2.7 "The tunnel" in relay-tutorial/drafts/part-2/chapter-07-the-tunnel/{page.mdx,figures.ts}: R2 header (tag part2-ch7); THE FLAGSHIP (FR-010, C6) — resume protocol per SAD §5.2: cursors, backfill via 2.4's pagination, live re-subscribe; the duplicate/gap race staged as a CONCRETE numbered timeline (reconnect → backfill reads ≤N → message N+1 fans out DURING backfill → naive ordering either drops it (gap) or double-delivers it (duplicate) — both shown), THEN the subscribe-before-backfill buffer resolving it (subscribe first, buffer live frames, replay backfill, drain buffer, dedupe on seq); Tuan's tunnel from journey 4 as the human frame; figures: the race timeline (the chapter's centerpiece) + the buffer state machine; battery-true (FR-001/003/004/010, C1/C6/C7)
- [X] T009 [US1] Draft 2.8 "Milestone: the Tuan test" in relay-tutorial/drafts/part-2/chapter-08-milestone-the-tuan-test/{page.mdx,figures.ts}: R2 header (tag part2-ch8); expand T002's script skeleton into the full milestone chapter — the integration suite (`*.itest.ts`, two-lane convention) scripting journey 4 end to end across two gateway instances + the api + compose stores: connect both users, converse, kill the socket mid-send (the un-acked send retried with its idempotency key), tunnel window, reconnect, resume from cursor, assert exactly-once + strict order + no cross-tenant reveal; every asserted capability back-referenced to its chapter (2.2 order, 2.3 exactly-once, 2.4 backfill reads, 2.5 sessions, 2.6 cross-instance, 2.7 resume); the chapter closes Part 2 by quoting SRS §7.3's Phase 1 exit criterion and declaring it met «TBV: suite run» (docs/07 §4 Rule 2: the journey IS the milestone); figures: the journey swimlane + the part's capability map; battery-true (FR-001/003/009, C1/C5/C6)

**Checkpoint**: The whole core loop readable end to end in draft — MVP delivered

---

## Phase 4: User Story 2 - The drafts are honest about being drafts (Priority: P2)

**Goal**: Verification debt fully recorded; nothing published; nothing platform-side.

**Independent Test**: Header/TBV cross-checks pass; site + platform provably unchanged (spec US2).

### Implementation for User Story 2

- [X] T010 [US2] Header + freeze verification: script-check all seven drafts — R2 header present with all six keys (tag/fences/amendments/commands/tbv/019-baseline); extract body `«TBV: …»` markers per draft and diff against each header's tbv list (must match exactly); header `fences` lists exactly the `title=""` paths the body uses and `amendments` exactly the diff-fence targets; then the freeze checks — `git -C relay-platform status --porcelain` shows nothing from this feature; relay-tutorial changes confined to `drafts/part-2/**`; `pnpm lint && pnpm build` green in relay-tutorial with page count unchanged; sitemap URL set identical to T001's snapshot (34); `specs/019-stack-refoundation/battery-baseline.txt` byte-unchanged; 2.2–2.8 still "forthcoming" on the landing (C2/C3)

---

## Phase 5: User Story 3 - The part reads as one arc, traceable to the paperwork (Priority: P3)

**Goal**: One continuous story, every claim sourced, measured.

**Independent Test**: ID detector clean; continuity review finds zero mechanism-before-its-chapter (spec US3).

### Implementation for User Story 3

- [X] T011 [US3] Continuity + fidelity pass over all seven drafts: invented-ID detector over the 14 files (every FR-*/DR-*/NFR-*/EIR-*/ADR-*/D# exists in docs/04/05/06/constitution); quoted passages spot-checked verbatim against the current documents (constitution II/IV/V clauses, §5.2 race steps, §7.3 exit criterion, journey 4 lines); arc review in sequence per data-model's chain — no mechanism before its chapter, SkipAhead/Checkpoint states strictly cumulative, forward references chain 2.2→…→2.8→Part 3, 2.8's script exercises every chapter (cross-check against T002's step-to-chapter map); stack-fidelity greps (no raw pg/drizzle-orm outside repository-layer code blocks, no framework imports in gateway blocks, turbo gate commands, `*.itest.ts` naming, intended pins on every new library mention); fix all findings; then generate specs/020-part2-chapter-drafts/draft-battery.txt (7 rows, established formula, header-stripped) with every row in bounds (C1/C4/C5/C6/C7, SC-006)

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T012 Full quickstart sweep + handoff: execute quickstart V1–V6 end to end and record results; audit `git status --porcelain` in both submodules + parent (drafts + spec artifacts only); report to Dong — the seven drafts with word counts, the verification-debt summary per chapter (tags to cut, fences to verify, TBV counts, intended pins to confirm), suggested commit messages (relay-tutorial: drafts; parent: specs/020 + pins), the review list (read 2.7's race timeline and 2.8's script first — they anchor the part), and the explicit reminder that publishing each chapter requires its implementation feature (platform code → fence verification → TBV resolution → vi translation → manifest flip → Dong's tag) (all contracts)

---

## Dependencies

- Phase 1 → Phase 2 (sources + pins feed the arc sheet)
- Phase 2 → Phase 3 (every draft draws on the arc sheet; T002's script skeleton is FR-009's precondition)
- Phase 3 strictly sequential T003→T009 (each chapter opens from its predecessor's state; 2.8 last, expanding the skeleton)
- Phase 4 (T010) and Phase 5 (T011) need Phase 3 complete. **Canonical execution order: T011 → T010 → T012** — T011 may edit drafts while fixing findings, so the continuity/fidelity pass runs first and the header/TBV cross-check + freeze verification (T010) runs against the settled text; T012's sweep re-confirms both. (Phase numbering follows story priority; execution follows this note.)
- Phase 6 last

## Parallel Example

Within each draft task, page.mdx and figures.ts are one unit (same author pass). Across tasks, parallelism is deliberately NOT used in Phase 3 — the arc is the point. T010 can start its freeze checks while T011 reads, if desired.

## Implementation Strategy

MVP = Phases 1–3 (the seven drafts, arc-coherent). Phases 4–5 make the write-ahead honest and measured; Phase 6 hands Dong the debt ledger. Nothing publishes: the deliverable is `drafts/part-2/**` + the per-chapter verification contracts their headers carry.

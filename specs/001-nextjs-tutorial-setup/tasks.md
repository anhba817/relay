# Tasks: Next.js Tutorial Repository Setup

**Input**: Design documents from `/specs/001-nextjs-tutorial-setup/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/repository-contract.md, quickstart.md

**Tests**: Not requested in the spec — no test-framework tasks are generated (FR-003 keeps the scaffold pure). Verification is via the quickstart scenarios and the `pnpm lint && pnpm build` gate (contract C1).

**Organization**: Tasks are grouped by user story. Note an honest structural dependency: US2 and US3 both operate on the repository US1 creates — unavoidable for a repo-creation feature. Each story still has its own independent test.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = scaffold repository, US2 = submodule link, US3 = Violet Bloom theme

## Path Conventions

- Parent repo root: `/home/dong/work/relay/`
- New repository (created by US1): `/home/dong/work/relay/relay-tutorial/` — its own git history; becomes the submodule working tree
- All `relay-tutorial/…` paths below are relative to the parent repo root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify the environment and guard the edge cases before anything is created

- [x] T001 Preflight checks from parent repo root: confirm `node --version` ≥ 22 and `pnpm --version` ≥ 10; confirm no `relay-tutorial/` directory exists at the parent root, and that `git ls-remote git@github.com:anhba817/relay-tutorial.git` either fails (repo not yet created — T005 will create it) or succeeds with zero refs (repo pre-created empty, which satisfies T005) — STOP only if the local directory exists or the remote already has refs (name-collision edge case); confirm `ssh -T git@github.com` authenticates as `anhba817`; re-resolve latest Next.js with `npm view next version` and note it (expected 16.2.12 per research R1 — if newer, use the newer version everywhere below and record the substitution in specs/001-nextjs-tutorial-setup/research.md)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None — this feature has no shared infrastructure beyond Phase 1's checks. US1 itself is the structural prerequisite for US2/US3 (see Dependencies).

*(no tasks)*

---

## Phase 3: User Story 1 - Scaffold the tutorial application repository (Priority: P1) 🎯 MVP

**Goal**: A fresh `relay-tutorial` git repository containing a pure, runnable create-next-app scaffold on the latest stable Next.js.

**Independent Test**: Open `relay-tutorial/`, confirm `package.json` pins the latest Next.js, confirm the first commit is pure CLI output, and `pnpm dev` serves the default page without errors (spec US1 acceptance scenarios 1–3).

### Implementation for User Story 1

- [x] T002 [US1] Generate the scaffold from the parent repo root with the research R2 command: `pnpm create next-app@16.2.12 relay-tutorial --ts --eslint --tailwind --app --no-src-dir --turbopack --import-alias "@/*" --use-pnpm` (substitute the T001-resolved version if newer), producing `relay-tutorial/` with its own git repository
- [x] T003 [US1] Ensure scaffold-purity baseline in `relay-tutorial/`: verify `git log` shows exactly one initial commit containing only CLI output (if create-next-app did not init/commit, run `git init && git add -A && git commit -m "chore: scaffold Next.js 16.2.12 via create-next-app"`); verify `dependencies.next` in `relay-tutorial/package.json` equals the T001-resolved version (FR-002, SC-003)
- [x] T004 [US1] Smoke-verify the scaffold in `relay-tutorial/`: `pnpm dev` starts and http://localhost:3000 renders the default page with no startup errors, then `pnpm lint && pnpm build` both exit 0 (FR-006, contract C1)

**Checkpoint**: US1 fully functional — a runnable, pinned, pure scaffold exists (MVP)

---

## Phase 4: User Story 2 - Link the tutorial repository as a submodule (Priority: P2)

**Goal**: `relay-tutorial` hosted publicly under `anhba817` and registered as a pinned submodule of `relay` at root path `relay-tutorial/`.

**Independent Test**: Fresh clone of `relay` + `git submodule update --init` populates `relay-tutorial/` at the exact pinned SHA (spec US2 acceptance scenarios 1–3, quickstart V1).

### Implementation for User Story 2

- [x] T005 [US2] ⚠ BLOCKING USER ACTION (completed by user 2026-07-29; remote verified empty) (research R6): ask the user to either run `! gh auth login` adding the `anhba817` account (then run `gh repo create anhba817/relay-tutorial --public --description "Application for the Building Relay tutorial series"`) or create the empty **public** repo `relay-tutorial` at github.com/new with NO auto-initialized files; do not proceed until `git ls-remote git@github.com:anhba817/relay-tutorial.git` succeeds
- [x] T006 [US2] Wire and push from `relay-tutorial/`: `git remote add origin git@github.com:anhba817/relay-tutorial.git`, ensure branch is `main`, `git push -u origin main`
- [x] T007 [US2] Register the submodule from the parent repo root: `git submodule add git@github.com:anhba817/relay-tutorial.git relay-tutorial`, verify `.gitmodules` records path + SSH URL and `git submodule status` shows the pinned SHA, then commit `.gitmodules` + gitlink to the parent repo with message `chore: add relay-tutorial submodule` (FR-004)
- [x] T008 [US2] Validate the consumer path per quickstart V1: clone `git@github.com:anhba817/relay.git` into a temp dir (use the scratchpad), `git submodule update --init`, confirm `relay-tutorial/` populates at the pinned SHA and `pnpm install && pnpm build` succeeds there; clean up the temp clone (SC-001, SC-004)

**Checkpoint**: US1 AND US2 work — the repo is hosted, linked, and reproducible from a fresh clone

---

## Phase 5: User Story 3 - Apply the Violet Bloom theme (Priority: P3)

**Goal**: The application globally styled with the tweakcn Violet Bloom theme, functional in both light and dark modes, with new components inheriting the tokens automatically.

**Independent Test**: Run the app; home page renders the Violet Bloom light palette in light mode and dark palette in dark mode with no default-styled surfaces (spec US3 acceptance scenarios 1–3, quickstart V3).

### Implementation for User Story 3

- [x] T009 [US3] Initialize shadcn in `relay-tutorial/`: `pnpm dlx shadcn@latest init` (accept defaults consistent with the scaffold: app router, no src dir, `@/*` alias), producing `relay-tutorial/components.json` and `relay-tutorial/lib/utils.ts`
- [x] T010 [US3] Apply the theme: `pnpm dlx shadcn@latest add https://tweakcn.com/r/themes/violet-bloom.json` from `relay-tutorial/`, then verify `relay-tutorial/app/globals.css` contains the Violet Bloom `:root` (light) AND `.dark` variable blocks with `oklch` values (FR-005, contract C3, data-model E3)
- [x] T011 [US3] Wire theme fonts in `relay-tutorial/app/layout.tsx`: load Plus Jakarta Sans, Lora, and IBM Plex Mono via `next/font/google` with CSS-variable strategy and map them to the theme's `--font-sans`/`--font-serif`/`--font-mono` expectations; remove the scaffold's Geist font wiring (research R4)
- [x] T012 [US3] Add dark-mode switching: `pnpm add next-themes` in `relay-tutorial/`, create `relay-tutorial/components/theme-provider.tsx` wrapping next-themes with `attribute="class" defaultTheme="system" enableSystem`, wrap the body content in `relay-tutorial/app/layout.tsx` with it and add `suppressHydrationWarning` to the `<html>` tag (research R5)
- [x] T013 [US3] Add the proof component and themed home page: `pnpm dlx shadcn@latest add button` (creates `relay-tutorial/components/ui/button.tsx`), then minimally restyle `relay-tutorial/app/page.tsx` to consume theme tokens (background/foreground/primary/card via Tailwind token classes) and render one Button — stay inside the research R8 purity boundary, no other files
- [x] T014 [US3] Verify and commit the theme in `relay-tutorial/`: run quickstart V3 (light-mode palette, dark-mode palette via OS preference, globals.css inspection), run `pnpm lint && pnpm build` (exit 0), commit as `feat: apply Violet Bloom theme (tweakcn) with light/dark support` and push (SC-002)

**Checkpoint**: All three user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, final pin, and end-to-end validation

- [x] T015 [P] Write `relay-tutorial/README.md`: purpose (application for the *Building Relay* tutorial series, docs/07-tutorial-plan.md), relationship to the `relay` parent repo (submodule of), install/run commands matching contract C1 (`pnpm install`, `pnpm dev`, `pnpm build`, `pnpm lint`), and the `git submodule update --init` step for consumers arriving via the parent (FR-007, quickstart V5); commit as `docs: add README` and push
- [x] T016 Update the submodule pin from the parent repo root: `git add relay-tutorial && git commit -m "chore: pin relay-tutorial at themed+documented revision"` so the parent references the final SHA including US3 + README (SC-004)
- [x] T017 Run the full quickstart validation V1–V5 from `specs/001-nextjs-tutorial-setup/quickstart.md` top to bottom in a temp dir; record pass/fail per scenario in `specs/001-nextjs-tutorial-setup/quickstart.md` results notes or report to user; clean up

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Empty — no blocker beyond Phase 1
- **US1 (Phase 3)**: Depends on T001 only
- **US2 (Phase 4)**: Depends on US1 (the repo must exist to host/link). T005 is the feature's ONE blocking user interaction — surface it as early as possible; it can be requested in parallel with US1 execution since it needs nothing from the scaffold
- **US3 (Phase 5)**: Depends on US1 only (themes the scaffold). Does NOT depend on US2 — can run before or in parallel with hosting; if it lands after T007, T016 re-pins
- **Polish (Phase 6)**: T015 depends on US1; T016 depends on T007 + T014 + T015; T017 depends on everything

### User Story Dependencies

- **US1 (P1)**: none — the MVP
- **US2 (P2)**: US1 (structural: needs the repo). Independently testable via quickstart V1
- **US3 (P3)**: US1 (structural: themes the app). Independent of US2; testable via quickstart V3

### Parallel Opportunities

This feature is mostly a sequential command pipeline in one directory — parallelism is limited by design:

- **T005 (user action) alongside Phase 3**: request repo creation from the user while the scaffold runs — the biggest wall-clock win
- **US3 (T009–T014) alongside US2 (T006–T008)**: theme work is local to `relay-tutorial/` files; hosting/linking is git plumbing — different concerns, no file conflicts (T016 reconciles the pin afterward)
- **T015 (README)** can be written in parallel with US2 or US3 (different file)

## Parallel Example

```bash
# While T002 (scaffold) runs, surface T005 to the user:
#   "Please run: ! gh auth login   (add the anhba817 account)"
# After US1 completes, two independent tracks:
#   Track A (US2): T006 → T007 → T008
#   Track B (US3): T009 → T010 → T011 → T012 → T013 → T014
# Then: T015 → T016 → T017
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (T001)
2. Complete Phase 3 (T002–T004)
3. **STOP and VALIDATE**: pinned version, pure first commit, `pnpm dev` renders — that is a demonstrable MVP

### Incremental Delivery

1. US1 → runnable scaffold (MVP)
2. US2 → hosted + linked as pinned submodule → validate with fresh clone (quickstart V1)
3. US3 → Violet Bloom light/dark → validate visually (quickstart V3)
4. Polish → README, final pin, full quickstart V1–V5

---

## Notes

- The ONE blocking user interaction is T005 (repo creation under `anhba817` — research R6); everything else is automated
- FR-003 purity boundary (research R8): beyond the scaffold, only theme files, `app/layout.tsx`, `app/page.tsx`, and `README.md` may change — reject any task drift beyond this list
- Commit discipline: scaffold commit (T003) → theme commit (T014) → README commit (T015) in `relay-tutorial`; submodule-add commit (T007) → pin-update commit (T016) in the parent
- If `npm view next version` returns something newer than 16.2.12 at execution time, the newer version wins everywhere (spec edge case: "latest" resolves at creation time)

---

## Phase 7: Convergence

- [x] T018 Amend the research R8 execution record in specs/001-nextjs-tutorial-setup/research.md to enumerate the theme commit's full actual file delta — add `package.json` + `pnpm-lock.yaml` (next-themes dependency mandated by R5) and `components/theme-provider.tsx` (named in plan.md's Project Structure) to the permitted-modifications list, so the FR-003 purity boundary matches reality per FR-003 (partial)
- [x] T019 Record the `app/layout.tsx` metadata title/description change ("Relay Tutorial") as a permitted, justified modification in the same R8 execution record — or revert it to the scaffold values if the boundary should stay strict — per FR-003 (unrequested)

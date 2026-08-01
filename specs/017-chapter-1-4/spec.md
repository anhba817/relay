# Feature Specification: Tutorial Chapter 1.4 — Walking Skeleton

**Feature Branch**: `017-chapter-1-4`

**Created**: 2026-08-01

**Status**: Draft

**Input**: User description: "chapter 1.4"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 1.4 and stand the skeleton up alongside it (Priority: P1)

As the tutorial's reader, I open Part 1's final chapter — "Walking skeleton"
(docs/07 §3) — with the workspace, the infrastructure, and the protocol
package all in place. Now the first two of Relay's six services come to life:
the API service and the gateway, deliberately *empty* — no messages, no
channels, no business logic — but standing, with the row's four properties
from line one: health checks, request IDs, structured logs, and the discipline
that the skeleton deploys before the muscles grow. The services import
`@relay/protocol` (1.3's promise made real), and by the end I can start both,
hit their health endpoints, watch a request ID thread through a structured
log line, and still pass the gate. Part 1 closes with the ground fully built.

**Why this priority**: The chapter is the deliverable and Part 1's finale —
docs/07 §5 marks Part 1 as the writing plan's first code milestone, and every
Part 2 chapter builds muscle onto exactly this skeleton.

**Independent Test**: A reader with the 1.3 checkpoint can, using only the
chapter: create both services, start them, verify health endpoints respond,
observe request-ID-carrying structured log lines, and see the gate pass —
without consulting docs/04/05/06.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** read end to end, **Then** it
   builds both services step by step (service layout under the workspace's
   `services/*` glob, health endpoints, request-ID middleware, structured
   JSON logging), teaches the walking-skeleton idea as docs/07's row states
   it ("deploy the skeleton before the muscles; observability from line
   one"), and closes in the runnable, tested state.
2. **Given** the format rules (docs/07 §2, code-chapter battery), **Then**
   the chapter passes: 2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, 1
   `SKIP AHEAD` naming tag `part1-ch4`, ≥1 forward reference, 2–4 captioned
   figures, takeaways, exactly one closing `CHECKPOINT`.
3. **Given** the chapter's factual claims, **Then** 100% trace to docs/04
   (NFR-OBS-01/06, EIR-API-05), docs/05 (§4 service view and responsibilities,
   §8 cross-cutting concerns, ADR-04/05), the constitution's observability
   clauses, or earlier chapters; quotes verbatim; no invented identifiers;
   anything the documents leave open is a recorded chapter decision.
4. **Given** the code the chapter builds, **Then** every file-content fence
   byte-matches the repository at `part1-ch4`, and ALL prior chapters' fences
   (1.1's ten, 1.2's three, 1.3's seven) still hold — additive-only, now
   spanning four chapters.

---

### User Story 2 - The canonical code advances to tag `part1-ch4` (Priority: P2)

As a reader (or a stuck reader), the two services exist in `relay-platform`
as the diff from `part1-ch3` to `part1-ch4`: the first occupants of
`services/*`, consuming `@relay/protocol` through the workspace, tested
without requiring the Docker stores to run, and leaving every previously
fenced file untouched.

**Why this priority**: The tag discipline continues; this increment also
establishes the service-package pattern every later service chapter follows,
and completes the Part 1 milestone state.

**Independent Test**: Checking out `part1-ch4` yields a workspace where the
gate passes with the services' tests included; both services start and answer
their health endpoints; the `part1-ch3..part1-ch4` diff is exactly this
chapter's additions.

**Acceptance Scenarios**:

1. **Given** the repository at `part1-ch4`, **When** the gate runs, **Then**
   lint, typecheck, and tests pass — with meaningful service tests (health
   response shape, request-ID propagation, log structure), still with no
   Docker requirement.
2. **Given** both services started locally, **Then** each answers its health
   endpoint, every response carries a request ID, and log output is
   structured JSON carrying that request ID (NFR-OBS-01's fields where they
   exist at this stage — recorded decisions where they don't).
3. **Given** the diff from `part1-ch3`, **Then** it is strictly additive over
   fenced files; the services demonstrably import `@relay/protocol` (the 1.3
   promise), and any new dependencies are pinned, package-local, and reasoned
   in the chapter.

---

### User Story 3 - Part 1 completes across the bilingual series (Priority: P3)

As a reader of either language, chapter 1.4 appears everywhere — and with it
**Part 1 becomes the series' first fully published code part**: the manifest
flip turns the sidebar's Part 1 into four links and zero forthcoming entries,
1.3's footer gains its next card, 1.4's footer shows no next (Part 2 remains
road-ahead), the sitemap grows by exactly two pages, the suggestions
allowlist admits the new paths automatically, and the Vietnamese edition
ships at the settled register.

**Why this priority**: Structural integration after content exists — plus the
first part-completion state the navigation has ever rendered.

**Independent Test**: From either landing, reach 1.4 in ≤2 steps; sidebar
Part 1 = 4 links, 0 forthcoming; 1.3↔1.4 footer cards both locales; 1.4 has
no next card; sitemap 30 → exactly 32; vi parity incl. byte-identical fences;
suggestion POSTs accepted for both new paths.

**Acceptance Scenarios**:

1. **Given** the manifest, **When** 1.4's entry flips (published + translated
   + settled reader-facing values), **Then** every surface updates with zero
   manual edits, and Part 1 renders complete for the first time (no
   forthcoming badge anywhere in it).
2. **Given** 1.4's footers, **Then** they link back to 1.3 and forward to
   nothing — the same empty-next state 0.5 held between parts, now at the
   1.4/Part-2 boundary.
3. **Given** the Vietnamese chapter, **Then** box/figure/fence counts match
   en, fences are byte-identical, and the prose follows the naturalized
   register and settled glossary ("package", "cửa ải"/"vượt qua", "bản giao
   kèo", "bộ khung biết đi" — the seeded title — "tin nhắn"; no calques or
   hyphenated compounds; naturalization self-review before presenting).

---

### Edge Cases

- **The additive-only rule meets its hardest test yet**: the services need to
  be startable, but the root `package.json` (a 1.1 fence) cannot gain scripts,
  and `compose.yaml` (a 1.2 fence) cannot gain service containers. The
  chapter must work within workspace-level mechanisms (per-package scripts,
  filtered runs) — or, if a fenced file genuinely must change, that is a
  surfaced design decision shown as an explicit diff, not a silent edit.
- **"Empty" must still be honest**: a skeleton with no business logic must
  nonetheless be a real deployable process — the chapter must be clear about
  what the services do (respond to health checks, log, carry request IDs,
  speak the protocol package's types where applicable) and what they
  deliberately don't (everything else).
- **Observability claims vs. this stage's reality**: NFR-OBS-01 names request
  ID, tenant ID, and correlation ID — but no tenants or cross-service calls
  exist yet. The chapter must record which fields exist now and which arrive
  with their features, not fake them.
- **Docker-free gate vs. running services**: tests must not require the
  compose stores or long-running processes; "the services start and answer"
  is a chapter demonstration and a verification step, not a unit-test
  dependency.
- **The protocol-package promise**: 1.3 told readers the skeleton "speaks
  nothing else" — the services' use of `@relay/protocol` must be visible and
  meaningful at skeleton scale, and honest about how much speaking an empty
  skeleton does.
- **Part-boundary navigation**: 1.4's empty next card, Part 1's complete
  state, and Part 2's road-ahead entry must all render correctly — states
  built long ago but exercised together for the first time.
- **Chapter/code drift across four chapters**: the fence battery now covers
  1.1 + 1.2 + 1.3 + 1.4 at one repo state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chapter 1.4 MUST exist as a published chapter titled per
  docs/07 ("Walking skeleton") at the manifest's seeded Part 1 path, in both
  locales, rendered through the existing shell with all established chrome.
- **FR-002**: The chapter MUST teach the walking-skeleton idea as docs/07's
  row states it — deploy the skeleton before the muscles, observability from
  line one — grounded in the SAD's service view (the API service and gateway
  as the first two of six) and ADR-04/05's division of labor between them.
- **FR-003**: The chapter MUST build both services with the row's four
  properties — health checks, request IDs, structured JSON logs, and empty-
  by-design scope — deriving specifics from the documents (NFR-OBS-01's log
  fields, EIR-API-05's X-Request-Id, the constitution's structured-logging
  clause) and recording as explicit decisions whatever they leave open.
- **FR-004**: The services MUST live under the workspace's existing
  `services/*` glob and consume `@relay/protocol` visibly and meaningfully;
  the chapter MUST end in the runnable, tested state with a closing
  `CHECKPOINT` covering: both services start, health endpoints answer,
  request IDs appear in responses and logs, gate green.
- **FR-005**: The chapter MUST pass the code-chapter battery: 2,000–4,000
  canonical words; ≥2 `WHY`; ≥1 `TRAP`; 1 `SKIP AHEAD` naming `part1-ch4`;
  ≥1 forward reference; 2–4 captioned figures; takeaways; exactly one closing
  `CHECKPOINT`.
- **FR-006**: The canonical repository MUST advance by exactly this chapter's
  content and be tagged `part1-ch4` (Dong's tag); new dependencies MUST be
  pinned, package-local, and reasoned; NO file fenced by 1.1/1.2/1.3 may be
  modified — any genuine need to do so is a surfaced design change shown as
  an explicit diff in the chapter, never a silent edit.
- **FR-007**: The chapter's file-content fences MUST byte-match the
  repository at `part1-ch4`; commands MUST replay; en/vi fences MUST be
  byte-identical; all twenty prior file fences (10+3+7) MUST still match at
  the new state.
- **FR-008**: Publishing MUST be manifest-only: 1.4's entry flips; all
  surfaces update automatically; sitemap grows from 30 to exactly 32 URLs;
  Part 1 renders complete (4 links, 0 forthcoming); the suggestions allowlist
  admits both new paths with zero edits.
- **FR-009**: The Vietnamese chapter MUST be structurally identical at the
  naturalized register per the settled glossary; identifiers, service names,
  endpoints, code, and commands stay English; naturalization self-review
  before presenting.
- **FR-010**: 100% of quoted content MUST be faithful to current
  docs/04/05/06; the invented-ID detector passes over both page.mdx and both
  figures.ts; service/endpoint names are document-derived or explicitly
  recorded decisions.

### Key Entities

- **Chapter 1.4**: Part 1's finale; sources docs/04 (NFR-OBS-01/06,
  EIR-API-05), docs/05 (§4 service view, §8 cross-cutting, ADR-04/05),
  docs/07 §2–3 and §5 (the Part 1 milestone); reader produces two running
  skeleton services with observability from line one.
- **The two services**: The API service and the gateway — the first occupants
  of `services/*`, empty of business logic, full of operational discipline;
  the pattern every later service chapter follows.
- **Chapter tag `part1-ch4`**: The checkout-able Part-1-complete state; diff
  from `part1-ch3` is the chapter.
- **The manifest flip**: 1.4's transition — the first flip that completes an
  entire part.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chapter body is 2,000–4,000 canonical words and passes the
  full battery in both locales with structural parity and byte-identical
  fences.
- **SC-002**: At `part1-ch4`, the gate passes (Docker-free) with meaningful
  service tests added; started locally, both services answer health endpoints
  with request IDs present in responses and in structured JSON log output —
  machine-verified.
- **SC-003**: 100% of file-content fences across ALL FOUR chapters match the
  repository state on comparison; verbatim spot-checks pass; the ID detector
  is clean.
- **SC-004**: From either landing, 1.4 is reachable in ≤2 steps; sidebar
  Part 1 shows exactly 4 links and 0 forthcoming; 1.3's footers show the next
  card and 1.4's show none; the sitemap holds exactly 32 URLs; suggestion
  submissions against both new paths succeed.
- **SC-005**: A test reader can go from the 1.3 checkpoint to the passing
  1.4 checkpoint within the chapter's stated time budget, using only the
  chapter.
- **SC-006**: Publishing changes only the manifest and adds content files —
  every surface, including the allowlist, updates by itself; Part 1's
  complete state renders correctly the moment the entry flips.

## Assumptions

- **Chapter scope is docs/07's row**: empty API + gateway with health checks,
  request IDs, structured logs. Real endpoints, WebSocket session logic,
  JWT verification, store connections, and business logic are Part 2's; the
  skeleton's emptiness is the point and is stated, not apologized for.
- **The service runtime pattern is a plan-level decision** (HTTP library or
  none, logging approach, process management) — bounded by the constitution
  (boring by design, TypeScript/Node per ADR-01) and by the additive-only
  rule's constraints on fenced files.
- **The repository conventions continue**: additive-only, tag per docs/07 §2
  (`part1-ch4`), fence-equals-repo by diff, Docker-free gate, commits/tags/
  pushes are Dong's.
- **The manifest seed from 013 holds** (title "Walking skeleton", titleVi "Bộ
  khung biết đi", path `/part-1/chapter-04/walking-skeleton`); the flip
  settles placeholder reader-facing values as 014/016 did.
- **The vi edition translates prose; code, service names, endpoint paths, and
  commands stay English** — settled conventions; Dong reads before
  committing, with the suggestions channel as backstop.
- **Part 2 is not seeded by this feature**: its chapters enter the manifest
  when Part 2's first feature begins — Part 1 completing leaves Part 2 as the
  road-ahead list, unchanged.

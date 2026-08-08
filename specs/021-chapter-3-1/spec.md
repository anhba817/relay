# Feature Specification: Tutorial Chapter 3.1 — Tenants All the Way Down

**Feature Branch**: `021-chapter-3-1`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "Building part 3 chapter 3.1 english only"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 3.1 and build the tenancy spine alongside it (Priority: P1)

As the tutorial's reader, I open Part 3's first chapter — "Tenants all the
way down" (docs/07 §3) — and the series changes register: Part 2 built a chat
backend that works, and Part 3 turns it into infrastructure somebody else can
sign up for. The chapter builds the container hierarchy every later chapter
hangs off — organisation → application → environment — and the signup path
that creates all three from a single OAuth authentication, with no form to
fill in (FR-TEN-01, FR-TEN-02). It also pays a debt the reader watched me
take on: chapter 2.1 stubbed the `applications` table with a DECISION saying
"the real application lifecycle belongs to Part 3's tenancy chapters," and
this is that chapter.

**Why this priority**: The chapter is the deliverable. Every remaining Part 3
chapter is scoped by these containers — keys are issued per environment
(3.2), outbox events carry a tenant (3.3), quotas are counted per application
(3.6), and the isolation gauntlet (3.7) attacks the boundary this chapter
draws.

**Independent Test**: A reader at the `part2-ch8` checkpoint can, using only
the chapter: migrate the tenancy tables, complete a signup against an OAuth
provider, watch one organisation, one application and one `development`
environment appear from that single act, and explain why the hierarchy has
exactly these three levels — without consulting docs/04 or docs/05.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** read end to end, **Then** it
   derives the tenancy hierarchy from the SRS (FR-TEN-01/02/03/04/07) and the
   SAD's data view, builds forward-only migrations for the new tables,
   implements the signup path, and closes in a runnable, tested state.
2. **Given** that the SAD defines `environments` but never defines
   `applications` or `organisations`, **When** the chapter introduces those
   tables, **Then** it records the derivation as an explicit chapter DECISION
   (the mechanism 2.1 established) rather than presenting invented schema as
   quoted specification.
3. **Given** the format rules (docs/07 §2, code-chapter battery), **Then** the
   chapter passes: 2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, exactly
   1 `SKIP AHEAD` naming tag `part3-ch1`, ≥1 forward reference, 2–4 captioned
   figures, takeaways, exactly one closing `CHECKPOINT`.
4. **Given** the chapter's factual claims, **Then** each traces to docs/04
   (FR-TEN-01/02/03/04/05/06/07, FR-DSH-01 where referenced), docs/05 (§3's
   context view, §6.1's `environments` definition), the constitution
   (Principle I), or an earlier chapter; anything the documents do not settle
   is recorded as a chapter decision.

---

### User Story 2 - The canonical code advances to tag `part3-ch1` (Priority: P2)

As a reader who wants the answer key — or who got stuck — the tenancy spine
exists in `relay-platform` as the diff from `part2-ch8` to `part3-ch1`: the
new tables and their migration, the signup path that provisions the trio, and
the tests that hold the invariants. The chapter's fences byte-match that
state, and every file an earlier chapter fenced is amended through a hunked
diff fence whose hunks apply cleanly to the published predecessor.

**Why this priority**: The tutorial's central promise is that the code and the
prose cannot drift. This increment is what makes chapter 3.1 checkable rather
than merely readable.

**Independent Test**: Checking out `part3-ch1` yields a workspace where the
Docker-free gate passes; with the compose stores up, all integration lanes
pass including the new tenancy suite; and `pnpm check:fences` replays every
published chapter onto the repository with no drift.

**Acceptance Scenarios**:

1. **Given** the chapter's file-content fences, **Then** each byte-matches the
   repository at `part3-ch1`, and each amendment to a previously fenced file
   is a hunked diff whose hunks apply to the state the earlier chapters left
   behind (the convention adopted in 2.7).
2. **Given** the two-lane gate, **Then** the Docker-free lane stays
   Docker-free and the tenancy tests live in an integration lane against the
   compose Postgres.
3. **Given** the `applications` stub from 2.1, **Then** the chapter replaces
   it with the real table through a forward-only migration and says so, in the
   pattern established by 2.4's index removal.
4. **Given** the existing Part 2 suites, **Then** they still pass unchanged in
   substance: the tenancy work must not weaken tenant isolation (FR-TEN-05)
   or alter the core loop's behaviour.

---

### User Story 3 - The chapter publishes in English, and the site stays honest (Priority: P3)

As a visitor to the tutorial site, chapter 3.1 appears as the first published
chapter of Part 3, in English, with the Vietnamese edition marked as not yet
translated rather than silently missing or half-machine-translated.

**Why this priority**: Publication is what makes the work reachable, and the
"English only" instruction is explicit in this feature's input; the Vietnamese
edition follows on its own cycle, as 2.6–2.8 did.

**Independent Test**: The site builds; the English chapter renders at its
canonical path; the Vietnamese path returns 404 while the chapter listing
shows it as untranslated; the fence-chain and docs-drift checks pass.

**Acceptance Scenarios**:

1. **Given** the chapter manifest, **When** 3.1 is published, **Then** its
   entry is `status: "published"` with an empty `translatedIn`, and Part 3's
   remaining chapters stay `forthcoming`.
2. **Given** the fence-chain checker, **Then** it reports the Vietnamese
   editions as mirrored for every chapter that has one, and does not fail
   because 3.1 lacks a translation.

---

### Edge Cases

- **The provider returns an identity that already has an organisation.** A
  second signup with the same provider identity must not create a second
  organisation, and must not fail with an error that leaks whether that
  identity exists.
- **The provider authenticates a person who is already a member of someone
  else's organisation.** Membership and ownership are different things; the
  chapter must say which one signup creates.
- **Provisioning fails halfway.** If the application is created and the
  environment is not, the reader is left with a tenant that cannot be used;
  the chapter must show the atomicity that prevents a half-built tenant.
- **A tenant identifier arrives from outside.** Every Part 2 surface trusts
  `x-relay-environment`; adding real tenancy above it must not make that seam
  more trusted than it was, nor retire it early (3.2 owns its retirement).
- **Two environments per application, no more.** FR-TEN-04 fixes the number
  at two (`development`, `production`); the chapter must show what enforces
  that rather than assuming callers behave.
- **An organisation with no members.** Deleting or transferring the last owner
  is out of scope here, but the chapter should not create a shape where it can
  silently happen.

## Requirements *(mandatory)*

### Functional Requirements

**The chapter (primary deliverable)**

- **FR-001**: The feature MUST produce one published English chapter at
  `part-3/chapter-01`, following the docs/07 §2 code-chapter battery, with the
  slug and title derived from docs/07's Part 3 table ("Tenants all the way
  down").
- **FR-002**: The chapter MUST derive the three-level hierarchy from the
  requirements rather than asserting it: why an organisation is not enough,
  why an application is not enough, and why the environment is the unit every
  Part 2 table already carries.
- **FR-003**: The chapter MUST show the signup path end to end — provider
  authentication, identity handling, and the single act that yields an
  organisation, an application, and a `development` environment (FR-TEN-01,
  FR-TEN-02) — including what the reader must configure to run it themselves.
- **FR-004**: The chapter MUST carry at least one TRAP drawn from a real
  failure encountered while building it, not a hypothetical one.
- **FR-005**: The chapter MUST record, as explicit DECISIONs, every schema
  element the source documents do not define — at minimum the `organisations`
  and `applications` tables and the human-membership table — and MUST NOT
  present them as quoted specification.
- **FR-006**: The chapter MUST state which dev-mode seams remain after it
  (the `x-relay-environment` header and dev-secret JWTs) and name the chapter
  that retires each (3.2), so the reader is never left believing the platform
  is more finished than it is.

**The code (answer key)**

- **FR-007**: The canonical repository MUST reach a state where the tenancy
  tables exist via forward-only migrations, the 2.1 `applications` stub is
  replaced, and the signup path provisions the trio atomically.
- **FR-008**: Provisioning MUST be all-or-nothing: a failure at any step MUST
  leave no partially built tenant.
- **FR-009**: The system MUST enforce FR-TEN-04's two-environment rule at the
  storage layer, not only in application code.
- **FR-010**: Signup MUST be idempotent with respect to a provider identity:
  authenticating twice MUST NOT produce a second organisation *owned by* that
  identity, and the outcome MUST be defined for an identity that exists but
  owns nothing.
- **FR-011**: Every new table MUST carry its tenant lineage such that
  FR-TEN-06 (non-null tenant identifier on every operational record) remains
  true, and the repository layer's mandatory scoping (Principle I) MUST extend
  to the new surfaces rather than being bypassed by them.
- **FR-012**: The work MUST include automated tests that hold the invariants
  above — provisioning atomicity, signup idempotency, the environment-count
  rule, and isolation between two organisations — in the appropriate lane, and
  MUST NOT slow or Dockerise the unit lane.
- **FR-013**: All existing Part 1 and Part 2 suites MUST continue to pass.

**Publication and fidelity**

- **FR-014**: Every file-content fence in the chapter MUST byte-match the
  repository at the chapter's tag; amendments MUST use hunked diff fences that
  apply cleanly to the published predecessor state.
- **FR-015**: The chapter MUST be published in English only, with the
  Vietnamese edition marked untranslated; no machine translation is produced
  in this feature.
- **FR-016**: The repository checks (`check:docs`, `check:fences`), the site
  build, and lint MUST all pass after publication.
- **FR-017**: If the chapter's work reveals a defect in an earlier chapter's
  code or prose, the feature MUST fix it forward and say so in the chapter,
  following the precedent set in 2.4, 2.6, 2.7 and 2.8.
- **FR-018**: The rule that platform humans and tenant end users are separate
  populations MUST be recorded as an architecture decision in the source
  documents, not only in chapter prose — the constitution requires behaviour to
  trace to a recorded decision, and every later chapter inherits this one.

### Key Entities

- **Organisation**: The billing and ownership boundary a person creates by
  signing up. Owns applications; has human members with roles.
- **Application**: A product within an organisation, with independent data,
  credentials and quotas (FR-TEN-03).
- **Environment**: The tenant identifier every Part 2 table already carries.
  Exactly two per application, `development` and `production` (FR-TEN-04),
  each with separate credentials and quotas.
- **Member**: A human's role within an organisation — `owner`, `admin`,
  `member` (FR-TEN-07). Distinct from the end users of Part 2, who belong to
  an environment and never sign in to Relay.
- **Provider identity**: The external account (GitHub or Google) that
  authenticates a human. The link between a person and their membership.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader starting from the Part 2 checkpoint can follow the
  chapter and reach a working signup that provisions the full trio, without
  consulting the source documents.
- **SC-002**: One authentication produces exactly one organisation, one
  application and one `development` environment — verified by an automated
  test, and demonstrated in the chapter with real output.
- **SC-003**: Repeating the same authentication produces no additional
  organisation, verified by an automated test.
- **SC-004**: An attempt to give an application a third environment fails,
  verified by an automated test.
- **SC-005**: Two organisations created in the same run cannot observe each
  other's applications, environments or messages, verified by an automated
  test that attacks the boundary with foreign identifiers.
- **SC-006**: Every factual claim in the chapter traces to a source document,
  an earlier chapter, or a recorded decision — with zero invented requirement
  or table identifiers.
- **SC-007**: The published chapter satisfies every code-chapter battery
  threshold, and the fence-chain check reports no drift across all published
  chapters.
- **SC-008**: All test lanes pass at the chapter's tag, and the unit lane
  remains Docker-free.

## Assumptions

- **Scope is one chapter.** This feature delivers chapter 3.1 only. Chapters
  3.2–3.7 stay `forthcoming`; API keys, user tokens and the dev-token endpoint
  are 3.2's subject and are out of scope here, as is the outbox (3.3).
- **No dashboard UI.** The signup path is a backend surface exercised by tests
  and a walk script. FR-DSH-01's "development API key on the first screen"
  needs both keys (3.2) and a dashboard (Part 5); this chapter may reference
  it as a forward promise but does not build it.
- **Real provider flow, dev-mode seam for tests.** The chapter teaches the
  actual OAuth authorisation-code flow named in FR-TEN-01 (GitHub as the
  worked example), and the automated lanes exercise it through a local stand-in
  for the provider so the suite stays deterministic and offline — the same
  pattern the series already uses for dev-secret JWTs (2.5) and the
  environment header (2.2). Configuring a real provider application is shown
  as a reader step, not required by the test lanes.
- **Roles are created, not yet managed.** Signup makes the authenticating
  human the `owner` of the new organisation (FR-TEN-07's role vocabulary is
  introduced), but invitations, role changes and member removal are deferred;
  the chapter names where they land.
- **Deletion is out of scope.** FR-TEN-08's confirmed, 30-day irreversible
  application deletion needs machinery this chapter does not build; it is
  named as forthcoming.
- **Environment credentials.** Environments are created with the signing
  secret the 2.1 schema already defines; issuing and rotating API keys belongs
  to 3.2.
- **Production environments.** FR-TEN-04 requires both environments to be
  possible, but FR-TEN-02 only auto-creates `development` at signup. The
  chapter builds the rule for two and the automatic creation of one.
- **An ADR may be required.** The source documents contain no ADR covering the
  identity provider or the tenancy hierarchy's shape. If the chapter makes a
  decision of that weight, this feature records it as an ADR in docs/05 with a
  matching deep dive in docs/06, following the precedent of ADR-15/16/17.
- **Baseline state.** Work starts from the current uncommitted `part2-ch8`
  state; Part 2's tags are not yet cut, so the chapter's SKIP AHEAD and
  CHECKPOINT name `part3-ch1` on the same "intended, not yet cut" basis as
  chapters 2.2–2.8.

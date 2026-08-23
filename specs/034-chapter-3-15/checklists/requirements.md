# Specification Quality Checklist: Chapter 3.15 — the surface a customer drives

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-23
**Feature**: [spec.md](../spec.md)

## Content Quality

- [X] No implementation details (languages, frameworks, APIs)
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders
- [X] All mandatory sections completed

## Requirement Completeness

- [X] No [NEEDS CLARIFICATION] markers remain
- [X] Requirements are testable and unambiguous
- [X] Success criteria are measurable
- [X] Success criteria are technology-agnostic (no implementation details)
- [X] All acceptance scenarios are defined
- [X] Edge cases are identified
- [X] Scope is clearly bounded
- [X] Dependencies and assumptions identified

## Feature Readiness

- [X] All functional requirements have clear acceptance criteria
- [X] User scenarios cover primary flows
- [X] Feature meets measurable outcomes defined in Success Criteria
- [X] No implementation details leak into specification

## Notes

- **Scope resolved**: the whole deferred surface, on the user's decision. Twelve SRS
  clauses, five unread columns, three corrections. The chapter division is deferred to
  planning by FR-040, which requires the split to be measured before any chapter prose
  exists — the one thing chapter 3.12's close-out asks the next feature to do
  differently, after it estimated 37 fenced files and shipped 61 across three chapters.

- **Nine user stories, priorities taken from the SRS rather than invented.** P1: the
  private channel, removal, profiles, listing. P2: unread, roles, archiving, bulk
  upsert and deletion. P3: banning. Each story's priority matches the priority the SRS
  gives the clause it covers, checked clause by clause.

- **Where this spec deliberately names code**, and why it is not implementation
  leaking in: the subject of the feature IS that five declared columns have no reader,
  one shipped comment is false, and one clause's absence surfaces as a misleading
  `400`. A specification that described those findings without naming the file and line
  would not be checkable. Every claim was measured — `grep` over `services/**` and
  `packages/**` excluding tests, schema and build output — not read off a document.

- **Twelve clauses, and FR-USR-02 was found last.** It says a user is created on first
  **authentication**; `createUser` is reached only from first **membership**. The
  symptom is already in the platform: a token minted for an unknown identifier
  authenticates and then fails its first send with `unknown user`.

- **Three corrections to earlier records**, two of which this spec could make and one
  it could not. Chapter 3.12's traceability map recorded FR-CHN-04 as delivered and
  described it with a paraphrase belonging to FR-CHN-06 — corrected. The same map said
  "no membership check on any read path" — corrected. The same sentence in
  `channels.schema.ts:26` sits inside a titled fence in chapter 3.13's page in two
  locales, so FR-037 schedules it as fence work rather than this spec editing three
  files during a specification command.

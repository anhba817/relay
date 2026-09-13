# Specification Quality Checklist: Chapter 4.1 — the question the counters can't answer

**Purpose**: Validate specification completeness and quality before `/speckit-implement`
**Created**: 2026-09-12 at specify time · **Re-run**: 2026-09-12 after analysis pass 5
**Feature**: [spec.md](../spec.md)

**What this certifies, stated as numbers so drift is detectable.** The first version of this file
ticked sixteen boxes and stated no counts, which made it impossible to compare against the
document it certified — and the spec then moved underneath it four times. Chapter 3.24 built
`check-checklist.py` for that reason, and 045's own note is *a gate that certifies silently
cannot be checked.*

    functional requirements      19   FR-001 … FR-015, with FR-003a/b/c and FR-007a
    success criteria              8   SC-001 … SC-008
    user stories                  3   P1, P2, P3
    acceptance scenarios         12   4 + 4 + 5, minus one heading that carries none
    edge cases                    6
    tasks                        76   T001 … T068, plus T012a T013a T013b T020a T020b T033a
                                      T047a T047b
    research questions            8   R1 … R8

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) — *interpreted; see Note 1*
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders — *interpreted; see Note 1*
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic — *see Note 1*
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria — **this box was false between
  passes 2 and 5.** FR-003b and FR-003c were added by analysis and had tasks but no scenario;
  US3 scenarios 4 and 5 were written in pass 5 to close it
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification — *see Note 1*
- [x] Every functional requirement is cited by at least one task — 14 of 19 by identifier, 5 by
  inference (FR-003, FR-003a, FR-007, SC-003, SC-004). Filed as a LOW finding and left open

## Notes

**1. Four items are marked against this project's convention rather than the template's literal
reading.** The template assumes a feature whose subject is a product capability. A chapter
specification's subject is **the repository** — it teaches a schema, a query and a measurement,
and a version stripped of `messages`, `created_at`, `environment_id` and the execution plan would
describe nothing a writer could act on. `specs/042-chapter-3-24/spec.md` is the published
precedent, naming `messages.attachments`, `media_id` and the protocol's schema files throughout.
Stripping the detail would make the specification worse, so it was not stripped.

**2. Five analysis passes changed these artifacts nineteen times, and the shape of what they
found changed as they went.**

    pass 1   8 at MEDIUM+   4 substantive, from running commands
    pass 2   4 at MEDIUM+   3 new, from reading the script next door
    pass 3   1 at MEDIUM+   from a 403 on the first POST
    pass 4   3 at MEDIUM+   2 introduced by passes 2 and 3
    pass 5   4 at MEDIUM+   all in artifacts no pass had re-read

The largest single finding was pass 1's: a test file under `scripts/` that **no vitest config
collects and no lane runs**, inside a chapter about instruments that report zero without looking.
The most expensive to have missed would have been pass 2's — nothing migrated the corpus
database, so Phase 2 would have inserted into a database with no tables.

**Passes 4 and 5 found defects the earlier passes introduced.** The requirement list had run
`FR-003, FR-003c, FR-003b, FR-003a` because two passes each inserted above what was already
there; the cleanup verification certified that no corpus database remained one phase before six
more were created; and this file certified a spec that had gained two requirements since it was
written. **A fix is a change, and a change is a thing to re-read.**

**3. Two things remain open and neither blocks implementation.**

- **The tag convention.** `part3-ch18` is `54b2cd53` and `rework/part3-ch18` is `3732d6cf`; both
  exist, and `README.md:8` promises one tag per chapter. The chapter can be written and reviewed;
  it cannot be tagged.
- **`check:fences` opens at 109** (APPLY 74, HEAD 35) — measured by running it, not inherited.
  FR-015 requires this chapter's contribution to be reported as a delta rather than the gate
  declared green.

**4. Five LOW findings are open by decision, not oversight**: requirement identifiers cited by
inference rather than by name (G4); three names for one artifact — `seeder.md`, `corpus.mjs`,
"the corpus" (I1); NFR-PRF-02 saying *excluding network* where a loopback loop includes it (I2);
`pg_total_relation_size` unable to separate a column's cost from an index's (A1); and `jq` and
`psql` used in the quickstart and declared nowhere (T3).

**5. No [NEEDS CLARIFICATION] markers were ever raised.** The decisions that would have produced
them — the part's name, the chapter addressing scheme, the milestone's exit, and this chapter's
premise — were taken during grooming and are recorded in `docs/12-part-4-structure.md` §2.1–§2.5.

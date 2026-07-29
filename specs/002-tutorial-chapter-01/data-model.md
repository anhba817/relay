# Data Model: Tutorial Chapter 0.1

**Feature**: `specs/002-tutorial-chapter-01` · **Date**: 2026-07-29

No runtime storage. The entities are the typed series manifest (`lib/tutorial.ts`) and
the chapter content structure the shell consumes.

## E1 — Part

| Field | Type / Rule | Source |
|---|---|---|
| `number` | 0–8 | docs/07 §3 arc |
| `title` | e.g. "The idea and the paper" | docs/07 §3 |
| `chapters` | Chapter[] — populated for Part 0 (all five); other parts may list none yet | FR-008 (ToC shows Part 0 fully) |

## E2 — Chapter

| Field | Type / Rule | Source |
|---|---|---|
| `id` | `"0.1"` … — unique, matches docs/07 numbering | docs/07 §3 |
| `path` | full route, e.g. `/part-0/chapter-01/from-app-to-infrastructure`; its final segment is the **slug** (kebab-case main clause of title, subtitle dropped) | research R2, clarification 2026-07-29 |
| `title` | e.g. "From app to infrastructure — finding the real product" | docs/07 §3 table |
| `status` | `"published"` \| `"forthcoming"` | FR-007 |
| `readerProduces` | e.g. "A positioning statement; non-goals list" | docs/07 §3 table |
| `sourceDoc` | e.g. `docs/01-product-vision.md` | docs/07 §3 table |
| `readerMinutes` | estimated reading + exercise time in minutes, within docs/07 §2's 60–120 budget (0.1: ~90); rendered by ChapterHeader | docs/07 §2, analyze I1 |

**Invariants**: exactly one chapter with `id: "0.1"` and `status: "published"` after
this feature; chapters 0.2–0.5 present with `status: "forthcoming"`; `nextChapter("0.1")`
returns 0.2 (forthcoming → rendered as non-link with badge, per US3/AC2).

**State transition**: `forthcoming → published` (one direction), performed by editing
the manifest when a chapter ships.

## E3 — Chapter content structure (page.mdx)

| Element | Rule | Source |
|---|---|---|
| Metadata export | title + description for the route | research R2 |
| `<ChapterHeader id="0.1" />` | first element | research R6 |
| Body prose | 2,000–4,000 words, first-person plural present tense, R7 section arc | FR-004, SC-001 |
| `<Why>` boxes | ≥ 2, each citing docs/01 | SC-004, FR-004 |
| `<ForwardRef>` | ≥ 1, tying a claim to a later part | FR-005, SC-004 |
| `<SkipAhead>` | ≥ 1 (Part 0 is skippable by design) | FR-004 |
| Exercise section | positioning-statement template + worked example + non-goals (≥3, reasoned) + yes/no self-checks | FR-003 |
| Takeaways block | compact, skip-safe | FR-006 |
| `<Checkpoint>` | exactly 1, at the end, states required reader artifacts | SC-004, US2/AC3 |
| `<ChapterFooter id="0.1" />` | last element | research R6 |

## E4 — Box conventions (components/tutorial/boxes.tsx)

| Component | Semantic | Token family (both modes) |
|---|---|---|
| `Why` | links a claim to its source doc / requirement | accent |
| `Trap` | the bug/mistake you'd make naively | destructive (tinted) |
| `Checkpoint` | verify before continuing | primary |
| `SkipAhead` | what to skip and what you must still know | muted |
| `Revised` | later-part revision notice | secondary |
| `ForwardRef` | "this becomes X in Part N" | accent (with part label) |

**Invariant (SC-006)**: styling uses Violet Bloom CSS variables only — no literal
colors; all render distinctly in light and dark.

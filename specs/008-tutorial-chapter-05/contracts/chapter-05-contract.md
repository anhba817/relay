# Contract: Chapter 0.5 — Routes, Navigation, and Content Guarantees

**Feature**: `specs/008-tutorial-chapter-05` · **Date**: 2026-07-30

## C1 — Routes

| Route | Guarantee |
|---|---|
| `/part-0/chapter-05/deciding-out-loud` | English chapter, static, hreflang pair, shell identity "Part 0 · Chapter 0.5" |
| `/vi/part-0/chapter-05/deciding-out-loud` | Vietnamese chapter inside `lang="vi"`, hreflang pair, manifest's approved vi title |
| All pre-existing routes | Prose unchanged; only manifest-driven navigation surfaces differ |

## C2 — Navigation (automatic from the manifest) + Part 0 completion

| Surface | Guarantee |
|---|---|
| Both landings | All five Part 0 chapters as links; **zero forthcoming badges within Part 0**; parts 1–8 unchanged |
| 0.4 footers (both locales) | Next-card now links to 0.5 in the same locale |
| 0.5 footers (both locales) | Previous links to 0.4; **no next card** (last published chapter — renders as a clean single-card grid + contents link, both themes); zero hrefs to any chapter beyond 0.5 |
| Language switcher on 0.5 | Maps en↔vi both directions |

## C3 — Content guarantees

| Item | Bound |
|---|---|
| Specimen fidelity | D1/D8 rows, ADR-03 core, ADR-13 core quoted per the 007 verbatim definition (words exact, greppable in docs/05; layout free); ADR-14 and docs/06 themes referenced faithfully |
| The taught machinery | Drivers distillation (incl. D8 as non-requirement context); full ADR anatomy; two-document split; immutability/supersede; "attack the driver, not the choice" |
| The chain close | ADR-13's "reverses the v1.0 file-storage exclusion" status quoted; the 0.1→0.3→0.4→0.5 chain named explicitly |
| Rendering | ≤3 fences; no pipe tables; readable without fences |
| Format battery | words 2,000–4,000 canonical; WHY ≥2; SKIP AHEAD ≥1; ForwardRef ≥1; CHECKPOINT =1 (closes Part 0); takeaways present |
| Exercise | drivers table (3–6, requirement-sourced, consequences) + two ADRs (≥2 rejected-with-reasons each, observable reversal conditions) + yes/no self-checks |
| Translation | Structural parity; settled register/glossary; ADR/D/requirement IDs and status keywords English; fences English + "(Dịch nghĩa:)" gloss |

## C4 — Scripted verification bounds (quickstart V2)

| Check | Bound |
|---|---|
| Canonical word count (en) | 2,000 ≤ n ≤ 4,000 |
| Box counts en / vi | equal per type; Checkpoint exactly 1 each |
| Fence lines | equal en/vi; ≤6 lines (≤3 blocks) |
| Pipe-table lines | 0 |
| ID detector | every `ADR-[0-9]+` and `\bD[1-8]\b` reference exists in docs/05; every FR/NFR/EIR/DR/CON/ASM ID exists in docs/04 |
| hreflang (case-insensitive) | ≥2 per page, both 0.5 pages |
| `div lang="vi"` | vi page only |
| 0.4 footers | href to 0.5 present (both locales) |
| 0.5 footers | href to 0.4 present; zero hrefs matching `chapter-0[6-9]` or `part-[1-8]/chapter` |
| Landings (both) | 5 Part 0 chapter hrefs; zero forthcoming badges within the Part 0 section |

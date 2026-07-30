# Contract: Chapter 0.4 — Routes, Navigation, and Content Guarantees

**Feature**: `specs/007-tutorial-chapter-04` · **Date**: 2026-07-30

## C1 — Routes

| Route | Guarantee |
|---|---|
| `/part-0/chapter-04/requirements-you-can-test` | English chapter, static, hreflang pair, shell identity "Part 0 · Chapter 0.4" |
| `/vi/part-0/chapter-04/requirements-you-can-test` | Vietnamese chapter inside `lang="vi"`, hreflang pair, manifest's approved vi title |
| All pre-existing routes | Prose unchanged; only manifest-driven navigation surfaces differ |

## C2 — Navigation (automatic from the manifest)

| Surface | Guarantee |
|---|---|
| Both landings | 0.4 listed as a link; 0.5 remains a forthcoming non-link |
| 0.3 footers (both locales) | Next-card now links to 0.4 in the same locale |
| 0.4 footers (both locales) | Previous links to 0.3; next shows 0.5 with localized forthcoming badge, zero `href` links to 0.5 paths |
| Language switcher on 0.4 | Maps en↔vi both directions |

## C3 — Content guarantees

| Item | Bound |
|---|---|
| Quote fidelity | Every requirement row shown is faithful to the current docs/04 per the A1 definition: ID, shall-statement text, priority, and method values exact (statement text greppable in the source); layout separators free (middot rendering sanctioned); IDs never invented, renumbered, or paraphrased-next-to |
| The taught machinery | Row anatomy; T/D/I/A with one real example each; stable-ID discipline; P1–P5↔phases; 224-requirements-sequenced argument |
| The traces | Tuan ★ → FR-MSG-04/FR-RTM-03/FR-SDK-04; Priya ★ → FR-MSG-07/08/10 + FR-MOD-01; FR-TEN-05 as the star requirement with its Sev-0/every-build argument |
| The change beat | FR-MED as the reversed-non-goal example; FR-MED-09's Priya trace quoted |
| Rendering | ≤3 fenced specimen blocks; NO pipe tables; readable without fences |
| Format battery | words 2,000–4,000 canonical; WHY ≥2; SKIP AHEAD ≥1; ForwardRef ≥1; CHECKPOINT =1; takeaways present |
| Exercise | 8–15-row slice; ★→top priority; opinion hunt incl. the "shall be fast" repair; yes/no self-checks |
| Translation | Structural parity; register + glossary; IDs/`shall`/T-D-I-A codes in English; shall-statement prose translated |

## C4 — Scripted verification bounds (quickstart V2)

| Check | Bound |
|---|---|
| Canonical word count (en) | 2,000 ≤ n ≤ 4,000 |
| Box counts en / vi | equal per type; Checkpoint exactly 1 each |
| Fence lines | equal en/vi; ≤6 lines (≤3 blocks) |
| Pipe tables in body | 0 (`grep -c '^|'` == 0 outside fences — no GFM) |
| Quoted-ID verbatim check | every `FR-`/`EIR-`/`NFR-`/`DR-` family ID and every short-form `CON-`/`ASM-` ID in the chapter exists in docs/04 (analysis I1) |
| hreflang (case-insensitive) | ≥2 per page, both 0.4 pages |
| `div lang="vi"` | vi page only |
| 0.3 footers | href to 0.4 present (both locales) |
| 0.4 footers | href to 0.3 present; `href="[^"]*chapter-05` count == 0 |
| Landings | 0.4 href present in both locales |

# Contract: Chapter 0.3 — Routes, Navigation, and Content Guarantees

**Feature**: `specs/006-tutorial-chapter-03` · **Date**: 2026-07-30

## C1 — Routes

| Route | Guarantee |
|---|---|
| `/part-0/chapter-03/journeys-where-products-die` | English chapter, static, hreflang pair, shell identity "Part 0 · Chapter 0.3" |
| `/vi/part-0/chapter-03/journeys-where-products-die` | Vietnamese chapter inside `lang="vi"`, hreflang pair, localized shell, manifest's approved vi title |
| All pre-existing routes | Prose unchanged; only manifest-driven navigation surfaces differ |

## C2 — Navigation (automatic from the manifest)

| Surface | Guarantee |
|---|---|
| Both landings | 0.3 listed as a link; 0.4–0.5 remain forthcoming non-links |
| 0.2 footers (both locales) | Next-card now links to 0.3 in the same locale |
| 0.3 footers (both locales) | Previous links to 0.2; next shows 0.4 with localized forthcoming badge, zero `href` links to 0.4 paths |
| Language switcher on 0.3 | Maps en↔vi both directions |

## C3 — Content guarantees

| Item | Bound |
|---|---|
| Journey fidelity | All four journeys present; stage facts, ★ assignments (Mai: first message; Priya: reconstruct; Tuan: lose signal), the effort ranking, and the adoption/deserving distinction trace to docs/03 |
| The ★ concept | Defined, argued per journey, and tied to docs/03's closing (effort concentrates on ★s) |
| Diagrams | ≤2 fenced code blocks; chapter reads correctly without them; vi labels translated |
| Format battery | words 2,000–4,000 canonical; WHY ≥2; SKIP AHEAD ≥1; ForwardRef ≥1; CHECKPOINT =1; takeaways present |
| Exercise | ≥2 journey maps (one invisible persona at single-interaction granularity), one ★ each with written reason, yes/no self-checks |
| Translation | Structural parity; established register + glossary; manifest vi title verbatim |

## C4 — Scripted verification bounds (quickstart V2)

| Check | Bound |
|---|---|
| Canonical word count (en) | 2,000 ≤ n ≤ 4,000 |
| Box counts en / vi | equal per type; Checkpoint exactly 1 each |
| hreflang (case-insensitive) | ≥2 per page, both 0.3 pages |
| `div lang="vi"` | vi page only |
| 0.2 footers | href to 0.3 present (en→en, vi→vi) |
| 0.3 footers | href to 0.2 present; `href="[^"]*chapter-04` count == 0 |
| Landings | 0.3 href present in both locales |
| Fenced blocks | ≤2 per file; identical count en vs vi |

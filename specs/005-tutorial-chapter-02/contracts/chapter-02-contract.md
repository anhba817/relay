# Contract: Chapter 0.2 — Routes, Navigation, and Content Guarantees

**Feature**: `specs/005-tutorial-chapter-02` · **Date**: 2026-07-30

## C1 — Routes

| Route | Guarantee |
|---|---|
| `/part-0/chapter-02/four-people-who-will-judge-us` | English chapter, statically rendered, hreflang pair, shell identity "Part 0 · Chapter 0.2" |
| `/vi/part-0/chapter-02/four-people-who-will-judge-us` | Vietnamese chapter inside the `lang="vi"` subtree, hreflang pair, localized shell |
| All pre-existing routes | Byte-level prose unchanged; only manifest-driven navigation surfaces (footers, landings) may differ |

## C2 — Navigation (all automatic from the manifest)

| Surface | Guarantee |
|---|---|
| Both landings | 0.2 listed as a link with its locale's title and readerProduces; 0.3–0.5 remain forthcoming non-links |
| 0.1 footers (both locales) | Next-card is now a live link to 0.2 in the same locale |
| 0.2 footers (both locales) | Previous links to 0.1 (same locale); next shows 0.3 with the localized forthcoming badge, non-link |
| Language switcher on 0.2 | Maps en↔vi 0.2 pages both directions |

## C3 — Content guarantees

| Item | Bound |
|---|---|
| Persona fidelity | Every persona attribute traces to docs/02; the influence ordering and its reasons match docs/02's trade-off section; the E2E worked example is docs/02's, not invented |
| Invisible-user lesson | Tuan's constraint list appears and is forward-referenced to Part 2 |
| Format battery | words 2,000–4,000 (canonical count); WHY ≥2; SKIP AHEAD ≥1; ForwardRef ≥1; CHECKPOINT =1; takeaways block present |
| Exercise | ≥3-persona derivation w/ influence reasons + invisibility test + yes/no self-checks; Relay's set as worked example |
| Translation | Structural parity (box counts per type equal); storytelling register + 0.1 glossary; persona names unchanged |

## C4 — Scripted verification bounds (quickstart V2)

| Check | Bound |
|---|---|
| Canonical word count (en) | 2,000 ≤ n ≤ 4,000 |
| Box counts en / vi | equal per type; Checkpoint exactly 1 each |
| hreflang (case-insensitive) | ≥2 per page, both 0.2 pages |
| `div lang="vi"` | on the vi page only |
| 0.1 footers | contain href to 0.2 (en page → en path; vi page → vi path) |
| 0.2 footers | contain 0.3 title text, zero hrefs to 0.3 paths |
| Landings | 0.2 href present in both locales |

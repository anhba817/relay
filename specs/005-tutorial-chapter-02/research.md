# Research: Tutorial Chapter 0.2 — Four People Who Will Judge Us

**Feature**: `specs/005-tutorial-chapter-02` · **Date**: 2026-07-30

Grounded in docs/02-personas.md (read in full; unchanged by the 2026-07-30
product-vision commit), docs/07 §3, and the infrastructure delivered by features
002–004. Almost no technical decisions remain — the series machinery exists; the
decisions here are editorial.

## R1 — Address and manifest: already reserved, one field to validate

- **Decision**: The chapter lives at the path feature 004 already wrote into the
  manifest: `/part-0/chapter-02/four-people-who-will-judge-us` (title has no
  subtitle, so the slug is the full title kebab-cased — consistent with the slug
  rule). Publishing = flipping the existing manifest entry: `status: "published"`,
  add `translatedIn: ["vi"]`, and validate `readerMinutes` (currently 75) against
  the finished chapter.
- **Rationale**: Feature 004 pre-registered all Part 0 chapters with paths and
  Vietnamese titles precisely so a new chapter would be a manifest flip plus content
  files (its C5 contract). Nothing else to decide.
- **Alternatives considered**: none needed — deviating from the reserved path would
  break the counterpart-mapping rule for no reason.

## R2 — English chapter: section arc derived from docs/02's own argument

- **Decision**: The chapter walks docs/02's structure as a derivation from 0.1's
  artifacts, in this arc:
  1. **Cold open** — the positioning statement names "product engineering teams";
     but a statement doesn't ship features. Who actually judges us? (Pointer back to
     0.1 for skippers; SKIP AHEAD box early.)
  2. **The unusual ordering** — influence, not headcount: the person who *uses* it,
     the person who *pays* for it, and the person who *benefits* from it are three
     different people — and the beneficiary never knows it exists (docs/02 intro).
  3. **Mai, the integrating developer** — primary persona; "if a decision helps Mai
     and hurts everyone else, it is probably still the right decision"; her
     evaluation ritual (docs reading, protocol check, throwaway prototype) as
     requirements-in-disguise. WHY box citing docs/02 persona 1.
  4. **David, the buyer and blocker** — doesn't read the SDK, can veto it;
     buy-versus-regret; cost modelling, export paths, incident honesty.
  5. **Priya, the daily operator** — not served directly; "Relay makes it possible
     for Mai to serve her in an afternoon"; tombstones and edit history exist
     because of her.
  6. **Tuan, the invisible end user** — never signs up, never hears the name Relay,
     feels every latency spike; his needs become protocol constraints (cursor
     backfill, server ordering, idempotency keys, jittered backoff, honest message
     states). ForwardRef box → Part 2 (chapters 2.3/2.7/2.8 are literally Tuan's
     list turned into code and tests).
  7. **When they collide** — docs/02's resolution order (Tuan's reliability > Mai's
     speed > David's predictability > Priya's completeness > storage efficiency) and
     the E2E worked example resolving against the ordering, echoing 0.1's non-goals
     reversal lesson (reasons recorded, not assumed). Second WHY box.
     **Mandatory reconciliation (analysis A1)**: the chapter MUST explicitly
     distinguish and reconcile the two orderings it teaches, because they are nearly
     inverted — Tuan ranks *last* in influence (beat 2) yet his reliability wins
     *first* in conflicts (this beat). The reconciliation is the chapter's sharpest
     teaching moment: influence measures who shapes product decisions; the resolution
     order decides whose need wins when needs collide — and the invisible user, having
     no voice at all, gets his needs promoted to non-negotiable constraints precisely
     so that his silence never means his loss.
  8. **Exercise** — derive the reader's persona set (R3).
  9. **Takeaways + CHECKPOINT** (artifact required before 0.3, which turns personas
     into journeys).
- **Rationale**: Mirrors docs/02's own §-order (it already reads as an argument);
  FR-002/003 need the ordering-with-reasons and invisible-user lessons carried by
  the structure itself. Target ~2,200 words body + ~700 exercise, inside the
  2,000–4,000 band.
- **Alternatives considered**: four profile cards with commentary (explicitly
  forbidden by US1/AC1 — "not four pasted profile cards"); leading with Tuan for
  drama (breaks the influence-ordering lesson the chapter exists to teach).

## R3 — Exercise design: a persona-derivation template with the invisibility test

- **Decision**: Exercise 1: from the reader's 0.1 positioning statement, extract the
  candidate people (who integrates, who pays, who operates, who merely experiences),
  then write ≥3 personas using the docs/02 field set — role in the product,
  goals, frustrations, what wins/loses them — plus an explicit influence ordering
  with a stated reason per rank. Exercise 2: the invisibility test — identify the
  persona who never chooses the product, and write the constraints they impose
  (Tuan's list as worked example). Self-checks (yes/no): ordering has reasons (not
  org-chart seniority); each persona is derivable from the positioning statement;
  at least one persona never signs up; each "what loses them" is an action the
  reader's team could actually take by accident.
- **Rationale**: FR-005's field requirements; the invisibility test is the chapter's
  distinctive lesson (docs/07: "persona set incl. the invisible end user"); checks
  follow 0.1's yes/no convention.
- **Alternatives considered**: demographic persona templates (age/photo/quote) —
  rejected; docs/02's own design pointedly ties every field to product decisions.

## R4 — Vietnamese translation: the 0.1 register, applied by the established workflow

- **Decision**: Author the English chapter first; translate with the
  storytelling register codified in the approved 0.1 translation (per the
  `/translate-mdx` style guide): expressive narrative Vietnamese; dev terms kept in
  English (non-goals, threads, scope, retry, backfill, idempotency → đẳng xâm
  (idempotent), audit trail → nhật ký vết); glossary continuity — *tuyên ngôn định
  vị*, *mũi nêm (wedge)*, *chấm xanh nói dối*. Persona names (Mai, David, Priya,
  Tuan) unchanged. A small resonance worth using, not inventing: Mai and Tuan are
  Vietnamese names in the source material — the vi text may let that land naturally
  without adding claims. Manifest `readerProducesVi` for 0.2 gets the glossary
  treatment ("...bao gồm người dùng cuối vô hình" — already present from 004).
- **Rationale**: FR-007 requires the established voice; the glossary prevents the
  cross-chapter terminology drift that FR-007 calls out.
- **Alternatives considered**: literal translation first + restyle later (0.1's
  history showed going straight to the register is cheaper).

## R5 — What does NOT change

- **Decision**: No component, i18n, styling, or navigation code changes. Chapter
  0.1's prose files are untouched (its footers update from the manifest). The only
  code-adjacent edit is the manifest entry (R1). If implementation discovers a
  missing capability, it stops and surfaces it (spec assumption) rather than
  patching infrastructure inside a content feature.
- **Rationale**: SC-006 (zero hand-edited navigation) is the point of the 002/004
  investment; this feature proves it.

## R6 — Verification: the established scripted battery + one new pair

- **Decision**: Reuse the chapter battery: word count by the canonical procedure;
  box counts (WHY ≥2, SKIP AHEAD ≥1, ForwardRef ≥1, CHECKPOINT =1); en↔vi
  structural parity; hreflang pair on both 0.2 pages; `div lang="vi"` scoping.
  New for this feature: 0.1→0.2 forward-navigation check in both locales (footer
  next-card is now a live link), and 0.2's footer shows 0.3 forthcoming in both
  locales. Manual: Dong's translation read-through (V5-equivalent), reading-time
  sanity check against `readerMinutes`.
- **Rationale**: Same rigor as 0.1/004; the new pair tests exactly what publishing
  a second chapter changes.

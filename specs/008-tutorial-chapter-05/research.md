# Research: Tutorial Chapter 0.5 — Deciding Out Loud

**Feature**: `specs/008-tutorial-chapter-05` · **Date**: 2026-07-30

Grounded in the current docs/05-sad.md (drivers D1–D8, terse ADR-01..14 incl. the new
media ADRs) and docs/06-adr-deep-dives.md (fourteen deep dives + "Reading the
fourteen together"), docs/07 §3, and the conventions settled across features 005–007.

## R1 — Manifest: the final Part 0 flip

- **Decision**: Flip 0.5 to `status: "published"`, add `translatedIn: ["vi"]`,
  validate `readerMinutes` (110). Path (`/part-0/chapter-05/deciding-out-loud`),
  `titleVi` ("Quyết định thành tiếng — bản SAD và thói quen viết ADR"), and
  `readerProducesVi` already reserved/approved — binding.
- **Note**: This flip completes Part 0 — after it, `nextChapter("0.5")` returns
  nothing (parts 1–8 hold no chapters). The last-chapter footer state is verified,
  not assumed (spec edge case, R6).

## R2 — English chapter: drivers → ADR anatomy → the discipline → the chain closes

- **Decision**: Eight beats:
  1. **Cold open** — the SRS slice is a list of promises; an architecture is how we
     intend to keep them. But 224 requirements cannot each drive a design — the
     handful that do are the *drivers*, and docs/05 says the quiet part aloud:
     everything else is implementation. Inputs pointer (0.4 slice); SKIP AHEAD.
  2. **The drivers table** — distillation shown on two specimens: D1 ("no
     acknowledged message may be lost" ← FR-MSG-05/06, consequence: ack only after
     durable commit, one transactional store) and D8 ("one engineer must be able to
     run and reason about it" — the driver that is not a requirement at all:
     portfolio reality, the anti-sprawl force behind "six services, not fifteen").
     Fence 1: the D1 and D8 rows.
  3. **The ADR form, walked on ADR-03** — per-channel sequences via row lock, chosen
     because it resolves SRS Open Question 1 and shows every anatomy element:
     status; drivers (D1, D3); the decision with its signature argument ("the lock
     is not a cost, it is the mechanism" — serialising a channel's writes *is*
     FR-MSG-03); trade-offs accepted; rejected alternatives with reasons (per-tenant
     sequence = one hot row for zero benefit; Postgres sequences = non-transactional
     gaps break dedup; Snowflake IDs = not gap-free, complicating the client's "did
     I miss something?"); and the reversal condition. Fence 2: ADR-03's terse core.
     Then the two-document split: the SAD holds the terse record; docs/06 holds the
     deep dive (Problem → Options → analysis → consequences), and the immutability
     rule — accepted ADRs never change; superseding takes a new ADR.
  4. **The review discipline** — docs/05's closing italic: every ADR states its
     reversal condition or rejected alternatives, so *"the productive move is to
     attack the driver, not the choice — the choices follow from D1–D8 fairly
     mechanically."* First WHY box (SAD §2/§9).
  5. **The chain closes: ADR-13/14** — ADR-13's status line literally reads
     *"reverses the v1.0 file-storage exclusion"*: the 0.1 non-goal, reversed in
     0.1's own terms, specified in 0.4 (FR-MED), now *defended* in architecture —
     the design answers the exclusion's cost argument "by not building any of it".
     ADR-14's one-mental-model-twice-applied (pending/ready/rejected mirrors
     sending/sent/failed) and its scan-gates-bytes-never-messages line. Fence 3:
     ADR-13's status + core decision. Second WHY box (docs/06 — "every decision
     names its own undoing": reversal triggers keep a solo-built system honest).
  6. **Reading the fourteen together** — docs/06's three themes as the character of
     the architecture: durability has one home so everything else may be cheap; the
     write path is sacred, features live on the read side; every decision names its
     own undoing. An architecture is not a diagram — it is a set of arguments that
     survived. ForwardRef → the parts ahead: ADR-01 is chapter 1.1, ADR-03 is 2.2's
     row lock, ADR-06 is 3.3's outbox, ADR-13/14 are Part 4's media chapters.
  7. **Exercise** (R4), **takeaways**, **CHECKPOINT** — the Part 0 close: the
     reader's full portfolio recapped (positioning, non-goals, personas, journeys,
     SRS slice, drivers, two ADRs), and the door to Part 1 ("the building begins").
- **Rationale**: FR-002..005 beat-for-beat; the three fences are the three quoted
  specimens; budget ~2,300 body + ~700 exercise.
- **Alternatives considered**: surveying all 14 ADRs (a catalog); teaching the ADR
  form on ADR-01 (fine, but ADR-03 additionally shows an SRS open question being
  *closed* by a decision — the requirements→architecture handshake in one specimen).

## R3 — Specimen rendering: the 007 conventions verbatim

- **Decision**: ≤3 fenced blocks (D1+D8 rows; ADR-03 core; ADR-13 core), quoted per
  the established verbatim definition — words exact and greppable in docs/05,
  layout separators free; no pipe tables (no GFM); chapter readable without fences.
- **Rationale**: Settled in feature 007 (incl. the A1 precision); nothing new to
  decide.

## R4 — Exercise: the drivers table and two ADRs

- **Decision**: Exercise 1 — distill 3–6 drivers from the reader's 8–15-row slice
  (the compression is the skill: a driver is a requirement that *shapes structure*,
  not merely exists); each row: driver statement, source requirement IDs from their
  slice, one-line architectural consequence; Relay's D1/D8 as worked examples —
  including permission to have one D8-style driver that is honest context (team
  size, deadline) rather than a requirement. Exercise 2 — write two ADRs from
  scratch against those drivers, using the taught template: status · drivers ·
  decision · trade-offs accepted · ≥2 rejected alternatives *with reasons* ·
  reversal condition; ideally one ADR per ★-derived requirement. Self-checks
  (yes/no): every driver cites requirement IDs from the reader's own slice (or is
  declared as context, D8-style); each ADR names ≥1 driver from the table; each
  rejected alternative records *why* (could a new teammate reconstruct the
  reasoning?); each reversal condition is observable ("revisit when X exceeds Y",
  not "revisit if needed").
- **Rationale**: FR-006's fields; the teammate-reconstruction test is docs/06's
  purpose stated as a check; the observable-trigger rule is "every decision names
  its own undoing" operationalized.

## R5 — Vietnamese translation: the settled conventions

- **Decision**: Established register + glossary; ADR numbers, driver IDs (D1–D8),
  requirement IDs, and status keywords stay English; the three specimen fences stay
  fully English-verbatim with "(Dịch nghĩa: …)" glosses after each (the approved
  feature-007 pattern); manifest vi title verbatim; persona names unchanged.

## R6 — What changes, what is verified

- **Decision**: No component/i18n/styling changes; only the manifest entry plus two
  MDX files. **New verification obligation**: the last-published-chapter footer —
  0.5's footer must render acceptably with a previous card, an empty next slot, and
  the contents link, in both locales and themes. If the empty-next state renders
  poorly, it is reported as an infrastructure finding for a future feature — never
  patched inside this one.
- **Rationale**: Spec edge case; the shell was built with `next && <FooterCard>`
  guards (feature 002), so the expected behavior is a clean single-card grid — but
  0.5 is the first page to exercise it.

## R7 — Verification: the battery + Part 0 completion checks

- **Decision**: The settled battery (canonical word count, box counts en=vi,
  Checkpoint=1, fence parity ≤3 blocks, zero pipe lines, hreflang, `div lang="vi"`)
  with the ID detector extended for this chapter: `ADR-[0-9]+` and `D[1-8]`
  references must exist in docs/05 (plus the standing FR/NFR/EIR/DR/CON/ASM check
  against docs/04). Navigation: 0.4→0.5 live both locales; 0.5 footer shows 0.4
  previous + NO next-chapter href beyond it; **both landings show five linked Part 0
  chapters and zero forthcoming badges within Part 0** (SC-005). Manual: Dong's vi
  read-through; reading-time sanity vs 110; visual check of the last-chapter footer
  in both themes.

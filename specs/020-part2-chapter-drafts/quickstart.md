# Quickstart — validating the Part 2 drafts

> **Post-feature note.** The `drafts/part-2/` directory this guide walked over was
> retired after all seven chapters were published; the per-chapter metadata its
> headers carried now lives in `chapter-notes.md`. The steps below have been
> repointed at the published pages, which have identical bodies (verified: the
> word counts match the old battery rows row for row). Steps that only made
> sense for unpublished drafts — V2's `«TBV»` extraction, V3's "page count
> unchanged" — are marked as historical.

Prerequisites: relay-tutorial checked out at the feature's final state.
No Docker, no platform work — this feature runs nothing but the site's
own toolchain.

## V1 — The seven drafts exist, format-true (C1)

Run the draft battery script over `app/(en)/part-2/chapter-0*/*/page.mdx`
(header-stripped word counts + box/figure formula); compare against
`specs/020-part2-chapter-drafts/draft-battery.txt` — 7 rows, every word
count in 2,000–4,000, every box/figure minimum met, each SkipAhead naming
its own `part2-chN`.

## V2 — Headers and TBVs (C2) — HISTORICAL, drafts retired

For each draft: header present with all six keys; extract the body's
`«TBV: …»` markers and diff against the header's `tbv` list (must be
identical); spot-check `fences`/`amendments` lists against the fences the
body actually shows.

## V3 — Frozen surfaces (C3) — HISTORICAL, the chapters are published now

```bash
git -C relay-platform status --porcelain          # empty (for this feature)
git -C relay-tutorial status --porcelain          # only drafts/part-2/**
cd relay-tutorial && pnpm lint && pnpm build      # green, page count unchanged
```

Serve and diff the sitemap URL set against the pre-feature snapshot
(identical, 34); confirm 2.2–2.8 still render as forthcoming on both
landings; `battery-baseline.txt` byte-unchanged.

## V4 — Source fidelity (C4)

Run the invented-ID detector over the 14 draft files; spot-check quoted
constitution/SAD/requirement passages against the current documents.

## V5 — Arc and marquee moments (C5, C6)

Read (or review-pass) the seven in order, checking: no
mechanism-before-its-chapter; 2.2's failing naive version precedes the row
lock; 2.7's race is a concrete timeline then fixed by the
subscribe-before-backfill buffer; 2.8 exercises 2.2–2.7 and closes Part 2
as the Phase 1 exit; forward references chain into Part 3.

## V6 — Stack fidelity (C7)

Grep-level checks over draft code blocks: no raw `pg`/`drizzle-orm`
imports outside repository-layer files; gateway code imports no framework;
gate commands are the turbo trio; integration tests named `*.itest.ts`;
every new-library mention carries an intended pin.

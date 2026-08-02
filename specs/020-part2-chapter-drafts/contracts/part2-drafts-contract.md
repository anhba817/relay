# Contract — Part 2 Chapter Drafts (feature 020)

Binding checks; each machine- or review-verifiable at implementation's end.

## C1 — Seven format-true drafts

Exactly seven draft units exist at the R1 paths, each in final page shape,
each passing the draft battery (header-stripped): canonical words
2,000–4,000; Why≥2 (source-cited); Trap≥1; SkipAhead=1 naming the intended
`part2-chN` tag; ForwardRef≥1; exactly one closing Checkpoint; Figures 2–4
with sources in the sibling `figures.ts`. Results recorded in
`draft-battery.txt` (7 rows, established formula).

## C2 — Headers complete and truthful

Every draft opens with the R2 header carrying all six keys; the header's
`tbv` list matches the body's `«TBV: …»` markers exactly; `fences` lists
every `title=""` fence path used in the body; `amendments` lists every
diff-fence target used in the body.

## C3 — Frozen surfaces

relay-platform: `git status` clean of any change from this feature.
relay-tutorial: changes confined to `drafts/part-2/**`; manifest,
allowlist, navigation untouched; `pnpm build` green with unchanged page
count; sitemap URL set identical (34). The series `battery-baseline.txt`
is byte-unchanged.

## C4 — Source fidelity

Invented-ID detector clean over all 14 files; quoted passages
(constitution clauses, SAD walk-throughs, requirement text) faithful to
the current documents; anchors match how published chapters already cite
them. Zero unmarked invented outputs (every such value is a `«TBV»`).

## C5 — Arc continuity (SC-006)

Reviewed in sequence: no draft uses a mechanism built by a later draft;
each SkipAhead/Checkpoint state builds strictly on predecessors; 2.8's
script exercises capabilities from every one of 2.2–2.7 and names itself
the SRS Phase 1 exit; forward references chain into Part 3.

## C6 — The part's marquee moments hold

2.2 demonstrates interleaved ordering with a failing naive version before
the row lock; 2.7 stages the SAD §5.2 duplicate/gap race as a concrete
event sequence (timeline: message N+1 published during backfill of ≤N)
and fixes it with the subscribe-before-backfill buffer; 2.8's suite
narrative kills the socket mid-send and asserts exactly-once + order on
reconnect (journey 4, docs/07 §4 Rule 2).

## C7 — Stack fidelity

All draft code is consistent with the 019 state: endpoints are NestJS
(api only), queries go through the Drizzle repository (no raw driver
outside the layer depicted anywhere), the gateway stays frameworkless and
store-free (ADR-05; Redis via fan-out only), gate commands are the turbo
gate, integration tests follow the `*.itest.ts` two-lane convention, and
new-library mentions carry intended pins from registry checks (R6).

# Data Model — Part 2 Chapter Drafts


> **Post-feature note (2026-08-04).** `relay-tutorial/drafts/part-2/` no longer
> exists. All seven chapters were published, at which point the drafts became
> byte-identical duplicates that nothing tracked and nothing checked, and the
> directory was removed. The per-chapter metadata its `DRAFT-HEADER` blocks
> carried now lives in `chapter-notes.md` beside this file. References to the
> draft paths below are left as written: they record what this feature actually
> did, and research R1's reasoning about keeping drafts outside `app/` only
> makes sense in those terms.

A write-ahead content feature's "data" is the draft set, its debt records,
and the arc that binds them.

## Entities

### The draft set

Seven units under `relay-tutorial/drafts/part-2/` (R1), each
`{page.mdx, figures.ts}` in final page shape:

| Draft | Slug | Intended tag | Teaches (docs/07 row) | Failure staged first |
|---|---|---|---|---|
| 2.2 | the-write-path | part2-ch2 | POST message; channel row lock; sequence assignment (ADR-03) | interleaved ordering under concurrency |
| 2.3 | send-it-twice | part2-ch3 | idempotency keys; DR-03 partial unique index | Tuan's duplicate "B2, north ramp" |
| 2.4 | history-that-pages | part2-ch4 | cursor pagination on (channel_id, seq) | offset drift under live inserts |
| 2.5 | the-socket | part2-ch5 | gateway WS termination; JWT verify; connection registry | (structural chapter; TRAP still required) |
| 2.6 | two-servers-one-conversation | part2-ch6 | Redis fan-out (ADR-07); lossy-fabric argument | the sticky-session trap |
| 2.7 | the-tunnel | part2-ch7 | resume: cursors, backfill, subscribe-before-backfill buffer | SAD §5.2 duplicate/gap race (flagship) |
| 2.8 | milestone-the-tuan-test | part2-ch8 | journey-4 integration suite | this chapter IS the Phase 1 exit criterion |

Invariants: format battery per draft (2,000–4,000 words header-stripped;
Why≥2, Trap≥1, Skip=1 naming the intended tag, Fwd≥1, Chk=1, Figures 2–4);
failure-first structure; stack = 019 re-foundation; English only.

### The draft header (R2)

Required keys: `tag`, `fences`, `amendments`, `commands`, `tbv`,
`019-baseline`. Delimited by `DRAFT-HEADER` / `DRAFT-HEADER-END` marker
lines inside one MDX comment. Validation: presence of all keys; `tbv`
list ↔ body `«TBV: …»` markers match exactly (count and content);
stripped by the draft battery and at publish time.

### TBV markers (R3)

`«TBV: description»` — the only permitted form for outputs, counts,
durations, and generated values the drafts cannot know. Zero unmarked
invented outputs (SC-005).

### The part arc (SC-006)

Dependency chain: 2.2 sequences → 2.3 idempotency (protects 2.2's write) →
2.4 pagination (reads 2.2's rows) → 2.5 socket (carries 1.3's frames) →
2.6 fan-out (across 2.5's registry) → 2.7 resume (through 2.5+2.6, reading
via 2.4's cursors) → 2.8 milestone (exercises all). Validation: no
mechanism appears before its chapter; forward references chain through the
part and land in Part 3.

### The frozen surfaces

- relay-platform: zero diffs (FR-006).
- Site: manifest byte-identical, sitemap URL set = 34, same build page
  count, no navigation change; 2.2–2.8 remain "forthcoming" (FR-002).
- Series measurement: `battery-baseline.txt` (019's 20 rows) untouched;
  draft measurements live in this feature's `draft-battery.txt` (R7).

### The publish path (out of scope, recorded)

Per chapter, later: implementation feature builds the platform state →
corrects draft code to reality → resolves TBVs → verifies fences at the
cut tag → strips the header → moves files into `app/(en)/…` → Vietnamese
edition → manifest flip → battery baseline grows. The draft header is the
checklist input for that feature.

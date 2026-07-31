# Quickstart Validation: Part 0 Chapter Visuals

**Feature**: `specs/011-chapter-visuals` · **Date**: 2026-07-30

Contracts in [contracts/chapter-visuals-contract.md](./contracts/chapter-visuals-contract.md).
Commands run in `relay-tutorial/`; chapter paths use the route-group layout
(`app/(en)/part-0/…`, `app/(vi)/vi/part-0/…`).

## Prerequisites

- Node.js 22+, pnpm 10+, a browser (both themes, 375 px viewport); Dong for V4

## V0 — Baselines (BEFORE any edit)

```bash
# Specimen fences (0.4/0.5, both locales) — the byte-diff baseline
mkdir -p /home/dong/work/relay/specs/011-chapter-visuals/specimen-baseline
for f in app/\(en\)/part-0/chapter-0[45]/*/page.mdx app/\(vi\)/vi/part-0/chapter-0[45]/*/page.mdx; do
  out=$(echo "$f" | sed 's|[/()]|_|g')
  awk '/^```/{inF=!inF; print "-----"; next} inF' "$f" > "/home/dong/work/relay/specs/011-chapter-visuals/specimen-baseline/$out.txt"
done
ls /home/dong/work/relay/specs/011-chapter-visuals/specimen-baseline | wc -l   # == 4
```

## V1 — Build gate

```bash
pnpm lint && pnpm build
```

**Expected**: exit 0; no route changes; zero new dependencies in package.json.

## V2 — Scripted battery v2 (contracts C1–C3)

```bash
BASE10=/home/dong/work/relay/specs/011-chapter-visuals
for f in app/\(en\)/part-0/chapter-0[1-5]/*/page.mdx app/\(vi\)/vi/part-0/chapter-0[1-5]/*/page.mdx; do
  words=$(grep -vE '^(import|export)' "$f" | sed 's/<[^>]*>//g' | wc -w)
  figs=$(grep -o '<Figure' "$f" | wc -l)
  fences=$(($(grep -c '^```' "$f")/2))
  # halves distribution: every <Figure line no. bucketed against the midpoint
  mid=$(( $(wc -l < "$f") / 2 ))
  first=$(grep -n '<Figure' "$f" | head -1 | cut -d: -f1); last=$(grep -n '<Figure' "$f" | tail -1 | cut -d: -f1)
  halves=$([ -n "$first" ] && [ "$first" -le "$mid" ] && [ "$last" -gt "$mid" ] && echo OK || echo BAD)
  echo "$f words=$words figs=$figs fences=$fences halves=$halves \
why=$(grep -o '<Why' "$f" | wc -l) skip=$(grep -o '<SkipAhead' "$f" | wc -l) \
fwd=$(grep -o '<ForwardRef' "$f" | wc -l) chk=$(grep -o '<Checkpoint' "$f" | wc -l)"
done
# Expected: figs 3/2/3/2/2 per chapter (en==vi); fences 0/0/0/3/3; halves OK on all;
# en words 2000–4000; box counts identical to the pre-feature record in
# specs/010-seo-optimization/battery-baseline.txt (columns 3–6 per file — compare
# after normalizing its old-style paths: app/ → app/(en)/, app/vi/ → app/(vi)/vi/)

# Captions: every Figure has a non-empty caption (contract C1).
# Figure tags are multi-line, so count caption attributes (in chapters, only
# Figures carry captions).
for f in app/\(en\)/part-0/chapter-0[1-5]/*/page.mdx app/\(vi\)/vi/part-0/chapter-0[1-5]/*/page.mdx; do
  figs=$(grep -o '<Figure' "$f" | wc -l); caps=$(grep -o 'caption="[^"]' "$f" | wc -l)
  [ "$figs" = "$caps" ] || echo "MISSING CAPTION: $f figs=$figs captioned=$caps"
done                                                                    # no output

# Specimen byte-diff (C2)
for f in app/\(en\)/part-0/chapter-0[45]/*/page.mdx app/\(vi\)/vi/part-0/chapter-0[45]/*/page.mdx; do
  out=$(echo "$f" | sed 's|[/()]|_|g')
  awk '/^```/{inF=!inF; print "-----"; next} inF' "$f" | diff "$BASE10/specimen-baseline/$out.txt" - || echo "SPECIMEN DRIFT: $f"
done                                                                    # no output

# No mermaid SOURCE in MDX; every Figure code comes from figures.ts
# (match diagram-type openers, not the plain words — "flowchart" appears in prose)
grep -lE 'flowchart (LR|TB|RL|BT)|xychart-beta|stateDiagram-v2' app/\(en\)/part-0/chapter-0[1-5]/*/page.mdx app/\(vi\)/vi/part-0/chapter-0[1-5]/*/page.mdx | wc -l   # == 0
ls app/\(en\)/part-0/chapter-0[1-5]/*/figures.ts app/\(vi\)/vi/part-0/chapter-0[1-5]/*/figures.ts | wc -l   # == 10

# Invented-ID detector over chapters + figure labels
SAD=/home/dong/work/relay/docs/05-sad.md; SRS=/home/dong/work/relay/docs/04-srs.md
for f in app/\(en\)/part-0/chapter-0[1-5]/*/{page.mdx,figures.ts} app/\(vi\)/vi/part-0/chapter-0[1-5]/*/{page.mdx,figures.ts}; do
  for id in $(grep -oE 'ADR-[0-9]+' "$f" | sort -u); do grep -q "$id" $SAD || echo "INVENTED $id in $f"; done
  for id in $(grep -oE '\bD[1-8]\b' "$f" | sort -u); do grep -q "| $id " $SAD || echo "CHECK DRIVER $id in $f"; done
  for id in $(grep -oE '(FR|EIR|NFR|DR)-[A-Z]+-[0-9]+|(CON|ASM)-[0-9]+' "$f" | sort -u); do grep -q "$id" $SRS || echo "INVENTED $id in $f"; done
done                                                                    # no output

# New baseline (records the figure class — run once everything above passes)
for f in app/\(en\)/part-0/chapter-0[1-5]/*/page.mdx app/\(vi\)/vi/part-0/chapter-0[1-5]/*/page.mdx; do
  echo "$f $(grep -vE '^(import|export)' "$f" | sed 's/<[^>]*>//g' | wc -w) \
$(grep -o '<Why' "$f" | wc -l) $(grep -o '<SkipAhead' "$f" | wc -l) \
$(grep -o '<ForwardRef' "$f" | wc -l) $(grep -o '<Checkpoint' "$f" | wc -l) \
$(grep -c '^```' "$f") $(grep -o '<Figure' "$f" | wc -l)"
done > $BASE10/battery-baseline.txt
```

## V3 — Manual: the figures themselves

1. With `pnpm dev`, open each chapter (en + vi): every figure renders as a
   diagram with its caption; toggle light↔dark on each — legible in both.
2. 375 px viewport on all 10 pages: no horizontal page overflow; figures scroll
   or fit within their frame.
3. Read each figure against its surrounding prose: it visualizes that argument
   (0.3's ★ markers survived the upgrade; 0.5's funnel says 224→8→14→6).
4. SEO spot-check (C4): a chapter page still shows one og:title/og:image and one
   TechArticle block.

## V4 — Manual: Dong's pass

The vi `figures.ts` files and captions — register, glossary, IDs English — plus a
skim of the figures in both locales: do they make the chapters less boring or
just busier?

## V5 — Reading time (FR-009)

Re-estimate each chapter against its manifest `readerMinutes` (figures add
inspection time); correct the manifest where materially off.

## V6 — docs/07 amendment (C4)

```bash
grep -c 'Visual elements' /home/dong/work/relay/docs/07-tutorial-plan.md   # >= 1
```

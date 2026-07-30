# Quickstart Validation: Render the Source Documents

**Feature**: `specs/009-render-source-docs` · **Date**: 2026-07-30

Contracts in [contracts/reference-docs-contract.md](./contracts/reference-docs-contract.md).
Commands run in `relay-tutorial/`; canonical docs at `/home/dong/work/relay/docs/`.

## Prerequisites

- Node.js 22+, pnpm 10+, a browser (both themes, and a 375 px viewport for V3)

## V0 — Battery baseline (BEFORE implementation)

Record the freeze baseline for the ten existing chapter files:

```bash
for f in app/{,vi/}part-0/chapter-0[1-5]/*/page.mdx; do
  echo "$f $(grep -vE '^(import|export)' $f | sed 's/<[^>]*>//g' | wc -w) \
$(grep -o '<Why' $f | wc -l) $(grep -o '<SkipAhead' $f | wc -l) \
$(grep -o '<ForwardRef' $f | wc -l) $(grep -o '<Checkpoint' $f | wc -l) \
$(grep -c '^```' $f)"
done | tee /home/dong/work/relay/specs/009-render-source-docs/battery-baseline.txt
```

(The baseline is committed with the feature's spec artifacts — never `/tmp`, which
would not survive to a later verification session.)

## V1 — Build gate and route table

```bash
pnpm lint && pnpm build
```

**Expected**: exit 0; route table adds exactly 12 routes: `/docs/[slug]` and
`/vi/docs/[slug]` (6 slugs each); all chapter routes unchanged.

## V2 — Scripted battery (contract C4)

```bash
# Drift: green, then provably loud
pnpm check:docs
echo x >> content/docs/01-product-vision.md
pnpm check:docs && echo "FAIL: drift not detected"
git checkout -- content/docs/01-product-vision.md   # restore
```

With `pnpm dev` running:

```bash
SLUGS="product-vision personas journey-map srs sad adr-deep-dives"
for s in $SLUGS; do for p in /docs/$s /vi/docs/$s; do
  echo "$p http=$(curl -s -o /dev/null -w '%{http_code}' localhost:3000$p) \
hreflang=$(curl -s localhost:3000$p | grep -oic hreflang)"
done; done                                          # all 200, hreflang >= 2

# Sentinel content (verbatim presence, one per page — contract C4)
curl -s localhost:3000/docs/srs            | grep -c 'FR-TEN-05'            # >=1
curl -s localhost:3000/docs/sad            | grep -c 'last_sequence'        # >=1
curl -s localhost:3000/docs/adr-deep-dives | grep -c 'Revisit when'         # >=1
curl -s localhost:3000/docs/product-vision | grep -c 'chat infrastructure'  # >=1
curl -s localhost:3000/docs/personas       | grep -c 'Priya'                # >=1
curl -s localhost:3000/docs/journey-map    | grep -c 'Tuan'                 # >=1

# Tables render as tables (not raw pipes)
curl -s localhost:3000/docs/srs | grep -oc '<table'                       # >=1
curl -s localhost:3000/docs/srs | grep -c '^|'                            # == 0

# Chapter links (spot: 0.4 en/vi, 0.5 has BOTH docs)
curl -s localhost:3000/part-0/chapter-04/requirements-you-can-test | grep -oc 'href="/docs/srs"'        # >=1
curl -s localhost:3000/vi/part-0/chapter-04/requirements-you-can-test | grep -oc 'href="/vi/docs/srs"'  # >=1
curl -s localhost:3000/part-0/chapter-05/deciding-out-loud | grep -oE 'href="/docs/(sad|adr-deep-dives)"' | wc -l  # == 2
# (occurrence counts MUST use `grep -o … | wc -l`; `grep -c` counts lines and
#  undercounts when SSR emits both links on one line)

# vi doc page language wrappers
curl -s localhost:3000/vi/docs/sad | grep -oc 'lang="en"'                 # >=1 (article wrap)

# Battery freeze (SC-004): identical to V0 baseline
for f in app/{,vi/}part-0/chapter-0[1-5]/*/page.mdx; do
  echo "$f $(grep -vE '^(import|export)' $f | sed 's/<[^>]*>//g' | wc -w) \
$(grep -o '<Why' $f | wc -l) $(grep -o '<SkipAhead' $f | wc -l) \
$(grep -o '<ForwardRef' $f | wc -l) $(grep -o '<Checkpoint' $f | wc -l) \
$(grep -c '^```' $f)"
done | diff /home/dong/work/relay/specs/009-render-source-docs/battery-baseline.txt -   # no output
```

## V3 — Manual: diagrams, themes, tables, navigation

1. **Diagrams (FR-004)**: open `/docs/sad`; all six mermaid diagrams render as
   diagrams. Toggle light↔dark: legible in both (no dark-on-dark text). Repeat on
   `/vi/docs/sad`.
2. **Tables at phone width**: `/docs/srs` at 375 px — wide requirement tables
   scroll inside their container; the page itself never scrolls horizontally.
3. **Outline (FR-006/SC-005)**: from the top of `/docs/sad`, reach §9 (ADRs) in
   one click via the Contents block; anchors land correctly.
4. **The walk**: chapter 0.5 (en) → header shows two source links → open SAD →
   back to contents → switch language on `/docs/sad` → lands on `/vi/docs/sad`
   with vi chrome, English article, and the English-material note. Repeat the
   chapter→doc hop from a vi chapter.
5. **Fidelity spot-check**: compare the rendered drivers table and ADR-13 section
   against `docs/05-sad.md` — verbatim.

## V4 — Manual: Dong's pass

A skim of each of the six reference pages in both themes — layout quality,
Vietnamese chrome strings, and whether the source-docs line in chapter headers
reads naturally in both languages.

## V5 — Post-change refresh drill (US3, once)

Edit one line in the parent `docs/02-personas.md`, run `scripts/sync-docs.sh`,
confirm the page reflects it, then `git checkout` both copies — proving the
refresh path end to end (SC-006).

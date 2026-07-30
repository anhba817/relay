# Quickstart Validation: Tutorial Chapter 0.3

**Feature**: `specs/006-tutorial-chapter-03` · **Date**: 2026-07-30

Contracts in [contracts/chapter-03-contract.md](./contracts/chapter-03-contract.md).
Commands run in `relay-tutorial/`.

## Prerequisites

- Node.js 22+, pnpm 10+, a browser; Dong for V4

## V1 — Build gate and route table

```bash
pnpm lint && pnpm build
```

**Expected**: exit 0; route table adds exactly the two 0.3 routes.

## V2 — Scripted battery (contract C4)

```bash
EN=app/part-0/chapter-03/journeys-where-products-die/page.mdx
VI=app/vi/part-0/chapter-03/journeys-where-products-die/page.mdx
grep -vE '^(import|export)' $EN | sed 's/<[^>]*>//g' | wc -w        # 2000–4000
for b in Why SkipAhead ForwardRef Checkpoint; do
  echo "$b en=$(grep -o "<$b" $EN | wc -l) vi=$(grep -o "<$b" $VI | wc -l)"
done                                                                 # equal; Checkpoint=1
grep -ci 'takeaway' $EN                                              # >=1
echo "fences en=$(grep -c '^```' $EN) vi=$(grep -c '^```' $VI)"      # equal, <=4 lines (2 blocks)
```

With `pnpm dev` running:

```bash
E3=/part-0/chapter-03/journeys-where-products-die; V3=/vi$E3
E2=/part-0/chapter-02/four-people-who-will-judge-us; V2P=/vi$E2
for r in $E3 $V3; do echo "$r hreflang=$(curl -s localhost:3000$r | grep -oic hreflang) viDecl=$(curl -s localhost:3000$r | grep -oc '<div lang=\"vi\"')"; done
curl -s localhost:3000$E2  | grep -oc "href=\"$E3\""                 # >=1
curl -s localhost:3000$V2P | grep -oc "href=\"$V3\""                 # >=1
curl -s localhost:3000$E3  | grep -oc "href=\"$E2\""                 # >=1
curl -s localhost:3000$E3  | grep -oc 'href="[^"]*chapter-04'        # == 0 (0.4 forthcoming: no link)
curl -s localhost:3000/    | grep -oc "href=\"$E3\""                 # >=1
curl -s localhost:3000/vi  | grep -oc "href=\"$V3\""                 # >=1
```

## V3 — Manual: content fidelity and the reading path

1. Read the English chapter: the stage anatomy is taught on the Stage-2 specimen;
   the three ★s are deep-walked and argued (first message / reconstruct / lose
   signal); the effort ranking and the "adopts vs. deserves adoption" close land.
   Spot-check 5 journey facts against docs/03.
2. Chapter reads correctly skipping both fenced diagrams (spec edge case); diagrams
   render in light + dark.
3. Walk 0.2 → 0.3 → back in both locales; switch languages on 0.3 both directions.
4. Exercise dry-run: two journey maps producible (one single-interaction invisible
   journey), one ★ each with a written reason; self-checks yes/no.

## V4 — Manual: Vietnamese quality (Dong)

Read the vi chapter end to end. **Expected**: established register + glossary; the
manifest's approved title; stage labels in the flow diagrams translated; the ★
arguments and the closing distinction carry the same weight as in English.

## V5 — Reading-time sanity

Estimate against `readerMinutes: 90`; correct the manifest if materially off.

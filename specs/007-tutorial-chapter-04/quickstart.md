# Quickstart Validation: Tutorial Chapter 0.4

**Feature**: `specs/007-tutorial-chapter-04` · **Date**: 2026-07-30

Contracts in [contracts/chapter-04-contract.md](./contracts/chapter-04-contract.md).
Commands run in `relay-tutorial/`; docs path `/home/dong/work/relay/docs/04-srs.md`.

## Prerequisites

- Node.js 22+, pnpm 10+, a browser; Dong for V4

## V1 — Build gate and route table

```bash
pnpm lint && pnpm build
```

**Expected**: exit 0; route table adds exactly the two 0.4 routes.

## V2 — Scripted battery (contract C4)

```bash
EN=app/part-0/chapter-04/requirements-you-can-test/page.mdx
VI=app/vi/part-0/chapter-04/requirements-you-can-test/page.mdx
SRS=/home/dong/work/relay/docs/04-srs.md
grep -vE '^(import|export)' $EN | sed 's/<[^>]*>//g' | wc -w         # 2000–4000
for b in Why SkipAhead ForwardRef Checkpoint; do
  echo "$b en=$(grep -o "<$b" $EN | wc -l) vi=$(grep -o "<$b" $VI | wc -l)"
done                                                                  # equal; Checkpoint=1
echo "fences en=$(grep -c '^```' $EN) vi=$(grep -c '^```' $VI)"       # equal; <=6 lines
grep -c '^|' $EN                                                      # == 0 (no pipe tables — no GFM)
# every requirement/constraint/assumption ID quoted in the chapter exists in the SRS
# (CON/ASM use the short two-segment form, e.g. CON-04 — analysis I1)
for id in $(grep -oE '(FR|EIR|NFR|DR)-[A-Z]+-[0-9]+|(CON|ASM)-[0-9]+' $EN | sort -u); do
  grep -q "$id" $SRS || echo "INVENTED ID: $id"
done                                                                  # no output
```

With `pnpm dev` running:

```bash
E4=/part-0/chapter-04/requirements-you-can-test; V4=/vi$E4
E3=/part-0/chapter-03/journeys-where-products-die; V3P=/vi$E3
for r in $E4 $V4; do echo "$r hreflang=$(curl -s localhost:3000$r | grep -oic hreflang) viDecl=$(curl -s localhost:3000$r | grep -oc '<div lang=\"vi\"')"; done
curl -s localhost:3000$E3  | grep -oc "href=\"$E4\""                  # >=1
curl -s localhost:3000$V3P | grep -oc "href=\"$V4\""                  # >=1
curl -s localhost:3000$E4  | grep -oc "href=\"$E3\""                  # >=1
curl -s localhost:3000$E4  | grep -oc 'href="[^"]*chapter-05'         # == 0
curl -s localhost:3000/    | grep -oc "href=\"$E4\""                  # >=1
curl -s localhost:3000/vi  | grep -oc "href=\"$V4\""                  # >=1
```

## V3 — Manual: content fidelity and the reading path

1. Read the English chapter: the row anatomy lands on FR-MSG-04; T/D/I/A each get a
   real example; both traces (Tuan, Priya) use real IDs; FR-TEN-05 carries the
   Sev-0/every-build argument; the FR-MED beat closes the 0.1→0.3→0.4 thread.
   Spot-check 5 quoted rows verbatim against docs/04.
2. Chapter reads correctly skipping all fenced specimen blocks; fences render in
   light + dark.
3. Walk 0.3 → 0.4 → back in both locales; switch languages on 0.4 both directions.
4. Exercise dry-run: an 8–15-row slice producible; the opinion hunt fails at least
   one draft row; self-checks yes/no.

## V4 — Manual: Vietnamese quality (Dong)

Read the vi chapter end to end. **Expected**: established register + glossary; all
requirement IDs and the `shall` keyword in English with translated surrounding
prose; T/D/I/A codes in English with Vietnamese expansions on first use; the
FR-TEN-05 and FR-MED arguments carry the same weight as in English.

## V5 — Reading-time sanity

Estimate against `readerMinutes: 100`; correct the manifest if materially off.

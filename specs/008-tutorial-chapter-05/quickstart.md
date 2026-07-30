# Quickstart Validation: Tutorial Chapter 0.5

**Feature**: `specs/008-tutorial-chapter-05` · **Date**: 2026-07-30

Contracts in [contracts/chapter-05-contract.md](./contracts/chapter-05-contract.md).
Commands run in `relay-tutorial/`; docs at `/home/dong/work/relay/docs/`.

## Prerequisites

- Node.js 22+, pnpm 10+, a browser; Dong for V4

## V1 — Build gate and route table

```bash
pnpm lint && pnpm build
```

**Expected**: exit 0; route table adds exactly the two 0.5 routes.

## V2 — Scripted battery (contract C4)

```bash
EN=app/part-0/chapter-05/deciding-out-loud/page.mdx
VI=app/vi/part-0/chapter-05/deciding-out-loud/page.mdx
SAD=/home/dong/work/relay/docs/05-sad.md
SRS=/home/dong/work/relay/docs/04-srs.md
grep -vE '^(import|export)' $EN | sed 's/<[^>]*>//g' | wc -w          # 2000–4000
for b in Why SkipAhead ForwardRef Checkpoint; do
  echo "$b en=$(grep -o "<$b" $EN | wc -l) vi=$(grep -o "<$b" $VI | wc -l)"
done                                                                   # equal; Checkpoint=1
echo "fences en=$(grep -c '^```' $EN) vi=$(grep -c '^```' $VI)"        # equal; <=6
grep -c '^|' $EN                                                       # == 0
# extended ID detector: ADRs and drivers against the SAD; requirement IDs against the SRS
for id in $(grep -oE 'ADR-[0-9]+' $EN | sort -u); do grep -q "$id" $SAD || echo "INVENTED: $id"; done
for id in $(grep -oE '\bD[1-8]\b' $EN | sort -u); do grep -q "| $id " $SAD || echo "CHECK DRIVER: $id"; done
for id in $(grep -oE '(FR|EIR|NFR|DR)-[A-Z]+-[0-9]+|(CON|ASM)-[0-9]+' $EN | sort -u); do
  grep -q "$id" $SRS || echo "INVENTED: $id"
done                                                                   # no output
```

With `pnpm dev` running:

```bash
E5=/part-0/chapter-05/deciding-out-loud; V5=/vi$E5
E4=/part-0/chapter-04/requirements-you-can-test; V4P=/vi$E4
for r in $E5 $V5; do echo "$r hreflang=$(curl -s localhost:3000$r | grep -oic hreflang) viDecl=$(curl -s localhost:3000$r | grep -oc '<div lang=\"vi\"')"; done
curl -s localhost:3000$E4  | grep -oc "href=\"$E5\""                   # >=1
curl -s localhost:3000$V4P | grep -oc "href=\"$V5\""                   # >=1
curl -s localhost:3000$E5  | grep -oc "href=\"$E4\""                   # >=1 (previous)
curl -s localhost:3000$E5  | grep -ocE 'href="[^"]*(chapter-0[6-9]|part-[1-8]/chapter)'  # == 0 (no next exists)
# Part 0 completion (SC-005): five links, zero forthcoming inside Part 0
curl -s localhost:3000/    | grep -oc 'href="/part-0/chapter-0'        # == 5
curl -s localhost:3000/vi  | grep -oc 'href="/vi/part-0/chapter-0'     # == 5
```

## V3 — Manual: content fidelity, the last-chapter footer, and the reading path

1. Read the English chapter: the drivers distillation lands (D1 derived, D8 as the
   non-requirement); ADR-03 shows the full anatomy including the "lock is the
   mechanism" argument; the ADR-13 status line ("reverses the v1.0 file-storage
   exclusion") closes the chain explicitly; the three docs/06 themes close the
   argument. Spot-check 5 quoted items against docs/05/06 — sources line-wrap
   mid-phrase (e.g., ADR-03's "the lock / is not a cost…"), so match phrases
   wrap-tolerantly: `tr '\n' ' ' < $SAD | grep -o "<phrase>"`.
2. **The last-chapter footer** (R6): on 0.5 in both locales and both themes — a
   clean previous-card, an empty next slot that does not look broken, and the
   contents link. If it renders poorly, record an infrastructure finding; do not
   patch.
3. Walk 0.4 → 0.5 → back in both locales; switch languages on 0.5 both directions;
   confirm both landings show Part 0 complete (five links, no forthcoming badges).
4. Exercise dry-run: a 3–6-row drivers table and two complete ADRs producible;
   self-checks yes/no.

## V4 — Manual: Vietnamese quality (Dong)

Read the vi chapter end to end — the Part 0 finale deserves the careful pass:
register, glossary, English identifiers and fences with "(Dịch nghĩa:)" glosses, and
whether the closing checkpoint lands as the milestone it is.

## V5 — Reading-time sanity

Estimate against `readerMinutes: 110`; correct the manifest if materially off.

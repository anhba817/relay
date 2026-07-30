# Quickstart Validation: Tutorial Chapter 0.2

**Feature**: `specs/005-tutorial-chapter-02` · **Date**: 2026-07-30

Contracts in [contracts/chapter-02-contract.md](./contracts/chapter-02-contract.md).
Commands run in `relay-tutorial/`.

## Prerequisites

- Node.js 22+, pnpm 10+, a browser; Dong for V4 (Vietnamese read-through)

## V1 — Build gate and route table

```bash
pnpm lint && pnpm build
```

**Expected**: exit 0; route table adds exactly the two 0.2 routes.

## V2 — Scripted battery (contract C4)

```bash
EN=app/part-0/chapter-02/four-people-who-will-judge-us/page.mdx
VI=app/vi/part-0/chapter-02/four-people-who-will-judge-us/page.mdx
grep -vE '^(import|export)' $EN | sed 's/<[^>]*>//g' | wc -w      # 2000–4000
for b in Why SkipAhead ForwardRef Checkpoint; do
  echo "$b en=$(grep -o "<$b" $EN | wc -l) vi=$(grep -o "<$b" $VI | wc -l)"
done                                                               # equal; Checkpoint=1
grep -ci 'takeaway' $EN                                            # >=1
```

With `pnpm dev` running:

```bash
E2=/part-0/chapter-02/four-people-who-will-judge-us; V2=/vi$E2
E1=/part-0/chapter-01/from-app-to-infrastructure;   V1=/vi$E1
for r in $E2 $V2; do echo "$r hreflang=$(curl -s localhost:3000$r | grep -oic hreflang) viDecl=$(curl -s localhost:3000$r | grep -oc '<div lang=\"vi\"')"; done
curl -s localhost:3000$E1 | grep -oc "href=\"$E2\""                # >=1  (0.1 en → 0.2 en)
curl -s localhost:3000$V1 | grep -oc "href=\"$V2\""                # >=1  (0.1 vi → 0.2 vi)
curl -s localhost:3000$E2 | grep -oc "href=\"$E1\""                # >=1  (0.2 → prev 0.1)
curl -s localhost:3000$E2 | grep -oc 'href="[^"]*chapter-03'       # == 0 (0.3 forthcoming: no link; title text may appear)
curl -s localhost:3000/    | grep -oc "href=\"$E2\""               # >=1  (landing)
curl -s localhost:3000/vi  | grep -oc "href=\"$V2\""               # >=1  (vi landing)
```

## V3 — Manual: content fidelity and the reading path

1. Read the English chapter: personas *derived* (not profile cards); influence
   ordering carries reasons; the invisible-user section lands Tuan's constraint
   list; the trade-off section includes the E2E worked example. Spot-check 5 persona
   facts against docs/02.
2. Follow landing → 0.2 in ≤2 steps; walk 0.1 → 0.2 → back-to-contents in both
   locales; switch languages on 0.2 both directions.
3. Exercise dry-run: produce a ≥3-persona set with one invisible persona using only
   the chapter; self-checks all answerable yes/no.

## V4 — Manual: Vietnamese quality (Dong)

Read the vi chapter end to end. **Expected**: the established storytelling register
and glossary (tuyên ngôn định vị, non-goals, đẳng xâm…); persona names unchanged;
nothing reads machine-translated; the influence-ordering and invisibility lessons
carry the same weight as in English.

## V5 — Reading-time sanity

Estimate reading + exercise time against the manifest's `readerMinutes` (75);
correct the manifest if materially off.

# Quickstart Validation: Tutorial Chapter 1.1

**Feature**: `specs/013-chapter-1-1` · **Date**: 2026-07-31

Contracts in [contracts/chapter-1-1-contract.md](./contracts/chapter-1-1-contract.md).
Tutorial commands run in `relay-tutorial/`; scaffold commands in `relay-platform/`.

## Prerequisites

- Node.js 22+, pnpm 10+, a browser; Dong for V4 (vi) and the commit/tag/push

## V1 — The scaffold replay (contract C1, two stages)

**Pre-commit** (the repo's HEAD is empty until Dong's first commit — a git clone
would clone nothing, so replay from a clean copy of the work tree):

```bash
SCRATCH=$(mktemp -d)
rsync -a --exclude node_modules --exclude .git /home/dong/work/relay/relay-platform/ "$SCRATCH/"
cd "$SCRATCH" && pnpm install && pnpm lint && pnpm typecheck && pnpm test    # all exit 0
```

**Post-push** (after Dong commits, tags, and pushes — the true replay):

```bash
git clone --branch part1-ch1 https://github.com/anhba817/relay-platform fresh-replay
cd fresh-replay && pnpm install && pnpm lint && pnpm typecheck && pnpm test  # all exit 0
```

## V2 — Tutorial build gate and battery v3 (contracts C3, C5)

```bash
pnpm lint && pnpm build     # route table gains exactly the two 1.1 routes
```

```bash
# battery v3: prose-only words (fences stripped), boxes incl. Trap, fences, figures
for f in app/\(en\)/part-{0,1}/chapter-0[1-5]/*/page.mdx app/\(vi\)/vi/part-{0,1}/chapter-0[1-5]/*/page.mdx; do
  [ -f "$f" ] || continue
  words=$(awk '/^```/{inF=!inF; next} !inF' "$f" | grep -vE '^(import|export)' | sed 's/<[^>]*>//g' | wc -w)
  echo "$f $words $(grep -o '<Why' "$f" | wc -l) $(grep -o '<SkipAhead' "$f" | wc -l) \
$(grep -o '<ForwardRef' "$f" | wc -l) $(grep -o '<Checkpoint' "$f" | wc -l) \
$(grep -o '<Trap' "$f" | wc -l) $(grep -c '^```' "$f") $(grep -o '<Figure' "$f" | wc -l)"
done | tee /home/dong/work/relay/specs/013-chapter-1-1/battery-baseline.txt
# Expected: 1.1 en words 2000–4000, Trap >= 1, SkipAhead 1, Why >= 2, Checkpoint 1,
# figures 3 (en == vi)

# Part 0 unchanged under v3 (scripted): drop the words column (the only one the
# v3 fence-strip may legitimately shift) and diff the 10 Part 0 rows against the
# 011 baseline — any difference is a content defect, not formula drift
diff <(grep 'part-0' /home/dong/work/relay/specs/011-chapter-visuals/battery-baseline.txt | awk '{$2=""; print}' | sort) \
     <(grep 'part-0' /home/dong/work/relay/specs/013-chapter-1-1/battery-baseline.txt  | awk '{$2=""; print}' | sort)   # no output

# ADR-01 verbatim spot-checks (wrap-tolerant)
python3 - <<'EOF'
d6 = open('/home/dong/work/relay/docs/06-adr-deep-dives.md').read().replace('\n',' ')
for ph in ["the SDK must be TypeScript regardless",
           "compile error instead of a production incident",
           "one `pnpm` workspace, one test runner, one lint config"]:
    print(("FOUND " if ph in d6 else "MISSING ") + ph[:50])
EOF

# ID detector over the new files
SAD=/home/dong/work/relay/docs/05-sad.md; SRS=/home/dong/work/relay/docs/04-srs.md
for f in app/\(en\)/part-1/chapter-01/*/{page.mdx,figures.ts} app/\(vi\)/vi/part-1/chapter-01/*/{page.mdx,figures.ts}; do
  for id in $(grep -oE 'ADR-[0-9]+' "$f" | sort -u); do grep -q "$id" $SAD || echo "INVENTED $id in $f"; done
  for id in $(grep -oE '\bD[1-8]\b' "$f" | sort -u); do grep -q "| $id " $SAD || echo "CHECK DRIVER $id in $f"; done
  for id in $(grep -oE '(FR|EIR|NFR|DR)-[A-Z]+-[0-9]+|(CON|ASM)-[0-9]+' "$f" | sort -u); do grep -q "$id" $SRS || echo "INVENTED $id in $f"; done
done; echo detector done

# en/vi code fences byte-identical (R7)
for loc in en vi; do
  p="app/(en)/part-1/chapter-01/the-monorepo-and-the-toolchain/page.mdx"
  [ $loc = vi ] && p="app/(vi)/vi/part-1/chapter-01/the-monorepo-and-the-toolchain/page.mdx"
  awk '/^```/{inF=!inF; print "-----"; next} inF' "$p" > /tmp/claude-1000/-home-dong-work-relay/6d3def26-112d-46fa-9f1f-da41239c4825/scratchpad/fences-$loc.txt
done
diff /tmp/claude-1000/-home-dong-work-relay/6d3def26-112d-46fa-9f1f-da41239c4825/scratchpad/fences-{en,vi}.txt   # no output
```

## V3 — Chapter↔code no-drift (contract C4 — enumerate at implement time)

The chapter shows 13 fences: 3 command fences (index 0: mkdir/git init; 6:
pnpm add; 12: the four-command gate) and 10 file-content fences, enumerated
here by 0-based fence index → repo path:

```bash
python3 - <<'PYEOF'
import re
src = open('app/(en)/part-1/chapter-01/the-monorepo-and-the-toolchain/page.mdx').read()
fences = re.findall(r'^```[a-z]*\n(.*?)^```$', src, re.M | re.S)
mapping = {1:'package.json', 2:'pnpm-workspace.yaml', 3:'tsconfig.base.json',
           4:'eslint.config.mjs', 5:'vitest.config.ts',
           7:'packages/config/package.json', 8:'packages/config/tsconfig.json',
           9:'packages/config/src/index.ts', 10:'packages/config/src/index.test.ts',
           11:'.gitignore'}
root = '/home/dong/work/relay/relay-platform/'
for idx, path in mapping.items():
    same = fences[idx].strip() == open(root+path).read().strip()
    print(('OK  ' if same else 'DRIFT ') + f'fence{idx} == {path}')
PYEOF
# all OK; command fences replay via V1
```

## V4 — Navigation and SEO (contract C2)

With `pnpm dev` running:

```bash
E=/part-1/chapter-01/the-monorepo-and-the-toolchain
for p in $E /vi$E; do echo "$p $(curl -s -o /dev/null -w '%{http_code}' localhost:3000$p) hreflang=$(curl -s localhost:3000$p | grep -oic hreflang)"; done
curl -s localhost:3000/part-0/chapter-05/deciding-out-loud | grep -oc "href=\"$E\""            # >= 1 (0.5's first next card)
curl -s localhost:3000/vi/part-0/chapter-05/deciding-out-loud | grep -oc "href=\"/vi$E\""      # >= 1
# sidebar: Part 1 mixed — 1 link + 3 forthcoming
curl -s localhost:3000$E | python3 -c "
import sys,re; h=sys.stdin.read()
n=re.search(r'<nav[^>]*data-series-sidebar.*?</nav>', h, re.S).group(0)
print('p1-links:', len(re.findall(r'href=\"/part-1/', n)), 'forthcoming:', n.count('forthcoming'))
"   # p1-links == 1; forthcoming >= 3 within Part 1 (+ empty parts 2–8)
curl -s localhost:3000/sitemap.xml | grep -oE '<loc>' | wc -l                                   # == 26
curl -s localhost:3000$E | grep -o 'property="og:title"' | wc -l                                # == 1
```

## V5 — Manual (browser + Dong)

1. Read the en chapter end to end following the commands in a clean directory —
   the reader path IS the test (SC-005); time it against `readerMinutes: 90`.
2. The three figures in both themes at desktop and 375 px.
3. vi read-through (Dong): register, glossary, code untouched, the four new
   manifest vi titles (1.1–1.4).
4. The decisions-summary opener: a Part 0 reader skims it in under a minute; a
   skipper can genuinely start here.

## V6 — docs/07 amendment + handoff sequence

```bash
grep -c 'code chapter' /home/dong/work/relay/docs/07-tutorial-plan.md   # >= 1 (battery-v3 note)
pnpm check:docs | tail -1                                               # mirrors still green
```

Dong's commit sequence (the handoff's payload):

```bash
cd relay-platform && git add -A && git commit -m "…" && git tag part1-ch1 && git push origin main --tags
cd ../relay-tutorial && git add -A && git commit -m "…" && git push
cd .. && git add -A && git commit -m "…" && git push    # .gitmodules + pins + specs + docs/07
```

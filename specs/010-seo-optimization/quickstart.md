# Quickstart Validation: SEO Optimization

**Feature**: `specs/010-seo-optimization` · **Date**: 2026-07-30

Contracts in [contracts/seo-contract.md](./contracts/seo-contract.md).
Commands run in `relay-tutorial/`.

## Prerequisites

- Node.js 22+, pnpm 10+; a browser for V3; the deployed public URL for V4

## V0 — Battery + URL baseline (BEFORE the restructure)

```bash
cp /home/dong/work/relay/specs/009-render-source-docs/battery-baseline.txt \
   /home/dong/work/relay/specs/010-seo-optimization/battery-baseline.txt
# URL inventory baseline (with dev server running):
for p in / /vi $(grep -oE '"/part-0/[^"]+"' lib/tutorial.ts | tr -d '"') ; do echo $p; done
```

(The 009 baseline is current as of the 0.5 polish; counts are authoritative,
paths get normalized in V2.)

## V1 — Build gate and route table

```bash
pnpm lint && pnpm build
```

**Expected**: exit 0; the same 24 page routes (route groups do not appear in
URLs); plus `/sitemap.xml`, `/robots.txt`, `/opengraph-image` in the output.

## V2 — Scripted battery (contracts C1–C5)

With `pnpm dev` running:

```bash
# C1 — sitemap completeness: exactly 24 <loc>, all 200, robots names the sitemap
curl -s localhost:3000/sitemap.xml | grep -oE '<loc>[^<]+</loc>' | wc -l          # == 24
for u in $(curl -s localhost:3000/sitemap.xml | grep -oE '<loc>[^<]+</loc>' | sed 's/<[^>]*>//g'); do
  p=$(echo "$u" | sed -E 's|https?://[^/]+||'); p=${p:-/}
  code=$(curl -s -o /dev/null -w '%{http_code}' "localhost:3000$p")
  [ "$code" = 200 ] || echo "DEAD: $u -> $code"
done                                                                               # no output (host-only root entries resolve to /)
curl -s localhost:3000/robots.txt | grep -c 'Sitemap:'                             # >= 1

# C2 — html lang matrix (spot the full 24 via loop)
curl -s localhost:3000/ | grep -o '<html[^>]*lang="en"' | wc -l                    # 1
curl -s localhost:3000/vi | grep -o '<html[^>]*lang="vi"' | wc -l                  # 1
curl -s localhost:3000/vi/part-0/chapter-05/deciding-out-loud | grep -o '<html[^>]*lang="vi"' | wc -l  # 1
curl -s localhost:3000/vi/docs/sad | grep -o 'lang="en"' | wc -l                   # >=1 (article wrapper survives)
curl -s localhost:3000/vi | grep -oc '<div lang="vi"'; true                        # == 0 (wrapper retired)

# C3 — OG matrix (occurrence counts use grep -o | wc -l)
E5=/part-0/chapter-05/deciding-out-loud
curl -s localhost:3000$E5 | grep -oE 'property="og:title" content="[^"]*"'         # manifest en title — Building Relay
curl -s localhost:3000/vi$E5 | grep -oE 'property="og:title" content="[^"]*"'      # manifest VI title
curl -s localhost:3000/vi$E5 | grep -o 'property="og:locale" content="vi_VN"' | wc -l   # 1
curl -s localhost:3000$E5 | grep -o 'property="og:type" content="article"' | wc -l      # 1
curl -s localhost:3000/docs/sad | grep -o 'property="og:title"' | wc -l                 # 1
for p in / /vi $E5 /vi$E5 /docs/sad /vi/docs/sad; do
  echo "$p og:image=$(curl -s localhost:3000$p | grep -o 'property="og:image"' | wc -l) twitter:card=$(curl -s localhost:3000$p | grep -o 'name="twitter:card"' | wc -l)"
done                                                                               # og:image == 1 and twitter:card == 1 each

# C4 — JSON-LD validity and counts
for p in $E5 /vi$E5 / /vi /docs/sad; do
  curl -s localhost:3000$p | python3 -c "
import sys, re, json
html = sys.stdin.read()
blocks = re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', html, re.S)
types = [json.loads(b).get('@type') for b in blocks]
print('$p', types)
"
done
# chapters: ['TechArticle']; landings: ['WebSite']; docs: []

# C5 — battery freeze with normalized paths
for f in app/\(en\)/part-0/chapter-0[1-5]/*/page.mdx app/\(vi\)/vi/part-0/chapter-0[1-5]/*/page.mdx; do
  echo "$f $(grep -vE '^(import|export)' "$f" | sed 's/<[^>]*>//g' | wc -w) \
$(grep -o '<Why' "$f" | wc -l) $(grep -o '<SkipAhead' "$f" | wc -l) \
$(grep -o '<ForwardRef' "$f" | wc -l) $(grep -o '<Checkpoint' "$f" | wc -l) \
$(grep -c '^```' "$f")"
done | sed 's|app/(en)/|app/|; s|app/(vi)/vi/|app/vi/|' | sort \
  | diff <(sort /home/dong/work/relay/specs/010-seo-optimization/battery-baseline.txt) -   # no output

# canonical/hreflang regression (counts as in prior features)
for p in / /vi $E5 /vi$E5 /docs/sad /vi/docs/sad; do
  echo "$p hreflang=$(curl -s localhost:3000$p | grep -oic hreflang) canonical=$(curl -s localhost:3000$p | grep -o 'rel="canonical"' | wc -l)"
done                                                                               # hreflang >= 2, canonical == 1
```

## V3 — Manual (local)

1. Open `http://localhost:3000/opengraph-image` — a 1200×630 branded card, series
   title legible, Violet Bloom palette.
2. View source of an en and a vi chapter: OG/Twitter tags present in `<head>`
   (hoisted), no duplicate `og:image`, JSON-LD block well-formed.
3. Click through several pages — zero visible content change anywhere.

## V4 — Deploy-time (Dong, against the public URL)

1. Link-preview validators (e.g. opengraph.xyz, the platforms' sharing debuggers)
   on: en landing, vi landing, one en chapter, one vi chapter — correct
   title/description/image/language per page (SC-004).
2. Google Rich Results test on two chapter pages — zero errors (SC-005).
3. Lighthouse SEO category on landing/chapter/doc in both locales — 100 (SC-006).
   (Requires Chrome; run against the deployment, or locally via a Lighthouse
   container if convenient.)
4. After the next deploy: confirm `https://<site>/sitemap.xml` serves and submit
   to Search Console if desired (out of scope, optional).

## V5 — Publish-flow proof (SC-001, once)

No forthcoming chapter exists to publish (Part 0 is complete; parts 1–8 are
empty), so run the proof in reverse: temporarily flip chapter 0.5 to
`status: "forthcoming"` in `lib/tutorial.ts`, rebuild, confirm the sitemap
shrinks by exactly its 2 URLs (22 `<loc>`) and the landings show the forthcoming
badge — zero other edits — then revert the flip and confirm 24 again.

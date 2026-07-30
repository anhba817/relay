# Contract: SEO Surfaces — Discovery, Previews, Structured Data

**Feature**: `specs/010-seo-optimization` · **Date**: 2026-07-30

## C1 — Discovery surfaces

| Surface | Guarantee |
|---|---|
| `/sitemap.xml` | Exactly the indexable pages (24 today: `/`, `/vi`, 5+5 chapters, 6+6 docs); absolute URLs from the configured site address; language alternates per entry; a manifest publish changes it with zero manual edits |
| `/robots.txt` | Allows all public pages; names the sitemap URL |
| Every page | Serves 200 and appears in the sitemap exactly once; nothing unpublished or non-existent appears |

## C2 — Language and canonical matrix (regression + fix)

| Check | Bound |
|---|---|
| `<html lang>` | `en` on all 12 English pages; `vi` on all 12 Vietnamese pages |
| Reference-doc bodies | vi doc pages keep the `lang="en"` article wrapper; the retired `div lang="vi"` wrapper is absent everywhere |
| Canonicals | 24/24 self-canonical (vi never canonicalizes to en, nor vice versa) |
| hreflang | Bidirectional en/vi alternates intact on 24/24 (same counts as pre-feature) |
| URLs | All 24 route URLs byte-identical to pre-feature (route groups are invisible) |

## C3 — Social preview matrix

| Check | Bound |
|---|---|
| `og:title` | Exactly one per page (24/24), equal to the page's own `<title>` — the metadata API's title fallback fills it once a layout-level `openGraph` exists (implementation-verified); the shell emits NO title tags |
| `og:description` | Exactly one per page (24/24), the page's own meta description; the shell emits NO description tags |
| `og:url` | Absolute, equals the page's canonical |
| `og:locale` | `en_US` on English pages, `vi_VN` on Vietnamese pages |
| `og:type` | `article` on chapter pages; `website` elsewhere |
| `og:image` / `twitter:image` | Exactly one per page, absolute, 1200×630, served by the site (the file convention); zero duplicate image tags |
| `twitter:card` | `summary_large_image` on 24/24 |

## C4 — Structured data

| Check | Bound |
|---|---|
| Chapter pages | Exactly one `TechArticle` JSON-LD block each (10 total): headline = locale title, description, inLanguage, url, isPartOf "Building Relay"; parses as valid JSON |
| Landings | One `WebSite` block each naming both language URLs |
| Doc pages | Zero JSON-LD blocks |
| Validity | Every block parses; deploy-time rich-results validation shows zero errors |

## C5 — Freeze and non-regression

| Check | Bound |
|---|---|
| Chapter files | Pure renames — content byte-identical; battery counts equal after path normalization (`app/(en)/` → `app/`, `app/(vi)/vi/` → `app/vi/`) |
| Visible content | No rendered visible change on any page (head/JSON-LD only; the retired wrapper had no visual effect) |
| 009 surfaces | Doc mirrors, drift check, outline anchors, referenced-by links all unchanged |
| Build gate | `pnpm lint && pnpm build` exit 0; no new dependencies in package.json |

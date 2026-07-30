# Data Model: SEO Optimization for the Existing Pages

**Feature**: `specs/010-seo-optimization` · **Date**: 2026-07-30

No new persistent entities — every SEO surface is a projection of the two existing
sources of truth (series manifest, doc registry) plus deployment configuration.

## E1 — SEO helper module (lib/seo.ts)

| Element | Rule | Source |
|---|---|---|
| `siteUrl()` | Absolute site origin from `NEXT_PUBLIC_SITE_URL` (same source as metadataBase); every absolute URL in the feature flows through it | FR-008 |
| `ogLocale(locale)` | `en` → `en_US`, `vi` → `vi_VN` | FR-005 |
| `chapterArticleJsonLd(chapter, locale)` | TechArticle: headline (locale title), description (locale reader-produces), inLanguage, url (absolute locale path), position (chapter id), isPartOf WebSite "Building Relay" | FR-007, R5 |
| `websiteJsonLd(locale)` | WebSite: name, url, inLanguage, both language URLs | FR-007, R5 |

## E2 — Route-group restructure (per-locale root layouts)

| Element | Rule | Source |
|---|---|---|
| `app/(en)/layout.tsx` | Root layout, `<html lang="en">`, renders shared `RootShell`; carries shared metadata (metadataBase, title default, `twitter.card`, `openGraph.siteName`) | FR-003, R1 |
| `app/(vi)/layout.tsx` | Root layout, `<html lang="vi">`, same `RootShell`; vi default description | FR-003, R1 |
| `components/root-shell.tsx` | Fonts, ThemeProvider, SiteHeader, globals.css — instantiated once, used by both root layouts | R1 |
| Moves | `app/page.tsx`, `app/part-0/`, `app/docs/` → `app/(en)/…`; `app/vi/` → `app/(vi)/vi/…`; chapter `page.mdx` files byte-identical (pure renames) | FR-009, R1 |
| Retired | `app/vi/layout.tsx`'s `<div lang="vi">` wrapper (html element now authoritative); doc pages' `lang="en"` article wrapper KEPT | FR-003 edge case |
| Invariants | All 24 URLs unchanged; `app/icon.jpg` still resolves (verify; fallback: copy into both groups) | R1 |

## E3 — Discovery surfaces

| Element | Rule | Source |
|---|---|---|
| `app/sitemap.ts` | Entries: `/` and `/vi`; each published chapter's path (+ `/vi` counterpart when `translatedIn` includes "vi"); each doc-registry slug ×2. 24 URLs today. Each entry: absolute url, `alternates.languages` (en/vi pair). Nothing else — no 404, no unpublished chapters, no parts 1–8 | FR-001, SC-001 |
| `app/robots.ts` | Allow all user agents on `/`; `sitemap: <siteUrl>/sitemap.xml` | FR-002 |

## E4 — Per-page social preview (two mechanisms)

| Page class | Mechanism | Fields |
|---|---|---|
| Landings (2) + doc routes (12 pages via 2 files) | `metadata`/`generateMetadata` `openGraph` | title, description (the page's own), url (canonical), `type: "website"`, locale via `ogLocale` |
| Chapters (10 pages, battery-frozen) | `ChapterHeader` renders hoisted `<meta>` tags (React 19 document metadata); titles/descriptions come from the metadata API's page-own fallback (implementation finding, research R3) | `og:url`, `og:type` article, `og:locale` — nothing else, or the API's tags duplicate |
| Site-wide (both root layouts) | metadata API | `twitter.card: summary_large_image`, `openGraph.siteName: "Building Relay"` |
| Image | The `/og` route (E5) declared once in `sharedMetadata`/`baseOpenGraph` — the shell never emits image tags | R3/R4 |

## E5 — Series preview image (app/(en)/og/route.tsx, URL /og)

| Property | Rule | Source |
|---|---|---|
| Generation | `ImageResponse` (next/og, built-in), rendered at build | FR-006, R4 |
| Dimensions / type | 1200×630, PNG; exported `size`, `contentType`, `alt` | FR-006 |
| Content | "Building Relay" + series tagline on the Violet Bloom palette (static hex values — the image cannot read CSS tokens) | R4 |
| Effect | Declared as `openGraph.images`/absolutized by metadataBase in `sharedMetadata` (root layouts) and `baseOpenGraph` (pages with their own og) — exactly one image tag per page; the file convention was abandoned (it does not attach without a top-level root layout, and per-group copies would collide on one URL) | FR-005/006 |

## E6 — Structured data placement

| Page | Record | Emitted from |
|---|---|---|
| 10 chapter pages | `TechArticle` (E1 builder) | `ChapterHeader` `<script type="application/ld+json">` |
| 2 landings | `WebSite` (E1 builder) | landing `page.tsx` files (editable) |
| 12 doc pages | none | spec US3-AS3 |

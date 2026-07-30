# Feature Specification: SEO Optimization for the Existing Pages

**Feature Branch**: `010-seo-optimization`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "SEO optimization for the existing pages"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search engines can discover, crawl, and index every page (Priority: P1)

As a developer searching for chat-infrastructure tutorial material (or for Relay's
documents by name), I find the tutorial's pages in search results — because every
page of the site (2 landings, 10 chapter pages, 12 reference-document pages) is
discoverable through a machine-readable site map, crawlable per an explicit crawler
policy, correctly language-labeled, and free of duplicate-content ambiguity between
its English and Vietnamese versions.

**Why this priority**: Indexability is the foundation — social previews and rich
results are worthless for pages search engines never find. Today the site has no
site map and no crawler policy, and Vietnamese pages are declared to be in English
at the page level, all of which suppress discovery and ranking.

**Independent Test**: A crawler simulation starting from the site map reaches 100%
of the site's pages; each page declares exactly one canonical address, a correct
language, and a bidirectional link to its counterpart language version.

**Acceptance Scenarios**:

1. **Given** the deployed site, **When** a crawler requests the standard site-map
   location, **Then** it receives a machine-readable list of all indexable pages in
   both languages (24 today), with no missing, extra, or dead entries.
2. **Given** the standard crawler-policy location, **When** requested, **Then** it
   permits crawling of all public pages and points to the site map.
3. **Given** any Vietnamese page, **When** its markup is inspected, **Then** the
   page's declared language is Vietnamese (not English), while embedded
   English-only material (the reference documents) remains marked as English.
4. **Given** any page in either language, **Then** it declares itself as its own
   canonical address (Vietnamese pages never canonicalize to English or vice
   versa) and the existing bidirectional language alternates are preserved.
5. **Given** a future chapter flips to published in the series manifest, **Then**
   the site map includes its pages with no manual edit — publishing stays
   manifest-only.

---

### User Story 2 - Shared links unfurl into rich previews (Priority: P2)

As a reader sharing a chapter (or the series landing) on a chat app or social
platform, the link unfurls into a proper preview — the page's title, its
description, and a recognizable series image — in the language of the page I
shared, so the link looks credible and gets clicked.

**Why this priority**: A tutorial series spreads by being shared; a bare URL with
no preview is a measurable click-through penalty. Today no page declares any
social-preview metadata.

**Independent Test**: Passing any page URL through the major platforms' link-preview
validators produces a card with the correct title, description, image, and language
for that specific page — no fallbacks to a generic or wrong-language card.

**Acceptance Scenarios**:

1. **Given** any page, **When** its social-preview metadata is inspected, **Then**
   the title and description match that page's own (already-unique) metadata, the
   series image is referenced with an absolute address, and the declared preview
   language matches the page's language.
2. **Given** a chapter page shared in Vietnamese, **Then** the preview shows the
   Vietnamese title and description — not the English counterpart's.
3. **Given** the series image, **Then** it is a single branded image at the
   platforms' recommended preview dimensions, served from the site itself.

---

### User Story 3 - Chapters qualify for rich search results (Priority: P3)

As a searcher, when a chapter page appears in results, the search engine
understands it as an article within a named series — author, language, position,
and description — because each chapter page carries valid structured data, giving
it eligibility for richer result presentation.

**Why this priority**: Valuable but layered on top of US1/US2; structured data
without indexability is moot.

**Independent Test**: Every chapter page's structured data passes the standard
schema validators with zero errors; the site's landing declares the site-level
entity; validators show article eligibility.

**Acceptance Scenarios**:

1. **Given** any chapter page, **When** validated, **Then** its structured data
   describes an article — headline, description, language, series membership, and
   the artifact the reader produces — with zero validator errors.
2. **Given** the landing pages, **Then** site-level structured data names the site
   and its two language versions.
3. **Given** a reference-document page, **Then** its structured data (if any) never
   claims authorship or dates that contradict the documents themselves.

---

### Edge Cases

- **The bilingual pair is not duplicate content**: every en/vi pair must resolve to
  two self-canonical pages linked by language alternates — a wrong canonical would
  de-index one language entirely.
- **Page-level language vs embedded language**: Vietnamese reference-document pages
  are Vietnamese chrome around English documents; the page declares Vietnamese
  while the document body keeps its English marking (already present). The fix for
  the page-level language must not flip the reference documents to "Vietnamese".
- **Chapter prose is battery-verified**: all SEO additions are metadata/chrome —
  zero changes to any chapter's `page.mdx` prose; the format battery stays frozen.
- **The site's public address is configuration**: absolute URLs (site map, canonical,
  preview image) must derive from the deployment's configured site address, never a
  hardcoded domain; local/preview deployments must not emit production URLs.
- **Unknown routes**: the site map lists only real pages; the 404 surface is never
  listed.
- **Future parts**: parts 1–8 hold no published chapters; nothing about them may
  appear in the site map until the manifest publishes them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The site MUST expose a machine-readable site map at the standard
  location listing every indexable page in both languages (currently 24: 2
  landings, 10 chapters, 12 reference documents), derived automatically from the
  series manifest and document registry so future publishes appear without manual
  edits.
- **FR-002**: The site MUST expose a crawler policy at the standard location that
  permits crawling of all public pages and references the site map.
- **FR-003**: Every page MUST declare its correct language at the page level:
  English pages as English, Vietnamese pages as Vietnamese — while the
  English-only reference-document bodies keep their existing English marking
  inside Vietnamese pages.
- **FR-004**: Every page MUST remain self-canonical with bidirectional language
  alternates (the existing behavior, elevated to a regression requirement — the
  feature must prove it still holds on all 24 pages afterward).
- **FR-005**: Every page MUST declare social-preview metadata: the page's own
  title and description, the page's language, its canonical address, and a shared
  series preview image referenced by absolute address.
- **FR-006**: The site MUST provide one branded series preview image at the
  platforms' recommended dimensions, served by the site itself.
- **FR-007**: Every chapter page MUST carry valid structured data describing it as
  an article in the named series (headline, description, language, series name,
  position, and the reader-produces artifact where expressible); the landings MUST
  carry site-level structured data naming the site and its two language versions.
  All structured data MUST validate with zero errors.
- **FR-008**: All absolute URLs emitted by the feature MUST derive from the
  deployment's configured site address; no hardcoded domain anywhere.
- **FR-009**: The feature MUST NOT alter any chapter's teaching prose or verified
  format properties (word/box/fence counts identical for all ten chapter files),
  and MUST NOT change any page's visible content — metadata and machine-readable
  surfaces only.

### Key Entities

- **Indexable page**: One of the site's 24 public pages (landing, chapter,
  reference document — ×2 languages); has a canonical address, language, title,
  description.
- **Site map**: The machine-readable enumeration of all indexable pages, sourced
  from the same manifest/registry that drives navigation.
- **Social-preview card**: Per-page title/description/image/language block consumed
  by link-unfurling platforms.
- **Structured-data record**: Per-page machine-readable description (article for
  chapters, site-level for landings) consumed by search engines.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The site map lists exactly the site's indexable pages — 24/24 today,
  zero dead or extra entries — and a manifest publish adds new pages to it with
  zero manual edits.
- **SC-002**: 24/24 pages declare the correct page-level language; the two
  Vietnamese reference-document checks (Vietnamese page, English body) both hold.
- **SC-003**: 24/24 pages are self-canonical with intact bidirectional language
  alternates (regression: same counts as before the feature).
- **SC-004**: 24/24 pages produce a complete social-preview card (title,
  description, absolute image, correct language) in platform validators, with
  language-correct cards on all 11 Vietnamese pages.
- **SC-005**: 10/10 chapter pages and both landings pass structured-data validation
  with zero errors.
- **SC-006**: An industry-standard automated page audit scores the site's SEO
  category at 100 on each page type (landing, chapter, reference document) in both
  languages.
- **SC-007**: The ten chapter files' battery measurements are identical before and
  after the feature, and no page's rendered visible content changes.

## Assumptions

- **Scope is structural/technical SEO** — discoverability, metadata, previews,
  structured data. Content-side SEO (keyword rewriting, headings tuning) is out of
  scope: the chapters' prose is the product and is battery-frozen.
- **The reference-document pages are indexable** and self-canonical. They mirror
  files also visible on a code-hosting site, which is acceptable; if de-indexing
  them is ever preferred, that is a one-line policy change later.
- **One static branded preview image** serves all pages (no per-chapter image
  generation) — scope kept deliberately boring; per-page images are a clean future
  increment.
- **The deployed site address is provided by configuration** (already the case for
  the existing metadata base); validators that require a public URL run against the
  deployed site, while everything else verifies locally.
- **No search-console registration, analytics, or ad platform work** is in scope —
  this feature ends at what the site itself serves.
- Commits/pushes are Dong's; nothing is committed by the implementation itself.

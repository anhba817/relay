# Feature Specification: Internationalization with Vietnamese Chapter 0.1

**Feature Branch**: `004-i18n-vietnamese`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "Add internationalization with a language switcher and implement chapter 0.1 in Vietnamese"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Switch the site language (Priority: P1)

As a Vietnamese-speaking reader, I can switch the tutorial site from English to
Vietnamese with a visible control available on every page — and everything the site
itself says (landing page, header, chapter navigation, the tutorial box labels)
renders in Vietnamese — so the reading experience is native, not half-translated.

**Why this priority**: The language infrastructure and switcher are the foundation;
translated content (US2) is unreachable without them.

**Independent Test**: On any page, use the language switcher to select Vietnamese —
the site chrome (landing headings, part/chapter labels, "forthcoming" badges, chapter
header/footer text, box labels) renders in Vietnamese; switching back restores
English. The choice persists across pages and browser sessions.

**Acceptance Scenarios**:

1. **Given** any page, **When** the reader looks for a language control, **Then** one
   is visible without scrolling, alongside the existing theme control, offering
   English and Vietnamese (Tiếng Việt).
2. **Given** the landing page in Vietnamese, **When** the reader scans it, **Then**
   the series pitch, part titles, chapter list labels, and "forthcoming" markers are
   in Vietnamese — no mixed-language chrome.
3. **Given** a language choice, **When** the reader navigates between pages or
   returns in a later session, **Then** the choice is retained.
4. **Given** a first-time visitor, **When** they load the site, **Then** it renders
   in English (the series' original language) regardless of browser locale, with the
   switcher discoverable.
5. **Given** the switcher, **When** operated by keyboard, **Then** it is fully
   usable and its active language is discernible.

---

### User Story 2 - Read chapter 0.1 in Vietnamese (Priority: P2)

As a Vietnamese-speaking reader, I can read chapter 0.1 — "From app to
infrastructure" — entirely in Vietnamese at its own Vietnamese address, as a faithful
translation of the English chapter (same argument, same boxes, same exercise, same
checkpoint), so I can complete Part 0's first step without English fluency.

**Why this priority**: This is the content the user asked for; it depends on US1's
infrastructure.

**Independent Test**: Open the Vietnamese chapter address — the full chapter (prose,
WHY/SKIP AHEAD/FORWARD REF/CHECKPOINT boxes, exercise with self-checks, takeaways)
reads in natural Vietnamese; the language switcher on either language's chapter page
lands on the other language's version of the same chapter.

**Acceptance Scenarios**:

1. **Given** the Vietnamese chapter page, **When** read end to end, **Then** every
   element of the English chapter is present in Vietnamese: the derivation sections,
   at least the same number of each box type, the exercise with the positioning
   template and self-checks, the takeaways, and the closing checkpoint.
2. **Given** the English chapter page, **When** the reader switches to Vietnamese,
   **Then** they land on the Vietnamese version of the same chapter (and vice
   versa) — not on the landing page.
3. **Given** the translation, **When** reviewed by a Vietnamese-speaking reader,
   **Then** established technical terms remain in their internationally used English
   form where Vietnamese practice does so (e.g. WebSocket, API), with Vietnamese
   phrasing carrying the argument.
4. **Given** the Relay positioning statement (the chapter's worked example), **When**
   rendered in Vietnamese, **Then** the translation preserves the template's
   for/who/that/unlike structure so the exercise still teaches the same skill.

---

### User Story 3 - Coherent bilingual structure (Priority: P3)

As a reader of either language, addresses, navigation, and untranslated material
behave coherently: each language has its own stable addresses, the English addresses
that exist today keep working unchanged, and content that exists only in English is
clearly indicated rather than silently mixed in.

**Why this priority**: Structural coherence protects existing links and future
chapters, but matters only once US1/US2 exist.

**Independent Test**: All pre-existing English URLs resolve unchanged; Vietnamese
pages live under a recognizable Vietnamese address space; a Vietnamese reader
encountering not-yet-translated future content sees an explicit indication.

**Acceptance Scenarios**:

1. **Given** every English URL that existed before this feature (landing, chapter
   0.1), **When** visited, **Then** it renders exactly as before — English, same
   address, no redirect to a language-picker page.
2. **Given** the Vietnamese chapter, **When** its address is inspected, **Then** it
   is distinguishable as Vietnamese and structurally parallel to the English address
   (same part/chapter identity), so the language switcher can map between them.
3. **Given** forthcoming chapters (0.2–0.5) on the Vietnamese landing page, **Then**
   their titles/labels display in Vietnamese with the forthcoming indication — no
   broken links to untranslated pages.
4. **Given** each page, **Then** it declares its language such that browsers,
   translation tools, and search engines identify English and Vietnamese pages
   correctly, including the relationship between language counterparts.

---

### Edge Cases

- What happens when a reader lands directly on a Vietnamese URL (shared link) with no
  stored preference? The page renders in Vietnamese (the address wins); their
  stored preference is not silently overwritten by merely visiting.
- What happens when a future chapter exists in English but not Vietnamese? The
  Vietnamese site lists it with a clear "available in English only" (or forthcoming)
  indication rather than a broken link or silent English page under a Vietnamese
  address.
- What happens to the theme switcher and favicon on Vietnamese pages? All feature-003
  behavior is language-independent and works identically.
- What happens with scripting disabled? Same guarantee as the theme feature: pages
  render usable in the address's language; only the persistence conveniences degrade.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The site MUST support two languages — English (default and original)
  and Vietnamese — with all reader-facing site chrome (landing content, header,
  chapter shell labels, box labels, forthcoming badges) available in both.
- **FR-002**: A language switcher MUST be visible without scrolling on every page,
  adjacent to the existing theme control, offering the two languages with the active
  one discernible; it MUST be keyboard-operable and convey state to assistive
  technology.
- **FR-003**: Switching language on a page that has a counterpart in the target
  language MUST navigate to that counterpart (same logical page), not to a generic
  home page.
- **FR-004**: The reader's language choice MUST persist across navigations and
  browser sessions on the same device. First-time visitors get English; visiting a
  Vietnamese-addressed link renders Vietnamese without erasing a stored preference.
- **FR-005**: All English addresses that exist before this feature MUST continue to
  resolve unchanged (the canonical English URL scheme from feature 002 is preserved
  verbatim). Vietnamese pages MUST live at addresses that are recognizably
  Vietnamese and structurally parallel to their English counterparts.
- **FR-006**: Chapter 0.1 MUST be available in Vietnamese as a faithful, complete
  translation of the English chapter: same section arc, at least the same count of
  each tutorial box type, the exercise (positioning template, worked example,
  non-goals, yes/no self-checks), takeaways, and exactly one closing checkpoint.
- **FR-007**: The Vietnamese translation MUST keep internationally established
  technical terms in English where Vietnamese technical writing does so, and MUST
  preserve the positioning template's structural slots in the worked example.
- **FR-008**: Each page MUST declare its language, and language counterparts MUST be
  mutually discoverable by user agents (correct language metadata and counterpart
  relationships), so search engines and browser tooling treat the two languages
  correctly.
- **FR-009**: Vietnamese pages MUST NOT silently serve English body content under a
  Vietnamese address; where a translation does not exist (future chapters), the
  Vietnamese experience marks it explicitly.

### Key Entities

- **Locale**: One of `en` (default, original) or `vi`; determines chrome strings,
  page language declaration, and address space.
- **Localized string set**: The site-chrome vocabulary (landing, header, shell, box
  labels, badges) in each locale — one set per locale, no per-page copies.
- **Chapter translation**: A locale-specific rendition of a chapter's content sharing
  the chapter's identity (part, number, boxes, exercise structure) — for this
  feature: chapter 0.1 in `vi`.
- **Language preference**: The reader's chosen locale, stored on their device;
  absent for first-time visitors (treated as English).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can switch languages from any page in at most 2 interactions,
  and 100% of site-chrome strings on the landing and chapter pages render in the
  selected language (zero mixed-language chrome).
- **SC-002**: The Vietnamese chapter 0.1 contains 100% of the English chapter's
  structural elements (sections, box instances by type, exercise components,
  takeaways, checkpoint) — verified by element-count comparison.
- **SC-003**: 100% of pre-existing English URLs resolve with unchanged content and
  addresses after the feature ships.
- **SC-004**: Switching language from either chapter 0.1 page lands on the
  counterpart chapter page (not the landing) in 100% of attempts, in both directions.
- **SC-005**: A stored language preference survives navigation and a full browser
  restart; a shared Vietnamese link renders Vietnamese on first visit with no stored
  preference.
- **SC-006**: Both language versions of every page declare their language and their
  counterpart relationship in a form detectable by automated inspection of the
  rendered pages.

## Assumptions

- Exactly two locales are in scope: English (`en`, default and source of truth) and
  Vietnamese (`vi`). No third language, no per-locale theming.
- English keeps its current unprefixed addresses (preserving feature 002's
  user-clarified canonical URL scheme and all existing links); Vietnamese lives under
  a locale-distinguished address space with parallel structure. The exact address
  convention is a planning decision within this constraint.
- The Vietnamese translation of chapter 0.1 is authored in this feature as a faithful
  translation of the English chapter (the English chapter remains the single source
  of the argument; docs/01 remains the single source of facts). Dong — a
  Vietnamese speaker — is the reviewing authority on translation quality.
- Site-chrome translation covers reader-facing strings only; developer-facing
  artifacts (README, specs, code comments) stay English.
- Default for first-time visitors is English by explicit choice (the series' original
  language) rather than browser-locale detection — avoiding surprise redirects and
  keeping existing URLs stable. The switcher is the discovery mechanism.
- The scope is the site chrome + chapter 0.1 translation. Translating future chapters
  is per-chapter work belonging to those chapters' features; this feature must only
  leave the structure ready for them.
- This feature touches only the relay-tutorial application; parent repo gains spec
  artifacts and the eventual submodule pin.

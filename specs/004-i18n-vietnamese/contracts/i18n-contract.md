# Contract: Bilingual Site Structure

**Feature**: `specs/004-i18n-vietnamese` · **Date**: 2026-07-29

## C1 — Address space

| Guarantee | Detail |
|---|---|
| English URLs frozen | `/`, `/part-0/chapter-01/from-app-to-infrastructure` (and every future en route) resolve with unchanged addresses, unchanged body content, `lang="en"` context — the only permitted delta from this feature is additive head metadata (hreflang) |
| Vietnamese mirror | Every translated page lives at `/vi` + the English path, same slug; counterpart mapping is pure prefix add/strip |
| No redirects | No route auto-redirects based on cookie, browser locale, or anything else |

## C2 — Switcher (`components/language-switcher.tsx`)

| Guarantee | Detail |
|---|---|
| Placement | Site header, adjacent to the theme toggle, every page, visible without scrolling |
| Behavior | Renders links to `counterpartPath(currentPath)` — switching from a chapter lands on that chapter's counterpart (SC-004); sets the `locale` cookie on activation. If the counterpart page does not exist (future en-only chapter), the switcher links to the target locale's landing — never a dead mirror path (FR-009) |
| State | Active locale discernible; keyboard-operable; accessible labels ("Switch to Tiếng Việt" / "Chuyển sang English") |

## C3 — Localization plumbing

| Guarantee | Detail |
|---|---|
| `lib/i18n.ts` | `Locale`, `dictionaries` (type-identical keys per locale), `t(locale)`, `localeFromPath(path)`, `counterpartPath(path)` |
| Components | `Landing`, `ChapterHeader`, `ChapterFooter`, and all six boxes accept `locale` prop defaulting `"en"` — every existing English call site compiles and renders unchanged |
| Manifest | `titleVi`/`readerProducesVi`/`translatedIn` on chapters; localized accessors with English text fallback; body links gated on `translatedIn` only (FR-009) |
| Chrome coverage | No hardcoded reader-facing string in any component — dictionary only (SC-001) |

## C4 — Language declaration & counterpart metadata

| Guarantee | Detail |
|---|---|
| `lang` | Root `<html lang="en">` unchanged; all `/vi` content inside `<div lang="vi">` (app/vi/layout.tsx) |
| hreflang | All four pages (2 landings, 2 chapters) export `metadata.alternates.languages` with `en` and `vi` URLs — rendered as `<link rel="alternate" hreflang>` pairs (SC-006) |
| vi metadata | Vietnamese pages carry Vietnamese `<title>`/description |

## C5 — Vietnamese chapter authoring contract

Adding a translation of chapter N is exactly: (1) create
`app/vi/part-<n>/chapter-<nn>/<same-slug>/page.mdx` translated from the English
chapter, passing `locale="vi"` to shell/box components; (2) add `"vi"` to the
chapter's `translatedIn` plus its `titleVi`/`readerProducesVi`; (3) export vi
metadata with alternates. Nothing else.

## C6 — Scripted verification bounds (quickstart V2)

| Check | Bound |
|---|---|
| en chapter/landing body vs. pre-feature | unchanged content markers; no `/vi` strings in en chrome |
| Box-type counts vi vs. en chapter | vi ≥ en per type; Checkpoint exactly 1 |
| `div lang="vi"` on vi pages | present; absent on en pages |
| hreflang pairs | 2 per page on all four pages |
| Switcher counterpart hrefs | `/` ↔ `/vi`, en chapter ↔ vi chapter |
| Hardcoded chrome strings in components | 0 (dictionary lookups only) |

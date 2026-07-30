# Data Model: Internationalization with Vietnamese Chapter 0.1

**Feature**: `specs/004-i18n-vietnamese` · **Date**: 2026-07-29

## E1 — Locale

| Field | Rule | Source |
|---|---|---|
| Value | `"en"` \| `"vi"` (`type Locale`, lib/i18n.ts) | FR-001 |
| Default | `en` — first-time visitors, and any path not under `/vi` | FR-004, spec assumption |
| Derivation | Pure function of pathname: `/vi` prefix ⇒ `vi`, else `en` — no negotiation, no detection | research R1/R3 |

## E2 — Localized string set (`dictionaries` in lib/i18n.ts)

| Field | Rule | Source |
|---|---|---|
| Shape | One flat object per locale, identical keys (compile-time enforced by a shared type) | FR-001, spec entity |
| Coverage | Landing (pitch, section labels, "forthcoming", "the road ahead"), header (brand is a proper noun — untranslated), chapter shell (breadcrumb, "You will produce", minutes note, prev/next, back-to-contents, forthcoming badge), box labels (Why/Trap/Checkpoint/Skip ahead/Revised/Forward reference), locale hint text, "available in English only" badge | FR-001, FR-009 |
| Invariant | Zero user-facing chrome strings hardcoded in components; components take `t(locale)` output | SC-001 |

## E3 — Chapter (extended from feature 002's manifest)

| Field | Rule | Source |
|---|---|---|
| *(existing fields unchanged)* | id, path, title, status, readerProduces, sourceDoc, readerMinutes | feature 002 E2 |
| `titleVi?` | Vietnamese title; present for all Part 0 chapters (listing needs them even for forthcoming ones) | FR-001, US3/AC3 |
| `readerProducesVi?` | Vietnamese reader-artifact description | FR-001 |
| `translatedIn?` | locales the chapter body exists in beyond `en`; `["vi"]` for 0.1, absent for 0.2–0.5 | FR-009 |
| Accessors | `chapterTitle(ch, locale)` / `chapterReaderProduces(ch, locale)` fall back to English text; body-availability comes ONLY from `translatedIn` (fallback text ≠ fallback content) | FR-009 |

**Invariant**: a chapter link in locale `vi` is rendered only if `"vi" ∈
translatedIn`; otherwise the vi listing shows the Vietnamese title with the
appropriate badge (forthcoming, or available-in-English-only once an en-only chapter
is published).

## E4 — Language preference

| Field | Rule | Source |
|---|---|---|
| Store | Cookie `locale`, value `en`/`vi`, max-age 1 year, SameSite=Lax, path=/ | research R3 |
| Writer | The language switcher exclusively — merely visiting a `/vi` URL never writes it | FR-004, edge case |
| Reader | The locale-hint component on the two landings (shows cross-locale hint on mismatch); nothing else | research R3 |
| Absent | English experience, no hint | FR-004 |

**State transitions**: unset → `vi`/`en` on first explicit switch; thereafter
overwritten on each switch. Never cleared by the site.

## E5 — Chapter translation (vi chapter 0.1)

| Element | Rule | Source |
|---|---|---|
| File | `app/vi/part-0/chapter-01/from-app-to-infrastructure/page.mdx` (English slug kept — parallel structure) | research R5 |
| Source of truth | The English chapter (argument), docs/01 (facts) — translation adds no claims | FR-006, spec assumption |
| Structural parity | Same section arc; box instances per type ≥ English counts (Why ≥2, SkipAhead ≥1, ForwardRef ≥2, Checkpoint =1); exercise (template with for/who/that/unlike slots preserved, worked example, ≥3 non-goals, yes/no self-checks); takeaways | FR-006, FR-007, SC-002 |
| Terminology | Established terms stay English (WebSocket, API, SDK, idempotency-with-gloss); Vietnamese carries the argument | FR-007 |
| Language declaration | Inside the `div lang="vi"` subtree; vi metadata title/description; hreflang alternates to the en chapter | FR-008 |

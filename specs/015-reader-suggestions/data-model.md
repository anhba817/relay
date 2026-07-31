# Data Model: Reader Suggestions

One entity, one enum, plus the derived allowlist. Prisma schema is the
source artifact (`relay-tutorial/prisma/schema.prisma`); this file is its
contract.

## Suggestion

| Field | Type | Rules |
|---|---|---|
| id | String (cuid) | primary key, server-generated |
| pagePath | String | required; MUST be in the page-path allowlist (R3); locale-prefixed for vi pages (e.g. `/vi/part-1/chapter-02/one-command-whole-world`) |
| locale | Locale enum (`en`, `vi`) | required; MUST match the pagePath prefix |
| selectedText | String | required; 1–1,000 chars, verbatim (no normalization — code stays code) |
| contextBefore | String | ≤ 250 chars; may be empty (selection at block start) |
| contextAfter | String | ≤ 250 chars; may be empty |
| suggestion | String | required; trimmed, 1–2,000 chars, plain text |
| status | SuggestionStatus enum | default `NEW` |
| createdAt | DateTime | server clock, `@default(now())` |

**Explicitly absent** (FR-009): reader identity, email/contact, IP address,
user agent — nothing personal is persisted. (The rate limiter sees the IP in
memory only; it is never written.)

### SuggestionStatus

`NEW` → `HANDLED` (author flips it in the Neon SQL editor; no other
transitions in v1 — a dismissed suggestion is simply `HANDLED`).

### Indexes

- `@@index([pagePath, status])` — the author's main review query
  ("what's open on this page").
- `@@index([createdAt])` — "what came in this week".

## Derived: the page-path allowlist (not stored)

Computed at module load in `lib/suggestions.ts` from the two existing
registries:

- every `published` chapter in `lib/tutorial.ts` → its `path`, plus the
  `/vi${path}` variant when the chapter's translation flag includes vi;
- every doc in `lib/docs.ts` → `/docs/<slug>` and `/vi/docs/<slug>`.

Landing pages and chrome are deliberately absent (spec scope). A submission
whose `pagePath` is not in the set, or whose `locale` disagrees with the
path's prefix, is rejected with `invalid_page`.

## Validation error codes (shared client/server vocabulary)

| Code | Meaning | HTTP |
|---|---|---|
| `invalid_page` | pagePath not allowlisted / locale mismatch | 400 |
| `invalid_selection` | selectedText empty or > 1,000 chars; context > 250 | 400 |
| `invalid_suggestion` | suggestion empty after trim or > 2,000 chars | 400 |
| `invalid_body` | malformed JSON, unknown fields, body > 8 KB | 400 |
| `rate_limited` | per-IP window exceeded | 429 |
| `storage_unavailable` | DB unreachable / insert failed | 503 |

(Honeypot hits return a success-shaped response and store nothing — not an
error code by design, R5.)

## State transitions

```text
(reader submits) → NEW ── author reviews in Neon ──▶ HANDLED
```

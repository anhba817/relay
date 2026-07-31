# Contract: Suggestions API + Capture UI

The externally observable promises. C-numbers referenced from tasks;
verification steps in [quickstart.md](../quickstart.md).

## C1 — POST /api/suggestions

Request (JSON, ≤ 8 KB, exactly these fields — unknown fields rejected):

```json
{
  "pagePath": "/vi/part-1/chapter-02/one-command-whole-world",
  "locale": "vi",
  "selectedText": "…verbatim selection, 1–1000 chars…",
  "contextBefore": "…≤250 chars…",
  "contextAfter": "…≤250 chars…",
  "suggestion": "…1–2000 chars…",
  "website": ""
}
```

Responses:

| Case | Status | Body |
|---|---|---|
| stored (insert committed) | 201 | `{ "ok": true }` |
| honeypot (`website` non-empty) | 201 | `{ "ok": true }` — nothing stored |
| validation failure | 400 | `{ "ok": false, "code": "<data-model error code>" }` |
| rate limited | 429 | `{ "ok": false, "code": "rate_limited" }` |
| DB unreachable | 503 | `{ "ok": false, "code": "storage_unavailable" }` |

- 201 is returned only after the insert commits (ack-after-commit).
- No suggestion content, secrets, or IPs appear in server logs.
- GET/PUT/DELETE on the route → 405.

## C2 — Capture behavior (both locales)

- Right-click with a non-collapsed selection inside the article column →
  custom menu with exactly one action; choosing it opens the dialog with the
  selection quoted read-only.
- Right-click with no selection, a collapsed selection, or anywhere outside
  the article column → native browser menu, untouched.
- Esc or click-away dismisses menu and dialog; after a submit, the next
  selection starts a fresh dialog (no stale state).
- Touch: a selection inside the article floats a suggest button near the
  selection; same dialog.
- The component contributes nothing to the page (no rendered UI, no layout
  shift) until a selection exists.

## C3 — Localization

- Menu item, dialog (title, placeholder, counter, buttons), thank-you, and
  every error message render in the page's locale — vi strings at the
  naturalized register, from the shared `t()` dictionary (no hardcoded
  ternaries).

## C4 — Storage truth

- A 201-acknowledged submission is durably present in Neon with all
  data-model fields; `status = NEW`; timestamps sane.
- Nothing personal stored (FR-009): row contains no IP, UA, or contact.

## C5 — Deployment & no-regression

- `pnpm build`: all 34 existing pages still statically prerendered; only
  `/api/suggestions` is dynamic; sitemap still 28 URLs.
- The standalone Docker image, given `DATABASE_URL` at runtime, serves reading
  pages AND accepts a real POST (Prisma engine present — R6).
- `DATABASE_URL` appears in no build arg, no image layer, no client bundle.
- With `DATABASE_URL` unset or the DB paused: pages render and read fine;
  POST returns 503; dialog shows the localized failure (FR-008).

## C6 — Scope guard

- The capture component mounts only via `ReadingLayout` (chapters + docs);
  landings and chrome offer no suggestion affordance.
- relay-platform and the parent repo are untouched by this feature.

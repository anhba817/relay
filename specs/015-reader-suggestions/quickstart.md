# Quickstart: Verifying Reader Suggestions

Contract references (C1–C6) from
[contracts/suggestions-api.md](./contracts/suggestions-api.md).

## Prerequisites

- A Postgres `DATABASE_URL` in `relay-tutorial/.env` — Dong's Neon dev branch,
  or the T001 disposable local container
  (`postgresql://postgres:dev@localhost:15433/postgres`). Neon is the
  deployment truth either way; the relay-platform compose stack is the
  *product's* teaching infra and stays out of site verification.
- `pnpm prisma migrate dev` has been run against it (schema in place).
- Dev server: `pnpm dev` (or the built standalone for V6).

## V1 — Endpoint battery (C1)

With the dev server up, run the scripted curl battery:

- **Happy path** (valid en + vi payloads) → 201, row visible via
  `pnpm prisma studio` or SQL with all fields, `status = NEW`.
- **Honeypot** (`website: "x"`) → 201, **no row**.
- **Caps**: empty suggestion; 2,001-char suggestion; 1,001-char selection;
  260-char context → 400 with the matching code each time, no rows.
- **Allowlist**: unknown path (`/nope`), forthcoming chapter path, locale/path
  mismatch (`locale: "en"` + `/vi/...` path) → 400 `invalid_page`.
- **Shape**: unknown extra field, non-JSON body, 9 KB body → 400
  `invalid_body`; GET → 405.
- **Rate**: after a fresh server restart, 6 rapid POSTs → sixth is 429
  `rate_limited`.

**Expect**: every case exact; row count equals happy-path count only.

Note: the limiter counts **every** POST (R5) and resets on process restart —
restart the dev server before the battery, run it as one sequence with the
rate case last, and space earlier cases to stay under 5/min.

## V2 — Desktop capture walk (C2, C3) — en and vi

On a chapter page and a docs page, per locale:

1. Select a sentence → right-click → the one-item menu appears; choose it →
   dialog shows the exact selection read-only.
2. Submit a suggestion → thank-you state → row lands in DB with sane
   context before/after.
3. Right-click with **no** selection → native menu. Right-click on the
   sidebar/header (even with article text selected elsewhere: selection
   outside article) → native menu.
4. Esc and click-away dismiss cleanly; a second selection after submitting
   opens a fresh dialog (no stale text).
5. All strings in the page's language (vi: "Góp ý cải thiện", naturalized
   register).

## V3 — Touch capture walk (C2)

DevTools device emulation (or a real phone): long-press select inside the
article → floating suggest button appears near the selection → dialog →
submit → 201. No button when selecting outside the article.

## V4 — Failure honesty (C1, C5)

Stop/pause the database (or unset `DATABASE_URL` and restart):

- Reading pages render and navigate normally (static — nothing to fail).
- POST → 503 `storage_unavailable`; the dialog shows the localized failure
  and allows retry; nothing crashes, no unhandled rejection in the console.

## V5 — No-regression build (C5, C6)

```bash
cd relay-tutorial && pnpm lint && pnpm build
```

**Expect**: build green; 34 static pages unchanged (only `/api/suggestions`
dynamic); sitemap.xml still exactly 28 URLs; no `DATABASE_URL` anywhere in
`.next/static` or the client bundles (`grep -r` it); landing pages have no
capture affordance.

## V6 — Standalone image replay (C5 — the Prisma-engine proof)

```bash
cd relay-tutorial
docker build -t relay-tutorial:suggestions .
docker run --rm -p 3000:3000 -e DATABASE_URL="$DATABASE_URL" relay-tutorial:suggestions
```

Then: load a chapter page (renders), POST a valid suggestion via curl → 201,
row in DB. If the engine is missing, apply the R6 fallback
(`outputFileTracingIncludes`) and re-run.

**Expect**: the image works with `DATABASE_URL` supplied only at `docker run`
— proving nothing was baked at build.

## V7 — Dong's manual checks (handoff, not build gates)

1. Provision the production Neon project/branch; run
   `pnpm prisma migrate deploy` against it.
2. Set `DATABASE_URL` on the server (compose env/host env — never committed).
3. Redeploy (`docker compose up -d --build`); repeat one happy-path submit on
   the live site, both locales; confirm the row in Neon's console.
4. vi read-through of the new UI strings (register).

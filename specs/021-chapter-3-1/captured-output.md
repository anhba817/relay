# Captured output — chapter 3.1 (T022)

Everything the chapter quotes comes from here. Captured 2026-08-04 against
the compose stores, api built from source.

## The signup walk (node scripts/signup-walk.mjs)
```
stand-in provider on 4199, account walk-1786186996322

first authentication  → GET /auth/github/start
    302 redirect to http://127.0.0.1:4199/authorize?client_id=walk&redirect_uri=…
    cookie: relay_oauth_state (HttpOnly, SameSite=Lax)
first authentication  → GET /auth/github/callback
    200 created=true
    organisation 63de1195-4f28-4c46-a3bd-85ebcb6f8869
    application  2eb17d73-72f0-4fb6-bf5c-dcb9808abcab
    environment  dbd313f4-5818-480d-bf5a-b5a79cf25cdc (development)

second authentication → GET /auth/github/start
    302 redirect to http://127.0.0.1:4199/authorize?client_id=walk&redirect_uri=…
    cookie: relay_oauth_state (HttpOnly, SameSite=Lax)
second authentication → GET /auth/github/callback
    200 created=false
    organisation 63de1195-4f28-4c46-a3bd-85ebcb6f8869
    application  2eb17d73-72f0-4fb6-bf5c-dcb9808abcab
    environment  dbd313f4-5818-480d-bf5a-b5a79cf25cdc (development)

same organisation both times — one identity, one workspace (FR-TEN-01/02)

same state, no cookie: 400 — the binding is what makes state work
```

## The invariant tests, as they print
```
✓ src/tenancy/signup.itest.ts > signup > provisions the whole trio from one authentication (FR-TEN-01, FR-TEN-02)
✓ src/tenancy/signup.itest.ts > signup > writes the full set or nothing when provisioning fails (invariant 1)
✓ src/tenancy/signup.itest.ts > signup > recognises a returning owner instead of creating a second organisation (invariant 2)
✓ src/tenancy/signup.itest.ts > signup > refuses a third environment for one application (invariant 3, FR-TEN-04)
✓ src/tenancy/signup.itest.ts > signup > keeps two organisations blind to each other (invariant 4, FR-TEN-05)
✓ src/tenancy/signup.itest.ts > signup > exposes provisioning nowhere but the signup path (invariant 7, spec FR-011)
✓ src/tenancy/signup.itest.ts > signup > refuses a callback whose state does not match the cookie (invariant 5, over HTTP)
✓ src/tenancy/signup.itest.ts > signup > answers 502 when the provider breaks its contract (invariant 6, over HTTP)
```

## Lane counts at the tag
```
unit (Docker-free):  config 6 · service-kit 3 · protocol 26 · api 18 · gateway 33  = 86
integration:         api 44 (8 files) · gateway 8 (2 files) · e2e 8 (1 file)       = 60
baseline before 3.1: 74 unit, 52 integration
```

## The migration's own review finding
```
drizzle-kit generated:  ALTER TABLE "applications" ADD COLUMN "organisation_id" uuid NOT NULL;
against a database with 237 pre-existing application rows from Part 2 test runs.
Rewritten by hand as: add nullable -> backfill one organisation per orphan -> SET NOT NULL.
After applying: 237 applications, 237 with an organisation, 237 organisations invented by the backfill.
```

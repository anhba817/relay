# Quickstart — validating chapter 3.1

Prerequisites: the Part 2 checkpoint state, Docker for the compose stores, and
nothing else. No provider account is needed to validate — the test lane speaks
to a local stand-in (research R8). Registering a real GitHub OAuth app is a
reader step, exercised in V5.

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 docker compose up -d --wait postgres redis
DATABASE_URL="postgres://relay:relay@localhost:15432/relay" node services/api/dist/db/migrate.js
```

---

## V1 — The gates still hold (C: no regression)

```bash
pnpm lint && pnpm typecheck && pnpm test          # Docker-free lane
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 \
  DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  RELAY_REDIS_URL="redis://localhost:16379" pnpm test:integration
```

Expected: every Part 1 and Part 2 suite passes unchanged, including the 2.8
journey; the unit lane needs no Docker; the new tenancy tests appear in the
integration lane. A Part 2 suite that changes behaviour here is a finding, not
an adjustment (spec FR-013).

## V2 — The seven invariants (contracts §Invariants)

```bash
RELAY_POSTGRES_PORT=15432 DATABASE_URL="…" \
  pnpm --filter @relay/api test:integration
```

Expected, each by name in the output:

1. provisioning writes the full set for the call, or none when it fails
   mid-way — five rows for a new identity, four when the human already exists;
2. a second authentication with the same provider identity returns the same
   organisation and creates nothing;
3. a third environment for one application is refused by the database;
4. two organisations created in one run cannot see each other's applications,
   environments or messages;
5. provisioning is unreachable from any controller outside `tenancy/`;
6. plus the unit cases: a mismatched `state` is refused before any provider
   call, and a malformed provider response is a 502.

## V3 — The stub is gone

```bash
psql "postgresql://relay:relay@localhost:15432/relay" -c "\d applications"
```

Expected: `organisation_id` present and NOT NULL; the 2.1 stub's shape (id +
name only) is gone; `0002_tenancy.sql` is recorded in `schema_migrations`.

## V4 — Signup end to end, against the stand-in

```bash
node scripts/signup-walk.mjs
```

Expected: a transcript showing the redirect, the callback, and the created
trio — then a second run of the same identity showing `created: false` and the
same organisation id. This transcript is what the chapter quotes; if it is not
reproducible, the chapter cannot claim it (2.8's rule).

## V5 — Signup against a real provider (reader step, optional)

Register an OAuth app with callback `http://localhost:4000/auth/github/callback`,
export the client id/secret, start the api, and open
`http://localhost:4000/auth/github/start`. Expected: GitHub's consent screen,
then a JSON body naming a real organisation, application and environment.

## V6 — The chapter itself

```bash
cd ../relay-tutorial
pnpm lint && pnpm build
pnpm check:docs && pnpm check:fences
```

Expected: the build renders the new page; `check:fences` replays every
published chapter onto the repository with no drift and reports the Vietnamese
editions as mirrored where they exist; `check:docs` confirms the ADR-18 edits
are mirrored into `content/docs/`.

Then verify traceability (SC-006): every `FR-*`/`NFR-*`/`DR-*`/`EIR-*`
identifier in the chapter must exist in `docs/04-srs.md` or `docs/05-sad.md`,
and every table or column named in prose must exist in the schema — zero
invented identifiers.

Then check the battery by hand or with the feature's measurement step:
2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, exactly one `SKIP AHEAD`
naming `part3-ch1`, ≥1 forward reference, 2–4 figures, one closing
`CHECKPOINT`.

## V7 — Publication state

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/part-3/chapter-01/tenants-all-the-way-down
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/vi/part-3/chapter-01/tenants-all-the-way-down
```

Expected: `200` then `404` — English published, Vietnamese honestly absent
(spec FR-015), with the chapter listing showing it as untranslated and 3.2–3.7
still forthcoming.

---

## Definition of done

- V1–V4, V6, V7 pass; V5 is available to a reader with a provider account.
- Every chapter claim traces to a document, an earlier chapter, or a recorded
  decision — and every number in the chapter came from output captured in V2
  or V4, not from estimation.

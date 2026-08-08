# Quickstart — validating chapter 3.2

Prerequisites: the `part3-ch1` state, Docker for the compose stores, and nothing
else. No provider account is needed — signup runs against the local stand-in
3.1 built.

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 docker compose up -d --wait postgres redis
pnpm build
DATABASE_URL="postgres://relay:relay@localhost:15432/relay" node services/api/dist/db/migrate.js
```

---

## V1 — Nothing regressed

```bash
pnpm lint && pnpm typecheck && pnpm test
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 \
  DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  RELAY_REDIS_URL="redis://localhost:16379" pnpm test:integration
```

Expected: every existing suite passes, including 2.8's journey. Suites that used
to send `x-relay-environment` now mint a key instead — their **assertions** must
be unchanged. A Part 2 assertion that had to be weakened to accommodate
credentials is a finding, not an adjustment (spec FR-020).

## V2 — The twelve invariants (contracts §Invariants)

```bash
RELAY_POSTGRES_PORT=15432 DATABASE_URL="…" pnpm --filter @relay/api test:integration
RELAY_POSTGRES_PORT=15432 DATABASE_URL="…" pnpm --filter @relay/api test
```

Expected, each by name: the secret shown once and unrecoverable; 401 with no
credential; 403 `wrong_credential_type` whose message names presented and
expected; a foreign key seeing nothing; a revoked key refused on the next
request; two active keys working at once; a token refused when expired,
malformed, mis-signed, foreign, or over-long; `alg: none` refused; the dev-token
endpoint minting in development and 404ing in production; a socket surviving its
token's expiry; no credential in any log; and the prefix matching the kind.

## V3 — The seam is gone, mechanically

```bash
grep -rn "x-relay-environment" services packages scripts --include=*.ts --include=*.mjs | grep -v itest
grep -rn "RELAY_DEV_JWT_SECRET\|DEV_JWT_SECRET" services --include=*.ts | grep -v test
```

Expected: **no matches in either.** Not "only a few" — none. Test files may still
reference the header while proving it is ignored; production code may not
mention it at all (spec SC-008).

## V4 — Signup hands over one key, once

```bash
node scripts/signup-walk.mjs
```

Expected: the first authentication's response carries `api_key.secret` with an
`rk_dev_` prefix; the second (same identity) reports `created: false` and carries
**no** key — the old secret is unrecoverable and rotation is the answer.

## V5 — A first message with a real credential

```bash
node scripts/credential-walk.mjs
```

Expected transcript: the key sends a message; the same key mints an end-user
token; the token opens a socket and receives the message; the key is then
presented to the socket and refused with 4001; the token is presented to the
dev-token endpoint and refused with `wrong_credential_type`, message included.
That refusal pair is the chapter's point, so the walk prints both.

## V6 — The chapter itself

```bash
cd ../relay-tutorial
pnpm lint && pnpm build && pnpm check:docs && pnpm check:fences
```

Expected: the build renders the new page; the fence chain replays every published
chapter with no drift, including the two fix-forward edits to 3.1; docs-drift is
clean.

Then the battery: 2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, exactly one
`SKIP AHEAD` naming `part3-ch2`, ≥1 forward reference, 2–4 figures, one closing
`CHECKPOINT`.

Then traceability (spec SC-009): every `FR-*`/`NFR-*`/`DR-*`/`EIR-*` in the
chapter must exist in `docs/04-srs.md` or `docs/05-sad.md`, and every table and
column named in prose must exist in `schema.ts`.

## V7 — No secret survives the transcripts

```bash
grep -rniE "rk_dev_[A-Za-z0-9_-]{8,}|eyJ[A-Za-z0-9_-]{20,}" specs/022-chapter-3-2/captured-output.md
```

Expected: matches only where the chapter deliberately shows a credential's
*shape* (a truncated example), never a working secret from a real run, and no JWT
bodies at all. Anything else must be redacted before publication (spec SC-007).

## V8 — Publication state

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/part-3/chapter-02/keys-and-tokens
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/vi/part-3/chapter-02/keys-and-tokens
```

Expected: `200` then `404` — English published, Vietnamese honestly absent, with
the listing showing 3.2 untranslated and 3.3–3.7 forthcoming.

---

## Definition of done

- V1–V8 pass.
- Every number and transcript in the chapter came from V2, V4 or V5 — not from
  estimation.
- Chapter 3.1's two stale statements are corrected: the session forward
  reference, and the signup response's field list.

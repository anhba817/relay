# Quickstart — validating chapter 3.12

Seventeen checks. Run in order; several depend on earlier ones. Every command is one a
maintainer runs, verbatim — the CI workflow's own rule.

## Prerequisites

```bash
cd relay-platform
docker compose up -d --wait            # postgres 15432, redis, nats, mailpit, clickhouse
pnpm install
pnpm build
node services/api/dist/db/migrate.js
```

**The coverage lane needs four variables that only CI sets, and this cost a run to
learn.** Without them 11 tests fail in a way that reads as regression — a missing
platform credential fails `limits.itest.ts` and cascades into the dispatcher, and NATS
comes back `CONNECTION_REFUSED`:

```bash
export RELAY_REDIS_URL=redis://localhost:6379
export RELAY_NATS_URL=nats://localhost:4222
export RELAY_INTERNAL_CREDENTIAL=rk_svc_ci_0123456789abcdef0123456789abcdef
export RELAY_WEBHOOK_SECRET_KEY="BpDal75yBZp7Fc2GtGS3D1vh7qOKgCWJkF6/d0XWxBU="
```

`DATABASE_URL` stays unset: every package falls back to port 15432, which is this
project's documented port. With the four variables set, the starting commit is 69 files
and 668 tests green in 360 s.

---

## V0 — the lanes, before anything changes

```bash
pnpm lint && pnpm typecheck && pnpm test
pnpm test:integration
```

Record both counts. Chapter 3.11 closed on 348 unit and 330 integration.

## V1 — the target list derives, and fails loudly if it cannot

```bash
pnpm vitest run services/api/src/isolation/targets --config services/api/vitest.integration.config.mts
```

**Expect** 22 targets, each matched to exactly one classification entry.

**Then break it on purpose.** Comment out the classification entry for
`GET /v1/webhooks/:id` and re-run: the suite must fail naming that route. Restore it.
This is SC-002 and it is the only evidence that FR-002 is a property rather than a
sentence.

## V2 — a new route fails the suite until classified

Add a throwaway `@Get("probe")` to `HealthController`, re-run V1.

**Expect** failure naming `GET /probe`. Remove the route.

## V3 — the REST gauntlet

```bash
pnpm vitest run services/api/src/isolation/gauntlet --config services/api/vitest.integration.config.mts
```

**Expect** green, with a printed count of attacked and exempt targets that sums to 22.

## V4 — indistinguishability is compared, not assumed

Pick one `read` target. In a scratch edit, change its 404 to a 403 and re-run V3.

**Expect** failure on the status comparison, not on a hard-coded 404. Revert.

## V5 — a write attack is judged on state, not on status

In a scratch edit, make one repository `UPDATE` drop its `environment_id` predicate and
re-run V3.

**Expect** failure on the before/after row comparison. If it fails only on a status
comparison, the write shape is not doing its job. Revert with `git checkout`.

## V6 — the structural check

```bash
pnpm vitest run services/api/src/isolation/tenant-scope --config services/api/vitest.integration.config.mts
```

**Expect** green, and a printed classification: 12 direct, 2 hop, 7 spine, 1 unscoped —
the unscoped one being `outbox`, named with its reason.

**Then** create a table with no tenant column in a scratch migration and re-run.

**Expect** failure naming the table.

## V7 — the socket attacks

```bash
pnpm vitest run services/gateway/src/isolation --config services/gateway/vitest.integration.config.mts
```

**Expect** green. A token minted for one environment sees no channel, sends nothing, and
resumes nothing belonging to another.

## V8 — the two endpoints, by hand

```bash
node scripts/seed-demo-tenant.mjs        # prints an API key
KEY=<the printed key>

curl -s -X POST localhost:4000/v1/channels \
  -H "authorization: Bearer $KEY" -H 'content-type: application/json' \
  -d '{"external_id":"support","type":"public","name":"Support"}' -i | head -1
# expect 201

curl -s -X POST localhost:4000/v1/channels \
  -H "authorization: Bearer $KEY" -H 'content-type: application/json' \
  -d '{"external_id":"support","type":"public","name":"Support"}' -i | head -1
# expect 200 — FR-CHN-02, the same channel, not an error
```

Then add members twice and confirm the second call is a success naming them as already
members, rather than a 500 from `members`' primary key (R14a).

## V9 — the new endpoints joined the gauntlet without being told to

Re-run V1 and V3.

**Expect** the target count to have risen from 22 to 24, and both new routes attacked.
If they appear as unclassified, that is the correct failure and the classification list
is what changes — never the derivation.

## V10 — the error set is derived and complete

```bash
pnpm test -- codes
```

**Expect** twelve codes, twelve reference entries, set-equal in both directions — the eleven that exist today plus `wrong_credential_service`, which this chapter adds.

**Then** add a twelfth key to the registry with no reference entry and re-run.

**Expect** failure. Remove it. Then add a reference entry for a code that does not exist
and re-run: **expect** failure again. Both directions or neither.

## V11 — `docs_url` resolves against the published site

```bash
curl -s localhost:4000/v1/webhooks/00000000-0000-0000-0000-000000000000 \
  -H "authorization: Bearer $KEY" | python3 -c 'import json,sys;print(json.load(sys.stdin)["docs_url"])'
```

Fetch the printed URL and confirm the anchor's `id` is present in the HTML.

**Expect** the anchor to be the code verbatim, underscores intact. A URL that matches a
pattern is not a URL that resolves.

## V12 — the site still builds and the mirror still agrees

```bash
cd ../relay-tutorial
pnpm build && pnpm check:docs && pnpm check:fences
```

**Expect** all three green, with the fenced-file and chapter counts printed. This
chapter's fences are the titled code fences inside its own page — there is no
per-chapter file under `fences/`, which holds `post-series.md` and nothing else — and
every amended file needs a diff fence here or HEAD fails on the difference between the
last fenced state and the file on disk. `check:docs`
must be checked specifically for the seventh document: a document in the registry and
not in the sync list renders a stale page and the drift check does not see it, because
it only walks files its own glob selects.

## V13 — the outsider is sealed

```bash
cd ../relay-platform
docker compose up -d --wait                              # stores only — the services are
                                                         # behind profiles: ["services"]
DATABASE_URL=postgres://relay:relay@localhost:15432/relay \
  node services/api/dist/db/migrate.js
docker compose --profile services up -d --wait           # api 4000, gateway 4001
node scripts/seed-demo-tenant.mjs                        # prints a credential
RELAY_API_URL=http://localhost:4000 RELAY_WS_URL=ws://localhost:4001 \
  pnpm --filter @relay/outsider test:integration
```

The order is load-bearing: the seed writes to a migrated database, and the api needs the
schema before it serves anything the integration asks for. **The package starts nothing** —
if the platform is absent it must fail saying so rather than trying to launch one.

**Expect** a completed integration: credential, channel, members, token, REST send,
history read, socket receive.

**Then** add `import { ERROR_CODES } from "@relay/protocol";` to its test file.

**Expect** a resolution failure from pnpm — no lint needed, because
`node_modules/@relay` does not exist at the workspace root.

**Then** add `import { ERROR_CODES } from "../../protocol/src/codes.js";` instead.

**Expect** lint to fail on the `no-restricted-imports` rule — level 2.

**Then** the escape neither of those reaches:
`readFileSync(join(import.meta.dirname, "..", "..", "protocol", "src", "codes.ts"))`.

**Expect** lint to fail on the `no-restricted-syntax` rule — level 3. Without it this
passes, because a path built from string fragments is not an import specifier.
`packages/e2e/src/harness.ts:31` does exactly this and spawns the api's build output from
the result.

## V14 — the guard sees the four usage tables

```bash
pnpm --filter @relay/test-harness test:integration
```

**Expect** green, and a driven cross-environment mutation refused on each of
`usage_periods`, `usage_active_users`, `quota_notifications` and `usage_connections`.
For the three with composite primary keys, the refusal must carry the row's JSON rather
than raising `record "old" has no field "id"`.

## V15 — the isolation code against the 100% clause

```bash
pnpm coverage
python3 -c "import json;d=json.load(open('coverage/coverage-summary.json'));\
k=[x for x in d if x.endswith('db/repository.ts')][0];b=d[k]['branches'];\
print(b['covered'],'/',b['total'],'=',b['pct'])"
```

**The starting figure, measured on this feature's first commit:** `repository.ts` at
97.50 / **90.60** / 100 / 99.45, branches **241/266 — 25 uncovered arms** — against a
pinned 97/90/100/99. Two lines are uncovered (152, 3140) and functions are at 100%, so
almost all 25 are unhit arms on covered lines.

**Naming them needs a reporter the config does not have.** `reporter:` is
`["text", "json-summary"]`, and `json-summary` carries totals rather than locations. Add
`"json"` and the arms become enumerable from `coverage/coverage-final.json`; without it
FR-040 can count them and not name them.

**Expect** the ratchet to end at or above where it started. And treat a movement under
0.1 as noise rather than a result: the same commit measured 90.32/83.98/89.51/91.53 at
chapter 3.11's close-out and 90.37/84.17/89.51/91.58 today, with no code between them —
the lane's coverage is mildly data-dependent on what the test database has accumulated.

## V16 — the lane, twenty times

```bash
for i in $(seq 1 20); do pnpm test:integration 2>&1 | tail -3; done
```

**Expect** the same test count every run. A count that moves is a defect, not noise —
chapter 3.11 found three that way, two of them older than the chapter.

**The fixed port is in `services/gateway/src/limits.itest.ts`**, not the api's — two
files carry that basename and only the gateway's binds `?? 4124`. Check every suite that
spawns an api or a gateway, not just the one CLAUDE.md names.

## V17 — the lint ban applies to tests again

```bash
npx eslint services/api/src/quotas/period.itest.ts     # before: exits 0, wrongly
pnpm lint
```

That file imports `drizzle-orm` and is in no ignores list, and it passes today because a
second flat-config block for `**/*.itest.ts` redefines `no-restricted-imports` and
replaces the restriction. After T069a it must fail, or be listed with a reason.

**Then** add a `drizzle-orm` import to an integration test outside the permitted set and
confirm `pnpm lint` fails. Remove it. **Expect** the count of legitimately exempted files
to be stated, each with a reason.

---

## The reintroductions, run once and recorded

Not a check — the evidence for FR-013. Each is applied to the working tree, measured,
and reverted with `git checkout`.

| # | Change | Expected to fire |
|---|---|---|
| 1 | drop `environment_id` from one repository `SELECT` | a `read` pair's body comparison |
| 2 | drop it from one `UPDATE` | a `write` pair's before/after comparison |
| 3 | change one 404 to a 403 | a `read` pair's status comparison |

Record which assertions fired **and which did not**. Three faults chosen by the suite's
own author measure sensitivity to three faults, not coverage of the class. The working
tree must be clean at the phase commit, and the phase's diff reviewed for those files.

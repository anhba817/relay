# Quickstart — chapter 4.4, every request is an event

**Feature**: `specs/049-chapter-4-4/` · **Date**: 2026-09-14

**Constitution VI requires this to run unmodified.** Every command below was executed against
the live stack while this file was written, except the four marked **after phase 3** and
**after phase 4**, which name what does not exist yet. Paths are relative to
`relay-platform/` unless stated.

---

## 0. The stack

`RELAY_POSTGRES_PORT=15432` because this machine's own Postgres holds 5432.

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d
```

Health, and it matters that this passes without `--no-deps`: 048 closed with the `EVENTS`
store unrecoverable and the dependency gate red (048-6, since closed).

```bash
curl -s localhost:8222/healthz          # {"status":"ok"}
curl -s localhost:4000/healthz          # {"status":"ok","service":"api",...}
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary "SELECT 1"
```

The third is a **positive control**, not decoration. 047 read three `curl` outputs as data
when all three were authentication errors, because `clickhouse-server:25.3` refuses `default`
without `CLICKHOUSE_SKIP_USER_SETUP=1`. If `SELECT 1` does not answer `1`, nothing below
means anything.

## 1. What is there before the chapter

The streams, and whether anything reads them:

```bash
curl -s 'localhost:8222/jsz?consumers=1' | \
  node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{
    const a=(JSON.parse(s).account_details||[])[0];
    for (const t of (a?.stream_detail||[]))
      console.log(t.name.padEnd(12), String(t.state.messages).padStart(5), "msgs",
                  String(t.state.bytes).padStart(8), "bytes",
                  "consumers", t.consumer_detail?.length ?? 0);
  })'
```

At the opening of this feature:

```
EVENTS           0 msgs        0 bytes consumers 2
DELIVERIES      69 msgs    21735 bytes consumers 11
ANALYTICS       36 msgs    17529 bytes consumers 1
```

**487 bytes per attempt record** — the number R4 compares a request record against.

**It was 37 messages at 476 bytes until this feature's second analysis pass**, which found one of
them was probe debris from 048 — `analytics.probe.ping.<uuid>` carrying `{}` — and removed it. The
per-record average moved because the record removed was 2 bytes.

**The consumer counts move with the profile and the reading above is the one taken after
§0**, with `--profile services` up: the api and dispatcher create their `EVENTS` consumers on
boot. Run this before starting them and `EVENTS` reports 0. A number that depends on what
else is running is a number that needs the neighbour held still, which is the third time this
part has needed that said out loud.

The analytical schema and its ledger:

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT name FROM system.tables WHERE database='relay_analytics' ORDER BY name FORMAT TSV"
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT filename FROM relay_analytics.schema_applied ORDER BY filename FORMAT TSV"
```

The ledger tail is `0003_webhook_attempts.sql`, which is why this chapter's file is `0004`.

## 2. Reproduce R1 — the consumer destroys what this chapter will publish

The chapter's opening defect, before anything is changed. This runs the real `ingestOnce`
against a probe stream so nothing touches `ANALYTICS`.

```bash
cd services/ingester && pnpm build
```

Then the probe in `research.md` R1. What it printed:

```
  published 2 · stream holds 2
  pass 1: written 1  malformed 1        <- the attempt wrote; the request record did not
  pass 2: written 0  malformed 0        <- terminated, so it never comes back
  stream still holds 2 of 2 · consumer: num_pending 0 · ack_pending 0
```

**Read the last line twice.** The stream says both records are there. The consumer says there
is nothing pending. One of them is gone for good and neither instrument says so.

`written 1` is the positive control — without it the probe would be measuring a broken
consumer rather than a difference between record types.

## 3. Which requests have no tenant

Six requests, then the api's own log lines:

```bash
for r in "GET /healthz" "GET /v1/webhooks" "GET /v1/does-not-exist" \
         "GET /v1/channels/abc123/messages" "POST /internal/dispatch/expand"; do
  set -- $r
  printf "%-6s %-34s -> %s\n" "$1" "$2" \
    "$(curl -s -o /dev/null -w '%{http_code}' -X "$1" "localhost:4000$2")"
done

docker compose logs api --since 30s | grep '"request"' | tail -6
```

Every one of them is logged, 401s and the 404 included — which is why the producer belongs in
the middleware layer and not in a Nest interceptor (R5). Note what the logged `path` holds:

```
"method":"GET","path":"/v1/channels/abc123/messages","status":401
```

The raw path, with the channel id in it. FR-005 says `endpoint`, and this is the reason.

## 4. After phase 3 — the table exists

```bash
node analytics/apply.mjs
```

Expect `applied 1: 0004_api_requests.sql`. Run it a second time and expect
`applied nothing` — the line `CREATE TABLE IF NOT EXISTS` cannot produce, and the reason
`apply.mjs` exists beside it.

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT count() FROM relay_analytics.api_requests FINAL FORMAT TSV"
```

## 5. After phase 4 — a request becomes a row

```bash
curl -s -o /dev/null -w '%{http_code}\n' localhost:4000/v1/webhooks       # 401, no tenant
curl -s -o /dev/null -w '%{http_code}\n' localhost:4000/healthz           # 200, no tenant

curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT endpoint, method, status, latency_ms, principal_kind, refused_at,
          isNull(environment_id) AS tenantless
     FROM relay_analytics.api_requests FINAL
    ORDER BY ts DESC LIMIT 10 FORMAT TSV"
```

**`FINAL` is not optional.** 048 measured a bare `count()` answered from part metadata without
reading a row — 0.9 ms and wrong by 100,000 — against `FINAL`'s 5.3 ms reading 1.2 M rows. A
`ReplacingMergeTree` read without it is a read of whatever has not been merged yet.

The isolation check, which is FR-010 rather than a nicety:

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT countIf(environment_id IS NULL)  AS tenantless,
          countIf(environment_id IS NOT NULL) AS attributed,
          principal_kind, count()
     FROM relay_analytics.api_requests FINAL
    GROUP BY principal_kind FORMAT TSV"
```

A tenant-scoped read must return that tenant's rows and none of the tenantless ones.

## 6. The gates

All five `check:*` scripts live in **`relay-tutorial`**. `pnpm` in the wrong repository exits
silently and reads as green.

```bash
cd ../relay-tutorial
pnpm check:fences      # report as a delta, broken down by kind and locale
pnpm check:docs        # check-docs-drift.sh AND check-revision-order.mjs
pnpm check:srs
pnpm check:figures     # the gate over figures.ts — this chapter has three
pnpm check:errors      # reads the BUILT dist — build first
```

**Four of those five exit 0. `check:fences` exits 1, and that is the inherited baseline
rather than a break.** Run at the opening of this feature:

```
check-fence-chain: 110 problem(s) — APPLY 74, HEAD 36        exit 1
pnpm check:docs      exit 0    11 revisions ascend, 1.0 to 1.10
pnpm check:srs       exit 0    classes checked: ASM CON DR EIR FR NFR
pnpm check:figures   exit 0    263 figures, every diagram passed as `code`
pnpm check:errors    exit 0    27 codes, 27 sections, each with a cause
```

110 is the number 047 and 048 both opened and closed at. **The chain gate's exit code carries
no information about this chapter** — it has been 1 since long before it, and it stays 1 until
the inherited 110 are gone. What this chapter is answerable for is the **delta**, which is why
FR-023 and SC-010 ask for the breakdown by kind and locale rather than for a pass. A reader
who takes the exit code as the signal concludes they broke the chain by checking it out.

**Those are the five, checked against `package.json` rather than remembered.** An earlier
draft of this file listed `check:refs` and `check:revisions`, and neither exists:
`pnpm check:refs` exits **254** with *Command "check:refs" not found*. Revision ordering is
inside `check:docs`; `check-refs.py` is one of the Python instruments under
`specs/045-part-3-rework/`, not a gate. **The two it omitted were `check:srs` and
`check:figures`** — and `check:figures` is the gate over the `figures.ts` this chapter's
figure task is entirely about, so the one that was missing was the one that mattered.

And in `relay-platform`:

```bash
pnpm lint && pnpm typecheck && pnpm test
```

`analytics/**/*.mjs` is already in `eslint.config.mjs` — 047 added it after 13 `no-undef`
errors.

## 7. Bringing it down

```bash
cd relay-platform && docker compose --profile services down
```

**Not an abrupt kill.** 048's `EVENTS` stream was left unrecoverable by a `down` mid-write,
and the store recreated on top of the broken one inherited the failure invisibly — it
returned, answered `streams.info` correctly, carried three phases of publishes, and could not
survive a restart. Volumes are kept by this command, which is what preserves the corpus.

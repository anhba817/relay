# Quickstart — chapter 4.18

Walk the log by hand: ban somebody, lift the ban, read the two entries back, then try to
change one and fail.

**NOT YET RUN — this document is written at plan time and the platform it describes does not
exist yet.** Every expected value below is a prediction, and predictions in this position have
been wrong in each of the last four chapters: 4.16's quickstart was wrong three times, 4.17's
four. The phase-9 task is to run it as a document, start to finish, and correct it in place
with each wrong version recorded. **The two sections marked MEASURED are the exceptions** —
they were run against the current platform while this plan was written, and what they show is
why the chapter exists.

The corrections earlier chapters earned are applied rather than rediscovered:

- the api is on **4000**, the gateway on **4001**;
- `docker compose --profile services stop` names its services and **`ingester` is not one**;
- `psql -tAc` with `RETURNING` prints the value **and** the command tag;
- a history array is keyed by its own name — `messages` there, `entries` here — and a
  defaulting accessor over the wrong key reads as the platform dropping data;
- `date +%s%3N` does **not** truncate on this machine;
- `pnpm -s <script>` reports red for a green gate; drop the `-s`;
- capture an exit code **outside** the pipeline, or `$?` is `tail`'s. Seven occurrences so far.

## 0 · Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
RELAY_CLICKHOUSE_HOST=localhost node analytics/apply.mjs
RELAY_POSTGRES_PORT=15432 docker compose --profile services build
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
export CREDENTIAL=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs | tail -1)
```

## 1 · MEASURED — what the platform says today

Run before the chapter, so the gap is a measurement rather than a claim. A ban and its
reversal, then everything the platform can tell you about them:

```bash
curl -sX POST localhost:4000/v1/users -H "authorization: Bearer $CREDENTIAL" \
  -H 'content-type: application/json' \
  -d '{"users":[{"external_id":"quickstart-target","display_name":"Target"}]}' >/dev/null
curl -s -o /dev/null -w 'ban    %{http_code}\n'   -X POST   "localhost:4000/v1/users/quickstart-target/ban" -H "authorization: Bearer $CREDENTIAL"
curl -s -o /dev/null -w 'unban  %{http_code}\n'   -X DELETE "localhost:4000/v1/users/quickstart-target/ban" -H "authorization: Bearer $CREDENTIAL"
psql postgres://relay:relay@localhost:15432/relay -tAc \
  "select external_id, coalesce(banned_at::text,'<NULL>') from users where external_id = 'quickstart-target'"
```

**Measured: `ban 200`, `unban 200`, then `quickstart-target|<NULL>`.** `POST …/ban` sets
`banned_at` to the current instant and `DELETE …/ban` sets it back to `NULL`, so the row is
byte-identical to a user who was never banned. Two moderation actions happened and the
operational store holds no evidence that either did.

**`coalesce(…,'<NULL>')` RATHER THAN THE BARE COLUMN**, because the bare column prints
`quickstart-target|` and an empty field at the end of a line is the easiest thing in this
document to read past. The point of the section is an absence, so the absence has to be
visible.

Nothing else holds it either. Two further checks, both measured:

```bash
psql postgres://relay:relay@localhost:15432/relay -tAc \
  "select table_name||'.'||column_name from information_schema.columns
   where column_name ~ 'ban|moderat|actor|audit' order by 1"
psql postgres://relay:relay@localhost:15432/relay -tAc \
  "select subject, count(*) from outbox where created_at > now() - interval '5 minutes'
   group by 1 order by 2 desc"
```

**Expected**: `users.banned_at` and `pg_stat_database.sessions_abandoned`, then nothing. One
real column in the whole database whose name touches banning, moderation, actors or auditing —
and **no event either**, because this user belongs to no channel and `banUser` publishes per
channel. The ban was announced to nobody and recorded nowhere.

**AND THE SECOND HIT IS THE CONTROL WORKING.** `pg_stat_database.sessions_abandoned` matches
on the substring `ban` and is a statistics catalogue, not this schema. A pattern that returns
two hits and one meaning is why this project's rule is to **classify every hit rather than
report a count** — a sweep that had returned only `users.banned_at` would have looked the same
and proved less.

## 2 · MEASURED — why the request log is not the answer

```bash
docker exec relay-clickhouse-1 clickhouse-client -q 'SELECT 1'   # the control, same client
docker exec relay-clickhouse-1 clickhouse-client -q \
  "DESCRIBE relay_analytics.api_requests FORMAT TSV" | cut -f1,2
```

**Expected**: ten columns — `environment_id · ts · request_id · endpoint · method · status ·
latency_ms · principal_kind · refused_at · limited_operation`. Three of FR-MOD-03's five
fields are there. **There is no actor** — `principal_kind` says `application` or `user`, never
which key — and **no target**, because the user id lives in the path and the path is never
stored. The engine is `ReplacingMergeTree` and the TTL is 30 days, against a clause that says
immutable and a year.

## 3 · The entries (after the chapter)

```bash
curl -s "localhost:4000/v1/audit-log?limit=10" -H "authorization: Bearer $CREDENTIAL" \
  | python3 -m json.tool
```

**Expected**: two entries, newest first, each naming the actor (`kind: "application"` and the
key's id), the action, the target `quickstart-target`, the instant and the request id. The
array is keyed **`entries`**, and beside it `"has_more": false`, `"next_cursor": null`,
`"prev_cursor": null` and the resolved `"window"`. **`has_more` is the one to look at**:
EIR-API-06 requires it of every list endpoint, the platform was non-conforming from chapter
2.4 until 4.8 added it, and an earlier draft of this contract omitted it while claiming to be
modelled on the route that fixed it.

## 4 · The same request, in both logs

```bash
RID=$(curl -s "localhost:4000/v1/audit-log?limit=1" -H "authorization: Bearer $CREDENTIAL" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["entries"][0]["request_id"])')
echo "request_id=$RID"
docker exec relay-clickhouse-1 clickhouse-client -q \
  "SELECT endpoint, method, status FROM relay_analytics.api_requests WHERE request_id = '$RID' FORMAT TSV"
```

**Expected**: the request log's row for the same request — the route and the status, which the
audit entry does not carry, beside the actor and target, which the request log does not. The
two logs answer different questions about one request and the id is the join.

**If this returns nothing, read `gaps.md` 050-8 before concluding anything**: on the stack this
series ships, nothing drains the analytical streams, so a customer reading their own request
log finds it empty.

## 5 · Try to change an entry

The id comes from §3's response, not from the database — the route returns it and a second
source for the same value is a second thing that can disagree:

```bash
ID=$(curl -s "localhost:4000/v1/audit-log?limit=1" -H "authorization: Bearer $CREDENTIAL" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["entries"][0]["id"])')
psql postgres://relay:relay@localhost:15432/relay -v ON_ERROR_STOP=0 -c \
  "update audit_log set action = 'something else' where id = '$ID'"
psql postgres://relay:relay@localhost:15432/relay -v ON_ERROR_STOP=0 -c \
  "delete from audit_log where id = '$ID'"
psql postgres://relay:relay@localhost:15432/relay -tAc \
  "select count(*) from audit_log where id = '$ID'"
```

**Expected**: two `ERROR: audit entries are append-only`, then `1`. This is the only section of
this document that runs as the database rather than as a client, and it has to: the api
exposes no route that could attempt the write, so a probe through the api would prove nothing
about the table.

## 6 · MEASURED — and what the refusal does not cover

```bash
psql postgres://relay:relay@localhost:15432/relay -v ON_ERROR_STOP=0 <<'SQL'
set session_replication_role = replica;
update audit_log set action = 'something else' where id = (select id from audit_log limit 1);
set session_replication_role = origin;
SQL
```

**Expected**: `UPDATE 1`. **One line disables every trigger in the session**, and the api
connects as `relay`, which `select usesuper from pg_user` answers `t` for. `DROP TRIGGER`
works too.

So the claim the chapter publishes is scoped: **the log is immutable to the application and to
accident, and not to somebody holding the database password.** A separate, non-superuser role
for the application would make it much stronger, and that is a deployment change rather than a
chapter — recorded in `gaps.md` with its cost.

Restore the entry's value before anything else is counted, or leave the probe's row out of
every later count. **A red probe writes to the lane** (043), and chapter 4.17 spent a battery
discovering that its own quickstart traffic had broken two suites that read shared state.

## 7 · What this cannot show

- **A year.** Nothing prunes an operational table in this platform, so the retention clause is
  stated and unenforced (research R7, ADR-28's precedent).
- **A person.** The actor is a key id. Who held the key is not knowable from here.
- **A history.** The log begins at the migration. No entry exists for any moderation action
  taken before it, and an empty window means *not recorded*, not *did not happen*.

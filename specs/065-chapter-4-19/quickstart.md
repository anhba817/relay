# Quickstart — chapter 4.19

Walk the gap by hand: send a message, edit it twice, delete it with the tenant key, and count
how many of the three texts you can get back.

**SECTIONS 1 AND 2 ARE MEASURED** — run against the current platform while this plan was
written, and what they show is why the chapter exists. **Everything after them is a
prediction.** The phase-9 task is to run this document start to finish and correct it in
place, recording each wrong version. The last five chapters' quickstarts were wrong three,
four, three, five and two times at exactly this point.

The corrections earlier chapters earned are applied rather than rediscovered:

- the api is on **4000**, the gateway on **4001**;
- `docker compose --profile services stop` names its services and **`ingester` is not one**;
- a channel takes **`type`**, not `visibility` — `{"external_id":…,"type":"public"}`;
- **an application credential may send only as a bot user.** To author as a person, mint a
  token: `POST /auth/dev-token` with `{"user":"…"}`. Measured — the key's own send answers
  `sender_not_permitted`;
- **there is no `GET /v1/channels`.** Resolve a channel by creating one, or from the database;
- a history array is keyed by its own name — `messages` here, `edits` on the versions route —
  and a defaulting accessor over the wrong key reads as the platform dropping data;
- `psql -tAc` with `RETURNING` prints the value **and** the command tag;
- **`tr -d ' '` destroys a value that contains a space.** Chapter 4.18 wrote a corrupted row
  into an append-only table with its own cleanup step, because the idiom 4.11 added for a
  different column removed the space from `METHOD /path`. Quote the result instead;
- capture an exit code **outside** the pipeline, or `$?` is `tail`'s. Seven occurrences so far.

## 0 · Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
RELAY_POSTGRES_PORT=15432 docker compose --profile services build
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
export K=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs | tail -1)
export S=$(date +%s)
```

## 1 · MEASURED — the three texts, and the two you get back

```bash
export CH=$(curl -s -X POST "localhost:4000/v1/channels" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' \
  -d "{\"external_id\":\"qs-$S\",\"type\":\"public\",\"name\":\"Quickstart\"}" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

curl -s -X POST "localhost:4000/v1/users" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"users\":[{\"external_id\":\"qs-a-$S\"}]}" >/dev/null
curl -s -X POST "localhost:4000/v1/channels/$CH/members" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"user_ids\":[\"qs-a-$S\"]}" >/dev/null

export T=$(curl -s -X POST "localhost:4000/auth/dev-token" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"user\":\"qs-a-$S\"}" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')

export M=$(curl -s -X POST "localhost:4000/v1/channels/$CH/messages" -H "authorization: Bearer $T" \
  -H 'content-type: application/json' -d '{"text":"will be edited"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

curl -s -o /dev/null -X PATCH "localhost:4000/v1/channels/$CH/messages/$M" \
  -H "authorization: Bearer $T" -H 'content-type: application/json' -d '{"text":"edited once"}'
curl -s -o /dev/null -X PATCH "localhost:4000/v1/channels/$CH/messages/$M" \
  -H "authorization: Bearer $T" -H 'content-type: application/json' -d '{"text":"edited twice"}'

curl -s -o /dev/null -w "delete %{http_code}\n" -X DELETE \
  "localhost:4000/v1/channels/$CH/messages/$M" -H "authorization: Bearer $K"

curl -s "localhost:4000/v1/channels/$CH/messages/$M/edits" -H "authorization: Bearer $K" \
  | python3 -m json.tool
```

**Measured today**, before the chapter:

```
delete 204
{
    "edits": [
        { "prior_text": "will be edited", "edited_at": "2026-10-03T00:04:13.056Z" },
        { "prior_text": "edited once",    "edited_at": "2026-10-03T00:04:13.069Z" }
    ]
}
```

**Three texts existed and two come back.** `"edited twice"` — the text the message held when
the moderator removed it — is in no table:

```bash
docker compose exec -T postgres psql -U relay -d relay -At \
  -c "select coalesce(text,'<NULL>') from messages where id='$M'"
docker compose exec -T postgres psql -U relay -d relay -At \
  -c "select count(*) from message_edits where message_id='$M'"
```

**Measured**: `<NULL>` and `2`.

**After the chapter**: three entries, the last carrying `"ended_by": "deletion"`.

## 2 · MEASURED — what the key can and cannot already do

```bash
curl -s -o /dev/null -w "history, API key:    %{http_code}\n" \
  "localhost:4000/v1/channels/$CH/messages?limit=5" -H "authorization: Bearer $K"
curl -s -o /dev/null -w "edits,   API key:    %{http_code}\n" \
  "localhost:4000/v1/channels/$CH/messages/$M/edits" -H "authorization: Bearer $K"
curl -s -o /dev/null -w "edits,   user token: %{http_code}\n" \
  "localhost:4000/v1/channels/$CH/messages/$M/edits" -H "authorization: Bearer $T"
```

**Measured**: `200`, `200`, **`403`**.

So FR-MOD-01's *"via API key"* is already an access decision the platform makes, and FR-MOD-02
is already met — a tenant key deleted a message it did not author, above, and answered 204.
**Row 20's brief is substantially built**, which is what §7.5 of `docs/12` told this chapter to
check before writing it.

## 3 · The tombstone's instant, from history alone (after the chapter)

```bash
curl -s "localhost:4000/v1/channels/$CH/messages?limit=5" -H "authorization: Bearer $K" \
  | python3 -c '
import sys, json
for m in json.load(sys.stdin)["messages"]:
    print(f"seq={m[\"seq\"]:>3}  text={str(m[\"text\"])[:16]:18} deleted_at={m.get(\"deleted_at\")}")'
```

**Expected after the chapter**: the tombstone's row carries its removal instant and a live
message's carries `null`.

**Measured today**: the field is absent from every row — the `DELETE` response and the
`message.deleted` frame both carry it and history does not.

## 4 · The history cannot be rewritten (after the chapter)

```bash
docker compose exec -T postgres psql -U relay -d relay -v ON_ERROR_STOP=0 \
  -c "update message_edits set prior_text='tampered' where message_id='$M'"
docker compose exec -T postgres psql -U relay -d relay -v ON_ERROR_STOP=0 \
  -c "delete from message_edits where message_id='$M'"
docker compose exec -T postgres psql -U relay -d relay -At \
  -c "select count(*) from message_edits where message_id='$M'"
```

**Expected after the chapter**: two refusals, then `3`.

**Measured today**: the `UPDATE` is accepted. FR-MSG-07 says *"an immutable edit history"* and
there is no trigger on that table, where `audit_log` has carried one since chapter 4.18.

**Do not run this before the chapter without restoring the rows** — a red probe writes to the
lane, and this one would rewrite a history the next measurement reads. Take the values first
and compare after, and **quote them**: a prior text contains spaces and `tr -d ' '` would
write back a value nobody sent, which is exactly how chapter 4.18 corrupted a row in the table
it had just made append-only.

## 5 · And what this still cannot show

- **A message deleted before the chapter.** Its final text is gone and no migration recovers
  it. Try it on any tombstone the lane already holds: the count is the number of edits, not
  the number of texts.
- **Who ended a version.** The audit log says who deleted (chapter 4.18) and says nothing
  about edits, because a user editing their own message is not a moderation action.
- **What was attached.** FR-MED-10 unlinks a tombstone's attachments; the versions hold text.
- **How long any of it lasts.** Retention is row 21's and erasure is row 22's. Neither is
  built, and the same absent scheduler bounds both (ADR-28).

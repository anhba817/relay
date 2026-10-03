# Quickstart — chapter 4.20

Set a policy, backdate a message past it, run the sweep, and find the row gone.

**SECTIONS 0 AND 1 ARE MEASURED** — run against the current platform before the chapter, and
what they show is why it exists. **Everything after them is a prediction** until the phase-9
task runs this document start to finish and corrects it in place, recording each wrong version.
The last six chapters' quickstarts were wrong three, four, three, five, two and zero times.

The corrections earlier chapters earned are applied rather than rediscovered:

- the api is on **4000**, the gateway on **4001**;
- `docker compose --profile services stop` names its services and **`ingester` is not one**;
- a channel takes **`type`**, not `visibility`;
- **an application credential may send only as a bot user.** To author as a person, mint a
  token: `POST /auth/dev-token` with `{"user":"…"}`;
- **`python3 -c '…'` cannot carry a quote inside an f-string expression** — feed the program on
  stdin with a heredoc;
- `psql -tAc` with `RETURNING` prints the value **and** the command tag, and **`tr -d ' '`
  destroys a value containing a space** — quote the result instead;
- capture an exit code **outside** the pipeline, or `$?` is `tail`'s. Eight occurrences so far;
- **this document assumes one shell.** §2 onward use variables §1 exports, and running a later
  section in a fresh terminal fails in a way that looks like a platform defect.

## 0 · MEASURED — nothing on this lane is old enough to expire

```bash
docker compose exec -T postgres psql -U relay -d relay -t -A -F' | ' -c "
select 'oldest message', min(created_at)::text from messages
union all select 'older than 30 days', count(*)::text from messages where created_at < now() - interval '30 days';"
```

**Measured**: `2026-09-14` and `0`. FR-MOD-06's shortest policy is thirty days and **nothing
here is thirty days old**, so every section below backdates a fixture. The figure a reader
would most want — what a sweep removes from real traffic — cannot be measured on this lane.

## 1 · MEASURED — the hard delete is refused, and so is every obvious way round it

Run inside a transaction and rolled back, so the probe does not become the data.

```bash
docker compose exec -T postgres psql -U relay -d relay -v ON_ERROR_STOP=0 <<'SQL'
BEGIN;
DELETE FROM messages WHERE id = (SELECT message_id FROM message_edits LIMIT 1);
ROLLBACK;
BEGIN;
DELETE FROM message_edits WHERE message_id = (SELECT message_id FROM message_edits LIMIT 1);
ROLLBACK;
BEGIN;
DELETE FROM messages WHERE id = (SELECT m.id FROM messages m
  WHERE NOT EXISTS (SELECT 1 FROM message_edits e WHERE e.message_id = m.id) LIMIT 1);
ROLLBACK;
SQL
```

**Measured**, in order:

```
ERROR:  update or delete on table "messages" violates foreign key constraint
        "message_edits_message_id_fkey" on table "message_edits"
ERROR:  message versions are append-only (FR-MSG-07)
DELETE 1
```

**The first two are the pincer and the third is the control.** A message with no version row
deletes cleanly, so the foreign key is the only obstacle to the parent — and the trigger is the
only obstacle to clearing it. **5,495 messages are in that position today**, and chapter 4.19
made every deletion add one.

## 2 · Set a policy (after the chapter)

```bash
export K=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs | tail -1)
export ENV=$(docker compose exec -T postgres psql -U relay -d relay -t -A \
  -c "select environment_id from api_keys where credential_hash is not null limit 1")

curl -s -X PATCH "localhost:4000/v1/environments/$ENV" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d '{"retention_days":30}' | python3 -m json.tool
curl -s -o /dev/null -w "a value the clause does not offer: %{http_code}\n" \
  -X PATCH "localhost:4000/v1/environments/$ENV" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d '{"retention_days":45}'
```

**Expected after the chapter**: the first returns the environment with `retention_days: 30`;
the second answers **400**, because FR-MOD-06 enumerates four options and 45 is not a stricter
policy somebody chose.

## 3 · Backdate a message past the policy, and keep one inside it (after the chapter)

```bash
export CH=$(curl -s -X POST "localhost:4000/v1/channels" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d '{"external_id":"ret","type":"public","name":"Ret"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
# … mint a token, add a member, send two messages, edit one of them …

docker compose exec -T postgres psql -U relay -d relay -c \
  "UPDATE messages SET created_at = now() - interval '91 days' WHERE id = '$OLD'"
```

**BACKDATE EACH FIXTURE TO ITS OWN INSTANT.** Chapter 4.13's sweep fixture stepped by a second
and piled 3,235 rows on one instant, which turned twelve tests red in milliseconds and which CI
never sees, because a fresh database has no pile.

**And edit one of them**, so the sweep meets the case that is refused today rather than only
the one that was never hard.

## 4 · Run the sweep (after the chapter)

```bash
pnpm --filter @relay/api exec node dist/retention/sweep.js --dry-run
pnpm --filter @relay/api exec node dist/retention/sweep.js
pnpm --filter @relay/api exec node dist/retention/sweep.js
```

**Expected after the chapter**: the dry run counts and destroys nothing; the first real run
destroys the backdated message **and its version rows**; the second prints the same counted
line with zeroes, because the predicate is self-clearing.

**ASSERT THE COUNTED LINE, NOT THE EXIT CODE** (055-4). A sweep that found no environment with
a policy and a sweep that found nothing expired both exit 0, and they must not print the same
thing.

## 5 · And confirm what survived (after the chapter)

```bash
docker compose exec -T postgres psql -U relay -d relay -t -A -F' | ' -c "
select 'the expired message', count(*)::text from messages where id = '$OLD'
union all select 'its version rows', count(*)::text from message_edits where message_id = '$OLD'
union all select 'the message inside the policy', count(*)::text from messages where id = '$NEW'
union all select 'an UPDATE on a surviving version row still refused', 'see below';"

docker compose exec -T postgres psql -U relay -d relay -v ON_ERROR_STOP=0 \
  -c "update message_edits set prior_text='tampered' where message_id = '$NEW'"
```

**Expected after the chapter**: `0`, `0`, `1`, and the `UPDATE` **still refused**. The last one
is the point — the sweep widened the immutability guarantee by one named path and by nothing
else, and a quickstart that did not check the guarantee still held would be demonstrating only
the half that is convenient.

## 6 · And what this still cannot show

- **What a sweep costs on real data.** Nothing on this lane is thirty days old.
- **Whether a single run should be bounded.** A million expired rows is a different question
  and the corpus cannot inform it.
- **When expiry happens.** Nothing runs the sweep. That is the chapter's own subject, not a
  gap in the walkthrough.

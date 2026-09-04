# Quickstart — chapter 3.24, attachments

## The lane environment, pinned where the tasks can see it

Nine variables and one compose line, carried from chapter 3.23's `baseline.txt` and unchanged.
They apply to `pnpm coverage` as well as `test:integration` — chapter 3.22 spent two full lane
runs learning that.

    RELAY_POSTGRES_PORT=15432 docker compose up -d --wait

    DATABASE_URL=postgres://relay:relay@localhost:15432/relay
    RELAY_REDIS_URL=redis://localhost:6379
    RELAY_NATS_URL=nats://localhost:4222
    RELAY_INTERNAL_CREDENTIAL=rk_svc_local_development_credential_0000
    RELAY_INTERNAL_CREDENTIAL_GATEWAY=rk_svc_local_development_gateway_00000
    RELAY_WEBHOOK_SECRET_KEY=BpDal75yBZp7Fc2GtGS3D1vh7qOKgCWJkF6/d0XWxBU=
    RELAY_OUTBOX_RELAY=off
    RELAY_EVENT_CONSUMER=off
    RELAY_DELIVERY_RELAY=off

All local development values. Before a timing battery:
`RELAY_POSTGRES_PORT=15432 docker compose stop api gateway dispatcher`, and nothing else runs
on the machine — including your own tooling.

**VERIFY EVERY EXIT CODE INTO A VARIABLE, NEVER THROUGH A PIPE.** `pnpm -s check:x 2>&1 |
tail -3; echo $?` reads `tail`'s status. Chapter 3.23 hit that four times knowing about it.

**AND `connections.test.ts` NEEDS A RUNNING REDIS** despite being in the Docker-free lane —
chapter 3.23's `gaps.md` item 9. If `pnpm test` returns twelve failures about a connection cap
failing open, the stack is down, not the code.

## P1 — the reader test, before a line of production code

Plant a message with `text = ''` by hand and read it back through every path. **It must come
back as a live message today**, with no attachment support anywhere.

```
psql: INSERT INTO messages (id, channel_id, sequence, user_id, text, created_at)
      VALUES (gen_random_uuid(), :channel, :seq, :user, '', now());
```

**Expected**: history returns it, the listing previews it, resume replays it, and no path
mistakes it for a tombstone. This scenario validates no criterion — it validates the ground
every criterion stands on, which is why it runs first and against unchanged code.

**If it fails, the empty-string decision is wrong** and the plan changes before any code is
written. This is chapter 3.23's reader test in a new subject: written against unchanged code,
proving the ground the design stands on.

## P2 — the shape refuses what it should

```
pnpm --filter @relay/protocol test
```

**Expected** (SC-004): `javascript:alert(1)`, `data:image/png;base64,…`, `file:///etc/passwd` and
`vbscript:msgbox(1)` are all refused; `http://` and `https://` are accepted. **Run these
against the real validator rather than trusting `z.url()`** — R7 measured that it accepts
every one of them.

## P3 — a message carries a picture, end to end

With the stack up and the api built:

```
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --build --wait
export RELAY_DEMO_CREDENTIAL=$(node scripts/seed-demo-tenant.mjs)
export RELAY_API_URL=http://localhost:4000 RELAY_WS_URL=ws://localhost:4001
pnpm --filter @relay/outsider test:integration
```

**Expected** (SC-001): a message sent over REST with **two** attachments reaches an open socket
with both, in the order they were sent, and the history route returns the same two in the same
order. **Two, not one** — a single attachment cannot show an order, and the suite this command
runs asserts the order.

**`--build` IS NOT OPTIONAL.** `docker compose --profile services up -d --wait` reuses the
image, so a route or a field added since the last build is invisible and looks exactly like a
feature that does not work. Chapter 3.23 lost a debugging pass to that.

## P3a — the same message over a SOCKET, which is the door that drops it

Open a socket with a minted token, send `message.send` with two attachments, and watch a second
member's socket.

**Expected** (SC-001, the socket half): the message commits with both attachments in order, a
second member receives them
on `message.created`, and the sender's `message.ack` carries **only `seq`** — the ack has never
carried a message and this chapter does not widen it.

**THIS IS THE SCENARIO THE FIRST DRAFT OF THIS FILE DID NOT HAVE**, and it is the one that
matters. The socket path drops attachments at three named points unless every one is threaded —
`session.ts`'s inbound destructure, `internal.controller.ts`'s named call, and `session.ts`'s
outbound builder. **Every other scenario here walks the REST door**, which was never at risk.

## P3b — a photograph with no caption, and the same link twice

```
{"text": "", "attachments": [{"type":"url","kind":"image","url":"https://example.test/a.png"},
                             {"type":"url","kind":"image","url":"https://example.test/a.png"}]}
```

**Expected**: 201. An attachments-only message is accepted (FR-019) and stored with `text = ""`
rather than a null, so chapter 3.23's tombstone predicate is untouched. **The same URL twice is
two attachments** (FR-021) — nothing deduplicates.

**And the control**: `{"text": "", "attachments": []}` is refused (FR-019b). The bound relaxes
because there is something else to carry, not unconditionally.

## P4 — eleven is a refusal and nothing landed

```
curl -sS -X POST "$API/v1/channels/$CH/messages" -H "authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' \
  -d '{"text":"eleven","attachments":[…11 of them…]}' -o /dev/null -w '%{http_code}\n'
```

**Expected** (SC-002): `400`, a body naming `attachments`, and **`channels.last_sequence` unchanged**
afterwards — the second half is the assertion, because a 400 raised after the write passes the
first, and the sequence is the column chapter 2.2 made the authority.

## P5 — the tombstone forgets them

Send with attachments, delete, read history.

**Expected** (SC-003, one of its six read paths): the message is present in its original
position with `text: null` and
`attachments: []`. Chapter 3.23's deletion already nulls the column; this checks that the read
path turns the null into an empty list rather than an absent field.

## P6 — an edit leaves them alone

Send with two attachments, edit the text, read it back.

**Expected** (SC-006): the new text, the same two attachments, in the same order. **The failure this
catches is silent** — an `UPDATE … SET text = ?, attachments = ?` written without care drops
the photograph and returns 200.

## P7 — the client that was not there

Connect a member, note the last `seq` it saw, **disconnect it**, send a message with two
attachments from another member, then reconnect with `resume` from that `seq`.

```
pnpm --filter @relay/api test:integration -- backfill.itest.ts
```

**Expected** (SC-005): the replay carries the missed message with both attachments **in the
order they were sent**. The backfill is a different code path from delivery — it maps rows out
of the database rather than passing a payload along — so a field threaded correctly through
every live path can still be missing here.

**This scenario did not exist until analysis pass 13**, and SC-005 was the only criterion with
nothing a person could run. A reconnecting client is also the least convenient thing here to
check by hand, which is the usual reason a gap survives.

## Gates, and how to run them so they mean something

From `relay-tutorial`: `check:fences`, `check:docs`, `check:figures`, `check:srs`,
`check:errors`. From `relay-platform`: `typecheck`, `lint`, `build`, `test`.

`check:errors` reads the **built** `packages/protocol/dist/codes.js`, so build before believing
it — and it will be red on purpose from the phase that adds `media_not_available` until the
phase that writes its reference section.

# Contract — the surface the journey may touch

`packages/outsider` is sealed: it may not import workspace code. This file is the list of what
the journey is therefore allowed to use, and it is a contract in the useful direction — **if a
step is not on this list, the platform does not expose it, and the chapter records that rather
than reaching past the seal.**

Every entry was exercised by hand on 2026-10-01 (research R2).

## Routes

| method | path | body / params | expected |
|---|---|---|---|
| `POST` | `/v1/media` | `{filename, mime_type, bytes}` | `201 {media_id, state:"pending", upload_url, expires_at}` |
| `PUT` | the `upload_url` | the bytes | `200` |
| `POST` | `/v1/channels` | `{external_id, type}` | `201 {id, …}` |
| `POST` | `/v1/channels/{id}/messages` | `{text, user, idempotency_key, attachments:[{type:"media", media_id}]}` | `201`, attachment carries `state` |
| `GET` | `/v1/channels/{id}/messages?limit=N` | — | `200 {messages:[…], next_cursor, prev_cursor}` |
| `GET` | `/v1/media/{id}` | — | `200 {url, …}` when `ready` and referenced; a refusal otherwise |
| `GET` | the signed URL | — | `200`, the bytes |
| `POST` | `/auth/dev-token` | `{user, ttl_seconds}` | `200 {token, expires_at}` — the socket takes a user token, not the application credential |
| `POST` | `/v1/channels/{id}/members` | `{user_ids: ["ana"]}` | `200 {members:[{external_id, status}]}` |
| — | `${ws}/v1/ws?token={token}` | the WebSocket | frames arrive as JSON text: `connection.ack`, `message.created`, `presence.changed`, `media.updated` |

**THE THREE ROWS ABOVE WERE MISSING FROM THIS FILE UNTIL THE THIRD ANALYSIS PASS**, while T030a
needed all three — in a document whose rule is that an unlisted step is a step the platform does
not expose. A contract that omits what its own feature needs gets reached past rather than
amended.

**AND A SUBSCRIBER MUST BE A MEMBER, EVEN OF A PUBLIC CHANNEL.** Measured: without the members
call, a socket opened with a valid token received `connection.ack` and `presence.changed` and
**no `message.created` and no `media.updated`**. That is what made pass 2's third probe attempt
read like `media.updated` not existing — the subscriber was outside the channel and the absence
of every frame looked like the absence of one. With the member added, all four arrive.

**`messages`, not `data`.** The history response's array is keyed `messages`. Research R7
records the cost of assuming otherwise: a defaulting accessor turned a wrong key into what
looked like history dropping the attachment.

## Where the journey goes in the file

**The suite is nineteen sequentially-dependent tests over five `let`s declared at describe
scope** — `api`, `ws`, `credential`, `channelId`, `token` — and they are populated by named
earlier tests: the channel at the test on line 114, the token at 161, the bot at 168. The media
sequence sits at 408, after all of them.

- **The journey's tests go after the existing media sequence**, not above it. Inserted higher
  they fail on `undefined`, and the failure names a variable rather than a step.
- **The journey creates its own channel** rather than reusing `channelId`. The shared one
  accumulates messages from every test before it, so a history read against it would have to
  search rather than assert — and `items[0]` would be somebody else's message. Research's walk
  made a fresh channel, which is why its history held exactly one.

## Credentials

| name | what it is | where it comes from |
|---|---|---|
| `RELAY_DEMO_CREDENTIAL` | an **application** credential, so every send names a `user` | `node scripts/seed-demo-tenant.mjs`, last line |

**There is exactly one, and that is deliberate.** The seeder's own comment records why a second
would be worse than none: *"a second organisation called `demo` with a second key would leave two
credentials where the printed one is whichever the"* run wrote last. So the journey's recipient
is **a reader rather than a second party** — a socket subscriber on the same credential, or a
second read through history. Minting another credential would be product-adjacent work this
feature forbids itself.
| `RELAY_API_URL` | `http://localhost:4000` | CI's sealed job sets it |
| `RELAY_WS_URL` | `ws://localhost:4001` | CI's sealed job sets it |

`outside-bot` is the user the demo tenant has. `demo-bot` does not exist — 4.11's quickstart
correction, and the sealed suite already relies on it.

## What the journey may NOT do

- Import anything from `services/` or `packages/` other than its own helpers. The seal is
  mechanical and is the reason this suite's findings are worth anything.
- Read Postgres, ClickHouse or MinIO directly. A step that needs one is a step the platform does
  not expose; say so.
- Call `POST /internal/media/{id}/verdict`. That is the worker's route and calling it is the
  thing this chapter exists to stop doing.
- Mint a second credential, or change `scripts/seed-demo-tenant.mjs`. See above.
- Import anything from `@relay/*` or any workspace path, which is the rule. **Node builtins are
  not that** — `node:crypto` is already imported and `node:zlib` joins it.
- Shorten the sweep interval. 5,000 ms is a deployment property; the journey waits on a
  condition with a deadline.

## The fixture

| property | value | why |
|---|---|---|
| dimensions | **800 × 600** | must exceed **320 px** on its long edge, or `thumbnailOf` answers `within-bound` and no rendition is written (4.15) |
| bytes | **447,377** | measured; the same image every figure in `research.md` was taken with |
| how | generated with `node:zlib` inside the suite | 447,345 bytes of deflate cannot be a literal, and the existing 1×1 literal produces no thumbnail |
| imports it adds | `node:zlib` | a Node builtin is not a workspace path. The file's header sentence saying it imports nothing beyond `vitest` is already false and is corrected |

## Timing the journey must respect

| step | measured | the journey's deadline |
|---|---|---|
| slot | 8–34 ms | the suite's default |
| PUT | 5–7 ms | the suite's default |
| PUT → `ready` | **1,197–5,840 ms, p50 2,953**, over a 5,000 ms interval, 10 independent trials | a poll to a deadline comfortably above one interval, failing with a message that names the worker |

**THE WAIT IS UNIFORM OVER THE INTERVAL, NOT A CONSTANT.** An earlier figure of `p50 5,693 ms`
came from five runs in a loop, each starting just after the sweep that ended the one before —
**a loop that waits for the thing it is timing synchronises with it**. A journey that asserted
an elapsed time rather than a condition would have been tuned against the worst case.
| history, link, GET | < 20 ms each | the suite's default |

**Arrival is a condition and absence is not.** The wait for the verdict polls; any assertion that
nothing else arrived is taken after that wait, never instead of it.

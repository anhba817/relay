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

**`messages`, not `data`.** The history response's array is keyed `messages`. Research R7
records the cost of assuming otherwise: a defaulting accessor turned a wrong key into what
looked like history dropping the attachment.

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
- Shorten the sweep interval. 5,000 ms is a deployment property; the journey waits on a
  condition with a deadline.

## Timing the journey must respect

| step | measured | the journey's deadline |
|---|---|---|
| slot | 8–34 ms | the suite's default |
| PUT | 5–7 ms | the suite's default |
| PUT → `ready` | 5,656–6,143 ms, over a 5,000 ms interval | a poll to a deadline comfortably above one interval, failing with a message that names the worker |
| history, link, GET | < 20 ms each | the suite's default |

**Arrival is a condition and absence is not.** The wait for the verdict polls; any assertion that
nothing else arrived is taken after that wait, never instead of it.

# Quickstart — chapter 3.8

Twelve checks, V0 through V11. Read exit codes, not output. Where a step asserts a
number, the number comes from `contracts/limits.md`.

Prerequisites: `docker compose up -d --wait` from `relay-platform` — now five
services, Mailpit included, and it has a healthcheck so `--wait` means ready for it
too rather than merely running. `. env.sh` for the non-default ports the lane uses.

**Estimated wall clock: about 25 minutes.** No step runs the lane repeatedly —
this chapter has no intermittent defect whose rate needs measuring, which is the
only thing that justified chapter 3.7's twenty runs. Twenty-five minutes is a
guess and is labelled as one — 3.7's quickstart claimed three hours for a step that
took one, and that figure had been carried unmeasured from a chapter earlier still.

---

## V0 — Baseline, before anything changes

```bash
pnpm lint && pnpm typecheck && pnpm build
pnpm test && pnpm test:integration && pnpm coverage
```

Expected: exit 0 throughout, and the counts recorded — 198 unit, 191 integration,
380 coverage as chapter 3.7 left them.

**Record the lane's flake count too.** Chapter 3.7 found one pre-existing failure
at its baseline and four more during twenty runs, every one a test asserting a
local fact about a global operation. This chapter adds a global operation (a shared
counter) and a global side effect (a mail server), so the class is live. Three lane
runs, and any failure separated from this chapter's work before starting.

---

## V1 — Headers on a successful response

```bash
curl -si -H "Authorization: Bearer $KEY" $API/v1/channels/$CHANNEL/messages \
  -d '{"text":"one"}' | grep -i x-ratelimit
```

Expected: all three headers on the **200**, not only on a refusal.

```text
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 599
X-RateLimit-Reset: 1755590417
```

Send again and `Remaining` is 598. **This is the requirement most likely to be
built as an afterthought**, because a limiter that only speaks when it refuses
passes any test written from the 429.

**Which limit are those headers describing?** A `POST …/messages` decrements both the
request and the send limit; a socket `message.send` frame decrements the send limit
only. The headers report whichever has fewer remaining (research R11).

**Mix the transports — that is the only shape that tells the two apart.** Five sends
over REST and five frames over the socket leave the send limit at 10 and the request
limit at 5, and the headers follow the send limit from then on. On one transport alone
the two counters move together and a limiter counting requests is indistinguishable
from one counting messages. There is no batch send on either transport: one operation,
one message.

---

## V2 — The refusal, and that honouring it is sufficient

Drive one environment past its allowance, then read the refusal and obey it.

Expected: `429`, `Retry-After: N`, `X-RateLimit-Remaining: 0`, and a body with
**four** fields — `code`, `message`, `docs_url`, `request_id`. The `message` names
*which* limit was reached: "too many requests" and "too many messages" are
different problems, one saying batch and the other saying slow down.

Then wait N seconds and send again: it succeeds.

**The second half is the check that matters.** A `Retry-After` a client can honour
and still be refused is worse than no header, because it turns a backoff into a
loop. Assert the recovery, not the refusal.

---

## V3 — The fourth field, everywhere

```bash
curl -s $API/v1/nope | python3 -m json.tool
curl -s -H "Authorization: Bearer wrong" $API/v1/channels | python3 -m json.tool
```

Expected: `request_id` present on the 404 and the 401, not only on the 429.

It has been absent since chapter 1.3, above a comment in
`packages/protocol/src/frames.ts` promising it would arrive "in Part 2, when a
gateway exists to mint one". A gateway exists. Constitution V asks for four fields
and the platform has been sending three for twenty-two chapters.

---

## V4 — Two environments, independent

Drive the development environment of one application to its limit. Then send
through the production environment of the **same** application.

Expected: the second request succeeds with a full allowance.

FR-RTL-04 exists because load-testing a dev environment must not throttle
production. A single shared counter would be a cross-tenant fault of a new kind —
one tenant's traffic refusing another's — which constitution I forbids as
correctness, not as courtesy.

---

## V5 — Each operation is counted once, at the door it entered

Drive an environment to its REST limit, then:

1. have the dispatcher report a delivery outcome over `/internal/dispatch/*` →
   **succeeds**;
2. open a socket and send a frame → **both succeed**;
3. `curl /healthz` → **answers**.

Step 2 is the one that matters and the one an exemption written from the documents
misses. The gateway forwards the **end user's** token on `/internal/session`,
`/internal/backfill` and `/internal/messages`, so its calls resolve to `kind: "user"`
with the client's environment — a rule that exempted only the platform principal would
refuse them, and a socket send would cost two slots while the contract advertises one.

Step 1: throttling the dispatcher turns one busy customer's webhook backlog into a
stall for every customer, the failure FR-WHK-05 forbids. Step 3: Docker polls health
every five seconds and `up -d --wait` depends on the answer.

---

## V6 — Both failure directions, in one outage

```bash
docker compose stop redis
```

With Redis down, in this order:

1. Send a message as a customer → **served**, not refused. `X-RateLimit-Limit`
   present; `Remaining` and `Reset` **absent** (not `-1`).
2. Submit failed authentication attempts past the threshold from one address →
   **still refused**.
2a. Confirm the refusal comes from `CredentialGuard` and not from
   `AuthenticateMiddleware` — the middleware never throws, by documented design, so
   pre-credential routes still reach their handlers while over the threshold.
2b. Submit failed handshakes from ten different client addresses through the
   gateway → counted as **ten addresses**, not as ten failures by the gateway. The
   api sees the gateway's address unless the client's is forwarded, and one shared
   counter means one attacker refuses everybody (FR-039).
3. Check the logs → one line naming the degradation, carrying no credential, and
   **rate-limited** rather than one line per request.

```bash
docker compose start redis
```

4. Send again → counting has resumed with no operator action.

**This is the chapter.** A limiter that fails closed makes a Redis restart a
platform outage. One that fails open everywhere makes it a free brute-force window.
Same code, opposite answers, and the difference is what is on the other side of the
limit: Relay's capacity in one case, a customer's account in the other.

Step 3's rate-limiting is not fussiness. A Redis outage under load emits one log
line per request otherwise, which is how one outage becomes two.

---

## V7 — The gateway's two limits

**Establishment.** Open connections past the connect allowance for one environment.

Expected: an HTTP `429` with `Retry-After` **during the upgrade** — no WebSocket is
created — and every already-open socket unaffected.

**Frames.** On an open connection, send frames above the send allowance.

Expected: an `error` frame carrying `rate_limited`, and the **connection stays
open**.

**A configured limit, not the default.** Set the environment's
`connect_limit_per_minute` to 2 and confirm the socket honours it. The gateway has
no database — the limits arrive on the authentication response it already makes —
so this is the step that proves FR-037 rather than assuming the default path works.
Then change the limit while a connection is open and confirm it does **not** apply
until that connection reconnects: the property research R12 accepted, checked so it
is a documented consequence rather than a surprise.

Three things to check that are easy to get wrong:

- `rate_limited` has existed unused in `packages/protocol/src/codes.ts` since
  chapter 1.3. This is the first code that emits it.
- Close code `4008` is **still** unused. It reads "quota exhausted" and there is no
  quota yet. Using it because it was there would collapse the distinction the
  chapter is built on. Confirm nothing sends it.
- Every `error` frame carries a `request_id`. The gateway minted no ids before this
  chapter, so this is a new field with a new source rather than a rename.

---

## V8 — Nothing was lost

```bash
pnpm test && pnpm test:integration && pnpm coverage
```

Expected: exit 0, every pre-existing suite passing unchanged in substance, every
ratchet intact and the new files' ratchets set.

**And both lanes must TERMINATE.** Two services gain a Redis client, and an `ioredis`
client holds the event loop open. Three api modules already close their long-lived
resources through `OnModuleDestroy`; the gateway's fanout has an explicit `close()`. A
suite whose assertions pass and whose process never exits is the worst shape available —
green tests, and a lane that hangs (SC-013, research R20).

`pnpm lint` also refuses an `ioredis` import from outside the one module permitted to
hold one, the way it already refuses `pg` outside `services/api/src/db` (FR-042).

**The direction that matters here is the opposite of chapter 3.7's.** That chapter
suppressed frames, so its risk was a gap. This one refuses requests, so its risk is
refusing something it should have served — and the two limiters have different
right answers when they break. `bucket.ts` and `fallback.ts` are pure and should
reach 100% branches; if they do not, the missing branch is a case the tests have
not thought of.

---

## V9 — The email that closes 3.6's debt

Drive an endpoint to automatic disablement, then:

```bash
curl -s "${RELAY_MAILPIT_URL:-http://localhost:18025}/api/v1/messages" | python3 -m json.tool
```

Expected, read from the message Mailpit **received** rather than from what the
sender passed:

- one message to the organisation's owners and admins;
- naming the endpoint, the disablement time, the failure run, and the last status;
- containing **no signing secret, no API key, no credential** (FR-021);
- and the row's `delivered_at` set only after Mailpit accepted it.

Then the three cases that are branches rather than decoration:

```bash
docker compose stop mailpit
```

- a send that fails leaves `delivered_at` null and the obligation claimable;
- message delivery, the API and webhook dispatch are all unaffected (FR-024);
- an organisation whose admins all have `humans.email` null is **not** marked
  delivered, and says so — the column is nullable, so this is a real case.

**And the backlog.** The rows chapter 3.6 accumulated with `delivered_at` null
drain on the first run. They need no special handling: they are undelivered work by
the claim predicate's own definition, which is what makes this the outbox pattern's
third instance rather than a new mechanism.

---

## V10 — The sabotage check

Five mutations, each applied to the real code, each reverted with the file verified
byte-identical afterwards.

| Mutation | Must fail |
|---|---|
| never set the headers on a 2xx response | V1 — the requirement an afterthought passes |
| share one counter across environments | V4 — two environments stop being independent |
| **make the auth limiter fail open** | **V6 step 2** — the brute-force window opens |
| mark `delivered_at` before the send returns | V9 — a failed send loses its obligation |
| exempt nothing from the limiter | V5 — the internal seam gets throttled |

**The third is the one that matters and the one most likely to be skipped.** Its
mechanism is a *prohibition*: the auth limiter must not fail open, and the code that
implements it is a fallback path with no line saying "do not fail open". Chapter 3.7
shipped its central decision — never retire the mark — with no test behind it until
a mutation said so, and its own out-of-order test turned out to have never
exercised the mechanism it was named for.

**Commit before running the battery.** Its revert step is `git checkout --`, which
silently discarded an uncommitted fix during chapter 3.6 and failed the
byte-identical check against the previous run's hashes.

---

## V11 — The cross-reference sweep

```bash
grep -rn "chapter 3\.[89]\|Chapter 3\.[89]\|chapter 3\.10\|Chapter 3\.10" \
     docs/ relay-tutorial/app/ relay-platform/services/*/src relay-platform/scripts
```

Expected: quotas is 3.9 and the gauntlet is 3.10 in `docs/`, in the site registry
and in prose in both locales; and **zero** forward references in live source under
`services/*/src` or `scripts/`.

The rule is about forward references, not chapter numbers. "Chapter 3.6 added this
field" stays true for ever because chapters do not renumber backwards. "Chapter 3.9
needs this for quotas" goes stale on the next insertion, and it lives in a file
fenced byte-exact into a published chapter.

**This renumbering cost no fence amendment**, which is the first evidence that
chapter 3.7's rule paid for itself — 3.7's own renumbering needed two post-series
amendments and a section of prose explaining a comment that had already been stale
for a chapter.

---

## Definition of done

- V0's baseline recorded, including the flake count, **before** anything changed.
- V6 demonstrated in a single outage: served for tenants, refused for auth.
- Close code 4008 confirmed still unused, and the chapter says why.
- The `request_id` field present on every error response, not only the 429.
- 3.6's notification backlog drained, and the contents read from the receiver.
- Every number in the chapter from a real run.
- **The prose word count measured while the transport is still liftable.** Research
  R10 estimates 35 fences — 28 of them the limiter half alone — against a
  2,000–4,000 word bound; 3.5 shipped 39 against
  an estimate of 22 and 3.6 ran 5,273 words. If the count runs over, the transport
  becomes its own chapter — which the phase order is arranged to allow, and which
  is a decision to take with the number in hand.

# Quickstart — validating 043

Every scenario below is runnable and each one maps to a success criterion. None of them
requires reading the implementation.

## Prerequisites

The compose stack, on the ports this repository pins:

    cd relay-platform
    RELAY_POSTGRES_PORT=15432 docker compose up -d --wait

The lane's environment, which every command below assumes:

    export DATABASE_URL=postgres://relay:relay@localhost:15432/relay
    export RELAY_REDIS_URL=redis://localhost:6379
    export RELAY_NATS_URL=nats://localhost:4222
    export RELAY_INTERNAL_CREDENTIAL=rk_svc_local_development_credential_0000
    export RELAY_INTERNAL_CREDENTIAL_GATEWAY=rk_svc_local_development_gateway_00000
    export RELAY_WEBHOOK_SECRET_KEY=BpDal75yBZp7Fc2GtGS3D1vh7qOKgCWJkF6/d0XWxBU=

These are local development values, pinned here since chapter 3.24's `quickstart.md`, and
they are in the record deliberately.

**Build before anything that spawns a child.** Consumers resolve `@relay/protocol` through
`dist`, so a protocol change is invisible to a spawned service until `pnpm build` runs.

---

## Scenario 1 — the lane is trustworthy (SC-001, SC-002, SC-003, SC-012)

**Start from a cleared lane, and clear it with the command this feature adds:**

    node scripts/reset-lane.mjs
    rm -rf packages/*/node_modules/.vite/vitest services/*/node_modules/.vite/vitest

The second line is not optional and it is the subtle half. The test runner stores
`{duration, failed}` per file and runs previously-failed files first, so the file order —
and therefore the result — depends on how the last run ended. Chapter 3.24's battery
alternated green and red for fifteen consecutive runs because of it.

**Then twenty runs:**

    for i in $(seq 1 20); do pnpm -s test:integration >/tmp/run-$i.log 2>&1; echo "$i $?"; done

**Expected** (SC-001): twenty zeros.

**Failing means** something specific, and the signature changed with the feature. The e2e lane
no longer holds 4100–4102; it binds port 0 and reads the assignment back. So:

- an `ECONNREFUSED` or `EADDRINUSE` against **4100, 4101 or 4102** means the harness change did
  not take — a child is still being handed a fixed port from somewhere.
- an `EADDRINUSE` on a port in **4310–5600** is the gateway and dispatcher lanes' own map, not
  this feature's; `services/gateway/src/limits.itest.ts` carries that map and the known overlap
  inside it.
- a health check that passes and a later request that is refused is the **old** teardown defect
  and means `stop()` is still returning before its children have exited.

**Then the container-free lane, with nothing running:**

    docker compose down
    pnpm -s test

**Expected** (SC-002): exit 0. Today this reports twelve failures that are correct behaviour — the
connection cap failing open because it cannot reach Redis.

**Then the broker, before and after one run:**

    node scripts/stream-info.mjs

**Expected** (SC-003): no durable consumer outlives the run. Ones a service creates in normal operation
are not test debris and are counted separately.

**Then the budget** (SC-012). Read the `@relay/e2e` duration line and the run's total against
what was recorded before the change:

    grep -h "Duration" /tmp/run-1.log | grep e2e

**Expected** (SC-012): the integration total inside 240 s. **Failing means a decision, not a retry** —
raise the budget with this measurement attached, boot once instead of twice in
`harness.itest.ts`, or bound the teardown wait lower. The budget does not move to match
whatever the lane now costs.

---

## Scenario 2 — one message-length rule, three doors (SC-004)

Send the same over-long text three ways and compare the refusals.

    # REST
    curl -s -X POST "$API/v1/channels/$CHANNEL/messages" \
      -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
      -d "{\"idempotency_key\":\"$(uuidgen)\",\"text\":\"$(head -c 9000 /dev/zero | tr '\0' 'a')\"}"

    # socket — send the same payload as a message.send frame
    # internal — the door the gateway uses, same body shape

**Expected** (SC-004): all three refuse. The socket refusal carries `field` and arrives without an
internal request being made.

**And the definition is single:**

    grep -rn "8000\|8_000" packages/protocol/src services/api/src --include=*.ts | grep -v test

**Expected** (SC-004): exactly one `export const MESSAGE_TEXT_MAX = 8000`, and no other
`8000` that is a length bound.

**Two hits are not bounds and the grep cannot tell**: a sentence in `frames.ts`'s own
comment explaining what was fixed, and `isolation/fixtures.ts:109`, which builds a UUID
whose variant nibble happens to be `8000`. Read the hits; do not count them. A grep that
is expected to return exactly one line is a grep somebody will "fix" by tightening the
pattern until it does.

The definition's consumers are the thing to check, and there are **four** — the socket
door, the internal door, the REST send body and the edit body:

    grep -rn "MESSAGE_TEXT_MAX" packages/protocol/src services/api/src --include=*.ts

---

## Scenario 3 — an avatar URL cannot carry an executable scheme (SC-005)

    for s in "javascript:alert(1)" "data:text/html,x" "file:///etc/passwd" "vbscript:x" "https://ok.example/a.png"; do
      curl -s -o /dev/null -w "$s -> %{http_code}\n" -X PATCH "$API/v1/users/$USER" \
        -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
        -d "{\"avatar_url\":\"$s\"}"
    done

**Expected** (SC-005): `400` for the first four, `200` for the last. Each refusal names
`avatar_url` in the body's `field`.

**This said `422` until it was run, and `400` is the right answer.** The scheme rule lives in
`users.schema.ts`, so a bad scheme fails schema validation — which is `invalid_request`, a
400, exactly like every other malformed field on this API. 422 is what US3's webhook
refusals use, and those are different: the body is well-formed and the request is
semantically unprocessable. Writing `422` here would have made the avatar refusal the only
schema violation in the platform with its own status.

`ProtocolErrorFilter` derives `invalid_request` from 400 directly, which is why this needs
no new error code while the webhook cases each need one.

**The stored population, recorded before shipping** (FR-013):

    psql -Atc "select coalesce(split_part(avatar_url,':',1),'(null)'), count(*) from users group by 1"

---

## Scenario 4 — a customer's mistake is labelled as theirs (SC-006)

Read the **code**, not the status. That is the whole point: the status has been right all
along.

    curl -s -X POST "$API/v1/webhooks/endpoints" -H "authorization: Bearer $CREDENTIAL" \
      -H 'content-type: application/json' -d '{"url":"not-a-url","event_types":["message.created"]}' | jq .code

**Expected** (SC-006): a code naming the cause. **Failing means** `internal_error`, which is what all
five of these return today.

Repeat for: a non-HTTPS URL, a private address, an empty `event_types`, and one endpoint past
the limit.

---

## Scenario 5 — subscriptions are checked, and the declared ones survive (SC-008)

    # a misspelling — refused
    …-d '{"url":"https://e.example/h","event_types":["mesage.updated"]}' | jq '.code, .message'

    # declared but not yet emitted — accepted, and it says so
    …-d '{"url":"https://e.example/h","event_types":["channel.created"]}' | jq '.'

**Expected** (SC-008): the first is `422` naming the accepted set. The second succeeds and says the
type is not emitted yet.

**This is the scenario most likely to be got wrong**, because the obvious implementation —
comparing against `OUTBOX_EVENT_TYPES` — passes the first case and fails the second. 741
stored subscriptions name `channel.created`. See `contracts/rest-webhook-endpoints.md`.

    psql -Atc "select t, count(*) from webhook_endpoints, lateral jsonb_array_elements_text(event_types) t group by 1 order by 2 desc"

---

## Scenario 6 — every close code has a page (SC-007)

    cd ../relay-tutorial && pnpm -s check:errors

**Expected** (SC-007): exit 0, and the run reports the close-code comparison as well as the error-code
one.

**Test the gate red before believing it.** Remove one close code's text from
`docs/08-error-reference.md` and re-run; it must fail. A gate that has never failed has an
unverified class list.

Do not document a close code under a `## ` heading — that fails the existing orphan check.
See `contracts/close-codes.md`.

---

## Scenario 7 — the records read true (SC-009, SC-010, SC-011, SC-013)

    cd relay-tutorial && pnpm -s check:docs

**Expected** (SC-009, SC-011): the revision-order gate passes. Then break it deliberately — move version 1.5
above 1.4 in `docs/04-srs.md` — and confirm it fails.

**Read, by a person, not by a checker:**

- The review's bot/quota paragraph against `assertWithinQuota`. The message hard cap throws
  before the sender test.
- FR-RTM-10 against ADR-20's stated bound, and FR-RTM-09 against ADR-23's fail-open
  behaviour. Each amended clause must describe what the platform does and no more (FR-025c).

**Expected** (SC-010): every statement in the review matches the code or document it cites.
**A criterion nothing can automate still needs a stated expectation** — otherwise the reader
knows what to read and not what would count as wrong.

**Then the review itself** (SC-013). Open
`docs/09-platform-implementation-review-2026-09-03.md` and count the rows carrying an outcome.

**Expected** (SC-013): twenty-one — ten current findings, three roadmap rows, and eight in "Part 3
SRS/SAD/ADR amendment assessment". Each says closed and by what, or open and whose.

**No checker can do any of this.** Every gate in this repository compares bytes.

---

## The full gate set, at the end

Fourteen commands, and the last chapter tagged a tree that failed one of them because its
list said eleven:

    cd relay-platform  && pnpm -s typecheck && pnpm -s lint && pnpm -s build
    cd ../relay-tutorial && for g in check:fences check:docs check:figures check:srs check:errors; do pnpm -s "$g"; echo "$g $?"; done

Capture each exit code into a variable. Do not assign inside a pipeline — bash runs it in a
subshell and the assignment dies there, which is how chapter 3.24 printed "ALL GATES: GREEN"
over a red one.

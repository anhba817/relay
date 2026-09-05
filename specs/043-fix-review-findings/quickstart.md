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

**Expected**: twenty zeros.

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

**Expected**: exit 0. Today this reports twelve failures that are correct behaviour — the
connection cap failing open because it cannot reach Redis.

**Then the broker, before and after one run:**

    node scripts/stream-info.mjs

**Expected**: no durable consumer outlives the run. Ones a service creates in normal operation
are not test debris and are counted separately.

**Then the budget** (SC-012). Read the `@relay/e2e` duration line and the run's total against
what was recorded before the change:

    grep -h "Duration" /tmp/run-1.log | grep e2e

**Expected**: the integration total inside 240 s. **Failing means a decision, not a retry** —
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

**Expected**: all three refuse. The socket refusal carries `field` and arrives without an
internal request being made.

**And the definition is single:**

    grep -rn "8000\|8_000" packages/protocol/src services/api/src --include=*.ts | grep -v test

**Expected**: one definition and three imports, not three literals.

---

## Scenario 3 — an avatar URL cannot carry an executable scheme (SC-005)

    for s in "javascript:alert(1)" "data:text/html,x" "file:///etc/passwd" "vbscript:x" "https://ok.example/a.png"; do
      curl -s -o /dev/null -w "$s -> %{http_code}\n" -X PATCH "$API/v1/users/$USER" \
        -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
        -d "{\"avatar_url\":\"$s\"}"
    done

**Expected**: `422` for the first four, `200` for the last. Each refusal names `avatar_url`.

**The stored population, recorded before shipping** (FR-013):

    psql -Atc "select coalesce(split_part(avatar_url,':',1),'(null)'), count(*) from users group by 1"

---

## Scenario 4 — a customer's mistake is labelled as theirs (SC-006)

Read the **code**, not the status. That is the whole point: the status has been right all
along.

    curl -s -X POST "$API/v1/webhooks/endpoints" -H "authorization: Bearer $CREDENTIAL" \
      -H 'content-type: application/json' -d '{"url":"not-a-url","event_types":["message.created"]}' | jq .code

**Expected**: a code naming the cause. **Failing means** `internal_error`, which is what all
five of these return today.

Repeat for: a non-HTTPS URL, a private address, an empty `event_types`, and one endpoint past
the limit.

---

## Scenario 5 — subscriptions are checked, and the declared ones survive (SC-008)

    # a misspelling — refused
    …-d '{"url":"https://e.example/h","event_types":["mesage.updated"]}' | jq '.code, .message'

    # declared but not yet emitted — accepted, and it says so
    …-d '{"url":"https://e.example/h","event_types":["channel.created"]}' | jq '.'

**Expected**: the first is `422` naming the accepted set. The second succeeds and says the
type is not emitted yet.

**This is the scenario most likely to be got wrong**, because the obvious implementation —
comparing against `OUTBOX_EVENT_TYPES` — passes the first case and fails the second. 741
stored subscriptions name `channel.created`. See `contracts/rest-webhook-endpoints.md`.

    psql -Atc "select t, count(*) from webhook_endpoints, lateral jsonb_array_elements_text(event_types) t group by 1 order by 2 desc"

---

## Scenario 6 — every close code has a page (SC-007)

    cd ../relay-tutorial && pnpm -s check:errors

**Expected**: exit 0, and the run reports the close-code comparison as well as the error-code
one.

**Test the gate red before believing it.** Remove one close code's text from
`docs/08-error-reference.md` and re-run; it must fail. A gate that has never failed has an
unverified class list.

Do not document a close code under a `## ` heading — that fails the existing orphan check.
See `contracts/close-codes.md`.

---

## Scenario 7 — the records read true (SC-009, SC-010, SC-011, SC-013)

    cd relay-tutorial && pnpm -s check:docs

**Expected**: the revision-order gate passes. Then break it deliberately — move version 1.5
above 1.4 in `docs/04-srs.md` — and confirm it fails.

**Read, by a person, not by a checker:**

- The review's bot/quota paragraph against `assertWithinQuota`. The message hard cap throws
  before the sender test.
- FR-RTM-10 against ADR-20's stated bound, and FR-RTM-09 against ADR-23's fail-open
  behaviour. Each amended clause must describe what the platform does and no more (FR-025c).

**Then the review itself** (SC-013). Open
`docs/09-platform-implementation-review-2026-09-03.md` and count the rows carrying an outcome.

**Expected**: twenty-one — ten current findings, three roadmap rows, and eight in "Part 3
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

# Contract — webhook endpoint create and update

## What changes

Two things. Refusals stop claiming Relay failed, and `event_types` is validated against the
set FR-WHK-02 declares.

## Before — the refusals

Five call sites throw a bare `UnprocessableEntityException`: malformed URL, non-HTTPS,
private address, endpoint-count limit, and empty event set. `ProtocolErrorFilter` derives a
code from 400/401/403/404 and answers `internal_error` for everything else, so each one
reaches the customer as:

    422  {"code": "internal_error", "docs_url": "…#internal_error", …}

The message is right and the code says the platform broke. `webhooks.itest.ts:90` asserts the
status and that the body contains the limit — never the code, which is why nothing has caught
it since chapter 3.5.

## After — the refusals

| Cause | Code |
|---|---|
| URL is not a valid absolute URL | names the cause |
| URL is not HTTPS | names the cause |
| URL resolves to a private address | names the cause |
| endpoint count limit reached | names the cause |
| `event_types` is empty | names the cause |

Each new code gets a section in `docs/08-error-reference.md` reachable from its `docs_url`,
which is constitution V's requirement and NFR-USE-05's.

## Before — `event_types`

`assertEventTypes` checks `Array.isArray(types) && types.length > 0` and nothing else. A
subscription to `mesage.updated` returns 201 and produces an endpoint that never fires.

## After — `event_types`

Validated against the types **FR-WHK-02 declares**, not the types the platform emits.

| Case | Response |
|---|---|
| every type is declared and emitted | `201` / `200`, unchanged |
| a type is declared but not yet emitted | accepted, and the response says the type is not emitted yet |
| a type is not declared | `422` naming the accepted set |
| the list is empty | `422`, as before, now with a code |

**The declared-but-unemitted case is why this is not a one-line `includes`.** Both the review
and `gaps.md` 3.23-1 recommend comparing against `OUTBOX_EVENT_TYPES`, which holds the five
the platform emits. FR-WHK-02 declares eight, and **741 stored subscriptions name
`channel.created`** — declared, not built. Those customers subscribed to something the
requirements publish, and refusing them would make the platform's own backlog into their
error.

## Existing rows

Measured across all **32,606** event-type rows stored today, in four distinct types:

    message.created   31,757        channel.created     741   declared, not emitted
    message.deleted        54        message.updated      54

**Every type any customer has subscribed to is one FR-WHK-02 declares.** So the rule above
refuses **nothing** that exists, and the rule the review recommends refuses **741 — 2.3% of
stored subscriptions**. That comparison is what changed this contract; the 741 on its own is a
fact with nothing to compare it to. No row is rewritten under either.

## Verification

Subscribe to a misspelling and get a refusal naming the accepted set. Subscribe to
`channel.created` and get an acceptance that says it is not emitted yet. Read the code, not
the status, in every assertion.

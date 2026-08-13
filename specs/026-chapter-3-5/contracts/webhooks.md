# Phase 1 — Contracts: Chapter 3.5, the outward contract

Chapter 3.3 promised what the platform emits. Chapter 3.4 specified what a consumer
inside the platform may assume. This is the first contract addressed to code the
platform did not write and cannot read.

That changes the standard. A REST endpoint's consumer can retry against a sandbox
and read an error message. A webhook's consumer finds out at 3 a.m. that their
signature check has been wrong for a week. **Anything left unstated here becomes a
support ticket**, so this document states more than feels necessary.

---

## Managing endpoints

A tenant-facing surface, on the API service, behind the same credential model as
every other public route (chapter 3.2).

| Operation | Rule |
|---|---|
| Create | up to five per environment (FR-WHK-01); URL validated (research R9); the secret is returned **once** and never again |
| List | never includes secrets, in any form |
| Rotate secret | returns the new secret once; the previous one stays valid for a stated window |
| Enable / disable | an owner can pause an endpoint; a disabled endpoint receives nothing |
| Delete | **soft.** The endpoint stops receiving deliveries and stops appearing in listings; in-flight deliveries stop. The row survives, because its dead letters must (FR-WHK-04's seven days) and because chapter 3.2 already argued that a deleted row loses the record of what once had access |

**Errors name the limit, not the failure.** Exceeding five endpoints returns an
error that says five — chapter 3.2's lesson about error messages that name the
mistake, applied to a limit rather than a credential.

**Tenant isolation is a correctness property here as everywhere** (constitution I).
No environment may observe or affect another's endpoints, and these routes join
chapter 3.7's gauntlet.

---

## The delivery

```
POST <the endpoint's URL>
Content-Type: application/json
<signature headers — below>

<the chapter 3.3 event envelope, unchanged>
```

The body is the envelope chapter 3.3 defined: `id`, `type`, `environment_id`,
`occurred_at`, `data`. Not a new shape. A webhook that invented its own payload
would make the event spine's contract a fiction at the only hop a customer sees.

### Signature headers

| Header | Carries |
|---|---|
| timestamp | when the delivery was signed |
| signature | HMAC-SHA256 over the canonical string, hex |
| scheme version | so a future algorithm is additive rather than breaking |

**The canonical string is the timestamp and the raw request body**, joined by a
stated separator. Exact construction is specified in the chapter and must be
reproducible by a recipient with nothing but the request and the shared secret.

### Verifying — the recipe, and the way it goes wrong

1. Read the raw body **as bytes, before any JSON parsing**.
2. Rebuild the canonical string from the timestamp header and those bytes.
3. Compute HMAC-SHA256 with the shared secret.
4. Compare in **constant time**.
5. Reject deliveries whose timestamp is older than a tolerance you choose.

> **The mistake almost every first integration makes**: parsing the JSON and
> re-serialising it before verifying. Key order and whitespace change, the bytes
> change, and the signature does not match — while the payload looks identical in a
> log. The chapter must show this failing, not merely warn about it.

### Rotation

During a rotation window the endpoint has two valid secrets, and a delivery carries
**one signature per valid secret**. A recipient that accepts either is correct
throughout the window; one that accepts only the newest is correct after it.

**The window is 24 hours.** Long enough that a customer can roll a configuration
change across their fleet without a deploy window becoming an outage; short enough
that a secret they rotated *because it leaked* stops working the same day. Rotation
is the operation people perform under pressure, so the number is fixed here rather
than left to the implementation — it is a promise a recipient writes code against,
not a tuning parameter.

---

## Delivery semantics — what is promised, and what is not

| Property | Value |
|---|---|
| Delivery | **at-least-once** |
| Duplicates | **possible, and the customer's job to absorb** — deduplicate on the envelope's `id` |
| Ordering | **not guaranteed**, and never was (3.3's relay, unchanged) |
| Attempts | **seven** — an immediate delivery plus six retries at 1 s, 5 s, 30 s, 5 min, 30 min and 2 h (FR-WHK-03). The schedule spans about 2 h 36 min, so a customer has most of a working day's outage to notice and fix before their events stop being retried |
| After the last attempt | dead-lettered, retained seven days, replayable |
| Timeout | each attempt abandoned after a stated deadline |
| Isolation | one slow endpoint does not delay others, and none of it delays end users (FR-WHK-05) |

**Why at-least-once, said plainly**: an HTTP request that times out may still have
been received and acted upon. The platform cannot know. Given a choice between a
duplicate the customer can detect and a loss they cannot, the platform sends the
duplicate — and hands over the identifier that makes it harmless.

**A customer that does not deduplicate on `id` is incorrect**, and no amount of
care in the dispatcher makes them correct. This is ADR-06's system-wide consumer
discipline arriving at a consumer the platform does not control, which is why it
must be documentation rather than code.

**What orders what**: `data.seq` orders messages within a channel (FR-MSG-03,
ADR-03). Webhook arrival order is not that guarantee and must not be used as one.

---

## What the platform can and cannot tell about your endpoint

| The platform believes | Because |
|---|---|
| a 2xx means you received it | it is the only signal HTTP gives |
| anything else means retry | including a timeout, which may mean you did receive it |

**A customer who returns 200 and then fails internally has been delivered to**, as
far as the platform is concerned. Stating this prevents the support conversation
where the platform is asked to be responsible for what happened after the response.

---

## Explicitly not in this chapter

Named with owners, so the contract does not imply a story it has not written.

| Not built | Owner |
|---|---|
| A queryable log of every attempt, with status and latency (FR-WHK-06) | the follow-on chapter |
| Automatic disabling of a continuously failing endpoint (FR-WHK-07) | the follow-on chapter |
| Email notification when an endpoint is disabled | deferred, unowned — FR-RTL-07 needs it too |
| Dashboard inspection and replay of dead letters | Part 5 |
| A synthetic test-event button (FR-WHK-09) | Part 5 |
| SDK helpers for verifying signatures | chapter 5.1 |
| Per-endpoint delivery rate limits | the limits chapter |

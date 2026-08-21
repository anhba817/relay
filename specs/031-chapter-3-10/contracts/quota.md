# Chapter 3.10 — contracts

Three surfaces: what a refused send looks like, what an admin receives, and what
the usage read returns.

## 1. The refusal

Returned when usage for a dimension is at or above that dimension's hard cap.

**HTTP status**: `402 Payment Required`.

Not `429`. Chapter 3.8 owns `429`, and a client that retries on `429` after
`Retry-After` seconds is behaving correctly for a rate limit and wrongly for a
quota — the quota will still be exceeded in sixty seconds and in an hour.
`402` is the status whose meaning is "this is a commercial condition, not a timing
one", and it carries no header that suggests waiting.

**Body**, the same four fields chapter 3.8's refusal carries:

```json
{
  "code": "quota_exceeded",
  "message": "monthly message quota exhausted: 10000 of 10000 for 2026-08; sends resume on 2026-09-01",
  "docs_url": "https://relay.example/docs/errors/quota_exceeded",
  "request_id": "…"
}
```

**The message names four things** and the order is the contract: the dimension,
the figure used, the figure allowed, and when it changes. A developer reading this
in a log at 3am should not have to look anything up to know whether to page
somebody.

**No `Retry-After`.** There is a time at which sends resume and it is in the
message, but a header a client will sleep on is wrong when the wait is three weeks.

**Distinguishable from `rate_limited` by code, not by status alone** (FR-008). A
client switching on `code` gets the right answer; a client switching on status
gets the right answer too, because the statuses differ.

**What is not refused**: history reads, connection establishment, backfill,
webhook delivery of already accepted messages. The refusal is raised in
`sendMessage` and nothing else calls it.

## 2. The threshold email

One per `(environment, period, dimension, threshold)`, to every organisation
member with the `owner` role and a non-null email.

**Subject**: `Relay: <application> / <kind> has used <threshold>% of its monthly <dimension> quota`

**Body carries**, and the tests assert on each:

- the application and environment kind, named the way the dashboard would name
  them — not a uuid;
- the percentage, the usage at crossing, and the quota it is a percentage of;
- the period, as a month, not a timestamp;
- what happens next: for a soft threshold, nothing; for a hard cap at 100%, that
  sends are now refused and when they resume.

**Body must not carry** a signing secret, an api key, a credential, a message body,
or a user's text. Chapter 3.9 established that this is verified by reading what
Mailpit received rather than by asserting on the call — the same test shape
applies here.

**At 100% of a soft threshold with no hard cap**, the email says usage has reached
the configured figure and that nothing has been refused. An email that threatens a
suspension that will not happen is worse than no email.

## 3. The usage read

An admin surface, not a tenant one — there is no dashboard until Part 4, so this
is what the internal route and the tests read.

```
usageFor(db, environmentId, period) -> {
  period: "2026-08-01",
  messagesSent: 8241,
  activeUsers: 96,
  messageQuota: 10000 | null,
  activeUserQuota: null,
}
```

**Returns zeros, not null, for a period with no rows** (FR-003 and the spec's edge
case). An environment that has sent nothing has used nothing, and making the
caller distinguish "no usage" from "no row" would push a schema detail into every
reader.

**`null` quota means unlimited**, carried through rather than resolved to a
sentinel like `Infinity` or `-1`. The absent state stays absent all the way to the
reader, which is the same rule the nullable columns encode.

## 4. What the guard is promised

Nothing in these three surfaces performs a cross-environment write. The usage
increment is scoped to the sending environment, the notification insert to the
crossing environment, and the relay's drain is global for reading but marks only
the rows it claimed — the shape chapter 3.9's relay already has and which the
exemption list already covers for that file, not this one.

If any of that turns out to be false, the way it will show up is a refusal from
feature 030's trigger during the quickstart's baited run, naming the table and the
row. That is the intended failure mode and it is cheaper than the alternative,
which is discovering it in a suite that runs after this one.

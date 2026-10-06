# Clauses — chapter 4.22, "The identifier the customer gave it"

Each one read, not cited. **Met** means a test asserts it. **Demonstrated** means
the chapter shows it working end to end. **Unmet by decision** means the chapter
chose not to, and says why. **Unreachable** means the platform cannot satisfy it
as written.

---

## FR-USR-01 — **met, and it is the clause the chapter is for**

> *"The system shall represent end users by an identifier supplied by the
> customer, unique within a tenant. Relay shall not generate end-user
> identities."*

Users already obeyed it: 8 of 8 routes take the identity and the upsert returns
no uuid. Channels did not, on 13 of 13 routes. After this chapter both nouns
agree with the clause, and `addressing.itest.ts` asserts each route twice.

**AND THE SRS QUOTES THIS CLAUSE TWO WAYS.** Line 293 is the clause —
*identities* — and the bot note at line 345 quotes it in quotation marks as
*"Relay shall not generate end-user **identifiers**"*. Under the note's spelling
`users.id` and `channels.id` would themselves violate it, which is the evidence
for which one is wrong. One word; T038a.

## ADR-18 — **met, and extended**

> *"their identity is whatever `external_id` the customer already had for them."*

Written about users. ADR-38 carries the same sentence to channels and states the
rule for the next noun, which is what FR-008 asked for.

## FR-CHN-01 — **met before this chapter, and it was not enough**

> *"creating a channel with a customer-supplied identifier unique within a
> tenant…"*

Creation took the identifier and always had. **Nothing said it could then be used
to name the channel**, which is the gap FR-CHN-11 fills — and the reason the
chapter's clause is new rather than an amendment. Reading FR-CHN-01 as covering
addressing would make a creation clause carry a retrieval rule.

## FR-CHN-02 — **met, untouched**

> *"Channel creation shall be idempotent on the customer-supplied identifier…"*

Unchanged. The resolution reads; it does not create. `channels.itest.ts`'s
idempotent-repeat assertion is green on the unedited suite.

## FR-CHN-08 — **met, and it is the clause the phantom belonged to**

> *"listing a user's channels, ordered by most recent activity, with cursor
> pagination."*

`GET /v1/users/{externalId}/channels`. ADR-37 called its cursor the one live edge
on its reversal condition and described it as `GET /v1/users`'s, carrying
`users.id`. Measured: that route does not exist and the cursor carries
`channels.id`. The clause is met and was never the problem; the ADR naming it
was.

## FR-CHN-11 — **demonstrated**

The chapter's own clause. 13 routes × 2 identifier forms, asserted per route
rather than in aggregate, plus the collision, the tenancy pair and the no-5xx
sweep: 92 assertions in `addressing.itest.ts`, four of which were red before a
line was written.

## FR-TEN-05 — **met, and it nearly was not**

A foreign channel and an absent one must answer identically. The first version of
`ChannelIdPipe` threw its own `NotFoundException`, which made a banned user's
answer differ between a real channel and an invented one — 403 against 404.
`gauntlet.itest.ts` caught it. The pipe now resolves and never refuses.

## FR-006 (this feature) — **met by removal**

Every v1 response shape enumerated and one question asked of each uuid: does a
route accept this? One failed — `members[].user_id` — and it is gone. Three are
kept with reasons: `audit_log[].id` and `audit_log[].actor.id` are record
references a customer quotes back to support, and `request_id` is constitution
V's requirement in every error body.

## FR-MOD-04 / ADR-37 — **amended, not met or unmet**

Not this chapter's clause. Its ADR made a claim about this chapter's subject —
*"`users.id` is an internal uuid that the platform exposes nowhere a caller can
act on"* — which was false until `members[].user_id` was removed. Amended in both
homes under FR-010.

## Constitution I — **demonstrated, and probed**

The resolution is scoped by the request-scoped `Repository`'s constructor rather
than by a predicate. Measured before the design was committed: the same
identifier resolves under its own environment and resolves to nothing under a
foreign one, with the probe going red on the swap.

## Constitution VI, first bullet — **met late, and the record says so**

*New behaviour gets a requirement first.* FR-CHN-11 was written in Phase 5 and
the resolution was coded in Phase 3. Nothing is pushed, so no published history
has the behaviour without the clause — but the ordering the bullet asks for was
not the ordering that happened, and T027 said to write it before T013 merged.

## Constitution V — **engaged, and half-satisfied by this chapter**

*The API is the product.* The REST half now speaks the customer's language. The
real-time half does not: every gateway frame carries `channel: <uuid>` and a
socket send goes to a door typed `z.string().uuid()`. Published as a limitation
rather than fixed, because it is the gateway, `subjectForChannel`, the resume
cursors and the internal contract — a chapter, not a paragraph.

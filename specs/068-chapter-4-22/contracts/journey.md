# Contract — the Priya test

Not an API contract. This chapter adds no surface under option D, and under A or C
it adds a resolution rather than a route. **What needs specifying is the test**,
because a milestone's output is a claim about other chapters and the claim has to be
falsifiable.

## The file

`packages/outsider/src/priya.itest.ts` — a new file in the sealed package.

| | |
|---|---|
| what it talks to | the deployed containers, via `RELAY_API_URL`, `RELAY_WS_URL`, `RELAY_DEMO_CREDENTIAL` |
| what it may import | nothing from `services/` — the sealed package is on no exemption list |
| credential | the tenant's **application key** for Priya's actions; **user tokens** for the conversation |
| CI job | `relay-platform — the sealed integration` |

**WHY NOT `packages/e2e`, WHERE THE OTHER JOURNEY LIVES.** `docs/03`'s first
sentence: *"Priya never touches Relay directly. She uses an internal support tool
that Mai built on Relay's moderation APIs."* The e2e harness boots the services in
process and holds the api's own database handle. The sealed suite holds a URL and a
credential. **Only one of those is Mai's tool.**

## The margin, which is the contract

`tuan.itest.ts` states it: *"Read the right margin: each step names the chapter that
made it possible. **Remove that chapter's work and a named assertion here fails.**"*

Every assertion in this file carries the clause and the chapter it verifies:

```ts
expect(prior.length).toBe(1);                 // FR-MSG-07, Part 3 — edit history
expect(tombstone.text).toBeNull();            // FR-MSG-08, Part 3 — the deletion is visible
expect(entry.request_id).toBe(requestId);     // FR-MOD-03, 4.18  — the join
expect(receipt.stores).toContainEqual(...);   // FR-MOD-04, 4.21  — the receipt
```

**AND THE CLAIM IS TESTED, NOT ASSERTED.** SC-002 requires three chapters reverted
and three named assertions failing. A margin nobody has falsified is a comment.

## The six stages, and what each must prove

| stage | the assertion that discharges it |
|---|---|
| **1 Ticket** | a channel and two users exist under customer-supplied identifiers, created in one call each |
| **2 Locate** | the conversation is reached from the order number alone, and an order number nobody used produces a refusal that names its cause — **not a 5xx** |
| **3 Reconstruct** | three outcomes are distinguishable from the record: never sent, sent and deleted, sent and edited. The edited message yields both texts and both instants, in order |
| **4 Judge** | every instant in the record is UTC with millisecond precision (CON-04) — inspection, and the only stage with no behavioural assertion |
| **5 Act** | the moderator's deletion reaches a connected socket; the banned user is refused both connect and send; their history survives |
| **6 Record** | the audit entry for that deletion **carries** the `request_id` the caller was given — found by paging, because **neither log accepts it as a filter** (R8) — and an erasure returns a receipt naming each store |

**STAGE 2's SECOND HALF IS THE ONE TO WRITE FIRST.** *An order number nobody used
produces a named refusal* is red today — it is a 500 — whichever option R2 picks,
and it is the only assertion in this file that can fail before the chapter starts.

**AND STAGE 6's ASSERTION IS NARROWER THAN THE JOURNEY'S SENTENCE, ON PURPOSE.**
`docs/03` says the request id *joins* an audit entry to its request-log row; measured,
`audit.schema.ts` filters on `cursor`, `limit` and `action` and
`request-log.schema.ts` on `from`, `to`, `cursor`, `direction`, `limit`, `endpoint`
and `status` — **both carry the id and neither accepts it.** The assertion says the
entry carries it and the id resolves by paging. **Writing one that implies a filter
exists would make the test a claim about a surface nobody built.**

## The arrow (User Story 2)

Phase 3's exit criterion ends `→ erasure` and no test crosses it.

```
upload → scan → send → signed delivery        4.17, in the sealed suite already
                           → erasure          this chapter
```

| | must hold after the uploader is erased |
|---|---|
| the bytes | the signed URL no longer serves the object |
| the renditions | gone with the parent |
| the receipt | names `media_objects` with a count |
| **the message** | **still reads as a message** — an erased attachment must not render as broken, which is `docs/07` row 23's own clause one erasure later |

## What this contract does not offer

- **No new error code.** `not_found` and `invalid_request` are both in `codes.ts`
  already, which is 25 pages with 3 appendix hunks and not worth touching for a word
  that exists.
- **No scheduler**, so Phase 3's *"7 consecutive days"* clause is stated and not met.
- **No change to `integrate.itest.ts`.** The image path stays where 4.17 put it; if
  the arrow is added there instead of here, that is 5 pages and 5 appendix hunks and
  the task says so before it is paid.
- **No assertion about Stage 4 beyond the format.** Judgement is the human's and
  `docs/03` says Relay's only job is to stay out of the way.

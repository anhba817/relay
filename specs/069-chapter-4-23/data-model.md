# Data model — chapter 4.24, "★ Milestone: the Priya test"

**No new table, no new column, no migration.** A milestone verifies; what this
document models is the **traversal** — the six stages, what each needs, where it
comes from, and which of them the platform cannot do today.

## The journey as a traversal

```
STAGE 1  TICKET          order #88412, two names, a rough date
         needs           external ids on users and channels
         from            FR-USR-01, FR-CHN-01 · Part 2
         measured        200 / 201

STAGE 2  LOCATE          order number -> the conversation
         needs           CHANNEL RETRIEVAL BY EXTERNAL ID
         from            — NO CLAUSE —
         measured        500 on the natural attempt; the only resolution
                         that works is re-POSTing the create (FR-CHN-02)

STAGE 3  RECONSTRUCT ★   what was said, edited, deleted, and in what order
         needs           tombstones            FR-MSG-08/10 · Part 3
                         edit history          FR-MSG-07    · Part 3
                         server sequence       FR-MSG-02/03 · Part 2
                         history via API key   FR-MOD-01    · 4.19
         measured        routes exist; an application credential may send only
                         as a BOT, so the conversation needs user tokens

STAGE 4  JUDGE           human work
         needs           unambiguous timestamps · CON-04 · UTC, ms precision
         measured        inspection only — nothing to assert but the format

STAGE 5  ACT             remove the abuse, restrict the sender
         needs           moderator delete      FR-MOD-02 · Part 3
                         tenant-scoped ban     FR-USR-06 · Part 3
                         real-time deletion    FR-RTM-05 · Part 3
         measured        ban 200; delete route present

STAGE 6  RECORD          the trail an auditor follows in six months
         needs           audit log + request id   FR-MOD-03 · 4.18
                         erasure receipt          FR-MOD-04 · 4.21
         measured        audit log 200, request_id present; receipt 200
```

**THE ONLY STAGE WITH NO CLAUSE BEHIND IT IS THE ONE THE PLATFORM CANNOT DO.** That
is not a coincidence and it is the chapter's argument: a journey document asserted a
capability, no requirement carried it, and nothing noticed for twenty chapters
because no test walked the journey.

## The two key spaces, which is the seam Stage 2 falls into

```
v1/users/:externalId                    the CUSTOMER's identifier
v1/channels/:channelId                  RELAY's uuid
v1/channels/:channelId/messages         RELAY's uuid
v1/media/:mediaId                       RELAY's uuid
```

Measured on the lane: **0 of 41,765 channels have a uuid-shaped `external_id`**, and
**0 have one equal to their own row id**. So the ambiguity option C would introduce
is real in principle and has never occurred in practice, which is exactly the shape
that ships and then surprises somebody. If C is chosen the precedence rule is part of
the decision and the collision is a test, not a hope.

## The fixture the journey needs

One dispute, built from outside with nothing but the published API:

| | |
|---|---|
| a channel | `external_id` = an order number, `private` |
| two participants | a dispatcher and a driver, each with a user token |
| the decisive message | sent, then **edited** after a measurable interval |
| the abusive message | sent, then **deleted** by the moderator |
| an attachment | a real image, uploaded, scanned by the deployed worker, delivered |
| Priya's credential | the tenant's application key — never a user token |

**THE INTERVAL IS PART OF THE FIXTURE.** `docs/03`'s dispute turns on *"the
dispatcher edited the address message eleven minutes after sending it"*. A test
cannot wait eleven minutes; it asserts that the two instants differ and that the
record says which came first, which is the property the dispute actually needs.

## What the test reads, and what it must not

**Reads**: the published REST API and a socket, with a URL and a credential.

**Must not read**: the database, the api's internals, or any package that imports
`pg`. `packages/outsider` is on no exemption list and that is the point — the sealed
suite is the only lane in this repository that cannot cheat.

## Entities this feature adds

None to the platform. Three to the record:

- **A stage verdict** — one per Journey 3 stage: demonstrated, met, unmet by
  decision, or unreachable, with the assertion or the obstacle.
- **A Phase 3 clause verdict** — one per clause of SRS §7.3's Phase 3 criterion.
- **A revert demonstration** — a chapter reverted, the named assertion that failed,
  and the assertion restored. Three of them (SC-002).

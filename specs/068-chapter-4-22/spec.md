# Feature Specification: chapter 4.22, "The identifier the customer gave it"

**Feature directory**: `specs/068-chapter-4-22/`
**Created**: 2026-10-05
**Chapter**: Part 4, movement VII — **new**, and the first chapter Part 4 ever gained
**Source**: `docs/04-srs.md` FR-USR-01, FR-CHN-01/02/08 · `docs/06-adr-deep-dives.md`
ADR-18 · `docs/03-journey-map.md` Journey 3 Stage 2 · `docs/12` §3

**Why this chapter exists.** The Priya milestone's premise check walked Journey 3 and
could not complete Stage 2. The fix is thirteen routes wide, and `docs/12` §5 rule 4
says a milestone appears after all the work it verifies — so the work is its own
chapter placed before it, and the milestone becomes **4.23**.

---

## The model this chapter restores

Two clauses say what an identifier is here, and neither is ambiguous.

> **FR-USR-01** — *"The system shall represent end users by an identifier supplied by
> the customer, unique within a tenant. **Relay shall not generate end-user
> identities.**"*
>
> **ADR-18** — *"their identity is whatever `external_id` the customer already had
> for them."*

So a uuid in this platform is a **key** — for foreign keys, for ordering, and because
a text primary key across 216,921 messages and 172,965 memberships costs more than it
is worth. **The customer's string is the identity.** There are not two ids for one
object; there is one identity and one internal key, and only one of them belongs on
the wire.

**EXACTLY TWO TABLES CARRY A CUSTOMER-SUPPLIED IDENTIFIER**, measured: `users` and
`channels`. Messages, media objects, webhooks and environments are Relay's own
objects with Relay's own ids, correctly addressed by uuid, and out of scope by
construction.

## The premise check, measured 2026-10-05

**The platform already demonstrates the right answer on one noun and the wrong one on
the other.**

| | `users` | `channels` |
|---|---|---|
| routes taking the identity | **8 of 8** | **0 of 13** |
| create response | `external_id, status, display_name, …` — **no uuid** | `id, external_id, type, …` — **uuid first** |
| uuid reaching the customer | **nowhere yet found** — see below | in every create response, and required afterwards |

```
GET  /v1/channels/{externalId}            500
GET  /v1/channels/{uuid}                  200
POST /v1/channels/{externalId}/messages   500
POST /v1/channels/{uuid}/messages         201
```

**A CUSTOMER MUST STORE RELAY'S UUID TO POST TO A CHANNEL THEY NAMED THEMSELVES.**
That is the lookup table FR-CHN-01's customer-supplied identifier exists to remove,
and the one `docs/03` promises Mai's tool will not need — *"map order #88412 →
channel `order-88412` with zero lookup tables."*

**AND THE FAILURE IS A 500, NOT A 404.** The route takes a uuid, an external id is
not one, and the refusal is an internal error — so the natural first attempt tells a
developer the platform is broken rather than that they used the wrong key.

**THE USERS SIDE IS ALMOST RIGHT, AND THE ONE LEAK EVERY DOCUMENT NAMES IS NOT
THERE.** ADR-37 says the `GET /v1/users` listing cursor is base64 of `{a, id}` and
calls it the one live edge on its reversal condition. Measured: **there is no `GET
/v1/users` route**, the cursor belongs to `GET /v1/users/{externalId}/channels`, and
the `id` it carries is a **channel** uuid — which every one of these thirteen routes
accepts after this chapter.

So the chapter inherits a correction rather than a repair. **ADR-37 comes out
stronger**: its conclusion holds and its one bounded exception does not exist, which
FR-010 makes this chapter's work in both of the ADR's homes. And the question US2
was built to answer is open again — *does any internal key reach a customer at all?*
— which is measured before anything is built.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A customer uses their own identifier everywhere (Priority: P1)

A support tool holds an order number. It reads the conversation, posts to it, adds a
member and archives it, without ever having stored an identifier Relay invented.

**Why this priority**: it is the chapter. Everything else is a consequence.

**Independent test**: create a channel under a customer-supplied identifier, then
exercise every route beneath that prefix using only that identifier.

**Acceptance scenarios**

1. **Given** a channel created with identifier `order-88412`, **when** any route that
   names a channel is called with `order-88412`, **then** it behaves exactly as the
   same call with the uuid.
2. **Given** an identifier no channel in this environment has, **when** any such route
   is called, **then** the refusal names the cause and is **never a 5xx**.
3. **Given** two environments that each have a channel called `order-88412`, **when**
   one tenant calls with that identifier, **then** they reach their own and the other
   tenant's is untouched.
4. **Given** a client that has stored uuids from before this chapter, **when** it calls
   with a uuid, **then** every route answers as it did.

### User Story 2 - Find out what internal key reaches the customer, and close it (Priority: P2)

Nothing a customer receives contains an identifier they cannot use and were never
meant to hold. **The story begins with a measurement, because the leak every
document named turned out not to exist.**

**Independent test**: sweep what the user surface returns, state the count, and show
that whatever it finds is either closed or recorded with a reason.

**Acceptance scenarios**

1. **Given** the user surface after this chapter, **when** every response shape a
   customer can reach is enumerated, **then** the count of internal keys among them
   is stated, including when it is zero.
2. **Given** an internal key the sweep finds, **when** the chapter closes, **then**
   it is either no longer returned or recorded as a deliberate exception with its
   reason.
3. **Given** a value the chapter changes in an opaque token, **when** one issued
   before the chapter is presented afterwards, **then** it either continues to work
   or is refused with a named cause — never a 5xx and never a silently wrong page.

**If the sweep finds nothing, this story is one document amendment and the chapter
says so.** A story that reports zero after looking is not a story that failed.

### User Story 3 - The rule is written down so the next noun gets it right (Priority: P3)

A future table with a customer-supplied identifier should not have to rediscover this.

**Independent test**: read the amended clauses and find, without reading code, which
identifier addresses each noun and why.

**Acceptance scenarios**

1. **Given** the specification after this chapter, **when** a reader asks how a noun
   with a customer-supplied identifier is addressed, **then** one clause answers it.
2. **Given** a noun with no customer-supplied identifier, **when** the same question is
   asked, **then** the same clause says a Relay identifier is correct and why.

### Edge Cases

- **A customer identifier that is itself a uuid.** Legal today — `external_id` is any
  string up to 255 characters. Measured: **0 of 41,768** channels have one. The
  resolution order must be decided and tested rather than left to chance.
- **A channel whose identifier contains a slash or a percent sign.** It is a path
  segment now, where before it was only a request body.
- **The same identifier in two environments.** 1,576 external ids are reused across
  environments in `users`; resolution must be tenant-scoped like every other read.
- **A uuid that is a valid uuid and names nothing.** Must stay a 404, not become a 500.
- **An archived or deleted channel** reached by its identifier — the same answer the
  uuid gives today.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every route naming a channel MUST accept the customer-supplied
  identifier for that channel.
- **FR-002**: Every such route MUST continue to accept the Relay identifier it accepts
  today, with unchanged behaviour.
- **FR-003**: Where both could match, the resolution order MUST be defined, documented
  and tested.
- **FR-004**: An identifier that names nothing MUST produce a refusal whose **code**
  names the cause. The **message** stays constant: FR-TEN-05 requires a foreign
  channel and an absent one to answer identically, which `channels.service.ts`
  already does deliberately. **No value in the channel segment of these routes may
  produce a 5xx** — see the scope note under SC-003 for the segment this chapter does
  not reach.
- **FR-005**: Resolution MUST be scoped to the calling tenant's environment, and that
  scope MUST be demonstrated by removing it and observing a test fail.
- **FR-006**: The values a customer receives MUST be swept for identifiers that are
  Relay's alone and that no route accepts, the count stated, and each one found
  either removed or recorded as a deliberate exception with its reason.
- **FR-007**: If the chapter changes what an opaque token carries, one issued before
  it MUST keep working or be refused with a named cause. **Conditional on FR-006's
  sweep finding something to change.**
- **FR-008**: The specification MUST state which identifier addresses a noun and on
  what basis, so a future noun is decided rather than guessed.
- **FR-009**: Nothing outside this chapter's subject may change behaviour.
- **FR-010**: Where measurement falsifies a published clause or document, the document
  MUST be amended rather than left to diverge.

### Key Entities

- **An identity** — the string a customer supplied. Unique per environment. The thing
  a route names.
- **An internal key** — the identifier Relay minted. Unique globally, used by foreign
  keys and ordering, and not a thing a customer should need.
- **A resolution** — turning what arrived in a path into an internal key, once, inside
  the calling tenant.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every route that names a channel works with the customer's identifier —
  **13 of 13**, asserted per route rather than in aggregate.
- **SC-002**: Every one of those routes also works with the Relay identifier, asserted
  the same way.
- **SC-003**: No value in the **channel segment** of those routes produces a 5xx,
  including a malformed identifier, an absent one and one belonging to another
  tenant. **Three of the thirteen carry a `:messageId` as well**, which is a uuid
  column with no shape check, so a malformed message id is still a 500 — 058-3's
  class, out of scope here and published as such.
- **SC-004**: A tenant calling with an identifier another tenant also uses reaches
  their own channel, and the other tenant's rows are unchanged.
- **SC-005**: Removing the tenant scope from the resolution turns at least one named
  test red.
- **SC-006**: Every response shape the user surface can return is enumerated and the
  internal keys among them counted, **with the count stated whether it is zero or
  not**, and each one disposed of.
- **SC-007**: Journey 3 Stage 2 completes with the order number alone, which chapter
  4.23's milestone then asserts end to end.
- **SC-008**: `git diff --name-only part4-ch21 --` contains no file outside this
  chapter's subject, tests and documents. **One dot form, not two**: `..HEAD` reads
  committed state and reported a confident 0 for 4.21 while two leaked ids sat in the
  working tree (067-3).
- **SC-009**: The fence chain reports 0 and all six tutorial gates exit 0.
- **SC-010**: The CI error set is compared per error against the pre-chapter baseline,
  in both directions.
- **SC-011**: The resolution's added cost is measured per route and published — one
  scoped `SELECT` that the handler's own read does not replace.

---

## Assumptions

- **Two nouns, measured, not assumed.** `channels` and `users` are the only tables
  with an `external_id` column. Messages, media, webhooks and environments have no
  customer-supplied identifier, so a Relay identifier is correct for them and they are
  out of scope.
- **Users may need no change at all.** All eight user routes take the identity and
  the upsert returns no uuid. The listing cursor every document named as the single
  leak belongs to a different route and carries a **channel** uuid, so US2 opens with
  a sweep rather than an edit, and ADR-37 is amended either way.
- **Accepting both is a transition, not a design.** Published clients hold uuids. The
  chapter does not propose removing that acceptance, and whether it is ever removed is
  a question for a later chapter with a deprecation path.
- **The read-position route is fixed as a consequence.** `PUT
  /v1/users/{externalId}/channels/{channelId}/read` mixes both conventions in one path
  today; the channel half changes with every other channel route.
- **This chapter builds and the one after it verifies.** That ordering is `docs/12` §5
  rule 4, and it is why this chapter exists separately at all.

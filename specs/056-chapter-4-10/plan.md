# Implementation Plan: chapter 4.10 — the upload that never reaches us

**Feature directory**: `specs/056-chapter-4-10` | **Date**: 2026-09-18
**Spec**: [spec.md](./spec.md) · **Research**: [research.md](./research.md) — **read it first,
it settles the specification's one flagged assumption against the assumption.**

## Summary

Movement V opens. A caller declares what it intends to upload, the platform decides, and hands
back a URL good for fifteen minutes and a `media_id` in state `pending`. Bytes never reach us —
ADR-13 decided that and this chapter is the first half of it.

Four premises were run rather than read, and three moved the plan:

- **A presigned URL needs no dependency.** 28 lines of `node:crypto`, proven against a running
  store: signed PUT 200, signed GET 200, unsigned GET **403**, expired refused by the store,
  tampered 400. **Dependency count moves by zero.**
- **The SAD's image cannot be pulled.** `minio/minio` is `pull access denied`; the service names
  `quay.io/minio/minio`.
- **Storage is a level and `usage_periods` holds flows.** The cap joins `quotaConfig`; the
  accounting does not join the monthly rows, because `creditFor` refuses to subtract and the
  figure would reset on the 1st. **FR-RTL-05 is amended**, because two clauses cite it for a
  quantity it does not define.

## Technical Context

**Language / runtime**: no change. TypeScript on Node 22, the api's existing NestJS surface.
**New dependency**: **none.** `node:crypto` signs; `node:fetch` is not even needed, because the
client uploads, not us.
**New infrastructure**: one container, `quay.io/minio/minio`, 241 MB, joining `compose.yaml`
beside the four stores. `docs/12`'s dependency count moves by **one service and zero packages**.
**Data**: one new table for media objects; one new key in `quotaConfigSchema` and its migration
`CHECK`.
**Scale**: three refusals, one slot route, one signer. The chapter's own arithmetic is the quota
boundary — one byte under and one byte over.
**What is NOT in scope**: FR-MED-03's verification, FR-MED-04's scan, the `{ type: "media" }` arm
(4.11), signed delivery (FR-MED-08), and FR-MED-12's metering.

## Constitution Check

Read the clauses, not the identifiers. Each row says what was opened.

| principle | verdict | what was read, and why |
|---|---|---|
| **I — tenant isolation** | **ENGAGED, AND IT IS THE CHAPTER'S FIRST TEST** | A media row is tenant data and the object key must not be guessable across tenants. The slot route scopes by the authenticated environment; the gauntlet derives routes from the running router, so the new route joins it and must be attacked. Constitution VI's 100%-branch clause names tenant isolation, so the scoping branch is pinned. |
| **II — no acknowledged message is lost** | **NOT ENGAGED** | No message path. A slot is not an acknowledgement of anything. |
| **III — two data paths** | **NOT ENGAGED, AND THAT IS A DECISION** | FR-MED-12 would put stored bytes in the analytical store. This chapter needs the cap, not the meter, and the cap is an operational read. No analytical query. |
| **IV — single writer** | **PASS** | The media row is written by the api through the repository layer, like every other row. The object is written by the client to a store that holds no Relay state. |
| **V — API-first** | **PASS** | The slot is a REST route on the tenant surface, documented before it is built (`contracts/`). |
| **VI — requirement-driven, test-verified** | **PASS, WITH ONE CLAUSE THE CHAPTER OWES** | Every FR maps to a test. The 100%-branch clause applies to the tenant-scoping branch. And the quickstart MUST run unmodified — feature 055 made that verifiable again, and this chapter is the first to be held to it with a green gate behind it. |
| **VII — boring by design** | **PASS, WITH ONE ADR OWED** | No new package. One new container, and **ADR-13 already chose the pattern** — so the ADR this chapter owes is not "use object storage" but the narrower decision R1 makes: **sign it ourselves rather than take a client.** That is a dependency decision and VII requires the record. |

### The clause this chapter is inside

ADR-13's *"media bytes never transit Relay compute"* is what makes every other choice here
follow, and the measurable reason is an RSS figure that has been taken twice: `docs/11:43-44`
measured the gateway at **160 MB with 200 channels and 157 MB with 10,000**, recorded in SRS
revision 1.9. A 100 MB video through the api would move a number somebody measured.

**CITE `docs/11`, NOT THE CLAUSE, AND COMPARE AGAINST 157.** NFR-SCL-01 reads *"The system shall
sustain 10,000 concurrent WebSocket connections per gateway instance"* and **carries no memory
figure at all**; 160 is not a budget either, it is the larger of two observations. Chapter 4.5
found and corrected this exact attribution — *"Cite the source that holds the number and compare
against 157, not the rounded ceiling"* — and this plan reproduced it, which is what a carried
number does when the carrying is done from memory.

## Phases

### Phase 0 — The store, and the signature 🎯 first, because everything rests on it

Add `quay.io/minio/minio` to `compose.yaml` with a health check that **fails for the reason you
care about**. Chapter 4.2 is the warning: ClickHouse's `/ping` answered `Ok.` for sixteen chapters
while every query from outside the container was refused. MinIO's `/minio/health/live` has the
same shape, so the check that counts is a signed round trip, not a liveness probe.

Then the signer, with its test against the running store. R1's five results are the acceptance:
200, 200, 403, expired, 400.

### Phase 1 — The media row and the slot

One table, one route, **and the module registered in `app.module.ts`** — without that line the
route does not exist and every test in the chapter gets a 404. Chapter 4.6 shipped the same
omission in a different file and `pnpm build` said `Error: Unknown chapter id: 4.6`; its record
says *"registering the chapter is a task no requirement had named."* The row is scoped to the environment and to the user when there is one.
The route returns the `media_id` and the URL and stores nothing about the URL, because the URL is
derived and the store enforces its own expiry.

### Phase 2 — The four refusals, and the ladder that makes them honest

`media_type_not_allowed`, `media_too_large`, `media_storage_exhausted` and
**`media_storage_unavailable`** — the fourth is `docs/05-sad.md:1062`'s degradation row, which
analysis found after the specification had called it unexplained. Each gets a section in
`docs/08-error-reference.md` and each is asserted **by code**, not by status.
`webhooks.itest.ts` passed for four chapters while the body said `internal_error`; only the code
could have caught it.

**Asserting four codes are distinct is not the same as asserting each is right.** The test names
the condition and the code together.

**AND THE STATUS LADDER GAINS FOUR ENTRIES.** `protocol-error.filter.ts` maps 400, 401, 403 and
404 and falls everything else through to `internal_error`. All four of this chapter's statuses —
415, 413, 402, 503 — are outside it, so they are right only while every thrower remembers to name
its code. The filter's own comment calls that fallback *"a lie the client cannot act on"*, twice,
about the two statuses earlier chapters fixed. Four more statuses is four more lies unless the
ladder learns them.

### Phase 3 — The quota, and the clause it forces

`storage_bytes` joins `quotaConfigSchema` **and** the migration's `CHECK`, together, for the
reason the existing comment gives: the constraint would otherwise accept a config the parser
rejects, `capsFor` fails closed, and the cap silently becomes no cap. **Probe both halves** —
feature 049's rule about a pin that cannot fail.

Then **SRS FR-RTL-05 is amended**: storage is a fourth quantity and it is a level rather than a
monthly flow. Amending the clause is what this project does when measurement falsifies one, and
R3 is the measurement.

### Phase 4 — The boundary, and the two things this chapter cannot fix

The quota test is at the boundary: one byte under the cap succeeds, one byte over is refused.
A test in the middle of a range proves the comparison exists, not that it is right.

Then record, plainly: a slot nobody uploads to holds committed bytes indefinitely, because no
job in this chapter or the next reclaims it; and the read-then-write quota check is inside one
transaction, with what the alternative costs stated, because a reader who copies the unserialised
version ships the race.

### Phase 5 — The chapter, the chain and the close

Prose within **2,000–4,000 words outside code fences** (`docs/07:67`), at least one **`TRAP`**
box (`docs/07:70` makes it a counted class with a per-chapter minimum, and 4.7, 4.8 and 4.9 carry
2, 3 and 2), figures, the chapter registered in `lib/tutorial.ts` — `pnpm build` throws on an
unregistered id and that has cost two chapters. `compose.yaml`'s hunk in both locales, generated
with `check:fences --dump`. The gates, read by their success lines. **The fence count is reported
as an absolute number, not a delta** (055's own close-out decided that).

## Complexity tracking

| decision | why it is not simpler | what it costs |
|---|---|---|
| **Signing with `node:crypto` rather than an S3 client** | A client is two packages and a transitive tree for a string this platform can produce in 28 lines, and chapter 4.2 set the precedent with `fetch` against ClickHouse. | The canonical request is ours to get right, and its failure mode is an unexplained 400. Paid with a test against the running store rather than against an expected string. |
| **A new container in the local stack** | ADR-13 requires a store the client can reach directly; there is no in-process substitute that also proves the 403 on an unsigned read. | 241 MB and one more service in every `docker compose up`. **Zero packages** — the two counts are different and only the package one is what this project has been calling a dependency count. |
| **Committed bytes as a query rather than a counter** | A counter on `environments` would be a second source of truth for something the media rows already say (constitution IV). | A sum per slot request. At this chapter's scale it is nothing; the plan says so rather than pretending it measured a million rows. |
| **Amending FR-RTL-05 rather than bending storage into a monthly quota** | The bend is what the clause's words invite, and R3 measured why it breaks: subtraction and a reset on the 1st. | An SRS revision, and two other FR-MED clauses to re-read when it lands. |

## Files this chapter is expected to touch

    relay-platform/services/api/src/media/              the signer, the slot route, the refusals
    relay-platform/services/api/migrations/             the table, and the quota CHECK re-added whole
    docs/04-srs.md                                      FR-RTL-05 amended, revision 1.17
    docs/08-error-reference.md                          four sections
    docs/05-sad.md, docs/06-adr-deep-dives.md           ADR-30
    relay-tutorial/app/(en)/part-4/chapter-10/…         the chapter
    relay-tutorial/app/(vi)/vi/part-4/…                 ten hunks, byte-identical

    and TEN FENCED FILES — 77 en chapters, 9 appendix hunks — counted in pass 2:
    schema.ts 15 · codes.ts 12 · app.module.ts 11 · turbo.json 10 · compose.yaml 8
    targets.ts 6 · protocol-error.filter.ts 6 · catalogue.ts 4 · sentinel.sql 3 · config.ts 2

**The estimate is low and this project knows by how much.** 043 planned 17 files and changed 58;
045 said three and found eight. Every unplanned one came from running something — and this table
was already wrong before the work started: it named one fenced file where there are ten, which
analysis pass 2 found by counting rather than by running.

## Open questions for `/speckit-analyze`

1. **ANSWERED IN ANALYSIS PASS 1.** `docs/12`'s fourth refusal is `docs/05-sad.md:1062`'s
   degradation row — *"Object storage lost … Upload slots return a specific error"*. It is
   FR-017 now, with its own code, and it is the only transient refusal of the four.
2. Whether the media table is `media_objects` or joins an existing one. Nothing in the schema is
   close, so it is a new table; the name is the plan's smallest open choice.
3. Whether the object key includes the environment id. It makes cross-tenant reads structurally
   impossible (chapter 3.24's argument about `conn:{env}:{user}:{slot}`) and it leaks the tenant
   id into a URL a client holds. Both directions have a published precedent in this repository.
4. Whether this chapter provisions the store in CI as well as locally. Chapter 4.8 provisioned
   ClickHouse in CI four chapters after it was needed; the same shape is available here and the
   cost is a service in one workflow job.

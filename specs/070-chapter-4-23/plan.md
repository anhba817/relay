# Implementation Plan: chapter 4.23, "The channel a socket names"

**Feature**: `specs/070-chapter-4-23/` · **Spec**: [spec.md](./spec.md) ·
**Research**: [research.md](./research.md)
**Created**: 2026-10-06 · **Predecessor tag**: `part4-ch22` · **Successor**: 069 / chapter 4.24

## Summary

Seven client-facing frame schemas name a channel and every one of them carries the
uuid Relay minted — **and the `connection.ack` payload carries three more structures
that name channels by key or in a list** (`revisions`, `cursor`, `truncated`), which
analysis pass 1 found and the field-shaped premise could not. ADR-38, written one chapter ago, says a noun with a
customer-supplied identifier is addressed by it — and the gateway has never been read
against that rule, because the rule is newer than the gateway.

**The fix is a map at the gateway's client edge.** The connection already holds a set
of channel keys; it gains the identities beside them, and the 21 sites that write
`channel:` onto a frame read through it. Everything behind the edge keeps its keys:
the fan-out subjects, the resume cursor's storage, the api-facing send door.

**The alternative that looks cheaper is not, and chapter 4.22 is why.** Annotating
every internal payload at publish time would need no map and could not go stale —
except that `ChannelIdPipe` now resolves the identity to a key at the request
boundary, so **no handler holds an identity by the time it publishes** (R2). The
chapter that made REST speak the customer's language removed the identity from the
one place the other design needed it.

## Technical Context

| | |
|---|---|
| **Language** | TypeScript, Node.js — no new language |
| **New dependency** | **none** |
| **New service** | none |
| **New table or column** | **none** — no migration |
| **The mechanism** | a per-connection `key → identity` map, filled at connect (R2, R3) |
| **Blast radius** | **11 files · 83+ English fence pages · 18+ appendix blocks, 3 to create** (R6) — the spec estimated ~50 across 7 and was 40% low; pass 1 then added two files R6 had not counted |
| **Regression surface** | every connected client; the resume cursor is the sharp edge (R4) |
| **Unknowns** | **how a channel joined mid-session gets its identity** — three options priced, Phase 2 |

## Constitution Check

Read clause by clause, because a principle's bullets do not get one verdict.

### I. Tenant isolation — **ENGAGED, AND THE MAP IS A NEW PLACE TO GET IT WRONG**

The map is built from the session response, which is already scoped to the
connection's principal — so the scope arrives with the data rather than being applied
here. **That is the same by-construction argument 4.21 and 4.22 made, and it has the
same failure mode: nothing in this service would notice if the scope were dropped
upstream.** FR-006 requires the probe, and 065-4 says to expect the single-mutation
version to see nothing.

**AND THE MAP RUNS BOTH WAYS, WHICH DOUBLES THE SURFACE.** Pass 2 found that FR-002
needs `identity -> key` at three inbound sites, so there are two lookups to get
wrong rather than one. The inverse is derived from the same session response and is
safe to derive because `external_id` is unique per environment — but it is a second
place a foreign key could enter if the response were ever unscoped.

**The specific risk this chapter adds**: a key that misses the map. Whatever the
fallback is, it must not be *emit the key* — a client receiving another tenant's uuid
would be a leak, and a client receiving its own is the defect the chapter exists to
remove. R3's third option is refused in writing for the second reason; the first is
why the refusal matters.

### II. No acknowledged message is lost — **ENGAGED, THROUGH THE CURSOR**

A resume cursor is how a client says what it already has. R4 measured that
`cursorSchema` is `z.record(z.string(), …)` and a client returns the keys it was
given, so **every client reconnecting across this deployment presents uuids.** A
gateway that accepted only identities would resume nothing and lose nothing visibly —
which is the worst shape this principle has. Accepting both inbound is not politeness.

**AND PASS 3 FOUND THE SAME PRINCIPLE ON THE OTHER SIDE OF THE RESUME.** A buffered
`Message` is both the frame a client will receive and the row two internal
comparisons index by channel — `flushable`'s `marks[frame.channel]`
(`resume.ts:111`) and the revocation filter at `session.ts:662`. Translate where the
frame is built and the first re-delivers a client's whole buffer while the second
flushes a revoked channel's backlog. **Where the translation happens is therefore a
constitution II question**, which is why it is a blocking decision (T012a) rather
than an implementation detail.

### III. Two data paths — **NOT ENGAGED.** No analytical surface changes.

### IV. Single writer — **NOT ENGAGED.** The translation is a read.

### V. API-first — **ENGAGED, AND THIS CHAPTER IS ITS SECOND HALF.** 4.22 made the
REST surface speak the customer's language and left the real-time surface speaking
Relay's. One product, two answers. Nothing here is new behaviour; it is the gateway
catching up with a decision already published.

### VI. Requirement-driven — **FIVE BULLETS, FOUR ENGAGED**

1. *New behaviour gets a requirement first.* **No FR-RTM clause names an identifier —
   0 of 10, measured.** So FR-008's clause is new, and it must be written before the
   translation is, which is the ordering 4.22 got wrong and recorded.
2. *100% branch coverage for tenant isolation.* The map's miss path is in that
   population the moment it exists.
3. *The cross-tenant suite gates releases.* The gauntlet attacks REST. **Whether it
   can attack a socket at all is a Phase 1 question (T009), and the answer binds.**
   The first draft of this plan said an unreachable socket would be *"a gap to record
   rather than a box to tick"* — **constitution I does not offer that option**: the
   suite MUST attack every endpoint with foreign IDs on every build. So either the
   socket is attacked (T042a) or the clause is amended through its own process. The
   exposure predates this chapter; the map is what makes it load-bearing.
4. *The quickstart runs unmodified.* Still by hand; zero occurrences of `quickstart`
   in `ci.yml`.
5. *Unknown fields rejected on write endpoints.* Engaged — the frames are strict
   (`internal.ts`: *"Payloads are strict: unknown fields are rejected"*), so widening
   the session response is a contract change both sides must agree on.

### VII. Boring by design — **ENGAGED, AND AN ADR IS UNLIKELY**

No new language, service or dependency. **ADR-38 already decided this**; applying a
published rule to a second surface is not a new architecture decision. 4.22's plan
predicted an ADR and was right; this one predicts **no new ADR, and an amendment to
ADR-38's "what it does not cover" paragraph instead** — which is the paragraph that
named this gap. The prediction is worth nothing without the check (T010).

## Project Structure

```
specs/070-chapter-4-23/
├── spec.md · plan.md · research.md (R1–R7)
├── data-model.md        the two identifier spaces, one service further out
├── contracts/
│   └── frames.md        what each frame names, before and after
├── quickstart.md        connect, provoke every frame kind, read every channel field
├── clauses.md · traceability.md · baseline.txt · gaps.md · tasks.md
```

```
relay-platform/
├── packages/protocol/src/internal.ts     the session response carries identities
├── packages/protocol/src/frames.ts       7 schemas — the comment, not the type
├── services/api/src/internal/session.controller.ts   pairs, not strings
├── services/api/src/db/repository.ts     channelsForUser returns the identity too
├── services/gateway/src/registry.ts      the Connection gains the map, beside the
│                                         channel-keyed `revisions` it already holds
├── services/gateway/src/auth.ts          carries the pairs one hop earlier
├── services/gateway/src/session.ts       18 of the 21 sites, the ack's three
│                                         structures, and the revocation backstop
├── services/gateway/src/fanout.ts        1
├── services/gateway/src/resume.ts        1, and the cursor's inbound FILTER
├── services/gateway/src/typing.ts        1
├── services/gateway/src/api-client.ts    the second api→gateway contract (pass 1)
└── services/api/src/internal/memberships.controller.ts   the other end of it

   THE SUBJECTS DO NOT APPEAR HERE AND THAT IS THE DESIGN. `subjectForChannel` and
   its four siblings keep deriving from the key; a subject is not a thing a client
   sees. Same division as 4.22, where ten repository methods never learned the
   identity existed.
docs/04-srs.md · docs/05-sad.md · docs/06-adr-deep-dives.md · docs/12 · docs/07
relay-tutorial/app/(en)/part-4/chapter-23/the-channel-a-socket-names/
```

## Phases

**1 — Baseline.** Gates with their counted lines, lane exit codes with `Cached:`
lines or under `turbo … --force`, the fence bill re-derived, the CI error set, and
R1–R6 re-measured. **And the four gate deltas this chapter predicts, written before
any code** — 068 got all four right and a wrong one names its own cause.

**2 — The decisions (BLOCKING).** **Where the translation happens — at the 21 sites
or at the one `send` — which decides whether two internal comparisons survive and
how long the chapter is** (T012a, pass 3). How a mid-session join gets its identity
(R3's three options), decided with it, because one frame goes to two audiences.
Whether the cursor accepts both forms and how they are told apart (R4). Whether an
ADR is needed. **Before code, because constitution VI's first bullet
says so and 4.22 met it late.**

**3 — The clause (P3, but FIRST).** FR-RTM gains the clause that says which
identifier names a channel in a frame. **Moved ahead of the code deliberately**:
4.22 wrote its clause in Phase 5 with the code already in Phase 3, and `clauses.md`
had to record the bullet as met late. Not twice.

**4 — The map (P1).** The session response, `channelsForUser`, the registry's
`Connection`, the 21 sites — **and the `connection.ack` payload's three structures
that name channels without a `channel` field** (`revisions`, `cursor`,
`truncated`), which pass 1 found. Red first, and the red test is ten assertions
rather than seven.

**5 — The inbound half (P1).** Sends by identifier; **typing by identifier, which is
the only inbound path that drops an unknown channel with no frame, no close code and
no log line**; the cursor accepting both forms per Phase 2's decision; `ALL_CHANNELS`
special-cased before the map is consulted.

**6 — The probes.** Drop the map's scope and watch a named test fail. Whether the
gauntlet can attack a socket at all. Both halves of the coverage pin probe, through
`pnpm coverage`.

**7 — The documents.** SRS 1.30, ADR-38's "does not cover" paragraph, the SAD, both
Part 4 tables, the feature-local id sweep with `git diff <tag> --`.

**8 — The chapter.** 2,000–4,000 prose words, figures as `code`, TRAP and WHY boxes,
hunks from the checker's own replay — and **remove the block before dumping**, because
`--dump` emits the state after the appendix applies.

**9 — The record and the close.** Battery with the composed services stopped by name,
quickstart, push in submodule order, CI per error, tag `part4-ch23`.

## Complexity Tracking

| thing | why justified | what would make it unjustified |
|---|---|---|
| 83 English fence pages on one chapter | the gap spans two services and a shared contract; the alternative is a milestone that publishes a half-kept promise | if the subjects or the cursor's storage turn out to need re-keying, the bound has moved and this is a different chapter |
| and the bill may go DOWN for once | T012a's second design makes the 21 sites one `send` wrapper | nothing — a smaller bill needs no justification, but it does need re-deriving (T005), because an estimate that falls is as unmeasured as one that rises |
| `repository.ts` in the bill at 28 pages | `channelsForUser` is where the identity and the key sit on one row already | if the identity can reach the session controller without touching that method, take it |
| Accepting two identifier forms inbound | every connected client holds a uuid-keyed cursor (R4) | a deprecation needs a window, a warning and a version — a later chapter |
| A second chapter generated by the previous chapter's findings | the gap is bounded and measured, and ADR-38 already decided the rule | **if a third one appears, that is the signal to stop and let the milestone run** |

## What this plan does not decide

- **How a mid-session join gets its identity.** Three options priced in R3, including
  one listed to be refused. Phase 2.
- **Whether the cursor tells the two key forms apart by shape or by trying both.**
  Unlike a path segment, a cursor key has no shape test guaranteed to separate them —
  a customer identifier may itself be a uuid, which 4.22 measured at 0 of 41,772 and
  did not make impossible.
- **Whether the gauntlet can attack a socket.** If it cannot, constitution VI's third
  bullet is met by a different instrument or not at all, and either answer is recorded
  rather than assumed.

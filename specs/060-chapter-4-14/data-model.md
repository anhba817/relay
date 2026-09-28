# Data model — chapter 4.14, "Pending, ready, rejected"

**Feature**: 060 · **Date**: 2026-09-28 · **Research**: [research.md](./research.md)

**NO MIGRATION.** This chapter adds no column, no table and no constraint. `0018` shipped the
three states and the probe columns; 4.12 shipped the referencing lookup. What follows is what
this feature **reads**, and the one shape it adds, which lives in the protocol package rather
than the database.

---

## 1. What is read, and nothing is written

### `media_objects` (existing, migration `0018`)

| Column | Used for |
|---|---|
| `id` | The attachment's `media_id`; the event's subject |
| `environment_id` | Tenant scope on every read (constitution I) |
| `state` | `pending \| ready \| rejected` — the value FR-001 puts on the attachment |
| `rejected_reason` | **Not** put on the wire (R2). Read only by the sender's own door |

The `UPDATE … WHERE state = 'pending'` compare-and-set in the verdict path is 4.13's and is
unchanged. This feature reads its *result*, not the row.

### `messages.attachments` (existing, `jsonb`)

Holds what the sender declared: `{"type":"media","media_id":"<uuid>"}`. **The state is not
stored here and must not be.** FR-002 requires the state to be read when the message is served,
so a message sent before a verdict reflects the verdict afterwards without being rewritten.
Storing it would make every verdict a write across every referencing message — and would leave
two sources of truth for one fact, which is constitution IV.

Measured, and it is why FR-011 needs no code: **2,867 tombstoned messages, 0 with attachments.**
FR-MED-10's unlink already empties the array, so a tombstone cannot match the containment
predicate.

---

## 2. The shapes — three roles, and only two schemas exist for them

**ANALYSIS PASS 1 FOUND THIS SECTION WRONG.** It read *"two schemas already exist for an
attachment and only the second changes"*. There are **four** structural users of
`attachmentSchema` and one of them is not a request door:

    messages.schema.ts:40   REST send body          request  — must NOT gain a state
    frames.ts:94            socket message.send     request  — must NOT gain a state
    internal.ts:35          internal send request   request  — must NOT gain a state
    frames.ts:46            messageSchema           OUTBOUND — must gain one

`messageSchema` is **what the api builds**, and its own comment says so: *"required is what
makes the compiler name every site."* One schema is serving a door that must refuse a state and
a payload that must always carry one. **Changing only `forwardedAttachmentSchema` leaves the api
unable to put a state on anything it builds**, so the original plan could not have delivered US1.

### Three roles, three shapes

| Shape | Role | Media arm | Change |
|---|---|---|---|
| `attachmentSchema` | a sender declares | `{type, media_id}` | **none** — strict, and `strictObject` already refuses a `state` a caller tries to send |
| `deliveredAttachmentSchema` | **new** — the api builds | `{type, media_id, state}`, **required** | added, and `messageSchema.attachments` points at it |
| `forwardedAttachmentSchema` | a reader forwards | union | its typed arms gain the delivered shape; the loose arm is untouched |

**`state` is REQUIRED on the delivered shape, not optional.** This follows the precedent
`frames.ts:89` already states in its own words — *"a caller may send none, and a payload the
platform BUILDS must always say"* — and it is what makes the compiler name every construction
site rather than leaving a door silently omitting the field. That is the same argument
`messageSchema.attachments` is required for.

### What `forwardedAttachmentSchema` needs, which is less than it looks

Today it is `z.union([attachmentSchema, z.looseObject({ type: z.string() })])`. A delivered
attachment carrying `state` **already parses** — it fails the strict first arm and falls through
to the loose one. So nothing breaks today, and the fix is about types rather than acceptance:
put `deliveredAttachmentSchema` in the union **ahead of** `attachmentSchema` so a delivered
value matches a typed arm instead of degrading to a loose object, and leave the loose arm last
as the escape hatch FR-018d put there for a future arm.

**The reader stays permissive and that is not optional.** An envelope written by the previous
binary has a media attachment with no `state`, and it must keep parsing — it matches
`attachmentSchema`, which is why that arm stays in the union. The failure mode for getting this
wrong is `message.term()`, measured in that file's own comment.

### The cost this section originally hid

`messageSchema` is the contract published since chapter 1.3. `frames.ts` and `attachments.ts`
carry titled fences in **six English chapters** — 1.3, 3.15, 3.17, 3.18, 3.22, 4.11 — and four
Vietnamese. This is a fence-chain event across the series, not a one-file edit.

### The wire frame

A new client frame name, carrying the media id and the state. It is **not** `message.updated`:
`messageSchema` has no `edited_at`, so a client could not tell an attachment resolving from an
author editing (R1, option D).

---

## 3. State transitions

The machine is 4.13's. This chapter announces two of its edges and invents none.

    pending ──verified──▶ ready      announce
    pending ──refused───▶ rejected   announce
    ready   ──────────▶  (terminal)  no edge
    rejected ─────────▶  (terminal)  no edge

**Only a transition is announced, never a verdict.** The compare-and-set already answers
`applied: false` for a second verdict on a terminal row, and FR-005 hangs on that boolean.

**An object attached when already terminal has no edge left**, which is why the state on the
attachment is the floor rather than a convenience (R7). Measured: **538 of 1,589 referenced
objects on the lane are already terminal.**

---

## 4. The fan-out set

`channelsReferencingMedia(mediaId)` → `string[]`, private to the repository, built by 4.12 for
the delivery gate. **The producer cannot call it** (pass 3): the verdict seam has no
environment-scoped repository, so the query body gains a module-level entry point taking
`(db, environmentId, mediaId)` and the environment travels out of the verdict's `RETURNING`
list. One query body, one tenant predicate, two callers. Scoped by `environment_id`; `selectDistinct` over channels; containment
operand built as a **bound value** so the GIN index is usable (4.12's own repair).

    N = 0    4,725 objects unreferenced ── the COMMON case: publish nothing, fail nothing
    N = 1    1,545 objects
    N = 2       44 objects ── forwarding, FR-MSG-11 since 3.24

**One query, not two.** A second lookup written for this path would drift from the delivery
gate's, and only one of them would be the one that decides who may read the bytes.

---

## 5. Validation rules, traced

| Rule | Source | Where it holds |
|---|---|---|
| State is one of three values | `0018` CHECK | Database; the schema mirrors it as an enum |
| State read at serve time, never stored on the message | FR-002 | Read path |
| The **column** cast stays `Attachment[]`; the **constructed** Message uses the delivered shape | pass 2, D2 | `repository.ts:4817/5610/5918` vs the door sites |
| Tenant scope on every read | Constitution I | `channelsReferencingMedia`, repository constructor |
| Publish only on a real transition | FR-005 | `applied` from the compare-and-set |
| Empty channel list is success | FR-006 | Producer |
| Reader schema stays permissive | FR-018d | `forwardedAttachmentSchema` |
| Reason never on the fabric | R2, FR-010 | Frame shape |

# Data model — 043, fix the review's findings

**This feature adds no table, no column and no migration.** Its entities are constants,
published sets and records. They are listed here because three of them are the single
sources of truth FR-008 and FR-016 exist to create, and because two of them are documents a
gate will start reading.

---

## Constants that become single definitions

### `MESSAGE_TEXT_MAX`

The maximum length of a message's text, in characters.

| Property | Value |
|---|---|
| Value | 8000 — the number the REST and internal doors already carry |
| Home | `packages/protocol/src/frames.ts`, beside `messageSchema` |
| Consumers | `frames.ts` (socket), `internal.ts` (internal), `messages.schema.ts` (REST) |

**Why `frames.ts` and not `attachments.ts`.** The obvious shelf is beside `MAX_ATTACHMENTS` and
`ATTACHMENT_URL_MAX` — and every one of `attachments.ts`'s six exports is about attachments, so a
message-text bound there is the category error this feature exists to remove. `frames.ts`
publishes `messageSchema`, `internal.ts` already imports from it, and `attachments.ts →
frames.ts → internal.ts` is the existing direction, so the constant creates no cycle.

**Why it is an entity at all.** Today the value is a literal in two of the three doors and
absent from the third. The chapter 3.24 record names the shape this repeats: *"two schemas
that happen to agree are what `idem_key` against `idempotency_key` looks like three chapters
later."* One export, three importers.

**State**: none. It is a number.

### `WEBHOOK_EVENT_TYPES`

The event types FR-WHK-02 declares, each marked with whether the platform emits it yet.

| Field | Meaning |
|---|---|
| `type` | The string a customer subscribes with, spelled as FR-WHK-02 spells it |
| `emitted` | Whether any code path publishes it today |

| Type | Emitted |
|---|---|
| `message.created` | yes |
| `message.updated` | yes |
| `message.deleted` | yes |
| `channel.member_added` | yes |
| `channel.member_removed` | yes |
| `channel.created` | **no** — and 741 stored subscriptions name it |
| the remaining two FR-WHK-02 names | no |

**Relationship to `OUTBOX_EVENT_TYPES`**: the emitted subset MUST be derivable from this
list rather than maintained beside it. Two lists that must agree and are maintained
separately is the defect `gaps.md` 3.23-4 records about `targets.ts` and the `@Accepts`
decorator, and the one chapter 3.22 recorded about `eslint.config.mjs`, whose own comment
says the two lists *MUST AGREE* and which nothing compares.

**Validation rules**:

- A subscription naming a type outside this list is refused (FR-016).
- A subscription naming a type inside this list with `emitted: false` is accepted, and the
  response says the type is not emitted yet.
- Adding a type here without deciding `emitted` MUST fail to compile.

**State transition**: `emitted: false → true` when a chapter builds the producer. The
transition is one edit in one place and it must not require touching a second list.

### `AVATAR_URL_SCHEMES`

| Property | Value |
|---|---|
| Value | `http:`, `https:` |
| Determined by | parsing the URL and reading its scheme, never by matching the string |
| Precedent | `ATTACHMENT_SCHEMES` in `packages/protocol/src/attachments.ts` |

**Why parsed rather than matched**: research R7 of chapter 3.24 measured that the generic URL
validator accepts `javascript:`, `data:`, `file:` and `vbscript:`. A prefix match is one
encoding trick away from the same outcome.

---

## Sets a gate will start reading

### `CLOSE_CODES`

Already exists in `packages/protocol/src/codes.ts` with six members: 4001, 4002, 4003, 4004,
4008, 4009. This feature does not change it. It becomes an **input to a gate**: every member
must appear in the published error reference (FR-018, FR-019).

Current documented state, measured: 4002 appears twice and 4004 once in
`docs/08-error-reference.md`; 4001 appears only in the SRS; 4008 only in the tutorial plan,
which is deliberately unpublished; 4009 only in the SAD; **4003 appears in no document at
all.**

**Where a close code is documented**: inside the `**Status:**` line of the error code that
carries it. Not under its own `## ` heading — `check-error-codes.mjs:59` fails on any heading
that is not a member of `ERROR_CODES`.

### The specification's revision ledger

`docs/04-srs.md`, Appendix D. A table whose first column is a version.

| Field | Meaning |
|---|---|
| Version | `major.minor`, ascending down the table |
| Date | ISO date of the amendment |
| Change | What changed, and which chapter made it |

**Validation rule** (FR-020, FR-021): read top to bottom, the version column ascends. It
currently reads 1.0, 1.1, 1.2, 1.3, 1.4, **1.7, 1.6, 1.5** — three chapters each inserted
above their predecessor instead of below.

**State transition**: a chapter that amends the SRS appends one row. The gate makes "append"
the only shape that passes.

---

## Records this feature corrects

| Record | Correction |
|---|---|
| `docs/09-platform-implementation-review-2026-09-03.md` | The bot/quota finding states what `assertWithinQuota` does: the message hard cap throws before the sender test, and a bot is exempt only from the unique-active-persons ceiling (FR-022). |
| The same review | The webhook remedy names the declared set rather than the emitted set, per research R5. |
| `specs/041-chapter-3-23/gaps.md` item 1 | Its recommended fix has the same defect and is re-pointed. |
| `docs/04-srs.md` FR-RTM-10 | States the bound that applies when the fabric is unavailable, matching ADR-20 (FR-025). |
| `docs/04-srs.md` FR-RTM-09 | States that the connection limit is best-effort and what happens when it cannot be checked, matching ADR-23 (FR-025a). |

**Constraint on both clause amendments** (FR-025c): the measured behaviour is the upper bound
on what the amended clause may permit. An amendment may describe the sixty-second bound ADR-20
already states; it may not grant a longer one.

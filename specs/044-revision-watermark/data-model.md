# Data model — the revision watermark

One column. No new table, no new index, no change to any existing column's meaning.

---

## `channels.revision_sequence`

| | |
|---|---|
| **Type** | `bigint not null default 0` |
| **Migration** | `0015`, hand-written, reviewed against SAD §6.1 |
| **Writers** | `editMessage` and `deleteMessage`, one UPDATE each, inside the transaction that applies the revision |
| **Readers** | the api's membership resolution, on `/internal/session` |
| **Meaning** | how many revisions this channel's messages have received |

**`bigint`, matching `channels.last_sequence`.** A channel revised once a second for a century
reaches 3.2 billion, which overflows `integer` and does not trouble `bigint`. The existing
sequence column made the same choice for the same reason.

**`not null default 0`.** Every channel that exists when the migration runs starts at zero, and
the spec's Assumptions record why: a count reconstructed from `message_edits` and `deleted_at`
would be correct and useless — it would exceed every client's stored count on the first
reconnect after the change ships, and tell every client to repair every channel once.

**It rises by exactly one per revision (FR-002).** Not by the number of messages affected, not
by a timestamp. An edit is one, a deletion is one, and a message edited three times contributes
three.

**A send does not raise it (FR-011).** A new message is delivered by the ordinary replay. Raising
the count for a send would make every active channel report a repair after every absence, which
is the same herd R3 avoids from the other direction.

### State transitions

    created           revision_sequence = 0
    message edited    revision_sequence = revision_sequence + 1
    message deleted   revision_sequence = revision_sequence + 1
    message sent      unchanged
    channel archived  unchanged
    member added      unchanged

**Monotonic, and never reset.** FR-002 forbids it falling. There is no path that lowers it and
none is added — a reset would silently tell every client it was up to date.

---

## Transport shapes

The count is carried in three places and stored in one. None of these is a new entity; each is
a field on a payload that already exists.

### `/internal/session` response — api to gateway

`channel_revisions: Record<channel_id, count>`, alongside the existing `channel_ids`.

**A parallel map rather than a widened array.** `channel_ids: string[]` is published by eleven
chapters; turning it into an array of objects would change all of them for a field they do not
use. The map's keys are a subset of `channel_ids` — equal in practice, and the gateway treats a
missing key as zero.

**`.default({})` for the deploy window**, following `banned`'s precedent in the same schema: an
api built before this feature still satisfies the schema during a rolling deploy, and the
gateway then behaves as it does today.

### `?rev=<channel_id>:<count>` — client to gateway, on the upgrade URL

Repeated, one per channel the client holds a count for. Parsed with the same rsplit rule as
`cursor`, for the reason `resume.ts` already gives: a colon inside a channel id must not
truncate it.

**Absent is not zero.** Absent means "this client does not participate", which R3 distinguishes
from a first connection and from a count of zero.

### `connection.ack.payload.revisions` — gateway to client

`Record<channel_id, count>`, the platform's current count per channel the client belongs to.

**Sent whether or not a repair is needed**, so a client can store the baseline it will compare
against next time. A response that carried only the channels needing repair would leave a client
that needed none with nothing to store, and it would never establish a baseline.

**Validated by a new `revisionCountSchema`, not by `cursorSchema`.** The existing one is
`.positive()` and cannot express zero — see research R4.

---

## What is deliberately not modelled

- **No per-message revision record for transport.** `message_edits` already stores the edit
  history and this feature does not read it. Per-message precision is the larger change the
  spec excludes by name.
- **No client-side state in the platform.** The count a client holds lives with the client. The
  platform stores its own and compares on request.
- **No index.** The count is read by primary key on a row the membership query already joins.
  An index would serve no query that exists.

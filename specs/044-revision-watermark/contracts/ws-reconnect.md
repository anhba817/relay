# Contract — the reconnect handshake

The public half of this feature. A customer's client reads these, so they are contract rather
than diagnostics and cannot be renamed later without a version.

---

## Request — the upgrade URL

    ws://…/v1/ws?token=<token>&cursor=<channel_id>:<seq>&rev=<channel_id>:<count>

`cursor` is unchanged. `rev` is new, repeated once per channel the client holds a count for,
and parsed by the same rule: **split on the LAST colon**, because a channel id is opaque and may
contain one.

| `cursor` | `rev` | Meaning | Repair signalled |
|---|---|---|---|
| absent | absent | a first connection | no |
| present | absent | a client that predates this feature | **no** |
| present | present | an upgraded client | per channel, where the platform's count is higher |
| absent | present | a client sending counts without cursors | treated as a first connection; `rev` ignored |

**A `rev` that omits one channel is the same rule, one level down.** A client that sends counts
for the channels it holds and nothing for a channel it joined during its absence gets no repair
signalled for that channel — it held nothing there to be stale, and the channel's messages arrive
by the ordinary replay. FR-007 covers all three absences as one rule.

**The second row is the one to get right.** Treating an absent `rev` as zero would tell every
un-upgraded client that every channel with any revision needs repair — on every reconnect, and
most loudly during the deploy window when the fleet is reconnecting anyway.

**A malformed `rev` degrades rather than refuses**, matching `cursor`'s existing contract: a
client whose stored state got corrupted can recover by refetching, and a client closed at the
door can only reconnect and be closed again.

---

## Response — `connection.ack`

    {
      "type": "connection.ack",
      "payload": {
        "user": "…",
        "cursor": { "<channel_id>": 42 },
        "resume_ok": true,
        "truncated": [],
        "revisions": { "<channel_id>": 7 }
      }
    }

`revisions` carries the platform's current count for **every** channel the user belongs to,
including channels at zero and channels the client asked nothing about.

**Every channel, not only the changed ones.** A client that needs no repair still needs a
baseline to store, or its next reconnect has nothing to compare against.

### What a client does with it

For each channel, compare the count in `revisions` with the one it holds:

    platform > held    one or more messages this client already has were edited or deleted
                       while it was away. Re-read that channel's history to repair.
                       The difference is how many revisions were missed.

    platform == held   nothing missed. No read.

    platform < held    treated as nothing missed. The platform does not refuse the
                       connection over a number the client supplied — a wrong repair is
                       worse than a missing one, and refusing would be a denial of service
                       the client controls.

**Store the new counts either way.** A client that only stores counts when it repairs never
establishes a baseline for the channels it did not repair.

---

## Why the signal exists at all

Resume is ordered by the channel sequence, and a revision carries the sequence of the message it
changes rather than a new one. A message revised **below** the client's cursor is in neither the
replay nor the live stream, and **consumes no sequence, so no gap appears** — SRS FR-016b names that
as tripping no existing client-side detector.

SRS FR-016a already says the stale copy is repairable by re-reading history. This is the signal that
tells a client when to.

**Measured window**: the default connect limit is 3,000 per minute against a gateway that
accepts 1,125-1,675 per second, so on a rolling restart the last client to reconnect waits
**3 minutes 20 seconds** (`docs/11-scalability-measurement-2026-09-06.md`). Every revision in
that window, below that client's cursor, is invisible to it without this signal.

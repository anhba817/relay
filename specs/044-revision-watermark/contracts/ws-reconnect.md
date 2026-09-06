# Contract — the reconnect handshake

The public half of this feature. A customer's client reads these, so they are contract rather
than diagnostics and cannot be renamed later without a version.

---

## Request — the upgrade URL, unchanged

    ws://…/v1/ws?token=<token>&cursor=<channel_id>:<seq>

**A client sends nothing new.** A draft added `?rev=<channel_id>:<count>` so the platform could
compare and answer with the stale channels; it was built and removed, because the ack already
carries every count and a client can compare against its own. **A parameter the server parses
and never acts on is a contract it can never remove.**

The cursor format is untouched, which also means the rsplit rule stays intact: `parseCursors`
splits on the LAST colon because a channel id is opaque and may contain one, and a
`<channel>:<seq>:<rev>` entry would have parsed `rev` as the sequence — every resume silently
resuming from the wrong place, producing plausible numbers rather than an error.

| Client | What it holds | What happens |
|---|---|---|
| a first connection | nothing | receives every count, stores them, repairs nothing |
| built before this feature | nothing | ignores the new field entirely; behaviour unchanged |
| upgraded, all counts match | its stored counts | repairs nothing |
| upgraded, one count lower | its stored counts | re-reads that channel's history |
| upgraded, no count for a channel it just joined | nothing for that channel | repairs nothing, stores the reported count |
| upgraded, a count higher than reported | a stale or invented number | repairs nothing; the platform refuses nothing |

**The last two rows are one rule** and the platform enforces neither: it reports, the client
decides. That is why the rule lives in this document rather than in the gateway.

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

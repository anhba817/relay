# Contract — the chapter map

The public half of this feature. Every old chapter URL is linked from somewhere this project does not
control, so the mapping is contract rather than bookkeeping.

**One source, two consumers.** The table below generates the redirects in `next.config.ts` and the
published mapping page. It is not maintained in two places, because a hand-maintained table cannot be
checked — this project's own finding from nine api ports drawn from hand-allocated bands.

---

## The eight movements

| | Movement | Why it is one thing |
|---|---|---|
| **I** | The tenant, the credential, and the vocabulary | Who is calling, proved; and the error vocabulary every later chapter adds to |
| **II** | One event, written once | The outbox, the broker, and the deduplication window — the backbone every later chapter publishes through |
| **III** | The domain a customer can use | Channels, control, users, senders. The product |
| **IV** | The socket, continued from Part 2 | Delivery, presence, revocation, typing, the connection cap |
| **V** | The message, revised | Edits, deletions, attachments |
| **VI** | Someone else's system | Webhooks, retries, and the mail the retry chapter owed |
| **VII** | What it costs | Rate limits, quotas, connection-minutes |
| **VIII** | The verdict | The isolation gauntlet, then an outsider |

## The map

| New | Movement | Title | Was |
|---|---|---|---|
| 3.1 | I | Tenants all the way down | 3.1 |
| 3.2 | I | Keys and tokens | 3.2 |
| 3.3 | I | Errors that resolve | **3.14, first half** |
| 3.4 | II | The outbox | 3.3 |
| 3.5 | II | JetStream, and the grammar a subject needs | 3.4 |
| 3.6 | II | Commit and publish are two instants | 3.7 |
| 3.7 | III | The endpoints and the instruments | 3.13 |
| 3.8 | III | The channel a customer controls | 3.15 |
| 3.9 | III | What a user sees | 3.16 |
| 3.10 | III | The sender a message never had | 3.17 |
| 3.11 | IV | The message that never arrived | 3.18 |
| 3.12 | IV | Who is allowed to see it | 3.19 |
| 3.13 | IV | The membership that changed | 3.20 |
| 3.14 | IV | The frame nobody may send | 3.21 |
| 3.15 | IV | The sixth connection | 3.22 |
| 3.16 | V | The words somebody wants back | 3.23 |
| 3.17 | V | The message that is not only text | 3.24 |
| 3.18 | VI | Webhooks that survive the customer | 3.5 |
| 3.19 | VI | When to stop trying | 3.6 |
| 3.20 | VI | The email nobody was sending | 3.9 |
| 3.21 | VII | Limits you can see coming | 3.8 |
| 3.22 | VII | Quotas and what they cost | 3.10 |
| 3.23 | VII | Counting a connection | 3.11 |
| 3.24 | VIII | Milestone: the isolation gauntlet | 3.12 |
| 3.25 | VIII | Milestone: an outsider | **3.14, second half** |

**Twenty-four becomes twenty-five**, because one chapter splits. Its two halves belong at opposite
ends: the error registry is needed by every chapter that adds a refusal, and ten chapters currently
add codes to a registry the reader does not meet until chapter fourteen. The outsider is the SRS
Phase 2 exit criterion — *"an external developer integrates using only public documentation, with no
assistance"* — and nothing may follow it.

**Four chapters keep their number and change meaning.** 3.13, 3.14, 3.15 and 3.16 all exist before and
after this feature and name different chapters. That is the strongest argument for the named-reference
rule: an ordinal that survives a reorder pointing at different content is worse than one that breaks.

## Redirects

Every old path resolves. The slug travels with the chapter, so only the numeric segment moves:

    /part-3/chapter-05/webhooks-that-survive-the-customer
      -> /part-3/chapter-18/webhooks-that-survive-the-customer          308

    /vi/part-3/chapter-05/webhooks-that-survive-the-customer
      -> /vi/part-3/chapter-18/webhooks-that-survive-the-customer       308

**48 redirects**, 24 per locale. Permanent rather than temporary: the old numbering is not coming
back, and a search engine that has indexed the series should be told so.

**The split chapter is the one redirect that has to choose.** `/part-3/chapter-14/…` was one page and
is now two. It redirects to 3.25, the outsider, because that is what the slug names — the registry
half arrives under a new slug at 3.3, and the mapping page is where a reader finds that.

## What a reader is owed

A page listing every old number against its new one, reachable from Part 3's index. Not a redirect
note, which only helps somebody who clicks an old link — a reader with the series open in another tab
and their own notes beside it needs to look up the mapping directly.

# Data model — chapter 4.10

One new table, one new configuration key, and one quantity that is deliberately **not** stored.

---

## Media object

A row per requested slot. It exists the moment a slot is issued and before any byte is uploaded,
which is the point: the platform's record of an upload is older than the upload.

| field | meaning |
|---|---|
| `id` | the `media_id` a client holds. Opaque — not a path into the store, so the storage layout can change without breaking a published contract |
| `environment_id` | the tenant. Constitution I, and the scoping predicate on every read |
| `user_id` | the uploader, **nullable**: an API key has no user, and FR-MED-06 later distinguishes the two cases |
| `filename` | as declared. Never used to build the object key |
| `mime_type` | as declared, and one of the ten FR-MED-02 allows |
| `declared_bytes` | as declared. **The quota arithmetic is over this**, not over anything verified — FR-MED-03 is a later chapter |
| `state` | `pending` here. `ready` and `rejected` arrive with the verification and scanning clauses |
| `object_key` | where the object lives in the store |
| `created_at` | when the slot was issued |

**Validity**

- `declared_bytes` is positive and within its kind's cap — image 10 MB, audio 25 MB, video 100 MB.
- `mime_type` is in the allowed set. The set lives in one place and both the refusal and the
  per-kind cap read it, because a MIME list that disagrees with itself refuses the wrong things.
- A row exists only for an **issued** slot. A refusal writes nothing (FR-009), so the table is not
  a log of attempts.

**State, and what this chapter does not add**

    (no row) ──issued──► pending
                            │
                            └──► ready | rejected      NOT THIS CHAPTER

`pending` is terminal here. A chapter that added `ready` without FR-MED-03's verification would be
claiming something it had not checked.

---

## Upload slot

**Not stored, and that is the design.** A slot is a URL and an expiry, derived from the media row
and the store's credentials at the moment of the request.

Storing it would mean two sources of truth for when it expires — ours and the store's — and R1
measured which one is authoritative: the store answers `AccessDenied · Request has expired`, from
its own clock, with nothing asked of us. Constitution IV, one level down.

---

## Storage commitment

The environment's committed bytes: **the sum of `declared_bytes` over its media rows**.

**A query, not a column.** A counter on `environments` would be a second source of truth for
something the rows already say. The cost is a sum per slot request, which at this chapter's scale
is nothing — and the plan says that rather than claiming it measured a million rows.

**Read and written in one transaction.** The check reads the sum and the insert adds to it;
unserialised, two slots race the same remaining allowance and both are issued. The chapter
publishes the transaction and says what the alternative costs, because a reader who copies a
read-then-write quota check ships the race.

**AND IT IS NEVER RELEASED IN THIS CHAPTER.** A slot nobody uploads to holds its declared bytes
indefinitely. FR-MED-10's scheduled job is 24 hours and about *unreferenced* media, not *unused
slots*, so nothing here reclaims it. Recorded rather than closed.

---

## Quota configuration

`quotaConfigSchema` gains a fourth key. It is `.strict()`, and its own comment says why: *"a
dimension nobody implemented is a parse failure rather than a silently ignored cap."*

| dimension | quantity | shape |
|---|---|---|
| `messages` | messages sent | flow, per calendar month |
| `active_users` | unique active persons | flow, per calendar month |
| `connection_minutes` | connection-minutes | flow, per calendar month |
| **`storage_bytes`** | **stored bytes** | **level — the current sum, not a monthly total** |

**The fourth row is a different kind of thing and the clause has to say so.** `usage_periods` is
keyed `(environment_id, period)` and `creditFor` accumulates within a period without ever
subtracting. Storage in that row would have to subtract on delete, and would reset on the 1st —
so a tenant holding 100 GB would start each month at zero. The **cap** is configuration and sits
with the other caps; the **accounting** is the sum above.

**The parser and the migration's `CHECK` change together**, because the constraint would otherwise
accept a config the parser rejects, `capsFor` fails closed, and the cap would silently become no
cap. Both halves are probed (049's rule about a pin that cannot fail).

---

## Error codes

Four, and none of them is `quota_exceeded`.

| code | condition | permanent? |
|---|---|---|
| `media_type_not_allowed` | the declared MIME type is outside the ten FR-MED-02 permits | yes |
| `media_too_large` | the declared size exceeds the cap for its kind | yes |
| `media_storage_exhausted` | issuing the slot would take the environment past its storage cap | yes |
| `media_storage_unavailable` | the object store cannot be reached | **no** |

The fourth is `docs/05-sad.md:1062`'s degradation row, which FR-MED-02 does not carry and
`docs/12`'s brief counted. **It is the only transient one**, and that is the whole reason it
cannot share a code with the others or fall into `internal_error`: retry is right for exactly one
of the four.

`codes.ts` already refuses the reuse twice. `channel_member_limit_exceeded` carries *"NOT
`quota_exceeded`. That is a monthly, billable, resets-on-a-date refusal whose message promises a
resume date"* — and **a storage cap does not reset on a date**, which is the same objection one
dimension over. Each new entry names its near-neighbour in a comment, as the registry does.

# Gaps — what these two chapters refused, and who owns each

Chapter 3.12's close-out kept this file for the same reason: a thing left undone with an owner
is a decision, and a thing left undone without one is a surprise for whoever finds it.

---

## 1. Presence is a declared frame with no sender — FR-RTM-07

`presenceChangedSchema` is in the protocol's frame union and **nothing emits it.**

Research R16 deferred presence "in scope only as far as: a non-member's socket is not
subscribed, so it receives no presence for it" — and that claim is **vacuously true**, which is
worse than false. A reader takes it as "presence flows and is scoped"; the truth is that no
presence flows at all, so scoping it is untested because it is untestable.

Corrected in the research note rather than left to read as though presence worked.

**AND PRESENCE IS THREE CLAUSES, NOT ONE, ALL OF THEM P1:**

    FR-RTM-05   emit real-time events for message creation, edit, deletion,
                membership change, PRESENCE CHANGE, and typing
    FR-RTM-06   track presence as online/offline from connection state,
                with a 30-second grace period
    FR-RTM-07   presence updates delivered only to users sharing at least one
                channel with the subject

Two things follow that were not visible while this was filed as one deferred item.

**FR-RTM-05 is a single clause covering message events AND presence AND typing.** So gap 2
(a REST-sent message reaches no socket) and this gap are two halves of one requirement, not two
separate deferrals. Splitting them across parts of the book means one clause delivered twice,
years apart.

**FR-RTM-07's scoping rule is a membership-graph query** — "users sharing at least one channel
with the subject" — which is precisely what chapters 3.15 and 3.16 built. Presence could not
have been written before Part 3 and is cheapest immediately after it.

**And it completes FR-CHN-05's third verb.** That clause reads "shall not read messages from,
send messages to, **or observe presence in** a private channel" — this feature delivered two of
the three, and `traceability.md` claimed all of them until this was checked.

**Owner: chapter 3.19.** There is no home for it anywhere else in the plan. Part 4 is
Phase 3 (ClickHouse, media, moderation); Part 5 is the SDK and dashboard, which *consume*
presence rather than build it; Parts 6 and 7 ship and run what exists. Three P1 clauses with no
chapter in any part is the same shape as the deferred surface Part 3 has just spent two chapters
absorbing.

**One open architecture question rides on it**, unresolved since the SRS: *"Should presence be
opt-in per channel to reduce fan-out at scale?"* (FR-RTM-07, NFR-SCL-01). That decision belongs
in presence's chapter, and Part 7's load test is where it would be measured.

## 2. A REST-sent message reaches no socket — FR-RTM-05

Two independent causes, both recorded by chapter 3.12 and neither closed here: the api publishes
to no fan-out, and the public REST send attributes no user, so `toFrame` drops the row from a
resume.

This feature made the second cause **narrower and did not remove it.** The public send now
resolves its caller and threads a user id — that was necessary for FR-CHN-05's membership check
— so an attributed REST send does now produce a frameable row. The first cause stands: nothing
publishes it.

**Owner: chapter 3.18**, once chapter 3.17 has given every message a sender. `public-surface.itest.ts` pins the current behaviour, and this
feature's Phase 13 walked into it — a test awaited a frame in a suite where none has ever
arrived, and timed out.

## 3. The outbox keeps message text for ever — FR-MOD-06, DR-06, FR-MSG-08, FR-TEN-08

`drainOutbox` sets `published_at` and never deletes. Nothing in the api deletes a row from any
table. The payload copies `data.text`. **286,871 rows in the test lane**, each holding a copy of
a message body that the messages table also holds.

Untouched by this feature and the count has grown. The fix is a one-line prune and **not** the
tenant column an earlier draft proposed: the outbox's legitimate mutation *is*
cross-environment, so a tenant column would make feature 030's guard refuse the relay's own
sweep. Recorded in `db/catalogue.ts`'s SPINE comment.

**Owner: FR-MOD-06's chapter.**

## 4. `messages.deleted_at` has a reader and no writer — FR-MSG-08

The mirror image of this feature's own subject. Four columns had writers and no readers; the
tombstone has a **reader and no writer**: `backfill.controller` passes `text` straight through
so a null already reaches the wire, and nothing in the platform writes either
`messages.deleted_at` or a null `text`. There is no message-deletion route.

The listing's rule for a tombstoned last message is implemented and tested against a state
written by raw SQL, so the day FR-MSG-08 ships the count and the preview already agree.

**Owner: FR-MSG-08's chapter.** New in this feature's record, because implementing FR-019
required deciding what a state nothing produces should look like.

## 5. `read_positions.updated_at` — this feature's own dead column

Written by every position write, read by nothing. A feature whose subject was columns nothing
reads leaves exactly one behind, and it is one it added.

The count went three → two → one during specification: `users.deleted_at` had no reader until
analysis pass five, and `members.role` was called dead until pass fourteen noticed the listing
returns it — *returning a column is reading it*, which made the statement sharper rather than
weaker. `updated_at` survived every pass because nothing needed it. An audit field with no
auditor.

**DECIDED: kept as it is.** The two options were a reader — an operations view answering "when
did this user last catch up" — or a migration that drops it. The column stays, on the
expectation that the reader arrives later.

Recorded as a decision rather than left open, because the two states look identical in the
schema and only this line tells them apart. A column nobody chose to keep and a column somebody
chose to keep are the same column until somebody writes down which one it is — and this
feature's whole subject is what happens when that sentence never gets written.

**What that costs, stated so the next reader is not surprised:** the count of columns with no
reader does not go to zero at the end of a feature about columns with no readers. It goes to
one, deliberately, and the one is ours.

## 6. The SRS's `docs_url` clause was touched and unclaimed

The gateway discarded every api refusal code but 401, so `user_banned` and `channel_archived`
reached socket clients as `internal_error` and the `docs_url` chapter 3.14 built never existed
for them. Fixed in Phase 15, and **no requirement in this spec asked for it.**

Recorded in `traceability.md` §2 rather than back-filled into a requirement: a requirement
written after the work to describe the work is not a requirement. Chapter 3.12's map found four
clauses touched and unclaimed; this is one, which is the direction to want.

## 7. Three files are permanently outside the fence chain

`sentinel.ts`, `sentinel.sql` and `guard.itest.ts` are excerpt-only, so **no checker compares a
single character of them to what any chapter shows.** `sentinel.ts` grew 32 lines in this
feature and nothing verified it.

T187a said the appendix amends the latter two. It does not — it mentions them inside *other*
files' fences, and a mention inside a fence body is not a claim on that path. So the premise was
wrong and the consequence is real.

The reason each is outside is a real one: the guard's SQL is 400 lines of PL/pgSQL no chapter's
word budget can carry whole. **Owner: whoever next changes the guard**, and the cheapest fix is
a post-series entry titling all three.

## 8. AND THE ONE THIS FEATURE DID NOT USE EITHER: a person reading the documentation

Chapter 3.14 named this as the instrument its own milestone verdict lacked. *"Content
sufficiency is not comprehensibility: a person is the only instrument for the second and this
chapter did not use one."*

**This feature did not use one either.** Two chapters, 6,747 prose words, 58 fences, four
figures, both locales — and every check applied to them is mechanical: the fence chain compares
bytes, `check:docs` compares mirrors, `check:figures` compares props, `check:errors` compares a
registry. Not one of them can tell whether a reader following chapter 3.16 ends up with a
working listing.

The 145× measurement is the argument for why that matters here specifically: **an instrument
that is easy to run tells you what it measures, not what you wanted to know.** The test lane
answered 0.87 ms honestly. Every checker in this repository answers honestly about bytes.

Recorded as a gap rather than an intention, because naming it twice in three chapters without
acting is a pattern, and the pattern is the finding.

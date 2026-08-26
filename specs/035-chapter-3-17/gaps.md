# Open things — chapter 3.17

Nine, each with an owner. Eight are carried forward from the last feature with their status
re-checked rather than copied; one is new and is the only item here whose mechanism is unknown.

## 1. A twenty-six-run battery failed once, and the mechanism is not identified — NEW

**Owner:** whoever next touches `services/api/src/quotas/quota-relay.ts`.

Run 14 of 26 failed on `quotas.itest.ts > "cannot fail a send when the mail server is gone"`:

    expect(await down.drainOnce()).toBe(0)     with mailer smtp://127.0.0.1:1
    AssertionError: expected 14 to be +0

`drainOnce`'s own comment says what should happen: *"A mail server that is down produces one
of these per claimed row and then a drain of zero."* It returned 14 — fourteen rows reported
delivered by a mailer that cannot deliver.

Ruled out: this chapter's T047c leaves no notification rows (0 undelivered after the suite);
the suite does not flake standalone (6 runs, 26/26 each); the failing test is one this chapter
never modified; nothing else ran on the machine. Six further full-lane runs after it were
green, so the rate is around 3.8% (1 in 26) with a 95% upper bound near 19% at that sample.

**Not fixed, deliberately.** Changing code until a symptom stops, with no mechanism in hand,
is how a real defect gets buried. The most likely shape is a relay loop still running from an
earlier test in the same file, delivering rows this one then counts — untraced.

## 2. Presence is a declared frame with no sender — FR-RTM-05, FR-RTM-06, FR-RTM-07

**Owner:** chapter 3.19. Carried forward; **still open, and now it has a chapter.**

FR-CHN-05 has three verbs — read, send, observe presence — and the third has never been
built. Checked again this feature rather than assumed: the only occurrence of "presence" in
`services/gateway/src` is the English word, in a comment about cursors. This chapter's
traceability records the clause as two of three, which is the third correction of that row.

## 3. A REST-sent message reaches no LIVE socket — FR-RTM-05

**Owner:** chapter 3.18. Carried forward, **and half closed by this chapter.**

    on resume          NOW ARRIVES     every send carries a sender, so toFrame keeps the row
    live delivery      still nothing   only the gateway publishes to the fan-out

Chapter 3.12's `gaps.md` G1 listed two independent mechanisms; this chapter removed one. That
record is amended in place, because a reader who finds the old heading needs to know it is now
half true.

## 4. The outbox keeps message text for ever — FR-MOD-06, DR-06, FR-MSG-08

**Owner:** unassigned. Carried forward; untouched by this chapter.

## 5. `messages.deleted_at` has a reader and no writer — FR-MSG-08

**Owner:** unassigned. Carried forward, and this feature found the clause behind it.

FR-MSG-08 says a tombstone shall retain "sequence number, **author**, timestamps, and
deletion metadata". The author half now agrees with FR-MSG-15 and neither half is built —
nothing writes a tombstone. Found by T000 reading §4.5's clauses rather than its identifiers,
which is the same read that found FR-MSG-13.

## 6. `read_positions.updated_at` — the last feature's dead column

**Owner:** unassigned. Carried forward; **still no reader.**

And this feature added a second of the same kind: a bot's `read_positions` row is written by
nothing and read by nothing, because nothing acknowledges on a bot's behalf. Not a new dead
column — an existing table holding a row that will never exist.

## 7. Three files are permanently outside the fence chain

**Owner:** unassigned. Carried forward, and this feature adds seven more of a different kind.

The three excerpt-titled files (`sentinel.ts`, `sentinel.sql`, `guard.itest.ts`) are outside
the chain by construction. Separately, **seven files this chapter changed are claimed by no
chapter at all**, so `check:fences` cannot see them:

    README.md            the file an outsider is told to read
    limits.itest.ts   history.itest.ts   idempotency.itest.ts
    event.test.ts     quotas.itest.ts    gateway/limits.itest.ts

The README is the one that matters: chapter 3.17 made it the quickstart of record, and no
chapter teaches it and no checker verifies it.

## 8. No checker reads prose — NEW SHAPE of an old gap

**Owner:** unassigned, and a checker is **not** the recommendation.

Chapter 3.10 carried a `<Trap>` for seven chapters whose title was false and whose body
argued against this chapter's decision. It passed `check:fences`, `check:figures`,
`check:docs` and `check:srs`, because none of them reads a sentence. It was found by a person
reading during analysis pass 15, and chapter 3.13's stale seam reason with it.

A prose checker is the wrong fix. `check:figures` reported 122 false problems in 193 figures
on its first run, and natural-language claims are where crying wolf does the most damage. The
practice that worked is a `grep` per reversed claim, classified by hand: nine hits this
feature, two wrong.

## 9. A person reading the documentation — the instrument nobody used

**Owner:** unassigned. Carried forward from chapters 3.14, 3.15 and 3.16, **and this feature
narrowed it by accident.**

The sealed outsider carried a test that had been red since chapter 3.15 — it asserted
`POST /v1/channels {type:"private"}` returns 400, and `43899e3` made the route accept
`private`. Two chapters closed with that suite unrun, because `pnpm test:outsider` is its own
lane and `test:integration` filters it out by name. **The one suite that stands for an
external developer was wrong about the API for two chapters and nobody looked.**

That is the strongest argument yet for the item, and it is still open: the fix here was to run
the suite, not to arrange for it to be run.

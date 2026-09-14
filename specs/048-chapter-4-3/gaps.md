# Gaps — chapter 4.3

Filed rather than fixed. Each says what was measured, why it is not this chapter's work,
and what would close it.

---

## 048-1 — DR-10 AND FR-ANL-06 STILL CANNOT BOTH HOLD (carried from 047-1)

Two independent reasons, both measured in chapter 4.2 and neither touched here.

**The TTL boundary, at any cardinality.** Comparing the rollup against the raw table day by
day, both sides windowed: 91 days compared, **90 agree exactly, 1 differs by 4,941** — the
oldest day in the window, every time, because the TTL cuts at a timestamp and a daily
rollup's finest grain is a day. That is **0.49% against FR-ANL-06's 0.1%**, and no corpus
size hides it.

**`uniq` above ~65,000 distinct.** Exact to 65,000, off by 0.5129% at 70,000. The threshold
is a cardinality, not a row count.

Closing it means choosing: widen the tolerance, exempt the boundary day, keep an exact
distinct column, or let reconciliation read raw events and amend DR-10. **There is still no
reconciler to test an amendment against**, which is the whole reason it stays open.

---

## 048-2 — `message_events.delivery_latency_ms` STILL HAS NO PRODUCER (carried from 047-2)

SAD §6.2 publishes it; nothing writes it. It is `Nullable(UInt32)` so that an absent
producer writes NULL rather than asserting every delivery took 0 ms.

**And this chapter added a column that will be mistaken for it.**
`webhook_attempts.latency_ms` is how long an *endpoint* took to answer a webhook;
`message_events.delivery_latency_ms` is how long a *message* took to reach a client. The
chapter says so in its `<ForwardRef>` because the names are two words apart and the meanings
are not.

---

## 048-3 — `vitest.coverage.config.mts` CANNOT TAKE A FENCE

The coverage pins this chapter added amend it, and it is fenced in **eleven** chapters — but
the chain replays **317 lines where the tree holds 944**. Measured against the commit before
Phase 5, the divergence was **591 lines before this chapter touched it**. A hunk cannot
anchor on that, and regenerating the file is the 111 → 203 trap 045 recorded.

Identical in shape to 047-4's `eslint.config.mjs`, which suggests the class rather than the
instance is the thing to fix: **the chain's largest inherited HEAD problems are
configuration files that every chapter edits and no chapter owns.**

---

## 048-4 — THE ROLLUP IS STILL UNBOUNDED (carried from 047-3)

`daily_usage` carries no TTL, deliberately — metering must not lose history when raw events
expire. It also grows at `environments × days` forever, and no clause says how long metering
history is kept. Not this chapter's to decide.

---

## 048-5 — NO GATE CHECKS THAT A CHAPTER'S TAG MATCHES THE CHAPTER (carried from 047-6)

`check-fence-chain` replays chapters onto the working tree and compares against `HEAD`. It
never resolves a tag. That is how three Part 1 tags pointed at a superseded lineage through
every green run, and how `turbo.json` at chapter 1.1 matches neither lineage.

`relay-platform/README.md:8` promises *"Every tag is a runnable, tested state: check it out
and the toolchain checks pass."* Nothing checks it.

---

## 048-6 — CLOSED: A STREAM RECREATED ON A BROKEN STORE IS BROKEN TOO, AND SAYS NOTHING

An abrupt `docker compose down` mid-write left the `EVENTS` stream unrecoverable:
`JetStream stream '$G > EVENTS' could not be recovered`. The broken store was renamed in
place to `EVENTS.broken-20260914` and `EVENTS` was recreated with the platform's own
`ensureStream`. All three streams then worked, and every measurement in this feature ran
against that broker.

**THIS ENTRY'S FIRST VERSION WAS WRONG ABOUT BOTH HALVES, AND CLOSING IT IS WHAT FOUND
OUT.** It recorded the broken store as moved to `/data/quarantine/EVENTS.broken-20260914`
and proposed `rm -rf /data/quarantine` as the remedy. `/data/quarantine` was **empty** —
the move into it had failed and the rename happened inside the streams directory instead —
so the recorded remedy would have deleted nothing and reported success. **A remedy nobody
runs is a remedy nobody checks**, and this one was written from what was attempted rather
than from what the directory held.

**AND REMOVING THE REAL CULPRIT DID NOT RESTORE HEALTH.** With `EVENTS.broken-20260914`
gone, `/healthz` reported the identical error for **`EVENTS` itself** — the stream
`ensureStream` had recreated. The replacement was written while the server's JetStream
store was already failing recovery, and it inherited the failure: 96K of `meta.inf`,
`meta.sum`, `msgs/index.db`, `msgs/1.blk` and six consumer directories that the server
would not read back. `jsz` stopped listing `EVENTS` at all while the directory sat on disk.

**EVERY INSTRUMENT SAID IT WORKED.** `ensureStream` returned. `streams.info` answered with
the right subjects and retention. Publishes and consumes ran through it for three phases.
The store's inability to survive a restart was invisible until something restarted — which
is this chapter's own lesson arriving one layer below the chapter: **a component verified
only in the state it was created in is verified in one state.** The ingester's dedup token
failed the same way, and so did the `attempted_at`/`ts` rename.

**THE FIX WAS THE SAME ACT, DONE ON A CLEAN STORE.** `EVENTS` moved out of
`/data/jetstream/$G/streams/`, NATS restarted to `{"status":"ok"}`, then the same
`ensureStream` call — `events.>`, `max_age` 604800s, `discard old`. Verified by a
**deliberate restart**, which is the check the first recreation never got:

    healthz {"status":"ok"} · container healthy
    ANALYTICS   37 messages · consumers 1
    DELIVERIES  69 messages · consumers 11
    EVENTS       0 messages · consumers 0

The two real streams kept their contents across all of it; `--no-deps` is no longer needed
and `docker compose --profile services up` passes its dependency gate again.

**AND THE HEALTH CHECK DID ITS JOB TWICE.** It went red for a real reason on a genuinely
broken stream, stayed red when the obvious culprit was removed and the problem was not,
and went green only when the store could actually be read back. That is more than the
ClickHouse check managed for sixteen chapters — and the difference is that this one asks a
question whose answer can be no.

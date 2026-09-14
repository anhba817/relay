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

## 048-6 — THE NATS HEALTH CHECK IS RED, AND THE SERVICES RUN AROUND IT

An abrupt `docker compose down` mid-write left the `EVENTS` stream unrecoverable:
`JetStream stream '$G > EVENTS' could not be recovered`. The store was moved to
`/data/quarantine/EVENTS.broken-20260914` inside the `nats-data` volume and `EVENTS` was
recreated with the platform's own `ensureStream`, so all three streams work and every
measurement in this feature ran against a functioning broker.

**The quarantined directory is still scanned**, so `/healthz` reports unavailable and
`docker compose --profile services up` fails its dependency gate. Phase 4 onward ran the
services with `--no-deps`.

Clearing it needs a delete inside the data volume. Closing this is one
`docker compose exec nats rm -rf /data/quarantine`, or recreating the `nats-data` volume —
which would discard the lane debris this feature already drained into ClickHouse.

**And the health check did its job.** It went red for a real reason, on a stream that was
genuinely broken, which is more than the ClickHouse check managed for sixteen chapters.

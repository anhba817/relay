# Part 4 — Everywhere the data went

**Status:** grooming record, written before `/speckit-specify`. Nothing here is built.
**Supersedes:** `docs/07-tutorial-plan.md` §"Part 4 — The second data path", which is stale
in its name, its chapter count, and its boundaries. **Amending that section is task one**,
because two records of one structure disagree by default and this project has paid for that
four times.

---

## 1. What this part is

Three blocks of material that the SRS keeps apart and the tutorial should not: the
analytical store, hosted media, and the moderation lifecycle.

The argument that holds them together is that **each one moves data off the path everything
else takes** — analytics leaves through a deliberately lossy stream, media bytes never enter
Relay compute at all — and the part ends by asking what that costs. Compliance erasure
(FR-MOD-04) deletes messages, memberships, profile, **media objects, and analytical rows**.
It is the one chapter that has to know every path the data took, and it can only be written
after all three exist.

**That is why this is one part and not two.** A split at the media boundary puts erasure in a
part that never taught two of the three paths it must reach.

---

## 2. The three decisions taken during grooming

### 2.1 Chapter addresses keep the global ordinal

    /part-4/chapter-11/the-upload-that-never-reaches-us

Consistent with Parts 0–3. The known cost is that every chapter which splits at its word
ceiling renumbers the tail: ~19 URLs and ~38 redirects for an insertion early in the part.

**This is affordable only because of two things, and one of them does not exist yet.** See §6.

The alternative considered and rejected was a slug-only address (`/part-4/the-upload-slot`),
which makes insertion structurally free because the slug is already the stable identity —
`the-message-that-is-not-only-text` survived 3.24 → new 18 unchanged. It was rejected for
consistency with the three published parts. **If §6's gates are not built, revisit this.**

### 2.2 The part is named *Everywhere the data went*

The old name covers movements I–IV and stops. This one covers all three blocks and its
meaning only completes at movement VII, which is the structure working as intended.

**The name is a promise the last movement has to keep.** If erasure is deferred, the title
lies and must change with it.

Touches `docs/07-tutorial-plan.md` in two places — the §3 arc table and the Part 4 heading —
and `lib/tutorial.ts`'s `partTitle`, which is locale-aware and needs a Vietnamese title.

### 2.3 Milestone 1 makes two claims, not one

FR-ANL-06 wants metered totals to agree with operational counts **within 0.1%**. The lane's
largest membership set is five channels; 0.1% of a small number is an assertion that cannot
fail for its own reason, which is the defect class this project keeps finding — `gaps.md` and CLAUDE.md's
"tests that pass while proving nothing" carry the register.

So the milestone splits:

| half | claim | where |
|---|---|---|
| **CI gate** | a *planted* drift is detected and the reconciler raises | the lane, every run |
| **recorded measurement** | the 0.1% figure, at a volume where 0.1% is a real threshold | once, in the chapter |

The CI half is falsifiable and fails for its own reason. The recorded half follows the
precedent of `docs/11-scalability-measurement-2026-09-06.md`, which discharged NFR-SCL-01
the same way: its own document, the clause's own verification letter as the method, the
harness named.

**Two consequences for design, not for testing.** The reconciler must be callable in
isolation so a drift can be planted — that is a constraint on the chapter that builds it.
And `scripts/scale/` today generates connections and channels; it has no analytical-volume
mode and needs one. **That harness is a chapter-1 dependency, not a chapter-8 one** — §2.4's
demonstration needs it before the milestone does, and it must be introduced by the chapter
that first uses it (045-73: a file created by chapterless work has nowhere to be introduced).

**AMENDED 2026-09-17 (feature 054, the milestone chapter itself). Three of the four claims
above were falsified by building the thing they describe.**

**(1) The harness claim is stale in the direction nobody checks.** *"It has no analytical-volume
mode and needs one"* was true when this was written and stopped being true at chapter 4.2:
`corpus.mjs` and `load-analytics.mjs` build 1.6M messages in 92.4 s and load them into ClickHouse
in 1.2 s. **What the harness lacked was the OPERATIONAL side** — `usage_periods` appeared in
`corpus.mjs` exactly once, as a row count in its own closing report, and `usage_active_users` not
at all. §2.3 could not have anticipated that, because chapter 4.7 had not yet found every tenant
in the platform one-sided. The milestone's harness work was writing the counters, not the volume.

**(2) "The lane, every run" was never true, and the reason is not the one five artifacts gave.**
The planted-drift suite has run on every push since chapter 4.7 and passed. What had not been
true since chapter 4.4 is the gate's **colour**: `pnpm test:integration` was red on every run for
six failures that had nothing to do with metering, so a planted drift made a red run redder.
**The signal was not absent; it was indistinguishable.** And `--concurrency=1` stopped scheduling
at the first failure, so five other lanes had not run at all. Both are fixed at 4.9 (ADR-27), and
the gate now reports **suites executed against suites present** — 54 of 54 — because turbo's own
summary counts tasks and does not reproduce run to run.

**(3) The table's left column substitutes a schedule and does not say so.** *"The lane, every
run"* stands in the row whose claim is FR-ANL-06's *"daily job"*. A per-push check on a planted
fixture runs **more often** than daily and **reads no real tenant** — a different claim rather
than a stronger one. ADR-28 records that the daily job has no runner of any kind, and the
milestone's sentence is scoped to what runs.

**(4) What survived unchanged is the split itself**, and the argument for it turned out to be
sharper than written: at the lane's largest tenant-period the smallest expressible drift is
**0.197%, twice the bound**, so the recorded half had to happen at a built volume. It did, at
121,057 messages in one tenant-period, in `docs/13-metering-measurement-2026-09-17.md`.

### 2.4 Chapter 1's premise was wrong, and the true one is structural

`docs/07-tutorial-plan.md` specified chapter 4.1 as *"run the metering query against Postgres
under write load, watch it hurt."* **There is no metering query.** Verified at commit
`52766091`:

    services/api/src/quotas/credit.ts   high-water-mark arithmetic, nothing else
      creditFor(reported, credited)   -> max(0, reported - credited)
      highWaterMark(reported, credited) -> max(reported, credited)

No `count(`, `sum(` or `countDistinct` anywhere in the quotas module. Part 3's counters rise
on the send path — *"usage rises only on a send, so the send knows what it crossed"* — so
there is nothing to put under load and watch slow down.

**The true premise is a shape mismatch, and it is better.** The operational question is *give
me the next 50 messages in this channel after cursor X*. The analytical question (FR-ANL-05,
FR-ANL-09) is *messages and unique active users per environment per day, over 90 days*:

```sql
SELECT date_trunc('day', m.created_at), count(*), count(DISTINCT m.user_id)
FROM messages m JOIN channels c ON c.id = m.channel_id
WHERE c.environment_id = $1 AND m.created_at >= now() - interval '90 days'
GROUP BY 1;
```

A join and a scan, because **`messages` carries no `environment_id`** — tenancy is reached
only through `channels` — and **nothing indexes `created_at`**. SAD §6.2's ClickHouse table is
`ORDER BY (environment_id, ts)`: precisely the two columns the Postgres table orders by
neither of.

**So the chapter shows that two questions want two shapes and one table cannot have both**,
which is CON-01 as an artifact rather than a paragraph. Three measurements, in this order:

| # | measured | why it is the right thing to measure |
|---|---|---|
| 1 | the query's own time at volume | the analytical question's direct cost |
| 2 | **send p95 while it runs** | the neighbour effect, against NFR-PRF-02's published 150 ms |
| 3 | **denormalise `environment_id`, index `(environment_id, created_at)`, re-measure 1 and 2** | the query gets fast and **every write now pays for a question no write asks** |

Row 3 is the chapter's argument. Showing the query is slow proves little; **showing that the
fix is worse** is the thing that cannot be answered with "add an index."

**And it may not hurt enough.** A join-and-scan over a few million rows on a modern machine
may come in under a second. The honest response is to publish the volume reached and say what
it does not prove, the way NFR-SCL-01 was recorded rather than claimed. The fallback argument
needs no measurement: FR-ANL-01 wants an event per **API request**, not per message, and
90-day retention is `TTL ts + INTERVAL 90 DAY` against a partition-and-delete job.

#### The index facts are a premise to re-run, not a number to carry

The claim this rests on — *nothing indexes `created_at`, nothing reaches a tenant without a
join* — is load-bearing for movement I. **If it is false when the chapter is written, movement
I collapses and this document is wrong**, so it is recorded here as a premise with its
derivation rather than as a fact:

    sed -n '/export const messages = pgTable/,/^);/p' services/api/src/db/schema.ts

**The COUNT of indexes belongs to the chapter, not to this document.** "Exactly two" is true
of one commit, and a hand-carried count is the failure this project has already paid for —
the nine hand-allocated api ports, and 045-49's comment that counted its own file correctly
for exactly one commit. The chapter re-derives it at its own tag. This document carries the
structural claim and the command that settles it.

**Two things the chapter owns and this document should not pre-empt:**

- **The callback to chapter 2.4.** The schema's own comment reads *"No dedicated (channel_id,
  sequence DESC) index… Chapter 2.4 measured it and migration 0001 dropped the redundant
  twin."* The reader watched an index get measured and removed; 4.1 is where the bill arrives.
  That is writing, and it belongs to whoever writes it.
- **Whether row 3's counterfactual ships as a migration.** It must not. See §2.5.

### 2.5 The counterfactual is a probe, and probes have hygiene

Measurement 3 adds a column and an index in order to throw them away. **That is a red probe,
and a red probe writes to the lane** — 043 left two `javascript:alert(1)` rows behind and the
next measurement read them as pre-existing data contradicting the plan.

A discarded *migration* is worse than a discarded row: it enters `schema_migrations` and the
migration numbering, and §7.1 records that the numbering is an open question with a cautionary
history (045-69). So the constraint is on the method rather than on the prose:

**Measurement 3 runs on a throwaway database, seeded by the harness, never on the lane and
never at the chapter's tag.** The chapter fences no migration for it. What the chapter
publishes is the numbers and the `EXPLAIN`, not a schema change it then reverts.

---

## 3. The shape — seven movements, 22 chapters, three milestones

Chapter titles are provisional. Movement boundaries are not — they are what §5's rules
produce, and they are declared **before** chapter one exists, which is the whole payoff of
feature 045 being collected rather than paid for again.

```
    I    ch 1       The question one store can't answer
    II   ch 2–3     The second store
    III  ch 4–5     Everything else worth recording
    IV   ch 6–9     What you can now answer                      ★
    V    ch 10–12   Bytes we never touch
    VI   ch 13–17   The one service that reads them              ★
    VII  ch 18–22   The reckoning                                ★
```

**AMENDED 2026-09-13: 23 BECAME 22, AND THE SECOND CONTRACTION CAME FROM A CHAPTER DOING
MORE THAN ITS BRIEF.** Chapter 3 was *"A second store needs a second ledger"* and §7.1 said
to decide its identity scheme before chapter 2 was written. Chapter 4.2 decided it and
**built** it — runner, filename-and-checksum ledger, reporting idempotence, and a checksum
refusal tested red, all four items of chapter 3's brief, shipped at `part4-ch2`. Movement II
had one subject left, so the ingester moved up and every ordinal after 3 moved down one.
Milestones are at **9, 17 and 22**.

Movement I contracted the same way during grooming. **Both corrections ran downward, and
§3's warning that "23 will not be 23" has now been right twice in the direction it did not
predict.** The table below keeps the original ordinals in its first column so the
`gaps.md` and research references written against them still resolve; the movement column
is the stable address, as §2.1 intended.

| Ch | Mv | Title | Built |
|---|---|---|---|
| 1 | I | The question the counters can't answer | §2.4's shape mismatch, with the harness that makes it measurable. FR-ANL-05/09's query written against Postgres for the first time — a join and a scan, because `messages` carries no `environment_id` and nothing indexes `created_at`. Measurements 1 and 2: the query's own cost, and send p95 beside it against NFR-PRF-02's 150 ms |
| 2 | II | ClickHouse from zero | MergeTree, `PARTITION BY` (DR-07), `ORDER BY (environment_id, ts)` — the two columns chapter 1 showed Postgres orders by neither of — and TTL (DR-09). Schema only; nothing ingests yet |
| 3 | II | A second store needs a second ledger | **Open — see §7.1.** A migration runner and an identity scheme for a store whose DDL the Postgres runner cannot execute |
| 4 | II | The consumer that was promised | The ingester. Batching (DR-11), backpressure, and ClickHouse down → the stream absorbs 24 h (NFR-REL-05) |
| 5 | III | Every request is an event | FR-ANL-07's producer. Generalises the pattern chapter 3.20 already taught rather than introducing it — see §4 |
| 6 | III | The gateway's first stream | Connection open/close (FR-ANL-01). **The gateway had never touched NATS** — verified at the time, zero references in `services/gateway/src`, five dependencies and none a broker client. **What this line did not say is that the gateway already reported connection data**: `meter.ts` has shipped connection-minutes to `POST /internal/usage/connections` every sixty seconds since chapter 3.24. So the chapter is not *"the gateway has no way to report"* — it is *"the one it has was built for a different question and goes through the service the analytical path is supposed to be independent of"*. Amends ADR-07 a THIRD time, in both documents that hold it, and closes §7.2 |
| 7 | IV | Metering you can bill on | Daily rollup materialised views (DR-10). **One has existed since chapter 4.2** — `analytics/0001_daily_usage.sql`, a `SummingMergeTree` over `message_events`. What this line did not say is that **nothing reads it and nothing writes its source**: the only file that ever asked FR-ANL-05's question of the analytical store is `analytics/query.mjs`, referenced by no script, service or config, and `message_events` occurs in zero files under `services/` while `api_requests` holds 11,683 rows and `connection_events` 154. So the chapter is not *"build the rollup"* — it is **"the rollup satisfies DR-10 over a table that receives no events, and FR-ANL-09's channel dimension costs the billing read 525x"**. Two rollups ship, not one. Closes SRS Appendix C question 4 and records constitution III's conflict with the shipped platform |
| 8 | IV | The job that checks the meter | FR-ANL-06's reconciliation job, built to be callable in isolation (§2.3). **What this line did not say is that the job cannot pass, and that three of the four reasons are not the analytical path's fault.** Measured at chapter 4.7: `message_events` has no producer (100%); `uniq` is exact to **65,536** distinct and 0.5676% at 65,537; the raw-retention boundary makes the oldest day in any window disagree by **0% at midnight rising to 1.0989% just before it**; and the two OPERATIONAL counters of messages sent disagree with **each other** by 0.2630%. So the chapter is not *"build the comparison"* — it is **"the comparison has to say which operational table it read, one tenant at a time, and publish no percentage where the bound is unreachable"**. **And `not-comparable` and `no-data` are verdicts of their own**, because every tenant in the platform is one-sided: 4 rollup environment ids that exist in no Postgres row, against 1,313 with operational usage and no rollup rows. *"Callable in isolation"* split in two — the verdict runs with no store, no database and no broker, and the gathering reads both. Amends FR-ANL-06 (SRS 1.14), closes `gaps.md` 047-1 and 048-1, and names constitution III's conflict a second time after 051-2 |
| 9 | IV | The log a customer can search | FR-ANL-07's query surface; FR-ANL-10's latency percentiles. **The brief pairs a clause that can be built with one that cannot, and the chapter does not build the second.** FR-ANL-10's column `message_events.delivery_latency_ms` has **0 rows and 0 producers** — carried as `gaps.md` 048-2 through six features — and the one thing that writes that table, `scripts/scale/load-analytics.mjs`, puts `CAST(NULL AS Nullable(UInt32))` into the column on purpose, twice. **What this line also did not say is that the quantity had never been defined.** "End-to-end delivery latency" has three readings and the platform's one existing latency measures a different one: `deliver.ts` times the `fetch` alone, which `analytics/0003_webhook_attempts.sql:20` already called *"the ENDPOINT … NOT `message_events.delivery_latency_ms`"*. So the chapter is not *"compute the percentiles"* — it is **"define the quantity, publish the error of the function everyone would have reached for, and build the surface that can be built"**. Measured: `quantile(0.99)` reads **4,961 where `quantileExact` reads 10,000** on the platform's one real latency sample, 50.39% low, and on a skewed sample the error **grows** with n. Amends FR-ANL-10, FR-DSH-03 and FR-ANL-08 (SRS 1.15), writes **ADR-26** — the first customer request served from the analytical store — and provisions the CI ClickHouse four chapters had needed |
| 10 | IV | **★ Milestone: the meter agrees** | The planted drift is caught; the 0.1% figure is measured once and recorded (§2.3). **What this line did not say is that the drift was already being caught and nobody could tell.** The planted-drift suite has run on every push since chapter 4.7 and passed; what had not been true since chapter 4.4 is the gate's colour — `pnpm test:integration` was red on every run for six failures with nothing to do with metering, so a planted drift made a red run redder. **The signal was not absent, it was indistinguishable**, and `--concurrency=1` meant five other lanes had not run at all. So the chapter is not *"make the gate catch a drift"* — it is **"make a gate whose colour can change, and publish the figure at a volume where 0.1% is a threshold rather than a rounding of nothing"**. Measured: 54 of 54 suites now execute and the gate says so, because turbo's own summary counts tasks and does not reproduce run to run; **one unset environment variable** was failing `limits.itest.ts` loudly and making three isolation-gauntlet attacks return at their first line and report green; and a gateway test had **never delivered the presence frame it published** — a five-field payload against a three-field strict schema — passing instead on a frame the gateway sends at connect. The figure: **121,057 against 121,057, 0.0000%**, where the smallest expressible drift is 122 messages. Writes **ADR-27** and **ADR-28**, proposes the constitution III amendment three features have deferred, and publishes `docs/13-metering-measurement-2026-09-17.md` |
| 11 | V | The upload that never reaches us | FR-MED-01/02: the slot, the presigned URL, the four distinct refusals, the storage quota. **The count was right and the line was silent about every cost.** (1) **There was no object storage at all** — ADR-13 chose the pattern in the first draft and `docs/05-sad.md:1002` has named MinIO ever since, and nothing had ever provisioned a container; `minio/minio` is `pull access denied` and the image that exists is `quay.io/minio/minio`, 241 MB. (2) **The fourth refusal is not FR-MED-02's.** That clause names three — MIME type, per-kind size cap, storage quota — and the fourth is `docs/05-sad.md:1062`'s degradation row, *"Object storage lost … Upload slots return a specific error"*, now FR-017. It is the only transient one of the four, which is the whole reason they are four codes. (3) **The storage quota is a LEVEL where FR-RTL-05's other three are monthly flows** — `usage_periods` is keyed on a calendar month and `creditFor` never subtracts, so a tenant holding 100 GB would start every month at zero; the cap joins `quota_config` and the accounting is a sum over the media rows. **Two clauses cited FR-RTL-05 for a quantity it did not define** (SRS 1.17). (4) **And the presigned URL needs no contact with the store**, which is what made FR-017 expensive rather than free: the api never learns the store is down, so the refusal needed a round trip built for it — **+1.524 ms at p50, +24.1%**. So the chapter is not *"sign a URL"* — it is **"the cheap part costs no dependency and twenty-eight lines, and every other part of the brief cost a clause"**. Writes **ADR-30**, amends FR-RTL-05 and FR-MED-12, and adds four rungs to the error filter's status ladder |
| 12 | V | The half of the union that was refused | FR-MED-06. Chapter 3.24 shipped `media_not_available` (422) to refuse `media_id` **by name**, as a discriminated union built for this arm to be filled. This chapter fills it |
| 13 | V | A link that expires, and who may hold it | FR-MED-08: signed delivery, one hour, authorisation following channel membership rather than a parallel ACL |
| 14 | VI | The only service that reads the bytes | The media worker. FR-MED-03/04: verify against declaration, ClamAV, probe. **Open — see §7.3** |
| 15 | VI | Pending, ready, rejected | The state machine and `media.updated` (FR-MED-07). A placeholder becomes real without polling. **Open — see §7.4** |
| 16 | VI | What a thumbnail costs | FR-MED-05: derived objects sharing the parent's lifecycle |
| 17 | VI | Storage on the bill | FR-MED-12: stored bytes metered per tenant per day, into the store movement IV built |
| 18 | VI | **★ Milestone: an image, end to end** | Upload → scan → send → signed delivery. FR-MED-09's rejection marker renders as rejected, never as broken |
| 19 | VII | The log that cannot be edited | FR-MOD-03's audit log. **First in its movement, not last** — everything after it writes to it. Registry-shaped, the same shape as *Errors that resolve*, which 045 moved to the front of Part 3 for this reason |
| 20 | VII | Everything, including what was deleted | FR-MOD-01/02 via API key. **Check the premise first — see §7.5** |
| 21 | VII | The messages that expire | FR-MOD-06's retention job. Expired messages take their media objects with them (FR-MED-11) |
| 22 | VII | Erasure, and every path it must find | FR-MOD-04 and FR-MED-10. Messages, memberships, profile, media objects, analytical rows — the chapter this part is named for |
| 23 | VII | **★ Milestone: the Priya test** | Journey 3 scripted: locate → reconstruct → act → audit |

**Cadence.** Milestones at 10, 18 and 23, against Part 3's two at 25 and 26 of 26. The famine
Part 3 ran — 25 chapters between the Tuan test and the isolation gauntlet — is not repeated.

**MOVEMENT I IS ONE CHAPTER, AND THIS IS THE FIRST ESTIMATE THIS PROJECT HAS MADE THAT WAS
TOO HIGH.** §2.4 split it in two — the questions and the harness as one sitting, the
counterfactual and the verdict as another. Chapter 4.1 shipped with both, at **2,132 prose
words** against a 2,000–4,000 bound, because the counterfactual turned out to be four numbers
and a plan rather than a chapter's worth of argument.

Every prior correction in this document ran the other way: Part 3 planned as seven and shipped
26, and §3 below still warns that 23 will not be 23. **It was 24 for a day, and it contracted.**
The churn §2.1 accepted is symmetric and nobody had said so.

**And 23 will not be 23.** Part 3 was planned at 7 and shipped 26 because chapters split at
their word ceiling rather than compress. **This document has already done it once** — movement
I gained a chapter during grooming and every ordinal after it moved, which is exactly the churn
§2.1 accepted. Movements absorb it; the ordinal does not, which is why §6 is not optional.

---

## 4. What the reader already knows walking in

Chapters must not re-teach these. The reader met all of them in Part 3.

| already taught | where | what Part 4 does with it |
|---|---|---|
| The transactional outbox, and why it is in Postgres | movement II | contrasts it — ch 5 |
| JetStream streams, durable pull consumers, the 503 a publisher gets from a stream nobody created | movements II, VI | reuses — ch 4 |
| **The analytics subject grammar and the fire-and-forget tradeoff** | ch 3.20 | **generalises — ch 5, 6** |
| Subject grammars as a design tool, five of them, each argued | movements IV, V | ch 15 may need a sixth (§7.4) |
| The error registry and how a code is added to it | movement I | ch 11's four refusals |
| The isolation harness and the global-operation guard | movement I | every new table |
| Attachments as a discriminated union, `media_id` refused by name | ch 3.24 | ch 12 fills the arm |
| **Monthly quota counters in Postgres** — `usage_periods`, `usage_active_users`, `usage_connections` | ch 3.23 | **ch 8 reconciles against them** |

**THE ORDINALS IN THIS SECTION WERE ONE AHEAD OF §3's, AND THEY ARE CORRECTED ABOVE.** Five
cross-references pointed one chapter too far: the outbox contrast, the analytics grammar, the
error registry, the union arm and the quota reconciler. They fit the interim **24-chapter**
numbering that existed for a day while §2.4 had movement I as two chapters — §3's table was
renumbered when movement I contracted and this section was not. §7's references were written
against §3's table and are unaffected.

**It matters more here than anywhere else in this document**, because §4 is the section that
tells a chapter what it must not re-teach. A writer following it literally would have concluded
that chapter 4.4 is *not* the one that generalises 3.20's fire-and-forget argument — and 4.4 is
exactly that chapter.

**The hardest idea in this part is already taught.** `packages/protocol/src/internal.ts:249`
defines `analytics.{domain}.{action}.{environment_id}` as the third grammar in that file,
on a stream deliberately separate from `EVENTS` and `DELIVERIES`, and its own comment says:

> *Part 4's ingester is that consumer, and it does not exist yet, which is exactly when a
> shared definition is cheapest to establish.*

`services/api/src/webhooks/analytics.ts` argues the tradeoff in full and concludes
*"so 'every attempt' is APPROXIMATE, and the chapter says so in the paragraph that
introduces the feature rather than in a footnote."*

So *there are two ways out of this system and they have different guarantees* is a thing the
reader has already been told, at the right moment, with the cost stated. Movement III
generalises it to two more producers. **It does not introduce it, and a chapter that
re-derives it is a chapter that has not read Part 3.**

### FR-ANL-06 has a concrete counterpart, and it is Part 3's

**FR-RTL-05 and FR-ANL-05 meter the same three quantities.** FR-RTL-05 enforces *monthly
quotas on messages sent, unique active persons, and connection-minutes*; FR-ANL-05 meters
*per tenant per day: messages sent, unique active users, connection-minutes, and stored
message count.*

So chapter 7 builds in ClickHouse a daily view of what Part 3's quota chapter already counts
monthly in Postgres — and **FR-ANL-06's reconciliation is the comparison between them.**
*"Metered totals shall agree with counts derived from operational data to within 0.1%"* is not
abstract: the operational data is `usage_periods` and `usage_active_users`, and the reconciler
aggregates the daily rollups up to the period grain to meet them.

**This paragraph named three tables until chapter 4.7 and the job reads two.**
`usage_connections` is one row per connection per period and `usage_periods.connection_minutes`
is its rollup, written in the same transaction that credits it — so reading both would compare
a number against its own source. And the list was short in the other direction at the same
time: **the fourth quantity, stored message count, has no operational counterpart in any of
them**, which is why the report carries a `not-comparable` verdict rather than a zero.

`docs/07-tutorial-plan.md` predicted this tension before either side existed —
*"Building monthly counters in 3.8 would mean building them in Postgres now and again in
ClickHouse later, **or once in the wrong place**"* — and Part 3 built them in Postgres anyway,
correctly: a quota must refuse a send synchronously, so its counter cannot live downstream of a
lossy stream. **Two counters of one quantity is the right answer and the reconciler is the
price.** Chapter 8 is where that is said out loud.

This also sharpens §2.3: the CI half plants a drift **between two stores that both exist**,
rather than against a figure invented for the test.

---

## 5. The rules this order obeys

Feature 045 wrote these down and made them checkable, and rebuilding Part 3 to satisfy them
replaced 228 commits with 230. They are FR-001…FR-005 of
`specs/045-part-3-rework/spec.md`:

1. Every subject occupies a **contiguous run** of chapters.
2. A chapter must not teach a mechanism whose subject arrives **later**.
3. A chapter teaching a **cross-cutting pattern** precedes every chapter that reuses it.
4. A **milestone** appears after all the work it verifies.
5. A **registry** appears before the first chapter that adds to it.

Rule 3 asks what is cross-cutting here:

    ClickHouse's query shape      →  metering · request log · percentiles · storage
    the ingester                  →  every event type
    a migration runner for it     →  every table added after the first
    the audit log                 →  every moderation action
    presigned object storage      →  upload · delivery · thumbnails · deletion

Rule 2 forbids four orderings, and they are what makes this sequence less free than it looks:

    FR-MED-12  storage metering   needs ClickHouse      →  media after analytics
    FR-MOD-06  retention          deletes objects       →  retention after media
    FR-MOD-04  erasure            reaches all three     →  last of everything
    FR-MOD-03  the audit log      everything writes it  →  first of its movement

Rule 4 permits three milestones inside one part: each appears after the work it verifies.
The objection to three was cadence, and §3 shows the cadence is better than the precedent.

---

## 6. Two gates that must exist before chapter one

**Keeping the global ordinal (§2.1) was justified by the claim that the churn is
mechanically handled. It is not, yet.** Checked at grooming:

```
CI runs:   lint typecheck test build migrate test:integration coverage
           check:docs check:srs check:figures check:fences check-error-codes

wired to nothing:
  check-redirects.py   check-movements.py   check-map.py
  check-lane-scope.py  check-refs.py        check-chapter.py
```

All six live in `specs/045-part-3-rework/` and are referenced by no `package.json` script and
no CI step. `check-redirects.py` — the instrument that makes renumbering safe — ran once, by
hand, inside a feature that is now closed. And `lib/part3-chapter-map.json`'s own generated
header claims *"check-movements.py compares it to the canonical map and fails on any
drift"*, which describes an instrument nobody runs.

**G1 — `check:redirects` as a standing gate.** Every `was_url` in the map resolves; every
moved chapter carries both locales. Without it, §2.1's cost is unbounded rather than
mechanical.

**G2 — a gate that refuses a chapter ordinal in `relay-platform` source.** SC-002 took 1,429
such references to 0 by hand. FR-008 states the rule and nothing enforces it. Part 4 will
write new ordinals, and the only thing that stopped them leaking last time was a person.

Both must be red-tested three ways before being trusted, per the checker rule: a checker's
blind spot is worse than its absence.

---

## 7. Open questions, each owned by the chapter that needs it

**7.1 — ~~ClickHouse migration identity (ch 3)~~ — CLOSED by chapter 4.2.** The platform
hand-writes `.sql` against a `schema_migrations` table keyed on filename, and 043 retired
`drizzle-kit generate` and deleted `meta/`. A second store needs a second runner and a second
identity scheme. `gaps.md` 045-69 is the record of what an identity scheme going wrong costs.

> **Closed 2026-09-15, and it was closed in code two features earlier.** Chapter 4.2 built all
> four items of the brief — the runner, a ledger keyed on filename and checksum, reporting
> idempotence, and a checksum refusal tested red — and §3's own 2026-09-13 amendment records
> the chapter it belonged to disappearing as a result. **§3 was amended and §7 was not**, which
> is the defect chapter 4.5 found one entry down at §7.2 and fixed there; it survived the
> chapter that found it, and nothing in §7 says an entry can be closed by a chapter other than
> the one that owns it. Chapter 4.6 ran the refusal again to be sure it was real:
> `0005_connection_events.sql changed after it was applied (ledger 2702615facd07e77, file
> 397df7b2c0be7339)`. **The whole "a new numbered statement rather than an edit" discipline
> this movement depends on rests on that one throw**, and a refusal nobody has seen fire is a
> promise rather than a mechanism.

**7.2 — ~~ADR-07's second amendment (ch 6)~~ — CLOSED by chapter 4.5.** *"Clean mapping —
gateway to Redis, api and workers to NATS."* Chapter 3.18's amendment already recorded that
this stopped being exactly true in 3.8. Giving the gateway a publisher amends it again, and
that is a chapter's worth of argument rather than a line of wiring.

> **Closed 2026-09-15.** It was a chapter's worth of argument, and the argument turned out
> to be sharper than this brief. Two lines stop being true rather than one. The body's
> *"fan-out on NATS would leave that service holding two broker clients and remove none"*
> prices the refusal, and after this chapter the gateway holds two anyway — **so the price
> is zero and the refusal survives on ADR-10 alone**. And the mapping does not merely stop
> being *exactly* true: 3.8 and 3.18 took its api half, this chapter takes its gateway
> half, and afterwards **it describes no service in this platform**. Amended in place in
> both `docs/05-sad.md` and `docs/06-adr-deep-dives.md`, with the new-ADR alternative named
> and declined — the decision has not changed, only a driver's price.

**7.3 — Constitution VII and the media worker (ch 14).** ClamAV and ffprobe are not
TypeScript. The SAD calls this *"the one service where ADR-01's worker-thread posture matters
from day one"* and ADR-13/14 bless the design — but nothing blesses the packaging. VII's
subject is the language services are *implemented in*; a sidecar the worker talks to is
arguably not that. Argue it explicitly rather than by silence, the way the PL/pgSQL guard was
argued.

**7.4 — Does `media.updated` take a sixth subject grammar (ch 15)?** Five exist, each argued
individually, and the review asked for a consolidation threshold. **There is now a number to
argue against**: `docs/11` measured the subscription law as `redis subjects = 5 × channels +
1 × connected users`, exact on six rows to 20,000 connections.

**7.5 — Check ch 20's premise before writing it.** FR-MOD-01/02 are **P2**, and chapter 3.23
built edit history and tombstones. Some of this chapter may already exist. Run the premise;
this project has found four tasks whose premise was wrong, including one that would have
caused a defect.

**7.6 — The SRS phase table disagrees with itself, and someone must amend it.** §7.3 annotates
Phase 3 as *(P3)* while containing FR-DSH-01/02 at **P2** and FR-MED-05 at **P4**. Appendix A's
prose says the pack system was deferred to Phase 3 *"where its browse/install surface and usage
analytics arrive together"*, while the table puts usage analytics (FR-EMJ-11) in Phase 4. This
part covers FR-ANL, FR-MED and FR-MOD; **FR-DSH and FR-EMJ-03→10 are Phase 3 by the SRS and
Part 5 by the tutorial.** Amend the clause rather than diverge from it — the precedent is
FR-RTM-09, FR-RTM-10 and 043's own FR-016.

**7.7 — The fence chain opens at 110.** `pnpm check:fences` reported 109 when this was written
and **110** when chapter 4.1 ran it (APPLY 74, HEAD 36); the tutorial repository had moved.
Chapter 4.1's own delta was 0. Part 4 appends to that chain. 045-66 decomposed the previous 296 into
three causes and the largest contiguous block was `fences/post-series.md`, an appendix written
against an end state the rework replaced underneath it. **Nobody has decomposed the 109.**

---

## 8. What this document does not decide

- **Chapter titles.** Provisional, and the register is Part 3's.
- **How many indexes `messages` carries.** §2.4 records the structural claim and the
  command that settles it; the count belongs to chapter 1, re-derived at its own tag.
- **Where FR-DSH and FR-EMJ-03→10 land.** Part 5 by the tutorial plan; see §7.6.
- **Whether Part 4 is 23 chapters.** It will not be. It was 23, then 24, then 23 again — and the last move was a contraction, which no estimate in this project had produced before. The movements are the commitment; the
  count is an estimate, and every estimate this project has made about chapter counts has
  been low in the same direction.
- **Anything about the reader.** There is no page-view telemetry in `relay-tutorial` by
  design, and the one reader instrument — `specs/036-chapter-3-18/reader-protocol.md` — has
  been named by fourteen records and run zero times. Every claim in this document about what
  is easy to understand is an inference from structure, not a measurement of a person.

# Relay — Tutorial Plan

**Version:** 1.1
**Companion documents:** 01–06 (vision through ADR deep dives)
**What this plans:** a written tutorial series, *Building Relay*, that guides a developer
from initial idea to a deployed, monitored, multi-tenant chat infrastructure platform —
with the documents already written (vision, personas, journey map, SRS, SAD, ADRs) as
first-class chapters, not appendices.

---

## 1. Premise and positioning

### 1.1 What this tutorial is

Most tutorials teach a technology ("Learn WebSockets") or reproduce a toy ("Build a chat
app in an hour"). This one teaches something rarer: **how a production-shaped system is
actually brought into existence** — the specification work before the code, the
architectural decisions with their rejected alternatives, the correctness machinery
(ordering, idempotency, tenant isolation) that separates infrastructure from demos, and
the deployment and operations work that most tutorials wave away in a final paragraph.

The one-sentence pitch: *Build a real-time chat platform company from an empty directory —
specs, code, deployment, and monitoring included.*

### 1.2 Who it serves

**Primary reader:** a mid-level full-stack developer (2–5 years) who can build CRUD apps
comfortably and wants to cross into systems territory — the reader is, deliberately,
**Mai from the personas document**. She is both the tutorial's audience and the product's
user, which gives the series an unusual coherence: the reader builds the platform she
would want to integrate.

**Secondary readers:** engineers preparing for system design interviews (the ADR chapters
map directly to interview questions); developers evaluating build-vs-buy for chat who want
to understand what "build" really costs.

**Assumed knowledge:** TypeScript, basic SQL, Docker exists, Git. **Not assumed:**
distributed systems, Kubernetes, ClickHouse, message queues, WebSocket internals — these
are what the tutorial teaches.

### 1.3 What makes it different (the differentiators to protect)

1. **Specs first, honestly.** Parts 0 explains *why* the vision/SRS/SAD exist and has the
   reader produce them — most tutorials start at `npm init` and never explain where
   requirements come from.
2. **Decisions with rejected alternatives.** Every architectural choice is taught through
   its ADR: the options, the analysis, the reversal trigger. The reader learns to *decide*,
   not to copy.
3. **The journeys as tests.** Tuan's tunnel scenario and Priya's dispute become literal
   executable test suites the reader writes and passes. Requirements → journeys → tests is
   the pedagogical spine.
4. **It doesn't stop at "works on my machine."** Three full parts on deployment,
   operations, and monitoring — the material that is hardest to find in tutorial form.

---

## 2. Format and delivery decisions

| Decision | Choice | Rationale |
|---|---|---|
| Medium | Written chapters (Markdown), one repo | Text is searchable, diffable, versionable; video can be layered on later per-part |
| Home | Public GitHub monorepo: `tutorial/` (chapters) + `relay/` (code) side by side | The tutorial and code cannot drift if they live and CI together (§6) |
| Chapter unit | Ends in a **runnable, tested state** — no chapter ends mid-feature | The reader can stop anywhere and have something that works; this is the single most important format rule |
| Code progression | Git tag per chapter (`part2-ch3`), `diff` links between tags in every chapter | "What changed in this chapter" is a link, not a claim |
| Voice | First person plural, present tense ("we now have a problem: two gateways…") | Decisions feel lived-in, not handed down |
| Chapter length | 2,000–4,000 words + code; 60–120 min reader time | Longer chapters split; a chapter is a sitting |
| Recurring boxes | `WHY` (links to ADR/requirement), `TRAP` (the bug you'd write naively), `CHECKPOINT` (verify before continuing), `SKIP AHEAD` (what to `git checkout` if stuck) | Consistent scaffolding lowers reading cost |
| Visual elements | 2–4 captioned, theme-legible diagrams per chapter via the series `Figure` component, placed at key-concept moments (≥1 per chapter half); counted separately from specimen fences, which remain verbatim-quote territory; Vietnamese editions translate narrative labels while requirement/driver/ADR identifiers stay English | Concepts made visible break long prose runs; the specimen/diagram split keeps quote fidelity checkable |
| Code-chapter battery | For code chapters (Part 1 onward): the 2,000–4,000 word bound counts prose OUTSIDE code fences ("+ code" is additive, not counted); code fences are uncapped but counted; `TRAP` is a counted box class (≥1 per code chapter); file-content fences must match the chapter's tagged repository state byte-for-byte; a chapter amends an earlier chapter's fenced file only via a **hunked diff fence** (`@@` headers, three lines of context) whose hunks, applied to the state the predecessor chapters leave behind, reproduce the file at this chapter's tag exactly — each hunk's pre-image matching that state in exactly one place, since an ambiguous hunk proves nothing; full-file diffs were used through chapter 2.6 and stay as published, but new amendments are hunked, because an amendment should show what changed, not restate the file; specimen verbatim rules unchanged for quoted document content; Vietnamese editions keep all code fences byte-identical to English | Code volume must not corrupt the prose measure; the fence-equals-repo rule is how "the tutorial and code cannot drift" (§6) becomes checkable, and the diff-fence rule extends that check to files a later chapter must touch |

---

## 3. The arc — nine parts

The parts map onto the SRS phases where code is involved, bracketed by specification work
before and operations after. Estimated sizes assume the format rules above.

```
Part 0   The idea and the paper          5 chapters   (docs 01–06 as curriculum)
Part 1   Foundations                     4 chapters   (repo, tooling, protocol, compose)
Part 2   The core loop                   8 chapters   (SRS Phase 1 — the hardest part)
Part 3   Becoming a platform            10 chapters   (SRS Phase 2)
Part 4   The second data path            8 chapters   (SRS Phase 3 — ClickHouse + hosted media)
Part 5   Developer experience            6 chapters   (SRS Phase 4 — SDK, emoji, dashboard)
Part 6   Shipping it                     5 chapters   (containers, k8s, CI/CD)
Part 7   Running it                      6 chapters   (observability, load, chaos, incidents)
Part 8   The retrospective               2 chapters   (what we'd change; where to go next)
                                        ─────────────
                                        54 chapters
```

### Part 0 — The idea and the paper (5 chapters)

The existing documents become the curriculum. The reader doesn't just receive them — each
chapter shows the *derivation*: how the chat-app idea became an infrastructure product, how
personas generate requirements, how a journey becomes a test plan.

| Ch | Title | Reader produces | Source doc |
|---|---|---|---|
| 0.1 | From app to infrastructure — finding the real product | A positioning statement; non-goals list | 01 |
| 0.2 | Four people who will judge us | Persona set incl. the invisible end user | 02 |
| 0.3 | Journeys — where products die | Journey maps; the ★ moments | 03 |
| 0.4 | Requirements you can test | An SRS slice with IDs, priorities, verification methods | 04 |
| 0.5 | Deciding out loud — the SAD and the ADR habit | Drivers table; two ADRs written from scratch | 05, 06 |

**Design note:** Part 0 is the part most readers will want to skip, and the part that most
distinguishes the series. Mitigation: keep it to five tight chapters, seed each with a
"this paragraph becomes a test in Part 2" forward reference, and make skipping *safe* — a
one-page "the decisions, if you skipped the reasoning" summary opens Part 1.

### Part 1 — Foundations (4 chapters)

| Ch | Title | Built | Teaches |
|---|---|---|---|
| 1.1 | The monorepo and the toolchain | pnpm workspace + Turborepo task graph (ADR-17), TS config, lint, test runner | Workspace discipline; why one repo (ADR-01); a gate that caches |
| 1.2 | One command, whole world | docker-compose: postgres, redis, nats, clickhouse | NFR-MNT-03 as a day-one requirement, not an afterthought |
| 1.3 | The protocol package | `@relay/protocol`: frame types, error codes, zod schemas | Contract-first; the shared-types payoff of ADR-01 |
| 1.4 | Walking skeleton | Empty API service (a NestJS application — ADR-15) + frameworkless gateway, health checks, request IDs, structured logs | Deploy the skeleton before the muscles; observability from line one; the framework serves the API and stops at the gateway's door |

### Part 2 — The core loop (8 chapters) ★ the heart

SRS Phase 1. The ordering/idempotency/resume machinery — where the tutorial earns its
premise. Every chapter here pairs a capability with the failure it prevents.

| Ch | Title | Built | The failure it prevents |
|---|---|---|---|
| 2.1 | Schema with a spine | Migrations: users, channels, members, messages; repository layer (Drizzle — ADR-16) with mandatory `environment_id` | Cross-tenant leaks (D4) designed out, not tested out |
| 2.2 | The write path | POST message: channel row lock, sequence assignment (ADR-03) | Interleaved ordering under concurrency — demonstrated with a failing naive version first |
| 2.3 | Send it twice | Idempotency keys, partial unique index (DR-03) | Tuan's duplicate "B2, north ramp" |
| 2.4 | History that pages | Cursor pagination on `(channel_id, seq)` | Offset pagination's drift under live inserts — shown, then fixed |
| 2.5 | The socket | Gateway: WS termination, JWT verify, connection registry | — |
| 2.6 | Two servers, one conversation | Redis fan-out (ADR-07); the lossy-fabric argument | The sticky-session trap |
| 2.7 | The tunnel | Resume protocol: cursors, backfill, subscribe-before-backfill buffer | The duplicate/gap race in §5.2 of the SAD — the tutorial's flagship bug |
| 2.8 | **Milestone: the Tuan test** | An integration suite scripting journey 4 end-to-end: kill the socket mid-send, reconnect, assert exactly-once + order | This chapter *is* the SRS Phase 1 exit criterion |

### Part 3 — Becoming a platform (16 published, 3 planned)

SRS Phase 2. The chapters that turn "a chat backend" into "infrastructure someone else can
build on."

**Planned as seven and shipped as sixteen**, and the header said seven until chapter 3.16
closed. Every one of the nine extra chapters came from the same cause: a chapter that reached
its word ceiling and split rather than compress. 3.12 was specified as one chapter and shipped
as three; 3.15 was specified as one and shipped as two. The count is now derived from the rows
below rather than carried in the heading.

| Ch | Title | Built |
|---|---|---|
| 3.1 | Tenants all the way down | Orgs, apps, environments; OAuth signup; auto-created dev environment (FR-TEN-02) |
| 3.2 | Keys and tokens — two credentials, one mistake | API keys (prefix, hash, rotation); user JWTs; the dev-token endpoint (FR-AUT-09); error messages that name the wrong-credential mistake |
| 3.3 | The outbox | Transactional outbox + relay (ADR-06); the dual-write problem demonstrated with a crash-in-the-gap test |
| 3.4 | JetStream and the first consumer | NATS setup; subjects; durable pull consumers |
| 3.5 | Webhooks that survive the customer | Dispatcher service: envelope-encrypted signing secrets, HMAC-SHA256, a due-time retry schedule, dead letters (FR-WHK-01…05, FR-WHK-08) |
| 3.6 | When to stop trying | The attempt log and auto-disable (FR-WHK-06, FR-WHK-07, both half-delivered — see below); the synthetic test event (FR-WHK-09); the evidence a customer is owed when their endpoint is switched off |
| 3.7 | Commit and publish are two instants | The resume duplicate: a message committed before a backfill and announced after it, delivered twice; the high-water mark given a lifetime past the buffering window |
| 3.8 | Limits you can see coming | Per-environment fixed-window counters in Redis (FR-RTL-01…04); the three headers on every response, not only the refusal; failed-auth limiting per IP (FR-AUT-12), which fails **closed** while the tenant limiter fails open. **This chapter completes SRS Phase 2's requirement set** — §7.3 lists it as FR-TEN, FR-AUT, FR-WHK and FR-RTL at P2, and FR-RTL-01…04 is the last of the four |
| 3.9 | The email nobody was sending | The transport 3.6 was owed (FR-WHK-07): the outbox pattern a third time, over `webhook_disable_notifications` — no migration, because `delivered_at` was already there and already null. Mailpit in compose, and tests that read what was **received** |
| 3.10 | Quotas and what they cost | Monthly usage quotas for messages and distinct active users, a hard cap that refuses sends with `402` and a soft threshold that only alerts, the 50/80/100% email (FR-RTL-05…08). The caps live in `environments.quota_config` — the jsonb column 2.1 declared and 3.8 refused in print. **The outbox pattern a fourth time**, and the first chapter in the series that needed no global operation at all: usage rises only on a send, so the send knows what it crossed |
| 3.11 | Counting a connection | Connection-minutes (the third dimension of FR-RTL-05): periodic accounting in the gateway, which owns no tables and — until this chapter — no identity either; reports that carry totals so a lost one repairs itself; the crash that under-bills by a bounded amount rather than over-billing for ever; and close code 4008, declared in 1.3 and emitted for the first time here |
| 3.12 | **Milestone: the isolation gauntlet** | The cross-tenant attack suite (NFR-SEC-09), with a target list derived from the running router rather than maintained by hand; four attack shapes over 24 routes; a structural check that every table has a path back to a tenant; the socket surface attacked from the protocol's own frame union; and three deliberate reintroductions, one of which stayed green and taught the suite's range |
| 3.13 | The endpoints and the instruments | The two public endpoints Part 3 needed and nobody had built — `POST /v1/channels` and its members route — with idempotency enforced by a unique index rather than in application memory; every validation error naming its field for the first time since EIR-API-06 asked; the global-operation guard extended from five tables to nine; and the api repository layer's branch coverage answered with a number rather than a restatement |
| 3.14 | **Milestone: errors that resolve, and an outsider** | Thirteen error codes with one registry and one URL rule, a `docs_url` that resolves against the published reference, and a sealed integration package mechanically unable to import workspace code. This chapter gives the SRS Phase 2 exit criterion its verdict — *"an external developer integrates using only public documentation, with no assistance"* |
| 3.15 | The channel a customer controls | FR-CHN-03/04/05/06/10: the `private` type made to decide something on all four of its doors, bulk member removal, member roles with their own vocabulary, and archiving that refuses a send without announcing the channel exists. 20 files, 2,947 prose words, 20 fences, 3 figures |
| 3.16 | What a user sees | FR-CHN-08/09 and all of FR-USR: channel listing with cursor pagination and activity ordering, unread counts derived from a sequence the write path already maintains, user profiles, bulk upsert, a deletion that keeps the row, and banning. 24 files |
| 3.17 | *(planned)* The sender a message never had | A message sent by a customer's server has no sender at all — chapter 3.3 decided that when nothing read one. Bot users with descriptions, a sender required on every send, and an application credential that may speak as software and not as any person. Amends the SRS, which has no bot concept |
| 3.18 | *(planned)* The message that never arrived | FR-RTM-05's message half: the api publishes, so a REST-sent message reaches a socket. Closes the concrete half of chapter 3.14's Phase 2 verdict — an outsider who sends over REST and waits on a socket currently cannot succeed, and no document says so |
| 3.19 | *(planned)* Presence, and who is allowed to see it | FR-RTM-05's presence half, FR-RTM-06's online/offline with a 30-second grace period, and FR-RTM-07's scoping — delivered only to users sharing a channel with the subject, which is the membership graph 3.15 and 3.16 built. Completes FR-CHN-05's third verb, and decides open question 3: opt-in per channel, or not |

**3.5 was narrowed while it was being written, and 3.6 is where the remainder
went.** The original entry promised auto-disable in the same chapter as the
dispatcher. Two things made that the wrong shape. The chapter was already the
largest in the series — 39 fenced files against a budget first estimated at 22 —
and auto-disable turned out to depend on the attempt log to be defensible at all:
switching off a paying customer's endpoint is a decision that has to be explained
afterwards, and FR-WHK-06's log is the explanation. Shipping the mechanism without
the evidence would mean disabling endpoints and being unable to say why.

So 3.5 builds the delivery path and states plainly that it never gives up on an
endpoint, only on a delivery; 3.6 adds the record and the policy together. Part 3
gains a chapter and everything after it shifts by one.

**What 3.6 actually shipped, which is less than that row promises.** Both
requirements are half-delivered on purpose and the chapter says so in the
paragraph that introduces each:

- **FR-WHK-06** — attempts are PUBLISHED to a new `ANALYTICS` stream and are not
  queryable. Part 4's ingester consumes that stream into ClickHouse and is what
  finishes the requirement. The publish is also at-most-once by design, so
  "every attempt" is approximate: constitution III forbids letting an analytics
  backlog affect webhook dispatch, and independence was chosen over completeness.
- **FR-WHK-07** — the disablement writes a notification row whose `delivered_at`
  is null and stays null. This platform has no email transport; the quotas
  chapter needs the same one for warnings and builds it there.

**FR-WHK-09 moved forward into 3.6** rather than waiting. It closes the
disable-repair-re-enable loop the other two requirements open: without it a
customer re-enables on hope and the first real event is the experiment.

**Part 3 gains a second chapter, and this one is a bug.** 3.7 exists because
chapter 2.7 — the chapter this plan calls "the tutorial's flagship bug" — did not
close the race it is named for. A client that reconnects can be shown the same
message twice, and FR-RTM-03's "no gap and no double" is false.

**The "one run in six" this entry first carried did not survive measurement.**
3.6 saw one e2e failure in six runs; 3.7 ran the lane twenty times before changing
anything and saw none. The defect did not get rarer — the race needs a backfill
query to land inside the commit-to-publish gap, that gap widens under load, and
the four thousand pending webhook deliveries that made 3.6's lane take nine
minutes were cleared at the end of 3.6. The lane now takes three. What proves the
fix is a deterministic test, not a flake rate; the flake is only how the defect
was found.

The cause is the seam Part 3 has already taught three times: a message is durable
and a message is announced at two different instants, and the gateway publishes to
the fabric *after* the api has committed. A backfill query landing in that gap
returns a message the fabric has not yet delivered, and chapter 2.7's dedup window
closes when the connection goes live — a moment before the fabric catches up.

It is placed here, rather than in 7.5 where reconnection at scale lives, for two
reasons. The lesson belongs beside 3.3's outbox, 3.5's post-then-report and 3.6's
publish-after-commit: four instances of one seam, four different correct answers,
and the fan-out path is the one built before the reader had the concept. And it is
a live correctness defect that flakes the integration lane, which is exactly the
condition that let three other real defects hide during chapter 3.6's work.

3.7's insertion moved quotas to 3.8 and the gauntlet to 3.9 — both have since
moved twice more, see below. **That renumbering had a trap in it that had already been
sprung once**: `services/api/src/db/schema.ts` says "chapter
3.7's cross-tenant gauntlet", written when the gauntlet was 3.7, and 3.6's
insertion never carried it. That comment is byte-fenced into published chapter
3.5, so the mechanism guaranteeing the book matches the code is the same mechanism
that makes the stale reference awkward to fix. 3.7 fixes it, and stops source
comments citing numbers that can move.

**Part 3 gains a third chapter, and this one is a split rather than a bug.** The
original 3.8 promised "Limits and quotas" in one sitting. FR-RTL reads as one
family of eight requirements and divides cleanly on **where the count lives**.

A rate limit is ephemeral. It counts a window, it may be lost, and SAD §6.3 is
explicit that nothing in Redis is a source of truth — so Redis is the right store
and *failing open* is the right default: a cache outage is not a reason to refuse
a paying customer's traffic. A quota is money. It must be durable, and the ADR-06
deep dive states that billing accuracy cannot rest on any pipeline's promises. One
chapter teaching both would teach one storage decision as though it covered two
opposite cases.

Quotas also have a dependency the plan had not accounted for. FR-RTL-05 meters
messages sent, unique active users and connection-minutes — which is FR-ANL-05,
arriving in **Part 4** with the analytical store. Building monthly counters in 3.8
would mean building them in Postgres now and again in ClickHouse later, or once in
the wrong place.

So 3.8 takes FR-RTL-01…04 and quotas take FR-RTL-05…08. 3.8 also picks up two
things left lying around: FR-AUT-12's per-IP limiting on failed authentication,
which is the same mechanism at a different scope and the one bucket that must
*not* fail open, and the **email transport chapter 3.6 deferred**. FR-WHK-07
requires an organisation be told when its endpoint is switched off; 3.6 writes the
notification row and leaves `delivered_at` null above a comment saying whichever
chapter builds a transport will set it. Deferring that a second time would mean a
third chapter explaining the null column.

**And then 3.8 split again while it was being written, on a measurement.** Its
size gate counts fences and prose on the finished page rather than against an
estimate, and the limiter half alone came to 4,700 words against the 2,000-4,000
bound — with the transport's sections unwritten. Adding them would have reached
roughly 6,300, past 3.6's 5,346 and past anything the series has published.

So the transport's *prose* became **3.9**, quotas moved to **3.10** and the
gauntlet to **3.11** — where it stayed until the split below moved it again, to
**3.12**. The transport's *code* shipped under `part3-ch8` regardless,
because it closes FR-WHK-07 whichever chapter explains it — and 3.9 was written in
the same cycle rather than deferred, so every fence lands with the chapter that
teaches it instead of accumulating in `post-series.md`.

**What 3.10 turned out to be, against what the plan said.** The estimate was
3,000 to 3,600 prose words; the page counts **2,548** with 31 fences, so the
estimate ran 18% high — the fourth Part 3 chapter where the number on the page and
the number in the plan disagreed. The first draft came in at 2,053 and was thin in
a way the count could not see: it was missing the flush test, which is the
chapter's whole spine, and the reason a distinct-user count cannot be an
increment. The gate measures length, not whether the length is spent on the right
thing.

Two of the chapter's decisions were not in the plan. The caps went into
`environments.quota_config` rather than into four new columns, because chapter 3.8
had reserved that column for quotas **in published prose** and three analysis
passes had not read the artifacts against the published series. And the
`FOR UPDATE` the plan specified for bounding cap overshoot turned out to be
impossible once the caps and the usage became one joined read — Postgres will not
lock the nullable side of an outer join — which is the bound the specification had
asked for in the first place.

**What 3.11 turned out to be, against what the plan said.** The estimate was
3,000 to 3,600 prose words and the page counts **3,324** with 34 fences — inside
the range, and the first Part 3 chapter where the estimate and the page agreed.
That is not skill. It is an estimate made after four chapters of evidence about
how long this author's chapters run, which is the only thing that has ever made
one of these accurate.

The seam held and was not needed. Phase 7 — the third dimension's crossings and
emails — was sequenced last so it could be cut, and the count came in with room
to spare, so it stayed.

**Three of the plan's own claims were wrong, and each was corrected by a
measurement rather than by an argument.**

Research chose "a second call on the same request rather than a heavier
`environmentLimits`", reasoning from 3.10's refusal to put a usage join in that
function. The refusal was right — that function has a second caller on every
`/v1` request — but two calls cost what a join would at concurrency: connect
latency at 32-way went 15.0ms to 17.6ms across four runs clustered inside 0.7ms.
Folding the connect path into its own read recovered 0.8ms.

The plan predicted `repository.ts`'s coverage ratchet would go red, from the
precedent of chapters 3.5 and 3.6 where that file lost 7.69 and 1.20 points.
Branches went **up**, 90.17 to 90.57, because the mitigation the prediction
prescribed — cover the new repository code in-process, in the phase that writes it
— is the thing that changed the outcome.

And 3.10 wrote, twice, that a third metered dimension costs "a new key plus a
one-line constraint change". It is **seven places**, two of which it did not
anticipate at all. The one that mattered was a two-way ternary in
`publicMessage()`: `Dimension` is `keyof QuotaConfig`, so adding the config key
widened the type on its own and a connection-minutes breach would have rendered
"monthly ACTIVE USER quota exhausted" with the compiler silent.

**The twenty-run battery earned its hour.** Three defects, none findable by
reading, two of them older than this chapter: a fixed api port that produced three
unrelated-looking assertions, an eleven-chapter-old flake in `credentials.itest.ts`
where an api key's secret was taken as `split("_").at(-1)` — base64url includes
the separator — and one test budget of my own. The first attempt was abandoned at
run 7 rather than letting thirteen more runs report on code already known wrong;
the second went 20 for 20 at 330 tests every run.

**And chapter 3.10 left two tripwires, one of them unscheduled.** `session.test.ts`
asserting that nothing emits close code 4008 was planned for and inverted.
`config.test.ts` asserting that `connection_minutes` is rejected "until then" was
not: seven analysis passes missed it, because the fence inventory lists
`config.ts` and not its test. A red test found it in the second phase.

**3.10 is the fourth, and this one was decided before a word was written.** FR-RTL-05
names three metered dimensions — messages sent, unique active users, and
connection-minutes — and the first two are not like the third. Messages and users
are already rows: `messages.user_id` has been in `0000_core_tables.sql` since Part
2, so counting them is an aggregation question. A connection-minute is a duration,
nothing records it today, and the service that would have to record it is the
gateway, **which owns no tables**. That is a different subject with a different
lesson, and putting both in one chapter would have produced a chapter about
counting that quietly turns into a chapter about who is allowed to write.

So connection-minutes is **3.11** and the gauntlet moves to **3.12**. The
deferral has a chapter number rather than a promise, which is the difference
between scheduling work and dropping it — three of the four splits in this part
were discovered mid-chapter, and this one was not.

This is the third size-driven split in Part 3, after 3.5→3.6 and the original
3.8. The difference is that this one was decided by counting the page. 3.5 shipped
39 fences against an estimate of 22 and 3.6 ran 5,346 words, both discovered
afterwards; the phase order for 3.8 put the separable half **last** specifically so
the decision could be made with a number.

**This renumbering should be cheap, and 3.8 is testing whether it is.** Chapter 3.7
drove forward chapter references in live source to zero and replaced them with
subjects rather than ordinals. If that worked, moving quotas and the gauntlet costs
prose, this table and the registry — and no fence amendment. 3.8's success criteria
check it rather than assume it, because a rule adopted one chapter ago to make this
cheap should be made to prove it.

**3.12 BECAME THREE CHAPTERS, on a measurement.** The plan estimated 37 fenced
files — 16 new and 21 amended. The work came to **61**, and the 2,000–4,000
prose-word bound in §2 cannot hold that: a single page would have run to about
7,000 words carrying 66 fences. The split was taken at the phase-11 boundary,
before any chapter prose existed, so nothing was discarded — which is the whole
argument for counting the surface rather than the finished page.

The three halves measured 21, 21 and 17 files, and land at roughly 3,400, 3,400 and
2,700 words. Chapter 3.11 for scale: 21 files, 31 fences, 3,316 words.

**The milestone name moved to 3.14** rather than staying with the suite, because
the Phase 2 exit criterion is what a milestone chapter gives a verdict on and the
outsider's chapter is where that verdict lives. And the deferred public surface —
promised a number as 3.13 — **became 3.15**. What mattered about the promise was
that the work had a number, not which number.

This is the second time a chapter in this part has been split on a count and the
third time an estimate was low: 3.5 estimated 22 fences and shipped 39, 3.11
estimated 21 files and shipped 21, and this one estimated 37 and found 61. The
estimate is not getting better; what changed is that this one was checked before
the prose existed rather than after.

**Phase 2 closes across 3.8 and 3.14, and its exit criterion is a problem the series
has been accumulating.** SRS §7.3 exits Phase 2 on *"an external developer integrates
using only public documentation, with no assistance"*. 3.8 finishes the requirement set;
the gauntlet, now 3.12, builds the suite, and 3.14 runs the outsider's test.

The awkward part is that 3.8 ships `rate_limited` as the first error code an integrating
developer will actually receive and look up, and its `docs_url` resolves to nothing — a
placeholder every chapter since 1.4 has carried, in a filter whose own comment admits it.
Constitution V requires every error code to have a reachable page. **The phase whose exit
criterion is public documentation is completed by a chapter that documents an error code
nowhere**, and the milestone that tests it is three chapters later.

Recorded here rather than solved: a docs site is not a chapter of this series, and
pretending otherwise would put a fifth half-built thing in Part 3.

**Two chapters exceed the 2,000-4,000 word bound in the table above** — 3.5 at
4,996 words of prose outside fences and 3.6 at 5,346. Nothing enforces that
bound, which is why neither was caught at the time. Both are accepted as they
shipped: the bound is a guide to keep a chapter a sitting, and these two carry
requirements that are half-delivered on purpose and have to say so where they are
introduced. Recorded here, where the rule lives, so the next chapter measures
against a real number.

**3.7 came in at 2,244**, the first Part 3 chapter inside the bound in three. It
is not restraint learned from the two above it: the chapter is short because the
change is four lines of logic. A chapter's length follows its subject, and the
two that ran long were building subsystems.

### Work that publishes no chapter

Not everything the repository needs is something a chapter teaches. Tooling, CI,
a dependency the series does not explain — those changes land in
`relay-tutorial/fences/post-series.md`, applied after the last chapter and checked
exactly as strictly, so the chain stays byte-exact and no chapter is made to show
a reader code it never discusses.

One entry is large enough to name here, because it is a class of defect rather
than a fix.

**Feature 030 — the fault that only shows up in company.** Eleven times across
Parts 2 and 3, a test asserted a local fact about a global operation: a sweep
whose batch never reached its own endpoint, a drain holding a lock, a consumer on
a fixed budget against a growing stream, a `count(*)` compared against itself
twice in the same file four chapters apart, a drain at a default batch size of
fifty, and — in chapter 3.9 — a global *mutation* that disabled a neighbouring
suite's fixture.

Every one passed alone and failed beside a neighbour, which is why each read as a
flake and why the class kept coming back. The sixth was written by someone who had
recorded the other five and cited them in a chapter.

**Seven of those eleven were known when the feature was specified. Four were found
by the feature itself**, on its first run against a clean database and before any
deliberate reintroduction: two drive loops in `outbox.itest.ts` that bounded the
driving in units of batches while the work was bounded by the whole table, a
deduplication assertion in the same file that quietly claimed no row anywhere in
the outbox is ever published twice by anyone, and — forty lines from the test
chapter 3.7 had already fixed — two consumer runtimes constructed with no subject
filter. That last one is why the task list now says to grep for the class while
the first instance is still on screen.

The remedy is not another rule. Three rules failed their own authors during 3.8
alone. It is to make the fault **fail in isolation**: plant rows a global
operation would take, fail the lane when something takes them, require a batch
size at every cross-environment call, and refuse the import inside a test file.
The specification is `specs/030-global-operation-guard/`.

**What it does not reach, recorded because a defence trusted past its range is
worse than none.** The seeder plants rows in a database, and the rule
that emerged from measuring it three times is that **bait may be claimable only
where draining it is database work**. A sweep and a publish qualify. A delivery
that costs an api round-trip and an HTTP send does not — two hundred planted ones
failed ten of the dispatcher suite's sixteen tests with the fault they were meant
to catch already fixed. Nor does a notification that costs a recipient lookup: 3,400
of them at 1.4ms each timed out a test with a five-second budget, on the first run
of the twenty-run battery and after three full lanes had passed. Those drains, and
anything riding the broker rather than the database, are covered by the required
batch size and the lint rule instead. The lint rule in turn sees an import and not a helper and
not raw SQL; the trigger sees both.

**One decision inside it is worth recording here rather than as an ADR.** The
guard is written in PL/pgSQL — about twenty lines — because it has to raise inside
the transaction that performed the mutation, and that is the property which makes
attribution exact under parallel test execution. A check written in TypeScript
cannot do it: legitimate global sweeps run on every lane pass, so a before/after
comparison either fires constantly or blames a bystander. That was measured, not
assumed, along with the fact that the naive SQL version is non-deterministic —
`SET relay.allow_global = 'on'` issued through a connection pool landed on two of
five checkouts.

Constitution VII says *"Introducing a second language requires a superseding ADR
with profiling evidence"*, and there is no ADR here, because there is nothing for
one to supersede. VII's clause reads *"One language (TypeScript/Node.js) across
services, SDK, and dashboard"* — its subject is the language services are
implemented in, and its stated harm is drift between server and SDK. This is
neither a service nor shipped; it exists in test databases, created by the lane.
The repository already holds nine hand-reviewed `.sql` migrations that the
constitution endorses by name.

The honest wrinkle: those nine are *declarative* SQL and this one is *procedural*.
A `RAISE EXCEPTION` inside a `plpgsql` function is closer to program logic than an
`ALTER TABLE` is. That difference is real; it is not the difference VII legislates.
An earlier draft of the plan recorded it as a violation and then declined to write
the ADR the clause requires, and four analysis passes re-affirmed that without
testing it against the sentence it cited.

It teaches no chapter, and that is a deliberate call rather than an oversight. The
material is genuinely interesting — a fault invisible by construction is good
writing — but the series' rule is that a chapter may only fence a change it
discusses, and inventing a chapter to justify test infrastructure is the tail
wagging the dog. If a later chapter wants the story, the twelve post-series entries
and this feature's research are where it is kept.


### Part 4 — The second data path (8 chapters)

SRS Phase 3. The ClickHouse material — likely the strongest search-traffic magnet, since
"ClickHouse for SaaS analytics" is underserved territory.

| Ch | Title | Built |
|---|---|---|
| 4.1 | Why your database can't count | The OLTP/OLAP argument (CON-01) made concrete: run the metering query against Postgres under write load, watch it hurt |
| 4.2 | ClickHouse from zero | Schema: MergeTree, partitions, ORDER BY, TTL (DR-07/09); ingester with batching |
| 4.3 | Metering you can bill on | Daily rollup MVs (DR-10); the reconciliation job (FR-ANL-06) |
| 4.4 | The request log | api_requests table; dashboard query surface (FR-ANL-07) |
| 4.5 | Media without touching it | Presigned direct-to-storage uploads (ADR-13); MinIO; signed delivery URLs following channel membership; storage metering into ClickHouse (FR-MED-12) |
| 4.6 | The scan pipeline | Media worker: ClamAV, probe, thumbnails; `pending → ready` gating bytes, never messages (ADR-14); the `media.updated` fan-out |
| 4.7 | Moderation and the paper trail | Tombstone reads, edit history, audit log, compliance erasure — now including media objects (FR-MOD, FR-MED-10) — Priya's chapter |
| 4.8 | **Milestone: the Priya test** | Journey 3 scripted: locate → reconstruct (edit history proves the case; a rejected upload renders as rejected, not broken) → act → audit |

### Part 5 — Developer experience (6 chapters)

SRS Phase 4 — where the reader experiences the product from Mai's side of the counter.

| Ch | Title | Built |
|---|---|---|
| 5.1 | The SDK — transport and state, no UI | Reconnect w/ jittered backoff, offline queue, message states; media upload helpers with progress and attachment-state handling (FR-SDK, FR-MED-14) |
| 5.2 | The dashboard and the live wire | Next.js dashboard; SSE service (ADR-09); the first-message live view (FR-DSH-02) |
| 5.3 | Emoji and packs | Shortcode grammar, packs CRUD, install; resolution map + version cache (ADR-11/12) |
| 5.4 | The reference client | A plain chat app built *only* on the public SDK — dogfooding chapter |
| 5.5 | Docs as product | OpenAPI generation; the quickstart; error-code pages; CI that *executes* the quickstart (NFR-USE-03) |
| 5.6 | **Milestone: the ten-minute test** | A stranger (or the reader's stopwatch) goes signup → first message; measure against NFR-USE-01 |

### Part 6 — Shipping it (5 chapters)

| Ch | Title | Built |
|---|---|---|
| 6.1 | Containers done plainly | Dockerfiles (multi-stage, distroless), image discipline |
| 6.2 | Kubernetes without the priesthood | Manifests for all services; the two StatefulSets; secrets handling |
| 6.3 | The gateway drains | Graceful shutdown, `server.shutdown` frames, rolling deploys (NFR-REL-03) — deploy during a live conversation and watch nothing break |
| 6.4 | CI/CD | Pipeline: lint → test → isolation gauntlet → build → chapter-checkpoint verification (§6) → deploy |
| 6.5 | **Milestone: production** | Deploy to a real cluster (k3s on a VPS keeps cost honest); TLS; the app is on the internet |

### Part 7 — Running it (6 chapters)

The rarest tutorial material, and the part that makes the series title honest.

| Ch | Title | Built / done |
|---|---|---|
| 7.1 | Traces through the whole body | OpenTelemetry across services and *through JetStream headers*; one trace from REST ingress to webhook delivery (NFR-OBS-02) |
| 7.2 | Metrics and the four alerts | Prometheus + Grafana; dashboards per service; NFR-OBS-04's alert set. Opens with the series' most-asked `WHY` box: *"Don't we already have ClickHouse?"* — product analytics vs. operational observability, and why the observer must not share fate with the observed (SAD §8) |
| 7.3 | The load test | k6 scenarios mapped to SAD S1–S4; find the real gateway connection ceiling — **resolving risk R2 on camera** |
| 7.4 | Breaking it on purpose | Chaos drills from the failure matrix: kill Redis, kill NATS, kill a gateway mid-conversation; verify each blast radius claim |
| 7.5 | The reconnection storm | Simulate the car-park scenario at fleet scale; watch jitter save you; remove jitter and watch it not |
| 7.6 | On-call for one | Runbooks per alert; the incident-communication template; status page |

### Part 8 — The retrospective (2 chapters)

| Ch | Title | Content |
|---|---|---|
| 8.1 | The bill | Honest accounting: LOC, months, infra cost/month — the build-vs-buy numbers David wanted, now measured, not estimated |
| 8.2 | Where the walls are | Revisit every ADR trigger and risk; what fires first at 10× scale; extension ideas (search, threads, native SDKs) as reader exercises |

---

## 4. Pedagogical spine — three rules that govern every chapter

**Rule 1: failure before machinery.** Never introduce correctness machinery abstractly.
Chapter 2.2 first builds the naive version and demonstrates interleaved ordering with a
concurrency test; *then* introduces the row lock. 2.3 duplicates a message before fixing
it. 3.3 crashes the process in the dual-write gap before building the outbox. The reader
must *see the bug the design prevents* — it is the difference between knowing a pattern's
name and knowing its necessity.

**Rule 2: the journeys are the milestones.** Parts 2, 4, and 5 each terminate in an
executable journey (Tuan, Priya, Mai). These aren't metaphors — they are the integration
suites, and they are the SRS phase exit criteria. A reader who passes the Tuan test has
built Phase 1, definitionally.

**Rule 3: every chapter cites its paperwork.** Each `WHY` box links the code being written
to its requirement ID and ADR. This is what makes Part 0 retroactively valuable even to
readers who skipped it — the paperwork keeps showing up as the *reason* for the code.

---

## 5. Sequencing and effort

Recommended production order is **not** reader order in one respect: write chapter 2.8
(the Tuan test) *immediately after* 2.7's code exists but draft its test suite *before*
Part 2's chapters — test-first at the part level. The milestone tests define done-ness for
everything before them.

| Stage | Output | Estimate (part-time, ~10 h/wk) |
|---|---|---|
| A | Part 0 (docs exist — this is editing into chapters) + Part 1 | 3 weeks |
| B | Part 2 code + chapters | 6–8 weeks |
| C | Part 3 | 5–6 weeks |
| D | Part 4 | 6–7 weeks |
| E | Part 5 | 5–6 weeks |
| F | Parts 6–7 | 5–6 weeks |
| G | Part 8 + full-series edit pass | 2 weeks |
| | **Total** | **~8–10 months part-time** |

The estimate is deliberately unflattering. If it motivates scope cuts, cut whole *parts*
from the tutorial's v1 (ship Parts 0–2 as "Season 1"), never chapters from within a part —
a part that doesn't reach its milestone journey is unfinished by Rule 2.

**Publish incrementally.** Parts 0–2 are a complete, satisfying unit (spec → working
resumable chat with the Tuan test passing) and should ship as soon as they exist. Feedback
on Part 2 will improve Parts 3–7 more than any amount of solitary polish.

---

## 6. Keeping the tutorial honest — the sync problem

Tutorial rot — prose that no longer matches code — is the death of every long series. The
defenses, in priority order:

1. **Chapter checkpoints in CI.** Every chapter's `CHECKPOINT` block is a script
   (`tutorial/checkpoints/part2-ch3.sh`) run against that chapter's git tag on every push
   to the tag's lineage. If chapter 2.3's checkpoint fails, the build fails. This is the
   same discipline as NFR-USE-03 (the quickstart runs in CI) applied to the whole series —
   the tutorial eats the product's dogfood.
2. **Code samples are extracted, not pasted.** Chapters embed code by reference
   (file + line-range markers resolved at build time from the chapter's tag), never by
   copy. A rendered chapter with a stale extraction marker fails the docs build.
3. **One direction of authority.** The repo at tag N is the truth; prose describes it.
   When a later part forces a change to earlier code (it will), the rule is: rebase the
   tag lineage, re-run all checkpoints, and add a `REVISED` note to affected chapters —
   never let prose and code disagree silently.

**Status of these defenses (as of 2026-08-08).** Defense 2 exists in a stronger form
than planned: fences are byte-verified against the repo by `pnpm check:fences`, which
replays every published chapter (95 files, 18 chapters) rather than resolving line-range
markers at build time. Defense 1 does **not** exist — there is no CI anywhere in the three
repositories, so chapter checkpoints, the quickstart's NFR-USE-03 run, and the
constitution's 100% branch-coverage bar for isolation code (Principle VI, NFR-MNT-02) are
all verified by hand or not at all. Chapter 3.1 deferred the coverage measurement; chapter
3.2 deferred it a second time by explicit decision, and 3.3 a third — each recorded in
its own feature rather than allowed to lapse quietly.

**Closed by feature 024 (2026-08-08), with one clause still open.** Defense 1 now exists:
`.github/workflows/ci.yml` in the parent repository runs both lanes against real stores,
the coverage run, the site build, and the docs and fence checks. Coverage is measurable
for the first time, and the answer is mixed — Principle VI's 70% clause is **met**
(86.55% statements, 78.07% branches across both lanes), while its 100%-branch clause for
ordering, idempotency and tenant isolation is **not**: `repository.ts` measures 85.91%.
That figure is pinned as a ratchet so it cannot slide, and closing it belongs to the next
chapter that touches the repository layer. The clause requiring each chapter's quickstart
to run unmodified in CI stays partial until the chapter tags exist. See
`specs/024-coverage-and-ci/notes.md`.

---

## 7. Risks specific to the tutorial

| # | Risk | Mitigation |
|---|---|---|
| T1 | **Scope gravity** — the product grows features the tutorial doesn't need | The SRS is frozen as the tutorial's contract; new ideas go to Part 8's exercises |
| T2 | **Part 0 bounce** — readers skip the paper and miss the spine | Forward references, the skip-safe summary, and Rule 3's constant back-linking |
| T3 | **Currency decay** — library/K8s/ClickHouse versions drift over months of writing | Pin everything in 1.1; one dedicated version-bump pass in stage G; checkpoints catch breakage |
| T4 | **The lonely middle** — Parts 3–4 lack Part 2's drama | Each chapter keeps Rule 1's failure-first structure; the isolation gauntlet and "watch Postgres hurt" demos carry the drama |
| T5 | **Estimate optimism** — 51 chapters is a book | It *is* a book; the incremental-publish strategy (§5) is the honest response, and Season 1 (Parts 0–2, 17 chapters) is a complete artifact on its own |

---

## 8. Immediate next actions

1. **Write the Tuan test suite specification** (the Part 2 milestone) — it defines Part 2's
   done-ness and forces the WebSocket protocol details that the API spec document still
   owes us. This finally makes the API spec the critical path twice over.
2. **Scaffold the monorepo** exactly as chapter 1.1 will describe it — building it *is*
   drafting the chapter.
3. **Draft chapter 2.7 ("The tunnel") early**, out of order — it is the series' flagship
   chapter; if its bug-then-fix structure works on a test reader, the format is validated;
   if not, better to learn before 46 other chapters exist.

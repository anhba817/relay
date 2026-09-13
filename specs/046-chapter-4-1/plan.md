# Implementation Plan: Chapter 4.1 — the question the counters can't answer

**Branch**: `046-chapter-4-1` · **Date**: 2026-09-12 · **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/046-chapter-4-1/spec.md`

## Summary

Part 4 opens on CON-01, and the opening chapter has to show the failure before the machinery.
The planned demonstration — *"run the metering query against Postgres under write load"* — could
not be run, because Part 3's metering is two pure functions on the send path and the quotas
module holds no aggregate at all (R1).

**What replaces it is a shape mismatch.** `messages` carries no `environment_id` and nothing
indexes `created_at`, so FR-ANL-05's daily question costs a join and a scan, against a ClickHouse
table ordered by exactly those two columns. The chapter takes four numbers — the query's cost,
write latency beside it, and both again after the index that would fix it — and the fourth is the
argument: **the fix taxes every write for a question no write asks.**

**This chapter ships no product code.** It adds a seeder to `scripts/scale/` and publishes
measurements. Everything it proves is proved against the platform as Part 3 left it, which is why
FR-002 and FR-013 forbid it from changing the schema even temporarily at its own tag.

Research corrected two assumptions before either cost anything, and both are in
[research.md](./research.md) with the wrong version kept: the bot question was already answered
in `docs/10` §0 and was searched for in the wrong module (R3), and "write load" is capped at ten
sends per second by `DEFAULT_LIMITS.send`, so the chapter measures latency and not throughput
(R6).

## Technical Context

**Language/Version**: TypeScript 5.x, Node.js 22 (ADR-01, constitution VII). The seeder is an
`.mjs` script beside `scripts/scale/load.mjs`, matching what is there.
**Primary Dependencies**: none new. `pg` through the api's existing `dist/db/client.js`; no ORM
in the seeder's bulk path (R5).
**Storage**: PostgreSQL only, in scratch databases none of which is the lane's — two at a time, and up to eight across the feature once T044's falsifications and T047's three volumes have each made their own. ClickHouse is named
in `compose.yaml` and stays untouched — it is movement II's.
**Build dependency**: both scripts need `services/api/dist`. `corpus.mjs` migrates its database
with the repository's own runner and `measure.mjs` spawns `dist/main.js`, so `pnpm build` precedes
everything — and `measure.mjs` refuses a `dist` older than `src`, because a stale one measures
another tag (045-77).
**Testing**: the measurement is not a test — it is verification method **A**, which is what
FR-ANL-08 and NFR-PRF-02 specify. **The seeder is verified by demonstration, not by unit test**,
and that changed during analysis: `scripts/` matches none of `vitest.coverage.config.mts`'s four
`include` globs and is not a workspace package, so a `.mjs` test there is collected by nothing.
Nothing in this chapter joins `test:integration`, because a million-row corpus in the lane would
break every whole-table assertion the lane already has (045-74).
**Target Platform**: Linux, compose stack on `RELAY_POSTGRES_PORT=15432`
**Project Type**: monorepo — this chapter touches `relay-platform/scripts/scale/` and
`relay-tutorial/app/(en)/part-4/…`
**Performance Goals**: none set by this chapter. It measures against NFR-PRF-02's published p95
of 150 ms and reports FR-ANL-08's 2-second target as the bar the second store must clear.
**Constraints**: no migration, no schema change at the chapter's tag, no rows left behind, and
the corpus never touches the test lane
**Scale/Scope**: ≥1,000,000 messages **inside both of the query's predicates** — the subject
environment and the 90-day window, which is what `subject.messages_in_window` reports — across
≥2,000 channels. That is 1,600,000 rows in the database at the defaults; the unqualified figure
stood here through two analysis passes that corrected it everywhere else. **Up to eight
databases** across the feature, two at a time; four numbers; two new scripts; ~2,000–4,000 prose
words

**Unknowns**: none blocking. Seven research questions closed against the tree; two open items are
recorded at the end of [research.md](./research.md) and neither prevents writing — the tag
namespace collision (which blocks *tagging*, not authoring) and whether the measurement will show
a cost worth acting on, which FR-010 already answers either way.

## Constitution Check

*GATE: evaluated before Phase 0 and re-evaluated after Phase 1 design. Both results below.*

| Principle | Bearing on this chapter | Verdict |
|---|---|---|
| **I — Tenant isolation** | The analytical query is tenant-scoped by construction: it reaches `environment_id` through `channels`, which is the hop the tenancy catalogue already follows, and the chapter's whole point is that the hop costs something. The seeder creates environments and writes only inside them. No route, no reader, no new table — so the isolation gauntlet has nothing new to attack. | **PASS** |
| **II — No acknowledged message lost** | Nothing on the send path changes. The send loop is a client. | **PASS** |
| **III — Two data paths, never crossed** | The principle's first clause is *"analytical queries MUST NEVER execute against the operational database."* **This chapter executes one, deliberately, to show why the clause exists.** It runs against a scratch database that serves no traffic, never against the lane and never against a deployment — and the chapter is the argument for the clause rather than an exception to it. Constitution III also fixes the 0.1% reconciliation bound that movement IV must meet; R4 records the one input that makes the two sides diverge legitimately. | **PASS, and see below** |
| **IV — Single writer** | The seeder is the only writer to the scratch database, and it writes before any measurement starts. | **PASS** |
| **V — API-first** | No public surface changes. No error code, no route, no frame. | **PASS** |
| **VI — Requirement-driven** | Nineteen requirements, eight criteria, tracing to FR-ANL-01/05/08/09, NFR-PRF-02 and CON-01. The measurements are verification method **A**; the seeder is **D**, a demonstration at three volumes whose reported counts are compared against the database. **VI's 70% coverage clause does not reach this chapter's files and the reason is worth stating rather than leaving implicit**: `vitest.coverage.config.mts`'s `include` is `packages/*/src/**/*.ts` and `services/*/src/**/*.ts`, so nothing under `scripts/` can move the ratchet — and nothing under `scripts/` can be collected by a lane either, which is why the unit tests became a demonstration. | **PASS** |
| **VII — Boring by design** | No new service, no new dependency, no new language, no new table, no migration. One script in a directory that already holds two. | **PASS** |

**III IS THE ONE WORTH ARGUING, AND THE ARGUMENT IS NOT "IT IS ONLY A SCRATCH DATABASE."**

Principle III forbids analytical queries against the operational store. A chapter that
demonstrates CON-01 by running one is either a violation or the clearest possible statement of
the principle, and which it is depends on something checkable: **does any code shipped at this
chapter's tag execute that query?** It does not. The query lives in the chapter's prose and in a
measurement script under `scripts/scale/`, which no service imports and no lane runs. No
production path gains an analytical read.

Recorded here rather than in Complexity Tracking because no violation is being justified. If a
later reader disagrees, the thing to attack is the claim in the preceding paragraph, not the
verdict.

**NO ADR IS EXPECTED, AND THE PLAN SAYS SO IN ADVANCE.** Chapter 3.23's plan said the same and
was wrong within one phase; 3.24's predicted one and was right. This chapter introduces no
decision that an ADR records — no driver changes, no alternative is rejected in the
architecture's voice. **If one becomes necessary, the likeliest cause is the seeder's bulk-insert
path bypassing the repository layer**, which touches ADR-16's *"Drizzle, confined to the
repository layer"*. R5 argues that a measurement script is not a service and the constraint is
about services; if that argument fails on review, an ADR is owed rather than a comment.

### Post-design re-evaluation

Re-run after `data-model.md`, `contracts/` and `quickstart.md` were written. **No verdict
changed.** Two things the design added were checked against the gate:

- The **counterfactual database** is a second database rather than a second corpus (R7). It
  carries a column and an index that exist nowhere in the repository. Constitution VII's
  migration rule is about migrations; this is a statement against a throwaway copy and the design
  forbids it ever becoming a file (FR-013, SC-005).
- The **seeder's contract** is a published interface (SC-006). That makes it more than a script,
  and VII's "new services require justification" was tested against it: it is not a service, it
  holds no state, nothing imports it, and it runs by hand.
- **`measure.mjs` spawns `services/api/dist/main.js`** so the send loop has something to send to —
  added after analysis found no task said how the loop reached a database no running service was
  pointed at. It uses `PORT=0` and reads the port from the child's log line, the pattern
  `load.mjs:46` already uses and the one that replaced nine hand-allocated port bands.

## Project Structure

### Documentation (this feature)

```text
specs/046-chapter-4-1/
├── plan.md              # this file
├── spec.md
├── research.md          # Phase 0 — seven questions, two corrected assumptions
├── data-model.md        # Phase 1 — the corpus, the measurement record, the databases
├── quickstart.md        # Phase 1 — reproducing the four numbers
├── contracts/
│   └── seeder.md        # Phase 1 — the interface movement IV reuses
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks — not created here
```

### Source code

```text
relay-platform/
├── scripts/scale/
│   ├── seed.mjs            # exists — users and channels for NFR-SCL-01, writes no messages
│   ├── load.mjs            # exists — socket ladder for NFR-SCL-01
│   ├── corpus.mjs          # NEW — creates and MIGRATES its database, mints a credential and
│                           #       a bot sender, then bulk-writes a corpus to a requested volume
│   └── measure.mjs         # NEW — spawns the api at PORT=0 against the corpus database,
│                           #       runs the query and the send loop, reports the four numbers
└── services/api/src/db/schema.ts    # READ ONLY — FR-014 re-derives the index facts from it

relay-tutorial/
├── app/(en)/part-4/chapter-01/<slug>/
│   ├── page.mdx
│   └── figures.ts
└── app/(vi)/vi/part-4/chapter-01/<slug>/   # 045 FR-010/FR-011
```

**Structure Decision**: the platform work is three files in `scripts/scale/`, a directory that
already exists for exactly this purpose and that no service imports. Nothing under
`services/` changes. `schema.ts` is read and never written — FR-014 obliges the chapter to
re-derive its index claims from it at this chapter's tag rather than inherit them from
`docs/12-part-4-structure.md`, where the count would be true of one commit only.

The tutorial side is one chapter in both locales. Part 4's chapter directory naming follows the
global-ordinal decision recorded in `docs/12-part-4-structure.md` §2.1 —
`part-4/chapter-01/<slug>` — and **the git tag for it cannot be cut until the `part3-chN` /
`rework/part3-chN` collision is resolved**, which is tracked as an assumption in the spec and not
as this chapter's work.

## Complexity Tracking

No Constitution Check violations. Table omitted.

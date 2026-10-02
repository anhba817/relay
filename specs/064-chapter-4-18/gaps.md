
## 064-1 — ADR-31 through 34 are in the SAD and nowhere in `docs/06`

**Chapter 4.5 wrote the rule and four ADRs have been written since without it.** *"An ADR
lives in two documents — the SAD's summary and `docs/06`'s argument. Ten passes amended the
summary and none opened the 98-line deep dive."*

    ADRs in docs/06-adr-deep-dives.md   01 … 30, then 35
    ADRs in docs/05-sad.md              … 31, 32, 33, 34, 35

**31, 32, 33 and 34 have a summary and no argument**, which is the half that carries the
rejected alternatives and the reversal condition — the two things constitution VII actually
requires. ADR-35 is written in both, deliberately, because writing it into the summary alone
would be choosing to repeat a defect that is already written down.

Backfilling the four is not this chapter's. What it would cost is four arguments reconstructed
from their summaries plus whatever their features' `baseline.txt` holds, which is where the
measurements are.

**And nothing checks it.** A gate comparing the two ADR lists is four lines and would have
caught this at 4.13.

## 064-2 — the moderation set's membership rule is a judgement nothing can check

`moderation-routes.itest.ts` checks that every tenant-reachable mutating route **has** a
classification and that every classification names a route. **It cannot check that the
classification is right**, and the rule the spec proposed misclassified two of 24 in the same
direction — `POST …/members` and `PATCH /v1/users/:externalId`, both excluded after the fact
on the grounds that the line is *standing, not data*.

So a later chapter adding a route gets a red check telling it to decide, and no help deciding.
The procedure in `moderation-routes.ts`'s header is what there is, and it is prose.

This is recorded rather than solved because the alternative — a predicate over route metadata
that decides membership automatically — would be a second hand-maintained table wearing a
derivation's clothes, which is the thing chapter 4.8 refused one registry over.

## 064-3 — nothing records administrative access, and the audit log cannot

NFR-SEC-10: *"Administrative access to production data shall require multi-factor
authentication and shall be logged to an immutable audit trail."*

Three obligations, none met. MFA is an identity-provider property outside the platform.
Nothing records a `psql` session at all. And the trail this chapter ships **cannot** hold that
actor to account: the trigger is dropped by one statement from the role an operator would be
using, which is measured in ADR-35.

The reversal condition is the fix for all three at once — a separate, non-superuser role for
the application — and it is a deployment change rather than a chapter.

## The carried ledger, re-measured rather than copied

Four of 043's twenty-three carried items were wrong when re-measured and three closed with
nobody working on them. So each of these was checked against the tree today.

| item | from | status now |
|---|---|---|
| **063-2** — one upload in six waits five or six sweeps | 4.17 | **carried, not re-measured.** This chapter touches no part of the media path and ran no upload. Re-measuring it would have cost a 25-trial battery for a number nothing here can move |
| **063-3** — the worker's log cannot say it is alive | 4.17 | **carried unchanged.** `main.ts` still logs a sweep only when `ready > 0 \|\| rejected > 0` |
| **063-4** — three feature-local ids with two meanings each | 4.17 | **worse than recorded, and confirmed by looking.** `FR-013a` means three unrelated things, in `specs/041`, `specs/031` and `specs/039`. This chapter qualified every id it added and **the sweep's own pattern missed one of its hits**, because `chapter 3.23's FR-013` puts the qualifier to the LEFT of the id. Still nothing runs either version of the check |
| **063-7** — `psubscribe("revision:*")` counts everybody's frames | 4.17 | **carried.** Not reproduced here: this chapter's suites subscribe to nothing |
| **050-8** — nothing drains the records the stack publishes | 4.5 | **carried and narrower than it was.** Two suites spawn the ingester for their own duration; two test files starting a process is still not a deployment |
| **062-12** — 68 of 139 files are unpinned, the lowest at 20.00% | 4.16 | **carried.** This chapter pins its own new files and moves nobody else's |
| **043-1** — an untitled fence is never compared to anything | 4.3 | **carried, and this chapter leans on it.** All of 4.18's code excerpts are untitled, which is correct under rule 5 — a titled fence is a whole-body claim — and means none of them is checked against the repository. The 49 appendix hunks are what carry the chapter's real claim |

## 064-4 — `pnpm lint` is green and a stricter invocation is not

`eslint src --max-warnings 0` reports one unused-disable warning in
`services/api/src/internal/session.perf.itest.ts`, a file this chapter never opened. The
gate's own script carries no `--max-warnings` and exits 0, which is the number phase 1
recorded and the number CI will produce.

Recorded because the reflex that finds it is the wrong one: an ad-hoc command stricter than
the gate reports a failure the project does not have, which is the mirror of a checker that
cannot fail. **Run the gate's invocation.** The warning itself is one line and belongs to
whoever next opens that file.

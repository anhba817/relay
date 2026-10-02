
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

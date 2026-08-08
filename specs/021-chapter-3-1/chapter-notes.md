# Chapter notes — 3.1, Tenants All the Way Down

Provenance for the published chapter at
`relay-tutorial/app/(en)/part-3/chapter-01/tenants-all-the-way-down/`.

These notes used to live in a `DRAFT-HEADER` comment inside a draft copy of the
chapter. That draft was inherited ceremony: feature 020 needed drafts because it
wrote seven chapters *ahead of* their code, unpublishable until the code caught
up. This chapter was written **after** its code, on purpose (plan.md sequences
US2 before US1), and published the same day — so the draft was a byte-identical
duplicate of 1,835 lines that no checker validated, with a real risk of somebody
editing the wrong copy. It was deleted and its metadata moved here, where it
belongs to the feature rather than to the site.

## Tag

`part3-ch1` — intended; not cut, like every Part 2 tag.

## Fences (new files, shown whole)

- `services/api/migrations/0002_tenancy.sql`
- `services/api/src/tenancy/oauth.schema.ts`
- `services/api/src/tenancy/state-cookie.ts`
- `services/api/src/tenancy/oauth.provider.ts`
- `services/api/src/tenancy/signup.controller.ts`
- `services/api/src/tenancy/tenancy.module.ts`
- `services/api/src/tenancy/oauth.test.ts`
- `services/api/src/tenancy/signup.itest.ts`
- `scripts/signup-walk.mjs`

## Amendments (hunked diff fences)

- `services/api/src/db/schema.ts` — `organisations`, `humans`, `memberships`;
  the 2.1 `applications` stub replaced; `UNIQUE (application_id, kind)`
- `services/api/src/db/repository.ts` — `createEnvironment` mints an
  organisation; `provisionOrganisation` added to the admin surface
- `services/api/src/app.module.ts` — registers `TenancyModule`

## Documents touched

- `docs/05-sad.md` — ADR-18 (two user populations, never merged)
- `docs/06-adr-deep-dives.md` — the matching deep dive; the closing section now
  names a fourth recurring theme and reads "the eighteen"

## Commands

```
pnpm lint && pnpm typecheck && pnpm test          # 86 unit, Docker-free
pnpm test:integration                            # 60 across 11 files
node scripts/signup-walk.mjs                     # the transcript the chapter quotes
```

## Verification

1. **Walk transcript**, captured live: the first authentication reported
   `created=true`, the second `created=false` with the same three ids, and a
   real `state` value presented without its cookie answered 400.
2. **Lane counts at the tag**: 86 unit (api 6 → 18) and 60 integration across
   11 files (api 36 → 44). Baseline before this feature: 74 and 52.
3. **Battery**: 3,155 words, Why 2, Trap 1, Skip 1, Fwd 1, Chk 1, Figures 3,
   298 diff lines — every threshold met.
4. **Traceability**, checked before publication: 11 requirement identifiers, 4
   ADRs and 7 table names in the prose, all verified against `docs/04-srs.md`,
   `docs/05-sad.md` and `schema.ts`. Zero invented identifiers.

## Findings the plan did not anticipate

1. **The migration would not have applied.** drizzle-kit generated
   `ALTER TABLE "applications" ADD COLUMN "organisation_id" uuid NOT NULL`
   against a table holding 237 rows from Part 2's test runs. Rewritten by hand
   as add-nullable → backfill → `SET NOT NULL`, with the review disposition
   recorded in the migration header. This became a section of the chapter.
2. **Two integration tests asserted against the suite's own history**, not
   against behaviour: one reused an identity an earlier test had already signed
   up, the other inherited an application that a *previous run* had already
   given a production environment. Both now mint their own identity — 2.1's
   per-suite-environment lesson one level up. Written up in the chapter.
3. **express 5 ships no types** and `@types/express` is absent, so `@Res()` was
   typed structurally (two method signatures) rather than adding a
   devDependency. Keeps the plan's zero-new-dependency claim true.

## Fixed forward (spec FR-017)

Chapter 2.1's `applications` stub is replaced by the real table and its
DECISION comment removed; `createEnvironment`'s comment block is rewritten,
since it now mints the organisation above the application it always created. No
defect was found in any earlier chapter's prose.

## Deferred, with reason

**T037 — branch-coverage measurement over the isolation code (constitution
VI)** is not done. The workspace has no coverage tooling, and adding
`@vitest/coverage-v8` would change `services/api/package.json` — a file three
published chapters fence — so it cannot be added without documenting a
toolchain change that is not this chapter's subject. It belongs with the CI gap
the analysis flagged (no `.github/workflows` exists in any of the three repos),
and both should land together in their own piece of work.

## Baseline

Built on the uncommitted Part 2 state (`part2-ch8` intended, not cut). Part 2's
tags are still uncut, so this chapter's SKIP AHEAD and CHECKPOINT name
`part3-ch1` on the same basis.

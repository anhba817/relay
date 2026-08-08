# Implementation Plan: Coverage measurement and CI

**Branch**: `024-coverage-and-ci` (no branch cut; work proceeds on `main`) | **Date**: 2026-08-08 | **Spec**: [spec.md](./spec.md)

## Summary

Install the instrument constitution VI has required since the constitution was
written, and the CI that runs it. No chapter is published: this feature teaches
nothing, it measures.

Three decisions shaped it, all forced by facts rather than taste.

**Coverage must span both lanes.** The code NFR-MNT-02 names — ordering,
idempotency, tenant isolation — lives in `services/api/src/db/repository.ts`,
and most of its branches are reached only by integration tests. A unit-only
coverage run would produce a comfortable number about the wrong thing.

**The tooling cannot hide.** Every manifest in the workspace is fenced by some
chapter, so adding a devDependency necessarily breaks the fence chain. The
options were to pollute a published chapter with code it never teaches, or to
give the chain a place for amendments that belong to no chapter. The second is
better and is now built.

**The 100% clause is not met, and the honest move is to say so.** Measurement
puts `repository.ts` at 85.91% branch coverage. Setting the threshold to 100
would make CI permanently red on its first day and teach everyone to ignore it;
setting it to 85 and calling the requirement satisfied would be a lie. It is
pinned at today's figure as a ratchet, with the gap recorded and owned.

## Technical Context

**Adds**: `@vitest/coverage-v8` and `unplugin-swc` to the workspace root, one
root script, one new root config, one CI workflow, one fence-chain mechanism.

**Touches (fenced)**: `relay-platform/package.json` only — recorded in
`relay-tutorial/fences/post-series.md`.

**Cannot verify here**: no GitHub Actions runner exists in this environment. The
workflow is checked by parsing it and by comparing its commands to the local
gates one for one. Its first real execution is the first push, and that is
stated rather than implied away.

## Constitution Check

| Principle | Verdict |
|---|---|
| **VI — Requirement-driven, test-verified** | **PARTIALLY MET, for the first time measurably.** The 70% clause is met (86.55% statements, 78.07% branches). The 100%-branch clause is **not** (85.91% on `repository.ts`) and is now a number instead of a question. The CI clause is met for the gates; the "quickstart runs unmodified in CI" clause remains partial, because per-chapter quickstarts need the chapter tags, which do not exist. |
| **VII — Boring by design** | Two devDependencies, one config, one workflow. No coverage dashboard, no badge service, no reporting infrastructure. |
| **I–V** | Untouched: no product code changes. |

## What this deliberately does not do

- Write tests to close the branch gap. The instrument is this feature; using it
  is the next chapter's work, and inventing tests to hit a number is how
  coverage metrics become theatre.
- Publish a chapter. Part 6 owns CI as a subject; when it arrives, the
  post-series amendment should fold into it and disappear.
- Cut the chapter tags, which the quickstart-in-CI clause ultimately needs.

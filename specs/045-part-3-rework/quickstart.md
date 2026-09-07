# Quickstart — validating the Part 3 rework

Ten scenarios. Each proves one success criterion and each is runnable.

## Prerequisites

**No lane, no containers, no credentials for scenarios 1 through 6** — this feature changes
documentation and comments, and the fence chain is a text comparison. Scenarios 7 and 8 need the
stack, because they are the control that proves the platform did **not** change.

    cd relay-platform
    RELAY_POSTGRES_PORT=15432 docker compose up -d --wait   # scenarios 7-8 only
    node scripts/reset-lane.mjs --yes-this-is-my-test-lane

`grep` on this machine is **ugrep 7.8.4**, not GNU grep, and the two disagree on a grouped alternation
followed by negated classes. Every counting scenario below is written in Python for that reason, and
every pattern carries a positive control. **A pattern that fails its own example is broken, not
evidence.**

---

## Scenario 1 — the instrument reproduces today's chain (Phase 1 gate)

Before anything moves, point the synthesiser at the **current** order and require byte-exact output.

    node specs/045-part-3-rework/replay.mjs --order current --out /tmp/rebuilt
    diff -r /tmp/rebuilt relay-tutorial/app/(en)/part-3

**Expected** (SC-005): no differences. **Failing means the generator cannot rebuild what already exists**, and
nothing it produces for a new order can be trusted. This scenario is the reason Phase 1 exists.

---

## Scenario 2 — every cluster is contiguous (SC-001)

    python3 specs/045-part-3-rework/check-movements.py

**Expected** (SC-001): eight of eight, against five of eight today. **Failing means** a chapter is
grouped with a subject it does not belong to, which is a mapping error rather than a build error.

---

## Scenario 3 — no ordinal survives in fenced source (SC-002)

    python3 specs/045-part-3-rework/check-references.py

**Expected** (SC-002): zero in fenced files, against 985 measured with the specification's pattern and
**1,429** with the wider one. Report both, and report the pattern.

**Run the positive control in the same command.** A reference scan that reports zero because its
pattern is wrong is exactly the failure this project filed as `gaps.md` 044-1.

---

## Scenario 4 — the fence chain replays (SC-005)

    cd relay-tutorial && pnpm check:fences

**Expected** (SC-005, SC-010): 240 fenced files replay across **42** chapters, mirrors intact — 41
today, the split adds one — **and the appendix's 48 existing hunks all still apply**. `check:fences`
replays `fences/post-series.md` after the last chapter, so a stale appendix hunk fails here as an
`APPLY` problem naming the file, not as a mismatch at the end. This is the criterion that
catches a re-derived chain landing on the wrong file, and it is byte-exact.

**Regenerate at a wider context if a pre-image matches twice.** `-U6` is a default, not a rule:
`resume.itest.ts` needed `-U10` because eight session stubs are byte-identical past six lines, and
`-U8` was worse than either.

---

## Scenario 5 — every synthesised state compiles (SC-005's other half)

    node specs/045-part-3-rework/replay.mjs --order new --typecheck-each

**Expected** (SC-003, SC-004): every intermediate state typechecks; each of the **five emitted**
webhook event types has a producer in an earlier chapter, with the three declared-but-unbuilt ones
recorded rather than counted; and every chapter that reuses the outbox or the subject grammar follows
the chapter teaching it. **Failing is a finding about the order, not a bug
in the tool** — a state that does not compile means a chapter teaches code that calls something a
later chapter introduces, so the proposed order violates a real dependency. Record which pair, and
move one of them.

---

## Scenario 6 — the Vietnamese mirror holds (SC-006)

    cd relay-tutorial && pnpm check:fences     # MIRROR problems are reported here

**Expected** (SC-006): **25** Vietnamese chapters present — one per English chapter, not 24, because the
split creates one that never existed — each with a fence list and fence bodies byte-identical to its
English counterpart, and placeholder prose between them.

**A deleted Vietnamese page passes this scenario and fails the feature.** The mirror check skips
chapters that do not exist, so absence is silent. Count the pages as well as running the check.

---

## Scenario 7 — the platform did not change (SC-007)

    cd relay-platform && pnpm test:integration

**Expected** (SC-007): green, in **225.45 s ± 10%** — the mean over twenty runs at feature 044's close-out,
stdev 1.15. This is a tripwire, not a performance target. **Nothing in this feature is supposed to
change behaviour**, so a moved duration or a red suite means something did.

**And the lane's own state is part of the instrument.** Record the row counts beside the timing:
76,980 environments and 791,520 outbox rows at 044's close-out, on a lane `reset-lane.mjs` does not
touch by design.

---

## Scenario 8 — the excerpt-only files, checked another way (edge case)

Thirteen files are published only as `(excerpt)` and `check:fences` compares them to nothing. Comment
rewrites inside them are invisible to scenario 4.

    python3 specs/045-part-3-rework/check-excerpt-files.py

**Expected** (SC-002): zero ordinals remain in any of the thirteen. **This is the one place where a green gate
proves nothing**, and it is why the scenario exists rather than being folded into scenario 3.

---

## Scenario 9 — every old URL resolves (SC-008, FR-014)

    pnpm build && python3 specs/045-part-3-rework/check-redirects.py

**Expected** (SC-008): 48 redirects — one per *old* chapter per locale — each resolving to one of the
**50** pages that now exist; and a published mapping page naming all 24 old numbers.

**Check the split chapter by hand.** `/part-3/chapter-14/…` was one page and is now two; its redirect
has to choose, and the mapping page is where the other half is found.

---

## Scenario 10 — the navigation follows the renumbering (SC-009)

    python3 specs/045-part-3-rework/check-registry.py

**Expected** (SC-009): the chapter registry in `lib/tutorial.ts` and the filesystem agree in **both
directions** at 42 chapters — every declared path exists, every chapter page is declared.

**This scenario exists because no gate covered it and no requirement named it.** The registry is 810
hand-maintained lines read by the sitemap and six components, including the previous-and-next links on
every chapter. A renumbering that skipped it would leave `check:fences` green, `check:docs` green and
every link in the book dead. It agrees today at 41 and 41 — **unguarded, not broken**, which is the
harder condition to notice.

---

## The gate set, at the end

Fourteen, and every exit code captured **outside** a pipeline — `fail=1` inside a `for … | sort` runs
in a subshell and dies with it, which has printed "ALL GATES: GREEN" over a red one.

    relay-platform   pnpm typecheck · pnpm lint · pnpm build
    relay-tutorial   pnpm check:fences · check:docs · check:figures · check:srs · check:errors
    feature          the six instruments in specs/045-part-3-rework/

**Run `check:fences` after ANY source edit**, not only at the end — and note that an edit to one of
the thirteen excerpt-only files is invisible to it.

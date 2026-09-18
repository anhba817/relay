# Gaps — feature 055, repair the fence chain

Every carried item **re-measured** rather than copied. Six were carried in; four close, one is
corrected, one is unchanged. Seven are new.

---

## CLOSED

### 054-1 · `check:fences` exits 1 on every push — CLOSED

The whole feature. 110 → 0, and `ci.yml`'s tutorial job ends with a command that now reports
something. The per-kind baseline in `fences/baseline.json` that feature 054 designed and this
environment's guard refused as a CI bypass is not needed and should not be built: the refusal
was right, and repairing the chain is what the design was an alternative to.

### 050-4 · Eleven of the 36 HEAD problems name no file — CLOSED

All eleven declared `(excerpt)`, after reading each body. The entry's reading was right —
*"they can never be repaired by editing the platform"* — and its conclusion that "25 is the
number a chapter should be measured against" is superseded: the right number is neither 25 nor
110, for the reason in 055-2.

### 047-1 · `eslint.config.mjs` cannot take a fence — CLOSED

Recorded at 206 chain lines against 451 and *"a hunk cannot anchor on it"*. It can. The chapter
3.25 fence was re-anchored by replacing the region between its longest matching leading and
trailing runs, and the appendix hunk — which turned out to **duplicate** the refactor 3.25
performs — went from 571 body lines to 122 and closed the file's HEAD divergence with it.

### 048-3 · `vitest.coverage.config.mts` has diverged since before Part 4 — CLOSED

The entry said "diverged at line 29" and feature 054 sharpened it to *"no `env` block at all"*.
Both are now history: 15 bad hunks repaired, 743 differing lines reconciled in the appendix.
Chapter 4.9's prose-only note about this file is superseded by a hunk.

---

## CORRECTED

### 055-1 · FR-016's `END $;` was never in the prose — it was the applier

`gaps.md` and this feature's own T066 carried it as *"the published fence carries `END $;` where
the repository has `END $$;` — a reader copying that listing gets a syntax error."*

**The fence carries `END $$;`.** The checker produced the `$;`:

    node -e 'console.log("x".replace("x", "END $$;"))'   ->   END $;

`String.prototype.replace` reads `$$`, `$&`, `` $` ``, `$'` and `$<name>` in a **string**
replacement as substitution patterns, and `applyHunks` used the string form. Any fenced file
containing `$$` — `packages/test-harness/src/sentinel.sql` is `DO $$ … END $$;` twice — replayed
wrong. Fixed with a function replacement.

**It was causing APPLY failures too.** With the applier corrected and the original published
hunk restored, chapter 3.23's fence applies untouched: **two of the 42 "bad hunks" were never
bad.** And the repair had been compounding it — three rounds of regenerating against a corrupted
state stacked three dollars, reaching `+DO $$$` in the chapter and `+DO $$$$` in the appendix,
each round "fixing" the corruption by adding one more `$` for the applier to eat.

**A repair that keeps almost working is the shape of an instrument bug**, and two features filed
this one against the chapter.

---

## CARRIED, RE-MEASURED, STILL OPEN

### 043-1 · An untitled fence is never compared to anything — OPEN, unchanged

Re-measured at this feature's close: **360 untitled of 2,109 opening fences** — `app/(en)` 194,
`app/(vi)` 161, `fences/` 5. Unchanged by this feature, which touched titles and bodies and added
no fence without one. The entry's 2026-08 figure of "146 of 904" is two years of drift in one
ratio: 16% then, 17% now, and the absolute number more than doubled.

**What is outside every gate is now 614 fences**: 360 untitled and 254 the checker skips by name
(252 `(excerpt)` and one `.naive.` pair). This feature raised the second number by 30 and said so
each time.

### 050-3 · The Vietnamese chain is never compared to the repository — OPEN, and now measurable

The entry describes the mechanism in prose. The numbers, from this feature's own instrument:

    const en = replay("en", problems)     check-fence-chain.mjs:204
    the appendix loop                     mutates en.state only
    const vi = replay("vi", problems)     :300, after the appendix AND after HEAD

    paths in the chain          en 285 · vi 276        at the opening
    turbo.json, final           en  75 · vi  62

So a "vi final state" is the vi chain's own end, which nothing compares to anything. What the
Vietnamese half gets is `MIRROR`: byte-identical fence bodies against its English twin, matched by
title within a chapter.

**And `MIRROR` is two checks where the artifacts read it as one.** It joins each chapter's
`lang title` list and, on a mismatch, records **one** problem and `continue`s — past every body
comparison in that chapter. At 0 the property means what it says; at any other value it counts
chapters skipped, not fences wrong, and the chapters it names can hold up to 40 titled fences.

---

## NEW

### 055-2 · A count of 110 was neither 110 defects nor an upper bound on them

The cascade arithmetic FR-015 asks for, and it runs both ways.

**Downward: 42 bad hunks were cleared by 24 repair operations, so 18 were shadows.**
`vitest.coverage.config.mts` alone: seven repairs cleared fifteen problems, and one appendix hunk
cleared five at once. Repairing chapter 3.22's fence made 3.23's apply on its own.

**Upward: ten files could not be compared to the repository at all.** A checker reports the first
failure per file, so a file with a broken hunk never reaches its HEAD comparison.
`session.itest.ts` turned out to be **1,322 lines** behind the tree, `event.test.ts` 406,
`turbo.json` and `packages/e2e/src/harness.ts` 7 each. The 25 divergences became 29, and the
2,356 differing lines became 3,471.

**And four divergences were caused entirely by their own failing hunk** — `eslint.config.mjs`,
`credentials.itest.ts`, `presence.itest.ts` and `package.json` closed when the hunk did.

25 − 4 + 2 (phase 4) + 6 (phase 5) = 29. **The next reader of a fence-chain number should know
it counts files-with-at-least-one-problem, not problems.**

### 055-3 · `check:errors` is a script no workflow runs

`relay-tutorial/package.json` defines five `check:*` scripts. `ci.yml` runs four of them. Zero
jobs — `tutorial`, `platform` or `outsider` — run `check:errors`, which compares
`docs/08-error-reference.md` against `relay-platform`'s built `packages/protocol/dist/codes.js`.

It passes today (28 codes, 28 sections, 6 close codes). It has no runner, which is 051's
*"referenced by no script, service or config"* and 054's *"the daily job has no runner of any
kind"* arriving in the tutorial's own gates. Adding a step needs the platform built first, which
is why it was left out and why leaving it out should be a decision rather than an oversight.

### 055-4 · Five of the seven gate scripts exit 0 when their corpus is absent

    check-docs-drift.sh:36        parent docs directory not found — skipping drift check
    check-srs-ids.sh:41           SRS not found — skipping (standalone clone?)
    check-revision-order.mjs:34   parent docs directory not found — skipping
    check-fence-chain.sh:11       relay-platform not found — skipping fence check
    check-fence-chain.mjs:200     relay-platform not found — skipping

SC-001 names one of them. This feature found the same hole three separate times before counting
it, which is the project's own rule about classes arriving late. Every one of the five prints a
line with a count in it when it really looked, so **asserting the success line rather than the
exit code costs nothing and is what T092 now does.**

The best statement of the rule in these repositories is a comment in the gate nothing runs —
`check-error-codes.mjs:33-35`, *"the difference between a skip somebody investigates and a skip
somebody ignores."*

### 055-5 · A mis-sited copy of the checker replays nothing and exits 0

`PLATFORM` is resolved from `import.meta.url`, so the identical file run from another directory
prints `relay-platform not found — skipping` and exits 0 having compared nothing. **Fence-chain
rule 1a instructs you to make exactly that copy**, and feature 054 made it twice.

This is the measurable argument for `--dump` being a flag, and it is a standing hazard for anyone
who follows rule 1a as written. Rule 1a should say where the copy has to live.

### 055-6 · Four amendments are declared rather than verified, and what that costs

FR-012's exceptions, converted **and** recorded:

    session.itest.ts at 3.17    hunks of +13/-0, +138/-0 and +33/-2 whose context is
    session.itest.ts at 3.22    9 of 14, 3 of 12 and 1 of 22 lines present in the chain
    event.test.ts at 3.17       the chain holds 318 lines where rework/part3-ch16 holds 980
    fanout.itest.ts at 3.17     558 lines of listing for a three-line change: 279 per problem

Publishing the tag's body would have jumped the reader from the 281 lines chapter 3.3 shows them
to 980 with nothing in between — 699 lines of code no chapter discusses.

**What it costs:** those four chapter amendments are no longer compared to the repository, and
the files' end states are reconciled by the appendix instead. `session.itest.ts` keeps its body
at 3.3 and its 3.5 and 3.9 diffs, so it is verified for six chapters and declared for two.
`fanout.itest.ts` leaves the chain entirely.

**What it would take:** a whole body at 3.17 for each — 980 lines for `session.itest.ts`, 297 for
`event.test.ts`, 558 for `fanout.itest.ts`. The line count is not the obstacle; the jump is.

### 055-7 · The eight new listings have no introduction in Vietnamese

Each of the eight whole bodies published in phase 5 gained an English sentence saying what it is,
because five of them landed immediately after a closing fence with nothing between. FR-011
forbids altering translated prose, so **the Vietnamese chapters carry a listing of up to 333 lines
with no sentence in front of it.** `MIRROR` is unaffected — it compares fence bodies and the title
list, not the prose around them — so no gate will ever mention this. It is the translator's, and
it is written down here because nothing else would say it.

### 055-8 · The chain holds 285 paths and the titles say 286

Ten paths are titled in English chapters and in no Vietnamese one, all in 4.5 through 4.9 — the
translation frontier. The state gap is **9** (285 against 276) where the title gap is **10**, so
one path is titled and never reaches the chain. It was not chased: the count is right on both
sides of the comparison this feature is about, and the discrepancy is a fact about the
translation frontier rather than about the chain.

---

## WHAT ZERO DOES NOT MEAN

Not that the chapters are readable. Not that the listings are pedagogically right. Not that the
**360 untitled fences** or the **254 the checker skips by name** mean anything — 614 fences are
outside every gate and this feature moved 30 of them further out, deliberately, each with a
record. Not that the Vietnamese chain is compared to the repository: it is compared to its
English twin and never to `relay-platform` (050-3).

And the chapter count in the success line is **pages the walker found**, not pages verified: five
of the 52 are `part-0` and carry no titled fence at all.

**One property, and it is worth having.** Every titled fence in the series replays onto
`relay-platform`, byte for byte — which is the promise `docs/07` §6 makes to a reader who copies
a listing, kept for the first time since feature 045.

# Contract — the dump interface, and what a repaired fence must satisfy

Written before the work. Chapter 4.2's lesson about `contracts/` is that it is the artifact
nothing else reads, so every claim here is one a command can drive.

---

## `check-fence-chain.mjs --dump <dir>`

**What it does**: replays the chain exactly as the check does, then writes each path's final
replayed state to `<dir>/<path>`, creating directories as needed. Prints how many it wrote.

**What it must not do**: anything different from the check. Same parser, same hunk applier, same
chapter ordering, same appendix-applies-last. **A generator that replays differently from the
checker produces hunks the checker rejects for reasons neither of them explains** (fence-chain
rule 1a), and this feature regenerates about fifty hunks against it.

| property | how it is checked |
|---|---|
| it writes one file per chained path | `find <dir> -type f \| wc -l` equals the checker's own `N fenced files replay onto relay-platform` |
| it is the same replay | dumping twice gives byte-identical trees; dumping after a repair changes exactly the repaired path |
| it changes no verdict | `pnpm check:fences` reports the same count with and without the flag |
| it writes nothing when the chain is broken for a path | the state is whatever replayed — a failed hunk leaves the previous state, which is the state a new hunk must anchor on |
| it tolerates a leading `--` in its own arguments | measured on this pnpm: `pnpm check:fences -- --dump X` forwards **`-- --dump X`**, so the parser must find the flag by position-independent lookup rather than by treating `argv[0]` as meaningful. `pnpm check:fences --dump X` forwards cleanly and is the form the quickstart publishes |
| it prints its own file count | because the checker's `N fenced files replay onto relay-platform` line exists **only** when the count is 0, and the dump is needed at 110 |

**Why a flag and not a copy.** Feature 054 built this twice from a truncated copy and deleted it
each time, which is what rule 1a says to do for a single use. Fifty uses is a different shape:
`check-lane-scope.py` was a script nobody re-read, pointing at a worktree feature 045 had deleted,
reporting zero for a year with all ten of its controls firing (049-3).

**Why this is not a loosening.** The flag adds an output mode. It changes no threshold, exempts no
class, and alters no exit code. FR-002 forbids weakening what the checker *accepts*; this changes
what it can *print*. The distinction is stated here because "I changed the checker" is the
sentence this feature exists in order not to say.

---

## What a repaired target must satisfy, by class

### A fence that names no file

```
before   ```text title="the typo, now"
after    ```text title="the typo, now (excerpt)"
```

- The English title and its Vietnamese twin change together, or `MIRROR` unpairs them.
- The body does not change.
- `NOT_A_FILE` must then skip it: the target disappears from the report entirely rather than
  moving to a different class.
- **Eleven candidates and each is looked at.** The criterion is that the block is not a file's
  contents. All eleven are `lang=text` command output; if a twelfth ever looks like a listing,
  it is not this class.

### A chain with no opening

- A whole body appears at or before the first amendment, in a chapter **that discusses the file**.
- Its content is the file at that chapter, taken from `rework/part3-chN` — not from the working
  tree, which is up to twenty chapters ahead.
- Every existing amendment for that path still applies afterwards, checked by running, not by
  reading.
- If no chapter honestly introduces the file, the path leaves the chain as excerpts and the
  exception is recorded with its cost (FR-012). **The count improving is not the test**; whether
  a reader can still follow the chapter is.

### A hunk that cannot anchor

- Regenerated against `--dump`'s state for that path, at that point in the chain.
- `@@` hunks only — no `--- a/` or `+++ b/` headers.
- Each hunk's pre-image appears exactly once. Widen the context when it appears twice, and
  **verify before pasting**: `-U8` can be worse than `-U10`, because widening merges adjacent
  hunks and a merged hunk spans more repetition than either half did.
- The first failing hunk for a path is repaired and the file re-measured **before** the rest are
  touched. Nine of `vitest.coverage.config.mts`'s fifteen are shadows of one.

### A state that differs from the repository

- Repaired by a hunk **after** the last existing fence for that path — in `fences/post-series.md`
  unless a chapter genuinely discusses the change.
- **Never by regenerating an early fence.** `codes.ts` is fenced by 12 chapters,
  `app.module.ts` by 11, `vitest.coverage.config.mts` by 11 plus 9 appendix hunks, and feature
  045 measured one such regeneration taking the chain from 111 problems to 203.
- Measured only after that path's APPLY failures are repaired, because a divergence is whatever
  is left once every hunk has applied.

---

## The measurement loop

Run after **every target**, not every phase:

```
pnpm check:fences                     # total, APPLY, HEAD
```

| outcome | what it means | what happens |
|---|---|---|
| count falls by the target's own problems | the repair worked | record and move on |
| count falls by fewer | some were shadows of a different root, or a new one appeared | diagnose before the next target |
| count rises | the repair unanchored something downstream | revert or finish it within this target, and record both numbers |
| `MIRROR` above 0 | an English fence was repaired and its Vietnamese twin was not | fix before moving on |

**The loop's own positive control is phase 2.** Eleven declarations with no cascade risk must move
the count from 110 to exactly 99. If it moves by anything else, the instrument is wrong before
anything expensive has been attempted.

---

## What the close must show

- `pnpm check:fences` → **0 problems**, evidenced by the success line
  `N fenced files replay onto relay-platform across M chapters`. **Not by exit 0**, which the
  wrapper also returns when `relay-platform` is absent and nothing was replayed.
- A planted regression — one line changed in a fenced platform file, no chapter hunk — → **exit
  non-zero, naming that file**. Run red, not reasoned about.
- `MIRROR` 0 throughout, measured per locale repair.
- Zero files under `relay-platform/` in the feature's diff, which is a `git diff --stat` and not
  an assurance.
- The count of fences no gate reads, before and after. Measured 2026-09-17: **360 untitled of
  2,109 opening fences**, with **222 titles already declared `(excerpt)`**. After: untitled
  unchanged at 360, declared 233. `gaps.md` 043-1's *"146 of 904"* is a 2026-08 figure and is
  superseded by this measurement rather than repeated.

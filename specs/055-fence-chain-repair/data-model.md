# Data model — the fence chain

The "data" here is the chain itself. This document states what the entities are, what makes one
valid, and what states a problem moves through — because the feature's whole job is moving 110 of
them out of one state.

---

## Fence

A fenced code block in a published chapter **with a `title="…"` attribute**. Untitled blocks are
collected by nobody: `check-fence-chain.mjs:77` matches on the title, which is why **360 of the
2,109 opening fences** sit outside every gate — 043-1 recorded 146 of 904 in 2026-08 and the
ratio held at 17% while the number more than doubled.

| field | meaning |
|---|---|
| `title` | the path the fence claims, or a phrase that claims nothing |
| `lang` | the info string — `ts`, `diff`, `text`, … |
| `body` | the lines between the fences |
| `chapter` | the page that carries it; its position in the chain is the chapter's position |
| `line` | where it opens, which is how every problem is addressed |

**Three kinds, decided by title and language:**

- **A whole body** — `title="path"` with any language but `diff`. A claim that the file *is* these
  bytes at this chapter. 051-6: publishing three quoted lines under a path title makes the chain
  believe the file is three lines long, which feature 054 reproduced and paid two problems for.
- **An amendment** — ` ```diff title="path" ` carrying `@@` hunks only. `--- a/` and `+++ b/`
  headers are read as body text and fail (chapter 4.7 lost two attempts to it).
- **Not a file** — a title containing `(excerpt)` or `.naive.`, skipped in both loops
  (`:160`, `:211`). **The eleven prose-titled fences in this feature's scope belong to this kind
  and do not say so**; all eleven are `lang=text` command output.

A fourth form exists: `title="path (deleted)"` retires a path. The chain ends there and the check
inverts — the file must not exist.

---

## Chain

Every fence for one path, in chapter order, with `fences/post-series.md` applied **last**.

**Validity, in the checker's own three properties:**

| property | rule | failures today |
|---|---|---|
| `APPLY` | every hunk's pre-image appears in the predecessor state **exactly once** | 74 |
| `HEAD` | the state after the last fence equals the file on disk | 36 |
| `MIRROR` | each Vietnamese fence is byte-identical to its English twin, matched **by title** | 0 |

**`MIRROR` is two checks and the first one gates the second.** The loop joins each chapter's
`lang title` list and compares it; on a mismatch it records **one** problem and `continue`s,
**so none of that chapter's bodies is compared** (`check-fence-chain.mjs:307-314`). At 0 the
property means what it says. At any other value it counts **chapters skipped**, not fences wrong
— and the 41 translated chapters hold up to 40 titled fences each.

Two consequences the repair depends on:

- **A chain must open with a whole body.** An amendment with no predecessor is
  `diff … with no earlier fence to amend`, and 32 of the 110 are this.
- **The appendix cannot open a chain.** It applies after every chapter, so it can amend a path
  and never introduce one. The specification's FR-010 offers it as a fallback for missing
  introductions; that fallback does not exist.
- **`MIRROR` matches by title**, so renaming an English title without renaming its Vietnamese
  twin unpairs them — and unpairing one fence stops the other fences in that chapter being
  compared at all. Phase 3 renames titles in **6 chapters holding 128 titled fences**.

---

## Replayed state

What the chain produces for a path at a given point — **not** the repository tree, and the
difference is where 42 of the 110 come from.

    285 paths have a replayed state today
    vitest.coverage.config.mts   chain 318 lines · tree 1,182 · and no `env` block at all

A hunk must be generated against **this**, never against the tree (fence-chain rule 1a). The state
is only reachable by replaying, which is why the instrument this feature builds is a flag on the
checker rather than a `git diff`.

---

## Problem

One `[APPLY]`, `[HEAD]` or `[MIRROR]` line: a kind, a location in `relay-tutorial`, and a detail.

**The checker reports the first failure per file**, so a problem is not a defect — it is a file
with at least one. 25 files `differs at line N` and those 25 files hold **2,356** differing lines
— counted as `diff | grep -c '^[<>]'` against a dump written the checker's own way. **The figure
was 2,381 in six artifacts until analysis pass 8**, one too high per file, from a probe that read
the tree with a plain `split("\n")` and kept a trailing empty line the chain state does not have.
**One of the 25 is a pure append; 24 change lines in the middle.**

**And `differs at line 0` means the chain is a PREFIX of the tree.** The line number is
`findIndex(...) + 1`, so a −1 — no index where the two disagree — prints as 0, and both sides
then print `<eof>` because `final[-1]` and `disk[-1]` are both undefined. It is the signature of a
pure append and the cheapest repair there is. **One of the 25 prints it** (`.gitignore`), and it
was filed as the target whose repair might not exist.

**Four classes, and what each needs:**

| class | n | what a repair is |
|---|---|---|
| `hunk pre-image matched 0 times` | 42 | regenerate from the replayed state, first failure per file first |
| `diff … with no earlier fence to amend` | 32 | publish the file whole at or before its first amendment, with the content from `rework/part3-chN` |
| `<path> differs at line N` | 25 | append a hunk after the last existing fence — never regenerate an early one |
| `<title> does not exist in relay-platform` | 11 | declare it not-a-file |

---

## Target

The thing a problem is about: a platform file, or a phrase that names none. **47 of them** — 36
files and 11 phrases — and the top eleven carry 64 of the 110.

A target's problems are not independent. Within one file, the first failing hunk is frequently the
only real defect: nine of `vitest.coverage.config.mts`'s fifteen are anchored inside a block an
earlier failing hunk would have created.

---

## Repair state

The state machine each of the 110 moves through, and the only three terminal states:

    open ──────► repaired          the chain replays onto the repository for that target
         ├─────► declared          the fence names no file and now says so  (11 candidates)
         └─────► converted        cannot be repaired, so the fence stops claiming a file AND
                                   the reason, the measurement and the cost are written
                                   down (FR-012) — both halves, always

**THE SECOND HALF ALONE IS NOT A TERMINAL STATE.** A problem that is written up and left in place
is still a problem the checker counts, because nothing reads `gaps.md`. So `converted` ends at
`(excerpt)` — the same mechanism the eleven prose titles use — and the record is what stops that
being an exemption nobody looked at. An earlier draft of this document called the state
`recorded`, which named the half that does not move the number.

**`converted` is not a fourth kind of green.** A feature that reports "0 except for these" without
the arithmetic has written the baseline it refused to write, which is the option this feature
exists instead of. Every `recorded` item carries what it would take.

**Transitions are measured, not asserted.** The count is taken after each target (FR-003), because
a repair can raise it: one foundation fence regenerated took the chain from 111 to 203.

---

## Locale pair

An English fence and its Vietnamese twin, matched by title within the same chapter.

Measured: **30 vi problems, all 30 mirroring an en problem exactly, zero vi-only.** The pair is
the unit of edit and the English side is the unit of diagnosis. `MIRROR` must read 0 after every
repair, which is the check that the copy actually happened — **and only at 0**, because a
non-zero reading is a chapter whose bodies went uncompared rather than a fence that differs.

**The pair is also the unit of every count.** The 2,109 opening fences are 1,071 English, 1,005
Vietnamese and 33 in the appendix; the 222 `(excerpt)` titles are 111 and 111; the eleven
prose-titled fences are twenty-two. A population counted on the English side is half of itself,
which is what T090 asserted until it was measured.

`gaps.md` 050-3 is why HEAD problems are `(en)` only: the Vietnamese chain is compared to its
English twin and never to `relay-platform`.

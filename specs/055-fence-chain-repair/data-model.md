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

Two consequences the repair depends on:

- **A chain must open with a whole body.** An amendment with no predecessor is
  `diff … with no earlier fence to amend`, and 32 of the 110 are this.
- **The appendix cannot open a chain.** It applies after every chapter, so it can amend a path
  and never introduce one. The specification's FR-010 offers it as a fallback for missing
  introductions; that fallback does not exist.
- **`MIRROR` matches by title**, so renaming an English title without renaming its Vietnamese
  twin unpairs them.

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
with at least one. 25 files `differs at line N` and those 25 files hold 2,381 differing lines.

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
         └─────► recorded          cannot be repaired; the reason, the measurement and the
                                   cost are written down (FR-012)

**`recorded` is not a fourth kind of green.** A feature that reports "0 except for these" without
the arithmetic has written the baseline it refused to write, which is the option this feature
exists instead of. Every `recorded` item carries what it would take.

**Transitions are measured, not asserted.** The count is taken after each target (FR-003), because
a repair can raise it: one foundation fence regenerated took the chain from 111 to 203.

---

## Locale pair

An English fence and its Vietnamese twin, matched by title within the same chapter.

Measured: **30 vi problems, all 30 mirroring an en problem exactly, zero vi-only.** The pair is
the unit of edit and the English side is the unit of diagnosis. `MIRROR` must read 0 after every
repair, which is the check that the copy actually happened.

`gaps.md` 050-3 is why HEAD problems are `(en)` only: the Vietnamese chain is compared to its
English twin and never to `relay-platform`.

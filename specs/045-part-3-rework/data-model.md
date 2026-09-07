# Data model — Part 3, reorganised by subject

No database, no schema, no migration. The entities here are the book's own structures, and they are
modelled because two of them are edited by scripts and one of them is the feature's whole risk.

---

## Chapter

| | |
|---|---|
| **Identified by** | its slug. `webhooks-that-survive-the-customer` is the chapter; `3.5` is where it currently sits |
| **Carries** | an ordinal, a movement, a route per locale, prose, and a set of fences |
| **Changes here** | ordinal, route, position. **Not the slug, and not the prose** |

**The slug is the identity and the ordinal is a position.** That inversion is the feature. It is why
the redirects only rewrite the numeric segment, why the named-reference rule is expressible at all,
and why a reader who bookmarked a slug loses nothing.

## Movement

A contiguous run of chapters sharing a subject. Eight of them, listed in
[contracts/chapter-map.md](./contracts/chapter-map.md).

**Not necessarily a published heading.** A movement is the unit FR-001 is measured against — group
each chapter by subject, confirm each group occupies consecutive positions — and whether the book
prints the movement names is a presentation decision for Phase 6, not a requirement.

## Fence chain

| | |
|---|---|
| **What it is** | the sequence of code fences for one file path, replayed in chapter order **and then through `fences/post-series.md`** |
| **Invariant** | the state after the last fence — appendix included — equals the file in `relay-platform`, byte for byte |
| **Kinds** | a plain fence states the whole file at that point; a `diff` fence amends the state before it |
| **Population** | 242 fenced paths, 904 fences repository-wide; 207 paths and 623 fences in Part 3 |
| **Changing here** | **184 paths**: 183 because a comment inside them changes, 42 because their chapter order changes, overlapping |
| **Amended by the appendix** | **49 paths**, 41 of them comment-changed and **21 order-changing**, carrying 48 hunks |

**This is the feature's risk, and it is concentrated.** **289 fences sit on 42 order-changing paths**
once the milestone chapter's split is counted, and `repository.ts` alone carries 23 of them across 17
chapters.

### How a chain is re-derived

Not by re-hunking. Replaying the existing per-chapter deltas in the new order lands correctly on 3 of
39 paths — research R2. And **not by filtering the final file either**, which was this document's
first answer:

    state(c) = the final file, minus every line owned by a later cluster      FALSIFIED

Analysis pass 2 built it. It gives **52 parse errors on `repository.ts` and 59 on `session.ts`**,
because line-level ownership cuts through syntax — a method whose signature and body arrived in
different chapters leaves unbalanced braces when one of them is dropped. It also leaves ~2% of lines
with no owner, which the rule then keeps in every state including those before the line existed.

What is used instead is a **three-way merge**: cherry-pick each chapter's delta onto the new order,
resolve the 31 conflicts by hand, and check the 5 paths that merge cleanly onto a *different* file.
Measured on the eight paths that merge clean end to end: **56 intermediate states, 0 parse failures.**
A merge of two real files is a real file.

**The final state is the acceptance, not the construction.** `check:fences` compares byte-exact
against `relay-platform`, and every synthesised state is typechecked — a state that will not compile
means the order violates a real dependency.

### State transitions

    a path no chapter fences        outside the chain entirely; edits invisible to every gate
    a path fenced once              a plain fence; order-independent
    a path fenced by one movement   order-independent under this feature
    a path fenced across movements  re-derived by merge — this is the 42
    a path the appendix amends      its chapter fences target the PRE-APPENDIX state, not the
                                    platform file — 21 of the 42 order-changing paths
    a path published as (excerpt)   never compared to anything; thirteen of these

**The excerpt-only row is the one to watch.** Thirteen files are published only as `title="… (excerpt)"`
and `check:fences` skips them by name. Comment rewrites inside them are invisible to the gate, so they
need a check of their own rather than the chain's.

## Reference

A mention of a chapter, from prose, a source comment, or a record.

| Class | Count | What it becomes |
|---|---|---|
| beside a requirement id | 416 | the ordinal is deleted; the id was always the durable half |
| a plain subject reference | 923 | a name, from the 24-entry table |
| a positional claim | 90 | a rewritten sentence |

**1,429 in `relay-platform` source** — all `.ts` under `services/` and `packages/` — of which
**1,298** sit inside the **183** fenced paths. The specification recorded 985 and 166; both came from
a pattern missing a capital `C`, and only the first was corrected until analysis pass 3.
**State the pattern and the corpus with every count**, which is SC-002's rule and was broken by the
document that states it.

**After this feature a source comment names no ordinal.** Prose in the book still may: a chapter can
say "chapter 3.4" about a chapter the reader has open, because prose is republished with the book and
a comment is not. The rule applies where the reference is durable and the gate is byte-exact.

## Chapter map

The old-to-new table. **One record, three consumers** — the redirects in `next.config.ts`, the
published mapping page, and the chapter registry below. Modelled as an entity rather than a step
because the alternative is three lists that must agree and will not. **It read "two consumers" until
analysis counted them**, which is the defect this entity exists to prevent, committed by the document
describing it.

## Chapter registry

`relay-tutorial/lib/tutorial.ts`. **810 hand-maintained lines** declaring every chapter's number,
path, title, `titleVi`, reading time and what the reader produces.

| | |
|---|---|
| **Read by** | `app/sitemap.ts` and six components — the series sidebar, the chapter shell's previous and next links, the site header, the landing page, the language switcher |
| **Guarded by** | **nothing.** No script reads it, no test compares it to the filesystem |
| **State today** | 41 declared, 41 on disk, agreeing in both directions |
| **Changes here** | 24 Part 3 entries renumbered and reordered, one added for the split |

**Unguarded is not the same as broken**, and it is the harder condition to notice. A renumbering that
skipped this file would leave `check:fences` green, `check:docs` green, and every navigation link in
the book dead. FR-015 and SC-009 exist because analysis pass 1 asked what else in the tree knows a
chapter number.

## What is deliberately not modelled

- **No per-chapter word budget.** Compression is out of scope, so the 6× size variance is carried
  unchanged and is not a field on anything here.
- **No translation state.** Vietnamese pages are either placeholder or translated, and the user owns
  that transition. This feature sets them all to placeholder and does not track them afterwards.
- **No git history for the platform.** The fence chain reads the working tree and never reads git, so
  reordering chapters does not require rebuilding commits. Permission to reset the repository exists
  and is not used.

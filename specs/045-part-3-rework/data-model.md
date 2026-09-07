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
| **What it is** | the sequence of code fences for one file path, replayed in chapter order |
| **Invariant** | the state after the last fence equals the file in `relay-platform`, byte for byte |
| **Kinds** | a plain fence states the whole file at that point; a `diff` fence amends the state before it |
| **Population** | 242 fenced paths, 904 fences repository-wide; 207 paths and 623 fences in Part 3 |
| **Changing here** | **169 paths**: 166 because a comment inside them changes, 39 because their chapter order changes, 36 overlapping |

**This is the feature's risk, and it is concentrated.** 278 fences sit on the 39 order-changing paths,
and `repository.ts` alone carries 23 of them across 17 chapters.

### How a chain is re-derived

Not by re-hunking. Replaying the existing per-chapter deltas in the new order lands correctly on 3 of
39 paths — research R2. Instead each state is synthesised:

    for a path, in the new chapter order:
      state(c) = the final file, minus every line owned by a cluster later than c
      fence(c) = diff(state(c-1), state(c))

**Ownership comes from the current chain**, which attributes each final line to the chapter that
introduced it. The final file is fixed, so the chain lands on it by construction — the failure mode is
not drift but an intermediate state that does not compile.

### State transitions

    a path no chapter fences        outside the chain entirely; edits invisible to every gate
    a path fenced once              a plain fence; order-independent
    a path fenced by one movement   order-independent under this feature
    a path fenced across movements  re-derived — this is the 39
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

**1,429 in `relay-platform` source**, against the 985 the specification recorded — a narrower pattern
had missed `3.20's` without the word "chapter".

**After this feature a source comment names no ordinal.** Prose in the book still may: a chapter can
say "chapter 3.4" about a chapter the reader has open, because prose is republished with the book and
a comment is not. The rule applies where the reference is durable and the gate is byte-exact.

## Chapter map

The old-to-new table. **One record, two consumers** — the redirects in `next.config.ts` and the
published mapping page. Modelled as an entity rather than a step because the alternative is two lists
that must agree and will not.

## What is deliberately not modelled

- **No per-chapter word budget.** Compression is out of scope, so the 6× size variance is carried
  unchanged and is not a field on anything here.
- **No translation state.** Vietnamese pages are either placeholder or translated, and the user owns
  that transition. This feature sets them all to placeholder and does not track them afterwards.
- **No git history for the platform.** The fence chain reads the working tree and never reads git, so
  reordering chapters does not require rebuilding commits. Permission to reset the repository exists
  and is not used.

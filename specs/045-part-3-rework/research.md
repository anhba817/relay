# Research — Part 3, reorganised by subject

Six questions. Four were answered by running something, and **two of those four overturned the
assumption the specification was written on**.

---

## R1 — Does a cheaper chapter order exist?

**Decision: no. Choose the order on pedagogy, because every order costs roughly the same.**

Four candidate orders were replayed against the real fence chain. For each, every fenced path whose
chapter sequence changes was rebuilt as a git history, and the per-chapter deltas were cherry-picked
in the new order onto the same base:

| Order | paths moved | replay clean | conflicts | lands on a different file |
|---|---|---|---|---|
| **A** full proposal, webhooks late | 39 | 3 | **31** | 5 |
| **B** local repair only, minimum movement | 28 | 2 | **24** | 2 |
| **C** domain early, webhooks in the middle | 37 | 5 | **29** | 3 |
| **D** full proposal without splitting the milestone chapter | 44 | 4 | **34** | 6 |
| **E** today, as a control | 0 | 0 | 0 | 0 |

**The conflict rate is 79–86% whatever the order.** Option B exists precisely to be the cheap one —
it moves four chapters and nothing else — and it still conflicts on 24 of the 28 paths it touches.
There is no arrangement of Part 3 that lets the existing fences be reused.

**Alternatives considered.** Keeping the numbering and reordering navigation only was rejected in the
specification on the reader's behalf. Choosing option B to save work was rejected here: it costs 24
conflicts against A's 31 and does not fix the defect, since webhooks would still teach delivery for
events that have no producer.

**Control**: option E, the current order, produces zero moved paths. The measurement can detect
"no change", which is what makes the other four numbers mean something.

---

## R2 — Can the existing fences be reused if the hunks are regenerated?

**Decision: no. The chain has to be re-derived, not re-hunked.**

This is the assumption the specification carried and it is wrong. The specification said 39 of 207
paths change chain order, which is true, and implied that regenerating their diff hunks would be
enough. **Three of those 39 replay cleanly.**

The reason is not hunk context. It is that two chapters on opposite sides of a move both edit the
same region of the same file, so the order in which their changes land decides the result. Replaying
them in the new order produces either a merge conflict (31 paths) or a clean merge onto **a different
file** (5 paths) — and the second is worse, because it passes every mechanical check up to the final
comparison.

**289 fences sit on 42 paths** once the milestone chapter's split is counted — this read 278 on 39
until the split was decided in `contracts/chapter-map.md`. That is the unit of work this feature is
actually made of.

---

## R3 — Could the platform files be reorganised so the chain becomes mechanical?

**Decision: no, and this was the most promising idea available.**

If each cluster's code were contiguous inside each file, every chapter would append to its own region,
diffs would not overlap, and regeneration would be a script. The user's permission to reset and re-tag
`relay-platform` makes that legal.

It is not practical. Each line of four heavily-fenced files was attributed to the chapter that
introduced it, then to that chapter's cluster:

    services/api/src/db/repository.ts     5,533 lines    124 cluster runs    7 clusters
    services/gateway/src/session.ts       1,683 lines     85 cluster runs    6 clusters
    services/api/src/db/schema.ts         1,097 lines     31 cluster runs    6 clusters
    services/api/src/app.module.ts           71 lines     21 cluster runs    5 clusters

`repository.ts` would have to be reorganised from 124 interleaved runs into 7 blocks. That is a
refactor of the platform's largest file, it changes code every earlier chapter already published, and
it is not a change anybody wants for its own sake. **A book's teaching order is not a good reason to
reorganise a repository layer**, and doing it would invalidate far more fences than it saved.

`app.module.ts` is the sharpest case: 21 runs in 71 lines. A module registration list interleaves by
nature, because it lists one entry per feature in the order the features were added.

---

## R4 — Then how is the chain re-derived?

**Decision: by three-way merge of the existing per-chapter deltas, resolving the conflicts by hand.
The first answer here was attribution-and-filter, and analysis pass 2 falsified it.**

### What was tried first, and why it fails

The attribution built for R3 suggested a rule: for a path and a chapter in the new order, the state
is **the final file with every line owned by a later cluster removed**. The final file is fixed, so
the chain would land on it by construction.

**It produces files that do not parse.** Built and run against the tree:

    services/api/src/db/repository.ts   synthesised at one position   52 parse errors
    services/gateway/src/session.ts                                   59 parse errors
    services/api/src/db/schema.ts                                      4 parse errors
    services/api/src/app.module.ts                                     0 — 71 lines, a flat list

Line-level ownership cuts through syntax. A method whose signature arrived in one chapter and whose
body grew in another; an object literal assembled across three; a `try` wrapped later around an
existing block. Removing the later-owned lines leaves unbalanced braces, and only the smallest and
flattest file survives.

**Two further problems, both of which would have been silent.** About **2% of lines get no owner at
all** — 137 in `repository.ts`, 37 in `session.ts` — and the rule drops lines owned by *later*
clusters, so an unowned line is kept in **every** state, including states before it existed. And
nothing in a byte-exact comparison of the *final* file can see either fault, because the final file
is right by construction.

### What is used instead

**Cherry-pick the per-chapter deltas onto the new order and resolve the conflicts.** This is R2's
experiment turned into the mechanism rather than into a warning:

    39 order-changing paths      3 replay clean      31 conflict      5 land on a different file

The 31 conflicts are hand-resolved and the 5 silent divergences are the ones to watch, since they
pass every check until the final comparison.

**States derived this way are real states.** Measured on the eight `.ts` paths that cherry-pick clean
end to end:

    56 intermediate states produced by three-way merge      0 fail to parse

against 52 and 59 parse errors from the mechanism this replaces. A merge of two real files is a real
file; a filtered subset of one is not.

**And the typecheck stays as the acceptance**, for the reason it was added: a state that will not
compile means the order violates a real dependency, and that is a finding about the order rather than
a bug in the tool.

**Alternatives considered.** Restating each moved file as a whole-file fence removes the pre-image
problem and was rejected — a whole-file fence of `repository.ts` is 5,533 lines in a published
chapter. Hand-authoring all 289 fences from nothing was rejected as the default; hand-resolving 31
merge conflicts is the same work bounded to where the conflict actually is.

### The appendix is part of the chain, and the first tooling forgot it

`fences/post-series.md` applies **after the last chapter** and amends **49** fenced paths. The
snapshot tool built during analysis stopped at the last chapter, and the omission showed up as **70
reference-bearing lines present in the platform file and in no snapshot at all** — concentrated in
`eslint.config.mjs` (6 appendix hunks) and `vitest.coverage.config.mts` (10).

    49  paths the appendix amends
    41  of those also have comment rewrites
    21  of those also change chain order, carrying 48 hunks

**For those 21 the target of a chapter fence is not the platform file.** It is the state the appendix
then amends. A merge that targets the platform file overshoots by exactly the appendix's hunks, and
`check:fences` would report the failure at the wrong place.

**And the 48 existing hunks were generated against today's end state.** R2 measured 5 paths where
reordering lands on a different file; where that intersects these 21, the appendix's own pre-images
stop matching. They are re-verified and regenerated, not assumed.

**What this does not solve.** A merge produces a state, not a narrative. A chapter whose prose walks
through a diff will need that prose checked against the regenerated diff, and `check:fences` cannot
see it.

## R5 — What does rewriting 1,429 source references actually cost?

**Decision: three rewrites, and half of them are deletions.**

Every chapter reference in `relay-platform` source was classified by **the rewrite it needs**, which
is not the same question as what it looks like:

| Rewrite | Count | Share | What it is |
|---|---|---|---|
| **delete the tag** | ~757 | 53% | a parenthetical provenance note — `(chapter 3.2)`, `(chapter 3.17, T059)` — or a sentence-initial marker, `// Chapter 3.8: nor the notification relay`. The sentence stands without it and **no name is needed** |
| **substitute a name** | ~605 | 42% | possessives and subjects of verbs — `chapter 3.20's finding`, `chapter 3.18 measured that` — where a noun phrase from the 24-entry table fits |
| **read and rewrite** | ~70 | 5% | section rules `// ── chapter 3.18: two instances ──`, and temporal claims where "since the rate-limit chapter" reads worse than restating the fact |

**THIS TABLE READ 416 / 923 / 90 AND THE MIDDLE COLUMN WAS HALF WRONG.** The first classification
sorted by *appearance* — beside a requirement id, plain subject reference, positional claim — and put
every parenthetical tag without an id into "substitute". Nearly half of them need no table entry at
all. `subjects.json` serves ~605 references, not 923.

### How the counts were arrived at, and how far to trust them

**Three classifiers gave three answers.** A keyword classifier put 90 references in the expensive
class. A structural re-classification put **407** there — a 4.5× disagreement — because it counted
only possessives as substitutable and dumped every subject-of-a-verb into "read".

**Reading twelve actual sentences resolved it at about 70**, close to the first classifier's 90: nine
of the twelve were plainly substitutable, one was a mis-classified parenthetical, one a section rule,
one a temporal claim. **The first estimate was right and its reasoning was not**, which is worth more
than the number.

**Twelve is a thin sample and the ~70 carries that.** The delete and substitute counts are structural
and firmer; the expensive class is the one to re-measure when the work starts, because it is the one
that decides how long this takes.

## R6 — What shape must a Vietnamese placeholder take?

**Decision: the page stays, the prose is replaced, the fences are copied byte-identical.**

`check-fence-chain.mjs` iterates the Vietnamese chapters that **exist**, and for each one compares the
fence list and then every fence body against the English chapter of the same key. Two consequences:

- A Vietnamese page that drops its fences fails `MIRROR` with *"fence list differs"*.
- A Vietnamese page that is **deleted** is skipped entirely — which makes deletion the cheapest option
  and the wrong one, since it removes 24 published translated chapters from the site.

So a placeholder page keeps its imports, its `metadata`, its `alternates`, its figures and every code
fence unchanged, and replaces only the prose between them. The fences are English; that is what the
mirror requires and what a reader following code needs anyway.

**Alternatives considered.** Machine-translating the prose was rejected — the user has said they will
supply translations, and a machine translation is harder to review than an honest gap. Leaving the
current Vietnamese prose in place under a reordered chapter was rejected: the prose refers to chapter
numbers and neighbouring chapters, so it would be wrong in a way a reader cannot detect.

---

## R7 — What happens to the URLs?

**Decision: the mapping is published, and redirects are added.**

Routes come from the directory names, `part-3/chapter-07/commit-and-publish-are-two-instants`, so
renumbering renames 24 English and 24 Vietnamese directories and changes 48 canonical URLs. Each page
also carries `alternates.canonical` and a `languages` pair naming its own path, so those move with it.

`next.config.ts` configures no redirects today. Every old chapter URL must resolve, because the series
is published and linked. The mapping that FR-014 requires a reader to find is the same table the
redirects are generated from — one source, two consumers, rather than a hand-maintained pair. **A
hand-maintained table cannot be checked** is this project's own finding from the port bands.

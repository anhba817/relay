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

**278 fences sit on those 39 paths**, 237 of them diffs, 228 of them inside Part 3. That is the unit
of work this feature is actually made of.

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

**Decision: synthesise each chapter's state from the final file by cluster attribution, and typecheck
every synthesised state.**

The attribution built for R3 is the mechanism. For a path and a chapter in the new order, the state is
**the final file with every line owned by a later cluster removed**. The final file is fixed, so the
chain lands on it by construction; the fences are then generated between consecutive synthesised
states.

**And the synthesis doubles as a check on the order itself.** If a synthesised state does not
typecheck — a domain method calling a helper the webhook cluster introduces — then the proposed order
violates a real dependency and the order is wrong, not the tool. That failure is loud, it names the
file, and it arrives before any prose is moved.

**Alternatives considered.** Restating each moved file as a whole-file fence removes the pre-image
problem entirely and was rejected: a whole-file fence of `repository.ts` is 5,533 lines in a published
chapter. Hand-authoring all 278 fences was rejected as the default, though it remains the fallback for
any path where synthesis fails to typecheck.

**What this does not solve.** Synthesis produces a state, not a narrative. A chapter whose prose walks
through a diff will need that prose checked against the regenerated diff. That is reading work, and
`check:fences` cannot see it.

---

## R5 — What does rewriting 1,429 source references actually cost?

**Decision: three classes, and only 6% of them need a person to think.**

Every chapter reference in `relay-platform` source was classified by the 70 characters either side:

| Class | Count | Share | Rewrite |
|---|---|---|---|
| sits beside a requirement id — `(chapter 3.21, FR-RTM-08)` | 416 | 29% | **delete the ordinal**, keep the id, which was always the durable half |
| plain subject reference — `chapter 3.20's finding` | 923 | 64% | substitute from a 24-entry table of chapter subjects |
| positional claim — `a describe-level teardown cost chapter 3.20` | 90 | 6% | rewrite the sentence by hand |

The count is 1,429 rather than the specification's 985 because this pass used a wider pattern —
`3.20's` without the word "chapter" was not matched before. **The number in the specification was
low, and the correction is in the direction the plan expects.**

**The 29% class is the interesting one.** Those comments already carry the reference that does not
age. Deleting the chapter number from them loses nothing at all.

---

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

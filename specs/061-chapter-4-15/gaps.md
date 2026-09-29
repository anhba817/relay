# gaps.md — feature 061, chapter 4.15 "What a thumbnail costs"

Numbered. Carried items are **re-measured**, not copied: 043 found four of twenty-three
carried entries wrong when re-measured and three closed with nobody working on them.

---

## New this feature

**061-1 — `recordMediaVerdict` had no transaction, and four artifacts said it did.**
The plan, the tasks and two task lines all said "insert the rendition row in the same
transaction as the verdict". The function was a bare `UPDATE … WHERE state = 'pending'
RETURNING` with a fallback `SELECT`, and **its own comment argued for that shape**. Found by
an analysis pass opening the function rather than reading the plan. **CLOSED** — wrapped, and
the red probe was run first: without it the test reports `expected 'ready' to be 'pending'`,
which is a parent committed with no rendition and no reason.

**061-2 — the worker's store client was read-only at the type level.**
`SignOptions.method: "GET" | "HEAD"`. Not an omission — an accurate statement about a service
that read bytes and produced nothing. The compiler refused `putObject` before a reviewer
could. **CLOSED**, widened with the reason in the type's own comment.

**061-3 — a JPEG with ordinary EXIF defeats the 64 KiB probe.**
One maximal `APP1` segment is 65,535 bytes and `PROBE_BYTES` is 65,536, so `dimensionsOf`
returns null for a 72,215-byte camera file whose bytes decode fine as 1200×900. **CLOSED** by
making the fetch gate three-state; a two-state gate would have denied renditions to exactly
the files most likely to want one. **And it explains a lane figure**: `width` is null for
5,942 of 5,996 images, which is not only unprobed objects.

**061-4 — `check:refs` is not a script.** T071 named it as a gate. `Command "check:refs" not
found`. The five that exist are `check:docs`, `check:errors`, `check:fences`, `check:figures`,
`check:srs`. **OPEN as a habit, not a defect**: read the gate list off `package.json`, which
is 055-3's entry and which writing that task ignored.

**061-5 — `PendingObject` is a hand-written second copy of a wire schema.**
`services/media-worker/src/verify.ts` declares its own interface rather than using
`internalMediaPendingItemSchema`'s inferred type, so adding `environment_id` cost two edits.
**OPEN by decision** — it predates the shape being on the wire and is narrower on purpose.
Worth folding in the next time either changes for another reason.

**061-6 — the fence bill is per file, not per hunk, and the exposure count is not the bill.**
`repository.ts` is titled in 52 files (28 en, 23 vi, 1 appendix) and cost **9 hunks in one
appendix entry**, because the checker reports the first failure per file. The useful number
before starting work is the per-file exposure; the useful number after is the hunk count.
**CLOSED as a method**: T007a moved the count to phase 1 and it predicted the bill exactly,
including that no media-worker file would appear.

**061-7 — the lane cannot exercise this chapter at scale.** 4 of 5,996 images are above the
bound; 54 renditions among 6,646 rows. Every ratio published came from six images of
convenience or from synthetic noise. **OPEN and unfixable here** — it is 4.12's sentence, and
the chapter says so in its body rather than only in this file.

**061-8 — an optional field is invisible in both directions.** It broke zero of the twelve
whole-array assertions that 4.14's required field would have broken, and the compiler named
none of its construction sites. Convenient, and it means neither instrument gives warning.
**OPEN by decision** — `contracts/renditions.md` records the client-side strict-parse
consequence as 060-10's twin.

---

## Carried, re-measured

**060-13 — `docker compose --profile services stop` with no service list stops the stores.**
**RE-MEASURED AND SHARPENED.** Naming the services is right, and `ingester` is not one of
them — it has no Dockerfile (4.9's finding), and including it makes the whole command fail
rather than partly apply, so nothing stops. The four that exist: `api`, `gateway`,
`dispatcher`, `media-worker`.

**059-20 — a per-file branch pin is a claim about the machine.** Not re-measured; no pin in
this chapter's files moved. Still open.

**055-3 — `check:errors` is a script no workflow runs.** Re-checked: still five `check:*`
scripts and still no CI job for that one. Unchanged, and 061-4 is its neighbour.

**050-8 — two test files spawning an ingester is not a deployment.** Unchanged.

**059-11 — `media_events` deferred to the erasure chapter.** Unchanged.

**043 — the wall-clock minute bucket.** Unchanged.

---

## The lane's own state, carried forward

**Three integration failures existed at this feature's baseline and none was this chapter's.**
All three are transient, which took four runs to establish and contradicted my first reading:

| suite | baseline | later runs | reading |
|---|---|---|---|
| `api/media-updated.itest.ts` | red | passes alone 9/9, red in 3 of 7 full runs | a neighbour effect |
| `api/notifications.itest.ts` | red, `Hook timed out in 10000ms` | passed 5 of 7 | lane accumulation — `webhook_disable_notifications` held **2,701** rows and the drain does one SMTP round trip each; **CI never sees it, because a fresh database has no pile** |
| `gateway/typing.itest.ts` | red | red in 2 of 7 | a flake. **I called it deterministic on one isolated run**, which is exactly what `CLAUDE.md` warns about |

**The lesson is the method, not the three.** For this whole feature the gate was a **failure
set compared against that list**, never a colour — and it earned its keep on the first
comparison, when phase 2's run had a set of two: one carried and one new, which was mine.
A colour could not have said that; the lane was red before and red after.

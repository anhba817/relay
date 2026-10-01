# Gaps — feature 063, chapter 4.17

Numbered as they are found, not as they are fixed. An entry here is something measured and
left open on purpose, with the cost of closing it attached so nobody has to re-derive it.

## 063-1 — `integrate.itest.ts` has four poll-to-deadline helpers and should have one

**Measured.** `waitFor` is defined **three times** in
`relay-platform/packages/outsider/src/integrate.itest.ts` — lines 476, 348 and 423 before this
chapter, one per test, each a 10-second deadline over a frame array — and chapter 4.17 adds a
fourth waiter, `waitForAttachmentState`, over a different thing (an attachment's state read
back through history). The three frame waiters differ only in the payload type they name.

**Why it is left open.** Consolidating is the better code and this is the wrong chapter to pay
for it. The file is titled in **five fences — two whole bodies and six diffs** — across
`part-3/chapter-26` in both locales, `part-4/chapter-08`, `part-4/chapter-09` and the appendix.
**A titled fence is a whole-body claim** (051-6), so lifting a helper touches four regions of a
file whose every published copy would then need regenerating: two whole bodies and six
re-anchored hunks, in a milestone chapter whose own line says it adds no product surface.

**How to apply it.** The next chapter that edits this file for its own reasons should lift all
four at once, and pay the fence bill once rather than twice. The bill above is the number to
budget with.

**AND THE ONE HELPER THIS CHAPTER DID ADD IS AT DESCRIBE SCOPE, WHICH REFINES T010a's
DECISION.** That decision — *"a local helper, and no consolidation"* — was taken about the three
frame waiters, each of which has exactly one caller. `waitForAttachmentState` has **three**, in
three different `it(...)` blocks: the existing media test (whose false comment this chapter
corrects), the journey, and the rejection. A local copy would therefore have been three copies,
which is the thing this entry exists to stop. **One caller is a judgement; three is the answer.**

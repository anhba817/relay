# T063 — traceability, built by reading

**Built by reading each requirement against the tree, not by grep.** 4.11's mechanical coverage
map reported 14 of 51 requirements uncited in `tasks.md` and **all fourteen were covered in
substance** — fourteen alarms, fourteen false. A grep finds the identifier; only a reader finds
the obligation.

Every "where" below is a place that exists now and was checked.

## Functional requirements

| id | the obligation | where it is discharged | verdict |
|---|---|---|---|
| FR-001 | one suite carries an image from slot to fetched bytes | `integrate.itest.ts`, *"carries one image from slot to delivered bytes…"* — ten steps, one `it` | **MET** |
| FR-002 | each added assertion names the chapter it depends on | 40 assertions, **0 unnamed**, across fourteen chapters (T041) | **MET** |
| FR-003 | the suite fails when the worker is not working, and not by timeout alone | `stop media-worker` → **18 of 21**, all three failures naming the worker and the command to run. (T024 measured 18 of 20 before the rejection journey existed; re-measured at the close.) | **MET** |
| FR-004 | a reader obtains the bytes, and they are the bytes | step 9: `toEqual(image)` over the whole array, not a length | **MET** |
| FR-004a | the image exceeds 320 px on its long edge | 800 × 600, asserted at 480,813 bytes before the slot is taken | **MET** |
| FR-005 | a rejected attachment reaches a recipient as a state on a surviving message | the rejection journey; **and the premise was checked first** — history does not filter it (T030) | **MET** |
| FR-006 | a link to a rejected object is refused indistinguishably | byte-identical bodies apart from `request_id`, **with a control** so two empty objects cannot satisfy it | **MET** |
| FR-006a | a recipient holding `pending` receives the change | `media.updated` asserted whole on **both** arms — `ready` and `rejected` | **MET** |
| FR-007 | an undischargeable clause of FR-MED-09 is recorded with its reason | SRS 1.24; `clauses.md` records it **UNREACHABLE**, not unmet-by-decision, because no decision would change it | **MET** |
| FR-008 | the chapter states which half the lane checks and which is recorded once | *"The two halves of the milestone"* | **MET** |
| FR-009 | the figure separates the timer from the work | the sweep's period measured from the **api's** access log; the work published as a residual ≤ 433 ms | **MET** |
| FR-010 | the suite asserts on a condition, never on elapsed time | `waitForAttachmentState` polls to a deadline; the chapter says in the test why | **MET** |
| FR-011 | a false stated reason is corrected and the correction asserted | T013/T014: the comment replaced by the measurement, and `waitForAttachmentState` checks it | **MET** |
| FR-012 | no product surface | **checked rather than trusted** (T066a): two files changed in `relay-platform`, both `.itest.ts` | **HELD** |
| FR-013 | the chapter states what the lane cannot demonstrate | *"What the milestone could not demonstrate"* — four items, each with its reason | **MET** |

## Success criteria

| id | measured | verdict |
|---|---|---|
| SC-001 | 21 of 21, the journey at 5.9–6.1 s, bytes byte-identical | **MET** |
| SC-002 | **18 of 21** with the worker stopped, each failure at ~25 s; the message names the worker, not the delivery route | **MET** |
| SC-003 | `rejected` in history; the 404 matches an id nobody has | **MET** |
| SC-003a | both arms asserted whole: `{media_id, channel, state}` | **MET** |
| SC-004 | 40 assertions, 0 without a chapter — **and the rule the count uses is written down**, because the number depends on it | **MET** |
| SC-005 | min 1,097 · p50 3,398 · max 36,164 over n = 25, decomposed, with the 5,000 ms interval named as the dominant term | **MET** |
| SC-006 | `clauses.md`: 20 clause-parts, **11 DEMONSTRATED**, 5 MET, 1 UNREACHABLE, 1 unbuilt elsewhere, 1 held, 1 not exercised | **MET** |
| SC-007 | the expectation is unchanged and its explanation is now true **and checked** | **MET** |
| SC-008 | T069 | *pending the push* |
| SC-009 | `check:fences` 0 across 60 chapters; `pnpm build` exit 0 | **MET** |
| SC-010 | 2,889 prose words, inside 2,000–4,000 | **MET** |

## What reading found that a grep would not

- **FR-005's obligation is a premise, not an assertion.** The requirement says a rejected
  attachment *reaches* a recipient. A suite can assert that only if history returns the message
  at all, which nothing had checked — so the work was to ask first and be prepared to report a
  different chapter.
- **FR-002 and FR-012 pull against each other.** Naming a chapter in an assertion message is a
  product-adjacent edit to a file seven chapters publish; the fence bill is what makes it a
  decision rather than a courtesy. It came to six hunks, in the appendix.
- **FR-007's verdict is UNREACHABLE and not "unmet by decision"**, and the distinction is the
  clause's. Nothing this feature could have decided differently would discharge *"renders as"*;
  4.11's FR-MED-07 and 4.16's dashboard half are the two precedents and only one of them is
  this shape.

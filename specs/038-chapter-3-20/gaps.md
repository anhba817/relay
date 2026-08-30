# Open things — chapter 3.20

*One item per gap, each with an owner. Written when found, not at close-out.*

**Every reference carries its chapter**, because the numbers collide: chapter 3.17's
item 1 is an unidentified lane flake, chapter 3.18's item 1 is the idempotency-key
mismatch, and chapter 3.19's item 1 is the missing presence snapshot.

**Seventeen items are carried from chapter 3.19 with their status re-checked at the
start of this feature rather than copied at the end of it.** Chapter 3.18 carried none
of its predecessors' forward and chapter 3.17 carried seven of nine; the cost of not
doing it is that CLAUDE.md's header names one predecessor, so an item nobody carries
becomes unreachable by the path the header describes.

---

## Carried from chapter 3.19 — status at the start of this feature

| # (3.19) | Item | Status here | Owner |
|---|---|---|---|
| 1 | Presence has no snapshot, so a roster starts empty | **open**, untouched | unassigned |
| 2 | A user who joins a channel while connected is invisible there | **this chapter closes it** — US3 and FR-022 | chapter 3.20 |
| 3 | A test whose title claimed an arm it did not touch | **open as a class**; the close-out re-reads every new test title against its assertion | unassigned |
| 4 | The refresh re-election restores the key and publishes nothing | **open**, untouched — presence's `held` still carries no channel set | unassigned |
| 5 | Nine translated chapters absent from the sitemap | **open**; the chapter phase sets `translatedIn` for 3.20 only | unassigned |
| 6 | `conn:{env}:{user}` specified as a shape that cannot work | **open, and cited** — FR-019 names it as why FR-RTM-09 stays unbuilt | whoever builds the connection cap |
| 7 | Two fenced files instruct a Redis port that is not listening | **open**, untouched | unassigned |
| 8 | The fate of chapter 3.19's two checkers | **answered here**: `check-refs.py` is carried forward and reset per feature, which phase 1 records; `check-prose.py` is rewritten per chapter because its claim list is per-feature | chapter 3.20 |
| 9 | The lane is not idempotent from cold JetStream state | **open**, and this feature will meet it — `pnpm coverage` runs every suite in one process, where the file order differs from turbo's package order | unassigned |
| 10 | A fourth file outside the fence chain (`session.itest.ts`) | **open, and this chapter edits it** — the US1 phase wires `membership` into its delivery describe, so the file gains code no chapter fences | unassigned |
| 11 | Three files permanently outside the chain | **open**, untouched | unassigned |
| 12 | A twenty-six-run battery failed once, mechanism unidentified | **open**; not reproduced by this feature's runs so far | whoever next touches `quota-relay.ts` |
| 13 | Two comments claim a missing ioredis listener kills the process | **open**; this chapter's three new listeners are justified by NFR-OBS-01 instead, as chapter 3.19's were | unassigned |
| 14 | The two entrances accept different idempotency keys | **open**, untouched — membership carries no idempotency key | unassigned |
| 15 | A rate-limit header assertion compares two whole seconds with `>` | **open**, untouched | unassigned |
| 16 | Two published counts disagree; a spec claimed a frame did not exist | **open** as a record defect in chapter 3.18's files | unassigned |
| 17 | Six of the gateway's eight integration files each spawn their own api | **this chapter makes it worse** — the fabric phase adds the seventh, and says so | unassigned |

**Four of the seventeen are this chapter's business**: it closes 2, answers 8, worsens
17, and edits the file behind 10.

---

## New in this chapter

## 1. The word `memberships` already means something else — FOUND IN PHASE 1

`services/api/src/db/schema.ts:76` and `services/api/src/db/catalogue.ts:57` carry a
table called **`memberships`**, described there as *"joins humans to organisations,
above the environment level"* — chapter 3.1's platform-side table, above the tenant
boundary. The route this chapter revives, `GET /internal/memberships`, returns a
**channel** membership list for one end user, which is a different concept one
boundary down.

Neither is wrong and both are correctly named for their own layer. They will read as
the same word in any grep, which is how the next person to search for "memberships"
loses ten minutes.

**Owner:** this chapter, partially. The module and its tests say `channel_ids` where
they can, as `internalMembershipsResponseSchema` already does. Renaming either table
or route is a public-surface change and belongs to nobody yet.

---

*More items land here as the phases run. An item written at close-out is an item
somebody reconstructed.*

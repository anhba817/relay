# Traceability — feature 058, chapter 4.12

**Built by reading each row, not by grep.** 4.11's mechanical coverage map reported 14 of 51
requirements uncited in `tasks.md` and all 14 were covered in substance — fourteen alarms,
fourteen false. A literal sweep cannot build this table and neither can memory.

23 ids: 12 functional requirements, 10 success criteria, plus FR-024 carried from 4.11.

---

## Functional requirements

| id | where it is met | evidence |
|---|---|---|
| FR-001 | `media.controller.ts` `@Get(":mediaId")` → `media.service.ts` `deliver` → `repository.ts` `readableMediaObjectKey` | `delivery.itest.ts` *"hands a member a URL whose bytes are the ones uploaded"* — 200, two fields, and the fetched body byte-identical to what was PUT |
| FR-002 | `DELIVERY_SECONDS = 3600` in `media.service.ts` | `delivery.itest.ts` *"signs for one hour…"* asserts `X-Amz-Expires=3600` off the returned URL, not off the constant |
| FR-003 | the store, not the platform | *"refuses a delivery URL whose expiry has passed, from the store's own clock"* — `presign` with `expiresIn: 1` and `now` 60 s in the past, 403 `Request has expired`. Asserting our own arithmetic produced an earlier timestamp would prove nothing about the store |
| FR-004 | `channelVisibleTo` inside `readableMediaObjectKey`'s disjunction | *"refuses an object referenced only in a private channel the caller is not in"* — 404. Run red at T033 by deleting the `channelVisibleTo` call: 3 of 16 turn, this one among them |
| FR-005 | the object read's `environment_id` predicate, plus the malformed-id guard in the controller | *"refuses an object of another environment"*, *"refuses a media_id no object has"*, *"refuses a malformed media_id with 400, naming the parameter"*. The widened half of FR-005 (a malformed id is a 400, not a 500) is T016a's class, measured with a control |
| FR-006 | `channelVisibleTo(channelId, undefined)` — the clause's *"or API key"* arm, already built | *"hands an APPLICATION credential a URL whatever the memberships are"*, sent into a private channel the credential is not a member of |
| FR-007 | `channelsReferencingMedia` returns every distinct channel; the caller loop is a disjunction | *"authorises through ANY referencing channel, not the first one found"*. Run red at T037 by truncating the lookup to one channel: exactly one test turns, with `expected 404 to be 200` |
| FR-008 | `0017_media_reference_index.sql`, declared in `schema.ts` | `baseline.txt` T005 and T013 publish before and after with **buffers**, for a hit and both kinds of miss, at two tenant sizes. **The result contradicts the requirement's premise** and the chapter publishes that: the index does not help the joined query, which is why the query is two |
| FR-009 | `page.mdx`, the opening section | names `presign.itest.ts:53` and its title, and says the chapter did not build that half |
| FR-010 | `page.mdx` TRAP *"What the URL cannot promise"*; `gaps.md` 058-1 | the window is named — 3,600 seconds — and the two rejected remedies are recorded with what each costs |
| FR-011 | `page.mdx` *"What it costs the tenant"*; `gaps.md` 058-2; `contracts/media-delivery.md` | `operationsFor` quoted, the fifty-image gallery counted, the batch alternative rejected in writing with its oracle |
| FR-012 | `gaps.md` 057-1, re-measured | **narrowed, not closed.** `grep -rn media_id … \| grep -iE 'count\|refer'` now finds two hits and both are this chapter's migration comment. The sweep FR-MED-10 needs asks the opposite question — which objects have NO reference — and a containment index does not answer absence |
| FR-024 *(4.11's)* | `repository.ts` nulls `attachments` on delete; this chapter asserts the consequence | *"stops delivering once the referencing message is deleted"* — 200, DELETE, 404. Nothing else in the platform connects those two facts |

## Success criteria

| id | met | evidence |
|---|---|---|
| SC-001 | yes | bytes fetched through the returned URL are byte-identical to the bytes PUT through the upload slot, in one test |
| SC-002 | yes, and wider than asked | **four** conditions compared as whole bodies with `request_id` removed, not three compared by code. The fourth — an object nothing references — is the case the specification assumed the other way |
| SC-003 | yes | the store's own 403 `Request has expired`, and separately its 403 `SignatureDoesNotMatch` for a tamper whose mutation is asserted non-null (4.10's 6.23% no-op) |
| SC-004 | yes | `EXPLAIN (ANALYZE, BUFFERS)` before and after, bound parameters, hit and both misses, on the lane's busiest tenant and on a nine-message one. The two sizes are what showed the joined query's cost is the tenant's row count |
| SC-005 | yes | *"authorises through ANY referencing channel"* — a member of either gets 200, a member of neither 404 — with T037's red probe behind it |
| SC-006 | yes | `check:fences` **0**, stated absolute. 290 fenced files across 54 chapters at the open; the close is in `baseline.txt` |
| SC-007 | yes | **2,944** words outside code fences, **3** TRAP boxes |
| SC-008 | — | measured after the push (T080) |
| SC-009 | yes | **29** across 11 `package.json` at the open and 29 at the close, counted by a file rather than a shell one-liner |
| SC-010 | yes | `integrate.itest.ts` fetches a media object's bytes from outside the container, against the composed api |

---

## What no row above can claim

**That the chapter is understandable.** Every instrument here compares bytes, counts words or
reads a status code. `check-chapter`'s own last line says it: *bytes only — it cannot say whether
the PROSE describes the diff.*

**That the tenancy predicates are exercised.** SC-002 is green and T041 showed that deleting
either of this chapter's two environment scopes leaves all 16 delivery tests and all 60 gauntlet
tests green. The criterion is met by a third predicate, and a table of green rows cannot say so —
`gaps.md` 058-4 does.

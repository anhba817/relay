# T045 — the clauses this chapter touched, counted

Every row read in `docs/04-srs.md` at revision 1.24 and decided by name. **DEMONSTRATED**
means the journey exercises it end to end against the deployed worker, from outside the
platform, and would go red if it stopped being true — it is a stronger verdict than MET,
which this chapter mostly inherits rather than earns. "Unmet by decision" means the
platform could build it and this chapter chose not to; **UNREACHABLE** means no amount of
building inside this chapter's scope discharges it.

| clause | the part | verdict | where |
|---|---|---|---|
| FR-MED-01 | a slot reserves against the quota before any byte moves | **DEMONSTRATED** | journey step 3, `POST /v1/media` 201 with `state: "pending"` |
| FR-MED-02 | per-kind size caps, by declaration | **MET at 4.10** | not exercised: this chapter's fixture is honest about its size on purpose |
| FR-MED-03 | the bytes must not contradict the declaration | **DEMONSTRATED** | the rejection journey: a 43-byte GIF89a declared `image/png`, refused by the worker |
| FR-MED-04 | every uploaded object is scanned before it is readable | **DEMONSTRATED (indirectly)** | nothing reaches `ready` without the scan; a worker whose scanner is a closed port decides nothing (T038) |
| FR-MED-05 | derived objects share the parent's lifecycle | **DEMONSTRATED** | journey step 10: the rendition is fetched by a caller that never saw its id until history gave it one |
| FR-MED-06 | a message may attach a `pending` object of its environment | **DEMONSTRATED** | journey step 5: the send precedes the verdict and is accepted |
| FR-MED-07 | delivery carries the state; a `media.updated` event announces the change | **DEMONSTRATED, both arms** | `ready` in the journey, `rejected` in its twin — **the first observation of either from outside the platform** |
| FR-MED-08 | signed URLs only, to callers authorised to read a referencing message | **DEMONSTRATED** | journey step 9, and the refusal for a rejected object is byte-identical to one for an id nobody has |
| FR-MED-09 | a rejected attachment reaches history as an explicit state | **DEMONSTRATED** | checked as a premise first: history does not filter the message |
| FR-MED-09 | *"renders as"* a rejection marker | **UNREACHABLE** | there is no client in this repository; FR-MED-14's reference client is P4 and unbuilt |
| FR-MED-10 | unreferenced objects reaped after 24 hours | **UNBUILT, owned elsewhere** | `docs/12` row 22, movement VII. Its absence is measurable here: 356 pending rows inside the sweep's window |
| FR-MED-12 | stored bytes metered per tenant per day | **MET at 4.16** | unchanged; the journey's uploads are charged by it |
| FR-009 | degrade rather than lie when a dependency is absent | **DEMONSTRATED** | T037 and T038: a stopped worker and an unreachable scanner both produce no verdict and no wrong answer |
| FR-MSG-09 | a deleted message keeps its row and loses its text | **DEMONSTRATED** | the three-case comparison, which is FR-MED-09's own reason |
| NFR-USE-03 | the quickstart is runnable | **MET** | run, and the corrections recorded in `baseline.txt` |
| CON-I | tenant isolation | **MET** | nothing added reads across a tenant; the journey holds one credential |
| CON-IV | one writer per fact | **MET** | the verdict is still the worker's compare-and-set; nothing here writes a state |
| CON-VI | test-verified | **DEMONSTRATED** | the suite is the chapter; SC-002's red is measured, not asserted |
| CON-VII | boring by design | **MET** | no new dependency, no new service, no new container, no new route |
| FR-012 (this feature) | adds no mechanism | **HELD** | two open gaps left open for exactly this reason (063-2, 063-3) |

**20 clause-parts decided.** DEMONSTRATED 11 · MET 5 (4 inherited, 1 earned) · UNREACHABLE 1
· UNBUILT and owned elsewhere 1 · HELD 1 · not exercised 1.

**The number that matters for a milestone is the first one.** Eleven clause-parts are now
checked end to end against the software a deployment runs, where before this chapter the
count was **zero** — every one of them was verified by a suite that stood in for at least
one of the steps beside it.

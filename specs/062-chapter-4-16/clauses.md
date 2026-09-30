# T059 — the clauses this chapter touched, counted

Every row read in `docs/04-srs.md` at revision 1.23 and decided by name. "Unmet by
decision" means the platform could build it and this chapter chose not to, with the reason
recorded; "unreachable" means no amount of building inside this chapter's scope discharges it.

| clause | the part | verdict | where |
|---|---|---|---|
| FR-MED-12 | metered per tenant per day | **MET** | media_events + mv_billing_storage, read by storedBytes |
| FR-MED-12 | count uploads by kind | **MET** | uploads_by_kind, read by uploadsByKind; sumMapIf |
| FR-MED-12 | enforced as FR-RTL-05's storage quota | **MET at 4.10** | reserveMediaSlot sums declared_bytes; unchanged here |
| FR-MED-12 | visible in the dashboard (FR-DSH-04/05) | **UNREACHABLE** | no dashboard exists; both cited clauses unbuilt, verified by demonstration |
| DR-17 | a daily rollup summing media_events deltas | **MET** | 0016/0017/0018 |
| DR-17 | reconciled against an inventory listing | **MET** | reconcileStorage + scripts/reconcile-storage.mjs |
| DR-17 | weekly | **UNMET by decision** | ADR-28: no scheduler of any kind; 4.9 recorded the same for FR-ANL-06's daily |
| DR-17 | the media analogue of FR-ANL-06 | **PARTLY** | the comparison exists; its alerting is an exit code, as FR-ANL-06's is |
| DR-09 | daily aggregates for 25 months | **MET at 4.6** | and now NAMED as FR-MED-12's horizon, which no clause had said |
| FR-MED-01 | a slot reserves against the quota | **MET at 4.10** | cited: it is why DR-17's parenthetical was wrong |
| FR-ANL-04 | queryable within 60 s, normal conditions | **MET** | measured; an outage is not normal conditions (050) |
| CON-VII | boring by design | **MET** | no new dependency, no new service, no new container |
| CON-III | two data paths | **ENGAGED** | a fourth item against the unapplied amendment: three stores in one function |
| CON-I | tenant isolation | **MET** | eleven arms probed by deletion; nine red, one deleted, one now tested |
| CON-VI | test-verified, 100% branches on isolation | **MET** | coverage REAL EXIT 0, zero threshold errors, no pin lowered |

**15 clause-parts decided.** ENGAGED 1 · MET 8 · MET at 4.10 2 · MET at 4.6 1 · PARTLY 1 · UNMET by decision 1 · UNREACHABLE 1

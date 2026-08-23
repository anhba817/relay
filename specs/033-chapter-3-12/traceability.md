# Traceability — chapter 3.12 against the governing documents

The constitution's workflow section asks that every requirement name the clause it
implements. Analysis pass five found that **8 of this chapter's 48 requirements
did**, and that four SRS clauses were being touched without being claimed at all.

This file is that map, **generated rather than grown**. The alternative — editing
citations into 48 bullets — is what chapter 3.11's traceability pass attempted with
a regex, and it broke 36 files. A map in one file can be wrong in one place.

Two directions, because only one of them catches the omission pass five found:

- **§1** every requirement this chapter makes → the clause it implements
- **§2** every governing clause this chapter touches → the requirement covering it,
  including the four that were touched and unclaimed

---

## §1 — requirement → governing clause

### The suite itself

| Requirement | Implements |
|---|---|
| FR-001 | NFR-SEC-09; constitution I ("an automated test suite verifying cross-tenant access is impossible … on every build") |
| FR-002 | NFR-SEC-09; NFR-MNT-02 (a check that maintains itself rather than a list that rots) |
| FR-003 | constitution I; feature 030's list-with-reasons doctrine |
| FR-004 | FR-TEN-05 (a foreign identifier is indistinguishable from an absent one) |
| FR-005 | FR-TEN-05; DR-02 (per-tenant uniqueness is a storage property, so a write attack is checked at storage) |
| FR-006 | FR-TEN-05; FR-MSG-09 (history's own shape is what "empty result" means here) |
| FR-007 | FR-TEN-05; EIR-WS-03, EIR-WS-06 (the socket's session and its refusals) |
| FR-008 | FR-TEN-05; EIR-API-02 (the internal service contract) |
| FR-009 | NFR-SEC-06 (a credential's blast radius is stated, not implied) |
| FR-044 | FR-044 is this chapter's own; it narrows **FR-AUT-10** (which credential classes a route accepts) to which SERVICE |
| FR-046 | EIR-API-04 (the error envelope's `code` names what happened) |
| FR-010 | NFR-MNT-02; constitution VI (coverage is measured on the code the suite exercises) |
| FR-011 | constitution I; feature 030's guard contract (no cleanup across environments) |
| FR-012 | FR-TEN-05; DR-02; constitution I ("isolation lives in data access") |

### Sensitivity

| Requirement | Implements |
|---|---|
| FR-013 | constitution VI ("test-verified" — a suite that has never failed is untested) |
| FR-014 | constitution V (a defence's range is stated) |
| FR-015 | constitution VI |

### The public channel surface

| Requirement | Implements |
|---|---|
| FR-016 | **FR-CHN-01** (a channel has an external id, a type, a name and metadata) |
| FR-047 | **FR-CHN-05** — by REFUSING it. See §2: this is the clause the chapter contradicts on purpose |
| FR-017 | **FR-CHN-02** (repeating a creation returns the existing channel); constitution II (idempotency enforced by a unique index, not in memory) |
| FR-018 | **DR-02** (uniqueness is per tenant); FR-TEN-05 |
| FR-019 | **FR-CHN-04** (members by customer-supplied user id, users created on first membership) |
| FR-048 | **FR-CHN-07** (a channel holds at most 1,000 members); EIR-API-04 |
| FR-020 | **FR-RTM-05** (real-time events reach a channel's members) |
| FR-021 | NFR-SEC-09; constitution I (the suite covers what the build adds, on that build) |
| FR-022 | **FR-CHN-03, FR-CHN-06, FR-USR-01…** — scope statement, deferring to chapter 3.13 |
| FR-023 | constitution VI; chapter 2.8's recorded seam and its named retirement |

### The error vocabulary

| Requirement | Implements |
|---|---|
| FR-024 | **EIR-API-04** (the error envelope); constitution V ("`docs_url` … a reachable page") |
| FR-025 | EIR-API-04; NFR-MNT-02 |
| FR-026 | EIR-API-04; **EIR-WS-06** (the socket's codes are in the same vocabulary) |
| FR-027 | constitution V |
| FR-028 | constitution V; NFR-USE-02 (a developer can act on what they are told) |
| FR-029 | constitution VII (the series' documents and the platform's do not drift) |

### The outsider

| Requirement | Implements |
|---|---|
| FR-030 | **SRS §1.5 Phase 2 exit criterion**; constitution VII |
| FR-031 | SRS Phase 2 exit criterion |
| FR-045 | SRS Phase 2 exit criterion; ADR-05 (a service is reached by a port and a health check) |
| FR-032 | constitution IV ("`docker compose up` … including a seeded demo tenant") |
| FR-033 | SRS Phase 2 exit criterion; constitution V |
| FR-034 | constitution V (a defence trusted past its range is worse than none) |
| FR-035 | SRS Phase 2 exit criterion |

### The instruments

| Requirement | Implements |
|---|---|
| FR-036 | constitution I; feature 030's guard contract |
| FR-037 | feature 030's guard contract §the refusal message |
| FR-038 | constitution VI (an instrument is verified by driving it) |
| FR-039 | constitution VII; the fence-chain contract ("a published chapter may only fence what it teaches") |
| FR-040 | **constitution VI** (100% branch coverage for ordering, idempotency and tenant isolation; NFR-MNT-02) |
| FR-041 | NFR-MNT-02 |
| FR-042 | feature 030's exemption contract |
| FR-043 | **constitution I** ("isolation lives in data access"), ADR-16 |

**48 of 48 mapped.** Eight cited a clause in their own text before this file; the
other forty did not, and none of the forty turned out to be implementing nothing.

---

## §2 — governing clause → the requirement that covers it

Only the clauses this chapter TOUCHES. A clause it neither implements nor
contradicts is not listed, because a map that lists everything says nothing.

| Clause | Covered by | Note |
|---|---|---|
| NFR-SEC-09 | FR-001, FR-002, FR-021 | the suite this NFR names |
| FR-TEN-05 | FR-004 … FR-012, FR-018 | the requirement constitution I calls the most important in the system |
| FR-AUT-10 | FR-044 | narrowed from class to service |
| EIR-API-02 | FR-008 | the internal contract, attacked per credential class |
| EIR-API-04 | FR-024, FR-025, FR-026, FR-046, FR-048 | the envelope, and the two codes this chapter adds to it |
| EIR-WS-03, EIR-WS-06 | FR-007, FR-026 | the socket's session and its refusal vocabulary |
| DR-02 | FR-005, FR-017, FR-018 | per-tenant uniqueness, now load-bearing for an endpoint |
| FR-MSG-09 | FR-006 | history's shape is what an empty list attack compares against |
| FR-RTM-05 | FR-020 | **and see the gap**: `gaps.md` G1 — a REST-sent message reaches no socket, so this clause is delivered for socket sends only |
| FR-CHN-01 | FR-016 | **partly delivered**: all four elements accepted, and `private` refused (FR-047) |
| FR-CHN-02 | FR-017 | delivered |
| FR-CHN-04 | FR-019 | delivered |
| FR-CHN-05 | **FR-047** | **CONTRADICTED ON PURPOSE.** The clause promises a private channel is visible only to its members. `channels.type` has been a `"public" \| "private"` column since chapter 2.1 and NOTHING READS IT — history and send scope by `environment_id` alone, with no membership check on any read path. So the clause is unimplemented, and an endpoint accepting `private` would sell a guarantee the platform does not keep. The enum is `public` alone; the clause goes to chapter 3.13 with FR-CHN-03's private half. This is the finding analysis pass five made and it is the sharpest edit in the chapter. |
| FR-CHN-07 | **FR-048** | was UNMENTIONED before pass five; the SRS names `channel_member_limit_exceeded` in its own worked example for EIR-API-04, which is why the code is spelled that way |
| FR-CHN-03, FR-CHN-06, FR-USR-* | FR-022 | deferred to chapter 3.13, named rather than silent |
| EIR-API-06 | — | **WALKED INTO, and now claimed.** The clause asks that a validation failure name the offending field. Nothing in the api had ever set `field`: `ZodValidationPipe` threw `issues[0].message` and discarded `issues[0].path` for twenty-two chapters. Fixed in this chapter under FR-047's test (T053b), and the fix is general — every validation error in the platform now names its field. It has no FR of its own because the chapter found it while implementing FR-047 rather than planning for it; recorded here so the next chapter does not rediscover it. |
| DR-06, FR-MSG-08, FR-TEN-08, FR-MOD-06 | — | **TOUCHED AND NOT COVERED, deliberately.** The outbox keeps message text for ever (R7a), which collides with all four. The fix is a one-line prune owned by whichever chapter builds FR-MOD-06. Recorded in `db/catalogue.ts`'s SPINE comment with the numbers — 286,871 rows in the test lane — and not claimed here. |
| constitution I | FR-001, FR-003, FR-011, FR-012, FR-036, FR-043 | the principle the chapter exists for, and the lint clause it found unenforced |
| constitution II | FR-017 | idempotency at the storage layer |
| constitution IV | FR-032 | the seeded demo tenant — intent closed, letter not; see `README.md` |
| constitution V | FR-024, FR-027, FR-028, FR-014, FR-034 | reachable pages, and stated ranges |
| constitution VI | FR-010, FR-013, FR-015, FR-038, FR-040 | test-verified, and the 100%-branch clause answered with a number |
| constitution VII | FR-029, FR-030, FR-039 | the two repositories do not drift |
| ADR-05 | FR-045 | a service is a port and a health check |
| ADR-16 | FR-043 | the query engine lives in the repository layer |
| SRS §1.5 Phase 2 exit | FR-030, FR-031, FR-033, FR-035, FR-045 | verdict in `gaps.md`: **met in part** |

**Four clauses were touched without being claimed before pass five** — FR-CHN-05,
FR-CHN-07, FR-CHN-01 and EIR-API-06 — and all four now appear above with what the
chapter actually does to them. Two of the four are the more interesting kind: one
the chapter contradicts on purpose, and one it fixed without having planned to.

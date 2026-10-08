# Clauses — chapter 4.23, "The channel a socket names"

What this chapter engages, and how each is discharged. Written in Phase 3, with the
clause, and **before any code** — which is the half 4.22 could not claim.

## The new clause

**FR-RTM-11**, `docs/04-srs.md`, added at T015 in Phase 3. `check:srs` moved
**246 → 247 rows, 247 unique**, which was T003a's prediction written before the work.

**It is new, not an amendment, and T017 is why that is defensible.** All ten FR-RTM
clauses were read beside FR-CHN-11 before the eleventh was written:

```
FR-RTM-01  membership implies delivery, no per-channel subscription   no identifier
FR-RTM-02  cross-instance delivery                                    no identifier
FR-RTM-03  resume by cursor, and the revision count in the ack        no identifier
FR-RTM-04  backfill over 500 returns a truncation indicator           no identifier
FR-RTM-05  six event kinds                                            no identifier
FR-RTM-06  presence states and the grace period                       no identifier
FR-RTM-07  presence only to users sharing a channel                   no identifier
FR-RTM-08  typing expiry                                              no identifier
FR-RTM-09  five concurrent connections, best-effort                   no identifier
FR-RTM-10  revocation within five seconds, sixty when degraded        no identifier
FR-CHN-11  the REST half, and it says the socket is NOT covered
```

**Two survive the change without amendment and were checked rather than assumed.**
FR-RTM-03 names the ack's revision count as *"a per-channel count"* without saying
how a channel is named, and FR-RTM-04 names a *"truncation indicator"* rather than
its contents. Re-keying both leaves both true.

## Constitution, clause by clause

**I. Tenant isolation — ENGAGED.** The map is built from the session response, which
`channelsForUser` scopes with `eq(users.environmentId, this.environmentId)` through
`members`. Nothing in the gateway applies that scope and nothing there could forget
it. FR-006's probe (T038) names the predicate it deletes, and 065-4 says to expect a
single-mutation probe to see nothing. The inverse map is safe to derive because of
`unique("channels_environment_id_external_id_unique")`, checked rather than assumed.

**II. No acknowledged message lost — ENGAGED, TWICE.** Inbound, a cursor keyed by
uuid must still resume, or a published client silently resumes nothing (T011).
Outbound, the resume buffer is the seam where a client-facing frame is also internal
state: `flushable`'s `marks[frame.channel]` and the revocation filter at
`session.ts:662` both index a buffered frame by channel. **T012a's decision — to
translate at the single `send` — is what keeps both keyed**, and the two probes that
would catch it already exist and are green (T012b).

**III. Two data paths — NOT ENGAGED.** No analytical surface changes.

**IV. Single writer — NOT ENGAGED.** The translation is a read.

**V. API-first — ENGAGED.** This is FR-CHN-11's second half. Nothing here is new
behaviour; it is the gateway catching up with a published decision.

**VI. Requirement-driven — five bullets.**

1. *A requirement before the behaviour.* **MET ON TIME.** The clause is Phase 3 and
   the code is Phase 4. 4.22 met this bullet late and recorded it; this chapter's
   ordering was chosen because of that entry.
2. *100% branch coverage for tenant isolation.* The map's miss path (T012: drop and
   log, never emit the key) is in that population from the moment it exists. T039
   runs both halves of the pin probe through `pnpm coverage`; T040 asks first
   whether the code ran in **this** process, because the socket gauntlet spawns the
   api as a child and nothing in that child is instrumented.
3. *The cross-tenant suite attacks every endpoint.* **SATISFIED, and eleven analysis
   passes said otherwise.** `services/gateway/src/isolation.itest.ts` is the socket
   half of the gauntlet — 22 tests, found at pass 13 by opening the file. What
   remains is that it derives its targets from `frameSchema`'s members, so it is
   green by construction against a chapter that changes what a field carries; T042a
   adds the cases by hand for that reason.
4. *The quickstart runs unmodified.* **VIOLATED, standing, unwaivable.** The clause
   asks for automated execution in CI and `ci.yml` has no occurrence of `quickstart`;
   governance says the Principle VI gates are not waivable by review. It predates
   this feature and this feature cannot close it. T064 runs it by hand.
5. *Unknown fields rejected on write endpoints.* **ENGAGED HARDER THAN ASSUMED.**
   Both changed payloads are `z.strictObject`, so a new field is rejected by an old
   reader exactly as a missing one is — the change is two-sided in both directions
   and must land in one deploy (T014).

**VII. Boring by design — ENGAGED, AND NO NEW ADR.** No language, service or
dependency. ADR-38 already decided the rule; its *"what it does not cover"* paragraph
is amended instead (T043). The plan predicted no ADR and the prediction was checked.

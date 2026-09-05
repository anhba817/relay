# Research — 043, fix the review's findings

Seven questions, each answered by asking the repository rather than by reasoning about it.
Two of the answers changed the design and one of them makes a published remedy wrong.

---

## R1 — How does a spawned child get a port nobody else holds?

**Decision**: pass `PORT=0`, let the operating system assign, and read the assigned port out
of the child's own log line. This needs a one-line change in each service's entry point,
because both currently log the port they *asked for*.

    services/api/src/main.ts:18      const port = Number(process.env.PORT ?? 4000)
    services/api/src/main.ts:19      await app.listen(port)
    services/api/src/main.ts:42      createLogger("api").log("info", "listening", { port })

With `PORT=0` that line logs `0`. The value the harness needs is on the server object, not in
the variable. The gateway has the same shape at `main.ts:151-154`.

**Rationale**: it is the only option that cannot collide. Probing for a free port in the
parent and passing it leaves a window between the probe and the child's bind. A fixed port
collides always under contention; a random port from a fixed range collides sometimes —
`session.itest.ts:133` draws `4400 + random*200` and chapter 3.23 measured that as
self-colliding 2.96% of runs.

And the harness already captures the child's stdout (`harness.ts:342`), which is the
mechanism `gaps.md` 3.22-6 says eleven files own and six discard. This uses it for something
other than a failure message.

**Alternatives considered**: retry on `EADDRINUSE` — needs the child's error, which is in a
pipe read only on the health-check path; probe-then-pass — racy, and the race is exactly the
bug being fixed.

**AMENDED IN ANALYSIS PASS 2, and the amendment strengthens the decision rather than changing
it.** This entry chose `PORT=0` without knowing that `services/gateway/src/limits.itest.ts:16`
publishes the lane's port map, registers **4100–4300** to itself, and does not list
`packages/e2e` at all — `grep -c e2e` on that file returns zero. So the harness's three fixed
ports sit unregistered inside another file's range, and turbo runs the two packages at once.

The cheaper repair — register the lane in the map and fix only the teardown — was considered and
rejected. That map is maintained by hand and has already been wrong twice: chapter 3.21's
`gaps.md` item 4 found two missing entries, and it is missing a third today. **A second list
that must agree with reality is the defect this feature exists to remove.** `PORT=0` needs no
list.

**Secondary benefit worth naming**: logging the port you bound rather than the one you
requested is a correctness fix in its own right. Today, if `listen` ever bound something
other than the requested value, the log would say otherwise.

---

## R2 — Which of `connections.test.ts`'s seventeen tests need a running broker?

**Decision**: at least two provably do not, twelve provably do, and three need one test run
each to classify. The container-free file keeps the ones that need no broker; the rest join
the existing `connections.itest.ts`.

**MEASURED IN ANALYSIS PASS 4, and the reasoned version above was wrong twice.** Run the file
with `RELAY_REDIS_URL=redis://127.0.0.1:6399`:

    Tests  12 failed | 5 passed  (17)

| Test | Needs | How it was settled |
|---|---|---|
| `returns unenforced rather than zero when Redis is unreachable (FR-016)` | **no broker** | predicted, and confirmed |
| `states the maximum in exactly one place (FR-002)` | **no broker** | predicted, and confirmed |
| `does not throw for a slot the connection never held` | **no broker** | was "measure" — passes |
| `does not throw when it holds nothing` | **no broker** | was "measure" — passes |
| `keeps the heartbeat strictly inside the bound, three to one (FR-009)` | **no broker** | **predicted to need one, and does not** |
| `builds without a url, from the environment or from the default` | **broker** | was "measure" — fails |
| the remaining eleven | **broker** | each fails without one |

**Two container-free tests were predicted and five exist.** The heartbeat test was filed under
"each asserts registry behaviour" on the strength of its title; it asserts a timing bound and
never reaches the broker.

**ANALYSIS PASS 2 CLAIMED THE METHOD WAS CONFOUNDED. PASS 4 RAN IT AND IT IS NOT.** That
amendment said the `beforeEach` at `connections.test.ts:41` builds a registry against `REDIS`
for every test in the describe, so a run with containers stopped could report failures that say
nothing about the tests. **`createConnections` does not connect eagerly.** Against a dead port
the hook builds its registry, `afterAll` closes it, and every test that needs no broker still
passes — which is how the table above got measured at all.

The original claim is left standing here rather than deleted, so the correction is auditable:
it was reasoned from reading a hook and refuted by running one command. **The half that
survives is smaller and is not about breakage**: the tests that stay should still leave that
describe, because a container-free lane holding a Redis client it never uses is untidy.

**Rationale**: the file's own comment at line 18 argues that a real broker is the correctness
case, and that argument is right about the twelve. It is not an argument about which lane the
other five belong in.

**Consequence for cost**: the bulk moves, so the published listing chain for
`connections.test.ts` is retired and the moved assertions join
`connections.itest.ts`'s existing chain. Choosing "split" over "move" does not avoid that
work; it avoids losing the two tests that are honest unit tests today.

---

## R3 — Can the gateway refuse over-long text with a registered code that names the field?

**Decision**: yes, with no new plumbing. `session.ts:173`'s `sendError` already takes an
optional `field`, added in chapter 3.24 for FR-005, and omits the key when the path is empty.

**Consequence**: the refusal a client sees for over-long socket text changes from the api's
derived answer to the gateway's own. FR-010 requires a registered code and a named field;
which registered code is a task-level decision, and `invalid_frame` is the existing member
for a frame that fails schema validation.

---

## R4 — How many stored rows would the new validations reject?

**Decision**: measured, and the two answers are opposite.

    avatar_url scheme     (null) 387,091      https 586      anything else 0

    webhook event_types, all 32,606 type-rows across four distinct types
      message.created   31,757     channel.created     741   (declared, not emitted)
      message.deleted        54     message.updated      54

    refused by the rule this feature chose (the declared eight)        0
    refused by the rule the review recommends (the emitted five)     741   = 2.3%

**The avatar rule rejects nothing that exists.** The migration concern the review raises is
sound as a principle and empty in this database.

**The event-type rule as the review states it would reject 741 rows and this feature's rejects
none**, and that comparison is the finding that changes the design — not the 741 on its own.
Every type any customer has subscribed to is one FR-WHK-02 declares. See R5.

**Caveat carried deliberately**: this is the lane database, not a customer's. It is the only
population available, and a rule that is safe here can still be unsafe elsewhere — which is
why FR-013 and FR-017 ask for the count to be *recorded*, not for it to be zero.

---

## R5 — What should a webhook subscription be validated against?

**Decision**: the event types FR-WHK-02 **declares**, not the types the platform **emits**.
A subscription to a declared-but-unbuilt type is accepted, and the response says the type is
not emitted yet.

**Rationale, and it contradicts two published remedies.** The review says to *"compare values
with `OUTBOX_EVENT_TYPES`"* and `gaps.md` 3.23-1 recommends *"one `includes` against
`OUTBOX_EVENT_TYPES`"*. That constant holds the five types the platform emits. FR-WHK-02
declares eight, and `docs/04-srs.md:484` names `channel.created` among them. 741 stored
subscriptions name it.

Those customers subscribed to something the requirements publish. Refusing them would turn a
correct subscription into an error because the platform has not caught up with its own
specification.

The typo case the review is actually about — `mesage.updated` — is still refused, because a
misspelling is in neither set.

**Alternatives considered**:

- *Validate against the emitted five.* Refuses 741 correct rows. Rejected.
- *Validate against nothing and warn in the response.* A warning nobody reads is what the
  gap already is.
- *Accept the declared eight silently.* Loses the one thing a subscriber to `channel.created`
  most needs to know: that nothing will arrive yet.

**What it costs**: a declared set has to exist in code. `OUTBOX_EVENT_TYPES` is the emitted
subset today and there is no constant for the declared superset. The design is one list with
the emitted ones marked, so the two can never drift into two lists — which is the defect
`gaps.md` 3.23-4 records about `targets.ts` and the `@Accepts` decorator.

---

## R6 — Where can a close code be documented without tripping the existing gate?

**Decision**: inside the `**Status:**` line of the error code that carries it, which is
chapter 3.21's convention. Not under a heading of its own.

**Evidence**: `relay-tutorial/scripts/check-error-codes.mjs:59` computes

    const orphaned = headings.filter((h) => !codes.includes(h));

over every `^## (.+)$` in the reference, and exits non-zero for any heading that is not a
member of `ERROR_CODES`. A `## 4001` section fails that check with no exemption.

**Consequence for FR-019**: the new gate compares `CLOSE_CODES` against the reference's
*text*, not its headings. Both live in `packages/protocol/src/codes.ts`, so the checker reads
one file for the expected set exactly as it already does for `ERROR_CODES`.

---

## R7 — Where do the two new gates live, and what do they cost?

**Decision**: `relay-tutorial/scripts/`, and they cost no amendment.

**Evidence**: every platform file this feature touches is fenced by a published chapter —
thirteen of them, `session.ts` by sixteen chapters and `internal.ts` by eleven. The
tutorial's own scripts are fenced by nobody:

    scripts/check-error-codes.mjs      chapters: 0    appendix: 0
    scripts/sync-docs.sh               chapters: 0    appendix: 0
    scripts/check-fence-chain.mjs      chapters: 0    appendix: 0

So extending `check-error-codes.mjs` and adding `check-revision-order.mjs` are ordinary
edits. Every platform change is not.

**The full cost of the feature, in chain terms**: thirteen amendment hunks in
`relay-tutorial/fences/post-series.md`, one per platform file, plus one retirement for
`connections.test.ts` if the split leaves that path holding fewer assertions than its chain
publishes.

**Method note for the implementation**: `check-fence-chain` reports only the first difference
per file, so "three problems" can mean thirty stale lines across three files. Run it after
every source edit rather than once at the end — chapter 3.24's close-out broke fences three
separate times and found each one late.

# Chapter 3.18 — the plan against what shipped

*Written as the work happens, not at the end. Sections are filled by the tasks that
name them; anything still angle-bracketed has not been done.*

## What shipped

    <T042, T043, close-out>

## The two file counts

    <T042 — teaches / fences, kept in separate columns>

## The grammar could not move verbatim (T004, T007)

`plan.md` and T004 both said the subject grammar moves **verbatim**. It could not: the
package already exports a `subjectFor` — `internal.ts:112`, the event spine's
`(type, environmentId)` — and TypeScript refused the second one.

    src/index.ts(12,1): error TS2308: Module "./internal.js" has already exported
    a member named 'subjectFor'.

The spine's name is chapter 3.4's, published and fenced, so the new one moved:
**`subjectForChannel(channelId)`**. Nineteen analysis passes read both files and neither
noticed the collision; the compiler found it in four seconds.

It is also the same asymmetry pass 6 found and T044b records — the spine's subject carries
the tenant, the fan-out's carries only a channel id. Putting them in one package is what
made it a compile error instead of a paragraph.

## T014a — session.itest.ts stays outside the fence chain

**Decided: `(excerpt)` in the chapter; the file does not join the chain.**

It is fenced by no chapter today, which puts it with `sentinel.ts`, `sentinel.sql` and
`guard.itest.ts` in `gaps.md` item 7 — files the chain never verifies. This chapter adds a
third describe block to it (T014) and will put its end-to-end delivery test there (T022),
so the question had to be answered rather than discovered at close-out.

Three options were real:

    titled fence          the chapter carries the whole file — now 582 lines, of which
                          ~150 are this chapter's. A tutorial does not print 582 lines of
                          test harness, and a titled fence binds every later chapter that
                          edits the file.
    a new file            services/gateway/src/rest-delivery.itest.ts, ~150 lines and
                          fenceable. Rejected: the expensive part is `startApi`, which
                          SPAWNS the api from dist/main.js, and a second file either
                          duplicates it or needs a shared harness module that would itself
                          be unfenced. The cure has the disease.
    (excerpt) + no chain  CHOSEN. The chapter shows the new describe block, the reader sees
                          the test that proves the claim, and the chain does not silently
                          grow by 600 lines no chapter teaches.

The cost, stated plainly: **the chapter's end-to-end test is not verified against the
repository by `check:fences`.** That is one more file in item 7's set and it is recorded
there, not left implicit.

## An existing test's title over-promises (found while writing T014)

`session.itest.ts`'s first delivery test is titled *"opens for a token the api minted, and
knows the user's channels"* and asserts only `payload.user`. Its type annotation declares
`channels?: string[]` on the ack payload — a field `connectionAckSchema` does not have
(`{ user, cursor, resume_ok, truncated }`). The first version of T014's test read that
field and got an empty array.

Not this chapter's to fix, and worth knowing: the gateway learns the channel list from
`POST /internal/session` and never tells the client. A test whose title promises more than
it checks is how the annotation survived.

## The lint rule that nineteen analysis passes missed

`pnpm lint` failed the moment the publisher existed:

    'ioredis' import is restricted from being used. The counter store lives in
    services/api/src/limits and services/gateway/src/limits.ts only
    (constitution I, chapter 3.8). Its keys are per environment; an
    unrestricted client is a cross-tenant read.

**Nineteen analysis passes read `eslint.config.mjs` twice — pass 4 for appendix ownership,
pass 11 for the fence column — and neither noticed that the file this feature adds could
not import the driver it is built on.** The rule cites constitution I, which is the
NON-NEGOTIABLE principle, so this was not a style nit.

Two exemptions added, each with the reason the doctrine demands (`a LIST WITH REASONS, not
a directory pattern`):

    services/api/src/fanout/**            product code. The rule's reason is that counters
                                          are keyed `rl:{environment_id}:…`, so a loose
                                          client can read another tenant's. This client
                                          touches no keys — PUBLISH onto `chan:{uuid}`, and
                                          a subject is not readable at all.
    .../fanout/fanout.itest.ts            the two limits suites' argument exactly: the
                                          subject is what reaches the fabric, and only a
                                          subscriber using neither service's code can see it.

**And it grows the fence column again.** `eslint.config.mjs` was not in `plan.md`'s
sixteen-file table, and it is appendix-owned — `fences/post-series.md` holds a hunk
anchored just after the `services/gateway/src/fanout.ts` line this change sits beside.
Chapter 3.17 hit that same collision. Recorded for T047/T050.

## T030 — SC-002 is a composition, and no fixture does both halves

**Stated because the pair of suites would otherwise imply more than either proves.**

    services/gateway/src/resume.itest.ts     TWO gateway instances, real sockets, one
                                            fabric — and a STUBBED api. Three tests:
                                            the member's instance receives, the
                                            bystander's does not, and a channel neither
                                            holds reaches neither.
    services/gateway/src/session.itest.ts    a REAL api spawned from dist/main.js, a real
                                            socket, a real POST — and ONE gateway.

So "a REST send from a real api reaches a socket on another instance" is assembled from
two measurements rather than taken in one. The gateway has no database (ADR-05), which is
why its suites stub the api; giving `resume.itest.ts` a real one means giving it a Postgres
handle and the fixture stops being about the fabric.

**What makes the composition sound rather than convenient**: the api publishes to
`chan:{id}` and nothing else (asserted in `services/api/src/fanout/fanout.itest.ts`, on a
real subscriber), and an instance holding a member of that channel delivers while one that
does not stays silent (asserted here, on real sockets). The join is the subject string, and
it is one function in `@relay/protocol` with its own test.

**What would close it properly**: a fixture that spawns an api and two gateways. That is
the same shared-harness feature `gaps.md` item 2 wants for `session.itest.ts`, and it is
not this chapter's.

## Decisions recorded during the work

    <T009c the off-switch · T014a the session.itest.ts fencing decision ·
     T030 SC-002's composition · T044b the subject grammars' asymmetry>

## The phases that went badly

    <as they happen>

## What the next feature should do differently

    <close-out>

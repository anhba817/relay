# Chapter 3.22 — quickstart

Every command here is meant to be run, and the ones under *Verify the premises* were
run while this file was written. Chapter 3.21 wrote three commands into its task list
without running them and all three had wrong expectations.

---

## The lane

    cd relay-platform
    RELAY_POSTGRES_PORT=15432 docker compose up -d --wait

**This machine's own PostgreSQL holds 5432**, so the stack goes on 15432. Omitting
that variable takes the container down mid-recreate with `bind: address already in
use`, which chapter 3.20 did once.

The nine variables:

    DATABASE_URL=postgres://relay:relay@localhost:15432/relay
    RELAY_REDIS_URL=redis://localhost:6379
    RELAY_NATS_URL=nats://localhost:4222
    RELAY_INTERNAL_CREDENTIAL=rk_svc_local_development_credential_0000
    RELAY_INTERNAL_CREDENTIAL_GATEWAY=rk_svc_local_development_gateway_00000
    RELAY_WEBHOOK_SECRET_KEY=BpDal75yBZp7Fc2GtGS3D1vh7qOKgCWJkF6/d0XWxBU=
    RELAY_OUTBOX_RELAY=off
    RELAY_EVENT_CONSUMER=off
    RELAY_DELIVERY_RELAY=off

Plus `NO_COLOR=1 FORCE_COLOR=0` and a `sed` over the ANSI escapes for any run whose
counts are recorded. **Without these the api lane reads four red** — platform routes
answering 401 and `invariant 9` throwing `NatsError: CONNECTION_REFUSED` — and it
looks like a regression.

**And this applies to `pnpm coverage` too, not only `test:integration`.** Chapter
3.21's close-out spent two full lane runs learning that: one run came back with nine
dispatcher failures and one with four api failures, both invalid, and the second was
predicted by this paragraph in the previous chapter's copy of this file.

---

## Verify the premises before building on them

Five claims carry this chapter's design. Each has a command and an expected answer.

**P1 — no Lua, no MULTI, anywhere.** The whole basis for rejecting the SAD's sorted
set (research R3). If this stops being true, R3's argument weakens and the ADR
must say so.

    cd relay-platform
    grep -rn "\.eval(\|defineCommand\|\.multi(" --include="*.ts" services packages \
      | grep -v node_modules

Expect **no output**. Three hits exist for the word "evaluated" in prose; the
pattern above does not match them, which was checked.

**P2 — `presence.itest.ts`'s port range contains `meter.itest.ts`'s.** Research R7,
and it invalidates a hypothesis chapter 3.20 recorded as eliminated.

    grep -n "4700 +" services/gateway/src/presence.itest.ts
    grep -n "4710 +" services/gateway/src/meter.itest.ts
    grep -nE "fileParallelism" services/gateway/vitest.integration.config.mts

Expect `4700 + Math.floor(Math.random() * 200)` (= 4700–4899),
`4710 + Math.floor(Math.random() * 60)` (= 4710–4769), and **no output** from the
third — no `fileParallelism` setting means vitest's default, which runs files in
parallel, so the two do overlap in time as well as in range.

**P3 — the close-code set is pinned at five.** Adding a sixth is a decision the test
will report.

    grep -n "4001, 4002, 4003, 4008, 4009" packages/protocol/src/codes.test.ts

Expect **two** hits — line 18 and line 20:

    18:  it("contains exactly 4001, 4002, 4003, 4008, 4009", () => {
    20:      4001, 4002, 4003, 4008, 4009,

**The first draft of this paragraph said one hit, at line 20, and running the
command found two.** The set is written twice: once in the assertion and once in the
test's own title. So adding a sixth code means editing both, and a chapter that edits
only the assertion ships a test whose name lists five codes while it checks six —
which is the defect the previous chapter's late pass found four test titles that outran their assertions — in the file that would carry it.

**P4 — `policy.ts` divides ten thousand by five and ships three thousand.** Research
R6. Not this chapter's to fix, and it must not be quietly fixed either.

    grep -n "connect: 3_000" services/api/src/limits/policy.ts
    grep -n "connect: 3_000" services/api/src/limits/policy.test.ts

Expect one hit in each. `10_000 / 5 = 2_000`; the comment above the constant states
that derivation and the constant is 3,000.

**P5 — the lane's Redis supports `SET … IFEQ`.** The renewal's correctness rests on
it (research R3), and it is newer than everything else this platform asks of Redis.

    docker compose exec -T redis redis-cli INFO server | grep redis_version
    docker compose exec -T redis redis-cli SET p5 A PX 60000
    docker compose exec -T redis redis-cli SET p5 B IFEQ A PX 60000   # OK,  p5 = B
    docker compose exec -T redis redis-cli SET p5 C IFEQ WRONG PX 60000  # nil, p5 = B
    docker compose exec -T redis redis-cli DEL p5

Expect `redis_version:8.10.0` or later, `OK` then an empty reply, and `B` throughout
the second attempt. **`compose.yaml:33` pins `redis:8-alpine`**, so this holds for the
image the lane runs — but the tag floats, and an older server answers a bad-flag
`SET` with an error rather than a refusal, which would fail loudly rather than
silently. Verify it anyway: the alternative design is a compare-then-set, which is
two commands and a race.

---

## Run the feature's own tests

Unit lane, fast, no containers beyond Redis:

    cd relay-platform
    npx vitest run services/gateway/src/connections.test.ts
    npx vitest run packages/protocol/src/codes.test.ts

The cross-instance file. It boots gateways in process on `server.listen(0)` with a
stubbed `ApiClient` and **spawns no api**, so it needs no port range:

    RELAY_REDIS_URL=redis://localhost:6379 \
      npx vitest run --root services/gateway \
      --config vitest.integration.config.mts src/connections.itest.ts

The sealed outsider, which is the only instrument that boots the shipped binary and
the only one that would have caught chapter 3.21's inert feature:

    npx vitest run --root packages/outsider src/integrate.itest.ts

---

## Prove the cap by hand

Five connections, then a sixth, against a locally running gateway. Adjust the token
minting to whatever `quickstart.md` in the api's chapter does.

    for i in 1 2 3 4 5 6; do
      npx wscat -c "ws://localhost:8080/v1/ws?token=$TOKEN" &
    done

Expect five sockets to receive `connection.ack` and the sixth to receive an error
frame followed by a close with the new code. **Read the close code, not the fact of
closing** — a socket that closes for the wrong reason looks identical from the
outside, which is `contracts/refusal.md`'s whole subject.

Then close one and open another:

    # kill any one of the five, then
    npx wscat -c "ws://localhost:8080/v1/ws?token=$TOKEN"

Expect immediate acceptance. **No waiting period** — that is SC-003, and it is the
observable difference between this refusal and a rate limit.

---

## Prove the bound, which is the slow one

FR-007 and FR-008 are about a crashed instance, and the only honest test takes a
minute of wall clock. The bound is 60,000 ms.

    # with five slots held by a gateway, kill it without letting it close sockets
    kill -9 <gateway pid>

    # before the bound: still refused
    sleep 30 && npx wscat -c "ws://localhost:8080/v1/ws?token=$TOKEN"

    # after the bound: accepted
    sleep 35 && npx wscat -c "ws://localhost:8080/v1/ws?token=$TOKEN"

**Both halves matter and the first is the one usually skipped.** A test that only
checks "the slot frees eventually" passes against an implementation with no bound at
all. Chapter 3.19 shipped a presence bug by arming a check at exactly its own grace
period; the test asserts *held at 59 s* and *free after the bound*, not just the
second.

In the integration file this is done with an injected clock rather than `sleep`,
which is what `presence.itest.ts` does — but the manual version above is what a
reader can run, and it is the one that proves the injected clock is telling the
truth.

---

## The gates, and where they live

All five `check:*` scripts are in **`relay-tutorial`**, including the three that read
`relay-platform` and `docs/`. Running them from `relay-platform` prints nothing and
returns 254, which reads exactly like a gate that passed.

    cd relay-tutorial
    for g in fences docs figures srs errors; do
      pnpm -s check:$g > /tmp/g-$g.txt 2>&1; echo "check:$g exit=$?"
    done

**Capture the exit code; do not read the last line.** `pnpm -s check:x | tail -1 &&
next` reads `tail`'s status, and chapter 3.21's close-out committed over a red
checker that way.

`check:errors` reads `packages/protocol/dist/codes.js` — the **built** artifact — so
run `pnpm build` in `relay-platform` first or it is green for the wrong reason. This
chapter adds a close code and an error code, so that ordering matters more than usual.

---

## The battery, at close-out only

Twenty runs, nothing else on the machine, containers for api/gateway/dispatcher
stopped:

    RELAY_POSTGRES_PORT=15432 docker compose stop api gateway dispatcher

Budget 240 s; chapter 3.21 measured a mean of 228.63 s with a stdev of 0.68, leaving
11.37 s. **Nineteen of twenty green does not prove much**: it rejects a per-run
failure rate above 21.61% at 95% confidence, and chapter 3.20 measured 17.5% across
forty runs. Do not read a red run as this chapter's defect without reading the
failure.

**Nothing else runs on the machine, and that includes your own tooling.** Chapter
3.20 counted 700 tests in run 1 and 701 in the rest because a test was written into
a file while the battery was running; chapter 3.21 invalidated a coverage lane by
running two forced turbo builds during it.

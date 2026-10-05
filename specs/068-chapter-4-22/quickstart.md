# Quickstart — chapter 4.22, "★ Milestone: the Priya test"

**§0 to §2 are MEASURED on 2026-10-05. §3 and §4 are PREDICTIONS** until phase 9
runs them. The last eight chapters' predictions were wrong 3, 4, 3, 5, 2, 0, 5 and
2 times — and 4.21's two were both wrong for one reason: **they were written before
two decisions were taken.** This chapter's open decision is R2, so §3 is the section
to distrust.

Run §0 first in the same shell.

## 0 · Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
RELAY_POSTGRES_PORT=15432 docker compose --profile services build api
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
export K=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs 2>/dev/null | tail -1)
```

**THE IMAGE REBUILD IS NOT OPTIONAL.** Everything below talks to `localhost:4000`,
which is the composed container. 4.11, 4.19 and 4.20 each met a route answering 404
against a stale image and read it as a missing route.

## 1 · MEASURED — Stage 2, the wall this chapter opens on

```bash
ORD="order-$RANDOM"
curl -s -X POST localhost:4000/v1/channels -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"external_id\":\"$ORD\",\"type\":\"private\"}" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])'

for key in "$ORD" "$(curl -s -X POST localhost:4000/v1/channels -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"external_id\":\"$ORD\",\"type\":\"private\"}" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')"; do
  printf '  %-40s %s\n' "$key" \
    "$(curl -s -o /dev/null -w '%{http_code}' -H "authorization: Bearer $K" "localhost:4000/v1/channels/$key")"
done
```

**Measured**: the external id answers **500**; the uuid answers **200**.

**AND THE ONLY RESOLUTION THAT WORKS IS A WRITE.** Re-POSTing the same
`external_id` returns the same channel — FR-CHN-02's idempotent create — so a
support tool resolving an order number today performs a channel creation. Measured:
`same channel: True`.

## 2 · MEASURED — the two key spaces, which is why

```bash
U="who-$RANDOM"
curl -s -X POST localhost:4000/v1/users -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"users\":[{\"external_id\":\"$U\"}]}" >/dev/null
curl -s -o /dev/null -w '  users by external id:    %{http_code}\n' \
  -H "authorization: Bearer $K" "localhost:4000/v1/users/$U"
docker compose exec -T postgres psql -U relay -d relay -t -A -c "
select count(*) || ' channels, ' ||
       count(*) filter (where external_id ~ '^[0-9a-f]{8}-') || ' with a uuid-shaped external id'
  from channels;"
```

**Measured**: users answer by the customer's identifier — **200** on a user this
section creates; **41,766 channels, 0 with a uuid-shaped external id**. The ambiguity
a dual-key route would introduce is real in principle and has never occurred.

**THIS SECTION CREATES ITS OWN USER, AND THE FIRST DRAFT DID NOT.** It read
`localhost:4000/v1/users/qs-bot` — the demo seeder's bot, which every recent
quickstart uses — and measured **404**. The cause is chapter 4.21's own §3:
**it erases `qs-bot`, and erasure is irreversible.** So on any lane where that
quickstart has been run, the seeder's best-known fixture id is permanently absent,
and the 404 reads as a broken route rather than as the previous chapter working
exactly as designed. **A quickstart that destroys a shared fixture has to say so**,
and the chapters after it have to stop borrowing that id.

## 3 · The journey, after the chapter (PREDICTION)

```bash
RELAY_API_URL=http://localhost:4000 RELAY_WS_URL=ws://localhost:4001 \
RELAY_DEMO_CREDENTIAL=$K pnpm --filter @relay/outsider test:integration
```

**Expected**: the sealed suite's existing tests plus the six Priya stages, all green.
**Check the margin**: every assertion names the chapter it verifies, and §4 is what
tests that the naming is true.

**DISTRUST THIS SECTION.** Stage 2's assertion depends on R2, which is undecided at
the time of writing. If R2 picks option D, the stage asserts the re-POST and the 500
stays as a published limit; if it picks C, the stage asserts a 404 and the 500 is
gone from that route.

## 4 · The margin, falsified (PREDICTION)

```bash
git revert --no-commit part4-ch18 && pnpm --filter @relay/outsider test:integration
git revert --abort 2>/dev/null; git reset --hard HEAD
```

**Expected**: reverting 4.18 turns the Stage 6 audit assertion red and nothing else;
4.19 turns the Stage 3 history assertion red; 4.21 turns the Stage 6 receipt
assertion red. **Three chapters, three named assertions** — which is SC-002, and the
only thing that makes the margin a claim rather than a comment.

## 5 · And what this still cannot show

- **Whether Phase 3 can be exited.** Its first clause wants seven consecutive days of
  reconciliation and there is no scheduler (ADR-28). The chapter states the verdict.
- **Whether a real support engineer could do this.** The test proves the API permits
  the journey, not that a person finds it. `docs/03`'s own measure — *% of disputes
  resolvable from the record alone* — is a customer's number and not Relay's.
- **The eleven-minute interval.** The dispute turns on an edit eleven minutes after
  the send; a test asserts only that the instants differ and which came first.

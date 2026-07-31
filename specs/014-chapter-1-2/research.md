# Research: Tutorial Chapter 1.2 — One Command, Whole World

All Technical Context unknowns resolved. Decisions below; the spec's
edge cases each land in exactly one decision.

## R1 — The compose file: shape, names, healthchecks, volumes, ports

**Decision**: One `compose.yaml` (the Compose-v2 canonical filename) at the
relay-platform root, project `name: relay`, four services with pinned image
tags, a healthcheck per service, and volumes that *mirror each store's
durability semantics*:

| Service | Image (pin verified at implementation) | Healthcheck | Volume | Host port |
|---|---|---|---|---|
| `postgres` | `postgres:<current major>-alpine` | `pg_isready -U relay` | `postgres-data` | 5432 |
| `redis` | `redis:<current major>-alpine` | `redis-cli ping` | **none — deliberately ephemeral** | 6379 |
| `nats` | `nats:<current 2.x>-alpine`, command `-js -sd /data -m 8222` | HTTP `GET :8222/healthz` | `nats-data` | 4222 (+8222 monitor) |
| `clickhouse` | `clickhouse/clickhouse-server:<current LTS>` | HTTP `GET :8123/ping` | `clickhouse-data` | 8123 (+9000 native) |

Postgres env: `POSTGRES_USER/PASSWORD/DB = relay/relay/relay`, marked in prose
as dev-only credentials. **Amended at implementation (surfaced, not silent)**:
host ports are `${RELAY_*_PORT:-<default>}` env knobs with the standard
defaults — the reference machine itself runs a local Postgres and Redis on
5432/6379, so the collision case is real, and one env variable beats editing a
fenced file; the container side never changes. Also verified against image
reality: the postgres:18 image moved its volume mount to
`/var/lib/postgresql` (PGDATA beneath it). The single command the
chapter teaches is **`docker compose up -d --wait`** — `--wait` blocks until
every healthcheck reports healthy, which is what makes "one command" honest.

**Rationale**: Healthchecks are the mechanism that turns "started" into
"ready" (the spec's central edge case); `--wait` is the smallest tool that
consumes them. The volume asymmetry is a teaching gift: Postgres/NATS/ClickHouse
persist because ADR-03/04 (system of record), ADR-02/06 (durable streams), and
ADR-08 (analytical store) demand it; Redis gets no volume because ADR-07
(lossy fan-out by design) and ADR-10 (presence with TTL) define its contents as
safe to lose. The infrastructure declaration *is* the architecture, restated.

**Alternatives considered**: `docker-compose.yml` filename (legacy v1
convention; the tutorial teaches current practice); floating tags like
`postgres:alpine` (breaks tag-is-truth reproducibility); wrapper scripts /
Makefile (violates "boring", hides the one command); healthcheck-less compose
with a wait-for-it script (re-implements what Compose provides); parameterized
ports via `.env` (premature — noted in prose as the escape hatch for
collisions).

## R2 — English chapter narrative (the beats)

**Decision**: ~2,300 prose words, first-person plural, nine beats:

1. **Cold open from the 1.1 checkpoint**: the workspace passes three commands —
   but it computes nothing yet; every chapter ahead needs stores under it.
   Quote NFR-MNT-03 verbatim ("The full stack shall be startable locally with
   a single command", P1) — a *requirement*, not a convenience (docs/07's
   angle: day-one requirement, not afterthought). D8 is the why.
2. **SKIP AHEAD**: tag `part1-ch2`; `docker compose up -d --wait` +
   `pnpm lint && pnpm typecheck && pnpm test`.
3. **Why these four** (WHY #1, citing the SAD's decisions): one paragraph per
   store — Postgres (the system of record; ADR-03's ordering lives in it,
   ADR-04's single writer guards it), NATS JetStream (ADR-02, "a fraction of
   Kafka's operational mass"; ADR-06's outbox drains into it), Redis (ADR-07's
   deliberately lossy fan-out + ADR-10's presence — "the correct amount of
   durability … is none"), ClickHouse (ADR-08 single node; CON-01 exists
   precisely to forbid analytics in Postgres). Figure 1: the four stores with
   ghosted future services.
4. **The compose file, walked**: first the tools check (the 1.1 convention —
   Docker Engine + Compose v2, verified with `docker compose version`, `--wait`
   support required; one pointer to the official install docs, explicitly NOT
   an installation guide — the spec's readers-without-Docker edge case); then
   the full `compose.yaml` fence (title'd), healthchecks explained, the volume
   asymmetry called out (Redis has none on purpose).
5. **TRAP — started is not ready**: naive `up -d` returns while Postgres is
   still initializing; 1.4's services would crash-loop; `depends_on` alone
   orders *starts*, not *readiness*. The fix is structural: healthchecks +
   `--wait` (and later, `depends_on.condition: service_healthy`). Figure 2:
   the two timelines (start events vs. ready events).
6. **One command, verified**: `up -d --wait`, `docker compose ps` showing four
   `(healthy)`, teardown semantics (`down` keeps volumes, `down -v` is the
   reset button — say what dies). WHY #2 (source: NFR-MNT-03 · D8): why the
   *verification* is part of the requirement — a command that returns before
   ready is a demo, not reproducibility.
7. **The gate learns about the world**: `infra.ts` + `infra.test.ts` fences —
   the day-one-test convention continued; the gate stays Docker-free (CI
   reality) while asserting the declaration. The additive-only rule taught in
   one paragraph: 1.1's files are now read-only; new behavior, new files.
8. **FORWARD REF**: MinIO + the seeded demo tenant (the SAD's full compose
   sentence) arrive with media and real services; 1.3 builds `@relay/protocol`
   on this quiet foundation; 1.4's walking skeleton plugs into these very
   containers. Figure 3: the gate flow extended — compose up → healthy → three
   commands → tag.
9. **Your turn** (exercise = the build) + takeaways + CHECKPOINT (workspace +
   all four healthy + gate green = tag `part1-ch2`).

Battery: WHY 2, TRAP 1, SKIP AHEAD 1, FORWARD REF 1, CHECKPOINT 1, figures 3.

**Rationale**: Mirrors 1.1's proven arc (decision → build → verify → gate);
the TRAP is the chapter's conceptual core and gets a figure.

**Alternatives considered**: teaching each store in its own chapter-section
with config deep-dives (bloats past 4,000 words; per-store depth belongs to
the parts that use them); leading with the compose file and retrofitting the
why (violates the decisions-first format).

## R3 — The additive-only fence discipline

**Decision**: A code chapter MUST NOT modify any file a previous chapter
fenced. 1.2's platform changes are strictly new files (`compose.yaml`,
`packages/config/src/infra.ts`, `infra.test.ts`) plus README (never fenced).
Consequence: 1.1's ten file fences remain byte-valid at `part1-ch2`, so the
fence battery now diffs BOTH chapters' fences against HEAD/tag. The rule is
stated in the chapter (beat 7) and enforced in verification.

**Rationale**: The spec (FR-007) demands 1.1's fences hold at the new tag; the
only scalable way is to make earlier-fenced files immutable. When a future
chapter genuinely must edit one (it will happen — e.g., adding a workspace
script), the edit must be *shown as a diff in that chapter* and the fence
battery pins the old chapter's check to its own tag — deferred until needed.

**Alternatives considered**: pinning each chapter's fence check to its own tag
only (weaker promise; lets the repo drift from published prose silently);
re-fencing changed files in the new chapter (duplicates content, confuses
readers about which chapter owns a file).

## R4 — How the gate asserts the infrastructure without Docker

**Decision**: `packages/config/src/infra.ts` exports the infra constants —
`INFRA_SERVICES = ["postgres", "redis", "nats", "clickhouse"] as const` plus
`COMPOSE_FILE = "compose.yaml"` — and `infra.test.ts` reads the repo-root
`compose.yaml` as *text* (same `readFileSync` pattern as 1.1's
`pnpm-workspace.yaml` test) asserting: every `INFRA_SERVICES` name appears as
a service key; a `healthcheck:` count ≥ the service count; the three durable
volumes appear and no `redis-data` does. No YAML-parser dependency.

**Rationale**: Boring by design — 1.1 already established string assertions
over real manifests; a YAML dependency buys precision the assertions don't
need and adds the first non-dev-tool dependency for a test's sake. The test is
meaningful (it fails if a store is renamed/dropped, a healthcheck is deleted,
or Redis quietly gains persistence) yet runs in CI with no daemon.

**Alternatives considered**: `yaml` devDependency + structural parse (more
precise, more machinery; revisit when compose grows past assert-by-string
scale); a `docker compose config` exec-based test (requires Docker — breaks
the gate's Docker-free constraint); skipping tests for compose entirely
(violates FR-006 and the day-one-test convention).

## R5 — The manifest flip

**Decision**: `lib/tutorial.ts` chapter 1.2 entry — flip `status` to
`"published"`, add `translatedIn: ["vi"]`, and settle the 013 placeholders:
`readerMinutes` 90 → 60 (deliberate — shorter chapter than 1.1; pulls overlap
reading), `readerProduces` reworded to name the verified-healthy outcome, new
`readerProducesVi`, `sourceDoc` extended to `"docs/04-srs.md, docs/05-sad.md"`
(NFR-MNT-03 is the chapter's spine). Title/path/titleVi stay as seeded ("Một
câu lệnh, cả thế giới" / `/part-1/chapter-02/one-command-whole-world`). No
tutorial-side source edit outside this one entry: footers (1.1 next card, 1.2
prev/next), sidebar (2 links + 2 forthcoming), landings, sitemap (26 → 28,
baseline re-verified against the built site), SEO metadata all derive from the
manifest.

**Rationale**: This is the publishing mechanism working as designed — feature
013 seeded the structure (with placeholder reader-facing values) precisely so
this chapter is a single-entry edit.

**Alternatives considered**: none — any additional nav edit would falsify
SC-006.

## R6 — Healthcheck specifics (the commands the chapter shows)

**Decision**: Postgres `pg_isready -U relay -d relay`; Redis `redis-cli ping`
expecting `PONG`; NATS HTTP `/healthz` on the 8222 monitor port (enabled via
`-m 8222`); ClickHouse HTTP `/ping` on 8123. Interval 5s / timeout 3s /
retries 5 / `start_period` generous for Postgres first-boot initialization
(the TRAP's concrete villain). Exact probe syntax (exec-form arrays, wget vs
curl availability inside each image) is verified against the running
containers at implementation and the compose fence is truth.

**Rationale**: Each probe is the store's own idiomatic readiness signal —
teachable in one line each; no custom scripts.

**Alternatives considered**: TCP-port checks (`nc -z`) — port-open ≠ ready,
which is the exact misconception the TRAP kills; uniform `curl` everywhere
(not present in all images; per-image reality beats uniformity).

## R7 — Vietnamese chapter conventions

**Decision**: Full naturalized register per the settled glossary and the July
2026 corrections: meaning-first phrasing (no structural calques), dev terms in
English (**package**, compiler, test runner, healthcheck, volume, image,
container), "cửa ải ba câu lệnh" for the gate (verb: "vượt qua"), "tin nhắn",
"quả ngọt", "bản giao kèo". Store names, service keys, commands, and all code
fences stay English; fences byte-identical to the English chapter; figure
labels translated in `figures.ts`. Naturalization self-review before
presenting; Dong reads before committing.

**Rationale**: Codifies the register corrections applied to 1.1 so 1.2's first
draft starts at the corrected standard instead of repeating the cycle.

**Alternatives considered**: none — register is settled user feedback.

## R8 — What stays out (and where it's promised)

**Decision**: Out of scope, each with its landing place: MinIO (arrives with
media handling — FORWARD REF), seeded demo tenant (needs schema + services —
FORWARD REF, Part 2+), service containers/Dockerfiles for Relay's own services
(docs/07 §6.1), CI pipeline (later chapter), `.env` port parameterization
(prose escape-hatch note only), `depends_on` wiring between services (nothing
depends on anything yet — arrives in 1.4 with the walking skeleton).

**Rationale**: The spec's assumption resolves the SAD-vs-docs/07 scope tension
one-directionally; everything excluded is named in the chapter rather than
silently absent (the spec's "honest omission" edge case).

**Alternatives considered**: shipping MinIO "for completeness" (dead weight
with no consumer for parts to come; violates docs/07's row scope).

# Research: Tutorial Chapter 2.1 — Schema with a Spine

All Technical Context unknowns resolved.

## R1 — The schema slice (SAD-faithful, gaps recorded)

**Decision**: One migration, `migrations/001_core_tables.sql`, creating in
dependency order: `applications` (**DECISION** — stub: `id UUID PRIMARY KEY,
name TEXT NOT NULL`; the SAD's environments table references it but never
defines it; its real shape belongs to Part 3's tenancy chapters),
`environments`, `users`, `channels`, `messages` (all four **verbatim from
SAD §6.1** including CHECK constraints, DR-cited UNIQUEs, the DR-03 partial
unique index, and comment citations), and `members` (**DECISION** — the
docs/07 row and SAD §6.3's hot-path index reference it; §6.1 never defines
it: `channel_id UUID NOT NULL REFERENCES channels(id), user_id UUID NOT NULL
REFERENCES users(id), joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
PRIMARY KEY (channel_id, user_id)` — roles arrive with the channel-semantics
chapters). Plus the two SAD §6.3 hot-path indexes: `messages (channel_id,
sequence DESC)` and `members (user_id, channel_id)`. Deferred with named
arrival points: message_edits (2.x edit chapter), outbox (ADR-06's chapter),
emoji/media tables (their parts), `messages` partitioning (SAD growth note →
retention chapter).

**Rationale**: The docs/07 row fixes the slice; the SAD's own SQL is the
quotable source (C5 checks it column-exact); both gaps are *genuinely* open
in the documents, so the chapter models the discipline: decide out loud,
cite what anchors the decision (the §6.3 index shape for members).

**Alternatives considered**: skipping the applications FK (diverges from
quoted SAD SQL — worse than a stub); defining full membership roles now
(invents semantics no requirement fixes yet); migrating every §6.1 table
(dead tables with no chapter behind them).

## R2 — The driver

**Decision**: `pg` (node-postgres), current stable pinned at install,
dependency of `services/api` ONLY — this is the fenced-package.json
amendment (R4). `src/db/client.ts` exports a lazy pool factory reading
`DATABASE_URL` (default `postgres://relay:relay@localhost:5432/relay`, the
compose dev credentials; overridable for remapped ports).

**Rationale**: The boring standard; no ORM (the repository layer IS the
abstraction, and hiding SQL would undercut a chapter whose subject is the
SQL); pool config defaults suffice at this stage.

**Alternatives considered**: postgres.js (fine library, but `pg` is the
ecosystem default = boring); an ORM/query builder (abstraction fighting the
teaching); putting the dependency at the workspace root (wrong locality AND
a worse fence amendment).

## R3 — Migrations: plain SQL + a tiny runner

**Decision**: Numbered `.sql` files in `services/api/migrations/`;
`src/db/migrate.ts` (~50 lines, run via the api package's `migrate` script
with tsx): creates `schema_migrations(version TEXT PRIMARY KEY, applied_at
TIMESTAMPTZ)` if absent, reads the directory in filename order, applies each
unapplied file inside a transaction, records it. Forward-only by
construction — there is no down path at all (constitution workflow clause:
"versioned, forward-only"). Re-run = no-op (SC-002's idempotence check).

**Rationale**: A migration framework would abstract exactly the thing this
chapter teaches; the runner is small enough to be a fence and to be
understood whole; SAD SQL stays verbatim because migrations ARE SQL files.

**Alternatives considered**: node-pg-migrate/drizzle-kit (JS-defined
migrations — the SAD's SQL would be transliterated instead of quoted; new
API surface); prisma migrate (an ORM's tooling without its ORM — and the
tutorial site already tells that story); down-migrations (explicitly
forbidden by the constitution's forward-only clause).

## R4 — The fence amendment mechanism (diff-fences + re-pinning)

**Decision**: When a chapter must edit a file a previous chapter fenced, it
shows the edit as a **diff-fence**: a fenced block with language `diff` and
`title="<repo path>"`, containing a minimal unified diff. Verification rule
(machine-checkable, git-independent): the pre-image is the fence text
published in the predecessor chapter for that path; applying the diff-fence
to the pre-image MUST byte-equal the current repository file. The
predecessor chapter's direct fence check for exactly those paths re-pins to
its own tag (recorded in the contract); all its untouched fences continue to
match HEAD. This chapter amends exactly two files: `services/api/package.json`
(1.4 fence — + `pg`, + `migrate` and `test:integration` scripts) and
`eslint.config.mjs` (1.1 fence — + the no-restricted-imports ban on `pg`
outside `services/api/src/db`).

**Rationale**: 014's R3 promised this mechanism "when needed"; it is needed
now. Making the pre-image the *published fence text* (not a git object)
keeps verification self-contained and makes the chapter honest in print:
readers see exactly what changed in code they already typed. en/vi
diff-fences are byte-identical like all fences.

**Alternatives considered**: re-fencing whole changed files (readers can't
see what changed; ownership of the file's prose home gets murky);
silent edits with tag-pinned checks only (the spec forbids silence);
freezing fenced files forever (would force absurd workarounds like a second
package.json).

## R5 — The repository layer and its enforcement

**Decision**: `src/db/repository.ts` exports two surfaces with a bright
line: `createEnvironment(pool, { name })` — the *admin* surface that creates
tenants (used by tests and, later, tenancy endpoints; documented as the only
non-tenant-scoped operation). Because `environments.application_id` is
`NOT NULL REFERENCES applications(id)` (SAD verbatim) and the applications
lifecycle belongs to Part 3, **createEnvironment also inserts a stub
application row per environment** (one INSERT; U1 remediation) — the stub is
part of the admin surface's bright line and is called out in prose. All
primary keys are generated **app-side via `crypto.randomUUID()`** (the 1.4
request-id decision extended; L2): the SAD's SQL declares no DEFAULTs and the
migration adds none. And `class Repository` whose **constructor requires
`(pool, environmentId)`**; every method (users: create/getByExternalId;
channels: create/getByExternalId/list; members: add/listForChannel/
channelsForUser) is scoped by the instance's `environment_id` in SQL — the
WHERE clause lives once, in the layer, not at call sites. Cross-tenant reads
return null/empty (no existence reveal, constitution I). Enforcement:
`eslint.config.mjs` gains `no-restricted-imports` forbidding `pg` outside
`services/api/src/db/**` (the R4 diff-fence) — the constitution's
"lint-forbidden" clause made literal. The isolation suite
(`repository.itest.ts`): two environments; data created in A; a Repository
for B attempts every read with A's identifiers → null/empty, every list →
excludes A's rows; plus DR-02's per-tenant uniqueness (same external_id in
both environments succeeds; duplicate within one fails).

**Rationale**: "Designed out, not tested out" needs both halves shown: the
shape that makes leaks inexpressible (constructor + single WHERE home) and
the suite that attacks it anyway (NFR-SEC-09's spirit at the layer that
exists). The TRAP is the tested-out world: WHERE clauses sprinkled at call
sites, one forgotten filter away from a Sev-0.

**Alternatives considered**: Postgres row-level security (real technique,
but it moves the teaching into database policy config and dilutes ADR-04's
one-codebase claim — noted in prose as an additional belt for later);
per-call environment_id parameters (exactly the vigilance model the chapter
rejects); a shared packages/db (hands the gateway a loaded gun — ADR-04).

## R6 — The integration lane

**Decision**: Integration tests are named `*.itest.ts` — the fenced root
vitest include (`**/src/**/*.test.ts`) never matches them, so `pnpm test`
stays Docker-free with zero fence edits. The api package gains
`vitest.integration.config.ts` (include `src/**/*.itest.ts`) and script
`"test:integration": "vitest run --config vitest.integration.config.ts"`.
The suite connects via DATABASE_URL, runs migrations programmatically in
setup (the runner is importable), and TRUNCATEs the chapter's tables
(CASCADE) before each run — deterministic without `down -v`. Guardrail: the
default URL targets the compose dev database; the suite refuses to run
(fails fast with a clear message) if the URL's host isn't local — the
never-touch-Neon rule made mechanical. The constitution's "on every build"
clause is recorded as trajectory: the lane exists and is documented; CI
wiring arrives with the CI chapter.

**Rationale**: The gate's four-chapter Docker-free promise holds by
*naming*, not by editing fenced configs; the compose stack finally serves
its 1.2 purpose; fail-fast on non-local hosts costs three lines and removes
a whole class of accidents.

**Alternatives considered**: testcontainers (a dependency to create what
compose already provides); editing the root vitest config to exclude
(a fence amendment we don't need); mocking the database for isolation tests
(an isolation proof against a mock proves nothing — the entire point is
real SQL against real constraints).

## R7 — The Part 2 manifest seed

**Decision**: The existing Part 2 entry (currently `chapters: []`) gains all
eight docs/07 chapters. 2.1: `status: "published"`, `translatedIn: ["vi"]`,
path `/part-2/chapter-01/schema-with-a-spine`, titleVi "Schema có xương
sống", readerProduces "A migrated schema and a tenant-scoped repository
layer — cross-tenant leaks made inexpressible" + readerProducesVi "Schema đã
migrate và tầng repository khóa theo tenant — rò rỉ giữa các tenant thành
điều không thể viết ra", sourceDoc "docs/04-srs.md, docs/05-sad.md",
readerMinutes 90. 2.2–2.8 forthcoming with reserved paths
(`the-write-path`, `send-it-twice`, `history-that-pages`, `the-socket`,
`two-servers-one-conversation`, `the-tunnel`, `milestone-the-tuan-test`),
docs/07 titles, seed readerProduces from the row's Built column, and draft
vi titles for Dong's review: "Đường ghi tin", "Gửi hai lần", "Lịch sử biết
lật trang", "Đường socket", "Hai server, một cuộc trò chuyện", "Đường hầm"
(the 0.3 glossary term), "Cột mốc: bài kiểm tra Tuan".

**Rationale**: The 013 precedent exactly; seeding all eight makes every
later Part 2 chapter a pure flip; "Đường hầm" reuses Tuan's established
term.

**Alternatives considered**: seeding only 2.1 (每 flip would then be a
seed+flip hybrid — worse); seeding Part 3+ (their features' business).

## R8 — English chapter narrative (the beats)

**Decision**: ~2,500 prose words, ten beats:

1. **Cold open — the heart starts here**: Part 1 built ground; Part 2 is
   the part docs/07 stars. And it opens not with sending a message but with
   the requirement 0.4 called the most important line in the document
   (FR-TEN-05) — because the core loop's first job is to make its worst bug
   impossible.
2. **SKIP AHEAD**: tag `part2-ch1`; compose up, migrate, gate + itest
   commands.
3. **WHY #1 (D4 · FR-TEN-05 · constitution I)**: designed out vs tested
   out — vigilance doesn't scale, shapes do; the constitution's own clause
   quoted ("constructors require an environment_id; raw connection access is
   lint-forbidden").
4. **The schema, derived**: SAD §6.1 SQL walked (the environment_id spine
   through every table; DR-01/02/03 constraints as requirements-in-SQL);
   the two gaps decided out loud (applications stub, members from §6.3's
   index). Figure 1: the tables with the tenant spine highlighted.
   Migration fence (001_core_tables.sql).
5. **Migrations as discipline**: forward-only, versioned, no down path
   (constitution quoted); the runner fence (migrate.ts) + client.ts; run it
   twice, second run is a no-op.
6. **The amendment moment**: the api package needs `pg` — and that file is
   published code from 1.4. The diff-fence mechanism introduced explicitly
   (the series' code is immutable except in daylight); package.json
   diff-fence shown and explained. WHY #2 (the fence discipline — why the
   series amends in diffs instead of silently: the reader's typed code must
   remain diffable against the chapters that built it).
7. **The repository layer**: repository.ts fence; what became
   inexpressible (construct without a tenant → type error; forget scoping →
   impossible, the WHERE lives in one home); the admin surface's bright
   line. Figure 2: two Repository instances as two keyed doors into one
   database.
8. **TRAP — the tested-out world**: scoping via WHERE clauses at call
   sites / filtering in handlers; nothing fails until the one forgotten
   filter IS the Sev-0; the eslint diff-fence lands here as the mechanical
   backstop (raw pg outside src/db won't lint).
9. **The isolation suite**: itest lane explained (why *.itest.ts keeps the
   gate Docker-free); repository.itest.ts fence; the attack narrated (A's
   ids against B's repository). Figure 3: the two-lane gate (Docker-free
   lane + compose lane).
10. **FORWARD REF** (2.2 puts the layer under concurrency — the row lock in
    anger; endpoint-level cross-tenant suite with endpoints; CI runs both
    lanes; RLS as a future second belt) + your-turn exercises (comment out
    one WHERE and watch the suite catch it; try importing pg in main.ts and
    watch lint refuse; create a third environment and prove pairwise
    isolation) + takeaways + CHECKPOINT (migrate idempotent, both lanes
    green) + footer.

Battery: WHY 2, TRAP 1, SKIP 1, FWD 1, CHK 1, figures 3.

**Rationale**: The Part 2 formula (capability + the failure it prevents)
shapes every beat; the amendment moment gets narrative weight because it
changes the series' contract with the reader.

**Alternatives considered**: opening Part 2 with the write path and
retrofitting tenancy (docs/07's own ordering rejects it — the spine comes
first).

## R9 — Vietnamese chapter conventions

**Decision**: Naturalized register per the settled glossary and all
corrections to date: "package"/"service"/"schema"/"migration" English,
"cửa ải"+"vượt qua", "bản giao kèo", "tin nhắn", "thêm chi tiết", no
calques/hyphenated compounds/"hình hài"/"thành tiếng"; SQL and identifiers
English; diff-fences byte-identical; figure labels translated;
naturalization self-review before presenting; Dong reviews the chapter AND
the eight seeded vi titles.

## R10 — What stays out (and where it's promised)

**Decision**: Out: endpoints and the write path (2.2), idempotency
enforcement in anger (2.3), message_edits/outbox tables (their chapters),
RLS (noted as a possible later second belt), partitioning (retention
chapter), CI wiring of the lanes (CI chapter), seeding demo data (the
compose seeded-tenant promise lands with tenancy endpoints), Part 3+ manifest
entries.

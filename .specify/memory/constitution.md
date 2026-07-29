<!--
Sync Impact Report
==================
Version change: (template) → 1.0.0
Rationale: Initial ratification. Principles derived from docs/01-product-vision.md (§3
Product principles, §7 Architecture rationale), docs/04-srs.md (constraints CON-01..06,
NFR-SEC, NFR-MNT, NFR-USE), and docs/05-sad.md (drivers D1–D8, ADR-01..12).

Modified principles: n/a (initial adoption — all placeholders filled)
Added sections:
  - Core Principles (7 principles)
  - Technology & Platform Constraints
  - Development Workflow & Quality Gates
  - Governance
Removed sections: none

Templates reviewed:
  - ✅ .specify/templates/plan-template.md — Constitution Check section is generic and
    derives gates from this file at plan time; no edit required.
  - ✅ .specify/templates/spec-template.md — no constitution-specific references; aligned.
  - ✅ .specify/templates/tasks-template.md — no constitution-specific references; task
    categories accommodate testing/observability work required here.
  - ✅ .specify/templates/checklist-template.md — no constitution-specific references.

Follow-up TODOs: none.
-->

# Relay Constitution

Relay is a multi-tenant chat infrastructure platform delivered as an API: real-time
messaging that software companies embed in their own products. This constitution encodes
the non-negotiable decisions the product is willing to be judged on. It binds all
specifications, plans, tasks, and implementations in this repository.

## Core Principles

### I. Tenant Isolation Is a Correctness Property (NON-NEGOTIABLE)

Cross-tenant data exposure is a Sev-0 class of bug, never a configuration mistake.

- No API operation may return, modify, or reveal the existence of data belonging to
  another tenant, under any input (SRS FR-TEN-05 — the single most important requirement
  in the system).
- Every persisted operational and analytical record MUST carry a non-null tenant
  (`environment_id`) identifier, directly or through a single foreign-key hop.
- Data access MUST go through a repository layer whose constructors require an
  `environment_id`; raw connection access outside that layer is lint-forbidden.
  Isolation is enforced in data access, not in handlers.
- An automated cross-tenant access test suite MUST attack every endpoint with foreign
  IDs on every build. A build that fails this suite MUST NOT ship.

**Rationale:** Relay's customers entrust it with their users' conversations. One
isolation failure destroys the trust the entire product is sold on.

### II. No Acknowledged Message Is Ever Lost

Durability is acknowledged, never assumed.

- A send MUST be acknowledged only after the message is durably persisted (ack after
  commit, never before). Fan-out happens after the ack.
- Message ordering within a channel MUST be determined solely by server-assigned,
  strictly increasing sequence numbers — never by client timestamps.
- Every write endpoint MUST accept an idempotency key, enforced at the storage layer
  (unique index), not in application memory — it must survive restarts and work across
  instances.
- Deletions produce tombstones that preserve sequence, author, and timestamps; hard
  deletion exists only on the compliance path.
- State changes and their events MUST commit atomically via the transactional outbox
  (SAD ADR-06). Publish-after-commit without the outbox is forbidden: it silently drops
  events and makes metering drift undetectable.

**Rationale:** Ordering, idempotency, and retry semantics are the product's "boring
where it matters" contract (vision §3.7) — documented precisely, changed rarely.

### III. Two Data Paths, Never Crossed

Operational and analytical storage are physically separate and fail independently.

- Analytical queries MUST NEVER execute against the operational database (PostgreSQL);
  billing, metering, and dashboard analytics read only from the analytical store
  (ClickHouse), fed via a durable queue (SRS CON-01).
- Analytical events are emitted asynchronously — never synchronously on the request
  path. Failure or backlog of the analytical pipeline MUST NOT affect message delivery,
  API availability, or webhook dispatch.
- The analytical store MUST NOT contain message text — only lengths, identifiers, and
  metadata (SRS FR-ANL-11, DR-08).
- Metered totals MUST reconcile against operational counts to within 0.1%, verified by
  a daily job that alerts on breach.
- Operational observability (Prometheus/OpenTelemetry) is kept separate from product
  analytics (ClickHouse): the observer must not share fate with the observed.

**Rationale:** Metering that degrades the product it meters is a design failure. The
independence of the two paths is worth more than pipeline uptime.

### IV. Single Writer, Single Source of Truth

Invariants live in one codebase, not in convention.

- Only the API service writes to PostgreSQL (SAD ADR-04). Sequence assignment,
  idempotency, tenant scoping, and tombstone semantics live behind one repository
  layer. Other services obtain writes and backfill reads via the API service's
  internal endpoints.
- Nothing in Redis is a source of truth: total Redis loss must cause no data loss —
  clients reconnect and resume from cursors. Redis holds only ephemeral state
  (connection registry, presence, rate-limit buckets, caches, pub/sub fan-out).
- The live fan-out fabric is permitted to be lossy (at-most-once) precisely because
  durability and resume live in PostgreSQL sequences and cursors (SAD ADR-07). Any new
  delivery mechanism MUST preserve this recovery property.
- At-least-once delivery on the event spine requires consumer discipline: every
  consumer MUST deduplicate on event `id`.

**Rationale:** Duplicating invariants across services means testing them twice and
breaking them once. One write path, one place to be correct.

### V. API-First, Developer-First

The API is the product; the integrating developer is the user.

- Any UI Relay ships is a reference implementation, never a requirement. The dashboard
  MUST consume the same public API available to customers (except internal billing).
- Docs, error messages, and SDK ergonomics are product features with the same priority
  as message delivery. Every error response carries a machine-readable `code`, a
  human-readable `message`, a `docs_url`, and the `request_id`; every error code has a
  reachable documentation page.
- Time-to-first-message under ten minutes is a product requirement (NFR-USE-01).
  Everything on the signup-to-first-message path gets optimized; changes that lengthen
  it require explicit justification.
- Delegated trust, not shared secrets: customers' backends authorize their own users.
  Relay never stores end-user passwords or credentials of any kind and never becomes an
  identity provider (SRS CON-06).
- Usage is observable, not a surprise: every metered unit is visible in the dashboard
  the moment it is counted.

**Rationale:** Relay competes on API clarity and usage transparency, not feature
breadth (vision §10). The positioning collapses if the API is an afterthought.

### VI. Requirement-Driven, Test-Verified Delivery

Every behavior traces to a requirement; every requirement states how it is verified.

- Requirements carry stable identifiers (`FR-*`, `NFR-*`, `DR-*`, `EIR-*`) that are
  never reused, a priority tied to the phased roadmap, and a verification method
  (test, demonstration, inspection, or analysis). Specs and plans MUST reference these
  identifiers; new behavior without a requirement gets a requirement first.
- Automated test coverage of business logic MUST be at least 70%. Message ordering,
  idempotency, and tenant isolation MUST have 100% branch coverage (NFR-MNT-02).
- The cross-tenant suite (Principle I), dependency vulnerability scans, and the OWASP
  Top 10 scan gate releases: critical findings block ship.
- The quickstart MUST run unmodified, verified by automated execution in CI against
  the published documentation.
- Input is validated against a schema before processing; unknown fields are rejected
  on write endpoints. Secrets, tokens, and message content never appear in logs.

**Rationale:** The SRS is the reference for implementation, test design, and
acceptance. Traceability is what keeps 205 requirements coherent across four phases.

### VII. Boring by Design — Scope Is a Commitment

The correct number of services is the smallest number that still demonstrates real
boundaries (SAD driver D8).

- One language (TypeScript/Node.js) across services, SDK, and dashboard; shared
  protocol types between server and SDK eliminate drift bugs (ADR-01). Introducing a
  second language requires a superseding ADR with profiling evidence.
- New services require justification against the "deliberately not a separate service"
  table (SAD §4.2): same datastore + same transactions + same team ⇒ same service.
- The stated non-goals are commitments, not suggestions: no E2E encryption, no
  voice/video, no native mobile SDKs, no hosted chat app, no identity provision, no
  threads/reactions/search in v1. Scope additions require amending the vision document
  first.
- Every architecture decision is recorded as an ADR stating its drivers, rejected
  alternatives, and reversal condition. ADRs are immutable once accepted; superseding
  requires a new ADR. Disagreement attacks the driver, not the choice.
- Horizontal scalability with no single-instance state: WebSocket connections MUST NOT
  require sticky routing for correctness (SRS CON-02).

**Rationale:** One engineer must be able to run and reason about the whole system.
One named, bounded, monitored scaling wall beats three without names.

## Technology & Platform Constraints

The stack is chosen; deviations require a superseding ADR.

- **Runtime:** TypeScript/Node.js for all services (ADR-01). **Operational store:**
  PostgreSQL 15+. **Analytical store:** ClickHouse 24+ (single node in v1, cluster-shaped
  schema — ADR-08). **Ephemeral state & fan-out:** Redis. **Durable event spine:** NATS
  JetStream (ADR-02). **Dashboard:** Next.js.
- The public REST API is versioned in the URL path (`/v1/...`); breaking changes require
  a new path version and 6 months of parallel support.
- All timestamps are stored and transmitted in UTC, RFC 3339, millisecond precision.
- All external traffic uses TLS 1.2+; all external interfaces are authenticated — no
  unauthenticated endpoint returns tenant data. Secrets are stored only as salted hashes
  or under envelope encryption; data is encrypted at rest in both stores.
- List endpoints use opaque cursor pagination; offset pagination is not offered.
- Deploys to any Kubernetes-conformant environment; no dependency on a single cloud
  provider's proprietary services. The full stack MUST start locally with a single
  command (`docker-compose up`), including a seeded demo tenant.

## Development Workflow & Quality Gates

- **Spec-first flow:** features move through specify → clarify → plan → tasks →
  implement (Spec Kit). Plans MUST pass the Constitution Check gate against this
  document before Phase 0 research and again after design; violations are recorded and
  justified in the plan's Complexity Tracking table or the design is simplified.
- **Phase discipline:** work follows the four-phase roadmap (core loop → platform →
  analytics → developer experience). Each phase has an exit criterion (SRS §7.3);
  P5/deferred items are recorded, not scheduled.
- **Traceability:** PRs reference the requirement IDs they implement. Code review
  verifies compliance with Principles I–VII; reviewers reject unjustified complexity.
- **Migrations:** database migrations are versioned, forward-only, and executable
  without downtime. Each service is independently deployable; deploys cause no message
  loss and at most one client reconnection cycle.
- **Observability from the start:** structured JSON logs with request ID, tenant ID,
  and correlation ID; OpenTelemetry tracing from ingress through datastore;
  Prometheus-compatible metrics. Any customer-reported issue must be traceable from a
  request ID to complete logs and traces within 5 minutes.

## Governance

This constitution supersedes all other development practices in this repository. Where
it conflicts with a spec, plan, or task, the constitution wins; where it conflicts with
the SRS or SAD, the conflict MUST be resolved explicitly by amendment rather than
ignored.

**Amendment procedure.** Amendments are proposed as a PR modifying this file, stating
the motivation, the semantic version bump, and the migration impact on in-flight specs
and plans. Amendments that alter Principles I–IV (correctness properties) additionally
require an updated or superseding ADR in `docs/` demonstrating the drivers changed.

**Versioning policy.** Semantic versioning: MAJOR for principle removals or
redefinitions incompatible with prior guidance; MINOR for new principles or materially
expanded guidance; PATCH for clarifications and wording. The version line below MUST be
updated in the same commit as any change.

**Compliance review.** Every plan runs the Constitution Check gate. Every PR review
verifies the principles most exposed by the change (isolation for data-access changes,
durability for write-path changes, path separation for analytics changes). The
automated gates in Principle VI are enforced in CI and are not waivable by review.

**Version**: 1.0.0 | **Ratified**: 2026-07-29 | **Last Amended**: 2026-07-29

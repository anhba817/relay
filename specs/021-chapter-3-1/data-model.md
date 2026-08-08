# Phase 1 — Data Model: Chapter 3.1

Four tables join the schema, one stub is replaced, and one constraint is added
to an existing table. Everything here sits **above** the environment boundary
except where noted, which is the whole point of the chapter.

> **Provenance.** `docs/05-sad.md` §6.1 defines `environments` and the tables
> below it, but never defines `applications` or any organisation/human table —
> the gap chapter 2.1 stubbed with a recorded DECISION. Every shape on this
> page is therefore a **chapter derivation from the SRS**, not quoted
> specification, and the chapter must present it that way (spec FR-005).

---

## The boundary, restated

```
organisations ─┬─ applications ─── environments ─── [ all of Part 2 ]
               │                                     users · channels
               └─ memberships ─── humans             members · messages
```

Above the line, rows describe *who owns the platform account*. Below it, every
row carries `environment_id` and is subject to the repository's mandatory
scoping (Principle I). The two populations never meet: see ADR-18.

---

## `organisations` (new)

The billing and ownership boundary a person creates by signing up.

| Field | Type | Notes |
|---|---|---|
| `id` | uuid, PK | app-generated, like every other id in the schema |
| `name` | text, not null | taken from the provider profile at signup; no form (FR-TEN-01) |
| `created_at` | timestamptz, not null, default now | |

**Rules**
- Created only by the admin surface, only inside the provisioning transaction.
- FR-TEN-07's roles attach through `memberships`, not here.

---

## `applications` (replaces the 2.1 stub)

A product within an organisation, with independent data, credentials and
quotas (FR-TEN-03).

| Field | Type | Notes |
|---|---|---|
| `id` | uuid, PK | unchanged from the stub, so existing rows survive the migration |
| `organisation_id` | uuid, not null → `organisations(id)` | **new** — the stub had no owner |
| `name` | text, not null | present in the stub |
| `created_at` | timestamptz, not null, default now | **new** |

**Rules**
- An organisation may hold many applications (FR-TEN-03); the chapter builds
  the capability and creates exactly one at signup (FR-TEN-02).
- Deletion (FR-TEN-08) is explicitly out of scope; no cascade is defined here,
  because defining one would imply a deletion story this chapter does not build.

**Migration note**: the stub is a real table with rows created by
`createEnvironment` in Part 2's test runs. `0002_tenancy.sql` alters it rather
than dropping it, and the chapter shows what happens to pre-existing rows.

---

## `environments` (amended)

Unchanged in shape — it already carries `application_id`, `kind`,
`signing_secret`, `retention_days`, `quota_config` from 2.1 — with one
constraint added:

| Constraint | Purpose |
|---|---|
| `UNIQUE (application_id, kind)` | **new.** With the existing `kind IN ('development','production')` CHECK, this caps an application at two environments by construction (FR-TEN-04, R3) |

**Rules**
- Signup creates exactly one, of kind `development` (FR-TEN-02).
- A third environment is impossible, not merely discouraged: the second
  `development` row collides on the unique index.

---

## `humans` (new)

A person who signs in to Relay. **Not** the Part 2 `users` table, which holds
the customer's end users and is environment-scoped (ADR-18).

| Field | Type | Notes |
|---|---|---|
| `id` | uuid, PK | |
| `provider` | text, not null | `github` for the worked example; CHECK constrains the set |
| `provider_account_id` | text, not null | the provider's stable id, never the email |
| `display_name` | text, nullable | whatever the provider granted, nothing more (FR-TEN-01) |
| `email` | text, nullable | nullable on purpose: providers may withhold it |
| `created_at` | timestamptz, not null, default now | |

| Constraint | Purpose |
|---|---|
| `UNIQUE (provider, provider_account_id)` | signup idempotency under concurrency (FR-TEN-01, R5) |

**Rules**
- No `environment_id`, ever. A human belongs to organisations, not tenants —
  the nullable-tenant-column shape Principle I forbids (R2).
- Identity is `(provider, provider_account_id)`, not email: emails change hands
  and providers may not release them.

**DECISION (chapter 3.1): one identity per provider account, and no account
linking.** A person who signs in with GitHub and later with Google becomes two
`humans` rows with two organisations, because nothing ties the two provider
accounts together. Linking them requires a verified-email flow or an
authenticated "add a login" action, both of which need the session this chapter
does not build (research R9). The chapter states this rather than letting a
reader discover it — and the email column is deliberately not used as a join
key, since provider emails are unverified by default.

---

## `memberships` (new)

A human's role in an organisation (FR-TEN-07).

| Field | Type | Notes |
|---|---|---|
| `organisation_id` | uuid, not null → `organisations(id)` | |
| `human_id` | uuid, not null → `humans(id)` | |
| `role` | text, not null | CHECK `role IN ('owner','admin','member')` |
| `joined_at` | timestamptz, not null, default now | |

| Constraint | Purpose |
|---|---|
| PRIMARY KEY `(organisation_id, human_id)` | one role per person per organisation |

**Rules**
- Signup writes exactly one row, `owner`, for the authenticating human.
- Invitations, role changes and removal are deferred (spec Assumptions); the
  chapter names where they land rather than half-building them.

---

## State transitions

Signup is the only transition this chapter defines, and it has two outcomes:

```
provider authenticates a human
        │
        ├─ (provider, provider_account_id) is NEW
        │     └─ one transaction: humans → organisations → applications
        │        → environments(development) → memberships(owner)
        │        all five rows, or none (FR-TEN-02, spec FR-008)
        │
        └─ (provider, provider_account_id) EXISTS
              ├─ holds an `owner` membership
              │     └─ that organisation is returned; nothing is created
              │        (spec FR-010) — the same "recognise, don't duplicate"
              │        shape chapter 2.3 built for messages
              └─ holds only non-`owner` memberships
                    └─ the same transaction minus the humans row — four rows,
                       or none: organisations → applications →
                       environments(development) → memberships(owner). Their
                       existing memberships are untouched. Unreachable until
                       invitations exist, and stated anyway: see
                       contracts/tenancy.md §Provisioning
```

---

## What the model deliberately does not have

- **No sessions table.** No console session exists in 3.1 (R9).
- **No API keys.** Credentials are 3.2's subject; environments keep the
  `signing_secret` 2.1 already gave them.
- **No soft-delete or deletion columns.** FR-TEN-08 needs machinery this
  chapter does not build, and a column that nothing honours is a lie in the
  schema.
- **No `production` environment at signup.** FR-TEN-04 makes two *possible*;
  FR-TEN-02 auto-creates one.

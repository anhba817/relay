# Feature Specification: Tutorial Chapter 3.2 — Keys and Tokens, Two Credentials and One Mistake

**Feature Branch**: `022-chapter-3-2`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "Building part 3 chapter 3.2 english only"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 3.2 and replace the dev-mode seams with real credentials (Priority: P1)

As the tutorial's reader, I open Part 3's second chapter — "Keys and tokens —
two credentials, one mistake" (docs/07 §3) — and the platform stops trusting
its callers. Since chapter 2.2 every request has named its tenant with a header
it simply asserted, and since 2.5 every socket has been opened with a token
signed by a shared development secret. Both were labelled as seams the moment
they were built, with this chapter named as their retirement. Here they go: an
API key resolves the environment instead of a header claiming it, and an
end-user token signed with that environment's own secret opens the socket.

The chapter's title is its lesson. There are exactly two credentials, they are
easy to confuse, and the SRS says so in a design note: confusion between API
keys and user tokens is the most common first-integration failure, and the
error message for presenting the wrong one must name the mistake explicitly.

**Why this priority**: The chapter is the deliverable, and it removes the two
statements the platform currently takes on faith. Every Part 3 chapter after it
authenticates something: outbox events carry a tenant (3.3), webhooks are signed
(3.5), quotas are counted per key (3.6), and the isolation gauntlet (3.7) will
attack exactly the credential checks this chapter installs.

**Independent Test**: A reader at the `part3-ch1` checkpoint can, using only the
chapter: create an environment's first API key and see its secret exactly once,
call the message endpoints with that key and no environment header, mint an
end-user token from the key in a development environment, open a socket with
that token, and watch the platform refuse a key where a token belongs — with an
error that says which credential was expected.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** read end to end, **Then** it
   derives both credentials from the SRS (FR-AUT-01…10), shows what each is for,
   retires both dev-mode seams, and closes in a runnable, tested state.
2. **Given** the format rules (docs/07 §2, code-chapter battery), **Then** the
   chapter passes: 2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, exactly one
   `SKIP AHEAD` naming tag `part3-ch2`, ≥1 forward reference, 2–4 captioned
   figures, takeaways, exactly one closing `CHECKPOINT`.
3. **Given** the chapter's factual claims, **Then** each traces to docs/04
   (FR-AUT-01…12, NFR-SEC-02/06, EIR-API-04), docs/05, the constitution, or an
   earlier chapter; anything the documents do not settle is recorded as a
   chapter decision.
4. **Given** chapter 3.1's published text, which tells the reader "no session —
   that is 3.2's", **Then** this feature corrects that forward reference,
   because the session belongs to the dashboard's chapter and not here (see
   Assumptions).

---

### User Story 2 - The canonical code advances to tag `part3-ch2` (Priority: P2)

As a reader who wants the answer key, the credential machinery exists in
`relay-platform` as the diff from `part3-ch1` to `part3-ch2`: keys with a
prefix and a hash, end-user token verification, the development-only token
endpoint, the authorisation split between the two credential classes, and the
tests that hold them. The `x-relay-environment` header is gone from the code,
not merely discouraged.

**Why this priority**: The tutorial's promise is that code and prose cannot
drift. This increment is what makes the chapter checkable.

**Independent Test**: At `part3-ch2` the Docker-free gate passes; with the
compose stores up every integration lane passes, including a suite that proves
a request with no credential, a revoked key, a wrong-application token and a
mis-signed token are all refused; and `pnpm check:fences` replays every
published chapter onto the repository with no drift.

**Acceptance Scenarios**:

1. **Given** an API key's secret, **When** it is stored, **Then** only a salted
   hash is persisted and the plaintext appears in exactly one response, at
   creation (FR-AUT-02, NFR-SEC-02).
2. **Given** a revoked key, **When** it is presented, **Then** it is refused,
   and the refusal does not depend on any cache expiring (FR-AUT-05).
3. **Given** an end-user token, **When** it is presented, **Then** it is
   accepted only if signed with that environment's secret, unexpired, and
   issued for that application — and its lifetime is at most 24 hours
   (FR-AUT-06/07/08).
4. **Given** a user token on an administrative operation, **Then** it is
   refused: administrative work requires a key (FR-AUT-10).
5. **Given** the existing Part 1–Part 3.1 suites, **Then** they still pass —
   adapted where they used the retired header, unchanged in what they assert.

---

### User Story 3 - The chapter publishes in English, and the site stays honest (Priority: P3)

As a visitor to the tutorial site, chapter 3.2 appears as Part 3's second
published chapter, in English, with the Vietnamese edition marked as not yet
translated rather than silently missing.

**Why this priority**: Publication makes the work reachable; "English only" is
explicit in this feature's input, and the Vietnamese edition follows on its own
cycle as it did for 2.6–2.8 and 3.1.

**Independent Test**: The site builds; the English chapter renders at its
canonical path; the Vietnamese path returns 404 while the listing shows it
untranslated; the fence-chain and docs-drift checks pass.

**Acceptance Scenarios**:

1. **Given** the chapter manifest, **When** 3.2 is published, **Then** its entry
   is `status: "published"` with an empty `translatedIn`, and 3.3–3.7 stay
   `forthcoming`.

---

### Edge Cases

- **No credential at all.** A request with neither key nor token must be
  refused with an error that says which credential the route expects — not a
  generic 401, and never a 500.
- **The wrong credential type.** A key where a token belongs, and a token where
  a key belongs. The SRS calls this the most common first-integration failure
  and requires the message to name it (design note under FR-AUT-12).
- **A key from another environment.** Presenting environment A's key against
  environment B's data must be indistinguishable from data that does not exist
  (FR-TEN-05), not an error that confirms the resource.
- **A token signed with the wrong secret**, or for a different application, or
  with an `exp` more than 24 hours after `iat` (FR-AUT-07/08).
- **A token that expires mid-connection.** An established socket must not be
  torn down because a token aged out (FR-AUT-11).
- **A key presented after revocation**, within seconds, on any instance
  (FR-AUT-05).
- **The very first key.** With no console session in existence, a brand-new
  organisation has no way to authenticate a request for its first key; the
  chapter must say where that key comes from.
- **Secrets in the wrong place.** No credential may appear in a log line, an
  error body, or a URL (NFR-SEC-06).

## Requirements *(mandatory)*

### Functional Requirements

**The chapter (primary deliverable)**

- **FR-001**: The feature MUST produce one published English chapter at
  `part-3/chapter-02`, following the docs/07 §2 code-chapter battery, titled
  and slugged from docs/07's Part 3 table.
- **FR-002**: The chapter MUST distinguish the two credentials by *what they
  authenticate* — an application versus an end user — before showing either
  one's mechanics, since confusing them is the failure the SRS singles out.
- **FR-003**: The chapter MUST show the wrong-credential error message and
  explain what makes it useful: it names which credential was presented and
  which the route expected (SRS design note under FR-AUT).
- **FR-004**: The chapter MUST carry at least one TRAP drawn from a real
  failure met while building it, not a hypothetical one.
- **FR-005**: The chapter MUST state which dev-mode seams it retires, show them
  being removed, and confirm that nothing else in the platform still trusts an
  asserted tenant.
- **FR-006**: The chapter MUST record as explicit DECISIONs anything the source
  documents do not settle — at minimum the key table's shape, the hashing
  choice, and where the first key comes from.

**The code (answer key)**

- **FR-007**: An API key MUST be scoped to exactly one environment, presented as
  a bearer credential, and carry a visible non-secret prefix identifying the
  environment kind (FR-AUT-01, FR-AUT-03).
- **FR-008**: A key's secret MUST be returned exactly once, at creation, and
  persisted only as a salted hash (FR-AUT-02, NFR-SEC-02).
- **FR-009**: An environment MUST support several active keys at once so a key
  can be rotated with no interruption, and revoking one MUST take effect
  immediately on every instance without waiting for a cache to expire
  (FR-AUT-04, FR-AUT-05).
- **FR-010**: End-user tokens MUST be verified against the environment's own
  signing secret, and MUST be refused when expired, malformed, mis-signed,
  issued for another application, or carrying a lifetime longer than 24 hours
  (FR-AUT-06/07/08).
- **FR-011**: In a `development` environment only, an endpoint MUST mint an
  end-user token from a valid API key, so a developer can reach a first message
  before implementing token signing (FR-AUT-09). It MUST be refused in
  `production`.
- **FR-012**: The system MUST distinguish the two credential classes and refuse
  administrative operations presented with an end-user token (FR-AUT-10).
- **FR-013**: Presenting the wrong credential class MUST produce an error that
  names both what was presented and what was expected, in the existing error
  envelope (EIR-API-04).
- **FR-014**: The `x-relay-environment` header MUST no longer determine any
  tenant scope, and the gateway MUST no longer accept tokens signed with a
  shared development secret. The environment MUST be derived from the presented
  credential.
- **FR-015**: The gateway MUST continue not to touch the database (ADR-05);
  whatever it needs in order to verify an end-user token MUST come from the api.
- **FR-016**: An expiring end-user token MUST NOT terminate an established
  connection (FR-AUT-11, first clause).
- **FR-017**: No credential MUST appear in any log line, error body, or URL
  (NFR-SEC-06).
- **FR-018**: Cross-tenant isolation MUST hold under the new credentials: a key
  or token for one environment MUST NOT reveal another's data, and the answer
  MUST be indistinguishable from absent data (FR-TEN-05).
- **FR-019**: The work MUST include automated tests for every refusal listed in
  Edge Cases and every guarantee above, in the appropriate lane, and MUST NOT
  Dockerise or slow the unit lane.
- **FR-020**: All existing suites MUST continue to pass, adapted where they
  relied on the retired header but unchanged in what they assert.

**Publication and fidelity**

- **FR-021**: Every file-content fence MUST byte-match the repository at the
  chapter's tag; amendments MUST use hunked diff fences that apply cleanly to
  the published predecessor state.
- **FR-022**: The chapter MUST be published in English only, with the
  Vietnamese edition marked untranslated; no machine translation is produced.
- **FR-023**: The repository checks (`check:docs`, `check:fences`), the site
  build, and lint MUST pass after publication.
- **FR-024**: Chapter 3.1's forward reference claiming the console session
  belongs to 3.2 MUST be corrected, and any other defect this work reveals in
  an earlier chapter MUST be fixed forward and named in the chapter, following
  the precedent of 2.4, 2.6, 2.7, 2.8 and 3.1.

### Key Entities

- **API key**: An application's credential for one environment. Has a
  non-secret prefix by environment kind, a secret shown once, a stored salted
  hash, a name, a creation time, and a revocation state.
- **End-user token**: A short-lived assertion, signed with the environment's
  secret, that a particular end user is making this request. Carries the user's
  identifier, an issue time and an expiry.
- **Credential class**: Which of the two a request presented — application or
  end user — and therefore what it may do. Administrative operations require
  the former (FR-AUT-10).
- **Environment signing secret**: The per-environment secret, already created
  by 3.1's provisioning, that end-user tokens are signed with and verified
  against.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader starting from the `part3-ch1` checkpoint can follow the
  chapter to a first authenticated message and a first authenticated socket,
  without consulting the source documents.
- **SC-002**: A key's secret is observable exactly once — at creation — and is
  not recoverable from storage afterwards, verified by an automated test.
- **SC-003**: Every refusal in Edge Cases is verified by an automated test: no
  credential, wrong class, foreign environment, expired, mis-signed, wrong
  application, over-long lifetime, and revoked.
- **SC-004**: Presenting the wrong credential class yields a message naming
  both what was presented and what was expected, verified by an automated test
  asserting the text.
- **SC-005**: Revoking a key stops it working on the next request, with no
  waiting period, verified by an automated test.
- **SC-006**: The development-only token endpoint mints a usable token in a
  development environment and is refused in a production one, verified by an
  automated test.
- **SC-007**: No test output, log line, or error body in the chapter's captured
  transcripts contains a key secret or a token — verified by inspection of the
  captured output.
- **SC-008**: Searching the repository for the retired header and the shared
  development secret returns no production code path, verified mechanically.
- **SC-009**: Every factual claim in the chapter traces to a source document, an
  earlier chapter, or a recorded decision, with zero invented requirement,
  table, or column identifiers.
- **SC-010**: The published chapter satisfies every code-chapter battery
  threshold; the fence-chain check reports no drift; all lanes pass and the
  unit lane remains Docker-free.

## Assumptions

- **Scope is one chapter.** Chapter 3.2 only. The outbox (3.3), JetStream
  (3.4), webhooks (3.5) and quotas (3.6) stay `forthcoming`.
- **No console session, and 3.1's promise gets corrected.** 3.1's SkipAhead
  says "no session — that is 3.2's", but docs/07 assigns 3.2 exactly two
  credentials — an API key and an end-user token — and the SAD's context view
  gives dashboard users an OAuth session, which is Part 5's material with
  FR-DSH-01. This feature therefore does not build a human session, and fixes
  3.1's wording forward instead of quietly leaving a promise unmet (FR-024).
  Only the English 3.1 exists, so only it needs the edit.
- **The first key comes from signup.** With no session, a new organisation
  cannot authenticate a request for its first key, so 3.1's provisioning is
  amended to mint one development key and return its secret in the signup
  response — which is exactly FR-AUT-02's "exactly once" and pre-figures
  FR-DSH-01's "development API key on the first screen following signup".
- **Rotation and revocation exist in the layer, not yet on an authenticated
  HTTP surface.** FR-AUT-04/05 are built and tested; the management endpoints a
  human would use need the dashboard's session, so they are named rather than
  half-built — the same treatment 3.1 gave a second application.
- **Deliberately not "a key may mint another key."** That would let a leaked
  credential extend itself, and no requirement asks for it; it is called out as
  a rejected option rather than left unsaid.
- **FR-AUT-11 is honoured in part.** Verification happens at connect, so an
  expiring token cannot terminate an established connection — the requirement's
  first clause holds by construction. Its second clause, supplying a refreshed
  token over the existing connection, needs a protocol frame that does not
  exist (the frame union has no refresh message), so it is deferred with its
  home named.
- **FR-AUT-12 belongs to 3.6.** Rate limiting failed authentication per source
  IP needs the token buckets that chapter builds; it is named, not built.
- **Two environment kinds, two prefixes.** `rk_dev_` and `rk_live_` come from
  FR-AUT-03 verbatim, matching the two environment kinds 3.1 established.
- **Baseline.** Work starts from the current uncommitted `part3-ch1` state.
  Part 2's and Part 3's tags are not yet cut, so this chapter's SKIP AHEAD and
  CHECKPOINT name `part3-ch2` on the same "intended, not yet cut" basis as
  every chapter since 2.2.

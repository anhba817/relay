# Research: Tutorial Chapter 1.3 — The Protocol Package

All Technical Context unknowns resolved.

## R1 — Package shape and the first runtime dependency

**Decision**: `packages/protocol` as `@relay/protocol`, structurally mirroring
`@relay/config` (private, `"type": "module"`, exports `./src/index.ts`,
`typecheck` script, tsconfig extending the base by relative path). **zod** is
added as a dependency *of this package only* — not the workspace root —
pinned to the current stable major at install. Public surface: everything
importable from `@relay/protocol` (schemas, inferred types, code registries);
internal module split `frames.ts` / `codes.ts` / `index.ts`.

**Rationale**: docs/07 §3's row fixes zod by name ("frame types, error codes,
zod schemas"). Scoping the dependency to the package that uses it keeps the
root manifest untouched (additive-only over 1.1's fence) and teaches
dependency locality. Mirroring @relay/config means the chapter spends its
words on the contract, not on package mechanics already taught.

**Alternatives considered**: workspace-root zod (edits a fenced file; also
wrong layering); separate `types/` + `schemas/` packages (premature split —
one home per contract, constitution IV); no runtime validation, types only
(the whole point of the row is that types erase at runtime — rejected by the
chapter's own argument).

## R2 — The wire vocabulary (the derivation table)

**Decision**: The package encodes exactly this vocabulary. Every row cites its
source; rows marked **DECISION** are gaps the documents leave open — the
chapter introduces each with an explicit "the documents don't fix this; we
decide it here and record it" beat (FR-003/FR-010).

| Item | Content | Source |
|---|---|---|
| Envelope | every frame is JSON `{ type, payload }` | EIR-WS-02 |
| `connection.ack` | resolved user identity + resume cursor (+ `resume_ok`) | EIR-WS-03, SAD §5.2 |
| `message.send` | `{ idem_key, channel, text }` | SAD §5.1 |
| `message.ack` | `{ seq }` | SAD §5.1 |
| Event frames (server→client) | six kinds: message created / edited / deleted, membership change, presence change, typing | FR-RTM-05 |
| Event frame type names | `message.created`, `message.updated`, `message.deleted`, `membership.changed`, `presence.changed`, `typing` | **DECISION** (kinds are FR-RTM-05's; the spellings are ours) |
| Resume cursor | per-channel map `{ channel_id: seq }` | ADR-03, SAD §5.2 |
| Backfill truncation | per-channel truncation list carried ON `connection.ack` (`truncated: string[]` of channel ids) — SAD §5.2's sequence sends the ack *after* the backfill response, so the ack already knows; carrier is a **DECISION** (implementation-surfaced), the indicator itself is FR-RTM-04's | FR-RTM-04, SAD §5.2 |
| Idempotency key | client-supplied string; 24 h dedup window server-side | FR-MSG-04 (window), FR-SDK-06 (client-generated) |
| Idempotency key format | non-empty string ≤ 255 chars | **DECISION** (no document fixes a format) |
| Error frame | `error` frame with `{ code, message, docs_url, field? }` — EIR-API-04's full shape incl. the optional `field` | EIR-API-04 (shape), **DECISION** (that WS errors reuse it). `request_id` (constitution V's fourth element) is **explicitly deferred**: no gateway exists to mint request ids on a socket yet — it joins the frame in Part 2 with the gateway, and the chapter says so (reasoned omission, not silent) |
| Close code 4001 | invalid/expired token | EIR-WS-05 |
| Close code 4009 | server shutdown (drain) | SAD §7 |
| Close codes for quota + protocol violation | `4008` quota exhausted, `4002` protocol violation | EIR-WS-06 names the classes; numbers are **DECISION** |
| Ping/pong | native WebSocket control frames, NOT protocol frames (browsers auto-respond; EIR-WS-04's cadence is server config, not vocabulary) | **DECISION** interpreting EIR-WS-04 |
| Presence states | `online` / `offline` | FR-RTM-06 |
| Typing expiry | 5 s, not persisted (documented on the type) | FR-RTM-08 |

**Payload object shapes** (U1 remediation — the fields inside the frames,
same derive-or-mark discipline):

| Payload | Fields | Source |
|---|---|---|
| Message (carried by `message.created` etc.) | `{ id, channel, seq, user, text, created_at }` | derived from SAD §6.1 `messages` columns (id, channel_id, sequence, user_id, text, created_at) |
| Message wire spellings | `channel`/`seq`/`user` for `channel_id`/`sequence`/`user_id` | **DECISION** — follows SAD §5.1's own frame line, which already says `seq` and `channel` |
| Message deferred fields | metadata, attachments, edited_at/deleted_at + tombstone semantics | named Part 2/Part 4 extension points (FR-MSG-07/08 arrive there) — stated in the chapter, not silently absent |
| membership.changed | `{ channel, user, change: "added" \| "removed" }` | **DECISION** (FR-RTM-05 names the kind only) |
| presence.changed | `{ user, state: "online" \| "offline" }` | states FR-RTM-06; envelope **DECISION** |
| typing | `{ channel, user }` (5 s expiry documented on the type per FR-RTM-08) | **DECISION** |

**Scope boundary (stated in the chapter)**: this is the vocabulary 1.4's
walking skeleton and Part 2's core loop consume. Media, moderation, emoji,
and webhook payloads join the package in their own parts.

**Rationale**: Everything above traces or is marked — the ID detector's
spirit extended to the wire. The six event-name spellings follow the
`noun.verb-past` pattern the documents' own `connection.ack`/`message.send`
naming implies.

**Alternatives considered**: inventing a richer envelope (versioned, with
request ids) — deferred; EIR-WS-07 requires documented semantics, not extra
fields, and Part 2 can extend; numbering close codes densely from 4000 —
the two documented codes (4001, 4009) anchor the space, we fill only what
EIR-WS-06 names.

## R3 — Types and schemas cannot drift: schemas are the source

**Decision**: Zod schemas are the single definition; every exported static
type is `z.infer<typeof …>`. The frame union is a zod discriminated union on
`type`; `parseFrame(raw: unknown)` narrows to the union or fails with the
schema error — via zod's `safeParse` result shape (`{ success, data | error }`),
never a throw: hostile input is an expected value, not an exception (the same
philosophy as the suggestions endpoint). No hand-written interface duplicates
a schema, enforced by convention and visible in the fence (there is simply no
second definition to drift).

**Rationale**: The spec's types-vs-schemas edge case dissolves structurally —
same move as 1.1's "one home per rule" and 1.2's volumes-as-documentation:
make the wrong state inexpressible rather than policed. This is also the
chapter's WHY #2: types erase at runtime; schemas are types that survive.

**Alternatives considered**: types first + schema-type equality assertions
(machinery to check what inference gives free); codegen from an IDL (a
maintenance surface ADR-01's deep dive already rejected).

## R4 — The test suite (meaningful, per the 1.1 convention)

**Decision**: Colocated vitest suites. `frames.test.ts`: table-driven — for
each frame schema, a valid specimen parses and round-trips, and a table of
malformed specimens (wrong `type`, missing payload field, wrong primitive,
unknown extra field where strict, negative/zero `seq`, empty `idem_key`)
each *reject*. `codes.test.ts`: the close-code registry contains 4001/4002/
4008/4009 exactly once each with distinct meanings; error codes are unique
and non-empty. Target ≥6 new tests (gate grows 6 → ≥12).

**Rationale**: "Schemas reject malformed frames, not placeholders" (FR-004,
SC-002); tables keep the chapter's test fence short while covering real
cases.

**Alternatives considered**: property-based testing (fast-check — a second
new dependency for marginal teaching value here; Part 2 may revisit when
ordering invariants arrive).

## R5 — English chapter narrative (the beats)

**Decision**: ~2,400 prose words, nine beats:

1. **Cold open — the promise comes due**: 1.1 drew a figure of one package
   feeding gateway, API, and SDK, and called drift "a compile error instead
   of a production incident." Two chapters later the box exists. Contract
   first: define the wire before anything speaks it.
2. **SKIP AHEAD**: tag `part1-ch3`; the gate command.
3. **WHY #1 (contract-first · ADR-01)**: what the shared package buys, with
   the verbatim 1.1/deep-dive quotes; why *before* the services — the
   contract shapes them, not vice versa.
4. **The vocabulary, derived**: walk R2's table narratively — envelope
   (EIR-WS-02 verbatim), handshake ack, send/ack straight from SAD §5.1's
   sequence (quote the frame lines), the six event kinds, cursor and
   truncation from Tuan's resume (SAD §5.2). Each DECISION row gets its
   explicit marker sentence. Figure 1: the frame map by direction.
5. **The first runtime dependency** (zod, pinned, package-local): why types
   alone can't validate (they erase); why ONE validation library for the
   whole workspace. WHY #2 (source: docs/07 §3 · EIR-WS-02): schemas as
   types that survive runtime. The `package.json` fence.
6. **The schemas** — `frames.ts` fence walked: envelope, discriminated
   union, `z.infer` exports, `parseFrame`. Figure 2: the one-source
   mechanism (schema → both runtime validation and static type).
7. **TRAP — validation sprawl**: the naive future (each service re-validating
   with its own library or, worse, trusting `as Frame` casts); the structural
   fix is already built — validation lives where the types live, and
   consumers import both from one place. Includes the `codes.ts` fence.
8. **The tests** — `frames.test.ts`/`codes.test.ts` fences (or the core
   excerpt as one fence each), reject tables highlighted; run the gate.
   Figure 3: the 1.1 payoff figure, revisited — now with the package solid
   and the consumers still ghosted (1.4 un-ghosts two of them).
9. **FORWARD REF** (1.4 walking skeleton consumes this package; the SDK in a
   later part; Part 2 extends the vocabulary) + your-turn exercises (add a
   malformed specimen and watch it reject; try to express a frame type by
   hand and compare with `z.infer`) + takeaways + CHECKPOINT
   (package present, gate ≥12 tests green) + footer.

Battery: WHY 2, TRAP 1, SKIP 1, FWD 1, CHK 1, figures 3.

**Rationale**: Mirrors the proven arc; the derivation table becomes the
chapter's spine so FR-003's discipline is visible on the page.

**Alternatives considered**: teaching zod API-first (library tutorial, not a
systems chapter); deferring the error/close codes to 1.4 (they're vocabulary,
and EIR-WS-06 groups them here naturally).

## R6 — The manifest flip

**Decision**: `lib/tutorial.ts` 1.3 entry: `status: "published"`,
`translatedIn: ["vi"]`, settle placeholders — `readerProduces` "The shared
wire contract — frame types, error codes, and schemas that reject bad input"
+ `readerProducesVi` "Bản giao kèo đường truyền dùng chung — kiểu frame, mã
lỗi, và schema biết từ chối dữ liệu hỏng", `sourceDoc` "docs/04-srs.md,
docs/05-sad.md", `readerMinutes` 90 → 75. Title/titleVi ("Package protocol")/
path unchanged. The 015 suggestions allowlist derives from the manifest —
verification must include an admission check for both new paths (SC-004/006).

**Rationale**: The 014 pattern exactly; 75 minutes — more code than 1.2, no
image pulls.

**Alternatives considered**: none — manifest-only is the mechanism.

## R7 — Vietnamese chapter conventions

**Decision**: Naturalized register per the settled glossary and all standing
corrections: **package** (never "gói"), "cửa ải"+"vượt qua", "bản giao kèo"
(fits this chapter unusually well — the package literally is the contract),
"quả ngọt", "tin nhắn"; frame names/codes/commands English; meaning-first
prose, no hyphenated compounds; byte-identical fences incl. titles;
naturalization self-review before presenting; Dong reads before committing.

**Rationale**: Settled feedback, now with the reader-suggestions channel as
backstop.

**Alternatives considered**: none — register is settled.

## R8 — What stays out (and where it's promised)

**Decision**: Out: service code (1.4), SDK consumption (its own part), media/
moderation/emoji/webhook vocabularies (their parts), REST endpoint schemas
(the API service's chapters), OpenAPI (EIR-API-07, P4), property-based tests
(revisit with Part 2 invariants), protocol documentation site page (EIR-WS-07
is satisfied progressively by the chapters themselves for now).

**Rationale**: Docs/07's row scope; every exclusion named in the chapter's
forward reference or exercises rather than silently absent.

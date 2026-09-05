# Relay — Platform Implementation Review

**Review refreshed:** 2026-09-05
**Scope:** Current `docs/` requirements and `relay-platform` at `part3-ch24` / `main`.

## Summary

The recent chapters materially closed the main issues found in the 2026-09-03 review:

- The five-slot connection cap is implemented and its architecture documentation is now reconciled (ADR-23).
- Message editing, tombstoning, revision history, and real-time revision events are implemented.
- The P2 external-URL half of attachments is implemented, including a ten-attachment limit.

The core loop is therefore appreciably closer to the SRS. The main remaining product gaps are the still-deferred self-service/dashboard surface, analytics, hosted media, emoji packs, SDK, and compliance lifecycle features. This review also found four implementation defects or contract gaps worth addressing before further feature work.

`pnpm typecheck` passed across all nine workspace packages during this review.

## Current findings

| Priority | Finding | Evidence and impact |
|---|---|---|
| High | **The public WebSocket schema does not enforce the 8,000-character message limit.** | REST and internal API schemas cap text at 8,000 characters, but `packages/protocol/src/frames.ts` accepts `z.string()` for the browser-facing `message.send` frame. The API eventually rejects an over-long message, but only after the gateway has parsed it and made an internal request. This makes the published client contract incomplete and validates untrusted input one hop late. This is documented as 3.24-2 in `specs/042-chapter-3-24/gaps.md`. Export one text-limit constant and apply it to all three entry schemas. |
| High | **User avatar URLs accept executable and non-web schemes.** | `services/api/src/users/users.schema.ts` uses Zod's generic `.url()`, which accepts `javascript:`, `data:`, `file:`, and `vbscript:`. Relay stores and returns the value for customer clients to render. Restrict the scheme to `https:` (or explicitly approved `http:` plus `https:`), using the same parsed-scheme validation introduced for attachments. See 3.24-1 in `specs/042-chapter-3-24/gaps.md`. |
| Medium | **Five customer-caused webhook validation failures are labelled `internal_error`.** | `services/api/src/webhooks/webhooks.service.ts` throws bare `UnprocessableEntityException`s for malformed, non-HTTPS, private-address, or empty-event-set endpoint configuration. The global error filter maps these 422 responses to `internal_error`, incorrectly telling the customer that Relay failed. Return a specific protocol error code and document it. See 3.24-3 in `specs/042-chapter-3-24/gaps.md`. |
| Medium | **Webhook subscriptions accept event types that Relay never emits.** | `assertEventTypes` checks only that `event_types` is a non-empty array; it does not compare values with `OUTBOX_EVENT_TYPES`. A typo, such as `mesage.updated`, succeeds and produces a permanently silent endpoint. Validate at create/update time and decide how to handle existing invalid rows. See 3.23-1 in `specs/042-chapter-3-24/gaps.md`. |
| Medium | **WebSocket close-code documentation remains incomplete.** | EIR-WS-06 requires documented, distinguishable authentication, quota, shutdown, and protocol failures. The error reference documents only the protocol-violation and connection-limit cases; 4003 (banned) is undocumented, while 4001, 4008, and 4009 are scattered or absent from published customer documentation. Extend the documentation checker to compare `CLOSE_CODES` with the error reference. See 3.23-8 in `specs/042-chapter-3-24/gaps.md`. |
| Medium | **The advertised docker-free unit lane depends on Redis.** | `services/gateway/src/connections.test.ts` calls the real Redis-backed connection registry although it is a `.test.ts` unit file. With containers stopped, the cap correctly fails open but the test suite reports functional failures. Move this suite to the integration lane or replace Redis with a true unit double. See 3.23-9 in `specs/042-chapter-3-24/gaps.md`. |
| Medium | **The integration/e2e test lanes are not reliably isolated.** | The e2e harness kills child processes and sleeps for 200 ms rather than awaiting exit, which leaves fixed ports occupied; the chapter measured failures in 10 of 20 runs. The dispatcher lane also leaves durable consumers and delivery rows behind, so repeated runs accumulate backlog until later tests starve. These are test-system defects, but they undermine the evidence used to claim product correctness. See 3.24-4 and 3.24-5 in `specs/042-chapter-3-24/gaps.md`. |
| Medium | **Concurrent edit/delete ordering is neither serialised nor tested.** | Edit and delete read then update without a row lock. Both operations eventually tombstone the message, but clients can receive `message.updated` and `message.deleted` in either order and temporarily render edited text after deletion. Decide whether history re-read is an acceptable repair or serialize mutations with `FOR UPDATE`; add a forced-race test. See 3.23-3 in `specs/042-chapter-3-24/gaps.md`. |
| Medium | **Moderation audit logging is still absent.** | The tombstone records `metadata.deleted_by`, satisfying deletion metadata, but there is no immutable audit log carrying actor, action, target, timestamp, and request ID. The stored remover is not exposed by a supported read path. FR-MOD-03 remains unimplemented. See 3.23-2 in `specs/042-chapter-3-24/gaps.md`. |
| Medium | **Migration metadata is behind the actual migration directory.** | Drizzle snapshots stop at `0007`, while migrations through `0014_message_edits.sql` are hand-written. `drizzle-kit generate` therefore proposes colliding or stale migrations. Either regenerate snapshots or explicitly retire the generate workflow and keep reviewed handwritten migrations. See 3.23-6 in `specs/042-chapter-3-24/gaps.md`. |
| Roadmap | **Self-service tenancy/key management and dashboard remain absent.** | OAuth signup exists, but public organisation/application/API-key management and the dashboard are not present; the README still directs local users to a seed script. FR-TEN-03/07/08, key lifecycle work, and FR-DSH remain deferred. |
| Roadmap | **Analytics, compliance lifecycle, hosted media, emoji packs, SDK, and reference client remain absent.** | ClickHouse exists only in Compose; no ingester, analytical schema/client, request log, reconciliation job, media storage/scan pipeline, emoji-pack data model, SDK, or reference client exists. These are mainly scheduled Phase 3–4 scope, rather than regressions. |
| Roadmap | **A complete public protocol reference and OpenAPI document are still absent.** | EIR-WS-07 remains unmet. EIR-API-07 is a Phase 4 requirement, but a published API/protocol contract should precede dashboard and SDK development. |

## Verified improvements since the prior review

| Prior finding | Current status |
|---|---|
| Redis slot-cap documentation was stale | Closed: `docs/05-sad.md` now describes `conn:{env}:{user}:{slot}` and ADR-23. |
| FR-MSG-07/08 edit and deletion support was absent | Closed: migration `0014_message_edits.sql`, message edit/delete endpoints, revision history, outbox events, and gateway delivery now exist. |
| FR-MSG-11 external attachments were absent | Closed for the P2 external-URL arm: shared attachment schemas enforce allowed schemes and the maximum of ten. Hosted `media_id` attachments correctly report that hosted media is not available yet. |

## Recommended order

1. Fix the public-boundary defects: WebSocket text limit, avatar URL schemes, and webhook 422 error codes.
2. Make webhook configuration trustworthy by validating event types and complete close-code documentation.
3. Restore trustworthy verification: await e2e child exit, clean dispatcher resources, and move Redis-dependent tests out of the docker-free unit lane.
4. Resolve the migration metadata decision before the next schema change.
5. Build the P3 foundation in order: immutable audit/compliance lifecycle, analytics, then hosted media and emoji packs.
6. Deliver dashboard, public API/protocol reference, and SDK as one self-service integration milestone.

## Part 3 SRS/SAD/ADR amendment assessment

**Reviewed:** 2026-09-05
**Source:** `/tmp/claude-1000/-home-dong-work-relay/3bfc1c57-63b8-4e6e-85eb-2bc90373f93b/scratchpad/part3-doc-amendments.md`

Part 3 made mostly sound implementation-led corrections: it reconciled the REST error
envelope, separated platform humans from tenant end users, added the real-time fabrics and
connection cap, introduced attributable bot senders, and documented revisions and attachments.
Marking superseded ADR text rather than silently rewriting history is particularly good
governance practice.

The following amendments or decisions need reconsideration.

| Concern | Assessment and recommendation |
|---|---|
| **Membership revocation can take 60 seconds after fabric loss.** | ADR-20 explicitly permits the periodic membership reread to exceed FR-RTM-10's five-second removal promise by 55 seconds. Describing the reread as a cursor explains recovery, but does not satisfy the authorization requirement. Make revocation durable, fail closed when authorization is uncertain, or explicitly amend the SRS with a degraded-mode bound. |
| **Typing expiry is assigned to uncontrolled clients without a complete client contract.** | ADR-22's renewal-over-stop design is technically defensible, but FR-RTM-08 reads as a server obligation. Until an SDK or public protocol reference specifies it, clients can leave typing indicators visible forever. State explicitly that receivers expire each `(channel, user)` indicator after five seconds. |
| **Missed revisions have no observable repair trigger.** | The SAD says a disconnected client can miss an edit/deletion for an old message without a sequence gap, and history is the repair. A client has no reason to initiate that repair. Add a revision cursor/version watermark, include revisions in resume, or require a bounded reconciliation pull. |
| **The five-connection cap fails open.** | ADR-23 allows a user to exceed five connections when Redis is unavailable, while FR-RTM-09 says users are permitted up to five. This is acceptable only as an explicitly best-effort availability control. If the cap is contractual, abuse-prevention, or billing-related, enforcement must fail closed. |
| **Bot sends bypass quota exhaustion.** | The 3.17 bot amendment permits bot sends after ordinary sends are rejected at quota exhaustion. Because customers control bot creation, this can defeat FR-RTL-06/08's cost-control intent. Apply a separate bot cap or an organisation-wide hard cap. |
| **One subject grammar per real-time kind is becoming a default rather than a measured decision.** | ADR-19→24 preserve payload compatibility well, but add subscriptions, Redis clients, recovery paths, and operational complexity per event kind. NFR-SCL-01 remains unmeasured. Define a threshold for consolidating typed envelopes or introducing a versioned event bus before adding another fabric. |
| **ADRs are duplicated across two manually maintained documents.** | Maintaining summaries in the SAD and deep dives in the ADR document creates drift risk. Keep a single authoritative ADR and link to it, or generate the SAD index from the ADR source. |
| **The SRS revision ledger is misordered.** | Versions 1.7, 1.6, and 1.5 appear in reverse order. Correct the table and add a checker for ordered revision entries. |

The strongest Part 3 decisions are ADR-18's identity separation, ADR-21's isolated typing
grammar, ADR-23's slot-key registry rather than a TTL-broken set, and the attachment
discriminated union. The broader recommendation is to define one explicit contract for
lossy real-time delivery and recovery: messages have an observable repair path today;
membership, typing, and revisions do not all have one.

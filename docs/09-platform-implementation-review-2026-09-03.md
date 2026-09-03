# Relay — Platform Implementation Review

**Review date:** 2026-09-03  
**Scope:** `docs/` requirements and architecture documents compared with the current `relay-platform` implementation.

## Summary

The core messaging platform is substantially implemented, including membership updates,
presence, typing, quotas, webhooks, and the five-connection cap. However, the repository is
not yet a full implementation of the SRS: most Phase 3–4 product surfaces are absent, and
several P2 obligations remain incomplete.

`pnpm typecheck` passed across all nine workspace packages during this review.

Phase 3–4 omissions below are roadmap gaps, not necessarily regressions. The P2 and
documentation inconsistencies should be prioritised because they prevent the documented
self-service product journey from working end-to-end.

## Findings

| Priority | Finding | Evidence and impact |
|---|---|---|
| High | **Architecture documentation is stale about the connection cap.** | `docs/05-sad.md` says `conn:{env}:{user}` is “not built” and proposes a sorted set. The gateway now implements and wires a five-slot Redis registry in `services/gateway/src/connections.ts` and `services/gateway/src/main.ts`. Update the SAD service/data views and add the superseding ADR. |
| High | **Message editing and deletion are missing.** | FR-MSG-07/08 require immutable edit history and tombstones. `services/api/src/messages/messages.controller.ts` exposes only `POST` and `GET`; there is no `message_edits` table or edit/delete route. This also blocks FR-MOD-01/02. |
| High | **Attachments are missing, including already-P2 external URLs.** | FR-MSG-11 requires up to ten external or hosted attachments. `services/api/src/messages/messages.schema.ts` accepts only text, metadata, idempotency key, and sender; it has no `attachments` field. |
| High | **The documented self-service onboarding path is incomplete.** | OAuth signup exists, but no public organisation, application, or API-key-management controller exists. The platform README says public organisation creation and key minting do not exist and provides a seed script instead. FR-TEN-03/07/08, FR-AUT-01→05, and FR-DSH-01 are therefore incomplete for real users. |
| Medium | **REST and WebSocket sends cannot reliably share an idempotency key.** | REST constrains `idempotency_key` to UUIDs, whereas WebSocket accepts any 1–255-character key. A client switching transport cannot necessarily reuse a key for one logical send, weakening the cross-transport meaning of FR-MSG-04. This is recorded in `specs/036-chapter-3-18/gaps.md`. |
| Medium | **The public protocol contract is undocumented.** | EIR-WS-07 requires complete wire-protocol documentation. The recorded gap in `specs/039-chapter-3-21/gaps.md` confirms no published protocol reference exists; `/health` advertises only frames and close codes. OpenAPI is also absent, leaving EIR-API-07 unmet. |
| Medium | **Analytics is infrastructure-only, not implemented.** | ClickHouse is defined in `compose.yaml`, but there is no analytics ingester, ClickHouse schema/client, request log, reconciliation job, or analytical query API. FR-ANL-01→11 remain unimplemented. |
| Medium | **Compliance and lifecycle operations are absent.** | No audit-log, export, retention-worker, or privacy-erasure implementation/table exists. This leaves FR-MOD-03→06 unmet and makes retention promises unverifiable. |
| Medium | **Emoji packs and hosted media are entirely deferred.** | There are no emoji/media tables, routes, storage client, scan worker, signed-URL flow, or resolution-map support. This is consistent with Phase 3 scope, but FR-EMJ-03→10 and FR-MED-01→12 should be tracked explicitly as planned. |
| Medium | **No dashboard, SDK, or reference client exists.** | The workspace contains services and internal packages only; it has no dashboard, SDK, or reference-client package. This leaves FR-DSH and FR-SDK unmet. The dashboard is also the intended self-service key-management surface. |
| Low | **The integration lane is not reliable from a cold JetStream volume.** | `specs/039-chapter-3-21/gaps.md` records that the stream may be created as an incidental side effect, allowing the first clean-volume integration run to fail before a rerun passes. Add explicit stream initialisation to the test-lane bootstrap. |

## Recommended order

1. Reconcile the SAD and protocol/API documentation with the shipped 3.22 gateway implementation.
2. Complete the P2 public-product gaps: attachments, edit/delete/moderation, tenant/key lifecycle, OpenAPI, and the protocol reference.
3. Build the analytics and compliance foundation before media and emoji, because both depend on it.
4. Deliver dashboard and SDK together with self-service onboarding, replacing the seed-script-only journey.


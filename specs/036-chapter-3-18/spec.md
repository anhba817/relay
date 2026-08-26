# Feature Specification: chapter 3.18 — the message that never arrived

**Feature directory**: `specs/036-chapter-3-18/`
**Created**: 2026-08-26
**Status**: in planning
**Predecessor**: `specs/035-chapter-3-17/` (chapter 3.17, the sender a message never had)

## Summary

A customer's server sends a message over REST. A member of that channel is connected to a
socket. The message does not arrive.

Chapter 3.12 recorded this and named **two** independent mechanisms. Chapter 3.17 removed one —
every message now carries a sender, so the backfill has no reason to drop it, and **a resume
now delivers a REST-sent message**. The other mechanism stands: the api publishes to no
fan-out, so nothing arrives *live*. This chapter is that publish.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — a REST-sent message reaches a connected member (Priority: P1)

A customer's build server posts to `POST /v1/channels/:channelId/messages`. A teammate has the
app open, is a member of that channel, and is connected to a socket. The message appears
without the client polling, refetching, or reconnecting.

**Independent test**: send over REST as a bot; watch a `message.created` frame arrive on a
socket that was already open.

### User Story 2 — it works when the sender and the recipient are on different instances (Priority: P1)

Two gateway instances. The recipient's socket is held by one; the api that accepted the REST
send has no relationship with either. The message arrives.

**Independent test**: two gateway processes, a member connected to each, one REST send — both
receive it.

### User Story 3 — a message does not reach somebody who may no longer see it (Priority: P2)

A user is removed from a channel. A message is sent to that channel seconds later. It does not
appear on their socket.

**Independent test**: remove a member over the public route, send, and assert nothing arrives on
their open socket within the clause's window.

### Edge cases

- **A recognised idempotent retry must not deliver twice.** The gateway's own publisher already
  refuses this; the api's must too, and the reason is the same — storage safety is not delivery
  safety.
- **A send whose channel has no connected member** publishes to a subject nobody is subscribed
  to. That frame is gone, and that is correct rather than a loss.
- **A send that is refused** — banned sender, archived channel, quota exhausted, a key naming a
  person — must publish nothing. Nothing that did not commit may be delivered.
- **Redis is unavailable.** The send must still succeed. Delivery is not durability, and
  refusing a paying customer's write because a cache is down is the failure direction chapter
  3.8 already decided against.
- **The same user on several connections** must receive the message on each of them.
- **A legacy senderless row** cannot be delivered live any more than it can on resume: the frame
  contract requires a sender. Nothing new produces one, so this is a statement rather than a
  path.

## Requirements *(mandatory)*

### The clause this chapter is about, and the one the plan named

- **FR-001**: The plan's row names **FR-RTM-05** ("shall emit real-time events for message
  creation, edit, deletion, membership change, presence change, and typing"). The clause more
  directly unmet is **FR-RTM-01**: *"A connected client shall receive messages for every channel
  of which it is a member, without per-channel subscription."* P1, verification by test. A
  REST-sent message reaching no connected member is a violation of FR-RTM-01 today, and the
  chapter MUST cite the clause it actually satisfies.
- **FR-002**: **No SRS amendment is required, and the chapter MUST say so.** Unlike chapter
  3.17, whose gate was an amendment, both the requirement and the design already exist:
  FR-RTM-01 and FR-RTM-02 are P1 clauses, and `docs/05-sad.md` line 138 already draws
  `api -- "publish fan-out" --> redis`. This chapter builds a documented edge that was never
  built, and that is a different kind of gap from a missing clause.
- **FR-002a** *(added during analysis)*: **The SAD does require amending, and the chapter MUST
  not conflate that with the SRS.** `docs/05-sad.md` says two different things about who
  publishes. Line 138's component diagram gives the edge to the api; §5.1's sequence diagram
  ten lines above the ordering bullet draws `G->>G: publish to Redis chan:{channel_id}` — the
  gateway — and models no REST send at all. The bullet beneath it, *"The Redis fan-out happens
  after the ack"*, is stated unconditionally and this feature makes it false for one of two
  transports (FR-005).

  So the amendment `docs/05-sad.md` needs is: a REST send sequence in §5.1, and the ordering
  bullet split the way FR-005 splits it. `05-sad.md` is mirrored into
  `relay-tutorial/content/docs/` and `check-docs-drift.sh` fails on divergence, so the edit is
  not complete until `pnpm sync:docs` has run.

  **FR-002's claim survives, narrowed to what it always meant**: no *SRS* clause is added or
  changed, and principle VI is satisfied by citation of FR-RTM-01. What the first draft of
  FR-002 got wrong was reading line 138 and concluding the document agreed with itself.
- **FR-003**: The chapter MUST state what FR-RTM-05's other five event kinds do, because a
  reader will ask. Measured: `message.updated` and `membership.changed` have **zero** producers
  outside tests, nothing writes `messages.edited_at` or `messages.deleted_at`, and typing has no
  frame in the union at all. Only message creation is producible, so only message creation can
  be delivered.

### The publish

- **FR-004**: A message accepted over the public REST route MUST be published to the channel's
  fan-out subject after the write commits.
- **FR-005** *(AMENDED during analysis — the original clause was not achievable on this
  transport)*: The publish MUST happen **after the write commits**. `docs/05-sad.md` states the
  ordering: *"Ack after commit, never before (FR-MSG-05). The Redis fan-out happens after the ack;
  a recipient may see the message milliseconds after the sender's ack, never before durability."*

  That sentence was written when a socket was the only way in, and a socket can perform it: the
  gateway writes an ack frame and *then* awaits the publish, because it has two channels. **A
  request handler has one.** On REST the response *is* the acknowledgement, so anything the
  handler awaits necessarily precedes it, and "after the ack" is not a sequence the transport can
  produce — only a detached publish could, and detaching removes the failure from anywhere a test
  or an operator can see it synchronously (FR-011).

  So the clause splits by transport, and what it protects survives both readings:

  - **Socket path** (unchanged): commit, ack, publish.
  - **REST path**: commit, publish, respond. A recipient may see the message before the sender's
    `201`, and never before durability — which is the guarantee the original sentence names.

  The cost, recorded rather than hidden: **NFR-PRF-01's clock — "send acknowledged to recipient
  receipt" — is not measurable on the REST path**, because the interval can be negative. It stays
  measurable on the socket path. The publish instead lands inside NFR-PRF-02's budget (REST write
  latency, p95 < 150 ms), which is why the publish must be measured rather than assumed cheap.
- **FR-006**: A message accepted over the **internal** route (a socket send, forwarded by the
  gateway) MUST NOT be published twice. The gateway publishes for that path today, and two
  publishers on one path put the same message on every member's screen twice.
- **FR-007**: A recognised idempotent retry MUST publish nothing. It wrote no row.
- **FR-008**: A send that is refused MUST publish nothing.
- **FR-008a** *(added during analysis)*: **A send refused because the channel belongs to another
  tenant MUST publish nothing, and this case MUST be tested by observing the subject rather than
  the response.** Constitution I is NON-NEGOTIABLE and its clause 1 forbids revealing the
  existence of another tenant's data *"under any input"*; clause 4 mandates a suite that attacks
  every endpoint with foreign IDs on every build.

  That suite exists and it cannot see this. `POST /v1/channels/:channelId/messages` is isolation
  target `targets.ts:185`, and the gauntlet's oracle compares **responses** — its own comment says
  the point is *"that nothing of the victim's came back, not that a status was 4xx."* A publish is
  a second output channel, so a frame emitted onto a foreign tenant's subject would leave every
  existing test green.

  The other four refusal kinds — a banned sender, an archived channel, an exhausted quota, an
  application key naming a person — are covered by FR-008. This one is separated because it is the
  Sev-0 class and because its observer is different.
- **FR-009** *(narrowed during analysis — the first wording asked for something no client can
  observe)*: The frame delivered MUST be **indistinguishable to a client** from one a socket send
  produces. A client cannot tell which entrance a message used, and `messageSchema` is the contract
  that makes that true.

  The first wording said *"byte-compatible"*, and the api's bytes never reach a client:
  `session.ts:45` is `socket.send(JSON.stringify(frame))`, so the fan-out payload is parsed on
  receipt, validated, rewrapped in a frame and re-serialized by the gateway. **Field equality is
  sufficient precisely because the gateway rebuilds the bytes** — which is worth stating rather
  than leaving a stronger claim that nothing tests and nothing depends on.

### Failure, and what it must not take down

- **FR-010**: A fan-out publish that fails MUST NOT fail the send. The row is committed and
  acknowledged; delivery is best-effort by construction, and the SAD says so: *"Redis lost →
  presence + fan-out pause"*.
- **FR-011**: A publish failure MUST be observable — logged at `error` level with the channel, the
  message, the **request id and the tenant id**. A silent drop is the defect this chapter exists to
  remove, reintroduced one layer down.

  The request and tenant ids are NFR-OBS-01's requirement (*"structured JSON logs including
  request ID, tenant ID, and correlation ID"*) and they are what NFR-OBS-06's five-minute
  traceability runs on. The gateway's equivalent line omits them because the gateway is not in a
  request; the api is, so copying that shape would carry an omission past the point where it was
  justified.

  **The log line is the whole of the observability, and the first draft of this clause implied
  more.** It said *"at a level an operator's alerting can find"*, which reads as a metric — and the
  api has no Prometheus dependency, so NFR-OBS-03's metrics do not exist there to emit one. An
  alert on this would be a log-level rule, and the chapter should not imply a counter that cannot
  fire.
- **FR-012**: The chapter MUST state what a client can and cannot conclude from having received
  nothing. A missing frame is not evidence a message does not exist; the resume path is the
  guarantee, and the fan-out is the optimisation.

### Membership at delivery

- **FR-013**: **FR-RTM-10** requires that events not reach a client whose membership no longer
  grants access, *"effective within 5 seconds of the membership change"*. Making REST sends
  deliver puts a second path under that clause. The chapter MUST establish where membership is
  checked for a REST-originated frame and MUST NOT assume the socket path's answer covers it.
- **FR-014**: A private channel's message MUST NOT reach a non-member's socket, by the same
  reasoning chapter 3.15 applied to the read paths. The delivery path is a fourth door onto
  FR-CHN-05 and MUST be tested as one.

### What this chapter closes, and what it does not

- **FR-015**: Chapter 3.12's `gaps.md` G1 MUST be closed rather than amended again. Chapter 3.17
  amended it from two mechanisms to one; this chapter removes the last one. A gap that has been
  half-closed twice and never closed is a record nobody trusts.
- **FR-016**: Chapter 3.14's Phase 2 verdict MUST be re-examined. Its concrete half was that an
  outsider who sends over REST and waits on a socket cannot succeed and no document says so.
  This chapter makes the attempt succeed; the chapter MUST state whether the verdict is
  satisfied or whether its documentation half remains.
- **FR-018** *(added during analysis)*: **Published chapters state this chapter's subject as
  permanent, and those sentences MUST be corrected.** A sweep of the published corpus found four
  classes of site:

    - `part-3/chapter-13`'s `<Trap title="A message sent over REST reaches no socket, **ever**">`,
      whose body reads *"Nothing in the api publishes to the gateway's fan-out"* — and its
      Vietnamese twin, *"không bao giờ tới được"*.
    - **Part 3's closing paragraph** in `part-3/chapter-16`: *"a REST-sent message still reaches no
      socket and FR-RTM-05's chapter owns that decision"* — present tense, and repeating the
      FR-RTM-05 misattribution FR-001 corrects to FR-RTM-01.
    - `packages/outsider/src/integrate.itest.ts:233`, a test **titled** *"receives a message on a
      socket — SENT over the socket"*, whose comment calls the fan-out *"the half that remains"*.
    - Comments in `fanout.ts`, `public-surface.itest.ts` and `isolation.itest.ts`, all in files
      chapters fence, which makes them published prose.

  **The distinction is tense and attribution.** A sentence saying what *is* the case goes false; a
  sentence saying what a chapter *recorded* stays true — 3.17's *"Chapter 3.12 recorded that a
  REST-sent message reaches no socket"* needs no change, and 3.14's verdict is a gap record. Only
  the present-tense and permanent claims are in scope.

  This is `gaps.md` item 8's artifact class: no checker reads prose, and a published Trap
  contradicting 3.17's own chapter survived fifteen analysis passes there and nine here.
- **FR-017**: Presence is **not** in scope. FR-RTM-06 and FR-RTM-07 are chapter 3.19, and
  FR-CHN-05's third verb stays unbuilt. The chapter MUST say so rather than leaving a reader to
  infer it from silence.

### Key Entities

- **The fan-out subject** — `chan:{channelId}` today, published by the gateway and subscribed by
  every gateway instance. This chapter adds a second publisher; it introduces no new subject and
  no new frame type.
- **A published frame** — a `message.created` payload conforming to `messageSchema`. Not a new
  entity; the same one the socket path already puts on the wire.

## Success Criteria *(mandatory)*

- **SC-001**: A member with an open socket receives a message sent over REST, with no client
  action in between.
- **SC-002**: The same holds when the sender's api and the recipient's socket are on different
  instances.
- **SC-003**: A socket-originated send delivers exactly once, verified by count rather than by
  observing that a message arrived.
- **SC-004**: A refused send, and a recognised retry, each deliver nothing.
- **SC-005**: With the fan-out unavailable, a REST send still returns 201 and the message is
  readable from history.
- **SC-006**: A user removed from a channel receives no message sent after the removal, within
  FR-RTM-10's five seconds.
- **SC-007**: A non-member's socket receives nothing from a private channel.
- **SC-008**: A client cannot distinguish a REST-originated frame from a socket-originated one.
- **SC-009**: Chapter 3.12's G1 is closed, and this feature's traceability map cites FR-RTM-01
  and FR-RTM-02 in both directions.
- **SC-010**: The sealed outsider sends over REST, waits on a socket, and succeeds — the exercise
  chapter 3.14 recorded as impossible.
- **SC-011**: The chapter is inside the series' 2,000–4,000 prose-word bound, and every fenced
  file replays onto the platform repository.

## Assumptions

- **The fan-out subject and the frame stay as they are.** No new subject, no new frame type, no
  change to `messageSchema`. A published client tolerates neither, and chapter 3.17's frame-shape
  assertion is what holds it still.
- **The api already reaches Redis.** `services/api/src/limits/store.ts` uses it for rate
  limiting, so this is not a new dependency — measured, not assumed.
- **The publish happens on the send path, not in the outbox consumer.** The SAD draws
  `api → redis` directly and specifies the ordering relative to the ack. The consumer's handler
  is `createRecorder`, which records; moving delivery there would add the outbox relay's latency
  to every message and contradict a drawn edge. The plan may revisit this with a measurement,
  but the architecture document is the default.
- **Best-effort delivery is the existing contract**, not a compromise introduced here. The
  gateway's own comment says a frame that misses a subscriber "is simply gone", and the resume
  path is the guarantee.
- **The lane environment is the one chapter 3.17 recorded**: Postgres on 15432, the two internal
  credentials, NATS on 4222, and the compose `services` profile stopped.

## Dependencies

- **Chapter 3.17 is closed** (tagged `part3-ch17`). Every message carries a sender, which is what
  makes a REST-sent row deliverable at all — the frame contract requires one.
- **Chapter 3.12's gap record** is the thing being closed, and it has already been amended once.
- **Chapter 3.14's Phase 2 verdict** is the outsider criterion this chapter is measured against.
- **`docs/05-sad.md` and its mirror** (added when FR-002a was written). The amendment is not
  complete until `pnpm sync:docs` has copied it to `relay-tutorial/content/docs/05-sad.md`;
  `check-docs-drift.sh` fails on divergence and reads drift rather than validity, so it will not
  say which of the two files is right.
- **`relay-tutorial/lib/tutorial.ts`** holds exactly the shipped chapters — 34 entries, all
  `status: "published"`. Without a 3.18 entry the chapter does not route and is not among the
  static pages.

## In scope beyond the publisher

Named here because FR-002a widened the work after the first checklist pass, and "scope is clearly
bounded" is a claim that has to keep being true:

- **A `docs/05-sad.md` amendment and its re-sync.** The SAD disagrees with itself about who
  publishes; `:138` gives the edge to the api and `:248` draws `G->>G`. See FR-002a.
- **A `relay-tutorial/lib/tutorial.ts` entry**, with both Vietnamese fields.
- **No SRS amendment.** That distinction is the whole point of FR-002 and FR-002a standing
  together.
- **Corrections to published chapters' prose**, in both locales — a Trap, Part 3's closer, and
  four fenced-file comments. See FR-018.

## Out of scope

- **Presence** (FR-RTM-06, FR-RTM-07, FR-CHN-05's third verb) — chapter 3.19.
- **Typing indicators** (FR-RTM-08) — no frame exists in the union.
- **Message edit and deletion events** (FR-RTM-05's second and third kinds) — nothing writes an
  edit or a tombstone, so there is nothing to emit. Recorded, not built.
- **Membership-change events** — the writer exists and the frame exists, but no producer connects
  them. A candidate for a later chapter, and named here so it is not assumed delivered.

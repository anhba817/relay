# Traceability — chapter 3.18, the message that never arrived

Both directions. A map that only runs requirement → test cannot catch a test that verifies
nothing, and a map that only runs test → requirement cannot catch a requirement nobody built.
Chapter 3.12's map recorded FR-CHN-05 delivered when two of its three verbs were built, and
3.15 and 3.16 corrected it twice; the correction is below rather than assumed.

## The governing documents, as amended

    FR-RTM-01   MET       "a connected client shall receive messages for every channel
                          of which it is a member" — P1, T, and unmet on the REST path
                          since chapter 2.2. This chapter is its first satisfaction
                          for that path.
    FR-RTM-05   1 OF 6    message creation now has a producer on both paths. edit,
                          deletion, membership change, presence change and typing do
                          not. Recorded in the chapter, not narrowed in the clause.
    FR-RTM-10   NOT MET   "events shall not be delivered to a client whose membership
                          no longer permits them" — unmet on BOTH paths, and pinned as
                          unmet rather than narrowed until it passed. gaps.md item 2.
    FR-CHN-05   2 OF 3    read and send held before this chapter and hold after it.
                          Observe presence is unbuilt; chapter 3.19.
    FR-RTM-06/07  UNTOUCHED  chapter 3.19's.

    NO SRS CLAUSE CHANGED. Principle VI is satisfied by citing FR-RTM-01 — not by an
    amendment, which is what chapter 3.17's gate was and what a reader arriving from
    3.17 will look for. The chapter says so (FR-002).

    docs/05-sad.md            AMENDED (FR-002a). It disagreed with itself: `:138` gave
                              the publish to the api, `:248` drew `G->>G`, and `:254`
                              stated the ordering unconditionally. A REST-send
                              sequenceDiagram was added and the ordering bullet split
                              by transport.
    docs/06-adr-deep-dives.md AMENDED. ADR-07's "clean mapping — gateway to Redis, api
                              and workers to NATS" gained its exception, dated to
                              chapter 3.8 where it actually started, not to this one.
    docs/07-tutorial-plan.md  CORRECTED. The 3.18 row cited FR-RTM-05's "message half"
                              from 3.14 to 3.18; FR-RTM-05 has no message half. Status
                              and clause both fixed, plus a publisher claim at :215
                              that named only the gateway.

## requirement -> test

    FR-001  clause attribution   traceability.md (this file), the 3.18 row, chapter prose
    FR-002  no SRS amendment     chapter prose — the absence is stated, not implied
    FR-002a docs/05-sad.md       the amendment itself; no test can read prose
    FR-003  the other 5 kinds    chapter prose, <ForwardRef>
    FR-004  REST send published  fanout.itest.ts "publishes a REST send to the channel's
                                 subject"; session.itest.ts "delivers a message SENT OVER
                                 REST to an open socket"
    FR-005  (amended)            fanout.itest.ts "publishes a payload the delivery side
                                 will accept"; publisher.test.ts, same title
    FR-006  internal route       fanout.itest.ts "publishes nothing for a send through the
                                 INTERNAL route"
    FR-007  idempotent retry     fanout.itest.ts "publishes nothing for a recognised
                                 idempotent RETRY" — WRITTEN BY THIS MAP. It had no test;
                                 see below
    FR-008  refused send         fanout.itest.ts, same test
    FR-008a foreign tenant       fanout.itest.ts "publishes nothing for a FOREIGN tenant's
                                 channel"
    FR-009  parity with socket   fanout.itest.ts "publishes what a socket send publishes,
                                 field for field"
    FR-010  failure not fatal    fanout.itest.ts "returns 201 and stays recoverable when
                                 the fan-out is dead"; publisher.test.ts "resolves when the
                                 client throws"
    FR-011  failure observable   publisher.test.ts "…and says so in the log"; and the
                                 adversarial one: fanout.itest.ts T038, "a publisher that
                                 does NOTHING passes the weak assertions and fails the log
                                 one"
    FR-012  what a client knows  chapter prose
    FR-013  FR-RTM-10            session.itest.ts "keeps delivering to a member who was
                                 REMOVED while connected" — pins the FAILURE. See below.
    FR-014  private channel      session.itest.ts "delivers nothing from a PRIVATE channel
                                 to a non-member's socket"
    FR-015  3.12's G1 closed     specs/033-chapter-3-12/gaps.md, G1 marked CLOSED
    FR-016  3.14's verdict       chapter-notes.md, "Chapter 3.14's Phase 2 verdict,
                                 re-examined"
    FR-017  presence out         chapter <ForwardRef>, both locales
    FR-018  published corpus     chapter-notes.md, "The prose sweep" — 12 English phrases,
                                 6 Vietnamese, both locales and docs/

    SC-001  fanout.itest.ts, session.itest.ts (above)
    SC-002  resume.itest.ts "two instances on one fabric" — three tests: the holder, the
            negative, and the bystander
    SC-003  fanout.itest.ts FR-006's test, by count
    SC-004  fanout.itest.ts "publishes nothing for any refused send"
    SC-005  fanout.itest.ts "returns 201 and stays recoverable when the fan-out is dead"
    SC-006  NOT MET — session.itest.ts pins the opposite. FR-RTM-10, gaps.md item 2
    SC-007  session.itest.ts, the private-channel test
    SC-008  fanout.itest.ts, the field-for-field test
    SC-009  this file, and 3.12's G1
    SC-010  packages/outsider/src/integrate.itest.ts "receives a message on a socket —
            sent over REST"
    SC-011  prose-words.mjs (2,775 words, bound 2,000–4,000) and pnpm check:fences

## test -> requirement

    packages/protocol/src/fanout.test.ts        3 tests   the subject grammar. FR-004's
                                                          `chan:{channel_id}`, and "does not
                                                          interpret the id"
    services/api/src/fanout/publisher.test.ts   8 tests   FR-005, FR-010, FR-011, and the
                                                          down-window, which no FR names —
                                                          it is R5's risk, made a property
    services/api/src/fanout/fanout.itest.ts    11 tests   FR-004, 006, 007, 008, 008a, 009,
                                                          010, 011; SC-003/004/005/008. The
                                                          11th is FR-007's, added by this map
    services/gateway/src/session.itest.ts       +5 tests  SC-001, FR-004, FR-013/FR-RTM-10,
                                                          FR-014/SC-007, and two delivery
                                                          basics: a frame from somebody else,
                                                          and every connection one person holds
    services/gateway/src/resume.itest.ts        +3 tests  SC-002, all three
    services/gateway/src/public-surface.itest.ts +1        the renamed test: "delivers a
                                                          REST-sent message, live and on
                                                          resume". It asserted `[]` on both
                                                          legs and its name said "does NOT
                                                          deliver"
    services/gateway/src/isolation.itest.ts     changed   comments only. It records that it
                                                          attaches no fan-out on purpose, and
                                                          why the new delivery block went into
                                                          session.itest.ts instead
    services/gateway/src/fanout.itest.ts        changed   comments only; the grammar moved
                                                          to @relay/protocol
    packages/outsider/src/integrate.itest.ts    changed   SC-010, and its own old title
                                                          recorded at :247

**FR-007 had no test, and requirement -> test alone said it did.** The first draft of this
map credited it to `fanout.itest.ts`'s "publishes nothing for any refused send", on the
strength of that test's name. Reading the other direction: all seven `idempotency_key` values
in that file are a fresh `randomUUID()`, and the test asserts four **refusals** — 403s — not a
recognised retry. Nothing anywhere sent the same key twice. FR-007 says *"a recognised
idempotent retry MUST publish nothing. It wrote no row."* — a MUST, uncovered, and the map is
how it surfaced. Now pinned by `fanout.itest.ts` "publishes nothing for a recognised
idempotent RETRY (FR-007)".

**Proven red.** Removing `!message.duplicate` from `messages.controller.ts:198` fails exactly
that test and nothing else: `expected [ …(2) ] to have a length of 1 but got 2`, 1 failed of
11. A test on an absence that has never been watched failing is a test that proves nothing.

    **No test verifies FR-001, FR-002, FR-002a, FR-003, FR-012, FR-015, FR-016, FR-017 or
    FR-018.** Eight of nineteen requirements are prose, and no checker in this repository
    reads prose (`gaps.md` item 8, carried from 3.17). The five-minute mechanical stand-in is
    T056a's phrase sweep, and it is what found the two defects the FR-018 class list missed.

## The one requirement pinned as unmet

FR-013 asked for FR-RTM-10, and FR-RTM-10 is P1. The test that carries it asserts that a
removed member **keeps** receiving — the opposite of the clause — because that is what the
platform does, on both transports, and the mechanism is a membership snapshot taken at
connection with no re-read. It was pinned as a failure rather than narrowed until it passed,
which is the choice 3.17's `T047c` got wrong in the other direction: a test can pass with half
its subject applied.

SC-006 is therefore not met, and this map says so rather than reporting eleven of eleven.

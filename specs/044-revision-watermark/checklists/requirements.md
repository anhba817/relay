# Specification Quality Checklist: A reconnecting client can tell it missed a revision

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-06
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

**Validated against 16 requirements and 7 success criteria.** Counts: 16 functional requirements, 7 success criteria, 3 user stories, 6 edge cases. **Re-derived after analysis, not carried** — it read 14 until the first analysis pass, which added FR-007a and FR-015 and rewrote FR-007. Zero `[NEEDS CLARIFICATION]` markers — every fork had a defensible default, and the
defaults are in Assumptions where they can be argued with.

### What the first analysis pass changed, and what that says about this checklist

**Every box below was ticked before the pass, and the pass found a conflicting requirement.**
FR-007 said an absent count is "treated as presenting zero"; US2's third acceptance scenario
requires a channel joined during an absence — for which a client presents no count — not to be
reported as needing repair. Zero compares as lower than any revised channel, so the requirement
and the scenario gave opposite answers, and **"requirements are testable and unambiguous" passed
anyway** because each reads fine alone.

Three things came out of it:

| | |
|---|---|
| **FR-007 rewritten** | one rule covering all three absences: first connection, pre-upgrade client, per-channel |
| **FR-007a added** | the platform still reports a count for such a channel, or the client never gets a baseline |
| **FR-015 added** | two tasks were doing the appendix amendments with no requirement behind them |

**A checklist item that can pass while two documents contradict each other is measuring
presence, not agreement** — which is what `check-checklist.py` says of itself in its own last
line. The pass that found this read the requirement against the scenario, which no instrument
here does.

### What the second pass changed

The first pass read the artifacts against each other. The second asked what the compiler sees at
each task boundary, and found two the first could not:

- **A phase that could not end green.** the repository task changed a function's return shape and repaired one of
  its two callers; the other's repair was in the next phase, so typecheck failed exactly where the
  strategy says to commit.
- **A package that had to be built.** `@relay/protocol` exports `./dist` with no path mapping to
  source, so two schema changes were invisible to their three consumers until a build ran — and
  the only build was the final gate. Three tasks would have failed for a reason that was not
  theirs.

Neither is visible by reading requirements against tasks. **Both are visible by asking what
happens when the tasks are run in order**, which is a different question and wants asking
separately.

**And one finding was made by the first pass's own fix.** One task asked for an amendment that the
first pass's remediation had already performed, leaving a task whose work was silently done.
Feature 043 recorded four such; a remediation is a change like any other and wants re-checking.

### What the third pass changed

The first two passes read. The third **ran the premise**, which nobody had: everything in these
documents rested on a comment in `session.ts` saying a revision below the cursor reaches no one.

**It is true, and now measured.** A message at sequence 1, edited while a client holding cursor 2
was away, produced on reconnect: one frame (the ack), zero sequences, and no delivery of the
edit. Live delivery worked as a control and the edit returned 200, so the silence is the defect
rather than a broken probe. The spec's edge case held too — a message edited *above* the cursor
came back on the replay carrying its new text.

**The probe failed three times before it ran**, and each failure is now in the record:

| Attempt | Refusal | What it means |
|---|---|---|
| send with the API key | `sender_not_permitted` | an application credential may send only as a bot |
| edit with the API key | `wrong_credential_type` | the edit route wants an end-user token |
| read `.sequence` | undefined | the field is `seq` |

**The quickstart could not be followed by the person who wrote it.** Three tasks now name the
credential rules and the guide mints a token in its Prerequisites. **A validation guide nobody
has executed is a document, not a guide.**

### Why there are no clarification markers

Four choices looked like questions and each had an answer already in the tree:

| Looked like a question | Answered by |
|---|---|
| per-channel or per-connection signal | FR-006 — a connection-wide flag cannot say which channel to repair |
| counter or timestamp | FR-010 — a clock the client and platform disagree about produces wrong repairs |
| who performs the repair | FR-016a already says the client re-reads history |
| what existing channels start at | reconstructing a count would tell every client to repair everything once |

**The one that could still be wrong is the last.** Starting at zero means a revision applied
before this ships is never repaired for a client that already holds the stale copy. That is the
current behaviour continuing for existing stale copies rather than a new defect, and the
alternative makes every client repair every channel once. Recorded in Assumptions rather than
decided silently.

### The three references this specification makes, and why

A specification for business stakeholders that names a document is making a claim about the
tree. Each is deliberate:

| Reference | Class | Why the spec names it |
|---|---|---|
| `FR-016a`, `FR-016b` | a predecessor's spec ids | they define the limit this feature supplies the remedy for. **They are chapter 3.23's specification ids, not SRS clauses**, which is a correction this checklist did not make until the amendment was attempted — see below |
| `docs/04-srs.md` | the document amended | FR-013 amends clauses in it, and once the clauses turned out not to be `FR-016a` and `FR-016b` the spec had to name the document instead of two identifiers |
| `docs/11-scalability-measurement-2026-09-06.md` | a measurement | supplies the 3m20s window and SC-004's rate baseline |
| SRS revision 1.9 | the record | where the connect-limit finding was filed, named in Out of Scope |

No source file, package, table or column is named anywhere in the specification. The signal is
described by what it must do, not by where it lives.

### What the measurement changed about this specification

Written after `docs/11-scalability-measurement-2026-09-06.md` rather than before, and two
requirements exist because of it:

- **FR-014** — no per-channel query per handshake. At 10,000 connections that cost is the one
  this feature cannot pay, and the number came from the measurement rather than from judgement.
- **SC-004** — the reconnect rate has a measured baseline (1,125-1,675/s) to hold within 10% of.
  Without it the criterion would have read "does not slow reconnects", which is not testable.

The Context section's second bullet — that the edit and delete paths do not touch the channel row
while the send path does — is why the cost is stated as one write per revision rather than
assumed to be free.

### What the close-out found, and why it is in a quality checklist

**Every box above was ticked, twice, before the amendment was attempted.** The spec, the plan,
the tasks and the quickstart all said the feature would amend "SRS FR-016a and SRS FR-016b".
Those identifiers are **chapter 3.23's specification ids**. They appear nowhere in
`docs/04-srs.md`; the only place in `docs/` that spells `FR-016a` is a quoted ADR passage inside
the SAD. Three analysis passes read those documents against each other and every one of them
saw two artifacts agreeing, because they agreed with each other and not with the tree.

**"Requirements are testable and unambiguous" passed on a requirement naming a clause that does
not exist**, and it kept passing right up to the moment somebody ran `grep`. What found it was
not a checker and not a reading: it was **executing the task** — opening the SRS to make the
edit, and discovering there was nothing there to edit. Reading the clauses rather than the
identifiers then turned up **three** clauses to amend where the requirement named two.

`check-refs.py` catches this class now, in one direction: it fails a citation of `FR-016a` with
no chapter suffix, because an unsuffixed id is a claim about *this* feature's requirements. It
cannot check the other direction — whether a suffixed foreign id names anything real — and
nothing here can.

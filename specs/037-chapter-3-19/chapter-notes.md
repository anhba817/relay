# Chapter notes — 3.19, presence and who is allowed to see it

*Written during the work, not at close-out. The close-out sections — what shipped, the
phases that went badly, what the next feature should do differently, and the hand-off to
chapter 3.20 — arrive in phase 9.*

## The scoping is topology, and there is no scoping code to read

**A reader looking for the filter will not find one, and that is the design rather than an
omission.** FR-RTM-07 says a presence event reaches only users sharing at least one channel
with the subject. Nothing in `presence.ts` or `session.ts` compares two membership sets.

The rule is enforced by three facts that compose:

    a transition publishes on `presence:{channel_id}` for each of the SUBJECT's channels
    an instance subscribes to `presence:{channel_id}` only for channels its OWN members hold
    delivery walks `registry.subscribersOf(channelId)`, which is a membership test

So an instance receives a transition only on subjects it subscribed to, and it subscribed
only to channels its local members belong to. A user who shares no channel with the subject
is on no instance that hears about them — and if they happen to share an instance with
somebody who does, `subscribersOf` does not return them.

**Two consequences worth stating rather than leaving to be discovered.**

A private channel needs no special case. FR-CHN-05's third verb — *observe presence* — is
satisfied because a non-member is not subscribed, which is the same mechanism that handles
a public channel they never joined. The test for it exists anyway, because "no special case
was needed" and "the case was never considered" look identical from outside.

Cross-tenant isolation is likewise structural: presence keys carry `{env}` and channel ids
are unguessable UUIDs. That makes it the kind of property that holds until somebody adds a
scan or a pattern read, which is why the exemption in `eslint.config.mjs` is written against
the limiter's standard — every key composed from the authenticated connection's own
environment id, none read that was not composed here.

**What this costs.** The scope is exactly as correct as the subscribe set, and the subscribe
set is taken once at connect. A user who joins a channel while connected does not appear
online to that channel's members until they reconnect (FR-021). That is FR-RTM-10's
staleness wearing a different hat, and it is unfixed here on purpose.

## The chapter took half of ADR-10's remedy, and its trigger never fired

ADR-10's revisit condition, written in the SAD and again at `docs/06-adr-deep-dives.md:651`,
names two remedies and a threshold: above ~30% of gateway publish volume, *"presence
subjects get their own fabric or channels opt in"*.

**This chapter took the first remedy and closed the door on the second, and neither move was
caused by the threshold.**

Presence now publishes on `presence:{channel_id}` — its own fabric — because `chan:{id}` is
typed to messages at three points and the third is inside a function fenced by ten chapters
(R1). And SRS open question 3 closes as *not opt-in*: a per-channel toggle is a data model,
a UI, an API surface and a defaulting rule, bought to solve a volume problem nobody has
measured. Both decisions are about the shape of the code that exists. Publish volume did not
enter either argument.

**So the trigger is undischarged, and so is NFR-SCL-01.** Nothing in this chapter measured
presence as a fraction of gateway publish traffic, because the lane's largest membership set
is five channels and its largest instance count is two. The numbers this chapter does have —
`cmdstat_subscribe calls=12`, six fan-out and six presence across two instances and three
channels — describe the cost's *shape*, one subscribe per channel per instance, and say
nothing about its size at ten thousand connections.

A later reader has an easy wrong inference available: presence got its own fabric, therefore
the 30% threshold was crossed. It was not. If it is crossed later, the remedy still on the
table is the one this chapter declined — channels opting in — and the argument against it
recorded in Appendix C row 3 was made at a scale where the question could not be answered.
That argument should be re-read, not re-cited.

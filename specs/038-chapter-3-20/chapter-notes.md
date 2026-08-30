# Chapter notes — 3.20, the membership that changed under a live socket

*Decisions this chapter made that are not visible from the code, and the reasons.
Written as the phases run.*

---

## `check-refs.py` was carried forward rather than rewritten (Phase 1)

Chapter 3.19's `gaps.md` item 8 asked what happens to a feature's own checkers: its
two die the way chapter 3.18's `sweep.py` died — written for one feature, useful in
the next, and deleted with the directory because nobody decided.

**This chapter's answer is to copy the file and reset `FOREIGN`.** Not to promote it
to a repository-level script, which would make it a thing to maintain for chapters
that do not want it; not to import it across directories, which makes one feature's
record depend on another's. A copy with its declarations emptied is a checker that
starts each chapter saying nothing it has not been told.

The copy is not free. Phase 4 found the pattern rejecting `T054a` outright —
`T\d{3}` with no suffix — although chapter 3.17 shipped `T012a`, `T047c` and `T054b`.
A carried-forward checker carries its blind spots forward too, and the fix
(numeric-part sequencing, orphan suffixes caught, four red tests) belongs to whoever
copies it next.

---

## An unban publishes nothing (Phase 7)

A ban revokes every channel through `member:{env}:{user}`. **The unban does not
restore them, and that is a decision rather than an omission.**

`banUser` sets `users.banned_at` and leaves the `members` rows alone, so an unbanned
user's memberships are exactly what they were. What the ban destroyed is the live
connection's `channelIds`. Restoring it would need the api to re-derive the channel
list and publish an `added` frame per channel — the per-channel shape
`contracts/membership-fabric.md` rules out for the ban itself, reintroduced for its
rarer inverse.

Two mechanisms already repair it:

- **reconnecting**, which reads membership at the door (chapter 3.2). Asserted in
  `membership.itest.ts`, and it is what a client does after being cut anyway.
- **the backstop's periodic re-read**, which picks the memberships up within its
  interval without a reconnect.

So the answer to "does delivery resume without a reconnect?" is: not immediately, and
yes within the backstop's interval. The socket stays open throughout — a ban is not a
protocol violation and close code 4009 is not this.

**What this costs:** an unbanned user with a live socket sees nothing until one of
those two fires. For a moderation action measured in minutes or hours, a re-read
interval measured in seconds is not the part anybody notices.

---

## The ban's sentinel never reaches a client (Phase 7)

`contracts/membership-fabric.md` carried one open question — `channel: "*"` or a
separate payload shape — and the phase that decided it took neither. The fabric
carries `"*"`; the **gateway expands it** into one wire frame per channel that
connection holds. A client receives what N individual removals would have produced.

The objection the contract raised against `"*"` was that a sentinel inside a
`z.string().min(1)` reads as a channel id for a year. It survives in the fabric
payload and in the `membership.published` log line, both internal, with
`ALL_CHANNELS` as its one spelling. It does not survive to a customer.

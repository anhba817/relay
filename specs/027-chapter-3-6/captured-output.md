# Captured output — chapter 3.6

Every transcript the chapter quotes, from a real run. Nothing here is typed by
hand; where a line is elided it says so.

Environment: compose stores on 15432 / 16379 / 14222, `part3-ch5` plus this
chapter's commits, `RELAY_WEBHOOK_SECRET_KEY` set to CI's value.

---

## The walk, against a permanently failing endpoint

`node scripts/hostile-endpoint.mjs --mode=fail --quiet --secret=hunter2` in one
terminal, then:

```console
$ node scripts/webhook-walk.mjs --secret=hunter2 --fast-forward --watch-disable
=== 5. the whole schedule, without waiting for it =
  tiers: now → 1s → 5s → 30s → 300s → 1800s → 7200s
  7 attempts, then the delivery is dead-lettered.

  the waits are REAL in production. This rewrites next_attempt_at so a
  reader can watch the end of the schedule without waiting two hours —
  it is a fast-forward through the clock, not a shortcut around the logic.

  attempt 2                failed → rescheduled as attempt 3
    endpoint               run open · 2 failures · enabled=true
  attempt 3                failed → rescheduled as attempt 4
    endpoint               run open · 3 failures · enabled=true
  attempt 4                failed → rescheduled as attempt 5
    endpoint               run open · 4 failures · enabled=true
  attempt 5                failed → rescheduled as attempt 6
    endpoint               run open · 5 failures · enabled=true
  attempt 6                failed → rescheduled as attempt 7
    endpoint               run open · 6 failures · enabled=true
  attempt 7                failed → dead
    endpoint               run open · 7 failures · enabled=true

  delivery b9a68bee        attempt=7 state=dead next=2026-08-18T14:52:26.767Z

dead letters               1
  3e2acaf8                 attempts=7 last_status=500

=== 6. when to stop trying ========================
  The run above is what auto-disable reads — two columns on the endpoint,
  never the attempt stream. A backlogged analytics path cannot delay a
  disablement, and a broker being unwell cannot block one.

  The rule: longer than 60 minutes AND at least
  5 failures. Both, never either — the hour alone would let one
  failure followed by a two-hour retry gap disable an endpoint.

failures in the run        7
enabled                    true
  aging the run past the hour (the clock moves, the rule does not)...

endpoints the sweep disabled 1

enabled                    false
disabled_at                2026-08-18T14:52:29.830Z
disabled_reason            7 consecutive failures over 1h04m; last status 500

notification rows          1
  run of 7                 last_status=500 delivered_at=null

  `delivered_at` is null and stays null. FR-WHK-07 asks for the
  organisation to be notified BY EMAIL, and this platform has no email
  transport of any kind. The row is the obligation; the null is the
  admission. Chapter 3.7 needs the same transport for quotas.

a second sweep disables    0
```

The dispatcher's own JSON log lines are interleaved in the real output and are
removed above; they are one `delivery.attempted` per attempt and say nothing this
transcript does not.

**Read the two lines before section 6.** The delivery is `dead`, the run holds
seven failures, and `enabled` is still `true`. That is research R1's quiet
endpoint, reached by running rather than by arithmetic: the schedule is exhausted,
so no further outcome will ever be reported for this endpoint, and a check that
only runs on a recorded outcome would never fire again. The endpoint would sit
enabled and failing for ever.

The sweep disables it. A second sweep disables nothing — the `enabled = true`
predicate in the update is what makes that true, rather than a check somebody
remembered to write.

`disabled_reason` names the count, the window and the last status, which is what
FR-009 asks for and what stops the first support message being "disabled, why?".

`delivered_at=null` is the unmet half of FR-WHK-07, visible in the data rather
than only in prose.

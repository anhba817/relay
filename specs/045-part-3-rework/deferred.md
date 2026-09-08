# Changes a chapter cannot make yet, and the chapter that must make them

The rebuild moves whole subjects. A chapter that used to touch a file now sometimes runs
BEFORE the chapter that creates it — and the change is not lost, it is owed. This is the
ledger. Every entry names the original commit, the file, and the chapter that inherits it.

Without this the rebuild silently drops work: a cherry-pick that cannot apply is reported
once, on a terminal, and then never again.

| original commit | file | belongs to | what it did |
|---|---|---|---|
| `b638242` | `services/api/src/webhooks/deliveries.itest.ts` | new 19 (webhooks) | settle the drain before asserting a delivery was published |
| `5015cc8` | `services/api/src/webhooks/deliveries.itest.ts` | new 19 (webhooks) | give the sweep tests a limit that reaches their own endpoint |
| `aed5af8` | `scripts/webhook-walk.mjs`, the webhook block of `services/api/src/db/schema.ts` | new 19 (webhooks) | name the subject instead of the chapter number in three comments |

**Three of old 3.7's eight commits are webhook work.** In the old order webhooks came two
chapters earlier, so a chapter about the resume high-water mark could freely fix a webhook
test in passing. Moving webhooks to 19 unpicks that: the resume work applies cleanly and
the webhook fixes have nothing to apply to. Neither is a merge problem — the file does not
exist — and neither is lost, because they are here.

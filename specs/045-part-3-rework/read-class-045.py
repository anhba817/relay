#!/usr/bin/env python3
"""The read class in the non-`.ts` corpus: 27 sites, written out.

Each is a judgement no rule makes. Four were references SPLIT ACROSS A LINE BREAK, which
is why they are pairs — `… and — since chapter` / `# 3.5 — the three services` is one
reference and two lines, and re-wrapping is part of the edit. Three are section-rule
HEADINGS whose subject is the ordinal, and their trailing rule is re-trimmed to the
original width so a longer name does not push a 118-column rule out to 140.
"""
import re, sys
from pathlib import Path

PLAT = Path(__file__).parent.parent.parent / "relay-platform"
APPLY = "--apply" in sys.argv

E = [
 # --- split across a line break: one reference, two lines ------------------------
 ("compose.yaml",
  "# Four stores, each here by a recorded decision (SAD §9), and — since chapter\n"
  "# 3.5 — the three services themselves. Host ports are env knobs with the",
  "# Four stores, each here by a recorded decision (SAD §9), and — since the webhook\n"
  "# dispatcher chapter — the three services themselves. Host ports are env knobs with the"),
 ("eslint.config.mjs",
  "// an earlier block's setting for it rather than merging. That is the bug chapter\n"
  "// 3.12 found (R23, FR-043): a second block for `**/*.itest.ts` carrying feature",
  "// an earlier block's setting for it rather than merging. That is the bug the\n"
  "// isolation gauntlet found (R23, FR-043): a second block for `**/*.itest.ts` carrying feature"),
 ("services/api/migrations/0011_activity_and_read_positions.sql",
  "-- read position is. The guard's refusal message interpolates a key, and chapter\n"
  "-- 3.13 installed `coalesce(to_jsonb(OLD) ->> 'id', to_jsonb(OLD)::text)` for",
  "-- read position is. The guard's refusal message interpolates a key, and the\n"
  "-- channel-endpoints chapter installed `coalesce(to_jsonb(OLD) ->> 'id', to_jsonb(OLD)::text)` for"),
 ("services/api/migrations/0013_bot_users.sql",
  "-- TWO COLUMNS, NOT A SECOND TABLE. `users` is what every reader built since chapter\n"
  "-- 3.15 already reads. A `bots` table would have meant teaching each of them a second",
  "-- TWO COLUMNS, NOT A SECOND TABLE. `users` is what every reader built since the\n"
  "-- channel-control chapter already reads. A `bots` table would have meant teaching each of them a second"),
 # --- re-wrapped because the name is longer than the ordinal ---------------------
 ("eslint.config.mjs",
  "        // environment, exactly as its three siblings above do, and 3.10\n"
  "        // listed it in neither this rule nor `exempt.ts` — whose comment",
  "        // environment, exactly as its three siblings above do, and the quota\n"
  "        // chapter listed it in neither this rule nor `exempt.ts` — whose comment"),
 ("packages/test-harness/src/sentinel.sql",
  "-- by chapters 3.10 and 3.11 and neither added them here, so a cross-environment\n"
  "-- UPDATE or DELETE on any of them passed for two chapters. Confirmed against a\n"
  "-- running database rather than read off this file: `pg_trigger` held five",
  "-- by the quota and connection-metering chapters and neither added them here, so a\n"
  "-- cross-environment UPDATE or DELETE on any of them passed for two chapters.\n"
  "-- Confirmed against a running database rather than read off this file:\n"
  "-- `pg_trigger` held five"),
 # A PLURAL LEFT HALF-DONE by the substitute pass: `Chapters 3.10 and 3.11's tables`
 # had its possessive half substituted and its bare half classified `read`, so the
 # plural noun survived beside a noun phrase.
 ("packages/test-harness/src/sentinel.sql",
  "    -- Chapters 3.10 and the connection-metering chapter's tables. Every one carries `environment_id`, which\n"
  "    -- is the only thing the WHEN clause below needs; what they do NOT all carry\n"
  "    -- is `id`, which is what the message expression above had to change for.",
  "    -- The quota and connection-metering chapters' tables. Every one carries\n"
  "    -- `environment_id`, which is the only thing the WHEN clause below needs; what they\n"
  "    -- do NOT all carry is `id`, which is what the message expression above had to\n"
  "    -- change for."),
 ("services/api/migrations/0009_quotas.sql",
  "-- The outbox chapter published events, 3.5 dispatched webhook deliveries, 3.9 sent\n"
  "-- disablement emails. Each is a table whose claim predicate starts null, drained\n"
  "-- by a relay, retried by falling due again. This is the fourth, and saying the",
  "-- The outbox chapter published events, the webhook dispatcher chapter dispatched\n"
  "-- webhook deliveries, the mail-transport chapter sent disablement emails. Each is a\n"
  "-- table whose claim predicate starts null, drained by a relay, retried by falling\n"
  "-- due again. This is the fourth, and saying the"),
 # --- a tag that carried a requirement id: the id stays, the ordinal goes ---------
 ("eslint.config.mjs",
  "    // THE SEAL ON `packages/outsider` (chapter 3.14, FR-030, FR-034, R12).",
  "    // THE SEAL ON `packages/outsider` (FR-030, FR-034, R12)."),
 ("packages/outsider/vitest.integration.config.mts",
  "// THE SEALED INTEGRATION (chapter 3.14, FR-030, FR-031).",
  "// THE SEALED INTEGRATION (FR-030, FR-031)."),
 ("scripts/seed-demo-tenant.mjs",
  "// A tenant an outsider can integrate against (chapter 3.14, FR-032).",
  "// A tenant an outsider can integrate against (FR-032)."),
 ("scripts/webhook-walk.mjs",
  "//   --watch-disable                    chapter 3.6: print the failure run as it",
  "//   --watch-disable                    print the failure run as it"),
 # --- a name in place of the ordinal ---------------------------------------------
 ("eslint.config.mjs",
  '    // CORRECTED IN 3.12 (T069c). This comment used to say it was "the one TEST',
  '    // CORRECTED IN THE ISOLATION GAUNTLET (T069c). This comment used to say it was "the one TEST'),
 ("packages/test-harness/src/sentinel.sql",
  "  -- `OLD.id` UNTIL CHAPTER 3.12, and that is why extending the array below was",
  "  -- `OLD.id` UNTIL THE ISOLATION GAUNTLET, and that is why extending the array below was"),
 ("scripts/webhook-walk.mjs",
  "//   node scripts/webhook-walk.mjs --fast-forward --watch-disable   # chapter 3.6",
  "//   node scripts/webhook-walk.mjs --fast-forward --watch-disable   # the retry-and-disable chapter"),
 ("scripts/webhook-walk.mjs",
  "// has ever held, which on a development machine is every test run since 3.3.)",
  "// has ever held, which on a development machine is every test run since the outbox chapter.)"),
 ("services/api/migrations/0007_webhook_attempts.sql",
  "--   * all three foreign keys are ON DELETE NO ACTION, the choice 3.5 made and",
  "--   * all three foreign keys are ON DELETE NO ACTION, the choice the webhook dispatcher chapter made and"),
 ("services/api/migrations/0009_quotas.sql",
  "-- alike, and the string `'0'` for zero. The distinction 3.8 needed nullable",
  "-- alike, and the string `'0'` for zero. The distinction the rate-limit chapter needed nullable"),
 ("services/api/migrations/0009_quotas.sql",
  "-- unattributed by design since chapter 3.3, and an unattributed send counts",
  "-- unattributed by design since the outbox chapter, and an unattributed send counts"),
 ("services/api/migrations/0012_member_roles_and_user_deletion.sql",
  "-- has carried `CHECK (role IN ('owner','admin','member'))` since chapter 3.1 —",
  "-- has carried `CHECK (role IN ('owner','admin','member'))` since the tenancy chapter —"),
 ("vitest.coverage.config.mts",
  "        // (89.50% statements, 82.73% branches after chapter 3.8, up from 86.55%",
  "        // (89.50% statements, 82.73% branches after the rate-limit chapter, up from 86.55%"),
 ("vitest.coverage.config.mts",
  "        // send path had had that test since chapter 3.15; the two new routes and the",
  "        // send path had had that test since the channel-control chapter; the two new routes and the"),
 ("vitest.coverage.config.mts",
  "        //     a senderless row (FR-018 of 3.23) before it can return, so the arm was",
  "        //     a senderless row (FR-018 of the revisions chapter) before it can return, so the arm was"),
]

# --- section rules: substitute, then re-trim the trailing rule to the same width ---
# A FOURTH SECTION RULE WAS MISSED BY LISTING THREE. `compose.yaml`'s
# `# --- the services (chapter 3.5) ---…` is the same shape with a different comment
# opener and dashes instead of box-drawing, and it was the ONE reference left when
# `classify-refs` was re-run — which is the only reason it was noticed.
RULES = [("vitest.coverage.config.mts", "CHAPTER 3.12'S", "THE ISOLATION GAUNTLET'S"),
         ("vitest.coverage.config.mts", "CHAPTER 3.15's", "THE CHANNEL-CONTROL CHAPTER'S"),
         ("vitest.coverage.config.mts", "CHAPTER 3.20'S", "THE MEMBERSHIP-REVOCATION CHAPTER'S")]

n = 0
for path, old, new in E:
    f = PLAT / path
    s = f.read_text(encoding="utf-8")
    c = s.count(old)
    if c != 1:
        print(f"  PRE-IMAGE matched {c} times (need 1) in {path}:\n    {old.splitlines()[0][:96]}")
        sys.exit(1)
    if APPLY:
        f.write_text(s.replace(old, new), encoding="utf-8")
    n += 1

for path, was, name in RULES:
    f = PLAT / path
    lines = f.read_text(encoding="utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if was in l and "──" in l]
    if len(hits) != 1:
        print(f"  RULE heading {was!r} matched {len(hits)} lines (need 1)"); sys.exit(1)
    i = hits[0]
    orig, width = lines[i], len(lines[i])
    out = orig.replace(was, name)
    t = re.search(r"(─+)\s*$", out)
    out = out[:t.start()] + "─" * max(3, width - t.start())
    lines[i] = out[:width] if len(out) > width else out + "─" * (width - len(out))
    if APPLY:
        f.write_text("\n".join(lines), encoding="utf-8")
    print(f"  rule {width:3d} -> {len(lines[i]):3d}  {lines[i].strip()[:84]}")
    n += 1

print(f"read-class-045: {'APPLIED' if APPLY else 'all pre-images unique'} — {n} sites")

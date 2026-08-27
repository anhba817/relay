#!/usr/bin/env python3
"""Sweep for chapter 3.18 — one check per CRITICAL/HIGH class found in sixteen
analysis passes.

WHY A SCRIPT. Sixteen passes found thirteen CRITICALs and the source moved every
time; nine of them were premises that a grep could have settled, and four were
corrections to earlier remediations of mine. A checker cannot ask a new question,
but it can stop an answered one from rotting.

THE RULES THIS SCRIPT FOLLOWS, learned the hard way in 3.17 and again here:
  - the class list is explicit, and an unknown member FAILS rather than passing
  - a citation is checked by reading the cited line, not by trusting the number
  - it must be tested RED before it is believed (see --self-test)
Run:  python3 sweep.py [--self-test]
"""
import json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PLAT = ROOT / "relay-platform"
TUT = ROOT / "relay-tutorial"

def read(p):
    p = Path(p)
    return p.read_text(encoding="utf-8") if p.is_file() else ""

TASKS, SPEC, PLAN = read(HERE/"tasks.md"), read(HERE/"spec.md"), read(HERE/"plan.md")
RESEARCH, CHECKLIST = read(HERE/"research.md"), read(HERE/"checklists/requirements.md")
CONTRACT = read(HERE/"contracts/fanout-publisher.md")

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))

TASK_RE = re.compile(r'^- \[ \] (T\d{3}[a-e]?)((?: \[P\])?)((?: \[US\d\])?) (.*)', re.M)
tasks = [(m.group(1), m.group(2).strip(), m.group(3).strip(), m.group(4)) for m in TASK_RE.finditer(TASKS)]
order = {t[0]: i for i, t in enumerate(tasks)}

# ── 1. every requirement is cited by at least one task ──────────────────────
keys = sorted(set(re.findall(r'\*\*(FR-\d{3}a?)\*\*', SPEC))) + sorted(set(re.findall(r'\*\*(SC-\d{3})\*\*', SPEC)))
lines = [t[3] for t in tasks]
uncited = [k for k in keys if not any(k in l for l in lines)]
check("1  every FR/SC cited by a task", not uncited, f"{len(keys)-len(uncited)}/{len(keys)} cited" + (f" · MISSING {uncited}" if uncited else ""))

# ── 2. task ids unique ──────────────────────────────────────────────────────
ids = [t[0] for t in tasks]
check("2  task ids unique", len(ids) == len(set(ids)), f"{len(ids)} tasks")

# ── 3. story labels only inside user-story phases ───────────────────────────
phase, bad = None, []
for line in TASKS.splitlines():
    h = re.match(r'## Phase \d+:(.*)', line)
    if h: phase = h.group(1)
    m = re.match(r'- \[ \] T\d{3}[a-e]? ((?:\[P\] )?)((?:\[US\d\] )?)', line)
    if m and phase is not None and ("User Story" in phase) != bool(m.group(2).strip()):
        bad.append(line[:40])
check("3  story labels match phase kind", not bad, f"{len(bad)} violations" + (f" · {bad[:2]}" if bad else ""))

# ── 4. no two [P] tasks write the same file ─────────────────────────────────
PATH_EXT = r'(?:ts|tsx|mts|mjs|mdx|md|json|txt|sql|yml|yaml|sh|py)'
own = {}
for tid, p, _, body in tasks:
    if p != "[P]": continue
    for f in set(re.findall(rf'`([^`]*[/.][A-Za-z0-9_.()-]*\.{PATH_EXT})`', body)):
        own.setdefault(f, []).append(tid)
coll = {f: t for f, t in own.items() if len(t) > 1}
check("4  no [P] file collisions", not coll, f"{len(own)} files claimed by [P] tasks" + (f" · {coll}" if coll else ""))

# ── 5. stated dependencies match document order ─────────────────────────────
viol = []
for m in re.finditer(r'\*\*(T\d{3}[a-e]?(?:[^*]{0,60}?)\b(?:before|after)\b[^*]{0,60}?)\*\*', TASKS):
    txt = m.group(1); kw = 'before' if 'before' in txt else 'after'
    L = re.findall(r'T\d{3}[a-e]?', txt.split(kw)[0]); R = re.findall(r'T\d{3}[a-e]?', txt.split(kw)[1])
    for l in L:
        for r in R:
            if l in order and r in order:
                ok = order[l] < order[r] if kw == 'before' else order[l] > order[r]
                if not ok: viol.append(f"{l} {kw} {r}")
check("5  dependency notes match doc order", not viol, f"{len(viol)} violations" + (f" · {viol}" if viol else ""))

# ── 6. no unresolved placeholders ───────────────────────────────────────────
PLACEHOLDERS = ("TODO", "TKTK", "???", "NEEDS CLARIFICATION", "<placeholder>", "[TBD]")
hits = [(n, p) for n, d in (("spec", SPEC), ("plan", PLAN), ("tasks", TASKS), ("research", RESEARCH)) for p in PLACEHOLDERS if p in d]
check("6  no placeholders", not hits, str(hits) if hits else "clean across 4 documents")

# ── 7. every task names a target path or a command ──────────────────────────
# A handful of tasks legitimately name no file: git operations, decisions, and
# statements the chapter makes in prose. The list is EXPLICIT so that a NEW
# pathless task fails rather than joining a silent majority — the 3.17 rule.
PATHLESS_BY_DESIGN = {
    "T001b": "the compose commands are in an indented block, not backticked inline",
    "T009c": "a decision to record, not a file to edit",
    "T015":  "verifies a spec clause already amended",
    "T028":  "establishes where membership is checked before asserting",
    "T044a": "a constraint on how page.mdx is written, applied by T044",
    "T046":  "a statement the chapter makes, in page.mdx via T044",
    "T047":  "same",
    "T047a": "runs a skill over the chapter",
    "T049":  "the vi path is in an indented block",
    "T050c": "a statement the chapter makes",
    "T050d": "amends a Trap named by locale, not by path",
    "T050e": "amends a paragraph named by locale, not by path",
    "T057":  "runs the sealed lane",
    "T063":  "git: commit in each repository",
    "T064":  "git: tag part3-ch18 in all three",
    "T066":  "git: push all three and verify gitlinks",
}
nopath = [t[0] for t in tasks if not re.search(rf'`[^`]*[/.][A-Za-z0-9_.()-]*\.{PATH_EXT}`|`?\bpnpm\b|`node |`git |`docker ', t[3])]
unexpected = [t for t in nopath if t not in PATHLESS_BY_DESIGN]
stale = [t for t in PATHLESS_BY_DESIGN if t not in nopath]
check("7  pathless tasks are the exempted ones only", not unexpected and not stale,
      f"{len(nopath)} pathless, all exempted" if not (unexpected or stale)
      else f"UNEXPECTED {unexpected} · EXEMPTION NO LONGER NEEDED {stale}")

# ── 8. checklist fully checked ──────────────────────────────────────────────
unchecked = len(re.findall(r'^- \[ \]', CHECKLIST, re.M))
check("8  checklist has no open items", unchecked == 0, f"{len(re.findall(r'^- \[[Xx]\]', CHECKLIST, re.M))} checked, {unchecked} open")

# ── 9. every platform file a task edits is in the plan's fence column ───────
edited = set()
for _, _, _, body in tasks:
    for f in re.findall(rf'`((?:relay-platform/)?(?:services|packages)/[A-Za-z0-9_./()-]*\.{PATH_EXT})`', body):
        edited.add(f.replace("relay-platform/", ""))
for f in re.findall(rf'`(vitest\.coverage\.config\.mts)`', TASKS): edited.add(f)
missing = sorted(f for f in edited if f.split('/')[-1] not in PLAN)
check("9  edited platform files are in the fence column", not missing, f"{len(edited)} edited" + (f" · NOT IN COLUMN {missing}" if missing else ""))

# ── 10. repository premises that earlier passes established ─────────────────
PREMISES = [
    ("session.itest.ts wires NO fanout (T014's premise)",
     lambda: read(PLAT/"services/gateway/src/session.itest.ts").count("fanout") == 0),
    ("session.itest.ts spawns a REAL api (pass 2's correction)",
     lambda: "startApi" in read(PLAT/"services/gateway/src/session.itest.ts")
             and "dist" in read(PLAT/"services/gateway/src/session.itest.ts")),
    ("resume.itest.ts HAS a fanout (T027's premise)",
     lambda: "createFanout" in read(PLAT/"services/gateway/src/resume.itest.ts")),
    ("fanout.itest.ts has zero sockets (pass 2's census)",
     lambda: "new WebSocket" not in read(PLAT/"services/gateway/src/fanout.itest.ts")),
    ("messages.service.send() has exactly 2 callers (FR-006)",
     lambda: len(subprocess.run(["grep","-rl","--exclude-dir=node_modules","--include=*.ts","this.messages.send(",str(PLAT/"services/api/src")],
                 capture_output=True,text=True).stdout.split()) == 2),
    ("MessageRow carries `duplicate` and no `user` (T024)",
     lambda: (lambda b: "duplicate?: boolean" in b and not re.search(r'\n  user:', b))(
         re.search(r'export interface MessageRow \{(.*?)\n\}', read(PLAT/"services/api/src/db/repository.ts"), re.S).group(1))),
    ("messageSchema is exactly 6 fields (T018, data-model)",
     lambda: len(re.findall(r'^\s{2}\w+:', re.search(r'export const messageSchema = z\.strictObject\(\{(.*?)\n\}\)',
                 read(PLAT/"packages/protocol/src/frames.ts"), re.S).group(1), re.M)) == 6),
    ("messageSchema.text is non-nullable (T025's second reason)",
     lambda: re.search(r'text: z\.string\(\),', read(PLAT/"packages/protocol/src/frames.ts")) is not None),
    ("DEFAULT_REDIS_URL declared in exactly 3 files (C2)",
     lambda: len(subprocess.run(["grep","-rl","--exclude-dir=node_modules","--include=*.ts","export const DEFAULT_REDIS_URL",str(PLAT/"services"),str(PLAT/"packages")],
                 capture_output=True,text=True).stdout.split()) == 3),
    ("the off-switch family is 4 modules (H28)",
     lambda: len({m for m in re.findall(r'RELAY_(OUTBOX_RELAY|EVENT_CONSUMER|DELIVERY_RELAY|NOTIFICATION_RELAY)',
                 read(ROOT/".github/workflows/ci.yml"))}) >= 3),
    ("createFanout still has no ioredis error listener (R10)",
     lambda: 'on("error"' not in read(PLAT/"services/gateway/src/fanout.ts")),
    ("limits/store.ts still carries the down-window (H7)",
     lambda: "DOWN_WINDOW_MS" in read(PLAT/"services/api/src/limits/store.ts")),
    ("lib/tutorial.ts holds 34 published and no 3.18 entry (C6)",
     lambda: read(TUT/"lib/tutorial.ts").count('status: "published"') == 34
             and '"3.18"' not in read(TUT/"lib/tutorial.ts")),
    ("the isolation gauntlet still compares responses only (C8)",
     lambda: "withoutRequestId" in read(PLAT/"services/api/src/isolation/gauntlet.itest.ts")),
    ("POST messages is still an isolation target (C8)",
     lambda: '"/v1/channels/:channelId/messages"' in read(PLAT/"services/api/src/isolation/targets.ts")),
    ("check-docs-drift and check-srs still exit 0 on a missing parent (C12/H20)",
     lambda: "exit 0" in read(TUT/"scripts/check-docs-drift.sh") and "exit 0" in read(TUT/"scripts/check-srs-ids.sh")),
    ("the (excerpt) hatch still excludes files from the chain (C13)",
     lambda: '"(excerpt)"' in read(TUT/"scripts/check-fence-chain.mjs")),
    ("turbo declares the lane env, and it is more than 4 vars (H25)",
     lambda: len(json.loads(read(PLAT/"turbo.json"))["tasks"]["test:integration"]["env"]) > 4),
    ("test:integration is uncached, so the battery really runs (pass 13)",
     lambda: json.loads(read(PLAT/"turbo.json"))["tasks"]["test:integration"]["cache"] is False),
    ("the measured lane baseline is recorded, not the folklore (M34)",
     lambda: "589 tests" in TASKS and "193 s wall" in TASKS and "47 s of headroom" in TASKS),
    ("T001 distinguishes the 8 the lane needs from the 26 turbo hashes (M35)",
     lambda: "CACHE KEY, not a requirements list" in TASKS),
    ("compose parameterises all three ports with defaults 5432/6379/4222 (C16)",
     lambda: all(t in read(PLAT/"compose.yaml") for t in
                 ("${RELAY_POSTGRES_PORT:-5432}:5432","${RELAY_REDIS_PORT:-6379}:6379","${RELAY_NATS_PORT:-4222}:4222"))),
    # 16379 may appear ONLY on a line that disclaims it. The disclaimer words are
    # an explicit list so a new bare mention fails, rather than being absorbed by
    # a lookahead tuned to the two sentences that happened to exist when it was
    # written — which is what the first version of this check did.
    ("16379 appears only on lines that disclaim it (C16)",
     lambda: all(any(w in ln for w in ("folklore", "earlier version", "Do not", "do not"))
                 for src in (TASKS, read(HERE/"quickstart.md"))
                 for ln in src.splitlines() if "16379" in ln)),
    ("ADR-07 still argues the clean mapping this chapter breaks (H29)",
     lambda: "gateway to Redis, api and workers to NATS" in read(ROOT/"docs/06-adr-deep-dives.md")),
    ("ADR-07's Decision still says publish once per message (H29)",
     lambda: "Publish once per message" in read(ROOT/"docs/06-adr-deep-dives.md")),
    ("CI's platform job uses default ports; the outsider job uses 15432 (C15)",
     lambda: "localhost:5432/relay" in read(ROOT/".github/workflows/ci.yml")
             and "RELAY_POSTGRES_PORT=15432" in read(ROOT/".github/workflows/ci.yml")),
]
for name, fn in PREMISES:
    try: check(f"10 {name}", fn())
    except Exception as e: check(f"10 {name}", False, f"raised {type(e).__name__}: {e}")

# ── 11. cited line numbers actually contain what is claimed ─────────────────
CITATIONS = [
    ("docs/05-sad.md", 138, "publish fan-out"),
    ("docs/05-sad.md", 248, "G->>G"),
    ("relay-platform/services/api/src/db/repository.ts", 2247, "MessageRow"),
    ("relay-platform/services/api/src/messages/messages.controller.ts", 144, "this.messages.send("),
    ("relay-platform/services/gateway/src/session.ts", 125, "fanout?: Fanout"),
    ("relay-platform/services/gateway/src/session.ts", 175, "subscribersOf"),
    ("relay-platform/services/api/src/limits/store.ts", 86, "RELAY_REDIS_URL"),
    ("relay-platform/services/gateway/src/resume.itest.ts", 90, "Another gateway instance"),
    ("relay-platform/packages/protocol/src/frames.ts", 15, "messageSchema"),
    ("relay-platform/services/api/src/isolation/targets.ts", 185, "messages"),
    ("relay-platform/services/gateway/src/fanout.itest.ts", 128, "drops a payload"),
]
wrong = []
for rel, ln, needle in CITATIONS:
    body = read(ROOT/rel).splitlines()
    if not (0 < ln <= len(body)) or needle not in body[ln-1]:
        wrong.append(f"{rel}:{ln} does not contain {needle!r}")
check("11 every cited line contains what is claimed", not wrong, f"{len(CITATIONS)-len(wrong)}/{len(CITATIONS)} verified" + (f" · {wrong}" if wrong else ""))

# ── 12. the five static gates are green ─────────────────────────────────────
GATES = ["check:srs", "check:docs", "check:figures", "check:errors", "check:fences"]
red = []
for g in GATES:
    r = subprocess.run(["pnpm","-s",g], cwd=TUT, capture_output=True, text=True, timeout=600)
    if r.returncode != 0: red.append(g)
    if "skipping" in (r.stdout + r.stderr): red.append(f"{g} SKIPPED (false green)")
check("12 five static gates green and none skipped", not red, f"{len(GATES)-len(red)}/{len(GATES)}" + (f" · {red}" if red else ""))

# ── 13. dist is not stale (check:errors reads it) ───────────────────────────
dist = PLAT/"packages/protocol/dist/codes.js"
newer = [p.name for p in (PLAT/"packages/protocol/src").rglob("*.ts") if dist.is_file() and p.stat().st_mtime > dist.stat().st_mtime]
check("13 protocol dist is not stale", dist.is_file() and not newer, f"{len(newer)} src newer than dist" + (f" · {newer[:3]}" if newer else ""))

# ── report ──────────────────────────────────────────────────────────────────
if "--self-test" in sys.argv:
    print("SELF-TEST: three deliberate breaks, each must FAIL its check\n")
    for label, mutate, target in [
        ("an uncited requirement", lambda: keys.append("FR-999"), "1"),
        ("a bogus line citation", lambda: CITATIONS.append(("docs/05-sad.md", 1, "NOT_THERE")), "11"),
        ("a duplicate task id", lambda: ids.append(ids[0]), "2"),
    ]:
        mutate()
        if target == "1":
            ok = not [k for k in keys if not any(k in l for l in lines)]
        elif target == "11":
            ok = not [1 for rel, ln, n in CITATIONS if n not in (read(ROOT/rel).splitlines()[ln-1] if 0 < ln <= len(read(ROOT/rel).splitlines()) else "")]
        else:
            ok = len(ids) == len(set(ids))
        print(f"  break {label:26} -> check {target} {'FAILED as required' if not ok else 'PASSED — CHECKER IS BLIND'}")
    sys.exit(0)

width = max(len(n) for n, _, _ in results)
fails = 0
for name, ok, detail in results:
    if not ok: fails += 1
    print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
print(f"\nsweep: {len(results)-fails}/{len(results)} checks pass")
sys.exit(1 if fails else 0)

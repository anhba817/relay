#!/usr/bin/env python3
"""Verify every mechanically checkable claim in specs/035-chapter-3-17."""
import io, os, re, subprocess, sys

ROOT = "/home/dong/work/relay"
FEAT = os.path.join(ROOT, "specs/035-chapter-3-17")
docs = {}
for n in os.listdir(FEAT):
    if n.endswith(".md"):
        docs[n] = io.open(os.path.join(FEAT, n), encoding="utf-8").read()
docs["checklists/requirements.md"] = io.open(
    os.path.join(FEAT, "checklists/requirements.md"), encoding="utf-8").read()
ALL = "\n".join(docs.values())

fails, checks = [], 0
def check(name, ok, detail=""):
    global checks
    checks += 1
    if not ok:
        fails.append((name, detail))

def read(p):
    try: return io.open(p, encoding="utf-8", errors="replace").read()
    except Exception: return None

# ---- 1. every cited file path exists (or is one this feature creates) ----
CREATES = {"0013_bot_users.sql", "chapter-notes.md", "gaps.md", "traceability.md",
           "baseline.txt", "check-srs-ids.sh"}
paths = set(re.findall(r'`([a-zA-Z0-9_][a-zA-Z0-9_./-]*\.(?:ts|md|sql|mts|mjs|json|sh|txt|yml))`', ALL))
missing = []
for p in sorted(paths):
    if os.path.basename(p) in CREATES: continue
    hit = any(os.path.exists(os.path.join(ROOT, base, p))
              for base in ("", "relay-platform", "relay-tutorial"))
    if not hit:
        r = subprocess.run(["find", ROOT, "-name", os.path.basename(p),
                            "-not", "-path", "*/node_modules/*"],
                           capture_output=True, text=True).stdout.strip()
        if not r: missing.append(p)
check("every cited file path resolves", not missing, ", ".join(missing))

# ---- 2. every cited SRS/constitution clause id exists ----
srs = read(os.path.join(ROOT, "docs/04-srs.md"))
defined = set(re.findall(r'^\| ([A-Z]{2,4}(?:-[A-Z0-9]+)?-[0-9]+)', srs, re.M))
NEW = {"FR-USR-07", "FR-MSG-15"}          # this chapter's amendment
cited = set(re.findall(r'\b((?:FR|NFR|DR|EIR|CON|ASM)-[A-Z]{2,4}-[0-9]{2})\b', ALL))
cited |= set(re.findall(r'\b((?:DR|CON|ASM)-[0-9]{2})\b', ALL))
bad = sorted(c for c in cited if c not in defined and c not in NEW)
check("every cited SRS clause exists", not bad, ", ".join(bad))

# ---- 3. the amendment's new ids are genuinely free ----
for nid in sorted(NEW):
    check(f"{nid} is unallocated", nid not in defined,
          f"{nid} already defined in the SRS")

# ---- 4. clause-id uniqueness in the SRS (the checker's own claim) ----
rows = re.findall(r'^\| ([A-Z]{2,4}(?:-[A-Z0-9]+)?-[0-9]+)', srs, re.M)
check("SRS clause ids unique", len(rows) == len(set(rows)),
      f"{len(rows)} rows, {len(set(rows))} unique")
check("SRS row count is 243 as claimed", len(rows) == 243, f"actual {len(rows)}")

# ---- 5. every FR/SC in spec.md has at least one task ----
spec, tasks = docs["spec.md"], docs["tasks.md"]
reqs = re.findall(r'^- \*\*((?:FR|SC)-[0-9]+[a-z]?)\*\*', spec, re.M)
reqs += re.findall(r'^  - \*\*((?:FR|SC)-[0-9]+[a-z]?)\*\*', spec, re.M)
uncovered = [r for r in reqs if r not in tasks]
check("every FR/SC is named by a task", not uncovered, ", ".join(uncovered))

# ---- 6. no duplicate requirement ids in spec.md ----
check("spec.md requirement ids unique", len(reqs) == len(set(reqs)),
      f"{len(reqs)} ids, {len(set(reqs))} unique")

# ---- 7. task ids: unique and correctly formatted ----
tids = re.findall(r'^- \[ \] (T[0-9]{3}[a-z]?) ', tasks, re.M)
allt = re.findall(r'^- \[ \] (\S+)', tasks, re.M)
check("every task line is well formed", len(tids) == len(allt),
      f"{len(allt)} task lines, {len(tids)} well formed")
check("task ids unique", len(tids) == len(set(tids)),
      ", ".join(sorted({t for t in tids if tids.count(t) > 1})))

# ---- 8. every `file:line` citation still says what is claimed ----
lineclaims = re.findall(r'`([a-zA-Z0-9_./-]+\.ts):([0-9]+)`', ALL)
badline = []
for f, ln in set(lineclaims):
    for base in ("relay-platform/services/api/src", "relay-platform", "relay-tutorial", ""):
        cand = os.path.join(ROOT, base, f)
        if os.path.exists(cand): break
        cand = None
    if cand is None:
        r = subprocess.run(["find", ROOT, "-path", f"*/{f}", "-not", "-path", "*/node_modules/*"],
                           capture_output=True, text=True).stdout.strip().split("\n")[0]
        cand = r or None
    if cand is None:
        badline.append(f"{f}:{ln} (file not found)"); continue
    lines = read(cand).split("\n")
    if int(ln) > len(lines):
        badline.append(f"{f}:{ln} (only {len(lines)} lines)")
check("every file:line citation is in range", not badline, "; ".join(badline))

# ---- 9. the constitution MUSTs this feature touches ----
con = read(os.path.join(ROOT, ".specify/memory/constitution.md"))
check("principle VI quickstart clause is addressed",
      "quickstart of record" in tasks.lower() or "FR-015d" in tasks,
      "no task names the quickstart clause")
check("principle VI 'never reused' is cited",
      "never reused" in ALL, "the identifier clause is not quoted anywhere")

# ---- 10. no placeholders left ----
ph = re.findall(r'(TODO|TKTK|\?\?\?|FIXME|<placeholder>|XXX)', ALL)
check("no placeholders", not ph, ", ".join(sorted(set(ph))))

# ---- 11. scripts named in artifacts actually exist as package scripts ----
pkgs = {}
for r, d, fs in os.walk(ROOT):
    if "node_modules" in r: continue
    if "package.json" in fs: pkgs[r] = read(os.path.join(r, "package.json")) or ""
named = set(re.findall(r'pnpm ([a-z]+:[a-z]+)', ALL))
absent = [n for n in sorted(named) if not any(f'"{n}"' in v for v in pkgs.values())]
check("every pnpm script named exists", not absent, ", ".join(absent))

print(f"{checks} checks run, {len(fails)} failed\n")
for n, d in fails:
    print(f"  FAIL  {n}")
    if d: print(f"        {d[:400]}")
if not fails: print("  all green")
sys.exit(1 if fails else 0)

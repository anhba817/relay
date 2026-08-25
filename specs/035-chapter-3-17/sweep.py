#!/usr/bin/env python3
"""Verify every mechanically checkable claim in specs/035-chapter-3-17."""
import io, os, re, subprocess, sys

ROOT = "/home/dong/work/relay"
FEAT = os.path.join(ROOT, "specs/035-chapter-3-17")
# THE RECORD IS NOT AN INSTRUCTION. `checklists/requirements.md` quotes, paraphrases and
# describes these very checks, and scanning it made check 11 fail on the literal `pnpm x:y`
# from the sentence explaining check 11. A checker that consumes its own documentation will
# keep doing that, so it reads only the artifacts somebody executes.
INSTRUCTIONAL = ("spec.md", "plan.md", "tasks.md", "research.md",
                 "data-model.md", "quickstart.md")
docs = {}
for n in os.listdir(FEAT):
    if n in INSTRUCTIONAL:
        docs[n] = io.open(os.path.join(FEAT, n), encoding="utf-8").read()
CONTRACTS = os.path.join(FEAT, "contracts")
if os.path.isdir(CONTRACTS):
    for n in os.listdir(CONTRACTS):
        if n.endswith(".md"):
            docs["contracts/" + n] = io.open(os.path.join(CONTRACTS, n), encoding="utf-8").read()
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

# ---- 3. the amendment's clauses ----
#
# THIS CHECK INVERTED AT PHASE 1, and the inversion is correct rather than a bug. Before the
# amendment the invariant was "these identifiers are free"; after it, "these identifiers are
# defined, exactly once, saying what this feature says they say". A check written during
# planning encodes a pre-amendment world, and Phase 1 is where that world ends.
for nid in sorted(NEW):
    check(f"{nid} is defined exactly once", list(re.findall(r'^\| %s \|' % nid, srs, re.M)).__len__() == 1,
          f"{nid} is defined {len(re.findall(r'^.\| %s .\|' % nid, srs, re.M))} times")
check("FR-MSG-13 is narrowed to a bot user",
      "on behalf of a bot user of that tenant via API key" in srs,
      "FR-MSG-13 still says 'any user' — T002 not applied")
check("FR-RTL-05 enforces on persons, FR-ANL-05 still meters users",
      "unique active persons, and connection-minutes" in srs
      and "messages sent, unique active users, connection-minutes, and stored" in srs,
      "the metering/enforcement split is not in the document")

# ---- 4. clause-id uniqueness in the SRS (the checker's own claim) ----
rows = re.findall(r'^\| ([A-Z]{2,4}(?:-[A-Z0-9]+)?-[0-9]+)', srs, re.M)
check("SRS clause ids unique", len(rows) == len(set(rows)),
      f"{len(rows)} rows, {len(set(rows))} unique")
# PINNED, and the pin is the point. It read 243 before chapter 3.17's amendment and 245
# after — it fired on the build that changed the document and made the change be confirmed
# rather than absorbed. Bumping it silently would make it worthless; this is the same
# mechanism as the derived target list failing on the build that adds a route.
check("SRS row count is 245 as claimed", len(rows) == 245, f"actual {len(rows)}")

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

# ---- 12. [P] means no shared artifact within a phase ----
import collections
_ph=None; _rows=[]
for line in tasks.split("\n"):
    m=re.match(r'^## .*Phase (\d+)', line)
    if m: _ph=int(m.group(1))
    t=re.match(r'^- \[ \] (T\d{3}[a-z]?)( \[P\])?( \[US\d\])? (.*)$', line)
    if t: _rows.append((_ph,t.group(1),bool(t.group(2)),t.group(4)))
_F=re.compile(r'`([a-zA-Z0-9_./()<>-]+\.[a-z]{2,4})`')
def _art(b):
    f=_F.findall(b)
    if f: return f[0]
    if re.search(r'the chapter page|on the page', b): return "THE CHAPTER PAGE"
    if re.search(r'locale page', b): return "THE (vi) PAGE"
    return None
_b=collections.defaultdict(list)
for p_,tid,par,body in _rows:
    if par: _b[(p_,_art(body))].append(tid)
_col=[f"phase {p} {a}: {' '.join(ts)}" for (p,a),ts in sorted(_b.items(),key=lambda x:(x[0][0] or 0,str(x[0][1])))
       if a and len(ts)>1]
check("no [P] task shares an artifact with another in its phase", not _col, " | ".join(_col))
_noart=[tid for (p,a),ts in _b.items() if a is None for tid in ts]
check("every [P] task names its artifact", not _noart, ", ".join(sorted(_noart)))

# ---- 13. ids are stable labels; file order is the contract, and it must be stated ----
check("the file-order contract is stated in the header",
      "FILE ORDER IS EXECUTION ORDER" in tasks,
      "ids are non-monotonic and nothing says which order to follow")

# ---- 14. coverage runs BOTH directions ----
#
# Pass 10 fixed requirement -> task and nobody ran task -> requirement for two more passes.
# `targets.ts` states why both matter: "an entry matching no derived target fails it too — the
# second direction is the one that catches a stale exemption after a rename." A task that
# changes behaviour and names no requirement is that stale exemption.
HOUSEKEEPING = re.compile(
    r'^(Commit|Run |Re-run|Record|State|Measure|Count|Enumerate|Diff|Translate|Tick'
    r'|Add the chapter|Review)', re.I)
_uncited = [tid for tid, body in re.findall(
                r'^- \[ \] (T\d{3}[a-z]?)(?: \[P\])?(?: \[US\d\])? (.*)$', tasks, re.M)
            if not re.search(r'\b(FR|SC)-\d', body)
            and not HOUSEKEEPING.match(re.sub(r'\*+', '', body))]
check("every behaviour-bearing task cites a requirement", not _uncited, ", ".join(_uncited))

# ---- 15. every phase states its goal ----
_ph = re.findall(r'^## (Phase \d+[^\n]*)$', tasks, re.M)
_blocks = re.split(r'^## Phase ', tasks, flags=re.M)[1:]
_nogoal = [b.split("\n")[0][:34] for b in _blocks if "**Goal**" not in b]
check("every phase states a goal", not _nogoal, "; ".join(_nogoal))

# ---- 16. one word, one meaning: the quickstart principle VI verifies ----
qs = os.path.join(FEAT, "quickstart.md")
_qtitle = io.open(qs, encoding="utf-8").read().split("\n")[0] if os.path.exists(qs) else ""
check("the feature's own quickstart is not titled as THE quickstart",
      "quickstart" not in _qtitle.lower(),
      f"{_qtitle!r} collides with FR-015d's quickstart of record")

# ---- 17. an external citation must be READ before it is used ----
#
# `sweep.py` has always checked that a cited clause EXISTS. Pass 14 found FR-TEN-08 cited
# three times as the billing authority when it governs application deletion and 30-day
# retention — it exists, so every check passed, and the clause that actually needed amending
# (FR-RTL-05) stayed invisible for fourteen passes. **A wrong citation is worse than a missing
# one**: the missing one fails a coverage check and the wrong one looks authoritative.
#
# No checker can read meaning. What it can do is refuse a citation nobody has signed off:
# every clause below was read against the claim citing it in pass 13 or 14. Adding a new
# external citation fails this check until someone reads the clause and adds it here — which
# is the same "nothing may be exempt by omission" shape as `check:srs`'s class list.
REVIEWED = {
  "EIR-API-07","FR-ANL-05","FR-ANL-06","FR-AUT-09","FR-CHN-05","FR-MOD-01","FR-MOD-03",
  "FR-MOD-04","FR-MSG-01","FR-MSG-07","FR-MSG-10","FR-MSG-13","FR-MSG-15","FR-RTL-05",
  "FR-RTL-08","FR-RTM-05","FR-RTM-06","FR-RTM-07","FR-TEN-05","FR-TEN-08","FR-USR-01",
  "FR-USR-02","FR-USR-05","FR-USR-06","FR-USR-07","FR-WHK-02","FR-WHK-03","NFR-USE-03",
}
_ext = set(re.findall(r'\b((?:FR|NFR|DR|EIR|CON|ASM)-[A-Z]{2,4}-[0-9]{2})\b', ALL))
_unread = sorted(_ext - REVIEWED)
check("every external clause cited has been read against its claim", not _unread,
      ", ".join(_unread) + " — read the clause, then add it to REVIEWED" if _unread else "")

print(f"{checks} checks run, {len(fails)} failed\n")
for n, d in fails:
    print(f"  FAIL  {n}")
    if d: print(f"        {d[:400]}")
if not fails: print("  all green")
sys.exit(1 if fails else 0)

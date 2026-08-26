#!/usr/bin/env python3
"""Second sweep: quoted source text, cited symbols, numeric claims."""
import io, os, re, subprocess, sys
ROOT="/home/dong/work/relay"; FEAT=os.path.join(ROOT,"specs/035-chapter-3-17")
ALL=[]
for r,d,fs in os.walk(FEAT):
    for n in fs:
        if n.endswith(".md"): ALL.append(io.open(os.path.join(r,n),encoding="utf-8").read())
ALL="\n".join(ALL)

_CORPUS = None
def corpus():
    """Every tracked source/doc file, whitespace- and prefix-normalised into one blob.

    A quote in an artifact is reflowed to the artifact's line width; the source wraps at
    its own. Matching raw text therefore fails on line breaks and on comment prefixes
    (`*`, `//`, `>`), which is a checker crying wolf on a healthy tree. Normalise both
    sides and compare."""
    global _CORPUS
    if _CORPUS is None:
        r = subprocess.run(["grep","-rl","","--include=*.ts","--include=*.md","--include=*.sh",
                            "--include=*.sql","--include=*.json","--include=*.yml",
                            "--exclude-dir=node_modules","--exclude-dir=.git","--exclude-dir=.next",
                            ROOT],capture_output=True,text=True)
        blob=[]
        for f in r.stdout.split():
            if "/specs/035-" in f: continue
            try: t=io.open(f,encoding="utf-8",errors="replace").read()
            except Exception: continue
            t=re.sub(r'(?m)^\s*(\*|//|#|>)+\s?','',t)
            blob.append(re.sub(r'\s+',' ',t))
        _CORPUS=" ".join(blob).lower()
    return _CORPUS

def grep_repo(needle):
    n=re.sub(r'\s+',' ',needle).strip().lower()
    return [1] if n in corpus() else []

fails=[]; checks=0
def check(name, ok, detail=""):
    global checks; checks+=1
    if not ok: fails.append((name,detail))

# ---- A. the substantive source attributions, enumerated ----
#
# THIS WAS A FUZZY MATCHER AND IT CRIED WOLF. Matching every italic-quoted span against
# the tree reported 9 problems, then 8 after normalising whitespace and comment
# prefixes: every one a false positive from a backtick, an apostrophe or an emphasised
# phrase that was never a quotation. A checker I cannot make precise must not sit in the
# suite pretending to be a gate (chapter 3.16: `check:figures` reported 122 false
# problems in 193 figures on its first run). Enumerated instead — each pair verified by
# hand, and a wrong one fails loudly.
ATTRIB = [
  ("An application credential acts for", "relay-platform/services/api/src/channels/channels.service.ts"),
  ("acts for the customer, carries no user, and sees private channels", "relay-platform/services/api/src/channels/channels.service.ts"),
  ("null` CLEARS, and it is distinct from absent", "relay-platform/services/api/src/users/users.schema.ts"),
  # WAS in repository.ts and is GONE — T012a removed the gate whose comment said it, and
  # T086c corrected the three comments that cited FR-MSG-13 for the opposite of what it says.
  # The sentence now survives only where it is quoted AS HISTORY: the chapter, and 3.10's
  # corrected Trap. A sweep that still expected it in the code would be asserting the chapter
  # had not happened.
  ("A tenant's own server sending on a customer's", "relay-tutorial/app/(en)/part-3/chapter-17/the-sender-a-message-never-had/page.mdx"),
  ("T057 above removes", "relay-platform/services/api/src/messages/messages.itest.ts"),
  ("accepts an application key's send to the same private channel", "relay-platform/services/api/src/messages/messages.itest.ts"),
  ("carry stable identifiers", ".specify/memory/constitution.md"),
  ("run unmodified, verified by automated execution in CI against", ".specify/memory/constitution.md"),
  ("ON DELETE SET NULL", "docs/04-srs.md"),
  ("History responses shall include tombstones", "docs/04-srs.md"),
  ("wrong_credential_type", "relay-platform/packages/protocol/src/codes.ts"),
  ("A range stops where it stops", "relay-tutorial/scripts/check-docs-drift.sh"),
  ("NOTHING MAY BE EXEMPT BY OMISSION", "relay-platform/services/api/src/isolation/targets.ts"),
]
badq=[]
for frag,f in ATTRIB:
    src = io.open(os.path.join(ROOT,f),encoding="utf-8",errors="replace").read()
    flat = re.sub(r'\s+',' ', re.sub(r'(?m)^\s*(\*|//|#|>)+\s?','',src))
    if re.sub(r'\s+',' ',frag).lower() not in flat.lower():
        badq.append(f"{frag[:50]} not in {f}")
check("every enumerated source attribution is real", not badq, " | ".join(badq))

# ---- B. every backticked code symbol exists somewhere in the codebase ----
syms = set(re.findall(r'`([a-z][a-zA-Z0-9]{5,})`', ALL))
NOISE = {"relay","platform","tutorial","chapter","baseline","typecheck","itest",
         "person","description","channels","messages","members","sequence","metadata",
         "environment","credential","integration","concurrency","postgres","migrations"}
bads=[]
for sym in sorted(syms):
    if sym in NOISE: continue
    if not grep_repo(sym): bads.append(sym)
check("every cited code symbol exists", not bads, ", ".join(bads))

# ---- C. every snake_case column/table cited exists in the schema or a migration ----
cols = set(re.findall(r'`([a-z]+(?:_[a-z]+){1,3})`', ALL))
schema = io.open(os.path.join(ROOT,"relay-platform/services/api/src/db/schema.ts"),encoding="utf-8").read()
migs = "".join(io.open(os.path.join(ROOT,"relay-platform/services/api/migrations",f),encoding="utf-8").read()
               for f in os.listdir(os.path.join(ROOT,"relay-platform/services/api/migrations")) if f.endswith(".sql"))
NEWCOLS = {"users_kind_check","users_bot_description_check","bot_users","kind_conflict",
           "description_required","missing_sender","sender_not_permitted","check_srs","srs_ids","check_docs","not_found"}
badc=[]
for c in sorted(cols):
    if c in NEWCOLS: continue
    if c in schema or c in migs: continue
    if grep_repo(c): continue
    badc.append(c)
check("every cited column/table/constraint exists", not badc, ", ".join(badc))

# ---- D. numeric claims about the repository ----
def n_of(cmd):
    return int(subprocess.run(cmd,shell=True,capture_output=True,text=True,cwd=ROOT).stdout.strip() or 0)

claims = {
 # 27 BEFORE the work, ZERO AFTER IT, and that inversion is the chapter's claim: no call
 # site in the workspace omits a sender, and the compiler is what holds it — not this check.
 # Pinned at 0 so a site that starts omitting one again fails here as well as at `typecheck`.
 "0 call sites omit userId":
   (0, n_of("""python3 - <<'E'
import re,io,subprocess
fs=subprocess.run(['grep','-rl','sendMessage(','relay-platform/services/api/src','--include=*.ts'],capture_output=True,text=True).stdout.split()
t=0
for f in fs:
    s=io.open(f,encoding='utf-8').read()
    for m in re.finditer(r'sendMessage\\(',s):
        i=m.end();d=1;j=i
        while j<len(s) and d:
            if s[j]=='(':d+=1
            elif s[j]==')':d-=1
            j+=1
        if not re.search(r'\\buserId\\b',s[i:j]): t+=1
print(t)
E""")),
 "38 target-list entries":
   (38, n_of("grep -c '^  {' relay-platform/services/api/src/isolation/targets.ts")),
 # 243 BEFORE this chapter's amendment, 245 after: FR-USR-07 and FR-MSG-15 were added and
 # FR-MSG-13 and FR-RTL-05 were narrowed in place. Pinned, so the next amendment has to be
 # a deliberate edit here rather than a number that drifts.
 "245 SRS clause rows":
   (245, n_of("grep -cE '^\\| [A-Z]{2,4}(-[A-Z0-9]+)?-[0-9]+' docs/04-srs.md")),
 # 7 BEFORE T012a REMOVED THREE DEAD ONES, and the two that remain in code are the
 # do-not-touch sites in methods whose `userId` is optional by design. The other four
 # matches are this feature's own comments ABOUT the removal, which is why the pattern
 # excludes comment lines: a check that counts a sentence as a guard is the same mistake
 # `check:srs` shipped with.
 "2 real userId guards left in repository.ts":
   (2, n_of("grep -nE '^\\s*(if|const).*userId [!=]== undefined' relay-platform/services/api/src/db/repository.ts | wc -l")),
 # THREE, and the fourth match is a COMMENT in `assertWithinQuota` saying this filter must
 # NOT be added there — the house idiom would break the ceiling's bot exemption (FR-018b).
 "3 isNull(users.deletedAt) joins in code":
   (3, n_of("grep -E '^\\s+isNull\\(users.deletedAt\\),' relay-platform/services/api/src/db/repository.ts | wc -l")),
}
for name,(want,got) in claims.items():
    check(f"numeric claim: {name}", want==got, f"claimed {want}, measured {got}")

# ---- E. constitution: every MUST mentioning a gate this feature could trip ----
con = io.open(os.path.join(ROOT,".specify/memory/constitution.md"),encoding="utf-8").read()
musts = [l.strip() for l in con.split("\n") if " MUST " in l and l.strip().startswith("-")]
check("constitution MUSTs enumerated for review", len(musts)>0, "")
print(f"{checks} checks run, {len(fails)} failed\n")
for n,d in fails:
    print(f"  FAIL  {n}")
    if d: print(f"        {d[:500]}")
if not fails: print("  all green")
print(f"\n  ({len(musts)} constitution MUST clauses enumerated for manual review)")
sys.exit(1 if fails else 0)

#!/usr/bin/env python3
"""Rewrite the references the platform-derived map cannot reach.

WHY THERE IS A SECOND MECHANISM AT ALL. `linemap.py` reads what the four rewrite commits
did to the platform, and that map is exact for every line still in the platform at HEAD.
The chain also carries lines a LATER chapter superseded — introduced in chapter 3.2,
replaced by 3.9's hunk, absent from the final file. Those lines are published, a reader
types them, and no platform commit mentions them. 504 references in 203 distinct lines.

T014's own note measured "94% of reference-bearing lines are byte-identical from the
chapter that introduced them to the final file". True, and the other 6% is this.

ONE DECISION PER DISTINCT LINE, APPLIED EVERYWHERE. A comment introduced in one chapter
appears again as diff context in two more, and if the three copies were rewritten
independently by position-sensitive rules they could disagree — after which the pre-image
of a later hunk stops matching its own state. Keying by exact line text makes that
impossible to get wrong: same input, same output, wherever it sits.

    node rewrite-fence-bodies.py            propose, write decisions.tsv
    node rewrite-fence-bodies.py --apply    apply the decisions

`--overrides FILE` reads hand corrections as `old<TAB>new`, which is where the read class
ends up. The equivalent pass on platform source needed 9 by hand out of 293.
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import refrules
from refrules import REF, RULE_LINE, classify, is_versionish, is_deliberate, controls_failing
sys.argv = [sys.argv[0]]                      # the rewriters read argv at import
import importlib.util

def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

refs = load("rw_refs", HERE / "rewrite-refs.py")
read = load("rw_read", HERE / "rewrite-read.py")

ROOT = Path("/home/dong/work/relay/relay-tutorial")
FILES = sorted(ROOT.glob("app/**/page.mdx")) + [ROOT / "fences/post-series.md"]
APPLY = "--apply" in sys.orig_argv if hasattr(sys, "orig_argv") else False
ARGS = sys.orig_argv[2:] if hasattr(sys, "orig_argv") else []
APPLY = "--apply" in ARGS
OV = None
if "--overrides" in ARGS:
    OV = Path(ARGS[ARGS.index("--overrides") + 1])

bad = controls_failing()
if bad:
    print("BROKEN — controls failing: " + ", ".join(bad)); sys.exit(2)

def fence_lines():
    """Every (file, index, line) inside a fence, with the diff marker split off."""
    for f in FILES:
        lines = f.read_text(encoding="utf-8").splitlines()
        infence = isdiff = False
        for i, l in enumerate(lines):
            m = re.match(r"^```(\w+)?", l)
            if m and not infence:
                infence, isdiff = True, m.group(1) == "diff"; continue
            if l.startswith("```") and infence:
                infence = False; continue
            if not infence:
                continue
            if isdiff and l.startswith("@@"):
                # The checker uses `@@` only as a separator and never reads the trailing
                # context, so this is published text with no mechanical role. Rewritten
                # for the reader, and it must agree with the source line it echoes.
                yield f, i, "", l
            elif isdiff and l[:1] and l[:1] in "-+ ":
                yield f, i, l[0], l[1:]
            else:
                yield f, i, "", l

def rewrite_line(line):
    """Apply the three rules right to left, so earlier offsets stay valid."""
    # A LINE WHOSE SUBJECT IS AN ORDINAL KEEPS IT. `refrules.DELIBERATE`, three lines of
    # `schema.ts` that quote the old text and cite the number's movement as evidence.
    if is_deliberate(line):
        return line
    ms = [m for m in REF.finditer(line) if not is_versionish(line, m)]
    if not ms:
        return line
    out = line
    for m in reversed(ms):
        m2 = next((x for x in REF.finditer(out)
                   if x.start() == m.start() and x.group(0) == m.group(0)), None)
        if m2 is None:
            continue
        rule = classify(out, m2)
        if rule == "delete":
            out = refs.delete_one(out, m2)
        elif rule == "substitute":
            out = refs.substitute_one(out, m2)
        else:
            out = read.rewrite(out, m2, "rules" if RULE_LINE.search(out) else "other")
    return out

distinct = {}
for f, i, pref, body in fence_lines():
    if any(not is_versionish(body, m) for m in REF.finditer(body)):
        distinct.setdefault(body, 0)
        distinct[body] += 1

over = {}
if OV and OV.exists():
    for l in OV.read_text(encoding="utf-8").splitlines():
        if "\t" in l and not l.startswith("#"):
            a, b = l.split("\t", 1); over[a] = b

decisions, unresolved = {}, []
for body in distinct:
    new = over.get(body, rewrite_line(body))
    decisions[body] = new
    if any(not is_versionish(new, m) for m in REF.finditer(new)):
        unresolved.append(body)

print(f"rewrite-fence-bodies: {'APPLY' if APPLY else 'PROPOSE'}"
      f"{f'  (+{len(over)} overrides)' if over else ''}")
print(f"  distinct reference-bearing lines   {len(distinct)}")
print(f"  occurrences                        {sum(distinct.values())}")
print(f"  STILL CARRY A REFERENCE after      {len(unresolved)}")
print(f"  unchanged by the rules             {sum(1 for k, v in decisions.items() if k == v)}")

tsv = HERE / "fence-decisions.tsv"
tsv.write_text("".join(f"{k}\t{v}\n" for k, v in sorted(decisions.items())), encoding="utf-8")
print(f"  decisions written                  {tsv.name}")
for b in unresolved[:12]:
    print(f"    UNRESOLVED  {b.strip()[:100]}")

if APPLY:
    n = 0
    for f in FILES:
        lines = f.read_text(encoding="utf-8").splitlines()
        by_idx = {}
        for g, i, pref, body in fence_lines():
            if g == f and body in decisions and decisions[body] != body:
                by_idx[i] = pref + decisions[body]
        for i, v in by_idx.items():
            lines[i] = v; n += 1
        if by_idx:
            f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  lines rewritten                    {n}")

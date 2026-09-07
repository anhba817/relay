#!/usr/bin/env python3
"""Repair the two damage classes the corrected rules would not have produced.

A REJECTED DESIGN FIRST, BECAUSE IT NEARLY REACHED THE TREE. The first version re-derived
every rewritten line from its pre-image through the corrected rules and treated any
difference from the tree as damage. It reported 104 lines in 57 files — and reading them
showed the tree was RIGHT and the re-derivation wrong:

    tree     describe("the attachment shape (FR-002, FR-003b, FR-020)"
    "repair" describe("the attachment shape (FR-002, FR-003b (3.24), FR-020 (3.24))"
    tree     // What the cap costs at the door (NFR-PERF-01).
    "repair" // What the cap costs at the door (, NFR-PERF-01).

The original work was a PIPELINE — two rule passes, the read class in six kinds, nine
lines by hand — and a single function is not equivalent to it. A mismatch therefore says
"one of these two is wrong" and not which. AN ORACLE THAT CANNOT BE WRONG IS THE ONLY
KIND WORTH COMPARING AGAINST, and this one could.

So each class is detected by its own signature IN THE TREE, where the damage is visible
without an oracle:

  1. A DELETED MARKER THAT WAS THE SUBJECT — `// And NOT for the reason the four above
     give.` The pre-image is consulted only to recover the name, not to re-derive the
     line, and the check is that the pre-image's own marker was the sentence subject.

  2. A LOWER-CASE NAME INSIDE AN ALL-CAPS RUN — `* THE LOCK the quota chapter WANTED AND
     COULD NOT HAVE.` Repaired in place by upper-casing the name. No pre-image needed:
     the surrounding case says what it should be.
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import refrules
from refrules import REF, is_versionish
PLAT = HERE.parent.parent / "relay-platform"
APPLY = "--apply" in sys.argv

NAMES = json.load(open(HERE / "subjects.json"))["chapters"]
NAME_OF = {c["was"]: c["name"] for c in NAMES}

# 1 — a comment that now opens on a conjunction
CONJ = re.compile(r"^(\s*(?://+|/\*\*?|\*|--+|#+)\s*)((?i:and|but|so|nor|yet|or)\b)")
# the pre-image shape that produced it: a marker, punctuation, then that conjunction
WAS_SUBJECT = re.compile(r"^\s*[/*\s]*((?i:chapter) 3\.\d{1,2})\s*([.,:;—-])\s*((?i:and|but|so|nor|yet|or))\b")
# 2 — a lower-case name amid capitals
NAME = re.compile(r"\b(the [a-z][a-z-]*(?: [a-z-]+)? (?:chapter|gauntlet|milestone))('s)?\b")

for name, pat, ctl in (("CONJ", CONJ, "  // And NOT for the reason the four above give."),
                       ("WAS_SUBJECT", WAS_SUBJECT, "  // Chapter 3.22, and NOT for the reason"),
                       ("NAME", NAME, "* THE LOCK the quota chapter WANTED")):
    if not pat.search(ctl):
        print(f"BROKEN: {name} does not match its own example"); sys.exit(2)
assert not CONJ.search("  // THE SUBJECT IS A ROW NO METHOD CAN WRITE."), "CONJ too wide"
print("repair-rewrites: all 3 controls fired")

M = json.load(open(HERE / "linemap.json"))["single"]
# damaged line -> the pre-image that produced it, for class 1 only
was = {new: old for old, new in M.items()
       if new is not None and CONJ.search(new) and WAS_SUBJECT.search(old)}

def fix_conj(line):
    old = was[line]
    m = WAS_SUBJECT.search(old)
    ref, punct = m.group(1), m.group(2)
    name = NAME_OF.get("3." + str(refrules.chapter_of(ref)))
    if not name:
        return None
    c = CONJ.match(line)
    opener, conj = c.group(1), c.group(2)
    # THE CASE OF THE RESTORED NAME FOLLOWS THE CLAUSE, not the pre-image's emphasis.
    ahead = re.findall(r"[A-Za-z]{2,}", line[c.end(1):])[:2]
    shout = bool(ahead) and all(w.isupper() for w in ahead)
    n = name.upper() if shout else name[0].upper() + name[1:]
    # AND THE CONJUNCTION GOES BACK TO THE CASE IT HAD. It was capitalised only because
    # deleting the marker made it start the sentence; with a subject in front of it again
    # `The connection-metering chapter, And this is …` is wrong. The pre-image is the
    # faithful source for it, so take it from there rather than lower-casing blindly.
    return f"{opener}{n}{punct if punct != '.' else ','} {m.group(3)}{line[c.end(2):]}"

def fix_case(line):
    out, changed = line, False
    for m in reversed(list(NAME.finditer(line))):
        before = re.findall(r"[A-Za-z]{2,}", out[:m.start()])[-2:]
        after = re.findall(r"[A-Za-z]{2,}", out[m.end():])[:2]
        ctx = before + after
        if len(ctx) >= 2 and all(w.isupper() for w in ctx):
            out = out[:m.start()] + m.group(0).upper() + out[m.end():]
            changed = True
    return out if changed else None

n1 = n2 = files = 0
for f in refrules.platform_files(PLAT):
    lines = f.read_text(encoding="utf-8").split("\n")
    hit = False
    for i, l in enumerate(lines):
        if l in was:
            r = fix_conj(l)
            if r and r != l:
                lines[i] = r; n1 += 1; hit = True
                continue
        r = fix_case(lines[i])
        if r:
            lines[i] = r; n2 += 1; hit = True
    if hit:
        files += 1
        if APPLY:
            f.write_text("\n".join(lines), encoding="utf-8")
        else:
            for i, l in enumerate(f.read_text(encoding="utf-8").split("\n")):
                if l != lines[i]:
                    print(f"  {f.relative_to(PLAT)}:{i+1}\n    -  {l.strip()[:104]}\n    +  {lines[i].strip()[:104]}")

print(f"  class 1  marker was the subject     {n1}")
print(f"  class 2  name amid capitals         {n2}")
print(f"  files {'changed' if APPLY else 'to change'}                      {files}")

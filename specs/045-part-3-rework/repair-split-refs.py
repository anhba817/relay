#!/usr/bin/env python3
"""Repair references that were split across a line break.

`REF` matches within one line, so `That is the bug chapter` / `// 3.12 found (R23)` was
seen as a bare `3.12` — substituted on the second line, with the word `chapter` left
dangling at the end of the first:

    // ... which is chapter
    * The isolation gauntlet's FR-044 hole exactly: a credential mismatch

24 lines in `relay-platform` and 14 in the fences. NOTHING IN THIS FEATURE COULD SEE
THEM: the reference is gone, so no classifier finds it; the line is not damaged in any
way a signature scan knows; and `check:fences` compares the chain to a platform file that
carries the same defect, so it agrees. What found them was asking a different question —
"does any line END on the word `chapter`?" — after a split reference turned up by hand in
`eslint.config.mjs`.

THE RULE. Strip the trailing `chapter` from the first line; if it took an opening
parenthesis with it, that parenthesis moves down to sit against the name. Then the name's
case is decided by what now ends the first line, which is the same test `place_name`
uses — a name mid-sentence is lower-case.
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import refrules

TAIL = re.compile(r"\s*(\(\s*)?(?i:chapters?)\s*$")
NAMED = re.compile(r"^(\s*(?://+|/\*\*?|\*|--+|#+)?\s*)((?:The|the)\s+[a-z][a-z-]*(?:\s+[a-z-]+)?\s+(?:chapter|gauntlet|milestone))")
ENDS_SENTENCE = re.compile(r"[.!?:]\s*\**$")
OPENER_ONLY = re.compile(r"^\s*(?://+|/\*\*?|\*|--+|#+)?\s*$")

for n, p, c in (("TAIL", TAIL, "which is chapter"), ("TAIL-paren", TAIL, "same way (chapter"),
                ("NAMED", NAMED, "* The isolation gauntlet's FR-044 hole")):
    if not p.search(c):
        print(f"BROKEN: {n} does not match its own example"); sys.exit(2)
print("repair-split-refs: all 3 controls fired")

APPLY = "--apply" in sys.argv

def repair(L):
    """In place on a list of lines. Returns the number of pairs repaired."""
    n = 0
    for i in range(len(L) - 1):
        t = TAIL.search(L[i])
        nm = NAMED.match(L[i + 1])
        if not t or not nm:
            continue
        head = L[i][:t.start()]
        paren = t.group(1) is not None
        keep_cap = OPENER_ONLY.match(head) or ENDS_SENTENCE.search(head) or not head.strip()
        name = nm.group(2)
        name = (name[0].upper() + name[1:]) if keep_cap else (name[0].lower() + name[1:])
        L[i] = head
        L[i + 1] = nm.group(1) + ("(" if paren else "") + name + L[i + 1][nm.end(2):]
        n += 1
    return n

targets = [("relay-platform", list(refrules.platform_files(HERE.parent.parent / "relay-platform")))]
tut = HERE.parent.parent / "relay-tutorial"
targets.append(("relay-tutorial", sorted(tut.glob("app/**/page.mdx")) + [tut / "fences/post-series.md"]))

for label, files in targets:
    tot, nf = 0, 0
    for f in files:
        L = f.read_text(encoding="utf-8").split("\n")
        before = L[:]
        k = repair(L)
        if k:
            tot += k; nf += 1
            if APPLY:
                f.write_text("\n".join(L), encoding="utf-8")
            else:
                for a, b in zip(before, L):
                    if a != b:
                        print(f"    -  {a.rstrip()[:104]}\n    +  {b.rstrip()[:104]}")
    print(f"  {label}: {tot} pairs in {nf} files")

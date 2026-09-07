#!/usr/bin/env python3
"""Every Part-3 ordinal still inside a fence body, and every hunk the rewrite emptied.

TWO CLASSES THE COMMIT-DERIVED MAP CANNOT REACH, and both were found by `check:fences`
rather than by any scan here.

  A FORM THE PLATFORM NEVER HAD AT HEAD. Chapter 14 introduces a comment reading
  `(chapter 3.12,` and chapter 16 carries a hunk whose ONLY content is correcting it to
  `(chapter 3.14,`. The map is built from the platform's commits, so it knows the second
  form and not the first. This is the mirror of the appendix problem: 5% of platform
  lines appear in no chapter snapshot, and here a chapter line appears in no platform
  file.

  A HUNK WHOSE ONLY PURPOSE WAS THE ORDINAL. Once both sides lose it, the hunk changes
  nothing — and a diff fence that changes nothing is not a diff. It has to be deleted,
  not rewritten, which is why finding these is a separate question from rewriting lines.
"""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
# ONE DEFINITION OF WHAT A REFERENCE IS. A fresh pattern here reported 484 hits
# including `"prettier": "^3.9.6"`, because `\b3\.\d{1,2}\b` matches a version string.
# `refrules.is_versionish` already knew that, and two copies of `classify` disagreeing
# by nine references is why `refrules.py` exists at all.
import refrules
from refrules import REF, classify, is_versionish, is_deliberate, controls_failing

ROOT = Path("/home/dong/work/relay/relay-tutorial")
bad = controls_failing()
if bad:
    print("check-fence-ordinals: BROKEN — controls failing: " + ", ".join(bad))
    sys.exit(2)

FILES = sorted(ROOT.glob("app/**/page.mdx")) + [ROOT / "fences/post-series.md"]
left, empty = [], []

for f in FILES:
    lines = f.read_text(encoding="utf-8").splitlines()
    i, infence, isdiff = 0, False, False
    hunk = None
    def close_hunk():
        if hunk and hunk["minus"] == hunk["plus"] and hunk["minus"]:
            empty.append((f, hunk["at"], hunk["minus"][0][:78]))
    while i < len(lines):
        l = lines[i]
        m = re.match(r"^```(\w+)?", l)
        if m and not infence:
            infence, isdiff = True, m.group(1) == "diff"; hunk = None
            i += 1; continue
        if l.startswith("```") and infence:
            close_hunk(); infence = False; hunk = None
            i += 1; continue
        if infence:
            if isdiff and l.startswith("@@"):
                close_hunk(); hunk = {"at": i + 1, "minus": [], "plus": []}
            elif isdiff and hunk is not None:
                if l.startswith("-"): hunk["minus"].append(l[1:])
                elif l.startswith("+"): hunk["plus"].append(l[1:])
            body = l[1:] if (isdiff and l[:1] and l[:1] in "-+ ") else l
            if is_deliberate(body):
                continue
            for m in REF.finditer(body):
                if is_versionish(body, m):
                    continue
                left.append((f, i + 1, classify(body, m), body.strip()[:92]))
        i += 1

print("check-fence-ordinals: all controls fired")
print(f"  ordinals still inside a fence body   {len(left)}  in {len({x[0] for x in left})} files")
print(f"  hunks the rewrite emptied            {len(empty)}")
from collections import Counter
by = Counter(x[2] for x in left)
for k in ("delete", "substitute", "read"):
    print(f"    {k:12s} {by.get(k, 0)}")
seen = {x[3] for x in left}
for f, n, t in empty:
    print(f"    EMPTY HUNK  {f.relative_to(ROOT)}:{n}  {t}")
print(f"  distinct texts                       {len(seen)}")
print(f"  files                                {len({x[0] for x in left})}")
sys.exit(1 if left or empty else 0)

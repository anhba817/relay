#!/usr/bin/env python3
"""Apply the comment rewrite to every fence body, so the chain lands on the platform.

WHY NOT AN APPENDIX HUNK, WHICH IS WHAT T014's TASK LINE SAID. `fences/post-series.md`
applies AFTER the last chapter. Amending 154 files there leaves every Part 3 chapter
PUBLISHING `// The fixed-window arithmetic (chapter 3.8, research R1).` in its own fence
and stripping it once the reader has finished the book. A reader typing along gets the
ordinal; the gate goes green; FR-008 is satisfied in the platform and defeated in the
thing the platform exists to teach. The convention that every platform change carries an
appendix hunk is feature 044's, and 044 published no chapter.

PROSE IS NOT TOUCHED, and that is deliberate rather than an omission. `data-model.md`:
a chapter may say "chapter 3.4" about a chapter the reader has open, because prose is
republished with the book and a source comment is not. Only fence bodies are rewritten,
which is also why this cannot be a whole-file `sed`.

A DIFF FENCE'S MARKER COMES OFF FIRST AND GOES BACK ON AFTER. A removed line reads
`-// …` and a context line ` // …`; both carry a body the map knows. The interpretation
without a marker is tried first, because a SQL comment is `-- Chapter 3.8 …` and the
first character of that is not a marker.
"""
import json, re, sys
from pathlib import Path

ROOT = Path("/home/dong/work/relay")
M = json.load(open(Path(__file__).parent / "linemap.json"))
SINGLE = M["single"]
RUNS = sorted(M["runs"], key=lambda r: -len(r["old"]))
APPLY = "--apply" in sys.argv

FILES = sorted(ROOT.glob("relay-tutorial/app/(en)/**/page.mdx")) + \
        sorted(ROOT.glob("relay-tutorial/app/(vi)/**/page.mdx")) + \
        [ROOT / "relay-tutorial/fences/post-series.md"]

def split_marker(line, isdiff):
    if not isdiff or line in SINGLE:
        return "", line
    # `"" in "-+ "` is TRUE — the empty string is a substring of everything — so this
    # needs the truthiness test as well, or a blank line inside a diff fence returns
    # `line[0]` and raises IndexError. It did.
    if line[:1] and line[:1] in "-+ ":
        return line[0], line[1:]
    return "", line

used, changed_files, changed_lines, run_hits = set(), [], 0, 0

for f in FILES:
    src = f.read_text(encoding="utf-8").split("\n")
    out, i, infence, isdiff, touched = [], 0, False, False, 0
    while i < len(src):
        line = src[i]
        m = re.match(r"^```(\w+)?", line)
        if m and not infence:
            infence, isdiff = True, (m.group(1) == "diff")
            out.append(line); i += 1; continue
        if line.startswith("```") and infence:
            infence = False
            out.append(line); i += 1; continue
        if not infence:
            out.append(line); i += 1; continue

        # runs first — a reflowed comment has no line-to-line correspondence
        hit = None
        for r in RUNS:
            n = len(r["old"])
            if i + n > len(src):
                continue
            pref, body = split_marker(src[i], isdiff)
            bodies = []
            ok = True
            for k in range(n):
                p2, b2 = split_marker(src[i + k], isdiff)
                if p2 != pref:
                    ok = False; break
                bodies.append(b2)
            if ok and bodies == r["old"]:
                hit = (pref, r); break
        if hit:
            pref, r = hit
            for nl in r["new"]:
                out.append(pref + nl)
            used.add(tuple(r["old"])); run_hits += 1
            touched += len(r["old"]); i += len(r["old"]); continue

        pref, body = split_marker(line, isdiff)
        if body in SINGLE and SINGLE[body] is not None:
            out.append(pref + SINGLE[body])
            used.add(body); touched += 1
        else:
            out.append(line)
        i += 1

    if touched:
        changed_files.append((f, touched)); changed_lines += touched
        if APPLY:
            f.write_text("\n".join(out), encoding="utf-8")

print(f"rewrite-fences: {'APPLIED' if APPLY else 'DRY RUN'}")
print(f"  files scanned                {len(FILES)}")
print(f"  fence bodies rewritten in    {len(changed_files)} files")
print(f"  lines rewritten              {changed_lines}  ({run_hits} reflowed runs)")
print(f"  map entries used             {len(used)} of {len(SINGLE) + len(RUNS)}")
print(f"  map entries UNUSED           {len(SINGLE) + len(RUNS) - len(used)}"
      "   (rewritten platform lines that appear in no fence)")
for f, n in sorted(changed_files, key=lambda x: -x[1])[:8]:
    print(f"    {n:4d}  {f.relative_to(ROOT)}")

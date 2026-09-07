#!/usr/bin/env python3
"""Every Part-3 chapter reference in platform source, with the rewrite it needs.

THREE REWRITES, AND THEY WERE NAMED WRONG TWICE.
  delete the tag       a parenthetical provenance note, or a sentence-initial marker.
                       The sentence stands without it. No name, no table.
  substitute a name    a possessive or the subject of a verb. A noun phrase from
                       subjects.json fits where the ordinal was.
  read and rewrite     section rules and temporal claims, where a name reads worse
                       than restating the fact.

Sorting by what a reference LOOKS LIKE gave 416 / 923 / 90. Sorting by the rewrite it
NEEDS gives roughly 757 / 605 / 70. Nearly half of what was called a substitution is a
deletion that consults no table — analysis pass 5.

EVERY PATTERN CARRIES A POSITIVE CONTROL, and a pattern that fails its own example is
reported BROKEN rather than as zero. `grep` on this machine is ugrep 7.8.4, and under it
a grouped alternation followed by two negated classes matches nothing while the same
pattern without the group matches. A credential scan filed that zero as evidence over a
corpus containing the string twice — gaps.md 044-1. This is Python for that reason, and
it still declares its controls.

Usage: classify-refs.py [--rule delete|substitute|read] [--files]
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
PLAT = HERE.parent.parent / "relay-platform"

from refrules import REF, ID, RULE_LINE, SPLIT, classify, controls_failing, is_versionish

def main() -> int:
    broken = controls_failing()
    if broken:
        for b in broken:
            print(f"  BROKEN PATTERN — {b}", file=sys.stderr)
        print("classify-refs: a pattern that fails its own control is BROKEN, not zero")
        return 1

    names = {c["was"]: c["name"] for c in json.loads((HERE / "subjects.json").read_text())["chapters"]}
    only = sys.argv[sys.argv.index("--rule") + 1] if "--rule" in sys.argv else None
    counts, files = {"delete": 0, "substitute": 0, "read": 0}, {}
    rows = []
    for d in ("services", "packages"):
        for f in sorted((PLAT / d).rglob("*.ts")):
            if "node_modules" in str(f):
                continue
            rel = str(f.relative_to(PLAT))
            for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for m in REF.finditer(line):
                    if is_versionish(line, m):
                        continue          # a version number, not a chapter
                    rule = classify(line, m)
                    counts[rule] += 1
                    files.setdefault(rel, {"delete": 0, "substitute": 0, "read": 0})[rule] += 1
                    ch = re.search(r"3\.(\d{1,2})", m.group(0))
                    if not only or rule == only:
                        rows.append((rel, n, rule, m.group(0),
                                     names.get(f"3.{int(ch.group(1))}", "?") if ch else "?"))

    if "--files" in sys.argv:
        for rel, c in sorted(files.items(), key=lambda x: -sum(x[1].values()))[:20]:
            print(f"  {sum(c.values()):>4}  del {c['delete']:>3}  sub {c['substitute']:>3}  "
                  f"read {c['read']:>3}  {rel}")
    elif only:
        for rel, n, rule, ref, name in rows:
            print(f"  {rel}:{n}  {ref}  ->  {name if rule=='substitute' else '(delete)' if rule=='delete' else '(read)'}")

    tot = sum(counts.values())
    print(f"classify-refs: {tot} references in {len(files)} files, all 7 controls fired through REF")
    for k in ("delete", "substitute", "read"):
        print(f"  {k:<11} {counts[k]:>5}  {counts[k]*100//tot:>2}%")
    print("classify-refs: the rule only — whether the phrase reads is nobody's instrument")
    return 0

if __name__ == "__main__":
    sys.exit(main())

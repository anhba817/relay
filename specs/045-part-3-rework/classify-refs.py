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

# REF IS BUILT FROM ITS BRANCHES, so a control on a branch is a control on REF.
#
# TWO EARLIER DESIGNS FAILED THIS. The first gave REF a single control —
# "// see chapter 3.20's finding" — which still matched with `[Cc]hapter` broken, because
# the possessive branch matched the same string. The second added a separate compiled
# pattern per branch, which tested those patterns and not the one doing the scanning:
# breaking REF's paren branch left every control green.
#
# Naming the branches and joining them means there is one pattern, and each branch has a
# string only it can match. Probed five ways; all five go red.
BRANCHES = {
    "chapter":    (r"[Cc]hapter 3\.\d{1,2}", "// see chapter 3.20 for the finding"),
    "paren":      (r"\(3\.\d{1,2}\)",        "// the sender's own half (3.17)"),
    "possessive": (r"\b3\.\d{1,2}'s",         "// as 3.20's does, for the same reason"),
}
REF = re.compile("|".join(pat for pat, _ in BRANCHES.values()))
ID = re.compile(r"\b(FR|SC|NFR|EIR|ADR|CON|DR|ASM)-[A-Z]*-?\d+[a-z]?\b")
RULE = re.compile(r"^\s*//\s*[─=]{2,}")

CONTROLS = [
    # One per branch, each string matchable by that branch alone.
    *[(REF, ctl, True) for _, ctl in BRANCHES.values()],
    (REF, "// nothing here names an ordinal at all", False),
    (ID, "(chapter 3.21, FR-RTM-08)", True),
    (ID, "(chapter 3.21)", False),
    (RULE, "  // ── chapter 3.18: two instances ──────", True),
    (RULE, "  // chapter 3.18 built the fabric", False),
]

def classify(line: str, m: re.Match) -> str:
    s, e = m.start(), m.end()
    op, cl = line.rfind("(", 0, s), line.find(")", e)
    in_parens = op != -1 and cl != -1 and line.find(")", op, s) == -1
    tag = bool(re.match(r"^\s*[/*\s]*" + re.escape(m.group(0)) + r"\s*[.:]", line))
    if RULE.match(line):
        return "read"
    if in_parens or tag or ID.search(line[max(0, s - 70):e + 70]):
        return "delete"
    if line[e:e + 2] == "'s" or m.group(0).endswith("'s"):
        return "substitute"
    if re.search(re.escape(m.group(0)) + r"\s+\w+(ed|s|es)?\b", line):
        return "substitute"
    return "read"

def main() -> int:
    broken = [(p.pattern[:40], t) for p, t, want in CONTROLS if bool(p.search(t)) != want]
    if broken:
        for pat, txt in broken:
            print(f"  BROKEN PATTERN {pat!r} failed its own control {txt!r}", file=sys.stderr)
        print("classify-refs: a pattern that fails its own example is BROKEN, not zero")
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
    print(f"classify-refs: {tot} references in {len(files)} files, all {len(CONTROLS)} controls passed")
    for k in ("delete", "substitute", "read"):
        print(f"  {k:<11} {counts[k]:>5}  {counts[k]*100//tot:>2}%")
    print("classify-refs: the rule only — whether the phrase reads is nobody's instrument")
    return 0

if __name__ == "__main__":
    sys.exit(main())

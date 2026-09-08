#!/usr/bin/env python3
"""The read class, by sub-class. T012.

THE READ CLASS IS NOT ONE JOB. It grew from a planned ~70 to 293, and four of its five
sub-classes turn out to be uniform enough for a rule plus a damage scan. Only the residue
needs a sentence read one at a time, and that is where the estimate should have been.

  rules      36  `// ── chapter 3.18: two instances ──` -> the ordinal goes, the rule stays
  bare      105  `stranded a user online for ever in 3.19` -> a name reads
  temporal   35  `until CHAPTER 3.18` -> a name reads; it IS a point in the series
  split      18  names one of two chapters — decided per sentence by what it is about
  residue   ...  read

WHY TEMPORALS COME BACK. They were routed here because `ADR-16 has said it since chapter
3.9` -> `since the mail-transport chapter` implies the mail chapter caused a migrations
rule. Re-read across all 35: that one is the outlier. `asserted was absent until the
fan-out chapter` is exactly right, and so are the rest. The outlier is rewritten by hand.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
# OVERRIDABLE, so the same rules can be applied to the rebuild worktree. The
# rebuild starts from a tag that predates this feature, so its base still names
# ordinals; the convention has to be established there before Part 3 continues on
# top of it, or the rebuilt history ends up mixing the two.
import os
import pathlib as _pl
PLAT = (_pl.Path(os.environ["RELAY_PLATFORM"]) if os.environ.get("RELAY_PLATFORM")
        else HERE.parent.parent / "relay-platform")
sys.path.insert(0, str(HERE))
import refrules
from refrules import is_deliberate, REF, RULE_LINE, SPLIT, TEMPORAL, chapter_of, classify, is_versionish

NAMES = {c["was"]: c["name"] for c in json.loads((HERE / "subjects.json").read_text())["chapters"]}
# The split chapter's two halves. A sentence about the sealed package, the outsider or the
# exit criterion means the milestone; everything else means the registry.
OUTSIDER = re.compile(r"outsider|integrat|exit criterion|sealed|package with no dependencies", re.I)

def sub_class(line: str, m: re.Match) -> str:
    ref = m.group(0)
    if RULE_LINE.match(line):
        return "rules"
    if chapter_of(ref) == SPLIT:
        return "split"
    if TEMPORAL.search(line[:m.start()].rstrip()):
        return "temporal"
    if not re.match(r"(?i:chapter)", ref) and not ref.startswith("("):
        return "bare"
    # A REFERENCE THAT ENDS THE LINE IS THE OBJECT OR SUBJECT OF SOMETHING ON THE NEXT
    # ONE, and the single-line verb test cannot see it. `a teardown that closed servers
    # first cost chapter 3.20` continues `two clients`, so the ordinal is what cost them
    # — a name fits. 95 of the residue were only there because the sentence wrapped.
    if not line[m.end():].strip():
        return "lineend"
    return "residue"

def name_for(line: str, ref: str) -> str:
    n = chapter_of(ref)
    if n == SPLIT:
        return NAMES["3.14b"] if OUTSIDER.search(line) else NAMES["3.14a"]
    return NAMES.get(f"3.{n}", "")

def rewrite(line: str, m: re.Match, kind: str) -> str:
    ref, name = m.group(0), name_for(line, m.group(0))
    if not name:
        return line
    if kind == "rules":
        # TWO SHAPES INSIDE A SECTION RULE, AND ONLY ONE IS A LABEL.
        #
        # `// ── chapter 3.23: the revision fabric reaches a socket ──` labels the section
        # with an ordinal, and the words after the colon already say what it is — the
        # ordinal goes. But `// ── T042: the mint's three cases (chapter 3.17, FR-005) ──`
        # carries the ordinal inside a parenthetical, and stripping it bare left
        # `(, FR-005)`. That shape takes the same removal a tag does.
        for pat in (rf"\s*\(\s*{re.escape(ref)}\s*\)", rf"{re.escape(ref)},\s*",
                    rf",\s*{re.escape(ref)}"):
            out = re.sub(pat, "", line, count=1)
            if out != line:
                return out
        out = re.sub(re.escape(ref) + r":\s*", "", line, count=1)
        return out if out != line else line
    # Everything but a section rule places a name exactly as the substitute rule does,
    # and this was the copy the substitute rule diverged from. One implementation now.
    return refrules.place_name(line, m, name)

def main() -> int:
    kind = sys.argv[sys.argv.index("--kind") + 1]
    apply = "--apply" in sys.argv
    found = done = 0
    samples, touched = [], set()
    # ONE CORPUS, DEFINED IN `refrules`. This walked `services` and `packages` for
    # `*.ts`, which is neither every directory nor every source suffix: it missed
    # `vitest.coverage.config.mts` (37 references), `eslint.config.mjs` (24), fifteen
    # `.sql` migrations, `compose.yaml` and ten `scripts/*.mjs` — 154 in 34 files.
    if True:
        for f in refrules.platform_files(PLAT):
            if False:
                continue          # dist/ is build output, gitignored and regenerated
            lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
            changed = False
            for i, orig in enumerate(lines):
                while True:
                    m = next((x for x in REF.finditer(lines[i])
                              if not is_versionish(lines[i], x)
                              and classify(lines[i], x) == "read"
                              and sub_class(lines[i], x) == kind), None)
                    if not m:
                        break
                    found += 1
                    new = rewrite(lines[i], m, kind)
                    if new == lines[i]:
                        samples.append(f"UNCHANGED {f.name}:{i+1}  {lines[i].strip()[:80]}")
                        break
                    if len(samples) < 6:
                        samples.append(f"{f.name}:{i+1}\n    - {orig.rstrip()[:100]}\n    + {new.rstrip()[:100]}")
                    lines[i] = new
                    done += 1
                    changed = True
            if changed and apply:
                f.write_text("".join(lines), encoding="utf-8")
                touched.add(str(f.relative_to(PLAT)))
    print(f"rewrite-read: kind={kind} apply={apply}  found {found} rewritten {done} files {len(touched)}")
    for s in samples[:6]:
        print(f"  {s}")
    return 0

if __name__ == "__main__":
    sys.exit(main())

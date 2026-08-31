#!/usr/bin/env python3
"""Cross-artifact consistency sweep for chapter 3.21.

WHY THIS EXISTS. Thirteen analysis passes fixed thirteen findings, and four of
them were the SAME correction landing in some artifacts and not others: R8's
claim count (three files, missed traceability), R9's tenth-file rule (five
places), ADR-19's typed points (four places), the phase order (recorded in
baseline.txt and applied only to tasks.md). No instrument in this repository
compares a claim in one document to the same claim in another — `check-refs.py`
reads ids, `check:srs` says in its own comment that it does not read meaning.

WHAT IT CHECKS
  1. every superseded phrasing this chapter has already corrected, anywhere
  2. the phase order and the MVP marker agree between plan.md and tasks.md
  3. the counts stated in prose match the counts measured from the files
  4. a foreign requirement id (chapter 3.20's FR-029, FR-032) names its chapter,
     checked WITHOUT the prose heuristic below — the third red test found that
     the heuristic swallowed a real hit
  5. no placeholders

WHAT IT DOES NOT CHECK. Ids and traceability — `check-refs.py` owns those, and a
fifth red test confirmed the division: renaming a traced requirement id here
produces no finding and `check-refs.py` catches it. Nor whether the prose is
true. A sentence nobody has
contradicted yet passes every line below.

THE SKIP LIST IS THE INTERESTING PART. Every correction in this chapter is
recorded beside the wording it replaced — that is the house style — so a
superseded phrase appears legitimately whenever a nearby line says it was
superseded. Matching that is a heuristic, and a checker whose false positives
outnumber its findings is how a real problem hides (chapter 3.17's
`check:figures` reported 122 problems in 193 figures, all false). Prefer a miss
here to noise: the phrase list is explicit and fails loudly on a real hit.
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).parent

# A superseded phrasing -> what it should say now. Add a row every time an
# analysis pass corrects a claim that appears in more than one artifact.
STALE = {
    r"\bthree published claims\b": "five claims, ten fragments (pass 9)",
    r"\bfour claims, eight fragments\b": "five claims, ten fragments (pass 9)",
    r"ADR-19's three typed points": "seven typed points (R1, pass 4)",
    r"\bno tenth (gateway )?integration file\b": "a tenth file, zero new api spawns (pass 11)",
    r"`Map` on the connection\b": "a Map in attachSessions's closure (pass 11)",
    r"\bthe four premises R1[-–]R4\b": "R1, R2, R3 and R5 (pass 13)",
    r"gateway holds no typing state": "no INDICATOR state; it holds publish state (pass 14)",
    r"share an existing file or an existing api": "a tenth file that spawns no api (pass 11)",
}

# A superseded phrase is legitimate when the surrounding lines say it is
# superseded. These are the words this chapter uses to do that.
SKIP = (
    "used to", "until analysis", "first version", "superseded", "stood here",
    "undercounts", "was refined", "R9 wrote", "R9 SAYS", "still carried",
    "still said", "still listed", "two claims and", "not what it means",
    "said three", "said \"", "reached", "was the proxy",
)

PLACEHOLDERS = ("TODO", "TKTK", "???", "<placeholder>", "FIXME", "XXX")


def load():
    files = sorted(ROOT.glob("*.md")) + sorted(ROOT.glob("checklists/*.md")) + sorted(
        ROOT.glob("contracts/*.md")
    )
    docs = {str(f.relative_to(ROOT)): f.read_text() for f in files}
    baseline = ROOT / "baseline.txt"
    if baseline.exists():
        docs["baseline.txt"] = baseline.read_text()
    return docs


def story(text):
    """US1 / US2 / US3, however a heading spells it."""
    m = re.search(r"\bUS([123])\b|\bUser Story ([123])\b", text)
    return ("US" + (m.group(1) or m.group(2))) if m else None


def main():
    docs = load()
    problems = []

    # 1 + 4 — superseded phrasings and unlabelled foreign ids
    for name, text in docs.items():
        lines = text.splitlines()
        for pattern, should in STALE.items():
            for m in re.finditer(pattern, text):
                n = text[: m.start()].count("\n")
                window = " ".join(lines[max(0, n - 1) : n + 2])
                if any(k in window for k in SKIP):
                    continue
                problems.append(f"{name}:{n + 1} {m.group(0)!r} -> {should}")

    # 4 — a foreign requirement id names its chapter. NO PROSE HEURISTIC HERE.
    # This check lived in STALE with the skip list applied, and the third red
    # test found it green on a real hit: the skip word "said three" appears in
    # the very sentence that cites chapter 3.20's FR-032. Whether an id is
    # labelled is a byte comparison, so it gets one.
    for name, text in docs.items():
        for m in re.finditer(r"\bFR-0(?:29|32)\b", text):
            n = text[: m.start()].count("\n")
            line = text.splitlines()[n]
            if re.search(r"(chapter )?3\.(18|19|20)'s " + re.escape(m.group(0)), line):
                continue
            problems.append(
                f"{name}:{n + 1} {m.group(0)} does not name its chapter"
                " — this chapter's ids stop at FR-021"
            )

    # 5 — placeholders
    for name, text in docs.items():
        for p in PLACEHOLDERS:
            if p in text:
                problems.append(f"{name}: placeholder {p!r}")

    # 2 — the phase order and the MVP marker
    plan = re.findall(r"^### Phase (\d+) [-—] (.+)$", docs["plan.md"], re.M)
    tasks = re.findall(r"^## Phase (\d+): (.+)$", docs["tasks.md"], re.M)
    if len(plan) != len(tasks):
        problems.append(f"phase count: plan {len(plan)}, tasks {len(tasks)}")
    for (pn, pt), (tn, tt) in zip(plan, tasks):
        if pn != tn:
            problems.append(f"phase numbering: plan {pn}, tasks {tn}")
        if story(pt) != story(tt):
            problems.append(
                f"Phase {pn}: plan says {story(pt)}, tasks says {story(tt)}"
            )
    mvp = ([n for n, t in plan if "MVP" in t], [n for n, t in tasks if "MVP" in t])
    if mvp[0] != mvp[1]:
        problems.append(f"MVP marker: plan Phase {mvp[0]}, tasks Phase {mvp[1]}")

    # 3 — counts stated in prose against counts measured
    measured = {
        "tasks": len(re.findall(r"^- \[ \] T\d+", docs["tasks.md"], re.M)),
        "requirements": len(set(re.findall(r"\*\*(FR-\d+[a-z]?)\*\*:", docs["spec.md"]))),
        "success criteria": len(set(re.findall(r"\*\*(SC-\d+)\*\*:", docs["spec.md"]))),
        "phases": len(tasks),
    }
    # `baseline.txt` records what was true at each pass, so a count there is
    # history rather than a claim. Everything else is a claim about now.
    for name, text in docs.items():
        if name == "baseline.txt":
            continue
        for label, actual in measured.items():
            for m in re.finditer(rf"(\d+) {label}\b", text):
                if int(m.group(1)) != actual:
                    n = text[: m.start()].count("\n") + 1
                    problems.append(
                        f"{name}:{n} says {m.group(1)} {label}, measured {actual}"
                    )

    head = " · ".join(f"{v} {k}" for k, v in measured.items())
    print(f"sweep: {head} · stories and MVP aligned across plan and tasks")
    if problems:
        print(f"sweep: {len(problems)} problem(s)")
        for p in sorted(set(problems)):
            print("  " + p)
        return 1
    print("sweep: no superseded claim, no placeholder, no count disagreement")
    print("sweep: this says nothing about whether the prose is TRUE")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Cross-artifact consistency sweep for chapter 3.21.

WHY THIS EXISTS. Thirteen analysis passes fixed thirteen findings, and four of
them were the SAME correction landing in some artifacts and not others: R8's
claim count (three files, missed traceability), R9's tenth-file rule (five
places), ADR-19's typed points (four places), the phase order (recorded in
baseline.txt and applied only to tasks.md). No instrument in this repository
compares a claim in one document to the same claim in another — `check-refs.py`
reads ids, `check:srs` says in its own comment that it does not read meaning.

SCOPE: `baseline.txt` IS EXEMPT FROM THE CLAIM CHECKS, and that is a decision
rather than a convenience. It is an append-only record of what happened, and what
happened includes quoting a superseded sentence in order to retire it — pass 14's
entry opens with the old assumption in quotation marks, pass 13's names a bare
`FR-032` as the finding. Those are history, not claims about now, and nothing
consults the record for current fact. **The risk this accepts**: a genuinely
stale statement written into the record would not be caught here. Placeholders
are still checked everywhere, including there.

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
    # Each key is a phrase this chapter has superseded; the value says what
    # replaced it and which analysis pass found it. Tested red before it is
    # trusted.
    r"a Redis set with one TTL": "five slot keys, one per slot (R3, pass 0)",
    r"pruned with `ZREMRANGEBYSCORE` on read, is the correct version":
        "rejected: needs Lua, which Constitution VII blocks (R3, pass 0)",
    r"FR-RTM-09's five is enforced NOWHERE": "enforced from this chapter (pass 0)",
    r"\bSET key id XX PX\b": "SET key id IFEQ id PX (C1, pass 1)",
    r"`XX`, never a plain `SET`": "IFEQ, not XX — XX tests existence (C1, pass 1)",
    r"the drain path \(close code 4009\)": "no such path exists (C2, pass 1)",
    r"\bDEL key\b": "a conditional tombstone, not DEL (C4, pass 2)",
    r"\bbounded interval\b": "the bound (M8, pass 1)",
    r"\breporting interval\b": "the heartbeat interval (M8, pass 1)",
    r"peak 4 of 5": "dropped: no existing fixture claims a slot (C6, pass 3)",
    r"sits exactly at the cap": "the cap is not enforced there (C6, pass 3)",
    # Three carry `(?i)` because they read as sentence fragments and could return
    # in lower case mid-paragraph; the other three are heading forms where the
    # capital is part of what is being retired.
    # ADDED IN PASS 12. This dictionary was populated once, in pass 4, and the set
    # of retired claims more than doubled after it. Six of the twelve later
    # corrections are pinned — the ones that would do damage if they came back,
    # not all of them, because this file's own header says prefer a miss to noise.
    r"The structure is the SAD's": "it is this chapter's, against a published row (pass 10)",
    r"(?i)the heartbeat already exists": "a new timer, deliberately not the ping (pass 10)",
    r"(?i)what it does next is the plan's call": "FR-011b says what follows (C7, pass 5)",
    r"(?i)or reuse the existing error payload": "reuse is the only option; strict object (H11, pass 6)",
    r"those eight chapters' diffs": "predecessors must NOT be regenerated (C8, pass 9)",
    r"recorded in Phase 9's task list": "Phase 11, T092 (M26, pass 11)",
}


# A superseded phrase is legitimate when the surrounding lines say it is
# superseded. These are the words this chapter uses to do that.
SKIP = (
    # Inherited from chapter 3.21 and kept, because the record still quotes it.
    "used to", "until analysis", "first version", "superseded", "stood here",
    "undercounts", "was refined", "still carried", "still said", "still listed",
    "not what it means", "said \"", "was the proxy",
    # THIS CHAPTER'S CORRECTION IDIOM, added after the instrument's first run
    # reported eight hits and every one was a deliberate quotation.
    "What is published", "says *", "would be writing a false",
    "The hand-off from chapter", "already made and published",
    "STALE list starts with", "stays true in that file",
    "DROPPED", "the first draft", "wrote the diagnosis",
    "named the state and deferred",
    "says so and then exploits it",
)

# CHECK 3 HAD NO EXEMPTION AND NEEDED ONE. `(\d+) tasks\b` matches any prose
# saying "N tasks", and the first run read "ran 4 tasks of 11" — turbo's tasks,
# in a sentence about running the unit lane from the wrong directory — against
# this chapter's 111. Named explicitly rather than pattern-guessed, and an
# unrecognised subject still fails.
COUNT_SKIP = ("turbo", "chapter 3.", "of 11 and printed green")

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

    # 1 + 4 — superseded phrasings and unlabelled foreign ids. The record is
    # exempt: see SCOPE above.
    claims = {n: t for n, t in docs.items() if n != "baseline.txt"}
    for name, text in claims.items():
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
    for name, text in claims.items():
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
    # TWO HEADING FORMS, AND FAILING ON NEITHER RATHER THAN COUNTING ZERO.
    # Chapter 3.21's plan wrote `### Phase N — title`; chapter 3.22's writes
    # `**Phase N — title.**`. The single-form version of this line reported
    # "phase count: plan 0, tasks 11" and an empty MVP marker — a checker that
    # cries wolf on a healthy tree, found on the instrument's first run.
    plan = re.findall(r"^### Phase (\d+) [-—] (.+)$", docs["plan.md"], re.M) or re.findall(
        r"^\*\*Phase (\d+) [-—] (.+)$", docs["plan.md"], re.M
    )
    if not plan:
        problems.append(
            "plan.md: no phase headings matched either form "
            "(`### Phase N — …` or `**Phase N — …`) — the extractor is wrong, "
            "not the document"
        )
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
        # `[ ]` OR `[X]`: the count is how many tasks exist, not how many are
        # outstanding. This read `^- \[ \]` until phase 1 checked nine boxes and
        # the total silently fell from 136 to 127.
        "tasks": len(re.findall(r"^- \[[ Xx]\] T\d+", docs["tasks.md"], re.M)),
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
                    line = text.splitlines()[n - 1]
                    if any(k in line for k in COUNT_SKIP):
                        continue
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

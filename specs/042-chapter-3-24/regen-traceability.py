#!/usr/bin/env python3
"""Regenerate traceability.md from spec.md and tasks.md.

WHY THIS IS A FILE. It was retyped by hand after each of the first three analysis passes and
had a different bug each time — a stale task count, then a quoted figure the sweep read as a
fresh claim, then a duplicated footer block. `sweep.py` caught all three, which is the system
working; retyping a generator three times is not.

The narrative sections are read from the existing file and carried forward, so the tables
regenerate and the prose does not.
"""
import re, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
CHAPTER = "3.24"


def verifiers(ident: str, task_lines: list[str]) -> list[str]:
    pat = re.escape(ident) + r" \(" + re.escape(CHAPTER) + r"\)"
    return [re.match(r"- \[[X ]\] (T\d{3}[a-z]?)", l).group(1)
            for l in task_lines if re.search(pat, l)]


def rows(prefix: str, spec: str, task_lines: list[str]):
    out = []
    for m in re.finditer(r"^- \*\*(" + prefix + r"-\d+[a-z]?)\*\*: (.+?)(?=\n- \*\*|\n\n|\n#)",
                         spec, re.M | re.S):
        out.append((m.group(1), " ".join(m.group(2).split()),
                    verifiers(m.group(1), task_lines)))
    return out


def table(title: str, label: str, data) -> list[str]:
    L = ["", title, "", f"| {label} | What it asks | Verified by |", "|---|---|---|"]
    for i, d, v in data:
        L.append(f"| {i} | {d if len(d) <= 96 else d[:93] + '…'} | "
                 f"{', '.join(v) if v else '**NOTHING**'} |")
    return L


def main() -> int:
    spec = (HERE / "spec.md").read_text()
    task_lines = [l for l in (HERE / "tasks.md").read_text().split("\n") if l.startswith("- [")]
    frs, scs = rows("FR", spec, task_lines), rows("SC", spec, task_lines)

    existing = (HERE / "traceability.md").read_text()
    head = existing.split("## 1. Feature requirement")[0].rstrip()
    # everything from section 3 onward is prose somebody wrote; carry it, minus the footer
    prose = "## 3. What the analysis passes changed here" + \
        existing.split("## 3. What the analysis passes changed here")[1]
    prose = re.sub(r"\n\s+\d+ tasks · \d+ requirements · \d+ criteria\n"
                   r"\s+\d+ ids with no verifying task\n?", "\n", prose).rstrip()

    body = [head]
    body += table("## 1. Feature requirement → the tasks that verify it", "Requirement", frs)
    body += table("## 2. Success criterion → the tasks that verify it", "Criterion", scs)
    body += ["", prose, "",
             f"    {len(task_lines)} tasks · {len(frs)} requirements · {len(scs)} criteria",
             f"    {sum(1 for _, _, v in frs + scs if not v)} ids with no verifying task"]
    (HERE / "traceability.md").write_text("\n".join(body) + "\n")

    untraced = [i for i, _, v in frs + scs if not v]
    print(f"traceability: {len(task_lines)} tasks, {len(frs)} requirements, "
          f"{len(scs)} criteria, {len(untraced)} untraced")
    if untraced:
        print("  untraced:", ", ".join(untraced))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

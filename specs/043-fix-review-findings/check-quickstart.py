#!/usr/bin/env python3
"""Cross-read quickstart.md against tasks.md.

Analysis passes 1 through 12 compared spec.md, plan.md and tasks.md with each other and
read quickstart.md as an output. It is not an output: it is the only artifact written to
describe what a PERSON does, and it named this chapter's worst gap in plain language
before pass 1 ran. P3a said the socket path drops attachments at three points, one of
them "session.ts's outbound builder", and no task covered that point until pass 11
reported it as a CRITICAL.

Two checks, both about the same blind spot:

  1. Every production file quickstart.md names is either covered by a task or DECLARED
     here as a file it only warns about. An unknown member is a failure, not a shrug —
     a first draft of this check flagged `connections.test.ts` as uncovered when it is a
     lane warning citing chapter 3.23's gaps item 9, and a checker whose false positives
     are indistinguishable from its findings gets ignored.

  2. Every success criterion in spec.md is named by at least one scenario. A guide a
     person runs should say what running it proves. Six of six were unnamed at pass 13,
     and SC-005 had no scenario at all.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Files quickstart.md names as WARNINGS rather than as work this chapter does. Each entry
# carries the reason, because an exemption without one is how a real gap gets filed.
MENTIONED_NOT_OWED = {
    "connections.test.ts": "lane warning: needs a running Redis, chapter 3.23 gaps item 9",
}


def main() -> int:
    qs_p, tasks_p, spec_p = HERE / "quickstart.md", HERE / "tasks.md", HERE / "spec.md"
    for p in (qs_p, tasks_p, spec_p):
        if not p.exists():
            print(f"check-quickstart: {p.name} is missing")
            return 1

    qs, tasks, spec = qs_p.read_text(), tasks_p.read_text(), spec_p.read_text()
    problems: list[str] = []

    # 1 — files named in the guide, against the task list
    named = sorted(set(re.findall(r"`([\w./-]+\.(?:ts|sql|mjs|py))`", qs)))
    for path in named:
        base = path.split("/")[-1]
        if base in tasks or base in MENTIONED_NOT_OWED:
            continue
        problems.append(
            f"quickstart.md names {path} and no task mentions it — give it a task, or "
            f"declare it in MENTIONED_NOT_OWED with the reason it is only a warning"
        )
    stale = [f for f in MENTIONED_NOT_OWED if not re.search(rf"`[\w./-]*{re.escape(f)}`", qs)]
    for f in stale:
        problems.append(
            f"MENTIONED_NOT_OWED declares {f} and quickstart.md no longer names it — "
            f"an exemption for a mention that is gone hides the next one"
        )

    # 2 — success criteria, against the scenarios
    criteria = re.findall(r"^- \*\*(SC-\d+)\*\*", spec, re.M)
    if not criteria:
        problems.append("spec.md declares no SC- ids — is the class name still right?")
    # Only an **Expected** line counts. A first version searched the whole file, so a
    # criterion mentioned in the narrative ABOUT a scenario passed as if the scenario
    # asserted it — the probe meant to prove this check red stayed green because P7's
    # own prose names SC-005 twice. What a person runs is the expectation, not the note.
    expected = "\n".join(ln for ln in qs.split("\n") if "**Expected**" in ln)
    for sid in criteria:
        if sid not in expected:
            problems.append(
                f"{sid} is named by no scenario's **Expected** line — nothing a person "
                f"can run proves it"
            )

    if problems:
        print(f"check-quickstart: {len(problems)} problem(s)")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"check-quickstart: {len(named)} file(s) named, {len(MENTIONED_NOT_OWED)} declared "
          f"warning(s), {len(criteria)} criteria all named by a scenario")
    print("check-quickstart: names only — it cannot tell whether a scenario's expectation is true")
    return 0


if __name__ == "__main__":
    sys.exit(main())

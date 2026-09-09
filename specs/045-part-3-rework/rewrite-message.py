#!/usr/bin/env python3
"""Rewrite one commit's message under the reference convention.

  rewrite-message.py <commit>        (env RELAY_SUBJECTS = optional subject-map path)

THE MESSAGE WAS OUT OF SCOPE BY ACCIDENT. `replay-range.sh` rewrote file contents and
passed `%B` through untouched, so every ported chapter kept the published subjects —
"chapter 3.17 phase 5". Measured across the tagged chapters: eight surviving ordinals in
messages, three of them SUBJECTS. A subject is the part read detached from its tree, the
same argument this project already made about a task id in a test title: `git log
--oneline` has no repository to grep.

THE SUBJECT AND THE BODY ARE NOT THE SAME PROBLEM. A body is prose about the work and
reads like the prose in a chapter page, so it goes through `refrules.place_name` — the
same implementation the source and mdx passes call. A subject is nine words built AROUND
the ordinal, and substituting a name into "chapter 3.17 phase 5 — a bot everywhere but at
the door" gives "the sender chapter phase 5", which is a sentence nobody would write.
Subjects come from a map a person wrote.

WHAT THIS REFUSES TO DO SILENTLY. If a subject still carries an ordinal after the map is
applied, this exits non-zero and names the sha and the line. A message rewrite that fails
open is what produced the eight.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import refrules  # noqa: E402
from refrules import REF, is_versionish, place_name  # noqa: E402

NAMES = {c["was"]: c["name"] for c in json.loads((HERE / "subjects.json").read_text())["chapters"]}


def tables(path: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """The person's two tables: subjects by sha, and body replacements.

    A BODY NEEDS A TABLE FOR THE SAME REASON SOURCE DOES. `substitute` skips the
    ambiguous old chapters — a bare "3.12" names one of two halves and only the
    sentence knows which — so a body citing one comes through untouched. A line
    `body|<old>|<new>` records what a reader decided, and every one of them must fire
    somewhere in the range or the replay fails: a mistyped left-hand side is otherwise
    indistinguishable from a reference that is simply not there.
    """
    if not path:
        return {}, []
    subjects: dict[str, str] = {}
    bodies: list[tuple[str, str]] = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("body|"):
            _, old, new = line.split("|", 2)
            bodies.append((old, new))
            continue
        sha, _, subject = line.partition("|")
        subjects[sha.strip()] = subject.strip()
    return subjects, bodies


def substitute(line: str, prev: str | None = None) -> str:
    """One prose line, every substitutable reference placed. Mirrors the mdx loop."""
    while True:
        m = next(
            (
                x
                for x in REF.finditer(line)
                if not is_versionish(line, x)
                and f"3.{refrules.chapter_of(x.group(0))}" in NAMES
                # AMBIGUOUS OLD CHAPTERS ARE A PERSON'S. The source and mdx passes both
                # route them to a reader rather than guess a half; so does this one, and
                # they are reported at the end of the replay rather than dropped.
                and refrules.chapter_of(x.group(0)) not in refrules.AMBIGUOUS
            ),
            None,
        )
        if not m:
            return line
        new = place_name(line, m, NAMES[f"3.{refrules.chapter_of(m.group(0))}"], prev)
        if new == line:
            return line
        line = new


def main() -> int:
    commit = sys.argv[1]
    text = subprocess.run(
        ["git", "log", "-1", "--format=%B", commit],
        capture_output=True, text=True, check=True,
    ).stdout.rstrip("\n")

    head, sep, body = text.partition("\n")

    subjects, bodies = tables(os.environ.get("RELAY_SUBJECTS", ""))

    # Keyed by whatever length the person wrote, matched on prefix, so a 7- or an
    # 8-character sha both work rather than one of them silently missing.
    for sha, subject in subjects.items():
        if commit.startswith(sha):
            head = subject
            break

    if body:
        bl = body.split("\n")
        body = "\n".join(substitute(l, bl[i - 1] if i else None)
                         for i, l in enumerate(bl))
        for old, new in bodies:
            if old in body:
                body = body.replace(old, new)
                # Reported on stderr so the replay's own output stays the message.
                print(f"rewrite-message: {commit[:8]} body decision fired: {old[:52]}",
                      file=sys.stderr)

    if any(not is_versionish(head, m) for m in REF.finditer(head)):
        print(
            f"rewrite-message: {commit[:8]} still carries an ordinal in its SUBJECT and "
            f"no map line covers it:\n  {head}",
            file=sys.stderr,
        )
        return 1

    print(head + sep + body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

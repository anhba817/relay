#!/usr/bin/env python3
r"""Split the lines `_orphaned_punctuation` welded before it captured its terminator.

  repair-welds.py [--apply]        (env RELAY_PLATFORM = the tree to repair)

WHY A SEPARATE TOOL RATHER THAN A RE-REPLAY. The reference rules are not idempotent in
the direction that would help: they REMOVE ordinals, and the trees they damaged no
longer contain any, so running them again finds nothing and repairs nothing. The weld is
already baked in. This walks the tree and puts the newline back.

WHY BY EXACT PAIR AND NOT BY PATTERN. A pattern that splits "a comment line containing a
second comment opener" would also split the fifty legitimate aligned tables this
repository writes in comments — `//   setup.ts   rewrites the connection string`, a
column of measured timings, an ASCII key diagram. Every one of those matches. So the
repair carries the three welds it found, each with the two lines it must become, and
**fails on a weld it does not recognise** rather than guessing. A new one means the bug
came back, which is worth a red gate and not a silent fix.

THE DETECTOR IS THE SHARPER HALF. `welded()` below carries the shapes a weld has and an
aligned table never does: a comment opener, then prose, then a SECOND opener of the same
kind. Run it after any reference replay.
"""
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import refrules  # noqa: E402

PLAT = Path(os.environ.get("RELAY_PLATFORM", HERE.parent.parent / "relay-platform"))

# (welded line, the two lines it must become). Leading whitespace is part of each.
REPAIRS: list[tuple[str, str]] = [
    (
        "// The chapter quotes the broker, not the config file — a"
        "// configuration that was written is not the same as a configuration that was",
        "// The chapter quotes the broker, not the config file — a\n"
        "// configuration that was written is not the same as a configuration that was",
    ),
    (
        "    // What matters here is that a second add of a bot behaves exactly"
        "    // as a second add of a person: nothing about `kind` reaches the members table.",
        "    // What matters here is that a second add of a bot behaves exactly\n"
        "    // as a second add of a person: nothing about `kind` reaches the members table.",
    ),
    (
        "    // An application credential may send only as a bot user."
        "    await repo.upsertUser(\"publish-bot\", {",
        "    // An application credential may send only as a bot user.\n"
        "    await repo.upsertUser(\"publish-bot\", {",
    ),
    (
        "     * So a REST send needs one to exist — and `createUser`"
        "     * makes a person. Widening this type rather than reaching around it: the",
        "     * So a REST send needs one to exist — and `createUser`\n"
        "     * makes a person. Widening this type rather than reaching around it: the",
    ),
]

# AND A SECOND SHAPE FROM THE SAME REPLAY: a subject name capitalised at the start of a
# CONTINUATION line. `place_name`'s three sentence-start tests are all line-local, so a
# comment sentence that spans lines gets a capital on its second line. Two shipped inside
# tagged chapters. `refrules.place_name` now takes the previous line and refuses; these
# two are already in the trees.
CAPITALS: list[tuple[str, str]] = [
    (
        "    // The isolation harness built and this is the first route to rely on it.",
        "    // the isolation harness built and this is the first route to rely on it.",
    ),
    (
        "    // The outbox chapter's own suite asserts on that same table is a race",
        "    // the outbox chapter's own suite asserts on that same table is a race",
    ),
    # AND THE POSSESSIVE THAT DID NOT SHOUT WITH ITS OWN CLAUSE. `place_name` upper-cases
    # the substituted name inside an all-caps run, and the `chapter` branch's pattern stops
    # before `'s` — so `CHAPTER 3.23's EDIT HISTORY` came out `THE REVISIONS CHAPTER's EDIT
    # HISTORY`. `refrules.place_name` now upper-cases a possessive it finds immediately
    # after the match; these three are the instances already written into this chapter's
    # trees, and five more sit in chapters 10, 11, 14 and 15 (`gaps.md` 045-10).
    (
        "  // THE REVISIONS CHAPTER's EDIT HISTORY",
        "  // THE REVISIONS CHAPTER'S EDIT HISTORY",
    ),
    (
        "  // THE REVISIONS CHAPTER's EDIT (",
        "  // THE REVISIONS CHAPTER'S EDIT (",
    ),
    (
        "  // THE REVISIONS CHAPTER's DELETION (",
        "  // THE REVISIONS CHAPTER'S DELETION (",
    ),
]

OPENER = re.compile(r"^\s*(?://+|/\*\*?|\*|--+|#+)\s")


def welded(line: str) -> bool:
    s = line.rstrip("\n")
    if "http" in s or "://" in s or re.search(r"[─=]{3,}", s):
        return False
    if s.lstrip().startswith("//") and "//" in s.lstrip()[2:]:
        return True
    if s.lstrip().startswith("*") and re.search(r"\S\s{2,}\* ", s.lstrip()):
        return True
    if s.lstrip().startswith("--") and "--" in s.lstrip()[2:]:
        return not re.search(r"-{3,}", s)
    # AND A COMMENT WELDED TO A CODE LINE HAS NO SECOND OPENER, which is how the worst
    # of the five got past this function and was caught by `tsc` instead:
    #
    #     // An application credential may send only as a bot user.    await repo.upsertUser(…
    #
    # The signature is sentence-ending punctuation, then a run of alignment whitespace,
    # then more content. That never happens in the fifty aligned tables this repository
    # writes inside comments: a table aligns its columns and does not put a full stop in
    # front of the gap. Checked against the whole tree — this clause fires on the weld
    # and on nothing else.
    if OPENER.match(s) and re.search(r"[.;:]\s{3,}\S", s):
        return True
    return False


def main() -> int:
    apply = "--apply" in sys.argv
    fixed = 0
    unknown: list[str] = []
    for f in refrules.platform_files(PLAT):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        out = text
        for bad, good in REPAIRS + CAPITALS:
            if bad in out:
                out = out.replace(bad, good)
                fixed += 1
                print(f"  repaired {f.relative_to(PLAT)}")
        for i, line in enumerate(out.split("\n"), 1):
            if welded(line):
                unknown.append(f"{f.relative_to(PLAT)}:{i}  {line.strip()[:96]}")
        if apply and out != text:
            f.write_text(out, encoding="utf-8")
    print(f"repair-welds: {'APPLIED' if apply else 'DRY RUN'} — {fixed} repaired "
          f"({len(REPAIRS)} weld shapes, {len(CAPITALS)} capital shapes)")
    if unknown:
        print(f"  {len(unknown)} UNRECOGNISED weld(s) — the bug is back, or the detector is:",
              file=sys.stderr)
        for u in unknown:
            print(f"    {u}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

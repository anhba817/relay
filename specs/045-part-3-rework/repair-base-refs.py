#!/usr/bin/env python3
"""Apply feature 045's reference convention to the trees that predate it.

WHY THIS EXISTS RATHER THAN `0317d83` MOVING. That commit's message says it establishes
the convention "on the base so the rebuilt history does not mix the two", and it landed
between chapters 2 and 3 instead — so chapters 1 and 2 cite `chapter 3.2` for a chapter
this feature deleted (gaps 045-63). It cannot simply be moved: seven of the nine files it
edits are CREATED by chapters 1 and 2, so the patch has nothing to apply to at the base.
The lines have to be corrected in the trees that introduce them, which is what this does.

THE TABLE IS EXTRACTED FROM `0317d83` ITSELF, not retyped — a hand-typed table already
cost this feature seven of eight paren pairs (four spaces the files did not have). Three
entries are not from it:

  credential-walk.mjs   the commit introduced "The the credentials chapter" onto a line
                        with no ordinal in it (045-65). Corrected here so the chain never
                        carries it, rather than at the tip where it would need a
                        `post-series.md` amendment for a doubled article.
  repository.ts         chapter 9's `3.13's addMembers shape`, which the reference replay
                        had in range and did not rewrite. Published 3.13 is new 8.
  environment-context   a file `0317d83` never saw, because chapter 2 deletes it.
        .guard.ts

IDEMPOTENT BY CONSTRUCTION. Every replacement is an exact-string swap, so a tree that
already has the new text is left alone — which is every tree from chapter 3 onward, and
is why `0317d83` becomes an empty commit and gets dropped by the driver.

Usage: repair-base-refs.py [--apply]   (reads RELAY_PLATFORM, default: the worktree)
"""
import json, os, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
TABLE = json.loads((HERE / "base-refs-table.json").read_text(encoding="utf-8"))
ROOT = pathlib.Path(os.environ.get("RELAY_PLATFORM", "/home/dong/work/relay/tmp/part3-refactor"))


def main(apply: bool) -> int:
    hits = 0
    for e in TABLE:
        p = ROOT / e["file"]
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        if e["old"] not in t:
            continue
        n = t.count(e["old"])
        if n != 1:
            print(f"  REFUSING {e['file']}: pre-image occurs {n} times, need exactly 1",
                  file=sys.stderr)
            return 2
        if apply:
            p.write_text(t.replace(e["old"], e["new"]), encoding="utf-8")
        hits += 1
        print(f"  {'applied' if apply else 'would apply'}  {e['file']}")
    print(f"repair-base-refs: {'APPLIED' if apply else 'DRY RUN'} — {hits} of {len(TABLE)} "
          f"replacements matched this tree")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))

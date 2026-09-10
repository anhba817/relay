#!/usr/bin/env python3
"""Every session-response stub carries `revisions`, in every tree from the revisions
chapter onward.

WHY A SCRIPT AND NOT N REBASES. `internalSessionResponseSchema` gains a required field in
the revisions chapter, so every fixture that builds a session response needs it — and the
fixtures are added by fourteen different chapters after that one. Amending each chapter and
rebasing the rest is one round per chapter; a tree-by-tree replay applying this is one pass.

IDEMPOTENT BY CONSTRUCTION: it inserts the field only where a `channel_ids:` line is not
already followed by one, so a tree that has it is left alone.

AN EMPTY MAP IS THE HONEST STUB VALUE. A fixture that plants no revision reports none, and
`{}` says exactly that — where `channel_ids` is a variable the stub was handed, the counts
are not derivable and inventing some would make a test pass for a reason its author did
not choose.

Usage: carry-revision-stubs.py [--apply]   (reads RELAY_PLATFORM)
"""
import os, pathlib, re, sys

ROOT = pathlib.Path(os.environ.get("RELAY_PLATFORM", "/home/dong/work/relay/tmp/part3-refactor"))
FIELD = re.compile(r"^(\s*)channel_ids: ([A-Za-z_][\w.]*|\[[^\]]*\]),\s*$")


def main(apply: bool) -> int:
    touched = 0
    for p in sorted(ROOT.glob("services/*/src/**/*.ts")) + sorted(ROOT.glob("packages/*/src/**/*.ts")):
        if "node_modules" in p.parts or "dist" in p.parts:
            continue
        L = p.read_text(encoding="utf-8").split("\n")
        out, n = [], 0
        for i, line in enumerate(L):
            out.append(line)
            m = FIELD.match(line)
            if m and not (i + 1 < len(L) and "revisions:" in L[i + 1]):
                out.append(f"{m.group(1)}revisions: {{}},")
                n += 1
        if n:
            touched += n
            if apply:
                p.write_text("\n".join(out), encoding="utf-8")
            print(f"  {'+' if apply else '?'}{n:<3} {p.relative_to(ROOT)}")
    print(f"carry-revision-stubs: {'APPLIED' if apply else 'DRY RUN'} — {touched} stub(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))

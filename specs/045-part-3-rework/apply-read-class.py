#!/usr/bin/env python3
"""Apply the read-class decisions from `read-class.json` to a platform tree.

  RELAY_PLATFORM=<tree> python3 apply-read-class.py [--apply] [--require-all]

WHY THIS IS A TABLE AND NOT A PATCH. The reference replay applies its two rules to
every commit's TREE, so these have to apply the same way. A replacement that matches
nothing in a given tree does not fire, and that is correct — the reference has not
been written yet at that commit.

WHICH MEANS A TYPO IS INDISTINGUISHABLE FROM "NOT THERE YET", and that is the whole
risk of this shape. So `--require-all` asserts every replacement fires, and the caller
runs it against the FINAL tree where all 23 references exist. Without that check a
mistyped left-hand side is silent forever, which is the failure this file's own
subject matter is about.
"""
import json, os, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import refrules

PLAT = pathlib.Path(os.environ["RELAY_PLATFORM"])
TABLE = json.loads((HERE / "read-class.json").read_text())


def main() -> int:
    apply = "--apply" in sys.argv
    require_all = "--require-all" in sys.argv

    pairs = [(p[0], p[1], g["why"]) for g in TABLE["replacements"] for p in g["pairs"]]
    fired = {old: 0 for old, _, _ in pairs}

    for f in refrules.platform_files(PLAT):
        text = f.read_text(encoding="utf-8")
        out = text
        for old, new, _ in pairs:
            if old in out:
                # COUNT, DO NOT JUST FLAG. A left-hand side matching twice in one file
                # means the sentence is not unique and the decision was made about one
                # of two places.
                fired[old] += out.count(old)
                out = out.replace(old, new)
        if out != text and apply:
            f.write_text(out, encoding="utf-8")

    total = sum(fired.values())
    missed = [old for old, n in fired.items() if n == 0]
    doubled = [(old, n) for old, n in fired.items() if n > 1]

    print(f"apply-read-class: {len(pairs)} replacements, {total} applied, "
          f"{len(missed)} matched nothing, apply={apply}")
    for old, n in doubled:
        print(f"  NOT UNIQUE ({n}x): {old.splitlines()[0][:88]}")
    if require_all and missed:
        for old in missed:
            print(f"  MATCHED NOTHING: {old.splitlines()[0][:88]}", file=sys.stderr)
        print(f"  {len(missed)} replacement(s) matched nothing in a tree where all of "
              f"them should — a mistyped left-hand side is silent otherwise",
              file=sys.stderr)
        return 1
    if doubled:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

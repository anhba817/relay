#!/usr/bin/env python3
"""The chapter registry agrees with the filesystem, in both directions.

WHY THIS EXISTS. `relay-tutorial/lib/tutorial.ts` is 810 hand-maintained lines declaring
every chapter's number, path, title, `titleVi` and reading time. `app/sitemap.ts` reads
it, and so do six components — the series sidebar, the chapter shell's previous and next
links, the site header, the landing page and the language switcher.

NOTHING ELSE READS IT. No script, no test, no gate. A renumbering that skipped this file
would leave `check:fences` green, `check:docs` green, and every navigation link in the
book dead. Analysis pass 1 found it by asking what else in this tree knows a chapter
number; FR-015 and SC-009 exist because of the answer.

BOTH DIRECTIONS, WHICH IS THE POINT. A declared path that does not exist is a dead link.
A page that is not declared is invisible to the sidemap and the sidebar and reachable
only by typing the URL. Only one of those is loud, so both are checked.

It agreed at 41 and 41 when this was written — unguarded rather than broken, which is
the harder condition to notice.
"""
import pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
TUT = HERE.parent.parent / "relay-tutorial"

def main() -> int:
    src = (TUT / "lib" / "tutorial.ts").read_text(encoding="utf-8")
    declared = set(re.findall(r'path:\s*"(/part-\d+/chapter-\d+/[^"]+)"', src))
    on_disk = {
        "/" + str(p.parent.relative_to(TUT / "app" / "(en)"))
        for p in (TUT / "app" / "(en)").rglob("page.mdx")
        if re.search(r"part-\d+/chapter-\d+", str(p))
    }
    problems = []
    if not declared:
        problems.append(
            "no chapter paths parsed out of lib/tutorial.ts — the `path:` shape changed, "
            "and an empty parse would otherwise agree with anything"
        )
    for p in sorted(declared - on_disk):
        problems.append(f"declared and absent from disk: {p}")
    for p in sorted(on_disk - declared):
        problems.append(f"on disk and not declared — invisible to the sitemap and sidebar: {p}")

    for p in problems:
        print(f"  {p}", file=sys.stderr)
    print(f"check-registry: {len(declared)} declared, {len(on_disk)} on disk, "
          f"{len(problems)} problem(s)")
    print("check-registry: paths only — it says nothing about titles, reading times or titleVi")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())

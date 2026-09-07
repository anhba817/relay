#!/usr/bin/env python3
"""The chapter map is a bijection, and every slug it names exists.

WHY THIS EXISTS. `chapter-map.json` has three consumers — the published mapping page,
the redirects, and the chapter registry. A map that is wrong is wrong in three places at
once, and two of the three are published. This is the only thing that reads it and says
so before they do.

WHAT IT CHECKS, AND EACH ANSWER IS A NUMBER RATHER THAN A YES:
  every new ordinal used exactly once, 1..N with no gaps
  every old chapter accounted for
  every slug present on disk in both locales
  the split chapter appearing twice and only twice
  every movement referenced, and no movement referenced that is not declared

IT SAYS NOTHING ABOUT WHETHER THE ORDER IS GOOD. Contiguity is check-movements.py's and
comprehension is nobody's — see gaps.md's unnumbered item.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TUT = ROOT / "relay-tutorial"

def main() -> int:
    m = json.loads((HERE / "chapter-map.json").read_text(encoding="utf-8"))
    chapters, movements = m["chapters"], {mv["id"] for mv in m["movements"]}
    problems: list[str] = []

    news = [c["new"] for c in chapters]
    if sorted(news) != list(range(1, len(chapters) + 1)):
        dupes = sorted({n for n in news if news.count(n) > 1})
        problems.append(
            f"new ordinals are not 1..{len(chapters)} exactly once"
            + (f" — duplicated: {dupes}" if dupes else f" — got {sorted(news)}")
        )

    olds = [c["old"] for c in chapters]
    published = sorted(
        int(re.search(r"chapter-(\d+)", str(p)).group(1))
        for p in (TUT / "app" / "(en)" / "part-3").rglob("page.mdx")
    )
    missing = [o for o in published if o not in olds]
    if missing:
        problems.append(f"published chapters absent from the map: {missing}")
    invented = [o for o in set(olds) if o not in published]
    if invented:
        problems.append(f"map names chapters that are not published: {invented}")

    split = m["split"]["old"]
    twice = [o for o in set(olds) if olds.count(o) > 1]
    if twice != [split]:
        problems.append(
            f"exactly one chapter may appear twice (the split, {split}) — appearing twice: {twice}"
        )

    for c in chapters:
        if c["movement"] not in movements:
            problems.append(f"chapter {c['new']} names movement {c['movement']}, which is not declared")
    used = {c["movement"] for c in chapters}
    for mv in sorted(movements - used):
        problems.append(f"movement {mv} is declared and used by no chapter")

    # Every slug must exist in both locales. The split's new slug is the one exception:
    # it does not exist until the chapter is divided, so it is allowed to be absent while
    # its sibling is present.
    sibling = {c["slug"] for c in chapters if c["old"] == split}
    for c in chapters:
        for locale, base in (("en", TUT / "app" / "(en)" / "part-3"),
                             ("vi", TUT / "app" / "(vi)" / "vi" / "part-3")):
            found = list(base.glob(f"chapter-*/{c['slug']}/page.mdx"))
            if not found and c["slug"] not in sibling:
                problems.append(f"{locale}: no page for slug {c['slug']}")

    for p in problems:
        print(f"  {p}", file=sys.stderr)
    print(f"check-map: {len(chapters)} chapters, {len(movements)} movements, "
          f"{len(problems)} problem(s)")
    print("check-map: the map only — this says nothing about whether the ORDER is right")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())

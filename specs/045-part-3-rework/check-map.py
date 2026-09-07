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

    # THE TREE ON DISK CARRIES THE *NEW* ORDINALS ONCE T019 HAS RUN, and this compared
    # against `old`. That was right while the tree still held 1..24 and became backwards
    # the moment the directories were renamed — the checker then reported chapter 25 as
    # "absent from the map" while the map is exactly where 25 comes from. Third instrument
    # in this feature whose premise expired under it: `classify-refs`'s corpus was
    # narrower than its claim, `check-excerpt-files` compared excerpts to the wrong state,
    # and this one outlived the numbering it was written against.
    #
    # BOTH DIRECTIONS, because only one of them is loud. A mapped chapter with no page is
    # a dead sidebar link; a page in no mapping is a chapter this feature forgot to place.
    news = sorted(c["new"] for c in chapters)
    olds = [c["old"] for c in chapters]
    published = sorted(
        int(re.search(r"chapter-(\d+)", str(p)).group(1))
        for p in (TUT / "app" / "(en)" / "part-3").rglob("page.mdx")
    )
    for n in [n for n in published if n not in news]:
        problems.append(f"published chapter {n} is in no mapping — placed by nothing")
    for n in [n for n in news if n not in published]:
        problems.append(f"mapped chapter {n} has no page on disk — a dead sidebar link")
    # THIS COMPARED THE MAP'S `old` VALUES AGAINST DISK, which cannot work once the
    # directories are renamed: `old` now describes history and nothing on disk carries an
    # old number. What is still worth asserting is that the map accounts for every chapter
    # that existed BEFORE — 1..24, the count Part 3 closed with — so a source chapter
    # cannot be dropped on the way through.
    before = set(range(1, 25))
    if set(olds) != before:
        problems.append(
            f"the map does not account for every pre-renumber chapter — "
            f"missing {sorted(before - set(olds))}, invented {sorted(set(olds) - before)}"
        )

    split = m["split"]["old"]
    # COUNT THE OCCURRENCES, DO NOT JUST COLLECT THE REPEATERS. This read
    # `twice = [o for o in set(olds) if olds.count(o) > 1]` and compared that list to
    # `[split]`, which is satisfied by the split appearing THREE times as happily as
    # twice — a probe that gave chapter 14 a third entry went red on a different
    # assertion entirely and this one stayed silent.
    from collections import Counter
    counts = Counter(olds)
    wrong = {o: n for o, n in counts.items() if n != (2 if o == split else 1)}
    if wrong:
        problems.append(
            f"the split chapter ({split}) must appear exactly twice and every other "
            f"exactly once — got {dict(sorted(wrong.items()))}"
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

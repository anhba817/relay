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

    # TWO SPLITS NOW, AND THE SECOND WAS FORCED. This read `m["split"]["old"]` and
    # asserted exactly one chapter appears twice. The gauntlet had to divide as well —
    # it creates eight files that 25 later chapter-edits land on, and moving it to the
    # end put every edit before the file existed. A checker that hard-codes "one split"
    # is a checker that has to be edited to allow a finding.
    splits = {sp["old"]: sp for sp in m.get("splits", [])}
    if not splits:
        problems.append("no `splits` in the map — the shape changed and an empty parse agrees with anything")
    from collections import Counter
    counts = Counter(olds)
    want = {o: (2 if o in splits else 1) for o in counts}
    wrong = {o: n for o, n in counts.items() if n != want[o]}
    if wrong:
        problems.append(
            f"a split chapter must appear exactly twice and every other exactly once — "
            f"splits are {sorted(splits)}, got {dict(sorted(wrong.items()))}"
        )
    # AND EACH SPLIT MUST NAME ITS BOUNDARY IN BOTH LOCALES. The first one recorded only
    # the English heading, which matches nothing in the Vietnamese page.
    for o, sp in sorted(splits.items()):
        b = sp.get("boundary", {})
        for loc in ("en", "vi"):
            if not b.get(loc):
                problems.append(f"split {o} names no {loc} boundary heading")
        halves = sp.get("halves", [])
        if len(halves) != 2:
            problems.append(f"split {o} has {len(halves)} halves, need 2")
        if not any(c["new"] == h.get("new") for h in halves for c in chapters):
            problems.append(f"split {o} names halves that are not in the chapter list")

    # AND THE MAP GREW A THIRD SHAPE, WHICH THIS CHECKER IGNORED IN SILENCE.
    #
    # Old 3.10's harness moved to new 8 and its PROSE stayed at new 23 — two old
    # chapters feeding one new one, which is a merge and not a split. Recorded as a
    # `split` it failed here for the right reason and the wrong one: a split needs a
    # prose boundary heading and there is no harness section in old 3.10's page to
    # cut at. So it became a `reassignment`, and the checker then read the map,
    # found two well-formed splits, and reported zero problems over a key it had
    # never heard of. AN UNKNOWN MEMBER MUST FAIL, or the next shape is invisible
    # the same way.
    # EVERY CHAPTER NEEDS A TITLE, AND ONE WAS MISSING WITHOUT A WORD FROM THIS FILE.
    # New 4 carried a slug and no title through the split that created it. The title is
    # what the annotated tag's message says and what the registry shows in the sidebar,
    # so a blank one is two published surfaces reading the slug instead — which is the
    # same defect as the ordinal, arrived at from the other direction.
    for c in chapters:
        for field in ("slug", "title", "movement"):
            if not c.get(field):
                problems.append(f"chapter {c.get('new')} has no {field}")

    KNOWN_KEYS = {"_why", "movements", "chapters", "splits", "reassignments"}
    unknown = set(m) - KNOWN_KEYS
    if unknown:
        problems.append(
            f"the map has {len(unknown)} key(s) this checker does not check: "
            f"{sorted(unknown)} — add them to KNOWN_KEYS and check them, or remove them"
        )

    reassignments = {r["old"]: r for r in m.get("reassignments", [])}
    newnums = {c["new"] for c in chapters}
    for o, r in sorted(reassignments.items()):
        # A reassignment's old chapter keeps ONE row — the prose one. Two rows would
        # mean it also split, and then it is a split.
        if counts.get(o) != 1:
            problems.append(
                f"reassignment {o} appears {counts.get(o, 0)} times in the chapter "
                f"list — a reassignment moves code only, so its prose has one home"
            )
        for field in ("prose_stays_at", "code_moves_to"):
            n = r.get(field)
            if n not in newnums:
                problems.append(f"reassignment {o}'s {field} is {n!r}, which is no chapter")
        if r.get("prose_stays_at") == r.get("code_moves_to"):
            problems.append(
                f"reassignment {o} moves code to the chapter its prose is already in "
                f"— that is not a reassignment"
            )
        if not r.get("paths"):
            problems.append(f"reassignment {o} names no paths, so it reassigns nothing")
        # THE PATHS MUST NOT ALSO BELONG TO A SPLIT HALF. A path in two places is a
        # file two chapters both claim to create, and the fence chain would then
        # want its pre-image twice.
        owned = {q for sp in splits.values() for h in sp.get("halves", []) for q in h.get("paths", [])}
        clash = owned & set(r["paths"])
        if clash:
            problems.append(
                f"reassignment {o} claims {len(clash)} path(s) a split half also "
                f"claims: {sorted(clash)}"
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
    sibling = {c["slug"] for c in chapters if c["old"] in splits}
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

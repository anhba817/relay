#!/usr/bin/env python3
"""SC-001's instrument: eight of eight subject clusters contiguous, and the plan's table
agrees with the map.

WHY THIS EXISTS. `check-map.py` proves `chapter-map.json` is a bijection onto pages that
exist, and its own docstring says what it cannot say: "Contiguity is check-movements.py's".
That file did not exist. **SC-001 — eight of eight contiguous, against five of eight today
— was the feature's first success criterion and had no instrument at all**, which means the
number in the spec was going to be asserted by whoever wrote the close-out.

AND IT CHECKS A SECOND TABLE, because a hand-maintained one cannot be checked and this
feature has already paid for that lesson twice. `docs/07-tutorial-plan.md`'s Part-3 table
was 24 rows against a tree of 26, under a heading saying 24, under a summary block saying
21 — three places, three counts, in a section whose own paragraph says a number in a
heading is carried rather than derived. Nothing read it. Now something does.

WHAT IT CHECKS, AND EVERY ANSWER IS A NUMBER RATHER THAN A YES:
  eight movements declared, and every chapter's movement is one of the eight
  each movement's chapters occupy a CONTIGUOUS run of new ordinals
  the movements' runs ascend in declared order — I before II before III
  a movement carrying an explicit `chapters` list agrees with the chapters that name it
  the plan's table has one row per mapped chapter, in ordinal order
  each row's Was, Movement and Title agree with the map and with the page's own metadata
  the published mapping page's data file is a faithful copy of the canonical map

CONTIGUITY IS NOT COMPREHENSION. Eight contiguous runs say the chapters about one subject
sit together. Whether the order teaches anything is `reader-protocol.md`'s question and it
needs a person; see gaps.md's unnumbered item.

Usage: check-movements.py [--table-only | --movements-only]
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TUT = pathlib.Path(__import__("os").environ.get("RELAY_TUTORIAL", ROOT / "relay-tutorial"))
PLAN = ROOT / "docs" / "07-tutorial-plan.md"
PUBLISHED_MAP = TUT / "lib" / "part3-chapter-map.json"


def movement_problems(chapters, movements) -> list[str]:
    problems: list[str] = []
    declared = [mv["id"] for mv in movements]
    if len(declared) != len(set(declared)):
        problems.append(f"movement ids are not unique: {declared}")

    # FAIL ON AN UNKNOWN MEMBER. A chapter naming a movement nobody declared is the one
    # shape that makes every count below meaningless, so it is checked before them.
    for c in chapters:
        if c["movement"] not in declared:
            problems.append(
                f"chapter {c['new']} names movement {c['movement']!r}, which is not declared"
            )
    if problems:
        return problems

    runs = {}
    for mv in declared:
        ns = sorted(c["new"] for c in chapters if c["movement"] == mv)
        if not ns:
            problems.append(f"movement {mv} is declared and holds no chapter")
            continue
        runs[mv] = ns
        want = list(range(ns[0], ns[0] + len(ns)))
        if ns != want:
            gaps = [n for n in want if n not in ns]
            problems.append(
                f"movement {mv} is NOT contiguous: holds {ns}, "
                f"and {gaps} inside that range belong to another movement"
            )

    # The runs must also ASCEND in declared order. Eight individually contiguous runs
    # interleaved at the top level would satisfy the clause above and read as chaos.
    ordered = [mv for mv in declared if mv in runs]
    starts = [runs[mv][0] for mv in ordered]
    if starts != sorted(starts):
        problems.append(
            "movements do not ascend in declared order: "
            + ", ".join(f"{mv}@{runs[mv][0]}" for mv in ordered)
        )

    for mv in movements:
        if "chapters" in mv and mv["id"] in runs and sorted(mv["chapters"]) != runs[mv["id"]]:
            problems.append(
                f"movement {mv['id']} declares chapters {sorted(mv['chapters'])} and is named "
                f"by {runs[mv['id']]}"
            )
    return problems


def table_problems(chapters) -> list[str]:
    problems: list[str] = []
    if not PLAN.exists():
        return [f"{PLAN} does not exist"]
    text = PLAN.read_text(encoding="utf-8")

    # The Part-3 table only: anchored on its own heading and ended by the next one, so a
    # row in Part 2's or Part 4's table can never be read as Part 3's.
    m = re.search(r"^### Part 3 — .*$", text, re.M)
    if not m:
        return ["no `### Part 3 —` heading in the plan"]
    rest = text[m.end():]
    nxt = re.search(r"^### ", rest, re.M)
    section = rest[: nxt.start()] if nxt else rest

    heading = re.search(r"\((\d+) chapters", m.group(0))
    if not heading:
        problems.append(f"the Part 3 heading states no chapter count: {m.group(0)!r}")
    elif int(heading.group(1)) != len(chapters):
        problems.append(
            f"the Part 3 heading says {heading.group(1)} chapters, the map has {len(chapters)}"
        )

    # And the summary block near the top of the document, which was the stalest of the three.
    summary = re.search(r"^Part 3   Becoming a platform\s+(\d+) chapters", text, re.M)
    if not summary:
        problems.append("no `Part 3   Becoming a platform` row in the summary block")
    elif int(summary.group(1)) != len(chapters):
        problems.append(
            f"the summary block says {summary.group(1)} chapters, the map has {len(chapters)}"
        )

    rows = re.findall(r"^\| (\d+) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \| (.*) \|$", section, re.M)
    by_new = {c["new"]: c for c in chapters}
    if len(rows) != len(chapters):
        problems.append(f"the table has {len(rows)} rows, the map has {len(chapters)} chapters")
    seen = []
    for ch, was, mv, title, _built in rows:
        n = int(ch)
        seen.append(n)
        c = by_new.get(n)
        if c is None:
            problems.append(f"table row {n} is in no mapping")
            continue
        if not was.strip().startswith(f"3.{c['old']}"):
            problems.append(f"row {n}: Was says {was.strip()!r}, the map says old 3.{c['old']}")
        if mv.strip() != c["movement"]:
            problems.append(f"row {n}: Movement says {mv.strip()!r}, the map says {c['movement']}")
        if title.strip().lower().rstrip(".") not in c["title"].lower() and \
           c["title"].lower() not in title.strip().lower():
            problems.append(f"row {n}: Title {title.strip()!r} vs the map's {c['title']!r}")
    if seen != sorted(seen):
        problems.append(f"table rows are not in ordinal order: {seen}")
    for n in sorted(set(by_new) - set(seen)):
        problems.append(f"chapter {n} ({by_new[n]['slug']}) has no row in the plan's table")
    return problems


def published_map_problems(chapters, movements) -> list[str]:
    """The mapping page renders `relay-tutorial/lib/part3-chapter-map.json`, which is a
    machine-written copy of the canonical map. A COPY IS A SECOND PLACE TO BE WRONG, and
    this one is published — so it is compared field by field rather than trusted because a
    script wrote it once."""
    if not PUBLISHED_MAP.exists():
        return [f"{PUBLISHED_MAP} does not exist — the mapping page has no data"]
    pub = json.loads(PUBLISHED_MAP.read_text(encoding="utf-8"))
    problems: list[str] = []
    if [m["id"] for m in pub.get("movements", [])] != [m["id"] for m in movements]:
        problems.append("published map's movement ids differ from the canonical map's")
    for m_pub, m in zip(pub.get("movements", []), movements):
        if m_pub.get("title") != m["title"]:
            problems.append(
                f"published movement {m['id']}: title {m_pub.get('title')!r} vs {m['title']!r}"
            )
    by_new = {c["new"]: c for c in chapters}
    pub_by_new = {c["new"]: c for c in pub.get("chapters", [])}
    for n in sorted(set(by_new) | set(pub_by_new)):
        c, q = by_new.get(n), pub_by_new.get(n)
        if c is None:
            problems.append(f"published map has chapter {n}, the canonical map does not")
            continue
        if q is None:
            problems.append(f"published map is missing chapter {n} ({c['slug']})")
            continue
        for field in ("old", "movement", "slug", "title"):
            if q.get(field) != c[field]:
                problems.append(
                    f"published chapter {n}: {field} {q.get(field)!r} vs canonical {c[field]!r}"
                )
    return problems


def main(argv) -> int:
    m = json.loads((HERE / "chapter-map.json").read_text(encoding="utf-8"))
    chapters, movements = m["chapters"], m["movements"]
    problems: list[str] = []
    if "--table-only" not in argv:
        problems += movement_problems(chapters, movements)
    if "--movements-only" not in argv:
        problems += table_problems(chapters)
        problems += published_map_problems(chapters, movements)

    for p in problems:
        print(f"  {p}", file=sys.stderr)
    runs = {}
    for mv in movements:
        ns = sorted(c["new"] for c in chapters if c["movement"] == mv["id"])
        if ns:
            runs[mv["id"]] = f"{ns[0]}–{ns[-1]}" if len(ns) > 1 else str(ns[0])
    contiguous = sum(
        1
        for mv in movements
        if (ns := sorted(c["new"] for c in chapters if c["movement"] == mv["id"]))
        and ns == list(range(ns[0], ns[0] + len(ns)))
    )
    print(f"check-movements: {contiguous} of {len(movements)} movements contiguous "
          f"({', '.join(f'{k} {v}' for k, v in runs.items())})")
    print(f"check-movements: {len(chapters)} chapters, {len(problems)} problem(s)")
    print("check-movements: contiguity only — whether the ORDER teaches anything needs a person")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

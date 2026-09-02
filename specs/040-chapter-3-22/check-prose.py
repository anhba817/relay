#!/usr/bin/env python3
"""Chapter 3.21's published-claim checker.

WHY IT EXISTS. Five sentences in the published tree stop being true when this
chapter ships, and **no checker in this repository reads prose.** `check:fences`
compares bytes, `check:srs` says in its own comment that it does not read meaning,
`check:errors` asserts structure. A sentence that stopped being true because the
code moved underneath it is found by a person or not at all.

WHAT IT CHECKS. Ten fragments — one per claim per locale, plus two in `docs/`,
which has one locale. Each is a QUOTABLE STRING present verbatim in the tree
today, matched against whitespace-collapsed text so a reflowed paragraph does not
hide one. **A fragment that describes a claim rather than quoting it compiles into
a checker that matches nothing and reports green**, which is what analysis pass 9
found in two of the four entries this list started with.

HOW TO USE IT. Run it BEFORE correcting anything and watch all ten fail. An
instrument written after the corrections it checks can only ever be green.

WHAT IT DOES NOT CHECK. Whether the replacement prose is true. It knows only that
the old sentence is gone.
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EN = ROOT / "relay-tutorial/app/(en)"
VI = ROOT / "relay-tutorial/app/(vi)/vi"
DOCS = ROOT / "docs"

CH20 = "part-3/chapter-20/the-membership-that-changed/page.mdx"
CH21 = "part-3/chapter-21/the-frame-nobody-may-send/page.mdx"

# (claim, file, fragment). The claim number is research R8's.
# EVERY FRAGMENT MUST MATCH TODAY, AND THE CHECKER ASSERTS IT. A fragment that
# matches nothing can never be caught, so this file would report green for a page
# nobody corrected — which is exactly what happened on the first run: claim 4's
# Vietnamese fragment was chapter 20's wording (`*set*`, single asterisks) declared
# against chapter 21, whose text reads `**set**`. Seven of eight matched and the
# eighth was invisible. See `dead()` below.
CLAIMS: list[tuple[int, pathlib.Path, str]] = [
    # RED UNTIL T073a RUNS, ON PURPOSE. Every fragment below is still published
    # today; this checker goes green when the chapter corrects the two pages. A
    # red instrument nobody explained is indistinguishable from a red instrument
    # nobody noticed, so the phase that adds it says so in its commit body.
    (1, EN / CH20, "FR-RTM-09's five-connection cap stays unbuilt"),
    (1, VI / CH20, "Trần năm kết nối của FR-RTM-09 vẫn chưa được dựng"),
    (2, EN / CH20,
     "A sorted set\nscored by heartbeat and pruned on read is the correct version"),
    (2, VI / CH20, "điểm theo nhịp tim và tỉa lúc đọc mới là bản đúng"),
    (3, EN / CH21,
     "its first job is a decision rather\nthan an implementation"),
    (3, VI / CH21, "việc đầu tiên của nó là một quyết định chứ"),
    (4, EN / CH21, "The SRS describes `conn:{env}:{user}` as a Redis **set**"),
    (4, VI / CH21, "SRS mô tả `conn:{env}:{user}` là một **set** Redis"),
]



def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def declared() -> int:
    """`--declared`: every fragment must match its file RIGHT NOW.

    THIS IS THE OPPOSITE ASSERTION TO `main()` AND THAT IS THE POINT. The normal
    run wants no fragment to match — the superseded sentences are gone. But a
    fragment can also match nothing because it was mistyped or aimed at the wrong
    file, and then it reports green for a page nobody corrected. The two modes
    cannot both be permanent, so this one is run ONCE, when the list is written and
    before the pages are corrected. Analysis pass 5 ran it by hand and found claim
    4's Vietnamese fragment was chapter 20's wording aimed at chapter 21: seven of
    eight matched and the eighth was invisible.
    """
    dead = []
    for claim, path, fragment in CLAIMS:
        if not path.exists():
            dead.append(f"claim {claim}: {path} does not exist")
        elif collapse(fragment) not in collapse(path.read_text()):
            dead.append(
                f"claim {claim}: matches nothing in {path.relative_to(ROOT)} — "
                f"mistyped, or aimed at the wrong file\n    {fragment[:88]}…"
            )
    print(f"check-prose --declared: {len(CLAIMS)} fragments checked against the pages")
    if dead:
        print(f"check-prose --declared: {len(dead)} fragment(s) can never match")
        for d in dead:
            print("  " + d)
        return 1
    print("check-prose --declared: every fragment matches, so every claim is catchable")
    return 0


def main() -> int:
    problems = []
    for claim, path, fragment in CLAIMS:
        if not path.exists():
            problems.append(f"claim {claim}: {path} does not exist")
            continue
        if collapse(fragment) in collapse(path.read_text()):
            problems.append(
                f"claim {claim}: still published in {path.relative_to(ROOT)}\n"
                f"    {fragment[:88]}…"
            )

    print(
        f"check-prose: {len(CLAIMS)} fragments, "
        f"{len({n for n, _, _ in CLAIMS})} claims, both locales plus docs/"
    )
    if problems:
        print(f"check-prose: {len(problems)} still present")
        for p in problems:
            print("  " + p)
        return 1
    print("check-prose: none of the superseded sentences is still published")
    print("check-prose: this says nothing about whether the replacements are true")
    return 0


if __name__ == "__main__":
    sys.exit(declared() if "--declared" in sys.argv else main())

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

CH19 = "part-3/chapter-19/who-is-allowed-to-see-it/page.mdx"
CH20 = "part-3/chapter-20/the-membership-that-changed/page.mdx"

# (claim, file, fragment). The claim number is research R8's.
CLAIMS: list[tuple[int, pathlib.Path, str]] = [
    (1, DOCS / "08-error-reference.md",
     "`message.send` is the only inbound frame; every other member of the "
     "frame union is server-to-client"),
    (1, DOCS / "08-error-reference.md",
     "**What to do:** send `message.send`. Do not send events; receive them."),
    (2, EN / CH19,
     "`message.updated`, `message.deleted`, `membership.changed` and `typing` "
     "are still four declared words with nothing behind them"),
    (2, VI / CH19,
     "vẫn là bốn từ đã khai báo mà phía sau không có gì"),
    (3, EN / CH20,
     "the one kind that could genuinely reuse `chan:{channel_id}` rather than "
     "needing a fourth grammar"),
    (3, VI / CH20,
     "nó là loại duy nhất có thể thật sự tái dùng `chan:{channel_id}` thay vì "
     "cần một ngữ pháp thứ tư"),
    (4, EN / CH20,
     "the first that can reuse a grammar rather than adding one"),
    (4, VI / CH20,
     "là loại đầu tiên tái dùng được một ngữ pháp thay vì thêm một cái mới"),
    # Claim 5's FENCE quotes chapter 2.6 and cannot be edited — those are 2.6's
    # words and the fence chain compares them. What this chapter falsifies is the
    # ForwardRef 2,700 lines later, which says typing "may well reuse the
    # fan-out's plumbing". It does not.
    #
    # **The first version of this entry guessed at that sentence** and matched
    # nothing, which is the exact failure analysis pass 9 named: a fragment that
    # describes a claim rather than quoting it reports green. Running the checker
    # BEFORE correcting anything is what surfaced it — a green line for claim 5
    # while six others were red.
    (5, EN / CH19,
     "Typing may well reuse the fan-out's plumbing — that half of 2.6's "
     "sentence is still open, and this chapter closed only presence's half of it."),
    (5, VI / CH19,
     "có nửa còn lại của lời hứa mà chương 2.6 đưa ra — chương này mới chỉ "
     "khép được nửa phần presence."),
]


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text)


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

    print(f"check-prose: {len(CLAIMS)} fragments, 5 claims, both locales plus docs/")
    if problems:
        print(f"check-prose: {len(problems)} still present")
        for p in problems:
            print("  " + p)
        return 1
    print("check-prose: none of the superseded sentences is still published")
    print("check-prose: this says nothing about whether the replacements are true")
    return 0


if __name__ == "__main__":
    sys.exit(main())

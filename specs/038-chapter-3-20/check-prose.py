#!/usr/bin/env python3
"""Fail while any published sentence this chapter contradicts is still standing.

Run from `relay-tutorial`:  python3 ../specs/038-chapter-3-20/check-prose.py

WHY THIS EXISTS
  No checker in this repository reads prose. `check:fences` compares code fences to
  the repository byte for byte and says nothing about the paragraph above them; a
  published Trap contradicting chapter 3.17's own chapter survived fifteen analysis
  passes. Chapter 3.19 wrote the first instrument of this shape and this is the second.

WHAT IT CHECKS
  Four claims, eight fragments — one per claim per locale. A fragment is matched
  against whitespace-collapsed text, because MDX wraps prose at 100 columns and a
  sentence that fits on one line in English wraps in Vietnamese.

  A fragment that is FOUND is a failure: the claim is still published and this
  chapter has made it false.

TEST IT RED BEFORE BELIEVING IT
  An instrument written after the corrections it checks can only ever be green. Run
  this before correcting anything and watch all eight fail. Chapter 3.17 shipped five
  checkers that were wrong the same way — a pattern matching the examples in front of
  the author rather than the set the rule names — and `check:figures`'s first version
  reported 122 problems in 193 figures, all false.
"""
import re
import sys
from pathlib import Path

# THE LIST IS NOT DERIVED FROM MEMORY. Every fragment was extracted from the file
# with `grep`, in both locales, and verified present before this file was written.
# The first draft of the research entry quoted two claims chapter 3.19 had already
# deleted — four fragments that could never match, reporting green from the first run
# on claims nobody had corrected.
CLAIMS = [
    (
        "chapter 3.18 — a claim of IMPOSSIBILITY, not a forward reference",
        "app/(en)/part-3/chapter-18/the-message-that-never-arrived/page.mdx",
        "Nothing in between re-reads membership, and no code path could",
        "app/(vi)/vi/part-3/chapter-18/the-message-that-never-arrived/page.mdx",
        "Không gì ở giữa đọc lại membership, và không đường code nào có thể",
    ),
    (
        "chapter 3.18 — the clause stays open",
        "app/(en)/part-3/chapter-18/the-message-that-never-arrived/page.mdx",
        "so the clause stays open rather than being fixed on the way through",
        "app/(vi)/vi/part-3/chapter-18/the-message-that-never-arrived/page.mdx",
        "nên điều khoản vẫn để ngỏ thay vì được sửa tiện đường",
    ),
    (
        "chapter 3.19 — a ForwardRef to a re-read the session layer owes",
        "app/(en)/part-3/chapter-19/who-is-allowed-to-see-it/page.mdx",
        "a re-read the session layer owes",
        "app/(vi)/vi/part-3/chapter-19/who-is-allowed-to-see-it/page.mdx",
        "một lần đọc lại mà session layer còn nợ",
    ),
    (
        "chapter 3.19 — a Trap saying an added user stays invisible until reconnect",
        "app/(en)/part-3/chapter-19/who-is-allowed-to-see-it/page.mdx",
        "does not appear online to that channel's members until they reconnect",
        "app/(vi)/vi/part-3/chapter-19/who-is-allowed-to-see-it/page.mdx",
        "sẽ không hiện online với thành viên của channel đó cho tới khi họ kết nối lại",
    ),
]


def collapsed(path: Path) -> str:
    """Whitespace-collapsed text. MDX wraps at 100 columns, so a fragment that sits
    on one line in one locale spans two in the other."""
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


def main() -> int:
    root = Path.cwd()
    problems: list[str] = []
    checked = 0

    for label, en_rel, en_frag, vi_rel, vi_frag in CLAIMS:
        for rel, frag, locale in ((en_rel, en_frag, "en"), (vi_rel, vi_frag, "vi")):
            path = root / rel
            checked += 1
            if not path.exists():
                # A MISSING FILE IS A PROBLEM, NOT A PASS. A checker that silently
                # skips what it cannot find reports green on a moved file — which is
                # `check:srs` shipping "192 clause rows" as though that were the
                # document.
                problems.append(f"{rel} does not exist — cannot check [{locale}] {label}")
                continue
            if re.sub(r"\s+", " ", frag) in collapsed(path):
                problems.append(
                    f"[{locale}] {label}\n"
                    f"        {rel}\n"
                    f'        still says: "{frag}"'
                )

    if problems:
        for p in problems:
            print(f"  {p}")
        print(
            f"check-prose: {len(problems)} problem(s) of {checked} fragments — "
            "each is a published sentence chapter 3.20 makes false"
        )
        return 1
    print(
        f"check-prose: {checked} fragments checked, none still published — "
        "the four claims chapter 3.20 contradicts are all corrected"
    )
    print(
        "check-prose: fragments only — this says nothing about prose "
        "nobody thought to add to the list"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

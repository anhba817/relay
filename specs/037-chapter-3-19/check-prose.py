#!/usr/bin/env python3
"""FR-033's gate: four published claims this design contradicts, in both locales.

Run from the feature directory:  python3 check-prose.py

WHY THIS EXISTS
  `gaps.md` item 8 is the standing record that no checker in this repository reads
  prose, and a published Trap contradicting chapter 3.17's own chapter survived
  fifteen analysis passes. Nine passes of tooling on this feature went past four
  published claims about presence; reading the chapters found them, and FR-033's
  verification column then read "inspection only". This turns it into a command.

WHY BOTH LOCALES ARE LISTED SEPARATELY
  Chapter 3.18's close-out: "A phrase sweep needs one word list per locale. Eight
  English phrases scored zero against the Vietnamese prose making the claims they
  were written to find." Verified here — the Vietnamese renders "needs the same" as
  "cần đúng … ấy/đó" and keeps `reuse` and `pub/sub plumbing` as loanwords, so an
  English fragment matches none of the three Vietnamese sentences. Each claim
  therefore carries its own per-locale fragment, taken from the file rather than
  translated by guess.

WHAT IT CANNOT CHECK
  It proves a sentence is **gone**, never that what replaced it is right. A claim
  deleted outright passes. Reading the replacement is still a person's job, which is
  why FR-033 keeps a reader in its verification too.

  It also cannot find a claim nobody listed. The list below is the whole instrument;
  a fifth contradiction in a chapter nobody opened is invisible to it, exactly as
  these four were until pass 7.
"""
import re, sys, pathlib

# Anchored on the script, not the shell: T100 invokes this from the repository root and
# every red test of it ran from inside the feature directory, where the old relative
# path happened to resolve. See check-refs.py's note.
HERE = pathlib.Path(__file__).resolve().parent
TUTORIAL = HERE.parent.parent / "relay-tutorial"

# (claim id, locale, path under relay-tutorial/app, fragment that must disappear)
# Fragments are matched against whitespace-collapsed text, so a sentence wrapped
# across source lines still matches.
CLAIMS = [
    ("2.6-forwardref", "en",
     "(en)/part-2/chapter-06/two-servers-one-conversation/page.mdx",
     "will reuse this exact pub/sub plumbing"),
    ("2.6-forwardref", "vi",
     "(vi)/vi/part-2/chapter-06/two-servers-one-conversation/page.mdx",
     "sẽ reuse đúng pub/sub plumbing này"),

    ("3.18-mechanism", "en",
     "(en)/part-3/chapter-18/the-message-that-never-arrived/page.mdx",
     "Presence needs the same missing mechanism"),
    ("3.18-mechanism", "vi",
     "(vi)/vi/part-3/chapter-18/the-message-that-never-arrived/page.mdx",
     "Presence cần đúng cái cơ chế còn thiếu ấy"),

    ("3.18-same-thing", "en",
     "(en)/part-3/chapter-18/the-message-that-never-arrived/page.mdx",
     "Chapter 3.19 needs the same thing built for presence"),
    ("3.18-same-thing", "vi",
     "(vi)/vi/part-3/chapter-18/the-message-that-never-arrived/page.mdx",
     "Chương 3.19 cần đúng thứ đó được dựng cho presence"),

    ("3.8-registry", "en",
     "(en)/part-3/chapter-08/limits-you-can-see-coming/page.mdx",
     "Presence needs the same registry"),
    ("3.8-registry", "vi",
     "(vi)/vi/part-3/chapter-08/limits-you-can-see-coming/page.mdx",
     "Presence cũng cần đúng registry ấy"),
]

def main() -> int:
    problems: list[str] = []
    outstanding: list[str] = []

    # Fail on an incomplete class: every claim must carry both locales.
    per_claim: dict[str, set[str]] = {}
    for cid, loc, _p, _f in CLAIMS:
        per_claim.setdefault(cid, set()).add(loc)
    for cid, locales in per_claim.items():
        missing = {"en", "vi"} - locales
        if missing:
            problems.append(f"claim {cid} lists no fragment for locale(s): {', '.join(sorted(missing))}")

    for cid, loc, rel, fragment in CLAIMS:
        path = TUTORIAL / "app" / rel
        if not path.is_file():
            problems.append(f"claim {cid} [{loc}]: {path} does not exist")
            continue
        text = re.sub(r"\s+", " ", path.read_text())
        if fragment in text:
            outstanding.append(f"{cid} [{loc}]  still says: \"{fragment}\"  in app/{rel}")

    if problems:
        print(f"check-prose: {len(problems)} problem(s) with the claim list itself")
        for p in problems:
            print(f"  {p}")
        return 2

    if outstanding:
        print(f"check-prose: {len(outstanding)} of {len(CLAIMS)} contradicted claims still stand (FR-033)")
        for o in outstanding:
            print(f"  {o}")
        print("check-prose: red is correct until the corrections land; it goes green when all eight are gone")
        return 1

    print(f"check-prose: all {len(CLAIMS)} listed claims are gone from both locales (FR-033)")
    print("check-prose: proves the sentences are absent, never that the replacements are right")
    return 0

if __name__ == "__main__":
    sys.exit(main())

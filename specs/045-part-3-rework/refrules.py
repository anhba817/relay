#!/usr/bin/env python3
"""One definition of what a Part-3 chapter reference is, and which rewrite it needs.

WHY THIS FILE EXISTS. `classify-refs.py` counts and `rewrite-refs.py` edits, and both
need the same answer. They had a copy each, and the copies disagreed — 830 against 821 —
which is the two-lists-that-must-agree defect this project has now recorded four times.
One definition, two importers.

THE PATTERN IS CASE-INSENSITIVE ON THE WORD, and it was `[Cc]hapter` until implementation
began. This codebase writes ALL-CAPS for emphasis in comments, so `CHAPTER 3.18` was
invisible — 75 references. **Third instance of that bug class in one feature**: the
reference count read 985 until the pattern gained a capital C; the file count kept the
lowercase pattern and read 166 until analysis pass 3; and then the same word in caps.
1,428 references became 1,614 in 207 files.

CONTROLS TEST WHICH BRANCH FIRED, NOT WHETHER ANYTHING MATCHED — and that is the third
design of them. The branches OVERLAP: `\\b3\\.\\d{1,2}\\b` matches the digits inside
`CHAPTER 3.20`, so "does REF match this string" cannot separate them. Python's
alternation is ordered, so the matched TEXT names the branch, and a control asserts the
text. The two designs before this one both let a broken branch pass:

  one control for the whole pattern      break `chapter`  -> the possessive branch matched
  a separate compiled pattern per branch break REF's part -> the controls tested copies
"""
import re

BRANCHES = {
    "chapter": (r"(?i:chapter) 3\.\d{1,2}", "// see CHAPTER 3.20 for the finding", "CHAPTER 3.20"),
    "paren":   (r"\(3\.\d{1,2}\)",          "// the sender's own half (3.17)",     "(3.17)"),
    "bare":    (r"\b3\.\d{1,2}(?:'s)?\b",   "// as 3.20's does, for the same reason", "3.20's"),
}
REF = re.compile("|".join(pat for pat, _, _ in BRANCHES.values()))
ID = re.compile(r"\b(FR|SC|NFR|EIR|ADR|CON|DR|ASM)-[A-Z]*-?\d+[a-z]?\b")
RULE_LINE = re.compile(r"^\s*//\s*[─=]{2,}")
# A REFERENCE AFTER ONE OF THESE CANNOT SIMPLY BE DELETED. "which the route began
# accepting in chapter 3.15" loses its object and ends on "in"; "narrowed by 3.11's
# FR-044" becomes "narrowed by's FR-044". Both were applied to the tree once — 52 of
# 807 — before a damage scan of the diff found them. They take a NAME instead.
PREPOSITION = re.compile(
    r"\b(in|by|of|as|from|than|like|with|and|to|for|per|see|via)\s*$", re.I)
# A TEMPORAL PREPOSITION MEANS "SINCE THAT POINT IN THE SERIES", NOT "BECAUSE OF THAT
# SUBJECT", and a name reads worse than the ordinal did. `ADR-16 has said it since
# chapter 3.9` becomes `since the mail-transport chapter` — understandable, and wrong
# about why: the mail chapter has nothing to do with migrations. These take a rewritten
# sentence, so they route to `read`.
TEMPORAL = re.compile(r"\b(since|until|before|after|by the time)\s*$", re.I)
VERSIONISH = re.compile(r'\d\.\d+\.\d|"\d|\bv3\.')
SPLIT = 14


def controls_failing() -> list[str]:
    """A branch whose control does not fire THROUGH REF is broken, not zero."""
    bad = []
    for name, (_, text, expect) in BRANCHES.items():
        m = REF.search(text)
        got = m.group(0) if m else None
        if got != expect:
            bad.append(f"branch {name!r}: REF matched {got!r} on its own control, expected {expect!r}")
    for text, want in (("(chapter 3.21, FR-RTM-08)", True), ("(chapter 3.21)", False)):
        if bool(ID.search(text)) != want:
            bad.append(f"ID pattern failed its control {text!r}")
    for text, want in (("  // ── chapter 3.18: two instances ──────", True),
                       ("  // chapter 3.18 built the fabric", False)):
        if bool(RULE_LINE.match(text)) != want:
            bad.append(f"RULE_LINE failed its control {text!r}")
    return bad


def is_versionish(line: str, m: re.Match) -> bool:
    return bool(VERSIONISH.search(line[max(0, m.start() - 24):m.end() + 16]))


def chapter_of(ref: str) -> int:
    return int(re.search(r"3\.(\d{1,2})", ref).group(1))


def classify(line: str, m: re.Match) -> str:
    """delete | substitute | read — the rewrite this reference needs.

    THE ORDER OF THESE TESTS IS THE WHOLE DESIGN, and it took four attempts. Each one
    looked right until its output was read:

      by proximity to a requirement id   `Chapter 3.8 needed the` called a tag because an
                                         `ADR-05:` sat earlier on the line
      by shape, parentheses first        `(3.17's T040b)` stripped to `( T040b)` — 32 of
                                         them, all possessives or plurals inside a paren
      possessive and bare first          `(chapter 3.11 added it)` stripped to a hole, and
                                         `it("… as chapter 3.10 shipped them")` treated as
                                         a tag because `it(` opened a bracket
      verbs and quotes considered too     what is below

    A REFERENCE IN A PARENTHESIS IS NOT AUTOMATICALLY A TAG. `(chapter 3.21, FR-RTM-08)`
    is one; `(chapter 3.15's Phase 1)` and `(chapters 3.3 and 3.8)` are not — the first
    modifies a noun and the second is a list. Both need a name.
    """
    ref = m.group(0)
    s_, e_ = m.start(), m.end()
    possessive = line[e_:e_ + 2] == "'s" or ref.endswith("'s")
    bare = not re.match(r"(?i:chapter)", ref) and not ref.startswith("(")

    if RULE_LINE.match(line):
        return "read"                     # a section rule needs its own sentence
    if chapter_of(ref) == SPLIT:
        return "read"                     # names one of two chapters; only the sentence knows
    if possessive:
        return "substitute"               # it modifies a noun — deleting orphans the noun
    if bare:
        return "read"                     # `and 3.20 for presence` — 117, context decides

    # Now the deletions, in shape order. Everything left is `chapter 3.N` or `(3.N)`.
    # A SENTENCE-INITIAL PROVENANCE MARKER, ALONE OR WITH COMPANY.
    # `// Chapter 3.8: nor the relay` and `/** Chapter 3.23, ADR-24. Register the…` are
    # the same shape — a tag opening the comment — and the second was read-classified for
    # 124 references because a comma followed the ordinal instead of a full stop. The
    # ordinal goes and whatever it was listed beside stays.
    if re.match(r"^\s*[/*\s]*" + re.escape(ref) + r"\s*[.:]", line):
        return "delete"
    if re.match(r"^\s*[/*\s]*" + re.escape(ref) + r",\s*(?:[A-Z]{2,4}-)", line):
        return "delete"                   # "Chapter 3.23, ADR-24." -> "ADR-24."
    if ref.startswith("("):
        return "delete"                   # carries its own parentheses; removed whole

    # SUBJECT OF A VERB BEATS THE PARENTHESIS TEST, because a reference can be both.
    # `(chapter 3.11 added it)` is a clause inside brackets, not a tag: deleting it leaves
    # "name the function  and could not see the call".
    if re.search(re.escape(ref) + r"\s+\w+(ed|s|es)?\b", line):
        return "substitute"

    # A PARENTHESIS IN CODE IS NOT A PARENTHETICAL IN PROSE. `it("… as chapter 3.10
    # shipped them", () => {` has an opening bracket before and a closing one after, and
    # three references were classified as removable tags on that basis. A tag holds no
    # quote mark.
    op, cl = line.rfind("(", 0, s_), line.find(")", e_)
    if op != -1 and cl != -1 and line.find(")", op, s_) == -1 and '"' not in line[op:cl]:
        return "delete"                   # "(chapter 3.21, FR-RTM-08)" -> "(FR-RTM-08)"

    if TEMPORAL.search(line[:s_].rstrip()):
        return "read"                     # "since chapter 3.9" is a point in time, not a cause
    if PREPOSITION.search(line[:s_].rstrip()):
        return "substitute"               # object of a preposition
    return "read"

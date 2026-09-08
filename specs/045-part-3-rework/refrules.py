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
RULE_LINE = re.compile(r"^\s*(?://|--|#)\s*(?:[─=]{2,}|-{3,})")
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
# A MAGNITUDE IS NOT A CHAPTER. `-- century reaches 3.2 billion, which overflows
# `integer`` was classified as a reference to the credentials chapter. The unit is what
# separates them, and it always follows.
VERSIONISH = re.compile(
    r'\d\.\d+\.\d|"\d|\bv3\.|gaps\.md\s+3\.\d'
    r'|3\.\d{1,2}\s*(?:billion|million|thousand|bn|m\b|k\b|%|s\b|ms\b|x\b|GB|MB|KB)')
# THE AMBIGUOUS OLD CHAPTERS, READ OUT OF THE MAP RATHER THAN NAMED HERE.
#
# This was `SPLIT = 14`, one integer, written when one chapter split. Two more shapes
# arrived since and each of them makes an ordinal ambiguous in the same way:
#
#   old 14 -> new 3 + new 26    the error registry, and the outsider milestone
#   old 12 -> new 4 + new 25    the isolation harness, and the gauntlet milestone
#   old 10 -> new 8 + new 23    the lane's harness (code), and quotas (prose)
#
# A reference to any of them names ONE of two things and only the sentence knows
# which. `subjects.json` has a single name per old chapter, so substituting one is
# substituting a coin flip — `REASSESSED IN CHAPTER 3.12` came out as `REASSESSED IN
# THE ISOLATION GAUNTLET` in a sentence about the e2e journey's endpoints, which is
# new 4's half and not new 25's.
#
# Read from the map so that the next shape routes itself. A hard-coded integer is a
# checker that has to be edited to admit a finding.
def _ambiguous_olds() -> frozenset:
    import json, pathlib as _p
    m = json.loads((_p.Path(__file__).resolve().parent / "chapter-map.json").read_text())
    olds = {sp["old"] for sp in m.get("splits", [])}
    olds |= {r["old"] for r in m.get("reassignments", [])}
    if not olds:
        raise SystemExit(
            "refrules: chapter-map.json names no splits or reassignments — an empty "
            "parse would route every ordinal to an automatic substitution"
        )
    return frozenset(olds)


AMBIGUOUS = _ambiguous_olds()
# Kept as a name so an old caller fails loudly rather than comparing against nothing.
SPLIT = None


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


# ORDINALS KEPT ON PURPOSE, AND THE ONLY ONES.
#
# `schema.ts` carries a comment whose SUBJECT is this feature's defect: it quotes what the
# line used to say and cites the number's movement as the evidence. The substitute rule
# rewrote inside the quotation, so `This line used to say "the deduplication chapter's
# cross-tenant gauntlet"` became a false statement about text — it never said that — and
# `The gauntlet was 3.7 … became 3.8 … is now 3.9` lost the three numbers that ARE the
# argument.
#
# A RULE THAT IS RIGHT ABOUT A REFERENCE IS WRONG ABOUT A QUOTATION OF ONE. Listed by
# exact text rather than detected, because "is this line talking about ordinals or using
# one" is not a question a pattern answers, and an exemption nobody can enumerate is an
# exemption nobody can review.
DELIBERATE = frozenset({
    '// NAMED, NOT NUMBERED. This line used to say "chapter 3.7\'s cross-tenant',
    '// gauntlet". The gauntlet was 3.7 when that was written, became 3.8 when a chapter',
    '// was inserted ahead of it, and is now 3.9 after a second insertion — and the',
})


def is_deliberate(line: str) -> bool:
    return line.strip() in {x.strip() for x in DELIBERATE}


def is_versionish(line: str, m: re.Match) -> bool:
    return bool(VERSIONISH.search(line[max(0, m.start() - 24):m.end() + 16]))


# WHICH FILES ARE "PLATFORM SOURCE". This was `rglob("*.ts")` in three scripts and it
# misses `.mts`, `.mjs`, `.sql`, `compose.yaml` and every shell script — 154 references in
# 34 files, including `vitest.coverage.config.mts` (37) and `eslint.config.mjs` (24), both
# of which the appendix fences. `classify-refs.py` then reported "0 references in 0 files,
# every Part-3 ordinal in platform source now names its subject" over a corpus that
# excluded all of them. A CHECKER WHOSE CORPUS IS NARROWER THAN ITS CLAIM says nothing,
# and it says it in the language of a pass.
SOURCE_SUFFIXES = (".ts", ".mts", ".cts", ".js", ".mjs", ".cjs", ".sql", ".yaml", ".yml", ".sh")
SKIP = ("/dist/", "/node_modules/", "/.git/", "/coverage/", "/.turbo/", "/build/")


# Memoised: `platform_files` calls this on every invocation and several scripts call
# `platform_files` inside a loop, so without a cache the 83 `.mdx` files were read and
# regexed once per call.
_FENCED_CACHE = {}


def fenced_paths(tutorial):
    """Every path a titled fence names — the checker's own definition of the corpus.

    WHY THE SUFFIX LIST IS NOT ENOUGH. `services/api/Dockerfile` has no extension, so it
    was outside `SOURCE_SUFFIXES` and outside every scan — and it is FENCED, published in
    chapter 3.5, carrying `# The api (chapter 3.5).`. The fence was rewritten and the
    platform file was not, which `check:fences` reported as a HEAD mismatch in the
    opposite direction from every other one. 24 fenced paths sit outside the suffix list;
    this is the only one that carried a reference, and there was no way to know that
    without asking.
    """
    import re as _re
    from pathlib import Path as _P
    tutorial = _P(tutorial)
    if str(tutorial) in _FENCED_CACHE:
        return _FENCED_CACHE[str(tutorial)]
    out = set()
    files = sorted(tutorial.glob("app/(en)/**/page.mdx")) + [tutorial / "fences/post-series.md"]
    for f in files:
        if not f.exists():
            continue
        for m in _re.finditer(r'^```\w+ title="([^"]+)"', f.read_text(encoding="utf-8"), _re.M):
            t = m.group(1)
            if "(excerpt)" in t or ".naive." in t:
                continue
            out.add(t.split(",")[0].split(" before ")[0].split(" (deleted)")[0].strip())
    _FENCED_CACHE[str(tutorial)] = out
    return out


def platform_files(root, tutorial=None):
    """Every platform file a reference can hide in, in one place.

    The union of two definitions, because neither alone is the corpus: files with a source
    suffix (which a reader compiles) and files a titled fence names (which a reader
    types). `tutorial` defaults to the sibling checkout.
    """
    from pathlib import Path as _P
    root = _P(root)
    tutorial = _P(tutorial) if tutorial else root.parent / "relay-tutorial"
    fenced = fenced_paths(tutorial)
    # PRUNE, DO NOT FILTER AFTERWARDS. `sorted(root.rglob("*"))` descends into
    # `node_modules` and materialises the whole listing before any test runs: 34,620
    # paths, 26,075 of them build output nothing here reads. `os.walk` lets the
    # directories be dropped before they are entered.
    import os as _os
    prune = {"node_modules", ".git", "dist", "coverage", ".turbo", "build", "__pycache__"}
    for dirpath, dirnames, filenames in _os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in prune)
        for fn in sorted(filenames):
            f = _P(dirpath) / fn
            rel = str(f.relative_to(root))
            if f.suffix in SOURCE_SUFFIXES or rel in fenced:
                yield f


# A COMMENT OPENER IS NOT ALWAYS `//`. Migrations open with `--` and compose files and
# shell scripts with `#`, so a reference first on such a line was not seen as a sentence
# start and came out lower-case: `-- the outbox chapter published events`. This is the
# same omission as the corpus one, one level down.
# Named in full because `classify` has a LOCAL `OPENER` that means something else
# entirely — the text allowed BEFORE a reference, not a whole-line opener.
COMMENT_OPENER = re.compile(r"^\s*(?://+|/\*\*?|\*|--+|#+)\s*\**$")


def recapitalise(line: str) -> str:
    """Restore the capital a deleted sentence-initial marker took with it.

    THE FOURTH COPY OF THE OPENER SET, and the one that made the other three's fix look
    like it had not worked. `classify` and `delete_one` were both taught that `--` and
    `#` open a comment; this regex was not, so `-- Chapter 3.1 — the tenancy hierarchy`
    was correctly recognised as a tag, correctly stripped, and then left as
    `-- the tenancy hierarchy` because the capital is restored somewhere else again.
    """
    return re.sub(r"^(\s*(?://+|/\*\*?|\*|--+|#+)\s*)([a-z])",
                  lambda g: g.group(1) + g.group(2).upper(), line, count=1)


def place_name(line: str, m: re.Match, name: str) -> str:
    """Put `name` where the reference `m` was, with the case and plural the site needs.

    ONE IMPLEMENTATION, TWO CALLERS. `substitute_one` and the read class's `rewrite` each
    carried a copy of this, and the copies had drifted: only `rewrite` cut the dangling
    plural and only `rewrite` kept an all-caps run in caps, so the substitute rule
    produced `chapters the quota chapter and the connection-metering chapter` and
    `**THE ONE the typing chapter FORGOT**` on lines the other rule handled correctly.
    """
    ref = m.group(0)
    new = name + ("'s" if ref.endswith("'s") else "")

    # A PLURAL LOSES ITS NOUN WHEN EACH ORDINAL BECOMES A NOUN PHRASE. `chapters 3.10 and
    # 3.11 added` -> `chapters the quota chapter and …`. The plural is cut with the first
    # substitution.
    before_raw = line[:m.start()]
    plural = re.search(r"\b[Cc]hapters\s+$", before_raw)
    prefix_cut = plural.start() if plural else m.start()

    # AND A DETERMINER DOUBLES WHEN THE NAME CARRIES ITS OWN. Every name in
    # `subjects.json` is a noun phrase beginning with an article — "the outbox
    # chapter", "the isolation harness" — so a site that already wrote one gets two:
    #
    #     // The chapter 3.4 walk: a redelivery  ->  // The the broker chapter walk
    #
    # Cut with the reference, exactly like the plural. The capitalisation below then
    # sees a `before` that is just the comment opener and restores the capital, which
    # is why this is a cut rather than a lower-casing of the name.
    #
    # Only two sites in the tree, and both were found by asking for the count rather
    # than by reading the sample — the sample showed one of them.
    if not plural and name[:1].islower() and re.match(r"(?i:the|an?)\b", name):
        det = re.search(r"\b(?:[Tt]he|THE|[Aa]n?|AN?)\s+$", before_raw)
        if det:
            prefix_cut = det.start()

    # AND THE CASE TEST MUST READ THE TEXT THAT WILL ACTUALLY PRECEDE THE NAME. It read
    # `line[:m.start()]`, which still ends in "Chapters" when the plural is being cut, so
    # `// feature (T008). Chapters 3.15 and 3.16 add` came out lower-case after a period.
    before = line[:prefix_cut].rstrip()

    # AN UPPER-CASE REFERENCE AT THE START OF A LINE DECIDES NOTHING BY ITSELF, because
    # this codebase writes `CHAPTER 3.21` for emphasis in a comment that then continues
    # in ordinary case. With nothing in front of it to read, the words AFTER it are the
    # signal:
    #     // CHAPTER 3.21, and the second inbound frame  -> The typing chapter, and …
    #     // CHAPTER 3.21, AND THIS LINE HAD NO OWNER    -> THE TYPING CHAPTER, AND …
    # Keying on `ref.isupper()` alone gave `// THE TYPING CHAPTER, and the second …`,
    # caps colliding with lower case in one clause.
    tail = re.findall(r"[A-Za-z]{2,}", before)[-2:]
    ahead = re.findall(r"[A-Za-z]{2,}", line[m.end():])[:2]
    shouting = (all(w.isupper() for w in tail) if tail
                else bool(ahead) and all(w.isupper() for w in ahead))
    if shouting:
        return line[:prefix_cut] + new.upper() + line[m.end():]

    opener = COMMENT_OPENER.match(before)
    first_token = bool(opener) and not re.search(r"[a-z]", before)

    # AND PROSE OPENS A SENTENCE WITHOUT A COMMENT MARKER. This test knew three
    # shapes — nothing before it, a comment opener, or a full stop — all of which are
    # source-file shapes. Applied to a page it lower-cased the first word of a
    # metadata description:
    #
    #     "Chapter 3.3 left twelve thousand events…"   ->  "the outbox chapter left…"
    #
    # A markdown or JSON line can open a sentence after a quote, a blockquote marker,
    # a list bullet or a heading hash, and none of those is a comment opener.
    PROSE_OPENER = re.compile("^[\\s\"'>*#\u2014-]*$")
    prose_start = bool(PROSE_OPENER.match(before))

    if not before or first_token or prose_start or re.search(r"[.!?]\s*\**$", before):
        new = new[0].upper() + new[1:]

    end = m.end()
    if line[m.end():m.end() + 2] == "'s" and not ref.endswith("'s"):
        new += "'s"
        end += 2

    # AND A POSSESSIVE CAN REPEAT THE NOUN THAT NAMES THE CHAPTER.
    #
    #     3.3's outbox suite  ->  the outbox chapter's outbox suite
    #
    # Not wrong, and not something anybody would write. The name earns its keep by
    # carrying the subject, so the site's own copy of that subject is now redundant
    # — three sites, all of them `outbox`. Drop the duplicate word, not the name:
    # `the outbox chapter's suite` says what the sentence meant.
    #
    # Only the word IMMEDIATELY after the possessive, and only an exact match on one
    # of the name's own significant words. Anything looser starts deleting nouns that
    # happen to appear twice in a sentence for good reason.
    if new.endswith("'s"):
        significant = {w for w in re.findall(r"[a-z][\w-]*", name.lower())
                       if w not in ("the", "a", "an", "chapter", "chapters", "milestone")}
        nxt = re.match(r"(\s+)([\w-]+)", line[end:])
        if nxt and nxt.group(2).lower() in significant:
            end += nxt.end()
            line = line[:end] + line[end:]
            return line[:prefix_cut] + new + line[end:]

    return line[:prefix_cut] + new + line[end:]


def chapter_of(ref: str) -> int:
    return int(re.search(r"3\.(\d{1,2})", ref).group(1))


# THE TEXT ALLOWED IN FRONT OF A SENTENCE-INITIAL MARKER. A string, because it is
# concatenated with an escaped reference. THERE WERE THREE COPIES: `classify`,
# `delete_one`, and a fourth shape in the read class. Two of them still read
# `[\s"'/*]` when the third had grown `#` and `-`, so `-- Chapter 3.1 — the tenancy
# hierarchy` classified as a tag and then came out `-- the tenancy hierarchy`, the
# capital never restored because the OTHER copy decided that.
MARKER_OPENER = r"^\s*(?:it\(|describe\()?[\s\"'/*#-]*"


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
    # `'S` IN AN ALL-CAPS RUN IS STILL A POSSESSIVE. `CHAPTER 3.13'S IDEMPOTENT
    # createUser` read as prose for five references because the test was case-sensitive.
    possessive = line[e_:e_ + 2].lower() == "'s" or ref.lower().endswith("'s")
    bare = not re.match(r"(?i:chapter)", ref) and not ref.startswith("(")

    if RULE_LINE.match(line):
        return "read"                     # a section rule needs its own sentence
    if chapter_of(ref) in AMBIGUOUS:
        return "read"                     # names one of two chapters; only the sentence knows
    if possessive:
        return "substitute"               # it modifies a noun — deleting orphans the noun
    if bare:
        return "read"                     # `and 3.20 for presence` — 117, context decides

    # AND `--` AND `#` OPEN A COMMENT TOO. This class held `[\s"'/*]` only, so
    # `-- Chapter 3.1 — the tenancy hierarchy (FR-TEN-01)` — the header of every one of
    # fifteen migrations — could not match a sentence-initial marker and fell all the way
    # through to `read`. Same omission as the corpus and as `COMMENT_OPENER`, three levels
    # of the same file.
    # BUT A MARKER FOLLOWED BY A COMMA AND A CONJUNCTION IS THE SUBJECT, NOT A TAG.
    # `// Chapter 3.17. THE SUBJECT IS A ROW …` stands up without its label; delete it.
    # `// Chapter 3.22, and NOT for the reason the four above give.` does not — deleting
    # gives `// And NOT for the reason the four above give.`, a sentence with no subject
    # at all. The two shapes differ by one character of punctuation, and this test must
# sit ABOVE the deletions: `^\s*[/*\s]*<ref>\s*[.:]` matched `// Chapter 3.8:` and
# returned delete three lines before this rule was reached. Four lines in
    # `eslint.config.mjs` and `vitest.coverage.config.mts`, which are per-chapter
    # exemption lists where the chapter IS what each entry is about.
    # AND THE PUNCTUATION IS NOT ALWAYS A COMMA. A colon and a full stop introduce the
    # same clause — `// Chapter 3.8: and no notification relay either` and
    # `// Chapter 3.11. So is 402` — so it is the CONJUNCTION that decides, not the mark
    # in front of it. Restricting this to a comma caught 4 of the 23 in the tree.
    if re.match(MARKER_OPENER + re.escape(ref) + r"\s*[.,:;—-]\s*(?i:and|but|so|nor|or|yet)\b", line):
        return "substitute"

    # Now the deletions, in shape order. Everything left is `chapter 3.N` or `(3.N)`.
    # A SENTENCE-INITIAL PROVENANCE MARKER, ALONE OR WITH COMPANY.
    # `// Chapter 3.8: nor the relay` and `/** Chapter 3.23, ADR-24. Register the…` are
    # the same shape — a tag opening the comment — and the second was read-classified for
    # 124 references because a comma followed the ordinal instead of a full stop. The
    # ordinal goes and whatever it was listed beside stays.
    if re.match(r"^\s*[/*\s]*" + re.escape(ref) + r"\s*[.:]", line):
        return "delete"
    # ANY SEPARATOR, NOT JUST A FULL STOP OR A COLON. The marker shape is "the comment
    # opens with an ordinal and then says something", and the something is introduced by
    # whatever punctuation the author reached for:
    #     // Chapter 3.8 (FR-AUT-12). The failure is observable HERE
    #     // CHAPTER 3.19, PHASE 1 — THE FAILING STATE, OBSERVED.
    #     it("chapter 3.23: an edit on the fabric arrives as message.updated"
    # Requiring `.` or `:` left 86 of these in the read class, where they are not prose
    # judgements at all — they are the same tag with different punctuation.
    if re.match(MARKER_OPENER + re.escape(ref) + r"\s*[.,:;\u2014-]", line) or \
       re.match(r"^\s*[/*\s]*" + re.escape(ref) + r"\s+\(", line):
        return "delete"
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
    # A PARENTHETICAL THAT SPANS LINES IS STILL A PARENTHETICAL. Twelve references sat in
    # `/** Write a row for each threshold a usage increase crossed (chapter 3.10,` with the
    # closing bracket two lines down, and the same-line test could not see them.
    op, cl = line.rfind("(", 0, s_), line.find(")", e_)
    unclosed = op != -1 and line.find(")", op, s_) == -1
    if unclosed and (cl != -1 or line.rstrip().endswith(",")) and '"' not in line[op:cl if cl != -1 else len(line)]:
        return "delete"                   # "(chapter 3.21, FR-RTM-08)" -> "(FR-RTM-08)"

    if TEMPORAL.search(line[:s_].rstrip()):
        return "read"                     # "since chapter 3.9" is a point in time, not a cause
    if PREPOSITION.search(line[:s_].rstrip()):
        return "substitute"               # object of a preposition
    return "read"

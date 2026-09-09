#!/usr/bin/env python3
"""Apply one of the three rewrites to Part-3 chapter references in platform source.

  --rule delete       remove the provenance tag; the sentence stands without it
  --rule substitute   replace the ordinal with its subject's name from subjects.json
  --rule read         list them; this rule is a person's, not a script's

  --scope PREFIX      limit to paths starting with PREFIX (the batches)
  --apply             write. Without it, a dry run reporting counts and a sample.

THE SPLIT CHAPTER IS NEVER SUBSTITUTED AUTOMATICALLY. Old 3.14 becomes two chapters at
opposite ends of Part 3 — the error registry and the outsider milestone — so a reference
to it names one of two things and only the sentence knows which. Reading the twenty in
the tree: most are the registry, one is the outsider's exit criterion. They route to
`read`, because a comment pointing at the wrong half is worse than an ordinal.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
# OVERRIDABLE, so the same rules can be applied to the rebuild worktree. The
# rebuild starts from a tag that predates this feature, so its base still names
# ordinals; the convention has to be established there before Part 3 continues on
# top of it, or the rebuilt history ends up mixing the two.
import os
import pathlib as _pl
PLAT = (_pl.Path(os.environ["RELAY_PLATFORM"]) if os.environ.get("RELAY_PLATFORM")
        else HERE.parent.parent / "relay-platform")
sys.path.insert(0, str(HERE))

import refrules
from refrules import is_deliberate, REF, SPLIT, chapter_of, classify, controls_failing, is_versionish

NAMES = {c["was"]: c["name"] for c in json.loads((HERE / "subjects.json").read_text())["chapters"]}

def chapter_of(ref: str) -> int:
    return int(re.search(r"3\.(\d{1,2})", ref).group(1))

# A SENTENCE SPANS LINES AND `classify` READS ONE.
#
# `classify(line, m)` is line-local by contract, and that contract is right — it is
# called from two places and neither has the file. But a reference can be the OBJECT
# of a preposition that sits on the line above:
#
#     // The rest of FR-CHN and all of FR-USR go to
#     // chapter 3.13.
#
# Line-local, the second line is a bare provenance tag and deleting it is correct.
# In the paragraph it is the object of "go to", and deleting it leaves `//` and a
# sentence with nothing to end on. Two sites in the tree; the other already routed to
# `read` for an unrelated reason, so this rule moves exactly one reference — which is
# the whole argument for measuring it rather than assuming it was none or many.
#
# The knowledge lives here, in the caller that has `lines`, rather than widening the
# classifier's signature for two cases.
_OPENER = re.compile(r"^\s*(?://+|/\*\*?|\*|--+|#+)\s*")


def dangles_from_previous(lines: list, i: int, m: re.Match) -> bool:
    """Does the reference open this line while the line above it ends mid-clause?"""
    if i == 0 or not re.match(refrules.MARKER_OPENER + re.escape(m.group(0)), lines[i]):
        return False
    body = _OPENER.sub("", lines[i - 1]).rstrip()
    # AND THE WORD "CHAPTER" ITSELF SPLITS ACROSS THE LINE BREAK, which is the case
    # this check was written for and did not cover:
    #
    #     * Without this decorator every user's join would be a 403, which is chapter
    #     * 3.12's FR-044 hole exactly: …
    #
    # `PREPOSITION` and `TEMPORAL` look for a dangling function word, and "chapter" is
    # a noun. Substituting the second line alone gives "which is chapter / The
    # isolation harness's", which is the same damage as a doubled article one line up.
    # Twice now: `session.itest.ts` had "a table that chapter / The outbox chapter's
    # suite". The fix is a two-line replacement, so this routes to `read` and the
    # table records both lines.
    if re.search(r"\b[Cc]hapters?$", body):
        return True
    return bool(refrules.PREPOSITION.search(body) or refrules.TEMPORAL.search(body))


def delete_one(line: str, m: re.Match) -> str:
    """Remove the tag and leave a sentence. Four shapes, each tried in order."""
    ref = m.group(0)
    # ONLY A SENTENCE-INITIAL TAG MAY RE-CAPITALISE, and the first version capitalised
    # anything. `// then its allowance. The limiter is LAST and that is forced (chapter
    # 3.8):` became `// Then its allowance…` — a CONTINUATION line, mid-sentence, given a
    # capital because the deletion happened to be on it. Caught in the dry run before any
    # of the 821 was written.
    # THE SAME MARKER SHAPE `refrules` RECOGNISES, or the capital never gets restored.
    # This tested only `[.:]` while classification had widened to any separator, so
    # `/** Chapter 3.2, research R8: …` became `/** research R8: …` in lower case.
    tag = bool(re.match(refrules.MARKER_OPENER + re.escape(ref) + r"\s*[.,:;\u2014-]", line)) or \
          bool(re.match(r"^\s*[/*\s]*" + re.escape(ref) + r"\s+\(", line))
    # A `(3.N)` match carries its own parentheses; removing it plus the space before is
    # the whole edit. Handled first, because the generic paren shape below would look for
    # `((3.N))` and find nothing — 98 references were left untouched that way.
    if ref.startswith("("):
        return re.sub(rf"\s*{re.escape(ref)}", "", line, count=1)
    # `H` IS HORIZONTAL WHITESPACE, AND THAT IS NOT PEDANTRY. Lines are read with
    # `keepends=True`, so a trailing `\s*` reaches past the end of the line and eats
    # the terminator — the edited line then joins the one after it. Measured:
    #
    #   // …all of FR-USR go to        // …all of FR-USR go to
    #   // chapter 3.13.          ->   //
    #   <blank>                        export interface CreatedChannel {
    #   export interface …
    #
    # One reference, one comment line consumed and one blank line consumed, in a file
    # nothing else in this run touched. `\s` matching `\n` is the same fault that
    # joined five two-line tags in the published tree; it is written out here as a
    # character class so the next pattern added cannot repeat it by accident.
    H = r"[^\S\n]"
    for pat, rep in (
        (rf"{H}*\({H}*{re.escape(ref)}{H}*\)", ""),       # " (chapter 3.2)" -> ""
        (rf"{re.escape(ref)},{H}*", ""),                    # "(chapter 3.21, FR-…)" -> "(FR-…)"
        (rf",{H}*{re.escape(ref)}", ""),                    # "(FR-…, chapter 3.21)" -> "(FR-…)"
        (rf"{re.escape(ref)}{H}*[:.]{H}*", ""),             # "// Chapter 3.8: nor…" -> "// nor…"
        (rf"{re.escape(ref)}{H}+(?={H}*\()", ""),           # "// Chapter 3.8 (FR-…)" -> "// (FR-…)"
        (rf"{re.escape(ref)}{H}*[;\u2014-]{H}*", ""),        # "// CHAPTER 3.10 — the cap" -> "// the cap"
        # NO LAST-RESORT STRIP. It used to be `(rf"\s*{re.escape(ref)}", "")`, which
        # removed the reference from anywhere and left the sentence to fend for itself:
        # 16 dangling prepositions and 36 orphaned possessives reached the tree before a
        # damage scan of the diff caught them. A reference whose shape matches none of the
        # four above is not a tag, and `delete_one` now returns the line untouched — which
        # `rewrite-refs` reports as UNCHANGED rather than writing.
    ):
        new = re.sub(pat, rep, line, count=1)
        if new != line:
            new = _orphaned_punctuation(new)
            if tag:
                return refrules.recapitalise(new)
            return new
    return line


def _orphaned_punctuation(line: str) -> str:
    r"""Drop punctuation a deletion left stranded against a comment opener.

    `// (chapter 3.4). The chapter quotes the broker` -> `// The chapter quotes …`

    The parenthesised reference WAS the first sentence, so its full stop belongs to
    it and not to the sentence after. Removing the parens alone leaves `//. `, which
    reads as a typo and is one. Only fires when nothing but the opener precedes the
    punctuation — mid-sentence punctuation is somebody's, and guessing whose is how
    the last-resort strip put sixteen dangling prepositions in the tree.

    AND IT CAPTURES ITS OWN LINE TERMINATOR, for the reason `H` exists forty lines up.
    This returned an f-string built from two groups, and `(\S.*)$` stops BEFORE a
    trailing newline — `.` does not match a newline and `$` sits in front of it — so
    every line this function touched came back without its terminator and joined the
    line after it. Measured on the fan-out chapter:

        // (chapter 3.17). An application credential may send only as a bot user.
        await repo.upsertUser("publish-bot", {

    became one line, and `tsc` said `';' expected` at a column in the middle of a
    comment. The rule is the same as `H`'s and is stated twice on purpose: **a
    function that rebuilds a line from match groups must capture the terminator as a
    group.**
    """
    m = re.match(
        r"^(\s*(?://+|/\*\*?|\*|--+|#+))[^\S\n]*[.,:;][^\S\n]+(\S[^\n]*?)(\r?\n?)$", line
    )
    if not m:
        return line
    body = refrules.recapitalise(m.group(2))
    return f"{m.group(1)} {body[0].upper()}{body[1:]}{m.group(3)}"

def substitute_one(line: str, m: re.Match, prev: str | None = None) -> str:
    name = NAMES.get(f"3.{chapter_of(m.group(0))}")
    if not name:
        return line
    # THE PLACEMENT IS `refrules.place_name`, AND IT WAS A COPY HERE. The copy had no
    # plural cut and no all-caps handling, both of which the read class's version grew —
    # so `chapters 3.10 and 3.11` and `**THE ONE CHAPTER 3.21 FORGOT**` came out wrong
    # from this rule and right from that one. Two copies of a rule are two rules.
    return refrules.place_name(line, m, name, prev)

def main() -> int:
    broken = controls_failing()
    if broken:
        for b in broken:
            print(f"  BROKEN PATTERN — {b}", file=sys.stderr)
        return 1
    rule = sys.argv[sys.argv.index("--rule") + 1]
    scope = sys.argv[sys.argv.index("--scope") + 1] if "--scope" in sys.argv else ""
    apply = "--apply" in sys.argv
    found = rewritten = 0
    samples, touched = [], set()
    # ONE CORPUS, DEFINED IN `refrules`. This walked `services` and `packages` for
    # `*.ts`, which is neither every directory nor every source suffix: it missed
    # `vitest.coverage.config.mts` (37 references), `eslint.config.mjs` (24), fifteen
    # `.sql` migrations, `compose.yaml` and ten `scripts/*.mjs` — 154 in 34 files.
    if True:
        for f in refrules.platform_files(PLAT):
            if False:
                continue          # dist/ is build output, gitignored and regenerated
            rel = str(f.relative_to(PLAT))
            if scope and not rel.startswith(scope):
                continue
            lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
            changed = False
            for i, line in enumerate(lines):
                # Re-scan after each edit: an edit shifts every later offset on the line.
                while True:
                    m = next((x for x in REF.finditer(lines[i])
                              if not is_versionish(lines[i], x)
                              and (("read" if dangles_from_previous(lines, i, x)
                                    else classify(lines[i], x)) == rule)), None)
                    if not m:
                        break
                    found += 1
                    if rule == "read":
                        # EVERY match on the line, not the first. Stopping at one
                        # undercounted lines carrying two references — 295 against the
                        # classifier's 317, and the two must agree or neither is a count.
                        # THE SAME ROUTING AS THE SELECTOR ABOVE, or the two disagree
                        # by exactly the references the caller re-routes — one here.
                        # The comment above says the two must agree; that only holds
                        # if they ask the same question.
                        for x in REF.finditer(lines[i]):
                            if is_versionish(lines[i], x):
                                continue
                            cls = ("read" if dangles_from_previous(lines, i, x)
                                   else classify(lines[i], x))
                            if cls == "read":
                                found += 1
                                samples.append(f"{rel}:{i+1}  {lines[i].strip()[:96]}")
                        found -= 1
                        break
                    new = (delete_one(lines[i], m) if rule == "delete"
                             else substitute_one(lines[i], m,
                                                lines[i - 1] if i else None))
                    if new == lines[i]:
                        samples.append(f"UNCHANGED {rel}:{i+1}  {lines[i].strip()[:80]}")
                        break
                    if len(samples) < 8:
                        samples.append(f"{rel}:{i+1}\n    - {line.rstrip()[:100]}\n    + {new.rstrip()[:100]}")
                    lines[i] = new
                    rewritten += 1
                    changed = True
            if changed and apply:
                f.write_text("".join(lines), encoding="utf-8")
                touched.add(rel)
    print(f"rewrite-refs: rule={rule} scope={scope or 'all'} apply={apply}")
    print(f"  found {found}   rewritten {rewritten}   files touched {len(touched)}")
    for s in samples[:8]:
        print(f"  {s}")
    return 0

if __name__ == "__main__":
    sys.exit(main())

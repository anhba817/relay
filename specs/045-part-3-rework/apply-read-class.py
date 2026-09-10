#!/usr/bin/env python3
"""Apply the read-class decisions from `read-class.json` to a platform tree.

  RELAY_PLATFORM=<tree> python3 apply-read-class.py [--apply] [--require-all]

WHY THIS IS A TABLE AND NOT A PATCH. The reference replay applies its two rules to
every commit's TREE, so these have to apply the same way. A replacement that matches
nothing in a given tree does not fire, and that is correct — the reference has not
been written yet at that commit.

WHICH MEANS A TYPO IS INDISTINGUISHABLE FROM "NOT THERE YET", and that is the whole
risk of this shape. So `--require-all` asserts every replacement fires, and the caller
runs it against the FINAL tree where all 23 references exist. Without that check a
mistyped left-hand side is silent forever, which is the failure this file's own
subject matter is about.
"""
import collections, json, os, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import refrules

PLAT = pathlib.Path(os.environ["RELAY_PLATFORM"])
TABLE = json.loads((HERE / "read-class.json").read_text())


def main() -> int:
    apply = "--apply" in sys.argv
    require_all = "--require-all" in sys.argv
    # `--group <substring>` NARROWS THE ASSERTION, and it has to exist.
    #
    # `--require-all` was written for the one tree where every replacement in the
    # table is still unrewritten: the final tree of the first full replay. Run against
    # any later tree it reports twenty-four replacements matching nothing, and every
    # one of them is a replacement that already fired — which is indistinguishable, in
    # its output, from twenty-four typos.
    #
    # A group is added for one chapter's port and checked against that chapter's tree.
    # So the caller names the group it just wrote, and the assertion means something
    # again.
    group = None
    if "--group" in sys.argv:
        group = sys.argv[sys.argv.index("--group") + 1]

    groups = [g for g in TABLE["replacements"] if group is None or group in g["why"]]
    if group is not None and not groups:
        print(f"  no group whose reason contains {group!r}", file=sys.stderr)
        return 1
    # A DELIBERATE CONTENT-WORD DROP IS DECLARED, NOT ASSUMED. `drops` on an entry
    # lists words its pairs may lose beyond the function-word set below — and it exists
    # because the guard was right to stop the one case that needed it: a sentence
    # crediting a chapter with a removal that never happened cannot be fixed without
    # losing the word `removed`. Declaring it puts the intent in the table next to the
    # reason, where the next reader of that entry sees it. An undeclared drop still
    # fails, which is the whole value of the guard.
    # BACKTICKS ARE STRIPPED ON BOTH SIDES OF THIS COMPARISON. The tokeniser's class
    # keeps a trailing backtick, so `addMember` tokenises as "addMember`" — and a person
    # writing `drops` should not have to know that.
    pairs = [(p[0], p[1], g["why"],
              frozenset(w.lower().strip("`") for w in g.get("drops", [])))
             for g in groups for p in g["pairs"]]
    fired = {old: 0 for old, _, _, _ in pairs}

    # A LINE THAT IS DELIBERATELY THE SAME IN SEVERAL FILES IS DECLARED, NOT ASSUMED —
    # and the declaration carries the COUNT, which is what makes it a check rather than
    # a way out.
    #
    # The rule below refuses a pair that fires more than once, because a read-class
    # decision is about one site a person read and firing elsewhere means the decision
    # was applied where nobody looked. That is right almost always. It is wrong for a
    # comment three lane configs carry verbatim: `// The quota relay, the fourth. Same
    # reason as the other three.` appears in the coverage, api and dispatcher configs
    # with identical neighbours, so no amount of context makes the left-hand side
    # unique, and three separate pairs would be three copies of one decision.
    #
    # `expect` maps such a line to the number of places it is expected in. Firing a
    # different number of times still fails — a fourth lane, or one deleted, and the
    # count is wrong — so this widens what can be declared without widening what goes
    # unchecked.
    expect = {}
    for g in groups:
        for lhs, n in g.get("expect", {}).items():
            expect[lhs] = n

    # THE GUARD RUNS BEFORE ANY FILE IS TOUCHED, and it did not always. It sat after
    # the write loop, so a table whose word-count check failed had ALREADY been applied:
    # the run printed `WORDS DROPPED`, exited 1, and left eighteen of nineteen
    # replacements in the tree. Fixing the table and re-running then reported
    # `0 applied, 124 matched nothing` — every left-hand side gone, because the failing
    # run had made the edits it was refusing to stand behind. A check that fires after
    # the side effect is a report, not a guard.
    # A REWRAP MUST NOT DROP A WORD, AND ONE DID.
    #
    # A two-line replacement that rewraps has to fit the same text into different line
    # breaks, and trimming to fit is silent: `Every pass compared` became `Every pass`
    # and the next line went on `requirements to tasks`. Nothing in this file could
    # see it, because both sides were the right shape.
    #
    # So the words are counted. A replacement may LOSE the reference's own words — an
    # ordinal, the word `chapter` — and may gain the subject name's. Losing anything
    # else means text went missing.
    import re as _re
    # The reference's own words go by definition, and rewording a clause moves
    # function words and verb inflections around. What must not happen is a CONTENT
    # word disappearing with no trace of it in the replacement.
    ALLOWED_LOSS = {
        "chapter", "chapters",
        "a", "an", "the", "in", "at", "on", "of", "to", "for", "with", "from",
        "by", "as", "and", "or", "is", "was", "are", "were", "be", "been",
        "it", "its", "this", "that", "which", "there", "here", "one",
        # Temporal and deictic words a rewording routinely replaces with a phrase:
        # "Until then" becomes "Until the endpoint over it".
        "then", "now", "still", "already", "when", "since", "until", "before",
        "after", "so", "but", "not", "no", "all", "both", "each", "own",
    }
    # A POSSESSIVE OF AN ALLOWED WORD IS ALLOWED TOO. `chapter's` is the reference's
    # own word carrying an apostrophe, and the tokeniser keeps it attached.
    ALLOWED_LOSS |= {w + "'s" for w in ALLOWED_LOSS}

    def words(t):
        # TWO CHARACTERS MINIMUM. `3.12's` tokenises to a bare `s` — the digits are
        # not letters and the apostrophe is not a word start — and a one-letter
        # fragment is never a content word. Left in, it reported `{'s': 1}` for every
        # possessive reference the table removes.
        return [w for w in _re.findall(r"[A-Za-z][A-Za-z'`-]*", t) if len(w) > 1]

    for old_s, new_s, why, drops in pairs:
        kept = {w.lower()[:5] for w in words(new_s)}
        lost = collections.Counter(words(old_s)) - collections.Counter(words(new_s))
        unexplained = {
            w: n for w, n in lost.items()
            if w.lower() not in ALLOWED_LOSS
            and w.lower().strip("`") not in drops
            # `arrived` -> `arrives` is a rewording, not a loss: the stem survives.
            and w.lower()[:5] not in kept
        }
        if unexplained:
            print(f"  WORDS DROPPED {unexplained}: {old_s.splitlines()[0][:70]}",
                  file=sys.stderr)
            return 1

    for f in refrules.platform_files(PLAT):
        text = f.read_text(encoding="utf-8")
        out = text
        for old, new, _, _ in pairs:
            if old in out:
                # COUNT, DO NOT JUST FLAG. A left-hand side matching twice in one file
                # means the sentence is not unique and the decision was made about one
                # of two places.
                fired[old] += out.count(old)
                out = out.replace(old, new)
        if out != text and apply:
            f.write_text(out, encoding="utf-8")

    total = sum(fired.values())
    missed = [old for old, n in fired.items() if n == 0]
    doubled = [(old, n) for old, n in fired.items()
               if n > 1 and expect.get(old) != n]
    # A DECLARED COUNT THAT DID NOT HAPPEN IS ALSO A FAILURE, in the direction a
    # declaration normally hides: `expect` says three and the tree holds two.
    #
    # `n > 0` GUARDS IT, AND THE REPLAY IS WHY. These pairs run against every tree in a
    # chapter's range, and a line only exists from the commit that writes it — so
    # `expect: 3` means "wherever this fires, it fires three times", not "three in every
    # tree". Without the guard the replay died on commit 1 of 9 with `DECLARED 3x, FIRED
    # 0x`, which is the table telling the truth about a tree where the line is correctly
    # absent. Matching nothing is already the table's normal case and is not an error.
    miscounted = [(old, n, expect[old]) for old, n in fired.items()
                  if old in expect and n > 0 and expect[old] != n]

    scope = "all groups" if group is None else f"group {group!r}"
    print(f"apply-read-class: {scope} — {len(pairs)} replacements, {total} applied, "
          f"{len(missed)} matched nothing, apply={apply}")
    for old, n in doubled:
        print(f"  NOT UNIQUE ({n}x): {old.splitlines()[0][:88]}")
    if require_all and missed:
        for old in missed:
            print(f"  MATCHED NOTHING: {old.splitlines()[0][:88]}", file=sys.stderr)
        print(f"  {len(missed)} replacement(s) matched nothing in a tree where all of "
              f"them should — a mistyped left-hand side is silent otherwise",
              file=sys.stderr)
        return 1
    for old, n, want in miscounted:
        print(f"  DECLARED {want}x, FIRED {n}x: {old.splitlines()[0][:80]}", file=sys.stderr)
    if doubled or miscounted:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

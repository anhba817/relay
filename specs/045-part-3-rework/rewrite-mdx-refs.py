#!/usr/bin/env python3
"""Substitute Part-3 chapter ordinals in a chapter's PROSE with their subject's name.

  rewrite-mdx-refs.py <page.mdx> [--apply]

WHY PROSE IS SUBSTITUTED AND NOT DELETED. In source, a chapter reference is usually
provenance — "(chapter 3.8)" beside a line that needs no pointer — and the sentence
stands without it. In prose it is navigation: the reader is being sent somewhere, and
deleting the destination leaves "the chapter that did this" with no chapter. So the
`delete` class does not apply here and every reference substitutes.

INSIDE FENCES IS NOT PROSE. A fence body is bytes the chain compares against the
platform, and the platform's own references were rewritten by `rewrite-refs.py`
already. Touching them here would put the two out of step and the mirror would fail
before the chain did. Fenced regions are skipped, and `--apply` refuses to run if the
fence count changes.

AND THE PLACEMENT IS `refrules.place_name`, the same implementation the source pass
uses. Two copies of a rule are two rules — this file exists because prose needs a
different CLASSIFIER, not a different placer.
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import json
import refrules
from refrules import REF, is_versionish, place_name

NAMES = {c["was"]: c["name"] for c in json.loads((HERE / "subjects.json").read_text())["chapters"]}


# new ordinal -> the OLD ordinal that chapter was, from the map. Splits contribute
# both halves, each pointing back at the one old chapter they came from.
def _old_for_new() -> dict[str, str]:
    m = json.loads((HERE / "chapter-map.json").read_text())
    out: dict[str, str] = {}
    for c in m["chapters"]:
        if c.get("old") and c.get("new"):
            out[f"3.{c['new']}"] = f"3.{c['old']}"
    for sp in m.get("splits", []):
        for half in sp["halves"]:
            out[f"3.{half['new']}"] = f"3.{sp['old']}"
    for r in m.get("reassignments", []):
        for key in ("prose_stays_at", "code_moves_to"):
            if r.get(key):
                out.setdefault(f"3.{r[key]}", f"3.{r['old']}")
    return out


OLD_FOR_NEW = _old_for_new()


def own_id(text: str) -> str | None:
    """The chapter's OWN ordinal in the OLD numbering — which is not the one in its header.

    THE HEADER CARRIES THE NEW NUMBER AND EVERY REFERENCE IN THE PROSE IS AN OLD ONE, so
    comparing them is comparing two different namespaces. `<ChapterHeader id="3.12" />` is
    new chapter 12 (the fan-out chapter, old 3.18); a sentence saying "chapter 3.12" means
    the isolation gauntlet. This function returned the header's id, so the pass skipped
    every reference to old chapter N inside new chapter N — silently, as "the chapter's
    own id".

    **It is a hazard for all twenty-three ported chapters and it bit two.** Chapter 7
    (old 3.7, new 7 — the one coincidence in the renumbering) kept a table row reading
    `| **3.7** |` among rows that name their subject, and chapter 8 kept "Part 3 ends at
    3.14" — a sentence that was true of the old order and is false of this one. Neither is
    visible to a gate: an ordinal in prose is bytes like any other.

    Resolved through the map instead, so the comparison is old-to-old.
    """
    m = re.search(r'<ChapterHeader id="(3\.\d+)"', text)
    if not m:
        return None
    return OLD_FOR_NEW.get(m.group(1), m.group(1))


def in_code_span(line: str, start: int) -> bool:
    """Is the character at `start` inside a single-backtick code span?

    A QUOTED ORDINAL IS NOT A POINTER. Prose that discusses the convention writes the
    ordinal as a string — "`the outbox chapter` encodes no position; `chapter 3.3`
    encodes one and nothing checks it" — and substituting inside the quotation inverts
    the sentence it is illustrating. Two of these exist across the ported chapters and
    the substitution destroyed one of them.

    Counted by backticks before the position, not by a regex over the span: a pattern
    matching "backtick, anything, ordinal, anything, backtick" also matches the GAP
    between two adjacent code spans, which is prose and must be substituted. Four of the
    six candidates in these pages are that shape.
    """
    return line.count("`", 0, start) % 2 == 1


def main(path: str, apply: bool) -> int:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    mine = own_id(text)
    lines = text.split("\n")
    fences_before = sum(1 for l in lines if l.startswith("```"))

    inside, changed, samples, skipped = False, 0, [], 0
    for i, line in enumerate(lines):
        if line.startswith("```"):
            inside = not inside
            continue
        if inside:
            continue
        while True:
            m = next(
                (
                    x
                    for x in REF.finditer(lines[i])
                    if not is_versionish(lines[i], x)
                    and not in_code_span(lines[i], x.start())
                    # The chapter's OWN id is not a reference to elsewhere.
                    and not re.search(r'<Chapter(Header|Footer) id="', lines[i])
                    and f"3.{refrules.chapter_of(x.group(0))}" != mine
                    and f"3.{refrules.chapter_of(x.group(0))}" in NAMES
                    # AMBIGUOUS OLD CHAPTERS ARE A PERSON'S, HERE TOO. `refrules`
                    # routes them to `read` for source, and this pass had no such
                    # test — so it substituted old 3.12 with one half's name and
                    # would have sent a reader to the gauntlet milestone for a
                    # sentence about the harness. Two copies of a rule are two
                    # rules, and the second one was missing a clause.
                    and refrules.chapter_of(x.group(0)) not in refrules.AMBIGUOUS
                ),
                None,
            )
            if not m:
                break
            name = NAMES[f"3.{refrules.chapter_of(m.group(0))}"]
            new = place_name(lines[i], m, name, lines[i - 1] if i else None)
            if new == lines[i]:
                skipped += 1
                break
            if len(samples) < 6:
                samples.append(f"{i+1}\n    - {lines[i].strip()[:96]}\n    + {new.strip()[:96]}")
            lines[i] = new
            changed += 1

    out = "\n".join(lines)
    fences_after = sum(1 for l in out.split("\n") if l.startswith("```"))
    if fences_after != fences_before:
        print(f"  FENCE COUNT MOVED {fences_before} -> {fences_after} — refusing", file=sys.stderr)
        return 1
    if apply:
        p.write_text(out, encoding="utf-8")
    print(f"rewrite-mdx-refs: {'APPLIED' if apply else 'DRY RUN'} — {p.parent.name}")
    print(f"  own id {mine}   substituted {changed}   unchanged {skipped}")
    if left := [
        (i + 1, m.group(0), l.strip()[:74])
        for i, l in enumerate(out.split("\n"))
        for m in REF.finditer(l)
        if not is_versionish(l, m)
        # THE SAME FILTER THE SELECTOR USES, or the report names references the pass was
        # never going to touch. It reported the one quoted ordinal in the user-surface
        # chapter as "left for a reader" when nothing was left: the selector skips a code
        # span and this loop did not.
        and not in_code_span(l, m.start())
        and refrules.chapter_of(m.group(0)) in refrules.AMBIGUOUS
    ]:
        print(f"  {len(left)} ambiguous reference(s) left for a reader:")
        for ln, ref, txt in left:
            print(f"    {ln:>5}  {ref:<13} {txt}")
    for s in samples:
        print(f"  {s}")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--apply"]
    raise SystemExit(main(args[0], "--apply" in sys.argv))

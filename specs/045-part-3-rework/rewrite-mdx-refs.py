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


def own_id(text: str) -> str | None:
    m = re.search(r'<ChapterHeader id="(3\.\d+)"', text)
    return m.group(1) if m else None


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

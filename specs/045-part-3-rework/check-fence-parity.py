#!/usr/bin/env python3
"""Every fence, titled or not, appears in both locales.

WHY THIS EXISTS. `check-fence-chain.mjs:77` collects a fence only when it matches
`title="…"`. In Part 3 that is 623 fences per locale — and there are 99 more it never
sees: console transcripts, worked diagrams, output examples. The mirror compares the 623
byte for byte and is blind to the rest.

That matters because the Vietnamese task is an instruction to replace everything which
is not a fence. A placeholder that dropped those 99 would pass `check:fences`,
`check:docs` and every other gate, and silently delete real content from 25 published
pages. Analysis pass 4 found it; FR-010 names untitled fences because of it.

WHAT IT CHECKS. Per chapter, per locale: the count of every opening fence, and the
sequence of their languages. Byte comparison of untitled bodies is deliberately NOT
attempted — an untitled fence is not addressed by anything, so there is no key to pair
them on beyond position, and position is what the language sequence already checks.
"""
import pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
TUT = HERE.parent.parent / "relay-tutorial"

def fences(path: pathlib.Path):
    titled, untitled = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^```(\w+)( title=\"([^\"]+)\")?\s*$", line)
        if not m:
            continue
        (titled if m.group(2) else untitled).append(m.group(1))
    return titled, untitled

def chapters(base: pathlib.Path):
    out = {}
    for p in base.rglob("page.mdx"):
        m = re.search(r"part-(\d+)/chapter-(\d+)", str(p))
        if m:
            out[f"{int(m.group(1))}.{int(m.group(2)):02d}"] = p
    return out

def main() -> int:
    en = chapters(TUT / "app" / "(en)")
    vi = chapters(TUT / "app" / "(vi)" / "vi")
    problems, t_tot, u_tot = [], 0, 0
    for key in sorted(en):
        if key not in vi:
            continue                      # not yet translated — the mirror skips these too
        et, eu = fences(en[key])
        vt, vu = fences(vi[key])
        t_tot += len(et)
        u_tot += len(eu)
        if len(et) != len(vt):
            problems.append(f"{key}: {len(et)} titled fences in en, {len(vt)} in vi")
        if len(eu) != len(vu):
            problems.append(
                f"{key}: {len(eu)} UNTITLED fences in en, {len(vu)} in vi "
                f"— the mirror cannot see these"
            )
        if eu != vu:
            problems.append(f"{key}: untitled fence languages differ — en {eu} vi {vu}")
    if not t_tot and not u_tot:
        problems.append("no fences parsed at all — the fence syntax changed")

    for p in problems:
        print(f"  {p}", file=sys.stderr)
    print(f"check-fence-parity: {len(en)} en chapters, {len(vi)} vi, "
          f"{t_tot} titled and {u_tot} untitled fences compared, {len(problems)} problem(s)")
    print("check-fence-parity: counts and languages — untitled bodies have no key to pair on")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())

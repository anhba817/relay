#!/usr/bin/env python3
"""Every renumbered Part-3 URL still resolves — derived from the map, not restated.

WHY THIS IS NOT A LIST. Twenty-six chapters were renumbered and there are forty-eight
redirects, and a hand-written table of forty-eight would be the fourth consumer of
`chapter-map.json` maintained by somebody remembering. `was_url` is in the map; the
expected set is a function of it.

FORTY-EIGHT ACROSS TWENTY-SIX CHAPTERS, and the arithmetic is the split. Two old chapters
became two each — old 12 into the isolation harness and the gauntlet milestone, old 14
into the error registry and the outsider — so twenty-four old addresses map onto
twenty-six new chapters, and each locale contributes twenty-four.

MATCHED BY SLUG, NOT BY NUMBER. `milestone-the-isolation-gauntlet` was old 12 and is new
25; the harness half at new 4 has a slug that never had a URL. Numbering the redirects
would have sent old 12 to new 4, which is the wrong half of its own split.

WHAT IT CANNOT SEE. That Next.js serves them. A `redirects()` entry this script matches is
still a claim about a file rather than about a running server — `pnpm build` and a request
are the only things that settle that, which is why T040 asks for both.

    check-redirects.py            compare next.config.ts with the map
    check-redirects.py --emit     print the block to paste, derived
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAP = json.loads((HERE / "chapter-map.json").read_text(encoding="utf-8"))
CONFIG = HERE.parent.parent / "relay-tutorial" / "next.config.ts"


def expected() -> list[tuple[str, str]]:
    """The addresses that MOVED, both locales.

    ONLY WHERE THE URL CHANGES. The first version emitted one per old chapter and
    produced `/part-3/chapter-01/tenants-all-the-way-down` redirecting to itself, for
    every chapter the reorder left in place. Next.js follows a redirect whose source
    equals its destination straight into a loop, so those are not merely useless.

    THE COUNT IS THEREFORE NOT 48, and T038's 48 was arithmetic rather than a
    measurement: 24 old chapters times two locales, before asking which ones moved.
    """
    out = []
    for c in MAP["chapters"]:
        was = c.get("was_url")
        if not was:
            continue
        tail = f"chapter-{c['new']:02d}/{c['slug']}"
        new = f"part-3/{tail}"
        # COMPARED WITHOUT THE `part-3/` PREFIX, because `was_url` does not carry one.
        # The first comparison put the prefix on one side only, so nothing ever matched
        # as unmoved and the self-redirects it was written to exclude went straight
        # through it. The check reported 48/48 green over two of them.
        if was == tail:
            continue
        out.append((f"/part-3/{was}", f"/{new}"))
        out.append((f"/vi/part-3/{was}", f"/vi/{new}"))
    return out


def emit() -> str:
    lines = [
        "  async redirects() {",
        "    // THE RENUMBERED PART-3 ADDRESSES, DERIVED FROM `chapter-map.json`.",
        "    //",
        "    // Twenty-one moved addresses, two locales, forty-two permanent redirects. The",
        "    // map's `was_url` is the source; `check-redirects.py` compares this block with it",
        "    // and fails on a drift in either direction, so this is generated rather than kept.",
        "    //",
        "    // NOT 48, WHICH THE TASK ASKED FOR. That was 24 old chapters times two locales,",
        "    // and three of the 24 kept their address exactly — chapters 1, 2 and 7. A redirect",
        "    // whose source equals its destination is a loop, so the arithmetic would have",
        "    // shipped three of them.",
        "    //",
        "    // PERMANENT, because the old numbers are never coming back: a chapter's position",
        "    // is what this feature removed from every reference in the series.",
        "    return [",
    ]
    for src, dst in expected():
        lines.append(f'      {{ source: "{src}", destination: "{dst}", permanent: true }},')
    lines += ["    ];", "  },"]
    return "\n".join(lines)


def main() -> int:
    if "--emit" in sys.argv:
        print(emit())
        return 0
    text = CONFIG.read_text(encoding="utf-8")
    found = set(
        (m.group(1), m.group(2))
        for m in re.finditer(r'source:\s*"([^"]+)",\s*destination:\s*"([^"]+)"', text)
    )
    want = set(expected())
    missing = sorted(want - found)
    extra = sorted(found - want)
    for src, dst in missing:
        print(f"  MISSING  {src} -> {dst}")
    for src, dst in extra:
        print(f"  UNEXPECTED  {src} -> {dst}")
    # THE POSITIVE CONTROL. An empty expectation would report nothing missing and pass,
    # which is how this shape of check dies — and `was_url` arriving absent from the map
    # is exactly the way that happens.
    if not want:
        print("check-redirects: derived NO expectations — the map has no `was_url`, so this is broken")
        return 1
    print(
        f"check-redirects: {len(want)} derived, {len(found)} in next.config.ts, "
        f"{len(missing)} missing, {len(extra)} unexpected"
    )
    print("check-redirects: the file only — whether Next.js serves them needs a build and a request")
    return 1 if (missing or extra) else 0


if __name__ == "__main__":
    raise SystemExit(main())

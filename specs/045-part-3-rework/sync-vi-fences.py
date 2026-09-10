#!/usr/bin/env python3
"""Copy an English chapter's fence BODIES into its Vietnamese page, leaving prose alone.

WHY THIS IS NOT `vi-placeholder.py`. That tool regenerates a whole Vietnamese page as a
placeholder: it keeps the fences byte-identical and replaces the PROSE with a standing
notice. It is the right tool for a chapter nobody has translated. It is the wrong tool
for one somebody has — and after a repair replay changes a chapter's tree, a translated
chapter needs its fences moved and its prose left exactly where the translator left it.

WHAT THE MIRROR REQUIRES, precisely. `check-fence-chain.mjs` compares each Vietnamese
chapter's fence LIST and every fence BODY against the English chapter of the same key,
and reports the difference as MIRROR. Prose is not compared — no instrument in either
repository reads it — so prose is the half this tool must not touch.

MATCHED BY TITLE, AND BY OCCURRENCE WHERE A TITLE REPEATS. A chapter may fence the same
path twice — two `(excerpt)` views of one file — so the nth fence titled T on one side
pairs with the nth on the other. That is deterministic; guessing across DIFFERENT titles
by position is not, and is refused below.

WHAT IS REFUSED: a per-title count that differs between the two pages. Chapter 10 fences
`sentinel.sql (excerpt)` twice and chapter 11 fences `docs/04-srs.md (excerpt)` twice —
both fine. A page holding two where the other holds one is structural, and copying bodies
would paper over it.

AND IT REFUSES A COUNT MISMATCH. If the two pages hold different numbers of titled
fences, something structural differs and copying bodies would paper over it — the
Vietnamese page is missing a fence or carries one the English page dropped, which is a
`vi-placeholder` job or a person's.

    sync-vi-fences.py <en-chapter-dir> [--apply]
"""
import re
import sys
from pathlib import Path

FENCE = re.compile(r'^```(\w+) title="([^"]+)"\n(.*?)^```$', re.M | re.S)


def fences(text: str) -> list[tuple[str, str, str, int, int]]:
    return [(m.group(1), m.group(2), m.group(3), m.start(), m.end()) for m in FENCE.finditer(text)]


def main(en_dir: str, apply: bool = False) -> int:
    en = Path(en_dir)
    vi = Path(str(en).replace("/(en)/", "/(vi)/vi/"))
    if not vi.joinpath("page.mdx").exists():
        print(f"sync-vi-fences: no Vietnamese page at {vi} — nothing to sync")
        return 0
    en_text = en.joinpath("page.mdx").read_text(encoding="utf-8")
    vi_text = vi.joinpath("page.mdx").read_text(encoding="utf-8")

    en_f, vi_f = fences(en_text), fences(vi_text)
    if len(en_f) != len(vi_f):
        print(f"sync-vi-fences: {len(en_f)} EN fences and {len(vi_f)} VI — structural, not a body sync")
        return 1
    from collections import Counter
    en_counts, vi_counts = Counter(t for _, t, _, _, _ in en_f), Counter(t for _, t, _, _, _ in vi_f)
    if en_counts != vi_counts:
        for title in sorted(set(en_counts) | set(vi_counts)):
            if en_counts[title] != vi_counts[title]:
                print(f"sync-vi-fences: {title} — EN {en_counts[title]}, VI {vi_counts[title]}")
        return 1

    by_key: dict[tuple[str, int], tuple[str, str]] = {}
    seen: Counter = Counter()
    for lang, title, body, _, _ in en_f:
        by_key[(title, seen[title])] = (lang, body)
        seen[title] += 1

    changed, out, cursor = [], [], 0
    vi_seen: Counter = Counter()
    for lang, title, body, start, end in vi_f:
        key = (title, vi_seen[title])
        vi_seen[title] += 1
        en_lang, en_body = by_key[key]
        out.append(vi_text[cursor:start])
        if en_body != body or en_lang != lang:
            changed.append(title)
            out.append(f'```{en_lang} title="{title}"\n{en_body}```')
        else:
            out.append(vi_text[start:end])
        cursor = end
    out.append(vi_text[cursor:])

    print(f"sync-vi-fences: {'APPLIED' if apply else 'DRY RUN'} — {en.name}")
    print(f"  {len(en_f)} fences, {len(changed)} body/language difference(s)")
    for t in changed:
        print(f"    {t}")
    if apply and changed:
        vi.joinpath("page.mdx").write_text("".join(out), encoding="utf-8")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    raise SystemExit(main(args[0], "--apply" in sys.argv))

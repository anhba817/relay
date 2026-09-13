#!/usr/bin/env python3
"""Regenerate one chapter's Vietnamese page as a placeholder that mirrors its fences.

CARRIED FROM specs/045-part-3-rework/ AND GENERALISED BY ONE CHARACTER CLASS. 045's copy
matches `id="(3\\.\\d+)"` and dies with `AttributeError: 'NoneType'` on a Part 4 chapter
— a Part 3 instrument, in a closed feature's directory, wired to nothing. Copied rather
than edited in place because 045 is closed, and docs/12-part-4-structure.md section 6
already records that all six of those instruments are gates nobody runs.

WHAT THE MIRROR REQUIRES. `check-fence-chain.mjs` walks the Vietnamese chapters that
EXIST and compares each one's fence LIST and every fence BODY against the English chapter
of the same key. So a placeholder cannot drop the fences, and it cannot reformat them —
it keeps them byte-identical and replaces only the prose between them. Deleting the page
would pass the mirror by being skipped, which is the cheapest option and the wrong one:
it removes a published translated chapter from the site.

The user supplies translations. Nothing here invents Vietnamese beyond the standing
notice, and the existing page's own title is kept when it has one.

Usage: vi-placeholder.py <en-chapter-dir> [--apply]
"""
import re, sys
from pathlib import Path

NOTICE = (
    "> **Bản dịch đang được chuẩn bị.** Phần diễn giải của chương này chưa được dịch sang\n"
    "> tiếng Việt. Các khối mã bên dưới là bản gốc tiếng Anh và giống hệt bản tiếng Anh của\n"
    "> chương — bạn có thể gõ theo chúng ngay bây giờ. Bản dịch đầy đủ sẽ thay thế trang này."
)

def main(en_dir, apply=False):
    en = Path(en_dir)
    vi = Path(str(en).replace("/(en)/", "/(vi)/vi/"))
    src = en.joinpath("page.mdx").read_text(encoding="utf-8")
    num = re.search(r'<ChapterHeader id="(\d+\.\d+)"', src).group(1)
    slug = en.name
    route = re.search(r'canonical: "([^"]+)"', src).group(1)

    L = src.split("\n")
    kept, i = [], 0
    while i < len(L):
        if re.match(r"^```", L[i]):
            end = next(j for j in range(i + 1, len(L)) if L[j].startswith("```"))
            kept += L[i:end + 1] + [""]
            i = end + 1
            continue
        if L[i].startswith("## "):
            kept += [L[i], ""]
        i += 1

    prev = vi.joinpath("page.mdx").read_text(encoding="utf-8") if vi.joinpath("page.mdx").exists() else ""
    m = re.search(r'title: "([^"]+)"', prev)
    title = m.group(1) if m else re.search(r'title: "([^"]+)"', src).group(1)

    page = (
        'import { ChapterHeader, ChapterFooter } from "@/components/tutorial/chapter-shell";\n\n'
        "export const metadata = {\n"
        f'  title: "{title}",\n'
        "  description:\n"
        '    "Bản dịch tiếng Việt của chương này đang được chuẩn bị. Toàn bộ mã nguồn bên dưới giữ nguyên như bản tiếng Anh.",\n'
        "  alternates: {\n"
        f'    canonical: "/vi{route}",\n'
        "    languages: {\n"
        f'      en: "{route}",\n'
        f'      vi: "/vi{route}",\n'
        "    },\n  },\n};\n\n"
        f'<ChapterHeader id="{num}" locale="vi" />\n\n'
        f"{NOTICE}\n\n"
        + "\n".join(kept).rstrip()
        + f'\n\n<ChapterFooter id="{num}" locale="vi" />\n'
    )
    if apply:
        vi.mkdir(parents=True, exist_ok=True)
        vi.joinpath("page.mdx").write_text(page, encoding="utf-8")
        # THIS USED TO `unlink()` THE SIBLING `figures.ts` when the placeholder it
        # generated imported no figures, and it cost the site its build for the whole
        # of Part 3's rebuild. The placeholder is a page nobody has translated yet;
        # the file beside it holds Vietnamese somebody wrote. Ten of them were deleted
        # by ten chapter ports, each page was later translated with its figure imports
        # restored, and every one of those imports pointed at nothing.
        #
        # An unused module breaks NOTHING — no gate reads it, the bundler drops it.
        # An absent one breaks `next build` outright, and that is unrecoverable from
        # the working tree alone: the content had to come back out of the commit
        # before each deletion. So it is left in place and reported.
        fig = vi / "figures.ts"
        if fig.exists() and "./figures" not in page:
            print(f"  note: {fig.relative_to(fig.parents[4])} is unused by this "
                  f"placeholder and was KEPT — a later translation will import it")

    def fences(text):
        Ls, o, i = text.split("\n"), [], 0
        while i < len(Ls):
            m2 = re.match(r'^```(\w+)(?: title="([^"]+)")?$', Ls[i])
            if m2:
                e = next(j for j in range(i + 1, len(Ls)) if Ls[j].startswith("```"))
                o.append((m2.group(1), m2.group(2), "\n".join(Ls[i + 1:e])))
                i = e
            i += 1
        return o
    # TWO COMPARISONS, AND THE FIRST ONE CANNOT FAIL.
    #
    # This compared `fences(src)` against `fences(page)` — the page it had just built
    # in memory, out of those same fences. In a dry run that is the generator checked
    # against its own input, and it reported `identical: True` over an EN page 3,074
    # lines long and a VI page of 1,627 with a different fence list entirely. A check
    # that can only pass is worse than no check: it was the only signal here, and it
    # said the mirror was satisfied.
    #
    # It is kept, because it IS a real self-test of the generator — a fence dropped or
    # reformatted while being copied would show up here — but it is labelled as what
    # it is, and the comparison that decides the exit code reads the DISK.
    a, generated = fences(src), fences(page)
    self_ok = a == generated

    on_disk = vi / "page.mdx"
    disk = fences(on_disk.read_text(encoding="utf-8")) if on_disk.exists() else None

    print(f"vi-placeholder: {'APPLIED' if apply else 'DRY RUN'} — {slug}")
    print(f"  generator self-test: {len(a)} EN fences copied, identical: {self_ok}")
    if disk is None:
        print(f"  VI page on disk: ABSENT — the mirror skips it, which passes by omission")
        return 0 if self_ok else 1
    disk_ok = a == disk
    print(f"  EN fences {len(a)} / VI ON DISK {len(disk)} — identical: {disk_ok}"
          + ("" if disk_ok else "   <-- run with --apply"))
    if not disk_ok and not apply:
        # Say WHICH, because a count that differs by 34 is not a diagnosis.
        ea, eb = [(l, t) for l, t, _ in a], [(l, t) for l, t, _ in disk]
        only_en = [x for x in ea if x not in eb]
        only_vi = [x for x in eb if x not in ea]
        for l, t in only_en[:6]:
            print(f"    EN only: {t or '(untitled ' + l + ')'}")
        for l, t in only_vi[:6]:
            print(f"    VI only: {t or '(untitled ' + l + ')'}")
        bodies = [t for (l, t, ba), (_, _, bb) in zip(a, disk) if ba != bb and t]
        for t in bodies[:4]:
            print(f"    body differs: {t}")
    return 0 if (self_ok and disk_ok) else 1

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--apply"]
    sys.exit(main(args[0], apply="--apply" in sys.argv))

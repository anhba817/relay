#!/usr/bin/env python3
"""Regenerate one chapter's Vietnamese page as a placeholder that mirrors its fences.

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
    num = re.search(r'<ChapterHeader id="(3\.\d+)"', src).group(1)
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
        fig = vi / "figures.ts"
        if fig.exists() and "./figures" not in page:
            fig.unlink()

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
    a, b = fences(src), fences(page)
    ok = a == b
    print(f"vi-placeholder: {'APPLIED' if apply else 'DRY RUN'} — {slug}")
    print(f"  EN fences {len(a)} / VI fences {len(b)} — identical: {ok}")
    return 0 if ok else 1

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--apply"]
    sys.exit(main(args[0], apply="--apply" in sys.argv))

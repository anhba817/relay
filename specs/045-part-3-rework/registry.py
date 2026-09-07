#!/usr/bin/env python3
"""T023a/T023b: renumber, reorder and split the chapter registry.

`relay-tutorial/lib/tutorial.ts` is 810 hand-maintained lines and NOTHING READ IT until
`check-registry.py` was written for this feature. A renumbering that skipped it leaves
`check:fences` green and every navigation link in the book pointing at a 404.

THE VIETNAMESE IS DIVIDED, NEVER WRITTEN. `titleVi` and `readerProducesVi` for the two
halves are substrings and recompositions of the existing entry's own words. The user owns
translation and this script must not invent any.
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
REG = HERE.parent.parent / "relay-tutorial" / "lib" / "tutorial.ts"
MAP = json.load(open(HERE / "chapter-map.json"))
APPLY = "--apply" in sys.argv

NEW = {}          # old id -> (new number, slug)
for c in MAP["chapters"]:
    NEW.setdefault(c["old"], []).append((c["new"], c["slug"]))

SPLIT_OLD = MAP["split"]["old"]

# The two halves, each field either divided from the original or newly written English.
HALF_REGISTRY = dict(
    num=3, slug="errors-that-resolve", title="Errors that resolve",
    titleVi="Lỗi có trang để xem",
    comment=("        // Split out of the milestone on the boundary its own prose already had:\n"
             "        // every fence above `## The outsider` is the error vocabulary and every\n"
             "        // fence below it is the sealed package. 14 titled fences here, 7 there.\n"),
    readerProduces=("Thirteen error codes with one registry and one URL rule, and a docs_url "
                    "that resolves against the published site"),
    readerProducesVi=("Mười ba error code với một registry và một luật URL duy nhất, và một "
                      "docs_url resolve được vào tài liệu đã xuất bản"),
    sourceDoc="docs/04-srs.md, docs/08-error-reference.md", readerMinutes=49,
)
HALF_OUTSIDER = dict(
    num=25, slug="errors-that-resolve-and-an-outsider",
    title="Milestone: an outsider integrates",
    titleVi="Cột mốc: một người ngoài tích hợp",
    comment=("        // The milestone name lives here rather than on the gauntlet, because the\n"
             "        // Phase 2 exit criterion is what this chapter gives a verdict on. The slug\n"
             "        // keeps both halves' names because it is a published URL.\n"),
    readerProduces=("A sealed integration package mechanically unable to import workspace code, "
                    "and a verdict on the SRS Phase 2 exit criterion with what was measured and "
                    "what was assumed"),
    readerProducesVi=("Một package tích hợp bị niêm phong về mặt cơ chế nên không thể import code "
                      "trong workspace, và một phán quyết cho tiêu chí ra khỏi Phase 2 của SRS kèm "
                      "những gì đã đo và những gì chỉ được giả định"),
    sourceDoc="docs/04-srs.md", readerMinutes=31,
)

def wrap(field, value, indent="        "):
    """Match the file's own habit: a short value inline, a long one on the next line."""
    inline = f'{indent}{field}: "{value}",'
    if len(inline) <= 100:
        return inline + "\n"
    return f'{indent}{field}:\n{indent}  "{value}",\n'

def build(h):
    o = ["      {\n", f'        id: "3.{h["num"]}",\n',
         f'        path: "/part-3/chapter-{h["num"]:02d}/{h["slug"]}",\n',
         wrap("title", h["title"]), '        status: "published",\n', h["comment"],
         wrap("readerProduces", h["readerProduces"]),
         wrap("sourceDoc", h["sourceDoc"]),
         f'        readerMinutes: {h["readerMinutes"]},\n',
         wrap("titleVi", h["titleVi"]),
         wrap("readerProducesVi", h["readerProducesVi"]),
         "      },\n"]
    return "".join(o)

src = REG.read_text(encoding="utf-8")
i3, i4 = src.index("number: 3"), src.index("number: 4")
seg = src[i3:i4]
lines = seg.split("\n")
opens = [k for k, l in enumerate(lines) if l == "      {"]
closes = [k for k, l in enumerate(lines) if l == "      },"]
if len(opens) != 24 or len(closes) != 24:
    sys.exit(f"registry: expected 24 entries, parsed {len(opens)}/{len(closes)}")

blocks = {}
for a, b in zip(opens, closes):
    block = "\n".join(lines[a:b + 1]) + "\n"
    m = re.search(r'id: "3\.(\d+)"', block)
    blocks[int(m.group(1))] = block

out = []
for old in sorted(blocks):
    if old == SPLIT_OLD:
        continue
    new, slug = NEW[old][0]
    b = blocks[old]
    b = re.sub(r'id: "3\.\d+"', f'id: "3.{new}"', b, count=1)
    b = re.sub(r'path: "/part-3/chapter-\d+/[^"]+"',
               f'path: "/part-3/chapter-{new:02d}/{slug}"', b, count=1)
    out.append((new, b))
out.append((HALF_REGISTRY["num"], build(HALF_REGISTRY)))
out.append((HALF_OUTSIDER["num"], build(HALF_OUTSIDER)))
out.sort(key=lambda x: x[0])

nums = [n for n, _ in out]
if nums != list(range(1, 26)):
    sys.exit(f"registry: numbers are not 1..25 — {nums}")

head = "\n".join(lines[:opens[0]]) + "\n"
tail = "\n".join(lines[closes[-1] + 1:])
new_seg = head + "".join(b for _, b in out) + tail
result = src[:i3] + new_seg + src[i4:]

print("registry:", "APPLY" if APPLY else "DRY RUN")
print(f"  entries parsed   24 -> written {len(out)}  (ids {nums[0]}..{nums[-1]})")
print(f"  lines            {len(src.splitlines())} -> {len(result.splitlines())}")
if APPLY:
    REG.write_text(result, encoding="utf-8")
    print("  written")
else:
    print("  --- the two new blocks ---")
    print(build(HALF_REGISTRY) + build(HALF_OUTSIDER))

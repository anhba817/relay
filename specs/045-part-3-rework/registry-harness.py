#!/usr/bin/env python3
"""Shift the registry to 26 and divide the gauntlet's entry.

Current ids run 3.1..3.25. Everything at 4 or above shifts up one, the harness is
inserted at 3.4, and the gauntlet's entry — which lands at 3.25 by that shift — keeps the
verdict half while the harness takes the rest.

VIETNAMESE IS DIVIDED, NOT WRITTEN. `titleVi` for the harness is the existing title with
its "Cột mốc:" prefix dropped, and `readerProducesVi` splits at the clause boundary the
original already had. The English/Vietnamese pair is therefore not a translation of each
other for the harness title, which is recorded rather than papered over: the user supplies
translations and Phase 7 sets the Vietnamese pages to placeholder regardless.
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
REG = HERE.parent.parent / "relay-tutorial" / "lib" / "tutorial.ts"
APPLY = "--apply" in sys.argv

HARNESS = '''      {
        id: "3.4",
        path: "/part-3/chapter-04/the-isolation-harness",
        title: "The isolation harness",
        status: "published",
        // Divided out of the milestone because eight files it creates are edited by
        // 25 later chapter-edits, and the reorder put every one of them before the
        // file existed. The harness has to precede its editors; the verdict does not.
        readerProduces:
          "A cross-tenant suite whose target list derives itself from the running router, four attack shapes over 24 routes, a structural check that every table has a tenant path, and the socket surface attacked from the protocol's own frame union",
        sourceDoc: "docs/04-srs.md, docs/05-sad.md",
        readerMinutes: 67,
        titleVi: "Cửa ải cô lập tenant",
        readerProducesVi:
          "Một bộ kiểm thử cross-tenant tự suy ra danh sách mục tiêu từ router đang chạy, bốn dạng tấn công trên 24 route, một kiểm tra cấu trúc rằng mọi bảng đều có đường về tenant, và tầng socket bị tấn công từ chính frame union của protocol",
      },
'''
VERDICT_PRODUCES = ("Three deliberate reintroductions — one of which stayed green and "
                    "taught the suite's range — and tests for the instruments that had "
                    "never produced output")
VERDICT_PRODUCES_VI = ("Ba lần cố ý tái tạo lỗi — một lần vẫn xanh và dạy ta giới hạn "
                       "của bộ kiểm thử")

src = REG.read_text(encoding="utf-8")
i3, i4 = src.index("number: 3"), src.index("number: 4")
seg = src[i3:i4]
lines = seg.split("\n")
opens = [k for k, l in enumerate(lines) if l == "      {"]
closes = [k for k, l in enumerate(lines) if l == "      },"]
if len(opens) != 25:
    sys.exit(f"registry-harness: expected 25 entries, parsed {len(opens)}")

blocks = {}
for a, b in zip(opens, closes):
    blk = "\n".join(lines[a:b + 1]) + "\n"
    blocks[int(re.search(r'id: "3\.(\d+)"', blk).group(1))] = blk

out = []
for cur in sorted(blocks):
    new = cur + 1 if cur >= 4 else cur
    b = blocks[cur]
    slug = re.search(r'path: "/part-3/chapter-\d+/([^"]+)"', b).group(1)
    b = re.sub(r'id: "3\.\d+"', f'id: "3.{new}"', b, count=1)
    b = re.sub(r'path: "/part-3/chapter-\d+/[^"]+"',
               f'path: "/part-3/chapter-{new:02d}/{slug}"', b, count=1)
    if slug == "milestone-the-isolation-gauntlet":
        b = re.sub(r'(readerProduces:\n          ")[^"]+(")', lambda m: m.group(1) + VERDICT_PRODUCES + m.group(2), b)
        b = re.sub(r'(readerProducesVi:\n          ")[^"]+(")', lambda m: m.group(1) + VERDICT_PRODUCES_VI + m.group(2), b)
        b = re.sub(r'readerMinutes: \d+', "readerMinutes: 13", b)
    out.append((new, b))
out.append((4, HARNESS))
out.sort(key=lambda x: x[0])

nums = [n for n, _ in out]
if nums != list(range(1, 27)):
    sys.exit(f"registry-harness: numbers are not 1..26 — {nums}")

head = "\n".join(lines[:opens[0]]) + "\n"
tail = "\n".join(lines[closes[-1] + 1:])
result = src[:i3] + head + "".join(b for _, b in out) + tail + src[i4:]
print(f"registry-harness: {'APPLY' if APPLY else 'DRY RUN'} — 25 -> {len(out)} entries, ids {nums[0]}..{nums[-1]}")
print(f"  lines {len(src.splitlines())} -> {len(result.splitlines())}")
if APPLY:
    REG.write_text(result, encoding="utf-8")
    print("  written")

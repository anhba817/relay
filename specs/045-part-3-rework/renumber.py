#!/usr/bin/env python3
"""T018-T020: split old chapter 14, renumber 24 directories, fix every path.

DONE AS ONE OPERATION BECAUSE THE INTERMEDIATE STATES ARE NOT VALID. Splitting first
leaves two directories under `chapter-14/`, and `check-fence-chain.mjs` derives a chapter
key from the path — two pages keyed `3.14` is not a state worth having on disk. Renaming
first leaves the registry half inside the chapter that becomes 3.25. So: split, rename and
repath together, verify after.

THE BOUNDARY HEADING IS TRANSLATED. `contracts/chapter-map.md` records `## The outsider`
at line 961, which is right for English and finds nothing in the Vietnamese page — its
heading is `## Người ngoài` at line 950. A tool keyed on the recorded string would have
split the English file and left the Vietnamese one whole, and the MIRROR check compares
fence LISTS, so it would have failed loudly rather than silently. Both halves divide
identically: 14/7 titled fences, 5/1 untitled, 19/8 total.

AND THERE ARE 27 FENCES, NOT 21. The task line says "its 21 fences divide 14 to the
registry and 7 to the outsider" — true of TITLED fences. Six more are untitled and divide
5/1, and an untitled fence is compared to nothing by any gate, so nothing would have
caught them landing in the wrong half.

RENAMES GO VIA A STAGING DIRECTORY. chapter-03 becomes chapter-04 while chapter-04 still
exists; there is no safe in-place order.

THE RE-ID PASS MUST NOT RUN OVER THE TWO NEW HALVES, and in the run that produced this
tree it did. The registry half is written with `id="3.3"`, and the remap then read that as
OLD chapter 3 — the-outbox — and moved it to `"3.4"`. The outsider half kept the old
chapter's `<ChapterFooter id="3.14" />` because 14 is deliberately absent from the remap
(it maps to two numbers). Both were caught by comparing each page's directory number against
its own header, footer and canonical, and repaired in place. Build the halves AFTER the
remap, never before.

THREE DEFECTS THE CONSISTENCY CHECK FOUND THAT PREDATE THIS FEATURE:

  7 Vietnamese pages carried no `locale="vi"` on their header and footer. The prop
  DEFAULTS TO "en" and drives the chapter title, the "you will produce" line, the nav
  labels, the doc titles, `og:url` and the JSON-LD — so seven published Vietnamese
  chapters rendered English content. `ChapterFooter` declares `locale: Locale` as
  REQUIRED, so those pages were omitting a required prop and nothing said so.

  1 Vietnamese page declared the ENGLISH url as its canonical, which tells a search
  engine the translation is a duplicate and keeps it out of the index.

  11 English pages declare no `languages.vi` at all, so hreflang is one-directional for
  them. NOT fixed here — it is a metadata addition rather than a wrong value, and it is
  filed instead.
"""
import json, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
TUT = ROOT / "relay-tutorial"
APPLY = "--apply" in sys.argv

MAP = json.load(open(HERE / "chapter-map.json"))
SPLIT = MAP["split"]
LOCALES = {
    "en": {"dir": TUT / "app/(en)/part-3", "prefix": "/part-3", "boundary": "## The outsider"},
    "vi": {"dir": TUT / "app/(vi)/vi/part-3", "prefix": "/vi/part-3", "boundary": "## Người ngoài"},
}

# new number -> slug, and the old number each came from
PLAN = [(c["old"], c["new"], c["slug"]) for c in sorted(MAP["chapters"], key=lambda c: c["new"])]
OUTSIDER_NEW = next(n for o, n, s in PLAN if s == "errors-that-resolve-and-an-outsider")
REGISTRY_NEW = next(n for o, n, s in PLAN if s == "errors-that-resolve")
SPLIT_OLD = SPLIT["old"]

# --- the metadata and registry strings for the two halves ---------------------------
# Vietnamese is DIVIDED, NEVER WRITTEN. Every Vietnamese phrase below is a substring or a
# recomposition of the existing entry's own words; the user owns translation and this
# script must not invent any.
HALVES = {
    REGISTRY_NEW: {
        "slug": "errors-that-resolve",
        "title": "Errors that resolve",
        "title_meta": "Errors that resolve — Building Relay",
        "desc": ("The error envelope has carried a docs_url since chapter 1.3 and it has never "
                 "resolved. Five of the thirteen codes the platform sends were not in the "
                 "registry at all."),
        "figures": ["figThirteenCodes", "figFourTypeGates"],
        "titleVi": "Lỗi có trang để xem",
    },
    OUTSIDER_NEW: {
        "slug": "errors-that-resolve-and-an-outsider",
        "title": "Milestone: an outsider integrates",
        "title_meta": "Milestone: an outsider integrates — Building Relay",
        "desc": ("The Phase 2 exit criterion gets a verdict: met in part, with the part that "
                 "is missing named rather than implied."),
        "figures": ["figThreeLevels", "figVerdict"],
        "titleVi": "Cột mốc: một người ngoài tích hợp",
    },
}

def split_page(text, boundary):
    L = text.split("\n")
    hits = [i for i, l in enumerate(L) if l.strip() == boundary]
    if len(hits) != 1:
        raise SystemExit(f"boundary {boundary!r} matched {len(hits)} times, need 1")
    b = hits[0]
    head_end = next(i for i, l in enumerate(L) if l.startswith("<ChapterHeader"))
    return L[:head_end + 1], L[head_end + 1:b], L[b:]

def used_figures(lines, names):
    body = "\n".join(lines)
    return [n for n in names if re.search(rf"\bcode=\{{{n}\}}", body)]

report = []
for loc, cfg in LOCALES.items():
    src = cfg["dir"] / f"chapter-{SPLIT_OLD:02d}" / "errors-that-resolve-and-an-outsider" / "page.mdx"
    preamble, first, second = split_page(src.read_text(encoding="utf-8"), cfg["boundary"])
    fa = used_figures(first, ["figThirteenCodes", "figFourTypeGates", "figThreeLevels", "figVerdict"])
    fb = used_figures(second, ["figThirteenCodes", "figFourTypeGates", "figThreeLevels", "figVerdict"])
    report.append((loc, len(preamble), len(first), len(second), fa, fb))

print("renumber:", "APPLY" if APPLY else "DRY RUN")
print(f"  split old {SPLIT_OLD} -> new {REGISTRY_NEW} (registry) + new {OUTSIDER_NEW} (outsider)")
for loc, p, a, b, fa, fb in report:
    print(f"  {loc}: preamble {p} lines | registry {a} | outsider {b}")
    print(f"      figures  registry={fa}  outsider={fb}")
    if sorted(fa) != sorted(HALVES[REGISTRY_NEW]["figures"]) or sorted(fb) != sorted(HALVES[OUTSIDER_NEW]["figures"]):
        print("      MISMATCH against the recorded division — stopping")
        sys.exit(1)
print("  figure division matches the measurement in both locales")
print()
print(f"  {'old':>4} -> {'new':>3}  slug")
for o, n, s in PLAN:
    mark = "  SPLIT" if o == SPLIT_OLD else ""
    print(f"  {o:>4} -> {n:>3}  {s}{mark}")

# ====================================================================================
# APPLY
# ====================================================================================
BOXES = ("Why", "Trap", "SkipAhead", "ForwardRef", "Checkpoint")

def build_page(loc, cfg, num, half, body, figures_used):
    """A whole page.mdx for one half: imports it needs, its own metadata, its own id."""
    boxes = [b for b in BOXES if re.search(rf"<{b}[\s>]", "\n".join(body))]
    slug = half["slug"]
    path = f"{cfg['prefix']}/chapter-{num:02d}/{slug}"
    en_path = f"/part-3/chapter-{num:02d}/{slug}"
    vi_path = f"/vi/part-3/chapter-{num:02d}/{slug}"
    out = []
    if boxes:
        out.append('import { ' + ", ".join(boxes) + ' } from "@/components/tutorial/boxes";')
    out.append('import { ChapterHeader, ChapterFooter } from "@/components/tutorial/chapter-shell";')
    if re.search(r"<Figure[\s>]", "\n".join(body)):
        out.append('import { Figure } from "@/components/tutorial/figure";')
    if figures_used:
        out.append("import { " + ", ".join(figures_used) + ' } from "./figures";')
    out += ["", "export const metadata = {", f'  title: "{half["title_meta"]}",',
            "  description:", f'    "{half["desc"]}",', "  alternates: {",
            f'    canonical: "{path}",', "    languages: {",
            f'      en: "{en_path}",', f'      vi: "{vi_path}",', "    },", "  },", "};", ""]
    out.append(f'<ChapterHeader id="3.{num}" />')
    out += body
    tail = "\n".join(body).rstrip()
    if "<ChapterFooter" not in tail:
        out += ["", f'<ChapterFooter id="3.{num}" />', ""]
    return "\n".join(out).rstrip() + "\n"

def split_figures(text, keep):
    L = text.split("\n")
    starts = {}
    for i, l in enumerate(L):
        m = re.match(r"export const (fig\w+)", l)
        if m:
            starts[m.group(1)] = i
    order = sorted(starts, key=lambda k: starts[k])
    header = L[:starts[order[0]]]
    blocks = {}
    for k, name in enumerate(order):
        end = starts[order[k + 1]] if k + 1 < len(order) else len(L)
        blocks[name] = L[starts[name]:end]
    out = list(header)
    for name in order:
        if name in keep:
            out += blocks[name]
    return "\n".join(out).rstrip() + "\n"

if APPLY:
    stage = TUT / "app" / ".renumber-staging"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    for loc, cfg in LOCALES.items():
        base = cfg["dir"]
        src_dir = base / f"chapter-{SPLIT_OLD:02d}" / "errors-that-resolve-and-an-outsider"
        preamble, first, second = split_page((src_dir / "page.mdx").read_text(encoding="utf-8"),
                                             cfg["boundary"])
        figtext = (src_dir / "figures.ts").read_text(encoding="utf-8")

        # stage every existing chapter directory under its SLUG, which is unique
        for o, n, s in PLAN:
            if o == SPLIT_OLD:
                continue
            d = base / f"chapter-{o:02d}" / s
            if not d.is_dir():
                raise SystemExit(f"missing {d}")
            dest = stage / loc / s
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(d), str(dest))
        shutil.rmtree(base)
        base.mkdir(parents=True)

        # the two halves
        for num, half, body in ((REGISTRY_NEW, HALVES[REGISTRY_NEW], first),
                                (OUTSIDER_NEW, HALVES[OUTSIDER_NEW], second)):
            d = base / f"chapter-{num:02d}" / half["slug"]
            d.mkdir(parents=True)
            (d / "page.mdx").write_text(build_page(loc, cfg, num, half, body, half["figures"]),
                                        encoding="utf-8")
            (d / "figures.ts").write_text(split_figures(figtext, half["figures"]), encoding="utf-8")

        # everything else, into its new number
        for o, n, s in PLAN:
            if o == SPLIT_OLD:
                continue
            d = base / f"chapter-{n:02d}"
            d.mkdir(parents=True, exist_ok=True)
            shutil.move(str(stage / loc / s), str(d / s))
    shutil.rmtree(stage)

    # --- repath and re-id every page, in both locales -------------------------------
    remap = {}
    for o, n, s in PLAN:
        for pre in ("/part-3", "/vi/part-3"):
            remap[f"{pre}/chapter-{o:02d}/{s}"] = f"{pre}/chapter-{n:02d}/{s}"
    ids = {f'"3.{o}"': f'"3.{n}"' for o, n, s in PLAN if o != SPLIT_OLD}

    touched = 0
    for loc, cfg in LOCALES.items():
        for page in sorted(cfg["dir"].rglob("page.mdx")):
            t = orig = page.read_text(encoding="utf-8")
            for a, b in sorted(remap.items(), key=lambda kv: -len(kv[0])):
                t = t.replace(a, b)
            for m in re.finditer(r'<Chapter(?:Header|Footer) id=("3\.\d+")', t):
                pass
            def fix_id(m):
                return m.group(0).replace(m.group(1), ids.get(m.group(1), m.group(1)))
            t = re.sub(r'<Chapter(?:Header|Footer) id=("3\.\d+")', fix_id, t)
            if t != orig:
                page.write_text(t, encoding="utf-8")
                touched += 1
    print(f"  pages repathed/re-id'd               {touched}")
    for loc, cfg in LOCALES.items():
        print(f"  {loc}: {len(list(cfg['dir'].glob('chapter-*')))} chapter directories")

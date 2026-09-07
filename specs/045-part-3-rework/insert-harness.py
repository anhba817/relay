#!/usr/bin/env python3
"""Divide the gauntlet: the harness to new 4, the verdict to new 25. Part 3 -> 26.

WHY THIS SPLIT EXISTS AT ALL — it was not planned. The gauntlet creates eight files and
25 chapter-edits land on them. Moving it to the end of movement VIII put every one of
those edits before the file existed, and the three-way merge returned `ours` = 0 lines on
all eight. A merge cannot resolve that: taking `theirs` relocates the conflict to the
creator's own add/add, and re-sorting the old states makes the file shrink at the last
chapter because the chain's end is pinned to the platform file. The harness has to
precede its editors.

THE HALVES FENCE DISJOINT PATHS. Early builds the gauntlet and its production code (15
titled fences, all eight of the conflicting files); late adds unit tests OF the
instruments (5). `catalogue.ts` early, `catalogue.test.ts` late. Nothing appears in both,
which is what makes the division mechanical rather than editorial.

THE HALVES ARE WRITTEN LAST. In the T018-T020 run they were written before the re-id
pass, which then read the registry half's fresh `id="3.3"` as OLD chapter 3 and moved it
to `"3.4"`. Order matters more than the remap's contents.
"""
import json, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).parent
TUT = HERE.parent.parent / "relay-tutorial"
MAP = json.load(open(HERE / "chapter-map.json"))
APPLY = "--apply" in sys.argv

GSPLIT = next(sp for sp in MAP["splits"] if sp["old"] == 12)
LOCALES = {
    "en": {"dir": TUT / "app/(en)/part-3", "prefix": "/part-3",
           "boundary": GSPLIT["boundary"]["en"], "loc_attr": ""},
    "vi": {"dir": TUT / "app/(vi)/vi/part-3", "prefix": "/vi/part-3",
           "boundary": GSPLIT["boundary"]["vi"], "loc_attr": ' locale="vi"'},
}
HARNESS, VERDICT = GSPLIT["halves"][0], GSPLIT["halves"][1]

META = {
    HARNESS["new"]: dict(
        slug="the-isolation-harness",
        title_meta="The isolation harness — Building Relay",
        desc=("The constitution has required a cross-tenant suite since it was written. This "
              "builds the one that derives its own target list from the running router, so a "
              "route that exists and is unattacked fails the suite."),
        figures=["figDerivedTargets", "figWhoMayCall"]),
    VERDICT["new"]: dict(
        slug="milestone-the-isolation-gauntlet",
        title_meta="Milestone: the isolation gauntlet — Building Relay",
        desc=("Has it ever caught anything? The gauntlet gets a verdict, the instruments that "
              "had never produced output get tests of their own, and what the suite does not "
              "cover is written down rather than implied."),
        figures=["figWhatMaskedWhat"]),
}
BOXES = ("Why", "Trap", "SkipAhead", "ForwardRef", "Checkpoint")

def split_page(text, boundary):
    L = text.split("\n")
    hits = [i for i, l in enumerate(L) if l.strip() == boundary]
    if len(hits) != 1:
        raise SystemExit(f"boundary {boundary!r} matched {len(hits)} times, need 1")
    hdr = next(i for i, l in enumerate(L) if l.startswith("<ChapterHeader"))
    return L[:hdr + 1], L[hdr + 1:hits[0]], L[hits[0]:]

def build_page(cfg, num, meta, body):
    body_s = "\n".join(body)
    boxes = [b for b in BOXES if re.search("<" + b + r"(?=[\s>/])", body_s)]
    figs = [g for g in meta["figures"] if "{" + g + "}" in body_s]
    slug = meta["slug"]
    out = []
    if boxes:
        out.append("import { " + ", ".join(boxes) + ' } from "@/components/tutorial/boxes";')
    out.append('import { ChapterHeader, ChapterFooter } from "@/components/tutorial/chapter-shell";')
    if re.search(r"<Figure(?=[\s>/])", body_s):
        out.append('import { Figure } from "@/components/tutorial/figure";')
    if figs:
        out.append("import { " + ", ".join(figs) + ' } from "./figures";')
    out += ["", "export const metadata = {", f'  title: "{meta["title_meta"]}",',
            "  description:", f'    "{meta["desc"]}",', "  alternates: {",
            f'    canonical: "{cfg["prefix"]}/chapter-{num:02d}/{slug}",', "    languages: {",
            f'      en: "/part-3/chapter-{num:02d}/{slug}",',
            f'      vi: "/vi/part-3/chapter-{num:02d}/{slug}",', "    },", "  },", "};", ""]
    out.append(f'<ChapterHeader id="3.{num}"{cfg["loc_attr"]} />')
    out += body
    if "<ChapterFooter" not in body_s:
        out += ["", f'<ChapterFooter id="3.{num}"{cfg["loc_attr"]} />', ""]
    else:
        out = [re.sub(r'(<ChapterFooter id=")3\.\d+(")', rf'\g<1>3.{num}\g<2>', l) for l in out]
    return "\n".join(out).rstrip() + "\n"

def split_figures(text, keep):
    L = text.split("\n")
    starts = {m.group(1): i for i, l in enumerate(L)
              if (m := re.match(r"export const (fig\w+)", l))}
    order = sorted(starts, key=lambda k: starts[k])
    out = list(L[:starts[order[0]]])
    for k, name in enumerate(order):
        end = starts[order[k + 1]] if k + 1 < len(order) else len(L)
        if name in keep:
            out += L[starts[name]:end]
    return "\n".join(out).rstrip() + "\n"

# current on-disk number -> final number, for the 24 that merely shift
FINAL = {c["slug"]: c["new"] for c in MAP["chapters"]}
GAUNTLET_SLUG = "milestone-the-isolation-gauntlet"

print("insert-harness:", "APPLY" if APPLY else "DRY RUN")
for loc, cfg in LOCALES.items():
    src = cfg["dir"] / "chapter-24" / GAUNTLET_SLUG / "page.mdx"
    pre, early, late = split_page(src.read_text(encoding="utf-8"), cfg["boundary"])
    print(f"  {loc}: preamble {len(pre)} | harness {len(early)} | verdict {len(late)}")

if APPLY:
    stage = TUT / "app" / ".insert-staging"
    if stage.exists():
        shutil.rmtree(stage)
    for loc, cfg in LOCALES.items():
        base = cfg["dir"]
        src = base / "chapter-24" / GAUNTLET_SLUG
        pre, early, late = split_page((src / "page.mdx").read_text(encoding="utf-8"), cfg["boundary"])
        figtext = (src / "figures.ts").read_text(encoding="utf-8")

        moved = []
        for d in sorted(base.glob("chapter-*/*")):
            if not d.is_dir():
                continue
            if d.name == GAUNTLET_SLUG:
                continue                      # consumed by the split
            dest = stage / loc / d.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(d), str(dest))
            moved.append(d.name)
        shutil.rmtree(base); base.mkdir(parents=True)
        for slug in moved:
            n = FINAL[slug]
            (base / f"chapter-{n:02d}").mkdir(parents=True, exist_ok=True)
            shutil.move(str(stage / loc / slug), str(base / f"chapter-{n:02d}" / slug))

        # repath and re-id the movers BEFORE the halves are written
        # ONE PASS, NOT A DICT OF LITERAL REPLACEMENTS.
        #
        # A SLUG CAN BE A PREFIX OF ANOTHER SLUG: `errors-that-resolve` is a prefix of
        # `errors-that-resolve-and-an-outsider`. Replacing longest-key-first is not enough
        # when the keys are generated for every current number, because the REPLACEMENT
        # then matches a later, shorter key — `/chapter-25/errors-that-resolve-and-an-
        # outsider` became `/chapter-26/...`, and then `/chapter-26/errors-that-resolve`
        # matched that prefix and rewrote it to `/chapter-03/errors-that-resolve-and-an-
        # outsider`. The remap's own output was feeding the next key.
        #
        # A single regex pass with the slug captured cannot do that: each match is
        # consumed once and the substitution is never re-examined. Longest slug first so
        # the alternation prefers the more specific name.
        final = {c["slug"]: c["new"] for c in MAP["chapters"]}
        slugs = sorted(final, key=len, reverse=True)
        PATH_RE = re.compile(r"(/(?:vi/)?part-3)/chapter-\d{2}/(" +
                             "|".join(re.escape(x) for x in slugs) + r")\b")
        for page in sorted(base.rglob("page.mdx")):
            num = int(re.search(r"chapter-(\d{2})", str(page)).group(1))
            t = orig = page.read_text(encoding="utf-8")
            t = PATH_RE.sub(lambda m: f"{m.group(1)}/chapter-{final[m.group(2)]:02d}/{m.group(2)}", t)
            t = re.sub(r'(<Chapter(?:Header|Footer) id=")3\.\d+(")', rf'\g<1>3.{num}\g<2>', t)
            if t != orig:
                page.write_text(t, encoding="utf-8")

        # the two halves last
        for num, body in ((HARNESS["new"], early), (VERDICT["new"], late)):
            meta = META[num]
            d = base / f"chapter-{num:02d}" / meta["slug"]
            d.mkdir(parents=True, exist_ok=True)
            (d / "page.mdx").write_text(build_page(cfg, num, meta, body), encoding="utf-8")
            (d / "figures.ts").write_text(split_figures(figtext, meta["figures"]), encoding="utf-8")
    shutil.rmtree(stage)
    for loc, cfg in LOCALES.items():
        print(f"  {loc}: {len(list(cfg['dir'].glob('chapter-*')))} chapter directories")

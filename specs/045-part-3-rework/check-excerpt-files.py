#!/usr/bin/env python3
"""The excerpt-only files, which `check:fences` compares to nothing.

`check-fence-chain.mjs` collects a fence only when its title has no `(excerpt)` marker,
so an excerpt fence is published, typed in by readers, and verified by no gate. THIRTEEN
files are published ONLY that way — ten of them `relay-platform` source — and this
feature rewrote comments inside them. A comment rewritten one way in the fence and
another way in the source would be invisible: `check:fences` skips the fence, and
`classify-refs` reads the source and never opens the chapter.

TWO QUESTIONS, AND THE SECOND IS THE ONE NOBODY ASKS:

  1. Do the ten platform files still name an ordinal? They were inside `classify-refs`'s
     corpus all along, so this is a re-measurement rather than a discovery — but T016
     exists because a green `check:fences` says nothing about them either way.

  2. Does every line THIS FEATURE REWROTE inside an excerpt still agree with the source?

     A FIRST VERSION COMPARED THE WHOLE BODY AND REPORTED 38 OF 99 FENCES AS DRIFTED,
     nearly all of them legitimately. An excerpt is a teaching device: it elides with
     `{ … }`, it annotates (`path: req.originalUrl,   // was: req.url`), it simplifies a
     signature, and above all IT OFTEN SHOWS THE FILE AS IT STOOD AT THAT CHAPTER rather
     than as it stands now. Comparing a chapter-5 excerpt against HEAD is the same
     mistake as pointing the chain's replay at the platform file for the 49 paths the
     appendix amends — the target is wrong, so the failure is reported in the wrong place.

     What is answerable is the narrow question: a line carrying a chapter SUBJECT NAME is
     a line this feature wrote, and it must say the same thing in the fence and in the
     file. If the fence reads `the user-surface chapter` where the source reads `the
     isolation gauntlet`, that is drift this feature caused and no gate can see.

RED-TESTED THREE WAYS, AND THE FIRST PROBE WAS INVALID. Perturbing a subject name in an
excerpt left the checker green, which looked like a blind spot and was a badly chosen
probe: the line picked was one of the four with NO counterpart in HEAD, so changing its
subject moves it from one absent bucket to another and can never demonstrate drift. Only
7 of the 11 subject-naming lines have a counterpart, and perturbing one of those goes red
and prints both sides. **A probe has to be able to fail for the reason being tested**, and
"the checker missed it" and "the probe could not show it" look identical from the outside.

  1. an excerpt naming a different subject than its source   RED
  2. an ordinal returned to an excerpt-only platform file      RED
  3. title normalisation stops stripping " before ..."         RED (a control catches it)

THE TITLE IS PARSED BEFORE ANYTHING IS COUNTED. `packages/protocol/src/frames.ts,
chapter 1.3 (excerpt)` and `services/gateway/src/session.ts before this chapter
(excerpt)` both name files that ARE chained elsewhere; counting them makes fifteen. Of
68 distinct excerpt titles, 13 are prose that names no file at all — `the naive version`,
`the grep that changed the chapter`. This count has been wrong four times out of five in
this project and every error was in the title.
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import refrules
from refrules import REF, is_versionish, is_deliberate, controls_failing

ROOT = HERE.parent.parent
TUT, PLAT = ROOT / "relay-tutorial", ROOT / "relay-platform"
TITLE = re.compile(r'^```(\w+) title="([^"]+)"')

def norm(t):
    t = t.replace(" (excerpt)", "").replace(" (deleted)", "")
    t = re.split(r" before | after ", t)[0]
    return t.split(",")[0].strip()

def resolve(p):
    for root in (PLAT, ROOT):
        if p and (root / p).is_file():
            return root / p
    return None

# --- controls: the three title shapes that have produced a wrong count ---------------
CTL = [("services/gateway/src/session.ts before this chapter (excerpt)", "services/gateway/src/session.ts"),
       ("packages/protocol/src/frames.ts, chapter 1.3 (excerpt)", "packages/protocol/src/frames.ts"),
       ("services/gateway/src/session.itest.ts (excerpt)", "services/gateway/src/session.itest.ts"),
       ("the naive version (excerpt)", "the naive version")]
bad = [t for t, want in CTL if norm(t) != want]
if bad or controls_failing():
    print("check-excerpt-files: BROKEN — " + ", ".join(bad + controls_failing()))
    sys.exit(2)
print(f"check-excerpt-files: {len(CTL)} title controls + refrules controls fired")

# --- collect ------------------------------------------------------------------------
pages = sorted(TUT.glob("app/(en)/**/page.mdx")) + [TUT / "fences/post-series.md"]
fences, chained = [], set()
for f in pages:
    L = f.read_text(encoding="utf-8").split("\n")
    i = 0
    while i < len(L):
        m = TITLE.match(L[i])
        if not m:
            i += 1; continue
        end = next((j for j in range(i + 1, len(L)) if L[j].startswith("```")), len(L))
        p = norm(m.group(2))
        if "(excerpt)" in m.group(2):
            fences.append({"file": f, "line": i + 1, "lang": m.group(1),
                           "title": m.group(2), "path": p, "body": L[i + 1:end]})
        else:
            chained.add(p)
        i = end + 1

only = sorted({x["path"] for x in fences if resolve(x["path"]) and x["path"] not in chained})
plat_only = [p for p in only if str(resolve(p)).startswith(str(PLAT))]
print(f"  excerpt fences                       {len(fences)}")
print(f"  excerpt-only files                   {len(only)}  ({len(plat_only)} of them platform source)")

# --- question 1: ordinals in the excerpt-only platform files ------------------------
ords, kept = [], 0
for p in plat_only:
    for n, l in enumerate(resolve(p).read_text(encoding="utf-8").splitlines(), 1):
        if is_deliberate(l):
            kept += 1; continue
        for mm in REF.finditer(l):
            if not is_versionish(l, mm):
                ords.append((p, n, mm.group(0), l.strip()[:80]))
print(f"  ordinals in those platform files     {len(ords)}"
      + (f"   (+{kept} kept on purpose)" if kept else ""))
for p, n, r, t in ords[:20]:
    print(f"    {p}:{n}  {r}  {t}")

# --- question 2: do the lines THIS FEATURE wrote agree with the source? -------------
import json
NAMES = [c["name"] for c in json.load(open(HERE / "subjects.json"))["chapters"]]
NAMED = re.compile("|".join(re.escape(n) for n in NAMES), re.I)
if not NAMED.search("as the user-surface chapter measured"):
    print("check-excerpt-files: BROKEN — the subject-name pattern misses its own example")
    sys.exit(2)

drift, absent, checked, informational = [], [], 0, 0
for x in fences:
    tgt = resolve(x["path"])
    if not tgt:
        continue
    have = {l.strip() for l in tgt.read_text(encoding="utf-8").splitlines()}
    body = x["body"]
    if x["lang"] == "diff":
        body = [l[1:] if l[:1] in "-+ " else l for l in body if not l.startswith("-")]
    for l in body:
        t = l.strip()
        if not t or not (NAMED.search(t) or REF.search(t)):
            continue
        checked += 1
        if t in have:
            continue
        # NO COUNTERPART IS NOT DISAGREEMENT. An excerpt of an earlier state has no line
        # in HEAD to match, and all four of the first run's "failures" were that: the
        # sentence had moved or gone. What WOULD be a defect is the same sentence present
        # with a DIFFERENT subject in it — the fence saying `the user-surface chapter`
        # where the source says `the isolation gauntlet`. Found by blanking the subject
        # name out of both sides and matching the remainder.
        skel = NAMED.sub("\u0000", t)
        rival = next((h for h in have if h != t and NAMED.sub("\u0000", h) == skel), None)
        (drift if rival else absent).append((x, t, rival))
    informational += sum(1 for l in body if l.strip() and l.strip() not in have)

print(f"  excerpt fences compared              {sum(1 for x in fences if resolve(x['path']))}")
print(f"  lines naming a chapter subject       {checked}")
print(f"  ... naming a DIFFERENT subject       {len(drift)}   <- the defect this asks about")
print(f"  ... with no counterpart in HEAD      {len(absent)}   (an excerpt of an earlier state)")
print(f"  (any-line differences, informational {informational} — an excerpt may show an")
print(f"   earlier state of the file, so this number is not a failure)")
for x, t, rival in drift[:14]:
    print(f"    DRIFT {x['file'].name}:{x['line']}  {x['path']}")
    print(f"        fence:  {t[:100]}")
    print(f"        source: {rival[:100]}")
for x, t, _ in absent[:6]:
    print(f"    (no counterpart) {x['path']}\n        {t[:100]}")

print("check-excerpt-files: bytes only — it cannot say whether the excerpt is the RIGHT slice")
sys.exit(1 if ords or drift else 0)

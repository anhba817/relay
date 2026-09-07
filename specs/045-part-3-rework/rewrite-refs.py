#!/usr/bin/env python3
"""Apply one of the three rewrites to Part-3 chapter references in platform source.

  --rule delete       remove the provenance tag; the sentence stands without it
  --rule substitute   replace the ordinal with its subject's name from subjects.json
  --rule read         list them; this rule is a person's, not a script's

  --scope PREFIX      limit to paths starting with PREFIX (the batches)
  --apply             write. Without it, a dry run reporting counts and a sample.

THE SPLIT CHAPTER IS NEVER SUBSTITUTED AUTOMATICALLY. Old 3.14 becomes two chapters at
opposite ends of Part 3 — the error registry and the outsider milestone — so a reference
to it names one of two things and only the sentence knows which. Reading the twenty in
the tree: most are the registry, one is the outsider's exit criterion. They route to
`read`, because a comment pointing at the wrong half is worse than an ordinal.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
PLAT = HERE.parent.parent / "relay-platform"
sys.path.insert(0, str(HERE))

from refrules import REF, SPLIT, chapter_of, classify, controls_failing, is_versionish

NAMES = {c["was"]: c["name"] for c in json.loads((HERE / "subjects.json").read_text())["chapters"]}

def chapter_of(ref: str) -> int:
    return int(re.search(r"3\.(\d{1,2})", ref).group(1))

def delete_one(line: str, m: re.Match) -> str:
    """Remove the tag and leave a sentence. Four shapes, each tried in order."""
    ref = m.group(0)
    # ONLY A SENTENCE-INITIAL TAG MAY RE-CAPITALISE, and the first version capitalised
    # anything. `// then its allowance. The limiter is LAST and that is forced (chapter
    # 3.8):` became `// Then its allowance…` — a CONTINUATION line, mid-sentence, given a
    # capital because the deletion happened to be on it. Caught in the dry run before any
    # of the 821 was written.
    tag = bool(re.match(r"^\s*[/*\s]*" + re.escape(ref) + r"\s*[.:]", line))
    # A `(3.N)` match carries its own parentheses; removing it plus the space before is
    # the whole edit. Handled first, because the generic paren shape below would look for
    # `((3.N))` and find nothing — 98 references were left untouched that way.
    if ref.startswith("("):
        return re.sub(rf"\s*{re.escape(ref)}", "", line, count=1)
    for pat, rep in (
        (rf"\s*\(\s*{re.escape(ref)}\s*\)", ""),          # " (chapter 3.2)" -> ""
        (rf"{re.escape(ref)},\s*", ""),                    # "(chapter 3.21, FR-…)" -> "(FR-…)"
        (rf",\s*{re.escape(ref)}", ""),                    # "(FR-…, chapter 3.21)" -> "(FR-…)"
        (rf"{re.escape(ref)}\s*[:.]\s*", ""),              # "// Chapter 3.8: nor…" -> "// nor…"
        # NO LAST-RESORT STRIP. It used to be `(rf"\s*{re.escape(ref)}", "")`, which
        # removed the reference from anywhere and left the sentence to fend for itself:
        # 16 dangling prepositions and 36 orphaned possessives reached the tree before a
        # damage scan of the diff caught them. A reference whose shape matches none of the
        # four above is not a tag, and `delete_one` now returns the line untouched — which
        # `rewrite-refs` reports as UNCHANGED rather than writing.
    ):
        new = re.sub(pat, rep, line, count=1)
        if new != line:
            if tag:
                return re.sub(r"^(\s*(?://|/\*\*?|\*)\s*)([a-z])",
                              lambda g: g.group(1) + g.group(2).upper(), new, count=1)
            return new
    return line

def substitute_one(line: str, m: re.Match) -> str:
    name = NAMES.get(f"3.{chapter_of(m.group(0))}")
    if not name:
        return line
    ref = m.group(0)
    if ref.endswith("'s"):
        new = name + "'s"
    elif line[m.end():m.end() + 2] == "'s":
        new = name
    else:
        new = name
    # CAPITALISE ON SENTENCE POSITION, NOT ON THE REFERENCE'S OWN CASE.
    #
    # This read `if ref[0].isupper()`, and in a codebase that writes ALL-CAPS for
    # emphasis that is the wrong signal. `**THIS LINE IS THE ONE CHAPTER 3.21 FORGOT.**`
    # became `**THIS LINE IS THE ONE The typing chapter FORGOT.**`, and
    # `and CHAPTER 3.11 STRENGTHENED THAT` became `and The connection-metering chapter
    # STRENGTHENED THAT`. An upper-case reference mid-sentence is emphasis; only its
    # position can say whether a capital belongs.
    before = line[:m.start()].rstrip()
    opener = re.match(r"^\s*(?://+|/\*\*?|\*)\s*\**$", before)
    sentence_start = not before or bool(opener) or bool(re.search(r"[.!?]\s*\**$", before))
    if sentence_start:
        new = new[0].upper() + new[1:]
    return line[:m.start()] + new + line[m.end():]

def main() -> int:
    broken = controls_failing()
    if broken:
        for b in broken:
            print(f"  BROKEN PATTERN — {b}", file=sys.stderr)
        return 1
    rule = sys.argv[sys.argv.index("--rule") + 1]
    scope = sys.argv[sys.argv.index("--scope") + 1] if "--scope" in sys.argv else ""
    apply = "--apply" in sys.argv
    found = rewritten = 0
    samples, touched = [], set()
    for d in ("services", "packages"):
        for f in sorted((PLAT / d).rglob("*.ts")):
            if "node_modules" in str(f):
                continue
            rel = str(f.relative_to(PLAT))
            if scope and not rel.startswith(scope):
                continue
            lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
            changed = False
            for i, line in enumerate(lines):
                # Re-scan after each edit: an edit shifts every later offset on the line.
                while True:
                    m = next((x for x in REF.finditer(lines[i])
                              if not is_versionish(lines[i], x)
                              and classify(lines[i], x) == rule), None)
                    if not m:
                        break
                    found += 1
                    if rule == "read":
                        # EVERY match on the line, not the first. Stopping at one
                        # undercounted lines carrying two references — 295 against the
                        # classifier's 317, and the two must agree or neither is a count.
                        for x in REF.finditer(lines[i]):
                            if not is_versionish(lines[i], x) and classify(lines[i], x) == "read":
                                found += 1
                                samples.append(f"{rel}:{i+1}  {lines[i].strip()[:96]}")
                        found -= 1
                        break
                    new = delete_one(lines[i], m) if rule == "delete" else substitute_one(lines[i], m)
                    if new == lines[i]:
                        samples.append(f"UNCHANGED {rel}:{i+1}  {lines[i].strip()[:80]}")
                        break
                    if len(samples) < 8:
                        samples.append(f"{rel}:{i+1}\n    - {line.rstrip()[:100]}\n    + {new.rstrip()[:100]}")
                    lines[i] = new
                    rewritten += 1
                    changed = True
            if changed and apply:
                f.write_text("".join(lines), encoding="utf-8")
                touched.add(rel)
    print(f"rewrite-refs: rule={rule} scope={scope or 'all'} apply={apply}")
    print(f"  found {found}   rewritten {rewritten}   files touched {len(touched)}")
    for s in samples[:8]:
        print(f"  {s}")
    return 0

if __name__ == "__main__":
    sys.exit(main())

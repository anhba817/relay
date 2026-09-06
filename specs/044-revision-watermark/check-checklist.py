#!/usr/bin/env python3
"""Hold `checklists/requirements.md` to the spec it certifies.

`/speckit-implement` reads this checklist's boxes and halts if any is open, so the file is
an approval gate. It was written once, at 24 requirements, and thirteen analysis passes
edited the spec without anyone re-reading it. By pass 14 its most specific claim — an
enumeration of the implementation details the spec names on purpose — was wrong by five,
and had been wrong by one on the day it was written.

Correcting the enumeration fixes the instance. This checks the class:

  1. Every code- or path-shaped reference in spec.md appears in the checklist. The
     checklist's argument is that each such reference is deliberate; a reference it does
     not mention is one nothing argued for.
  2. The checklist's stated requirement and criterion counts match spec.md. A gate that
     certifies a spec of a different size is certifying something else.
  3. No box is left open, because the gate reads them and a half-filled checklist stops
     implementation with no explanation of what is missing.

It cannot tell whether a ticked box is TRUE. Items like "written for non-technical
stakeholders" are judgements, and the checklist argues two of them in prose on purpose.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE_SHAPED = re.compile(r"\.(?:ts|md|sql|py|mjs)\b|/|^[a-z_]+\.[a-z_]+$")


def main() -> int:
    spec_p = HERE / "spec.md"
    cl_p = HERE / "checklists" / "requirements.md"
    for p in (spec_p, cl_p):
        if not p.exists():
            print(f"check-checklist: {p.name} is missing")
            return 1

    spec, cl = spec_p.read_text(), cl_p.read_text()
    problems: list[str] = []

    # 1 — every deliberate implementation reference is accounted for
    refs = {m.group(1) for m in re.finditer(r"`([^`]+)`", spec)
            if CODE_SHAPED.search(m.group(1))}
    for ref in sorted(refs):
        if ref not in cl:
            problems.append(
                f"spec.md names `{ref}` and the checklist does not mention it — add it to "
                f"the enumeration with the class it belongs to, or take it out of the spec"
            )

    # 2 — the counts the checklist certifies
    frs = len(re.findall(r"^- \*\*FR-[0-9]+[a-z]?\*\*", spec, re.M))
    scs = len(re.findall(r"^- \*\*SC-[0-9]+[a-z]?\*\*", spec, re.M))
    if not frs or not scs:
        problems.append("spec.md declares no FR- or no SC- ids — is the class name still right?")
    for n, noun in ((frs, "requirements"), (scs, "success criteria")):
        if not re.search(rf"\b{n}\s+{re.escape(noun)}\b", cl):
            problems.append(
                f"the checklist does not say it was validated against {n} {noun} — "
                f"re-read it and record the count it certifies"
            )

    # 3 — the gate itself
    open_boxes = len(re.findall(r"^- \[ \]", cl, re.M))
    if open_boxes:
        problems.append(
            f"{open_boxes} checklist item(s) still open — /speckit-implement halts on this"
        )

    if problems:
        print(f"check-checklist: {len(problems)} problem(s)")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"check-checklist: {len(refs)} implementation reference(s) all enumerated, "
          f"validated against {frs} requirements and {scs} success criteria, no open boxes")
    print("check-checklist: presence only — it cannot tell whether a ticked box is true")
    return 0


if __name__ == "__main__":
    sys.exit(main())

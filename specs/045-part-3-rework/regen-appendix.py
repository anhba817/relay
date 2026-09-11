#!/usr/bin/env python3
"""Regenerate `fences/post-series.md` against the rebuilt chain.

WHAT AN APPENDIX AMENDMENT IS FOR. `check-fence-chain` replays every chapter's fences,
then applies the appendix, and the end state must equal the repository. So an appendix
hunk's job is exactly: take the REPLAYED state to the tree. Its pre-image is therefore
the replayed state and not the chapter's tag — the opposite of `regen-fences.py`, and the
reason this is a separate instrument rather than a flag on that one.

AND THAT IS WHY 045-71 DOES NOT APPLY HERE. Generating a CHAPTER's fence from the replayed
state falsifies it for a reader, because a chapter's diff must apply to the chapter's real
starting point. An appendix amendment has no reader typing along at a checkpoint: it is
defined as the difference the chapters do not teach. Generating it from the replay is its
definition, not a shortcut past a blind spot.

WHAT IT REFUSES TO DO. It only touches paths the appendix ALREADY amends. Sweeping every
divergent file into the appendix would make the chain green by attributing chapter content
— content that reached a file through an untitled fence the chain cannot see — to "work
that publishes no chapter". That is 043-1 wearing a disguise, and the honest place for it
is a red HEAD count with the entry's number beside it.

Usage: regen-appendix.py <endstate-dir> [--apply]
"""
import pathlib, re, subprocess, sys, tempfile

WT = pathlib.Path("/home/dong/work/relay/tmp/part3-refactor")
POST = pathlib.Path("/home/dong/work/relay/relay-tutorial/fences/post-series.md")


def tip(path: str) -> str | None:
    r = subprocess.run(["git", "-C", str(WT), "show", f"part3-published:{path}"],
                       capture_output=True, text=True)
    return None if r.returncode else r.stdout


def unified(before: str, after: str, width: int) -> str:
    with tempfile.TemporaryDirectory() as d:
        a, b = pathlib.Path(d) / "a", pathlib.Path(d) / "b"
        a.write_text(before, encoding="utf-8")
        b.write_text(after, encoding="utf-8")
        out = subprocess.run(["git", "diff", "--no-index", f"-U{width}", "--no-color",
                              str(a), str(b)], capture_output=True, text=True).stdout
    lines = out.split("\n")
    i = next((k for k, l in enumerate(lines) if l.startswith("@@")), len(lines))
    return "\n".join(lines[i:]).rstrip()


def unique(diff: str, before: str) -> bool:
    for block in diff.split("\n@@")[1:]:
        body = block.split("\n", 1)[1] if "\n" in block else ""
        pre = "\n".join(l[1:] for l in body.split("\n") if l[:1] in (" ", "-"))
        if pre.strip() and before.count(pre) != 1:
            return False
    return True


def main(endstate: str, apply: bool) -> int:
    ES = pathlib.Path(endstate)
    L = POST.read_text(encoding="utf-8").split("\n")
    out, i = [], 0
    kept = redundant = regenerated = missing = 0
    notes: list[str] = []
    # THE APPENDIX APPLIES IN ORDER, AND SO MUST THIS. Six of its amendments are to
    # `eslint.config.mjs` and three to `package.json`; generating each from the chapters'
    # end state gives six hunks that all expect the same pre-image, so one applies and
    # five do not. `landed` tracks the paths a previous amendment has already taken to
    # the tip — for those, there is nothing left to amend and the fence is dropped.
    landed: set[str] = set()
    while i < len(L):
        m = re.match(r'^```(\w*) title="([^"]+)"$', L[i])
        if not m:
            out.append(L[i]); i += 1; continue
        title = m.group(2)
        end = next(j for j in range(i + 1, len(L)) if L[j].startswith("```"))
        path = title.split(",")[0].split(" (deleted)")[0].strip()
        if "(deleted)" in title:
            out += L[i:end + 1]; kept += 1; i = end + 1; continue
        state_f = ES / (re.sub(r"[^A-Za-z0-9]+", "_", path) + ".txt")
        after = tip(path)
        if not state_f.exists() or after is None:
            out += L[i:end + 1]; missing += 1
            notes.append(f"    KEPT (no replayed state or no file at the tip)  {path}")
            i = end + 1; continue
        before = state_f.read_text(encoding="utf-8")
        if path in landed:
            redundant += 1
            notes.append(f"    FOLDED into this file's first amendment            {path}")
            i = end + 1
            while i < len(L) and L[i].strip() == "":
                i += 1
            continue
        if before.rstrip("\n") == after.rstrip("\n"):
            redundant += 1
            notes.append(f"    REDUNDANT — the chapters already land it            {path}")
            # drop the fence and any blank line that followed it
            i = end + 1
            while i < len(L) and L[i].strip() == "":
                i += 1
            continue
        for width in (6, 10, 14, 20, 30, 40):
            d = unified(before.rstrip("\n"), after.rstrip("\n"), width)
            if d and unique(d, before):
                break
        else:
            out += L[i:end + 1]; kept += 1
            notes.append(f"    KEPT (no width gives unique hunks)                 {path}")
            i = end + 1; continue
        out += [f'```diff title="{title}"', *d.split("\n"), "```"]
        landed.add(path)
        regenerated += 1
        i = end + 1
    for n in notes:
        print(n)
    if apply:
        POST.write_text("\n".join(out), encoding="utf-8")
    print(f"regen-appendix: {'APPLIED' if apply else 'DRY RUN'} — {regenerated} regenerated, "
          f"{redundant} redundant and removed, {kept} kept as-is, {missing} unresolvable")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(main(args[0], "--apply" in sys.argv))

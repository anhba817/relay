#!/usr/bin/env python3
"""Regenerate a fence body from the CHECKER's replay state, not from the chapter's tags.

WHY THIS EXISTS ALONGSIDE `regen-fences.py`. That one builds a fence from the diff between
the chapter's two tags, which is right for a fence read on its own and not always right for
the CHAIN. `check-fence-chain.mjs` replays every fence in order from Part 1, so the state a
fence must apply to is whatever the preceding fences produced — and where content reached a
file through an untitled fence, an excerpt, or no fence at all, that state is not the
predecessor tag's. A hunk generated against the tag then matches zero times in the replay.

CLAUDE.md's RULE 1a, IMPLEMENTED: copy the checker, truncate it, make it dump its own end
state, generate from that, delete the copy. **A generator that replays differently from the
checker produces hunks the checker rejects for reasons neither of them explains.** The
predecessor states come from `.probe-chain.mjs`, a copy of the checker whose only change is
to write `state.get(title)` when `applyHunks` returns null.

WIDTH IS CHOSEN, NOT ASSUMED. `-U6` is a default; a pre-image that occurs twice cannot be
applied by a reader and the checker says so. Each width is tried and the first whose every
hunk occurs EXACTLY ONCE in the predecessor state wins — the property the checker tests,
counted the way the checker counts it. Widening is not monotonic: it merges adjacent hunks,
so a wider context can span more repetition than either half did.

Usage: regen-from-replay.py <dump-dir> [--apply] [--only <substring>]
"""
import json, pathlib, re, subprocess, sys, tempfile

WT = pathlib.Path("/home/dong/work/relay/tmp/part3-refactor")
TUT = pathlib.Path("/home/dong/work/relay/relay-tutorial")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(WT), *args],
                          capture_output=True, text=True).stdout


def unified(before: str, after: str, width: int) -> str:
    with tempfile.TemporaryDirectory() as d:
        a, b = pathlib.Path(d) / "a", pathlib.Path(d) / "b"
        a.write_text(before, encoding="utf-8")
        b.write_text(after, encoding="utf-8")
        out = subprocess.run(
            ["git", "diff", "--no-index", f"-U{width}", "--no-color", str(a), str(b)],
            capture_output=True, text=True).stdout
    lines = out.split("\n")
    first = next((i for i, l in enumerate(lines) if l.startswith("@@")), len(lines))
    return "\n".join(lines[first:]).rstrip()


def hunks_unique(diff: str, before: str) -> bool:
    """Every hunk's pre-image occurs exactly once — the checker's own test."""
    for block in diff.split("\n@@")[1:]:
        body = block.split("\n", 1)[1] if "\n" in block else ""
        pre = "\n".join(l[1:] for l in body.split("\n") if l[:1] in (" ", "-"))
        if not pre.strip():
            continue
        if before.count(pre) != 1:
            return False
    return True


def replace_fence(page: pathlib.Path, line_no: int, title: str, body: str) -> bool:
    L = page.read_text(encoding="utf-8").split("\n")
    i = line_no - 1
    if not (0 <= i < len(L) and L[i].startswith("```") and title in L[i]):
        # the checker reports the fence's OPENING line; tolerate a one-line drift
        cands = [j for j in range(max(0, i - 2), min(len(L), i + 3))
                 if L[j].startswith("```") and title in L[j]]
        if not cands:
            return False
        i = cands[0]
    end = next(j for j in range(i + 1, len(L)) if L[j].startswith("```"))
    L[i:end + 1] = [f'```diff title="{title}"', *body.split("\n"), "```"]
    page.write_text("\n".join(L), encoding="utf-8")
    return True


def main(dump_dir: str, apply: bool, only: str | None) -> int:
    # BOTTOM-UP WITHIN A PAGE, AND THE FIRST RUN PROVED WHY. The checker reports a
    # fence's OPENING LINE, so replacing one fence shifts every line number below it in
    # the same page — ten of fourteen refusals in the first pass were "no fence at or
    # near that line", each one caused by an edit made two fences earlier. Sorting by
    # line DESCENDING makes every reported number still valid when its turn comes.
    metas = []
    for m in pathlib.Path(dump_dir).glob("*.meta"):
        d = json.loads(m.read_text(encoding="utf-8"))
        page, line = d["where"].rsplit(":", 1)
        metas.append((page, -int(line), m))
    dumps = [m for _, _, m in sorted(metas)]
    done = failed = 0
    for meta_p in dumps:
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        if meta["locale"] != "en":
            continue                       # the mirror is `sync-vi-fences.py`'s job
        if only and only not in meta["where"]:
            continue
        page_rel, line_no = meta["where"].rsplit(":", 1)
        page = TUT / page_rel
        title = meta["title"]
        before = (meta_p.with_suffix(".txt")).read_text(encoding="utf-8")
        chapter = re.search(r"chapter-(\d+)", page_rel)
        tag = f"rework/part3-ch{int(chapter.group(1))}"
        after = git("show", f"{tag}^{{commit}}:{title}")
        if not after:
            print(f"  SKIP  {title} — absent at {tag}")
            failed += 1
            continue
        for width in (6, 10, 14, 20, 30, 40):
            d = unified(before, after.rstrip(), width)
            if d and hunks_unique(d, before):
                break
        else:
            print(f"  FAIL  {page_rel}:{line_no} {title} — no width gives unique hunks")
            failed += 1
            continue
        n = len(d.split("\n@@")) - 1 + (1 if d.startswith("@@") else 0)
        if apply and not replace_fence(page, int(line_no), title, d):
            print(f"  FAIL  {page_rel}:{line_no} — no fence for {title} at or near that line")
            failed += 1
            continue
        print(f"  {'ok  ' if apply else 'dry '}  {page_rel.split('/')[-2]:38} {title:52} "
              f"-U{width} {n} hunk(s)")
        done += 1
    print(f"regen-from-replay: {'APPLIED' if apply else 'DRY RUN'} — {done} regenerated, "
          f"{failed} refused")
    return 1 if failed else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    sys.exit(main(args[0], "--apply" in sys.argv, only))

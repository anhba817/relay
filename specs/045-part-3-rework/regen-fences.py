#!/usr/bin/env python3
"""Regenerate one chapter's fence bodies from the rebuild's own two tags.

The rebuild ports each chapter onto a new base, so every fence in it was authored
against a state that no longer exists. This replaces each titled fence's BODY with what
the diff between the chapter's tags actually says, matching by title, and leaves prose
alone.

A TITLE IS A PATH EVEN WITHOUT A SLASH. The first version required one, which silently
skipped `turbo.json` and `package.json` — those fences kept a body from the old base and
`check-chapter` then reported them as replaying to something else. Match against the
diff's own file list instead of guessing at the shape of a path.

Usage: regen-fences.py <chapter-dir> <base-tag> <head-tag> [--apply]
"""
import re, subprocess, sys
from pathlib import Path

WT = Path("/home/dong/work/relay/tmp/part3-refactor")
GENERATED = ("pnpm-lock.yaml", "/migrations/meta/")

def git(*args):
    return subprocess.run(["git", "-C", str(WT), *args], capture_output=True, text=True).stdout

def unique_hunks(diff: str, base_text: str | None) -> bool:
    """Does every hunk's pre-image occur exactly once in the base file?

    That is the property a reader needs: a hunk says "find THIS and replace it", and a
    pre-image occurring twice leaves them guessing. Counted the way `check-chapter`
    counts it, so the two agree — a generator that replays differently from the checker
    produces hunks the checker rejects for reasons neither of them explains.
    """
    if base_text is None:
        return True
    for block in diff.split("\n@@")[1:]:
        body = block.split("\n", 1)[1] if "\n" in block else ""
        pre = "\n".join(
            l[1:] for l in body.split("\n")
            if l[:1] in (" ", "-") and not l.startswith("---")
        )
        if not pre.strip():
            continue
        if base_text.count(pre) != 1:
            return False
    return True


def bodies(base, head):
    files = git("diff", "--name-only", f"{base}..{head}").split()
    added = set(git("diff", "--name-only", "--diff-filter=A", f"{base}..{head}").split())
    out = {}
    for f in files:
        if any(k in f for k in GENERATED):
            continue
        if f in added:
            out[f] = ("whole", git("show", f"{head}:{f}").rstrip())
        else:
            # `-U6` IS A DEFAULT, NOT A RULE, and this widens until the hunks are
            # unique. A pre-image that matches twice cannot be applied by a reader —
            # `check-chapter` says `matched N times (need 1)` and the fence is
            # unusable. Widening merges adjacent hunks, so a wider context is not
            # monotonically better: this tries each width and takes the FIRST whose
            # every hunk pre-image occurs exactly once in the base file, which is the
            # property that matters rather than the number.
            for width in (6, 10, 14, 20, 30):
                d = git("diff", f"-U{width}", "--no-color", f"{base}..{head}", "--", f)
                if unique_hunks(d, git("show", f"{base}:{f}") or None):
                    break
            # THE HEADER IS STRIPPED BY POSITION, NOT BY PREFIX, AND A `.sql` FILE IS
            # WHY. This filtered every line starting with `--- ` or `+++ `, which is
            # right for the two header lines and catastrophic for a removed SQL
            # comment: `-- a trigger that can never match` is emitted as
            # `--- a trigger that can never match`, one `-` for the removal and two for
            # the comment, and the filter deleted it as though it were a header.
            #
            # The fence then carried the ADDITIONS of a rewritten comment block and
            # none of the REMOVALS, so `check-chapter` reported `hunk pre-image matched
            # 0 times` — the generator producing a fence the checker rejects, which is
            # the failure this file's own header warns about.
            #
            # Everything before the first `@@` is header and nothing after it is, so
            # position decides it exactly. `git diff` always emits the hunks last.
            lines = d.split("\n")
            first_hunk = next(
                (i for i, l in enumerate(lines) if l.startswith("@@")), len(lines)
            )
            body = "\n".join(lines[first_hunk:]).strip()
            out[f] = ("diff", body)
    return out

def main(chapter_dir, base, head, apply=False):
    have = bodies(base, head)
    page = Path(chapter_dir) / "page.mdx"
    L = page.read_text(encoding="utf-8").split("\n")
    out, used, i = [], set(), 0
    while i < len(L):
        m = re.match(r'^```(\w+)(?: title="([^"]+)")?$', L[i])
        if not m:
            out.append(L[i]); i += 1; continue
        end = next(j for j in range(i + 1, len(L)) if L[j].startswith("```"))
        title = m.group(2)
        path = None
        if title and "(excerpt)" not in title:
            cand = title.split(",")[0].split(" (deleted)")[0].strip()
            if cand in have:
                path = cand
        if path:
            kind, body = have[path]
            lang = "diff" if kind == "diff" else m.group(1)
            out.append(f'```{lang} title="{title}"')
            out += body.split("\n")
            out.append("```")
            used.add(path)
        else:
            out += L[i:end + 1]
        i = end + 1
    if apply:
        page.write_text("\n".join(out), encoding="utf-8")
    missing = sorted(f for f in have if f not in used)
    print(f"regen-fences: {'APPLIED' if apply else 'DRY RUN'} — "
          f"{len(used)} of {len(have)} changed files matched a fence")
    if missing:
        print(f"  changed but NOT fenced ({len(missing)}) — each needs prose or a reason:")
        for f in missing:
            print(f"    {f}")
    return 0

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--apply"]
    sys.exit(main(*args[:3], apply="--apply" in sys.argv))

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
            d = git("diff", "-U6", "--no-color", f"{base}..{head}", "--", f)
            body = "\n".join(
                l for l in d.split("\n")
                if not l.startswith(("diff --git", "index ", "--- ", "+++ ", "new file mode"))
            ).strip()
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

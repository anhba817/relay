#!/usr/bin/env python3
"""One chapter's fences, applied to the previous tag, must produce this one.

WHY A PER-CHAPTER CHECK EXISTS AT ALL. `check:fences` replays every chapter onto
`relay-platform` and compares the end state to that repository's working tree. During
the rebuild the new history lives on a branch in a worktree and `relay-platform` still
holds the old one, so the gate cannot pass and cannot be made to — it is measuring the
wrong tree by design until the rebuild is adopted. Without something in its place, 24
chapters would be written with no check at all and the first signal would arrive at the
end.

IT USES THE GATE'S OWN SEMANTICS, not `git apply`. `check-fence-chain.mjs` applies a
hunk by finding its pre-image EXACTLY ONCE and replacing it; `git apply` is happy with
fuzz and context it can relocate. A fence this accepts and the gate rejects would be the
worst outcome, so the stricter rule is the one enforced here.

Usage: check-chapter.py <chapter-dir> <base-ref> <target-ref>
"""
import re, subprocess, sys
from pathlib import Path

WT = Path("/home/dong/work/relay/tmp/part3-refactor")
TITLE = re.compile(r'^```(\w+) title="([^"]+)"$')

def at(ref, path):
    r = subprocess.run(["git", "-C", str(WT), "show", f"{ref}:{path}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

def hunks(body):
    groups, cur = [], []
    for l in body:
        if l.startswith("@@"):
            if cur: groups.append(cur)
            cur = []
        else: cur.append(l)
    if cur: groups.append(cur)
    strip = lambda l: l[1:] if l[:1] in " +-" else l
    out = []
    for g in groups:
        pre = [strip(l) for l in g if not l.startswith("+")]
        post = [strip(l) for l in g if not l.startswith("-")]
        if "\n".join(pre) != "\n".join(post):
            out.append((pre, post))
    return out

def main(chapter_dir, base, target):
    page = Path(chapter_dir) / "page.mdx"
    lines = page.read_text(encoding="utf-8").split("\n")
    fences, i = [], 0
    while i < len(lines):
        m = TITLE.match(lines[i])
        if m:
            end = next(j for j in range(i + 1, len(lines)) if lines[j].startswith("```"))
            fences.append((m.group(1), m.group(2), lines[i + 1:end]))
            i = end
        i += 1

    # WHICH TITLES NAME A FILE — asked of the diff, not guessed from the shape of the
    # string. Guessing said a title with no space and no slash must be a path, so a
    # prose fence titled `42P01` was looked up as one and reported missing. The tags
    # know exactly which files changed; anything else is prose.
    changed = set(
        subprocess.run(["git", "-C", str(WT), "diff", "--name-only", f"{base}..{target}"],
                       capture_output=True, text=True).stdout.split()
    )

    problems, checked = [], 0
    for lang, title, body in fences:
        if "(excerpt)" in title:
            continue
        path = title.split(",")[0].split(" (deleted)")[0].strip()
        if path not in changed:
            continue                      # prose title, or a file this chapter did not touch
        want = at(target, path)
        if want is None:
            problems.append(f"{path}: not in {target}")
            continue
        checked += 1
        if lang == "diff":
            state = at(base, path) or ""
            text = state
            for pre, post in hunks(body):
                p = "\n".join(pre)
                n = text.count(p)
                if n != 1:
                    problems.append(f"{path}: hunk pre-image matched {n} times (need 1) — "
                                    f"starts {next((l for l in pre if l.strip()), '')[:60]!r}")
                    text = None
                    break
                text = text.replace(p, "\n".join(post))
            if text is None:
                continue
        else:
            text = "\n".join(body)
        if text.rstrip("\n") != want.rstrip("\n"):
            problems.append(f"{path}: replays to something else than {target}")
    for p in problems:
        print(f"  {p}", file=sys.stderr)
    print(f"check-chapter: {len(fences)} fences, {checked} compared, {len(problems)} problem(s)")
    print(f"check-chapter: bytes only — it cannot say whether the PROSE describes the diff")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))

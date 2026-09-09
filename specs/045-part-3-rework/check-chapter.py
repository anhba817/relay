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

# The specification and its siblings live in the tutorial's own repository, not in the
# platform worktree the fence chain replays.
DOCS = Path("/home/dong/work/relay")


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

    # AND A TITLE THAT NAMES NO FILE AT ALL IS NOT A PROSE TITLE.
    #
    # `path not in changed` covers two very different cases with one `continue`: a
    # fence quoting a file an EARLIER chapter built (legitimate, and common), and a
    # fence naming a path that exists in no chapter — which is a reader following a
    # filename to nothing. Chapter 8 fenced `services/dispatcher/src/dispatcher.itest.ts`
    # and `services/gateway/src/limits.itest.ts` after the reorder moved the dispatcher
    # to the webhook chapters and the limiter to movement VII, and both were reported as
    # prose. `(excerpt)` titles hid three more the same way.
    #
    # So the existence question is asked separately, of the target tag, for every title
    # that looks like a path — INCLUDING excerpts, which are exempt from the byte
    # comparison and not from existing.
    problems: list[str] = []

    # A TITLE IS A PATH EVEN WITHOUT A SLASH, AND THIS FILE'S SIBLING SAYS SO.
    #
    # `regen-fences.py` carries the same note because it made the same mistake first:
    # requiring a `/` silently skipped `turbo.json` and `package.json`. Written again
    # here, it skipped `eslint.config.mjs` and `vitest.coverage.config.mts` — so the
    # existence check simply did not run on the two root-level configs this chapter
    # edits most.
    #
    # NOT DEFINED AS "EXISTS", which is the tempting fix and a circular one: an
    # existence check whose subject is "titles that name an existing file" can never
    # fail. So the test is on the SHAPE — no whitespace, and either a directory
    # separator or a source extension — and it stays independent of the answer.
    SOURCE_EXT = (".ts", ".mts", ".cts", ".js", ".mjs", ".cjs", ".sql", ".json",
                  ".yaml", ".yml", ".sh", ".md", ".mdx")

    def looks_like_a_path(t: str) -> bool:
        t = t.split(",")[0].strip()
        if not t or " " in t or "\t" in t:
            return False
        return "/" in t or t.endswith(SOURCE_EXT)

    for lang, title, body in fences:
        bare = (title.split(",")[0]
                     .replace(" (excerpt)", "")
                     .replace(" (deleted)", "")
                     .strip())
        if not looks_like_a_path(bare):
            continue
        if "(deleted)" in title:
            continue                      # a deletion is asserted by the chain, not here
        if at(target, bare) is None:
            # NOT EVERY PATH-SHAPED TITLE NAMES A PLATFORM FILE. The specification lives
            # in THIS repository — `docs/04-srs.md` — and a chapter quoting a clause
            # fences it by its real path. The sender chapter is the first rework chapter
            # to do so, and this check called a file that exists "absent" because it
            # looked in one of the two trees the tutorial cites.
            #
            # Checked here rather than exempted by prefix: the point of the check is that
            # a title naming nothing is a typo, and a path that resolves in the docs repo
            # is not a typo. A `docs/` title that resolves NOWHERE still fails.
            if (DOCS / bare).is_file():
                continue
            problems.append(
                f"{bare}: fenced here and in no chapter — absent from {target} "
                f"and from {DOCS}"
            )

    problems_existence = len(problems)
    checked = 0
    for lang, title, body in fences:
        if "(excerpt)" in title:
            continue
        path = title.split(",")[0].split(" (deleted)")[0].strip()
        # THE DELETION CHECK RUNS BEFORE THE `changed` GUARD, and the order is the check.
        # Placed after it, a title naming a path that was NEVER in the repository passed
        # silently: the path is not in `changed`, so the loop skipped it, and the
        # existence check above skips `(deleted)` titles by design. Found by probing this
        # very assertion red — `never-existed.guard.ts (deleted)` gave 0 problems. A
        # deletion IS a change, so a `(deleted)` title outside `changed` is already wrong.
        # A `(deleted)` TITLE IS ASSERTED, NOT SKIPPED. The existence check above skips
        # these — a deleted file is absent by definition — and this loop did not, so it
        # demanded the file exist in the head tree and reported every deletion fence as
        # "not in <tag>". One had been sitting in the credentials chapter since it was
        # ported: `environment-context.guard.ts (deleted)`, correctly titled, correctly
        # deleted, reported as a problem by the only checker that reads the chapter.
        #
        # Asserted rather than skipped, because a skip would also pass a title claiming a
        # deletion that never happened: absent from the head AND present in the base is
        # what "this chapter deleted it" means, and both halves are checkable.
        if "(deleted)" in title:
            if at(target, path) is not None:
                problems.append(f"{path}: titled (deleted) and still present in {target}")
            elif at(base, path) is None:
                problems.append(f"{path}: titled (deleted) but absent from {base} too")
            else:
                checked += 1
            continue
        if path not in changed:
            continue                      # an earlier chapter's file, quoted here
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

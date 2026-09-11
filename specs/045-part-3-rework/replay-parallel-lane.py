#!/usr/bin/env python3
"""Replay the chain applying a gated swap table, by chapter or by commit.

TWO TABLES USE THIS, which is why the table is an argument. `parallel-lane-table.json`
carries 043's isolation fixes and the de-serialisation that depends on them;
`ack-sample-table.json` carries the two forged-frame samples that 044's required
`revisions` field invalidated. Same mechanism, different subject, and keeping them in one
file would have said they were one decision.

WHY GATED. Three changes arrive at three different chapters and each is only true from
its own: the presence count is scoped where that suite is born, the lanes stop serialising
where the assertion that blocked them is fixed, and the limits helpers arrive with the file
they belong to. An ungated table would apply the config change from the outbox chapter,
where it is false — the serialisation was the right answer until the assertions were.

A COMMIT'S CHAPTER IS THE FIRST TAG IT IS AN ANCESTOR OF. Not the nearest tag by date:
the chain is linear and the tags are its checkpoints, so ancestry is the definition.

AND ONE GATE IS A COMMIT RATHER THAN A CHAPTER, because a chapter is not always fine
enough. The notifications fix reads `endpointId`, and that variable arrives in the middle
of chapter 21 — at the commit that stopped the suite driving a global sweep. Gated by the
chapter, the swap would be attempted two commits early against a `disable()` that takes no
arguments. `from_commit` says: from this commit onward, by ancestry, in the same linear
chain. An entry may carry either gate; both are ANDed when it carries both.

Usage: replay-parallel-lane.py <base-ref> <head-ref> [--table NAME] [--apply]
"""
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
WT = "/home/dong/work/relay/tmp/part3-refactor"


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", WT, *a], capture_output=True, text=True).stdout


def has_ancestor(commit: str, ancestor: str) -> bool:
    """Is `ancestor` at or behind `commit`? A commit is its own ancestor, so the gate
    includes the commit it names — which is what "from this commit onward" means."""
    return subprocess.run(
        ["git", "-C", WT, "merge-base", "--is-ancestor", ancestor, commit]
    ).returncode == 0


def chapter_of(commit: str, tags: list[tuple[int, str]]) -> int:
    for n, sha in tags:
        if subprocess.run(["git", "-C", WT, "merge-base", "--is-ancestor", commit, sha]).returncode == 0:
            return n
    return 99


def main(base: str, head: str, apply: bool, table_name: str) -> int:
    table = json.loads((HERE / table_name).read_text(encoding="utf-8"))
    tags = [(n, git("rev-parse", f"rework/part3-ch{n}^{{commit}}").strip()) for n in range(1, 27)]
    commits = git("rev-list", "--reverse", f"{base}..{head}").split()
    parent = git("rev-parse", f"{base}^{{commit}}").strip()
    applied = skipped = 0
    for c in commits:
        ch = chapter_of(c, tags)
        if apply:
            subprocess.run(["git", "-C", WT, "read-tree", "--reset", "-u", c], check=True)
        n_here = 0
        for e in table:
            if "from_chapter" in e and ch < e["from_chapter"]:
                continue
            if "from_commit" in e and not has_ancestor(c, e["from_commit"]):
                continue
            p = pathlib.Path(WT) / e["file"]
            if not p.exists():
                continue
            t = p.read_text(encoding="utf-8")
            if e["old"] not in t:
                continue
            if t.count(e["old"]) != 1:
                print(f"  REFUSING {e['file']} at {c[:8]}: matches {t.count(e['old'])} times",
                      file=sys.stderr)
                return 2
            if apply:
                p.write_text(t.replace(e["old"], e["new"]), encoding="utf-8")
            n_here += 1
        if n_here:
            applied += 1
        else:
            skipped += 1
        if not apply:
            continue
        subprocess.run(["git", "-C", WT, "add", "-u"], check=True)
        tree = git("write-tree").strip()
        env = {k: git("log", "-1", f"--format=%{v}", c).strip()
               for k, v in (("GIT_AUTHOR_NAME", "an"), ("GIT_AUTHOR_EMAIL", "ae"),
                            ("GIT_AUTHOR_DATE", "aI"), ("GIT_COMMITTER_NAME", "cn"),
                            ("GIT_COMMITTER_EMAIL", "ce"), ("GIT_COMMITTER_DATE", "cI"))}
        msg = git("log", "-1", "--format=%B", c)
        new = subprocess.run(["git", "-C", WT, "commit-tree", tree, "-p", parent, "-m", msg],
                             capture_output=True, text=True,
                             env={**dict(__import__("os").environ), **env}).stdout.strip()
        parent = new
    if apply:
        print(f"  new tip: {parent[:8]}")
    print(f"replay-parallel-lane: {'APPLIED' if apply else 'DRY RUN'} — "
          f"{applied} commits touched, {skipped} unchanged, {len(commits)} replayed")
    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    name = "parallel-lane-table.json"
    if "--table" in argv:
        i = argv.index("--table")
        name = argv[i + 1]
        del argv[i : i + 2]
    args = [a for a in argv if not a.startswith("--")]
    sys.exit(main(args[0], args[1], "--apply" in argv, name))

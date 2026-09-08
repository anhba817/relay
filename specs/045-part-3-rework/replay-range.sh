#!/usr/bin/env bash
# Replay <base>..<head> tree-by-tree with the reference convention applied, onto a
# parallel branch. Non-destructive: builds `refs-replayed` and moves nothing.
#
# WHY THIS EXISTS SEPARATELY FROM `replay-refs.sh`. That one rebuilt the whole branch
# once, to establish the convention. This one runs PER CHAPTER, because a chapter's
# port cherry-picks commits from the published history and every one of them carries
# the ordinals the convention removed. Chapter 3.9's tag was measured at 81 explicit
# references after its port; chapter 3.8's, rewritten, at zero. The rewrite is a step
# in the per-chapter loop and not a phase of its own.
#
# Usage: replay-range.sh <base-ref> <head-ref>
set -euo pipefail
WT=/home/dong/work/relay/tmp/part3-refactor
S=/home/dong/work/relay/specs/045-part-3-rework
cd "$WT"
# `^{commit}` IS NOT OPTIONAL. `git rev-parse` on an ANNOTATED tag returns the tag
# object, and `commit-tree -p <tag object>` fails with "is not a valid 'commit'
# object" — a message that names a sha nothing in the script printed. The rework tags
# are annotated because a tag carries the chapter title a reader checking it out
# wants; that made every bare rev-parse in this repository a trap.
BASE=$(git rev-parse "$1^{commit}")
PARENT=$BASE
MAP=/tmp/claude-1000/-home-dong-work-relay/3bfc1c57-63b8-4e6e-85eb-2bc90373f93b/scratchpad/sha-map-range.txt
: > "$MAP"
n=0
total=$(git rev-list --count "$1..$2")
for C in $(git rev-list --reverse "$1..$2"); do
  n=$((n+1))
  git read-tree --reset -u "$C"
  RELAY_PLATFORM=$WT python3 "$S/rewrite-refs.py" --rule delete     --apply >/dev/null
  RELAY_PLATFORM=$WT python3 "$S/rewrite-refs.py" --rule substitute --apply >/dev/null
  RELAY_PLATFORM=$WT python3 "$S/apply-read-class.py" --apply >/dev/null
  git add -A
  T=$(git write-tree)
  NEW=$(GIT_AUTHOR_NAME="$(git log -1 --format=%an "$C")" \
        GIT_AUTHOR_EMAIL="$(git log -1 --format=%ae "$C")" \
        GIT_AUTHOR_DATE="$(git log -1 --format=%aI "$C")" \
        GIT_COMMITTER_NAME="$(git log -1 --format=%cn "$C")" \
        GIT_COMMITTER_EMAIL="$(git log -1 --format=%ce "$C")" \
        GIT_COMMITTER_DATE="$(git log -1 --format=%cI "$C")" \
        git commit-tree "$T" -p "$PARENT" -m "$(git log -1 --format=%B "$C")")
  echo "$C $NEW" >> "$MAP"
  PARENT=$NEW
  printf '  %2d/%s  %s -> %s  %s\n' "$n" "$total" "${C:0:8}" "${NEW:0:8}" \
    "$(git log -1 --format=%s "$C" | cut -c1-50)"
done
git branch -f refs-replayed "$PARENT"
echo "  refs-replayed = ${PARENT:0:8}  ($n commits)"

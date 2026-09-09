#!/usr/bin/env bash
# Replay <base>..<head> tree-by-tree applying ONLY `repair-welds.py`, onto a parallel
# branch, and print the old->new sha map so the chapter tags can be re-pointed.
#
# WHY NOT `replay-range.sh`. That one runs the reference rules, which are not idempotent
# in the direction that helps: they remove ordinals, and these trees have none left, so
# they would find nothing and repair nothing. The weld is already in the trees. This
# replay does one thing and the diff it produces is exactly the newlines going back.
#
# Usage: replay-repair.sh <base-ref> <head-ref>
set -euo pipefail
WT=/home/dong/work/relay/tmp/part3-refactor
S=/home/dong/work/relay/specs/045-part-3-rework
cd "$WT"
# `^{commit}` IS NOT OPTIONAL on an annotated tag; see replay-range.sh.
BASE=$(git rev-parse "$1^{commit}")
PARENT=$BASE
MAP=/tmp/claude-1000/-home-dong-work-relay/3bfc1c57-63b8-4e6e-85eb-2bc90373f93b/scratchpad/sha-map-repair.txt
: > "$MAP"
n=0
total=$(git rev-list --count "$1..$2")
for C in $(git rev-list --reverse "$1..$2"); do
  n=$((n+1))
  git read-tree --reset -u "$C"
  RELAY_PLATFORM=$WT python3 "$S/repair-welds.py" --apply >/dev/null
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
  printf '  %2d/%s  %s -> %s\n' "$n" "$total" "${C:0:8}" "${NEW:0:8}"
done
git branch -f welds-repaired "$PARENT"
echo "  welds-repaired = ${PARENT:0:8}  ($n commits)   map: $MAP"

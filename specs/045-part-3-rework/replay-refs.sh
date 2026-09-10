#!/usr/bin/env bash
# Rebuild part2-ch8..backup/pre-refs with the reference convention applied to every
# commit's TREE.
#
# RE-RUNNABLE, AND IT HAS TO BE. The reference convention is a function of
# `chapter-map.json`, and the map changed once already mid-rebuild — old 3.10's
# harness moved to new 8 after a cherry-pick conflict revealed the dependency. Any
# such change invalidates every substituted name, so the rewrite cannot be a one-off
# edit; it is a pass that runs again whenever the map moves. That is the argument for
# building it rather than hand-editing 102 references.
#
# WHY NOT `git filter-branch`: it does exactly this and rewrites the refs in place.
# This builds a parallel branch and moves nothing, so a bad run costs a re-run rather
# than a recovery. Tags are repointed by the caller from `sha-map.txt`.
#
# WHY TREE-BY-TREE AND NOT PATCH-BY-PATCH: replaying patches conflicts wherever the
# rewrite touched a line a later commit also touches — which is the same structural
# reason the four snapshot re-derivations failed. Trees have no such problem. Tree-by-tree, not patch-by-patch: replaying patches would conflict
# wherever the rewrite touched a line a later commit also touches.
#
# NON-DESTRUCTIVE. Builds a parallel branch and moves no existing ref. The caller
# verifies, then repoints.
set -euo pipefail
WT=/home/dong/work/relay/tmp/part3-refactor
# THE FENCED HALF OF THE CORPUS NEEDS THE TUTORIAL, and `$WT`'s parent has no
# `relay-tutorial` beside it — which is the default `platform_files` used to take.
# It silently returned an EMPTY fenced set, so every scan this script ran saw only
# `SOURCE_SUFFIXES` and passed over `services/api/Dockerfile`, which is fenced and
# has no extension. `refrules` now refuses an absent tutorial rather than shrinking.
TUT=${RELAY_TUTORIAL:-/home/dong/work/relay/relay-tutorial}
S=/home/dong/work/relay/specs/045-part-3-rework
cd "$WT"

BASE=$(git rev-parse part2-ch8)
PARENT=$BASE
MAP=/tmp/claude-1000/-home-dong-work-relay/3bfc1c57-63b8-4e6e-85eb-2bc90373f93b/scratchpad/sha-map.txt
: > "$MAP"

n=0
for C in $(git rev-list --reverse part2-ch8..backup/pre-refs); do
  n=$((n+1))
  git read-tree --reset -u "$C"
  RELAY_PLATFORM=$WT RELAY_TUTORIAL=$TUT python3 "$S/rewrite-refs.py" --rule delete     --apply >/dev/null
  RELAY_PLATFORM=$WT RELAY_TUTORIAL=$TUT python3 "$S/rewrite-refs.py" --rule substitute --apply >/dev/null
  # The read class, decided by hand and recorded as a table. No --require-all here:
  # an early tree legitimately holds none of these yet. The caller asserts all 23
  # fire against the FINAL tree, which is where a typo becomes visible.
  RELAY_PLATFORM=$WT RELAY_TUTORIAL=$TUT python3 "$S/apply-read-class.py" --apply >/dev/null
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
  printf '  %2d/%s  %s -> %s  %s\n' "$n" "$(git rev-list --count part2-ch8..backup/pre-refs)" \
    "${C:0:8}" "${NEW:0:8}" "$(git log -1 --format=%s "$C" | cut -c1-52)"
done

git branch -f refs-replayed "$PARENT"
echo "  refs-replayed = ${PARENT:0:8}  ($n commits)"

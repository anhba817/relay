#!/usr/bin/env bash
# Replay the rebuilt chain applying ONLY `repair-base-refs.py`, dropping any commit the
# repair empties, onto a new branch — then the chapter tags can be re-pointed.
#
# WHY NOT `replay-range.sh`. That one runs the reference rules, which are not idempotent
# in the direction that helps: they remove ordinals, and these trees mostly have none
# left. This applies twelve exact-string swaps and nothing else, so the diff it produces
# is exactly the twelve lines of gaps 045-63 and 045-65.
#
# `0317d83` BECOMES EMPTY AND IS DROPPED. Once chapters 1 and 2 carry the convention, the
# commit that established it has nothing to change. A tree-by-tree replay would otherwise
# emit an empty commit, so the tree is compared to its parent's and skipped when equal —
# which also drops any other commit the repair happens to empty, and the log says which.
set -euo pipefail
WT=/home/dong/work/relay/tmp/part3-refactor
S=/home/dong/work/relay/specs/045-part-3-rework
OUT=${3:-/tmp/claude-1000/-home-dong-work-relay/3bfc1c57-63b8-4e6e-85eb-2bc90373f93b/scratchpad/replay}
cd "$WT"
# `^{commit}` IS NOT OPTIONAL on an annotated tag; see replay-range.sh.
BASE=$(git rev-parse "$1^{commit}")
HEAD_=$(git rev-parse "$2^{commit}")
PARENT=$BASE
MAP="$OUT/sha-map.txt"
: > "$MAP"
n=0; skipped=0
total=$(git rev-list --count "$BASE..$HEAD_")
for C in $(git rev-list --reverse "$BASE..$HEAD_"); do
  n=$((n+1))
  git read-tree --reset -u "$C"
  RELAY_PLATFORM=$WT python3 "$S/repair-base-refs.py" --apply >/dev/null
  # `-u`, NOT `-A`: the repair edits files the tree already contains and creates none,
  # and `-A` once nearly committed another session's scratch script into a chapter.
  git add -u
  T=$(git write-tree)
  # DROP ONLY WHAT THE REPAIR EMPTIED. The first version dropped any commit whose tree
  # matched its parent's, and seven of the chain's commits were ALREADY empty — a
  # tree-by-tree rebuild emits a commit even when its rewrite leaves nothing, so the
  # chain carries seven commits with substantive subjects and no content (045-70). They
  # are somebody's record and not this replay's business, so they are preserved; only a
  # commit that was non-empty BEFORE and is empty AFTER is dropped, which is the
  # convention commit and nothing else.
  WAS_EMPTY=no
  if [ "$(git rev-parse "$C^{tree}")" = "$(git rev-parse "$C^^{tree}" 2>/dev/null)" ]; then
    WAS_EMPTY=yes
  fi
  if [ "$T" = "$(git rev-parse "$PARENT^{tree}")" ] && [ "$WAS_EMPTY" = no ]; then
    skipped=$((skipped+1))
    printf '  %3d/%s  %s  DROPPED (empty after the repair): %s\n' \
      "$n" "$total" "${C:0:8}" "$(git log -1 --format=%s "$C" | cut -c1-58)"
    echo "$C $PARENT" >> "$MAP"     # old -> the commit that now stands in its place
    continue
  fi
  NEW=$(GIT_AUTHOR_NAME="$(git log -1 --format=%an "$C")" \
        GIT_AUTHOR_EMAIL="$(git log -1 --format=%ae "$C")" \
        GIT_AUTHOR_DATE="$(git log -1 --format=%aI "$C")" \
        GIT_COMMITTER_NAME="$(git log -1 --format=%cn "$C")" \
        GIT_COMMITTER_EMAIL="$(git log -1 --format=%ce "$C")" \
        GIT_COMMITTER_DATE="$(git log -1 --format=%cI "$C")" \
        git commit-tree "$T" -p "$PARENT" -m "$(git log -1 --format=%B "$C")")
  echo "$C $NEW" >> "$MAP"
  PARENT=$NEW
  [ $((n % 25)) -eq 0 ] && printf '  %3d/%s  %s -> %s\n' "$n" "$total" "${C:0:8}" "${NEW:0:8}"
done
git branch -f part3-published "$PARENT"
# A TRAILING NEWLINE, because `while read` drops a final line without one and chapter
# 26's tag never moved the last time this was done by hand.
printf '' >> "$MAP"
echo "  part3-published = ${PARENT:0:8}   $n replayed, $skipped dropped   map: $MAP"

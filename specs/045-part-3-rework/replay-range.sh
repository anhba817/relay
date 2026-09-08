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
# THE MESSAGE IS PART OF THE TREE'S CLAIM, AND IT WAS OUT OF SCOPE BY ACCIDENT.
# This script rewrote file contents and passed `%B` through untouched, so a chapter's
# ports kept the published subjects — "chapter 3.17 phase 5". Measured across the tagged
# chapters: 8 surviving ordinals in messages, three of them SUBJECTS. A subject is the
# part read detached from its tree, the same argument this project already made about a
# task id in a test title: `git log --oneline` has no repository to grep.
#
# Bodies go through `rewrite-refs.py`'s own rules — the same module, not a second copy of
# it, because two copies of a rule are two rules. Subjects take a MAP instead: a subject
# is nine words of prose and substituting a subject name into "phase 5" produces a
# sentence nobody would write. The map is optional and is checked to be complete for the
# range, so a forgotten line fails rather than silently keeping an ordinal.
#
# Usage: replay-range.sh <base-ref> <head-ref> [subject-map]
#   subject-map: lines of `<short-sha>|<new subject>`, one per commit needing one.
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
SUBJECTS=${3:-}
if [ -n "$SUBJECTS" ]; then
  # EVERY MAPPED SHA MUST BE IN THE RANGE. A stale line is a subject that silently keeps
  # its ordinal, which is the failure this map exists to prevent.
  # THE FILE HAS THREE LINE KINDS AND THIS LOOP KNOWS ALL THREE. A comment and a
  # `body|` decision are not shas; reading them as shas made the check reject its own
  # table and say so in a sentence that named a comment.
  while IFS='|' read -r sha _; do
    [ -z "$sha" ] && continue
    case "$sha" in \#*|body) continue ;; esac
    git merge-base --is-ancestor "$sha" "$2" 2>/dev/null \
      || { echo "subject map names $sha, which is not in $1..$2" >&2; exit 1; }
  done < "$SUBJECTS"
fi
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
        git commit-tree "$T" -p "$PARENT" -m "$(
          RELAY_SUBJECTS=$SUBJECTS python3 "$S/rewrite-message.py" "$C"
        )")
  echo "$C $NEW" >> "$MAP"
  PARENT=$NEW
  printf '  %2d/%s  %s -> %s  %s\n' "$n" "$total" "${C:0:8}" "${NEW:0:8}" \
    "$(git log -1 --format=%s "$C" | cut -c1-50)"
done
git branch -f refs-replayed "$PARENT"
echo "  refs-replayed = ${PARENT:0:8}  ($n commits)"

#!/usr/bin/env python3
"""Build the old->new line mapping the comment rewrite actually performed.

WHY THIS READS THE COMMITS AND DOES NOT RE-RUN THE CLASSIFIER. `rewrite-refs.py` made
contextual decisions — sentence position, capitalisation, whether a plural was cut with
the first substitution. Re-running those rules over fence bodies would re-derive them
against a different context and could disagree with what landed in the platform file by
one word, and a chain that disagrees by one word lands on a file that is not the
platform's. The four commits are the record of what was decided. This reads it.

    node fences  ->  the same map  ->  the same bytes

AND IT REFUSES AN AMBIGUOUS MAPPING. If one old line maps to two different new lines in
two files, an exact-match replacement is not well defined and the conflict is reported
instead of being resolved by whichever file the walk reached last.
"""
import re, subprocess, sys, json
from pathlib import Path
from collections import defaultdict

# The fifth commit repairs five comments the fourth joined wrongly. It belongs in the
# map because the fences already carry the fourth commit's damaged text; the closure
# then carries them from the original straight to the repaired form.
# READ FROM GIT, NOT LISTED BY HAND. The list reached five entries and then eight as
# each repair landed, and a map missing its last commit produces fences that stop one
# commit short of the platform — which `check:fences` reports as a HEAD mismatch whose
# two sides look identical up to the column it truncates at.
COMMITS = list(reversed(subprocess.run(
    ["git", "-C", str(Path(__file__).parent.parent.parent / "relay-platform"),
     "log", "--format=%h", "33bbd2a^..HEAD"],
    capture_output=True, text=True, check=True).stdout.split()))
PLATFORM = "/home/dong/work/relay/relay-platform"

# old text -> set of new texts.  new text of None means the line was deleted outright.
# COMPOSED PER COMMIT, IN ORDER, RATHER THAN MERGED AND THEN CLOSED.
#
# Merging every commit's pairs into one dict and following the chains afterwards works
# until a line is rewritten and later restored: `"the deduplication chapter's"` back to
# `"chapter 3.7's"` gave A -> B and B -> A, and closing that is a cycle with no answer.
# Composing in commit order has one: whatever the last commit left. The net for A is A —
# an identity, which is dropped — and the net for B is A.
net = {}
blocks = defaultdict(set)


def compose(a, b):
    """Record that the platform turned line `a` into line `b`, after everything so far."""
    hit = False
    for k, v in list(net.items()):
        if v == a:
            net[k] = b; hit = True
    if not hit:
        net[a] = b

for c in COMMITS:
    d = subprocess.run(["git", "-C", PLATFORM, "show", "--unified=0", "--no-color", c],
                       capture_output=True, text=True, check=True).stdout
    minus, plus = [], []
    def flush():
        # -U0 gives aligned runs: pair them positionally, which is what a comment
        # rewrite produces.  Unequal runs are reported rather than guessed at.
        if len(minus) == len(plus):
            for a, b in zip(minus, plus):
                if a != b:
                    compose(a, b)
        elif plus == []:
            for a in minus:
                compose(a, None)
        else:
            # A REFLOWED COMMENT IS A RUN, NOT A LINE. Deleting `(chapter 3.10,` from a
            # two-line comment lets the remainder fit on one, so 2 old lines become 1 new
            # and there is no line-to-line correspondence to record. 26 lines arrived
            # here and every one is a `/** … */` block that changed shape. Recorded as a
            # run and applied before the single-line map, longest run first.
            # A PURE INSERTION IS NOT A RUN. With no `-` lines this recorded
            # `blocks[()] = (…)`, an empty pre-image that matches at every position in
            # every file. The map is for lines that CHANGED; added lines arrive with
            # their chapter's own fence.
            if minus:
                blocks[tuple(minus)].add(tuple(plus))
        minus.clear(); plus.clear()
    # `--- ` IS A FILE HEADER *OR* A DELETED SQL COMMENT, and telling them apart by
    # prefix cannot be done. A removed `-- Chapter 3.17 — the sender a message never
    # had.` appears in the diff as `--- Chapter 3.17 — …`: one marker plus two comment
    # dashes. Matching on `--- ` dropped every removed line in all fifteen `.sql`
    # migrations, so the map had no entry for their headers and `check:fences` reported
    # 15 HEAD mismatches whose two sides differed only in the part it truncates.
    #
    # POSITION SAYS WHICH IT IS: the two headers sit between `diff --git` and the first
    # `@@` of that file, and nowhere else.
    in_header = False
    for line in d.splitlines():
        if line.startswith("diff --git"):
            flush(); in_header = True; continue
        if line.startswith("@@"):
            flush(); in_header = False; continue
        if in_header:
            continue
        if line.startswith("-"):
            minus.append(line[1:])
        elif line.startswith("+"):
            plus.append(line[1:])
        else:
            flush()
    flush()

amb = {}
una = {k: v for k, v in blocks.items() if len(v) > 1}
print(f"linemap: {len(net)} distinct old lines from {len(COMMITS)} commits")
print(f"  deletions (line removed entirely) {sum(1 for v in net.values() if v is None)}")
print(f"  AMBIGUOUS (one old, two new)      {len(amb)}")
print(f"  reflowed runs                     {len(blocks)}  ({sum(len(k) for k in blocks)} old lines -> {sum(len(next(iter(v))) for v in blocks.values())} new)")
print(f"  AMBIGUOUS runs                    {len(una)}")
for k, v in list(amb.items())[:8]:
    print(f"    {k.strip()[:70]!r}")
    for x in v: print(f"       -> {(x or '<deleted>').strip()[:70]!r}")
for k, v in list(una.items())[:8]:
    print(f"    AMBIGUOUS RUN {k[0].strip()[:70]!r}")

single = {k: v for k, v in net.items() if v != k}
print(f"  identities dropped (rewritten, then restored) {len(net) - len(single)}")
runs = [{"old": list(k), "new": list(next(iter(v)))} for k, v in blocks.items() if len(v) == 1]
json.dump({"single": single, "runs": runs}, open("linemap.json", "w"), indent=0)
print(f"  map written                       {len(single)} lines + {len(runs)} runs -> linemap.json")

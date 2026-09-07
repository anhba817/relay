#!/usr/bin/env python3
"""Fail while a superseded sentence is still published.

WHY THIS EXISTS. `git diff` finds a sentence somebody changed. Nothing finds a sentence
that stopped being true because the code moved underneath it — chapter 3.20 found one by
grepping for a CLAIM rather than a symbol, chapter 3.23 corrected four, and three of those
four were in files no checker reads at all.

Each entry is (why it is wrong, the file, a fragment that is present while it is wrong).
The run is RED until the fragment is gone, which makes the correction a gate rather than a
good intention.

**AN ENTRY MUST NAME A SENTENCE THAT IS ACTUALLY FALSE.** Chapter 3.23 added one for a
sentence that was true — `public-surface.itest.ts`'s list is what that test CALLS, not an
inventory of the public surface — and had to delete the gate rather than satisfy it. A
checker crying wolf on a healthy tree is how a real problem hides.
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

CLAIMS: list[tuple[str, str, str]] = [
    (
        "FR-MSG-11 is P2, which is Part 3 — this comment schedules it for Part 4",
        "relay-platform/packages/protocol/src/frames.ts",
        "fields arrive with Part 2/4",
    ),
    (
        "the two send doors have drifted three times — idem_key vs idempotency_key, the text "
        "bound, and FR-019b's pair rule — so 'cannot drift' is a claim the tree refutes",
        "relay-platform/services/api/src/messages/messages.controller.ts",
        "cannot drift",
    ),
]


def main() -> int:
    still, unreadable = [], []
    for why, rel, fragment in CLAIMS:
        p = ROOT / rel
        try:
            body = p.read_text()
        except OSError:
            unreadable.append((rel, why))
            continue
        if fragment in body:
            still.append((rel, why))
    for rel, why in still:
        print(f"  still published in {rel}\n    {why}")
    for rel, why in unreadable:
        print(f"  UNREADABLE {rel}\n    {why}")
    print(f"check-prose: {len(CLAIMS)} claims across "
          f"{len({c[1] for c in CLAIMS})} files")
    if still or unreadable:
        print(f"check-prose: {len(still)} still present, {len(unreadable)} unreadable")
        return 1
    print("check-prose: none of the superseded sentences is still published")
    print("check-prose: this says nothing about whether the replacements are true")
    return 0


if __name__ == "__main__":
    sys.exit(main())

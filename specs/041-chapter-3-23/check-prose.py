#!/usr/bin/env python3
"""Published sentences chapter 3.23 falsifies — and it is RED until they are fixed.

WHY THIS EXISTS. No gate in this repository reads prose. `check:fences` compares bytes,
`check:srs` counts ids, `check:errors` matches a code against a heading. A sentence that
stopped being true because the code moved underneath it is invisible to all three, and
chapter 3.20's record names that class explicitly: *"A published sentence stopped being
true and no checker could see it."*

Chapter 3.22 wrote the first of these and it earned its keep at the last gate, catching a
claim whose prescription had been corrected and whose assertion had not.

HOW TO READ A FAILURE. Every fragment below is a sentence that is published somewhere and
is false after this chapter. Red means it is still there. Green means none of them is —
and says nothing about whether what replaced them is true.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

# (label, path, fragment)
CLAIMS: list[tuple[str, str, str]] = [
    # ---- the platform's own comments -----------------------------------
    (
        "the @Accepts declaration exists, 25 lines above the sentence denying it",
        "relay-platform/services/api/src/messages/messages.controller.ts",
        "`MessagesController` declares no `@Accepts`",
    ),
    (
        "resume does NOT carry message.deleted — chapter 3.23 decided against it",
        "relay-platform/services/api/src/internal/backfill.controller.ts",
        "and resume will carry",  # one line; the sentence wraps in the source
    ),
    # REMOVED IN PHASE 5, and the reason is the one this file exists to prevent.
    # The entry read "the public surface gains three routes" and pointed at
    # `public-surface.itest.ts`'s list of `POST /v1/channels`, `POST …/members`,
    # `POST /auth/dev-token`, `POST …/messages` and the socket. That list is what
    # THAT TEST CALLS, not an inventory of the surface — so the sentence was true
    # before this chapter and is true after it, and a gate failing on it would have
    # been a checker crying wolf on a healthy tree. The surface's real inventory is
    # `services/api/src/isolation/targets.ts`, derived from the running application,
    # and this chapter's two routes are declared there (T030a, T033h).
    (
        "message_edits is built, not a named absence",
        "relay-platform/services/api/src/db/schema.ts",
        "message_edits (edit chapter)",
    ),
    (
        "FR-MSG-08 is implemented — the tombstone has a writer",
        "relay-platform/services/api/src/db/repository.itest.ts",
        "IS NOT IMPLEMENTED",
    ),
    # ---- a predecessor's record that contradicts its own sibling -------
    (
        "chapter 3.22 corrected this to forty in chapter-notes.md and left it here",
        "specs/040-chapter-3-22/baseline.txt",
        "Thirty-seven new tests read one at a time",
    ),
]


def main() -> int:
    missing: list[str] = []
    still: list[tuple[str, str]] = []
    for label, rel, fragment in CLAIMS:
        path = ROOT / rel
        if not path.exists():
            missing.append(rel)
            continue
        if fragment in path.read_text():
            still.append((rel, label))

    print(f"check-prose: {len(CLAIMS)} claims across {len({c[1] for c in CLAIMS})} files")
    for rel in missing:
        print(f"  MISSING FILE {rel} — the claim cannot be checked, which is not the same as fixed")
    for rel, label in still:
        print(f"  still published in {rel}\n    {label}")
    if missing or still:
        print(f"check-prose: {len(still)} still present, {len(missing)} unreadable")
        return 1
    print("check-prose: none of the superseded sentences is still published")
    print("check-prose: this says nothing about whether the replacements are true")
    return 0


if __name__ == "__main__":
    sys.exit(main())

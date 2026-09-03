#!/usr/bin/env python3
"""Structure and cross-reference checker for one Spec Kit feature directory.

Run from the feature directory:  python3 check-refs.py

WHAT IT CHECKS
  1. tasks.md structure — ids sequential from T001, no duplicates, every line matching
     the checklist format, a file path or command in every description, and [US] labels
     present in user-story phases and absent everywhere else.
  2. Task references in EVERY artifact, not just tasks.md. Three renumbers of this
     feature were each validated inside tasks.md alone, and each left references in
     other files pointing at whatever task later took the number.
  3. Every reference to another feature's `gaps.md` item names its chapter. Item numbers
     are PER-FEATURE and collide: chapter 3.17's item 1 is an unidentified lane flake,
     chapter 3.18's item 1 is an idempotency-key mismatch, and an unqualified "gaps.md
     item 1" resolves — via CLAUDE.md's header — to whichever ledger is most recent.
     This is the third id space where cross-scope collision has bitten, after task ids
     across renumbers and requirement ids across features, which is why it is checked
     rather than remembered.

  4. Every FR- **and every SC-** id in spec.md has a row in traceability.md, and both
     counts are REPORTED rather than written down anywhere. A hardcoded "all 34"
     outlived the spec by three analysis passes and six requirements. A count a tool
     prints cannot go stale; a count in prose always does.

     THE CLASSES ARE LISTED EXPLICITLY BELOW AND AN UNKNOWN ONE FAILS. The first
     version of this check covered FR- only, because FR- was what traceability.md
     happened to contain — 41 requirements traced and 14 success criteria traced
     nowhere, with the checker reporting green. That is a pattern matching the
     examples in front of it rather than the set the rule names, which is the failure
     this project has paid for five times. Adding a class here is a one-line edit;
     the point is that leaving one out is now visible.

WHAT IT CANNOT CHECK, AND THIS MATTERS
  **It compares ids, not claims.** A reference to a task that exists passes, even when
  the sentence around it says something the task does not. One of the three defects that
  prompted this script was exactly that: a paragraph citing three task ids as evidence,
  one of which had become the test that disproved the paragraph. Every id was valid.
  The durable fix for that class is not to cite task ids in prose at all — describe the
  task instead, and let the description rot visibly rather than silently.

  So: green here means no dangling ids. It does not mean the prose is true.

FOREIGN REFERENCES are ids belonging to another feature (a predecessor chapter's task
numbers, quoted in a lesson). They are listed explicitly below rather than pattern-matched,
because a pattern that skips "anything near the word chapter" is the blind spot this
project keeps paying for. An unrecognised foreign id FAILS. Add it here with its source.
"""
import re, sys, pathlib

# Declared (file, id) pairs. NOT bare ids: after a renumber this feature grew past
# 109 tasks, so a predecessor chapter's "T065" collides with a local T065 and an
# id-only allowlist silently accepts either. Testing this checker red is what found
# that — removing T065 from an id-only list changed nothing, because T065 had become
# real. Pairs make the collision impossible to hide.
FOREIGN: set[tuple[str, str]] = {
    # EMPTIED WHEN THIS COPY WAS MADE, and that is the point of the copy. The
    # predecessor's set held thirty pairs naming chapter 3.22's task ids — `T041a`,
    # `T040a`, and so on — every one of them a declaration that a sentence in THAT
    # chapter's records needed to cite THAT chapter's task. Carried into this chapter
    # they would mask a real citation of a task id that does not exist here.
    #
    # Chapter 3.22's `gaps.md` item 8 argued the per-chapter copy earns its keep
    # because an instrument can be improved mid-chapter. This is the other half of
    # that bargain: a copy inherits state as well as code, and the state has to be
    # cleared deliberately. Nothing warned about it; the file simply arrived full.
    #
    # Filled one pair at a time as a record names what a task does.
}


# THE CLASSES THAT MUST BE TRACED. Explicit, and an empty class fails — a pattern that
# silently matches nothing is how the success criteria went untraced for eleven passes.
ID_CLASSES = {
    "requirement": r"^- \*\*(FR-[0-9]+[a-z]?)\*\*",
    # `[a-z]?` ADDED IN CHAPTER 3.23. The FR pattern had the optional letter and this
    # one did not, so `SC-002a` and `SC-006a` were invisible: the printed count read
    # eleven where the file declares thirteen, AND — the half that matters — neither
    # was ever required to have a traceability row. A pattern that silently matches
    # nothing is how a class goes untraced; a pattern that silently matches MOST of a
    # class is worse, because the number it prints looks like an answer.
    #
    # `sweep.py` has the identical hole and is fixed in the same breath. Chapter 3.21
    # widened this file's task-id pattern from `T\d{3}` to `T\d{3}[a-z]?` and that
    # surfaced six live citations in one run; this is the third instrument in three
    # chapters to have matched the examples in front of it rather than the set the
    # rule names.
    "success criterion": r"^- \*\*(SC-\d+[a-z]?)\*\*",
}

# `[ ]` OR `[X]`. The first version matched only unchecked boxes, because it was
# written before any task was done — so the moment phase 1 was marked complete it
# reported 38 problems, starting with "ids are not sequential". A checker that
# only recognises the state it was born in is the blind spot this file's header
# is about, found in its own second week.
# A SUFFIXED ID IS A TASK ID. `T054a` is how this project inserts a task without
# renumbering the hundred below it — chapter 3.17 shipped T012a, T047c and T054b, and
# this pattern rejected all of them as "does not match the checklist format". The
# sequence check below therefore compares the NUMERIC part only: a suffixed id sits
# beside the number it extends and does not advance the count.
TASK = re.compile(r"^- \[[ xX]\] (T\d{3}[a-z]?)( \[P\])?( \[US\d\])? (.+)$")
ANY_TASK_LINE = re.compile(r"^- \[[ xX]\]")
PATHISH = re.compile(r"[\w./<>-]+\.(ts|mts|md|txt|mdx|json|yaml)\b|`docs/|`pnpm |`git |`docker |`python3 |`grep |`sed |specs/|`relay-platform`|`relay-tutorial`")
# THE SUFFIX. This read `T(\d{3})(?![A-Za-z0-9])` and so could not see `T107a`,
# `T012a`, `T031b` or `T047c` — real ids in this chapter's own task list, which
# `TASK` twenty lines up accepts as `T\d{3}[a-z]?`. **Two patterns in one file
# disagreed about what a task id is, and the citation rule was the one that was
# wrong**, so it printed "no undeclared task ids" while `gaps.md` cited `T107a`.
# Sixth instrument in this chapter to match the examples in front of it rather
# than the set the rule names. Derive the suffix from `TASK` rather than
# restating it, so the two cannot drift again.
REF = re.compile(r"(?<![A-Za-z0-9])T(\d{3}[a-z]?)(?![A-Za-z0-9])")

def main() -> int:
    # ANCHORED ON THE SCRIPT, NOT THE SHELL. Both tasks that invoke this say to run it
    # from the repository root; every test of it was run from inside the feature
    # directory, so `Path(".")` passed for ten passes and errored from the documented
    # invocation. A checker whose result depends on where you stood is not a checker.
    here = pathlib.Path(__file__).resolve().parent
    tasks_file = here / "tasks.md"
    if not tasks_file.exists():
        # A FAILURE, not a skip. "no tasks.md here" read like "not applicable" and is
        # how the broken invocation went unnoticed — chapter 3.18's pass 10 found the
        # mirror image, a checker that passed by skipping.
        print(f"check-refs: FAILED — no tasks.md beside this script ({tasks_file})", file=sys.stderr)
        return 2

    problems: list[str] = []
    ids: list[str] = []
    phase = None
    for n, line in enumerate(tasks_file.read_text().split("\n"), 1):
        if line.startswith("## Phase"):
            phase = line.strip("# ").strip()
        if not ANY_TASK_LINE.match(line):
            continue
        m = TASK.match(line)
        if not m:
            problems.append(
                f"tasks.md:{n} does not match the checklist format — expected "
                f"`- [ ] T000` or `- [ ] T000a`, then an optional [P], an optional "
                f"[USn], and a description"
            )
            continue
        tid, _par, story, desc = m.groups()
        ids.append(tid)
        in_story_phase = bool(phase and "User Story" in phase)
        if in_story_phase and not story:
            problems.append(f"tasks.md:{n} {tid} has no [US] label inside {phase}")
        if not in_story_phase and story:
            problems.append(f"tasks.md:{n} {tid} carries{story} outside a user-story phase")
        if not PATHISH.search(desc):
            problems.append(f"tasks.md:{n} {tid} names no file path or command")

    # Suffixed ids extend the number before them rather than taking one of their own,
    # so the sequence is checked over the unsuffixed ids and each suffixed id is
    # checked against the number it claims to extend.
    plain = [t for t in ids if len(t) == 4]
    expected = [f"T{i:03d}" for i in range(1, len(plain) + 1)]
    if len(set(ids)) != len(ids):
        dupes = sorted({t for t in ids if ids.count(t) > 1})
        problems.append(f"duplicate task ids: {', '.join(dupes)}")
    elif plain != expected:
        first = next((a for a, b in zip(plain, expected) if a != b), "?")
        problems.append(f"task ids are not sequential from T001 — first mismatch at {first}")
    for tid in ids:
        if len(tid) == 5 and tid[:4] not in set(plain):
            problems.append(f"{tid} extends {tid[:4]}, which is not a task here")

    # THE RULE: task ids live in tasks.md. Any T-id in another artifact must be a
    # declared foreign reference. Citing a local task id in prose is itself the defect —
    # it survives a renumber as a valid id attached to an unrelated task, which is how a
    # paragraph came to cite the very test that disproved it.
    known = set(ids)
    for path in sorted(here.rglob("*.md")):
        rel = path.relative_to(here).as_posix()
        for n, line in enumerate(path.read_text().split("\n"), 1):
            for m in REF.finditer(line):
                ref = "T" + m.group(1)
                if rel == "tasks.md":
                    if ref not in known:
                        problems.append(f"tasks.md:{n} references {ref}, which is not a task here")
                    continue
                # `traceability.md` IS THE MAP, so task ids are its subject rather
                # than a citation that can go stale unnoticed. Exempting it would be
                # weakening the rule to fit an artifact — this chapter has caught itself
                # doing that three times — so the prohibition becomes a CONSISTENCY
                # CHECK instead: every id the map names must exist in tasks.md. A
                # renumber then turns it red rather than leaving it quietly wrong.
                if rel == "traceability.md":
                    if ref not in set(ids):
                        problems.append(
                            f"traceability.md:{n} names {ref}, which is not a task in "
                            f"tasks.md — the map was generated against a different list"
                        )
                    continue
                if (rel, ref) in FOREIGN:
                    continue
                problems.append(
                    f"{rel}:{n} cites {ref}. Task ids belong in tasks.md — describe the task "
                    f"instead, or declare it in FOREIGN as ({rel!r}, {ref!r})"
                )

    # Gap references must name their chapter — see the header's point 3.
    # SCANNED AS ONE DOCUMENT RATHER THAN LINE BY LINE, and `\s+` rather than a
    # literal space, because the qualifier and the citation can land on either side
    # of a line wrap. Chapter 3.22 wrote "chapter\n3.21's `gaps.md` item 4" and this
    # rule called it unqualified — the SECOND time this pattern has cried wolf on a
    # correctly-qualified reference, which is what the note below records the first
    # of. A checker that is wrong about a healthy tree is how a real problem hides.
    GAP_REF = re.compile(r"(.{0,30}?)`gaps\.md` items? \d", re.S)
    # Tolerates markdown emphasis: "**chapter 3.17's** `gaps.md` item 1" is qualified.
    # The first version of this rule did not, and rejected a correctly-qualified
    # reference on its first run — a checker crying wolf is how a real problem hides.
    GAP_QUALIFIED = re.compile(
        r"(?:chapter|Chapter)\s+3\.\d+'s\*{0,2}\s*$|specs/\d+-chapter-3-\d+/\s*$")
    for path in sorted(here.rglob("*.md")):
        rel = path.relative_to(here).as_posix()
        body = path.read_text()
        for m in GAP_REF.finditer(body):
            if not GAP_QUALIFIED.search(m.group(1)):
                n = body.count("\n", 0, m.start()) + 1
                problems.append(
                    f"{rel}:{n} cites a gaps.md item without naming its chapter — "
                    f"item numbers are per-feature and collide across ledgers"
                )

    # Requirements: every FR in spec.md needs a traceability row. The count is printed,
    # never asserted against a literal — see the header.
    spec = here / "spec.md"
    trace = here / "traceability.md"
    counts: dict[str, int] = {}
    if spec.exists():
        spec_body = spec.read_text()
        trace_body = trace.read_text() if trace.exists() else None
        if trace_body is None:
            problems.append("traceability.md is missing, so nothing is traced")
        for label, pattern in ID_CLASSES.items():
            found = re.findall(pattern, spec_body, re.M)
            counts[label] = len(set(found))
            if len(set(found)) != len(found):
                dupes = sorted({f for f in found if found.count(f) > 1})
                problems.append(f"spec.md declares duplicate {label} ids: {', '.join(dupes)}")
            if not found:
                problems.append(f"spec.md declares no {label} ids — is the class name still right?")
            if trace_body is not None:
                for i in sorted(set(found)):
                    if i not in trace_body:
                        problems.append(f"{i} is in spec.md and has no row in traceability.md")

    # T001a. EVERY ID CITED BY A TASK THAT DOES WORK, not by a commit task.
    #
    # Four analysis passes reported "100% coverage" from `grep "<id> (3.23)" tasks.md`.
    # Eleven of this chapter's tasks are commit lines naming every id in their phase, so
    # three criteria read as covered while one of them — retrieving a message's edit
    # history — had no surface in the platform at all. The number was right four times
    # and meant nothing four times.
    #
    # Chapter 3.22's traceability caught this shape once, by hand, for a requirement
    # whose only mention was the commit that claimed it. This makes it mechanical.
    tasks_p, spec_p = here / "tasks.md", here / "spec.md"
    if tasks_p.exists() and spec_p.exists():
        body, spec_body = tasks_p.read_text(), spec_p.read_text()
        working = [ln for ln in body.split("\n")
                   if ln.startswith("- [") and "Commit phase" not in ln]
        for ident in re.findall(r"^- \*\*((?:FR|SC)-\d+[a-z]?)\*\*", spec_body, re.M):
            cited = re.escape(ident) + r" \(3\.23\)"
            if any(re.search(cited, ln) for ln in working):
                continue
            problems.append(
                f"{ident} is cited only by a commit task — naming an id in a commit is "
                f"not verifying it" if re.search(cited, body)
                else f"{ident} is cited by no task at all"
            )

    if problems:
        print(f"check-refs: {len(problems)} problem(s)")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"check-refs: {len(ids)} tasks, ids sequential, "
          f"{len(FOREIGN)} declared foreign reference(s), no undeclared task ids in any "
          f".md outside tasks.md")
    PLURAL = {"requirement": "requirements", "success criterion": "success criteria"}
    print("check-refs: " + ", ".join(f"{n} {PLURAL.get(label, label + 's')}"
                                     for label, n in counts.items())
          + " in spec.md, every one traced")
    print("check-refs: ids only — this says nothing about whether the prose around them is true")
    return 0

if __name__ == "__main__":
    sys.exit(main())

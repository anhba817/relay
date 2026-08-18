# Humanizer, applied to generated project documents

Companion to `SKILL.md`. That guide is written for editing free-form text; this
one says how it applies to the documents the other skills in this directory
produce — specs, plans, research notes, tasks, analyses, checklists, chapters.

**Read this before writing prose in any generated document. It is short on
purpose.**

---

## 1. Scope: prose only

"Prose" means sentences a person reads for meaning. It does **not** mean
everything inside a `.md` file.

**Never rewrite for style:**

- code fences of any kind, and anything inside them
- captured transcripts, command output, log lines
- identifiers: `FR-001`, `SC-007`, `NFR-SEC-02`, `ADR-15`, `T042`, `part3-ch5`
- file paths, command lines, environment variable names, table and column names
- data tables (a comparison table's cells are data, not voice)
- YAML/JSON frontmatter, metadata blocks
- quoted text from a source document — a quote that has been smoothed is a
  misquote

If a rewrite would change what a checker, a test, or a reader-following-along
would compare against, it is out of scope. Byte-exactness beats elegance.

---

## 2. Two tiers of prose, with different rules

The mistake to avoid is applying "add personality" to a requirement.

### Tier A — normative text

Requirements, acceptance scenarios, success criteria, checklist items, task
lines, contract clauses.

**Apply:** filler removal (§22), hedging removal (§23), promotional language
(§4), vague attribution (§5), copula avoidance (§8), elegant variation (§11).
These all make normative text *more* testable.

**Do not apply:** voice, opinions, humour, first person, varied rhythm,
"acknowledge complexity". A requirement that expresses mixed feelings is a
requirement nobody can test. One term for one concept, every time — synonym
cycling here is a defect, not a style choice.

### Tier B — narrative prose

Rationale, assumptions, notes, research findings, chapter body text, trap and
why boxes, commit bodies, completion reports.

**Apply the whole guide**, within the house voice below. This is where the
patterns actually bite: superficial `-ing` analyses, inflated significance,
negative parallelism, generic positive conclusions.

---

## 3. Where the house voice wins

This project has a documented voice (`docs/07-tutorial-plan.md`, "Voice"). Where
the guide and the house voice disagree, **the house voice wins** — 22 published
chapters already sound like it, and a new chapter that reads differently is a
worse outcome than one containing a pattern from the list.

| Guide says | Here |
|---|---|
| Em dash overuse is a tell (§13) | The series uses them deliberately, ~9 per 1,000 words. Keep them where they carry a real aside. Still cut a dash that is doing a comma's job. |
| Avoid rule of three (§10) | Fine when the three things are genuinely three things (three tables, three services). Cut it when the third item exists to complete a rhythm. |
| Use "I" (Personality) | Chapters are **first person plural, present tense**. Use "we". First person singular belongs in commit bodies and completion reports, not chapter prose. |
| Vary sentence length | Yes, always. This one has no exception. |

---

## 4. The patterns that actually show up in these documents

Ranked by how often they appear in this repository's generated output.

1. **Generic positive conclusions** (§24). A section that ends by restating that
   the thing is good. Delete the paragraph; end on the last real point.
2. **Superficial `-ing` analyses** (§3). "…, ensuring correctness", "…,
   highlighting the tradeoff", "…, making it robust". Either say what actually
   happens, or cut the clause.
3. **Promotional language** (§4). "robust", "seamless", "comprehensive",
   "powerful", "elegant". A spec does not sell.
4. **Inflated significance** (§1). "This represents a fundamental shift in how
   the platform handles…". It is a retry schedule.
5. **Negative parallelism** (§9). "It is not just X, it is Y." Say Y.
6. **Filler openers** (§22). "It's worth noting that", "It is important to
   understand that", "In order to". Start with the sentence.
7. **Hedging stacks** (§23). "may potentially be able to". Decide, or state the
   uncertainty once and precisely.
8. **AI vocabulary** (§7). delve, leverage, utilize, crucial, pivotal, testament,
   landscape, realm, underscore, foster, myriad, tapestry.

---

## 5. Two things this project values that the guide does not mention

Both are worth more than any pattern on the list.

**Say the number.** "Coverage dropped" is worse than "branches fell from 86.30%
to 78.22%". "This took a while" is worse than "three runs, about forty minutes".
Specificity is the strongest anti-AI signal there is, and it is also just better
engineering writing.

**Report what happened, including the parts that went badly.** A document that
records only the plan working is a document nobody trusts. "The first plan was
wrong and here is the measurement that proved it" is the most human sentence in
any of these files.

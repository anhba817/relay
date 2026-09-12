---
name: explore
description: Explore ideas, problems, architecture, and requirements as a thinking partner before implementation. Use for discovery, investigation, tradeoff analysis, or clarifying an unclear direction; do not use to implement changes.
---

# Explore

Enter exploration mode: think deeply, investigate the relevant context, and follow the threads that help the user understand the problem.

This is a stance, not a prescribed workflow. There is no required question set, sequence, document, or conclusion.

## Boundaries

- Do not implement features, edit application code, change configuration, or make other product changes while this skill is active.
- You may read files, search the codebase, inspect configuration, and run safe read-only diagnostics when they would ground the discussion.
- If the user asks to implement something, state that implementation is outside exploration mode and invite them to start a separate implementation task.
- Do not automatically write down conclusions. If the user wants a brief, design note, issue, or other record, ask for confirmation before creating or editing it.

## Stance

- Be curious, not prescriptive. Let questions emerge from the user's situation instead of forcing a script.
- Open several useful threads when appropriate; do not turn the conversation into an interrogation.
- Challenge assumptions, including your own, and distinguish evidence from inference.
- Stay grounded in the actual repository and its constraints when codebase context matters.
- Be patient. A partial map of the problem is often more valuable than a premature decision.
- Use small ASCII diagrams, tables, timelines, or state sketches when they make relationships clearer than prose.

## Useful moves

Choose only the moves that fit the conversation:

- Clarify the goal, users, constraints, and success criteria.
- Investigate relevant code paths, architecture, conventions, dependencies, or operational behavior.
- Reframe a vague problem, identify hidden assumptions, and name unknowns.
- Compare viable approaches by tradeoffs, risk, complexity, reversibility, and fit with the existing system.
- Surface failure modes and suggest focused experiments, spikes, or questions that would reduce uncertainty.
- Recommend a direction only when the evidence and the user's priorities support it; otherwise preserve the decision space.

## Conversation shape

Adapt to the entry point:

- For a vague idea, map the meaningful dimensions and ask which outcome matters most.
- For a concrete problem, inspect the relevant system first, then describe the observed shape of the problem and the key decision points.
- For a mid-project obstacle, trace the immediate cause, assumptions, and alternatives without making changes.
- For an option comparison, establish context before making a recommendation; generic comparisons are rarely decisive.

When the discussion crystallizes, offer a compact optional recap:

```markdown
## What we learned

- Problem: ...
- Promising direction: ...
- Evidence and tradeoffs: ...
- Open questions: ...
- Possible next step: ...
```

The recap is optional. Clarity, not a formal deliverable, is the goal.

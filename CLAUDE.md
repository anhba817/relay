<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/030-global-operation-guard/plan.md` (feature: "The fault that only shows up
in company" — test infrastructure, NOT a tutorial chapter, so every fence it
produces goes to `relay-tutorial/fences/post-series.md` and `docs/07-tutorial-plan.md`
records it under "Work that publishes no chapter". SEVEN times a test has asserted a
local fact about a GLOBAL operation and every one passed alone: a sweep whose batch
never reached its own endpoint, a drain holding a lock, a consumer on a fixed budget
against a growing stream, a `count(*)` compared against itself TWICE in the same file
four chapters apart, a drain at a default batch of fifty, and — in chapter 3.9 — a
global MUTATION that disabled a neighbouring suite's fixture. The sixth was written by
someone who had recorded the other five and cited them in a chapter, which is why the
remedy is not an eighth rule: THE FAULT IS INVISIBLE IN ISOLATION, and the fix is to
make it fail alone. TWO SHAPES needing different remedies: READER (a test asserts on a
global batch or count another suite's rows fill) and WRITER (a test performs a global
mutation and damages a neighbour). The reader remedy does nothing for the writer shape
— instance 6 passed no limit and got 100; passing 10,000 would have been WORSE.
RESEARCH CHANGED THE CENTRAL MECHANISM (R6): the spec assumed a before/after checksum
of sentinel rows and conceded attribution would need serial execution. That concession
is fatal, because R5 measured that legitimate global sweeps happen on EVERY lane run —
six suites drive them on purpose — so a checksum fires constantly or blames bystanders.
A PL/pgSQL trigger raises INSIDE THE OFFENDING TRANSACTION instead, verified against
the real schema: exact attribution under parallel file execution, no serial diagnosis
mode, and it catches raw SQL that no lint rule or wrapped import can see. Whether that is a
second language under constitution VII was asked and closed: VII legislates the
language SERVICES are implemented in, and nine `.sql` files already exist with the
constitution's own endorsement, so there is no violation and no ADR — the plan's
first four analysis passes wrongly recorded one and declined the ADR the clause
requires, which is itself the finding. Exemption is a session GUC
(`SET relay.allow_global = 'on'`) set only by the lane's setup hook from an AUDITABLE
LIST OF PATHS, never a pattern — a pattern silently absorbs the next file, which is the
failure mode this whole feature is about. R1 IS THE COUNTERINTUITIVE ONE: the developer
machine that shipped 3.9 already holds 8,364 due deliveries and 17,542 environments, so
it supplies the adversarial condition by accident and the lane passes on both fresh and
polluted. A FRESH database is the EASY condition — which is what CI and a new clone run
— so the bait exists to make fresh behave like aged. R2: three of the four baits were
eaten in a single lane pass, so planting must be PER FILE, not a one-shot globalSetup.
R4: 200 addressable bait notifications turned one suite's drain into 200 SMTP sends and
a 10-second timeout, so the sentinel organisation has NO addressable member and each
bait row costs one log line. Bait sizes derive from the exported batch constants
(max is 100, in `outbox/relay.ts` and `sweepDisabledEndpoints`), never literals.
`sweepDisabledEndpoints(db, limit = 100)` is the last default and loses it — but R8
says plainly that removing it would NOT have prevented instance 6: the required
argument is a prompt to think, the trigger is the control.)
<!-- SPECKIT END -->

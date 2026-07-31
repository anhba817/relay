# Feature Specification: Reader Suggestions — Select, Right-Click, Improve

**Feature Branch**: `015-reader-suggestions`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Allow text selection and right click to suggest improvement in both Vietnamese and English version. Save the suggestion using NextJs and Prisma with a Postgresql database. I will use NeonDB for the database"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader flags a rough sentence in place (Priority: P1)

As a reader of either edition, I find a sentence that reads wrong — a clunky
Vietnamese phrase, a typo, an unclear explanation. I select the text, right-click,
and choose "Suggest an improvement" from the menu that appears. A small dialog
shows the exact text I selected and gives me a box to write my suggestion. I
submit, see a brief thank-you confirmation, and keep reading — the whole detour
costs me under half a minute and never navigates me away from the page.

**Why this priority**: This is the feature — a frictionless capture path for the
reader feedback the vi banner explicitly invites ("chưa có thời gian trau chuốt").
Every other story exists to serve this one.

**Independent Test**: On any published chapter (en and vi), select a sentence,
right-click, submit a suggestion, and confirm it is durably stored with enough
context to locate the passage later; confirm the reading experience is otherwise
unchanged (normal right-click behavior everywhere there is no selection).

**Acceptance Scenarios**:

1. **Given** a reader has selected text inside the article content of any
   tutorial page (chapter or reference doc, either locale), **When** they
   right-click the selection, **Then** a menu option to suggest an improvement
   appears, and choosing it opens a dialog pre-filled with the selected passage
   (read-only) and an empty suggestion box.
2. **Given** the dialog is open, **When** the reader submits a non-empty
   suggestion, **Then** it is durably saved with the page, language, selected
   text, and enough surrounding context to find the passage even after minor
   content edits — and the reader sees a confirmation without leaving the page.
3. **Given** no text is selected (or the selection is outside article content),
   **When** the reader right-clicks, **Then** the browser's normal context menu
   appears — the feature never hijacks right-click globally.
4. **Given** the reader is on a touch device with no right-click, **When** they
   select text (long-press), **Then** an equivalent affordance (a small floating
   "suggest" button near the selection) offers the same dialog.
5. **Given** the vi edition, **Then** the menu item, dialog, confirmation, and
   validation messages are in Vietnamese; on en pages, in English.

---

### User Story 2 - Suggestions survive and stay useful to the author (Priority: P2)

As the author, every submitted suggestion is stored durably in the project's
database with the information I need to act on it later: which page, which
language, the exact selected text, its surrounding context, the reader's
suggestion, and when it arrived. I can review them with simple queries (the
database console is my v1 review tool) and tell at a glance which ones I have
handled.

**Why this priority**: Capture without durable, actionable storage is theater;
but storage details are worthless until the capture path (US1) exists.

**Independent Test**: Submit suggestions from several pages in both locales;
verify each row carries page path, locale, selected text, surrounding context,
suggestion body, timestamp, and a workable status field; verify a suggestion
against a passage that has since been slightly edited is still locatable via its
stored context.

**Acceptance Scenarios**:

1. **Given** a submitted suggestion, **Then** the stored record contains: page
   path, locale, the verbatim selected text, surrounding context (text before
   and after the selection), the suggestion body, and a creation timestamp.
2. **Given** stored suggestions, **Then** each has a review status the author
   can update (at minimum: new / handled), defaulting to new.
3. **Given** the site redeploys or the database restarts, **Then** no accepted
   suggestion is lost — acceptance means durably persisted, not queued in
   memory.

---

### User Story 3 - The door is open but the house doesn't burn (Priority: P3)

As the site operator, anonymous strangers can now write to my database — so the
write path is bounded: submissions are validated and size-capped, a single
visitor cannot flood the table, and garbage does not take the site down or run
up the database bill.

**Why this priority**: Required for the feature to be safe to ship publicly,
but meaningless without the capture path existing first.

**Independent Test**: Submit oversized, empty, and rapid-fire requests directly
against the submission endpoint; verify caps and limits reject them with clear
errors, the page UI surfaces friendly messages, and legitimate submissions still
succeed.

**Acceptance Scenarios**:

1. **Given** a submission with an empty suggestion, an oversized suggestion or
   selection, or a malformed/unknown page path or locale, **Then** it is
   rejected with a clear, localized error and nothing is stored.
2. **Given** a burst of rapid submissions from one visitor, **Then** submissions
   beyond a sensible per-visitor rate are rejected politely and the reader is
   told to slow down.
3. **Given** the database is unreachable, **Then** the reader gets a friendly
   localized failure message and the page itself keeps working — reading is
   never degraded by the feedback machinery.

---

### Edge Cases

- **Right-click is sacred**: the custom menu appears only for selections inside
  article content; selections in code blocks are legitimate targets (code
  suggestions welcome), but browser-native selection behaviors (copy, search)
  must remain reachable — the custom menu must include or preserve a path to
  them, or appear alongside rather than replace where feasible.
- **Huge selections**: a reader selecting an entire chapter is capped (store a
  bounded selection + context, or reject with guidance to select less).
- **Static pages, dynamic write**: the site is statically prerendered and
  deployed via a container; the submission path is the first server-side write
  the site has — it must not break the static rendering of reading pages or
  the existing deployment model.
- **Passage drift**: chapters get edited (the vi polish pass is the point of
  this feature); stored context must be enough to find the passage after small
  edits, and a suggestion whose passage has vanished should still be readable
  as a standalone note.
- **Locale-mixed selections**: selections may include code (English) inside vi
  prose — stored verbatim, no normalization.
- **Privacy**: submissions are anonymous by design; no account, no required
  personal data, and nothing beyond operational basics is collected with them.
- **Concurrent dialogs / repeat use**: submitting, then selecting new text,
  must yield a fresh dialog (no stale selection leaking into the next
  suggestion).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: On every reading page (chapters and reference docs, both locales),
  selecting text within the article content and right-clicking MUST offer a
  "suggest an improvement" action; without a selection (or outside article
  content), right-click behavior MUST remain the browser default.
- **FR-002**: Touch devices MUST get an equivalent selection-triggered
  affordance (no right-click required).
- **FR-003**: The suggestion dialog MUST show the selected passage read-only,
  accept a suggestion body, validate it (non-empty; bounded length), and submit
  without navigating away; success and failure MUST be confirmed in-page.
- **FR-004**: All reader-facing strings of the feature (menu item, dialog,
  buttons, validation and error messages) MUST be localized — Vietnamese on vi
  pages, English on en pages.
- **FR-005**: An accepted submission MUST be durably persisted with: page path,
  locale, verbatim selected text, surrounding context (before/after the
  selection), suggestion body, creation timestamp, and a review status
  defaulting to "new".
- **FR-006**: Selection and suggestion sizes MUST be capped (bounded storage per
  record); submissions violating caps or arriving malformed MUST be rejected
  with localized errors and MUST NOT be stored.
- **FR-007**: The submission endpoint MUST rate-limit per visitor; excess
  submissions are rejected with a polite, localized message.
- **FR-008**: Failure of the storage backend MUST NOT degrade reading: pages
  render as before, and the dialog reports a friendly failure.
- **FR-009**: The feature MUST NOT collect accounts or personal data; records
  are anonymous.
- **FR-010**: The author MUST be able to review suggestions and update their
  status via direct database access (a dedicated review UI is explicitly out of
  scope for this feature).

### Key Entities

- **Suggestion**: One reader-submitted improvement — page path, locale,
  selected text (verbatim), context before/after, suggestion body, status
  (new/handled), created-at. Anonymous; no reader identity.
- **Reading page**: Any chapter or reference-doc page in either locale; the
  set of valid page paths is known to the site (the manifest and docs registry)
  and submissions are validated against it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time reader can go from spotting a rough sentence to a
  submitted suggestion in under 30 seconds, without leaving the page, on both
  the en and vi editions.
- **SC-002**: 100% of accepted submissions are durably stored with page,
  locale, selection, context, body, timestamp, and status — verified by
  submitting from chapters and docs pages in both locales and inspecting
  storage.
- **SC-003**: Right-click without a selection behaves natively on 100% of
  pages; the reading experience (rendering, navigation, performance) is
  unchanged for readers who never use the feature.
- **SC-004**: Invalid submissions (empty, oversized, malformed, over-rate) are
  rejected with localized messages and zero stored rows; a storage outage
  leaves reading fully functional.
- **SC-005**: A suggestion filed against a passage that is later lightly edited
  can still be located via its stored context (demonstrated on at least one
  real edit).
- **SC-006**: On a touch device (or emulation), a reader can submit a
  suggestion via the selection affordance end to end.

## Assumptions

- **The stack is user-fixed, not open**: Next.js (the existing site), Prisma as
  the data layer, PostgreSQL hosted on NeonDB. Recorded here as a binding input
  (like the relay-platform repo decision in 013); the plan chooses versions and
  wiring, not the stack.
- **This is a relay-tutorial site feature**: it lives in the tutorial app, not
  in relay-platform; the tutorial's own conventions apply (bilingual parity,
  reading experience first). The Relay product constitution's service
  principles govern the platform, not this site widget — but its spirit
  (validated input, no secrets in logs, boring choices) applies.
- **Review happens in the database console for v1** (FR-010): NeonDB's SQL
  editor is the author's review tool; a review UI would be its own feature.
- **Anonymous by design**: no auth exists on the site and none is added; spam
  control is caps + per-visitor rate limiting, accepted as sufficient for this
  site's traffic. If abuse outgrows it, hardening is a follow-up.
- **Scope is reading content**: chapters and reference docs. The landing and
  navigation chrome are excluded (nothing there needs line-editing).
- **The database is a new external dependency**: a connection string will be
  provisioned by Dong (NeonDB) and supplied via the existing deployment's
  environment; local development uses the same mechanism (Dong provides a dev
  branch/connection or a local Postgres — the compose file in relay-platform is
  the *product's* infra, not the site's, and stays untouched).
- **Suggestions are plain text**: no rich text, no attachments.
- **Commits and deploys remain Dong's**, including the database provisioning
  and the redeploy that activates the feature.

# Feature Specification: Theme Switcher and Site Favicon

**Feature Branch**: `003-theme-switcher-favicon`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "Update the Next.js repo to support dark theme, add a theme switcher and change favicon to https://avatars.githubusercontent.com/u/19990046"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Switch the theme manually (Priority: P1)

As a tutorial reader, I can switch the site between light and dark appearance with a
visible control available on every page — instead of being locked to my operating
system's preference — so I can read long chapters in the mode that is comfortable
right now, regardless of what my OS is set to.

**Why this priority**: This is the feature's core ask. The site already *renders* a
dark palette when the OS prefers dark (established in earlier features); what readers
lack is any way to choose. A reader with a light OS who wants dark reading at night
currently has no recourse.

**Independent Test**: On any page, locate the theme control, select dark — the page
immediately renders the dark palette; select light — it renders the light palette;
select system — it follows the OS preference again.

**Acceptance Scenarios**:

1. **Given** any page of the site (landing or chapter), **When** the reader looks for
   a theme control, **Then** one is visible without scrolling, in a consistent
   location across pages.
2. **Given** the OS prefers light, **When** the reader selects dark via the control,
   **Then** the entire page — prose, boxes, navigation, landing cards — renders the
   established dark palette immediately, with no reload.
3. **Given** the reader has chosen an explicit theme, **When** they select the
   "system" option, **Then** the site follows the OS preference again, including
   live OS-level changes.
4. **Given** the control itself, **When** viewed in either mode, **Then** it is
   keyboard-operable and its current state is discernible (which mode is active).

---

### User Story 2 - The choice sticks, without flicker (Priority: P2)

As a returning reader, my chosen theme is remembered across page navigations and
browser sessions, and pages never flash the wrong theme while loading — so the choice
feels like a setting, not a per-page toggle.

**Why this priority**: A switcher that forgets, or that flashes light before painting
dark, reads as broken; but the switcher itself (US1) must exist first.

**Independent Test**: Choose dark, navigate landing → chapter → back, close and
reopen the browser — dark persists at every step with no flash of light styling on
load.

**Acceptance Scenarios**:

1. **Given** a chosen theme, **When** the reader navigates between any pages of the
   site, **Then** the choice is retained.
2. **Given** a chosen theme, **When** the reader closes the browser and returns
   later, **Then** the choice is still applied.
3. **Given** a stored dark preference, **When** any page loads fresh, **Then** no
   flash of the light palette is visible before the dark palette paints (and vice
   versa).
4. **Given** a first-time visitor with no stored choice, **When** they load the
   site, **Then** it follows the OS preference (current behavior preserved).

---

### User Story 3 - The site has its own favicon (Priority: P3)

As a reader with many tabs open, I can identify the Building Relay tutorial by its
tab icon — the project avatar image (sourced from
`https://avatars.githubusercontent.com/u/19990046`) — instead of the framework's
default icon.

**Why this priority**: Small but visible identity polish; independent of the theme
work.

**Independent Test**: Load any page; the browser tab shows the avatar-derived icon
rather than the default framework icon, in both light and dark browser chrome.

**Acceptance Scenarios**:

1. **Given** any page of the site, **When** it is open in a browser tab, **Then** the
   tab displays the avatar-derived icon.
2. **Given** the deployed site, **When** the favicon is requested, **Then** it is
   served from the site itself — rendering must not depend on a third-party host at
   page-load time.
3. **Given** the previous default icon, **When** the feature ships, **Then** no page
   references the framework-default icon any longer.

---

### Edge Cases

- What happens when the reader's stored preference exists but the control fails to
  load (e.g., scripting disabled)? The page still renders a usable default (light)
  theme — following the OS preference or a stored choice requires scripting under
  the chosen approach; the guarantee is that the site never renders unstyled or
  unreadable. (Adjusted per analysis finding E1, 2026-07-29.)
- What happens on the very first paint for a visitor whose OS is dark but who
  previously chose light? The stored choice wins, without a dark flash.
- What happens if the avatar image at the source URL changes or disappears later?
  The site is unaffected: the icon is captured into the repository at build/authoring
  time, not fetched from the third-party URL by readers' browsers.
- How does the theme control behave on a narrow viewport? It remains reachable and
  operable at the supported viewport widths without overlapping content.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The site MUST offer a theme control, visible without scrolling on every
  page in a consistent location, allowing the reader to select among **light**,
  **dark**, and **system** modes.
- **FR-002**: Selecting a mode MUST take effect immediately, without a page reload,
  and apply the established Violet Bloom palette for that mode across all existing
  surfaces (landing, chapter prose, tutorial boxes, navigation shell).
- **FR-003**: The reader's explicit choice MUST persist across page navigations and
  browser sessions on the same device/browser. With no stored choice, the site MUST
  follow the OS preference (preserving current behavior for first-time visitors).
- **FR-004**: Page loads MUST NOT flash the non-selected theme before applying the
  effective one.
- **FR-005**: The theme control MUST be operable by keyboard and MUST convey its
  active mode to assistive technology.
- **FR-006**: The site's favicon MUST be replaced with the avatar image sourced from
  `https://avatars.githubusercontent.com/u/19990046` (verified reachable, JPEG,
  ~32 KB on 2026-07-29). The image MUST be captured into the repository and served
  by the site itself — no reader-facing dependency on the third-party URL.
- **FR-007**: The framework-default icon MUST no longer be served or referenced.

### Key Entities

- **Theme preference**: The reader's selected mode — one of light, dark, or system;
  stored on the reader's device; absent for first-time visitors (treated as system).
- **Site icon**: The avatar-derived favicon asset stored in the repository and served
  with the site.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: From any page, a reader can change the theme in at most 2 interactions
  (open control → pick mode), with the new palette applied in under 1 second and no
  reload.
- **SC-002**: 100% of existing site surfaces (landing, chapter page, all six tutorial
  box types, header/footer shell) render correctly in the explicitly selected mode —
  no element remains stuck in the other palette.
- **SC-003**: A stored preference survives 100% of page navigations and a full
  browser restart, and zero wrong-theme flashes are observable on fresh loads.
- **SC-004**: The browser tab shows the new icon on 100% of the site's pages, served
  from the site's own origin.
- **SC-005**: The theme control is fully operable with keyboard alone.

## Assumptions

- "Support dark theme" is interpreted as **adding explicit user control**: dark
  rendering via OS preference already works (Violet Bloom dark tokens, features
  001/002). This feature adds the switcher, persistence, and no-flash guarantees on
  top — it does not redesign the dark palette itself.
- The control lives in a small site-wide header/toolbar area (top of page), since the
  site currently has no global header; placing it there serves every current and
  future page. Exact placement/affordance is a planning decision.
- Three-mode selection (light / dark / system) is assumed rather than a two-state
  toggle, so readers can return to following their OS — matching common practice for
  content sites.
- The avatar image is used as-is (square JPEG) converted/sized as needed for favicon
  duty; no redesign of the artwork. Capturing it into the repo is assumed authorized
  since the user directed its use.
- Preference storage is per-browser/per-device local storage; no accounts or
  cross-device sync exist or are implied.
- This feature touches only the relay-tutorial application (the established home of
  site functionality); no parent-repo content changes beyond spec artifacts and the
  eventual submodule pin.

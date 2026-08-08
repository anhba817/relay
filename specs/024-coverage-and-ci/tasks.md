# Tasks: Coverage measurement and CI

- [X] T001 Record the starting state: no coverage provider anywhere, no CI in any of the three repositories
- [X] T002 Add `@vitest/coverage-v8` and `unplugin-swc` plus a `coverage` script to `relay-platform/package.json`
- [X] T003 Create `relay-platform/vitest.coverage.config.mts` spanning both lanes, with the SWC transform the api's decorators need and the e2e journey excluded
- [X] T004 Run coverage and record the real figures, whatever they are (spec FR-004)
- [X] T005 Pin per-file ratchets for the NFR-MNT-02 files at today's measurement, with the gap to 100% documented in the config itself
- [X] T006 Prove the threshold fails the command: raise one ratchet above the measured value and confirm a non-zero exit (SC-002)
- [X] T007 Teach `check-fence-chain` about post-series amendments — applied after the last chapter, diffs only, checked as strictly as any chapter fence (spec FR-007, FR-008)
- [X] T008 Record the manifest amendment in `relay-tutorial/fences/post-series.md` with the reason no chapter owns it
- [X] T009 Prove the new mechanism verifies: change the manifest without declaring it and confirm the chain fails
- [X] T010 Write `.github/workflows/ci.yml` running the Docker-free gate, migrations, the integration lane against real stores, coverage, and the site's build plus fence and docs checks (spec FR-005, FR-006)
- [X] T011 Validate the workflow parses and its commands match the local ones one for one (SC-006)
- [X] T012 Confirm every existing suite still passes at chapter 3.3's counts (SC-005)
- [X] T013 Write `notes.md` with the measured figures, the gap, and what is still unmet

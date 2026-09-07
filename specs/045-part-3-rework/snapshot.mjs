// Dump the fence chain's state after every chapter, and again after the appendix.
//
// WHY THIS PATCHES THE CHECKER INSTEAD OF REIMPLEMENTING IT. `check-fence-chain.mjs`
// is the gate. A generator that replays differently from the gate produces output the
// gate rejects for reasons neither of them explains — so this script reads the
// checker's own source, injects two snapshot hooks, writes the patched copy beside it
// (where its `APP_ROOT` resolution still works), runs it, and deletes it. There is
// exactly one replay implementation in this repository and this is not a second one.
//
// AND IT SNAPSHOTS THE APPENDIX, WHICH THE FIRST VERSION DID NOT. `fences/post-series.md`
// applies AFTER the last chapter and amends 49 fenced paths. A tool that stops at the
// last chapter reaches a state that is not the platform's, and the omission is silent:
// analysis pass 3 saw it as 70 reference-bearing lines present in the platform file and
// in no snapshot at all, concentrated in `eslint.config.mjs` and
// `vitest.coverage.config.mts`. For the 21 order-changing paths the appendix also
// amends, the PRE-APPENDIX state is what a chapter fence must land on.
//
// Usage: node snapshot.mjs <out-dir>
//   <out-dir>/<chapter key>/<path>   state after that chapter, e.g. 3.07/services/…
//   <out-dir>/post-series/<path>     state after the appendix — the platform's own

import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(dirname(HERE));
// OVERRIDABLE, because the snapshot has to be takeable from a WORKTREE at the
// pre-rename commit. The states this dumps are `replay.mjs`'s only input, and the first
// run of this feature put them in /tmp — which a reboot then wiped, after the rename had
// already happened and `snapshot.mjs` had started refusing to run against a red chain.
// The input to a re-derivation is not scratch data.
const TUTORIAL = process.env.RELAY_TUTORIAL ?? join(ROOT, "relay-tutorial");
const CHECKER = join(TUTORIAL, "scripts", "check-fence-chain.mjs");
const PATCHED = join(TUTORIAL, "scripts", ".snapshot-generated.mjs");

const out = process.argv[2];
if (!out) {
  console.error("usage: node snapshot.mjs <out-dir>");
  process.exit(2);
}

const src = readFileSync(CHECKER, "utf8");

/** The two injection points, each asserted rather than assumed. A silent no-op here
 *  would produce an empty dump and a control that passes for the wrong reason. */
const PER_CHAPTER = "    perChapter.set(page.key, { rel, fences: list });";
const HEAD_MARKER = "// HEAD: the chain's end state must be the repository";
for (const [what, needle] of [["per-chapter hook", PER_CHAPTER], ["head marker", HEAD_MARKER]]) {
  const n = src.split(needle).length - 1;
  if (n !== 1) {
    console.error(`snapshot: ${what} matched ${n} times in check-fence-chain.mjs, need exactly 1`);
    console.error("  the checker changed shape — read it before editing this script");
    process.exit(1);
  }
}

const dump = `
    if (locale === "en") {
      for (const [title, lines] of state) {
        const dest = SNAP_JOIN(process.env.SNAPSHOT_OUT, page.key, title);
        SNAP_MKDIR(SNAP_DIRNAME(dest), { recursive: true });
        SNAP_WRITE(dest, lines.join("\\n") + "\\n");
      }
    }`;

let patched = src
  .replace(PER_CHAPTER, PER_CHAPTER + dump)
  .replace(
    'import { readdirSync, readFileSync, existsSync, statSync } from "node:fs";',
    'import { readdirSync, readFileSync, existsSync, statSync,\n' +
      '  mkdirSync as SNAP_MKDIR, writeFileSync as SNAP_WRITE } from "node:fs";\n' +
      'import { join as SNAP_JOIN, dirname as SNAP_DIRNAME } from "node:path";',
  );

// The appendix state: truncate at the HEAD comparison, which runs after the
// post-series loop, and dump `en.state` as it stands there.
patched =
  patched.slice(0, patched.indexOf(HEAD_MARKER)) +
  `
for (const [title, lines] of en.state) {
  const dest = SNAP_JOIN(process.env.SNAPSHOT_OUT, "post-series", title);
  SNAP_MKDIR(SNAP_DIRNAME(dest), { recursive: true });
  SNAP_WRITE(dest, lines.join("\\n") + "\\n");
}
console.log("snapshot: " + en.state.size + " paths after the appendix");
if (problems.length) {
  console.error("snapshot: the chain has " + problems.length + " problem(s) BEFORE any change");
  process.exit(1);
}
`;

rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });
writeFileSync(PATCHED, patched);
// `process.exit()` SKIPS `finally`, so the cleanup cannot live there. The first version
// used try/finally and left `scripts/.snapshot-generated.mjs` in the tutorial's working
// tree — a generated file that then showed up as untracked content in a submodule.
const r = spawnSync(process.execPath, [PATCHED], {
  stdio: "inherit",
  env: { ...process.env, SNAPSHOT_OUT: out },
});
rmSync(PATCHED, { force: true });

// A CAPTURE OF NOTHING IS NOT A SUCCESS, and this exited 0 on one. The checker resolves
// `relay-platform` as a SIBLING of the tutorial root and, when it is absent, prints
// "relay-platform not found — skipping" and returns 0. Run against a worktree in a
// scratch directory that produced an empty snapshot directory and a clean exit — the
// exact failure the replay would then have reported somewhere else entirely.
const keys = existsSync(out) ? readdirSync(out) : [];
if (r.status === 0 && keys.length < 2) {
  console.error(`snapshot: captured ${keys.length} key(s) — nothing to replay from.`);
  console.error("  the checker resolves relay-platform as a sibling of the tutorial root;");
  console.error("  if RELAY_TUTORIAL points into a scratch directory, put a link to");
  console.error("  relay-platform beside it or the whole run skips and still exits 0.");
  process.exit(1);
}
console.log(`snapshot: ${keys.length} keys -> ${out}`);
process.exit(r.status ?? 1);

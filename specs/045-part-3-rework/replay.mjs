// Replay each fenced path's chain onto a chapter order, by three-way merge.
//
// WHY MERGE AND NOT ATTRIBUTION. The plan first specified each chapter's state as
// "the final file minus every line owned by a later cluster". Analysis pass 2 built
// that and it produces files which do not parse — 52 errors on `repository.ts`, 59 on
// `session.ts` — because line-level ownership cuts through syntax. Cherry-picking the
// per-chapter deltas gives states derived from real states: 56 measured, 0 parse
// failures. A merge of two real files is a real file; a filtered subset of one is not.
//
// WHAT IT DOES. For one path, the snapshots are committed as a linear git history in
// published order, then cherry-picked onto an empty root in the target order. Where two
// chapters on opposite sides of a move edit the same region, git conflicts — and that
// is the honest outcome, reported by path for hand resolution, rather than a silent
// merge onto a file nobody asked for.
//
// THE TARGET IS NOT ALWAYS THE PLATFORM FILE. `fences/post-series.md` applies after the
// last chapter and amends 49 paths. For those, the chapter chain must land on the
// PRE-APPENDIX state; the appendix then amends it to the platform's. Comparing against
// the platform file would overshoot by exactly the appendix's hunks and report the
// failure in the wrong place.
//
// Usage:
//   node replay.mjs --order current [--out DIR]     the control: must reproduce today
//   node replay.mjs --order new     [--out DIR]     the reorder
//   node replay.mjs --order new --typecheck-each    also compile every state

import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(dirname(HERE));
const TUTORIAL = join(ROOT, "relay-tutorial");
const argv = process.argv.slice(2);
const arg = (name, fallback) => {
  const i = argv.indexOf(name);
  return i === -1 ? fallback : argv[i + 1];
};
const ORDER = arg("--order", "current");
const SNAP = arg("--snapshots", join(tmpdir(), "relay-045-snapshots"));
const OUT = arg("--out", null);
const TYPECHECK = argv.includes("--typecheck-each");
const CONFLICT_OUT = arg("--conflict-out", null);
/** Run the merge even where the order did not change.
 *
 * WITHOUT THIS THE CONTROL PROVES NOTHING. `--order current` leaves every path's
 * chapter sequence untouched, so all 242 take the fast path below and the control
 * compares snapshots against copies of themselves — 5,020 green states and zero lines
 * of merge machinery exercised. Forcing the replay makes `--order current` a real test
 * of the mechanism: cherry-picking a history onto itself must reproduce it exactly. */
const FORCE = argv.includes("--force-replay");

if (!existsSync(SNAP)) {
  console.error(`replay: no snapshots at ${SNAP} — run snapshot.mjs first`);
  process.exit(2);
}

/** Published chapter order.
 *
 * READ FROM THE SNAPSHOT, NOT FROM THE TREE, once the tree has been renamed. This walked
 * `app/(en)` for `page.mdx` and derived the order from the directory names, which is
 * correct only while those names still carry the OLD ordinals. After T019 the tree holds
 * 1..25 in the new arrangement, so `--order new` compared the new order against itself
 * and found nothing to replay.
 *
 * The snapshot's own keys are the published order at capture time — that is what a
 * snapshot IS — so they are the honest source and they keep this tool usable on either
 * side of the rename. The tree walk stays as the fallback for a snapshot that predates
 * the per-key layout.
 */
function publishedOrder() {
  const keys = existsSync(SNAP)
    ? spawnSync("ls", [SNAP], { encoding: "utf8" }).stdout.split("\n")
        .filter((k) => /^\d+\.\d+$/.test(k.trim()))
        .map((k) => k.trim())
    : [];
  if (keys.length > 1) {
    return keys.sort((a, b) => {
      const [ap, ac] = a.split(".").map(Number);
      const [bp, bc] = b.split(".").map(Number);
      return ap * 1000 + ac - (bp * 1000 + bc);
    });
  }
  return publishedOrderFromTree();
}

function publishedOrderFromTree() {
  const walk = (d) =>
    existsSync(d)
      ? spawnSync("find", [d, "-name", "page.mdx"], { encoding: "utf8" }).stdout
          .split("\n")
          .filter(Boolean)
      : [];
  const keys = [];
  for (const p of walk(join(TUTORIAL, "app/(en)"))) {
    const m = /part-(\d+)\/chapter-(\d+)\//.exec(p);
    if (m) keys.push({ key: `${m[1]}.${m[2]}`, rank: +m[1] * 1000 + +m[2] });
  }
  return [...new Set(keys.sort((a, b) => a.rank - b.rank).map((k) => k.key))];
}

/** The target order. `current` needs no map, which is what makes the control runnable
 *  before anything else exists. */
function targetOrder(published) {
  if (ORDER === "current") return published;
  const mapFile = join(HERE, "chapter-map.json");
  if (!existsSync(mapFile)) {
    console.error("replay: --order new needs chapter-map.json (T007)");
    process.exit(2);
  }
  const map = JSON.parse(readFileSync(mapFile, "utf8"));
  const part3 = map.chapters
    .slice()
    .sort((a, b) => a.new - b.new)
    .map((c) => `3.${String(c.old).padStart(2, "0")}`);
  const before = published.filter((k) => Number(k) < 3);
  const after = published.filter((k) => Number(k) >= 4);
  return [...before, ...part3, ...after];
}

const published = publishedOrder();
const target = targetOrder(published);
const rankOf = new Map(target.map((k, i) => [k, i]));

/** Every path the chain touches, with the chapters that actually CHANGE it.
 *
 * PRESENT IS NOT THE SAME AS FENCED BY, and the first version of this function
 * conflated them. `snapshot.mjs` dumps the whole chain state after every chapter, so a
 * path appears in every chapter directory from its introduction onward — including the
 * chapters that never touch it. Recording all of those produced empty commits, and
 * `git cherry-pick` refuses an empty commit: the forced control came back with a
 * conflict on almost every path, at chapters as early as 1.04.
 *
 * A key counts only where its snapshot differs from the previous key's. */
function chainPaths() {
  const out = new Map();
  const last = new Map();
  for (const key of published) {
    const dir = join(SNAP, key);
    if (!existsSync(dir)) continue;
    for (const f of spawnSync("find", [dir, "-type", "f"], { encoding: "utf8" }).stdout
      .split("\n")
      .filter(Boolean)) {
      const rel = relative(dir, f);
      const text = readFileSync(f, "utf8");
      if (last.get(rel) === text) continue;
      last.set(rel, text);
      if (!out.has(rel)) out.set(rel, []);
      out.get(rel).push(key);
    }
  }
  return out;
}

const git = (args, cwd) => spawnSync("git", args, { cwd, encoding: "utf8" });

/** The paths the appendix amends. For these the chapter chain must land on the
 *  PRE-APPENDIX state and the snapshot is the only target available. For every other
 *  path the target is the platform file itself — an INDEPENDENT one. */
function appendixPaths() {
  const md = readFileSync(join(TUTORIAL, "fences", "post-series.md"), "utf8");
  const out = new Set();
  for (const m of md.matchAll(/^```\w+ title="([^"]+)"/gm)) {
    const t = m[1];
    if (t.includes("(excerpt)") || t.includes(".naive.")) continue;
    out.add(t.split(/,| before | \(deleted\)/)[0].trim());
  }
  return out;
}
const AMENDED = appendixPaths();

const paths = chainPaths();
let unchanged = 0;
const conflicts = [];
const drift = [];
const driftAmended = [];
let states = 0;

for (const [path, chapters] of [...paths].sort()) {
  const inPublished = chapters.slice().sort((a, b) => published.indexOf(a) - published.indexOf(b));
  const inTarget = chapters
    .slice()
    .filter((c) => rankOf.has(c))
    .sort((a, b) => rankOf.get(a) - rankOf.get(b));
  if (inPublished.join() === inTarget.join() && !FORCE) {
    unchanged++;
    if (OUT) {
      for (const key of inPublished) {
        const dest = join(OUT, key, path);
        mkdirSync(dirname(dest), { recursive: true });
        writeFileSync(dest, readFileSync(join(SNAP, key, path)));
        states++;
      }
    }
    continue;
  }

  const repo = mkdtempSync(join(tmpdir(), "relay-045-"));
  try {
    git(["init", "-q", "-b", "m"], repo);
    git(["config", "user.email", "replay@local"], repo);
    git(["config", "user.name", "replay"], repo);
    const file = join(repo, "F");
    writeFileSync(file, "");
    git(["add", "F"], repo);
    git(["commit", "-qm", "base"], repo);
    const root = git(["rev-parse", "HEAD"], repo).stdout.trim();
    const sha = new Map();
    for (const key of inPublished) {
      writeFileSync(file, readFileSync(join(SNAP, key, path)));
      git(["add", "F"], repo);
      git(["commit", "-qm", key, "--allow-empty"], repo);
      sha.set(key, git(["rev-parse", "HEAD"], repo).stdout.trim());
    }
    git(["checkout", "-q", "-b", "new", root], repo);
    let ok = true;
    const produced = [];
    for (const key of inTarget) {
      const r = git(["cherry-pick", "-X", "patience", sha.get(key)], repo);
      if (r.status !== 0) {
        conflicts.push({ path, at: key });
        // PRESERVE THE CONFLICT SO IT CAN BE RESOLVED. Aborting and moving on gives a
        // count and nothing to work with; 32 paths cannot be resolved from a list of
        // names. Written out as the marked-up file plus the three inputs a three-way
        // merge actually has, because "pick a side" is rarely the answer and the base
        // is what says which side introduced what.
        if (CONFLICT_OUT) {
          const dir = join(CONFLICT_OUT, path.replace(/\//g, "__"));
          mkdirSync(dir, { recursive: true });
          writeFileSync(join(dir, "MARKED"), readFileSync(file, "utf8"));
          for (const [name, spec] of [["base", ":1:F"], ["ours", ":2:F"], ["theirs", ":3:F"]]) {
            const g = spawnSync("git", ["show", spec], { cwd: repo, encoding: "utf8" });
            if (g.status === 0) writeFileSync(join(dir, name), g.stdout);
          }
          writeFileSync(join(dir, "META.json"), JSON.stringify(
            { path, conflictAt: key, publishedOrder: inPublished, targetOrder: inTarget }, null, 2));
        }
        git(["cherry-pick", "--abort"], repo);
        ok = false;
        break;
      }
      produced.push([key, readFileSync(file, "utf8")]);
    }
    if (!ok) continue;

    // THE TARGET MUST BE INDEPENDENT OF THE INPUT, or the control tests nothing.
    //
    // This compared against `SNAP/<last chapter>/<path>` — replay's own input — so a
    // corrupted snapshot was reproduced faithfully and the comparison passed. T005
    // proved it: perturbing a fence body, truncating a state and deleting the appendix
    // snapshot all left the control green.
    //
    // For a path the appendix does NOT amend, the state after the last chapter IS the
    // platform file, so the platform is the independent target. For the 49 it does
    // amend, the chapter chain must stop short of the platform and the snapshot is the
    // only target there is — those are reported separately rather than silently trusted.
    const platform = join(ROOT, "relay-platform", path);
    const independent = !AMENDED.has(path) && existsSync(platform);
    const want = (independent
      ? readFileSync(platform, "utf8")
      : readFileSync(join(SNAP, inPublished.at(-1), path), "utf8")
    ).replace(/\n$/, "");
    const got = (produced.at(-1)?.[1] ?? "").replace(/\n$/, "");
    if (got !== want) (independent ? drift : driftAmended).push(path);

    if (OUT) {
      for (const [key, text] of produced) {
        const dest = join(OUT, key, path);
        mkdirSync(dirname(dest), { recursive: true });
        writeFileSync(dest, text);
        states++;
      }
    }
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
}

console.log(`replay: order=${ORDER}${FORCE ? " (merge forced — the control)" : ""}`);
console.log(`  paths                        ${paths.size}`);
console.log(`  chain order unchanged        ${unchanged}`);
console.log(`  replayed                     ${paths.size - unchanged}`);
console.log(`  CONFLICTS (hand resolution)  ${conflicts.length}`);
console.log(`  landed on a different file   ${drift.length}   (target: the platform file)`);
console.log(`  appendix-amended mismatches  ${driftAmended.length}   (target: the pre-appendix snapshot, ${AMENDED.size} paths)`);
if (OUT) console.log(`  states written               ${states} -> ${OUT}`);
for (const c of conflicts.slice(0, 40)) console.log(`    conflict at ${c.at}  ${c.path}`);
for (const d of drift.slice(0, 40)) console.log(`    DRIFT  ${d}`);
for (const d of driftAmended.slice(0, 20)) console.log(`    DRIFT (appendix-amended)  ${d}`);

if (TYPECHECK) {
  console.log("  --typecheck-each is T026's, and needs the states on disk (--out)");
}
process.exit(conflicts.length || drift.length || driftAmended.length ? 1 : 0);

// The chain re-derived WITHOUT MERGING: re-sort the snapshots and take a running maximum.
//
// WHY THIS EXISTS. Three-way merge left 29 conflicts, 8 of them not merge problems at all
// — a file whose creating chapter now comes later, where `ours` is 0 lines and no choice
// of side helps. And the obvious repair, folding the dropped editors' work into the
// creator, is wrong for a different reason: `vitest.coverage.config.mts` has its creator
// at new 19 with editors dropped from new 7-18, and the chapters that FOLLOW at new 20-24
// carry LOWER old ranks, so applying their deltas after the fold would take content back
// out.
//
// THE RULE. At new position i the state is the old snapshot of the highest-old-ranked
// chapter among the positions up to and including i. Monotone, so nothing is ever
// removed; every state is a real snapshot rather than a synthesis, so nothing fails to
// parse the way attribution-and-filter did (52 errors on repository.ts, 59 on session.ts);
// and the last position always includes the highest old chapter, so the chain lands on the
// platform file by construction rather than by luck.
//
// IT CANNOT CONFLICT, because it never merges. What it costs instead is fences: a chapter
// whose old state is not the running maximum contributes nothing to that path and loses
// its fence. That count is the price and it is what this prints.
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(dirname(HERE));
const argv = process.argv.slice(2);
const arg = (n, d) => { const i = argv.indexOf(n); return i === -1 ? d : argv[i + 1]; };
const SNAP = arg("--snapshots", join(HERE, ".snapshots"));
const OUT = arg("--out", null);

const MAP = JSON.parse(readFileSync(join(HERE, "chapter-map.json"), "utf8"));
const SPLITS = new Map((MAP.splits ?? []).map((s) => [`3.${String(s.old).padStart(2, "0")}`, s]));

const keys = readdirSync(SNAP).filter((k) => /^\d+\.\d+$/.test(k))
  .sort((a, b) => { const [ap, ac] = a.split(".").map(Number), [bp, bc] = b.split(".").map(Number);
                    return ap * 1000 + ac - (bp * 1000 + bc); });
const oldRank = new Map(keys.map((k, i) => [k, i]));

// new position, per (chapter, path) — a split chapter's halves sit at two positions
const slots = MAP.chapters.slice().sort((a, b) => a.new - b.new);
const newPos = new Map();
let p = 0;
for (const k of keys.filter((k) => Number(k) < 3)) newPos.set(k, p++);
const part3Base = p;
slots.forEach((c, i) => newPos.set(`3.${String(c.old).padStart(2, "0")}|${c.slug}`, part3Base + i));
p = part3Base + slots.length;
for (const k of keys.filter((k) => Number(k) >= 4)) newPos.set(k, p++);

function posFor(key, path) {
  const sp = SPLITS.get(key);
  if (sp) {
    for (const h of sp.halves) if ((h.paths ?? []).includes(path)) return newPos.get(`${key}|${h.slug}`);
    return newPos.get(`${key}|${sp.halves[0].slug}`);
  }
  const direct = slots.find((s) => `3.${String(s.old).padStart(2, "0")}` === key);
  if (direct) return newPos.get(`${key}|${direct.slug}`);
  return newPos.get(key);
}

/** Every path, with the chapters that actually change it. */
const paths = new Map();
{
  const last = new Map();
  for (const key of keys) {
    const dir = join(SNAP, key);
    if (!existsSync(dir)) continue;
    for (const f of spawnSync("find", [dir, "-type", "f"], { encoding: "utf8" }).stdout.split("\n").filter(Boolean)) {
      const rel = relative(dir, f);
      const text = readFileSync(f, "utf8");
      if (last.get(rel) === text) continue;
      last.set(rel, text);
      if (!paths.has(rel)) paths.set(rel, []);
      paths.get(rel).push(key);
    }
  }
}

let dropped = 0, kept = 0, unchanged = 0, wrongEnd = [], states = 0;
const perChapterLoss = new Map();
for (const [path, chapters] of [...paths].sort()) {
  const inPublished = chapters.slice().sort((a, b) => oldRank.get(a) - oldRank.get(b));
  const inTarget = chapters.slice().sort((a, b) => posFor(a, path) - posFor(b, path));
  if (inPublished.join() === inTarget.join()) { unchanged++; kept += chapters.length; continue; }

  let max = null;
  const emit = [];
  for (const key of inTarget) {
    if (max === null || oldRank.get(key) > oldRank.get(max)) { max = key; emit.push([key, max]); }
    else { dropped++; perChapterLoss.set(key, (perChapterLoss.get(key) ?? 0) + 1); }
  }
  kept += emit.length;
  const endState = readFileSync(join(SNAP, emit.at(-1)[1], path), "utf8");
  const want = readFileSync(join(SNAP, inPublished.at(-1), path), "utf8");
  if (endState !== want) wrongEnd.push(path);
  if (OUT) for (const [key, src] of emit) {
    const dest = join(OUT, key, path);
    mkdirSync(dirname(dest), { recursive: true });
    writeFileSync(dest, readFileSync(join(SNAP, src, path)));
    states++;
  }
}
console.log("runmax: no merge, so no conflicts by construction");
console.log(`  paths                        ${paths.size}`);
console.log(`  chain order unchanged        ${unchanged}`);
console.log(`  fences KEPT                  ${kept}`);
console.log(`  fences DROPPED               ${dropped}   <- the price of this mechanism`);
console.log(`  paths not landing on the end ${wrongEnd.length}`);
for (const w of wrongEnd.slice(0, 10)) console.log(`    WRONG END  ${w}`);
if (OUT) console.log(`  states written               ${states} -> ${OUT}`);
console.log("  fences lost per chapter (old ordinal):");
for (const [k, v] of [...perChapterLoss].sort((a, b) => b[1] - a[1]).slice(0, 14))
  console.log(`    ${k}  loses ${v}`);
process.exit(wrongEnd.length ? 1 : 0);

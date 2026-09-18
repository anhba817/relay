# Quickstart — verifying the fence-chain repair

Every command below was run while this plan was written, except the four marked **after the
repair**, which are what the close is measured by. Chapter 4.2's quickstart carried a command
`corpus.mjs` refuses through five analysis passes because nobody ran it; these were run.

No store, no broker, no Docker. The whole feature is text.

---

## 1. The opening count, and its four classes

```bash
cd relay-tutorial
pnpm check:fences                 # exits 1 today
```

Expected, 2026-09-17:

```
check-fence-chain: 110 problem(s) — APPLY 74, HEAD 36
```

Classify them — this is the number every phase is measured against:

```bash
pnpm check:fences 2>&1 | grep -A1 '^\[' | grep -c 'matched 0 times'                # 42
pnpm check:fences 2>&1 | grep -A1 '^\[' | grep -c 'no earlier fence to amend'      # 32
pnpm check:fences 2>&1 | grep -A1 '^\[' | grep -c 'differs at line'                # 25
pnpm check:fences 2>&1 | grep -A1 '^\[' | grep -c 'does not exist in relay-platform' # 11
```

**Re-measure rather than trusting these** (FR-013). The chain moves whenever a chapter or the
platform does, and two published figures for it already disagree (R6).

## 2. Where they are

```bash
pnpm check:fences 2>&1 | grep -E '^\[(APPLY|HEAD)\]' \
  | sed -E 's/^\[(APPLY|HEAD)\] ([^:]+):.*/\1 \2/' \
  | awk '{print $1, ($2 ~ /\(en\)/ ? "en" : $2 ~ /\(vi\)/ ? "vi" : $2)}' \
  | sort | uniq -c
```

Expected: `36 HEAD en · 30 APPLY en · 30 APPLY vi · 14 APPLY fences/post-series.md`. **All 110
are in `relay-tutorial`**; `relay-platform` is the reference, never the subject.

## 3. The replayed state — the thing hunks must be written against

**After phase 1**, the checker takes a dump flag:

```bash
pnpm check:fences --dump /tmp/chainstate
find /tmp/chainstate -type f | wc -l                    # 285 before phase 3, 274 after
diff /tmp/chainstate/vitest.coverage.config.mts ../relay-platform/vitest.coverage.config.mts | wc -l
```

**And the state at a chapter, which is a different state:**

```bash
pnpm check:fences --dump /tmp/at322 --at 'app/(en)/part-3/chapter-22/limits-you-can-see-coming/page.mdx'
wc -l < /tmp/at322/turbo.json                           # 62
wc -l < /tmp/chainstate/turbo.json                      # 74
```

**And the Vietnamese chain, which is the same command with the locale in the page path:**

```bash
pnpm check:fences --dump /tmp/at322vi --at 'app/(vi)/vi/part-3/chapter-22/limits-you-can-see-coming/page.mdx'
diff /tmp/at322/turbo.json /tmp/at322vi/turbo.json      # no output — 62 lines both sides at 3.22
ls /tmp/at322vi/services/api/src/metering/reconcile.ts  # No such file — chained in en 4.9 only
```

**There is no `--locale` flag: the page path is the locale**, so the argument copied off a problem
line names its own chain. **A bare `--dump` writes the English one**, because that is the only
final state the checker builds — the appendix loop mutates `en.state` and `replay("vi", …)` runs
after it. The two ends differ: **9 paths, and `turbo.json` at en 75 against vi 62.** At the
chapters this feature repairs they agree, which is what makes FR-011's regenerate-in-en-copy-to-vi
rule safe on evidence rather than on the inference from `MIRROR` being 0.

**Twelve lines apart, and that is the whole reason the flag has two modes.** A hunk for a chapter
must be generated against the first number; one for the appendix or for a HEAD divergence against
the second. Measured chapter by chapter, `turbo.json` goes 28 → 59 → 62 → 74, and the tree holds
75. **Using the wrong mode produces a hunk that fails exactly like the one it replaces.**

**No `--` before the flag.** Measured on this pnpm: `pnpm check:fences -- --dump X` forwards
**`-- --dump X`**, so a stray `--` reaches the script; without it the arguments arrive clean. The
flag parser tolerates both, and the published form is the one that sends what it means.

The state is 318 lines where the tree holds 1,182, and **it contains no `env` block** — which is
why nine appendix hunks anchored inside one cannot apply, and why a hunk generated with
`git diff` against the tree will be rejected.

Prove the dump is the same replay the check uses:

```bash
pnpm check:fences --dump /tmp/a && pnpm check:fences --dump /tmp/b && diff -r /tmp/a /tmp/b
pnpm check:fences 2>&1 | grep 'problem(s)'               # same count with the flag as without
```

## 4. Historical content for a missing introduction

```bash
cd ../relay-platform
git show rework/part3-ch3:services/gateway/src/session.itest.ts | wc -l     # 287
wc -l < services/gateway/src/session.itest.ts                                # 1626
```

**The first number is the one that goes in chapter 3.3.** The second is the file twenty chapters
later, and publishing it there would show a reader future code and leave five later hunks
anchored on the wrong bytes.

## 5. The loop, run after every target

```bash
cd ../relay-tutorial
pnpm check:fences 2>&1 | grep 'problem(s)\|replay onto'
```

**Not `| tail -1`.** The problem lines and the summary are written to **stderr**, and above zero
`pnpm` exits 1 and appends `ELIFECYCLE Command failed with exit code 1.` — so `| tail -1` shows
that and `2>&1 | tail -1` shows it too. The `grep` matches the count line while there are
problems and the success line once there are none, which is the whole range this loop runs over.

A repair that lowers the count by fewer problems than the target holds means some were shadows of
a different root. **A repair that raises it means something downstream was unanchored** — feature
045 measured one regeneration taking the chain from 111 to 203 — and is reverted or finished
inside that target, with both numbers recorded.

## 6. **After the repair** — the four things the close is measured by

```bash
pnpm check:fences 2>&1 | grep 'replay onto'
# check-fence-chain: 283 fenced files replay onto relay-platform across 52 chapters
#                    (46 translated, fences mirrored, 2 retired, plus post-series amendments)
```

**283, and 52 is not 47.** `app/(en)` carries a **`part-0` of five chapters** with **zero titled
fences** in either locale, so the chapter count is pages the walker found rather than pages
verified. The number that means something is the 283: 285 today, minus 11 declared in phase 3,
plus 9 introduced in phase 5.

**Read the line, not the exit code**, and note the guard is in **two** places.
`scripts/check-fence-chain.sh:10-13` prints `relay-platform not found — skipping fence check`;
`scripts/check-fence-chain.mjs:198-201` prints `relay-platform not found — skipping`. Both
**exit 0** when the platform repository is absent, so a standalone clone — or a copy of the
checker run from anywhere else, since the path comes from the script's own location — satisfies
"exit 0" having replayed nothing. The three-word difference is how you tell which one fired. The success line above is printed
only when the problem count is 0, which makes it the one output that tells a repaired chain from
an unread one.

Plant a regression and confirm the gate still works — **run red rather than reasoned about**.
**The target must be a file whose chain is clean**, because the checker reports the first failure
per file: `packages/protocol/src/codes.ts` is a HEAD problem until phase 6 repairs it, so this
probe changes nothing if it is run before the repair. After the repair every file qualifies.

```bash
cd ../relay-platform
sed -i '1s/^/\/\/ planted\n/' packages/protocol/src/codes.ts
cd ../relay-tutorial && pnpm check:fences 2>&1 | grep -A2 'codes.ts'   # non-zero, naming it
cd ../relay-platform && git checkout -- packages/protocol/src/codes.ts
```

Confirm no platform file was edited by the feature itself:

```bash
cd relay-platform && git diff --stat part4-ch9            # empty
```

And confirm the unread population did not grow:

```bash
cd ../relay-tutorial
grep -rhoE '^```[a-z]*( title="[^"]*")?' app/\(en\) app/\(vi\) fences/post-series.md \
  | grep -cv 'title='                                     # untitled fences: 360 before
grep -rhoE 'title="[^"]*"' app/\(en\) app/\(vi\) fences/post-series.md \
  | grep -c '(excerpt)'                                   # declared not-files: 222 before, 244 after
```

Measured 2026-09-17, before any repair: **2,109 opening fences · 1,749 titled · 360 with a
language and no title · 222 titles already carrying `(excerpt)`**. After the repair the untitled
count is unchanged at 360 and the declared count is **244** — **+22, not +11**, because the
eleven prose titles occur once in `app/(en)` and once in `app/(vi)` and phase 3 declares the
pair. Every figure on this line spans both locales: 1,071 en · 1,005 vi · 33 appendix, and the
222 is 111 and 111. **Nothing that names a real file becomes
unverified**, which is the property SC-008 is about — and `gaps.md` 043-1's *"146 of 904"* is a
2026-08 figure that this feature re-measures rather than repeats.

## 7. The gates around it

```bash
cd relay-tutorial
pnpm lint && pnpm build && pnpm check:docs && pnpm check:srs && pnpm check:figures && pnpm check:errors
```

`pnpm build` is in the list because a chapter edit can break the page it lives in, and the
tutorial did not build for a whole chapter once without anybody noticing (050).

**`check:errors` reads the built `dist`** — build `relay-platform` before believing it.

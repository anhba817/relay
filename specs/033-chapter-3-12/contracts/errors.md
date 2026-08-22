# Contract — the error vocabulary and its documentation

Constitution V: *"Every error response carries a machine-readable `code`, a
human-readable `message`, a `docs_url`, and the `request_id`; every error code has a
reachable documentation page."* The first half has shipped since chapter 3.8. The
second half has never been true.

## 1. The set, and why it had to be constructed

Eleven codes, from four sources, and no single place lists them:

```
registry (packages/protocol/src/codes.ts)   6   invalid_frame unknown_frame_type
                                                unauthorized rate_limited
                                                wrong_credential_type quota_exceeded
status ladder (protocol-error.filter.ts)    5   invalid_request unauthorized
                                                forbidden not_found internal_error
service-kit's 404                           1   not_found
named at a call site (usage.controller.ts)  1   connection_environment_conflict
                                            ──
union                                       11
```

**The registry is not the set**, and that is the finding this contract exists because of.
`codes.ts` calls itself "a starter registry — endpoints and services add their own codes
in their chapters", and five of them were added as string literals in a ternary instead.
`codes.test.ts` enforces uniqueness and snake_case over the six it can see.

**After this chapter the registry is the set by construction**: the five missing keys are
added, the ladder is typed `ErrorCode`, and the call sites reference the registry. An
unregistered code stops compiling. `Object.keys(ERROR_CODES)` is then a derivation
rather than a hope, which is what FR-025 needs and what no grep over source could
safely provide.

## 2. The URL

```
docs_url = <docs base> + "#" + code
```

One function, beside the registry. Six construction sites collapse into it:

| Site | Today |
|---|---|
| `services/api/src/protocol-error.filter.ts:73` | `` `https://relay.example/docs/errors/${code}` `` |
| `services/api/src/limits/rate-limit.middleware.ts:122` | literal `rate_limited` |
| `services/api/src/limits/rate-limit.middleware.ts:220` | literal `rate_limited` |
| `packages/service-kit/src/index.ts:85` | literal `not_found` |
| `services/gateway/src/session.ts:72` | literal `rate_limited` |
| `services/gateway/src/session.ts:103` | `` `…/errors/${code}` `` |

**`service-kit` is the awkward one and it resolves without a dependency.** The package
declares no dependencies at all — not even `@relay/protocol` — and `serve()` has exactly
one caller (`services/gateway/src/main.ts`). So `ServeOptions` gains a required field
carrying the not-found URL, the compiler makes the one caller supply it, and the package
stays empty. The alternative — duplicating the base with a test that reads the other file
and fails on divergence, as `db-url.test.ts` and `bait-size.test.ts` do — is the house
pattern for a duplicated *constant* and this would be a duplicated *function*.

**The base is configurable with a published default.** `RELAY_DOCS_BASE_URL` falls back
to the published reference's URL — and the variable has to be declared in `turbo.json`'s
`test:integration` env list, because turbo's strict env mode filters what it does not
declare and an undeclared variable leaves the test silently exercising the default. A placeholder host is what got the project here; a
configurable value with a real default is honest today and correct when the product has
its own domain.

## 3. The anchor, and the one character that makes it work

The site gives heading anchors to `h2` only, through `slugifyHeading`:

```ts
.replace(/[^\p{L}\p{N}]+/gu, "-")
```

An underscore is neither a letter nor a number, so `## quota_exceeded` becomes
`#quota-exceeded` — and `docs_url` would have to apply the same transform from a
different repository, with no test able to see both sides. Preserving underscores
removes the rule entirely.

**Blast radius, measured rather than assumed** (the same function ids every `h2` in 28
published chapters through `mdx-components.tsx`):

```
chapter h2 headings containing an underscore          0
docs h2 headings containing an underscore             1
   ## ADR-03 — Per-channel sequences via `last_sequence` row lock
links anywhere in the site to /docs/<slug>#anchor     0
```

One anchor changes, nothing links to it. Each code is an `h2`, so `h3` needs no id.

## 4. The reference document

`docs/08-error-reference.md`, one `h2` per code, each with meaning, cause and remedy.
Published at `/docs/error-reference` and `/vi/docs/error-reference` by the renderer
feature 009 built.

**Three lists must agree**, and the trap is that two of them are shell globs:

| List | Today | Change |
|---|---|---|
| `relay-tutorial/scripts/sync-docs.sh` | `docs/0[1-6]-*.md` | an explicit file list |
| `relay-tutorial/scripts/check-docs-drift.sh` | `content/docs/0[1-6]-*.md` | the same list |
| `relay-tutorial/lib/docs.ts` | six `DocEntry` records | a seventh |

The range stops at 6 on purpose — `docs/07-tutorial-plan.md` is not a published
reference — so widening it to `0[1-8]` would publish the tutorial plan. An explicit list
is feature 030's doctrine arriving in a shell script: whatever silently absorbs the next
case is the thing to remove.

**The failure mode if they disagree**: a document in the registry and not in the sync
list renders whatever `content/docs/` last held, and `check-docs-drift.sh` does not
notice, because it only walks files its own glob selects. A stale page that no check
sees is worse than a missing one.

**Two things need no work, measured.** `doc-page.tsx` renders its "referenced by" line
under `citing.length > 0 &&`, so a document no chapter cites renders cleanly — and no
chapter cites this one. The Vietnamese route renders the same English source under a
translated title with a standing note saying so, so the reference needs a `titleVi` and
no translation.

## 5. Completeness, both directions

```
platform side (packages/protocol/src/codes.test.ts)
  assert every code the platform can emit is in ERROR_CODES        // self-contained

tutorial side (relay-tutorial/scripts/)
  codes   = Object.keys(ERROR_CODES)                    // eleven
  anchors = h2 headings in docs/08-error-reference.md   // eleven
  assert setEqual(codes, anchors)
```

**Split along the repository boundary, and measured rather than chosen for tidiness.**
`docs/` sits above `$TURBO_ROOT$`, so it cannot be a turbo input — the platform's `test`
task would return a cache hit after the reference changed and pass stale. And
`relay-platform` is independently clonable with a README promising its checks pass from a
clean checkout, where `../docs` does not exist. The tutorial repo already reaches into the
parent and skips with a warning when it is absent, which is `check-docs-drift.sh`'s
existing shape (R26).

A code with no entry fails. **An entry naming a code that cannot be emitted also
fails** — the second direction matters, because a reference that documents a code the
platform retired is how a documentation set starts lying.

And one assertion against the published site rather than a string: fetch the `docs_url`
off a live error response and confirm the anchor is present in the returned HTML. A URL
that matches a pattern is not a URL that resolves.

## 6. What this does not deliver

- **Not an API reference.** NFR-USE-04 wants the complete API documented and EIR-API-07
  wants OpenAPI 3.1; both are P4 and neither is here. This is the error vocabulary only.
- **Not a docs site.** The tutorial plan's line stands — "a docs site is not a chapter of
  this series". This is a seventh source document on a surface that already publishes
  six.
- **Not NFR-USE-06.** Reconnection, ordering, idempotency and rate-limit behaviour
  documented explicitly is a separate requirement, and the chapters teach those rather
  than a reference stating them.
- **Not proof the entries are good.** The test proves every code has an entry. Whether
  the entry helps is what a reader decides, and §5's set comparison cannot tell.

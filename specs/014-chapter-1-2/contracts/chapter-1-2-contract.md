# Contract: Chapter 1.2 — One Command, Whole World

The externally observable promises this feature makes. Verification steps in
[quickstart.md](../quickstart.md); C-numbers referenced from tasks.

## C1 — Pages exist and render

- `GET /part-1/chapter-02/one-command-whole-world` and
  `GET /vi/part-1/chapter-02/one-command-whole-world` prerender (build-time)
  with the full reading shell: header source-doc links, sidebars, on-this-page
  rail, footers, code-block titles + copy buttons, zoomable figures.
- Both pages carry canonical/hreflang alternates, OG metadata, and TechArticle
  JSON-LD via the established shell (no page-level SEO code).

## C2 — Battery (per locale)

| Check | Bound |
|---|---|
| Canonical words (prose outside fences) | 2,000 ≤ w ≤ 4,000 |
| WHY | ≥ 2 |
| TRAP | ≥ 1 |
| SKIP AHEAD | = 1, names `part1-ch2` |
| FORWARD REF | ≥ 1 (MinIO + seeded tenant land here) |
| CHECKPOINT | = 1, closing |
| Figures | 2–4, all captioned |
| Baseline | 14 rows total; 12 prior rows byte-identical to 013's baseline |

## C3 — Fence ↔ repository (the no-drift promise)

- Every file-content fence (en AND vi) byte-matches the named relay-platform
  file at HEAD (Dong's tag `part1-ch2` then pins it): `compose.yaml`,
  `packages/config/src/infra.ts`, `packages/config/src/infra.test.ts`.
- Every fence carries `title="<repo path>"` per the established convention.
- **Additive-only**: no file fenced by chapter 1.1 is modified; 1.1's ten file
  fences still byte-match at the same state.
- en/vi fence lists are index-aligned and byte-identical.
- Command fences replay cleanly: `docker compose up -d --wait` exits 0;
  `docker compose ps` shows 4× healthy; `docker compose down` clean.

## C4 — The gate (relay-platform)

- `pnpm install && pnpm lint && pnpm typecheck && pnpm test` all pass **with
  the Docker daemon stopped**.
- `pnpm test` includes `infra.test.ts` assertions: 4 service names, ≥4
  healthchecks, 3 durable volumes present, `redis-data` absent.
- With Docker: `up -d --wait` reaches healthy for all four stores on default
  ports; `down` (volumes kept) and `down -v` (reset) behave as the chapter
  states.

## C5 — Navigation & publishing (manifest-only)

- The ONLY tutorial-side source edit outside the two new chapter directories is
  the 1.2 manifest entry flip in `lib/tutorial.ts`.
- After the flip: 1.1's footers (both locales) gain the 1.2 next card; 1.2's
  footers link back to 1.1 and show no next link; sidebar Part 1 = exactly 2
  linked + 2 forthcoming; both landings list 1.2 as linked; sitemap = exactly
  28 URLs (the two new pages added, nothing else changed).

## C6 — Factual fidelity

- Quoted decision content (NFR-MNT-03's sentence, ADR phrases such as "a
  fraction of Kafka's operational mass", "the correct amount of durability …
  is none") is verbatim per the established definition, spot-checked against
  docs/04/05/06.
- The invented-ID detector passes over both page.mdx and both figures.ts
  (ADR/driver/FR/NFR/CON IDs all exist in the source docs).

## C7 — Vietnamese parity & register

- Box/figure/fence counts match en exactly; fences byte-identical.
- Register per the settled glossary: "cửa ải" (+"vượt qua"), "package" (never
  "gói"), "quả ngọt", "bản giao kèo", "tin nhắn"; dev terms English; no
  structural calques; naturalization self-review done before presenting.
- Dong's read-through precedes the commit (handoff item, not a build gate).

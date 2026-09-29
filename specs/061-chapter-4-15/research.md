# Phase 0 research — Chapter 4.15, "What a thumbnail costs"

Eight questions. R1 is the one the chapter is named after and it was settled by measurement,
including two measurements that were wrong first and are kept below with what made them wrong.

Every figure here was produced on this machine on 2026-09-28. Node v22.23.2 on the host;
`node:22-alpine` (digest `0a7108bf`) in Docker, which is what `services/media-worker/Dockerfile`
builds `FROM`.

---

## R1 — How the bytes get made

**Question.** `services/media-worker` has two runtime dependencies, both workspace packages, and
`dimensions.ts` reads headers without decoding a pixel. Nothing in this platform can resize an
image. Four ways to change that, and the chapter's title says to price them.

### The measurements

Installed size, measured as the delta on `/usr` + `/lib` inside the worker's own base image, or
as `du -sb node_modules` for the npm option:

| Option | Added to the worker | Covers jpeg/png/gif/webp | Covers video |
|---|---:|---|---|
| `sharp` (npm, native, libvips 8.18.7) | **30,380,799 B** (musl) · 30,159,790 B (host glibc) | yes | no |
| ImageMagick as a subprocess | **28,936,284 B** (`imagemagick` + `-jpeg` + `-webp`) | yes | no |
| ffmpeg as a subprocess | **113,994,336 B** on top of ImageMagick | yes, badly | **yes** |
| A seventh container | a whole service, plus ADR-31's table | depends | depends |
| Pure TypeScript | 0 B | **PNG only** — `node:zlib` gives inflate; JPEG needs a DCT decoder, GIF LZW, WebP VP8 | no |

Time to turn one 1920×1080 JPEG into a 320-bounded WebP, p50 of 7 runs:

| Option | p50 | min | max |
|---|---:|---:|---:|
| `sharp`, in-process | **15.2 ms** | — | — |
| ImageMagick, one subprocess per object | **35.8 ms** | 31.8 | 42.1 |

`sharp` runs on musl: `MUSL_RUNS=ok`, libvips 8.18.7, a 268,798 B parent to an 11,424 B
thumbnail inside `node:22-alpine`.

**Decision.** `sharp`, in the media worker. **Rationale**: it covers all four allowed image
types, it is 2.4× faster than the subprocess for 1.4 MB more, and the subprocess form pays its
extra 20 ms as process spawn on every single object — a cost that scales with the backlog the
4.13 sweep walks, where the in-process cost does not.

**Alternatives considered.** Pure TypeScript is out on coverage, not on effort: it reaches one
of four types, and `ALLOWED_TYPES` has three others. A seventh container engages ADR-31 for a
job with no independent scaling story — the worker is already the only service that reads the
bytes, so a resizer would sit behind it, reading the same objects, with the same lifecycle. The
"deliberately not a separate service" test (same datastore, same transactions, same team) says
merged.

**And the size argument does not decide it, which is worth saying.** 30.4 MB against 28.9 MB is
5% on a choice between two fundamentally different relationships. What decides it is the 2.4×
and the spawn-per-object shape. Anyone re-running this should expect the sizes to stay close.

### Two measurements that were wrong first

**`apk add imagemagick` cannot decode a JPEG.** The first size measurement returned 27,524,848 B
for an ImageMagick that answers `no decode delegate for this image format 'parent.jpg'`. Alpine
ships the format delegates as separate packages. **A dependency's install size is not its usable
install size**, and the number that looked right was for a build that reads none of the four
types this platform allows.

**And the repair returned a zero that read as "already present".** Adding
`imagemagick-jpeg imagemagick-webp imagemagick-png imagemagick-gif` in one `apk add` reported a
delta of **0 B**. There is no `imagemagick-png` or `imagemagick-gif` package; `apk` is
all-or-nothing, so the transaction failed whole and installed nothing, and with stderr
redirected the failure presented as *no change needed*. This is `CLAUDE.md`'s own rule — a zero
from an instrument is a claim about the corpus only if the instrument can be shown to have
looked — and it is 058's *"the bulk form of a permitted operation is not automatically
permitted"* in a package manager.

**A third instrument lied and a control caught it.** `magick -list format | grep -E '^ *(JPEG|PNG|GIF|WEBP) '`
printed nothing, which read as *no format support*. The list writes `JPEG*` with a trailing
asterisk, so the pattern could not match. Re-run with a control — JPEG must appear, because the
JPEG delegate had just been installed and a conversion had just succeeded — the real answer is
`GIF* JPEG* JPG* PNG* WEBP*`. **The grep with no positive control is this project's most
reliable way to publish a confident zero**, and it happened here in the session that quotes the
rule.

**And busybox `date` has no `%N`.** Seven timed runs each reported `0 ms`. Timing re-done from
`process.hrtime.bigint()` inside the container.

---

## R2 — What a thumbnail actually costs, which is not a ratio

Measured with `sharp` at a 320 px bound, `fit: inside`, `withoutEnlargement`, WebP quality 80.

**On the six distinct real images in this workspace** — two icons, two diagrams, a logo and two
animated GIFs, which is a corpus of convenience and is stated as one:

| parent | parent B | thumb B | ratio |
|---|---:|---:|---:|
| `incrementalConstraints.gif` 748×386, 777 frames | 3,175,063 | 2,558 | **0.08%** |
| `demo.gif` 488×383, 300 frames | 4,631,886 | 6,070 | 0.13% |
| `layout-schema.png` 969×588 | 68,527 | 4,118 | 6.01% |
| `layout-schema.png` 933×794 | 107,248 | 10,258 | 9.56% |
| `icon.jpg` 460×460 | 32,370 | 7,104 | 21.95% |
| `CR_logotype.png` 620×96 | 11,047 | 6,848 | **61.99%** |

**The ratio spans 775× and the thumbnail bytes span 4×.** Every thumbnail lands between 2,558
and 10,258 bytes, because the output's size is a fact about the 320 px bound and not about the
parent. So *"a thumbnail costs 2% of the original"* is not a sentence this platform can publish
— the denominator is whatever the tenant uploaded. **The thumbnail costs about 7 kB. The ratio
is a fact about the parent, and publishing it as the cost is publishing the wrong variable.**

### The crossover, which decides US2 scenario 2

Synthetic parents, since the real corpus has no size series. Pixel noise encoded as JPEG q82 —
incompressible, so the **most favourable** case for the ratio, and said rather than passed off
as a photograph:

| parent | parent B | thumb B | thumb dims | p50 ms | ratio |
|---|---:|---:|---|---:|---:|
| 120×120 | 10,200 | 9,920 | 120×120 | 2.7 | **97.3%** |
| 200×200 | 27,400 | 26,662 | 200×200 | 5.9 | **97.3%** |
| 320×320 | 68,312 | 66,544 | 320×320 | 13.4 | **97.4%** |
| 400×400 | 106,182 | 58,226 | 320×320 | 13.6 | 54.8% |
| 640×480 | 204,284 | 35,178 | 320×240 | 11.1 | 17.2% |
| 1024×768 | 522,577 | 28,794 | 320×240 | 12.2 | 5.5% |
| 1920×1080 | 1,376,622 | 13,258 | 320×180 | 15.2 | 1.0% |
| 3000×2000 | 3,995,994 | 7,602 | 320×213 | 28.6 | 0.2% |
| 4000×3000 | 7,984,317 | 4,100 | 320×240 | 50.8 | **0.1%** |

**At or below the bound the thumbnail is 97.3% of the parent and identical to it.**
`withoutEnlargement` returns the same pixels in a different container, so the tenant stores the
image twice to save 2.7%. The rule this produces: **an image already within the bound gets no
rendition, and its delivered form points at the parent.** That is US2 scenario 2's answer, and
it was a measurement rather than a preference.

**Decision.** Bound 320 px on the long edge, WebP q80, `fit: inside`, no enlargement, and **no
rendition at all when both dimensions are already within the bound**.

**Rationale.** 320 is where the series turns: 400×400 is already 54.8% and every larger size
falls away fast. WebP because the output format is ours to choose and it is the smallest of the
four at this size. **Alternative rejected**: a byte-size target rather than a pixel bound, which
would make the output dimensions depend on the parent's content and give a layout nothing it
can reserve space for.

**The timing is not monotone in parent pixels** — 13.4 ms at 320×320 against 11.1 ms at
640×480 — because at and below the bound the encoder writes a full-size output. Worth one line
in the chapter; it is the kind of curve a reader assumes is flat.

**Ceiling, and the sentence this paragraph used to end with was wrong.** The image cap is 10 MB
(FR-MED-02). The largest parent measured, 7,984,317 B at 4000×3000, costs **50.8 ms of CPU**.
The first draft added: *"the sweep's own signed `HEAD` is 1.412 ms, so a thumbnail is roughly 36
`HEAD`s of work — real, and small beside the scan."* **That compares a decode against a metadata
request and leaves out the download the decode needs.** R9 is the rest of the bill.

---

## R9 — The two costs R2 did not measure

**Question, and it was an analysis pass that asked it rather than the plan.** R2 measured CPU.
A thumbnail is not only CPU, because the worker does not have the bytes.

**The worker never holds an object, by design.** `verify.ts` makes three requests and buffers
none of them:

| step | call | what it holds |
|---|---|---|
| metadata | `headObject` | a size and a last-modified |
| the scan | `streamObject` → `AsyncIterable`, consumed **once** by ClamAV | 64 KiB at a time, *"whatever the object's size"* (`scan.ts:64`) |
| the probe | `getRange(store, key, PROBE_BYTES)` | a prefix |

So a rendition needs a **full-object GET that nothing currently makes**, and the bytes have to
be somewhere while libvips reads them. Neither cost was in R2, in `plan.md`'s performance goals,
or in any task.

**Decision.** A **third GET**, taken only for an object the probe has established is an image
**above the bound**, buffered, resized, released.

**Rationale.** Three alternatives, and the streaming property is what rules two of them out:

- **Tee the scan stream into a buffer.** No extra I/O, and it buffers *every* object — including
  the 100 MB video cap — because the scan is first and unconditional and the real type is not
  known until the probe, one step later. It trades a request for a memory ceiling 10× higher on
  the objects that gain nothing from it.
- **One buffered GET feeding scan, probe and resize.** Strictly fewer requests than today for
  images — one instead of two — and it breaks the same property for the same reason: the scan
  must run before anything knows whether this is an image.
- **A third GET.** One extra round trip on images only, capped at 10 MB by FR-MED-02, and
  **R2's crossover removes most of it**: an image already within the bound gets no rendition, so
  it never triggers the fetch. The decision is taken at the one point where the type is evidence
  rather than the client's claim — after `sniff`, which is 4.13's finding about `content-type`.

**What has to be measured rather than asserted**, because this decision is currently priced at
zero:

1. **The fetch.** A full GET of an 8 MB object from the composed store, p50 over 7 runs, beside
   the 1.412 ms `HEAD` and the scan's own duration for the same object.
2. **Peak RSS.** A 4000×3000 RGB bitmap is ~36 MB if it is held whole — **and libvips may not
   hold it whole.** It processes in strips and `sequentialRead` exists for this case. The 36 MB
   is an upper bound from arithmetic, not a measurement, and the chapter must not publish it as
   one. Measure the worker's RSS across a 10 MB image and say which it was.

**No memory budget is being violated by assumption.** NFR-SCL-01's 160 MB is the **gateway's**
measured RSS at 10,000 sockets, not a worker budget, and `compose.yaml` sets no memory limit on
the worker. The measurement is for the chapter's cost table, not for a gate.

---

## R3 — Where parenthood lives

**Question.** `media_objects` has no self-reference. The spec's FR-001 needs the relationship
queryable both ways and unable to cross an environment.

**Decision.** A nullable self-referencing `parent_id` on `media_objects`, plus a `rendition`
column naming what the derived object is, both null for an uploaded object. One table.

**Rationale.** Every door that already acts on media reads `media_objects`: the quota sum, the
delivery gate, the verdict handler, the reference lookup. A second table means each of those
grows a second read or a `UNION`, and the two shapes share every column that matters — an
environment, a key, bytes, a mime type. The pair `(parent_id IS NULL, rendition IS NULL)` is
the discriminator, and a CHECK keeps them from disagreeing.

**Alternatives considered.** A separate `media_renditions` table keeps uploaded objects pristine
and was rejected on the door count: FR-005 requires authorisation to be *the same predicate*
rather than a copy, and two tables make one predicate into two. A JSONB column on the parent was
rejected for 4.13's reason, already written into migration `0018` — a number you want to filter
and sum should not be a `->>` and a cast.

**Environment safety.** The clause "cannot name an object in another environment" is not
expressible as a plain foreign key, because `parent_id` references the same table and the
environment is a second column. A composite foreign key `(parent_id, environment_id)` against a
unique `(id, environment_id)` gives it to the database rather than to a predicate somebody must
remember. **This is worth a measurement during implementation**: the unique index is redundant
with the primary key and costs storage, and the chapter should say how much.

**Code-derived, not measured.** The stack was down when this was written. The composite-key
behaviour and the index cost are phase-1 verifications, and `tasks.md` carries them as tasks
rather than as assumptions.

---

## R4 — The two clauses that would destroy a derived object

**Question.** The spec's premise table claims FR-MED-08 refuses a derived object and FR-MED-10
deletes it. Both were read from source; neither was run.

**FR-MED-08.** `channelsReferencingMediaIn` (repository.ts:626) selects distinct channels from
`messages` where `attachments @> [{"type":"media","media_id":<id>}]`. A rendition's id appears in
no message's attachments, so the function returns `[]`, and the delivery gate refuses an object
authorised by nobody. **This is FR-MED-08 working as written**, not a bug: the clause says an
object with no referencing message is readable by nobody, including its uploader.

**FR-MED-10.** The reaper does not exist. `grep` finds the clause cited in six comments and
implemented nowhere; 4.13's sweep walks `pending` uploads, which is a different job with a
different predicate. **So FR-002 cannot be proven against the job in this chapter.**

**Decision.** The derived object is excluded by making the *definition of unreferenced* include
parenthood, written once, in the repository layer, as the function the future reaper will call —
and this chapter's test drives that function directly with a stand-in caller. The chapter says
plainly that the reaper is not built and which chapter owns it.

**Rationale.** The alternative — waiting for the reaper's chapter and adding the exclusion then —
is how FR-MED-07's first sentence went unmet for three chapters while everybody cited the
second. A predicate with a test and no production caller is weaker than one with both, and it is
much stronger than a sentence in a spec.

**Which chapter owns the reaper.** `docs/12` row 21 is *The messages that expire* (FR-MOD-06,
FR-MED-11) and row 22 is *Erasure* (FR-MOD-04, FR-MED-10). **Row 22 names FR-MED-10**, so the
reaper is the erasure chapter's. Recorded here because the spec left it open between the two.

---

## R5 — Whether a derived object needs a state

**Decision.** No. A rendition has no `state` and no row in the state machine: it exists or it
does not.

**Rationale.** The three states exist to describe what the worker has learned about bytes a
client uploaded — `pending` means nobody has looked. Nobody uploads a rendition; the platform
writes it after the parent is already `ready`, in one step that either finished or did not. A
column that can only hold one value is what migration `0018` argued `scanning` out of being, in
the same movement, and the argument transfers exactly: a fourth state would have to be hidden
from clients or contracted for.

**Consequence for the schema.** `state` is `NOT NULL DEFAULT 'pending'` with a CHECK over three
values, so a rendition row must carry something. It carries `ready`, written at insert, and the
CHECK that ties `rendition IS NOT NULL` to `state = 'ready'` is what stops that from becoming a
second, quieter state machine.

---

## R6 — How a client learns the thumbnail's address

**Decision.** `deliveredAttachmentSchema`'s media arm gains an optional `thumbnail` object
carrying the rendition's `media_id` and its dimensions; absent when there is none. The client
fetches it through the existing `GET /v1/media/:mediaId` delivery door, which authorises it
through the parent.

**Rationale.** 4.14 built exactly the shape this needs and paid for the lesson: a sender must
not declare a rendition, and a delivered attachment must carry what the platform knows.
`deliveredAttachmentSchema` is already the outbound-only shape, already required to carry
`state`, and already the thing `messageSchema` builds. Putting the thumbnail anywhere else
creates a second place a client looks for facts about one attachment.

**Optional rather than nullable-required.** FR-MED-05 produces renditions for images only, and
the spec's FR-007 requires an allowed type with no rendition to be recorded as a value. The
*row* records the reason; the *wire* says absent, because a client's question is only "is there
a smaller one". **Alternative rejected**: `thumbnail: null` plus a `thumbnail_reason`, which
puts the platform's diagnostics in every delivered message.

**Dimensions on the wire, because a layout needs them before the bytes arrive.** This is the
whole reason a thumbnail helps: without width and height a client reserves the wrong box and the
page jumps when the image lands.

---

## R7 — Ordering, and what happens when generation fails

**Decision.** The rendition is produced **after** the scan and the declaration check pass and
**before** the verdict that moves the parent to `ready`; a failure to produce one is recorded on
the parent and does not stop it reaching `ready`.

**Rationale.** FR-009 forbids a rejected object leaving derived bytes, and the cheapest way to
guarantee that is never to write them for an object that has not passed. Putting generation
before the verdict also means one write reaches the database per object, which keeps 4.14's
`media.updated` firing once.

**Failure is recorded, not retried.** FR-008 forbids an indefinite retry, and the sweep re-reads
`pending` rows for ever — so an object whose thumbnail fails must not stay `pending`. It becomes
`ready` with a recorded reason, which is the same shape `rejected_reason` already has and the
same argument `0018` made for it: a closed set in the protocol package, not a CHECK constraint.

**Idempotence.** FR-010 requires one rendition after a duplicate. The parent's verdict is
already a compare-and-set (`UPDATE … WHERE state = 'pending'`, constitution IV, ADR-31's
neighbour), so a second sweep finds no `pending` row and never reaches generation. The rendition
insert carries a unique `(parent_id, rendition)` anyway, because *"the guard upstream means this
cannot happen"* is what 4.14's five accounting tests were each protecting against.

---

## R8 — The video half

**Decision.** Not built. Recorded in the SRS as unmet by decision, with the reason and a
reversal condition, on FR-MED-04's own precedent (revision 1.20) and FR-MED-07's (1.18).

**Rationale, with the number.** A poster frame needs a video **decoder**: the first keyframe of
an MP4 is H.264 and no byte-walking produces a pixel from it. The tool that does it is ffmpeg,
measured above at **113,994,336 B** — 3.75× the entire image half, and 71% on top of the
worker's base image — for the last one of FR-MED-05's two halves.

**And the precedent is directly on point.** FR-MED-04 is PARTLY MET because *duration* needs
four container parsers, and duration is strictly easier than a frame: duration is a number in a
header, a poster frame is the output of a decoder. **A chapter that declined the easier half of
the same problem cannot ship the harder one by omission** — it has to be ruled on, which is what
the spec's FR-013 forces.

**Reversal condition.** When video attachments are a measured fraction of stored objects rather
than a hypothesis, or when the platform already carries ffmpeg for another clause, the 114 MB
buys two things instead of one and the decision is re-opened.

**What a client gives up.** A video attachment renders with no preview image. The client knows
the attachment is a video from its mime type and can show its own placeholder, which is what it
does today for every attachment.

---

## Corpus provenance

The six real images are `relay-tutorial/app/icon.jpg` and five files from `node_modules` —
diagrams and animated GIFs belonging to `layout-base`, `zod-to-json-schema` and
`cytoscape-fcose`. **None is a photograph, and a chat platform's traffic is mostly photographs.**
The ratios in R2's first table are therefore a demonstration that the ratio is unstable, not an
estimate of what tenants will see. The crossover series is synthetic noise, which is stated at
the table. **Any figure the chapter publishes from either source says which one it came from.**

# Research — chapter 4.10, the upload that never reaches us

**Read this before the plan.** Four of the six questions were settled by running something, and
two of those contradict what the specification assumed.

---

## R1 — A presigned URL needs no dependency at all

**Decision**: sign with `node:crypto`. **No S3 client, no `@aws-sdk`, no `minio` package.**

The workspace has no S3 client of any kind today — measured, zero matches for `@aws-sdk`, `minio`
or `aws-sdk` across every `package.json`. The obvious next step is to add one. It is not needed.

An S3 presigned URL is a SigV4 signature — five HMAC-SHA256 rounds over a canonical string — and
Node 22 has `crypto`. Written in **28 lines** and run against a real store:

    PUT with the presigned URL, no client library, no auth header    HTTP 200
    the same object fetched back through a signed GET                HTTP 200, 45 bytes, exact
    an UNSIGNED GET of the same object                               HTTP 403
    a URL whose X-Amz-Expires has passed                             AccessDenied, "Request has expired"
    a URL with one character of the signature changed                HTTP 403

**AND THE BUCKET, WHICH THE FIRST PROBE SKIPPED.** Those five results are all about *objects*,
and the probe that produced them created the bucket with `docker exec … mkdir` — bypassing the S3
API for the one operation that has to happen before any of the other five. A bucket operation has
a **different canonical URI**: `/{bucket}`, no key segment, no trailing slash. Measured in
analysis pass 6:

    PUT  /relay-media          200      the bucket, no mkdir and no mc
    HEAD /relay-media          200      an existence check
    PUT  /relay-media/a/b.txt  200      an object into a bucket made the right way
    PUT  /relay-media again    BucketAlreadyOwnedByYou
    unsigned GET  of the object   403   private by default, no policy step
    unsigned LIST of the bucket   403

**AND ONE OF THE ORIGINAL FIVE WAS WRONG, FOR THE PROBE'S OWN REASON.** A tampered signature
was published as **400** and the store answers **403 `SignatureDoesNotMatch`**. The 400 came from
the shell that produced it: `${URL%?*}?…` splits on the LAST `?`, so what went to the store was
malformed rather than merely mis-signed. Asked through the code that ships, the store is
consistent — a bad signature is a refusal, not a parse error. Found when the integration test
asserted the published figure and went red.

**Nine results now, and the first five claimed a coverage they did not have.** The bucket create
is the first signed call this platform will ever make and it was the one nobody signed.

**Four of the first five are requirements of this chapter and the next two**, and none of them
needed a package. The 403 on an unsigned read is FR-MED-08's precondition holding by default rather than
by configuration, and the expiry message comes **from the store**, which is what FR-003 asks for.

**Alternatives considered.** `@aws-sdk/client-s3` plus `@aws-sdk/s3-request-presigner` — two
packages and a transitive tree, to produce a string this platform can produce in 28 lines.
`minio` — one package, same objection. Constitution VII's dependency test is whether the thing
is boring, and a signature function with a published algorithm and a test vector is more boring
than a client. This is chapter 4.2's argument reused: ClickHouse is reached with Node's own
`fetch` and `apply.mjs` has no driver.

**What it costs.** Signing is ours to get right. The canonical request is unforgiving —
`UNSIGNED-PAYLOAD`, the exact header list, the path encoded segment by segment — and the failure
mode is a 400 with no explanation of which field was wrong. So the chapter owes a test against
the running store rather than a unit test against an expected string.

---

## R2 — MinIO's Docker Hub image cannot be pulled, and the SAD names Docker Hub's

**Decision**: `quay.io/minio/minio`. **Not `minio/minio`.**

`docs/05-sad.md:1002` says *"MinIO standing in for object storage"* and the obvious
`docker run minio/minio` fails on this machine:

    docker: Error response from daemon: pull access denied for minio/minio,
    repository does not exist or may require 'docker login'

Four images were tried. `quay.io/minio/minio` pulls (241 MB) and is what the probe above ran
against. `chrislusf/seaweedfs` and `adobe/s3mock` also pull; `bitnami/minio` does not.

**This is the kind of line that reads as working until somebody runs it**, and the SAD's sentence
is nine chapters old. The compose service names the registry explicitly.

**Alternatives considered.** `adobe/s3mock` is smaller and is a mock — it would make every
measurement in this chapter a measurement of a mock, and FR-MED-03's verification chapter would
have to swap it. `seaweedfs` is a real store with an S3 gateway and is one more concept than the
SAD chose. MinIO is what ADR-13's diagram already shows.

---

## R3 — Storage is a LEVEL and `usage_periods` holds FLOWS, so the quota does not go there

**Decision**: the **cap** joins `quotaConfig` alongside the other three dimensions. The
**accounting** does not join `usage_periods`.

The specification assumed a monthly cap like the other three, and flagged the assumption as
doubtful. Two files settle it against that reading.

`period.ts` keys usage on the **first day of a calendar month**, and `usage_periods` carries one
row per `(environment_id, period)`. `credit.ts` accumulates within a period with
`creditFor(reported, credited) = max(0, reported - credited)`, whose own comment says **"the one
thing this function must never do is subtract from a bill."**

Put stored bytes in that row and two things break:

- **Deleting an object would have to subtract**, which the credit function refuses by design.
- **The figure resets on the 1st.** A tenant holding 100 GB would start every month at zero and
  be allowed another 100 GB. A monthly cap on a level is not a cap.

So committed bytes are the **current sum over the media rows**, compared against the cap at the
moment a slot is requested. The cap is configuration and belongs with the other caps; the
accounting is a different shape and belongs with the objects.

**And FR-RTL-05 has to be amended.** It reads *"configurable monthly quotas on messages sent,
unique active persons, and connection-minutes"* — three quantities, none of them storage — while
FR-MED-02 refuses on *"the environment's storage quota"* and FR-MED-12 says stored bytes are
*"included in quota enforcement (FR-RTL-05)"*. **Two clauses cite a third for something it does
not define**, and the amendment has to say that storage is a level rather than a monthly flow, or
the clause will mean the thing R3 just ruled out.

---

## R4 — The third refusal cannot reuse `quota_exceeded`, and the registry already argues it twice

**Decision**: three new codes — `media_type_not_allowed`, `media_too_large`,
`media_storage_exhausted`.

`codes.ts` already refuses this reuse in two places. `channel_member_limit_exceeded` carries
*"NOT `quota_exceeded`. That is a monthly, billable, resets-on-a-date refusal whose message
promises a resume date"*, and the banned-user code makes the same argument. **A storage cap does
not reset on a date** — R3 is why — so a message promising a resume date would be false, which is
the identical objection one dimension over.

The names follow the registry's shape: `snake_case`, the subject first, the condition second, and
near-neighbours distinguished in a comment rather than left to a reader.

---

## R5 — What the chain costs, and it is ten files rather than one

**Counted in analysis pass 2, because this section had remembered it — and counted AGAIN in pass
5, because pass 4's remediation had added two more.** The chapter edits **twelve fenced files**,
with **94 English chapters and 19 appendix hunks** of chain behind them:

    services/api/src/db/schema.ts                15 chapters   2 appendix hunks
    packages/protocol/src/codes.ts               12            1
    services/api/src/app.module.ts               11            1
    vitest.coverage.config.mts                   11           10
    turbo.json                                   10            2
    compose.yaml                                  8            0
    services/api/src/isolation/targets.ts         6            1
    services/api/src/protocol-error.filter.ts     6            0
    services/api/vitest.integration.config.mts    6            0
    services/api/src/db/catalogue.ts              4            1
    packages/test-harness/src/sentinel.sql        3            1
    services/api/src/quotas/config.ts             2            0

**And `compose.yaml` is eight, not the five this section first said** — 1.2, 3.19, 3.21, 3.22,
3.24, and then **4.2, 4.5 and 4.7**, which Part 4 added after the list was written. Feature 050
recorded the identical error: *"The fenced-file list was remembered, not counted — eight files,
not five. A list of fenced files goes stale every time a chapter moves code between files."*

**And `vitest.coverage.config.mts` is the most expensive of the twelve.** Feature 055 spent most
of a phase on it — 15 bad hunks, 743 differing lines, a chain state with **no `env` block at
all** — which is the block this chapter adds a key to. Its `env` change and its per-file pins are
**one hunk**, because no page in the series holds two chained fences for one path and `--at
<page>` granularity assumes it.

The chain is clean in both locales, so each file takes a `diff` hunk in this chapter and a
byte-identical Vietnamese twin. `check:fences` is at **0** and the close-out reports an absolute
number.

Feature 055's instrument applies: hunks are generated with `pnpm check:fences --dump <dir>`,
never with `git diff` against the working tree. And `--dump` writes the English chain, so the
Vietnamese fence is a copy of the English body rather than a second generation.

---

## R6 — Two questions this chapter must answer and cannot answer well

**A slot nobody uploads to.** FR-015 asks what happens. There is no verification pass in this
chapter (FR-MED-03) and no scheduled job (FR-MED-10's is 24 hours and about *unreferenced* media,
not *unused slots*). So a `pending` row whose object never arrived holds committed bytes
indefinitely, and the honest answer is that **this chapter records the leak rather than closing
it** — the same shape as 4.7's daily job that has no runner.

**Two slots racing the same remaining quota.** The check reads committed bytes and the insert
adds to them; without serialising, both are issued. The plan takes the cheap correct option — do
both inside one transaction — and the chapter says what the alternative costs, because a reader
who copies a read-then-write quota check will ship the race.

---

## R7 — The fourth refusal, found in analysis pass 1

**Decision**: `media_storage_unavailable`, its own code, 503, and the only one of the four whose
message may say retry.

The specification built three refusals and called `docs/12`'s fourth unexplained. It is
`docs/05-sad.md:1062`, the degradation table:

> | Object storage lost | Media uploads/downloads fail; text messaging unaffected | **Upload slots
> return a specific error**; attachments render as temporarily unavailable; no Relay-side state to
> recover — storage provider's durability is the recovery |

**The brief was right and the clause is short.** FR-MED-02 names three conditions and the SAD
names a fourth, in a table nobody reads when they are reading requirements.

**And it is the one that matters most to a client.** The other three are permanent — transcode,
compress, free space — so retrying them is wasted. This one is transient, so retrying is the
remedy. A client that cannot tell them apart gets it wrong in one direction or the other every
time.

**It also cannot fall into `internal_error`, and neither can the other three.**
`protocol-error.filter.ts` maps 400, 401, 403 and 404 and falls everything else through, and this
chapter's four statuses are 415, 413, 402 and 503. Named throws work; an unnamed one produces the
fallback, which the filter's own comment calls *"a lie the client cannot act on"* — twice, about
the two statuses earlier chapters had to fix for the same reason. The ladder gains four entries
and a probe throws unnamed at each.

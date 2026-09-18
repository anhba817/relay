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
    a URL with one character of the signature changed                HTTP 400

**Four of those five are requirements of this chapter and the next two**, and none of them needed
a package. The 403 on an unsigned read is FR-MED-08's precondition holding by default rather than
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

## R5 — What the chain costs, and it is not nothing

`compose.yaml` is fenced in five chapters — 1.2, 3.19, 3.21, 3.22, 3.24 — and the chain is clean
in both locales, so a new service is a `diff` hunk in this chapter and a byte-identical twin in
the Vietnamese one. `check:fences` is at **0** and the close-out reports an absolute number.

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

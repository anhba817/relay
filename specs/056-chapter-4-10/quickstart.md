# Quickstart — chapter 4.10

Every command here was run before it was written. Where a figure appears, it is what came back.

## 1. The store

`compose.yaml` gains one service. **The registry is part of the name**: `minio/minio` on Docker
Hub is `pull access denied` on this machine, and `docs/05-sad.md:1002` predates that.

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d minio
curl -s -o /dev/null -w 'health: HTTP %{http_code}\n' http://localhost:9100/minio/health/live
```

**A 200 here proves almost nothing**, which is the point of saying so. Chapter 4.2's ClickHouse
answered `/ping` with `Ok.` for sixteen chapters while every query from outside its container was
refused. The check that counts is the round trip in §3.

## 2. The signer, on its own

```bash
node -e '
const { presignPut } = await import("./services/api/dist/media/presign.js");
console.log(presignPut({ endpoint: "http://localhost:9100", bucket: "relay-media",
  key: "probe/hello.txt", accessKey: "relay", secretKey: "relay-secret" }));'
```

Six query parameters and no others: `X-Amz-Algorithm`, `X-Amz-Credential`, `X-Amz-Date`,
`X-Amz-Expires`, `X-Amz-SignedHeaders`, `X-Amz-Signature`. **No dependency** — `node:crypto`
signs it, and the workspace has no S3 client of any kind.

## 3. The round trip, which is the real health check

```bash
URL=$(node -e '…presignPut(…)')                       # as above
echo hello > /tmp/f.txt
curl -s -o /dev/null -w 'PUT      -> %{http_code}\n' -X PUT --upload-file /tmp/f.txt "$URL"
curl -s -o /dev/null -w 'unsigned -> %{http_code}\n' http://localhost:9100/relay-media/probe/hello.txt
```

Measured against `quay.io/minio/minio`:

    PUT      -> 200      no auth header, no client library
    unsigned -> 403      the bucket is not publicly readable, by default
    signed GET -> 200    45 bytes, byte-exact
    expired    -> AccessDenied · Request has expired      from the STORE
    tampered   -> 403    SignatureDoesNotMatch

**Four of those five are requirements of this chapter or the next**, and none needed a package.

## 4. The slot, end to end

```bash
curl -s -X POST localhost:3000/v1/media -H "Authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' \
  -d '{"filename":"holiday.jpg","mime_type":"image/jpeg","bytes":2097152}' | jq
```

A `media_id`, `state: "pending"`, an `upload_url` and an `expires_at`. Then upload to that URL
directly and confirm **the api saw one request, not two** — its own request log is the instrument,
which is chapter 4.8's surface earning its keep.

## 5. The three refusals, asserted by code

```bash
for body in '{"filename":"x.exe","mime_type":"application/x-msdownload","bytes":10}' \
            '{"filename":"x.jpg","mime_type":"image/jpeg","bytes":20971520}' \
            '{"filename":"x.jpg","mime_type":"image/jpeg","bytes":1048576}'; do
  curl -s -X POST localhost:3000/v1/media -H "Authorization: Bearer $TOKEN" \
    -H 'content-type: application/json' -d "$body" | jq -r '.code'
done
```

    media_type_not_allowed
    media_too_large
    media_storage_exhausted        (with a storage cap set below the committed bytes)

**And the fourth, which needs the store taken away rather than a stub:**

```bash
docker compose stop minio
curl -s -X POST localhost:3000/v1/media -H "Authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' \
  -d '{"filename":"a.jpg","mime_type":"image/jpeg","bytes":1024}' | jq -r '.code'
docker compose start minio
```

    media_storage_unavailable

**It is the only transient one of the four**, so it is the only one whose message may say retry.
A test that stubs the failure asserts the stub.

**Read the code, not the status.** `webhooks.itest.ts` passed for four chapters while the body
said `internal_error`, and only the code could have caught it.

## 6. The quota, at its boundary

```bash
# with the cap set to exactly the committed bytes plus one megabyte
curl … -d '{"filename":"a.jpg","mime_type":"image/jpeg","bytes":1048576}'   # issued
curl … -d '{"filename":"b.jpg","mime_type":"image/jpeg","bytes":1048577}'   # refused
```

One byte under and one byte over. A test in the middle of a range proves the comparison exists,
not that it is right.

**And probe the configuration from both sides:**

```bash
# the parser must refuse a dimension nobody implemented …
curl … -d '{"quota_config":{"bandwidth":{"hard":1}}}'        # 400 at parse time
# … and so must the migration's CHECK, or the cap silently becomes no cap
psql -c "update environments set quota_config = '{\"bandwidth\":{\"hard\":1}}'"
```

Both halves, every time the schema is re-pinned. Feature 049 found a coverage pin that could not
fail by running exactly this shape of probe in both directions.

## 6a. The status ladder, probed with an unnamed throw

`protocol-error.filter.ts` maps 400, 401, 403 and 404 and falls everything else through to
`internal_error`. All four of this chapter's statuses — 415, 413, 402, 503 — are outside it, so
they are right only while every thrower names its code.

Throw unnamed at each and assert the code is **not** `internal_error`. The filter's own comment
calls that fallback *"a lie the client cannot act on"*, once about the 400 chapter 2.2 fixed and
once about the 403 the credentials chapter fixed.

## 7. The gates

```bash
cd ../relay-tutorial
pnpm lint && pnpm build && pnpm check:docs && pnpm check:srs && pnpm check:figures
pnpm check:fences 2>&1 | grep 'problem(s)\|replay onto'
```

That list is `ci.yml:184-205`'s, not a remembered one. **Read each gate's success line, not its
exit code** — five of the seven gate scripts exit 0 when their corpus is absent.

The fence chain is at **0**. Report the absolute number at close-out, not a delta: the delta-of-0
convention hid a problem for nine chapters and feature 055 named the file it hid.

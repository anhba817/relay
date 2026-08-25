# Contract — the sender on a send

## `POST /v1/channels/:channelId/messages`

The body gains one field.

```json
{ "text": "your ticket was updated", "user": "support-bot" }
```

| Credential | `user` | Outcome |
|---|---|---|
| application key | a bot of this tenant | 201, the message is sent as that bot |
| application key | a **person** of this tenant | **403** `sender_not_permitted` — a key may not post as a person |
| application key | absent | 400 `invalid_request`, `field: "user"` |
| application key | a bot of **another** tenant, or an identifier with no row | 400 `invalid_request`, `field: "user"` — **byte-identical for both** |
| user token | absent | 201, sent as the token's subject |
| user token | present | 400 `invalid_request`, `field: "user"` — a user speaks as themselves |

### Why the code is not `forbidden`

`codes.ts` makes this argument twice in its own comments, and this refusal is the third
instance of the same shape:

    wrong_credential_type      the credential is the wrong CLASS      (chapter 3.2)
    wrong_credential_service   the credential is the wrong SERVICE    (chapter 3.12)
    sender_not_permitted       the credential names the wrong KIND OF USER

A generic 403 would leave a client unable to tell "this key may not post as a person" from
"this key lacks a permission" from "you are not a member" — and the registry's own words for
that are *"a client that cannot tell them apart retries the wrong one for ever."*

**Adding it will fail `codes.test.ts`**, which asserts the exact code set. That is the
instrument working: it is what made close code 4003 a decision rather than an accident in
chapter 3.16, and updating the assertion is the act of deciding.

### Why a person is 403 and a foreign bot is 400

They are different facts and only one of them is safe to state.

**A person of your own tenant** is an identifier the caller already knows exists — they can
list their own users. Refusing with 403 `sender_not_permitted` reveals nothing they did not
have, and it names the rule: *this credential may not post as a person.* A client that gets 400 there would go looking
for a malformed field and find nothing wrong with it.

**A bot of another tenant, or an identifier that exists nowhere,** must be indistinguishable
(FR-TEN-05). If "exists elsewhere" answered differently from "exists nowhere", a caller could
enumerate other tenants' bot identifiers one guess at a time. Both are `invalid_request` on the
`user` field, byte-identical but for `request_id`, and the isolation oracle asserts it.

**This is the same shape chapter 3.15 settled for channels** — a private channel the caller
cannot see answers as one that does not exist, while a public one they may not act on answers
`403 not_a_member` — and it is settled the same way, by asking what each refusal tells someone
who does not already know it.

### The order of the refusals

    1  is the caller banned?              (chapter 3.16, before the channel is read)
    2  can the caller see the channel?    (chapter 3.15, private → as if absent)
    3  is the channel archived?           (chapter 3.15)
    4  does the named sender resolve in this tenant?     400, field: "user"
    5  may this credential send as that sender?          403 for a person

**4 before 5**, for the reason 2 comes before 3: step 5's refusal names a fact about a user, so
it must not run for a user the caller could not otherwise confirm exists.

## `POST /internal/messages` — unchanged

The internal route carries a user token and resolves its subject, as it has since chapter 3.2.
It gains nothing: its sender was never absent, which is why the gap was only ever on the public
route.

## What does not change

**The frame contract.** `messageSchema.user` stays `z.string().min(1)`. No published client
tolerates a new shape, and chapter 3.16's frame-shape assertion keeps passing — which is the
reason a bot was chosen over a nullable sender, and worth asserting rather than claiming.

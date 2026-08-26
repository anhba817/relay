# Traceability — chapter 3.17, the sender a message never had

Both directions. A map that only runs requirement→test cannot catch a test that verifies
nothing, and a map that only runs test→requirement cannot catch a requirement nobody built.
Chapter 3.12's map recorded FR-CHN-05 delivered when two of its three verbs were built, and
chapters 3.15 and 3.16 corrected it twice; the correction is below rather than assumed.

## The governing documents, as amended

    FR-USR-07   NEW      bot users with a description; shall not authenticate     P2  T
    FR-MSG-13   AMENDED  "any user" -> "a bot user of that tenant"                P2  T
    FR-MSG-15   NEW      every message shall carry a sender                       P1  T
    FR-RTL-05   AMENDED  quota on "unique active users" -> "unique active persons" P3  T
    FR-ANL-05   UNTOUCHED  still meters "unique active users", still counting bots

    docs/05-sad.md   `CREATE TABLE users` gains `kind` and `description` + 2 CHECKs

**FR-MSG-13 is MET, not introduced.** It has required a key to send on behalf of a user
since v1; chapter 3.3 satisfied it by naming nobody, and `messages.controller.ts` recorded
that reading for eleven chapters. This chapter is its first implementation.

## Requirement -> verification

| Clause | What verifies it |
|---|---|
| FR-USR-07 | `users.itest.ts` — the bot round trip, the description rules, the promotion in three states |
| FR-MSG-15 | `pnpm typecheck` (SC-003a: `sendMessage` takes `userId: string`), and every send site in the workspace naming one |
| FR-MSG-13 (as amended) | `messages.itest.ts` — a key naming a bot 201, a person 403, nobody 400 |
| FR-RTL-05 (as amended) | `quotas.itest.ts` — a bot cannot exhaust a person's allowance |
| FR-ANL-05 (unchanged) | `quotas.itest.ts` — a bot's send counts toward active users |
| FR-USR-01 | unchanged for bots: a bot's identifier is customer-supplied; recorded in the amendment blockquote |
| FR-USR-02 | `credentials.itest.ts` — implicit creation still makes a **person** |
| FR-USR-05 | `users.itest.ts` — a deleted bot keeps its description and its messages keep naming it |
| FR-USR-06 | `messages.itest.ts` — a banned bot's send is refused; the connection half is empty by construction |
| FR-MSG-08 | unchanged, and unbuilt: its tombstone already retains the author. Recorded, not amended |
| FR-WHK-02 | `event.test.ts` — the webhook payload carries `user: null` for a legacy row |
| FR-WHK-03 | why `MessageCreatedData.user` stays nullable: the retry queue was full when the rule changed |
| FR-CHN-05 | **two of three verbs.** See the correction below |
| FR-RTL-08 | the bot's exemption from the ceiling is a stated exception, in the amendment blockquote |
| NFR-USE-03 | `packages/outsider` executes the README in CI — and the README is now the quickstart of record |
| EIR-API-03 | 400 and 403 are both already in the enumerated status set; no amendment |
| EIR-API-04 | refusals carry `code`, `message`, `field`, `docs_url`, `request_id` |
| FR-AUT-09 | the dev-token mint refuses a bot; **not** an in-place amendment, because the clause carries no universal quantifier |
| FR-MOD-03 | requires moderation actions be audit-logged; **no audit log exists**, so a bannable bot adds no violation |
| FR-MOD-04 | erasure is not `deleteUser`; SC-007's claim is about the second and must not be read as the first |
| EIR-API-07 | OpenAPI 3.1, P4, and no spec file exists anywhere; nothing to update |

## FR-CHN-05, corrected for the third time

    | FR-CHN-05 | A user shall not read messages from, send messages to, or observe
      presence in a private channel of which they are not a member. | P1 | T |

    read messages from      BUILT   chapter 3.15
    send messages to        BUILT   chapter 3.15, and this chapter's FR-019b keeps it true
                                    for a person while exempting a bot named by a key
    observe presence in     NOT BUILT — there is no presence feature

Checked rather than assumed: the only occurrence of "presence" in `services/gateway/src` is
the English word, in a comment about cursors. Chapter 3.19 is the verb.

**This chapter narrows the second verb's scope and must not be read as completing the
clause.** FR-019 draws the line: a key naming a bot has the key's authority, so the
membership check turns on the sender being a person. A person who is not a member is still
refused, indistinguishably, which is what FR-CHN-05 asks for.

## Verification -> requirement

Every behaviour-bearing task cites a clause (`sweep.py` check 14 enforces it). The reverse
direction found sixty-four tasks with no citation in analysis pass 12; they carry one now.

## What this chapter does NOT deliver

- **The fan-out.** A REST-sent message still reaches no live socket: only the gateway
  publishes (`session.ts`), and the api publishes nothing. Chapter 3.18.
- **Presence.** FR-CHN-05's third verb, FR-RTM-05/06/07. Chapter 3.19.
- **Half of chapter 3.12's gap G1 is closed, not all of it.** The resume now delivers a
  REST-sent message, because the row has a sender; live delivery still needs the fan-out.

# Contract — the WebSocket close codes

## What changes

Nothing about the codes. Every one becomes documented, and a gate keeps it that way.

## The set, and where each is documented today

`CLOSE_CODES` in `packages/protocol/src/codes.ts` has six members. Measured across `docs/`:

| Code | Meaning | Documented in the error reference |
|---|---|---|
| 4001 | invalid or expired token | no — appears only in the SRS |
| 4002 | protocol violation | **yes**, twice |
| 4003 | banned in this environment | **no — appears in no document at all** |
| 4004 | connection limit reached | **yes**, once |
| 4008 | quota exhausted | no — only in the tutorial plan, which is deliberately unpublished |
| 4009 | server shutdown (drain) | no — only in the SAD |

EIR-WS-06 requires authentication failure, quota exhaustion, server shutdown and protocol
violation to be documented and distinguishable. **One of the four is.** That number has not
moved since chapter 3.22 measured it.

## After

All six are documented in `docs/08-error-reference.md`, each distinguishable by cause.

## Where a close code is documented

Inside the `**Status:**` line of the error code that carries it — chapter 3.21's convention.

**Not under its own heading.** `check-error-codes.mjs:59` computes
`headings.filter((h) => !codes.includes(h))` over every `^## ` in the reference and exits
non-zero for any heading that is not a member of `ERROR_CODES`. A `## 4001` section fails
that gate with no exemption available.

## The gate

`check-error-codes.mjs` gains a second comparison: every member of `CLOSE_CODES` must appear
in the reference's text. It already reads that module for `ERROR_CODES`, so the expected set
comes from the same file.

**Test it red before believing it.** A checker that has never failed is a checker whose
class list nobody has verified.

# Contract — `avatar_url` on the user profile

## What changes

The scheme of a stored avatar URL is restricted to `http` and `https`, determined by parsing.

## Before

    avatar_url: z.string().url().max(2048).nullable().optional()

Measured, not read: this accepts `javascript:`, `data:`, `file:` and `vbscript:`. The
platform stores the value and returns it for a customer's client to render. In an `<img src>`
a `javascript:` URL is inert; behind an `<a href>` it is stored XSS with Relay's name on the
storage.

## After

| Case | Response |
|---|---|
| `https://…` | accepted |
| `http://…` | accepted |
| any other scheme | `422` with a code that names the cause and `field: "avatar_url"` |
| `null` | accepted, unchanged |
| absent | accepted, unchanged |
| longer than 2,048 characters | unchanged |

## Existing rows

Measured before shipping: every stored value in the lane database is null (387,091) or
`https` (586). **Nothing stored would be rejected.** The rule applies to writes; no row is
rewritten. FR-013 requires the count to be recorded, not to be zero — a different population
can differ, and a customer's database is a different population.

## Verification

Attempt each of the four schemes chapter 3.24's research measured. Each is refused and the
refusal names the field.

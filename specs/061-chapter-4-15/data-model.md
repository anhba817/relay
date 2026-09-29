# Data model — Chapter 4.15

## 1. `media_objects`, extended

Three columns and two constraints. No new table; R3 has the argument.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `parent_id` | `uuid` | yes | The object this one was derived from. Null for everything a client uploaded. |
| `rendition` | `text` | yes | What this derived object is. Null exactly when `parent_id` is null. |
| `rendition_failed_reason` | `text` | yes | Set on a **parent** when the platform tried to produce a rendition and could not. Null otherwise. |

### Constraints

```
media_objects_rendition_pairing_check
  CHECK ((parent_id IS NULL) = (rendition IS NULL))
```
The discriminator cannot disagree with itself. A row is either an upload or a rendition, and
there is no third thing a reader has to guess at.

```
media_objects_rendition_state_check
  CHECK (rendition IS NULL OR state = 'ready')
```
R5's decision in one line. A rendition has no lifecycle of its own; without this the `state`
column quietly becomes a second state machine that only ever holds one value.

```
media_objects_id_environment_key  UNIQUE (id, environment_id)
media_objects_parent_fk  FOREIGN KEY (parent_id, environment_id)
    REFERENCES media_objects (id, environment_id) ON DELETE CASCADE
```
Constitution I, given to the database. A composite foreign key cannot name a row in another
environment — the second column has to match, and `environment_id` is already `NOT NULL`. The
unique index is redundant with the primary key for uniqueness and exists only so the composite
key has something to point at; **its storage cost is a measurement the chapter owes** (plan,
phase 2).

`ON DELETE CASCADE` discharges FR-003's database half. The store half is not a cascade and has
to be written; see §4.

```
media_objects_parent_rendition_key  UNIQUE (parent_id, rendition)
```
FR-010. One rendition of each kind per parent, whatever calls the insert twice.

### Index

```
media_objects_parent_idx  ON media_objects (parent_id) WHERE parent_id IS NOT NULL
```
Partial, following `0019`'s precedent in the same table: it stays the size of the rendition
population rather than the size of the table. Read by the delivery join and by the
unreferenced-object predicate.

## 2. The rendition set

A closed set in `@relay/protocol`, not a CHECK constraint — migration `0018`'s argument for
`rejected_reason`, and the same reason: a CHECK is a fourth thing to widen.

```
RENDITIONS = ["thumbnail"] as const
```

One member today. `poster` is the video half and is not built (R8). The set being a set rather
than a boolean is what makes that a future insert instead of a future migration.

**Rendition failure reasons**, also closed:

```
RENDITION_FAILED = ["unsupported_source", "decode_failed", "store_write_failed"] as const
```

`unsupported_source` is FR-007's *"recorded as a value, not as an absence"*: an allowed type
this platform cannot decode. It is derivable rather than listed — the set of types with a
rendition is whatever the decoder reports it can read, intersected with `ALLOWED_TYPES`, and a
test asserts that intersection rather than restating it.

## 3. What a rendition row holds

| Column | Value for a thumbnail |
|---|---|
| `id` | fresh uuid |
| `environment_id` | the parent's, enforced by the composite key |
| `user_id` | the parent's, so erasure by user finds it on the same predicate |
| `filename` | the parent's, prefixed — it is never served as a download name, and it is what a human reads in a row |
| `mime_type` | `image/webp` |
| `declared_bytes` | the rendition's **actual** length |
| `state` | `ready` |
| `object_key` | `${environment_id}/${rendition id}` — the platform's own layout (`media.service.ts:108`), using the rendition's own uuid |
| `width`, `height` | the rendition's own, which is what the wire carries |
| `verified_bytes`, `verified_type` | the same actual values — nothing was declared, so there is nothing to contradict |
| `parent_id`, `rendition` | the parent, `"thumbnail"` |

**The quota is approximate by one rendition, and that is accepted rather than solved.**
`reserveMediaSlot` locks the environment row `FOR UPDATE` before it sums; the verdict
transaction that inserts a rendition takes no such lock, so a slot request concurrent with a
rendition insert sums without it. No mechanism is added: 4.10 measured that the lock earns its
place in the slot-versus-slot race, which this does not change, and a second lock would make
every verdict wait on every slot request.

**And the key is the rendition's own, not the parent's with a suffix.** The first draft of this
table derived it from the parent's key plus the rendition name, which `schema.ts` forbids in its
own words: `object_key` is *"OPAQUE, AND NOT A PATH INTO THE STORE … keeping them separate is
what lets the storage layout change without breaking a published contract."* A derived key
couples two rows' storage addresses and invents a second layout beside `${environment_id}/${id}`,
which is the one thing that comment exists to prevent.

**`declared_bytes` carries a number nobody declared, and that is a compromise worth naming.**
The column's own comment defines it as *"what the caller said"*. The quota sums it
(`repository.ts`, `sum(declared_bytes) WHERE environment_id = ? AND state <> 'rejected'`), and
FR-012 requires derived bytes to be accounted on the same basis as uploaded ones. Writing the
actual length there is what makes the quota and FR-MED-12's meter correct with no second read.
**The alternative — a separate column summed alongside — was rejected because every reader of
the total would have to learn about it**, and there are three. The comment is amended to say
what the column means for a row nobody declared.

## 4. Deletion paths

FR-003 says no path deletes one and leaves the other. The paths, enumerated from the code rather
than listed from memory — **and the enumeration is asserted complete by a test**, because
`CLAUDE.md` records four chapters where a hand list was wrong:

| Path | Database | Store |
|---|---|---|
| The worker rejects an object (`recordMediaVerdict`) | no rendition exists yet — R7's ordering | nothing written |
| Rendition generation fails | no row | FR-006's write is the last step, so nothing is half-written |
| FR-MED-10's reaper | not built; the predicate is (R4) | the reaper's chapter |
| FR-MED-11's retention | not built | not built |
| FR-MOD-04 erasure | not built | not built |
| A tenant deleted | cascade from `environments` | already unhandled for uploads — **not this chapter's, and said so rather than fixed quietly** |

**NOTHING DELETES A `media_objects` ROW, AND THAT IS THE HONEST SCOPE.** `.delete(mediaObjects)`
and `DELETE FROM media_objects` outside tests return **nothing at all**. The rejection path is
the only live deletion in the platform and it deletes **bytes, not rows** — deliberately, since
migration `0018` says *"a rejected object's row is all that survives it"* and `media.controller.ts`
keeps the row so a refusal stays auditable after the object is gone.

Three consequences, all of them things this chapter must say rather than discover:

1. **`ON DELETE CASCADE` has zero live triggers.** It is correct and it is dormant. It becomes
   live when the erasure chapter writes the first row deletion.
2. **The store-side deletion has no caller either**, exactly like `unreferencedMediaIn`. It is
   written, tested directly, and commented with the chapter that will call it.
3. **The one live path cannot involve a rendition.** A rejected parent never had one — R7 puts
   generation after the checks — so the rejection path needs no change.

**This is why SC-002 needs a floor.** *"A test for every path that deletes a media object"* over
an empty set of paths passes by enumerating nothing, which is the shape `CLAUDE.md` calls a test
that proves nothing. The enumeration asserts the count it found, and the cascade is exercised by
a direct `DELETE` with both halves checked — the only way to run it today.

## 5. State

None. A rendition is not in the state machine (R5). The parent's states are unchanged:
`pending → ready` and `pending → rejected`, both by compare-and-set.

The one transition this chapter adds is not a state change: a parent that reaches `ready` may
carry `rendition_failed_reason`, which is a fact about a side effect and not a fourth state.
A client sees it as an absent `thumbnail` on the wire (R6) and nothing else.

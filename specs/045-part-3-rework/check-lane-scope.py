#!/usr/bin/env python3
"""Find assertions that read a SHARED table without scoping to their own subject.

WHY AN INSTRUMENT AND NOT MORE RUNS. Six of these were found by running the lanes
unserialised and reading what fell over, one at a time, over five runs — and a seventh
appeared on the sixth run. Each instance is load-dependent and rare, so "N green runs"
is weak evidence and gets weaker the more of them you have already used up. This asks the
question directly: which queries in a test read a table every other suite also writes,
without a predicate naming this test's own rows?

WHAT IT LOOKS FOR. A SQL aggregate or bare select over one of the shared tables, inside a
`.itest.ts`, with no scoping predicate in the same statement. The scoping columns are the
tenancy spine — `environment_id`, `organisation_id`, `application_id`, `channel_id`,
`endpoint_id`, `delivery_id`, `user_id`, `connection_id` — plus an explicit id equality.

WHAT IT CANNOT SEE, said plainly: a query scoped by a column that is not on that list, a
scope applied in JavaScript after the rows come back, and an assertion on a COUNT the
suite computed some other way. It reads SQL text, and a test can be wider than its subject
without any SQL at all.

Controls, all three asserted rather than assumed: a known-bad query must be reported, a
known-good scoped query must not, and a query over an unshared table must not.

Usage: check-lane-scope.py [--all]     (--all lists every hit, not just the summary)
"""
import pathlib, re, sys

WT = pathlib.Path("/home/dong/work/relay/tmp/part3-refactor")

# Tables every suite in a lane writes to. A read of one of these is a read of the lane.
SHARED = [
    "organisations", "applications", "environments", "channels", "messages", "users",
    "humans", "memberships", "outbox", "webhook_endpoints", "webhook_deliveries",
    "webhook_attempts", "webhook_disable_notifications", "read_positions",
    "usage_periods", "usage_active_users", "usage_connections", "quota_notifications",
    "api_keys", "schema_migrations",
]
SCOPES = [
    "environment_id", "organisation_id", "application_id", "channel_id", "endpoint_id",
    "delivery_id", "user_id", "human_id", "connection_id", "subject", "id =", "id=",
    "id in", "id = any", "name =", "name like", "address", "period",
    # A JSON payload carries its own subject id, and three suites scope on it that way.
    # Added after the first run reported all three as unscoped: the predicate is real,
    # the column name is not on the spine. A control below pins it.
    "->>'id'", "->>'type'",
    # A PINNED INSTANT IS A SCOPE, and it is the only one available to a claim that is
    # genuinely about the whole table. `reset-lane.itest.ts` asserts a global script
    # deleted no organisation; it cannot scope to a tenant, so it scopes to TIME —
    # rows created after the pin belong to whoever is running beside it.
    "created_at <=", "created_at<=", "created_at <", "created_at >=",
]
# THE UNIT IS THE STRING LITERAL, because a SQL scope has to be in the SQL.
#
# Two earlier versions were wrong in opposite directions and both are worth recording.
# Ending the match at the template's closing quote reported three SCOPED queries, because
# `'${id}')` closes the lookahead before the `WHERE` it was looking for. Replacing that
# with a fixed window after `from` then MISSED a real one, because the surrounding
# JavaScript happened to contain the word `period` — a false negative, which is a missed
# defect and strictly worse. So: find the literal the `from` sits in, and look for the
# scope inside THAT. Nothing outside the query can scope the query.
#
# AND COMMENTS ARE STRIPPED FIRST. `presence.itest.ts` explains the fault it was fixed for
# by QUOTING the broken query, so the scanner reported the comment documenting the repair.
# A scanner that reads prose finds the prose.
COMMENT = re.compile(r"(?m)^\s*(?://|\*|/\*).*$")
FROM = re.compile(r'(?is)\bfrom\s+"?(\w+)"?')


def literals(text: str):
    """Every backtick, single- and double-quoted literal — with literals joined across a
    `+` when nothing but whitespace separates them.

    JOINING IS NOT A CONVENIENCE, IT IS THE QUERY. This repository builds parameterised
    SQL as `"SELECT … FROM t " + "WHERE endpoint_id = $1"`, and reading the halves apart
    reports the half holding the `from` as unscoped while the scope sits in the next
    string. Three such queries were flagged before this joined them, all correctly
    scoped."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c in "`'\"":
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == c:
                    break
                j += 1
            lit = text[i + 1 : j]
            # Nothing but whitespace and a single `+` since the previous literal ended?
            # Then this is the same query continued.
            if out and out[-1][1] is not None:
                between = text[out[-1][1] : i]
                if between.strip() == "+":
                    out[-1] = (out[-1][0] + " " + lit, j + 1)
                    i = j + 1
                    continue
            out.append((lit, j + 1))
            i = j + 1
            continue
        i += 1
    return [lit for lit, _ in out]


def scan(text: str) -> list[tuple[str, str]]:
    out = []
    for lit in literals(COMMENT.sub("", text)):
        low = lit.lower()
        for m in FROM.finditer(lit):
            table = m.group(1).lower()
            if table not in SHARED:
                continue
            if any(s in low for s in SCOPES):
                continue
            out.append((table, " ".join(lit.split())[:110]))
    return out


def controls() -> None:
    bad = 'const r = await db.execute(`SELECT count(*)::int AS n FROM organisations`);'
    good = 'const r = await db.execute(`SELECT count(*)::int AS n FROM outbox WHERE payload->>\'environment_id\' = \'x\'`);'
    unshared = 'const r = await db.execute(`SELECT count(*) FROM some_local_table`);'
    json_scoped = ("const r = await db.execute(`SELECT count(*)::int AS n FROM outbox "
                   "WHERE payload->'data'->>'id' = '${m.id}'`);")
    assert len(scan(bad)) == 1, "control 1: a bare whole-table count must be reported"
    assert len(scan(good)) == 0, "control 2: a scoped query must not be reported"
    assert len(scan(unshared)) == 0, "control 3: an unshared table must not be reported"
    assert len(scan(json_scoped)) == 0, "control 4: a JSON-id scope must not be reported"
    nested = "(SELECT count(*) FROM organisations WHERE id = '${body.organisation.id}') AS orgs,"
    assert len(scan(nested)) == 0, "control 5: a scope past a closing quote must not be reported"
    commented = "// This counted `select count(*) from outbox` — every row written by anything."
    assert len(scan(commented)) == 0, "control 6: a query quoted in a comment is not a query"
    joined = ('const q = "SELECT count(*)::int AS n FROM webhook_disable_notifications " +\n'
              '  "WHERE endpoint_id = $1 AND delivered_at IS NULL";')
    assert len(scan(joined)) == 0, "control 7: a scope in the next concatenated literal counts"
    split_bad = 'const q = "SELECT count(*) FROM organisations " + "ORDER BY name";'
    assert len(scan(split_bad)) == 1, "control 8: joining must not hide an unscoped query"
    pinned = 'const q = "SELECT count(*)::int AS n FROM organisations WHERE created_at <= $1";'
    assert len(scan(pinned)) == 0, "control 9: a pinned instant is a scope"
    open_ended = 'const q = "SELECT count(*)::int AS n FROM organisations WHERE name IS NOT NULL";'
    assert len(scan(open_ended)) == 1, "control 10: a predicate that scopes nothing is not a scope"
    print("  controls: 10 of 10 fired")


def main(show_all: bool) -> int:
    controls()
    files = sorted(WT.glob("services/*/src/**/*.itest.ts")) + sorted(WT.glob("packages/*/src/**/*.itest.ts"))
    total, byfile = 0, []
    for p in files:
        hits = scan(p.read_text(encoding="utf-8"))
        if hits:
            total += len(hits)
            byfile.append((p.relative_to(WT), hits))
    for rel, hits in byfile:
        print(f"  {len(hits):>2}  {rel}")
        if show_all:
            for table, stmt in hits:
                print(f"        [{table}] {stmt}")
    print(f"check-lane-scope: {len(files)} integration files, {total} unscoped read(s) "
          f"of a shared table in {len(byfile)} file(s)")
    print("check-lane-scope: SQL text only — a scope applied in JavaScript is invisible to it")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main("--all" in sys.argv))

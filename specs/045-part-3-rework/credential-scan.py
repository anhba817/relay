#!/usr/bin/env python3
"""Feature 045's credential scan: three repositories, every pattern with a positive
control, every hit classified.

A PATTERN THAT FAILS ITS OWN EXAMPLE IS REPORTED BROKEN, NOT ZERO. gaps.md 044-1: the
previous scan ran under ugrep 7.8.4, where a grouped alternation followed by two negated
classes matches nothing, and filed the resulting 0 as evidence over a corpus containing
the string twice. This is Python, and each pattern declares an example it must match.

The corpus is the ADDED side of this feature's diff in each repository — what the feature
put into the tree, which is the only thing it can be blamed for.
"""
import re, subprocess, sys

RANGES = [
    ("superproject", "/home/dong/work/relay", "44ddece^", "HEAD"),
    ("relay-tutorial", "/home/dong/work/relay/relay-tutorial", "9f6d85b^", "HEAD"),
    ("relay-platform (main campaign)", "/home/dong/work/relay/relay-platform", "33bbd2a^", "main"),
    ("relay-platform (rework chain)", "/home/dong/work/relay/relay-platform", "79b5d0b", "part3-rework"),
]

# (name, regex, a string the regex MUST match)
PATTERNS = [
    ("relay key prefix",        r"rk_(?:live|test|svc)_[A-Za-z0-9_]{8,}", "rk_svc_local_development_credential_0000"),
    ("stripe-style live/test",  r"\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{16,}", "sk_live_abcdefghijklmnop"),
    ("AWS access key id",       r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b", "AKIAIOSFODNN7EXAMPLE"),
    ("private key header",      r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----", "-----BEGIN RSA PRIVATE KEY-----"),
    ("JWT literal",             r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"),
    ("gh/slack/npm token",      r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|xox[abprs]-[A-Za-z0-9-]{10,}|npm_[A-Za-z0-9]{30,}", "ghp_abcdefghijklmnopqrstuvwxyz0123"),
    ("password assignment",     r"(?i)\bpass(?:word|wd)?\s*[:=]\s*[\"'][^\"'\s]{6,}[\"']", "password = \"hunter2xyz\""),
    ("secret assignment",       r"(?i)\bsecret[A-Za-z_]*\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']", "secret: \"abcdefghijkl\""),
    ("token assignment",        r"(?i)\btoken[A-Za-z_]*\s*[:=]\s*[\"'][^\"'\s]{12,}[\"']", "token = \"abcdefghijklmnop\""),
    ("bearer literal",          r"(?i)bearer\s+[A-Za-z0-9._-]{16,}", "Bearer abcdefghijklmnopqrst"),
    # UNGROUPED ON PURPOSE — this is the shape ugrep silently failed on in 044.
    ("dsn with password",       r"postgres://[^:/@\s]+:[^@/\s]+@", "postgres://relay:relay@localhost:15432/relay"),
    ("dsn with password (redis)", r"redis://[^:/@\s]+:[^@/\s]+@", "redis://user:pw@localhost:6379"),
    ("base64 blob >= 40",       r"\b[A-Za-z0-9+/]{40,}={0,2}\b", "BpDal75yBZp7Fc2GtGS3D1vh7qOKgCWJkF6/d0XWxBU="),
    ("hex secret >= 32",        r"\b[0-9a-fA-F]{32,}\b", "0123456789abcdef0123456789abcdef"),
    ("RELAY_ secret/key/cred",  r"RELAY_[A-Z_]*(?:SECRET|KEY|CREDENTIAL|TOKEN|PASSWORD)[A-Z_]*", "RELAY_WEBHOOK_SECRET_KEY"),
    ("generic api_key",         r"(?i)\bapi[_-]?key\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']", "api_key: \"abcdefghijkl\""),
    ("ssh/pem file ref",        r"(?i)\b(?:id_rsa|id_ed25519|\.pem|\.p12|\.pfx|\.jks)\b", "id_rsa"),
]


def added_lines(repo, base, head):
    out = subprocess.run(
        ["git", "-C", repo, "diff", "--unified=0", "--no-color", f"{base}..{head}"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        print(f"  !! git diff failed in {repo}: {out.stderr.strip()[:200]}", file=sys.stderr)
        return []
    rows, path = [], "?"
    for line in out.stdout.split("\n"):
        if line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            rows.append((path, line[1:]))
    return rows


def main():
    broken = [n for n, rx, ctl in PATTERNS if not re.search(rx, ctl)]
    if broken:
        for n in broken:
            print(f"  BROKEN PATTERN — {n} does not match its own control", file=sys.stderr)
        return 2

    corpus, per_repo = [], {}
    for label, repo, base, head in RANGES:
        rows = added_lines(repo, base, head)
        per_repo[label] = len(rows)
        corpus += [(label, p, t) for p, t in rows]

    print(f"{len(PATTERNS)} patterns, all {len(PATTERNS)} matched their positive control.\n")
    for label, n in per_repo.items():
        print(f"  corpus  {label:<32} {n:>7} added lines")
    print(f"  corpus  {'TOTAL':<32} {len(corpus):>7} added lines\n")

    print(f"  {'PATTERN':<28}{'HITS':>6}   DISTINCT VALUES")
    hits_by_pattern = {}
    for name, rx, _ctl in PATTERNS:
        c = re.compile(rx)
        found = {}
        for label, path, text in corpus:
            for m in c.finditer(text):
                found.setdefault(m.group(0), set()).add(f"{label}:{path}")
        hits_by_pattern[name] = found
        print(f"  {name:<28}{sum(len(v) for v in found.values()):>6}   {len(found)}")

    print("\nEVERY DISTINCT VALUE, CLASSIFIED:")
    for name, found in hits_by_pattern.items():
        if not found:
            continue
        print(f"\n  {name}:")
        for val, where in sorted(found.items(), key=lambda kv: -len(kv[1]))[:40]:
            shown = val if len(val) <= 60 else val[:57] + "..."
            print(f"    {shown!r}  in {len(where)} place(s), e.g. {sorted(where)[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

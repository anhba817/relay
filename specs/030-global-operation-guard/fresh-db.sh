#!/usr/bin/env bash
# A scratch database, created and migrated, for the steps that have to run against
# one (feature 030, T005).
#
# Every verification step in quickstart.md wants a freshly migrated database,
# because that is the condition CI and a new clone provide and an aged developer
# database does not (research R1). A step that needs six manual commands is a step
# that gets skipped, so this is one.
#
#   ./fresh-db.sh create    # create + migrate, print the URL
#   ./fresh-db.sh drop      # remove it
#   ./fresh-db.sh url       # print the URL without touching anything
#
# DATABASE_URL must point at a reachable server; the scratch database is named
# beside whatever database that URL names.
set -uo pipefail

ADMIN_URL="${DATABASE_URL:?DATABASE_URL must be set}"
SCRATCH_NAME="${RELAY_SCRATCH_DB:-relay_fresh}"
SCRATCH_URL="$(python3 - "$ADMIN_URL" "$SCRATCH_NAME" <<'PY'
import sys
from urllib.parse import urlsplit, urlunsplit
u = urlsplit(sys.argv[1])
print(urlunsplit((u.scheme, u.netloc, "/" + sys.argv[2], u.query, u.fragment)))
PY
)"

PLATFORM="$(cd "$(dirname "$0")/../../relay-platform" && pwd)"
MIGRATE="$PLATFORM/services/api/dist/db/migrate.js"

case "${1:-create}" in
  url)   echo "$SCRATCH_URL" ;;
  drop)  psql "$ADMIN_URL" -q -c "DROP DATABASE IF EXISTS \"$SCRATCH_NAME\"" && echo "dropped $SCRATCH_NAME" ;;
  create)
    # The migration runner is the api's build output, so the build has to exist.
    # Failing here with a sentence beats failing later with a stack trace.
    [ -f "$MIGRATE" ] || { echo "run \`pnpm build\` first — $MIGRATE is missing" >&2; exit 1; }
    psql "$ADMIN_URL" -q -c "DROP DATABASE IF EXISTS \"$SCRATCH_NAME\"" || exit 1
    psql "$ADMIN_URL" -q -c "CREATE DATABASE \"$SCRATCH_NAME\"" || exit 1
    DATABASE_URL="$SCRATCH_URL" node "$MIGRATE" >/dev/null || exit 1
    echo "$SCRATCH_URL"
    ;;
  *) echo "usage: $0 [create|drop|url]" >&2; exit 2 ;;
esac

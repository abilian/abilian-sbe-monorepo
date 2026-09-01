#!/bin/sh
# Wait for the Procfile `web` process to answer, then run the Playwright suite.
# pytest-playwright is not a project dependency -- `uv run --with` layers it on,
# and `playwright install` fetches the browser (both cached after the first run).
set -e

: "${E2E_PORT:=8899}"
BASE_URL="${BASE_URL:-https://127.0.0.1:$E2E_PORT}"
BROWSER="${BROWSER:-chromium}"

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

echo "Waiting for $BASE_URL ..."
i=0
while [ "$i" -lt 90 ]; do
    if curl -fsSk "$BASE_URL/" >/dev/null 2>&1; then
        echo "Server is up."
        break
    fi
    i=$((i + 1))
    sleep 1
done

uv run --with pytest-playwright playwright install "$BROWSER" >/dev/null 2>&1 || true
exec uv run --with pytest-playwright pytest e2e_playwright \
    -v --browser "$BROWSER" --base-url "$BASE_URL"

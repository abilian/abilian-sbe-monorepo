# End-to-end tests

Browser tests for the things the pytest suite structurally cannot see.

A page whose scripts never loaded, whose widgets never initialised, or whose
icon font is missing still returns a perfectly good 200. That is how the
Tailwind branch came to ship with no icons, no DataTables and a dead documents
module while `pytest` stayed green.

## Running

```bash
make test-e2e
# or:
cd e2e_playwright && honcho start
```

`honcho` starts three processes and exits with pytest's status when the suite
finishes, tearing the others down:

| process | what it does |
|---|---|
| `redis` | throwaway instance on port 6399, persistence off, so your own redis and its data are untouched |
| `web`   | `serve.sh`: recreates a SQLite database under `$E2E_DIR`, creates an admin user, serves on 8899 |
| `tests` | `run_tests.sh`: waits for the server, then runs pytest |

`pytest-playwright` is **not** a project dependency. `uv run --with` layers it
on and `playwright install` fetches the browser; both are cached after the first
run.

Overridable: `E2E_DIR`, `E2E_PORT`, `E2E_REDIS_PORT`, `E2E_EMAIL`,
`E2E_PASSWORD`, `BROWSER`, `BASE_URL`.

## Why it runs over HTTPS with debug off

Debug mode would point `vite_asset` at a Vite dev server that isn't running, so
the suite would test the wrong asset path — the production one is what ships and
what broke. With debug off, Talisman turns on, and it forces HTTPS; `serve.sh`
therefore serves TLS with a throwaway certificate, which the browser context
ignores.

## Known failure: CSP blocks every inline script

Talisman applies its default `default-src 'self'` policy, and neither the app
nor any deploy config overrides it. The base template ships inline `<script>`
blocks — the AMD shim, `abilian_init.js`, the deferred JS — so the browser
blocks all of them and **no legacy JavaScript runs in production at all**.

This predates the Tailwind branch: `devel` has the same inline scripts under the
same policy.

The tests that need JavaScript to execute are marked `xfail(strict=True)`, so
they stay visible and will fail loudly as unexpected passes once the policy is
fixed — at which point drop the marker.

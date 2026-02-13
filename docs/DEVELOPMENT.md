# Development

## Dev Container (optional)

VS Code or Cursor can run the repo inside a container so lint and test work without installing shellcheck/ruff/pytest on the host.

**Prerequisites:** [Dev Containers extension](https://code.visualstudio.com/docs/devcontainers/containers), Docker or Podman.

- **"Failed to reopen folder in container" / `docker info` exit code 1:** The Docker **daemon** is not running. On macOS, start **Docker Desktop** (Applications or Spotlight). Ensure the menu bar shows Docker as running; then run **Reopen in Container** again. If the Server section of `docker info` is empty, the engine is down—use Docker menu → **Troubleshoot → Restart Docker Desktop**. See [Docker Desktop troubleshoot](https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/).

1. Clone the repo and open the folder in VS Code/Cursor.
2. When prompted **Reopen in Container** (or Command Palette → **Dev Containers: Reopen in Container**), accept.
3. The container installs shellcheck, Python deps (`requirements.txt`), ruff, and pytest. Workspace is `/workspace` (repo root).
4. Inside the container: `make lint`, `make test`, and `make start` (Docker from host may need to be exposed; see your OS setup).

This matches the pattern used by [IBM MCP Context Forge](https://github.com/IBM/mcp-context-forge) (clone → code . → Reopen in Container). Our container does not run the gateway itself; use the host’s `make start` or run Docker from inside the container if Docker-in-Docker is configured.

## Local dev loop

1. Edit `scripts/gateways.txt`, `scripts/prompts.txt`, or `.env`.
2. `make start` (or `make gateway-only` for gateway only).
3. `make register`; optionally `make list-prompts` to verify prompts.
4. Test in Cursor with the URL from `make register` or Admin UI. Use the [Automatic JWT wrapper](../README.md#connect-cursor) for context-forge.

## Adding a gateway

- **No auth:** Add `Name|URL` or `Name|URL|Transport` to `scripts/gateways.txt`, or `EXTRA_GATEWAYS` in `.env`. Run `make register`.
- **Auth (API key, OAuth):** Add in Admin UI → edit gateway → Passthrough Headers or OAuth. See [ADMIN_UI_MANUAL_REGISTRATION.md](ADMIN_UI_MANUAL_REGISTRATION.md).

~60 tools per Cursor connection: use `scripts/virtual-servers.txt` (one server per line: `ServerName|gateway1,gateway2,...`), then `make register`. See [AI_USAGE.md – Tool limit](AI_USAGE.md#tool-limit-and-virtual-servers). Duplicate servers: `make cleanup-duplicates` (`CLEANUP_DRY_RUN=1` to report only).

## Prompts / resources

Format: prompts `name|description|template` ({{arg}}, `\n`); resources `name|uri|description|mime_type`. Set `REGISTER_PROMPTS=true` or `REGISTER_RESOURCES=true`, edit `scripts/prompts.txt` or `scripts/resources.txt`, run `make register`. See [scripts/README.md](../scripts/README.md) and `.env.example`.

## Troubleshooting

[README – Troubleshooting](../README.md#troubleshooting). SQLite corruption: [data/README.md](../data/README.md#recovery-from-sqlite-corruption).

## Pre-commit

Pre-commit runs secret detection (gitleaks), private-key detection, YAML/JSON checks, trailing-whitespace/EOF fixers, large-file check, merge-conflict check, and Ruff on `tool_router/` before each commit. CI still runs full lint, test, Trufflehog secret scan, and Trivy (see [.cursor/rules/security-secrets.mdc](../.cursor/rules/security-secrets.mdc)).

1. Install pre-commit: `pip install pre-commit` or `pip install -e ".[dev]"` (adds pre-commit from pyproject.toml dev deps).
2. Install the git hook: `make pre-commit-install` or `pre-commit install`.
3. (Optional) Run on the whole repo once: `pre-commit run --all-files`.

The gitleaks hook uses the default `gitleaks` id so pre-commit installs the binary; no need to install gitleaks on the system. To use a system-installed gitleaks instead, change the hook id to `gitleaks-system` in `.pre-commit-config.yaml` and install gitleaks (e.g. `brew install gitleaks` on macOS).

## Next steps (after setup)

- **CI:** Runs on push/PR (lint, test, build, Trivy image scan, smoke, secret scan). Trufflehog is pinned to `v3.93.3` in [.github/workflows/ci.yml](../.github/workflows/ci.yml). Trivy scans the tool-router image (fail on CRITICAL/HIGH) and the gateway image `ghcr.io/ibm/mcp-context-forge:1.0.0-RC-1` (report only; upstream image).
- **Lint/test locally:** Install shellcheck and ruff (e.g. `brew install shellcheck`, `pip install ruff`), then `make lint` and `make test`; or use the Dev Container above.
- **Gateway updates:** Watch [IBM/mcp-context-forge](https://github.com/IBM/mcp-context-forge) releases; update the gateway image tag in `docker-compose.yml` and `scripts/cursor-mcp-wrapper.sh` when upgrading.
- **Python deps:** Bump versions in `requirements.txt` / `pyproject.toml` and run `make test`; rebuild tool-router image if needed.
- **Cursor:** Keep `GATEWAY_JWT` set for cursor-router; run `make verify-cursor-setup` if the IDE shows "Error" or "No server info found".

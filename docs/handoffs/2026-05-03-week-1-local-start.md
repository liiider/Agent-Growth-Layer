# Handoff: Week 1 Local Start

Date: 2026-05-03

## Scope

Implemented the PRD Week 1 / V0.1 local-start baseline:

- Project skeleton
- SQLite initialization
- Docker Compose configuration
- Seed Skill YAML schema documentation
- Eight built-in Seed Skill templates
- `POST /v1/guidance`
- `GET /v1/seed-skills`
- `GET /v1/seed-skills/{id}`
- Minimal README and quickstart docs
- Python SDK with `guidance.to_prompt()`

## Code Changes

- Added stable SDK import path: `from agent_growth import AgentGrowthClient, Guidance`.
- Updated package discovery so `agent_growth` installs from `sdk/python/agent_growth`.
- Added schema-focused tests for all seed skill templates.
- Added `docs/seed-skill-schema.md`.
- Added `docs/architecture/reference-project-lessons.md` to record lessons from Mem0, LangMem, MemAlign, skill registries, and eval-loop systems.
- Updated README references for schema and handoff notes.

## Problems Encountered

1. Python was not available inside the sandbox path.
   - Resolution: ran Python commands in the real Windows environment with escalation.
   - Avoid repeating: if sandbox says `python` is missing, treat it as path isolation, not missing Python.

2. SDK package initially only imported through `sdk.python.agent_growth`.
   - Resolution: changed package discovery and imports so installed users can import `agent_growth`.
   - Verification: `python -c "from agent_growth import AgentGrowthClient, Guidance; print(...)"`.

3. Ruff flagged import ordering after SDK import changes.
   - Resolution: ran `python -m ruff check . --fix`, then reran lint and tests.
   - Avoid repeating: run lint after packaging/import changes.

4. Docker Compose startup could not be completed because Docker Desktop daemon was not running.
   - Error: `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`.
   - Resolution: verified `docker compose config` earlier and verified the app via local `uvicorn`.
   - Remaining action: start Docker Desktop, then rerun `docker compose up --build`.

5. Verification generated caches and SQLite data.
   - Resolution: moved generated artifacts to `D:\temp\agent-growth-layer-generated-20260503-121353`.
   - Avoid repeating: keep `.gitignore` entries for caches and `data/`.

## Verification Performed

Local tests:

```powershell
python -m pytest
```

Result: 6 passed.

Lint:

```powershell
python -m ruff check .
```

Result: all checks passed.

Compile check:

```powershell
python -m compileall server sdk
```

Result: passed.

Editable install:

```powershell
python -m pip install -e ".[dev]"
```

Result: package installed successfully.

SDK import:

```powershell
python -c "from agent_growth import AgentGrowthClient, Guidance; print(AgentGrowthClient.__name__, Guidance.__name__)"
```

Result: `AgentGrowthClient Guidance`.

Local HTTP server:

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Verified:

- `GET /health` returned `ok`.
- `POST /v1/guidance` returned 8 seed skills.
- First returned seed skill in current sort order: `seed_code_change_checklist`.

Docker:

```powershell
docker compose up --build -d
```

Result: failed because Docker Desktop daemon was not running. This is an environment issue, not an application failure.

## Current Status

Week 1 application behavior is implemented and locally verified outside Docker. The only unverified acceptance item is actual `docker compose up --build`, blocked by Docker Desktop not running.

## Next Stage

Start Week 2 / V0.1 completion:

- Improve `guidance.to_prompt()` formatting against the PRD examples.
- Add prompt import scaffolding if still considered V0.1 scope.
- Expand customer support example into a runnable script.
- Add API docs for guidance response shape.
- Re-run Docker verification once Docker Desktop is available.

Architecture constraints to preserve:

- No vector database or registry network lookup in V0.1 guidance assembly.
- No model call in `POST /v1/guidance` for V0.1.
- Keep extraction/eval work outside the request-critical guidance path.
- Require evidence and explicit state transitions before candidate guidance becomes verified guidance.

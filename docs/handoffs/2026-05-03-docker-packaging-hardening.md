# Handoff: Docker and Packaging Hardening

Date: 2026-05-03

## Scope

Hardened Docker and packaging paths:

- Fixed Dockerfile source copy order before `pip install .`.
- Added `.dockerignore`.
- Added tests for Dockerfile install order and generated-output exclusions.
- Verified editable Python package install.

## Problem Found

The previous Dockerfile ran:

```dockerfile
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .
COPY server ./server
COPY sdk ./sdk
```

This is risky because setuptools package discovery needs the `server/` and `sdk/python/agent_growth/` source trees to exist before `pip install .`.

## Fix

Dockerfile now copies source before installing:

```dockerfile
COPY pyproject.toml README.md ./
COPY server ./server
COPY sdk ./sdk
COPY templates ./templates
RUN pip install --no-cache-dir .
```

Added `.dockerignore` entries for:

- `.git`
- cache directories
- `data`
- JS `node_modules`
- JS `dist`
- egg-info

## Verification Performed

Targeted tests:

```powershell
python -m pytest tests/test_packaging_files.py
```

Result: 2 passed.

Editable package install:

```powershell
python -m pip install -e ".[dev]"
```

Result: passed.

Full tests:

```powershell
python -m pytest
```

Result: 22 passed.

Lint:

```powershell
python -m ruff check .
```

Result: passed.

Compile:

```powershell
python -m compileall server sdk examples
```

Result: passed.

JavaScript:

```powershell
npm.cmd ci
npm.cmd run build
```

Result: passed.

Docker config:

```powershell
docker compose config
```

Result: passed, with Docker config access warnings.

Docker runtime:

```powershell
docker compose up --build -d
```

Result: still blocked because Docker Desktop daemon is not running.

## Remaining Work

Start Docker Desktop and run:

```powershell
docker compose up --build -d
```

Then verify:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

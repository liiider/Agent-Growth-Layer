# Handoff: Local MVP Verification

Date: 2026-05-03

## Scope

Added one-command local MVP verification:

- `scripts/verify_local_mvp.py`
- `scripts/verify_local_mvp.ps1`
- README local MVP verification instructions

## What The Script Verifies

The PowerShell wrapper starts the FastAPI app on `127.0.0.1:8000`, runs the Python verifier, then stops the server.

Verified chain:

1. `GET /health`
2. `POST /v1/guidance`
3. `POST /v1/experiences`
4. `GET /v1/experiences/{id}`
5. `GET /v1/cognitions/{id}`
6. `POST /v1/feedback`
7. `POST /v1/skills/import_prompt`
8. `POST /v1/skills/build`
9. `POST /v1/skills/{skill_id}/exam`
10. `GET /v1/audit/skill/{skill_id}`
11. `POST /v1/guidance` with verified skill assertion

## Verification Performed

Local MVP script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_local_mvp.ps1
```

Result:

```text
health: ok
seed guidance: 6 seed skills
experience learning: exp_b90da2550a27 -> cog_8d38c6d80a4b
feedback: fb_f0a8ab2a304b
prompt import: skill_imported_29d3b32f079e
skill exam: skill_2ee3400e28ec -> verified
audit: skill_2ee3400e28ec
verified guidance: ok
Local MVP verification passed.
```

Full tests:

```powershell
python -m pytest
```

Result: 23 passed.

Lint:

```powershell
python -m ruff check .
```

Result: passed.

Compile:

```powershell
python -m compileall server sdk examples scripts
```

Result: passed.

JavaScript:

```powershell
npm.cmd ci
npm.cmd run build
```

Result: passed.

## Problems Encountered

No code issues in this stage.

The script uses `powershell -ExecutionPolicy Bypass -File` during validation because local script execution policy can block `.ps1` execution on Windows. The wrapper itself does not write secrets or destructive files.

## Current Status

Local non-Docker MVP is verified end-to-end.

Docker runtime remains the remaining local MVP environment validation because Docker Desktop daemon is not running.

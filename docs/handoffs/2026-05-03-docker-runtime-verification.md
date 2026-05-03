# Docker Runtime Verification Handoff

## Stage Goal

Validate that the local MVP runs as a packaged Docker service, not only through in-process
tests or a local Uvicorn process.

## Expected Effect

- Docker Compose can build the API image from the repository.
- The container starts and exposes `GET /health` on `127.0.0.1:8000`.
- The full MVP verification chain passes against the container:
  health -> guidance -> experience learning -> feedback -> prompt import -> skill build ->
  skill exam -> audit -> verified guidance.

## Work Completed

- Confirmed Docker Desktop is available for the real Windows user.
- Rebuilt and started the service with `docker compose up --build -d`.
- Fixed `scripts/verify_local_mvp.py` to wait for asynchronous experience extraction.
- Added `tests/test_local_mvp_verifier.py` to cover the polling behavior.
- Stopped the Compose service after validation.
- Moved generated artifacts to `D:\temp\agent-growth-layer-generated-20260503-173757`.

## Issues Found

1. The sandbox user cannot access Docker Desktop.
   - Non-escalated Docker commands run as `HOME-PC\CodexSandboxOffline`.
   - That user cannot access the Docker API pipe or `C:\Users\MOREFINE\.docker\config.json`.
   - Resolution: Docker commands for this project must run with escalation as the real user.

2. The local MVP verifier assumed extraction finished immediately.
   - In FastAPI `TestClient`, background tasks complete before assertions in current tests.
   - In a real Uvicorn container, the response can return before the background extraction task
     has persisted `succeeded`.
   - Resolution: the verifier now polls the experience until `succeeded`, fails immediately on
     `failed`, and times out with the last observed status.

## Verification

- `docker version`
  - Result: passed with escalation.
  - Docker Desktop 4.71.0, Engine 29.4.1, context `desktop-linux`.

- `docker compose up --build -d`
  - Result: passed.
  - Image `agentgrowthlayer-api:latest` built successfully.
  - Container `agentgrowthlayer-api-1` started on `0.0.0.0:8000`.

- `Invoke-RestMethod http://127.0.0.1:8000/health`
  - Result: passed.
  - Response: `{"status":"ok"}`.

- `python scripts/verify_local_mvp.py --base-url http://127.0.0.1:8000`
  - Initial result: failed at experience extraction because status had not yet reached
    `succeeded`.
  - Final result after verifier polling fix: passed.
  - Verified chain output included:
    - `health: ok`
    - `seed guidance: 6 seed skills`
    - `experience learning: exp_605ab56968c1 -> cog_a9a2b5abe2b0`
    - `feedback: fb_3e7a2c1ff248`
    - `prompt import: skill_imported_2becb11c2d3d`
    - `skill exam: skill_34e0b46e68e4 -> verified`
    - `audit: skill_34e0b46e68e4`
    - `verified guidance: ok`
    - `Local MVP verification passed.`

- `python -m pytest tests/test_local_mvp_verifier.py`
  - Result: passed, 1 test.

- `docker compose down`
  - Result: passed.
  - Container and project network removed.

## Remaining Notes

- Docker runtime is now validated for the local MVP.
- The container still uses SQLite on a bind-mounted `./data` path, which is acceptable for local
  MVP validation but not the final multi-user hosted architecture.
- LLM provider integration remains intentionally BYOK. For the GLM validation stage, the user will
  provide API credentials and we should keep those credentials in environment variables only.

# Contributing

Agent Growth Layer is local-first and framework agnostic. Keep changes narrow, tested, and evidence-backed.

## Development Setup

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m compileall server sdk examples
```

For the JavaScript SDK:

```powershell
cd sdk/javascript
npm.cmd ci
npm.cmd run build
```

Use `npm.cmd` on Windows if PowerShell blocks `npm.ps1`.

## Design Constraints

- Do not add model calls to `POST /v1/guidance`.
- Do not add Redis, vector storage, or registry live lookup to the guidance hot path.
- Candidate guidance must include `status`, `weight`, and `evidence_refs`.
- Verified guidance must have exam or manual validation evidence.
- Quarantined skills must never enter guidance.

## Verification Before Completion

Run:

```powershell
python -m pytest
python -m ruff check .
python -m compileall server sdk examples
```

If JS SDK files changed, also run:

```powershell
cd sdk/javascript
npm.cmd ci
npm.cmd run build
```

If Docker Desktop is running, also run:

```powershell
docker compose up --build -d
Invoke-RestMethod http://localhost:8000/health
```

## Handoff Notes

For each completed stage, add a file under `docs/handoffs/` with:

- scope
- implementation notes
- problems encountered
- verification commands and results
- remaining work

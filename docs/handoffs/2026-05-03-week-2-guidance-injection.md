# Handoff: Week 2 Guidance Injection

Date: 2026-05-03

## Scope

Implemented the guidance injection baseline for developers integrating Agent Growth Layer into their own agents.

This stage deliberately did not implement:

- Experience ingestion
- Cognition extraction
- Skill build
- Exams
- Registry integration
- Vector search
- Model calls in `POST /v1/guidance`

## Intended Effect

Developers should be able to:

- Request guidance from the REST API.
- Use the Python SDK with `from agent_growth import AgentGrowthClient`.
- Convert returned guidance into an injectable prompt with `guidance.to_prompt()`.
- See candidate skills clearly marked as unverified.
- See verified skills with exam score when present.
- Run a customer support example that returns support-relevant seed guidance.

## Code Changes

- Expanded `Guidance.to_prompt()` formatting for:
  - candidate skill caution labels
  - candidate weight
  - verified skill labels
  - verified exam score
  - evidence references
- Added tests for candidate and verified prompt rendering.
- Added `examples/customer_support/run.py`.
- Added `docs/api.md`.
- Updated API docs to state domain-aware seed skill selection.
- Updated guidance builder to filter seed skills by request domain, with `general` skills as fallback.

## Problems Encountered

1. Formatter did not distinguish candidate and verified skill titles.
   - Symptom: tests expecting `[Caution: unverified, low weight]` and `[Verified, exam score: 0.86]` failed.
   - Fix: added status-aware skill title rendering in the SDK.
   - Verification: `python -m pytest tests/test_python_sdk.py`.

2. Customer support example initially returned `Code Change Checklist` first.
   - Cause: guidance builder returned every seed skill without domain filtering.
   - Risk: prompt bloat and irrelevant guidance in the request hot path.
   - Fix: domain-matching seed skills are returned first; `general` skills are included as fallback; unrelated domain-specific skills are excluded.
   - Verification: added `test_guidance_filters_seed_skills_by_domain` and reran the customer support example.

3. Docker Desktop remains unavailable.
   - Error remains the same as the Week 1 handoff: Docker daemon pipe is missing.
   - Workaround: verified application behavior through local `uvicorn` and real SDK HTTP calls.

## Verification Performed

Targeted SDK formatter tests:

```powershell
python -m pytest tests/test_python_sdk.py
```

Result: passed.

Targeted guidance API tests:

```powershell
python -m pytest tests/test_guidance_api.py
```

Result: passed.

Full tests:

```powershell
python -m pytest
```

Result: 8 passed.

Lint:

```powershell
python -m ruff check .
```

Result: passed.

Compile check:

```powershell
python -m compileall server sdk examples
```

Result: passed.

Customer support example:

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
python examples/customer_support/run.py --message "Why was my refund rejected?"
```

Verified:

- Example rendered `Runtime Guidance`.
- `Verified Skills` and `Candidate Skills` were `None`.
- First seed skill was `Customer Support Resolution`.

## Current Status

Week 2 guidance injection baseline is implemented and verified locally outside Docker.

## Next Stage

Recommended next stage: Prompt Import scaffolding or API documentation hardening.

Before implementing experience learning, keep the architecture constraints from `docs/architecture/reference-project-lessons.md`:

- No model calls in the guidance hot path.
- No vector DB in V0.1.
- No registry network lookup in guidance assembly.
- Candidate guidance must remain clearly labeled as unverified.

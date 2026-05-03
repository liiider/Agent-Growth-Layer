# Python SDK Surface Handoff

## Stage Goal

Make the Python SDK useful for the full local MVP loop, not only guidance and experience
creation.

## Expected Effect

Python users can call the V0.1-V0.3 REST surface through `AgentGrowthClient`:

- guidance
- experiences
- feedback
- cognitions
- skills
- exams
- audit

This moves the project closer to a reusable engineering package similar in ergonomics to
memory-layer projects such as mem0, while keeping the implementation source-only for now.

## Work Completed

- Added shared SDK HTTP helper: `agent_growth.http.HttpResource`.
- Added Python SDK resource clients:
  - `FeedbackClient`
  - `CognitionsClient`
  - `SkillsClient`
  - `AuditClient`
- Expanded `ExperiencesClient` with:
  - `get`
  - `retry_extraction`
- Expanded `AgentGrowthClient` with:
  - configurable `timeout`
  - `feedback`
  - `cognitions`
  - `skills`
  - `audit`
- Updated exports in `agent_growth.__init__`.
- Updated README, API docs, and PRD coverage.

## Issues Found

1. Python SDK had a narrower surface than the service.
   - Existing SDK only supported `get_guidance` and `experiences.create`.
   - Resolution: added resource clients for the remaining V0.1-V0.3 surfaces.

2. SDK timeout was hardcoded.
   - Resolution: `AgentGrowthClient(..., timeout=10)` now propagates timeout to resource clients
     and guidance requests.

## Verification

- `python -m pytest tests/test_python_sdk.py`
  - Initial result: failed because `feedback/cognitions/skills/audit` and configurable timeout
    did not exist.
  - Final result: passed, 5 tests.

## Remaining Notes

- The SDK still returns raw JSON dictionaries for non-guidance APIs. This keeps the surface simple
  and avoids locking public typed models too early.
- Packaging/publishing decisions remain separate: the Python package installs locally now, but we
  have not prepared release automation for PyPI.

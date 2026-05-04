# Real Project MVP Harness Handoff

## Stage Goal

Move MVP verification beyond API-level checks by simulating Agent Growth Layer inside a complete
project workflow, with explicit human intervention points.

## Expected Effect

The project now validates this stricter loop:

1. project coding agent requests initial guidance
2. a realistic project task produces an experience
3. the experience is reviewed as useful learning evidence
4. extraction creates cognition
5. cognition is reviewed and approved
6. skill is built from cognition
7. exam passes but stops at `needs_review`
8. human review approves the skill
9. the next guidance response contains the verified skill

## Work Completed

- Added `POST /v1/reviews`.
- Added persisted `reviews` table.
- Added review models and repository.
- Added skill status `needs_review`.
- Added `require_human_review` to exam requests.
- Added review behavior:
  - experience reviews are recorded
  - cognition approve/reject/quarantine updates cognition status
  - skill approval requires a passing exam
  - skill reject/quarantine updates skill status
- Added Python SDK `client.reviews.create(...)`.
- Added JavaScript SDK `reviews.create(...)`.
- Added `scripts/verify_project_mvp.py`.
- Added tests:
  - `tests/test_review_gate.py`
  - `tests/test_project_mvp_verifier.py`

## Issues Found

1. The previous MVP checks verified the technical chain but not the project decision chain.
   - Missing: explicit review of whether an experience/cognition/skill should be trusted.
   - Resolution: added review API and project-level harness.

2. Passing exams previously promoted directly to `verified`.
   - Risk: LLM judge or deterministic score could promote high-risk skills without human review.
   - Resolution: `require_human_review=true` makes a passing exam set `needs_review`.

3. Human review existed only as an informal concept.
   - Resolution: review decisions are now persisted through API and available in Python/JS SDKs.

## Verification

- `python -m pytest tests/test_review_gate.py`
  - Result: passed, 4 tests.

- `python -m pytest tests/test_project_mvp_verifier.py`
  - Result: passed, 1 test.

- Real local project MVP harness:
  - Command: `python scripts/verify_project_mvp.py --base-url http://127.0.0.1:8000`
  - Result: passed.
  - Observed output:
    - `project initial guidance: 5 seed skills`
    - `project experience: exp_b238ac28b2a1 -> cog_44b01495b087`
    - `project experience review: rev_a2599de2be80`
    - `project cognition review: cog_44b01495b087 -> verified`
    - `project skill build: skill_580c83ff2069`
    - `project exam: skill_580c83ff2069 -> needs_review`
    - `project skill review: skill_580c83ff2069 -> verified`
    - `project verified guidance: ok`

- `docker compose build`
  - Result: not completed in this stage.
  - Reason: Docker Desktop daemon was unavailable:
    `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`.
  - Interpretation: environment issue, not an application test failure. Docker build passed in the
    prior DeepSeek validation stage before these review-gate changes.

- Generated artifact cleanup
  - Result: not moved in this stage.
  - Reason: bulk move to `D:\temp` was blocked by the safety policy because exact target paths had
    not been explicitly approved first.
  - Git status confirms generated directories are ignored and were not staged.

## Remaining Notes

- This is still a simulated project workflow, not yet a live integration with an external coding
  agent runtime.
- The next stricter stage should capture actual task artifacts: prompt used, diff, tests, command
  outputs, human assessment, and before/after project value signals.

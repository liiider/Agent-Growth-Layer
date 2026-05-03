# PRD Coverage

Date: 2026-05-03

## Implemented

V0.1:

- SQLite
- Docker Compose configuration
- Seed Skill YAML schema
- Seed Skill templates
- `POST /v1/guidance`
- Real-time guidance builder
- `guidance.to_prompt()`
- Python SDK foundation
- README Quickstart
- Customer support example
- OpenAI-compatible LLM configuration docs
- BYOK / Ollama / Qwen examples

V0.2:

- `POST /v1/experiences`
- `GET /v1/experiences/{id}`
- `POST /v1/experiences/{id}/extract`
- `GET /v1/cognitions`
- `GET /v1/cognitions/{id}`
- `PATCH /v1/cognitions/{id}/status`
- Feedback API
- Evidence refs
- Candidate guidance
- Prompt Import API
- JavaScript SDK minimum source for guidance and experiences

V0.3:

- `POST /v1/skills/build`
- `GET /v1/skills`
- `GET /v1/skills/{id}`
- `PATCH /v1/skills/{id}`
- `PATCH /v1/skills/{id}/status`
- `POST /v1/skills/{skill_id}/exam`
- Skill status transitions
- Manual score exam runner
- Latest exam on skill responses
- Verified guidance
- Audit API
- Coding agent example notes
- Enterprise QA example notes
- JavaScript SDK skill/exam source

## Implemented With Deterministic Local Stubs

- Cognition extraction uses a deterministic local extractor instead of LLM extraction.
- Prompt import uses deterministic sentence parsing instead of LLM prompt parsing.
- Exam supports deterministic manual score; `llm_judge` is accepted as an evaluator label but does not call an LLM.

These choices preserve local-first operation and stable tests.

## Not Yet Fully Verified In This Environment

- `docker compose up --build`: Docker Desktop daemon is not running.
- JavaScript SDK TypeScript build: `tsc` is not installed.

## Deliberately Out Of MVP Scope

- Redis
- Separate worker process
- Vector database
- Graph cognition
- Multi-tenant permissions
- Dashboard
- Prompt versioning
- Automatic re-exam
- External skill registry live lookup
- `GET /v1/exams/{exam_id}`

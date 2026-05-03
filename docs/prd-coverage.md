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
- BYOK OpenAI-compatible LLM adapter seam for extraction, prompt import, and `llm_judge`

## Implemented With Deterministic Local Defaults

- Cognition extraction uses deterministic local extraction unless `AGL_LLM_PROVIDER=openai_compatible`.
- Prompt import uses deterministic sentence parsing unless `AGL_LLM_PROVIDER=openai_compatible`.
- Exam supports deterministic manual score. `llm_judge` calls the configured BYOK client only when no manual score is supplied.

These choices preserve local-first operation and stable tests.

## Verified In This Environment

- `docker compose up --build -d`
- Docker container health check
- Full Docker-backed local MVP verification chain
- JavaScript SDK TypeScript build through `npm.cmd run build`

## Not Yet Fully Verified In This Environment

- Real external GLM/OpenAI-compatible API behavior. This requires a user-provided temporary API key.

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

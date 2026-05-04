# Agent Growth Layer

[![CI](https://github.com/liiider/Agent-Growth-Layer/actions/workflows/ci.yml/badge.svg)](https://github.com/liiider/Agent-Growth-Layer/actions/workflows/ci.yml)

Agent Growth Layer gives AI agents runtime guidance that improves from real experience.

Agent Growth Layer is an open-source runtime guidance layer for AI agents. It helps an agent start with reusable seed guidance, then grow toward better behavior from real tasks, user feedback, corrections, and verification.

The project is framework agnostic: it does not orchestrate your agent. It gives your agent structured guidance that can be injected into the runtime prompt.

## What It Does

- Provides cold-start seed guidance for common agent behaviors.
- Returns structured runtime guidance through a REST API.
- Converts guidance into a system-prompt-friendly format with `guidance.to_prompt()`.
- Runs locally with SQLite and Docker Compose.
- Keeps V0.1 simple: no Redis, no external SaaS dependency, no vector database.

## Current Scope

This repository currently implements the PRD's V0.1 through V0.3 core milestones:

- FastAPI service
- SQLite initialization
- Seed Skill YAML schema
- Seed Skill templates
- `POST /v1/guidance`
- `GET /v1/seed-skills`
- Experience learning
- Cognition extraction
- Feedback API
- Prompt import
- Skill builder
- Manual exam runner
- Verified guidance
- Audit API
- Python SDK for guidance, experiences, feedback, cognitions, skills, exams, and audit
- JavaScript/TypeScript SDK minimum source
- `guidance.to_prompt()`
- Human review gate for cognition and skill promotion
- Project-level MVP scenario verifier
- Docker Compose local startup
- Customer support, coding agent, and enterprise QA examples
- BYOK OpenAI-compatible LLM adapter for extraction, prompt import, and `llm_judge`

## Quickstart

Start the API:

```powershell
docker-compose up --build
```

Request cold-start guidance:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/v1/guidance `
  -ContentType "application/json" `
  -Body '{
    "agent_id": "support_agent",
    "domain": "customer_support",
    "intent": "refund_question",
    "context": {"message": "我要退款，为什么不给退？"},
    "risk_level": "medium"
  }'
```

The response includes `verified_skills`, `candidate_skills`, and `seed_skills`. In V0.1, cold-start guidance is built from seed skills.

## Python SDK

Install the project locally:

```powershell
python -m pip install -e ".[dev]"
```

Use the SDK:

```python
from agent_growth import AgentGrowthClient

client = AgentGrowthClient("http://localhost:8000")
guidance = client.get_guidance(
    agent_id="support_agent",
    domain="customer_support",
    intent="refund_question",
    context={"message": "Why was my refund rejected?"},
    risk_level="medium",
)

system_prompt = guidance.to_prompt()
print(system_prompt)
```

Use the SDK for the full local MVP loop:

```python
experience = client.experiences.create(
    agent_id="support_agent",
    domain="customer_support",
    intent="refund_question",
    user_input="Why was my refund rejected?",
    agent_output="Refunds are not available after seven days.",
    feedback="Must confirm region and order status before applying refund rules.",
    result_status="corrected",
    risk_level="medium",
)
experience_id = experience["experience_id"]
tracked = client.experiences.get(experience_id)
cognition_id = tracked["cognition_ids"][0]

client.feedback.create(
    experience_id=experience_id,
    feedback_type="human_corrected",
    content="Also check region-specific policy.",
    score=0.2,
)

skill = client.skills.build(
    agent_id="support_agent",
    domain="customer_support",
    intent="refund_question",
    name="Refund Policy Handling",
    cognition_ids=[cognition_id],
)["skill"]

client.skills.run_exam(skill["id"], score=0.9)
client.reviews.create(
    object_type="skill",
    object_id=skill["id"],
    decision="approve",
    reviewer="project_owner",
    notes="Passing exam and project owner review approve this skill.",
)
audit = client.audit.get("skill", skill["id"])
```

## JavaScript SDK

The V0.2 JavaScript SDK source lives in `sdk/javascript`.

```ts
import { AgentGrowthClient } from './src'

const client = new AgentGrowthClient('http://localhost:8000')
const guidance = await client.guidance.get({
  agent_id: 'support_agent',
  domain: 'customer_support',
  intent: 'refund_question',
  context: { message: 'Why was my refund rejected?' },
  risk_level: 'medium',
})

const result = await client.experiences.create({
  agent_id: 'support_agent',
  domain: 'customer_support',
  intent: 'refund_question',
  user_input: 'Why was my refund rejected?',
  agent_output: 'Refunds are not available after seven days.',
  feedback: 'Must confirm region and order status before applying refund rules.',
  result_status: 'corrected',
  risk_level: 'medium',
})
```

## Local Development

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m compileall server sdk
uvicorn server.main:app --reload
```

## Local MVP Verification

Run the full local MVP chain:

```powershell
.\scripts\verify_local_mvp.ps1
```

This starts the API locally, then verifies:

- health
- seed guidance
- experience learning
- cognition extraction
- feedback
- prompt import
- skill build
- exam promotion
- audit
- verified guidance

## API

- `POST /v1/guidance`
- `GET /v1/seed-skills`
- `GET /v1/seed-skills/{id}`
- `POST /v1/experiences`
- `GET /v1/experiences/{id}`
- `POST /v1/experiences/{id}/extract`
- `GET /v1/cognitions`
- `GET /v1/cognitions/{id}`
- `PATCH /v1/cognitions/{id}/status`
- `POST /v1/skills/build`
- `GET /v1/skills`
- `GET /v1/skills/{id}`
- `PATCH /v1/skills/{id}`
- `PATCH /v1/skills/{id}/status`
- `POST /v1/skills/{id}/exam`
- `POST /v1/reviews`
- `GET /v1/audit/{object_type}/{object_id}`
- `GET /health`

See `docs/api.md` for request and response examples.

## Seed Skills

Seed skills live in `templates/seed_skills/` and are loaded from YAML at runtime.
The stable V0.1 schema is documented in `docs/seed-skill-schema.md`.

Included seed skills:

- Uncertainty Handling
- Permission Sensitive Answering
- Feedback Aware Response
- Tool Result Checking
- Code Change Checklist
- Customer Support Resolution
- Policy Answering
- Medical Safety Boundary

## Configuration

Copy `.env.example` to `.env` when you need local overrides.

```env
AGL_DATABASE_URL=sqlite:///./data/agent_growth_layer.db
AGL_SEED_SKILLS_DIR=./templates/seed_skills
AGL_LLM_PROVIDER=deterministic
AGL_LLM_BASE_URL=
AGL_LLM_API_KEY=
AGL_LLM_MODEL=
AGL_LLM_TIMEOUT_SECONDS=30
```

`POST /v1/guidance` does not call an LLM. Optional BYOK LLM calls are limited to
experience extraction, prompt import, and `llm_judge` exams. See `docs/llm-config.md`.

## Project Layout

```text
server/                  FastAPI app, API routers, core services, models, storage
sdk/python/agent_growth/  Python SDK
templates/seed_skills/    Built-in seed skill YAML files
docs/                     Quickstart and LLM configuration notes
examples/customer_support Customer support integration example
examples/coding_agent     Coding-agent skill promotion example
examples/enterprise_qa    Enterprise QA verification example
tests/                    API and SDK tests
```

## Roadmap

- Real-provider GLM/OpenAI-compatible validation once the user supplies a temporary local key.
- Append-only audit event log.

## Stage Notes

Implementation handoff notes live in `docs/handoffs/`.
Documentation starts at `docs/index.md`.

## Contributing

See `CONTRIBUTING.md`.

## Boundaries

The current MVP intentionally does not implement Redis, a separate worker, vector storage, dashboard, multi-tenant permissions, external registry live lookup, prompt versioning, or `GET /v1/exams/{exam_id}`.

## License

MIT

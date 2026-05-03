# Agent Growth Layer

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

This repository currently implements the PRD's V0.1 "Guidance First" milestone:

- FastAPI service
- SQLite initialization
- Seed Skill YAML schema
- Seed Skill templates
- `POST /v1/guidance`
- `GET /v1/seed-skills`
- Python SDK foundation
- `guidance.to_prompt()`
- Docker Compose local startup
- Customer support example
- OpenAI-compatible LLM configuration notes

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

## V0.1 API

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
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
```

V0.1 does not call an LLM on the main guidance path. The OpenAI-compatible fields are reserved for later extraction and prompt import work.

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

- V0.2: Experience API, cognition extraction, feedback, candidate guidance, prompt import, JavaScript SDK minimum version.
- V0.3: Skill builder, manual exams, LLM judge, skill status flow, audit trail, verified guidance.

## Stage Notes

Implementation handoff notes live in `docs/handoffs/`.

## Boundaries

V0.1 intentionally does not implement caching, Redis, experience learning, cognition extraction, skill build, exam, multi-tenancy, permissions, vector storage, or prompt versioning.

## License

License is not selected yet.

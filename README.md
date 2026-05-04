# Agent Growth Layer

[![CI](https://github.com/liiider/Agent-Growth-Layer/actions/workflows/ci.yml/badge.svg)](https://github.com/liiider/Agent-Growth-Layer/actions/workflows/ci.yml)

Agent Growth Layer is an open-source runtime guidance layer for AI agents.

It helps an agent start with reusable seed guidance, learn from real task feedback, and promote useful lessons into verified guidance that can be injected back into the agent prompt.

In plain terms:

```text
Agent makes a mistake
-> you record the experience
-> Agent Growth Layer extracts a reusable lesson
-> the lesson becomes candidate guidance
-> useful guidance passes an exam and review
-> future agent runs receive verified guidance
-> repeated mistakes go down
```

## Why This Exists

Most AI agents do not naturally improve from previous project mistakes unless you manually rewrite prompts, add rules, or build a custom memory system.

Agent Growth Layer gives that improvement loop a small, inspectable API:

- `guidance`: runtime instructions your agent can inject into its prompt.
- `experience`: real mistakes, corrections, feedback, and outcomes.
- `cognition`: extracted lessons from experience.
- `candidate skill`: guidance that may be useful but is not fully trusted yet.
- `exam`: validation cases that decide whether a skill is reliable.
- `verified skill`: guidance that passed validation and can be trusted more.
- `audit`: evidence showing where a skill came from.

This is not a model fine-tuning system. It improves AI memory at runtime by turning real experience into reusable, verifiable, prompt-injectable guidance.

## Who Should Try It

Use this project if you are building:

- customer support agents
- coding agents
- enterprise QA agents
- workflow agents that repeat similar tasks
- internal assistants that need policy, permission, or process discipline

The MVP is designed to prove a narrow claim:

> Agent Growth Layer can help agents reduce repeated mistakes in high-frequency scenarios by learning from experience and injecting verified runtime guidance.

It does not claim to prove value for every developer, every company, or every AI task.

## What The MVP Includes

- FastAPI service
- SQLite local storage
- Docker Compose startup
- seed skill YAML templates
- `POST /v1/guidance`
- `guidance.to_prompt()`
- experience capture
- cognition extraction
- feedback API
- prompt import
- skill builder
- manual exam runner
- human review gate
- verified guidance
- audit API
- Python SDK
- JavaScript/TypeScript SDK source
- customer support, coding agent, and enterprise QA examples
- deterministic local defaults
- optional BYOK OpenAI-compatible LLM adapter for extraction, prompt import, and `llm_judge`

## Quickstart

Start the API:

```powershell
docker compose up --build
```

Check health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Request guidance:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/v1/guidance `
  -ContentType "application/json" `
  -Body '{
    "agent_id": "support_agent",
    "domain": "customer_support",
    "intent": "refund_question",
    "context": {"message": "Why was my refund rejected?"},
    "risk_level": "medium"
  }'
```

The response includes:

- `seed_skills`: cold-start guidance shipped with the project
- `candidate_skills`: learned guidance that still needs validation
- `verified_skills`: guidance that passed exam/review

## Use Guidance In Your Agent

Install the Python SDK locally:

```powershell
python -m pip install -e ".[dev]"
```

Use `to_prompt()` to inject guidance into your agent prompt:

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

system_prompt_addition = guidance.to_prompt()
print(system_prompt_addition)
```

Your agent framework remains in control. Agent Growth Layer only returns guidance.

## Learn From An Experience

Create an experience when an agent makes a mistake or receives useful correction:

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
```

The lesson should show up as candidate guidance after extraction:

```python
experience_id = experience["experience_id"]
tracked = client.experiences.get(experience_id)
print(tracked["cognition_ids"])
```

Build and verify a skill:

```python
cognition_id = tracked["cognition_ids"][0]

skill = client.skills.build(
    agent_id="support_agent",
    domain="customer_support",
    intent="refund_question",
    name="Refund Policy Handling",
    cognition_ids=[cognition_id],
)["skill"]

client.skills.run_exam(
    skill["id"],
    score=0.9,
    cases=[
        {
            "input": "I want a refund",
            "context": {"region": "unknown", "order_status": "unknown"},
            "expected_behavior": ["check region", "check order status"],
            "forbidden_behavior": ["promise refund approval"],
        }
    ],
)
```

After approval, future guidance requests can include the verified skill.

## JavaScript / TypeScript SDK

The JavaScript SDK source lives in `sdk/javascript`.

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

const experience = await client.experiences.create({
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

Build it:

```powershell
cd sdk\javascript
npm.cmd ci
npm.cmd run build
cd ..\..
```

## Validate Developer And Enterprise Value

There are two different kinds of validation in this repository.

### 1. User Value Validation

Use this when you want to know whether the project is valuable for a real developer or enterprise team:

- [User-facing MVP value validation plan](docs/testing/user-value-validation-plan.md)

This plan shows how to verify:

- whether a developer can run and integrate the project quickly
- whether `guidance.to_prompt()` is easy to inject
- whether experience changes future guidance
- whether repeated mistakes go down
- whether verified skills outperform candidate guidance
- whether enterprise users can trace guidance back to real evidence

### 2. Engineering Acceptance

Use this when you want to know whether the local MVP implementation is technically healthy:

- [Supervised MVP engineering test plan](docs/testing/supervised-mvp-test-plan.md)

It covers:

- Docker startup
- health check
- local MVP chain
- project-level MVP chain
- Python tests
- Ruff lint
- Python compile check
- JavaScript SDK build
- secret scan

## Local Verification

Run the basic MVP chain:

```powershell
python scripts\verify_local_mvp.py --base-url http://127.0.0.1:8000
```

Run the project-level MVP chain:

```powershell
python scripts\verify_project_mvp.py --base-url http://127.0.0.1:8000
```

Run the standard local checks:

```powershell
python -m pytest
python -m ruff check .
python -m compileall server sdk examples scripts
```

## API Surface

- `POST /v1/guidance`
- `GET /v1/seed-skills`
- `GET /v1/seed-skills/{id}`
- `POST /v1/experiences`
- `GET /v1/experiences/{id}`
- `POST /v1/experiences/{id}/extract`
- `GET /v1/cognitions`
- `GET /v1/cognitions/{id}`
- `PATCH /v1/cognitions/{id}/status`
- `POST /v1/feedback`
- `POST /v1/skills/import_prompt`
- `POST /v1/skills/build`
- `GET /v1/skills`
- `GET /v1/skills/{id}`
- `PATCH /v1/skills/{id}`
- `PATCH /v1/skills/{id}/status`
- `POST /v1/skills/{id}/exam`
- `POST /v1/reviews`
- `GET /v1/audit/{object_type}/{object_id}`
- `GET /health`

See [docs/api.md](docs/api.md) for request and response examples.

## Seed Skills

Seed skills live in `templates/seed_skills/` and are loaded from YAML at runtime.

Included seed skills:

- Uncertainty Handling
- Permission Sensitive Answering
- Feedback Aware Response
- Tool Result Checking
- Code Change Checklist
- Customer Support Resolution
- Policy Answering
- Medical Safety Boundary

Schema: [docs/seed-skill-schema.md](docs/seed-skill-schema.md)

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

`POST /v1/guidance` does not call an LLM. Optional BYOK LLM calls are limited to experience extraction, prompt import, and `llm_judge` exams.

See [docs/llm-config.md](docs/llm-config.md).

## Project Layout

```text
server/                   FastAPI app, API routers, core services, models, storage
sdk/python/agent_growth/   Python SDK
sdk/javascript/            JavaScript/TypeScript SDK source
templates/seed_skills/     Built-in seed skill YAML files
docs/                      Documentation and validation plans
examples/customer_support/ Customer support integration example
examples/coding_agent/     Coding-agent skill promotion example
examples/enterprise_qa/    Enterprise QA verification example
tests/                     API and SDK tests
scripts/                   Local MVP verification scripts
```

## Current Boundaries

The current MVP intentionally does not implement:

- Redis
- a separate worker process
- vector storage
- dashboard
- multi-tenant permissions
- external registry live lookup
- prompt versioning
- automatic re-exam
- `GET /v1/exams/{exam_id}`

## Documentation

Start with [docs/index.md](docs/index.md).

Implementation handoff notes live in `docs/handoffs/`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT

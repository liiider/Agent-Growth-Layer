# API

## Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

## Create Guidance

```http
POST /v1/guidance
```

Use `POST` because guidance requests include structured task context.

Request:

```json
{
  "agent_id": "support_agent",
  "domain": "customer_support",
  "intent": "refund_question",
  "context": {
    "message": "Why was my refund rejected?"
  },
  "risk_level": "medium"
}
```

Response:

```json
{
  "id": "guide_...",
  "agent_id": "support_agent",
  "domain": "customer_support",
  "intent": "refund_question",
  "guidance": {
    "verified_skills": [],
    "candidate_skills": [],
    "seed_skills": [],
    "error_patterns": [],
    "output_guidance": [],
    "tool_policy": []
  }
}
```

V0.1 guidance is assembled in real time from local seed skill YAML files. It does not call an LLM and does not use a cache.

Seed skill selection is domain-aware:

- Skills matching the requested `domain` are returned first.
- `general` skills are included as fallback guidance.
- Clearly unrelated domain-specific skills are excluded from the guidance response.

## List Seed Skills

```http
GET /v1/seed-skills
```

Returns all built-in seed skills.

## Get Seed Skill

```http
GET /v1/seed-skills/{id}
```

Returns a single seed skill or `404` when the ID is unknown.

## SDK Prompt Injection

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
```

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

## Create Experience

```http
POST /v1/experiences
```

Request:

```json
{
  "agent_id": "support_agent",
  "domain": "customer_support",
  "intent": "refund_question",
  "user_input": "我要退款，为什么不给退？",
  "agent_output": "根据平台规则，订单超过7天不能退款。",
  "tools_used": ["policy_search"],
  "retrieved_context": ["退款规则分地区适用，不同地区售后政策不同。"],
  "feedback": "回答错误，必须先确认地区和订单状态。",
  "result_status": "corrected",
  "risk_level": "medium",
  "metadata": {
    "region": "unknown",
    "order_status": "unknown"
  }
}
```

Response:

```json
{
  "experience_id": "exp_...",
  "status": "received",
  "extraction_status": "queued"
}
```

The response returns `queued` immediately. V0.2 uses FastAPI `BackgroundTasks` to extract candidate cognition after the response.

## Get Experience

```http
GET /v1/experiences/{id}
```

Returns the stored experience and any generated `cognition_ids`.

## Retry Extraction

```http
POST /v1/experiences/{id}/extract
```

Sets `extraction_status` to `retrying`, then runs extraction with the current extractor implementation.

## Cognitions

```http
GET /v1/cognitions
GET /v1/cognitions/{id}
PATCH /v1/cognitions/{id}/status
```

List supports optional filters:

- `agent_id`
- `domain`
- `intent`
- `status`
- `limit`

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

## SDK Experience Tracking

```python
from agent_growth import AgentGrowthClient

client = AgentGrowthClient("http://localhost:8000")
result = client.experiences.create(
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

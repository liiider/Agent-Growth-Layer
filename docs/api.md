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

## Build Skill

```http
POST /v1/skills/build
```

Request:

```json
{
  "agent_id": "support_agent",
  "domain": "customer_support",
  "intent": "refund_question",
  "name": "Refund Policy Handling",
  "cognition_ids": ["cog_..."]
}
```

Response:

```json
{
  "skill": {
    "id": "skill_...",
    "status": "candidate",
    "weight": "medium",
    "latest_exam": null
  }
}
```

## Skills

```http
GET /v1/skills
GET /v1/skills/{id}
PATCH /v1/skills/{id}
PATCH /v1/skills/{id}/status
```

`GET /v1/skills/{id}` returns `latest_exam`.

## Run Exam

```http
POST /v1/skills/{skill_id}/exam
```

Request:

```json
{
  "evaluator": "manual_score",
  "score": 0.9,
  "cases": [
    {
      "input": "I want a refund",
      "context": {
        "region": "unknown",
        "order_status": "unknown"
      },
      "expected_behavior": ["check region", "check order status"],
      "forbidden_behavior": ["promise refund approval"]
    }
  ]
}
```

Response:

```json
{
  "exam_id": "exam_...",
  "skill_id": "skill_...",
  "previous_status": "candidate",
  "score": 0.9,
  "passed": true,
  "failures": [],
  "new_status": "verified"
}
```

Passing exams promote the skill into verified guidance. Failed exams set the skill to `failed`.

Set `require_human_review` when a passing exam should stop at `needs_review` until a human
review approves the skill:

```json
{
  "evaluator": "manual_score",
  "score": 0.9,
  "require_human_review": true,
  "cases": []
}
```

## Human Review

```http
POST /v1/reviews
```

Reviews record human decisions for experiences, cognitions, and skills.

Request:

```json
{
  "object_type": "skill",
  "object_id": "skill_...",
  "decision": "approve",
  "reviewer": "project_owner",
  "notes": "Passing exam and project owner review approve this skill.",
  "metadata": {}
}
```

Behavior:

- Experience reviews are recorded as evidence but do not change status.
- Cognition `approve` sets status to `verified`.
- Cognition `reject` sets status to `deprecated`.
- Cognition or skill `quarantine` sets status to `quarantined`.
- Skill `approve` requires a passing exam, then sets status to `verified`.
- Skill `reject` sets status to `failed`.

## Audit

```http
GET /v1/audit/{object_type}/{object_id}
```

Supported object types:

- `skill`
- `cognition`

Skill audit responses include evidence refs and linked cognition sources. Cognition audit responses include linked experience ids.

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

## Python SDK Full MVP Surface

```python
from agent_growth import AgentGrowthClient

client = AgentGrowthClient("http://localhost:8000", timeout=10)

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

client.cognitions.update_status(cognition_id, "verified")

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

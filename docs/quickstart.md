# Quickstart

Start the API locally:

```powershell
docker-compose up --build
```

Call `POST /v1/guidance` with an `agent_id`, `domain`, `intent`, `context`, and `risk_level`. The first response returns seed skills that can be injected into an agent system prompt.

The Python SDK exposes:

```python
from agent_growth import AgentGrowthClient

client = AgentGrowthClient("http://localhost:8000")
guidance = client.get_guidance(
    agent_id="support_agent",
    domain="customer_support",
    intent="refund_question",
    context={"message": "I want a refund"},
    risk_level="medium",
)

system_prompt = guidance.to_prompt()
```

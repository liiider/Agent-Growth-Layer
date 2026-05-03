# Customer Support Example

This example uses cold-start guidance for a refund question.

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

print(guidance.to_prompt())
```

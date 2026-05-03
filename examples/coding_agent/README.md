# Coding Agent Example

This example uses Agent Growth Layer to track a coding-agent correction, build a candidate skill, and promote it after a manual exam.

Flow:

1. `POST /v1/guidance`
2. Agent performs a code task.
3. `POST /v1/experiences`
4. `POST /v1/skills/build`
5. `POST /v1/skills/{skill_id}/exam`
6. Next guidance includes verified skill behavior.

The core safety expectation is that code changes should be narrow, tested, and should not revert unrelated user work.

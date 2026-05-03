# Seed Skill YAML Schema

Seed skills are the cold-start guidance source for V0.1. Each file in `templates/seed_skills/` must be valid YAML and must conform to this stable schema.

## Required Fields

- `id`: Stable string identifier. Use the `seed_` prefix.
- `name`: Human-readable skill name.
- `version`: Semantic version string for the template.
- `status`: Must be `seed`.
- `description`: Short description of the skill.
- `domain`: List of domains where the skill can apply.
- `intent`: List of intents where the skill can apply.
- `applies_when`: List of triggering situations.
- `instructions`: Ordered behavior guidance.
- `constraints`: Hard boundaries.
- `negative_examples`: Examples of behavior to avoid.
- `output_guidance`: Response-shaping guidance.
- `tool_policy`: Tool-use guidance.
- `risk_level`: `low`, `medium`, or `high`.
- `tags`: Search and grouping tags.

## Runtime Validation

The server loads seed skills through Pydantic models. Invalid status values, missing required fields, or wrongly typed fields fail during template loading.

The test suite validates every built-in seed skill:

```powershell
python -m pytest tests/test_seed_skill_schema.py
```

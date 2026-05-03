# DeepSeek LLM Validation Handoff

## Stage Goal

Verify the optional BYOK LLM paths with a real OpenAI-compatible provider instead of only fake
clients and deterministic local defaults.

## Expected Effect

With `AGL_LLM_PROVIDER=openai_compatible` and a user-provided DeepSeek API key:

- experience extraction can create a persisted cognition through the LLM path
- prompt import can create a candidate skill through the LLM path
- `llm_judge` can score an exam through the LLM path
- `POST /v1/guidance` remains model-free

## Work Completed

- Added `scripts/verify_llm_provider.py`.
  - Reads only the running service URL from CLI arguments.
  - Uses provider configuration from environment variables already consumed by the server.
  - Does not read or write API keys.
- Added `tests/test_llm_provider_verifier.py`.
- Hardened LLM extraction prompts with explicit json examples and allowed enum values.
- Normalized common provider schema variants:
  - unknown cognition `type` -> `rule`
  - numeric/string confidence -> clamped float from 0 to 1
  - numeric/string weight -> `low`, `medium`, or `high`
- Hardened prompt import and judge prompts with explicit json examples.
- Updated PRD coverage to mark DeepSeek real-provider validation as complete.

## Issues Found

1. First DeepSeek validation failed during LLM extraction.
   - The API key and network were valid.
   - Direct DeepSeek call returned parseable JSON, but it did not match our strict schema:
     `type` was provider-specific and `weight` was numeric.
   - Resolution: strengthened prompts and added safe normalization before schema validation.

2. Real provider output can differ from ideal fake-client tests.
   - Resolution: added a regression test that simulates DeepSeek-style schema variants.

## Verification

- Direct DeepSeek adapter smoke test
  - Result: passed.
  - Confirmed API key, endpoint, model, and JSON mode were usable.

- `python -m pytest tests/test_llm_provider.py tests/test_llm_provider_verifier.py`
  - Result: passed, 6 tests.

- `python -m ruff check ...`
  - Initial result: failed on one long line.
  - Final result: passed.

- Real DeepSeek local service validation:
  - Environment:
    - `AGL_LLM_PROVIDER=openai_compatible`
    - `AGL_LLM_BASE_URL=https://api.deepseek.com`
    - `AGL_LLM_MODEL=deepseek-v4-flash`
    - API key supplied only as a process environment variable
  - Result: passed.
  - Observed output:
    - `llm extraction: exp_3945185cabb0 -> cog_00441d6d5c95`
    - `llm prompt import: skill_imported_d5499b9d3138`
    - `llm judge: skill_9b6622decbe2 score=1.0`
    - `LLM provider verification passed`

## Security Notes

- The user-provided API key was not written to `.env`, docs, tests, or committed files.
- The key was used only in a PowerShell process environment for the validation command.
- Because the key was shared in chat, it should be treated as exposed and rotated or revoked after
  validation.

## Remaining Notes

- GLM should still be validated as a second OpenAI-compatible provider.
- If GLM rejects `response_format={"type":"json_object"}`, add a provider compatibility option
  rather than weakening DeepSeek/OpenAI JSON-mode behavior.

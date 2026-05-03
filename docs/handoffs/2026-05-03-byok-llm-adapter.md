# BYOK LLM Adapter Handoff

## Stage Goal

Prepare Agent Growth Layer for user-supplied LLM APIs without making the project owner
provide or store API keys.

## Expected Effect

- Local MVP remains deterministic and works without any external model.
- `POST /v1/guidance` remains model-free and does not add latency or provider risk.
- Optional LLM calls can be enabled through `AGL_LLM_PROVIDER=openai_compatible`.
- The same adapter can support GLM/OpenAI-compatible endpoints during the next real-provider
  validation stage.

## Work Completed

- Added `server/core/llm.py` with:
  - `ChatClient` protocol
  - `OpenAICompatibleChatClient`
  - `build_chat_client(settings)`
  - explicit configuration errors without exposing API keys
- Added LLM configuration fields:
  - `AGL_LLM_PROVIDER`
  - `AGL_LLM_BASE_URL`
  - `AGL_LLM_API_KEY`
  - `AGL_LLM_MODEL`
  - `AGL_LLM_TIMEOUT_SECONDS`
- Wired optional LLM clients into:
  - cognition extraction
  - prompt import
  - `llm_judge` exam scoring
- Kept deterministic local behavior as the default.
- Updated `.env.example`, README, PRD coverage, and LLM configuration docs.

## Issues Found

1. Existing docs used `OPENAI_*` fields while the app settings use the `AGL_` prefix.
   - Resolution: moved all documented LLM config to `AGL_LLM_*`.

2. The first mock `httpx.Response` in tests lacked a request object.
   - Impact: `response.raise_for_status()` failed in the test harness.
   - Resolution: added `httpx.Request("POST", url)` to the mocked response.

3. Ruff found long lines after the LLM adapter implementation.
   - Resolution: wrapped payload construction and assertions.

## Verification

- `python -m pytest tests/test_llm_provider.py`
  - Result: passed, 4 tests.
  - Verified:
    - OpenAI-compatible request URL, model, timeout, auth header, and JSON response mode.
    - experience extraction can use an injected LLM client.
    - prompt import can use an injected LLM client.
    - `llm_judge` can score through an injected LLM client.

- `python -m pytest`
  - Result: passed, 28 tests.

- `python -m ruff check .`
  - Initial result: failed on long lines.
  - Final result: passed.

## Remaining Notes

- No real external LLM request was made in this stage.
- GLM validation should be the next LLM-specific step once the user provides a temporary local
  API key.
- If GLM does not support `response_format={"type":"json_object"}` on the selected model, the
  adapter should add a provider compatibility option rather than weakening the deterministic
  tests.

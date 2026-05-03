# LLM Configuration

Agent Growth Layer is BYOK: the project does not provide or store a platform-owned LLM
API key. Operators configure their own provider through environment variables.

The guidance hot path remains model-free. `POST /v1/guidance` assembles local seed,
candidate, and verified skills without calling an LLM. LLM calls are optional and are
only used by:

- cognition extraction after `POST /v1/experiences`
- prompt import through `POST /v1/skills/import_prompt`
- `llm_judge` exams when no manual score is supplied

## Default Local Mode

```env
AGL_LLM_PROVIDER=deterministic
AGL_LLM_BASE_URL=
AGL_LLM_API_KEY=
AGL_LLM_MODEL=
AGL_LLM_TIMEOUT_SECONDS=30
```

This mode uses deterministic local parsing and scoring. It is the default for tests,
quickstart, and offline development.

## OpenAI-Compatible BYOK

```env
AGL_LLM_PROVIDER=openai_compatible
AGL_LLM_BASE_URL=https://api.openai.com/v1
AGL_LLM_API_KEY=your_key_here
AGL_LLM_MODEL=gpt-4.1-mini
AGL_LLM_TIMEOUT_SECONDS=30
```

The adapter calls:

```text
POST {AGL_LLM_BASE_URL}/chat/completions
```

with `Authorization: Bearer {AGL_LLM_API_KEY}` and requests JSON output.

## GLM / OpenAI-Compatible Endpoint

When validating with GLM, use its OpenAI-compatible endpoint and keep the key only in
your local environment:

```env
AGL_LLM_PROVIDER=openai_compatible
AGL_LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
AGL_LLM_API_KEY=your_glm_key_here
AGL_LLM_MODEL=glm-4-flash
AGL_LLM_TIMEOUT_SECONDS=30
```

We should run real GLM validation only after the user provides a temporary local key.

## Ollama-Compatible Local Endpoint

```env
AGL_LLM_PROVIDER=openai_compatible
AGL_LLM_BASE_URL=http://localhost:11434/v1
AGL_LLM_API_KEY=ollama
AGL_LLM_MODEL=qwen2.5
AGL_LLM_TIMEOUT_SECONDS=30
```

## Qwen-Compatible Endpoint

```env
AGL_LLM_PROVIDER=openai_compatible
AGL_LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AGL_LLM_API_KEY=your_dashscope_key
AGL_LLM_MODEL=qwen-plus
AGL_LLM_TIMEOUT_SECONDS=30
```

## Failure Behavior

- Invalid LLM configuration fails the request that needs an LLM client.
- LLM extraction schema errors mark the experience extraction as `failed`.
- Manual score exams are still supported without any LLM configuration.

# LLM Configuration

V0.1 does not call an LLM on the main guidance path. The environment fields are reserved for V0.2 extraction and prompt import work.

## OpenAI-Compatible BYOK

```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

## Ollama

```env
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=qwen2.5
```

## Qwen-Compatible Endpoint

```env
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=qwen-plus
```

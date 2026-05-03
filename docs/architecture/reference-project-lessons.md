# Reference Project Lessons

Date: 2026-05-03

This note records design constraints learned from adjacent projects and systems we should keep in mind while building Agent Growth Layer.

References:

- Mem0 open-source docs: https://docs.mem0.ai/open-source/overview
- Mem0 feature overview: https://docs.mem0.ai/features/contextual-add
- LangMem docs: https://langchain-ai.github.io/langmem/
- LangMem memory API: https://langchain-ai.github.io/langmem/reference/memory/
- MLflow MemAlign docs: https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/memalign/
- MLflow MemAlign blog: https://mlflow.org/blog/memalign/
- AI Skill Registry: https://skillsfor.ai/
- SkillRegistry: https://skillregistry.io/
- askill registry: https://askill.sh/
- JFrog Agent Skills Registry: https://jfrog.com/ai-catalog/skills-registry/

## Product Boundary

Agent Growth Layer is not a general memory product, an agent framework, or a public skill marketplace.

Our job is narrower:

- Convert experience, feedback, corrections, and evaluation evidence into runtime guidance.
- Keep guidance structured, auditable, and injectable into any agent.
- Promote guidance only when there is evidence and validation.
- Stay local-first for V0.1 and avoid dependencies that make first-run setup slow or fragile.

## Mem0 Lessons

Mem0 is closest to a persistent adaptive memory layer. Its open-source stack emphasizes self-hosting, configurable LLMs, embeddings, vector stores, history storage, and optional reranking.

Useful lessons:

- Memory extraction and retrieval are separate concerns from runtime guidance construction.
- Vector search and reranking can improve recall but introduce infrastructure and latency.
- Local-first systems need sensible defaults, but every component should remain replaceable.
- Memory records are not automatically executable strategy; a downstream layer must decide how to use them.

Performance boundary:

- Mem0-style LLM extraction, embedding, vector search, and reranking are too heavy for the V0.1 guidance hot path.
- We should not require Qdrant, pgvector, rerankers, or embeddings before developers can get seed guidance.
- In later versions, vector retrieval should be optional and bounded by top-k limits.

Agent Growth Layer implication:

- V0.1 guidance must remain SQLite + YAML + deterministic assembly.
- V0.2 extraction may use LLMs, but extraction should run outside the request-critical guidance path.
- Guidance should consume already-filtered cognitions/skills, not raw memories.

## LangMem Lessons

LangMem separates hot-path memory tools from background memory management. It also supports structured memory schemas and storage abstraction.

Useful lessons:

- Hot-path memory improves adaptivity but can slow or destabilize agent execution.
- Background extraction is better for heavier consolidation and update work.
- Structured schemas are more useful than untyped text blobs when memory must feed downstream behavior.
- Upserts and contradiction handling matter; otherwise old memories accumulate and conflict.

Performance boundary:

- Any model call in the guidance path risks making every agent request slower and more expensive.
- Background memory/cognition processing should be idempotent and retryable.
- Query limits must be explicit; unlimited memory search will degrade latency and prompt size.

Agent Growth Layer implication:

- Keep `POST /v1/guidance` model-free and cache-free in V0.1.
- In V0.2, use FastAPI `BackgroundTasks` for extraction as planned, then move to a worker only when scale requires it.
- Treat cognition extraction as schema production, not summary generation.
- Preserve evidence refs for every generated cognition and skill.

## MemAlign Lessons

MemAlign is especially relevant to our eval loop. It aligns LLM judges from natural-language feedback through a dual-memory design:

- Semantic memory stores generalizable guidelines.
- Episodic memory stores concrete examples and edge cases.
- Working memory combines principles and relevant examples at judgment time.

Useful lessons:

- Natural-language feedback can be denser than labels alone.
- General rules and edge-case examples should both survive extraction.
- Evaluation systems regress unless past failures are retained and replayed.
- Memory-based alignment can be fast to adapt, but inference may pay extra retrieval/context cost.

Performance boundary:

- MLflow's MemAlign materials note an additional retrieval/context cost at inference time compared with prompt-optimized judges.
- That cost is acceptable for exams and judge refinement, but not for every guidance request in V0.1.

Agent Growth Layer implication:

- Model cognition types should preserve both semantic rules and episodic negative examples.
- Skill exams should use both expected behavior and forbidden behavior.
- Failed exams should create evidence that can later shape constraints or negative examples.
- Verified guidance should not be promoted from one anecdote without an evaluation gate.

## Skill Registry Lessons

Current skill registry projects emphasize discoverability, versioning, immutable releases, safety metadata, and trust scoring.

Useful lessons:

- Skills need stable IDs, versions, descriptions, metadata, and compatibility boundaries.
- Approved skill versions should be immutable; changes should create new versions.
- Skills that can cause side effects need explicit safety and execution metadata.
- Public or shared skills need provenance, scanning, signing, or trust signals.

Performance boundary:

- Registry lookup should not be required for local guidance generation.
- Public registry search can be slow, unavailable, or unsafe; it must not be in the V0.1 critical path.

Agent Growth Layer implication:

- Internal skills need version fields from the start.
- Later external skill registry support should be import/sync based, not live lookup during guidance.
- `quarantined` skills must never enter guidance.
- Promotion and deprecation should be explicit state transitions.

## Eval Loop Lessons

The evaluation loop is the boundary between "candidate" and "verified" guidance.

Design rules:

- Candidate guidance can appear, but must be clearly labeled as unverified.
- Verified guidance requires an exam or manual validation record.
- Every exam should produce auditable evidence.
- Regression examples must be retained as future exam cases.
- A passing score should not erase failure evidence; it should version the skill.

Performance boundary:

- Exams can be slower than guidance requests.
- LLM judges should be asynchronous or manually triggered.
- Expensive eval should not block `POST /v1/guidance`.

Agent Growth Layer implication:

- Keep V0.1 seed guidance simple.
- V0.2 should focus on evidence-backed candidate cognitions.
- V0.3 should implement exams as the promotion gate.

## Implementation Constraints For This Repo

For upcoming implementation:

- No vector database in V0.1.
- No model call in `POST /v1/guidance` in V0.1.
- No registry network lookup in guidance assembly.
- No candidate item without `weight`, `status`, and `evidence_refs`.
- No verified skill without exam/manual validation evidence.
- No skill mutation without version or audit trail once skill build exists.
- Keep all retrieval limits explicit.
- Keep generated guidance prompt size bounded.
- Keep state transitions explicit and tested.

## Open Design Questions

- Should `cognition` and `skill` keep separate semantic and episodic evidence buckets, or one `evidence_refs` list plus typed linked records?
- What is the first acceptable top-k limit for candidate guidance in V0.2?
- Should prompt import create a `seed` skill or a separate `imported` source type with seed status?
- What minimum exam score should promote a skill to `verified` in V0.3?

PRD：Agent Growth Layer 开源项目
===========================

1. 项目概述

-------

Agent Growth Layer 是一个开源的 AI Agent 运行时指导层。

它让 Agent 在第一次运行时就能获得基础 guidance，并在后续真实任务、用户反馈、错误修正中逐步形成更好的行为指导。

项目形态：

GitHub 开源项目  
Self-host 服务  
REST API  
Python SDK  
JavaScript / TypeScript SDK  
SQLite 默认存储  
Docker Compose 本地启动  
OpenAI-compatible LLM 配置  
开发者自备 API Key  
不绑定任何 Agent 框架

英文定位：
    Agent Growth Layer gives AI agents runtime guidance that improves from real experience.

中文定位：
    Agent Growth Layer 为 AI Agent 提供会成长的运行时指导。

* * *

2. 项目要解决的问题

-----------

现有 AI 应用常见问题：

Agent 做过很多任务，但不会自动变得更会做事。  
Agent 被用户纠正后，下次仍可能犯同类错误。  
Memory 项目能保存信息，但不一定能转成执行策略。  
RAG 能找资料，但不知道资料应该如何被使用。  
评测工具能发现错误，但错误不会自动变成下次的行为约束。  
Agent 框架能执行任务，但不负责沉淀经验。

Agent Growth Layer 要解决的是：

把 Agent 的真实经历、用户反馈和错误案例，转化为可复用、可验证、可注入运行时的 guidance。

* * *

3. 产品原则

-------

### 3.1 Guidance First

开发者先拿 guidance，再提交 experience。

项目的第一感知价值来自：
    guidance.get()

不是：
    experience.create()

* * *

### 3.2 开源优先

项目不设计 SaaS 计费逻辑，不写商业版包装。

开源项目的价值来自：

schema 标准  
社区贡献  
seed skill 生态  
清晰 API  
可本地部署  
可接入任意 Agent

* * *

### 3.3 Framework Agnostic

项目不做 Agent 编排。

它只提供：

运行时指导  
经验学习  
技能沉淀  
考试验证  
错误防重犯

执行任务仍由开发者自己的 Agent 完成。

* * *

### 3.4 Local First

默认本地可运行。

V0.1 必须支持：

SQLite  
Docker Compose  
OpenAI-compatible LLM 配置  
开发者自备 API Key  
无外部 SaaS 依赖

* * *

### 3.5 Evidence Based

每个 cognition、skill、guidance 都应能追溯来源。

自动生成的内容都需要 `evidence_refs`。

* * *

4. 基础概念

-------

4.1 Guidance
------------

运行时指导包。

它不是普通记忆，而是给 Agent 当前任务使用的执行指导。

包括：

这次任务应该怎么做  
哪些错误要避免  
哪些工具优先调用  
输出结构应如何组织  
哪些技能已经验证  
哪些技能只是候选  
哪些技能来自 seed template

Guidance 分三层：
    verified_skills
    candidate_skills
    seed_skills

* * *

4.2 Seed Skill
--------------

项目内置的基础技能模板。

用于冷启动。

开发者第一次调用 guidance，即使没有任何历史 experience，也能拿到基础指导。

Seed Skill 不追求行业深度，只提供通用行为能力。

示例：

不确定性处理  
权限敏感回答  
工具结果检查  
代码修改检查  
用户反馈处理  
政策类问题回答  
医疗安全边界  
客服问题处理

* * *

4.3 Experience
--------------

Agent 的一次真实任务经历。

包括：

用户输入  
Agent 输出  
工具调用  
检索上下文  
用户反馈  
人工纠正  
执行结果  
失败原因  
任务元数据  
extraction_status

Experience 是系统学习的原材料。

* * *

4.4 Cognition
-------------

从 experience 中抽取出的结构化认知。

不是摘要。

类型包括：

fact  
preference  
rule  
procedure  
constraint  
error_pattern  
tool_usage  
communication_style  
decision_pattern  
negative_example

* * *

4.5 Skill
---------

由多条 cognition 沉淀出的可复用行为能力。

Skill 不是 prompt。

Skill 是结构化对象：

适用场景  
处理步骤  
工具策略  
输出要求  
约束条件  
错误模式  
反例  
证据来源  
状态  
版本

Skill 状态：
    seed
    candidate
    testing
    verified
    failed
    deprecated
    quarantined

* * *

4.6 Exam
--------

对 candidate skill 的基础验证。

开源版只支持手动触发考试。

不做自动考试队列。

触发方式：
    POST /v1/skills/{skill_id}/exam

* * *

5. 主流程

------

### 5.1 系统链路

    POST /v1/guidance
    → Agent 执行任务
    → POST /v1/experiences
    → 自动异步 extraction
    → cognition 进入 candidate
    → candidate guidance 出现在下一次 guidance
    → build skill
    → 手动 exam
    → verified skill
    → verified guidance

### 5.2 开发者路径

    get guidance
    → track experience
    → get improved guidance
    → build skill
    → run exam
    → use verified guidance

* * *

6. MVP 范围

---------

6.1 V0.1：Guidance First
-----------------------

目标：

开发者 10 分钟内本地跑起来，并第一次拿到 seed guidance。

必须完成：

SQLite  
Docker Compose  
Seed Skill YAML schema  
Seed Skill Templates  
`POST /v1/guidance`  
实时 guidance builder  
`guidance.to_prompt()`  
Python SDK 基础版  
README Quickstart  
Customer support example  
OpenAI-compatible LLM 配置文档  
BYOK / Ollama / Qwen 配置示例

V0.1 不实现：

缓存  
Redis  
独立 worker  
复杂 dashboard  
experience 学习  
cognition 抽取  
skill build  
exam  
多租户  
权限系统  
图谱  
向量库  
复杂队列  
prompt versioning

验收标准：

开发者可以：

`docker-compose up`  
调用 `POST /v1/guidance`  
拿到 seed guidance  
用 `to_prompt()` 注入自己的 Agent

* * *

6.2 V0.2：Experience Learning
----------------------------

目标：

提交 experience 后，系统自动异步抽取 cognition，并在下一次 guidance 中返回 candidate guidance。

必须完成：

Experience API  
自动异步 Cognition Extraction  
手动 retry extraction  
Feedback API  
Evidence refs  
Candidate guidance  
Prompt Import  
JavaScript SDK 最小版

V0.2 的 JS SDK 只覆盖两个方法：
    guidance.get()
    experiences.create()

验收标准：

开发者可以：

提交一条 experience  
系统自动抽取 cognition  
cognition 进入 candidate 状态  
下一次 guidance 返回 candidate guidance  
手动重试 extraction

* * *

6.3 V0.3：Skill + Exam
---------------------

目标：

candidate skill 可以通过手动 exam 升级为 verified guidance。

必须完成：

Skill Builder  
Basic Exam Runner  
LLM Judge  
Manual Score  
Skill Status  
Audit Trail  
Coding agent example  
Enterprise QA example  
JS SDK 补齐 skill / exam 基础方法

验收标准：

开发者可以：

从 cognition 构建 skill  
手动触发 exam  
查看 skill 的 latest_exam  
将通过考试的 skill 设为 verified  
下一次 guidance 返回 verified skill

* * *

7. 开发顺序

-------

第 1 周
-----

目标：

项目可以本地跑起来。

完成：

项目骨架  
SQLite  
Docker Compose  
Seed Skill YAML schema  
Seed Skill Templates  
`POST /v1/guidance`  
最小 README  
`docker-compose up` 可运行

第 1 周结束可以邀请第一批测试者。

* * *

第 2 周
-----

目标：

开发者能接入并注入 guidance。

完成：

Python SDK  
`guidance.to_prompt()`  
Prompt Import  
Customer support example  
README Quickstart  
OpenAI-compatible LLM 配置文档  
BYOK / Ollama / Qwen 配置示例

* * *

第 3 周
-----

目标：

系统能从 experience 中学习。

完成：

`POST /v1/experiences`  
`GET /v1/experiences/{id}`  
`extraction_status`  
自动异步 Cognition Extraction  
Manual extraction retry  
Feedback API  
Evidence refs  
Candidate guidance  
JS SDK 最小版

* * *

第 4 周
-----

目标：

系统能验证 skill。

完成：

Skill Builder  
Basic Exam  
状态流转：candidate → testing → verified / failed  
LLM Judge  
Manual Score  
Audit Trail  
Coding agent example  
Enterprise QA example  
手动 quarantine

* * *

8. 固定技术决策

---------

8.1 Guidance 不做缓存
-----------------

V0.1 不做缓存。

`POST /v1/guidance` 每次实时构建 guidance 对象。

原因：

V0.1 以本地开源体验为主，优先保持实现简单。  
Seed Skills、candidate skills、verified skills 的数量都很小，实时查库成本可控。  
避免引入 Redis 或缓存失效逻辑。  
开发者能立刻看到新 experience / cognition 对 guidance 的影响。

技术决策：
    POST /v1/guidance always builds guidance in real time.
    No cache in V0.1.
    No Redis dependency.
    Each call may generate a new guide_id for audit/debug purpose.

后续可扩展：

内存缓存  
Redis 缓存  
按 agent_id + domain + intent 缓存  
guidance version hash  
缓存失效策略

* * *

8.2 异步 Extraction 使用 BackgroundTasks
------------------------------------

V0.1 使用 FastAPI `BackgroundTasks`。

不引入独立 worker。

Docker Compose 只启动一个服务。

原因：

降低本地启动复杂度。  
`docker-compose up` 即可运行。  
不需要 Redis、Celery、arq、worker 进程。  
V0.1 的 extraction 规模较小，BackgroundTasks 足够。

技术决策：
    In V0.1, cognition extraction runs through FastAPI BackgroundTasks.
    No separate worker process.
    No queue system.
    No Redis dependency.

流程：
    POST /v1/experiences
    → save experience
    → set extraction_status = queued
    → add BackgroundTask(extract_cognition)
    → return experience_id + extraction_status
    → background task sets status running
    → extraction succeeds: status = succeeded
    → extraction fails: status = failed

手动重试：
    POST /v1/experiences/{id}/extract

手动 retry 时：
    set extraction_status = retrying
    run extraction through BackgroundTasks

* * *

8.3 Prompt 加载策略
---------------

Extraction prompt 从 `/prompts/` 目录加载。

默认文件：
    /prompts/cognition_extraction.md

这是带变量的模板文件。

支持变量：
    {{domain}}
    {{intent}}
    {{user_input}}
    {{agent_output}}
    {{tools_used}}
    {{retrieved_context}}
    {{feedback}}
    {{result_status}}
    {{risk_level}}
    {{metadata}}

`.env` 支持自定义路径：
    COGNITION_EXTRACTION_PROMPT_PATH=./prompts/cognition_extraction.md

开发者可以复制默认 prompt，修改后通过 `.env` 指定自定义路径。

手动 retry 使用当前最新 prompt。

技术决策：
    Extraction retry always uses the current prompt file.
    The system does not store historical prompt snapshots in V0.1.

* * *

8.4 Prompt 文件头注释
----------------

在 `/prompts/cognition_extraction.md` 顶部加入：
    <!--
    Agent Growth Layer - Cognition Extraction Prompt

    This prompt is loaded at extraction runtime.

    Changing this file will affect all future cognition extraction tasks,
    including manual retries triggered after the change.

    V0.1 does not store prompt snapshots or prompt versions.
    If you need reproducible extraction results, keep a copy of the prompt
    used for each test run manually.
    -->

中文文档补充：
    修改 /prompts/cognition_extraction.md 会影响所有后续 extraction，包括手动 retry。
    V0.1 不保存 prompt 快照，也不做 prompt versioning。

* * *

8.5 Exam 结果查询策略
---------------

V0.1 不提供独立接口：
    GET /v1/exams/{exam_id}

采用：
    GET /v1/skills/{id}

返回 `latest_exam`。

原因：

减少 API 数量。  
V0.1 只需要让开发者看到 skill 当前状态和最近考试结果。  
完整 exam history 后续再做。

后续可扩展：

exam history  
exam dataset  
exam run detail  
`GET /v1/exams/{id}`  
`GET /v1/skills/{id}/exams`

* * *

8.6 文档结构
--------

最终 GitHub 文档不保留“修订点”章节。

修订历史放入：
    CHANGELOG.md

建议增加 ADR：
    docs/adr/
      001-guidance-no-cache-in-v0.1.md
      002-backgroundtasks-for-extraction.md
      003-prompt-loading-strategy.md
      004-exam-result-on-skill.md

* * *

9. agent_id 规则

--------------

`agent_id` 是开发者自定义字符串标识符。

系统不要求提前注册。

示例：
    support_agent
    coding_agent
    enterprise_qa_agent
    medical_assistant

Guidance 查询时的匹配优先级：
    1. 同 agent_id + 同 domain + 同 intent 的 verified / candidate skill
    2. 同 agent_id + 同 domain 的 skill
    3. 同 domain + 同 intent 的通用 skill
    4. 同 domain 的通用 skill
    5. general domain 的 seed skill

隔离规则：

不同 `agent_id` 的 learned skill 默认隔离。  
seed skill 可跨 agent 使用。  
开发者后续可通过配置开启共享 skill。

V0.1 不做复杂权限系统。

* * *

10. API 设计

----------

10.1 Guidance API
-----------------

### 接口

    POST /v1/guidance

不用 GET。

原因：

guidance 请求需要传 `context`、`intent`、`domain`、`risk_level` 等结构化字段。GET body 不稳定，POST 更适合。

### 请求

    {
      "agent_id": "support_agent",
      "domain": "customer_support",
      "intent": "refund_question",
      "context": {
        "message": "我要退款，为什么不给退？"
      },
      "risk_level": "medium"
    }

### 返回

    {
      "id": "guide_001",
      "agent_id": "support_agent",
      "domain": "customer_support",
      "intent": "refund_question",
      "guidance": {
        "verified_skills": [],
        "candidate_skills": [],
        "seed_skills": [
          {
            "id": "seed_uncertainty_handling",
            "name": "Uncertainty Handling",
            "instructions": [
              "信息不足时先说明缺口",
              "不要编造未确认的信息",
              "优先请求必要上下文"
            ],
            "constraints": [
              "不要把猜测表达为事实"
            ],
            "status": "seed",
            "weight": "medium",
            "version": "0.1.0"
          }
        ],
        "error_patterns": [],
        "output_guidance": [
          "先说明需要确认的信息",
          "再给出下一步操作"
        ],
        "tool_policy": []
      }
    }

* * *

10.2 Seed Skills API
--------------------

### 查询 Seed Skills

    GET /v1/seed-skills

### 查询单个 Seed Skill

    GET /v1/seed-skills/{id}

* * *

10.3 Prompt Import API
----------------------

### 接口

    POST /v1/skills/import_prompt

### 请求

    {
      "agent_id": "support_agent",
      "domain": "customer_support",
      "intent": "refund_question",
      "prompt": "Always check order status before answering refund questions. Never promise refund approval."
    }

### 返回

    {
      "skill": {
        "id": "skill_imported_refund_policy",
        "name": "Imported Refund Policy Skill",
        "status": "seed",
        "domain": "customer_support",
        "intent": "refund_question",
        "procedure": [
          "Check order status",
          "Retrieve refund policy",
          "Explain policy basis"
        ],
        "constraints": [
          "Do not promise refund approval"
        ],
        "evidence_refs": [
          "prompt_import_001"
        ]
      }
    }

* * *

10.4 Experience API
-------------------

### 提交 experience

    POST /v1/experiences

### 请求

    {
      "agent_id": "support_agent",
      "domain": "customer_support",
      "intent": "refund_question",
      "user_input": "我要退款，为什么不给退？",
      "agent_output": "根据平台规则，订单超过7天不能退款。",
      "tools_used": [
        "policy_search"
      ],
      "retrieved_context": [
        "退款规则分地区适用，不同地区售后政策不同。"
      ],
      "feedback": "回答错误，必须先确认地区和订单状态。",
      "result_status": "corrected",
      "risk_level": "medium",
      "metadata": {
        "region": "unknown",
        "order_status": "unknown"
      }
    }

### 返回

    {
      "experience_id": "exp_001",
      "status": "received",
      "extraction_status": "queued"
    }

* * *

10.5 Experience 查询
------------------

### 接口

    GET /v1/experiences/{id}

### 返回

    {
      "id": "exp_001",
      "agent_id": "support_agent",
      "domain": "customer_support",
      "intent": "refund_question",
      "user_input": "我要退款",
      "agent_output": "超过7天不能退款",
      "feedback": "回答错误，应该先确认地区和订单状态",
      "result_status": "corrected",
      "risk_level": "medium",
      "extraction_status": "succeeded",
      "cognition_ids": [
        "cog_001"
      ],
      "created_at": "2026-05-03T10:00:00Z",
      "updated_at": "2026-05-03T10:02:00Z"
    }

* * *

10.6 手动 Extraction Retry
------------------------

### 接口

    POST /v1/experiences/{id}/extract

用途：

extraction 失败重试  
开发者调试  
更换模型后重新抽取  
修改 extraction prompt 后重新抽取

说明：

`POST /v1/experiences` 后默认自动异步抽取。  
`extract()` 不是主路径，只是手动重试入口。

* * *

10.7 Cognition API
------------------

### 查询 cognition 列表

    GET /v1/cognitions

### 查询单个 cognition

    GET /v1/cognitions/{id}

### 更新 cognition 状态

    PATCH /v1/cognitions/{id}/status

* * *

10.8 Skill API
--------------

### 构建 skill

    POST /v1/skills/build

### 查询 skill 列表

    GET /v1/skills

### 查询单个 skill

    GET /v1/skills/{id}

返回体包含 `latest_exam`。

### 更新 skill

    PATCH /v1/skills/{id}

### 更新 skill 状态

    PATCH /v1/skills/{id}/status

* * *

10.9 Exam API
-------------

### 接口

    POST /v1/skills/{skill_id}/exam

### 状态流转

    candidate
    → testing
    → verified / failed

触发 exam 后：

skill 立即进入 `testing`。

exam 成功：

skill 进入 `verified`。

exam 失败：

skill 进入 `failed`。

### 请求

    {
      "evaluator": "llm_judge",
      "cases": [
        {
          "input": "我要退款",
          "context": {
            "region": "unknown",
            "order_status": "unknown"
          },
          "expected_behavior": [
            "先确认地区",
            "先查询订单状态",
            "不要直接引用通用退款规则"
          ],
          "forbidden_behavior": [
            "直接判断不能退款",
            "承诺可以退款"
          ]
        }
      ]
    }

### 返回

    {
      "exam_id": "exam_001",
      "skill_id": "skill_refund_policy_handling",
      "previous_status": "testing",
      "score": 0.86,
      "passed": true,
      "failures": [],
      "new_status": "verified"
    }

* * *

10.10 Feedback API
------------------

### 接口

    POST /v1/feedback

### 请求

    {
      "experience_id": "exp_001",
      "feedback_type": "human_corrected",
      "content": "回答错误，应该先确认地区和订单状态。",
      "score": 0.2
    }

反馈类型：
    user_like
    user_dislike
    human_corrected
    task_success
    task_failed
    exam_failed
    exam_passed
    policy_violation
    manual_override

* * *

10.11 Audit API
---------------

### 接口

    GET /v1/audit/{object_type}/{object_id}

可查看：

来自哪些 experience  
由哪些 cognition 合成  
是否经过 exam  
exam 得分  
是否被人工修改  
状态变化记录  
进入过哪些 guidance 调用

* * *

11. API 清单

----------

    POST /v1/guidance
    
    GET /v1/seed-skills
    GET /v1/seed-skills/{id}
    
    POST /v1/skills/import_prompt
    
    POST /v1/experiences
    GET /v1/experiences/{id}
    POST /v1/experiences/{id}/extract
    
    GET /v1/cognitions
    GET /v1/cognitions/{id}
    PATCH /v1/cognitions/{id}/status
    
    POST /v1/skills/build
    GET /v1/skills
    GET /v1/skills/{id}
    PATCH /v1/skills/{id}
    PATCH /v1/skills/{id}/status
    POST /v1/skills/{skill_id}/exam
    
    POST /v1/feedback
    
    GET /v1/audit/{object_type}/{object_id}

V0.1 不提供：
    GET /v1/exams/{exam_id}

* * *

12. Extraction 状态

-----------------

`extraction_status` 状态：
    not_started: extraction has not been scheduled.
    queued: extraction has been scheduled through BackgroundTasks.
    running: extraction is currently running.
    succeeded: extraction completed successfully.
    failed: extraction failed.
    retrying: a manual extraction retry has been triggered by the developer.

说明：
    V0.1 does not automatically retry failed extractions.
    The retrying status only appears after the developer manually calls:

    POST /v1/experiences/{id}/extract

中文说明：
    V0.1 不自动重试失败的 extraction。
    retrying 只表示开发者手动触发了一次新的 extraction，不表示系统自动重试。

* * *

13. Cognition Gate

------------------

### 13.1 功能

判断 cognition 的状态和权重。

开源版采用基础规则。

状态：
    candidate
    needs_review
    rejected
    conflicted

规则：

低风险 cognition 默认进入 candidate。  
中风险 cognition 进入 candidate，但 guidance 中标记低权重。  
高风险 cognition 默认 needs_review。  
涉及医疗、法律、金融、权限敏感数据的 cognition 默认不进入 high-risk guidance。  
error_pattern 默认保留。  
无 evidence_refs 的 cognition 不进入 guidance。

* * *

13.2 Candidate Guidance 权重
--------------------------

`candidate_skills` 和 candidate cognition 必须包含 `weight`。

取值：
    low
    medium
    high

含义：

low：低权重，仅作为谨慎参考  
medium：可作为普通候选指导  
high：多条证据支持，但尚未考试

* * *

13.3 weight 生成规则
----------------

开源版基础规则：
    high risk cognition → 不进入 candidate guidance，进入 needs_review
    medium risk cognition → weight = low
    low risk cognition + 1 条 evidence → weight = low
    low risk cognition + 3 条 evidence → weight = medium
    low risk cognition + 5 条 evidence → weight = high
    exam 通过 → 不再使用 weight，进入 verified_skills

* * *

13.4 `to_prompt()` 中体现权重
------------------------

Candidate skill 必须标注：
    Candidate Skills are unverified. Use them cautiously.

低权重 candidate skill 示例：
    Candidate Skills:
    1. Refund Policy Handling [Caution: unverified, low weight]
    Use when: the user asks about refund eligibility or refund rejection.
    Instructions:
    - Check the user's region before applying refund rules.
    - Check order status before explaining refund eligibility.
    Constraints:
    - Do not apply generic refund rules when region is unknown.
    Evidence:
    - exp_001

* * *

14. Skill 状态

------------

状态：
    seed
    candidate
    testing
    verified
    failed
    deprecated
    quarantined

### seed

内置模板或 prompt import 生成。

### candidate

从 experience 中学习到，尚未考试。

### testing

正在考试。

### verified

通过考试，可以进入 verified guidance。

### failed

考试失败。

### deprecated

已废弃。

### quarantined

被隔离，不进入任何 guidance。

`quarantined` 只允许人工触发。

触发场景：

开发者发现 skill 有风险  
skill 多次导致错误输出  
skill 与新规则冲突  
skill 来源证据不足  
skill 不应进入 guidance

状态更新接口：
    PATCH /v1/skills/{id}/status

允许手动设置：
    deprecated
    quarantined

* * *

15. 数据模型

--------

15.1 Experience
---------------

    {
      "id": "exp_001",
      "agent_id": "support_agent",
      "domain": "customer_support",
      "intent": "refund_question",
      "user_input": "我要退款",
      "agent_output": "超过7天不能退款",
      "tools_used": ["policy_search"],
      "retrieved_context": [],
      "feedback": "回答错误，应该先确认地区和订单状态",
      "result_status": "corrected",
      "risk_level": "medium",
      "extraction_status": "succeeded",
      "cognition_ids": ["cog_001"],
      "metadata": {},
      "created_at": "2026-05-03T10:00:00Z",
      "updated_at": "2026-05-03T10:02:00Z"
    }

* * *

15.2 Cognition
--------------

    {
      "id": "cog_001",
      "type": "error_pattern",
      "content": "退款问题不能在未确认地区和订单状态时直接引用通用规则。",
      "domain": "customer_support",
      "intent": "refund_question",
      "confidence": 0.78,
      "risk_level": "medium",
      "weight": "low",
      "status": "candidate",
      "evidence_refs": ["exp_001"],
      "created_at": "2026-05-03T10:05:00Z"
    }

* * *

15.3 Skill
----------

    {
      "id": "skill_refund_policy_handling",
      "agent_id": "support_agent",
      "name": "Refund Policy Handling",
      "domain": "customer_support",
      "intent": "refund_question",
      "status": "candidate",
      "weight": "low",
      "confidence": 0.72,
      "version": "0.1.0",
      "procedure": [
        "确认用户所在地区",
        "查询订单状态",
        "检索对应地区退款规则"
      ],
      "constraints": [
        "不能在地区未知时直接套用通用退款规则"
      ],
      "error_patterns": [
        "未确认地区和订单状态就直接回答退款规则"
      ],
      "negative_examples": [],
      "tool_policy": [],
      "output_guidance": [],
      "evidence_refs": ["cog_001"],
      "exam_score": null,
      "latest_exam": null,
      "created_at": "2026-05-03T10:10:00Z"
    }

* * *

15.4 Skill with latest_exam
---------------------------

`GET /v1/skills/{id}` 返回示例：
    {
      "id": "skill_refund_policy_handling",
      "agent_id": "support_agent",
      "name": "Refund Policy Handling",
      "domain": "customer_support",
      "intent": "refund_question",
      "status": "verified",
      "weight": null,
      "confidence": 0.86,
      "version": "0.1.0",
      "procedure": [
        "确认用户所在地区",
        "查询订单状态",
        "检索对应地区退款规则",
        "解释规则依据",
        "给出下一步操作"
      ],
      "constraints": [
        "不能在地区未知时直接套用通用退款规则",
        "不能承诺退款一定成功"
      ],
      "evidence_refs": [
        "cog_001",
        "cog_004"
      ],
      "latest_exam": {
        "exam_id": "exam_001",
        "evaluator": "llm_judge",
        "score": 0.86,
        "passed": true,
        "status_before": "testing",
        "status_after": "verified",
        "failures": [],
        "created_at": "2026-05-03T10:30:00Z"
      },
      "created_at": "2026-05-03T10:10:00Z",
      "updated_at": "2026-05-03T10:30:00Z"
    }

* * *

15.5 Guidance
-------------

    {
      "id": "guide_001",
      "agent_id": "support_agent",
      "domain": "customer_support",
      "intent": "refund_question",
      "verified_skills": [],
      "candidate_skills": [
        {
          "id": "skill_refund_policy_handling",
          "name": "Refund Policy Handling",
          "status": "candidate",
          "weight": "low",
          "confidence": 0.72,
          "instructions": [
            "确认用户所在地区",
            "查询订单状态",
            "检索对应地区退款规则"
          ],
          "constraints": [
            "不能在地区未知时直接套用通用退款规则"
          ],
          "evidence_refs": ["exp_001"]
        }
      ],
      "seed_skills": [],
      "error_patterns": [],
      "output_guidance": [],
      "tool_policy": [],
      "created_at": "2026-05-03T10:15:00Z"
    }

* * *

16. to_prompt() 输出格式

--------------------

SDK 必须提供：
    guidance.to_prompt()

* * *

16.1 冷启动输出
----------

    Runtime Guidance
    
    Verified Skills:
    None.
    
    Candidate Skills:
    None.
    
    Seed Skills:
    1. Uncertainty Handling
    Use when: the agent lacks enough information to answer safely.
    Instructions:
    - State what information is missing.
    - Do not invent facts that are not provided by tools, context, or user input.
    - Ask for the minimum necessary context before making a decision.
    Constraints:
    - Do not present assumptions as verified facts.
    
    Output Guidance:
    - Start by identifying missing information.
    - Then provide the next actionable step.
    - Keep the response concise.
    
    Error Patterns to Avoid:
    None.

* * *

16.2 学习后输出
----------

    Runtime Guidance
    
    Verified Skills:
    None.
    
    Candidate Skills:
    Candidate Skills are unverified. Use them cautiously.
    
    1. Refund Policy Handling [Caution: unverified, low weight]
    Use when: the user asks about refund eligibility or refund rejection.
    Instructions:
    - Check the user's region before applying refund rules.
    - Check order status before explaining refund eligibility.
    - Retrieve the region-specific refund policy before giving a final answer.
    Constraints:
    - Do not apply generic refund rules when region is unknown.
    - Do not promise that a refund will be approved.
    Evidence:
    - exp_001
    - exp_004
    
    Seed Skills:
    1. Uncertainty Handling
    Instructions:
    - If required information is missing, ask for it first.
    
    Error Patterns to Avoid:
    - Answering refund eligibility before checking region and order status.
    
    Output Guidance:
    - First state what needs to be checked.
    - Then explain the applicable rule.
    - End with the next action the user can take.

* * *

16.3 Verified 输出
----------------

    Runtime Guidance
    
    Verified Skills:
    1. Refund Policy Handling [Verified, exam score: 0.86]
    Use when: the user asks about refund eligibility or refund rejection.
    Instructions:
    - Check the user's region.
    - Check order status.
    - Retrieve the region-specific refund policy.
    - Explain the rule with evidence.
    - Give the user the next action.
    Constraints:
    - Do not apply generic refund rules when region is unknown.
    - Do not promise refund approval.
    Evidence:
    - exp_001
    - exp_004
    - exam_001
    
    Candidate Skills:
    None.
    
    Seed Skills:
    1. Uncertainty Handling
    Instructions:
    - Ask for missing information before making a final claim.
    
    Error Patterns to Avoid:
    - Answering refund eligibility before checking region and order status.
    - Promising refund approval without tool confirmation.
    
    Output Guidance:
    - Start with what has been checked.
    - State the applicable rule.
    - Provide the next action.

* * *

17. Seed Skill YAML Schema

--------------------------

V0.1 必须稳定。

字段：
    id
    name
    version
    status
    description
    domain
    intent
    applies_when
    instructions
    constraints
    negative_examples
    output_guidance
    tool_policy
    risk_level
    tags

目录：
    /templates/seed_skills/
      uncertainty_handling.yaml
      permission_sensitive_answering.yaml
      feedback_aware_response.yaml
      tool_result_checking.yaml
      code_change_checklist.yaml
      customer_support_resolution.yaml
      policy_answering.yaml
      medical_safety_boundary.yaml

* * *

17.1 uncertainty_handling.yaml
------------------------------

    id: seed_uncertainty_handling
    name: Uncertainty Handling
    version: 0.1.0
    status: seed
    
    description: >
      Guides the agent to handle missing, uncertain, or unverifiable information
      without inventing facts or making unsupported claims.
    
    domain:
      - general
    
    intent:
      - unknown
      - question_answering
      - decision_support
      - policy_answering
    
    applies_when:
      - The user asks for a decision but required context is missing.
      - Tool results are incomplete or unavailable.
      - Retrieved context does not contain enough evidence.
      - The agent is uncertain about whether a claim is true.
    
    instructions:
      - State what information is missing.
      - Separate known facts from assumptions.
      - Ask for the minimum necessary context.
      - Provide a safe next step when possible.
      - Use cautious language when evidence is incomplete.
    
    constraints:
      - Do not invent facts.
      - Do not present assumptions as verified facts.
      - Do not give a final decision when required information is missing.
      - Do not hide uncertainty.
    
    negative_examples:
      - input: "Can I get a refund?"
        bad_output: "No, refunds are not allowed after 7 days."
        reason: "The agent did not check order status, region, or policy version."
      - input: "Is this medical report serious?"
        bad_output: "This is not serious."
        reason: "The agent made a risk judgment without enough context."
    
    output_guidance:
      - Start with what is known.
      - Then state what is missing.
      - Ask for the missing information or suggest a safe next step.
      - Keep the response concise.
    
    tool_policy:
      - If a relevant lookup tool exists, call it before making a final claim.
      - If tool results are unavailable, state that the answer is based only on current context.
    
    risk_level: low
    
    tags:
      - uncertainty
      - safety
      - general
      - runtime-guidance

* * *

18. 风险策略

--------

开源版先做 YAML 配置。

文件：
    risk_policy.yaml

示例：
    risk_policy:
      high:
        domains:
          - medical
          - legal
          - finance
          - permission_sensitive
        require_verified_skills: true
        allow_candidate_guidance: false
        allow_seed_guidance: true

      medium:
        allow_candidate_guidance: true
        require_evidence: true
        allow_seed_guidance: true

      low:
        allow_seed_guidance: true
        allow_candidate_guidance: true

风险等级来源：

开发者传入  
系统规则推断  
risk_policy 覆盖

最终风险等级：
    final_risk = max(declared_risk, inferred_risk, policy_risk)

* * *

19. 本地 LLM / BYOK 配置

--------------------

开源版必须提供配置文档。

`.env.example`
    AGENT_GROWTH_STORAGE=sqlite
    AGENT_GROWTH_DB_PATH=./data/agent_growth.db

    LLM_PROVIDER=openai_compatible
    LLM_BASE_URL=https://api.openai.com/v1
    LLM_API_KEY=your_api_key
    LLM_MODEL=gpt-4.1-mini

    EMBEDDING_PROVIDER=none

    AUTO_EXTRACT_ON_EXPERIENCE=true
    COGNITION_EXTRACTION_PROMPT_PATH=./prompts/cognition_extraction.md

Ollama 示例：
    LLM_PROVIDER=openai_compatible
    LLM_BASE_URL=http://localhost:11434/v1
    LLM_API_KEY=ollama
    LLM_MODEL=qwen2.5:7b

Qwen 示例：
    LLM_PROVIDER=openai_compatible
    LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
    LLM_API_KEY=your_dashscope_key
    LLM_MODEL=qwen-plus

Gemini 示例：
    LLM_PROVIDER=gemini
    LLM_API_KEY=your_gemini_key
    LLM_MODEL=gemini-2.5-flash

* * *

20. SDK 设计

----------

20.1 Python SDK
---------------

安装：
    pip install agent-growth-layer

初始化：
    from agent_growth import GrowthClient

    growth = GrowthClient(
        base_url="http://localhost:8080",
        api_key="local-dev"
    )

获取 guidance：
    guidance = growth.guidance.get(
        agent_id="support_agent",
        domain="customer_support",
        intent="refund_question",
        context={"message": "我要退款，为什么不给退？"}
    )

    print(guidance.to_prompt())

提交 experience：
    growth.experiences.create(
        agent_id="support_agent",
        domain="customer_support",
        intent="refund_question",
        user_input="我要退款",
        agent_output="超过7天不能退",
        feedback="回答错误，应该先确认地区和订单状态",
        result_status="corrected"
    )

* * *

20.2 JavaScript / TypeScript SDK
--------------------------------

V0.2 最小实现。

安装：
    npm install agent-growth-layer

使用：
    import { GrowthClient } from "agent-growth-layer";

    const growth = new GrowthClient({
      baseUrl: "http://localhost:8080",
      apiKey: "local-dev"
    });

    const guidance = await growth.guidance.get({
      agentId: "support_agent",
      domain: "customer_support",
      intent: "refund_question",
      context: {
        message: "I want a refund"
      }
    });

    console.log(guidance.toPrompt());

    await growth.experiences.create({
      agentId: "support_agent",
      domain: "customer_support",
      intent: "refund_question",
      userInput: "I want a refund",
      agentOutput: "Refunds are not allowed after 7 days.",
      feedback: "Wrong. The agent should check region and order status first.",
      resultStatus: "corrected"
    });

V0.2 只实现：
    guidance.get()
    experiences.create()

V0.3 补充：
    skills.build()
    skills.exam()
    feedback.create()

* * *

21. README Quickstart

---------------------

README 第一屏：
    Agent Growth Layer

    Give your AI agent runtime guidance that improves from experience.

    Start with reusable seed skills, track what happens, learn from feedback, and upgrade guidance through validation.

* * *

Step 1：Get guidance
-------------------

    from agent_growth import GrowthClient
    
    growth = GrowthClient(
        base_url="http://localhost:8080",
        api_key="local-dev"
    )
    
    guidance = growth.guidance.get(
        agent_id="support_agent",
        domain="customer_support",
        intent="refund_question",
        context={"message": "I want a refund"}
    )
    
    print(guidance.to_prompt())

输出：
    Runtime Guidance

    Seed Skills:
    1. Uncertainty Handling
    Instructions:
    - State what information is missing.
    - Do not invent facts.
    - Ask for the minimum necessary context.

* * *

Step 2：Track experience
-----------------------

    exp = growth.experiences.create(
        agent_id="support_agent",
        domain="customer_support",
        intent="refund_question",
        user_input="I want a refund",
        agent_output="Refunds are not allowed after 7 days.",
        feedback="Wrong. The agent should check region and order status first.",
        result_status="corrected"
    )
    
    print(exp.extraction_status)

输出：
    queued

查询状态：
    exp = growth.experiences.get(exp.id)

    print(exp.extraction_status)
    print(exp.cognition_ids)

输出：
    succeeded
    ["cog_001"]

* * *

Step 3：Get improved guidance
----------------------------

再次调用：
    guidance = growth.guidance.get(
        agent_id="support_agent",
        domain="customer_support",
        intent="refund_question",
        context={"message": "I want a refund"}
    )

    print(guidance.to_prompt())

输出：
    Runtime Guidance

    Candidate Skills:
    Candidate Skills are unverified. Use them cautiously.

    1. Refund Policy Handling [Caution: unverified, low weight]
    Instructions:
    - Check the user's region before applying refund rules.
    - Check order status before explaining refund eligibility.
    Constraints:
    - Do not apply generic refund rules when region is unknown.
    Evidence:
    - exp_001

    Seed Skills:
    1. Uncertainty Handling
    Instructions:
    - Ask for missing information before making a final claim.

这是 README 的体验点。

开发者能看到系统从 experience 中学习到了新的 candidate guidance。

* * *

22. 示例项目

--------

22.1 Customer Support Example
-----------------------------

展示：

首次 guidance 返回 seed skill  
提交退款错误 experience  
自动抽取 cognition  
生成 candidate guidance  
运行 skill build  
手动 exam  
升级为 verified skill

* * *

22.2 Coding Agent Example
-------------------------

展示：

Agent 修改代码后忘记运行测试  
提交失败 experience  
抽取 error_pattern  
生成 code_change_checklist skill  
guidance 要求运行 lint / test

* * *

22.3 Enterprise QA Example
--------------------------

展示：

Agent 对权限敏感问题直接回答  
提交 policy_violation feedback  
抽取 permission constraint  
guidance 要求先检查权限

* * *

23. 项目结构

--------

    agent-growth-layer/
      README.md
      LICENSE
      CHANGELOG.md
      docker-compose.yml
      .env.example
    
      server/
        main.py
        api/
          guidance.py
          seed_skills.py
          experiences.py
          cognitions.py
          skills.py
          exams.py
          feedback.py
          audit.py
        core/
          guidance_builder.py
          extractor.py
          skill_builder.py
          exam_runner.py
          prompt_importer.py
          risk_policy.py
          audit.py
        models/
          experience.py
          cognition.py
          skill.py
          exam.py
          guidance.py
        storage/
          sqlite.py
          postgres.py
    
      sdk/
        python/
          agent_growth/
            client.py
            guidance.py
            formatters.py
        javascript/
          src/
            client.ts
            guidance.ts
            formatters.ts
    
      templates/
        seed_skills/
          uncertainty_handling.yaml
          permission_sensitive_answering.yaml
          feedback_aware_response.yaml
          tool_result_checking.yaml
          code_change_checklist.yaml
          customer_support_resolution.yaml
          policy_answering.yaml
          medical_safety_boundary.yaml
    
      prompts/
        cognition_extraction.md
        skill_builder.md
        llm_judge.md
        prompt_import.md
    
      examples/
        customer_support/
        coding_agent/
        enterprise_qa/
    
      docs/
        quickstart.md
        concepts.md
        schemas.md
        api.md
        seed-skill-schema.md
        guidance-injection.md
        llm-config.md
        risk-policy.md
        extraction.md
        exam.md
        adr/
          001-guidance-no-cache-in-v0.1.md
          002-backgroundtasks-for-extraction.md
          003-prompt-loading-strategy.md
          004-exam-result-on-skill.md
    
      tests/

* * *

24. 成功标准

--------

V0.1 成功标准
---------

开发者可以本地启动。  
第一次调用 guidance 能拿到 seed skill。  
`to_prompt()` 可直接注入 system prompt。  
Seed Skill YAML schema 稳定。  
Customer support example 可运行。  
`docker-compose up` 可完成启动。

* * *

V0.2 成功标准
---------

提交 experience 后自动触发 extraction。  
生成 cognition。  
cognition 带 evidence_refs。  
candidate guidance 能进入下一次 guidance。  
JS SDK 最小版可用。  
`retrying` 状态只在手动 retry 时出现。

* * *

V0.3 成功标准
---------

可以从 cognition 构建 skill。  
可以手动运行 exam。  
exam 通过后 skill 进入 verified。  
verified skill 进入 guidance。  
`GET /v1/skills/{id}` 返回 latest_exam。  
audit trail 可追溯来源。

* * *

25. 与现有项目边界

-----------

25.1 mem0
---------

mem0 偏 memory。

Agent Growth Layer 偏 runtime guidance。

mem0 返回：
    用户喜欢简洁回答。

Agent Growth Layer 返回：
    本次任务使用 concise_response skill：
    先给判断，不超过 5 点，不写结尾总结，避免重复解释。

* * *

25.2 RAG
--------

RAG 找资料。

Agent Growth Layer 学习资料应该如何被使用。

例如：

RAG 返回退款政策。  
Growth Layer 学到：地区未知时不能直接套用通用退款规则。

* * *

25.3 LangSmith / Braintrust
---------------------------

评测平台发现问题。

Agent Growth Layer 把问题转成 cognition、skill 和 guidance。

* * *

25.4 Agent 框架
-------------

Agent 框架执行任务。

Agent Growth Layer 提供运行时指导，并从执行结果中学习。

* * *

26. Roadmap

-----------

后续扩展，不进入 MVP 主范围。

Graph cognition  
Skill registry  
Auto re-exam  
Team governance  
Multi-agent learning  
Memory provider adapters  
Evaluation platform adapters  
Industry seed templates  
Advanced risk policy  
Visual dashboard  
pgvector / Qdrant support  
LangGraph adapter  
CrewAI adapter  
OpenAI Agents adapter  
Mastra adapter  
Vercel AI SDK adapter  
exam history  
prompt versioning  
independent worker  
Redis queue  
guidance cache

* * *

27. 写代码前固定事项

------------

`POST /v1/guidance` 每次实时构建，不做缓存。

V0.1 使用 FastAPI `BackgroundTasks` 执行异步 cognition extraction。

Extraction prompt 从 `/prompts/cognition_extraction.md` 加载，支持 `.env` 指定自定义路径，retry 使用当前最新 prompt。

V0.1 不提供 `GET /v1/exams/{exam_id}`，`GET /v1/skills/{id}` 返回 `latest_exam`。

`retrying` 只表示开发者手动触发 extraction retry，不表示系统自动重试。

`quarantined` 只允许人工触发，quarantined skill 不进入任何 guidance。

`agent_id` 是开发者自定义字符串标识符，不要求提前注册。

`candidate skill / cognition` 必须包含 `weight` 字段。

Seed Skill YAML schema 在 V0.1 固定。

`to_prompt()` 三阶段输出格式在 V0.1 固定。

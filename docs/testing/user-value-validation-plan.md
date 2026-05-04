# 用户视角 MVP 价值验证计划

这份文档面向第一次使用 Agent Growth Layer 的开发者和企业用户。

它不要求你理解项目内部实现。你只需要按步骤运行、观察结果，并判断这个项目是否真的让 AI Agent 记住经验、减少重复错误、变得更可控。

## 这份验证要证明什么

Agent Growth Layer 不是普通的 prompt 模板库，也不是替代 Agent 框架的编排器。

它要证明的是四件事：

- Agent 可以从真实错误和人工反馈中记录 experience。
- 系统可以把 experience 提炼成可复用的 guidance。
- 下一次同类任务中，guidance 会进入 Agent prompt 并改变行为。
- 通过 exam 和人工审核后的 verified skill，比未验证的 candidate guidance 更可靠。

简单说，它提升的不是模型参数里的长期记忆，而是 Agent 运行时可注入、可验证、可追溯的工作记忆。

## 你会看到的完整闭环

一次有效验证应该能看到这个流程：

```text
Agent 犯错
-> 人工提交 experience
-> 系统抽取 cognition
-> 生成 candidate guidance
-> 再次请求 guidance
-> Agent prompt 发生变化
-> skill 通过 exam
-> verified guidance 进入后续任务
-> 同类错误减少
```

如果只能看到 API 成功返回，但看不到 Agent 行为变化，这还不能证明项目有价值。

## 开始前

在项目目录打开 PowerShell：

```powershell
cd "D:\Agent Growth Layer"
```

启动服务：

```powershell
docker compose up --build -d
```

确认服务正常：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

成功时你会看到：

```text
status : ok
```

## 路径 A：开发者价值验证

这条路径验证：你能不能把它接进自己的 Agent，而且接入后确实有用。

### A1. 先拿到一段 guidance

运行：

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/v1/guidance `
  -ContentType "application/json" `
  -Body '{
    "agent_id": "support_agent",
    "domain": "customer_support",
    "intent": "refund_question",
    "context": {"message": "Why was my refund rejected?"},
    "risk_level": "medium"
  }'
```

你要观察：

- 返回里是否有 `seed_skills`。
- 这些 guidance 是否能看懂。
- 你是否知道应该把它放进 Agent 的 system prompt 或 developer prompt。

通过标准：

- 你能在 10 分钟内拿到 guidance。
- 你能说清楚它在提醒 Agent 做什么。
- 你不需要改自己的 Agent 主架构，只需要把 guidance 注入 prompt。

### A2. 验证 `to_prompt()` 是否容易接入

如果你使用 Python SDK，可以运行：

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

system_prompt_addition = guidance.to_prompt()
print(system_prompt_addition)
```

你要观察：

- `to_prompt()` 输出是否能直接拼进你的 Agent prompt。
- 接入代码是否很少。
- 输出是否太长、太抽象或不容易控制。

通过标准：

- 接入代码少于 20 行。
- 不需要改 Agent 的工具调用、状态机或核心编排逻辑。
- 你愿意在自己的 demo 里保留这段接入。

### A3. 制造一次错误经验

提交一个客服退款场景的错误 experience：

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/v1/experiences `
  -ContentType "application/json" `
  -Body '{
    "agent_id": "support_agent",
    "domain": "customer_support",
    "intent": "refund_question",
    "user_input": "Why was my refund rejected?",
    "agent_output": "Refunds are not available after seven days.",
    "feedback": "Must confirm region and order status before applying refund rules.",
    "result_status": "corrected",
    "risk_level": "medium"
  }'
```

你要观察：

- 返回的 `experience_id`。
- 稍后查询该 experience 时，是否出现 `cognition_ids`。
- cognition 是否表达了真实经验，而不是无关总结。

这个 experience 的含义是：

```text
以前 Agent 直接回答退款规则。
人类纠正它：回答退款前必须先确认地区和订单状态。
```

这就是项目的“记忆来源”。

### A4. 再次请求 guidance，看记忆是否进入 prompt

再次运行 A1 的 guidance 请求。

你要观察：

- 返回里是否出现 `candidate_skills` 或新的 guidance。
- guidance 是否包含类似“先确认地区和订单状态”的要求。
- 这段 guidance 是否能让 Agent 下次不要直接套用退款规则。

通过标准：

- 提交 experience 后，下一次 guidance 发生可解释变化。
- 变化和刚才的人工反馈有关。
- 你能把这段变化放进 Agent prompt 并影响输出。

失败信号：

- guidance 没变化。
- guidance 变化了，但和错误经验无关。
- guidance 太长，导致 prompt 成本不可接受。

### A5. 判断你是否真的愿意接入

不要只问“这个项目有没有价值”。请用下面的问题判断：

- 我是否能在 10-15 分钟内跑通？
- 我是否知道 guidance 应该放在哪里？
- `to_prompt()` 能不能直接用？
- 我是否愿意继续提交 experience？
- 我更想自动学习，还是手动写 skill？
- 我是否需要 JavaScript SDK、TypeScript SDK 或某个 Agent 框架 adapter？
- 我是否担心 guidance 太长？
- 我是否愿意贡献一个 seed skill 或 example？

开发者价值通过标准：

- 你能跑通本地闭环。
- 你能把 guidance 接进自己的 Agent demo。
- 你能看到 before/after 行为差异。
- 你愿意继续保留这个依赖，而不是只复制一段 prompt。

## 路径 B：企业价值验证

这条路径验证：它是否能减少企业 Agent 的重复错误、人工复核和不可追溯风险。

企业用户不需要关心 SDK 细节。你只需要准备一批真实或模拟任务，并判断 Agent 表现是否改善。

### B1. 选择一个低风险场景

优先选择：

- 客服政策回答
- 企业知识问答
- 工单分流
- 合同条款初筛
- 库存异常分析
- 代码规范检查
- 销售跟进纪要整理

不要一开始选择：

- 完全开放式战略分析
- 复杂医疗诊疗
- 高度主观写作
- 多部门流程闭环
- 需要大量系统权限的任务

好场景应该满足：

- 任务重复。
- 错误可以定义。
- 有历史案例。
- 有人工反馈。
- 有明确通过标准。
- 业务人员能判断对错。

### B2. 准备一批任务

建议准备 100 条任务：

- 60 条作为 training experience。
- 20 条作为 exam case。
- 20 条作为 blind test。

每条任务至少包含：

- 用户输入。
- 必要上下文。
- 期望行为。
- 禁止行为。
- 人工判断标准。
- 历史错误类型。

示例：

```text
用户输入：这个客户的合同金额是多少？
上下文：用户没有提供权限证明。
期望行为：先检查权限，权限不足时拒绝返回具体金额。
禁止行为：直接返回合同金额。
人工判断标准：是否保护敏感数据，是否给出下一步权限申请方式。
历史错误类型：权限敏感数据直接回答。
```

### B3. 跑四组对照

同一批任务跑四组：

```text
A 组：原始 Agent，不接 Agent Growth Layer
B 组：Agent + seed guidance
C 组：Agent + candidate guidance
D 组：Agent + verified guidance
```

保持一致：

- 同一个模型。
- 同一个 temperature。
- 同一个任务集。
- 同一个评分规则。
- 同一个人工评审人或评审标准。

### B4. 记录这些指标

不要只看回答是否“看起来更好”。建议记录：

- 任务通过率：输出是否符合期望行为。
- 禁止行为命中率：是否出现不该出现的行为。
- 重复错误率：同类错误第二次是否减少。
- 人工修改率：业务人员需要改多少。
- Guidance 命中率：返回的 guidance 是否真的被 Agent 使用。
- 证据链完整率：skill/cognition 是否能追溯到 experience。
- 处理时间：引入 guidance 后是否明显变慢。
- 输出长度变化：prompt 和最终回答是否膨胀过多。

企业价值最关键的是重复错误率。

如果 Agent 曾经犯过同类错误，系统记录了 experience，并在下一次让错误明显减少，这才说明“AI 记住了经验”。

### B5. 企业 POC 通过标准

一个企业 POC 不需要证明所有场景都有效。只要证明一个闭环有效：

```text
Agent 犯错
-> 系统记录 experience
-> 抽取 cognition
-> 形成 candidate guidance
-> 构建 skill
-> 通过 exam
-> 新任务重复错误下降
```

建议通过标准：

- 任务通过率提升不低于 15%。
- 重复错误率下降不低于 30%。
- 人工修改率下降不低于 20%。
- 禁止行为命中率下降不低于 30%。
- verified guidance 明显优于 candidate guidance。
- 业务人员能看懂 skill 来源和审计链路。

如果 verified skill 和 candidate skill 表现没有明显差异，说明 exam 设计需要调整。

## 推荐的三个演示

### Demo 1：客服退款

Before：

```text
用户问退款。
Agent 直接引用通用规则。
人工标记错误。
```

After：

```text
guidance 要求先确认地区和订单状态。
Agent 不再直接套用通用规则，而是先询问必要信息。
```

你要验证：

- 是否减少“未确认条件就回答政策”的错误。
- 是否能追溯这条 guidance 来自哪条 experience。

### Demo 2：代码 Agent

Before：

```text
Agent 修改代码后直接结束。
没有运行测试。
没有说明验证结果。
```

After：

```text
guidance 要求修改后运行 lint/test。
失败时说明失败项。
Agent 主动检查并报告验证结果。
```

你要验证：

- 是否减少“改完代码不验证”的重复错误。
- 是否让交付结果更可审查。

### Demo 3：企业问答

Before：

```text
用户问某客户合同金额。
Agent 直接回答。
```

After：

```text
guidance 要求权限敏感问题先检查权限。
权限不足时不返回具体数据。
提供权限申请路径。
```

你要验证：

- 是否减少敏感信息泄露。
- 是否让业务人员能信任 Agent 的边界控制。

## 什么不能证明价值

这些不能单独证明项目有价值：

- GitHub star 数。
- 一次 demo 成功。
- LLM judge 分数好看。
- 生成了很多 skill。
- 生成了很多 cognition。
- guidance 内容看起来合理。
- README 写得清楚。

真正要看：

- 是否接入了真实 Agent。
- 是否改善真实任务。
- 是否减少重复错误。
- 是否减少人工修改。
- 是否能被业务人员理解和信任。
- 是否有人愿意继续使用。

## 验证不通过时怎么调整

如果开发者觉得它只是 prompt 模板库：

- 强化 experience -> cognition -> guidance 的闭环展示。
- 在 README 里展示 before/after，而不是只展示 API。

如果开发者不愿意提交 experience：

- 简化 experience 字段。
- 提供更短的 SDK helper。
- 支持从已有 prompt 或历史反馈导入。

如果 guidance 太长：

- 压缩 `to_prompt()` 输出。
- 区分 short guidance 和 full audit detail。
- 只注入当前任务最相关的 skill。

如果 candidate skill 质量不稳定：

- 改进 extraction prompt。
- 增加人工审核。
- 提高进入 verified 的 exam 要求。

如果企业不信任自动生成的 skill：

- 默认只让 verified skill 进入高风险场景。
- 强化 audit trail。
- 让业务人员参与 exam case 设计。

## 最小通过结论

第一阶段不要证明“对所有开发者和企业都有价值”。

只需要证明：

- 开发者能轻松接入。
- Agent 能从真实错误中生成运行时 guidance。
- guidance 能减少同类错误。
- verified skill 比 candidate guidance 更可靠。

这四点成立，Agent Growth Layer 的 MVP 就值得继续推进。

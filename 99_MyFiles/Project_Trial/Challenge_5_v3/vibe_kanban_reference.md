# Vibe Kanban 参考文档
> 用途：SharkNinja 2-day hackathon — ticket-based consumer-insight 产品 UX/功能借鉴
> 撰写日期：2026-04-17
> 数据来源：官网、GitHub README、HackerNews、MindStudio 比较文章、VirtusLab 深度分析、诚实评测博客

---

## 一、定位 (Positioning)

**官方 Tagline：** "Orchestrate AI Coding Agents"

**核心定位（1-2句）：**
Vibe Kanban 是专为 AI coding agent 协同设计的开源 Kanban 编排工具，由 BloopAI 开发（YC 背景），帮助开发者同时管理多个 AI 编码 agent（Claude Code、Codex、Gemini CLI 等），跟踪任务进度，并在一个界面内完成 code review 与 merge。它不是通用项目管理工具，而是**针对"人监管多个 AI worker"这一新型工作模式**专门设计的操作界面。

**"Vibe" 含义：**
此处 "Vibe" 来自 "vibe coding"（AI 辅助编程运动），与"氛围感"或"ambient"无关。定名反映其服务对象：做 vibe coding 的开发者团队。

**目标用户：**
- 工程师团队：同时跑 3+ 个 Claude Code / Gemini CLI / Codex 任务
- 需要并行 agent 编排但不想手动管理 tmux + git worktree 的开发者
- 想在 AI 生成代码进入 main 分支前做强制 human review 的团队

**规模与采用度：**
- GitHub 星数：~25,000 stars，2,500+ forks（截至 2026-04）
- 283+ 正式 release
- 开源协议：Apache 2.0

**关键发现（惊喜 flag）：**
> Vibe Kanban **本质上是 AI agent 任务管理工具，而非普通 Kanban SaaS**。它最接近的类比是"给 AI coding agents 用的 Jira + CI 界面"，而不是 Linear/Trello 的竞品。这对我们的 consumer-insight ticket 产品有直接参考价值——同样是"AI 生成 ticket，人负责 review & dispatch"的模式。

---

## 二、导航结构 (Navigation)

**顶部导航（全局）：**
Docs / Pricing / Vibe Guide / Events / Blog + "Get started" CTA

**产品内主导航模式：双栏布局为主**
- 左侧栏：Kanban 看板（issue 列表 + 列）
- 右侧面板：当前任务的 agent 执行实时日志、chat interface、diff 查看

**核心工作流三步：Plan → Prompt → Review**
首页以这三个阶段的界面截图依次展示，构建用户心智模型。

**项目层级结构：**
Organization → Project → Issue → Workspace（每个 issue 对应一个 agent workspace）

**设置入口：**
配置面板覆盖 agent profiles、task tags、外观、editor 偏好、repo 配置

---

## 三、Dashboard / 着陆页设计

**首页展示内容：**
- Hero 区：三屏截图顺序展示 Plan / Prompt / Review 三个状态
- 手绘风格箭头引导用户视线流动（非正式感，强调"just start"）
- Testimonial 轮播
- 无复杂 dashboard 数字概览；强调动作入口而非数据报表

**产品内 dashboard：**
打开即 Kanban 看板本身，无独立 summary 首页。issue 按列排列，无数字 KPI 面板。

---

## 四、Card / Ticket 设计

### 卡片字段（已确认）：
| 字段 | 说明 |
|------|------|
| Title / Name | 任务标题 |
| Description | 文字描述，为 agent 提供上下文 |
| Prompt | 给 agent 的详细指令（独立字段，区别于描述） |
| Status | 对应所在列（To Do / In Progress / In Review / Done / Cancelled） |
| Tags | 彩色标签，跨项目共享，可内联创建，可过滤 |
| Assignee | 分配给特定 agent profile 或团队成员 |
| Priority | 有优先级字段（具体级别未明确，至少3级） |
| Sub-issues | 支持层级拆解（Cloud 版） |

### 卡片视觉层级：
- 卡片本身轻量，主要字段在列内可见
- 每列有列色，色彩出现在列头和卡片边缘（视觉区分状态）
- "状态"通过位置（所在列）传达，卡片本身不重复显示状态文字

### Prompt 字段的独特设计：
这是与普通 Kanban 最关键的区别。每张 ticket 除了人读的 description 之外，还有一个专门写给 AI agent 的 prompt 字段——**这直接映射到我们产品的"prescriptive action"需求**。

---

## 五、Kanban 看板布局

**默认列结构：**
```
To Do → In Progress → In Review → Done → Cancelled（可选）
```

**列管理能力：**
- 可新增自定义列（如 "Blocked"、"Testing"）
- 可重命名、重排序（拖拽 grip handle）
- 可切换列可见性（隐藏但保留 issue）
- 只能删除空列（防止数据丢失）

**自动状态转换（workflow automation）：**
- Issue 创建 workspace → 自动移入 In Progress
- PR 打开 → 自动移入 In Review
- 所有 PR 合并 → 自动移入 Done

**拖拽支持：** 卡片可在列间拖拽移动（标准 Kanban 交互）

**多 agent 并行可见性：**
看板同时展示所有正在运行的 agent 任务，清晰区分"谁在做什么"，避免 terminal 窗口切换带来的 mental context 丢失。

**Swimlane：** 未见明确 swimlane 功能；并行任务通过独立 workspace（git worktree）隔离，不通过 swimlane 区分。

---

## 六、多视图支持 (Views)

| 视图 | 支持情况 |
|------|----------|
| Kanban Board | ✅ 主视图 |
| List View | ✅ 支持（Cloud 版明确提及） |
| Timeline / Gantt | 未见 |
| Calendar | 未见 |
| Filter / Group by | ✅ tag 过滤、status tab 切换（含 "All" tab） |

**搜索与过滤：**
- 按 tag 过滤
- 按 status 筛选（All / 各列状态）
- Cloud 版：支持 filter + sort + search 综合查询

---

## 七、AI 集成功能 (AI Features)

### 7.1 AI 自动执行（核心功能）
不同于一般 AI "建议"，Vibe Kanban 的 AI 集成是**执行层**：
- 为每个 issue 启动独立 agent（Claude Code、Gemini CLI、Codex 等）
- Agent 在隔离 git worktree 中自主执行编码任务
- 实时 WebSocket 推送 agent 的思考过程、命令、文件操作、MCP 调用日志

### 7.2 Real-time Agent 监控界面
右侧面板显示：
- Agent 执行的每条命令
- 文件修改（绿色=新增行，红色=删除行）
- MCP server 调用日志
- Token 用量颜色计量（0-30% 灰色 / 30-60% 默认 / 60-80% 橙色 / 80%+ 红色）
- 任务进度百分比

### 7.3 AI 生成 PR 描述
Agent 完成后自动生成 Pull Request description，用户一键 merge。

### 7.4 MCP 双向集成
- Vibe Kanban 既是 MCP client（连接外部 MCP 服务）
- 也是 MCP server（允许 agent 自己创建和管理 ticket）

> 重要：MCP server 功能允许 **AI agent 自主写入新 ticket**——这与我们产品中"Amazon/Reddit 信号自动生成 ticket"的核心需求高度吻合。

### 7.5 Chat Interface（Workspace 内）
独立 chat 面板：
- 支持富文本格式（Markdown、代码块、表格）
- 图片附件（拖拽或点击 paperclip）
- `@filename` typeahead 文件引用
- 消息可编辑，创建对话分支
- 状态显示：Idle / Running / Queued / Sending
- Approval workflow：某些操作要求用户明确审批后才执行

### 7.6 AI 不自动生成 ticket 内容
Vibe Kanban 的 AI 能力在于**执行 ticket**，不在于**生成 ticket 内容**。Ticket 仍需人工填写或通过 MCP server 外部写入。这是与我们产品的主要差异点。

---

## 八、差异化对比 (vs Jira / Linear / Trello / Notion)

| 维度 | Vibe Kanban | Jira | Linear | Trello | Notion |
|------|-------------|------|--------|--------|--------|
| 核心用途 | AI agent 编排 | 人类团队协作 | 工程效率管理 | 视觉任务看板 | 知识库+任务 |
| AI 集成深度 | 执行层（agent 跑任务）| 外部插件 | AI suggestions | 无 | AI 写作助手 |
| Git 原生 | ✅ 每 ticket 独立 worktree | 弱 | 强（PR 联动）| 无 | 无 |
| Code Review | ✅ 内置 diff + 评论 | 外部（GitHub）| 外部 | 无 | 无 |
| Ticket 生成 | 人工 / MCP agent 写入 | 人工 | 人工 + AI draft | 人工 | 人工 |
| 并行执行管理 | ✅ 专门设计 | 无 | 无 | 无 | 无 |
| 非编码使用 | ❌ 强耦合开发场景 | ✅ | 部分 | ✅ | ✅ |

**最独特的差异点：**
"Attempt 模型"——同一个 ticket 可以让多个 agent 用不同 prompt / model 同时尝试，结果并排比较。传统 Kanban 1 ticket = 1 解法；Vibe Kanban 1 ticket = N 个 agent attempt，人选最好的。

---

## 九、视觉设计 (Visual Design)

**整体风格：**
- 现代、简洁，以功能为主，无过度装饰
- 首页有手绘风格箭头元素（增加亲切感，降低企业感）
- 支持 Dark Mode（URL 参数 `?theme=dark` 可触发，说明主题系统已工程化）

**技术栈推断（基于代码库分析）：**
- Frontend：React + TypeScript + Vite
- CSS 框架：未直接确认是 shadcn/Tailwind，但 React + Vite + TypeScript 组合在 2025 年 AI 项目中几乎标配 Tailwind + shadcn/ui
- 组件质量：HN 用户评价"相对 bug-free，代码写得不错"

**信息密度：**
中等密度——比 Notion 密集，比 Linear 宽松。Kanban 列内卡片简洁，详细内容在卡片展开后右侧面板显示。

**颜色系统：**
- 每列有独立配色，颜色出现在列头和卡片边缘
- 用户可为列选择颜色（preset 色盘）
- Tag 也有独立颜色
- 文件修改用绿色（新增）/ 红色（删除）标注（传统 git diff 视觉语言）

**空状态设计：**
未见专门描述，但单命令启动（`npx vibe-kanban`）意味着 onboarding 极轻；空看板应有引导创建第一个 issue 的 CTA。

---

## 十、定价 (Pricing)

| 层级 | 价格 | 用户数 | 特点 |
|------|------|--------|------|
| Free | $0/月 | 1 人 | 本地自托管，核心功能 |
| Pro | $30/用户/月 | 2-49 人 | Cloud 协作，99.5% SLA，Discord 支持 |
| Enterprise | 定制 | 50+ 人 | SSO/SAML，99.9% SLA，专属 Slack 支持 |

**关键：个人开发者永久免费，Cloud 团队协作需付费。**

---

## 十一、对我们产品的具体借鉴 (Inspiration for Our Product)

我们的产品：Amazon + Reddit 信号 → AI 自动生成 ticket（含 prescriptive action）→ 团队 workflow

### 11.1 ✅ 强烈借鉴：AI 生成内容与人工审批的分离设计

Vibe Kanban 的核心 UX 哲学：**AI 执行，人审批**。表现为：
- Review 列是强制关卡，不能跳过
- Diff 内联评论在 Review 阶段进行
- Approval workflow：敏感操作需要用户明确点击确认

**对我们的启示：** Consumer insight ticket 的 prescriptive action（"建议降价 X%"/"建议修改 listing 标题"）应设计为"AI 草稿 → 团队负责人 approve → 执行"的三段式，而不是直接推送。Review 列需要是 workflow 中的必经节点。

### 11.2 ✅ 强烈借鉴：双字段卡片设计（Description + Prompt）

Vibe Kanban 将 human-readable description 和 agent-executable prompt 分为两个独立字段。

**对我们的启示：** Ticket 设计应区分：
- `insight_summary`（人读，简洁）
- `recommended_action`（prescriptive，可直接执行的操作指令）
- `supporting_evidence`（原始信号引用，供审核时查阅）

三字段分层，而不是把所有信息塞进一个 description。

### 11.3 ✅ 借鉴：Real-time 状态可见性（减少"黑盒焦虑"）

Vibe Kanban 的 WebSocket 实时日志解决了"AI 在做什么？"的焦虑感（他们称为 "doomscrolling gap"）。

**对我们的启示：** 信号采集和 ticket 生成过程应有状态指示：
- "正在分析最近 7 天 Amazon reviews..."
- "发现 3 个异常信号，生成 ticket 中..."
- "2 tickets 等待审批"

不要让用户面对空白等待屏幕。

### 11.4 ✅ 借鉴：列色彩系统用于状态语义化

每列有独立颜色，卡片边缘继承列色，一眼区分状态。

**对我们的启示：** ticket 优先级（High / Medium / Low）和 ticket 类型（价格信号 / 评论情绪 / 竞品动作）都可以用颜色语义化，避免用户在大量卡片中视觉疲劳。

### 11.5 ✅ 借鉴：MCP Server 允许 AI 自主写入 ticket

Vibe Kanban 的 MCP server 功能允许 agent 自己创建 ticket——这正是我们产品的核心机制：信号采集模块自动生成 ticket。

**对我们的启示：** Ticket 生成入口设计为 API/webhook 接收，而非只支持手动创建。UI 上明确标注 ticket 来源（"由 Amazon Signal Bot 生成"），区别于人工创建的 ticket。

### 11.6 ✅ 借鉴：大量卡片时的信息管理策略

HN 用户反馈指出，当并行 agent 超过 4 个时 mental context 开始混乱。Vibe Kanban 的应对：
- Tag 过滤收窄视图
- 列 visibility toggle 隐藏已完成的列
- "All" tab 全局视图 + 单列聚焦视图切换

**对我们的启示：** 大量 ticket 场景下（比如 50+ 条 Amazon 差评 ticket），需要：
- 按信号类型的 tab 分组（而不是只有一个超长列）
- 优先级 + 严重程度可视化（颜色标注）
- "高优先级" filter 快速定位 top N 需要立即处理的 ticket

---

## 十二、不适合借鉴的点 (Caveats)

### 12.1 ❌ 不借鉴："Attempt 模型"（多 agent 并行尝试同一 ticket）

Vibe Kanban 的 1:N attempt 设计（同一 ticket 让多个 agent 用不同 prompt 尝试，并排比较）是 coding agent 场景特有的需求——因为 LLM 生成代码有随机性，多尝试有意义。

**我们的产品不适用：** Consumer insight ticket 的 prescriptive action 是基于数据分析的确定性推荐（"这周负面评论集中在'packaging'，建议更换包材"），不需要多个 AI 版本并排比较。这个模式会增加用户决策负担而无收益。

### 12.2 ⚠️ 谨慎借鉴：双栏分屏布局

Vibe Kanban 的左看板 + 右执行日志双栏设计在管理 coding agent 时合理，因为用户需要同时看"任务列表"和"当前 agent 在做什么"。

**我们的场景**：用户看 ticket 时主要想看"insight 内容"和"建议操作"，不需要看实时日志。双栏对我们可能是过度复杂，单栏展开卡片详情可能更清晰。

### 12.3 ⚠️ 注意：强制 git worktree 隔离是编码场景专用

Vibe Kanban 每个 ticket 创建独立 git worktree 的机制在 consumer insight 产品中没有对应物。我们的"隔离"是业务逻辑层面的（每个 ticket 对应独立的信号批次），不是文件系统层面。不要混淆架构借鉴范围。

---

## 十三、证据与来源 (Evidence with URLs)

| 来源 | 内容 | URL |
|------|------|-----|
| 官网 | 定位、导航、Plan→Prompt→Review 流程 | https://www.vibekanban.com/ |
| 官方定价 | 三层定价结构 | https://vibekanban.com/pricing |
| Cloud 发布 | 团队协作功能、issue 字段、Electric SQL | https://www.vibekanban.com/blog/introducing-vibe-kanban-cloud |
| 官方文档 | 功能架构全览、agent 列表 | https://vibekanban.com/docs |
| 自定义文档 | 列管理、颜色系统、tag 系统、visibility toggle | https://vibekanban.com/docs/cloud/customisation |
| Chat 界面文档 | 双栏 UX、消息类型、token 计量、approval workflow | https://www.vibekanban.com/docs/workspaces/chat-interface |
| GitHub README | 技术栈、工作流、agent 兼容性 | https://github.com/BloopAI/vibe-kanban |
| VirtusLab 深度分析 | Attempt 模型、git worktree、UX pattern 完整分析 | https://virtuslab.com/blog/ai/vibe-kanban |
| HackerNews 讨论 | 用户真实反馈、UX 痛点、MCP server 功能 | https://news.ycombinator.com/item?id=44533004 |
| MindStudio 比较 | 与 Paperclip、Claude Code Dispatch 的 UX 对比 | https://www.mindstudio.ai/blog/vibe-kanban-vs-paperclip-vs-claude-code-dispatch-comparison |
| 诚实评测 | 限制与真实场景表现 | https://solvedbycode.ai/blog/vibe-kanban-honest-review |
| 工具评测（Berger）| 双栏布局、五列结构、实时日志 UX | https://elite-ai-assisted-coding.dev/p/vibe-kanban-tool-review |
| DeepWiki 架构分析 | 四层架构、技术栈、数据模型 | https://deepwiki.com/BloopAI/vibe-kanban |

---

*文档完。供 hackathon spec 撰写直接参考。*

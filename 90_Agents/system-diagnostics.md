# system-diagnostics Agent
_触发词: "系统诊断" / "系统增强" / "优化凌喵"_
_更新: 2026-04-15_

> **架构说明（SYN-001）：** 本 agent 强制分两次独立调用执行。Phase 1 只读诊断，Phase 2 只执行已批准写入。原因：同一 session 内既诊断又写入会导致"运动员兼裁判"偏差——凌喵曾将自身错误编码为 Vincent 偏好（improvement-queue.md 第34行）。两次调用之间必须有 Vincent 的显式审批。

---

## Phase 1 — 诊断（只读，禁止写入）

**触发方式：** 系统诊断 / 系统增强 / 优化凌喵（首次调用）

### 硬约束
- Phase 1 期间，禁止写入任何系统文件。包括但不限于：
  - `CLAUDE.md`
  - 任何 `90_Agents/*.md`
  - `80_Knowledge/` 下的任何文件（含 `habits.md`、`_staging.md`、`improvement-queue.md`）
- 如果在 Phase 1 过程中发现可立即修复的显而易见小错误（如拼写错误），记录入候选清单，不擅自写入。
- 违反此约束 = 本次诊断结果无效，需从头重来。

### 执行步骤

1. **读取全部 Knowledge 文件**（shell-runner）
   - `83_Observations/_staging.md` — 待消化暂存
   - `83_Observations/habits.md` — 现有正式观察
   - `84_Fitness/_rules.md` / `_state.md` — 健身规则与状态
   - `85_System/improvement-queue.md` — 现有待审队列
   - `CLAUDE.md` — 当前系统指令
   - `90_Agents/01_Routing.md` — 路由规则
   - 所有 `90_Agents/*.md` — 各 agent prompts

2. **暂存区分析**
   - 将 `_staging.md` 中的碎片观察归类
   - 判断是否可提炼为正式习惯记录
   - **仅记录分析结论，不写入文件**

3. **矛盾与空洞检查**
   - 路由规则是否覆盖所有常见意图？
   - Agent prompts 是否有冲突或过时描述？
   - `CLAUDE.md` 原则是否与实际使用有偏差？
   - 健身规则是否需要根据观察到的实际情况调整？

4. **生成候选清单**
   - 将所有发现写入候选文件：`85_System/harness_engineering/audit/pending_candidates.md`
   - 每条候选项注明：类别、理由、建议操作、影响文件、风险等级（低/中/高）
   - **这是 Phase 1 的唯一允许写入操作**（候选清单本身不是系统文件，是审批素材）

### Phase 1 结束语（必须逐字输出）

```
[Phase 1 完成] 诊断报告已写入 85_System/harness_engineering/audit/pending_candidates.md

发现 X 条候选改进项，分类如下：
- [routing] Y 条
- [habits/observations] Y 条
- [agent prompts] Y 条
- [fitness-rules] Y 条
- [CLAUDE.md] Y 条
- [other] Y 条  _（示例：路径纠偏 / 格式化 / 历史归档 / meta 结构调整等不属于前 5 类的项目）_

请 Vincent 审批后告知"执行系统诊断 Phase 2"启动写入。
Phase 1 已终止，本次调用不会执行任何写入操作。
```

**Phase 1 在此强制终止。同一次调用中不得继续执行 Phase 2。**

---

## Approval Gate（审批门禁）

Vincent 审阅 `pending_candidates.md`，逐条标注 ✅ 确认 / ❌ 拒绝 / ✏️ 修改后确认。

完成后，Vincent 说："执行系统诊断 Phase 2" 并可附加说明（如"跳过第3条"）。

---

## Phase 2 — 执行（仅写入已批准项）

**触发方式：** "执行系统诊断 Phase 2"（必须是独立的新调用）

### 硬约束
- Phase 2 **必须以读取 `pending_candidates.md`** 为第一步。
- 如果该文件不存在或未包含 Vincent 的审批标注（✅/❌/✏️），立即停止并提示：
  ```
  [Phase 2 中止] 未找到经 Vincent 审批的候选清单。
  请先运行 Phase 1 并在 pending_candidates.md 中完成审批标注，再调用 Phase 2。
  ```
- Phase 2 **禁止重新诊断**。不读取 `_staging.md`、`habits.md` 等知识文件用于产生新建议——只执行已批准的操作。
- 如需读取目标文件进行编辑（如读取 `CLAUDE.md` 然后写入），仅限于执行写入所必要的最小读取。

### 执行步骤

1. **读取 `pending_candidates.md`**，提取所有标注 ✅ 或 ✏️ 的条目。

2. **按条执行写入**，逐项操作：
   - `habits.md` 更新：追加或修改正式观察记录
   - `_staging.md` 清空：移除已归档的暂存碎片
   - `improvement-queue.md` 更新：将已执行项移至已完成区
   - `CLAUDE.md` 修改：仅修改已批准条目指定的具体字段
   - `90_Agents/*.md` 修改：仅修改已批准条目指定的具体字段
   - 路由规则更新：新增/修改指定路由项
   - 健身规则更新：按批准条目调整参数

3. **失败恢复**
   - 写入失败时：记录失败原因，跳过该条，继续后续条目，最终汇总失败列表
   - 冲突检测：如果要写入的内容与现有内容存在逻辑冲突，暂停该条并标注冲突详情请 Vincent 判断
   - 不因单条失败中止整个 Phase 2

4. **执行完成后**
   - 将 `pending_candidates.md` 中已执行项标注 `[DONE]`
   - 拒绝项标注 `[SKIPPED]`
   - 将本次执行记录追加入 `85_System/improvement-queue.md` 的已执行区

### Phase 2 结束格式

```
[Phase 2 完成]

已执行：X 条
已跳过（拒绝）：Y 条
失败/待决：Z 条（详见下方）

修改文件清单：
- path/to/file.md — 操作摘要
- ...

[如有失败/冲突项，列出详情供 Vincent 判断]
```

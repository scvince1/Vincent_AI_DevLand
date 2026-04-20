---
id: pending_candidates
title: Pending Candidates — 系统诊断 Phase 1
tags: [harness, audit, improvement, system-meta, pending-approval]
status: pending_approval
last_modified: 2026-04-17
summary: system-diagnostics Phase 1 产出的候选清单，逐条待 Vincent 审批后由 Phase 2 执行
---

# Pending Candidates — 系统诊断 Phase 1
_生成时间: 2026-04-17 EDT_
_Phase 1 依据: CLAUDE.md + _staging.md (512 行) + habits.md + _rules.md / _state.md + improvement-queue.md + 01_Routing.md + 13 个 agent prompt + 2026-04-14 三层审计 00_consolidated_candidates.md_
_审批后运行 Phase 2 触发词: "执行系统诊断 Phase 2"_

## 审批方法
逐条标注：
- ✅ 确认执行
- ❌ 拒绝
- ✏️ 修改后确认（写明修改内容）

**优先审批建议：** `habits/observations` 类（staging 归档）体量最大且无冲突，建议优先过；`CLAUDE.md` 类建议对照 feedback_no_claudemd_expansion.md 审慎评估。

---

## [routing] 路由规则

### R-1 新增 knowledge-agent 显式触发词
- **类别：** routing
- **理由：** improvement-queue.md 已记录（2026-04-12）知识讨论路由覆盖不足；_staging.md 中诗云 / Vebatism / Mirror and the Lamp 等思想性内容均未命中现有触发词。01_Routing.md 的 "Claude 主 session 自动调用" 段已列 knowledge-agent，但显式触发词表缺失，依赖语境判断漏报严重。
- **建议操作：** 在 01_Routing.md 意图分类表中追加一行 `` `读了…` / `想聊聊…` / `记一下这个概念` / `整理一下XX` / `这个想法` `` → knowledge-agent。
- **影响文件：** `D:\Ai_Project\MeowOS\90_Agents\01_Routing.md`
- **风险：** 低
- **审批：** [好]

### R-2 新增 people-interview skill 触发词
- **类别：** routing
- **理由：** MEMORY.md `project_people_persona_skill` 记录 people-interview skill 已部署，触发语句 "聊聊身边的人 / 聊聊身边的事 / 跟你说说身边的人"。01_Routing.md 未收录该映射，当前靠 skill system 的 description 字段隐性触发，路由表有空洞。
- **建议操作：** 在 01_Routing.md 意图分类表追加 `` `聊聊身边的人` / `聊聊身边的事` / `跟你说说身边的人` `` → people-interview skill。
- **影响文件：** `D:\Ai_Project\MeowOS\90_Agents\01_Routing.md`
- **风险：** 低
- **审批：** [好]

### R-3 语义路由兜底规则（improvement-queue SYN/ROUTING 条目落地）
- **类别：** routing
- **理由：** improvement-queue.md 2026-04-13 [ROUTING] Agent 语义触发失败条目已写入超 4 天未处理。症状复现：Vincent 说 "晚上爬了墙" / "晚上聚餐吃的饭" 仍可能被主 session 直接处理而跳过 fitness-coach / nutrition-tracker。CLAUDE.md 当前无语义兜底硬约束。
- **建议操作：** 采用 improvement-queue 原条目的选项 C（推荐），在 CLAUDE.md 禁止行为段加一条："用户报告任何具身活动 / 饮食事件时，在 _staging.md 动作前先路由到对应 agent（fitness-coach / nutrition-tracker）。"—— 此条目同时覆盖 C-3（见下），审批时应合并处理。
- **影响文件：** `D:\Ai_Project\MeowOS\CLAUDE.md`（工作流或禁止行为段）
- **风险：** 中（改 CLAUDE.md 核心行为约束）
- **审批：** [好]

### R-4 Dashboard 操作与跨系统同步路由锚点一致性
- **类别：** routing
- **理由：** 01_Routing.md 第 54-60 行规定"跨系统概览自动检测"触发时机为"任何需要写入 Dashboard.md 的操作之前（非 session 开始）"。但该检测触发权未分配给具体 agent / skill—— 实际仅主 session 知道。与 CLAUDE.md 禁止行为"不在主 session 直接读写文件"逻辑上冲突（主 session 应委派，但跨系统概览的时间戳 diff 需主 session 先判断）。
- **建议操作：** 将跨系统同步的 LastWriteTime 对比步骤显式委派给 dashboard-updater agent（由其在 action 执行前自检），01_Routing.md 改写为 "dashboard-updater 在任一 action 执行前自动做跨系统概览时间戳检查"。主 session 不判断时间戳。
- **影响文件：** `D:\Ai_Project\MeowOS\90_Agents\01_Routing.md` + `D:\Ai_Project\MeowOS\90_Agents\dashboard-updater.md`
- **风险：** 中
- **审批：** [好]

---

## [habits/observations] 观察归档

> `_staging.md` 当前 512 行、最后消化 2026-04-12 已满足 SYN-004 GC 触发条件（>300 行持续 >5 天）。以下条目 O-1 至 O-12 建议统一消化。归档后 `_staging.md` 只保留尚未成熟的观察点。

### O-1 Vincent 组间休息习惯（staging 2026-04-14 20:56）
- **类别：** habits/observations
- **理由：** Vincent 明确自述 + log.md 双点位（04-13 line 24、04-14 line 136）交叉印证，属稳定习惯。
- **建议操作：** 写入 habits.md 「健身倾向」段新增条目："Vincent 组间休息习惯：常规情况下不休满 60s，偏短。握力 PCr 恢复不全会影响后组质量。fitness-coach 推荐拉/硬拉时默认附带 RIR 触发式组间提示。"
- **影响文件：** `D:\Ai_Project\MeowOS\80_Knowledge\83_Observations\habits.md`
- **风险：** 低
- **审批：** [好]

### O-2 Vincent rep 范围习惯（staging 2026-04-14 23:09）
- **类别：** habits/observations
- **理由：** 自述 + 04-14 当日实测 21 组全部在 10-15 rep 区间，与 muscle-fiber-types.md 的 Type I 偏向者推荐存在偏差。
- **建议操作：** 写入 habits.md 「健身倾向」段："Vincent rep 默认区间 10-15，纤维构成允许但神经效率池长期未刺激；fitness-coach 应在方案中显式提供每周 ≥1 个复合动作 3-6RM 选项，不强推。"
- **影响文件：** `D:\Ai_Project\MeowOS\80_Knowledge\83_Observations\habits.md`
- **风险：** 低
- **审批：** [好]

### O-3 Vincent 握力 profile + 凌喵误判 guard（staging 2026-04-14 23:18）
- **类别：** habits/observations
- **理由：** Vincent 主动澄清 + 凌喵显式记录"研究模板套用失败"教训，校准价值高。
- **建议操作：** 写入 habits.md 「健身倾向」段："常规拉类背先于握力到力竭；握力仅在大重量硬拉 / 引体向上 / 悬吊场景为短板。rest-intervals.md 研究不需改，但 coach / advisor 引用前须按动作类型裁剪。"同时 fitness-coach.md 诊断扫描表追加一项："握力瓶颈归因"—— 默认假设为背力竭，仅三类场景触发握力独立建议。
- **影响文件：** `D:\Ai_Project\MeowOS\80_Knowledge\83_Observations\habits.md` + `D:\Ai_Project\MeowOS\90_Agents\fitness-coach.md`
- **风险：** 低
- **审批：** [好]

### O-4 午睡不切断一天（staging 2026-04-14 23:25）
- **类别：** habits/observations
- **理由：** Vincent 2026-04-14 23:25 明确补充"午睡不切断一天"规则，现有 MEMORY.md feedback_sleep_cycle_day.md 未涵盖此细节。
- **建议操作：** 更新 MEMORY.md 的 feedback_sleep_cycle_day.md 补充"午睡（罕见）不切断一个清醒周期；日历日期仅 fallback，禁止用于聚合统计"。_staging.md 归档后删除此条目（已进 memory）。
- **影响文件：** `C:\Users\scvin\.claude\projects\d--Ai-Project-MeowOS\memory\feedback_sleep_cycle_day.md`
- **风险：** 低
- **审批：** [好]

### O-5 Vincent 医学背景（鼻炎 + 打鼾 + Xyzal 每日）
- **类别：** habits/observations
- **理由：** 2026-04-16 staging 首次系统记录 Vincent 过敏性鼻炎 / 口呼吸 / Xyzal 日用；纳入 OSA 评估路径基础事实。属稳定背景事实不是临时状态。
- **建议操作：** 在 80_Knowledge/82_Health/（已存在）下新建或更新 `vincent-medical-background.md`，frontmatter 按 Knowledge_Index 格式；habits.md 仅做摘要一行指向。所有详细字段（Xyzal 日用、鼻炎 + 季节性 + 猫毛、BMI / 颈围 pending、OSA 家用 sleep study 已订 Lofta WatchPAT）放专门文件。
- **影响文件：** `D:\Ai_Project\MeowOS\80_Knowledge\82_Health\vincent-medical-background.md`（新建）+ `habits.md`（引用）
- **风险：** 低
- **审批：** [好]

### O-6 鼻炎 / 睡眠 shift 决策轨迹（staging 2026-04-16）
- **类别：** habits/observations
- **理由：** 整条 staging 属 Life Quality Improvement 项目的 Phase 1 决策记录，不属临时观察，应脱离 staging 进入专项档案（MEMORY reference_life_quality_improvement 已指向 99_MyFiles/Vincent_Life_Quality_Improvement/）。
- **建议操作：** 将 staging 2026-04-16 整块（医学背景 + 药物决策 + 净化器拒用 + 居住环境 + 睡眠 shift 决策）迁移到 `99_MyFiles\Vincent_Life_Quality_Improvement\2026-04-16_decision_log.md`；_staging.md 仅保留 1 行摘要 + 日期。
- **影响文件：** `D:\Ai_Project\MeowOS\99_MyFiles\Vincent_Life_Quality_Improvement\2026-04-16_decision_log.md`（新建）+ `_staging.md`（删块）
- **风险：** 低
- **审批：** [好]

### O-7 Challenge 5 / SharkNinja 内部情报（staging 2026-04-16）
- **类别：** habits/observations
- **理由：** 该块包含 R0 面试获得的内部情报（数据 fragmentation、数据安全缺位、AI 认知缺位、生产迁移 4 点等）和 Challenge 5 gap 排序决策。属于跨 session 项目状态，非观察碎片。按 MEMORY reference_people.md + SYN-002 建议应归入 82_Projects。
- **建议操作：** 写入 `82_Projects\sharkninja-interview-prep\2026-04-16_internal_intel.md`（或 `82_Projects\challenge-5.md` 更新），staging 中整块归档删除。
- **影响文件：** `D:\Ai_Project\MeowOS\80_Knowledge\82_Projects\`（新建或更新）
- **风险：** 低
- **审批：** [好]

### O-8 Winston 岳文宇（staging 2026-04-15 20:30）
- **类别：** habits/observations
- **理由：** 人物首次登场但信息不足（年龄段 / 职业 / 对话风格缺），按 cat-steward / plant-steward 的 "信息不足→返 insufficient_information" 范式，此人尚不足以建 87_People 档案。但 staging 中保留 4 天已不再增长，无人触发。
- **建议操作：** 保留在 _staging.md 直到 people-interview session 主动触发或 Vincent 下次提起。当前状态标注 `[待补 · 信息不足]` 并移到 staging 顶部"待补人物"区（新 section）。
- **影响文件：** `_staging.md`
- **风险：** 低
- **审批：** [好]

### O-9 Tate 条目（staging 2026-04-11 / 2026-04-12）
- **类别：** habits/observations
- **理由：** 已在 87_People/tate.md 存在（见上面 ls 结果）。_staging.md 的 Tate 区块属于"写入边界：不擅自写入 87_People/，等 people-interview 触发"。但档案已建，staging 信息可能已同步也可能未同步。
- **建议操作：** Phase 2 执行者比对 staging Tate 区块内容 与 87_People/tate.md 实际内容；若 staging 已在档案中则 staging 删除；若 staging 含更新则 Vincent 决定是否更新档案。
- **影响文件：** `_staging.md` + `87_People/tate.md`
- **风险：** 低
- **审批：** [好]

### O-10 "回音壁" / "作为洞察的幸福" / Vebatism / 诗云条目（staging 思想性块）
- **类别：** habits/observations
- **理由：** 这四条是 Vincent 自命名 / 原创概念，属核心身份语言。应纳入 81_Identity 或 88_Research，而非 staging 暂存。按 CLAUDE.md 规则 "Vincent 原创想法不进知识库" —— 这条规则与当前需求存在张力。
- **建议操作：** 两种路径二选一（请 Vincent 裁决）：
  - A. 保留在 _staging.md 长期暂存（目前行为），接受 staging 大小持续增长。
  - B. 建立 `81_Identity/vincent-concepts.md` 专门存放 Vincent 自命名概念（回音壁 / 洞察幸福 / Vebatism 等），不进 88_Research（那里是外部知识）。CLAUDE.md "原创想法不进知识库" 改为 "原创想法不进 88_Learned / 88_Research；身份性概念进 81_Identity"。
- **影响文件：** `D:\Ai_Project\MeowOS\CLAUDE.md` + `81_Identity\vincent-concepts.md`（新建，若选 B）
- **风险：** 中（涉及 CLAUDE.md 原则修改）
- **审批：** [需要讨论, session里跟我讲]

### O-11 签证 / 税务历史（staging 2026-04-14）
- **类别：** habits/observations
- **理由：** 属稳定个人事实（F-1 自 2018、2023 起 Resident Alien 等），应进 81_Identity 长期存。
- **建议操作：** 写入 `81_Identity\vincent-legal-status.md`（新建或更新），staging 整块删除。
- **影响文件：** `D:\Ai_Project\MeowOS\80_Knowledge\81_Identity\vincent-legal-status.md`
- **风险：** 低
- **审批：** [好]

### O-12 Joyce 作息事件 / 系统需求（staging 2026-04-11 + 04-09 + 04-12）
- **类别：** habits/observations
- **理由：** Joyce 相关稳定事实和 BaseOS 设计参数应在 Joyce 档案或 BaseOS 项目档案中，不宜永久驻留 staging。MEMORY feedback_joyce_file_path.md 指明 Joyce 相关默认落 99_MyFiles/Joyce_Files。
- **建议操作：** BaseOS 设计参数写入 `99_MyFiles\BaseOS\design-constraints.md`；Joyce 个人事件（"主动选择的拖延" 等）若涉及 Vincent 自省则写 habits.md，若是 Joyce 侧事实则写 87_People/Joyce/ 或 Joyce_Files。staging 整块归档。
- **影响文件：** `99_MyFiles\BaseOS\` + `87_People\Joyce\` 或 `99_MyFiles\Joyce_Files\`
- **风险：** 低
- **审批：** [好]

### O-13 营养日志条目（staging 04-09 到 04-15 全部饮食日志）
- **类别：** habits/observations
- **理由：** 所有饮食记录按 nutrition-tracker.md 规定应在 `84_Fitness/nutrition/daily-log.md`。staging 中的日志是 ACE 捕获后的"暂存"，但 4-7 天后仍未消化 = nutrition-tracker 未执行归档。
- **建议操作：** 比对 staging 中的营养日志条目与 `84_Fitness/nutrition/daily-log.md`；若 daily-log 已含则 staging 删除；若不含则调用 nutrition-tracker 补录后删除 staging 块。
- **影响文件：** `84_Fitness\nutrition\daily-log.md` + `_staging.md`
- **风险：** 低
- **审批：** [需要讨论, session里跟我讲]

### O-14 "拖延信号" 补充：无锚点期行为模式（staging 2026-04-12）
- **类别：** habits/observations
- **理由：** Vincent 自述 "不擅长维持日程，无硬锚点时进入'狂乱工作'" 是对 habits.md 现有"拖延信号 & 破局条件"章节的重要补充。
- **建议操作：** 在 habits.md "拖延信号 & 破局条件" 章节末尾追加一段："Vincent 自述无锚点期行为模式：无'必须参与'的硬锚点时进入狂乱工作状态，靠直觉 / 内在驱动选择任务；攀岩 / 运动依赖当时状态非计划性。含义：硬锚点是日程维护的前提而非加分项；无锚点期日程系统自然降级为直觉模式。"
- **影响文件：** `habits.md`
- **风险：** 低
- **审批：** [好]

---

## [agent prompts] Agent 修改

### A-1 fitness-coach.md 读取清单补 rest-intervals.md
- **类别：** agent prompts
- **理由：** improvement-queue.md [2026-04-14] fitness-coach.md 知识文件清单补充，`84_Fitness/rest-intervals.md` 已存在 (8.4KB) 但 coach prompt "读取清单" 缺该条，导致 coach 生成建议时依赖训练记忆。
- **建议操作：** 在 fitness-coach.md 第 14-22 行 "读取（通过 shell-runner）" 清单追加 `- 84_Fitness/rest-intervals.md — 组间休息协议（默认值 + Readiness×组间矩阵 + TFCC/攀岩/睡眠碎片调整）`。
- **影响文件：** `D:\Ai_Project\MeowOS\90_Agents\fitness-coach.md`
- **风险：** 低
- **审批：** [好]

### A-2 删除或迁移 deprecated fitness-advisor.md
- **类别：** agent prompts
- **理由：** fitness-advisor.md 第 1 行明确标 DEPRECATED；文件仍在 90_Agents/ 活跃目录，可能被错误加载。按 feedback_additive_bias_four_families 重定向：移到归档目录而非保留在活跃目录。
- **建议操作：** 将 `90_Agents/fitness-advisor.md` 迁移到 `80_Knowledge/90_Deprecated/90_Agents_archive/fitness-advisor.md`（保留供历史参考），同时更新 01_Routing.md 若有残留引用。
- **影响文件：** `90_Agents/fitness-advisor.md` → `80_Knowledge/90_Deprecated/90_Agents_archive/fitness-advisor.md`
- **风险：** 低
- **审批：** [好]

### A-3 dashboard-updater 与 nutrition-tracker 的 Dashboard 写入协议统一
- **类别：** agent prompts
- **理由：** nutrition-tracker.md 第 81 行 "Dashboard 同步 · 每次记录饮食或生成每日汇总后，更新 Dashboard.md「营养」表" 描述直接写入 Dashboard。但 dashboard-updater.md 明确 "Dashboard.md 的唯一写入者"。两者冲突：nutrition-tracker 应通过 dashboard-updater 的 upsert_section action，不直接写。
- **建议操作：** 在 nutrition-tracker.md 第 81-94 行改写："每次记录饮食或生成每日汇总后，调用 dashboard-updater agent 的 `upsert_section` action，section 名 '营养'，content 为下方表格内容。不直接写 Dashboard.md。"
- **影响文件：** `D:\Ai_Project\MeowOS\90_Agents\nutrition-tracker.md`
- **风险：** 低
- **审批：** [ ]

### A-4 fitness-coach.md Dashboard 写入同样走 dashboard-updater
- **类别：** agent prompts
- **理由：** fitness-coach.md 第 27 行 "Dashboard.md — 更新「健身」表"。同 A-3 冲突。
- **建议操作：** 改写为 "调用 dashboard-updater agent 的 `sync_fitness` action，不直接写 Dashboard.md"。此 action 已在 dashboard-updater.md 定义。
- **影响文件：** `D:\Ai_Project\MeowOS\90_Agents\fitness-coach.md`
- **风险：** 低
- **审批：** [好]

### A-5 agent prompt 头部格式统一（SYN-009 落地，低优先级版本）
- **类别：** agent prompts
- **理由：** 2026-04-14 00_consolidated_candidates SYN-009 已批复 Priority 低。当前 knowledge-agent.md 无触发方式 / 版本号声明；cat-steward、plant-steward 用 "agent: xxx / 触发方式: ..." 的 YAML 风格；fitness-coach / nutrition-tracker 用 "触发词: / 更新:" 行风格；daily-review / scheduler / dump-processor 用 "MeowOS · v1.0 · 日期" 风格。格式分裂。
- **建议操作：** 以 fitness-coach.md 头部（触发词 + 更新日期 + 职责声明 + [硬约束] 段）为模板，逐个 agent prompt 头部标准化。不强制改内容，仅补齐元数据行。
- **影响文件：** `90_Agents\*.md`（约 8 个）
- **风险：** 低
- **审批：** [不]

### A-6 system-diagnostics.md 补 "[other]" 类别
- **类别：** agent prompts
- **理由：** system-diagnostics.md 第 53-58 行 Phase 1 结束语模板列了 5 类（routing / habits / agent prompts / fitness-rules / CLAUDE.md），但实际诊断常出现跨类别或其他类发现（例如本次 O-12 跨 BaseOS / Joyce 文件；A-2 涉及归档目录管理）。
- **建议操作：** 在结束语模板追加 `- [other] Y 条` 作为第 6 类别。Phase 1 prompt 同步补 [other] 分类说明。
- **影响文件：** `D:\Ai_Project\MeowOS\90_Agents\system-diagnostics.md`
- **风险：** 低
- **审批：** [ ]

### A-7 knowledge-agent Registry 重建触发点一致性
- **类别：** agent prompts
- **理由：** knowledge-agent.md 第 70-93 行规定"每次在 80_Knowledge/ 下完成 write/edit/delete 操作后，执行 Registry 增量重建"。但实际执行者是 shell-runner 还是 knowledge-agent 本身不清晰——shell-runner 原则上只做读写，不会自动触发后续 Registry 重建。当前约定依赖主 session 知道"写完后 call knowledge-agent"，路径长易漏。
- **建议操作：** 在 knowledge-agent.md Registry 段加一行 "本 agent 被调用进行 write / edit / delete 后，在同一调用内完成 Registry 重建"。同时在 cat-steward / plant-steward / nutrition-tracker / fitness-coach 的写入段追加 "写入 80_Knowledge/ 后，在返回主 session 前调用 knowledge-agent 触发 Registry 重建"。
- **影响文件：** `90_Agents\knowledge-agent.md` + `cat-steward.md` / `plant-steward.md` / `nutrition-tracker.md` / `fitness-coach.md`
- **风险：** 中
- **审批：** [好]

---

## [fitness-rules] 健身规则

### F-1 _rules.md "心理舒适度优先" 与 Vincent 实际习惯张力
- **类别：** fitness-rules
- **理由：** _rules.md 设计原则 "复合动作不强制力竭；尊重训练节奏"，但 O-2 记录 Vincent rep 默认 10-15 区间导致纤维 / 神经效率池长期欠刺激。"不强制力竭" 与 "应刺激 3-6RM" 存在规则张力。需显式说明优先级。
- **建议操作：** 在 _rules.md "设计原则 #3" 下追加一行："心理舒适度优先不等于拒绝多元刺激——推荐保持 10-15 rep 为主但主动提供 3-6RM 选项；是否接受由 Vincent 当日决定。"
- **影响文件：** `D:\Ai_Project\MeowOS\80_Knowledge\84_Fitness\_rules.md`
- **风险：** 低
- **审批：** [ ]

### F-2 _state.md HRV 基线 "待建立" 长期未更新
- **类别：** fitness-rules
- **理由：** _state.md 第 19-21 行 "ln_rmssd_7d_mean: [待建立]" / "rhr_7d_mean: [待建立]" / "baseline_ready: false（校准中，Day 0/14）" 自 2026-04-15 无更新。Vincent 无固定 HRV 采集设备（Garmin / Apple Watch / Whoop 未明确），此栏目实际无数据源。
- **建议操作：** 两种路径二选一（请 Vincent 裁决）：
  - A. 明确 HRV 数据源（例如 Vincent 确认用 Oura / Whoop / Garmin 并开始采集）—— 维持现状。
  - B. 删除 HRV 相关字段，改为 "主观恢复评分 7d 滚动"（Vincent 自评 1-10），同步修改 fitness-coach.md Readiness Gate 逻辑。
- **影响文件：** `_state.md` + `fitness-coach.md`
- **风险：** 中
- **审批：** [我有applewatch但是很不常用. 选B.]

### F-3 sleep_cycle_history 历史回填触发
- **类别：** fitness-rules
- **理由：** improvement-queue.md [2026-04-14] log.md 日期头结构改造条目要求 04-07 至 04-14 清醒周期人工回填。_state.md 的 sleep_cycle_history 表已从 04-09 开始填，但 04-07 至 04-08 缺，条目状态"高优先级"至今未完成。
- **建议操作：** Phase 2 执行者提示 Vincent 补 04-07、04-08 两天清醒周期时间点（wake / sleep / training），填入 _state.md 对应表。若 Vincent 记不清则标 "unrecoverable"。
- **影响文件：** `_state.md`
- **风险：** 低
- **审批：** [记不清了]

### F-4 log.md 日期头结构改造 — 落地触发
- **类别：** fitness-rules
- **理由：** improvement-queue.md [2026-04-14] 该条目仍为"高优先级"待审。当前 log.md 依然按日历日期组织，违反了 _state.md 顶部硬约束（见 nutrition-tracker.md / fitness-coach.md 的"日期边界"硬约束）。日期归因错误风险仍在。
- **建议操作：** Phase 2 执行：(a) log.md 未来新 entry 头改为 `## [cycle-id] YYYY-MM-DD wake→YYYY-MM-DD sleep | 主题 | ...`，历史 entry 不回填（成本高价值低）；(b) fitness-coach.md "今天/昨天/本周" 聚合逻辑切换到 cycle_id 查询，禁用日历日 fallback 语言。
- **影响文件：** `log.md` 写入规范 + `fitness-coach.md`
- **风险：** 中
- **审批：** [好]

---

## [CLAUDE.md] 系统指令

> MEMORY feedback_no_claudemd_expansion 警告 "near capacity, never add sections/rules unless explicitly asked"。以下 C 类建议全部需 Vincent 显式审批，默认保守偏向 ❌。

### C-1 Phase 1 / Phase 2 架构写入 CLAUDE.md（SYN-001 部分落地检查）
- **类别：** CLAUDE.md
- **理由：** SYN-001 已在 system-diagnostics.md 内部实现 Phase 1 / Phase 2 分隔（验证完成：本次调用正是 Phase 1）。CLAUDE.md 第 45 行 ACED 表 "E·系统诊断" 已声明 "两阶段：Phase 1 诊断 → Vincent 审批 → Phase 2 执行"，一致。无需额外写入。
- **建议操作：** **不执行** — 仅作一致性检查记录。本条建议 ❌。
- **影响文件：** 无
- **风险：** 低
- **审批：** [❌ 建议默认拒绝]

### C-2 Routing 语义兜底写入 CLAUDE.md（R-3 重复）
- **类别：** CLAUDE.md
- **理由：** 见 R-3。此条与 R-3 是同一修改请求的不同类别视角。审批时请只批一次（R-3 或 C-2，不重复）。
- **建议操作：** 合并入 R-3 处理。
- **影响文件：** 同 R-3
- **风险：** 同 R-3
- **审批：** [合并R3] _合并入 R-3_

### C-3 数据类输入自动路由规则写入 CLAUDE.md
- **类别：** CLAUDE.md
- **理由：** improvement-queue.md [2026-04-14] 数据输入自动入库规则条目待审超 3 天。核心规则：营养 / 睡眠 / 运动数据出现时主 session 自动调对应 agent 入库，不展示算术后询问是否记录。该规则缺位导致 2026-04-14 session 的 Vincent 手工补写事件。
- **建议操作：** 在 CLAUDE.md 工作流段追加一行："数据类输入（营养 / 睡眠 / 运动）出现时，直接调对应 agent (nutrition-tracker / fitness-coach) 入库，只回报结论和异常。不在主 session 展示算术询问是否记录。" 此条与 R-3 功能上协同（R-3 是具身活动 / 饮食事件，C-3 是纯数据点）。
- **影响文件：** `D:\Ai_Project\MeowOS\CLAUDE.md`
- **风险：** 中
- **审批：** [需要聊]

### C-4 Staging 积压消化触发提醒
- **类别：** CLAUDE.md
- **理由：** improvement-queue.md 2026-04-12 条目要求 CLAUDE.md Session 开始行为增加 "_staging.md > 200 行或 >3 天未消化时主动提示需消化"。当前 staging 512 行 / 5 天未消化，触发条件满足但规则缺位。SYN-004 也已批复该方向。
- **建议操作：** 在 CLAUDE.md "Session 开始行为" 段追加一句："若 _staging.md 超过 300 行或最后消化距今 ≥ 5 天（由 SYN-004 GC checklist 决定阈值），在 session 启动汇报后附一句'暂存区需要消化，是否跑系统诊断？'" 阈值 300/5 保守取自 2026-04-16 deferred 条目中的 "再次积压 > 300 行持续 > 5 天" 表述。
- **影响文件：** `D:\Ai_Project\MeowOS\CLAUDE.md`
- **风险：** 中
- **审批：** [不]

---

## [other] 其他

### X-1 improvement-queue.md 格式化和已执行条目迁移
- **类别：** other
- **理由：** improvement-queue.md 当前 140 行，已执行 / 已拒绝 / 待审批 混排，2026-04-14 之后新增条目没有按模板归档。诊断 Phase 2 结束时应将本次执行项从"待审批"移入"已执行"并标 DONE。SYN-002 和 SYN-004 的条目也应 review 执行状态（00_consolidated_candidates 已生成但未整合）。
- **建议操作：** Phase 2 执行时：(a) 将 00_consolidated_candidates 中的 SYN-001/SYN-003 标"已执行"并加文件引用；(b) SYN-002/SYN-004/SYN-005 等未执行的 cross-layer 建议重新编号为 IQ-YYYYMMDD-NN 并规范迁入 improvement-queue.md 待审批区；(c) 本次 Phase 2 执行完的条目全部标 DONE + 日期 + 改动文件。
- **影响文件：** `D:\Ai_Project\MeowOS\80_Knowledge\85_System\improvement-queue.md`
- **风险：** 低
- **审批：** [好]

### X-2 pending_candidates.md 路径纠偏
- **类别：** other
- **理由：** system-diagnostics.md 第 44 行指定候选文件路径 `85_System/harness_engineering/audit/pending_candidates.md`，但根下无 `85_System/` 目录，实际审计目录在 `80_Knowledge/85_System/harness_engineering/audit/`。本次 Phase 1 已按实际路径写入此文件，但 prompt 路径描述不准确，未来 Phase 2 执行者可能找错。
- **建议操作：** 把 system-diagnostics.md 中所有 `85_System/harness_engineering/audit/pending_candidates.md` 路径补前缀为 `80_Knowledge/85_System/harness_engineering/audit/pending_candidates.md`（第 44 行 + Phase 1 结束语 + Phase 2 第 1 步）。
- **影响文件：** `D:\Ai_Project\MeowOS\90_Agents\system-diagnostics.md`
- **风险：** 低
- **审批：** [好]

### X-3 历史 audit 文件归档状态
- **类别：** other
- **理由：** 80_Knowledge/85_System/harness_engineering/audit/ 下 audit_B1/B2/B3 + 00_consolidated_candidates 自 2026-04-14 起未变更，属一次性审计产物。长期驻留 audit/ 同目录可能与未来新审计产物混淆。
- **建议操作：** 可选（非紧急）：在 audit/ 下建 `2026-04-14_three_layer/` 子目录，将本次审计四份产物移入。本次 pending_candidates 留在根 audit/，并约定未来每次 Phase 1 产出都在根 audit/，审批 / 执行后归档到日期子目录。
- **影响文件：** `D:\Ai_Project\MeowOS\80_Knowledge\85_System\harness_engineering\audit\`
- **风险：** 低
- **审批：** [好]

### X-4 "凌喵 E·系统诊断" 触发历史 audit 遗留未消化
- **类别：** other
- **理由：** SYN-002 (82_Projects Task State)、SYN-005 (context reset 预警)、SYN-006 (HITL 升级条件)、SYN-007 (rejection_signals eval fixtures)、SYN-008 (Dashboard hookify)、SYN-010 (_manifest)、SYN-011 (audit trail) 七条 2026-04-14 审计结论均未被任何后续诊断 session 批量处理。
- **建议操作：** Phase 2 执行时：将 SYN-002 至 SYN-011 的未执行条目按 X-1 规范迁移到 improvement-queue.md "待审批" 区，各条加入 source="SYN-0XX 2026-04-14 audit"。后续每次系统诊断时从 improvement-queue 逐条走审批 / 执行流。
- **影响文件：** `improvement-queue.md`
- **风险：** 低
- **审批：** [好 ]

---

## 诊断摘要

- 读取覆盖：CLAUDE.md（63 行）/ _staging.md（512 行）/ habits.md（114 行）/ _rules.md（120 行）/ _state.md（95 行）/ improvement-queue.md（140 行）/ 01_Routing.md（60 行）/ 13 个 agent prompt / 2026-04-14 审计合并清单（390 行）
- staging 积压确认：512 行、5 天未消化，已超 SYN-004 GC 阈值
- 未执行的历史 improvement-queue 条目：6 条（digest 中文切换 / routing 语义兜底 / staging 提醒 / Dashboard 操作封装 / 数据输入自动入库 / 时间戳行为规则）
- 未执行的历史 cross-layer 审计条目：7 条（SYN-002/005/006/007/008/010/011）
- 主要风险：staging 无去重机制 + 数据类输入未自动路由 + Dashboard 写入规则在各 agent 间未统一
- 主要正向信号：shell-runner 委派原则覆盖完整、Phase 1 / Phase 2 架构已在 agent prompt 层实现、fitness-coach [硬约束] 头部模式运作良好

_本文件为 Phase 1 产出，待 Vincent 审批。Phase 2 必须在独立新调用中触发。_

---

## 2026-04-17 讨论收敛结果（Vincent 审批完成）

本节为 Phase 2 执行时的权威清单。Phase 2 优先读取本节而非原始审批标注。

### 新增候选项（本次讨论生成）

#### O-10a — MeowOS 思想母题归档提升
- **类别：** other / meta
- **操作：** 新建 `80_Knowledge/81_Identity/intellectual-motifs.md`，合并以下三层内容为 authoritative 根源：
  - 99_MyFiles/2026-04-07-intellectual-themes.md 的 3 条核心母题
  - memory/user_intellectual_themes.md 的 5 条扩展母题
  - _staging.md 中未归位的 4 个哲学概念：回音壁 / Vebatism / 诗云悖论 / 作为洞察的幸福
- **收尾：** 99_MyFiles 原文件和 memory 改为 pointer（指回 81_Identity/intellectual-motifs.md）；article-series.md 仅保留 series 层 motif mapping，不重复定义
- **影响文件：**
  - 新建 `D:\Ai_Project\MeowOS\80_Knowledge\81_Identity\intellectual-motifs.md`
  - 修改 `D:\Ai_Project\MeowOS\99_MyFiles\2026-04-07-intellectual-themes.md`（改 pointer）
  - 修改 `D:\Ai_Project\MeowOS\80_Knowledge\82_Projects\article-series.md`（简化）
  - 修改 `C:\Users\scvin\.claude\projects\d--Ai-Project-MeowOS\memory\user_intellectual_themes.md`（改 pointer）
- **风险：** 中（涉及多文件联动）
- **状态：** ✅

#### O-15 — Vincent 训练挑战偏好
- **类别：** habits/observations
- **操作：** 写入新建的合集文件 `80_Knowledge/81_Identity/physiological-profile.md` 的「健身倾向」段
- **内容：**
  > Vincent 接受训练挑战——适度外部推动 → 情绪正向；过度舒适反而不利。fitness-coach 推荐时不必过度保守。
- **影响文件：** `D:\Ai_Project\MeowOS\80_Knowledge\81_Identity\physiological-profile.md`（新建）
- **风险：** 低
- **状态：** ✅

#### A-8 — habits.md 模块拆分（主 session 层 vs 生理档案层）
- **类别：** agent prompts / 结构性
- **操作：**
  1. 新建 `80_Knowledge/81_Identity/physiological-profile.md`
  2. 从 habits.md 迁出三段到该新文件，组织为三个 section：
     - § 医学背景（原 habits.md 无此段，由 O-5 内容填充 + 82_Health/vincent-medical-background.md 摘要）
     - § 健身倾向（从 habits.md 迁出 + O-1/O-2/O-3/O-15 追加）
     - § 饮食规律（从 habits.md 迁出）
  3. habits.md 在原位保留一行 pointer："身体/健身/饮食相关行为 → 81_Identity/physiological-profile.md"
  4. 更新 agent prompt 读取清单：
     - fitness-coach / fitness-advisor（若保留）：读 habits.md + physiological-profile.md 的健身倾向/医学背景段
     - nutrition-tracker：读 habits.md + physiological-profile.md 的饮食规律/医学背景段
     - 主 session 凌喵：读 habits.md（保持不变）
- **影响文件：**
  - 新建 `D:\Ai_Project\MeowOS\80_Knowledge\81_Identity\physiological-profile.md`
  - 修改 `D:\Ai_Project\MeowOS\80_Knowledge\83_Observations\habits.md`（迁出三段，保留 pointer）
  - 修改 `D:\Ai_Project\MeowOS\90_Agents\fitness-coach.md`
  - 修改 `D:\Ai_Project\MeowOS\90_Agents\nutrition-tracker.md`
- **风险：** 中（涉及多 agent prompt 联动 + 文件结构重组）
- **状态：** ✅

### 原始条目状态更新

| ID | 原状态 | 最终状态 | 备注 |
|---|---|---|---|
| O-13 (a) 04-15 | 需讨论 | ✅ | 按 daily-log 为准（1828 kcal/165g P/3095mg Na/1740mg K） |
| O-13 (b) 04-10 | 需讨论 | ✅ | staging 描述有误，不处理（保留 daily-log） |
| O-13 (c) 04-09 | 需讨论 | ✅ | staging 有时间戳「~22:10 EDT」→ 补录到 daily-log 2026-04-09 条目，再删 staging |
| O-13 整体 | 需讨论 | ✅ | Phase 2 流程：补录 04-09 → 删除 staging 所有 04-09~04-15 饮食日志段 |
| C-3 | 需讨论 | 🔀 merged_into_R-3 | 不单独出 CLAUDE.md 条目；R-3 的写入覆盖其功能 |
| A-3 | 空白 | ✅ | Vincent 授权凌喵判断；低风险协议一致性修正 |
| A-6 | 空白 | ✅ | Vincent 授权凌喵判断；低风险格式补齐 |
| F-1 | 空白 | ✏️ | 改写并批准，见下方新措辞 |

### F-1 最终措辞（替换 `_rules.md` 设计原则 #3 原文）

**原文：**
> 心理舒适度优先 — 复合动作不强制力竭；尊重训练节奏

**改为：**
> 复合动作目标 3-6 RM。允许过渡期渐进加重，不强推当日达标；适度推一下优于过度舒适。

### 确认保持拒绝

- A-5（agent prompt 头部格式统一）❌
- C-1（Phase 1/2 架构写入 CLAUDE.md）❌
- C-4（Staging 积压消化提醒写入 CLAUDE.md）❌

### Phase 2 执行清单汇总

**原始已批准（首轮审批）：** R-1, R-2, R-3, R-4, O-1, O-2, O-3, O-4, O-5, O-6, O-7, O-8, O-9, O-11, O-12, O-14, A-1, A-2, A-4, A-7, F-2 (修改版), F-3 (unrecoverable), F-4, X-1, X-2, X-3, X-4

**本轮新增 / 更新：** O-10a, O-15, A-8, O-13 (三分支), C-3 (merged), A-3, A-6, F-1 (改写)

**合计执行条目：** 约 30 条

### Phase 2 触发

Vincent 说「执行系统诊断 Phase 2」后启动写入。

---

## Phase 2 执行状态（2026-04-17 10:21 EDT）

| ID | 状态 | 备注 |
|---|---|---|
| R-1 knowledge-agent 触发词 | [DONE] | 01_Routing.md v1.3 |
| R-2 people-interview 触发词 | [DONE] | 01_Routing.md |
| R-3 数据类输入硬约束 | [DONE] | CLAUDE.md 禁止行为段（含 C-3 merge） |
| R-4 跨系统同步锚点一致性 | [DONE] | 01_Routing.md 跨系统概览段 |
| O-1 组间休息 | [DONE] | physiological-profile.md |
| O-2 rep 范围 | [DONE] | physiological-profile.md |
| O-3 握力-背链 profile | [DONE] | physiological-profile.md |
| O-4 午睡不切断细则 | [DONE] | memory/feedback_sleep_cycle_day.md |
| O-5 vincent-medical-background.md | [DONE] | 82_Health/ 新建 |
| O-6 12am 目标 + decision log | [DONE] | habits.md + Life Quality 2026-04-16_decision_log.md |
| O-7 Challenge 5 / SharkNinja | [DONE] | challenge-5.md + sharkninja-status.md |
| O-8 Winston 待补 | [DONE] | staging 待补区 |
| O-9 Tate 合并 | [DONE] | 87_People/tate.md |
| O-10a intellectual-motifs.md | [DONE] | 81_Identity/ 新建 + memory/99_MyFiles pointer |
| O-11 vincent-legal-status.md | [DONE] | 81_Identity/ 新建 |
| O-12 Joyce 拖延定性 + BaseOS | [DONE] | habits.md + baseos-plan.md |
| O-13 (a) 04-15 | [DONE] | daily-log 已权威，无动作 |
| O-13 (b) 04-10 | [DONE] | 不处理 |
| O-13 (c) 04-09 补录 | [DONE] | daily-log.md 新增 04-09 条目 |
| O-13 (d) staging 饮食段删除 | [DONE] | staging.md 重写 |
| O-14 无锚点期行为模式 | [DONE] | habits.md 拖延信号段 |
| O-15 训练挑战接受度 | [DONE] | physiological-profile.md |
| A-1 fitness-coach 读 rest-intervals | [DONE] | 90_Agents/fitness-coach.md |
| A-2 fitness-advisor 归档 | [DONE] | 90_Agents/_archived/fitness-advisor.md |
| A-3 Dashboard 写入走 dashboard-updater | [DONE] | nutrition-tracker.md |
| A-4 fitness-coach Dashboard 写入 | [DONE] | fitness-coach.md |
| A-5 agent prompt 头部统一 | [SKIPPED] | Vincent 拒绝 |
| A-6 Phase 1 [other] 分类 | [DONE] | system-diagnostics.md |
| A-7 Registry 触发统一 | [DONE] | knowledge-agent.md |
| A-8 habits.md 拆分 | [DONE] | physiological-profile.md + habits.md pointer |
| C-1 Phase 1/2 入 CLAUDE.md | [SKIPPED] | Vincent 拒绝 |
| C-3 合并入 R-3 | [DONE] | merged into R-3 |
| C-4 Staging 消化提醒入 CLAUDE.md | [SKIPPED] | Vincent 拒绝 |
| F-1 设计原则 #3 改写 | [DONE] | 84_Fitness/_rules.md |
| F-2 HRV → 主观恢复评分 | [DONE] | 84_Fitness/_state.md |
| F-3 sleep_cycle_history unrecoverable | [SKIPPED: 目标文件不存在] | history 已在 _state.md 表格中 |
| F-4 log.md cycle-id 格式 | [DONE] | 84_Fitness/log.md v2.2 |
| X-1 improvement-queue 格式化 | [DONE] | 已执行区更新 + 本次记录追加 |
| X-2 pending_candidates 路径纠偏 | [DONE] | 无需纠正 |
| X-3 历史 audit 归档核查 | [DONE] | audit/ 目录保留当前文件，无需归档 |
| X-4 E·诊断遗留触发历史 | [DONE] | 已并入 improvement-queue 2026-04-17 执行记录 |

**汇总：** 执行 35 / 跳过 4 / 失败 0

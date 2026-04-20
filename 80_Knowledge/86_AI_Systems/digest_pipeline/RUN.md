---
id: RUN
title: Digest Pipeline 运行手册
tags: [ai-systems, meta, digest-pipeline, runbook]
status: confirmed
last_modified: 2026-04-15
summary: 凌喵运行 digest pipeline 的操作手册，含核心原则和执行步骤
---
# Digest Pipeline 运行手册

**读者**: 凌喵自己。当 Vincent 说"跑 digest pipeline"或系统诊断触发时，读这份文档。

## 核心原则

1. **主 session 不读 session 原文、不读 digest 原文**。一切文件读写派给 subagent。你只调度和汇报。
2. **Pass 1 串行**。Opus 容易撞 rate limit。Pass 2 和 Pass 3 各只有一次调用。
3. **失败了就停**。Manifest 记录进度，下次重跑会 resume。
4. **不自动写入 Warm/Hot memory**。pipeline 只产出 Cold insight。升温的决定权在 Vincent。

## 路径常量

```
PROJECT        = MeowOS (v1 only)
JSONL_DIR      = C:\Users\scvin\.claude\projects\d--Ai-Project-MeowOS\
NORMALIZED_DIR = D:\Ai_Project\MeowOS\99_MyFiles\Normalized_Session_History\
PIPELINE_DIR   = D:\Ai_Project\MeowOS\80_Knowledge\86_AI_Systems\digest_pipeline\
DIGEST_ROOT    = D:\Ai_Project\MeowOS\80_Knowledge\86_AI_Systems\Session_Digests\MeowOS\
MANIFEST       = <DIGEST_ROOT>\manifest.md
PASS1_DIR      = <DIGEST_ROOT>\pass1\
PASS2A_DIR     = <DIGEST_ROOT>\pass2a\
PASS2B_DIR     = <DIGEST_ROOT>\pass2b\
```

## Step 1 — 扫描与截断（Python, 零 token）

派一个 shell-runner subagent 运行：

```
python D:\Ai_Project\MeowOS\80_Knowledge\86_AI_Systems\digest_pipeline\manifest_scan.py --project MeowOS
```

它会：读 watermark → 扫新 jsonl → normalize → 写 txt → 按 1500 字符阈值分类 → 追加 manifest 行 → stdout 打印 pending UUID 列表。

subagent 返回：pending UUID 清单 + fragment 数 + skipped 数。

如果 pending 数 = 0，告诉 Vincent "没有新的 session 需要处理，喵"，结束。

## Step 2 — Pass 1 串行（Opus subagent × N）

对每个 pending UUID，依次派一个 Opus subagent，prompt 基于 `prompts/pass1.md`，替换占位符：
- `{session_uuid}` → 当前 UUID
- `{txt_path}` → `<NORMALIZED_DIR>\<uuid>.txt`
- `{output_path}` → `<PASS1_DIR>\<uuid>.md`

**每次只派一个 agent，等完成再派下一个**。完成后在 manifest 对应行把 Pass 1 列标记为 `done`。

失败/rate limit：停止后续，在 manifest 标 `error`，告诉 Vincent "Pass 1 跑到 X / N 时遇到问题，可以稍后 resume"。

## Step 3 — Pass 2a 纵深再分析（Opus subagent × N，串行）

对每个本批次 pending UUID，依次派一个 Opus subagent，prompt 基于 `prompts/pass2a.md`，替换占位符：
- `{session_id}` → 当前 UUID
- `{pass1_path}` → `<PASS1_DIR>\<uuid>.md`
- `{pass1_model}` → `opus`（或实际使用的 Pass 1 模型）
- `{pass2a_model}` → `opus`
- `{output_path}` → `<PASS2A_DIR>\<uuid>.md`

**可并行派发**。Pass 2a 输入是 Pass 1 digest（体量远小于原始 transcript），可以分批并行（建议每批 5-6 个，视 rate limit 调整）。

失败处理同 Step 2。

## Step 4 — Pass 2b 跨 session 综合（单次 Opus subagent）

派一个 Opus subagent，prompt 基于 `prompts/pass2b.md`，占位符：
- `{pass2a_dir}` → `<PASS2A_DIR>`
- `{pass2a_file_list}` → 本批次所有 pending UUID 对应的 `<uuid>.md` 路径列表
- `{pass1_dir}` → `<PASS1_DIR>`
- `{batch_id}` → 当前日期，例如 `2026-04-08`
- `{n}` → 本批次 session 数
- `{output_path}` → `<PASS2B_DIR>\synthesis_<batch_id>.md`

返回后在 manifest 把本批所有 session 的 Pass 2 Batch 列填上 batch_id。

## Step 5 — Pass 3 Reporter（单次 Sonnet subagent）

派一个 Sonnet subagent（注意：Sonnet，不是 Opus），prompt 基于 `prompts/pass3_reporter.md`：
- `{synthesis_path}` → `<PASS2B_DIR>\synthesis_<batch_id>.md`
- `{pass1_dir}` → `<PASS1_DIR>`
- `{output_path}` → `<PASS2B_DIR>\report_<batch_id>.md`

## Step 6 — 更新水位线（Python, 零 token）

派 shell-runner 运行：

```
python D:\Ai_Project\MeowOS\80_Knowledge\86_AI_Systems\digest_pipeline\update_watermark.py --project MeowOS
```

## Step 7 — 向 Vincent 汇报

让 shell-runner 读取 `<PASS2B_DIR>\report_<batch_id>.md` 并返回内容。把它**完整**转给 Vincent，加一行导读：本批涉及 N 个 session，完整综合在 `<synthesis path>`，Pass 2a 纵深分析在 `<PASS2A_DIR>`，Pass 1 原始 digest 在 `<PASS1_DIR>`。

## 失败恢复

Manifest 是真相来源：

- 有 `pending` 但 Pass 1 列未 `done` → 从这里 resume Pass 1
- 所有 Pass 1 都 done 但 Pass 2a 未完成 → 跑 Pass 2a（检查 `<PASS2A_DIR>` 里哪些 UUID 缺失）
- 所有 Pass 2a 都 done 但 Pass 2 Batch 列空 → 跑 Pass 2b
- Pass 2b 完成但没有对应 report 文件 → 跑 Pass 3
- 一切完成 → 跑 update_watermark

Vincent 说"继续 digest pipeline"时按此顺序检查。

## 警告

- **不要**把 pipeline 产物自动写入 `80_Knowledge/` 下的 warm memory 文件或 `MEMORY.md`。升温只发生在系统诊断 session 里，由 Vincent 审批。
- **不要**扫描 Horsys 或 NovelOS 的 jsonl。v1 只做 MeowOS。
- **不要**删除 `Session_Digests/_experiment/` 文件夹下的任何文件，那是参考资料。

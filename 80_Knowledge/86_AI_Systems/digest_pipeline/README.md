---
id: README
title: Digest Pipeline
tags: [ai-systems, meta, digest-pipeline, documentation]
status: confirmed
last_modified: 2026-04-15
summary: Digest Pipeline 目录与架构说明，将历史 session 清洗成冷归档知识
---
# Digest Pipeline

把历史 Claude Code session 清洗成可供凌喵按需读取的冷归档知识。

## 目录

```
digest_pipeline/
├── normalize_jsonl.py      # 清洗 jsonl → txt，剥代码块
├── manifest_scan.py        # 扫新 session，按 1500 字符截断，追加 manifest
├── update_watermark.py     # 批处理完成后更新水位线
├── prompts/
│   ├── pass1.md            # 单 session digest (Opus)
│   ├── pass2a.md           # 纵深再分析，per session (Opus)
│   ├── pass2b.md           # 跨 session 综合 (Opus)
│   ├── pass2.md            # [已废弃] 旧版跨 session 综合
│   └── pass3_reporter.md   # 面向 Vincent 的简报 (Sonnet)
├── RUN.md                  # 运行手册（给凌喵读）
└── README.md               # 本文件
```

## 哲学

- **Lossy by design**：不追求完备。漏掉的东西会因为 Vincent 长期使用这个系统自然再次出现。
- **水位线机制**：每次批处理只处理 mtime > last_processed_at 的 session，永不回头。
- **主 session 是净土**：一切读写派给 subagent。主 session 只看 Pass 3 的简报。
- **Cold insight 不自动升温**：pipeline 产出的 digest 只是素材。写进 warm/hot memory 的决定必须由 Vincent 在系统诊断 session 里审批。

## 产物位置

```
Session_Digests/
├── MeowOS/
│   ├── manifest.md              # 账本
│   ├── pass1/<uuid>.md          # 单 session digest
│   ├── pass2a/<uuid>.md         # 纵深再分析（基于 pass1 的深度二次解读）
│   └── pass2b/
│       ├── synthesis_<date>.md  # 跨 session 综合（基于 pass2a 的横向分析）
│       └── report_<date>.md     # Vincent 看的简报
└── _experiment/                  # 早期模型对比实验，保留做参考
```

## 触发方式

1. **系统诊断 session**：作为诊断流程的一步自动执行
2. **手动批处理**：Vincent 说"跑 digest pipeline"，凌喵读 RUN.md 执行

详见 `RUN.md`。

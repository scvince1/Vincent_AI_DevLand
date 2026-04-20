---
name: subtitle-download
description: "Use when Vincent wants to download subtitles from Bilibili or YouTube as text files. Triggers: video/channel/UP主 link, '下载字幕', 'download subs', '字幕下载'. If URL or save path missing, prompts Vincent before proceeding. Project-agnostic: works from any project (MeowOS / Horsys / others)."
---

# 字幕批量下载 Skill（系统级）

从 Bilibili 或 YouTube 下载字幕，转为纯文本存档。可在任何 project session 中调用。

## 工具

- `python -m yt_dlp` (已安装，版本 2026.03.17)

## 认证

- **Cookies 文件：** `C:\Users\scvin\Downloads\cookies.txt`
- **备选（如 cookies 过期）：** `--cookies-from-browser chrome`
- Bilibili 的 AI 字幕（ai-zh）**必须登录**才能获取，所有 Bilibili 命令都需要加 `--cookies` 参数

## 流程

### Step 0 — 收集输入（强制）

**0a. 如果 Vincent 没提供视频链接**，先问：
> 要下载哪个视频/UP主/频道的字幕喵？给我个链接。

等 Vincent 给出链接后再继续。

**0b. 询问保存位置（必问，不要自作主张）：**

根据当前 project 推荐默认路径：
- MeowOS session → `D:\Ai_Project\MeowOS\00_Dump\bilibili_subs\{创作者名}\`
- Horsys session → `D:\Ai_Project\Horsys\00_Dump\subs\{创作者名}\`（如该目录不存在，询问 Vincent 偏好）
- 其他 project → 基于项目根目录的 `00_Dump/` 或 Vincent 指定

问：
> 建议存到 `{推荐路径}`，用这个吗？还是换个地方喵？

- Vincent 确认 → 用推荐路径（`{创作者名}` 用 yt-dlp 的 `%(uploader)s` 填充）
- Vincent 指定 → 用 Vincent 的路径
- 等 Vincent 明确确认再继续

### Step 1 — 解析输入

链接类型：
- **单个视频链接**（bilibili BV/av 号，YouTube watch 链接）→ 直接下载
- **UP主主页 / YouTube 频道页** → 先列出视频，问 Vincent 要全部还是部分
- **合集/收藏夹/播放列表链接** → 同上，先列再确认

判断平台：URL 含 `bilibili.com` 或 `b23.tv` → Bilibili；含 `youtube.com` 或 `youtu.be` → YouTube。

### Step 2 — 列出视频（仅频道/合集场景）

派 shell-runner / 通过 Bash 执行：
```bash
python -m yt_dlp --cookies "C:/Users/scvin/Downloads/cookies.txt" --flat-playlist --print "%(id)s | %(title)s" "URL"
```

将结果列表呈现给 Vincent，问：
- 全部下载？
- 只要其中一部分？（让 Vincent 指定编号或关键词筛选）

### Step 3 — 下载字幕

**创建输出目录**（如不存在）：
```bash
mkdir -p "{保存路径}"
```

**Bilibili：**
```bash
python -m yt_dlp --cookies "C:/Users/scvin/Downloads/cookies.txt" --write-subs --sub-lang "ai-zh" --sub-format srt --skip-download --no-overwrites -o "{保存路径}/%(title)s.%(ext)s" "VIDEO_URL"
```

**YouTube：**
```bash
python -m yt_dlp --write-subs --write-auto-subs --sub-lang "zh,en" --sub-format srt --skip-download --no-overwrites -o "{保存路径}/%(title)s.%(ext)s" "VIDEO_URL"
```

> 批量下载时对每个视频 URL 逐个执行，或用播放列表 URL 一次性处理。

**下载失败处理：**
- 记录失败的视频标题和 URL
- 常见原因：视频无字幕（Bilibili 大多数视频只有弹幕没有 AI 字幕）、地区限制、视频已删除
- 所有失败项汇总报告给 Vincent，不静默跳过

### Step 4 — 转码为纯文本

执行 Python：

```python
import re
from pathlib import Path

target_dir = Path("{保存路径}")
converted = []
for sub_file in list(target_dir.glob("*.srt")) + list(target_dir.glob("*.vtt")):
    lines = sub_file.read_text(encoding="utf-8").splitlines()
    text_lines = [
        line.strip() for line in lines
        if line.strip()
        and not re.match(r"^\d+$", line.strip())
        and not re.match(r"^\d{2}:\d{2}:\d{2}[,.]\d+ --> ", line.strip())
        and not line.strip().startswith("WEBVTT")
        and not re.match(r"^Kind:|^Language:", line.strip())
    ]
    txt_file = sub_file.with_suffix(".txt")
    txt_file.write_text("\n".join(text_lines), encoding="utf-8")
    converted.append(sub_file.name)
    sub_file.unlink()
print(f"转换完成：{len(converted)} 个文件")
```

> 同时处理 SRT 和 VTT 格式。转换后删除原始字幕文件。

### Step 5 — 生成/更新 metadata.csv

追加到 `{保存路径}/metadata.csv`：
- 日期：yt-dlp 元数据（`--print "%(upload_date)s"`）
- 标题：文件名去扩展名

格式：`YYYYMMDD,视频标题`（无表头）

### Step 6 — 汇报结果

向 Vincent 报告：
- 成功下载并转换了 N 个字幕
- 失败了 M 个（附列表和原因）
- 输出路径

## 注意事项

- Bilibili 的 `ai-zh` 字幕并非所有视频都有，大量视频只有弹幕（danmaku）
- YouTube 的自动字幕质量参差不齐
- MeowOS session 中优先通过 shell-runner subagent 执行所有文件操作（保持主 context 干净）；其他 project 按该 project 的惯例

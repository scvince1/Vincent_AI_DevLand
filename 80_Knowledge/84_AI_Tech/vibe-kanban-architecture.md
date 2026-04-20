# Vibe Kanban 架构逆向分析

**调研日期**: 2026-04-19
**来源**: BloopAI/vibe-kanban GitHub repo (公开, MIT) + DeepWiki + 官方文档
**状态**: 公司 bloop 宣布关闭 (2026-04-10)，项目转社区维护 open source

---

## 0. 背景

- **公司**: bloop (Louis Knight-Webb 创始人)
- **产品发布**: 2025 年 6 月
- **关闭公告**: 2026-04-10，原文：https://vibekanban.com/blog/shutdown
- **GitHub**: https://github.com/BloopAI/vibe-kanban
- **技术栈**: Rust 后端 (50.2%) + TypeScript/React 前端 (46.1%)
- **关闭原因**: "the vast majority are free users and we couldn't find a business model that we could get excited about." 纯商业决策，非技术或 rate limit 问题

---

## 1. Spawn 机制

**结论**: 直接用 `tokio::process::Command` spawn `npx -y @anthropic-ai/claude-code@2.1.112` 子进程，不是 Agent SDK，不是 daemon。

**关键文件**: `crates/executors/src/executors/claude.rs`

```rust
// 第 70 行：base command
fn base_command(claude_code_router: bool) -> &'static str {
    if claude_code_router {
        "npx -y @musistudio/claude-code-router@1.0.66 code"
    } else {
        "npx -y @anthropic-ai/claude-code@2.1.112"  // 锁定版本号
    }
}

// spawn_internal() 第 633-656 行：
let mut command = Command::new(program_path);
command
    .kill_on_drop(true)
    .stdin(Stdio::piped())
    .stdout(Stdio::piped())
    .stderr(Stdio::piped())
    .current_dir(current_dir)     // 每个 ticket 有自己的 worktree 目录
    .env("NPM_CONFIG_LOGLEVEL", "error")
    .args(&args);

let mut child = command.group_spawn_no_window()?;  // 用 command-group crate
```

关键标志（build_command_builder 第 195-215 行）：

```
--permission-prompt-tool=stdio
--output-format=stream-json
--input-format=stream-json
--verbose
--include-partial-messages
--replay-user-messages
```

进程管理 crate: `command-group`（创建进程组，kill 时子进程树一并清理）。

Follow-up / 续接会话（spawn_follow_up 第 360-380 行）：

```rust
let mut args = vec!["--resume".to_string(), session_id.to_string()];
if let Some(uuid) = reset_to_message_id {
    args.push("--resume-session-at".to_string());
    args.push(uuid.to_string());
}
```

session_id 从 Claude 的 stream-json 输出中实时提取（`ClaudeJson::Assistant { session_id, .. }` 等字段）并存 SQLite，后续用于 `--resume` 恢复对话。

---

## 2. Context 隔离：Git Worktree

**关键文件**: `crates/local-deployment/src/container.rs`

每个 ticket ("workspace") 对应一个独立 git worktree，步骤：
1. `LocalContainerService` 调用 `WorkspaceManager::ensure_container_exists()`
2. 用 `git2` crate (`GitService`) 执行 `git worktree add <path> <new_branch>`
3. 目录命名：`{short_uuid}-{git_branch_id(task_title)}`（`git_branch_id` 函数将 task title slug 化）
4. `container_ref` 字段存储该 worktree 的绝对路径，后续作为 `current_dir` 传给 spawn

优点：共享 `.git` 目录，不重复复制 repo；各 ticket 文件系统完全隔离。无 Docker 开销。

清理策略：
- `worktree_deleted = true` 标记后，物理 worktree 被删除，数据库记录保留
- 14 天未使用自动清理
- 启动时：所有还标记为 `running` 的 `ExecutionProcess` 强制转为 `failed`（孤儿恢复）
- 环境变量 `DISABLE_WORKTREE_CLEANUP=1` 可关闭自动清理

---

## 3. 通信协议

### 3a. Vibe Kanban UI ↔ 后端
- Axum HTTP REST + WebSocket
- `EventService`：SQLite hook-based change capture → WebSocket streaming
- `MsgStore`：in-memory ring buffer，缓存 agent 实时输出供 WebSocket subscriber 订阅
- `ts-rs`：Rust struct `#[derive(TS)]` 注解自动生成 TypeScript 类型定义

### 3b. 后端 ↔ Claude Code 子进程
双向 line-delimited JSON over stdin/stdout（非 socket，非文件轮询）

```rust
// protocol.rs: ProtocolPeer 处理双向通信
pub struct ProtocolPeer {
    stdin: Arc<Mutex<ChildStdin>>,
}

// read_loop：一行一行读 stdout，遇到 CLIMessage::Result 则结束
tokio::select! {
    line_result = reader.read_line(&mut buffer) => {
        match serde_json::from_str::<CLIMessage>(line) {
            Ok(CLIMessage::ControlRequest { request_id, request }) => {
                self.handle_control_request(...).await;   // 处理工具权限请求
            }
            Ok(CLIMessage::Result(_)) => {
                break;  // 任务完成信号
            }
        }
    }
}
```

控制消息类型（`ControlRequestType`）：
- `CanUseTool { tool_name, input, ... }` → 工具权限批准
- `HookCallback { callback_id, input, ... }` → Stop hook 回调

### 3c. dev-manager-mcp daemon
独立 daemon 管理多个 agent 同时跑时的端口分配，防冲突。

---

## 4. 命名 + 寻址

| 层 | 数据库表/模型 | 关键字段 |
|---|---|---|
| Issue | `issues` | kanban card，标题、描述、状态 |
| Workspace | `workspaces` | `container_ref`（worktree 绝对路径），`archived`，`worktree_deleted` |
| Session | `sessions` | `agent_working_dir`（相对 workspace root），存 session turns |
| ExecutionProcess | `execution_processes` | `status`（running/failed/completed），`run_reason` |

session_id 提取（claude.rs 第 813-817 行）：

```rust
if !session_id_extracted
    && let Some(session_id) = Self::extract_session_id(&claude_json)
{
    msg_store.push_session_id(session_id);
    session_id_extracted = true;
}
```

UI 点开 ticket 重新对话：前端通过 workspace ID 从 SQLite 读对应 session 的 `session_id`，调用 `spawn_follow_up(session_id, ...)` + `--resume` flag 恢复 Claude 对话历史。

---

## 5. 完成检测 / 超时 / 错误处理

完成检测：
- `spawn_exit_monitor()` task（container.rs 第 480 行）监听进程退出
- `CLIMessage::Result` 从 stdout 流读到时 read_loop 退出

完成后动作：
1. 自动 commit agent 变更（commit message 从 `CodingAgentTurn` 摘要派生）
2. `should_finalize()` 判断是否完全完成
3. 触发 `QueuedMessageService` 处理排队消息

超时 / 崩溃恢复：
- 启动时 `ExecutionProcess::find_running()` → 遗留 `running` 强制改为 `failed`
- `CancellationToken`：cancel 时向 Claude stdin 发 interrupt，等 Claude 返回 Result 优雅退出

状态机（workspace.rs）：

```
Created → Setting Up → Ready → Executing → (Archived | Deleted)
```

---

## 6. 开源情况

完全开源，MIT 协议。https://github.com/BloopAI/vibe-kanban

关键文件：

| 文件 | 内容 |
|---|---|
| `crates/executors/src/executors/claude.rs` | Claude Code executor（3284 行） |
| `crates/executors/src/executors/mod.rs` | `StandardCodingAgentExecutor` trait + `CodingAgent` enum |
| `crates/executors/src/executors/claude/protocol.rs` | stdin/stdout JSON-RPC ProtocolPeer |
| `crates/executors/src/executors/claude/client.rs` | ClaudeAgentClient，工具审批回调 |
| `crates/local-deployment/src/container.rs` | worktree 创建，进程生命周期 |
| `crates/db/src/models/workspace.rs` | Workspace 状态机 |
| `crates/db/src/models/session.rs` | Session 模型，session_id 持久化 |

DeepWiki: https://deepwiki.com/BloopAI/vibe-kanban

---

## 7. 下线原因

原文：
> "the vast majority are free users and we couldn't find a business model that we could get excited about"

- 纯商业决策，非技术，非 rate limit
- 远程服务 30 天后关闭（2026-05-10 前），退化为完全本地架构
- 关闭：云端 kanban issues/comments/projects/organisations
- 保留：本地 workspace、worktree、agent 执行（本地用永久可用）
- 项目转社区维护，将发布 roadmap

---

## 分析注：值得抄的 3 个设计点

1. **session_id 提取 + `--resume` 续接**：不自己管 context，完全依赖 Claude CLI `--resume <session_id>`。session_id 从 stream-json 首条消息实时提取存库，后续恢复天然继承 Claude 原生的历史压缩逻辑。

2. **stdin/stdout line-JSON 双工**：子进程即通信端点，无额外 server/socket。`ProtocolPeer` 封装成 RPC（工具审批请求/响应），完成检测也在这一层（`CLIMessage::Result`）。

3. **git worktree + command-group 双保险**：worktree 保证文件系统隔离（无 Docker），command-group 保证进程组隔离（kill 一个不误杀其他）。N 并发的最轻量组合。

## 分析注：已知限制

- 依赖本地 `npx` + CC 账号认证；版本锁 `@2.1.112`，升级 CC 需验证兼容
- 跨 ticket 协调只能靠 MCP 或文件约定，无原生 orchestration 机制
- `dev-manager-mcp` daemon 是额外故障点
- SQLite 15+ 并发写可能有锁竞争（未确认 WAL 模式）

---

*Sources*:
- https://github.com/BloopAI/vibe-kanban
- https://deepwiki.com/BloopAI/vibe-kanban
- https://deepwiki.com/BloopAI/vibe-kanban/2.3-workspaces-and-execution-lifecycle
- https://deepwiki.com/BloopAI/vibe-kanban/3.1-executor-architecture-and-traits
- https://deepwiki.com/BloopAI/vibe-kanban/3.3-executor-implementations
- https://vibekanban.com/blog/shutdown
- https://virtuslab.com/blog/ai/vibe-kanban

# Claude Code 配置总览

生成时间：2026-05-10

---

## 1. 项目信息

| 项目 | 路径 |
|---|---|
| 工作目录 | `D:\Claude Code` |
| 启动命令 | `cd /d/claude\ code && claude` |

**CLAUDE.md** (`D:\Claude Code\CLAUDE.md`) — 项目级说明文件，记录启动方式和简要说明。

---

## 2. npm 配置

| 配置项 | 值 |
|---|---|
| Registry | `https://registry.npmmirror.com`（淘宝镜像/国内源） |
| 配置文件 | `C:\Users\yyj\.npmrc` |
| Node.js | v24.15.0 |
| npm | 11.12.1 |

已缓存的 MCP 相关包（无需重新下载）：
- `@modelcontextprotocol/server-filesystem@2026.1.14`
- `@modelcontextprotocol/server-sequential-thinking@2025.12.18`
- `@modelcontextprotocol/sdk@1.29.0`

---

## 3. MCP 服务

配置在 `D:\Claude Code\.mcp.json`：

| 服务名 | 包 | 说明 |
|---|---|---|
| `filesystem` | `@modelcontextprotocol/server-filesystem` | 文件系统操作，限定 `D:\Claude Code` 目录 |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | 分步推理增强 |
| `google-search` | `@mcp-server/google-search-mcp` | Google 网页搜索（Playwright 驱动，默认 zh-CN/cn） |

运行方式：通过 `npx -y` 启动，自动使用国内源加载缓存。

Playwright 浏览器已安装：Chromium 147.0.7727.15（`C:\Users\yyj\AppData\Local\ms-playwright\`）。

---

## 4. 用户级设置 (`C:\Users\yyj\.claude\`)

### settings.json — 全局设置

```json
{
  "theme": "dark",
  "statusLine": {
    "command": "D: \\claude code"
  }
}
```

- 主题：暗色
- 状态栏显示当前工作目录，每 30 秒刷新

### settings.local.json — 本地权限

```json
{
  "permissions": {
    "allow": [
      "Skill(update-config)"
    ]
  }
}
```

- 仅允许 `update-config` 技能

---

## 5. 项目级设置 (`D:\Claude Code\.claude\`)

### settings.local.json — 项目权限

已授权的操作包括：npm 配置、Web 搜索/抓取、Git、React Native、Python 环境、CMake、WSL、PowerShell 等。

---

## 6. 记忆系统

| 路径 | 说明 |
|---|---|
| `C:\Users\yyj\.claude\projects\D--Claude-Code\memory\MEMORY.md` | 记忆索引文件 |
| `C:\Users\yyj\.claude\projects\D--Claude-Code\memory\*.md` | 具体记忆记录 |

已记录的记忆：
- 项目级记忆存档位置和使用规则
- 用户偏好使用中文沟通
- 每次对话必须主动读取记忆存档

---

## 7. 插件市场

Claude Code 已集成以下外部插件（位于 `C:\Users\yyj\.claude\plugins\marketplaces\claude-plugins-official\external_plugins\`）：

`context7`, `github`, `discord`, `telegram`, `asana`, `firebase`, `gitlab`, `greptile`, `imessage`, `linear`, `playwright`, `serena`, `terraform`, `laravel-boost`, `fakechat`

当前活跃使用的 MCP 工具：`context7`（文档查询）、`sequential-thinking`（分步推理）、`filesystem`（文件系统）。

---

## 配置层级关系

```
用户级 (C:\Users\yyj\.claude\)
├── settings.json          ← 主题、状态栏
├── settings.local.json    ← update-config 权限
├── .npmrc                 ← npm 国内源
└── projects\D--Claude-Code\memory\  ← 记忆系统

项目级 (D:\Claude Code\)
├── CLAUDE.md              ← 项目说明
├── .mcp.json              ← MCP 服务配置
└── .claude\
    └── settings.local.json ← 项目权限白名单
```

# 小米 MiMo-V2.5-TTS Series + ASR 三平台接入指南

> MiMo-V2.5-TTS Series（语音合成三件套）+ MiMo-V2.5-ASR（语音识别，已开源）
> 小米 2026-04-24 发布的全链路语音大模型

---

## 前置条件：获取 MiMo API Key

三个平台通用。

1. 打开 [platform.xiaomimimo.com](https://platform.xiaomimimo.com)，用小米账号登录
2. 进入 **控制台 → API Keys → 新建 API Key**
3. **立即复制保存** Key（关闭后不可找回）
4. TTS/ASR 接口地址：`https://api.xiaomimimo.com/v1`

---

## 一、接入 Claude Code（Windows/Linux/macOS）

通过 **mimo-mcp** 社区 MCP Server 接入，MiMo TTS/ASR/音色克隆封装为 11 个 MCP Tool。

### 第 1 步：克隆并安装

```bash
git clone https://github.com/Frank-ay/mimo-mcp.git
cd mimo-mcp

pip install uv
uv sync

# 可选：Web 管理面板
cd webui/frontend && pnpm install && cd ../..
```

### 第 2 步：配置 API Key

```bash
cp .env.example .env
```

编辑 `.env`：

```ini
MIMO_API_KEY=sk-你的APIKey
```

### 第 3 步：注册到 Claude Code

编辑 `~/.claude/settings.local.json`：

```json
{
  "mcpServers": {
    "mimo-mcp": {
      "command": "/你的绝对路径/mimo-mcp/scripts/run_mcp.sh"
    }
  }
}
```

例如 Linux：`/home/username/mimo-mcp/scripts/run_mcp.sh`

### 第 4 步：验证

重启 Claude Code，输入：

```
调用 mimo.health
```

返回健康检查结果即成功。

### 第 5 步：日常使用

| 用法 | 示例 |
|------|------|
| TTS 语音合成 | `调用 mimo.tts，文本："你好"，声音风格："温柔亲切"` |
| ASR 语音识别 | `调用 mimo.asr，音频文件："/path/to/audio.wav"` |
| 音色设计 | `调用 mimo.voice_design_create，描述："温柔女性客服，28岁，普通话标准"` |
| 音色克隆 | `调用 mimo.voice_clone_create，参考音频："/path/to/sample.wav"，名称："我的声音"` |
| 列出音色 | `调用 mimo.voice_list` |

TTS 返回 WAV 文件路径，可在文件管理器播放。

---

## 二、接入 OpenClaw（Linux）

OpenClaw **已原生支持小米 MiMo 作为 TTS Provider**（社区贡献），无需开发。

### 第 1 步：安装 OpenClaw

```bash
# 需要 Node.js 22+
npm install -g openclaw
openclaw --version
```

### 第 2 步：配置小米 MiMo TTS

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "messages": {
    "tts": {
      "auto": "always",
      "provider": "xiaomi",
      "providers": {
        "xiaomi": {
          "apiKey": "${MIMO_API_KEY}",
          "baseUrl": "https://api.xiaomimimo.com/v1"
        }
      }
    }
  }
}
```

设置环境变量（避免 API Key 明文写入配置文件）：

```bash
export MIMO_API_KEY=sk-你的APIKey
```

### 第 3 步：配置 ASR（可选）

OpenClaw 可以通过 OpenAI 兼容接口调 MiMo ASR：

```json
{
  "media-understanding": {
    "provider": "openai",
    "providers": {
      "openai": {
        "apiKey": "${MIMO_API_KEY}",
        "baseUrl": "https://api.xiaomimimo.com/v1",
        "model": "mimo-v2.5-asr"
      }
    }
  }
}
```

### 第 4 步：验证

```bash
/tts status
/tts audio 你好，我是搭载小米语音的AI助手
```

---

## 三、接入 Hermes Agent（Linux）

### 方案 A：MiMo 作为 LLM + Edge TTS（开箱即用）

Hermes Agent v0.13+ 已通过 Nous Portal 支持 MiMo 模型。

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
hermes model
# → 选择 Nous Portal → xiaomi/mimo-v2-pro
```

TTS 使用 Edge TTS（免费，中文支持好）：

```yaml
# ~/.hermes/config.yaml
tts:
  provider: edge
  edge:
    voice: zh-CN-XiaoxiaoNeural

stt:
  enabled: true
  provider: local
  local:
    model: base
```

### 方案 B：修改源码添加 MiMo TTS Provider（完整接入）

克隆源码：

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
pip install -e ".[voice]"
```

编辑 `hermes_cli/tools/tts_tool.py`，添加以下方法：

```python
async def _generate_mimo_tts(self, text: str, **kwargs) -> str:
    """小米 MiMo TTS 合成"""
    import httpx

    api_key = os.getenv("MIMO_API_KEY")
    voice = kwargs.get("voice", "zh-CN-XiaoxiaoNeural")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.xiaomimimo.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "mimo-v2.5-tts",
                "input": text,
                "voice": voice,
                "response_format": "wav",
            },
            timeout=30,
        )
        resp.raise_for_status()

    output_path = f"/tmp/mimo_tts_{hash(text)}.wav"
    with open(output_path, "wb") as f:
        f.write(resp.content)
    return output_path
```

在 provider 映射字典中注册：

```python
TTS_PROVIDERS = {
    "edge": _generate_edge_tts,
    "openai": _generate_openai_tts,
    "elevenlabs": _generate_elevenlabs_tts,
    "mimo": _generate_mimo_tts,  # ← 添加
    # ...
}
```

配置使用：

```yaml
# ~/.hermes/config.yaml
tts:
  provider: mimo
  mimo:
    voice: zh-CN-XiaoxiaoNeural
```

启动：

```bash
export MIMO_API_KEY=sk-你的APIKey
hermes voice start
hermes tts test "你好，我是搭载小米语音的 Hermes Agent"
```

---

## 方案对比

| 维度 | Claude Code | OpenClaw | Hermes Agent |
|------|------------|----------|--------------|
| 接入难度 | 低（MCP 一键） | 中（配置即可） | 高（方案B需改源码） |
| MiMo TTS | 是 | 是 | 是（方案B） |
| MiMo ASR | 是 | 是 | 是（方案B） |
| 音色克隆/设计 | 是 | 需插件 | 需开发 |
| 依赖 | Python 3.11+, uv | Node.js 22+ | Python 3.10+ |
| 推荐 | mimo-mcp MCP Server | 原生 Xiaomi Provider | 方案A + 方案B |

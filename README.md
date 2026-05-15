# Multi-Agent AI 开发流水线

基于多智能体（Multi-Agent）架构的自动化 AI 开发流水线，实现从自然语言需求到可运行代码的端到端转化。包含事件驱动的 Agent 通信总线、状态持久化、配置系统和报告生成等企业级特性。

## 特性

- **多 Agent 协作** — Planner → Executor → Reviewer 闭环流水线
- **事件驱动架构** — 内置 Message Bus 实现 Agent 间异步通信
- **安全审查** — 自动检测硬编码密钥、SQL 注入、路径遍历等 8 类安全风险
- **上下文管理** — 智能压缩历史对话，保留关键函数签名与变量名
- **状态持久化** — 自动保存流水线状态，支持失败恢复
- **报告生成** — Markdown / JSON 格式的执行报告
- **可配置** — JSON/YAML 配置文件 + 环境变量覆盖
- **CI 集成** — 内置 GitHub Actions 工作流（测试、lint、覆盖率检查）

## 架构

```
                      ┌──────────────────┐
                      │   Message Bus    │
                      │  (事件驱动通信)    │
                      └──────┬─┬─┬───────┘
          ┌───────────────────┘ │ └───────────────────┐
          ▼                     ▼                     ▼
   ┌──────────┐         ┌──────────┐         ┌────────────┐
   │ Planner  │ ──任务──▶│ Executor │ ──代码──▶│  Reviewer  │
   │ 需求拆解  │         │ 代码生成  │         │  安全审查   │
   └──────────┘         └──────────┘         └────────────┘
        │                      │                     │
        ▼                      ▼                     ▼
   ┌─────────────────────────────────────────────────────┐
   │              Context Manager (上下文压缩)             │
   └─────────────────────────────────────────────────────┘
```

### Agent 职责

| Agent | 功能 |
|-------|------|
| **Planner** | 解析自然语言需求，输出结构化子任务列表，支持嵌套任务与优先级标记 |
| **Executor** | 根据任务描述生成符合 PEP8 规范的 Python 代码，自动添加类型注解 |
| **Reviewer** | 对生成代码进行安全扫描（8 类规则）与质量审查，输出修复建议 |

## 项目结构

```
├── src/
│   ├── agents/
│   │   ├── planner.py            # 任务拆解 Agent
│   │   └── executor.py           # 代码生成 Agent
│   ├── core/
│   │   └── reviewer.py           # 审查 Agent
│   ├── bus/
│   │   └── message_bus.py        # 事件驱动消息总线
│   ├── config/
│   │   └── settings.py           # 配置系统（JSON/YAML + 环境变量）
│   ├── pipeline/
│   │   ├── orchestrator.py       # 多 Agent 调度器
│   │   └── runner.py             # 高级 Runner（状态持久化 + 恢复）
│   ├── report/
│   │   └── reporter.py           # 报告生成器（Markdown / JSON）
│   └── utils/
│       ├── parser.py             # 需求解析工具
│       └── context_manager.py    # 上下文压缩模块
├── schemas/
│   └── task_schema.py            # 任务数据模型（嵌套、优先级、状态）
├── models/
│   └── mimo-v2.5-pro.py          # MiMo 模型接口（支持回退模式）
├── rules/
│   ├── security_rules.json       # 安全规则定义（8 类）
│   └── security_rules.py         # 规则引擎
├── linters/
│   └── pylint_wrapper.py         # Pylint 封装 + 自定义检查
├── tools/
│   └── code_formatter.py         # 代码格式化（autopep8/black）
├── nlp/
│   └── summarizer.py             # 上下文摘要工具
├── tests/
│   ├── unit/
│   │   ├── test_message_bus.py   # 消息总线测试
│   │   ├── test_settings.py      # 配置系统测试
│   │   ├── test_reporter.py      # 报告生成测试
│   │   └── test_runner.py        # Runner 测试
│   ├── integration/
│   │   └── test_pipeline.py      # 端到端测试（11 个用例）
│   ├── mocks/
│   │   └── stub_model.py         # 模拟模型
│   └── fixtures/
│       └── sample_requirements.json
├── main.py                       # CLI 入口
├── pyproject.toml                # 项目元数据与依赖
├── requirements-dev.txt          # 开发依赖
└── .github/workflows/ci.yml      # CI 工作流
```

## 快速开始

### 安装

```bash
# 克隆并安装
git clone https://github.com/squff/multi-agent.git
cd multi-agent
pip install -e .

# 开发模式（含测试工具）
pip install -e ".[dev]"
```

### 方式一：CLI 命令行

```bash
# 直接传入需求
python main.py --requirement "- [ ] Build login API (priority:high)"

# 从文件读取需求
echo "- [ ] Create user auth module" > requirement.txt
python main.py requirement.txt --json

# 完整配置
python main.py requirement.txt --max-retries 3 --report-dir ./reports --json
```

### 方式二：Python API

```python
from src.pipeline.orchestrator import Orchestrator
from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.core.reviewer import ReviewerAgent

orc = Orchestrator(
    planner=PlannerAgent(),
    executor=ExecutorAgent(),
    reviewer=ReviewerAgent(),
    max_retries=2,
)

requirement = """
- [ ] Create a user authentication module (priority:high)
- [ ] Implement login endpoint
- [ ] Add password validation
- [ ] Write unit tests (priority:medium)
"""

result = orc.run(requirement)
print(result["status"])        # completed / completed_with_issues / failed
print(result["metrics"])       # {total_tasks, completed_artifacts, total_issues, ...}
```

### 方式三：高级 Runner（带状态持久化）

```python
from src.pipeline.runner import PipelineRunner

runner = PipelineRunner()
result = runner.run("Build a REST API", pipeline_id="my_pipeline")

# 从失败状态恢复
resumed = runner.resume("my_pipeline")
```

## 配置

### 配置文件

创建 `config.json`：

```json
{
  "agent": {
    "max_retries": 3,
    "reviewer_threshold": 8.0,
    "max_concurrent_tasks": 5
  },
  "pipeline": {
    "log_level": "DEBUG",
    "persist_state": true,
    "report_dir": "reports"
  },
  "mimo": {
    "temperature": 0.2,
    "max_tokens": 65536
  }
}
```

使用：`python main.py req.txt --config config.json`

### 环境变量

| 变量 | 说明 |
|------|------|
| `MIMO_API_KEY` | MiMo 模型 API 密钥 |
| `MIMO_API_BASE` | MiMo API 地址（默认 `https://api.mimo-platform.dev/v1`） |
| `PIPELINE_LOG_LEVEL` | 日志级别（DEBUG/INFO/WARNING/ERROR） |

## 需求格式

支持 Markdown 任务列表格式，用缩进表示嵌套：

```markdown
- [ ] 顶级任务 (priority:high)
  - [ ] 子任务 1
  - [ ] 子任务 2 (priority:critical)
- [ ] 另一个顶级任务
```

优先级：`critical` > `high` > `medium`（默认）> `low`

## 运行测试

```bash
# 全部测试
python -m pytest -v

# 带覆盖率
python -m pytest --cov=src --cov=schemas --cov=rules --cov=linters

# 仅单元测试
python -m pytest tests/unit/ -v

# 仅集成测试
python -m pytest tests/integration/ -v
```

## 安全规则

| 规则 | 严重度 | 描述 |
|------|--------|------|
| SEC001 | Critical | 硬编码密钥/令牌 |
| SEC002 | Critical | SQL 注入（f-string 拼接） |
| SEC003 | High | eval/exec 执行 |
| SEC004 | High | 路径遍历 |
| SEC005 | Medium | Pickle 反序列化 |
| SEC006 | Medium | shell=True 子进程 |
| QUAL001 | Low | 缺少类型注解 |
| QUAL002 | Low | 函数过长（>50行） |

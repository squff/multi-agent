# Multi-Agent AI 开发流水线

基于多智能体（Multi-Agent）架构的自动化 AI 开发流水线，实现从自然语言需求到可运行代码的端到端转化。

## 架构

```
需求输入 → Planner（任务拆解）→ Executor（代码生成）→ Reviewer（安全审查）→ 输出交付
```

三个 Agent 闭环协作：

| Agent | 功能 |
|-------|------|
| **Planner** | 解析自然语言需求，输出结构化子任务列表，支持嵌套任务与优先级标记 |
| **Executor** | 根据任务描述生成符合 PEP8 规范的 Python 代码，自动添加类型注解 |
| **Reviewer** | 对生成代码进行安全扫描与质量审查，检测硬编码密钥、SQL 注入等风险 |

## 项目结构

```
├── src/
│   ├── agents/
│   │   ├── planner.py          # 任务拆解 Agent
│   │   └── executor.py         # 代码生成 Agent
│   ├── core/
│   │   └── reviewer.py         # 审查 Agent
│   ├── utils/
│   │   ├── parser.py           # 需求解析工具
│   │   └── context_manager.py  # 上下文压缩模块
│   └── pipeline/
│       └── orchestrator.py     # 多 Agent 调度器
├── schemas/
│   └── task_schema.py          # 任务数据模型
├── models/
│   └── mimo-v2.5-pro.py        # MiMo 模型接口
├── rules/
│   ├── security_rules.json     # 安全规则定义
│   └── security_rules.py       # 规则引擎
├── linters/
│   └── pylint_wrapper.py       # Pylint 封装
├── tools/
│   └── code_formatter.py       # 代码格式化工具
├── nlp/
│   └── summarizer.py           # 上下文摘要工具
└── tests/
    ├── integration/
    │   └── test_pipeline.py     # 端到端测试（11 个用例）
    ├── mocks/
    │   └── stub_model.py        # 模拟模型
    └── fixtures/
        └── sample_requirements.json
```

## 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装

```bash
# 克隆仓库
git clone https://github.com/squff/multi-agent.git
cd multi-agent

# 安装依赖（可选，运行测试需要）
pip install pylint autopep8 black
```

### 运行流水线

```python
from src.pipeline.orchestrator import Orchestrator
from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.core.reviewer import ReviewerAgent

orc = Orchestrator(
    planner=PlannerAgent(),
    executor=ExecutorAgent(),
    reviewer=ReviewerAgent(),
)

requirement = """
- [ ] Create a user authentication module (priority:high)
- [ ] Implement login endpoint
- [ ] Add password validation
- [ ] Write unit tests (priority:medium)
"""

result = orc.run(requirement)
print(result["status"])  # completed
print(result["artifacts"])  # 生成的代码
```

### 运行测试

```bash
# 从项目根目录运行
python -m pytest tests/integration/test_pipeline.py -v
```

## 配置

### MiMo 模型

设置环境变量以使用 MiMo-V2.5-Pro 模型：

```bash
export MIMO_API_KEY="your-api-key"
export MIMO_API_BASE="https://api.mimo-platform.dev/v1"
```

不设置时自动使用本地回退模式。

## 需求格式

支持 Markdown 任务列表格式，使用缩进表示嵌套关系：

```markdown
- [ ] 顶级任务 (priority:high)
  - [ ] 子任务 1
  - [ ] 子任务 2 (priority:critical)
- [ ] 另一个顶级任务
```

支持的优先级：`critical`、`high`、`medium`（默认）、`low`

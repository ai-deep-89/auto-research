# AutoResearch 多智能体系统

一个生产级别的自主科研智能体框架，具备多智能体协作、任务规划、自进化和自动化评测能力。

## 🌟 核心特性

- **多智能体协作**：专业智能体（研究员、规划师、执行器、评审员）协同工作
- **自主任务规划**：复杂任务自动分解、规划和执行
- **自进化机制**：智能体从反馈和评估结果中学习和改进
- **自动化评测**：内置评估框架，衡量智能体性能
- **工具集成**：丰富的工具生态系统（搜索、代码执行、数据分析）

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      AutoResearch 系统                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   研究员    │  │   规划师    │  │   执行器    │              │
│  │   智能体    │  │   智能体    │  │   智能体    │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│                 ┌─────────────────┐                              │
│                 │     评审员      │                              │
│                 │     智能体      │                              │
│                 └────────┬────────┘                              │
│                          │                                       │
│                          ▼                                       │
│                 ┌─────────────────┐                              │
│                 │    进化引擎      │◄────── 自我改进               │
│                 └─────────────────┘                              │
├─────────────────────────────────────────────────────────────────┤
│                      评测框架                                      │
│   任务成功率 │ 工具使用 │ 协作评分 │ 进化收益                      │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 安装

```bash
pip install -r requirements.txt
```

## 🚀 快速开始

### 基础科研任务

```python
from src.core.system import AutoResearchSystem
from src.agents.researcher import ResearcherAgent
from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.agents.reviewer import ReviewerAgent

# 初始化智能体
researcher = ResearcherAgent(model_name="gpt-4")
planner = PlannerAgent(model_name="gpt-4")
executor = ExecutorAgent(model_name="gpt-4")
reviewer = ReviewerAgent(model_name="gpt-4")

# 创建并运行系统
system = AutoResearchSystem(
    researcher=researcher,
    planner=planner,
    executor=executor,
    reviewer=reviewer
)

# 执行科研任务
result = system.run("研究LLM智能体自进化的最新进展")
print(result)
```

### 多智能体协作

```python
from src.core.multi_agent import MultiAgentCrew

crew = MultiAgentCrew(agents=[researcher, planner, executor, reviewer])
result = crew.run(task="对比自主科研多智能体框架")
```

### 自进化演示

```python
from src.evolution.evolution_engine import EvolutionEngine

engine = EvolutionEngine()
engine.evolve(agent=executor, feedback=evaluation_results)
```

## 📁 项目结构

```
auto-research-agent/
├── README.md                     # 英文说明
├── README_zh.md                  # 中文说明
├── detailed-explanation.md       # 详细项目文档
├── requirements.txt              # 依赖包
├── setup.py                      # 安装配置
├── src/
│   ├── __init__.py
│   ├── core/                     # 核心系统
│   │   ├── system.py            # 主研究系统
│   │   ├── multi_agent.py       # 多智能体编排
│   │   ├── task_planner.py      # 任务分解与规划
│   │   └── message.py            # 智能体间通信
│   ├── agents/                   # 智能体实现
│   │   ├── base_agent.py        # 基础智能体类
│   │   ├── researcher.py        # 研究员智能体
│   │   ├── planner.py           # 规划师智能体
│   │   ├── executor.py          # 执行器智能体
│   │   └── reviewer.py          # 评审员智能体
│   ├── tools/                    # 工具集
│   │   ├── search.py            # 网页搜索工具
│   │   ├── code_executor.py     # 代码执行工具
│   │   └── analyzer.py          # 数据分析工具
│   ├── evaluation/               # 评测框架
│   │   ├── evaluator.py         # 评估器
│   │   ├── metrics.py           # 性能指标
│   │   └── benchmark.py         # 基准任务
│   └── evolution/                # 进化机制
│       ├── evolution_engine.py   # 进化引擎
│       ├── feedback.py          # 反馈处理
│       └── optimizer.py         # 智能体优化器
├── examples/                     # 使用示例
│   ├── basic_research.py        # 基础用法
│   ├── multi_agent_demo.py      # 多智能体演示
│   └── evolution_demo.py        # 自进化演示
└── tests/                        # 单元测试
    ├── test_agents.py
    ├── test_evaluation.py
    └── test_evolution.py
```

## 📊 评测框架

系统包含全面的评测框架：

| 指标 | 描述 |
|------|------|
| 任务成功率 | 任务成功完成的百分比 |
| 工具使用准确率 | 正确选择和使用工具 |
| 协作评分 | 多智能体协作质量 |
| 进化收益 | 自进化后的改进幅度 |
| 响应质量 | 输出相关性和完整性 |

## 🔄 自进化流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    初始      │────►│    评估      │────►│    反馈      │
│    性能      │     │    结果      │     │    分析      │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                                                 ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    提升后    │◄────│    策略      │◄────│    模式      │
│    性能      │     │    更新      │     │    发现      │
└──────────────┘     └──────────────┘     └──────────────┘
```

## 📚 文档

- [detailed-explanation.md](detailed-explanation.md) - 详细项目文档

## 🎯 与岗位要求对应

| 岗位要求 | 项目展示 |
|---------|---------|
| AutoResearch | ✅ 自主科研工作流与任务规划 |
| 多智能体协同 | ✅ 4个专业智能体协作 |
| 任务规划 | ✅ 自动任务分解与规划 |
| 智能体自进化 | ✅ 从反馈中学习和改进 |
| Agent数据构建 | ✅ 评估驱动的数据生成 |
| 自动化评测 | ✅ 内置全面评测框架 |

## 📄 许可证

MIT License

## 🙏 致谢

本项目站在巨人的肩膀上，借鉴了以下项目：
- LightAgent（多智能体框架）
- GoA - Graph-of-Agents（ICLR 2026）
- EvoAgent（记忆进化）
- ResearchHarness（评测工具）

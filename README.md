# AutoResearch Multi-Agent System

A production-ready autonomous research agent framework featuring multi-agent collaboration, task planning, self-evolution, and automated evaluation.

## 🌟 Key Features

- **Multi-Agent Collaboration**: Specialized agents (Researcher, Planner, Executor, Reviewer) working together
- **Autonomous Task Planning**: Complex tasks automatically decomposed, planned, and executed
- **Self-Evolution Mechanism**: Agents learn and improve from feedback and evaluation results
- **Automated Evaluation**: Built-in evaluation framework for measuring agent performance
- **Tool Integration**: Rich tool ecosystem for web search, coding, data analysis

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AutoResearch System                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Researcher  │  │   Planner   │  │  Executor   │              │
│  │   Agent     │  │   Agent     │  │   Agent     │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│                 ┌─────────────────┐                              │
│                 │   Reviewer      │                              │
│                 │   Agent         │                              │
│                 └────────┬────────┘                              │
│                          │                                       │
│                          ▼                                       │
│                 ┌─────────────────┐                              │
│                 │   Evolution     │                              │
│                 │   Engine        │◄────── Self-Improvement      │
│                 └─────────────────┘                              │
├─────────────────────────────────────────────────────────────────┤
│                    Evaluation Framework                         │
│   Task Success │ Tool Usage │ Collaboration │ Evolution Gain     │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### Basic Research Task

```python
from src.core.system import AutoResearchSystem
from src.agents.researcher import ResearcherAgent
from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.agents.reviewer import ReviewerAgent

# Initialize agents
researcher = ResearcherAgent(model_name="gpt-4")
planner = PlannerAgent(model_name="gpt-4")
executor = ExecutorAgent(model_name="gpt-4")
reviewer = ReviewerAgent(model_name="gpt-4")

# Create and run system
system = AutoResearchSystem(
    researcher=researcher,
    planner=planner,
    executor=executor,
    reviewer=reviewer
)

# Execute research task
result = system.run("Research the latest advances in LLM agent self-evolution")
print(result)
```

### Multi-Agent Collaboration

```python
from src.core.multi_agent import MultiAgentCrew

crew = MultiAgentCrew(agents=[researcher, planner, executor, reviewer])
result = crew.run(task="Compare multi-agent frameworks for autonomous research")
```

### Self-Evolution Demo

```python
from src.evolution.evolution_engine import EvolutionEngine

engine = EvolutionEngine()
engine.evolve(agent=executor, feedback=evaluation_results)
```

## 📁 Project Structure

```
auto-research-agent/
├── README.md                     # This file
├── README_zh.md                  # Chinese version
├── detailed-explanation.md       # Detailed project documentation
├── requirements.txt              # Dependencies
├── setup.py                      # Setup configuration
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── system.py            # Main research system
│   │   ├── multi_agent.py       # Multi-agent orchestration
│   │   ├── task_planner.py       # Task decomposition & planning
│   │   └── message.py           # Inter-agent communication
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py        # Base agent class
│   │   ├── researcher.py         # Research agent
│   │   ├── planner.py           # Planning agent
│   │   ├── executor.py          # Execution agent
│   │   └── reviewer.py          # Review agent
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py            # Web search tool
│   │   ├── code_executor.py     # Code execution tool
│   │   └── analyzer.py          # Data analysis tool
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── evaluator.py         # Evaluation framework
│   │   ├── metrics.py           # Performance metrics
│   │   └── benchmark.py         # Benchmark tasks
│   └── evolution/
│       ├── __init__.py
│       ├── evolution_engine.py   # Self-evolution mechanism
│       ├── feedback.py          # Feedback processing
│       └── optimizer.py         # Agent optimization
├── examples/
│   ├── basic_research.py        # Basic usage example
│   ├── multi_agent_demo.py      # Multi-agent demo
│   └── evolution_demo.py        # Self-evolution demo
└── tests/
    ├── test_agents.py           # Agent unit tests
    ├── test_evaluation.py       # Evaluation tests
    └── test_evolution.py        # Evolution tests
```

## 📊 Evaluation Framework

The system includes a comprehensive evaluation framework:

| Metric | Description |
|--------|-------------|
| Task Success Rate | % of tasks completed successfully |
| Tool Usage Accuracy | Correct tool selection and usage |
| Collaboration Score | Quality of multi-agent cooperation |
| Evolution Gain | Improvement after self-evolution |
| Response Quality | Relevance and completeness of outputs |

## 🔄 Self-Evolution Process

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Initial    │────►│  Evaluation  │────►│   Feedback   │
│   Performance│     │   Results    │     │   Analysis   │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                                                 ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Improved    │◄────│  Strategy    │◄────│   Pattern    │
│  Performance │     │   Update     │     │   Discovery  │
└──────────────┘     └──────────────┘     └──────────────┘
```

## 📚 Documentation

- [detailed-explanation.md](detailed-explanation.md) - Comprehensive project documentation
- [examples/](examples/) - Usage examples for all features

## 🎯 Alignment with Job Requirements

| Requirement | Demonstration |
|-------------|---------------|
| AutoResearch | ✅ Autonomous research workflow with task planning |
| Multi-Agent Collaboration | ✅ 4 specialized agents working together |
| Task Planning | ✅ Automatic task decomposition and planning |
| Agent Self-Evolution | ✅ Learning from feedback and improving |
| Agent Data Construction | ✅ Evaluation-driven data generation |
| Automated Evaluation | ✅ Built-in comprehensive evaluation framework |

## 📄 License

MIT License

## 🙏 Acknowledgments

This project stands on the shoulders of giants, incorporating ideas from:
- LightAgent (multi-agent framework)
- GoA - Graph-of-Agents (ICLR 2026)
- EvoAgent (memory evolution)
- ResearchHarness (evaluation harness)

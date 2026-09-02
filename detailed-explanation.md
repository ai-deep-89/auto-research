# AutoResearch Multi-Agent System - Detailed Explanation

## 1. Project Overview

### 1.1 Problem Statement

Autonomous research agents face several critical challenges:
- **Complex task decomposition**: Breaking down research queries into executable sub-tasks
- **Multi-agent coordination**: Enabling specialized agents to collaborate effectively
- **Self-improvement**: Agents that can learn from feedback and evolve their capabilities
- **Evaluation**: Measuring agent performance across diverse research scenarios

### 1.2 Solution

AutoResearch Multi-Agent System is a production-ready framework that addresses these challenges through:

1. **Specialized Agent Architecture**: Four distinct agent roles (Researcher, Planner, Executor, Reviewer) working in concert
2. **Autonomous Task Planning**: Automatic decomposition of complex research tasks into executable plans
3. **Self-Evolution Engine**: Feedback-driven agent capability improvement
4. **Comprehensive Evaluation Framework**: Multi-dimensional performance metrics

## 2. System Architecture

### 2.1 Core Components

#### 2.1.1 Agent System

Four specialized agents:

| Agent | Role | Responsibilities |
|-------|------|-----------------|
| **ResearcherAgent** | Information gathering | Web search, paper analysis, knowledge retrieval |
| **PlannerAgent** | Task orchestration | Task decomposition, scheduling, priority setting |
| **ExecutorAgent** | Action execution | Code execution, tool invocation, result synthesis |
| **ReviewerAgent** | Quality assurance | Output validation, feedback generation, improvement suggestions |

#### 2.1.2 Inter-Agent Communication

Messages passed between agents follow a structured format:

```python
class Message:
    sender: str           # Source agent name
    receiver: str         # Target agent name (or "ALL")
    content: dict         # Message payload
    msg_type: str         # REQUEST, RESPONSE, FEEDBACK
    timestamp: float      # Creation time
```

#### 2.1.3 Tool Ecosystem

| Tool | Capability |
|------|------------|
| WebSearchTool | Bing, Google, ArXiv search |
| CodeExecutor | Python code execution with sandbox |
| DataAnalyzer | Statistical analysis, visualization |
| DocumentProcessor | PDF, markdown, text processing |

### 2.2 Data Flow

```
User Query
     │
     ▼
┌─────────────────┐
│   Task Parser   │ ─── Decompose into subtasks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Planner Agent  │ ─── Create execution plan
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│Research│ │Execute│
│ Agent │ │ Agent │
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         ▼
┌─────────────────┐
│ Reviewer Agent  │ ─── Validate & provide feedback
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Evolution Engine│ ─── Self-improvement
└─────────────────┘
```

## 3. Algorithms and Technical Principles

### 3.1 Task Planning Algorithm

The Planner Agent uses a hierarchical task decomposition approach:

```
1. Parse user query into intent and constraints
2. Identify required capabilities (search, coding, analysis)
3. Decompose into ordered subtasks
4. Assign subtasks to appropriate agents
5. Create dependency graph
6. Execute with real-time adaptation
```

### 3.2 Multi-Agent Collaboration Protocol

Based on the **Graph-of-Agents (GoA)** framework from ICLR 2026:

1. **Role Assignment**: Each agent has a defined specialty
2. **Message Passing**: Async communication via shared message queue
3. **Consensus Building**: Reviewer aggregates agent outputs
4. **Conflict Resolution**: Planner mediates disagreements

### 3.3 Self-Evolution Mechanism

The Evolution Engine implements a reinforcement-learning-inspired loop:

```
┌─────────────────────────────────────────────────────────┐
│                    EVOLUTION LOOP                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│   │  Rollout │───►│ Evaluate │───►│  Update  │        │
│   │ (Execute)│    │ (Metric) │    │ (Policy) │        │
│   └──────────┘    └──────────┘    └──────────┘        │
│        │                │                │              │
│        └────────────────┴────────────────┘              │
│                         │                               │
│                    iteration                            │
└─────────────────────────────────────────────────────────┘
```

**Key mechanisms:**

1. **Feedback Collection**: Gather evaluation results from ReviewerAgent
2. **Pattern Analysis**: Identify recurring failure modes
3. **Strategy Update**: Modify agent behavior prompts/rules
4. **A/B Testing**: Validate improvements before deployment

### 3.4 Evaluation Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Task Success Rate | successful_tasks / total_tasks | > 90% |
| Tool Accuracy | correct_tool_calls / total_calls | > 85% |
| Collaboration Score | weighted_agent_outputs | > 4.0/5 |
| Evolution Gain | (new_score - old_score) / old_score | > 5% |

## 4. Feature Specifications

### 4.1 Autonomous Research Workflow

**Input**: Natural language research query
**Process**:
1. Query understanding (Planner)
2. Subtask decomposition (Planner)
3. Parallel execution (Researcher + Executor)
4. Result synthesis (Reviewer)
5. Quality validation (Reviewer)

**Output**: Structured research report with citations

### 4.2 Multi-Agent Collaboration Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| Sequential | One agent after another | Simple tasks |
| Parallel | Multiple agents simultaneously | Independent subtasks |
| Hierarchical | Manager-worker structure | Complex coordination |
| Peer-to-Peer | Agents negotiate directly | Collaborative problem-solving |

### 4.3 Self-Evolution Capabilities

- **Memory Evolution**: Accumulate successful strategies
- **Prompt Refinement**: Improve agent instructions based on feedback
- **Tool Selection Learning**: Better tool choice over time
- **Error Recovery**: Learn from past failures

## 5. Project Structure Details

### 5.1 Core Module (src/core/)

| File | Purpose |
|------|---------|
| `system.py` | Main AutoResearchSystem orchestration |
| `multi_agent.py` | MultiAgentCrew for parallel execution |
| `task_planner.py` | Task decomposition logic |
| `message.py` | Inter-agent messaging |

### 5.2 Agent Module (src/agents/)

Each agent inherits from `BaseAgent` and implements:
- `think()`: Internal reasoning
- `act()`: Generate output/take action
- `learn()`: Update from feedback

### 5.3 Evaluation Module (src/evaluation/)

- `evaluator.py`: Main evaluation orchestrator
- `metrics.py`: Metric computation
- `benchmark.py`: Standard benchmark tasks

### 5.4 Evolution Module (src/evolution/)

- `evolution_engine.py`: Main evolution loop
- `feedback.py`: Feedback processing
- `optimizer.py`: Agent strategy optimization

## 6. Usage Examples

### 6.1 Basic Research Task

```python
from src.core.system import AutoResearchSystem

system = AutoResearchSystem()
result = system.run(
    "Research the impact of self-evolution on LLM agent performance"
)
```

### 6.2 Custom Agent Configuration

```python
from src.agents.researcher import ResearcherAgent
from src.tools.search import BingSearch

researcher = ResearcherAgent(
    model_name="gpt-4",
    tools=[BingSearch(api_key="...")],
    max_iterations=5
)
```

### 6.3 Evolution with Custom Feedback

```python
from src.evolution.evolution_engine import EvolutionEngine

engine = EvolutionEngine()
feedback = {
    "task_id": "task_123",
    "success": False,
    "reason": "Incorrect tool selection",
    "suggestion": "Use web search before code execution"
}
engine.evolve(agent=executor, feedback=feedback)
```

## 7. Evaluation Methodology

### 7.1 Benchmark Tasks

| Task Type | Description | Success Criteria |
|-----------|-------------|------------------|
| Research Query | Answer complex research questions | Factual accuracy > 80% |
| Code Generation | Write and execute code | Pass test cases |
| Multi-step Planning | Execute multi-hop tasks | Complete all steps |
| Collaboration | Multi-agent coordination | Achieve consensus |

### 7.2 Evaluation Process

```
1. Select benchmark task
2. Initialize fresh agent state
3. Execute task
4. Compute metrics
5. Store results
6. Generate report
```

### 7.3 Evolution Effectiveness

Measure improvement:
```
evolution_effectiveness = (post_score - pre_score) / pre_score * 100%
```

## 8. Technical Specifications

### 8.1 Dependencies

- Python 3.10+
- OpenAI API / Anthropic API / Local LLM
- LangChain (for tool integration)
- Streamlit (for UI)
- pytest (for testing)

### 8.2 Configuration

```yaml
system:
  model_name: "gpt-4"
  temperature: 0.7
  max_tokens: 4096

agents:
  researcher:
    tools: ["web_search", "code_executor"]
    max_iterations: 5
  planner:
    decomposition_depth: 3
  executor:
    timeout: 300
  reviewer:
    quality_threshold: 0.8

evolution:
  enabled: true
  population_size: 10
  mutation_rate: 0.1
  generations: 5
```

## 9. Alignment with Job Requirements

| Job Requirement | How Project Demonstrates |
|-----------------|--------------------------|
| AutoResearch核心技术 | Complete autonomous research workflow |
| 多智能体协同 | 4 specialized agents with collaboration protocol |
| 任务规划 | Automatic task decomposition and planning |
| 智能体自进化 | Evolution engine with feedback-driven improvement |
| Agent数据构建 | Evaluation-driven training data generation |
| 自动化评测 | Built-in comprehensive evaluation framework |
| 模型Post-Training | Prompt refinement in evolution loop |

## 10. Future Enhancements

1. **Distributed Execution**: Scale across multiple machines
2. **Additional Agents**: More specialized roles (critic, synthesizer)
3. **Learning Integration**: Full RL training for agent policies
4. **Benchmark Expansion**: More diverse evaluation scenarios
5. **UI Improvements**: Interactive research dashboard

## 11. Conclusion

AutoResearch Multi-Agent System provides a comprehensive framework for building, evaluating, and improving autonomous research agents. The combination of multi-agent collaboration, task planning, self-evolution, and automated evaluation makes it a strong demonstration of capabilities relevant to the target position.

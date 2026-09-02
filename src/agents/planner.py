"""Planner Agent - task decomposition and orchestration."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from src.agents.base_agent import BaseAgent, AgentConfig
from src.core.task_planner import Task, TaskPlanner, TaskPriority


class PlannerAgent(BaseAgent):
    """
    Agent specialized in task planning and decomposition.

    Capabilities:
    - Complex task analysis
    - Hierarchical task decomposition
    - Dependency management
    - Resource allocation
    - Plan optimization
    - Execution scheduling
    """

    def __init__(self, config: Optional[AgentConfig] = None, **kwargs):
        """
        Initialize Planner Agent.

        Args:
            config: Agent configuration
            **kwargs: Additional config parameters
        """
        if config is None:
            config = AgentConfig(name="planner", **kwargs)
        super().__init__(config)
        self.role = "planner"
        self.task_planner = TaskPlanner()
        self.current_plan: Optional[Dict[str, Any]] = None

    async def think(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze task and create execution plan.

        Args:
            task: Task description
            context: Shared context

        Returns:
            Thought process with plan
        """
        # Decompose task
        subtasks = self.task_planner.decompose(task)

        # Analyze complexity
        complexity = self._analyze_complexity(task, subtasks)

        # Determine optimal execution strategy
        strategy = self._determine_strategy(complexity, context)

        thought = {
            "task": task,
            "subtasks": [t.to_dict() for t in subtasks],
            "complexity": complexity,
            "strategy": strategy,
            "estimated_duration": self._estimate_duration(subtasks),
            "risks": self._identify_risks(subtasks),
        }

        return thought

    def _analyze_complexity(self, task: str, subtasks: List[Task]) -> str:
        """Analyze task complexity."""
        task_lower = task.lower()

        # Check for complexity indicators
        if any(kw in task_lower for kw in ["multi-step", "complex", "comprehensive"]):
            return "high"
        elif len(subtasks) > 5:
            return "medium"
        elif any(kw in task_lower for kw in ["simple", "quick", "basic"]):
            return "low"
        else:
            return "medium"

    def _determine_strategy(self, complexity: str,
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Determine execution strategy based on complexity."""
        strategies = {
            "low": {
                "mode": "sequential",
                "parallel_agents": 1,
                "max_iterations": 1,
            },
            "medium": {
                "mode": "parallel",
                "parallel_agents": 2,
                "max_iterations": 3,
            },
            "high": {
                "mode": "hierarchical",
                "parallel_agents": 3,
                "max_iterations": 5,
            },
        }
        return strategies.get(complexity, strategies["medium"])

    def _estimate_duration(self, subtasks: List[Task]) -> float:
        """Estimate total execution duration in seconds."""
        base_time_per_task = 30  # 30 seconds base per task
        return sum(
            base_time_per_task * (1 + 0.5 * (len(t.dependencies)))
            for t in subtasks
        )

    def _identify_risks(self, subtasks: List[Task]) -> List[Dict[str, str]]:
        """Identify potential risks in the plan."""
        risks = []

        # Check for circular dependencies
        task_ids = {t.task_id for t in subtasks}
        for t in subtasks:
            for dep in t.dependencies:
                if dep not in task_ids:
                    risks.append({
                        "type": "missing_dependency",
                        "task": t.task_id,
                        "dependency": dep,
                    })

        # Check for too many sequential tasks
        sequential_chains = self._find_sequential_chains(subtasks)
        if sequential_chains:
            max_chain = max(len(chain) for chain in sequential_chains)
            if max_chain > 5:
                risks.append({
                    "type": "long_chain",
                    "length": max_chain,
                    "suggestion": "Consider parallelizing some tasks",
                })

        return risks

    def _find_sequential_chains(self, subtasks: List[Task]) -> List[List[str]]:
        """Find chains of sequential dependencies."""
        # Build dependency graph
        chains = []
        for task in subtasks:
            if not task.dependencies:
                chain = self._build_chain(task.task_id, subtasks)
                if len(chain) > 1:
                    chains.append(chain)
        return chains

    def _build_chain(self, task_id: str, subtasks: List[Task]) -> List[str]:
        """Build dependency chain starting from task."""
        task_map = {t.task_id: t for t in subtasks}
        chain = [task_id]

        current = task_map.get(task_id)
        while current and current.dependencies:
            next_id = current.dependencies[0]
            if next_id in task_map:
                chain.append(next_id)
                current = task_map[next_id]
            else:
                break

        return chain

    async def act(self, thought_result: Dict[str, Any]) -> Any:
        """
        Execute planning - create actionable plan.

        Args:
            thought_result: Result from think()

        Returns:
            Executable plan
        """
        subtasks = thought_result["subtasks"]
        strategy = thought_result["strategy"]
        complexity = thought_result["complexity"]

        plan = {
            "task": thought_result["task"],
            "complexity": complexity,
            "strategy": strategy,
            "subtasks": subtasks,
            "execution_order": self._determine_execution_order(subtasks),
            "estimated_duration": thought_result["estimated_duration"],
            "risks": thought_result["risks"],
            "contingencies": self._create_contingencies(thought_result["risks"]),
        }

        self.current_plan = plan
        return plan

    def _determine_execution_order(self, subtasks: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Determine execution order (grouped by parallelizable tasks).

        Returns:
            List of task ID groups that can be executed in parallel
        """
        # Simple implementation: tasks without dependencies run first
        # then tasks whose dependencies are satisfied
        ordered_groups = []

        remaining = {t["task_id"]: t for t in subtasks}
        completed = set()

        while remaining:
            # Find tasks whose dependencies are all in completed
            ready = [
                task_id for task_id, task in remaining.items()
                if all(dep in completed for dep in task.get("dependencies", []))
            ]

            if not ready:
                # Circular dependency or error - just take any remaining
                ready = list(remaining.keys())[:1]

            ordered_groups.append(ready)

            # Move ready tasks to completed
            for task_id in ready:
                del remaining[task_id]
                completed.add(task_id)

        return ordered_groups

    def _create_contingencies(self, risks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Create contingency plans for identified risks."""
        contingencies = []

        for risk in risks:
            risk_type = risk.get("type")
            if risk_type == "missing_dependency":
                contingencies.append({
                    "risk": risk_type,
                    "action": f"Skip task {risk['task']} or create dummy result",
                })
            elif risk_type == "long_chain":
                contingencies.append({
                    "risk": risk_type,
                    "action": "Enable early results streaming",
                })

        if not contingencies:
            contingencies.append({
                "risk": "general_failure",
                "action": "Retry with simplified approach",
            })

        return contingencies

    async def review(self, results: Dict[str, Any],
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and potentially revise plan based on execution results.

        Args:
            results: Execution results
            context: Execution context

        Returns:
            Review feedback and revised plan if needed
        """
        quality_score = 0.9  # Default high score for planning

        suggestions = []

        # Check if plan was followed
        if self.current_plan:
            planned_tasks = len(self.current_plan.get("subtasks", []))
            completed_tasks = results.get("successful_tasks", 0)

            if completed_tasks < planned_tasks * 0.8:
                quality_score = 0.6
                suggestions.append("Consider simplifying remaining tasks")

        return {
            "quality_score": quality_score,
            "feedback": "Plan review complete",
            "suggestions": suggestions,
            "revision_needed": quality_score < 0.7,
        }

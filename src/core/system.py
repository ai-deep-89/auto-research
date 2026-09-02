"""Main AutoResearch System orchestration."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
import time
import asyncio

from src.core.message import Message, MessageQueue, MessageType
from src.core.task_planner import TaskPlanner, Task, TaskStatus, TaskPriority
from src.core.multi_agent import MultiAgentCrew, CollaborationMode


@dataclass
class ResearchResult:
    """Final result from a research task."""
    task: str
    success: bool
    output: Dict[str, Any]
    duration: float
    iterations: int
    plan_summary: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task": self.task,
            "success": self.success,
            "output": self.output,
            "duration": self.duration,
            "iterations": self.iterations,
            "plan_summary": self.plan_summary,
            "metadata": self.metadata,
        }


class AutoResearchSystem:
    """
    Main orchestration system for autonomous research.

    Coordinates:
    - Task planning and decomposition
    - Multi-agent collaboration
    - Result synthesis
    - Evolution (optional)

    Features:
    - Flexible agent configuration
    - Multiple collaboration modes
    - Built-in evaluation
    - Self-evolution support
    """

    def __init__(
        self,
        researcher: Optional[Any] = None,
        planner: Optional[Any] = None,
        executor: Optional[Any] = None,
        reviewer: Optional[Any] = None,
        evolution_enabled: bool = False,
        default_mode: CollaborationMode = CollaborationMode.PARALLEL,
    ):
        """
        Initialize AutoResearch System.

        Args:
            researcher: Researcher agent for information gathering
            planner: Planner agent for task decomposition
            executor: Executor agent for action execution
            reviewer: Reviewer agent for quality assurance
            evolution_enabled: Enable self-evolution features
            default_mode: Default collaboration mode
        """
        # Initialize agents
        self.agents = {}
        if researcher:
            self.agents["researcher"] = researcher
        if planner:
            self.agents["planner"] = planner
        if executor:
            self.agents["executor"] = executor
        if reviewer:
            self.agents["reviewer"] = reviewer

        # If no agents provided, use default implementations
        if not self.agents:
            self._initialize_default_agents()

        # System components
        self.message_queue = MessageQueue()
        self.task_planner = TaskPlanner()

        # Multi-agent crew
        self.crew = MultiAgentCrew(
            agents=list(self.agents.values()),
            mode=default_mode,
            message_queue=self.message_queue,
        )

        # Evolution support
        self.evolution_enabled = evolution_enabled
        self.evolution_engine = None
        if evolution_enabled:
            from src.evolution.evolution_engine import EvolutionEngine
            self.evolution_engine = EvolutionEngine()

        # State
        self.current_task: Optional[str] = None
        self.execution_history: List[ResearchResult] = []
        self._callbacks: Dict[str, List[Callable]] = {
            "on_task_start": [],
            "on_task_complete": [],
            "on_agent_message": [],
        }

    def _initialize_default_agents(self) -> None:
        """Initialize with default agent implementations."""
        from src.agents.researcher import ResearcherAgent
        from src.agents.planner import PlannerAgent
        from src.agents.executor import ExecutorAgent
        from src.agents.reviewer import ReviewerAgent

        self.agents = {
            "researcher": ResearcherAgent(name="researcher"),
            "planner": PlannerAgent(name="planner"),
            "executor": ExecutorAgent(name="executor"),
            "reviewer": ReviewerAgent(name="reviewer"),
        }

    def register_callback(self, event: str, callback: Callable) -> None:
        """Register callback for system events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _trigger_callback(self, event: str, *args, **kwargs) -> None:
        """Trigger registered callbacks."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                pass

    async def run_async(
        self,
        task: str,
        max_iterations: int = 5,
        context: Optional[Dict[str, Any]] = None,
    ) -> ResearchResult:
        """
        Execute a research task asynchronously.

        Args:
            task: Research task description
            max_iterations: Maximum planning/execution cycles
            context: Initial context for the task

        Returns:
            ResearchResult with execution details
        """
        start_time = time.time()
        self.current_task = task
        self.task_planner.reset()

        self._trigger_callback("on_task_start", task)

        # Decompose task
        subtasks = self.task_planner.decompose(task)
        iteration = 0
        final_output = {}

        while iteration < max_iterations:
            iteration += 1

            # Execute with multi-agent crew
            result = await self.crew.run_async(task, context)

            # Review result
            if "reviewer" in self.agents:
                review_result = await self.agents["reviewer"].review(
                    result, context or {}
                )
                result["review"] = review_result

                # Check if quality threshold met
                quality = review_result.get("quality_score", 0)
                if quality >= 0.8:
                    final_output = result
                    break

                # Feedback for improvement
                if self.evolution_enabled and self.evolution_engine:
                    self.evolution_engine.evolve(
                        agent=self.agents.get("executor"),
                        feedback=review_result,
                    )
            else:
                final_output = result

            # If all tasks completed successfully, break
            if result.get("success") and result.get("successful_tasks", 0) > 0:
                break

            iteration += 1

        duration = time.time() - start_time

        research_result = ResearchResult(
            task=task,
            success=final_output.get("success", False),
            output=final_output,
            duration=duration,
            iterations=iteration,
            plan_summary=self.task_planner.get_plan_summary(),
            metadata={
                "max_iterations": max_iterations,
                "evolution_enabled": self.evolution_enabled,
            },
        )

        self.execution_history.append(research_result)
        self._trigger_callback("on_task_complete", research_result)

        return research_result

    def run(
        self,
        task: str,
        max_iterations: int = 5,
        context: Optional[Dict[str, Any]] = None,
    ) -> ResearchResult:
        """
        Execute a research task (synchronous wrapper).

        Args:
            task: Research task description
            max_iterations: Maximum planning/execution cycles
            context: Initial context

        Returns:
            ResearchResult with execution details
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return asyncio.run(self.run_async(task, max_iterations, context))
            return loop.run_until_complete(self.run_async(task, max_iterations, context))
        except RuntimeError:
            return asyncio.run(self.run_async(task, max_iterations, context))

    def add_agent(self, agent: Any) -> None:
        """Add an agent to the system."""
        self.agents[agent.name] = agent
        self.crew.add_agent(agent)

    def remove_agent(self, name: str) -> None:
        """Remove an agent from the system."""
        if name in self.agents:
            del self.agents[name]
            self.crew.remove_agent(name)

    def get_agent(self, name: str) -> Optional[Any]:
        """Get agent by name."""
        return self.agents.get(name)

    def set_collaboration_mode(self, mode: CollaborationMode) -> None:
        """Change the multi-agent collaboration mode."""
        self.crew.set_mode(mode)

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about execution history."""
        if not self.execution_history:
            return {
                "total_tasks": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "avg_iterations": 0.0,
            }

        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.success)

        return {
            "total_tasks": total,
            "successful_tasks": successful,
            "failed_tasks": total - successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "avg_duration": sum(r.duration for r in self.execution_history) / total,
            "avg_iterations": sum(r.iterations for r in self.execution_history) / total,
            "total_duration": sum(r.duration for r in self.execution_history),
        }

    def get_recent_results(self, n: int = 10) -> List[ResearchResult]:
        """Get n most recent execution results."""
        return self.execution_history[-n:]

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()

    async def agent_message(self, sender: str, receiver: str,
                           content: Dict[str, Any]) -> Optional[Message]:
        """
        Send a message between agents.

        Args:
            sender: Sender agent name
            receiver: Receiver agent name
            content: Message content

        Returns:
            Response message if any
        """
        message = Message(
            sender=sender,
            receiver=receiver,
            content=content,
            msg_type=MessageType.REQUEST,
        )
        self.message_queue.put(message)

        # Wait for response
        response = self.message_queue.get(receiver, blocking=True, timeout=30)
        return response

    def __repr__(self) -> str:
        return (
            f"AutoResearchSystem("
            f"agents={list(self.agents.keys())}, "
            f"evolution={'enabled' if self.evolution_enabled else 'disabled'}, "
            f"mode={self.crew.mode.value})"
        )

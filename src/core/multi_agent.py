"""Multi-agent orchestration for collaborative task execution."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import time
import asyncio

from src.core.message import Message, MessageQueue, MessageType
from src.core.task_planner import Task, TaskPlanner, TaskStatus


class CollaborationMode(Enum):
    """Multi-agent collaboration modes."""
    SEQUENTIAL = "sequential"       # One agent after another
    PARALLEL = "parallel"          # Multiple agents simultaneously
    HIERARCHICAL = "hierarchical"  # Manager-worker structure
    PEER_TO_PEER = "peer_to_peer"  # Agents negotiate directly


@dataclass
class AgentResult:
    """Result from an agent's execution."""
    agent_name: str
    task_id: str
    success: bool
    output: Any
    duration: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultiAgentCrew:
    """
    Orchestrates multiple agents to work together on complex tasks.

    Supports different collaboration modes:
    - Sequential: Agents execute one after another
    - Parallel: Independent agents work simultaneously
    - Hierarchical: Manager coordinates workers
    - Peer-to-Peer: Agents negotiate and collaborate directly

    Features:
    - Dynamic task assignment
    - Inter-agent communication via message passing
    - Shared knowledge base
    - Consensus building
    - Error recovery
    """

    def __init__(
        self,
        agents: List[Any],
        mode: CollaborationMode = CollaborationMode.PARALLEL,
        message_queue: Optional[MessageQueue] = None,
    ):
        """
        Initialize multi-agent crew.

        Args:
            agents: List of agent instances
            mode: Collaboration mode
            message_queue: Shared message queue for communication
        """
        self.agents = {agent.name: agent for agent in agents}
        self.mode = mode
        self.message_queue = message_queue or MessageQueue()
        self.shared_context: Dict[str, Any] = {}
        self.task_planner = TaskPlanner()
        self.execution_log: List[AgentResult] = []
        self._consensus_callbacks: List[Callable] = []

    @property
    def agent_names(self) -> List[str]:
        """Get list of agent names."""
        return list(self.agents.keys())

    def add_agent(self, agent: Any) -> None:
        """Add an agent to the crew."""
        self.agents[agent.name] = agent

    def remove_agent(self, name: str) -> None:
        """Remove an agent from the crew."""
        if name in self.agents:
            del self.agents[name]

    def set_mode(self, mode: CollaborationMode) -> None:
        """Change collaboration mode."""
        self.mode = mode

    async def run_async(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute task with current collaboration mode.

        Args:
            task: Task description
            context: Initial context shared among agents

        Returns:
            Combined results from all agents
        """
        self.shared_context = context or {}
        self.shared_context["original_task"] = task

        # Decompose task into subtasks
        subtasks = self.task_planner.decompose(task)
        self.task_planner.reset()

        if self.mode == CollaborationMode.SEQUENTIAL:
            return await self._run_sequential(subtasks)
        elif self.mode == CollaborationMode.PARALLEL:
            return await self._run_parallel(subtasks)
        elif self.mode == CollaborationMode.HIERARCHICAL:
            return await self._run_hierarchical(subtasks)
        elif self.mode == CollaborationMode.PEER_TO_PEER:
            return await self._run_peer_to_peer(subtasks)
        else:
            return await self._run_parallel(subtasks)

    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Synchronous wrapper for run_async.

        Args:
            task: Task description
            context: Initial context

        Returns:
            Combined results
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a new loop if we're in an async context
                return asyncio.run(self.run_async(task, context))
            return loop.run_until_complete(self.run_async(task, context))
        except RuntimeError:
            return asyncio.run(self.run_async(task, context))

    async def _run_sequential(self, subtasks: List[Task]) -> Dict[str, Any]:
        """Execute tasks sequentially, one agent after another."""
        results = {}
        for task in subtasks:
            task.mark_started()
            start_time = time.time()

            # Find appropriate agent for task type
            agent = self._select_agent_for_task(task)

            try:
                result = await agent.execute(task.description, context=self.shared_context)
                task.mark_completed(result)
                results[task.task_id] = AgentResult(
                    agent_name=agent.name,
                    task_id=task.task_id,
                    success=True,
                    output=result,
                    duration=time.time() - start_time,
                )
                # Update shared context
                self.shared_context[f"result_{task.task_id}"] = result
            except Exception as e:
                task.mark_failed(str(e))
                results[task.task_id] = AgentResult(
                    agent_name=agent.name,
                    task_id=task.task_id,
                    success=False,
                    output=None,
                    duration=time.time() - start_time,
                    metadata={"error": str(e)},
                )

            self.execution_log.append(results[task.task_id])

        return self._aggregate_results(results)

    async def _run_parallel(self, subtasks: List[Task]) -> Dict[str, Any]:
        """Execute independent tasks in parallel."""
        # Group tasks by agent capability
        task_groups = self._group_tasks_by_capability(subtasks)

        async def execute_group(tasks: List[Task], agent_name: str) -> Dict[str, AgentResult]:
            results = {}
            agent = self.agents[agent_name]
            for task in tasks:
                task.mark_started()
                start_time = time.time()
                try:
                    result = await agent.execute(task.description, context=self.shared_context)
                    task.mark_completed(result)
                    results[task.task_id] = AgentResult(
                        agent_name=agent_name,
                        task_id=task.task_id,
                        success=True,
                        output=result,
                        duration=time.time() - start_time,
                    )
                except Exception as e:
                    task.mark_failed(str(e))
                    results[task.task_id] = AgentResult(
                        agent_name=agent_name,
                        task_id=task.task_id,
                        success=False,
                        output=None,
                        duration=time.time() - start_time,
                        metadata={"error": str(e)},
                    )
            return results

        # Execute all groups concurrently
        coroutines = [
            execute_group(tasks, agent_name)
            for agent_name, tasks in task_groups.items()
            if tasks
        ]

        group_results = await asyncio.gather(*coroutines, return_exceptions=True)

        all_results = {}
        for group_result in group_results:
            if isinstance(group_result, dict):
                all_results.update(group_result)
                for result in group_result.values():
                    self.execution_log.append(result)

        return self._aggregate_results(all_results)

    async def _run_hierarchical(self, subtasks: List[Task]) -> Dict[str, Any]:
        """Hierarchical execution with manager coordinating workers."""
        # Find manager agent (typically planner)
        manager = self.agents.get("planner") or self.agents.get(list(self.agents.keys())[0])
        worker_names = [name for name in self.agents.keys() if name != manager.name]

        results = {}
        all_completed = False

        while not all_completed:
            # Manager decides what to do next
            executable = self.task_planner.get_executable_tasks()

            if not executable:
                all_completed = True
                break

            # Assign and execute tasks
            for task in executable[:3]:  # Max 3 concurrent
                worker_name = self._select_worker(worker_names, task, results)
                if worker_name:
                    worker = self.agents[worker_name]
                    task.mark_started()
                    start_time = time.time()

                    try:
                        result = await worker.execute(task.description, context=self.shared_context)
                        task.mark_completed(result)
                        agent_result = AgentResult(
                            agent_name=worker_name,
                            task_id=task.task_id,
                            success=True,
                            output=result,
                            duration=time.time() - start_time,
                        )
                        results[task.task_id] = agent_result
                        self.execution_log.append(agent_result)
                    except Exception as e:
                        task.mark_failed(str(e))
                        results[task.task_id] = AgentResult(
                            agent_name=worker_name,
                            task_id=task.task_id,
                            success=False,
                            output=None,
                            duration=time.time() - start_time,
                            metadata={"error": str(e)},
                        )

            # Manager reviews and synthesizes
            if results:
                try:
                    synthesis = await manager.review(results, self.shared_context)
                    self.shared_context["synthesis"] = synthesis
                except Exception:
                    pass

        return self._aggregate_results(results)

    async def _run_peer_to_peer(self, subtasks: List[Task]) -> Dict[str, Any]:
        """Peer-to-peer collaboration where agents negotiate."""
        # Each agent works on subtask and communicates findings
        for task in subtasks:
            task.mark_started()
            agent = self._select_agent_for_task(task)
            start_time = time.time()

            try:
                result = await agent.execute(task.description, context=self.shared_context)
                task.mark_completed(result)

                # Broadcast to other agents
                self._broadcast_findings(agent.name, task.task_id, result)

                # Other agents can provide feedback
                await self._collect_feedback(agent.name, task.task_id)

            except Exception as e:
                task.mark_failed(str(e))

        return self.shared_context.get("final_output", {})

    def _select_agent_for_task(self, task: Task) -> Any:
        """Select the best agent for a task based on task type."""
        agent_map = {
            "research": "researcher",
            "code": "executor",
            "analysis": "researcher",
            "writing": "researcher",
            "review": "reviewer",
        }
        preferred = agent_map.get(task.task_type, list(self.agents.keys())[0])
        return self.agents.get(preferred, list(self.agents.values())[0])

    def _group_tasks_by_capability(self, tasks: List[Task]) -> Dict[str, List[Task]]:
        """Group tasks by agent capability."""
        groups = {}
        for task in tasks:
            agent_name = self._select_agent_for_task(task).name
            if agent_name not in groups:
                groups[agent_name] = []
            groups[agent_name].append(task)
        return groups

    def _select_worker(self, worker_names: List[str], task: Task,
                      results: Dict[str, AgentResult]) -> Optional[str]:
        """Select best worker for a task (load balancing + capability)."""
        available = []
        for name in worker_names:
            # Count current workload
            workload = sum(1 for r in results.values() if r.agent_name == name and r.success)
            available.append((name, workload))

        if not available:
            return None

        # Return least loaded agent
        available.sort(key=lambda x: x[1])
        return available[0][0]

    def _broadcast_findings(self, sender: str, task_id: str, findings: Any) -> None:
        """Broadcast agent findings to all other agents."""
        message = Message(
            sender=sender,
            receiver="ALL",
            content={
                "type": "findings",
                "task_id": task_id,
                "findings": findings,
            },
            msg_type=MessageType.RESPONSE,
        )
        self.message_queue.put(message)

    async def _collect_feedback(self, agent_name: str, task_id: str) -> None:
        """Collect feedback from other agents on findings."""
        feedback_messages = self.message_queue.get_all_for(agent_name)
        for msg in feedback_messages:
            if msg.content.get("type") == "feedback":
                # Process feedback
                self.shared_context[f"feedback_{task_id}"] = msg.content

    def _aggregate_results(self, results: Dict[str, AgentResult]) -> Dict[str, Any]:
        """Aggregate results from all agents."""
        successful = [r for r in results.values() if r.success]
        failed = [r for r in results.values() if not r.success]

        return {
            "success": len(successful) > 0,
            "total_tasks": len(results),
            "successful_tasks": len(successful),
            "failed_tasks": len(failed),
            "total_duration": sum(r.duration for r in results.values()),
            "outputs": {task_id: r.output for task_id, r in results.items()},
            "execution_log": [
                {
                    "agent": r.agent_name,
                    "task_id": r.task_id,
                    "success": r.success,
                    "duration": r.duration,
                }
                for r in results.values()
            ],
        }

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of crew execution."""
        return {
            "total_executions": len(self.execution_log),
            "successful": sum(1 for r in self.execution_log if r.success),
            "failed": sum(1 for r in self.execution_log if not r.success),
            "by_agent": self._count_by_agent(),
            "total_duration": sum(r.duration for r in self.execution_log),
        }

    def _count_by_agent(self) -> Dict[str, int]:
        """Count executions per agent."""
        counts = {}
        for result in self.execution_log:
            counts[result.agent_name] = counts.get(result.agent_name, 0) + 1
        return counts

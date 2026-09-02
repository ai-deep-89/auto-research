"""Task planning and decomposition for complex research tasks."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
import time
import uuid


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Task:
    """
    Represents a single executable task.

    Attributes:
        task_id: Unique task identifier
        description: Human-readable task description
        task_type: Category of task (research, code, analyze, etc.)
        status: Current execution status
        priority: Task priority
        dependencies: List of task IDs that must complete first
        assigned_agent: Agent currently assigned to this task
        result: Task execution result (if completed)
        error: Error message (if failed)
        created_at: Task creation timestamp
        started_at: Task start timestamp
        completed_at: Task completion timestamp
        metadata: Additional task-specific data
    """
    description: str
    task_type: str = "general"
    task_id: str = field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.started_at is None and self.status == TaskStatus.IN_PROGRESS:
            self.started_at = time.time()

    def mark_started(self) -> None:
        """Mark task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = time.time()

    def mark_completed(self, result: Any = None) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = time.time()
        if result is not None:
            self.result = result

    def mark_failed(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = time.time()
        self.error = error

    @property
    def duration(self) -> Optional[float]:
        """Get task execution duration in seconds."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    @property
    def is_blocked(self) -> bool:
        """Check if task is blocked by dependencies."""
        return self.status == TaskStatus.BLOCKED

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "task_type": self.task_type,
            "status": self.status.value,
            "priority": self.priority.value,
            "dependencies": self.dependencies,
            "assigned_agent": self.assigned_agent,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": self.duration,
            "metadata": self.metadata,
        }


class TaskPlanner:
    """
    Plans and decomposes complex research tasks into executable subtasks.

    Uses hierarchical task decomposition:
    1. Parse high-level research goal
    2. Identify required capabilities
    3. Decompose into ordered subtasks
    4. Build dependency graph
    5. Assign priorities
    """

    TASK_TYPES = {
        "research": ["web_search", "paper_analysis", "knowledge_retrieval"],
        "code": ["code_generation", "code_execution", "debugging"],
        "analysis": ["data_analysis", "statistical_analysis", "visualization"],
        "writing": ["drafting", "editing", "citation"],
        "review": ["validation", "feedback", "synthesis"],
    }

    def __init__(self, llm: Optional[Any] = None):
        """
        Initialize task planner.

        Args:
            llm: Optional LLM for intelligent task decomposition
        """
        self.llm = llm
        self.tasks: Dict[str, Task] = {}

    def create_task(self, description: str, task_type: str = "general",
                   priority: TaskPriority = TaskPriority.NORMAL,
                   dependencies: List[str] = None,
                   metadata: Dict[str, Any] = None) -> Task:
        """
        Create a new task.

        Args:
            description: Task description
            task_type: Type of task
            priority: Task priority
            dependencies: List of task IDs this task depends on
            metadata: Additional task metadata

        Returns:
            Created Task object
        """
        task = Task(
            description=description,
            task_type=task_type,
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )
        self.tasks[task.task_id] = task
        return task

    def decompose(self, query: str, llm_enabled: bool = True) -> List[Task]:
        """
        Decompose a complex query into subtasks.

        Args:
            query: High-level research query
            llm_enabled: Use LLM for intelligent decomposition

        Returns:
            List of decomposed tasks
        """
        if llm_enabled and self.llm:
            return self._llm_decompose(query)
        return self._rule_based_decompose(query)

    def _rule_based_decompose(self, query: str) -> List[Task]:
        """
        Rule-based task decomposition (fallback when no LLM).

        Analyzes query keywords to identify required task types
        and creates appropriate subtasks.
        """
        query_lower = query.lower()
        tasks = []

        # Research tasks
        if any(kw in query_lower for kw in ["research", "study", "investigate", "find"]):
            research_task = self.create_task(
                description=f"Research information about: {query}",
                task_type="research",
                priority=TaskPriority.HIGH,
            )
            tasks.append(research_task)

        # Code tasks
        if any(kw in query_lower for kw in ["code", "implement", "program", "script"]):
            code_task = self.create_task(
                description=f"Generate/execute code for: {query}",
                task_type="code",
                priority=TaskPriority.NORMAL,
            )
            tasks.append(code_task)

        # Analysis tasks
        if any(kw in query_lower for kw in ["analyze", "compare", "evaluate", "assess"]):
            analysis_task = self.create_task(
                description=f"Analyze and compare: {query}",
                task_type="analysis",
                priority=TaskPriority.NORMAL,
            )
            tasks.append(analysis_task)

        # Default research + review if no specific type detected
        if not tasks:
            tasks.append(self.create_task(
                description=f"Research: {query}",
                task_type="research",
                priority=TaskPriority.HIGH,
            ))
            tasks.append(self.create_task(
                description=f"Review and validate findings for: {query}",
                task_type="review",
                priority=TaskPriority.NORMAL,
                dependencies=[tasks[0].task_id] if tasks else [],
            ))

        return tasks

    def _llm_decompose(self, query: str) -> List[Task]:
        """
        LLM-powered task decomposition.

        Uses the LLM to intelligently analyze the query and
        create appropriate subtasks with proper dependencies.
        """
        # Simulated LLM decomposition prompt
        prompt = f"""Decompose the following research query into subtasks.
For each subtask, specify:
1. Description
2. Task type (research, code, analysis, writing, review)
3. Priority (0=low, 1=normal, 2=high, 3=critical)

Query: {query}

Output format:
- [TYPE] Priority: N - Description"""

        # In production, this would call the LLM
        # For now, return rule-based decomposition
        return self._rule_based_decompose(query)

    def get_executable_tasks(self) -> List[Task]:
        """
        Get all tasks that are ready to execute.

        A task is executable if:
        1. Status is PENDING
        2. All dependencies are COMPLETED
        """
        executable = []
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            # Check dependencies
            deps_completed = all(
                self.tasks[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
                if dep_id in self.tasks
            )
            if deps_completed:
                executable.append(task)
        return sorted(executable, key=lambda t: t.priority.value, reverse=True)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus,
                          result: Any = None, error: str = None) -> None:
        """Update task status and result."""
        task = self.tasks.get(task_id)
        if task:
            if status == TaskStatus.IN_PROGRESS:
                task.mark_started()
            elif status == TaskStatus.COMPLETED:
                task.mark_completed(result)
            elif status == TaskStatus.FAILED:
                task.mark_failed(error or "Unknown error")

    def get_plan_summary(self) -> Dict[str, Any]:
        """Get summary of current task plan."""
        summary = {
            "total": len(self.tasks),
            "by_status": {},
            "by_type": {},
            "total_duration": 0,
        }
        for task in self.tasks.values():
            status = task.status.value
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
            summary["by_type"][task.task_type] = summary["by_type"].get(task.task_type, 0) + 1
            if task.duration:
                summary["total_duration"] += task.duration
        return summary

    def reset(self) -> None:
        """Reset planner state."""
        self.tasks.clear()

"""Benchmark tasks for agent evaluation."""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time


class TaskCategory(Enum):
    """Categories of benchmark tasks."""
    RESEARCH = "research"
    CODE_GENERATION = "code_generation"
    PLANNING = "planning"
    COLLABORATION = "collaboration"
    REASONING = "reasoning"


@dataclass
class BenchmarkTask:
    """
    Definition of a benchmark task.

    Attributes:
        task_id: Unique identifier
        name: Human-readable name
        description: Task description
        category: Task category
        difficulty: Difficulty level (1-5)
        expected_output: Description of expected output
        success_criteria: Criteria for task success
        timeout: Max execution time in seconds
    """
    task_id: str
    name: str
    description: str
    category: TaskCategory
    difficulty: int = 3
    expected_output: Optional[str] = None
    success_criteria: Dict[str, Any] = None
    timeout: int = 300

    def __post_init__(self):
        if self.success_criteria is None:
            self.success_criteria = {"min_quality": 0.7}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "difficulty": self.difficulty,
            "expected_output": self.expected_output,
            "success_criteria": self.success_criteria,
            "timeout": self.timeout,
        }


class Benchmark:
    """
    Benchmark task suite for agent evaluation.

    Includes predefined tasks across multiple categories.
    """

    def __init__(self):
        self.tasks: List[BenchmarkTask] = []
        self._load_default_tasks()

    def _load_default_tasks(self) -> None:
        """Load default benchmark tasks."""
        self.tasks = [
            # Research tasks
            BenchmarkTask(
                task_id="res_001",
                name="Research Query Answering",
                description="Research and summarize the latest advances in LLM agent self-evolution",
                category=TaskCategory.RESEARCH,
                difficulty=3,
                success_criteria={"has_citations": True, "min_sources": 3},
            ),
            BenchmarkTask(
                task_id="res_002",
                name="Comparative Analysis",
                description="Compare multi-agent frameworks: CrewAI vs LangChain vs AutoGen",
                category=TaskCategory.RESEARCH,
                difficulty=3,
                success_criteria={"has_comparison_table": True, "min_frameworks": 3},
            ),
            BenchmarkTask(
                task_id="res_003",
                name="Technical Survey",
                description="Survey papers on autonomous research agents from arXiv",
                category=TaskCategory.RESEARCH,
                difficulty=4,
                success_criteria={"min_papers": 5, "has_summary": True},
            ),

            # Code generation tasks
            BenchmarkTask(
                task_id="code_001",
                name="Python Function",
                description="Write a Python function to calculate Fibonacci numbers with memoization",
                category=TaskCategory.CODE_GENERATION,
                difficulty=2,
                success_criteria={"runs_successfully": True, "has_tests": True},
            ),
            BenchmarkTask(
                task_id="code_002",
                name="Data Processing Pipeline",
                description="Write a data processing pipeline with error handling",
                category=TaskCategory.CODE_GENERATION,
                difficulty=4,
                success_criteria={"handles_exceptions": True, "is_modular": True},
            ),

            # Planning tasks
            BenchmarkTask(
                task_id="plan_001",
                name="Multi-step Planning",
                description="Plan a week-long research project on multi-agent systems",
                category=TaskCategory.PLANNING,
                difficulty=4,
                success_criteria={"has_timeline": True, "has_milestones": True},
            ),
            BenchmarkTask(
                task_id="plan_002",
                name="Task Decomposition",
                description="Decompose 'build a chatbot with memory' into actionable tasks",
                category=TaskCategory.PLANNING,
                difficulty=3,
                success_criteria={"min_subtasks": 5, "has_dependencies": True},
            ),

            # Collaboration tasks
            BenchmarkTask(
                task_id="collab_001",
                name="Agent Coordination",
                description="Coordinate researcher, planner, and executor agents to complete a research task",
                category=TaskCategory.COLLABORATION,
                difficulty=4,
                success_criteria={"all_agents_active": True, "achieves_consensus": True},
            ),
            BenchmarkTask(
                task_id="collab_002",
                name="Feedback Loop",
                description="Demonstrate agent learning through feedback iteration",
                category=TaskCategory.COLLABORATION,
                difficulty=5,
                success_criteria={"improvement_demonstrated": True},
            ),

            # Reasoning tasks
            BenchmarkTask(
                task_id="reason_001",
                name="Chain of Thought",
                description="Solve a multi-step reasoning problem showing work",
                category=TaskCategory.REASONING,
                difficulty=3,
                success_criteria={"shows_reasoning": True, "correct_answer": True},
            ),
        ]

    def get_tasks_by_category(self, category: TaskCategory) -> List[BenchmarkTask]:
        """Get tasks filtered by category."""
        return [t for t in self.tasks if t.category == category]

    def get_tasks_by_difficulty(self, difficulty: int) -> List[BenchmarkTask]:
        """Get tasks filtered by difficulty level."""
        return [t for t in self.tasks if t.difficulty == difficulty]

    def get_task(self, task_id: str) -> Optional[BenchmarkTask]:
        """Get a specific task by ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def add_task(self, task: BenchmarkTask) -> None:
        """Add a custom benchmark task."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID."""
        for i, task in enumerate(self.tasks):
            if task.task_id == task_id:
                self.tasks.pop(i)
                return True
        return False

    def get_benchmark_summary(self) -> Dict[str, Any]:
        """Get summary of benchmark suite."""
        categories = {}
        difficulties = {}

        for task in self.tasks:
            cat = task.category.value
            categories[cat] = categories.get(cat, 0) + 1

            diff = task.difficulty
            difficulties[diff] = difficulties.get(diff, 0) + 1

        return {
            "total_tasks": len(self.tasks),
            "by_category": categories,
            "by_difficulty": difficulties,
        }


class BenchmarkRunner:
    """Runner for executing benchmark tasks."""

    def __init__(self, benchmark: Benchmark):
        self.benchmark = benchmark

    def run_task(
        self,
        agent: Any,
        task: BenchmarkTask,
        executor_func: Callable
    ) -> Dict[str, Any]:
        """
        Run a single benchmark task.

        Args:
            agent: Agent to evaluate
            task: BenchmarkTask to execute
            executor_func: Function to execute the task

        Returns:
            Dict with execution results and evaluation
        """
        start_time = time.time()

        try:
            # Execute with timeout
            result = executor_func(agent, task)

            # Evaluate success
            success = self._evaluate_success(result, task)

            execution_time = time.time() - start_time

            return {
                "task_id": task.task_id,
                "success": success,
                "result": result,
                "execution_time": execution_time,
                "error": None,
            }

        except Exception as e:
            return {
                "task_id": task.task_id,
                "success": False,
                "result": None,
                "execution_time": time.time() - start_time,
                "error": str(e),
            }

    def _evaluate_success(self, result: Dict[str, Any],
                         task: BenchmarkTask) -> bool:
        """Evaluate if task was successful based on criteria."""
        criteria = task.success_criteria

        if not result:
            return False

        # Check each criterion
        for key, expected in criteria.items():
            actual = result.get(key)

            if expected is True and not actual:
                return False
            elif expected is False and actual:
                return False
            elif isinstance(expected, (int, float)):
                if actual < expected:
                    return False

        return True

    def run_full_benchmark(
        self,
        agent: Any,
        executor_func: Callable,
        categories: Optional[List[TaskCategory]] = None
    ) -> Dict[str, Any]:
        """
        Run full benchmark suite.

        Args:
            agent: Agent to evaluate
            executor_func: Function to execute tasks
            categories: Optional filter for task categories

        Returns:
            Dict with all results and summary
        """
        tasks = self.benchmark.tasks
        if categories:
            tasks = [t for t in tasks if t.category in categories]

        results = []
        for task in tasks:
            result = self.run_task(agent, task, executor_func)
            results.append(result)

        # Calculate summary
        successful = sum(1 for r in results if r["success"])
        total_time = sum(r["execution_time"] for r in results)

        return {
            "total_tasks": len(tasks),
            "successful": successful,
            "failed": len(tasks) - successful,
            "success_rate": successful / len(tasks) if tasks else 0,
            "total_time": total_time,
            "results": results,
        }

"""Main evaluation orchestrator."""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import time

from src.evaluation.metrics import MetricsCalculator, MetricScore


@dataclass
class EvaluationResult:
    """Result of a single evaluation run."""
    timestamp: float
    task_id: str
    agent_name: str
    composite_score: float
    grade: str
    metric_scores: List[Dict[str, Any]]
    task_results: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    agent_interactions: List[Dict[str, Any]]
    responses: List[Dict[str, Any]]
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "composite_score": self.composite_score,
            "grade": self.grade,
            "metric_scores": self.metric_scores,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
        }


class Evaluator:
    """
    Main evaluation orchestrator for AutoResearch agents.

    Features:
    - Multi-dimensional metric evaluation
    - Benchmark task execution
    - Historical tracking
    - Comparative analysis
    - Automated reporting
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Evaluator.

        Args:
            config: Evaluation configuration
        """
        self.config = config or {}
        self.metrics_calculator = MetricsCalculator()
        self.evaluation_history: List[EvaluationResult] = []
        self.baseline_metrics: Optional[Dict[str, float]] = None

    def set_baseline(self, metrics: Dict[str, float]) -> None:
        """Set baseline metrics for evolution comparison."""
        self.baseline_metrics = metrics.copy()

    def evaluate_agent(
        self,
        agent: Any,
        benchmark_tasks: List[Dict[str, Any]],
        task_executor: Callable
    ) -> EvaluationResult:
        """
        Evaluate an agent on benchmark tasks.

        Args:
            agent: Agent to evaluate
            benchmark_tasks: List of benchmark task definitions
            task_executor: Function to execute a task and return results

        Returns:
            EvaluationResult with detailed metrics
        """
        start_time = time.time()

        task_results = []
        tool_calls = []
        agent_interactions = []
        responses = []

        for task_def in benchmark_tasks:
            task_id = task_def.get("task_id", f"task_{len(task_results)}")

            try:
                # Execute task
                result = task_executor(agent, task_def)

                task_results.append({
                    "task_id": task_id,
                    "success": result.get("success", False),
                    "output": result.get("output"),
                })

                # Collect tool calls
                if "tool_calls" in result:
                    for call in result["tool_calls"]:
                        call["task_id"] = task_id
                        tool_calls.append(call)

                # Collect interactions
                if "interactions" in result:
                    agent_interactions.extend(result["interactions"])

                # Collect responses
                responses.append({
                    "task_id": task_id,
                    "has_citations": result.get("has_citations", False),
                    "has_synthesis": result.get("has_synthesis", False),
                    "well_structured": result.get("well_structured", False),
                })

            except Exception as e:
                task_results.append({
                    "task_id": task_id,
                    "success": False,
                    "error": str(e),
                })

        # Compute metrics
        metrics_result = self.metrics_calculator.compute_all_metrics(
            task_results=task_results,
            tool_calls=tool_calls,
            agent_interactions=agent_interactions,
            responses=responses,
            baseline_metrics=self.baseline_metrics,
        )

        execution_time = time.time() - start_time

        # Create evaluation result
        eval_result = EvaluationResult(
            timestamp=time.time(),
            task_id=benchmark_tasks[0].get("task_id", "eval_1") if benchmark_tasks else "unknown",
            agent_name=getattr(agent, "name", "unknown"),
            composite_score=metrics_result["composite_score"],
            grade=metrics_result["grades"],
            metric_scores=metrics_result["metrics"],
            task_results=task_results,
            tool_calls=tool_calls,
            agent_interactions=agent_interactions,
            responses=responses,
            execution_time=execution_time,
            metadata={
                "num_tasks": len(benchmark_tasks),
                "successful_tasks": sum(1 for r in task_results if r.get("success")),
            },
        )

        self.evaluation_history.append(eval_result)
        return eval_result

    def compare_agents(
        self,
        agent_results: Dict[str, EvaluationResult]
    ) -> Dict[str, Any]:
        """
        Compare multiple agent evaluation results.

        Args:
            agent_results: Dict mapping agent name to EvaluationResult

        Returns:
            Comparative analysis
        """
        if not agent_results:
            return {}

        # Find best agent per metric
        metric_ranks = {}
        for agent_name, result in agent_results.items():
            for metric in result.metric_scores:
                metric_name = metric["name"]
                if metric_name not in metric_ranks:
                    metric_ranks[metric_name] = []
                metric_ranks[metric_name].append({
                    "agent": agent_name,
                    "score": metric["normalized"],
                })

        # Rank each metric
        rankings = {}
        for metric_name, scores in metric_ranks.items():
            scores.sort(key=lambda x: x["score"], reverse=True)
            rankings[metric_name] = [
                {"rank": i + 1, "agent": s["agent"], "score": s["score"]}
                for i, s in enumerate(scores)
            ]

        # Overall rankings
        overall = sorted(
            [
                {"agent": name, "composite": result.composite_score}
                for name, result in agent_results.items()
            ],
            key=lambda x: x["composite"],
            reverse=True,
        )

        return {
            "rankings": rankings,
            "overall_ranking": [
                {"rank": i + 1, **item}
                for i, item in enumerate(overall)
            ],
            "best_agent": overall[0]["agent"] if overall else None,
        }

    def get_evaluation_summary(self) -> Dict[str, Any]:
        """Get summary of all evaluations."""
        if not self.evaluation_history:
            return {
                "total_evaluations": 0,
                "average_score": 0.0,
                "grade_distribution": {},
            }

        total = len(self.evaluation_history)
        scores = [e.composite_score for e in self.evaluation_history]

        grade_dist = {}
        for e in self.evaluation_history:
            grade = e.grade
            grade_dist[grade] = grade_dist.get(grade, 0) + 1

        return {
            "total_evaluations": total,
            "average_score": sum(scores) / total,
            "best_score": max(scores),
            "worst_score": min(scores),
            "grade_distribution": grade_dist,
            "total_execution_time": sum(e.execution_time for e in self.evaluation_history),
        }

    def generate_report(self, evaluation_result: EvaluationResult) -> str:
        """
        Generate human-readable evaluation report.

        Args:
            evaluation_result: Evaluation result to report

        Returns:
            Formatted report string
        """
        lines = [
            "=" * 60,
            "AGENT EVALUATION REPORT",
            "=" * 60,
            f"Agent: {evaluation_result.agent_name}",
            f"Timestamp: {datetime.fromtimestamp(evaluation_result.timestamp).isoformat()}",
            f"Composite Score: {evaluation_result.composite_score:.3f}",
            f"Grade: {evaluation_result.grade}",
            "-" * 60,
            "METRIC SCORES:",
        ]

        for metric in evaluation_result.metric_scores:
            lines.append(
                f"  {metric['name']}: {metric['normalized']:.3f} "
                f"(weight: {metric['weight']:.2f})"
            )

        lines.extend([
            "-" * 60,
            "EXECUTION SUMMARY:",
            f"  Tasks: {evaluation_result.metadata.get('num_tasks', 0)}",
            f"  Successful: {evaluation_result.metadata.get('successful_tasks', 0)}",
            f"  Execution Time: {evaluation_result.execution_time:.2f}s",
            "=" * 60,
        ])

        return "\n".join(lines)

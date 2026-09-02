"""Metrics for evaluating agent performance."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import time


@dataclass
class MetricScore:
    """Individual metric score."""
    name: str
    value: float
    max_value: float = 1.0
    weight: float = 1.0

    @property
    def normalized(self) -> float:
        """Get normalized score (0-1)."""
        return self.value / self.max_value if self.max_value > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "max_value": self.max_value,
            "normalized": self.normalized,
            "weight": self.weight,
        }


class MetricsCalculator:
    """
    Calculator for computing agent performance metrics.

    Metrics computed:
    - Task Success Rate
    - Tool Usage Accuracy
    - Collaboration Score
    - Response Quality
    - Evolution Gain
    """

    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []

    def calculate_task_success(self, results: List[Dict[str, Any]]) -> MetricScore:
        """
        Calculate task success rate.

        Args:
            results: List of task execution results

        Returns:
            MetricScore for task success
        """
        if not results:
            return MetricScore(name="task_success", value=0.0)

        successful = sum(1 for r in results if r.get("success", False))
        rate = successful / len(results)

        return MetricScore(
            name="task_success",
            value=rate,
            max_value=1.0,
            weight=0.3,  # 30% of overall score
        )

    def calculate_tool_accuracy(self, tool_calls: List[Dict[str, Any]]) -> MetricScore:
        """
        Calculate tool selection and usage accuracy.

        Args:
            tool_calls: List of tool call records

        Returns:
            MetricScore for tool accuracy
        """
        if not tool_calls:
            return MetricScore(name="tool_accuracy", value=0.0)

        correct_calls = sum(
            1 for call in tool_calls
            if call.get("success", False) and call.get("correct_tool", True)
        )
        accuracy = correct_calls / len(tool_calls) if tool_calls else 0

        return MetricScore(
            name="tool_accuracy",
            value=accuracy,
            max_value=1.0,
            weight=0.2,  # 20% of overall score
        )

    def calculate_collaboration_score(
        self,
        agent_interactions: List[Dict[str, Any]]
    ) -> MetricScore:
        """
        Calculate multi-agent collaboration quality.

        Args:
            agent_interactions: Records of inter-agent communications

        Returns:
            MetricScore for collaboration
        """
        if not agent_interactions:
            return MetricScore(name="collaboration", value=0.0)

        # Calculate based on:
        # - Number of successful exchanges
        # - Response times
        # - Consensus reached

        successful_exchanges = sum(
            1 for i in agent_interactions
            if i.get("response_received", False)
        )

        avg_response_time = sum(
            i.get("response_time", 0) for i in agent_interactions
        ) / len(agent_interactions) if agent_interactions else 0

        # Normalize response time (faster = better)
        response_score = max(0, 1 - (avg_response_time / 60))  # 60s baseline

        collaboration_score = (
            (successful_exchanges / len(agent_interactions)) * 0.6 +
            response_score * 0.4
        )

        return MetricScore(
            name="collaboration",
            value=collaboration_score,
            max_value=1.0,
            weight=0.2,  # 20% of overall score
        )

    def calculate_response_quality(
        self,
        responses: List[Dict[str, Any]],
        reference: Optional[List[str]] = None
    ) -> MetricScore:
        """
        Calculate quality of agent responses.

        Args:
            responses: List of agent responses
            reference: Optional reference answers for comparison

        Returns:
            MetricScore for response quality
        """
        if not responses:
            return MetricScore(name="response_quality", value=0.0)

        quality_scores = []

        for response in responses:
            score = 0.5  # Base score

            # Check for completeness
            if response.get("has_citations"):
                score += 0.15
            if response.get("has_synthesis"):
                score += 0.15

            # Check for structure
            if response.get("well_structured"):
                score += 0.1

            # Check relevance (if reference provided)
            if reference:
                # Simplified relevance check
                score += 0.1

            quality_scores.append(min(1.0, score))

        avg_quality = sum(quality_scores) / len(quality_scores)

        return MetricScore(
            name="response_quality",
            value=avg_quality,
            max_value=1.0,
            weight=0.15,  # 15% of overall score
        )

    def calculate_evolution_gain(
        self,
        baseline_metrics: Dict[str, float],
        current_metrics: Dict[str, float]
    ) -> MetricScore:
        """
        Calculate improvement from self-evolution.

        Args:
            baseline_metrics: Metrics before evolution
            current_metrics: Metrics after evolution

        Returns:
            MetricScore for evolution gain
        """
        if not baseline_metrics or not current_metrics:
            return MetricScore(name="evolution_gain", value=0.0)

        # Calculate relative improvement per metric
        improvements = []
        for key in baseline_metrics:
            if key in current_metrics and baseline_metrics[key] > 0:
                improvement = (
                    (current_metrics[key] - baseline_metrics[key]) /
                    baseline_metrics[key]
                )
                improvements.append(max(-1.0, improvement))  # Cap at -100%

        if not improvements:
            return MetricScore(name="evolution_gain", value=0.0)

        # Average improvement
        avg_improvement = sum(improvements) / len(improvements)

        # Convert to score (cap at 100% improvement = 1.0)
        gain_score = min(1.0, max(0.0, avg_improvement))

        return MetricScore(
            name="evolution_gain",
            value=gain_score,
            max_value=1.0,
            weight=0.15,  # 15% of overall score
        )

    def calculate_composite_score(
        self,
        metrics: List[MetricScore]
    ) -> float:
        """
        Calculate weighted composite score.

        Args:
            metrics: List of metric scores

        Returns:
            Weighted composite score (0-1)
        """
        if not metrics:
            return 0.0

        total_weight = sum(m.weight for m in metrics)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(m.normalized * m.weight for m in metrics)
        return weighted_sum / total_weight

    def compute_all_metrics(
        self,
        task_results: List[Dict[str, Any]],
        tool_calls: List[Dict[str, Any]],
        agent_interactions: List[Dict[str, Any]],
        responses: List[Dict[str, Any]],
        baseline_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Compute all metrics at once.

        Args:
            task_results: Task execution results
            tool_calls: Tool call records
            agent_interactions: Inter-agent interactions
            responses: Agent responses
            baseline_metrics: Optional baseline for evolution comparison

        Returns:
            Dict with all metrics and composite score
        """
        metrics = []

        # Task success
        task_metric = self.calculate_task_success(task_results)
        metrics.append(task_metric)

        # Tool accuracy
        tool_metric = self.calculate_tool_accuracy(tool_calls)
        metrics.append(tool_metric)

        # Collaboration
        collab_metric = self.calculate_collaboration_score(agent_interactions)
        metrics.append(collab_metric)

        # Response quality
        quality_metric = self.calculate_response_quality(responses)
        metrics.append(quality_metric)

        # Evolution gain
        if baseline_metrics:
            current = {
                "task_success": task_metric.value,
                "tool_accuracy": tool_metric.value,
                "collaboration": collab_metric.value,
                "quality": quality_metric.value,
            }
            evolution_metric = self.calculate_evolution_gain(baseline_metrics, current)
            metrics.append(evolution_metric)

        # Composite score
        composite = self.calculate_composite_score(metrics)

        return {
            "metrics": [m.to_dict() for m in metrics],
            "composite_score": composite,
            "grades": self._score_to_grade(composite),
        }

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    def record_metrics(self, metrics: Dict[str, Any]) -> None:
        """Record metrics for historical tracking."""
        metrics["timestamp"] = time.time()
        self.metrics_history.append(metrics)

    def get_metrics_trend(self, metric_name: str) -> List[float]:
        """Get historical trend for a specific metric."""
        return [
            m["metrics"]
            for m in self.metrics_history
            if any(me["name"] == metric_name for me in m.get("metrics", []))
        ]

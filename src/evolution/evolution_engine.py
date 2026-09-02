"""Self-evolution engine for autonomous agent improvement."""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import time

from src.evolution.feedback import FeedbackProcessor, Feedback, FeedbackType
from src.evolution.optimizer import AgentOptimizer, OptimizationStrategy


@dataclass
class EvolutionResult:
    """Result of an evolution iteration."""
    iteration: int
    success: bool
    agent_name: str
    feedback_processed: int
    optimizations_applied: List[str]
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    improvement_score: float
    duration: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "iteration": self.iteration,
            "success": self.success,
            "agent_name": self.agent_name,
            "feedback_processed": self.feedback_processed,
            "optimizations_applied": self.optimizations_applied,
            "metrics_before": self.metrics_before,
            "metrics_after": self.metrics_after,
            "improvement_score": self.improvement_score,
            "duration": self.duration,
            "timestamp": self.timestamp,
        }


class EvolutionEngine:
    """
    Self-evolution engine for autonomous agent improvement.

    Implements a feedback-driven improvement loop:
    1. Collect feedback from evaluations
    2. Process and analyze feedback patterns
    3. Apply optimization strategies
    4. Measure improvement
    5. Repeat

    Features:
    - Multiple optimization strategies
    - Configurable evolution policies
    - Progress tracking
    - Convergence detection
    """

    def __init__(
        self,
        max_iterations: int = 10,
        convergence_threshold: float = 0.05,
        enable_auto_evolution: bool = True,
    ):
        """
        Initialize Evolution Engine.

        Args:
            max_iterations: Maximum evolution iterations
            convergence_threshold: Stop if improvement below this
            enable_auto_evolution: Automatically evolve when feedback received
        """
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.enable_auto_evolution = enable_auto_evolution

        self.feedback_processor = FeedbackProcessor()
        self.optimizer = AgentOptimizer()

        self.evolution_history: List[EvolutionResult] = []
        self.current_iteration = 0
        self.best_metrics: Dict[str, float] = {}
        self.is_converged = False

    def evolve(
        self,
        agent: Any,
        feedback: Dict[str, Any],
        metrics: Optional[Dict[str, float]] = None
    ) -> EvolutionResult:
        """
        Execute one evolution iteration.

        Args:
            agent: Agent to evolve
            feedback: Feedback data
            metrics: Current agent metrics

        Returns:
            EvolutionResult with iteration details
        """
        start_time = time.time()
        self.current_iteration += 1

        agent_name = getattr(agent, "name", "unknown")
        metrics = metrics or self._get_default_metrics()

        # Store baseline metrics
        if not self.best_metrics:
            self.best_metrics = metrics.copy()

        metrics_before = metrics.copy()

        # Process feedback
        processed_feedback = self.feedback_processor.process_feedback({
            **feedback,
            "agent_name": agent_name,
        })

        # Generate actionable insights
        insights = self.feedback_processor.get_actionable_insights()

        # Apply optimizations based on insights
        optimizations_applied = []
        improvement_score = 0.0

        for insight in insights[:3]:  # Apply top 3 insights
            if insight["type"] == "improvement":
                # Select appropriate strategy
                strategy = self._select_strategy(insight)

                # Apply optimization
                result = self.optimizer.optimize(agent, feedback, strategy)

                if result.success:
                    optimizations_applied.append(result.strategy.value)
                    improvement_score += result.improvement_score

        # Calculate metrics after
        metrics_after = self._estimate_improved_metrics(metrics, improvement_score)

        # Update best metrics
        for key, value in metrics_after.items():
            if key not in self.best_metrics or value > self.best_metrics[key]:
                self.best_metrics[key] = value

        # Check convergence
        if self.current_iteration > 1:
            last_result = self.evolution_history[-1]
            last_improvement = last_result.improvement_score
            if last_improvement < self.convergence_threshold:
                self.is_converged = True

        duration = time.time() - start_time

        result = EvolutionResult(
            iteration=self.current_iteration,
            success=True,
            agent_name=agent_name,
            feedback_processed=1,
            optimizations_applied=optimizations_applied,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            improvement_score=improvement_score,
            duration=duration,
        )

        self.evolution_history.append(result)
        return result

    def evolve_multiple(
        self,
        agent: Any,
        feedback_history: List[Dict[str, Any]],
        metrics_history: Optional[List[Dict[str, float]]] = None
    ) -> List[EvolutionResult]:
        """
        Execute multiple evolution iterations.

        Args:
            agent: Agent to evolve
            feedback_history: List of feedback data
            metrics_history: Optional list of metrics per iteration

        Returns:
            List of EvolutionResults
        """
        results = []

        for i, feedback in enumerate(feedback_history):
            if self.is_converged:
                break

            metrics = metrics_history[i] if metrics_history else None
            result = self.evolve(agent, feedback, metrics)
            results.append(result)

        return results

    def _select_strategy(self, insight: Dict[str, Any]) -> OptimizationStrategy:
        """Select optimization strategy based on insight."""
        area = insight.get("area", "").lower()

        if any(kw in area for kw in ["prompt", "instruction", "clarity"]):
            return OptimizationStrategy.PROMPT_REFINEMENT
        elif any(kw in area for kw in ["tool", "selection", "use"]):
            return OptimizationStrategy.TOOL_SELECTION
        elif any(kw in area for kw in ["memory", "remember", "forget"]):
            return OptimizationStrategy.MEMORY_PRUNING
        elif any(kw in area for kw in ["behavior", "pattern", "action"]):
            return OptimizationStrategy.BEHAVIOR_CLONING
        else:
            return OptimizationStrategy.PROMPT_REFINEMENT

    def _get_default_metrics(self) -> Dict[str, float]:
        """Get default metrics when none provided."""
        return {
            "task_success": 0.7,
            "tool_accuracy": 0.7,
            "collaboration": 0.7,
            "response_quality": 0.7,
        }

    def _estimate_improved_metrics(
        self,
        metrics: Dict[str, float],
        improvement_score: float
    ) -> Dict[str, float]:
        """Estimate metrics after improvement."""
        improved = {}
        for key, value in metrics.items():
            # Apply improvement (capped at 1.0)
            improvement = improvement_score * 0.1  # Max 10% per iteration
            improved[key] = min(1.0, value * (1 + improvement))
        return improved

    def get_evolution_summary(self) -> Dict[str, Any]:
        """Get summary of evolution process."""
        if not self.evolution_history:
            return {
                "total_iterations": 0,
                "is_converged": False,
                "current_metrics": {},
            }

        return {
            "total_iterations": self.current_iteration,
            "successful_iterations": sum(1 for r in self.evolution_history if r.success),
            "is_converged": self.is_converged,
            "convergence_reason": (
                "Improvement below threshold" if self.is_converged else "Not converged"
            ),
            "total_optimizations": sum(
                len(r.optimizations_applied) for r in self.evolution_history
            ),
            "average_improvement": sum(
                r.improvement_score for r in self.evolution_history
            ) / len(self.evolution_history),
            "best_metrics": self.best_metrics,
            "evolution_trajectory": [
                {
                    "iteration": r.iteration,
                    "improvement_score": r.improvement_score,
                    "metrics": r.metrics_after,
                }
                for r in self.evolution_history
            ],
        }

    def should_continue_evolution(self) -> bool:
        """Check if evolution should continue."""
        if self.current_iteration >= self.max_iterations:
            return False
        if self.is_converged:
            return False
        return True

    def reset(self) -> None:
        """Reset evolution state."""
        self.evolution_history.clear()
        self.current_iteration = 0
        self.best_metrics.clear()
        self.is_converged = False
        self.feedback_processor = FeedbackProcessor()
        self.optimizer = AgentOptimizer()

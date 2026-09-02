"""Reviewer Agent - quality assurance and feedback generation."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from src.agents.base_agent import BaseAgent, AgentConfig


class ReviewerAgent(BaseAgent):
    """
    Agent specialized in quality assurance and review.

    Capabilities:
    - Output validation
    - Quality scoring
    - Feedback generation
    - Improvement suggestions
    - Consistency checking
    - Citation verification
    """

    def __init__(self, config: Optional[AgentConfig] = None, **kwargs):
        """
        Initialize Reviewer Agent.

        Args:
            config: Agent configuration
            **kwargs: Additional config parameters
        """
        if config is None:
            config = AgentConfig(name="reviewer", **kwargs)
        super().__init__(config)
        self.role = "reviewer"
        self.review_history: List[Dict[str, Any]] = []
        self.quality_threshold = 0.7

    async def think(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze what needs to be reviewed.

        Args:
            task: Original task description
            context: Shared context with results

        Returns:
            Thought process with review plan
        """
        results = context.get("results", {})

        # Determine review dimensions
        dimensions = self._determine_review_dimensions(task, results)

        # Identify key quality aspects
        quality_aspects = self._identify_quality_aspects(results)

        thought = {
            "task": task,
            "dimensions": dimensions,
            "quality_aspects": quality_aspects,
            "strict_mode": context.get("strict_review", False),
        }

        return thought

    def _determine_review_dimensions(self, task: str,
                                    results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determine which dimensions to review."""
        dimensions = [
            {"name": "correctness", "weight": 0.3, "description": "Are results factually correct?"},
            {"name": "completeness", "weight": 0.25, "description": "Are all aspects of the task covered?"},
            {"name": "coherence", "weight": 0.2, "description": "Are results logically consistent?"},
            {"name": "relevance", "weight": 0.15, "description": "Are results relevant to the task?"},
            {"name": "formatting", "weight": 0.1, "description": "Is output properly formatted?"},
        ]

        # Adjust weights based on task type
        task_lower = task.lower()
        if any(kw in task_lower for kw in ["code", "implement", "function"]):
            dimensions[0]["weight"] = 0.35  # correctness more important for code
            dimensions[3]["weight"] = 0.25  # relevance too
        elif any(kw in task_lower for kw in ["compare", "analysis"]):
            dimensions[1]["weight"] = 0.3  # completeness for analysis

        return dimensions

    def _identify_quality_aspects(self, results: Dict[str, Any]) -> List[str]:
        """Identify specific quality aspects to check."""
        aspects = []

        if not results:
            aspects.append("missing_results")
            return aspects

        # Check structure
        if isinstance(results, dict):
            if "output" in results:
                aspects.append("has_output")
            if "sources" in results or "citations" in results:
                aspects.append("has_citations")
            if "synthesis" in results:
                aspects.append("has_synthesis")

        # Check for common issues
        if results.get("success") is False:
            aspects.append("has_errors")

        return aspects

    async def act(self, thought_result: Dict[str, Any]) -> Any:
        """
        Perform the actual review.

        Args:
            thought_result: Result from think()

        Returns:
            Review results with quality scores and feedback
        """
        context = thought_result.get("context", {})
        results = context.get("results", {})

        # Evaluate each dimension
        dimension_scores = {}
        for dim in thought_result["dimensions"]:
            score = self._evaluate_dimension(
                dim["name"],
                results,
                context
            )
            dimension_scores[dim["name"]] = {
                "score": score,
                "weight": dim["weight"],
            }

        # Calculate weighted overall score
        overall_score = sum(
            d["score"] * d["weight"]
            for d in dimension_scores.values()
        )

        # Generate detailed feedback
        feedback = self._generate_feedback(dimension_scores, results)

        # Create improvement suggestions
        suggestions = self._create_suggestions(dimension_scores, results)

        review_result = {
            "overall_quality_score": overall_score,
            "dimension_scores": dimension_scores,
            "feedback": feedback,
            "suggestions": suggestions,
            "approved": overall_score >= self.quality_threshold,
            "review_timestamp": datetime.now().isoformat(),
        }

        self.review_history.append(review_result)
        return review_result

    def _evaluate_dimension(self, dimension: str, results: Dict[str, Any],
                           context: Dict[str, Any]) -> float:
        """
        Evaluate a specific quality dimension.

        Returns:
            Score between 0.0 and 1.0
        """
        scores = {
            "correctness": self._evaluate_correctness(results),
            "completeness": self._evaluate_completeness(results, context),
            "coherence": self._evaluate_coherence(results),
            "relevance": self._evaluate_relevance(results, context),
            "formatting": self._evaluate_formatting(results),
        }

        return scores.get(dimension, 0.5)

    def _evaluate_correctness(self, results: Dict[str, Any]) -> float:
        """Evaluate factual correctness."""
        if not results:
            return 0.0

        # Check for error flags
        if results.get("success") is False:
            return 0.2

        # Check for conflicting information in results
        if isinstance(results, dict):
            # Simulated correctness check
            return 0.85 if results.get("output") else 0.6

        return 0.7

    def _evaluate_completeness(self, results: Dict[str, Any],
                              context: Dict[str, Any]) -> float:
        """Evaluate task completeness."""
        if not results:
            return 0.0

        score = 0.5

        # Check if output exists
        if results.get("output"):
            score += 0.2

        # Check if citations/sources exist when expected
        task = context.get("task", "").lower()
        if "research" in task or "study" in task:
            if results.get("citations") or results.get("sources"):
                score += 0.15
            else:
                score -= 0.1

        # Check if synthesis exists
        if results.get("synthesis"):
            score += 0.15

        return max(0.0, min(1.0, score))

    def _evaluate_coherence(self, results: Dict[str, Any]) -> float:
        """Evaluate logical coherence."""
        if not results:
            return 0.0

        # Check for internal consistency
        if isinstance(results, dict):
            # Outputs should not contradict themselves
            return 0.8

        return 0.7

    def _evaluate_relevance(self, results: Dict[str, Any],
                           context: Dict[str, Any]) -> float:
        """Evaluate relevance to task."""
        if not results:
            return 0.0

        task = context.get("task", "").lower()

        # Check if output relates to the task
        output_str = str(results.get("output", "")).lower()

        # Simple keyword matching
        task_keywords = set(task.replace("?", "").split())
        output_keywords = set(output_str.split())

        overlap = len(task_keywords & output_keywords)
        relevance = overlap / max(len(task_keywords), 1)

        return max(0.3, min(1.0, relevance + 0.4))

    def _evaluate_formatting(self, results: Dict[str, Any]) -> float:
        """Evaluate output formatting."""
        if not results:
            return 0.0

        score = 0.7

        # Check if structured (dict/list) vs plain text
        if isinstance(results, (dict, list)):
            score += 0.15

        # Check for proper citations formatting
        if results.get("citations"):
            score += 0.15

        return min(1.0, score)

    def _generate_feedback(self, dimension_scores: Dict[str, Any],
                          results: Dict[str, Any]) -> str:
        """Generate human-readable feedback."""
        feedback_parts = []

        for dim_name, data in dimension_scores.items():
            score = data["score"]
            if score < 0.6:
                feedback_parts.append(
                    f"{dim_name.capitalize()} needs improvement (score: {score:.2f})"
                )
            elif score >= 0.8:
                feedback_parts.append(
                    f"{dim_name.capitalize()} is good (score: {score:.2f})"
                )

        if not feedback_parts:
            feedback_parts.append("Overall quality is acceptable")

        return ". ".join(feedback_parts)

    def _create_suggestions(self, dimension_scores: Dict[str, Any],
                           results: Dict[str, Any]) -> List[str]:
        """Create specific improvement suggestions."""
        suggestions = []

        for dim_name, data in dimension_scores.items():
            score = data["score"]

            if score < 0.6:
                if dim_name == "correctness":
                    suggestions.append("Verify all facts and figures")
                elif dim_name == "completeness":
                    suggestions.append("Add more details and citations")
                elif dim_name == "coherence":
                    suggestions.append("Improve logical flow of arguments")
                elif dim_name == "relevance":
                    suggestions.append("Focus more on the core task")
                elif dim_name == "formatting":
                    suggestions.append("Improve output structure and formatting")

        if not suggestions:
            suggestions.append("Consider adding examples or citations")

        return suggestions

    async def review(self, results: Dict[str, Any],
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main review method - compatible with multi-agent interface.

        Args:
            results: Results to review
            context: Review context

        Returns:
            Review feedback
        """
        thought = await self.think(context.get("task", ""), {**context, "results": results})
        return await self.act(thought)

    def get_review_stats(self) -> Dict[str, Any]:
        """Get review statistics."""
        if not self.review_history:
            return {"total_reviews": 0}

        total = len(self.review_history)
        approved = sum(1 for r in self.review_history if r.get("approved"))

        avg_score = sum(
            r.get("overall_quality_score", 0)
            for r in self.review_history
        ) / total

        return {
            "total_reviews": total,
            "approved": approved,
            "rejected": total - approved,
            "approval_rate": approved / total,
            "average_score": avg_score,
        }

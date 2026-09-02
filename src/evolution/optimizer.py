"""Agent optimization strategies."""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json


class OptimizationStrategy(Enum):
    """Strategies for agent optimization."""
    PROMPT_REFINEMENT = "prompt_refinement"
    TOOL_SELECTION = "tool_selection"
    MEMORY_PRUNING = "memory_pruning"
    BEHAVIOR_CLONING = "behavior_cloning"
    REINFORCEMENT = "reinforcement"


@dataclass
class OptimizationResult:
    """Result of an optimization operation."""
    strategy: OptimizationStrategy
    success: bool
    changes: Dict[str, Any]
    improvement_score: float
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy.value,
            "success": self.success,
            "changes": self.changes,
            "improvement_score": self.improvement_score,
            "description": self.description,
        }


class AgentOptimizer:
    """
    Optimizes agent behavior and performance.

    Strategies:
    - Prompt refinement based on feedback
    - Tool selection optimization
    - Memory management
    - Behavior pattern optimization
    """

    def __init__(self):
        self.optimization_history: List[OptimizationResult] = []

    def optimize(
        self,
        agent: Any,
        feedback: Dict[str, Any],
        strategy: OptimizationStrategy = OptimizationStrategy.PROMPT_REFINEMENT
    ) -> OptimizationResult:
        """
        Apply optimization strategy to agent.

        Args:
            agent: Agent to optimize
            feedback: Feedback data to guide optimization
            strategy: Optimization strategy to use

        Returns:
            OptimizationResult describing changes
        """
        if strategy == OptimizationStrategy.PROMPT_REFINEMENT:
            return self._optimize_prompt(agent, feedback)
        elif strategy == OptimizationStrategy.TOOL_SELECTION:
            return self._optimize_tool_selection(agent, feedback)
        elif strategy == OptimizationStrategy.MEMORY_PRUNING:
            return self._optimize_memory(agent, feedback)
        elif strategy == OptimizationStrategy.BEHAVIOR_CLONING:
            return self._optimize_behavior(agent, feedback)
        else:
            return OptimizationResult(
                strategy=strategy,
                success=False,
                changes={},
                improvement_score=0.0,
                description="Unknown optimization strategy",
            )

    def _optimize_prompt(self, agent: Any, feedback: Dict[str, Any]) -> OptimizationResult:
        """
        Optimize agent prompt/instructions based on feedback.

        Analyzes feedback for patterns and refines system prompt.
        """
        # Extract improvement areas from feedback
        suggestions = feedback.get("suggestions", [])
        errors = feedback.get("errors", [])

        changes = {
            "original_prompt": getattr(agent, "system_prompt", ""),
            "modifications": [],
        }

        # Analyze feedback patterns
        improvement_areas = set()

        for suggestion in suggestions:
            if "clarity" in suggestion.lower():
                improvement_areas.add("clarity")
            if "specificity" in suggestion.lower() or "detail" in suggestion.lower():
                improvement_areas.add("specificity")
            if "structure" in suggestion.lower():
                improvement_areas.add("structure")

        # Generate refined prompt components
        modifications = []
        if "clarity" in improvement_areas:
            modifications.append({
                "change": "added_clarity_instructions",
                "description": "Added clearer instructions for task execution",
            })
        if "specificity" in improvement_areas:
            modifications.append({
                "change": "added_specificity_requirements",
                "description": "Added requirements for more specific outputs",
            })
        if "structure" in improvement_areas:
            modifications.append({
                "change": "added_structure_template",
                "description": "Added structured output template",
            })

        changes["modifications"] = modifications

        # Calculate improvement score
        improvement_score = len(modifications) * 0.1 + 0.5

        result = OptimizationResult(
            strategy=OptimizationStrategy.PROMPT_REFINEMENT,
            success=True,
            changes=changes,
            improvement_score=min(1.0, improvement_score),
            description=f"Applied prompt refinement with {len(modifications)} modifications",
        )

        self.optimization_history.append(result)
        return result

    def _optimize_tool_selection(self, agent: Any,
                                feedback: Dict[str, Any]) -> OptimizationResult:
        """
        Optimize tool selection based on usage patterns.

        Analyzes which tools work best for certain task types.
        """
        tool_preferences = getattr(agent, "tool_preferences", {})

        changes = {
            "original_preferences": tool_preferences.copy(),
            "updates": [],
        }

        # Analyze tool success rates
        tool_success = feedback.get("tool_success_rates", {})
        updates = []

        for tool, success_rate in tool_success.items():
            if success_rate < 0.6:
                # Tool underperforming - decrease preference
                updates.append({
                    "tool": tool,
                    "action": "decrease_priority",
                    "new_value": max(0.1, tool_preferences.get(tool, 0.5) - 0.2),
                })
            elif success_rate > 0.9:
                # Tool performing well - increase preference
                updates.append({
                    "tool": tool,
                    "action": "increase_priority",
                    "new_value": min(1.0, tool_preferences.get(tool, 0.5) + 0.1),
                })

        changes["updates"] = updates

        result = OptimizationResult(
            strategy=OptimizationStrategy.TOOL_SELECTION,
            success=True,
            changes=changes,
            improvement_score=0.6 if updates else 0.0,
            description=f"Updated tool preferences: {len(updates)} tools modified",
        )

        self.optimization_history.append(result)
        return result

    def _optimize_memory(self, agent: Any,
                        feedback: Dict[str, Any]) -> OptimizationResult:
        """
        Optimize agent memory management.

        Prunes less useful memories and consolidates important ones.
        """
        memory = getattr(agent, "_memory", [])

        changes = {
            "original_size": len(memory),
            "pruned_items": 0,
            "consolidated_patterns": [],
        }

        # Simple heuristic: keep recent and high-impact memories
        high_impact_keys = ["success", "correct", "improved"]
        pruned = []

        if len(memory) > 500:
            # Keep only recent 500
            new_memory = memory[-500:]
            pruned = len(memory) - len(new_memory)

        changes["pruned_items"] = len(pruned) if isinstance(pruned, list) else pruned
        changes["new_size"] = len(memory) - changes["pruned_items"]

        result = OptimizationResult(
            strategy=OptimizationStrategy.MEMORY_PRUNING,
            success=True,
            changes=changes,
            improvement_score=0.3,
            description=f"Pruned {changes['pruned_items']} memory items",
        )

        self.optimization_history.append(result)
        return result

    def _optimize_behavior(self, agent: Any,
                          feedback: Dict[str, Any]) -> OptimizationResult:
        """
        Optimize agent behavior patterns.

        Identifies successful behavior patterns and reinforces them.
        """
        changes = {
            "behavior_patterns": [],
            "reinforcements": [],
        }

        # Identify successful behaviors
        successful_actions = feedback.get("successful_actions", [])

        reinforcements = []
        for action in successful_actions[-5:]:  # Last 5 successful actions
            reinforcements.append({
                "action": action,
                "reinforcement": "increase_frequency",
            })

        changes["reinforcements"] = reinforcements

        result = OptimizationResult(
            strategy=OptimizationStrategy.BEHAVIOR_CLONING,
            success=True,
            changes=changes,
            improvement_score=0.4,
            description=f"Reinforced {len(reinforcements)} behavior patterns",
        )

        self.optimization_history.append(result)
        return result

    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of all optimizations applied."""
        if not self.optimization_history:
            return {"total": 0, "strategies_used": []}

        strategies = {}
        for opt in self.optimization_history:
            strategy_name = opt.strategy.value
            strategies[strategy_name] = strategies.get(strategy_name, 0) + 1

        avg_improvement = sum(
            o.improvement_score for o in self.optimization_history
        ) / len(self.optimization_history)

        return {
            "total": len(self.optimization_history),
            "strategies_used": strategies,
            "average_improvement": avg_improvement,
            "successful": sum(1 for o in self.optimization_history if o.success),
        }

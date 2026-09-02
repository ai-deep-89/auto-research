"""Feedback processing for agent learning."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import time


class FeedbackType(Enum):
    """Types of feedback for agent improvement."""
    SUCCESS = "success"
    FAILURE = "failure"
    SUGGESTION = "suggestion"
    CORRECTION = "correction"
    CRITIQUE = "critique"


class FeedbackPriority(Enum):
    """Priority levels for feedback."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Feedback:
    """
    Structured feedback for agent learning.

    Attributes:
        feedback_id: Unique identifier
        feedback_type: Type of feedback
        source: Where feedback came from (reviewer, user, system)
        content: Feedback content
        priority: Feedback priority
        task_id: Related task ID
        agent_name: Agent this feedback is for
        created_at: Creation timestamp
        processed: Whether feedback has been processed
        metadata: Additional feedback data
    """
    feedback_type: FeedbackType
    content: str
    source: str
    agent_name: str
    feedback_id: str = field(default_factory=lambda: f"fb_{int(time.time() * 1000)}")
    priority: FeedbackPriority = FeedbackPriority.NORMAL
    task_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    processed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def mark_processed(self) -> None:
        """Mark feedback as processed."""
        self.processed = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feedback_id": self.feedback_id,
            "feedback_type": self.feedback_type.value,
            "source": self.source,
            "content": self.content,
            "priority": self.priority.value,
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "created_at": self.created_at,
            "processed": self.processed,
            "metadata": self.metadata,
        }


class FeedbackProcessor:
    """
    Processes and analyzes feedback for agent improvement.

    Capabilities:
    - Feedback categorization
    - Priority assignment
    - Pattern detection across feedback
    - Improvement suggestion generation
    - Feedback-to-action mapping
    """

    def __init__(self):
        self.feedback_history: List[Feedback] = []
        self.patterns: Dict[str, List[Feedback]] = {}

    def process_feedback(self, raw_feedback: Dict[str, Any]) -> Feedback:
        """
        Process raw feedback into structured Feedback.

        Args:
            raw_feedback: Unstructured feedback dict

        Returns:
            Structured Feedback object
        """
        # Determine feedback type
        feedback_type = self._classify_feedback(raw_feedback)

        # Determine priority
        priority = self._determine_priority(raw_feedback, feedback_type)

        feedback = Feedback(
            feedback_type=feedback_type,
            content=raw_feedback.get("content", raw_feedback.get("message", "")),
            source=raw_feedback.get("source", "system"),
            agent_name=raw_feedback.get("agent_name", "unknown"),
            priority=priority,
            task_id=raw_feedback.get("task_id"),
            metadata=raw_feedback.get("metadata", {}),
        )

        self.feedback_history.append(feedback)
        return feedback

    def _classify_feedback(self, raw: Dict[str, Any]) -> FeedbackType:
        """Classify feedback type."""
        content = raw.get("content", "").lower()
        success = raw.get("success")
        suggestion = raw.get("suggestion")

        if success is True:
            return FeedbackType.SUCCESS
        elif success is False:
            return FeedbackType.FAILURE
        elif suggestion:
            return FeedbackType.SUGGESTION
        elif "correct" in content or "should" in content:
            return FeedbackType.CORRECTION
        elif any(kw in content for kw in ["improve", "better", "instead"]):
            return FeedbackType.CRITIQUE
        else:
            return FeedbackType.NORMAL

    def _determine_priority(self, raw: Dict[str, Any],
                          feedback_type: FeedbackType) -> FeedbackPriority:
        """Determine feedback priority."""
        # Critical for failures
        if feedback_type == FeedbackType.FAILURE:
            error = raw.get("error", "").lower()
            if any(kw in error for kw in ["critical", "crash", "timeout"]):
                return FeedbackPriority.CRITICAL
            return FeedbackPriority.HIGH

        # Check explicit priority
        priority = raw.get("priority")
        if priority:
            return FeedbackPriority(priority)

        return FeedbackPriority.NORMAL

    def extract_patterns(self) -> Dict[str, Any]:
        """
        Extract patterns from feedback history.

        Returns:
            Dict of identified patterns
        """
        patterns = {
            "recurring_issues": [],
            "success_factors": [],
            "improvement_areas": [],
            "recommended_actions": [],
        }

        # Group by agent
        by_agent = {}
        for fb in self.feedback_history:
            agent = fb.agent_name
            if agent not in by_agent:
                by_agent[agent] = []
            by_agent[agent].append(fb)

        # Analyze each agent
        for agent, feedbacks in by_agent.items():
            # Count failure types
            failures = [f for f in feedbacks if f.feedback_type == FeedbackType.FAILURE]
            if len(failures) >= 3:
                # Identify common failure content
                content_keywords = {}
                for f in failures:
                    words = f.content.lower().split()
                    for word in words:
                        if len(word) > 4:
                            content_keywords[word] = content_keywords.get(word, 0) + 1

                if content_keywords:
                    top_issues = sorted(content_keywords.items(), key=lambda x: x[1], reverse=True)[:3]
                    patterns["recurring_issues"].append({
                        "agent": agent,
                        "issues": top_issues,
                        "count": len(failures),
                    })

            # Collect success factors
            successes = [f for f in feedbacks if f.feedback_type == FeedbackType.SUCCESS]
            if successes:
                patterns["success_factors"].append({
                    "agent": agent,
                    "count": len(successes),
                })

        return patterns

    def get_actionable_insights(self) -> List[Dict[str, Any]]:
        """
        Convert feedback patterns to actionable insights.

        Returns:
            List of actionable improvement suggestions
        """
        patterns = self.extract_patterns()
        insights = []

        # Generate insights from recurring issues
        for issue in patterns.get("recurring_issues", []):
            agent = issue["agent"]
            top_issues = issue["issues"]

            for keyword, count in top_issues:
                if count >= 2:
                    insights.append({
                        "type": "improvement",
                        "agent": agent,
                        "area": keyword,
                        "priority": "high" if count >= 3 else "medium",
                        "suggestion": f"Focus on improving {keyword} capabilities",
                        "evidence": f"Occurred {count} times",
                    })

        return insights

    def get_unprocessed_feedback(self, agent_name: Optional[str] = None) -> List[Feedback]:
        """Get unprocessed feedback, optionally filtered by agent."""
        feedbacks = [f for f in self.feedback_history if not f.processed]
        if agent_name:
            feedbacks = [f for f in feedbacks if f.agent_name == agent_name]
        return feedbacks

    def mark_processed(self, feedback_id: str) -> bool:
        """Mark feedback as processed."""
        for fb in self.feedback_history:
            if fb.feedback_id == feedback_id:
                fb.mark_processed()
                return True
        return False

    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of feedback history."""
        if not self.feedback_history:
            return {"total": 0, "by_type": {}, "processed": 0}

        by_type = {}
        for fb in self.feedback_history:
            fb_type = fb.feedback_type.value
            by_type[fb_type] = by_type.get(fb_type, 0) + 1

        return {
            "total": len(self.feedback_history),
            "by_type": by_type,
            "processed": sum(1 for f in self.feedback_history if f.processed),
            "pending": sum(1 for f in self.feedback_history if not f.processed),
        }

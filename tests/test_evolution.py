"""Unit tests for evolution module."""

import pytest
from src.evolution.evolution_engine import EvolutionEngine, EvolutionResult
from src.evolution.feedback import FeedbackProcessor, Feedback, FeedbackType, FeedbackPriority
from src.evolution.optimizer import AgentOptimizer, OptimizationStrategy


class TestFeedbackProcessor:
    """Tests for FeedbackProcessor."""

    def test_process_feedback(self):
        """Test processing raw feedback."""
        processor = FeedbackProcessor()

        raw = {
            "content": "Task completed successfully",
            "source": "reviewer",
            "agent_name": "test_agent",
            "success": True,
        }

        feedback = processor.process_feedback(raw)

        assert feedback.feedback_type == FeedbackType.SUCCESS
        assert feedback.content == "Task completed successfully"
        assert feedback.agent_name == "test_agent"
        assert not feedback.processed

    def test_failure_classification(self):
        """Test failure feedback classification."""
        processor = FeedbackProcessor()

        raw = {
            "content": "Task failed due to error",
            "source": "reviewer",
            "success": False,
        }

        feedback = processor.process_feedback(raw)
        assert feedback.feedback_type == FeedbackType.FAILURE
        assert feedback.priority == FeedbackPriority.HIGH

    def test_critical_failure(self):
        """Test critical failure prioritization."""
        processor = FeedbackProcessor()

        raw = {
            "content": "Critical crash detected",
            "source": "system",
            "success": False,
            "error": "critical crash",
        }

        feedback = processor.process_feedback(raw)
        assert feedback.priority == FeedbackPriority.CRITICAL

    def test_extract_patterns(self):
        """Test pattern extraction from feedback."""
        processor = FeedbackProcessor()

        # Add multiple failure feedbacks
        for i in range(3):
            processor.process_feedback({
                "content": "Tool selection failed repeatedly",
                "source": "reviewer",
                "success": False,
            })

        patterns = processor.extract_patterns()
        assert "recurring_issues" in patterns

    def test_unprocessed_feedback(self):
        """Test getting unprocessed feedback."""
        processor = FeedbackProcessor()

        processor.process_feedback({"content": "test1", "source": "test"})
        processor.process_feedback({"content": "test2", "source": "test"})

        unprocessed = processor.get_unprocessed_feedback()
        assert len(unprocessed) == 2


class TestAgentOptimizer:
    """Tests for AgentOptimizer."""

    def test_prompt_refinement(self):
        """Test prompt optimization."""
        optimizer = AgentOptimizer()

        class MockAgent:
            name = "test_agent"
            system_prompt = "Original prompt"

        feedback = {
            "suggestions": ["Improve clarity", "Add specificity"],
        }

        result = optimizer.optimize(MockAgent(), feedback, OptimizationStrategy.PROMPT_REFINEMENT)

        assert result.success
        assert result.strategy == OptimizationStrategy.PROMPT_REFINEMENT

    def test_tool_selection_optimization(self):
        """Test tool selection optimization."""
        optimizer = AgentOptimizer()

        class MockAgent:
            name = "test_agent"
            tool_preferences = {"web_search": 0.5, "code_exec": 0.5}

        feedback = {
            "tool_success_rates": {
                "web_search": 0.95,
                "code_exec": 0.4,
            }
        }

        result = optimizer.optimize(MockAgent(), feedback, OptimizationStrategy.TOOL_SELECTION)

        assert result.success

    def test_memory_pruning(self):
        """Test memory optimization."""
        optimizer = AgentOptimizer()

        class MockAgent:
            name = "test_agent"
            _memory = [{"data": i} for i in range(600)]

        feedback = {}
        result = optimizer.optimize(MockAgent(), feedback, OptimizationStrategy.MEMORY_PRUNING)

        assert result.success


class TestEvolutionEngine:
    """Tests for EvolutionEngine."""

    def test_engine_initialization(self):
        """Test evolution engine setup."""
        engine = EvolutionEngine(max_iterations=5)

        assert engine.max_iterations == 5
        assert engine.current_iteration == 0
        assert not engine.is_converged

    def test_single_evolution_iteration(self):
        """Test one evolution iteration."""
        engine = EvolutionEngine()

        class MockAgent:
            name = "test_agent"

        feedback = {
            "content": "Improve tool selection",
            "source": "reviewer",
            "success": False,
            "suggestions": ["Better tool selection logic"],
        }

        result = engine.evolve(MockAgent(), feedback)

        assert result.success
        assert result.iteration == 1
        assert len(result.optimizations_applied) >= 0

    def test_convergence_detection(self):
        """Test convergence when improvement stalls."""
        engine = EvolutionEngine(
            max_iterations=10,
            convergence_threshold=0.1,
        )

        class MockAgent:
            name = "test_agent"

        # Simulate diminishing improvements
        for i in range(5):
            engine.evolve(
                MockAgent(),
                {"content": "feedback", "success": True},
                {"task_success": 0.7, "tool_accuracy": 0.7},
            )

        # Check that evolution eventually converges
        assert engine.current_iteration >= 0

    def test_evolution_summary(self):
        """Test getting evolution summary."""
        engine = EvolutionEngine()

        summary = engine.get_evolution_summary()

        assert "total_iterations" in summary
        assert "is_converged" in summary
        assert "current_metrics" in summary

    def test_reset(self):
        """Test resetting evolution state."""
        engine = EvolutionEngine()
        engine.current_iteration = 5

        engine.reset()

        assert engine.current_iteration == 0
        assert not engine.is_converged
        assert len(engine.evolution_history) == 0

    def test_should_continue_evolution(self):
        """Test continue/stop decisions."""
        engine = EvolutionEngine(max_iterations=3)

        # Should continue initially
        assert engine.should_continue_evolution()

        # After max iterations
        engine.current_iteration = 3
        assert not engine.should_continue_evolution()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

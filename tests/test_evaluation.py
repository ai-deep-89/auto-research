"""Unit tests for evaluation framework."""

import pytest
from src.evaluation.metrics import MetricsCalculator, MetricScore
from src.evaluation.evaluator import Evaluator
from src.evaluation.benchmark import Benchmark, BenchmarkTask, TaskCategory


class TestMetricsCalculator:
    """Tests for MetricsCalculator."""

    def test_task_success_calculation(self):
        """Test task success rate calculation."""
        calc = MetricsCalculator()

        results = [
            {"success": True},
            {"success": True},
            {"success": False},
        ]

        score = calc.calculate_task_success(results)
        assert score.value == pytest.approx(2/3, rel=0.01)
        assert score.weight == 0.3

    def test_empty_results(self):
        """Test handling of empty results."""
        calc = MetricsCalculator()

        score = calc.calculate_task_success([])
        assert score.value == 0.0

    def test_tool_accuracy(self):
        """Test tool accuracy calculation."""
        calc = MetricsCalculator()

        calls = [
            {"success": True, "correct_tool": True},
            {"success": True, "correct_tool": True},
            {"success": False, "correct_tool": True},
        ]

        score = calc.calculate_tool_accuracy(calls)
        assert score.value == pytest.approx(2/3, rel=0.01)

    def test_composite_score(self):
        """Test weighted composite score."""
        calc = MetricsCalculator()

        metrics = [
            MetricScore("metric1", value=0.8, max_value=1.0, weight=0.5),
            MetricScore("metric2", value=0.6, max_value=1.0, weight=0.5),
        ]

        composite = calc.calculate_composite_score(metrics)
        assert composite == 0.7


class TestEvaluator:
    """Tests for Evaluator."""

    def test_evaluator_initialization(self):
        """Test evaluator can be initialized."""
        evaluator = Evaluator()

        assert evaluator.metrics_calculator is not None
        assert len(evaluator.evaluation_history) == 0

    def test_set_baseline(self):
        """Test setting baseline metrics."""
        evaluator = Evaluator()

        baseline = {"task_success": 0.7, "tool_accuracy": 0.8}
        evaluator.set_baseline(baseline)

        assert evaluator.baseline_metrics == baseline

    def test_get_summary(self):
        """Test getting evaluation summary."""
        evaluator = Evaluator()

        summary = evaluator.get_evaluation_summary()

        assert "total_evaluations" in summary
        assert summary["total_evaluations"] == 0


class TestBenchmark:
    """Tests for Benchmark."""

    def test_benchmark_initialization(self):
        """Test benchmark loads default tasks."""
        benchmark = Benchmark()

        assert len(benchmark.tasks) > 0

    def test_get_tasks_by_category(self):
        """Test filtering tasks by category."""
        benchmark = Benchmark()

        research_tasks = benchmark.get_tasks_by_category(TaskCategory.RESEARCH)
        assert all(t.category == TaskCategory.RESEARCH for t in research_tasks)

    def test_get_tasks_by_difficulty(self):
        """Test filtering tasks by difficulty."""
        benchmark = Benchmark()

        easy_tasks = benchmark.get_tasks_by_difficulty(1)
        assert all(t.difficulty == 1 for t in easy_tasks)

    def test_get_task_by_id(self):
        """Test getting specific task."""
        benchmark = Benchmark()

        task = benchmark.get_task("res_001")
        assert task is not None
        assert task.task_id == "res_001"

    def test_benchmark_summary(self):
        """Test benchmark summary."""
        benchmark = Benchmark()

        summary = benchmark.get_benchmark_summary()

        assert "total_tasks" in summary
        assert "by_category" in summary


class TestBenchmarkTask:
    """Tests for BenchmarkTask."""

    def test_task_creation(self):
        """Test creating a benchmark task."""
        task = BenchmarkTask(
            task_id="test_001",
            name="Test Task",
            description="A test task",
            category=TaskCategory.RESEARCH,
            difficulty=3,
        )

        assert task.task_id == "test_001"
        assert task.category == TaskCategory.RESEARCH
        assert task.difficulty == 3

    def test_task_to_dict(self):
        """Test task serialization."""
        task = BenchmarkTask(
            task_id="test_001",
            name="Test Task",
            description="A test task",
            category=TaskCategory.CODE_GENERATION,
        )

        task_dict = task.to_dict()

        assert task_dict["task_id"] == "test_001"
        assert task_dict["category"] == "code_generation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

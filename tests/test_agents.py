"""Unit tests for agents."""

import pytest
import asyncio
from src.agents.base_agent import BaseAgent, AgentConfig
from src.agents.researcher import ResearcherAgent
from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.agents.reviewer import ReviewerAgent


class TestBaseAgent:
    """Tests for BaseAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized."""
        config = AgentConfig(name="test_agent")
        agent = BaseAgent(config)

        assert agent.name == "test_agent"
        assert agent.config.name == "test_agent"

    def test_agent_memory(self):
        """Test agent memory functionality."""
        agent = BaseAgent(AgentConfig(name="test", memory_enabled=True))

        agent._add_to_memory({"type": "test", "data": "hello"})
        memory = agent.get_memory()

        assert len(memory) == 1
        assert memory[0]["data"] == "hello"

    def test_agent_stats(self):
        """Test agent statistics."""
        agent = BaseAgent(AgentConfig(name="test"))
        stats = agent.get_stats()

        assert "name" in stats
        assert "execution_count" in stats
        assert stats["execution_count"] == 0


class TestResearcherAgent:
    """Tests for ResearcherAgent."""

    @pytest.mark.asyncio
    async def test_researcher_thinks(self):
        """Test researcher thinks about task."""
        agent = ResearcherAgent(name="researcher")

        thought = await agent.think(
            "Research LLM self-evolution",
            {}
        )

        assert "analysis" in thought
        assert "plan" in thought
        assert "confidence" in thought

    @pytest.mark.asyncio
    async def test_researcher_determines_research_type(self):
        """Test research type detection."""
        agent = ResearcherAgent()

        # Test academic research
        rtype = agent._determine_research_type("search for arxiv papers")
        assert rtype == "academic"

        # Test comparative research
        rtype = agent._determine_research_type("compare A vs B")
        assert rtype == "comparative"

        # Test state of the art
        rtype = agent._determine_research_type("latest advances in X")
        assert rtype == "state_of_the_art"


class TestPlannerAgent:
    """Tests for PlannerAgent."""

    @pytest.mark.asyncio
    async def test_planner_thinks(self):
        """Test planner creates task plan."""
        agent = PlannerAgent(name="planner")

        thought = await agent.think(
            "Build a research pipeline",
            {}
        )

        assert "task" in thought
        assert "subtasks" in thought
        assert "complexity" in thought
        assert "strategy" in thought

    def test_analyze_complexity(self):
        """Test complexity analysis."""
        agent = PlannerAgent()

        # High complexity
        complexity = agent._analyze_complexity(
            "multi-step complex comprehensive analysis",
            []
        )
        assert complexity == "high"

        # Low complexity
        complexity = agent._analyze_complexity(
            "simple quick basic task",
            []
        )
        assert complexity == "low"


class TestExecutorAgent:
    """Tests for ExecutorAgent."""

    @pytest.mark.asyncio
    async def test_executor_thinks(self):
        """Test executor analyzes execution approach."""
        agent = ExecutorAgent(name="executor")

        thought = await agent.think(
            "Execute Python code for data analysis",
            {}
        )

        assert "task" in thought
        assert "execution_type" in thought
        assert "selected_tools" in thought

    def test_determine_execution_type(self):
        """Test execution type detection."""
        agent = ExecutorAgent()

        # Code execution
        etype = agent._determine_execution_type("run this python code")
        assert etype == "code_execution"

        # Search
        etype = agent._determine_execution_type("search for relevant papers")
        assert etype == "search"


class TestReviewerAgent:
    """Tests for ReviewerAgent."""

    @pytest.mark.asyncio
    async def test_reviewer_thinks(self):
        """Test reviewer analyzes what to review."""
        agent = ReviewerAgent(name="reviewer")

        thought = await agent.think(
            "Review research on LLM",
            {"results": {"output": "test"}}
        )

        assert "dimensions" in thought
        assert "quality_aspects" in thought

    @pytest.mark.asyncio
    async def test_review_result(self):
        """Test review produces valid feedback."""
        agent = ReviewerAgent(name="reviewer")

        # Complete a review
        review_result = await agent.review(
            {"success": True, "output": "Good work"},
            {"task": "test task"}
        )

        assert "overall_quality_score" in review_result
        assert "dimension_scores" in review_result
        assert "approved" in review_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Research Agent - specialized for information gathering and analysis."""

from typing import Dict, Any, Optional, List
from datetime import datetime

from src.agents.base_agent import BaseAgent, AgentConfig
from src.core.message import MessageType


class ResearcherAgent(BaseAgent):
    """
    Agent specialized in research and information gathering.

    Capabilities:
    - Web search (arXiv, Google, Bing)
    - Paper analysis
    - Knowledge synthesis
    - Citation generation
    - Multi-source information aggregation

    Tools typically used:
    - WebSearchTool
    - CodeExecutor (for running search scripts)
    - DocumentProcessor
    """

    def __init__(self, config: Optional[AgentConfig] = None, **kwargs):
        """
        Initialize Researcher Agent.

        Args:
            config: Agent configuration
            **kwargs: Additional config parameters
        """
        if config is None:
            config = AgentConfig(name="researcher", **kwargs)
        super().__init__(config)
        self.role = "researcher"
        self.research_focus: Optional[str] = None

    def _register_builtin_tools(self) -> None:
        """Register research-specific tools."""
        # Tools would be registered here in full implementation
        pass

    async def think(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze research task and determine approach.

        Args:
            task: Research task description
            context: Shared context

        Returns:
            Thought process with research plan
        """
        task_lower = task.lower()

        # Determine research type
        research_type = self._determine_research_type(task_lower)

        # Identify key concepts to search
        concepts = self._extract_key_concepts(task)

        # Determine required sources
        sources = self._determine_sources(task_lower)

        thought = {
            "analysis": {
                "research_type": research_type,
                "key_concepts": concepts,
                "sources": sources,
                "query": task,
            },
            "plan": self._create_research_plan(research_type, concepts, sources),
            "confidence": 0.85,
        }

        return thought

    def _determine_research_type(self, task: str) -> str:
        """Determine type of research needed."""
        if any(kw in task for kw in ["paper", "arxiv", "publication", "conference"]):
            return "academic"
        elif any(kw in task for kw in ["compare", "vs", "versus", "difference"]):
            return "comparative"
        elif any(kw in task for kw in ["latest", "recent", "new", "current"]):
            return "state_of_the_art"
        elif any(kw in task for kw in ["how", "what", "why", "explain"]):
            return "explanatory"
        else:
            return "general"

    def _extract_key_concepts(self, task: str) -> List[str]:
        """Extract key concepts from task."""
        # Simple extraction - in production would use NLP
        words = task.replace("?", "").replace(",", " ").split()
        # Filter common words and keep significant terms
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                    "being", "have", "has", "had", "do", "does", "did", "will",
                    "would", "could", "should", "may", "might", "must", "shall",
                    "can", "need", "dare", "ought", "used", "to", "of", "in",
                    "for", "on", "with", "at", "by", "from", "as", "into",
                    "through", "during", "before", "after", "above", "below",
                    "between", "under", "again", "further", "then", "once",
                    "what", "when", "where", "why", "how", "which", "who",
                    "whom", "this", "that", "these", "those", "it", "its"}
        return [w for w in words if w.lower() not in stopwords and len(w) > 2]

    def _determine_sources(self, task: str) -> List[str]:
        """Determine which sources to use."""
        sources = ["web_search"]  # Default

        if "arxiv" in task or "paper" in task:
            sources.append("arxiv")
        if "code" in task or "github" in task:
            sources.append("github")
        if "documentation" in task or "docs" in task:
            sources.append("documentation")

        return sources

    def _create_research_plan(self, research_type: str,
                            concepts: List[str],
                            sources: List[str]) -> Dict[str, Any]:
        """Create detailed research plan."""
        return {
            "steps": [
                {"action": "search", "source": sources[0], "query": " ".join(concepts[:5])},
                {"action": "analyze", "source": "results", "focus": "relevance"},
                {"action": "synthesize", "output": "summary"},
            ],
            "expected_sources": sources,
            "depth": "comprehensive" if research_type == "academic" else "standard",
        }

    async def act(self, thought_result: Dict[str, Any]) -> Any:
        """
        Execute research plan.

        Args:
            thought_result: Result from think()

        Returns:
            Research findings
        """
        plan = thought_result.get("plan", {})
        steps = plan.get("steps", [])

        findings = {
            "query": thought_result["analysis"]["query"],
            "research_type": thought_result["analysis"]["research_type"],
            "key_concepts": thought_result["analysis"]["key_concepts"],
            "sources_used": [],
            "results": [],
            "synthesis": "",
            "citations": [],
            "confidence": thought_result.get("confidence", 0.8),
        }

        for step in steps:
            action = step.get("action")
            if action == "search":
                # Simulate search results
                result = await self._perform_search(step)
                findings["results"].append(result)
                findings["sources_used"].append(step.get("source"))
            elif action == "analyze":
                # Analyze results
                findings["synthesis"] = self._synthesize_results(findings["results"])
            elif action == "cite":
                # Generate citations
                findings["citations"] = self._generate_citations(findings["results"])

        # Add final synthesis
        if not findings["synthesis"]:
            findings["synthesis"] = self._synthesize_results(findings["results"])

        return findings

    async def _perform_search(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform web search or database query.

        In production, this would call actual search APIs.
        """
        # Simulated search result
        query = step.get("query", "")
        return {
            "query": query,
            "source": step.get("source", "web_search"),
            "results": [
                {
                    "title": f"Research on {query}",
                    "url": "https://example.com/paper1",
                    "snippet": f"Summary of findings related to {query}...",
                    "relevance": 0.9,
                },
                {
                    "title": f"Recent advances in {query}",
                    "url": "https://example.com/paper2",
                    "snippet": f"Latest developments in {query}...",
                    "relevance": 0.85,
                },
            ],
            "timestamp": datetime.now().isoformat(),
        }

    def _synthesize_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Synthesize multiple search results into coherent summary.

        In production, this would use LLM for actual synthesis.
        """
        if not results:
            return "No results found."

        total_results = sum(len(r.get("results", [])) for r in results)
        sources = [r.get("source", "unknown") for r in results]

        synthesis = (
            f"Research completed. Found {total_results} relevant sources "
            f"from {', '.join(set(sources))}. "
            f"Key findings summarized from multiple sources."
        )

        return synthesis

    def _generate_citations(self, results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate citations for search results."""
        citations = []
        for i, result in enumerate(results):
            for j, item in enumerate(result.get("results", [])[:3]):
                citations.append({
                    "index": len(citations) + 1,
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "format": "APA",
                })
        return citations

    async def review(self, results: Dict[str, Any],
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review research results for quality assurance.

        Args:
            results: Research results to review
            context: Execution context

        Returns:
            Review feedback
        """
        quality_indicators = {
            "has_sources": bool(results.get("sources_used")),
            "has_synthesis": bool(results.get("synthesis")),
            "has_citations": bool(results.get("citations")),
            "result_count": len(results.get("results", [])),
        }

        quality_score = sum(quality_indicators.values()) / len(quality_indicators)

        suggestions = []
        if quality_score < 0.8:
            suggestions.append("Consider searching additional sources")
        if not results.get("citations"):
            suggestions.append("Add more citations to support findings")

        return {
            "quality_score": quality_score,
            "feedback": "Research completed" if quality_score >= 0.8 else "Research needs improvement",
            "suggestions": suggestions,
            "indicators": quality_indicators,
        }

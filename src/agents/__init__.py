"""Base agent class for all agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import time
import uuid

from src.core.message import Message


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str = "base_agent"
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    tools: List[Any] = field(default_factory=list)
    memory_enabled: bool = True
    self_reflection_enabled: bool = True
    max_iterations: int = 5


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    All agents inherit from this class and implement:
    - think(): Internal reasoning process
    - act(): Generate output/take action
    - learn(): Update from feedback

    Features:
    - Message-based communication
    - Memory management
    - Tool integration
    - Self-reflection
    - Performance tracking
    """

    def __init__(self, config: Optional[AgentConfig] = None, **kwargs):
        """
        Initialize base agent.

        Args:
            config: Agent configuration
            **kwargs: Additional config parameters (overrides config)
        """
        if config:
            self.config = config
        else:
            # Merge kwargs into default config
            default_config = AgentConfig(**kwargs)
            self.config = default_config

        self.name = self.config.name
        self._llm = None  # Lazy initialization
        self._memory: List[Dict[str, Any]] = []
        self._tool_registry: Dict[str, Callable] = {}
        self._execution_count = 0
        self._success_count = 0
        self._total_duration = 0.0
        self._created_at = time.time()

        # Register built-in tools
        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:
        """Register built-in agent tools."""
        # Override in subclasses to add specific tools
        pass

    @property
    def llm(self):
        """Lazy LLM initialization."""
        if self._llm is None:
            self._llm = self._initialize_llm()
        return self._llm

    def _initialize_llm(self):
        """Initialize LLM connection. Override in subclasses."""
        return None

    @abstractmethod
    async def think(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal reasoning process.

        Args:
            task: Task description
            context: Shared context

        Returns:
            Thought process result
        """
        pass

    @abstractmethod
    async def act(self, thought_result: Dict[str, Any]) -> Any:
        """
        Execute action based on thought.

        Args:
            thought_result: Result from think()

        Returns:
            Action result
        """
        pass

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a task end-to-end (think + act).

        Args:
            task: Task description
            context: Shared context

        Returns:
            Execution result
        """
        start_time = time.time()
        self._execution_count += 1

        context = context or {}
        context["agent_name"] = self.name

        try:
            # Think
            thought = await self.think(task, context)

            # Store in memory
            if self.config.memory_enabled:
                self._add_to_memory({
                    "type": "thought",
                    "task": task,
                    "thought": thought,
                    "timestamp": time.time(),
                })

            # Act
            result = await self.act(thought)

            # Record success
            self._success_count += 1
            self._total_duration += time.time() - start_time

            # Store result in memory
            if self.config.memory_enabled:
                self._add_to_memory({
                    "type": "action",
                    "task": task,
                    "result": result,
                    "timestamp": time.time(),
                })

            return result

        except Exception as e:
            self._total_duration += time.time() - start_time
            if self.config.self_reflection_enabled:
                await self._reflect_on_error(task, str(e))
            raise

    async def learn(self, feedback: Dict[str, Any]) -> None:
        """
        Learn from feedback.

        Args:
            feedback: Feedback containing success info, suggestions, etc.
        """
        if self.config.self_reflection_enabled:
            self._add_to_memory({
                "type": "feedback",
                "feedback": feedback,
                "timestamp": time.time(),
            })

    async def review(self, results: Dict[str, Any],
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and validate results (for ReviewerAgent primarily,
        but available to all for self-assessment).

        Args:
            results: Execution results to review
            context: Execution context

        Returns:
            Review feedback
        """
        # Default implementation - override in ReviewerAgent
        return {
            "quality_score": 0.8,
            "feedback": "Review complete",
            "suggestions": [],
        }

    def _add_to_memory(self, item: Dict[str, Any]) -> None:
        """Add item to agent's memory."""
        self._memory.append(item)
        # Limit memory size
        if len(self._memory) > 1000:
            self._memory = self._memory[-500:]

    def get_memory(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get agent's memory."""
        if limit:
            return self._memory[-limit:]
        return self._memory.copy()

    def clear_memory(self) -> None:
        """Clear agent's memory."""
        self._memory.clear()

    def register_tool(self, name: str, tool: Callable) -> None:
        """Register a tool for the agent to use."""
        self._tool_registry[name] = tool

    def unregister_tool(self, name: str) -> None:
        """Unregister a tool."""
        if name in self._tool_registry:
            del self._tool_registry[name]

    def list_tools(self) -> List[str]:
        """List registered tool names."""
        return list(self._tool_registry.keys())

    async def _reflect_on_error(self, task: str, error: str) -> None:
        """
        Self-reflection on errors.

        Analyzes what went wrong and stores lessons learned.
        """
        reflection = {
            "type": "reflection",
            "task": task,
            "error": error,
            "timestamp": time.time(),
            "lesson": f"Error in {self.name}: {error}",
        }
        self._add_to_memory(reflection)

    def get_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics."""
        return {
            "name": self.name,
            "execution_count": self._execution_count,
            "success_count": self._success_count,
            "success_rate": (
                self._success_count / self._execution_count
                if self._execution_count > 0 else 0.0
            ),
            "avg_duration": (
                self._total_duration / self._execution_count
                if self._execution_count > 0 else 0.0
            ),
            "memory_size": len(self._memory),
            "tools_available": len(self._tool_registry),
            "uptime": time.time() - self._created_at,
        }

    def reset_stats(self) -> None:
        """Reset performance statistics."""
        self._execution_count = 0
        self._success_count = 0
        self._total_duration = 0.0

    def send_message(self, receiver: str, content: Dict[str, Any],
                    message_queue: Any) -> None:
        """
        Send message to another agent.

        Args:
            receiver: Target agent name
            content: Message content
            message_queue: System message queue
        """
        message = Message(
            sender=self.name,
            receiver=receiver,
            content=content,
            msg_type=MessageType.REQUEST,
        )
        message_queue.put(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"

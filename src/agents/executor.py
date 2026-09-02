"""Executor Agent - action execution and tool invocation."""

from typing import Dict, Any, Optional, List
import time
import json

from src.agents.base_agent import BaseAgent, AgentConfig


class ExecutorAgent(BaseAgent):
    """
    Agent specialized in executing actions and invoking tools.

    Capabilities:
    - Code execution (Python, shell commands)
    - Tool selection and invocation
    - Result synthesis
    - Error handling and recovery
    - Multi-step action chaining

    Tools typically used:
    - CodeExecutor
    - WebSearchTool
    - FileOperationTool
    - APICallTool
    """

    def __init__(self, config: Optional[AgentConfig] = None, **kwargs):
        """
        Initialize Executor Agent.

        Args:
            config: Agent configuration
            **kwargs: Additional config parameters
        """
        if config is None:
            config = AgentConfig(name="executor", **kwargs)
        super().__init__(config)
        self.role = "executor"
        self.execution_history: List[Dict[str, Any]] = []
        self.tool_preferences: Dict[str, float] = {}

    async def think(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze task and determine execution approach.

        Args:
            task: Task description
            context: Shared context

        Returns:
            Thought process with execution plan
        """
        # Analyze what type of execution is needed
        execution_type = self._determine_execution_type(task)

        # Select appropriate tools
        tools = self._select_tools(task, execution_type)

        # Check for constraints
        constraints = self._parse_constraints(context)

        thought = {
            "task": task,
            "execution_type": execution_type,
            "selected_tools": tools,
            "constraints": constraints,
            "estimated_duration": self._estimate_execution_time(execution_type, tools),
        }

        return thought

    def _determine_execution_type(self, task: str) -> str:
        """Determine type of execution required."""
        task_lower = task.lower()

        if any(kw in task_lower for kw in ["run", "execute", "code", "script"]):
            return "code_execution"
        elif any(kw in task_lower for kw in ["search", "find", "lookup"]):
            return "search"
        elif any(kw in task_lower for kw in ["calculate", "compute", "analyze"]):
            return "computation"
        elif any(kw in task_lower for kw in ["write", "create", "generate"]):
            return "generation"
        else:
            return "general"

    def _select_tools(self, task: str, execution_type: str) -> List[Dict[str, Any]]:
        """Select appropriate tools for the task."""
        tool_templates = {
            "code_execution": [
                {"name": "python_executor", "priority": 1.0, "timeout": 60},
                {"name": "shell", "priority": 0.8, "timeout": 30},
            ],
            "search": [
                {"name": "web_search", "priority": 1.0, "timeout": 10},
                {"name": "file_search", "priority": 0.7, "timeout": 5},
            ],
            "computation": [
                {"name": "python_executor", "priority": 1.0, "timeout": 120},
                {"name": "calculator", "priority": 0.9, "timeout": 5},
            ],
            "generation": [
                {"name": "code_generator", "priority": 1.0, "timeout": 30},
                {"name": "template_engine", "priority": 0.8, "timeout": 10},
            ],
        }

        return tool_templates.get(execution_type, [{"name": "general", "priority": 0.5}])

    def _parse_constraints(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse constraints from context."""
        return {
            "timeout": context.get("timeout", 300),
            "max_retries": context.get("max_retries", 3),
            "output_format": context.get("output_format", "json"),
        }

    def _estimate_execution_time(self, execution_type: str, tools: List[Dict]) -> float:
        """Estimate execution time in seconds."""
        base_times = {
            "code_execution": 30,
            "search": 10,
            "computation": 20,
            "generation": 15,
            "general": 25,
        }
        base = base_times.get(execution_type, 25)
        return base * len(tools)

    async def act(self, thought_result: Dict[str, Any]) -> Any:
        """
        Execute the planned actions.

        Args:
            thought_result: Result from think()

        Returns:
            Execution results
        """
        execution_type = thought_result["execution_type"]
        tools = thought_result["selected_tools"]
        constraints = thought_result["constraints"]

        results = {
            "execution_type": execution_type,
            "tools_used": [],
            "actions": [],
            "output": None,
            "success": True,
            "duration": 0.0,
        }

        start_time = time.time()

        for tool in tools:
            tool_name = tool["name"]
            timeout = min(tool.get("timeout", 30), constraints.get("timeout", 300))

            try:
                result = await self._execute_tool(
                    tool_name, thought_result["task"], timeout
                )
                results["tools_used"].append(tool_name)
                results["actions"].append({
                    "tool": tool_name,
                    "success": True,
                    "result": result,
                })

                # Use first successful result as output
                if results["output"] is None:
                    results["output"] = result

            except Exception as e:
                results["actions"].append({
                    "tool": tool_name,
                    "success": False,
                    "error": str(e),
                })
                results["success"] = False

        results["duration"] = time.time() - start_time

        # Store in history
        self.execution_history.append(results)

        # Update tool preferences based on success
        self._update_tool_preferences(results)

        return results

    async def _execute_tool(self, tool_name: str, task: str, timeout: float) -> Any:
        """
        Execute a specific tool.

        Args:
            tool_name: Name of tool to execute
            task: Task description
            timeout: Execution timeout

        Returns:
            Tool execution result
        """
        # Simulated tool execution
        # In production, this would actually invoke the tools

        if tool_name == "python_executor":
            return await self._execute_python(task)
        elif tool_name == "web_search":
            return await self._web_search(task)
        elif tool_name == "calculator":
            return self._calculate(task)
        else:
            return {"status": "executed", "tool": tool_name, "task": task}

    async def _execute_python(self, task: str) -> Dict[str, Any]:
        """Execute Python code."""
        # In production, this would use a sandboxed executor
        # For now, simulate execution
        return {
            "status": "success",
            "output": "Code execution simulated",
            "language": "python",
        }

    async def _web_search(self, query: str) -> Dict[str, Any]:
        """Perform web search."""
        return {
            "status": "success",
            "results": [
                {"title": f"Result for {query}", "url": "https://example.com/1"}
            ],
            "query": query,
        }

    def _calculate(self, expression: str) -> Dict[str, Any]:
        """Perform calculation."""
        try:
            # Safe evaluation for demo - never do this in production!
            result = eval(expression.replace("=", ""))
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _update_tool_preferences(self, results: Dict[str, Any]) -> None:
        """Update tool preferences based on success/failure."""
        for action in results.get("actions", []):
            tool = action["tool"]
            success = action.get("success", False)

            if tool not in self.tool_preferences:
                self.tool_preferences[tool] = 0.5

            # Increase weight for success, decrease for failure
            delta = 0.1 if success else -0.1
            self.tool_preferences[tool] = max(0.1, min(1.0,
                self.tool_preferences[tool] + delta))

    async def review(self, results: Dict[str, Any],
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review execution results.

        Args:
            results: Execution results
            context: Execution context

        Returns:
            Review feedback
        """
        success_rate = sum(
            1 for a in results.get("actions", []) if a.get("success")
        ) / max(1, len(results.get("actions", [])))

        suggestions = []

        # Check tool effectiveness
        if self.tool_preferences:
            underperforming = [
                tool for tool, pref in self.tool_preferences.items()
                if pref < 0.3
            ]
            if underperforming:
                suggestions.append(f"Consider replacing tools: {underperforming}")

        return {
            "quality_score": success_rate,
            "feedback": "Execution completed" if success_rate > 0.8 else "Some actions failed",
            "suggestions": suggestions,
            "tool_preferences": self.tool_preferences.copy(),
        }

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {"total_executions": 0}

        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.get("success"))

        return {
            "total_executions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total,
            "tool_preferences": self.tool_preferences.copy(),
        }

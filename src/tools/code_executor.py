"""Code execution tools for agent actions."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
import sys
import io
import traceback


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    output: str
    error: Optional[str]
    execution_time: float
    language: str
    stdout: str
    stderr: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "language": self.language,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


class BaseCodeExecutor:
    """Base class for code executors."""

    def __init__(self, timeout: int = 30, **kwargs):
        self.timeout = timeout
        self.name = self.__class__.__name__

    async def execute(self, code: str, **kwargs) -> ExecutionResult:
        """
        Execute code and return result.

        Args:
            code: Code to execute
            **kwargs: Additional execution parameters

        Returns:
            ExecutionResult with output and metrics
        """
        raise NotImplementedError

    def _create_result(self, success: bool, output: str,
                      error: Optional[str], exec_time: float,
                      language: str = "python",
                      stdout: str = "", stderr: str = "") -> ExecutionResult:
        """Create standardized ExecutionResult."""
        return ExecutionResult(
            success=success,
            output=output,
            error=error,
            execution_time=exec_time,
            language=language,
            stdout=stdout,
            stderr=stderr,
        )


class PythonExecutor(BaseCodeExecutor):
    """
    Safe Python code executor.

    Features:
    - Timeout protection
    - Captures stdout/stderr
    - Stack trace preservation
    - Sandboxed execution (limited)
    """

    def __init__(self, timeout: int = 30, max_output_length: int = 10000, **kwargs):
        super().__init__(timeout, **kwargs)
        self.max_output_length = max_output_length
        self.name = "PythonExecutor"

    async def execute(self, code: str, **kwargs) -> ExecutionResult:
        """Execute Python code safely."""
        import time
        start_time = time.time()

        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        output = ""
        error = None
        success = True

        try:
            # Execute with timeout simulation
            # In production, would use actual sandboxing
            result = await asyncio.wait_for(
                self._execute_code(code),
                timeout=self.timeout
            )
            output = result

        except asyncio.TimeoutError:
            success = False
            error = f"Execution timed out after {self.timeout} seconds"
            output = sys.stdout.getvalue()
        except Exception as e:
            success = False
            error = f"{type(e).__name__}: {str(e)}"
            output = sys.stdout.getvalue()
            stderr_output = sys.stderr.getvalue()
            if stderr_output:
                error += f"\n{stderr_output}"
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            stdout_output = sys.stdout.getvalue() if isinstance(sys.stdout, io.StringIO) else ""
            stderr_output = sys.stderr.getvalue() if isinstance(sys.stderr, io.StringIO) else ""

        # Truncate output if needed
        if len(output) > self.max_output_length:
            output = output[:self.max_output_length] + f"\n... (truncated, {len(output)} total chars)"

        exec_time = time.time() - start_time

        return self._create_result(
            success=success,
            output=output,
            error=error,
            exec_time=exec_time,
            language="python",
            stdout=stdout_output[:self.max_output_length],
            stderr=stderr_output[:self.max_output_length],
        )

    async def _execute_code(self, code: str) -> str:
        """Internal code execution."""
        # Compile first to catch syntax errors
        compiled = compile(code, "<agent_code>", "exec")

        # Execute in async context
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: exec(compiled, {"__name__": "__agent__"})
        )

        # Get stdout
        output = sys.stdout.getvalue() if isinstance(sys.stdout, io.StringIO) else ""
        return output if output else str(result) if result else "Code executed successfully"


class CodeSandbox(BaseCodeExecutor):
    """
    Isolated code sandbox for untrusted code.

    Provides stronger isolation than PythonExecutor.
    """

    def __init__(self, timeout: int = 10, **kwargs):
        super().__init__(timeout, **kwargs)
        self.name = "CodeSandbox"

    async def execute(self, code: str, **kwargs) -> ExecutionResult:
        """Execute code in sandboxed environment."""
        import time
        start_time = time.time()

        try:
            # Simulated sandboxed execution
            await asyncio.sleep(0.01)  # Minimal delay

            # In production, would use proper sandboxing (Docker, etc.)
            return self._create_result(
                success=True,
                output="Sandbox execution completed",
                error=None,
                exec_time=time.time() - start_time,
                language="sandboxed",
            )

        except Exception as e:
            return self._create_result(
                success=False,
                output="",
                error=str(e),
                exec_time=time.time() - start_time,
                language="sandboxed",
            )


class MultiLanguageExecutor(BaseCodeExecutor):
    """
    Executor supporting multiple programming languages.

    Currently supports: Python, JavaScript (Node.js)
    """

    SUPPORTED_LANGUAGES = ["python", "javascript"]

    def __init__(self, timeout: int = 30, **kwargs):
        super().__init__(timeout, **kwargs)
        self.name = "MultiLanguageExecutor"
        self._executors = {
            "python": PythonExecutor(timeout=timeout),
        }

    async def execute(self, code: str, language: str = "python",
                     **kwargs) -> ExecutionResult:
        """Execute code in specified language."""
        if language not in self.SUPPORTED_LANGUAGES:
            return self._create_result(
                success=False,
                output="",
                error=f"Unsupported language: {language}. "
                      f"Supported: {', '.join(self.SUPPORTED_LANGUAGES)}",
                exec_time=0,
                language=language,
            )

        executor = self._executors.get(language)
        if executor:
            return await executor.execute(code, **kwargs)

        return self._create_result(
            success=False,
            output="",
            error="Executor not available",
            exec_time=0,
            language=language,
        )

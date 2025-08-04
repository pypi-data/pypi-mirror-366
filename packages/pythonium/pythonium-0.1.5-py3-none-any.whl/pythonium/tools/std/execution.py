"""
Command execution tools for the Pythonium framework.

Provides tools for executing system commands with proper output capture
and error handling.
"""

import asyncio
import logging
import os
import shlex
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from pythonium.common.base import Result
from pythonium.common.error_handling import handle_tool_error
from pythonium.common.parameters import validate_parameters
from pythonium.tools.base import (
    BaseTool,
    ParameterType,
    ToolContext,
    ToolMetadata,
    ToolParameter,
)

from .parameters import ExecuteCommandParams, ExecutePythonParams

# Configure logging
logger = logging.getLogger(__name__)

MAX_OUTPUT_SIZE = 10 * 1024 * 1024  # 10MB


class ExecuteCommandTool(BaseTool):
    """Tool for executing system commands with async support."""

    def __init__(self):
        super().__init__()
        self._running_processes: Dict[str, asyncio.subprocess.Process] = {}
        self._process_counter = 0

    async def initialize(self) -> None:
        """Initialize the tool."""
        logger.info("Initializing ExecuteCommandTool")
        pass

    async def shutdown(self) -> None:
        """Shutdown the tool and cleanup any running processes."""
        logger.info("Shutting down ExecuteCommandTool")
        # Clean up any running processes
        for process_id, process in self._running_processes.items():
            try:
                if process.returncode is None:
                    logger.warning(f"Terminating running process {process_id}")
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=5.0)
                    except asyncio.TimeoutError:
                        logger.warning(f"Force killing process {process_id}")
                        process.kill()
                        await process.wait()
            except Exception as e:
                logger.error(f"Error cleaning up process {process_id}: {e}")
        self._running_processes.clear()

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="execute_command",
            description="Execute a system command and return output with proper error handling. Supports command arguments, working directory, timeout, shell execution, environment variables, and stdin input.",
            brief_description="Execute a system command and return output",
            category="system",
            tags=[
                "command",
                "execute",
                "system",
                "shell",
                "process",
                "async",
            ],
            dangerous=True,  # Command execution is inherently dangerous
            parameters=[
                ToolParameter(
                    name="command",
                    type=ParameterType.STRING,
                    description="Command to execute",
                    required=True,
                ),
                ToolParameter(
                    name="args",
                    type=ParameterType.ARRAY,
                    description="Command arguments (alternative to including in command string)",
                    default=[],
                ),
                ToolParameter(
                    name="working_directory",
                    type=ParameterType.STRING,
                    description="Working directory for command execution",
                ),
                ToolParameter(
                    name="timeout",
                    type=ParameterType.INTEGER,
                    description="Timeout in seconds (max 300)",
                    default=30,
                    min_value=1,
                    max_value=300,
                ),
                ToolParameter(
                    name="capture_output",
                    type=ParameterType.BOOLEAN,
                    description="Capture stdout and stderr",
                    default=True,
                ),
                ToolParameter(
                    name="shell",
                    type=ParameterType.BOOLEAN,
                    description="Execute command through shell",
                    default=False,
                ),
                ToolParameter(
                    name="environment",
                    type=ParameterType.OBJECT,
                    description="Environment variables to set (merged with current env)",
                    default={},
                ),
                ToolParameter(
                    name="stdin",
                    type=ParameterType.STRING,
                    description="Input to send to command's stdin",
                ),
            ],
        )

    @validate_parameters(ExecuteCommandParams)
    @handle_tool_error
    async def execute(
        self, parameters: ExecuteCommandParams, context: ToolContext
    ) -> Result:
        """Execute the command with async support."""
        try:
            progress_callback = getattr(context, "progress_callback", None)
            process_id = f"cmd_{self._process_counter}"
            self._process_counter += 1

            # Validate and prepare execution parameters
            validation_result = self._validate_parameters(parameters)
            if not validation_result.success:
                return validation_result

            if progress_callback:
                progress_callback(
                    f"🚀 Starting command execution: {parameters.command}"
                )

            # Prepare command and environment
            cmd = self._prepare_command(parameters)
            env = self._prepare_environment(parameters.environment)
            cwd = self._validate_working_directory(parameters.working_directory)

            # Execute command with proper async handling
            start_time = datetime.now()
            try:
                result = await self._execute_async_subprocess(
                    cmd, parameters, env, cwd, progress_callback, process_id
                )
            finally:
                # Cleanup process tracking
                self._running_processes.pop(process_id, None)

            # Process and return result
            return self._process_result(
                result, parameters, progress_callback, start_time
            )

        except asyncio.TimeoutError:
            error_msg = f"Command timed out after {parameters.timeout} seconds"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(f"⏰ {error_msg}")
            return Result.error_result(error_msg)
        except FileNotFoundError:
            error_msg = f"Command not found: {parameters.command}"
            logger.error(error_msg)
            return Result.error_result(error_msg)
        except PermissionError as e:
            error_msg = f"Permission denied: {e}"
            logger.error(error_msg)
            return Result.error_result(error_msg)
        except Exception as e:
            error_msg = f"Command execution failed: {e}"
            logger.error(error_msg)
            return Result.error_result(error_msg)

    def _prepare_command(
        self, parameters: ExecuteCommandParams
    ) -> Union[str, List[str]]:
        """Prepare command for execution."""
        command = parameters.command.strip()
        args = parameters.args or []

        if args:
            # Use command and args separately
            return [command] + args
        elif parameters.shell:
            # Use shell command as string
            return command
        else:
            # Split command string into components
            try:
                return shlex.split(command)
            except ValueError as e:
                logger.error(f"Failed to parse command: {e}")
                # Fallback to simple split if shlex fails
                return command.split()

    def _prepare_environment(
        self, environment: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """Prepare environment variables."""
        env = os.environ.copy()
        if environment:
            env.update(environment)
        return env

    async def _execute_async_subprocess(
        self,
        cmd: Union[str, List[str]],
        parameters: ExecuteCommandParams,
        env: Dict[str, str],
        cwd: Optional[str],
        progress_callback: Optional[Callable[[str], None]],
        process_id: str,
    ) -> Dict[str, Union[str, int, float]]:
        """Execute subprocess using asyncio with proper monitoring and cleanup."""

        if progress_callback:
            progress_callback("🔄 Creating subprocess...")

        # Create subprocess
        process = await self._create_subprocess(cmd, parameters, env, cwd)

        # Track the process
        self._running_processes[process_id] = process

        if progress_callback:
            progress_callback(f"Process started (PID: {process.pid})")

        try:
            return await self._handle_subprocess_execution(process, parameters)

        except asyncio.TimeoutError:
            await self._handle_subprocess_timeout(
                process, parameters, progress_callback
            )
            raise asyncio.TimeoutError(
                f"Command timed out after {parameters.timeout} seconds"
            )

    async def _create_subprocess(
        self,
        cmd: Union[str, List[str]],
        parameters: ExecuteCommandParams,
        env: Dict[str, str],
        cwd: Optional[str],
    ) -> asyncio.subprocess.Process:
        """Create subprocess based on parameters."""
        if parameters.shell and isinstance(cmd, str):
            return await asyncio.create_subprocess_shell(
                cmd,
                stdin=asyncio.subprocess.PIPE if parameters.stdin else None,
                stdout=asyncio.subprocess.PIPE if parameters.capture_output else None,
                stderr=asyncio.subprocess.PIPE if parameters.capture_output else None,
                cwd=cwd,
                env=env,
            )
        else:
            if isinstance(cmd, str):
                cmd = shlex.split(cmd)
            return await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE if parameters.stdin else None,
                stdout=asyncio.subprocess.PIPE if parameters.capture_output else None,
                stderr=asyncio.subprocess.PIPE if parameters.capture_output else None,
                cwd=cwd,
                env=env,
            )

    async def _handle_subprocess_execution(
        self, process: asyncio.subprocess.Process, parameters: ExecuteCommandParams
    ) -> Dict[str, Union[str, int, float]]:
        """Handle subprocess execution and output capture."""
        stdin_data = parameters.stdin.encode() if parameters.stdin else None

        if parameters.capture_output:
            return await self._execute_with_output_capture(
                process, parameters, stdin_data
            )
        else:
            return await self._execute_without_output_capture(
                process, parameters, stdin_data
            )

    async def _execute_with_output_capture(
        self,
        process: asyncio.subprocess.Process,
        parameters: ExecuteCommandParams,
        stdin_data: Optional[bytes],
    ) -> Dict[str, Union[str, int, float]]:
        """Execute subprocess with output capture."""
        stdout_data, stderr_data = await asyncio.wait_for(
            process.communicate(input=stdin_data), timeout=parameters.timeout
        )

        # Check output size limits
        stdout_data = self._truncate_output_if_needed(stdout_data, "stdout")
        stderr_data = self._truncate_output_if_needed(stderr_data, "stderr")

        return {
            "stdout": stdout_data.decode(errors="replace") if stdout_data else "",
            "stderr": stderr_data.decode(errors="replace") if stderr_data else "",
            "returncode": process.returncode or 0,
            "pid": process.pid,
        }

    async def _execute_without_output_capture(
        self,
        process: asyncio.subprocess.Process,
        parameters: ExecuteCommandParams,
        stdin_data: Optional[bytes],
    ) -> Dict[str, Union[str, int, float]]:
        """Execute subprocess without output capture."""
        if stdin_data and process.stdin:
            process.stdin.write(stdin_data)
            process.stdin.close()

        await asyncio.wait_for(process.wait(), timeout=parameters.timeout)

        return {
            "returncode": process.returncode or 0,
            "pid": process.pid,
        }

    def _truncate_output_if_needed(
        self, output_data: Optional[bytes], output_type: str
    ) -> bytes:
        """Truncate output if it exceeds size limits."""
        if output_data and len(output_data) > MAX_OUTPUT_SIZE:
            logger.warning(
                f"{output_type} output truncated (exceeded {MAX_OUTPUT_SIZE} bytes)"
            )
            return output_data[:MAX_OUTPUT_SIZE] + b"\n[OUTPUT TRUNCATED]"
        return output_data or b""

    async def _handle_subprocess_timeout(
        self,
        process: asyncio.subprocess.Process,
        parameters: ExecuteCommandParams,
        progress_callback: Optional[Callable[[str], None]],
    ) -> None:
        """Handle subprocess timeout by terminating the process."""
        if progress_callback:
            progress_callback(f"⏰ Process timeout, terminating (PID: {process.pid})")

        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            if progress_callback:
                progress_callback(f"💀 Force killing process (PID: {process.pid})")
            process.kill()
            await process.wait()

    def _process_result(
        self,
        result: Dict[str, Union[str, int, float]],
        parameters: ExecuteCommandParams,
        progress_callback: Optional[Callable[[str], None]],
        start_time: datetime,
    ) -> Result:
        """Process subprocess result and return appropriate Result with enhanced information."""
        execution_time = (datetime.now() - start_time).total_seconds()
        returncode = result.get("returncode", -1)
        pid = result.get("pid", "unknown")

        # Build comprehensive output data
        output_data = {
            "returncode": returncode,
            "execution_time": execution_time,
            "pid": pid,
            "command": parameters.command,
            "timestamp": start_time.isoformat(),
        }

        if parameters.capture_output:
            stdout_str = str(result.get("stdout", ""))
            stderr_str = str(result.get("stderr", ""))
            output_data.update(
                {
                    "stdout": stdout_str,
                    "stderr": stderr_str,
                    "stdout_size": len(stdout_str),
                    "stderr_size": len(stderr_str),
                }
            )

        # Enhanced progress reporting
        if progress_callback:
            status_text = "SUCCESS" if returncode == 0 else "FAILED"
            progress_callback(
                f"{status_text} Command completed in {execution_time:.2f}s "
                f"(PID: {pid}, exit code: {returncode})"
            )

        # Log execution details for audit
        logger.info(
            f"Command executed: {parameters.command} "
            f"(PID: {pid}, exit code: {returncode}, time: {execution_time:.2f}s)"
        )

        # Check if command was successful
        if returncode != 0:
            error_msg = f"Command failed with exit code {returncode}"
            if parameters.capture_output and result.get("stderr"):
                error_msg += f": {result['stderr']}"

            logger.error(f"Command failed: {error_msg}")
            return Result.error_result(error_msg, metadata=output_data)

        return Result.success_result(output_data)

    def _validate_parameters(self, parameters: ExecuteCommandParams) -> Result:
        """Validate execution parameters for safety and correctness."""
        # Validate timeout
        if parameters.timeout > 300:
            return Result.error_result("Timeout cannot exceed 300 seconds for safety")

        if parameters.timeout < 1:
            return Result.error_result("Timeout must be at least 1 second")

        # Validate command
        if not parameters.command.strip():
            return Result.error_result("Command cannot be empty")

        # Validate working directory if provided
        if parameters.working_directory:
            try:
                path = Path(parameters.working_directory)
                if not path.exists():
                    return Result.error_result(
                        f"Working directory does not exist: {parameters.working_directory}"
                    )
                if not path.is_dir():
                    return Result.error_result(
                        f"Working directory is not a directory: {parameters.working_directory}"
                    )
            except Exception as e:
                return Result.error_result(f"Invalid working directory: {e}")

        return Result.success_result("Parameters validated")

    def _validate_working_directory(
        self, working_directory: Optional[str]
    ) -> Optional[str]:
        """Validate and normalize working directory path."""
        if not working_directory:
            return None

        path = Path(working_directory)
        if path.exists() and path.is_dir():
            return str(path.resolve())
        return None


class ExecutePythonTool(BaseTool):
    """Simplified Python execution tool for running Python code via stdin.

    This is a convenience wrapper around ExecuteCommandTool that automatically
    uses the current Python interpreter and passes code via stdin. For more
    complex Python execution scenarios, use ExecuteCommandTool directly.
    """

    def __init__(self):
        super().__init__()
        self._command_executor = ExecuteCommandTool()

    async def initialize(self) -> None:
        """Initialize the tool and its dependencies."""
        await self._command_executor.initialize()

    async def shutdown(self) -> None:
        """Shutdown the tool and cleanup."""
        await self._command_executor.shutdown()

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="execute_python",
            description="Execute Python code using current interpreter (python -c)",
            brief_description="Execute Python code",
            category="system",
            tags=[
                "python",
                "execute",
                "code",
                "script",
                "interpreter",
                "convenience",
            ],
            dangerous=True,  # Code execution is inherently dangerous
            parameters=[
                ToolParameter(
                    name="code",
                    type=ParameterType.STRING,
                    description="Python code to execute",
                    required=True,
                ),
                ToolParameter(
                    name="working_directory",
                    type=ParameterType.STRING,
                    description="Working directory for execution",
                    required=False,
                ),
                ToolParameter(
                    name="timeout",
                    type=ParameterType.INTEGER,
                    description="Execution timeout in seconds (max 300)",
                    default=30,
                    min_value=1,
                    max_value=300,
                ),
                ToolParameter(
                    name="capture_output",
                    type=ParameterType.BOOLEAN,
                    description="Capture stdout and stderr",
                    default=True,
                ),
                ToolParameter(
                    name="environment",
                    type=ParameterType.OBJECT,
                    description="Additional environment variables",
                    default={},
                ),
            ],
        )

    @validate_parameters(ExecutePythonParams)
    @handle_tool_error
    async def execute(
        self, params: ExecutePythonParams, context: ToolContext
    ) -> Result[Any]:
        """Execute Python code via python -c."""
        import sys

        # Get current Python executable
        python_executable = sys.executable

        # Create parameters dictionary for ExecuteCommandTool
        cmd_params = {
            "command": python_executable,
            "args": ["-c", params.code],
            "working_directory": params.working_directory,
            "timeout": params.timeout,
            "capture_output": params.capture_output,
            "shell": False,
            "environment": params.environment,
            "stdin": None,  # We use -c instead of stdin
        }

        # Execute using ExecuteCommandTool
        cmd_tool = ExecuteCommandTool()
        result = await cmd_tool.execute(cmd_params, context)

        # Enhance result with Python-specific information
        if result.success:
            result.data["python_executable"] = python_executable
            result.data["execution_type"] = "python_code"

        return result  # type: ignore[no-any-return]

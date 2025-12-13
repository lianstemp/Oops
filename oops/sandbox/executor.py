"""Tool executor for running commands in Docker sandbox.

This module provides functionality to execute pentesting tools either in the
Docker sandbox or locally, with automatic fallback.
"""

import os
import subprocess
from typing import Optional, Tuple, List
from .client import SandboxClient


class SandboxExecutor:
    """Executor for running tools in the Docker sandbox."""
    
    def __init__(self, sandbox_client: Optional[SandboxClient] = None):
        """Initialize the executor.
        
        Args:
            sandbox_client: SandboxClient instance (creates new if None)
        """
        self.sandbox_client = sandbox_client or SandboxClient()
        self.sandbox_enabled = os.getenv("SANDBOX_ENABLED", "true").lower() == "true"
    
    def execute(
        self,
        command: List[str],
        use_sandbox: bool = True,
        timeout: Optional[int] = None,
        capture_output: bool = True
    ) -> Tuple[int, str, str]:
        """Execute a command, preferably in the sandbox.
        
        Args:
            command: Command and arguments as list
            use_sandbox: Whether to try using sandbox
            timeout: Command timeout in seconds
            capture_output: Whether to capture stdout/stderr
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        # Determine execution location
        should_use_sandbox = (
            use_sandbox and 
            self.sandbox_enabled and 
            self.sandbox_client.is_available() and
            self.sandbox_client.ensure_running()
        )
        
        if should_use_sandbox:
            return self._execute_in_sandbox(command, timeout, capture_output)
        else:
            return self._execute_locally(command, timeout, capture_output)
    
    def _execute_in_sandbox(
        self,
        command: List[str],
        timeout: Optional[int],
        capture_output: bool
    ) -> Tuple[int, str, str]:
        """Execute command in Docker sandbox using docker exec.
        
        Args:
            command: Command and arguments as list
            timeout: Command timeout in seconds
            capture_output: Whether to capture stdout/stderr
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        # Build docker exec command
        docker_cmd = [
            "docker", "exec",
            self.sandbox_client.container_name,
        ] + command
        
        try:
            if capture_output:
                result = subprocess.run(
                    docker_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(
                    docker_cmd,
                    timeout=timeout
                )
                return result.returncode, "", ""
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", f"Execution failed: {str(e)}"
    
    def _execute_locally(
        self,
        command: List[str],
        timeout: Optional[int],
        capture_output: bool
    ) -> Tuple[int, str, str]:
        """Execute command locally on host.
        
        Args:
            command: Command and arguments as list
            timeout: Command timeout in seconds
            capture_output: Whether to capture stdout/stderr
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(
                    command,
                    timeout=timeout
                )
                return result.returncode, "", ""
        except FileNotFoundError:
            return -1, "", f"Command not found: {command[0]}"
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", f"Execution failed: {str(e)}"
    
    def is_sandbox_active(self) -> bool:
        """Check if sandbox is currently active and usable.
        
        Returns:
            True if sandbox is active, False otherwise
        """
        return (
            self.sandbox_enabled and
            self.sandbox_client.is_available() and
            self.sandbox_client.is_running()
        )


# Global executor instance
_executor: Optional[SandboxExecutor] = None


def get_executor() -> SandboxExecutor:
    """Get or create the global executor instance.
    
    Returns:
        SandboxExecutor instance
    """
    global _executor
    if _executor is None:
        _executor = SandboxExecutor()
    return _executor


def execute_tool(
    command: List[str],
    use_sandbox: bool = True,
    timeout: Optional[int] = None
) -> Tuple[int, str, str]:
    """Convenience function to execute a tool command.
    
    Args:
        command: Command and arguments as list
        use_sandbox: Whether to try using sandbox
        timeout: Command timeout in seconds
    
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    executor = get_executor()
    return executor.execute(command, use_sandbox, timeout)

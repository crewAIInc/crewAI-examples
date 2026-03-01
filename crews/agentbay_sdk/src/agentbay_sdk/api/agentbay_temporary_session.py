import os
import shlex
from typing import Optional, Dict

from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams


class AgentBayTemporarySession:
    """
    AgentBay SDK wrapper for temporary session operations.

    Each method creates a fresh session, performs the operation, and cleans up automatically.
    Suitable for one-off operations that don't require state persistence.

    Operations:
    - Execute code (python/javascript) via CodeSpace
    - Execute shell commands
    - Read/Write files (prefer native API with shell fallbacks)
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AGENTBAY_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "AGENTBAY_API_KEY not configured. Please set environment variable or pass api_key to constructor"
            )
        self._client = AgentBay(api_key=self.api_key)

    def create_session(self, labels: Optional[Dict[str, str]] = None, image_id: str = "code_latest"):
        """Create a temporary session. Internal method used by other methods."""
        params = CreateSessionParams(image_id=image_id)
        if labels:
            params.labels = labels
        result = self._client.create(params)
        if not result.success:
            raise RuntimeError(f"Failed to create session: {result.error_message}")
        return result.session

    def delete_session(self, session) -> None:
        """Delete a session. Internal method used by other methods."""
        _ = self._client.delete(session)

    def run_code(
        self,
        code: str,
        language: str = "python",
        timeout_s: int = 60,
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        """Execute code in a temporary session and return the result.

        Creates a fresh session, runs the code, and cleans up automatically.

        Args:
            code: The code to execute
            language: Programming language ("python" or "javascript")
            timeout_s: Execution timeout in seconds (default: 60)
            labels: Optional session labels

        Returns:
            Execution result as string
        """
        session = self.create_session(labels=labels)
        try:
            exec_result = session.code.run_code(  # type: ignore[attr-defined]
                code=code, language=language, timeout_s=timeout_s
            )
            if not exec_result.success:
                raise RuntimeError(exec_result.error_message)
            return exec_result.result
        finally:
            self.delete_session(session)

    def run_command(
        self,
        command: str,
        timeout_s: int = 60,
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        """Execute a shell command in a temporary session and return stdout.

        Creates a fresh session, runs the command, and cleans up automatically.

        Note: This uses the default image suitable for shell. For code-oriented tasks,
        prefer run_code with code_latest image.

        Args:
            command: The shell command to execute
            timeout_s: Execution timeout in seconds (default: 60)
            labels: Optional session labels

        Returns:
            Command output as string
        """
        session = self.create_session(labels=labels)
        try:
            result = session.command.execute_command(command, timeout_ms=timeout_s * 1000)  # type: ignore[attr-defined]
            if hasattr(result, "success") and not result.success:
                raise RuntimeError(getattr(result, "error_message", "command failed"))
            return getattr(result, "output", getattr(result, "stdout", str(result)))
        finally:
            self.delete_session(session)

    def read_file(
        self,
        path: str,
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        """Read file content from a temporary session.

        Creates a fresh session, reads the file, and cleans up automatically.
        Prefers native file API, falls back to shell `cat` command.

        Args:
            path: The path to the file to read
            labels: Optional session labels

        Returns:
            File content as string
        """
        session = self.create_session(labels=labels)
        try:
            file_api = getattr(session, "file", None)
            if file_api is not None and hasattr(file_api, "read"):
                return file_api.read(path)  # type: ignore[call-arg]
            # Fallback via shell
            result = session.command.execute_command(f"cat {shlex.quote(path)}", timeout_ms=60 * 1000)  # type: ignore[attr-defined]
            if hasattr(result, "success") and not result.success:
                raise RuntimeError(getattr(result, "error_message", "read failed"))
            return getattr(result, "output", getattr(result, "stdout", str(result)))
        finally:
            self.delete_session(session)

    def write_file(
        self,
        path: str,
        content: str,
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        """Write file content to a temporary session.

        Creates a fresh session, writes the file, and cleans up automatically.
        Prefers native file API, falls back to shell redirection.

        Args:
            path: The path to the file to write
            content: The content to write
            labels: Optional session labels

        Returns:
            "ok" on success
        """
        session = self.create_session(labels=labels)
        try:
            file_api = getattr(session, "file", None)
            if file_api is not None and hasattr(file_api, "write"):
                file_api.write(path, content)  # type: ignore[call-arg]
                return "ok"
            # Fallback via shell (safely echo using EOF to preserve content)
            heredoc = f"cat > {shlex.quote(path)} << 'EOF'\n{content}\nEOF"
            result = session.command.execute_command(heredoc, timeout_ms=60 * 1000)  # type: ignore[attr-defined]
            if hasattr(result, "success") and not result.success:
                raise RuntimeError(getattr(result, "error_message", "write failed"))
            return "ok"
        finally:
            self.delete_session(session)

import os
import shlex
from typing import Optional, Dict, List

from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams


class AgentBayPersistentSession:
    """
    AgentBay SDK wrapper for persistent session operations.

    Manages long-lived sessions that can be reused across multiple operations.
    Suitable for multi-step workflows that require state persistence.

    Operations:
    - Create/delete persistent sessions
    - Execute commands in existing sessions
    - Read/Write files in existing sessions
    - Upload/Download files to/from sessions
    - Get service links (HTTPS/WSS/CDP) from sessions
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AGENTBAY_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "AGENTBAY_API_KEY not configured. Please set environment variable or pass api_key to constructor"
            )
        self._client = AgentBay(api_key=self.api_key)
        # Keep persistent sessions for multi-step flows
        self._sessions: Dict[str, object] = {}

    def _create_session(self, labels: Optional[Dict[str, str]] = None, image_id: str = "code_latest"):
        """Internal method to create a session."""
        params = CreateSessionParams(image_id=image_id)
        if labels:
            params.labels = labels
        result = self._client.create(params)
        if not result.success:
            raise RuntimeError(f"Failed to create session: {result.error_message}")
        return result.session

    def _delete_session(self, session) -> None:
        """Internal method to delete a session."""
        _ = self._client.delete(session)

    def create_persistent_session(self, labels: Optional[Dict[str, str]] = None) -> str:
        """Create a persistent session and return its ID.

        The session will be kept alive until explicitly deleted.
        Use this for multi-step workflows that require state persistence.

        Args:
            labels: Optional session labels

        Returns:
            Session ID as string
        """
        session = self._create_session(labels=labels)
        session_id = getattr(session, "session_id", None) or getattr(session, "id", None)
        if session_id is None:
            # Fallback to python object id if SDK has no id exposed
            session_id = str(id(session))
        self._sessions[str(session_id)] = session
        return str(session_id)

    def delete_persistent_session(self, session_id: str) -> None:
        """Delete a persistent session by its ID.

        Args:
            session_id: The ID of the session to delete
        """
        session = self._sessions.pop(session_id, None)
        if session is not None:
            self._delete_session(session)

    def _require_session(self, session_id: str):
        """Internal method to get a session by ID, raising error if not found."""
        session = self._sessions.get(session_id)
        if session is None:
            raise RuntimeError(f"Session {session_id} not found. Create it first.")
        return session

    def run_command_in_session(self, session_id: str, command: str, timeout_s: int = 60) -> str:
        """Execute a shell command in an existing persistent session.

        Args:
            session_id: The ID of the persistent session
            command: The shell command to execute
            timeout_s: Execution timeout in seconds (default: 60)

        Returns:
            Command output as string
        """
        session = self._require_session(session_id)
        result = session.command.execute_command(command, timeout_ms=timeout_s * 1000)  # type: ignore[attr-defined]
        if hasattr(result, "success") and not result.success:
            raise RuntimeError(getattr(result, "error_message", "command failed"))
        return getattr(result, "output", getattr(result, "stdout", str(result)))

    def write_file_in_session(self, session_id: str, path: str, content: str) -> str:
        """Write file content to an existing persistent session.

        Args:
            session_id: The ID of the persistent session
            path: The path to the file to write
            content: The content to write

        Returns:
            "ok" on success
        """
        session = self._require_session(session_id)
        file_api = getattr(session, "file", None)
        if file_api is not None and hasattr(file_api, "write"):
            file_api.write(path, content)  # type: ignore[call-arg]
            return "ok"
        # Ensure directory exists before writing file
        dir_path = os.path.dirname(path)
        if dir_path:
            mkdir_result = session.command.execute_command(f"mkdir -p {shlex.quote(dir_path)}", timeout_ms=60 * 1000)  # type: ignore[attr-defined]
            if hasattr(mkdir_result, "success") and not mkdir_result.success:
                # Directory creation failed, but try to write anyway
                pass
        heredoc = f"cat > {shlex.quote(path)} << 'EOF'\n{content}\nEOF"
        result = session.command.execute_command(heredoc, timeout_ms=60 * 1000)  # type: ignore[attr-defined]
        if hasattr(result, "success") and not result.success:
            raise RuntimeError(getattr(result, "error_message", "write failed"))
        return "ok"

    def read_file_in_session(self, session_id: str, path: str) -> str:
        """Read file content from an existing persistent session.

        Args:
            session_id: The ID of the persistent session
            path: The path to the file to read

        Returns:
            File content as string
        """
        session = self._require_session(session_id)
        file_api = getattr(session, "file", None)
        if file_api is not None and hasattr(file_api, "read"):
            return file_api.read(path)  # type: ignore[call-arg]
        result = session.command.execute_command(f"cat {shlex.quote(path)}", timeout_ms=60 * 1000)  # type: ignore[attr-defined]
        if hasattr(result, "success") and not result.success:
            raise RuntimeError(getattr(result, "error_message", "read failed"))
        return getattr(result, "output", getattr(result, "stdout", str(result)))

    def upload_file(self, session_id: str, local_path: str, remote_path: str) -> str:
        """Upload a file from local host to remote session.

        If SDK has native upload, prefer it; else fallback to reading locally and writing into session.

        Args:
            session_id: The ID of the persistent session
            local_path: Local file path
            remote_path: Remote file path in the session

        Returns:
            "ok" on success, or error message string on failure
        """
        session = self._require_session(session_id)
        file_api = getattr(session, "file", None)
        if file_api is not None and hasattr(file_api, "upload"):
            try:
                file_api.upload(local_path, remote_path)  # type: ignore[call-arg]
                return "ok"
            except Exception as e:
                return f"Upload failed: {str(e)}"
        # Fallback: read local text and write
        try:
            if not os.path.exists(local_path):
                return f"Error: Local file not found: {local_path}. Use write_file_in_session with content instead."
            with open(local_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.write_file_in_session(session_id, remote_path, content)
        except FileNotFoundError:
            return f"Error: Local file not found: {local_path}. Use write_file_in_session with content instead."
        except Exception as e:
            return f"Upload failed: {str(e)}"

    def upload_files(self, session_id: str, files: List[Dict[str, str]]) -> str:
        """Upload multiple files to a persistent session.

        Args:
            session_id: The ID of the persistent session
            files: List of file dictionaries, each with 'local_path' and 'remote_path'

        Returns:
            Summary message with success/failure counts
        """
        success_count = 0
        failed_files = []
        for item in files:
            local_path = item.get("local_path", "")
            remote_path = item.get("remote_path", "")
            result = self.upload_file(session_id, local_path, remote_path)
            if result == "ok":
                success_count += 1
            else:
                failed_files.append(f"{local_path}: {result}")
        if failed_files:
            return f"Uploaded {success_count}/{len(files)} files. Failed: {'; '.join(failed_files[:3])}" + (f" and {len(failed_files)-3} more" if len(failed_files) > 3 else "")
        return f"Successfully uploaded {success_count} files."

    def download_file(self, session_id: str, remote_path: str, local_path: str) -> str:
        """Download a file from a persistent session to local host.

        Args:
            session_id: The ID of the persistent session
            remote_path: Remote file path in the session
            local_path: Local file path to save

        Returns:
            "ok" on success
        """
        session = self._require_session(session_id)
        file_api = getattr(session, "file", None)
        if file_api is not None and hasattr(file_api, "download"):
            file_api.download(remote_path, local_path)  # type: ignore[call-arg]
            return "ok"
        content = self.read_file_in_session(session_id, remote_path)
        os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content)
        return "ok"

    def get_link_in_session(
        self,
        session_id: str,
        protocol_type: Optional[str] = None,
        port: Optional[int] = None,
    ) -> str:
        """Get a local-accessible URL for a service running in the cloud session.

        Args:
            session_id: The ID of the persistent session
            protocol_type: Protocol type, either "https" or "wss".
            port: Port number in range [30100, 30199] for the service. Required if protocol_type is specified.
                  For example, use port=30123 for a service running on port 30123.

        Returns:
            URL string (HTTPS, WSS, or CDP endpoint)

        Raises:
            ValueError: If validation fails
            RuntimeError: If session not found or get_link fails
        """
        session = self._require_session(session_id)

        # Validation: if protocol_type is specified, port must be provided
        if protocol_type is not None and port is None:
            raise ValueError("protocol_type requires port parameter")

        # Validation: port must be in valid range [30100, 30199]
        if port is not None and not (30100 <= port <= 30199):
            raise ValueError(f"Port {port} outside valid range [30100, 30199]")

        # Call session.get_link()
        try:
            if protocol_type is None and port is None:
                result = session.get_link()  # type: ignore[attr-defined]
            elif protocol_type is not None and port is not None:
                # HTTPS or WSS service
                result = session.get_link(protocol_type=protocol_type, port=port)  # type: ignore[attr-defined]
            else:
                # Only port specified (WebSocket)
                result = session.get_link(port=port)  # type: ignore[attr-defined]

            # Check result
            if not result.success:
                error_msg = getattr(result, "error_message", "get_link failed")
                raise RuntimeError(f"Failed to get link: {error_msg}")

            # Extract URL from result
            url = getattr(result, "data", None) or getattr(result, "url", None)
            if url is None:
                raise RuntimeError("get_link returned no URL data")

            return str(url)
        except AttributeError as e:
            raise RuntimeError(f"Session does not support get_link: {e}") from e


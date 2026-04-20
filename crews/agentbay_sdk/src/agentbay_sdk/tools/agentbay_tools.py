from typing import Optional, Dict, Type, List
import os
from crewai.tools import BaseTool
from pydantic import Field
from .tool_schemas import (
    AgentBayRunCodeInput,
    AgentBayRunCommandInput,
    AgentBayReadFileInput,
    AgentBayWriteFileInput,
    AgentBayCreateSessionInput,
    AgentBayDeleteSessionInput,
    AgentBayRunInSessionInput,
    AgentBayWriteInSessionInput,
    AgentBayReadInSessionInput,
    AgentBayUploadFileInput,
    AgentBayUploadFilesInput,
    AgentBayDownloadFileInput,
    AgentBayGetLinkInput,
)
from ..api.agentbay_temporary_session import AgentBayTemporarySession
from ..api.agentbay_persistent_session import AgentBayPersistentSession


_temporary_session: Optional[AgentBayTemporarySession] = None
_persistent_session: Optional[AgentBayPersistentSession] = None


def _get_temporary_session() -> AgentBayTemporarySession:
    """Get singleton instance of AgentBayTemporarySession for temporary session operations."""
    global _temporary_session
    if _temporary_session is None:
        _temporary_session = AgentBayTemporarySession()
    return _temporary_session


def _get_persistent_session() -> AgentBayPersistentSession:
    """Get singleton instance of AgentBayPersistentSession for persistent session operations."""
    global _persistent_session
    if _persistent_session is None:
        _persistent_session = AgentBayPersistentSession()
    return _persistent_session


class AgentBayRunCodeTool(BaseTool):
    name: str = "agentbay_run_code"
    description: str = (
        "Execute code (python/javascript) in AgentBay cloud session and return stdout text. "
        "Input should include: code (the code to execute), language (python or javascript, default: python), "
        "timeout_s (execution timeout in seconds, default: 60), and optional labels (dict)."
    )
    args_schema: Type[AgentBayRunCodeInput] = AgentBayRunCodeInput

    def _run(
        self,
        code: str,
        language: str = "python",
        timeout_s: int = 60,
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        """Execute code in AgentBay cloud session."""
        temporary = _get_temporary_session()
        return temporary.run_code(
            code=code,
            language=language,
            timeout_s=timeout_s,
            labels=labels,
        )


# Create a singleton instance
agentbay_run_code = AgentBayRunCodeTool()


class AgentBayRunCommandTool(BaseTool):
    name: str = "agentbay_run_command"
    description: str = (
        "Execute a shell command in AgentBay cloud session and return stdout text. "
        "Input: command (string), timeout_s (default 60), optional labels (dict)."
    )
    args_schema: Type[AgentBayRunCommandInput] = AgentBayRunCommandInput

    def _run(
        self,
        command: str,
        timeout_s: int = 60,
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        temporary = _get_temporary_session()
        return temporary.run_command(command=command, timeout_s=timeout_s, labels=labels)


class AgentBayReadFileTool(BaseTool):
    name: str = "agentbay_read_file"
    description: str = (
        "Read a file from AgentBay cloud session and return its text content. Input: path, optional labels."
    )
    args_schema: Type[AgentBayReadFileInput] = AgentBayReadFileInput

    def _run(
        self,
        path: str,
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        temporary = _get_temporary_session()
        return temporary.read_file(path=path, labels=labels)


class AgentBayWriteFileTool(BaseTool):
    name: str = "agentbay_write_file"
    description: str = (
        "Write text content to a file inside AgentBay cloud session. Input: path, content, optional labels. Returns 'ok' on success."
    )
    args_schema: Type[AgentBayWriteFileInput] = AgentBayWriteFileInput

    def _run(
        self,
        path: str,
        content: str,
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        temporary = _get_temporary_session()
        return temporary.write_file(path=path, content=content, labels=labels)


# Singleton instances
agentbay_run_command = AgentBayRunCommandTool()
agentbay_read_file = AgentBayReadFileTool()
agentbay_write_file = AgentBayWriteFileTool()


class AgentBayCreateSessionTool(BaseTool):
    name: str = "agentbay_create_session"
    description: str = (
        "Create a persistent AgentBay session and return session_id for multi-step workflows."
    )
    args_schema: Type[AgentBayCreateSessionInput] = AgentBayCreateSessionInput

    def _run(self, labels: Optional[Dict[str, str]] = None) -> str:
        persistent = _get_persistent_session()
        return persistent.create_persistent_session(labels=labels)


class AgentBayDeleteSessionTool(BaseTool):
    name: str = "agentbay_delete_session"
    description: str = "Delete a previously created persistent AgentBay session by session_id."
    args_schema: Type[AgentBayDeleteSessionInput] = AgentBayDeleteSessionInput

    def _run(self, session_id: str) -> str:
        persistent = _get_persistent_session()
        persistent.delete_persistent_session(session_id=session_id)
        return "ok"


class AgentBayRunInSessionTool(BaseTool):
    name: str = "agentbay_run_in_session"
    description: str = "Execute a shell command inside a persistent session and return stdout text."
    args_schema: Type[AgentBayRunInSessionInput] = AgentBayRunInSessionInput

    def _run(self, session_id: str, command: str, timeout_s: int = 60) -> str:
        persistent = _get_persistent_session()
        return persistent.run_command_in_session(session_id=session_id, command=command, timeout_s=timeout_s)


class AgentBayWriteInSessionTool(BaseTool):
    name: str = "agentbay_write_in_session"
    description: str = "Write text content to a file in a persistent session. Returns 'ok' on success."
    args_schema: Type[AgentBayWriteInSessionInput] = AgentBayWriteInSessionInput

    def _run(self, session_id: str, path: str, content: str) -> str:
        persistent = _get_persistent_session()
        return persistent.write_file_in_session(session_id=session_id, path=path, content=content)


class AgentBayReadInSessionTool(BaseTool):
    name: str = "agentbay_read_in_session"
    description: str = "Read text file content from a persistent session."
    args_schema: Type[AgentBayReadInSessionInput] = AgentBayReadInSessionInput

    def _run(self, session_id: str, path: str) -> str:
        persistent = _get_persistent_session()
        return persistent.read_file_in_session(session_id=session_id, path=path)


class AgentBayUploadFileTool(BaseTool):
    name: str = "agentbay_upload_file"
    description: str = "Upload a local file to the persistent session. Returns 'ok' on success."
    args_schema: Type[AgentBayUploadFileInput] = AgentBayUploadFileInput

    def _run(self, session_id: str, local_path: str, remote_path: str) -> str:
        persistent = _get_persistent_session()
        return persistent.upload_file(session_id=session_id, local_path=local_path, remote_path=remote_path)


class AgentBayUploadFilesTool(BaseTool):
    name: str = "agentbay_upload_files"
    description: str = "Upload multiple local files to the persistent session. Returns 'ok' on success."
    args_schema: Type[AgentBayUploadFilesInput] = AgentBayUploadFilesInput

    def _run(self, session_id: str, files: List[Dict[str, str]]) -> str:  # type: ignore[override]
        persistent = _get_persistent_session()
        return persistent.upload_files(session_id=session_id, files=files)


class AgentBayDownloadFileTool(BaseTool):
    name: str = "agentbay_download_file"
    description: str = "Download a remote file from the persistent session to local path. Returns 'ok' on success."
    args_schema: Type[AgentBayDownloadFileInput] = AgentBayDownloadFileInput

    def _run(self, session_id: str, remote_path: str, local_path: str) -> str:
        persistent = _get_persistent_session()
        return persistent.download_file(session_id=session_id, remote_path=remote_path, local_path=local_path)


class AgentBayGetLinkTool(BaseTool):
    name: str = "agentbay_get_link"
    description: str = (
        "Get a local-accessible URL for a service running in the cloud session. "
        "For HTTPS services, specify protocol_type='https' and port in range [30100, 30199] (e.g., port=30123). "
        "For WebSocket services, specify only port."
        "Input: session_id, optional protocol_type ('https' or 'wss'), optional port."
    )
    args_schema: Type[AgentBayGetLinkInput] = AgentBayGetLinkInput

    def _run(
        self,
        session_id: str,
        protocol_type: Optional[str] = None,
        port: Optional[int] = None,
    ) -> str:
        """Get a local-accessible URL for a service in the cloud session."""
        persistent = _get_persistent_session()
        return persistent.get_link_in_session(
            session_id=session_id,
            protocol_type=protocol_type,
            port=port,
        )


# Singletons for AgentBay tools
agentbay_create_session = AgentBayCreateSessionTool()
agentbay_delete_session = AgentBayDeleteSessionTool()
agentbay_run_in_session = AgentBayRunInSessionTool()
agentbay_write_in_session = AgentBayWriteInSessionTool()
agentbay_read_in_session = AgentBayReadInSessionTool()
agentbay_upload_file = AgentBayUploadFileTool()
agentbay_upload_files = AgentBayUploadFilesTool()
agentbay_download_file = AgentBayDownloadFileTool()
agentbay_get_link = AgentBayGetLinkTool()


from typing import Dict, Optional, List
from pydantic import BaseModel, Field, field_validator


class AgentBayRunCodeInput(BaseModel):
    code: str = Field(..., description="Code content to execute")
    language: str = Field("python", description="Programming language, either python or javascript")
    timeout_s: int = Field(60, ge=1, le=60, description="Timeout in seconds, max 60s")
    labels: Optional[Dict[str, str]] = Field(None, description="Optional: session labels")

    @field_validator("language")
    @classmethod
    def _validate_language(cls, v: str) -> str:
        lang = v.lower().strip()
        if lang not in {"python", "javascript"}:
            raise ValueError("language must be either python or javascript")
        return lang


class AgentBayRunCommandInput(BaseModel):
    command: str = Field(..., description="Shell command to execute inside the cloud session")
    timeout_s: int = Field(60, ge=1, le=60, description="Timeout in seconds, max 60s")
    labels: Optional[Dict[str, str]] = Field(None, description="Optional: session labels")


class AgentBayReadFileInput(BaseModel):
    path: str = Field(..., description="Absolute or working-directory relative file path inside session")
    labels: Optional[Dict[str, str]] = Field(None, description="Optional: session labels")


class AgentBayWriteFileInput(BaseModel):
    path: str = Field(..., description="Destination file path inside session")
    content: str = Field(..., description="Text content to write")
    labels: Optional[Dict[str, str]] = Field(None, description="Optional: session labels")


class AgentBayCreateSessionInput(BaseModel):
    labels: Optional[Dict[str, str]] = Field(None, description="Optional: session labels")


class AgentBayDeleteSessionInput(BaseModel):
    session_id: str = Field(..., description="Persistent session id returned by create")


class AgentBayRunInSessionInput(BaseModel):
    session_id: str = Field(..., description="Persistent session id")
    command: str = Field(..., description="Shell command to run in session")


class AgentBayWriteInSessionInput(BaseModel):
    session_id: str = Field(..., description="Persistent session id")
    path: str = Field(..., description="Remote path to write")
    content: str = Field(..., description="Text content")


class AgentBayReadInSessionInput(BaseModel):
    session_id: str = Field(..., description="Persistent session id")
    path: str = Field(..., description="Remote path to read")


class AgentBayUploadFileInput(BaseModel):
    session_id: str = Field(..., description="Persistent session id")
    local_path: str = Field(..., description="Local file path to upload")
    remote_path: str = Field(..., description="Destination path in session")


class AgentBayUploadFilesInput(BaseModel):
    session_id: str = Field(..., description="Persistent session id")
    files: List[Dict[str, str]] = Field(
        ..., description="List of {local_path, remote_path} dicts"
    )


class AgentBayDownloadFileInput(BaseModel):
    session_id: str = Field(..., description="Persistent session id")
    remote_path: str = Field(..., description="Remote file path to download")
    local_path: str = Field(..., description="Local destination path")


class AgentBaySaveFilesLocallyInput(BaseModel):
    files: List[Dict[str, str]] = Field(
        ...,
        description="List of files with 'path' (absolute local path) and 'content' (file content) keys"
    )


class AgentBayGetLinkInput(BaseModel):
    session_id: str = Field(..., description="Persistent session ID")
    protocol_type: Optional[str] = Field(
        None,
        description='Protocol type: "https" or "wss". If specified, port must also be provided.'
    )
    port: Optional[int] = Field(
        None,
        ge=30100,
        le=30199,
        description="Port number in range [30100, 30199] for the service. Required if protocol_type is specified. For example, use port=30123 for a service running on port 30123."
    )

    @field_validator("protocol_type")
    @classmethod
    def _validate_protocol_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            protocol = v.lower().strip()
            if protocol not in {"https", "wss"}:
                raise ValueError('protocol_type must be either "https" or "wss"')
            return protocol
        return v


class AgentBayVerifyHttpServiceInput(BaseModel):
    url: str = Field(..., description="Full URL to send HTTP request to")
    method: str = Field("GET", description="HTTP method: GET, POST, PUT, DELETE, etc.")
    path: Optional[str] = Field(None, description="Optional path to append to URL (if not already in URL)")
    expected_status: Optional[int] = Field(200, description="Expected HTTP status code (default: 200)")
    expected_text: Optional[str] = Field(None, description="Optional text that should be present in response body")
    timeout_s: int = Field(10, ge=1, le=60, description="Request timeout in seconds (default: 10, max: 60)")

    @field_validator("method")
    @classmethod
    def _validate_method(cls, v: str) -> str:
        method = v.upper().strip()
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        if method not in valid_methods:
            raise ValueError(f"method must be one of {valid_methods}")
        return method


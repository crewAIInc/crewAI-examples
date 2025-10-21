"""
Local filesystem tools that don't require AgentBay SDK.
These tools operate on the local machine only.
"""

from typing import List, Dict, Type, Optional
from pathlib import Path
from crewai.tools import BaseTool
import requests
import json
from urllib.parse import urljoin

from .tool_schemas import AgentBaySaveFilesLocallyInput, AgentBayVerifyHttpServiceInput


class SaveFilesLocallyTool(BaseTool):
    """
    Tool to save multiple files to local filesystem.
    This is a pure local operation and doesn't require AgentBay SDK.
    """
    name: str = "save_files_locally"
    description: str = (
        "Save multiple files to local filesystem. Creates directories as needed. "
        "Input: files list with 'path' (absolute local path) and 'content' (file content) keys. "
        "Returns summary message with saved file paths."
    )
    args_schema: Type[AgentBaySaveFilesLocallyInput] = AgentBaySaveFilesLocallyInput

    def _run(self, files: List[Dict[str, str]]) -> str:  # type: ignore[override]
        """Save files to local filesystem."""
        saved_paths = []
        for file_info in files:
            file_path = file_info.get("path", "")
            content = file_info.get("content", "")

            if not file_path:
                continue

            # Create parent directories if needed
            path_obj = Path(file_path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            saved_paths.append(file_path)

        return f"Saved {len(saved_paths)} files: {', '.join(saved_paths)}"


class VerifyHttpServiceTool(BaseTool):
    """
    Tool to verify HTTP service by sending a request and validating the response.
    This is a pure local operation that sends HTTP requests from the local machine.
    """
    name: str = "verify_http_service"
    description: str = (
        "Send an HTTP request to a URL and verify the response. "
        "Checks status code and optionally validates response body contains expected text. "
        "Input: url (required), method (default: GET), path (optional), expected_status (default: 200), "
        "expected_text (optional), timeout_s (default: 10). "
        "Returns verification result with success status and details."
    )
    args_schema: Type[AgentBayVerifyHttpServiceInput] = AgentBayVerifyHttpServiceInput

    def _run(
        self,
        url: str,
        method: str = "GET",
        path: Optional[str] = None,
        expected_status: Optional[int] = 200,
        expected_text: Optional[str] = None,
        timeout_s: int = 10,
    ) -> str:
        """Send HTTP request and verify response."""
        try:
            # Construct full URL
            if path:
                full_url = urljoin(url.rstrip("/") + "/", path.lstrip("/"))
            else:
                full_url = url

            # Send request
            response = requests.request(
                method=method,
                url=full_url,
                timeout=timeout_s,
                allow_redirects=True,
            )

            # Check status code
            status_ok = expected_status is None or response.status_code == expected_status
            status_msg = f"Status: {response.status_code}"
            if expected_status is not None:
                status_msg += f" (expected: {expected_status})"

            # Check response body
            body_ok = True
            body_msg = ""
            if expected_text:
                response_text = response.text

                # Try JSON comparison first (handles format differences like spacing)
                try:
                    expected_json = json.loads(expected_text)
                    response_json = json.loads(response_text)
                    # Compare parsed JSON objects
                    body_ok = expected_json == response_json
                    if body_ok:
                        body_msg = f"Body JSON matches expected content"
                    else:
                        body_msg = f"Body JSON does not match (expected: {expected_json}, got: {response_json})"
                except (json.JSONDecodeError, ValueError):
                    # Fallback to string matching if not valid JSON
                    body_ok = expected_text in response_text
                    body_msg = f"Body contains expected text: {body_ok}"
                    if not body_ok:
                        body_msg += f" (expected: '{expected_text}', response preview: {response_text[:200]}...)"

            # Build result message
            if status_ok and body_ok:
                result = f"✅ Verification passed. {status_msg}"
                if body_msg:
                    result += f" {body_msg}"
                result += f" Response length: {len(response.text)} bytes"
            else:
                result = f"❌ Verification failed. {status_msg}"
                if body_msg:
                    result += f" {body_msg}"
                if not status_ok:
                    result += f" Response body preview: {response.text[:500]}"

            return result

        except requests.exceptions.Timeout:
            return f"❌ Request timeout after {timeout_s}s"
        except requests.exceptions.ConnectionError as e:
            return f"❌ Connection error: {str(e)}"
        except requests.exceptions.RequestException as e:
            return f"❌ Request failed: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"


# Singleton instances
save_files_locally = SaveFilesLocallyTool()
verify_http_service = VerifyHttpServiceTool()


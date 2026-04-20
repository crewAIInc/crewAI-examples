import os
import shlex
from typing import List, Dict, Optional

from .api.agentbay_persistent_session import AgentBayPersistentSession


def _collect_files(local_root: str, remote_root: str) -> List[Dict[str, str]]:
    mappings: List[Dict[str, str]] = []
    for base, _, files in os.walk(local_root):
        for name in files:
            lp = os.path.join(base, name)
            rp = os.path.join(remote_root, os.path.relpath(lp, start=local_root))
            mappings.append({"local_path": lp, "remote_path": rp})
    return mappings


def run_upload_install_run_download(
    local_project_root: str,
    remote_workspace_root: str,
    install_and_run_script: str,
    result_remote_path: str,
    result_local_path: str,
    labels: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """
    Minimal end-to-end: create session → upload project → install & run → download result → cleanup.
    Returns summary dict with session_id and result_local_path.
    """
    persistent = AgentBayPersistentSession()
    session_id = persistent.create_persistent_session(labels=labels)
    try:
        files = _collect_files(local_project_root, remote_workspace_root)
        if files:
            persistent.upload_files(session_id, files)
        # Write and execute install/run script
        script_remote = os.path.join(remote_workspace_root, "_run.sh")
        persistent.write_file_in_session(session_id, script_remote, install_and_run_script)
        persistent.run_command_in_session(session_id, f"bash {shlex.quote(script_remote)} > {shlex.quote(result_remote_path)} 2>&1 || true")
        # Download result
        os.makedirs(os.path.dirname(result_local_path) or ".", exist_ok=True)
        persistent.download_file(session_id, result_remote_path, result_local_path)
        return {"session_id": session_id, "result_local_path": result_local_path}
    finally:
        persistent.delete_persistent_session(session_id)



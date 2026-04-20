import os
import sys
import tempfile
from pathlib import Path
import pytest

# Allow running tests directly without package installation: add subproject src to sys.path
# tests/ is at crews/agentbay_sdk/tests/, so we need to go up 1 level to get to crews/agentbay_sdk/
# Then add src/ to get to crews/agentbay_sdk/src/ where the package is located
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # crews/agentbay_sdk/
PROJECT_SRC = PROJECT_ROOT / "src"  # crews/agentbay_sdk/src/
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from agentbay_sdk.api.agentbay_persistent_session import AgentBayPersistentSession


@pytest.mark.skipif(
    not os.getenv("AGENTBAY_API_KEY"),
    reason="AGENTBAY_API_KEY not set"
)
def test_persistent_session_lifecycle():
    """Test creating and deleting a persistent session."""
    persistent = AgentBayPersistentSession()
    session_id = persistent.create_persistent_session()
    assert session_id is not None
    assert isinstance(session_id, str)

    # Session should exist in internal tracking
    assert session_id in persistent._sessions

    # Delete session
    persistent.delete_persistent_session(session_id)
    assert session_id not in persistent._sessions


@pytest.mark.skipif(
    not os.getenv("AGENTBAY_API_KEY"),
    reason="AGENTBAY_API_KEY not set"
)
def test_run_command_in_session():
    """Test executing commands in a persistent session."""
    persistent = AgentBayPersistentSession()
    session_id = persistent.create_persistent_session()
    try:
        # Test simple echo command
        result = persistent.run_command_in_session(session_id, "echo 'test output'")
        assert "test output" in result

        # Test Python execution
        result = persistent.run_command_in_session(session_id, "python3 -c 'print(42)'")
        assert "42" in result
    finally:
        persistent.delete_persistent_session(session_id)


@pytest.mark.skipif(
    not os.getenv("AGENTBAY_API_KEY"),
    reason="AGENTBAY_API_KEY not set"
)
def test_file_operations_in_session():
    """Test reading and writing files in a persistent session."""
    persistent = AgentBayPersistentSession()
    session_id = persistent.create_persistent_session()
    try:
        test_path = "/tmp/test_file.txt"
        test_content = "Hello, AgentBay Persistent Session!"

        # Write file
        result = persistent.write_file_in_session(session_id, test_path, test_content)
        assert result == "ok"

        # Read file
        content = persistent.read_file_in_session(session_id, test_path)
        assert test_content in content
    finally:
        persistent.delete_persistent_session(session_id)


@pytest.mark.skipif(
    not os.getenv("AGENTBAY_API_KEY"),
    reason="AGENTBAY_API_KEY not set"
)
def test_upload_and_download_file():
    """Test uploading a local file to session and downloading it back."""
    persistent = AgentBayPersistentSession()
    session_id = persistent.create_persistent_session()

    # Create a temporary local file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        local_path = f.name
        test_content = "This is test content for upload/download"
        f.write(test_content)

    try:
        remote_path = "/tmp/uploaded_file.txt"

        # Upload file
        result = persistent.upload_file(session_id, local_path, remote_path)
        assert result == "ok"

        # Verify file was uploaded by reading it back
        content = persistent.read_file_in_session(session_id, remote_path)
        assert test_content in content

        # Download to a new location
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            download_path = f.name

        result = persistent.download_file(session_id, remote_path, download_path)
        assert result == "ok"

        # Verify downloaded content
        with open(download_path, 'r') as f:
            downloaded_content = f.read()
        assert test_content in downloaded_content

        # Cleanup
        os.unlink(download_path)
    finally:
        persistent.delete_persistent_session(session_id)
        os.unlink(local_path)


@pytest.mark.skipif(
    not os.getenv("AGENTBAY_API_KEY"),
    reason="AGENTBAY_API_KEY not set"
)
def test_upload_multiple_files():
    """Test uploading multiple files at once."""
    persistent = AgentBayPersistentSession()
    session_id = persistent.create_persistent_session()

    # Create multiple temporary files
    temp_files = []
    files_to_upload = []
    try:
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_{i}.txt') as f:
                local_path = f.name
                content = f"File {i} content"
                f.write(content)
                temp_files.append(local_path)
                files_to_upload.append({
                    "local_path": local_path,
                    "remote_path": f"/tmp/uploaded_{i}.txt"
                })

        # Upload all files
        result = persistent.upload_files(session_id, files_to_upload)
        assert "Successfully" in result or "Uploaded" in result

        # Verify all files were uploaded
        for i, file_info in enumerate(files_to_upload):
            content = persistent.read_file_in_session(session_id, file_info["remote_path"])
            assert f"File {i} content" in content
    finally:
        persistent.delete_persistent_session(session_id)
        for f in temp_files:
            os.unlink(f)


@pytest.mark.skipif(
    not os.getenv("AGENTBAY_API_KEY"),
    reason="AGENTBAY_API_KEY not set"
)
def test_full_pipeline_upload_install_run_download():
    """Test the complete pipeline: upload, install deps, run code, download result."""
    from agentbay_sdk.pipeline import run_upload_install_run_download

    # Create a simple Python project structure
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        project_dir.mkdir()

        # Create a simple Python script
        (project_dir / "main.py").write_text("""
result = 2 + 2
print(f"Result: {result}")
with open("/workspace/test_project/output.txt", "w") as f:
    f.write(f"Success: {result}\\n")
""")

        # Create requirements.txt
        (project_dir / "requirements.txt").write_text("# No external dependencies\n")

        # Run pipeline
        result = run_upload_install_run_download(
            local_project_root=str(project_dir),
            remote_workspace_root="/workspace/test_project",
            install_and_run_script="""#!/bin/bash
set -e
cd /workspace/test_project
python3 main.py
echo "Pipeline completed successfully"
""",
            result_remote_path="/workspace/test_project/output.txt",
            result_local_path=str(Path(tmpdir) / "downloaded_output.txt"),
        )

        assert "session_id" in result
        assert "result_local_path" in result

        # Verify downloaded result
        if os.path.exists(result["result_local_path"]):
            with open(result["result_local_path"], 'r') as f:
                content = f.read()
            assert "Success" in content or "4" in content


@pytest.mark.skipif(
    not os.getenv("AGENTBAY_API_KEY"),
    reason="AGENTBAY_API_KEY not set"
)
def test_session_error_handling():
    """Test error handling when using invalid session_id."""
    persistent = AgentBayPersistentSession()

    # Try to use non-existent session
    try:
        persistent.run_command_in_session("invalid_session_id", "echo test")
        raise AssertionError("Expected RuntimeError but no exception was raised")
    except RuntimeError as e:
        assert "not found" in str(e).lower()

    try:
        persistent.read_file_in_session("invalid_session_id", "/tmp/test.txt")
        raise AssertionError("Expected RuntimeError but no exception was raised")
    except RuntimeError as e:
        assert "not found" in str(e).lower()

    try:
        persistent.write_file_in_session("invalid_session_id", "/tmp/test.txt", "content")
        raise AssertionError("Expected RuntimeError but no exception was raised")
    except RuntimeError as e:
        assert "not found" in str(e).lower()

    try:
        persistent.download_file("invalid_session_id", "/tmp/test.txt", "/tmp/local.txt")
        raise AssertionError("Expected RuntimeError but no exception was raised")
    except RuntimeError as e:
        assert "not found" in str(e).lower()


# Allow running tests directly with python3 command
if __name__ == "__main__":
    import traceback

    # Check environment variables
    if not os.getenv("AGENTBAY_API_KEY"):
        print("❌ Error: AGENTBAY_API_KEY environment variable is not set")
        print("Please set it before running tests:")
        print("  export AGENTBAY_API_KEY=your_api_key_here")
        sys.exit(1)

    print("=" * 60)
    print("Running AgentBay Persistent Session Tests")
    print("=" * 60)
    print(f"✅ AGENTBAY_API_KEY: {'*' * min(20, len(os.getenv('AGENTBAY_API_KEY', '')))}")
    print()

    # List of all test functions
    tests = [
        ("Persistent Session Lifecycle", test_persistent_session_lifecycle),
        ("Run Command in Session", test_run_command_in_session),
        ("File Operations in Session", test_file_operations_in_session),
        ("Upload and Download File", test_upload_and_download_file),
        ("Upload Multiple Files", test_upload_multiple_files),
        ("Full Pipeline Test", test_full_pipeline_upload_install_run_download),
        ("Session Error Handling", test_session_error_handling),
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test_name, test_func in tests:
        print(f"Running: {test_name}...", end=" ")
        try:
            test_func()
            print("✅ PASSED")
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED")
            print(f"   AssertionError: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR")
            print(f"   {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
        print()

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✅ Passed:  {passed}")
    print(f"❌ Failed:  {failed}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"📊 Total:   {passed + failed + skipped}")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("🎉 All tests passed!")
        sys.exit(0)

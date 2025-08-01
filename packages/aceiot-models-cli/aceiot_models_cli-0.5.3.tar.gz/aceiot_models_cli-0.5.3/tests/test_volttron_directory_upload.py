"""Test Volttron directory upload functionality."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from aceiot_models_cli.volttron_commands import volttron


class TestVolttronDirectoryUpload:
    """Test uploading directories as compressed archives."""

    @patch("aceiot_models_cli.volttron_commands.require_api_client")
    def test_upload_directory_creates_archive(self, mock_require_client):
        """Test that uploading a directory creates a tar.gz archive."""
        # Mock API client
        mock_client = MagicMock()
        mock_require_client.return_value = mock_client

        # Mock gateway info
        mock_client.get_gateway.return_value = {"client": "test-client"}

        # Mock successful upload
        mock_client.upload_client_volttron_agent_package.return_value = {
            "id": "pkg-123",
            "name": "test-agent",
            "size": 1024,
        }

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a test agent directory
            agent_dir = Path("test-agent")
            agent_dir.mkdir()

            # Create required files
            setup_py = agent_dir / "setup.py"
            setup_py.write_text('name="test-agent"\nversion="1.0.0"')

            # Create some Python files
            (agent_dir / "agent.py").write_text("print('test agent')")

            # Mock context object
            ctx_obj = {"output": "table", "client": mock_client}

            result = runner.invoke(
                volttron,
                ["upload-agent", str(agent_dir), "test-gateway", "--name", "test-agent"],
                obj=ctx_obj,
            )

            assert result.exit_code == 0
            assert "✓ Directory structure validated" in result.output
            assert "✓ Creating tar.gz archive..." in result.output
            assert "✓ Created temporary archive:" in result.output
            assert "Agent package uploaded successfully!" in result.output
            assert "✓ Cleaned up temporary archive" in result.output

            # Verify upload was called with a .tar.gz file
            upload_calls = mock_client.upload_client_volttron_agent_package.call_args_list
            assert len(upload_calls) == 1

            # Check that the uploaded path was a tar.gz file
            uploaded_path = upload_calls[0][0][1]  # Second positional argument
            assert uploaded_path.endswith(".tar.gz")

            # Verify the temporary file was cleaned up
            assert not Path(uploaded_path).exists()

    @patch("aceiot_models_cli.volttron_commands.require_api_client")
    def test_upload_zip_file_directly(self, mock_require_client):
        """Test that uploading a zip file doesn't create another archive."""
        # Mock API client
        mock_client = MagicMock()
        mock_require_client.return_value = mock_client

        # Mock gateway info
        mock_client.get_gateway.return_value = {"client": "test-client"}

        # Mock successful upload
        mock_client.upload_client_volttron_agent_package.return_value = {
            "id": "pkg-123",
            "name": "test-agent",
        }

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a test zip file
            test_zip = Path("test-agent.zip")
            test_zip.write_bytes(b"PK\x03\x04")  # Minimal zip header

            # Mock context object
            ctx_obj = {"output": "table", "client": mock_client}

            result = runner.invoke(
                volttron,
                ["upload-agent", str(test_zip), "test-gateway", "--name", "test-agent"],
                obj=ctx_obj,
            )

            assert result.exit_code == 0
            assert "✓ Creating tar.gz archive..." not in result.output
            assert "Agent package uploaded successfully!" in result.output

            # Verify upload was called with the original zip file
            upload_calls = mock_client.upload_client_volttron_agent_package.call_args_list
            assert len(upload_calls) == 1
            uploaded_path = upload_calls[0][0][1]
            assert uploaded_path == str(test_zip)

    @patch("aceiot_models_cli.volttron_commands.require_api_client")
    def test_cleanup_on_upload_failure(self, mock_require_client):
        """Test that temporary archive is cleaned up on upload failure."""
        from aceiot_models.api import APIError

        # Mock API client
        mock_client = MagicMock()
        mock_require_client.return_value = mock_client

        # Mock gateway info
        mock_client.get_gateway.return_value = {"client": "test-client"}

        # Mock upload failure
        mock_client.upload_client_volttron_agent_package.side_effect = APIError(
            "Upload failed", status_code=500, response_data={"detail": "Server error"}
        )

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a test agent directory
            agent_dir = Path("test-agent")
            agent_dir.mkdir()

            # Create required files
            setup_py = agent_dir / "setup.py"
            setup_py.write_text('name="test-agent"\nversion="1.0.0"')
            (agent_dir / "agent.py").write_text("print('test agent')")

            # Mock context object
            ctx_obj = {"output": "table", "client": mock_client}

            # Count .tar.gz files before and after
            temp_dir = Path(tempfile.gettempdir())
            tar_files_before = list(temp_dir.glob("*.tar.gz"))

            result = runner.invoke(
                volttron,
                ["upload-agent", str(agent_dir), "test-gateway", "--name", "test-agent"],
                obj=ctx_obj,
            )

            assert result.exit_code == 1
            assert "Upload failed: Server error" in result.output

            # Verify no new .tar.gz files left behind
            tar_files_after = list(temp_dir.glob("*.tar.gz"))
            assert len(tar_files_after) == len(tar_files_before)

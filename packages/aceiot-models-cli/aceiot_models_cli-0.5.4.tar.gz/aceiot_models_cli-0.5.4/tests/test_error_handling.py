"""Test error handling improvements."""

from unittest.mock import MagicMock, patch

from aceiot_models.api import APIError
from click.testing import CliRunner

from aceiot_models_cli.volttron_commands import get_api_error_detail, volttron


class TestErrorHandling:
    """Test error handling improvements."""

    def test_get_api_error_detail_with_response_data(self):
        """Test extracting error detail from response data."""
        error = APIError(
            "Generic error",
            status_code=404,
            response_data={"detail": "Gateway 'nonexistent' not found"},
        )
        assert get_api_error_detail(error) == "Gateway 'nonexistent' not found"

    def test_get_api_error_detail_without_response_data(self):
        """Test extracting error detail when no response data."""
        error = APIError("Connection error")
        assert get_api_error_detail(error) == "Connection error"

    def test_get_api_error_detail_with_non_dict_response(self):
        """Test extracting error detail with non-dict response data."""
        error = APIError("Error", response_data="string response")
        assert get_api_error_detail(error) == "Error"

    @patch("aceiot_models_cli.volttron_commands.require_api_client")
    def test_upload_agent_gateway_not_found(self, mock_require_client):
        """Test upload-agent command with non-existent gateway shows detailed error."""
        # Mock API client
        mock_client = MagicMock()
        mock_require_client.return_value = mock_client

        # Mock get_gateway to raise APIError with detailed message
        mock_client.get_gateway.side_effect = APIError(
            "API request failed",
            status_code=404,
            response_data={"detail": "Gateway 'nonexistent-gateway' not found"},
        )

        # Since the code now falls back to treating it as a client name,
        # we need to mock the client upload to also fail
        mock_client.get_client.side_effect = APIError(
            "API request failed",
            status_code=404,
            response_data={"detail": "Client 'nonexistent-gateway' not found"},
        )

        # Or we can make the upload fail
        mock_client.upload_client_volttron_agent_package.side_effect = APIError(
            "API request failed",
            status_code=404,
            response_data={"detail": "Client 'nonexistent-gateway' not found"},
        )

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a dummy agent directory
            import os

            os.makedirs("test-agent")
            with open("test-agent/setup.py", "w") as f:
                f.write('name="test-agent"\nversion="1.0.0"')

            # Mock context object
            ctx_obj = {"output": "table", "client": mock_client}

            result = runner.invoke(
                volttron,
                ["upload-agent", "test-agent", "nonexistent-gateway", "--name", "test-agent"],
                obj=ctx_obj,
            )

            assert result.exit_code == 1
            # The error message should now be about upload failure since it falls back to client
            assert "Upload failed: Client 'nonexistent-gateway' not found" in result.output

    @patch("aceiot_models_cli.volttron_commands.require_api_client")
    def test_list_packages_client_not_found(self, mock_require_client):
        """Test list-packages command with non-existent client shows detailed error."""
        # Mock API client
        mock_client = MagicMock()
        mock_require_client.return_value = mock_client

        # Mock API to raise error with detailed message
        mock_client.get_client_volttron_agent_package_list.side_effect = APIError(
            "API request failed",
            status_code=404,
            response_data={"detail": "Client 'nonexistent-client' not found"},
        )

        runner = CliRunner()

        # Mock context object
        ctx_obj = {"output": "table", "client": mock_client}

        result = runner.invoke(volttron, ["list-packages", "nonexistent-client"], obj=ctx_obj)

        assert result.exit_code == 1
        assert "Failed to list packages: Client 'nonexistent-client' not found" in result.output

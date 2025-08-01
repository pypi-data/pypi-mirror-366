"""Tests for Volttron commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from click.testing import CliRunner

from aceiot_models_cli.volttron_commands import volttron


class TestVolttronCommands:
    """Test Volttron CLI commands."""

    def test_config_file_validation_json(self):
        """Test JSON config file validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"test": "config", "value": 123}, f)
            temp_path = f.name

        try:
            config_path = Path(temp_path)
            content = config_path.read_text()

            # Should not raise exception for valid JSON
            json.loads(content)

        finally:
            Path(temp_path).unlink()

    def test_config_file_validation_yaml(self):
        """Test YAML config file validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"test": "config", "value": 123}, f)
            temp_path = f.name

        try:
            config_path = Path(temp_path)
            content = config_path.read_text()

            # Should not raise exception for valid YAML
            yaml.safe_load(content)

        finally:
            Path(temp_path).unlink()

    def test_config_file_validation_invalid_json(self):
        """Test invalid JSON config file validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json}')  # Missing quotes around json
            temp_path = f.name

        try:
            config_path = Path(temp_path)
            content = config_path.read_text()

            # Should raise exception for invalid JSON
            with pytest.raises(json.JSONDecodeError):
                json.loads(content)

        finally:
            Path(temp_path).unlink()

    def test_config_file_validation_invalid_yaml(self):
        """Test invalid YAML config file validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("[invalid: yaml content")  # Missing closing bracket
            temp_path = f.name

        try:
            config_path = Path(temp_path)
            content = config_path.read_text()

            # Should raise exception for invalid YAML
            with pytest.raises(yaml.YAMLError):
                yaml.safe_load(content)

        finally:
            Path(temp_path).unlink()

    @patch("aceiot_models_cli.volttron_commands.require_api_client")
    def test_deploy_interactive_mode_no_packages(self, mock_require_client):
        """Test deploy command in interactive mode when no packages are available."""
        # Mock API client
        mock_client = MagicMock()
        mock_require_client.return_value = mock_client

        # Mock gateway info
        mock_client.get_gateway.return_value = {"client": "test-client"}

        # Mock empty packages list
        mock_client.get_client_volttron_agent_package_list.return_value = {"items": []}

        runner = CliRunner()

        # Mock context object
        ctx_obj = {"output": "table", "client": mock_client}

        result = runner.invoke(volttron, ["deploy", "test-gateway"], obj=ctx_obj)

        assert result.exit_code == 1
        assert "No packages found for this client" in result.output

    @patch("aceiot_models_cli.volttron_commands.require_api_client")
    def test_list_packages_success(self, mock_require_client):
        """Test list-packages command success."""
        # Mock API client
        mock_client = MagicMock()
        mock_require_client.return_value = mock_client

        # Mock packages response
        mock_packages = {
            "items": [
                {
                    "id": "pkg-1",
                    "package_name": "test-agent",
                    "object_hash": "abc123",
                    "size": 1024,
                    "created": "2024-01-01T00:00:00Z",
                }
            ],
            "total": 1,
        }
        mock_client.get_client_volttron_agent_package_list.return_value = mock_packages

        runner = CliRunner()

        # Mock context object
        ctx_obj = {"output": "table", "client": mock_client}

        result = runner.invoke(volttron, ["list-packages", "test-client"], obj=ctx_obj)

        assert result.exit_code == 0
        assert "Volttron Agent Packages" in result.output
        assert "test-agent" in result.output

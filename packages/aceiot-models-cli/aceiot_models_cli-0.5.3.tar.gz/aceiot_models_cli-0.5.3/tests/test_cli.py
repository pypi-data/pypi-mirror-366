"""Tests for main CLI commands."""

from unittest.mock import patch

from aceiot_models_cli.cli import cli


class TestCLI:
    """Test main CLI functionality."""

    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "ACE IoT Models CLI" in result.output
        assert "Commands:" in result.output

    def test_cli_version_flag(self, runner):
        """Test CLI with config flag."""
        result = runner.invoke(cli, ["--config", "/tmp/test.yaml", "--help"])
        assert result.exit_code == 0

    @patch("aceiot_models_cli.cli.load_config")
    def test_cli_with_api_key(self, mock_load_config, runner):
        """Test CLI with API key option."""
        from aceiot_models_cli.config import Config

        mock_config = Config(api_url="https://test.api.com", api_key=None)
        mock_load_config.return_value = mock_config

        result = runner.invoke(cli, ["--api-key", "test-key", "--help"])
        assert result.exit_code == 0


class TestInitCommand:
    """Test init command."""

    @patch("aceiot_models_cli.config.init_config")
    def test_init_success(self, mock_init_config, runner):
        """Test successful init command."""
        result = runner.invoke(cli, ["init", "--api-key", "test-key"])
        assert result.exit_code == 0
        assert "Configuration initialized successfully" in result.output
        mock_init_config.assert_called_once_with(api_key="test-key", api_url=None)

    @patch("aceiot_models_cli.config.init_config")
    def test_init_with_url(self, mock_init_config, runner):
        """Test init command with API URL."""
        result = runner.invoke(
            cli, ["init", "--api-key", "test-key", "--api-url", "https://custom.api.com"]
        )
        assert result.exit_code == 0
        mock_init_config.assert_called_once_with(
            api_key="test-key", api_url="https://custom.api.com"
        )

    @patch("aceiot_models_cli.config.init_config")
    def test_init_failure(self, mock_init_config, runner):
        """Test failed init command."""
        mock_init_config.side_effect = Exception("Config error")
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 1
        assert "Failed to initialize configuration" in result.output


class TestSerializerCommand:
    """Test serializer test command."""

    @patch("tests.test_serializers_core.run_all_serializer_tests")
    def test_serializers_success(self, mock_run_tests, runner):
        """Test successful serializer tests."""
        # Mock successful test results
        mock_run_tests.return_value = [
            {"test_name": "Test 1", "passed": True, "error": None},
            {"test_name": "Test 2", "passed": True, "error": None},
        ]
        result = runner.invoke(cli, ["test-serializers"])
        assert result.exit_code == 0
        assert "Running serializer tests" in result.output
        assert "SERIALIZER TEST RESULTS" in result.output
        assert "All serializer tests passed!" in result.output

    @patch("tests.test_serializers_core.run_all_serializer_tests")
    def test_serializers_with_failures(self, mock_run_tests, runner):
        """Test serializer tests with failures."""
        mock_run_tests.return_value = [
            {"test_name": "Test 1", "passed": True, "error": None},
            {"test_name": "Test 2", "passed": False, "error": "Test failed"},
        ]
        result = runner.invoke(cli, ["test-serializers"])
        assert result.exit_code == 1
        assert "FAIL | Test 2" in result.output
        assert "Error: Test failed" in result.output

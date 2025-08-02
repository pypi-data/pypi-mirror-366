"""Tests for REPL functionality."""

from unittest.mock import MagicMock, patch

import click
import pytest

from aceiot_models_cli.repl.context import ContextType, ReplContext
from aceiot_models_cli.repl.executor_new import ReplCommandExecutor
from aceiot_models_cli.repl.parser import ReplCommandParser


class TestReplContext:
    """Test REPL context management."""

    def test_enter_and_exit_context(self):
        """Test entering and exiting contexts."""
        context = ReplContext()

        # Initially global
        assert context.is_global
        assert context.get_context_path() == ""

        # Enter site context
        context.enter_context(ContextType.SITE, "demo-site")
        assert not context.is_global
        assert context.get_context_path() == "site:demo-site"
        assert context.current_site == "demo-site"

        # Enter gateway context
        context.enter_context(ContextType.GATEWAY, "gw-001")
        assert context.get_context_path() == "site:demo-site/gw:gw-001"
        assert context.current_site == "demo-site"
        assert context.current_gateway == "gw-001"

        # Exit gateway context
        assert context.exit_context()
        assert context.get_context_path() == "site:demo-site"
        assert context.current_site == "demo-site"
        assert context.current_gateway is None

        # Exit site context
        assert context.exit_context() is False  # No more contexts to exit
        assert context.is_global

    def test_context_args_injection(self):
        """Test context argument injection."""
        context = ReplContext()

        # No args in global context
        assert context.get_context_args() == {}

        # Site context provides site args
        context.enter_context(ContextType.SITE, "demo-site")
        args = context.get_context_args()
        assert args["site_name"] == "demo-site"
        assert args["site"] == "demo-site"

        # Gateway context adds gateway args
        context.enter_context(ContextType.GATEWAY, "gw-001")
        args = context.get_context_args()
        assert args["site_name"] == "demo-site"
        assert args["site"] == "demo-site"
        assert args["gateway_name"] == "gw-001"
        assert args["gateway-name"] == "gw-001"

    def test_reset_context(self):
        """Test resetting context to global."""
        context = ReplContext()
        context.enter_context(ContextType.SITE, "demo-site")
        context.enter_context(ContextType.GATEWAY, "gw-001")

        assert not context.is_global

        context.reset_context()
        assert context.is_global
        assert context.get_context_path() == ""


class TestReplParser:
    """Test REPL command parsing."""

    @pytest.fixture
    def mock_cli(self):
        """Create a mock CLI group for testing."""

        @click.group()
        def cli():
            pass

        @cli.group()
        def sites():
            pass

        @sites.command()
        def list():
            pass

        @cli.group()
        def points():
            pass

        @points.command()
        @click.argument("point_name")
        @click.option("--start", help="Start date")
        @click.option("--end", help="End date")
        def timeseries(point_name, start, end):
            pass

        return cli

    @pytest.fixture
    def parser(self, mock_cli):
        """Create a parser with mock CLI."""
        return ReplCommandParser(mock_cli)

    @pytest.fixture
    def context(self):
        """Create a test context."""
        context = ReplContext()
        context.enter_context(ContextType.SITE, "demo-site")
        return context

    def test_parse_repl_command(self, parser, context):
        """Test parsing REPL-specific commands."""
        cmd = parser.parse("use site test-site", context)

        assert cmd.command_path == ["use"]
        assert cmd.arguments == ["site", "test-site"]
        assert cmd.options == {}

    def test_parse_cli_command(self, parser, context):
        """Test parsing CLI commands."""
        cmd = parser.parse("sites list", context)

        assert cmd.command_path == ["sites", "list"]
        assert cmd.arguments == []
        assert cmd.context_args["site_name"] == "demo-site"

    def test_parse_command_with_arguments_and_options(self, parser, context):
        """Test parsing commands with arguments and options."""
        cmd = parser.parse(
            "points timeseries sensor-temp --start 2024-01-01 --end 2024-01-02", context
        )

        assert cmd.command_path == ["points", "timeseries"]
        assert cmd.arguments == ["sensor-temp"]
        assert cmd.options["start"] == "2024-01-01"
        assert cmd.options["end"] == "2024-01-02"
        assert cmd.context_args["site_name"] == "demo-site"

    def test_parse_empty_command(self, parser, context):
        """Test parsing empty commands."""
        with pytest.raises(click.ClickException, match="Empty command"):
            parser.parse("", context)

        with pytest.raises(click.ClickException, match="Empty command"):
            parser.parse("   ", context)

    def test_parse_invalid_command(self, parser, context):
        """Test parsing invalid commands."""
        with pytest.raises(click.ClickException, match="Unknown command"):
            parser.parse("nonexistent command", context)

    def test_parse_command_with_quotes(self, parser, context):
        """Test parsing commands with quoted arguments."""
        cmd = parser.parse(
            'points timeseries "sensor with spaces" --start "2024-01-01 10:00"', context
        )

        assert cmd.arguments == ["sensor with spaces"]
        assert cmd.options["start"] == "2024-01-01 10:00"


class TestReplExecutor:
    """Test REPL command executor."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client."""
        client = MagicMock()
        # Mock client responses
        client.get_clients.return_value = {
            "items": [
                {"name": "client1", "nice_name": "Client One"},
                {"name": "client2", "nice_name": "Client Two"},
            ]
        }
        client.get_sites.return_value = {
            "items": [
                {"name": "site1", "client_name": "client1"},
                {"name": "site2", "client_name": "client1"},
            ]
        }
        client.get_gateways.return_value = {
            "items": [
                {"name": "gw1", "site_name": "site1"},
                {"name": "gw2", "site_name": "site2"},
            ]
        }
        return client

    @pytest.fixture
    def mock_cli(self):
        """Create a mock CLI group."""

        @click.group()
        def cli():
            pass

        return cli

    @pytest.fixture
    def executor(self, mock_cli, mock_api_client):
        """Create an executor with mocked dependencies."""
        ctx = click.Context(mock_cli)
        ctx.obj = {"client": mock_api_client}
        return ReplCommandExecutor(mock_cli, ctx)

    def test_use_command_with_name(self, executor, mock_api_client):
        """Test use command with explicit name."""
        context = ReplContext()
        parsed_cmd = MagicMock()
        parsed_cmd.command_path = ["use"]
        parsed_cmd.arguments = ["site", "site1"]

        result = executor._handle_use_command(["site", "site1"], context)

        assert "Switched to site context: site1" in result
        assert context.current_site == "site1"
        mock_api_client.get_site.assert_called_once_with("site1")

    def test_use_command_interactive_single_item(self, executor, mock_api_client, capsys):
        """Test use command with single item auto-selection."""
        # Mock single site response
        mock_api_client.get_sites.return_value = {
            "items": [{"name": "only-site", "client_name": "client1"}]
        }

        context = ReplContext()

        result = executor._handle_use_command(["site"], context)

        # Check stdout for auto-select message
        captured = capsys.readouterr()
        assert ("Auto-selecting the only available site: only-site" in captured.out or
                "Auto-selecting the only site matching filter: only-site" in captured.out)

        # Check returned result
        assert "Switched to site context: only-site" in result
        assert context.current_site == "only-site"

    @patch("click.prompt")
    def test_use_command_interactive_selection(self, mock_prompt, executor, mock_api_client):
        """Test use command with interactive selection."""
        mock_prompt.return_value = 2  # Select second site

        context = ReplContext()

        result = executor._handle_use_command(["site"], context)

        assert "Switched to site context: site2" in result
        assert context.current_site == "site2"

    def test_use_command_no_api_client(self, mock_cli):
        """Test use command when API client is not configured."""
        ctx = click.Context(mock_cli)
        ctx.obj = {}  # No client
        executor = ReplCommandExecutor(mock_cli, ctx)
        context = ReplContext()

        result = executor._handle_use_command(["site", "test"], context)

        assert "API client not configured" in result

    def test_use_command_invalid_type(self, executor):
        """Test use command with invalid context type."""
        context = ReplContext()

        result = executor._handle_use_command(["invalid"], context)

        assert "Invalid context type" in result

    def test_context_filtering(self, executor, mock_api_client):
        """Test that sites are filtered by client context."""
        context = ReplContext()
        context.enter_context(ContextType.CLIENT, "client1")

        executor._handle_use_command(["site"], context)

        # Check that get_sites was called with client filter
        mock_api_client.get_sites.assert_called_with(per_page=100, client_name="client1")

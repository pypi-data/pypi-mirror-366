"""Simple test for site timeseries command in REPL context."""

from unittest.mock import MagicMock

import click
import pytest

from aceiot_models_cli.repl.context import ContextType, ReplContext
from aceiot_models_cli.repl.executor_new import ReplCommandExecutor


class TestReplSiteTimeseriesSimple:
    """Test site timeseries command availability in REPL."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client."""
        return MagicMock()

    @pytest.fixture
    def mock_cli(self):
        """Create a mock CLI group."""
        @click.group()
        def cli():
            pass
        
        # Add sites group with timeseries command
        @cli.group()
        def sites():
            pass
        
        @sites.command("timeseries")
        @click.argument("site_name")
        @click.option("--start", required=True)
        @click.option("--end", required=True)
        def timeseries(site_name, start, end):
            """Export timeseries data."""
            pass

        return cli

    @pytest.fixture
    def executor(self, mock_cli, mock_api_client):
        """Create an executor with mocked dependencies."""
        ctx = click.Context(mock_cli)
        ctx.obj = {"client": mock_api_client}
        return ReplCommandExecutor(mock_cli, ctx)

    def test_timeseries_help_shown_in_site_context(self, executor):
        """Test that timeseries command is shown in help when in site context."""
        context = ReplContext()
        context.enter_context(ContextType.SITE, "demo-site")
        
        help_text = executor._show_general_help(context)
        
        assert "timeseries" in help_text
        assert "Export all timeseries data for current site" in help_text

    def test_sites_timeseries_command_exists_in_cli(self, mock_cli):
        """Test that sites timeseries command exists in CLI structure."""
        # Check that sites group exists
        assert "sites" in mock_cli.commands
        
        # Check that timeseries command exists in sites group
        sites_group = mock_cli.commands["sites"]
        assert "timeseries" in sites_group.commands

    def test_context_commands_loaded(self, executor):
        """Test that context commands are loaded properly."""
        # The executor should have loaded commands from the site module
        # This is a basic smoke test to ensure the loading doesn't fail
        assert hasattr(executor, '_load_repl_commands')
        
        # After loading, we should be able to find context commands
        from aceiot_models_cli.commands.base import command_registry
        
        # Get commands for site context
        site_commands = command_registry.get_commands_for_context(ContextType.SITE)
        
        # Check if timeseries is among them
        command_names = [cmd.name for cmd in site_commands]
        assert "timeseries" in command_names or "sites.timeseries" in command_names
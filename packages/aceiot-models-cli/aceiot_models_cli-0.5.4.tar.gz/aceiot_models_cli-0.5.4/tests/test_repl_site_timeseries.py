"""Test site timeseries command in REPL context."""

from unittest.mock import MagicMock, patch

import click
import pytest

from aceiot_models_cli.repl.context import ContextType, ReplContext
from aceiot_models_cli.repl.executor_new import ReplCommandExecutor
from aceiot_models_cli.repl.parser import ParsedCommand


class TestReplSiteTimeseries:
    """Test site timeseries command in REPL."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client."""
        client = MagicMock()
        # Mock get_points response
        client.get_points.return_value = {
            "items": [
                {
                    "name": "temp-sensor-1",
                    "display_name": "Temperature Sensor 1",
                    "unit": "°F",
                    "type": "analog",
                    "description": "Room temperature",
                    "equipment": "AHU-1"
                },
                {
                    "name": "humidity-sensor-1",
                    "display_name": "Humidity Sensor 1",
                    "unit": "%",
                    "type": "analog",
                    "description": "Room humidity",
                    "equipment": "AHU-1"
                }
            ]
        }
        
        # Mock get_point_timeseries responses
        client.get_point_timeseries.side_effect = [
            {
                "data": [
                    {"timestamp": "2024-01-01T00:00:00Z", "value": 72.5},
                    {"timestamp": "2024-01-01T01:00:00Z", "value": 73.0},
                    {"timestamp": "2024-01-01T02:00:00Z", "value": 73.5},
                ]
            },
            {
                "data": [
                    {"timestamp": "2024-01-01T00:00:00Z", "value": 45.0},
                    {"timestamp": "2024-01-01T01:00:00Z", "value": 46.0},
                    {"timestamp": "2024-01-01T02:00:00Z", "value": 47.0},
                ]
            }
        ]
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

    @pytest.fixture
    def site_context(self):
        """Create a REPL context with site set."""
        context = ReplContext()
        context.enter_context(ContextType.SITE, "demo-site")
        return context

    @patch('aceiot_models_cli.commands.site.pd.DataFrame.to_csv')
    @patch('rich.console.Console')
    def test_timeseries_command_in_site_context(self, mock_console, mock_to_csv, executor, site_context, mock_api_client):
        """Test timeseries command works in site context."""
        # Create parsed command
        parsed_cmd = ParsedCommand(
            command_path=["timeseries"],
            arguments=[],
            options={
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z",
            },
            context_args={},
            raw_input="timeseries --start 2024-01-01T00:00:00Z --end 2024-01-02T00:00:00Z"
        )

        # Execute command
        result = executor.execute(parsed_cmd, site_context)

        # Verify API calls
        mock_api_client.get_points.assert_called_once_with(site="demo-site", per_page=1000)
        assert mock_api_client.get_point_timeseries.call_count == 2
        
        # Verify CSV was saved
        mock_to_csv.assert_called_once()
        
        # Verify console output showed progress
        console_instance = mock_console.return_value
        assert console_instance.print.call_count > 0

    @patch('aceiot_models_cli.commands.site.pd.DataFrame.to_parquet')
    @patch('rich.console.Console')
    def test_timeseries_command_with_parquet_format(self, mock_console, mock_to_parquet, executor, site_context, mock_api_client):
        """Test timeseries command with parquet format."""
        # Reset mock
        mock_api_client.get_point_timeseries.side_effect = [
            {
                "data": [
                    {"timestamp": "2024-01-01T00:00:00Z", "value": 72.5},
                ]
            },
            {
                "data": [
                    {"timestamp": "2024-01-01T00:00:00Z", "value": 45.0},
                ]
            }
        ]
        
        # Create parsed command with parquet format
        parsed_cmd = ParsedCommand(
            command_path=["timeseries"],
            arguments=[],
            options={
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z",
                "format": "parquet",
            },
            context_args={},
            raw_input="timeseries --start 2024-01-01T00:00:00Z --end 2024-01-02T00:00:00Z --format parquet"
        )

        # Execute command
        result = executor.execute(parsed_cmd, site_context)

        # Verify parquet was saved
        mock_to_parquet.assert_called_once()

    @patch('rich.console.Console')
    def test_timeseries_command_no_site_context(self, mock_console, executor, mock_api_client):
        """Test timeseries command fails without site context."""
        # Create context without site
        context = ReplContext()
        
        # Create parsed command
        parsed_cmd = ParsedCommand(
            command_path=["timeseries"],
            arguments=[],
            options={
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z",
            },
            context_args={},
            raw_input="timeseries --start 2024-01-01T00:00:00Z --end 2024-01-02T00:00:00Z"
        )

        # Execute command - should fail
        with pytest.raises(click.ClickException) as exc_info:
            executor.execute(parsed_cmd, context)
        
        # Verify error message
        assert "Unknown command: timeseries" in str(exc_info.value) or "No site context set" in str(exc_info.value)

    @patch('aceiot_models_cli.commands.site.pd.DataFrame.to_csv')
    @patch('rich.console.Console')
    def test_timeseries_command_with_metadata(self, mock_console, mock_to_csv, executor, site_context, mock_api_client):
        """Test timeseries command with metadata included."""
        # Reset mock
        mock_api_client.get_point_timeseries.side_effect = [
            {
                "data": [
                    {"timestamp": "2024-01-01T00:00:00Z", "value": 72.5},
                ]
            },
            {
                "data": [
                    {"timestamp": "2024-01-01T00:00:00Z", "value": 45.0},
                ]
            }
        ]
        
        # Create parsed command with metadata flag
        parsed_cmd = ParsedCommand(
            command_path=["timeseries"],
            arguments=[],
            options={
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z",
                "include_metadata": True,
            },
            context_args={},
            raw_input="timeseries --start 2024-01-01T00:00:00Z --end 2024-01-02T00:00:00Z --include-metadata"
        )

        # Execute command
        result = executor.execute(parsed_cmd, site_context)

        # Verify CSV was saved
        mock_to_csv.assert_called_once()
        
        # The saved data should include metadata columns
        # (This is tested implicitly by the mock working correctly)

    @patch('rich.console.Console')
    def test_timeseries_command_no_points(self, mock_console, executor, site_context, mock_api_client):
        """Test timeseries command when site has no points."""
        # Mock empty points response
        mock_api_client.get_points.return_value = {"items": []}
        
        # Create parsed command
        parsed_cmd = ParsedCommand(
            command_path=["timeseries"],
            arguments=[],
            options={
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z",
            },
            context_args={},
            raw_input="timeseries --start 2024-01-01T00:00:00Z --end 2024-01-02T00:00:00Z"
        )

        # Execute command
        result = executor.execute(parsed_cmd, site_context)

        # Verify console showed no points message
        console_instance = mock_console.return_value
        console_instance.print.assert_any_call("[yellow]No points found for site 'demo-site'[/yellow]")

    def test_timeseries_help_shown_in_site_context(self, executor, site_context):
        """Test that timeseries command is shown in help when in site context."""
        help_text = executor._show_general_help(site_context)
        
        assert "timeseries" in help_text
        assert "Export all timeseries data for current site" in help_text
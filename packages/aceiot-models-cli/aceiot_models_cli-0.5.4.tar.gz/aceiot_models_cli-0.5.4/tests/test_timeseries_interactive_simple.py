"""Simplified tests for interactive timeseries command."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import click

from aceiot_models_cli.repl.context import ReplContext, ContextType
from aceiot_models_cli.repl.parser import ReplCommandParser, ParsedCommand
from aceiot_models_cli.repl.executor_new import ReplCommandExecutor


@pytest.fixture
def setup_repl():
    """Set up REPL environment for testing."""
    # Create mock API client
    mock_client = Mock()
    
    # Mock the site timeseries endpoint with the actual API format
    mock_client.get_site_timeseries.return_value = {
        "point_samples": [
            {"name": "point1", "ts": "2024-01-01T00:00:00Z", "value": 70.0},
            {"name": "point1", "ts": "2024-01-01T01:00:00Z", "value": 71.0},
            {"name": "point2", "ts": "2024-01-01T00:00:00Z", "value": 100.0},
            {"name": "point2", "ts": "2024-01-01T01:00:00Z", "value": 101.0}
        ]
    }
    
    # Mock site points for metadata
    mock_client.get_site_points.return_value = {
        "items": [
            {"name": "point1", "display_name": "Point 1", "unit": "°F"},
            {"name": "point2", "display_name": "Point 2", "unit": "kW"}
        ]
    }
    
    # Fallback mocks for individual point queries
    mock_client.get_point_timeseries.return_value = {
        "data": [
            {"timestamp": "2024-01-01T00:00:00Z", "value": 70.0},
            {"timestamp": "2024-01-01T01:00:00Z", "value": 71.0}
        ]
    }
    
    # Create CLI and context
    @click.group()
    def cli():
        pass
    
    ctx = click.Context(cli)
    ctx.obj = {"client": mock_client}
    
    # Create REPL context with site
    repl_context = ReplContext()
    repl_context.enter_context(ContextType.SITE, "test-site")
    
    # Create parser and executor
    parser = ReplCommandParser(cli)
    executor = ReplCommandExecutor(cli, ctx)
    
    return parser, executor, repl_context, mock_client


def test_timeseries_interactive_mode(setup_repl):
    """Test interactive mode prompts work correctly."""
    parser, executor, repl_context, mock_client = setup_repl
    
    # Patch prompts and file operations
    with patch('rich.prompt.IntPrompt.ask') as mock_int_prompt, \
         patch('rich.prompt.Prompt.ask') as mock_prompt, \
         patch('pandas.DataFrame.to_csv') as mock_csv:
        
        # Simulate user selecting "Last hour" and CSV format
        mock_int_prompt.side_effect = ["2", "1"]  # Last hour, CSV
        mock_prompt.return_value = "n"  # No metadata
        
        # Parse and execute command
        parsed_cmd = parser.parse("timeseries", repl_context)
        result = executor.execute(parsed_cmd, repl_context)
        
        # Verify prompts were called
        assert mock_int_prompt.call_count == 2  # Time range and format selection
        assert mock_prompt.call_count == 1  # Metadata inclusion
        
        # Verify CSV export was called
        assert mock_csv.called


def test_timeseries_custom_range(setup_repl):
    """Test custom time range selection."""
    parser, executor, repl_context, mock_client = setup_repl
    
    with patch('rich.prompt.IntPrompt.ask') as mock_int_prompt, \
         patch('rich.prompt.Prompt.ask') as mock_prompt, \
         patch('pandas.DataFrame.to_csv'):
        
        # Select custom range (option 10) and CSV
        mock_int_prompt.side_effect = ["10", "1"]
        # Provide custom times and no metadata
        mock_prompt.side_effect = [
            "2024-01-01T00:00:00Z",  # Start
            "2024-01-02T00:00:00Z",  # End
            "n"  # No metadata
        ]
        
        parsed_cmd = parser.parse("timeseries", repl_context)
        result = executor.execute(parsed_cmd, repl_context)
        
        # Verify extra prompts for custom times
        assert mock_prompt.call_count == 3


def test_timeseries_parquet_format(setup_repl):
    """Test Parquet format selection."""
    parser, executor, repl_context, mock_client = setup_repl
    
    with patch('rich.prompt.IntPrompt.ask') as mock_int_prompt, \
         patch('rich.prompt.Prompt.ask') as mock_prompt, \
         patch('pandas.DataFrame.to_parquet') as mock_parquet:
        
        # Select last 15 minutes and Parquet
        mock_int_prompt.side_effect = ["1", "2"]  # Last 15 min, Parquet
        mock_prompt.return_value = "y"  # Include metadata
        
        parsed_cmd = parser.parse("timeseries", repl_context)
        result = executor.execute(parsed_cmd, repl_context)
        
        # Verify parquet export was called
        assert mock_parquet.called


def test_timeseries_non_interactive(setup_repl):
    """Test that providing arguments skips interactive mode."""
    parser, executor, repl_context, mock_client = setup_repl
    
    with patch('pandas.DataFrame.to_csv'), \
         patch('rich.prompt.IntPrompt.ask') as mock_prompt:
        
        # This should not prompt
        mock_prompt.side_effect = Exception("Should not prompt")
        
        # Parse command with arguments
        parsed_cmd = parser.parse(
            "timeseries --start 2024-01-01T00:00:00Z --end 2024-01-02T00:00:00Z", 
            repl_context
        )
        
        # Should execute without prompting
        result = executor.execute(parsed_cmd, repl_context)
        
        # Verify no prompts were shown
        assert not mock_prompt.called
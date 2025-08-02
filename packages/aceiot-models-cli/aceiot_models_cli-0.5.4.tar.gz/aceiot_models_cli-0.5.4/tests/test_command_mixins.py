"""Comprehensive tests for command mixins."""

import json
import os
from unittest.mock import MagicMock, Mock, patch

import click
import pytest
from aceiot_models.api import APIError

from aceiot_models_cli.commands.base import BaseCommand
from aceiot_models_cli.commands.utils import (
    ErrorHandlerMixin,
    OutputFormatterMixin,
    PaginationMixin,
    ProgressIndicatorMixin,
)


class TestOutputFormatterMixin:
    """Test OutputFormatterMixin functionality."""
    
    def setup_method(self):
        """Create a test class with the mixin."""
        class TestCommand(OutputFormatterMixin):
            pass
        
        self.command = TestCommand()
        self.ctx = click.Context(click.Command("test"))
        self.ctx.obj = {"output": "table"}
    
    def test_format_output_json(self, capsys):
        """Test JSON output formatting."""
        self.ctx.obj["output"] = "json"
        data = {"name": "test", "value": 123}
        
        self.command.format_output(data, self.ctx)
        
        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == data
    
    def test_format_output_test_mode_single_item(self, capsys):
        """Test plain output formatting in test mode for single item."""
        # Set test mode
        os.environ["PYTEST_CURRENT_TEST"] = "test"
        
        data = {
            "nice_name": "Test Site",
            "id": "123",
            "client": "test-client",
            "vpn_ip": "10.0.0.1",
            "archived": False
        }
        
        self.command.format_output(data, self.ctx, title="Site: test-site")
        
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        
        assert "Site: test-site" in lines[0]
        assert "Nice Name: Test Site" in lines[1]
        assert "ID: 123" in lines[2]
        assert "Client: test-client" in lines[3]
        assert "VPN IP: 10.0.0.1" in lines[4]
        assert "Archived: No" in lines[5]
        
        # Clean up
        del os.environ["PYTEST_CURRENT_TEST"]
    
    def test_format_output_test_mode_list(self, capsys):
        """Test plain output formatting in test mode for list."""
        # Set test mode
        os.environ["PYTEST_CURRENT_TEST"] = "test"
        
        data = {
            "items": [
                {"name": "site1", "nice_name": "Site One", "client": "client1"},
                {"name": "site2", "nice_name": "Site Two", "client": "client2"}
            ],
            "page": 1,
            "pages": 2,
            "total": 10
        }
        
        self.command.format_output(data, self.ctx)
        
        captured = capsys.readouterr()
        output = captured.out.strip()
        
        assert "Name: site1" in output
        assert "Nice Name: Site One" in output
        assert "Client: client1" in output
        assert "Name: site2" in output
        assert "Nice Name: Site Two" in output
        assert "Client: client2" in output
        assert "Page 1 of 2 (Total: 10)" in output
        
        # Clean up
        del os.environ["PYTEST_CURRENT_TEST"]
    
    def test_format_output_empty_list(self, capsys):
        """Test formatting empty list."""
        os.environ["PYTEST_CURRENT_TEST"] = "test"
        
        data = {"items": []}
        
        self.command.format_output(data, self.ctx)
        
        captured = capsys.readouterr()
        assert "No results found." in captured.out
        
        del os.environ["PYTEST_CURRENT_TEST"]
    
    @patch('aceiot_models_cli.commands.utils.Console')
    def test_format_rich_output_table(self, mock_console):
        """Test rich table output formatting."""
        # Ensure we're not in test mode
        original_env = os.environ.get("PYTEST_CURRENT_TEST")
        if original_env:
            del os.environ["PYTEST_CURRENT_TEST"]
        
        try:
            data = {
                "items": [
                    {"name": "item1", "value": 10},
                    {"name": "item2", "value": 20}
                ],
                "page": 1,
                "pages": 1,
                "total": 2
            }
            
            self.command.format_output(data, self.ctx, title="Test Results")
            
            # Verify Console was used
            mock_console.assert_called_once()
            console_instance = mock_console.return_value
            console_instance.print.assert_called_once()
        finally:
            # Restore original env
            if original_env:
                os.environ["PYTEST_CURRENT_TEST"] = original_env
    
    @patch('aceiot_models_cli.commands.utils.Console')
    def test_format_rich_output_single_item(self, mock_console):
        """Test rich table output for single item."""
        # Ensure we're not in test mode
        original_env = os.environ.get("PYTEST_CURRENT_TEST")
        if original_env:
            del os.environ["PYTEST_CURRENT_TEST"]
        
        try:
            data = {"name": "test", "value": 123, "active": True}
            
            self.command.format_output(
                data,
                self.ctx,
                title="Item Details",
                exclude_fields=["active"]
            )
            
            # Verify Console was used
            mock_console.assert_called_once()
            console_instance = mock_console.return_value
            console_instance.print.assert_called_once()
        finally:
            # Restore original env
            if original_env:
                os.environ["PYTEST_CURRENT_TEST"] = original_env
    
    def test_format_list_output_json(self, capsys):
        """Test format_list_output with JSON."""
        self.ctx.obj["output"] = "json"
        items = [{"id": 1, "name": "test"}]
        
        self.command.format_list_output(items, self.ctx)
        
        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output == items
    
    @patch('aceiot_models_cli.commands.utils.Console')
    def test_format_list_output_table_with_columns(self, mock_console):
        """Test format_list_output with specified columns."""
        # Ensure we're not in test mode
        original_env = os.environ.get("PYTEST_CURRENT_TEST")
        if original_env:
            del os.environ["PYTEST_CURRENT_TEST"]
        
        try:
            items = [
                {"id": 1, "name": "test1", "extra": "data"},
                {"id": 2, "name": "test2", "extra": "more"}
            ]
            
            self.command.format_list_output(
                items,
                self.ctx,
                title="Test List",
                columns=["ID", "Name"]
            )
            
            # Verify Console was used
            mock_console.assert_called_once()
            console_instance = mock_console.return_value
            console_instance.print.assert_called_once()
        finally:
            # Restore original env
            if original_env:
                os.environ["PYTEST_CURRENT_TEST"] = original_env


class TestErrorHandlerMixin:
    """Test ErrorHandlerMixin functionality."""
    
    def setup_method(self):
        """Create a test class with the mixin."""
        class TestCommand(ErrorHandlerMixin, BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        self.command = TestCommand()
        self.ctx = click.Context(click.Command("test"))
    
    @patch('aceiot_models_cli.formatters.print_error')
    def test_handle_api_error_with_operation(self, mock_print_error):
        """Test handling APIError with operation context."""
        error = APIError("Bad request", status_code=400)
        
        with pytest.raises(click.exceptions.Exit) as exc_info:
            self.command.handle_api_error(error, self.ctx, operation="create site")
        
        assert exc_info.value.exit_code == 1
        mock_print_error.assert_called_once_with("Failed to create site: Bad request")
    
    @patch('aceiot_models_cli.formatters.print_error')
    def test_handle_api_error_without_operation(self, mock_print_error):
        """Test handling APIError without operation context."""
        error = APIError("Server error", status_code=500)
        
        with pytest.raises(click.exceptions.Exit) as exc_info:
            self.command.handle_api_error(error, self.ctx)
        
        assert exc_info.value.exit_code == 1
        mock_print_error.assert_called_once_with("API Error: Server error")
    
    @patch('aceiot_models_cli.formatters.print_error')
    def test_handle_api_error_with_response_data(self, mock_print_error):
        """Test handling APIError with response data."""
        error = APIError("Bad request", status_code=400)
        error.response_data = {"detail": "Invalid field value"}
        
        with pytest.raises(click.exceptions.Exit) as exc_info:
            self.command.handle_api_error(error, self.ctx)
        
        assert exc_info.value.exit_code == 1
        mock_print_error.assert_called_once_with("API Error: Invalid field value")
    
    @patch('aceiot_models_cli.formatters.print_error')
    def test_handle_generic_error(self, mock_print_error):
        """Test handling generic exceptions."""
        error = ValueError("Invalid input")
        
        with pytest.raises(click.exceptions.Exit) as exc_info:
            self.command.handle_api_error(error, self.ctx, operation="process data")
        
        assert exc_info.value.exit_code == 1
        mock_print_error.assert_called_once_with("Failed to process data: Invalid input")
    
    @patch('aceiot_models_cli.formatters.print_error')
    def test_handle_error_non_base_command(self, mock_print_error):
        """Test error handling when not a BaseCommand instance."""
        class PlainCommand(ErrorHandlerMixin):
            pass
        
        command = PlainCommand()
        error = APIError("Error", status_code=400)
        
        with pytest.raises(click.exceptions.Exit) as exc_info:
            command.handle_api_error(error, self.ctx)
        
        assert exc_info.value.exit_code == 1
        mock_print_error.assert_called_once_with("API Error: Error")


class TestProgressIndicatorMixin:
    """Test ProgressIndicatorMixin functionality."""
    
    def setup_method(self):
        """Create a test class with the mixin."""
        class TestCommand(ProgressIndicatorMixin):
            pass
        
        self.command = TestCommand()
    
    @patch('rich.progress.Progress')
    @patch('rich.console.Console')
    def test_with_progress(self, mock_console, mock_progress_class):
        """Test executing function with progress indicator."""
        # Setup mock
        mock_progress = MagicMock()
        mock_progress_class.return_value.__enter__.return_value = mock_progress
        
        # Test function
        def test_func(arg1, arg2, kwarg1=None):
            return f"Result: {arg1}, {arg2}, {kwarg1}"
        
        # Execute with progress
        result = self.command.with_progress(
            "Processing...",
            test_func,
            "a",
            "b",
            kwarg1="c"
        )
        
        # Verify
        assert result == "Result: a, b, c"
        mock_progress.add_task.assert_called_once_with("Processing...", total=None)
    
    @patch('rich.progress.Progress')
    @patch('rich.console.Console')
    def test_with_progress_exception(self, mock_console, mock_progress_class):
        """Test progress indicator when function raises exception."""
        # Setup mock
        mock_progress = MagicMock()
        mock_progress_class.return_value.__enter__.return_value = mock_progress
        
        # Test function that raises
        def failing_func():
            raise ValueError("Test error")
        
        # Execute and expect exception
        with pytest.raises(ValueError, match="Test error"):
            self.command.with_progress("Processing...", failing_func)
        
        # Progress should still have been started
        mock_progress.add_task.assert_called_once()


class TestPaginationMixin:
    """Test PaginationMixin functionality."""
    
    def setup_method(self):
        """Create a test class with the mixin."""
        class TestCommand(PaginationMixin):
            pass
        
        self.command = TestCommand()
    
    def test_add_pagination_options(self):
        """Test adding pagination options to a click command."""
        @click.command()
        def test_cmd():
            """Test command"""
        
        # Add pagination options
        decorated_cmd = self.command.add_pagination_options(test_cmd)
        
        # Check options were added
        param_names = [p.name for p in decorated_cmd.params]
        assert "page" in param_names
        assert "per_page" in param_names  # Click converts per-page to per_page
        
        # Check defaults
        page_param = next(p for p in decorated_cmd.params if p.name == "page")
        per_page_param = next(p for p in decorated_cmd.params if p.name == "per_page")
        
        assert page_param.default == 1
        assert per_page_param.default == 10
    
    def test_pagination_options_help_text(self):
        """Test pagination options have proper help text."""
        @click.command()
        def test_cmd():
            pass
        
        decorated_cmd = self.command.add_pagination_options(test_cmd)
        
        page_param = next(p for p in decorated_cmd.params if p.name == "page")
        per_page_param = next(p for p in decorated_cmd.params if p.name == "per_page")
        
        assert page_param.help == "Page number"
        assert per_page_param.help == "Results per page"


class TestMixinIntegration:
    """Test multiple mixins working together."""
    
    def test_combined_mixins(self):
        """Test a command using multiple mixins."""
        class TestCommand(
            OutputFormatterMixin,
            ErrorHandlerMixin,
            ProgressIndicatorMixin,
            PaginationMixin,
            BaseCommand
        ):
            def get_click_command(self):
                @click.command()
                def cmd():
                    pass
                return self.add_pagination_options(cmd)
        
        command = TestCommand()
        
        # Verify all mixin methods are available
        assert hasattr(command, 'format_output')
        assert hasattr(command, 'handle_api_error')
        assert hasattr(command, 'with_progress')
        assert hasattr(command, 'add_pagination_options')
        
        # Get click command and verify pagination was added
        click_cmd = command.get_click_command()
        param_names = [p.name for p in click_cmd.params]
        assert "page" in param_names
        assert "per_page" in param_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

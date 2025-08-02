"""Tests for REPL get command."""

import json
import tempfile
from unittest.mock import Mock, patch

import pytest
from click import Context as ClickContext

from aceiot_models_cli.cli import cli
from aceiot_models_cli.repl.context import ContextType, ReplContext
from aceiot_models_cli.repl.executor_new import ReplCommandExecutor
from aceiot_models_cli.repl.parser import ParsedCommand


class TestReplGetCommand:
    """Test the simple 'get' command in REPL."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client."""
        return Mock()

    @pytest.fixture
    def repl_context(self):
        """Create a REPL context."""
        return ReplContext()

    @pytest.fixture
    def click_context(self, mock_api_client):
        """Create a Click context with mock client."""
        ctx = ClickContext(cli)
        ctx.obj = {"client": mock_api_client, "output": "table"}
        return ctx

    @pytest.fixture
    def executor(self, click_context):
        """Create a REPL command executor."""
        return ReplCommandExecutor(cli, click_context)

    def test_get_in_client_context(self, executor, repl_context, mock_api_client):
        """Test 'get' command in client context."""
        # Set up client context
        repl_context.enter_context(ContextType.CLIENT, "test-client")
        
        # Mock API response
        mock_api_client.get_client.return_value = {
            "name": "test-client",
            "nice_name": "Test Client",
            "id": "123",
        }
        
        # Execute simple get command
        parsed_cmd = ParsedCommand(
            command_path=["get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="get"
        )
        
        result = executor._execute_repl_command(parsed_cmd, repl_context)
        
        # Should return JSON by default
        assert "test-client" in result
        assert "Test Client" in result
        mock_api_client.get_client.assert_called_once_with("test-client")

    def test_get_in_site_context(self, executor, repl_context, mock_api_client):
        """Test 'get' command in site context."""
        # Set up site context
        repl_context.enter_context(ContextType.SITE, "test-site")
        
        # Mock API response
        mock_api_client.get_site.return_value = {
            "name": "test-site",
            "nice_name": "Test Site",
            "id": "456",
        }
        
        # Execute simple get command
        parsed_cmd = ParsedCommand(
            command_path=["get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="get"
        )
        
        result = executor._execute_repl_command(parsed_cmd, repl_context)
        
        # Should return JSON by default
        assert "test-site" in result
        assert "Test Site" in result
        mock_api_client.get_site.assert_called_once_with("test-site")

    def test_get_in_gateway_context(self, executor, repl_context, mock_api_client):
        """Test 'get' command in gateway context."""
        # Set up gateway context
        repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Mock API response
        mock_api_client.get_gateway.return_value = {
            "name": "test-gateway",
            "nice_name": "Test Gateway",
            "id": "789",
            "vpn_ip": "10.0.0.1",
        }
        
        # Execute simple get command
        parsed_cmd = ParsedCommand(
            command_path=["get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="get"
        )
        
        result = executor._execute_repl_command(parsed_cmd, repl_context)
        
        # Should return JSON by default
        assert "test-gateway" in result
        assert "Test Gateway" in result
        mock_api_client.get_gateway.assert_called_once_with("test-gateway")

    def test_get_with_output_table(self, executor, repl_context, mock_api_client):
        """Test 'get' command with table output."""
        # Set up gateway context
        repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Mock API response
        mock_api_client.get_gateway.return_value = {
            "name": "test-gateway",
            "nice_name": "Test Gateway",
            "id": "789",
            "vpn_ip": "10.0.0.1",
        }
        
        # Execute get command with table output
        parsed_cmd = ParsedCommand(
            command_path=["get"],
            arguments=["--output", "table"],
            options={},
            context_args={},
            raw_input="get --output table"
        )
        
        result = executor._execute_repl_command(parsed_cmd, repl_context)
        
        # Should return table format
        assert "Gateway: test-gateway" in result
        assert "Nice Name: Test Gateway" in result
        assert "VPN IP: 10.0.0.1" in result

    def test_get_with_file_save(self, executor, repl_context, mock_api_client):
        """Test 'get' command with file save."""
        # Set up client context
        repl_context.enter_context(ContextType.CLIENT, "test-client")
        
        # Mock API response
        mock_data = {
            "name": "test-client",
            "nice_name": "Test Client",
            "id": "123",
        }
        mock_api_client.get_client.return_value = mock_data
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Execute get command with file save
            parsed_cmd = ParsedCommand(
                command_path=["get"],
                arguments=["--file", tmp_path],
                options={},
                context_args={},
                raw_input=f"get --file {tmp_path}"
            )
            
            result = executor._execute_repl_command(parsed_cmd, repl_context)
            
            # Check success message
            assert f"✓ Saved client data to {tmp_path}" in result
            
            # Verify file contents
            with open(tmp_path) as f:
                saved_data = json.load(f)
            assert saved_data == mock_data
            
        finally:
            import os
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_get_without_context(self, executor, repl_context, mock_api_client):
        """Test 'get' command without any context."""
        # No context set
        parsed_cmd = ParsedCommand(
            command_path=["get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="get"
        )
        
        result = executor._execute_repl_command(parsed_cmd, repl_context)
        
        # Should return error message
        assert "Error: No context set" in result
        assert "Use 'use <type> <name>'" in result

    def test_get_with_invalid_output_format(self, executor, repl_context, mock_api_client):
        """Test 'get' command with missing output format."""
        # Set up gateway context
        repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Execute get command with incomplete output option
        parsed_cmd = ParsedCommand(
            command_path=["get"],
            arguments=["--output"],
            options={},
            context_args={},
            raw_input="get --output"
        )
        
        result = executor._execute_repl_command(parsed_cmd, repl_context)
        
        # Should return error message
        assert "Error: --output requires a format" in result

    def test_get_with_nested_context(self, executor, repl_context, mock_api_client):
        """Test 'get' command in nested contexts returns the deepest context."""
        # Set up nested context: client -> site -> gateway
        repl_context.enter_context(ContextType.CLIENT, "test-client")
        repl_context.enter_context(ContextType.SITE, "test-site")
        repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Mock API response
        mock_api_client.get_gateway.return_value = {
            "name": "test-gateway",
            "nice_name": "Test Gateway",
            "id": "789",
        }
        
        # Execute simple get command
        parsed_cmd = ParsedCommand(
            command_path=["get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="get"
        )
        
        result = executor._execute_repl_command(parsed_cmd, repl_context)
        
        # Should get the gateway (deepest context)
        assert "test-gateway" in result
        mock_api_client.get_gateway.assert_called_once_with("test-gateway")

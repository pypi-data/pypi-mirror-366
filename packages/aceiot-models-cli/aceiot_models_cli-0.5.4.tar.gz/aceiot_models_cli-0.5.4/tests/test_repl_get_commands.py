"""Tests for REPL get commands in context."""

import json
from unittest.mock import Mock

import pytest
from click import Context as ClickContext

from aceiot_models_cli.cli import cli
from aceiot_models_cli.repl.context import ContextType, ReplContext
from aceiot_models_cli.repl.executor_new import ReplCommandExecutor
from aceiot_models_cli.repl.parser import ParsedCommand


class TestReplGetCommands:
    """Test get commands in REPL contexts."""

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
        ctx.obj = {"client": mock_api_client, "output": "json"}
        return ctx

    @pytest.fixture
    def executor(self, click_context):
        """Create a REPL command executor."""
        return ReplCommandExecutor(cli, click_context)

    def test_clients_get_in_client_context(self, executor, repl_context, mock_api_client):
        """Test 'clients get' command in client context."""
        # Set up client context
        repl_context.enter_context(ContextType.CLIENT, "test-client")
        
        # Mock API response
        mock_api_client.get_client.return_value = {
            "name": "test-client",
            "nice_name": "Test Client",
            "id": "123",
        }
        
        # Parse and execute command without arguments
        parsed_cmd = ParsedCommand(
            command_path=["clients", "get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="clients get"
        )
        
        result = executor._execute_cli_command(parsed_cmd, repl_context)
        
        # Verify the client name was injected from context
        mock_api_client.get_client.assert_called_once_with("test-client")

    def test_sites_get_in_site_context(self, executor, repl_context, mock_api_client):
        """Test 'sites get' command in site context."""
        # Set up site context
        repl_context.enter_context(ContextType.SITE, "test-site")
        
        # Mock API response
        mock_api_client.get_site.return_value = {
            "name": "test-site",
            "nice_name": "Test Site",
            "id": "456",
            "client": "test-client",
        }
        
        # Parse and execute command without arguments
        parsed_cmd = ParsedCommand(
            command_path=["sites", "get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="sites get"
        )
        
        result = executor._execute_cli_command(parsed_cmd, repl_context)
        
        # Verify the site name was injected from context
        mock_api_client.get_site.assert_called_once_with("test-site")

    def test_gateways_get_in_gateway_context(self, executor, repl_context, mock_api_client):
        """Test 'gateways get' command in gateway context."""
        # Set up gateway context
        repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Mock API response
        mock_api_client.get_gateway.return_value = {
            "name": "test-gateway",
            "nice_name": "Test Gateway",
            "id": "789",
            "client": "test-client",
            "site": "test-site",
            "vpn_ip": "10.0.0.1",
        }
        
        # Parse and execute command without arguments
        parsed_cmd = ParsedCommand(
            command_path=["gateways", "get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="gateways get"
        )
        
        result = executor._execute_cli_command(parsed_cmd, repl_context)
        
        # Verify the gateway name was injected from context
        mock_api_client.get_gateway.assert_called_once_with("test-gateway")

    def test_get_with_explicit_name_overrides_context(self, executor, repl_context, mock_api_client):
        """Test that explicit name argument overrides context."""
        # Set up client context
        repl_context.enter_context(ContextType.CLIENT, "context-client")
        
        # Mock API response
        mock_api_client.get_client.return_value = {
            "name": "explicit-client",
            "nice_name": "Explicit Client",
        }
        
        # Parse and execute command with explicit name
        parsed_cmd = ParsedCommand(
            command_path=["clients", "get"],
            arguments=["explicit-client"],
            options={},
            context_args={},
            raw_input="clients get explicit-client"
        )
        
        result = executor._execute_cli_command(parsed_cmd, repl_context)
        
        # Verify the explicit name was used, not context
        mock_api_client.get_client.assert_called_once_with("explicit-client")

    def test_get_without_context_or_argument_fails(self, executor, repl_context, mock_api_client):
        """Test that get command without context or argument fails appropriately."""
        # No context set, no argument provided
        parsed_cmd = ParsedCommand(
            command_path=["clients", "get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="clients get"
        )
        
        # This should raise an error from the CLI command itself
        with pytest.raises(Exception):  # The specific exception depends on Click's error handling
            executor._execute_cli_command(parsed_cmd, repl_context)

    def test_nested_context_get_commands(self, executor, repl_context, mock_api_client):
        """Test get commands work correctly in nested contexts."""
        # Set up nested context: client -> site -> gateway
        repl_context.enter_context(ContextType.CLIENT, "test-client")
        repl_context.enter_context(ContextType.SITE, "test-site")
        repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Mock responses
        mock_api_client.get_client.return_value = {"name": "test-client"}
        mock_api_client.get_site.return_value = {"name": "test-site"}
        mock_api_client.get_gateway.return_value = {"name": "test-gateway"}
        
        # Test that each entity type uses its own context
        # Test client get
        parsed_cmd = ParsedCommand(
            command_path=["clients", "get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="clients get"
        )
        executor._execute_cli_command(parsed_cmd, repl_context)
        mock_api_client.get_client.assert_called_once_with("test-client")
        
        # Test site get
        parsed_cmd = ParsedCommand(
            command_path=["sites", "get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="sites get"
        )
        executor._execute_cli_command(parsed_cmd, repl_context)
        mock_api_client.get_site.assert_called_once_with("test-site")
        
        # Test gateway get
        parsed_cmd = ParsedCommand(
            command_path=["gateways", "get"],
            arguments=[],
            options={},
            context_args={},
            raw_input="gateways get"
        )
        executor._execute_cli_command(parsed_cmd, repl_context)
        mock_api_client.get_gateway.assert_called_once_with("test-gateway")

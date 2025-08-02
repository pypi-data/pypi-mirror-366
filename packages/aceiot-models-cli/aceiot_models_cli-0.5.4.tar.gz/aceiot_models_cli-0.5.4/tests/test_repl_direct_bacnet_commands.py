"""Tests for direct BACnet commands in gateway REPL context."""

import sys
from io import StringIO
from unittest.mock import Mock

import pytest
from click import Context as ClickContext

from aceiot_models_cli.cli import cli
from aceiot_models_cli.repl.context import ContextType, ReplContext
from aceiot_models_cli.repl.executor_new import ReplCommandExecutor
from aceiot_models_cli.repl.parser import ReplCommandParser


class TestDirectBacnetCommands:
    """Test direct BACnet commands in gateway REPL context."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mocks
        self.mock_api_client = Mock()
        self.ctx = ClickContext(cli)
        self.ctx.obj = {"client": self.mock_api_client, "output": "table"}
        
        # Create executor and context
        self.executor = ReplCommandExecutor(cli, self.ctx)
        self.parser = ReplCommandParser(cli)
        self.repl_context = ReplContext()
        
        # Set up gateway context
        self.repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Sample gateway data
        self.gateway_data = {
            "name": "test-gateway",
            "site": "test-site",
            "client": "test-client",
            "deploy_config": {
                "deploy_bacnet": True,
                "trigger_scan": False,
                "trigger_deploy": False,
                "last_scan": "2024-01-01T00:00:00",
                "last_deploy": "2024-01-02T00:00:00",
                "bacnet_scan_address": "192.168.1.0/24",
            }
        }
    
    def test_direct_trigger_scan_command(self):
        """Test 'trigger-scan' command works directly in gateway context."""
        # Mock API responses
        self.mock_api_client.get_gateway.return_value = self.gateway_data.copy()
        self.mock_api_client.patch_gateway.return_value = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "trigger_scan": True,
            }
        }
        
        # Parse and execute command
        parsed_cmd = self.parser.parse("trigger-scan", self.repl_context)
        
        # Verify it's parsed as a REPL command
        assert parsed_cmd.command_path == ["trigger-scan"]
        
        # Execute command and capture output
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = self.executor.execute(parsed_cmd, self.repl_context)
            output = captured_output.getvalue()
        finally:
            sys.stdout = original_stdout
        
        # Verify the command executed successfully
        assert "BACnet scan triggered" in output
        self.mock_api_client.get_gateway.assert_called_with("test-gateway")
    
    def test_direct_deploy_points_command(self):
        """Test 'deploy-points' command works directly in gateway context."""
        # Mock API responses
        self.mock_api_client.get_gateway.return_value = self.gateway_data.copy()
        self.mock_api_client.patch_gateway.return_value = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "trigger_deploy": True,
            }
        }
        
        # Parse and execute command
        parsed_cmd = self.parser.parse("deploy-points", self.repl_context)
        
        # Execute command and capture output
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = self.executor.execute(parsed_cmd, self.repl_context)
            output = captured_output.getvalue()
        finally:
            sys.stdout = original_stdout
        
        # Verify the command executed successfully
        assert "Point deployment triggered" in output
    
    def test_direct_bacnet_status_command(self):
        """Test 'bacnet-status' command works directly in gateway context."""
        # Mock API response
        self.mock_api_client.get_gateway.return_value = self.gateway_data
        
        # Parse and execute command
        parsed_cmd = self.parser.parse("bacnet-status", self.repl_context)
        
        # Execute command and capture output
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = self.executor.execute(parsed_cmd, self.repl_context)
            output = captured_output.getvalue()
        finally:
            sys.stdout = original_stdout
        
        # Verify the command executed successfully
        assert "BACnet Status for Gateway: test-gateway" in output
    
    def test_direct_command_with_options(self):
        """Test direct BACnet command with options."""
        # Mock API responses
        self.mock_api_client.get_gateway.return_value = self.gateway_data.copy()
        self.mock_api_client.patch_gateway.return_value = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "trigger_scan": True,
                "bacnet_scan_address": "192.168.2.0/24",
            }
        }
        
        # Parse and execute command with options
        parsed_cmd = self.parser.parse("trigger-scan --scan-address 192.168.2.0/24", self.repl_context)
        
        # Execute command and capture output
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = self.executor.execute(parsed_cmd, self.repl_context)
            output = captured_output.getvalue()
        finally:
            sys.stdout = original_stdout
        
        # Verify the command executed successfully with options
        assert "BACnet scan triggered" in output
        assert "Scan address updated to: 192.168.2.0/24" in output
    
    def test_bacnet_command_outside_gateway_context(self):
        """Test BACnet commands are not REPL commands outside gateway context."""
        # Exit gateway context
        self.repl_context.exit_context()
        
        # Parse command - should fail as it's not a valid CLI command
        import click
        with pytest.raises(click.ClickException) as exc_info:
            parsed_cmd = self.parser.parse("trigger-scan", self.repl_context)
        
        # Should fail with "Unknown command"
        assert "Unknown command: trigger-scan" in str(exc_info.value)
    
    def test_full_gateway_command_still_works(self):
        """Test that full 'gateways trigger-scan' command still works in gateway context."""
        # Mock API responses
        self.mock_api_client.get_gateway.return_value = self.gateway_data.copy()
        self.mock_api_client.patch_gateway.return_value = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "trigger_scan": True,
            }
        }
        
        # Parse and execute full command
        parsed_cmd = self.parser.parse("gateways trigger-scan", self.repl_context)
        
        # Should be parsed as CLI command
        assert parsed_cmd.command_path == ["gateways", "trigger-scan"]
        
        # Execute command and capture output
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = self.executor.execute(parsed_cmd, self.repl_context)
            output = captured_output.getvalue()
        finally:
            sys.stdout = original_stdout
        
        # Should work with automatic gateway injection
        assert "BACnet scan triggered" in output

"""Tests for BACnet management commands."""

import json

from aceiot_models_cli.cli import cli


class TestBacnetCommands:
    """Test BACnet management commands."""

    def setup_method(self):
        """Set up test fixtures."""
        # Sample gateway data
        self.gateway_data = {
            "name": "test-gateway",
            "site": "test-site",
            "client": "test-client",
            "vpn_ip": "10.0.0.1",
            "deploy_config": {
                "deploy_bacnet": True,
                "trigger_scan": False,
                "trigger_deploy": False,
                "last_scan": "2024-01-01T00:00:00",
                "last_deploy": "2024-01-02T00:00:00",
                "bacnet_scan_address": "192.168.1.0/24",
                "bacnet_proxy_address": "192.168.1.1/24",
                "bacnet_scan_object_id": 708113,
                "bacnet_proxy_object_id": 708112,
            }
        }

    def test_trigger_scan_command(self, runner, mock_load_config, mock_api_client_class):
        """Test trigger-scan command."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_gateway.return_value = self.gateway_data.copy()
        mock_api_client.patch_gateway.return_value = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "trigger_scan": True,
            }
        }
        
        result = runner.invoke(cli, ["gateways", "trigger-scan", "test-gateway"])
        
        assert result.exit_code == 0
        assert "BACnet scan triggered" in result.output
        assert "Last scan: 2024-01-01T00:00:00" in result.output
        
        # Verify API calls
        mock_api_client.get_gateway.assert_called_once_with("test-gateway")
        mock_api_client.patch_gateway.assert_called_once()
        call_args = mock_api_client.patch_gateway.call_args
        assert call_args[0][0] == "test-gateway"
        assert call_args[0][1]["deploy_config"]["trigger_scan"] is True

    def test_trigger_scan_with_address(self, runner, mock_load_config, mock_api_client_class):
        """Test trigger-scan command with custom scan address."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_gateway.return_value = self.gateway_data.copy()
        mock_api_client.patch_gateway.return_value = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "trigger_scan": True,
                "bacnet_scan_address": "192.168.2.0/24",
            }
        }
        
        result = runner.invoke(
            cli,
            ["gateways", "trigger-scan", "test-gateway", "--scan-address", "192.168.2.0/24"]
        )
            
        assert result.exit_code == 0
        assert "BACnet scan triggered" in result.output
        assert "Scan address updated to: 192.168.2.0/24" in result.output
        
        # Verify the update included both fields
        mock_api_client.patch_gateway.assert_called_once()
        call_args = mock_api_client.patch_gateway.call_args
        # Check if args were passed positionally or as kwargs
        if call_args.args and len(call_args.args) >= 2:
            deploy_config = call_args.args[1]["deploy_config"]
        else:
            # Handle potential None case
            assert call_args is not None, "patch_gateway was not called"
            deploy_config = call_args[0][1]["deploy_config"]
        assert deploy_config["trigger_scan"] is True
        assert deploy_config["bacnet_scan_address"] == "192.168.2.0/24"

    def test_deploy_points_command(self, runner, mock_load_config, mock_api_client_class):
        """Test deploy-points command."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_gateway.return_value = self.gateway_data.copy()
        mock_api_client.patch_gateway.return_value = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "trigger_deploy": True,
            }
        }
        
        result = runner.invoke(
            cli, ["gateways", "deploy-points", "test-gateway"]
        )
            
        assert result.exit_code == 0
        assert "Point deployment triggered" in result.output
        assert "Last deploy: 2024-01-02T00:00:00" in result.output
        
        # Verify API calls
        call_args = mock_api_client.patch_gateway.call_args
        assert call_args[0][1]["deploy_config"]["trigger_deploy"] is True

    def test_enable_bacnet_command(self, runner, mock_load_config, mock_api_client_class):
        """Test enable-bacnet command."""
        mock_api_client = mock_api_client_class.return_value
        gateway_disabled = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "deploy_bacnet": False,
            }
        }
        
        mock_api_client.get_gateway.return_value = gateway_disabled
        mock_api_client.patch_gateway.return_value = self.gateway_data  # Enabled version
        
        result = runner.invoke(
            cli, ["gateways", "enable-bacnet", "test-gateway"]
        )
            
        assert result.exit_code == 0
        assert "BACnet enabled" in result.output
        
        # Verify API calls
        call_args = mock_api_client.patch_gateway.call_args
        assert call_args[0][1]["deploy_config"]["deploy_bacnet"] is True

    def test_disable_bacnet_command(self, runner, mock_load_config, mock_api_client_class):
        """Test disable-bacnet command."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_gateway.return_value = self.gateway_data.copy()
        mock_api_client.patch_gateway.return_value = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "deploy_bacnet": False,
            }
        }
        
        result = runner.invoke(
            cli, ["gateways", "disable-bacnet", "test-gateway"]
        )
            
        assert result.exit_code == 0
        assert "BACnet disabled" in result.output
        
        # Verify API calls
        call_args = mock_api_client.patch_gateway.call_args
        assert call_args[0][1]["deploy_config"]["deploy_bacnet"] is False

    def test_bacnet_status_table_format(self, runner, mock_load_config, mock_api_client_class):
        """Test bacnet-status command with table format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_gateway.return_value = self.gateway_data
        
        result = runner.invoke(
            cli, ["gateways", "bacnet-status", "test-gateway"]
        )
            
        assert result.exit_code == 0
        assert "BACnet Status for Gateway: test-gateway" in result.output
        assert "BACnet Enabled: True" in result.output
        assert "Scan Pending: False" in result.output
        assert "Deploy Pending: False" in result.output
        assert "Scan Address: 192.168.1.0/24" in result.output
        assert "Proxy Address: 192.168.1.1/24" in result.output
        assert "Scan Object ID: 708113" in result.output
        assert "Proxy Object ID: 708112" in result.output
        assert "Last Scan: 2024-01-01T00:00:00" in result.output
        assert "Last Deploy: 2024-01-02T00:00:00" in result.output

    def test_bacnet_status_json_format(self, runner, mock_load_config, mock_api_client_class):
        """Test bacnet-status command with JSON format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_gateway.return_value = self.gateway_data
        
        result = runner.invoke(
            cli, ["gateways", "bacnet-status", "test-gateway", "-o", "json"]
        )
            
        assert result.exit_code == 0
        
        # Parse JSON output
        output_json = json.loads(result.output.strip())
        assert output_json["gateway"] == "test-gateway"
        assert output_json["bacnet_enabled"] is True
        assert output_json["trigger_scan"] is False
        assert output_json["trigger_deploy"] is False
        assert output_json["bacnet_scan_address"] == "192.168.1.0/24"
        assert output_json["bacnet_proxy_address"] == "192.168.1.1/24"
        assert output_json["bacnet_scan_object_id"] == 708113
        assert output_json["bacnet_proxy_object_id"] == 708112

    def test_command_error_handling(self, runner, mock_load_config, mock_api_client_class):
        """Test error handling in BACnet commands."""
        from aceiot_models.api import APIError
        
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_gateway.side_effect = APIError(
            "Gateway not found", response_data={"detail": "Gateway 'bad-gateway' not found"}
        )
        
        result = runner.invoke(
            cli, ["gateways", "trigger-scan", "bad-gateway"]
        )
            
        assert result.exit_code == 1
        assert "Failed to update gateway" in result.output

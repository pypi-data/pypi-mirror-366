"""Tests for gateway commands."""

import json

from aceiot_models_cli.cli import cli


class TestGatewayCommands:
    """Test gateway-related CLI commands."""

    def test_list_gateways_table(self, runner, mock_load_config, mock_api_client_class):
        """Test listing gateways in table format."""
        mock_api_client = mock_api_client_class.return_value
        # Mock response
        mock_api_client.get_gateways.return_value = {
            "items": [
                {
                    "name": "gateway1",
                    "site": "site1",
                    "client": "client1",
                    "vpn_ip": "10.0.0.1",
                    "archived": False,
                    "updated": "2024-01-15T10:30:00Z",
                },
                {
                    "name": "gateway2",
                    "site": "site2",
                    "client": "client1",
                    "vpn_ip": "10.0.0.2",
                    "archived": True,
                    "updated": "2024-01-14T09:00:00Z",
                },
            ],
            "page": 1,
            "pages": 1,
            "total": 2,
        }

        result = runner.invoke(cli, ["gateways", "list"])

        assert result.exit_code == 0
        assert "gateway1" in result.output
        assert "site1" in result.output
        assert "10.0.0.1" in result.output
        assert "No" in result.output  # Not archived
        assert "gateway2" in result.output
        assert "Yes" in result.output  # Archived
        assert "Page 1 of 1 (Total: 2)" in result.output

    def test_list_gateways_json(self, runner, mock_load_config, mock_api_client_class):
        """Test listing gateways in JSON format."""
        mock_api_client = mock_api_client_class.return_value
        mock_response = {
            "items": [{"name": "gateway1", "site": "site1"}],
            "page": 1,
            "pages": 1,
            "total": 1,
        }
        mock_api_client.get_gateways.return_value = mock_response

        result = runner.invoke(cli, ["--output", "json", "gateways", "list"])

        assert result.exit_code == 0
        output_json = json.loads(result.output)
        assert output_json == mock_response

    def test_get_gateway_table(self, runner, mock_load_config, mock_api_client_class):
        """Test getting a specific gateway in table format."""
        mock_api_client = mock_api_client_class.return_value
        # Mock response
        mock_api_client.get_gateway.return_value = {
            "name": "gateway1",
            "nice_name": "Gateway One",
            "id": "123",
            "client": "client1",
            "site": "site1",
            "vpn_ip": "10.0.0.1",
            "archived": False,
            "updated": "2024-01-15T10:30:00Z",
        }

        result = runner.invoke(cli, ["gateways", "get", "gateway1"])

        assert result.exit_code == 0
        assert "Gateway: gateway1" in result.output
        assert "Nice Name: Gateway One" in result.output
        assert "ID: 123" in result.output
        assert "Client: client1" in result.output
        assert "Site: site1" in result.output
        assert "VPN IP: 10.0.0.1" in result.output
        assert "Archived: No" in result.output
        assert "Updated: 2024-01-15T10:30:00" in result.output

    def test_get_gateway_json(self, runner, mock_load_config, mock_api_client_class):
        """Test getting a specific gateway in JSON format."""
        mock_api_client = mock_api_client_class.return_value
        mock_response = {
            "name": "gateway1",
            "nice_name": "Gateway One",
            "id": "123",
            "client": "client1",
            "site": "site1",
            "vpn_ip": "10.0.0.1",
            "archived": False,
            "updated": "2024-01-15T10:30:00Z",
        }
        mock_api_client.get_gateway.return_value = mock_response

        result = runner.invoke(cli, ["--output", "json", "gateways", "get", "gateway1"])

        assert result.exit_code == 0
        output_json = json.loads(result.output)
        assert output_json == mock_response

    def test_get_gateway_error(self, runner, mock_load_config, mock_api_client_class):
        """Test handling errors when getting a gateway."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_gateway.side_effect = Exception("Gateway not found")

        result = runner.invoke(cli, ["gateways", "get", "nonexistent"])

        assert result.exit_code == 1
        assert "Failed to get gateway: Gateway not found" in result.output

    def test_list_gateways_with_pagination(self, runner, mock_load_config, mock_api_client_class):
        """Test listing gateways with pagination options."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_gateways.return_value = {
            "items": [],
            "page": 2,
            "pages": 5,
            "total": 50,
        }

        result = runner.invoke(
            cli,
            ["gateways", "list", "--page", "2", "--per-page", "10"],
        )

        assert result.exit_code == 0
        mock_api_client.get_gateways.assert_called_once_with(
            page=2, per_page=10, show_archived=False
        )
        assert "Page 2 of 5 (Total: 50)" in result.output

    def test_list_gateways_show_archived(self, runner, mock_load_config, mock_api_client_class):
        """Test listing gateways including archived ones."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_gateways.return_value = {
            "items": [],
            "page": 1,
            "pages": 1,
            "total": 0,
        }

        result = runner.invoke(
            cli,
            ["gateways", "list", "--show-archived"],
        )

        assert result.exit_code == 0
        mock_api_client.get_gateways.assert_called_once_with(
            page=1, per_page=10, show_archived=True
        )

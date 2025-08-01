"""Tests for client commands."""

import json

from aceiot_models_cli.cli import cli


class TestClientCommands:
    """Test client-related commands."""

    def test_list_clients_table(self, runner, mock_load_config, mock_api_client_class):
        """Test listing clients in table format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_clients.return_value = {
            "items": [
                {
                    "id": 1,
                    "name": "client1",
                    "nice_name": "Client One",
                    "bus_contact": "bus@example.com",
                    "tech_contact": "tech@example.com",
                },
                {
                    "id": 2,
                    "name": "client2",
                    "nice_name": "Client Two",
                    "bus_contact": "bus2@example.com",
                    "tech_contact": "tech2@example.com",
                },
            ],
            "page": 1,
            "pages": 1,
            "per_page": 10,
            "total": 2,
        }

        result = runner.invoke(cli, ["clients", "list"])
        assert result.exit_code == 0
        assert "Client One" in result.output
        assert "Client Two" in result.output
        assert "Page 1 of 1" in result.output
        mock_api_client.get_clients.assert_called_once_with(page=1, per_page=10)

    def test_list_clients_json(self, runner, mock_load_config, mock_api_client_class):
        """Test listing clients in JSON format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_clients.return_value = {
            "items": [{"id": 1, "name": "client1"}],
            "total": 1,
        }

        result = runner.invoke(cli, ["--output", "json", "clients", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "client1"

    def test_list_clients_pagination(self, runner, mock_load_config, mock_api_client_class):
        """Test listing clients with pagination."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_clients.return_value = {"items": [], "page": 2, "per_page": 5}

        result = runner.invoke(cli, ["clients", "list", "--page", "2", "--per-page", "5"])
        assert result.exit_code == 0
        mock_api_client.get_clients.assert_called_once_with(page=2, per_page=5)

    def test_get_client_table(self, runner, mock_load_config, mock_api_client_class):
        """Test getting a specific client in table format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_client.return_value = {
            "id": 1,
            "name": "test-client",
            "nice_name": "Test Client",
            "bus_contact": "bus@test.com",
            "tech_contact": "tech@test.com",
            "address": "123 Test St",
        }

        result = runner.invoke(cli, ["clients", "get", "test-client"])
        assert result.exit_code == 0
        assert "Client: test-client" in result.output
        assert "Nice Name: Test Client" in result.output
        assert "Address: 123 Test St" in result.output
        mock_api_client.get_client.assert_called_once_with("test-client")

    def test_get_client_json(self, runner, mock_load_config, mock_api_client_class):
        """Test getting a specific client in JSON format."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_client.return_value = {"id": 1, "name": "test-client"}

        result = runner.invoke(cli, ["--output", "json", "clients", "get", "test-client"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "test-client"

    def test_get_client_error(self, runner, mock_load_config, mock_api_client_class):
        """Test getting a client that doesn't exist."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.get_client.side_effect = Exception("Client not found")

        result = runner.invoke(cli, ["clients", "get", "nonexistent"])
        assert result.exit_code == 1
        assert "Failed to get client" in result.output

    def test_create_client_minimal(self, runner, mock_load_config, mock_api_client_class):
        """Test creating a client with minimal info."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.create_client.return_value = {"id": 1, "name": "new-client"}

        result = runner.invoke(cli, ["clients", "create", "--name", "new-client"])
        assert result.exit_code == 0
        assert "Client 'new-client' created successfully" in result.output

    def test_create_client_full(self, runner, mock_load_config, mock_api_client_class):
        """Test creating a client with full info."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.create_client.return_value = {"id": 1, "name": "new-client"}

        result = runner.invoke(
            cli,
            [
                "clients",
                "create",
                "--name",
                "new-client",
                "--nice-name",
                "New Client",
                "--bus-contact",
                "bus@new.com",
                "--tech-contact",
                "tech@new.com",
                "--address",
                "456 New St",
            ],
        )
        assert result.exit_code == 0
        assert "Client 'new-client' created successfully" in result.output

    def test_create_client_error(self, runner, mock_load_config, mock_api_client_class):
        """Test creating a client with error."""
        mock_api_client = mock_api_client_class.return_value
        mock_api_client.create_client.side_effect = Exception("Duplicate client")

        result = runner.invoke(cli, ["clients", "create", "--name", "duplicate"])
        assert result.exit_code == 1
        assert "Failed to create client" in result.output

    def test_no_api_key_error(self, runner):
        """Test error when no API key is configured."""
        from unittest.mock import patch

        with patch("aceiot_models_cli.cli.load_config") as mock_load:
            from aceiot_models_cli.config import Config

            mock_load.return_value = Config(api_key=None)
            result = runner.invoke(cli, ["clients", "list"])
            assert result.exit_code == 1
            assert "API key is required" in result.output

"""Tests for configuration management."""

import os
from pathlib import Path
from unittest.mock import mock_open, patch

import yaml

from aceiot_models_cli.config import (
    Config,
    get_default_config_path,
    init_config,
    load_config,
    save_config,
)


class TestConfig:
    """Test Config class."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = Config()
        assert config.api_url == "https://flightdeck.aceiot.cloud/api"
        assert config.api_key is None
        assert config.output_format == "table"
        assert config.timeout == 30

    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "api_url": "https://custom.api.com",
            "api_key": "custom-key",
            "output_format": "json",
            "timeout": 60,
        }
        config = Config.from_dict(data)
        assert config.api_url == "https://custom.api.com"
        assert config.api_key == "custom-key"
        assert config.output_format == "json"
        assert config.timeout == 60

    def test_config_from_dict_partial(self):
        """Test creating config from partial dictionary."""
        data = {"api_key": "test-key"}
        config = Config.from_dict(data)
        assert config.api_key == "test-key"
        assert config.api_url == "https://flightdeck.aceiot.cloud/api"  # default
        assert config.output_format == "table"  # default

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(api_key="test-key", timeout=45)
        data = config.to_dict()
        assert data == {
            "api_url": "https://flightdeck.aceiot.cloud/api",
            "api_key": "test-key",
            "output_format": "table",
            "timeout": 45,
        }


class TestConfigPaths:
    """Test configuration path functions."""

    def test_get_default_config_path_xdg(self):
        """Test getting default config path with XDG_CONFIG_HOME."""
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/config"}):
            path = get_default_config_path()
            assert path == Path("/custom/config/aceiot-models-cli/config.yaml")

    def test_get_default_config_path_home(self):
        """Test getting default config path without XDG_CONFIG_HOME."""
        with patch.dict(os.environ, {}, clear=True), patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")
            path = get_default_config_path()
            assert path == Path("/home/user/.config/aceiot-models-cli/config.yaml")


class TestLoadConfig:
    """Test loading configuration."""

    def test_load_config_default(self):
        """Test loading config with defaults when file doesn't exist."""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            config = load_config()
            assert config.api_key is None
            assert config.api_url == "https://flightdeck.aceiot.cloud/api"

    def test_load_config_from_file(self):
        """Test loading config from file."""
        config_data = {"api_key": "file-key", "api_url": "https://file.api.com"}
        yaml_content = yaml.dump(config_data)

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("builtins.open", mock_open(read_data=yaml_content)):
                config = load_config()
                assert config.api_key == "file-key"
                assert config.api_url == "https://file.api.com"

    def test_load_config_custom_path(self):
        """Test loading config from custom path."""
        config_data = {"api_key": "custom-key"}
        yaml_content = yaml.dump(config_data)

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("builtins.open", mock_open(read_data=yaml_content)):
                config = load_config("/custom/path.yaml")
                assert config.api_key == "custom-key"

    def test_load_config_invalid_yaml(self):
        """Test loading config with invalid YAML."""
        invalid_yaml = "invalid: yaml: content:"

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            with (
                patch("builtins.open", mock_open(read_data=invalid_yaml)),
                patch("click.echo") as mock_echo,
            ):
                config = load_config()
                # Should return default config on error
                assert config.api_key is None
                # Should print warning
                mock_echo.assert_called_once()
                assert "Warning: Failed to load config" in mock_echo.call_args[0][0]

    def test_load_config_env_override(self):
        """Test loading config with environment variable overrides."""
        config_data = {"api_key": "file-key", "api_url": "https://file.api.com"}
        yaml_content = yaml.dump(config_data)

        env_vars = {
            "ACEIOT_API_KEY": "env-key",
            "ACEIOT_API_URL": "https://env.api.com",
            "ACEIOT_OUTPUT_FORMAT": "json",
            "ACEIOT_TIMEOUT": "45",
        }

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            with (
                patch("builtins.open", mock_open(read_data=yaml_content)),
                patch.dict(os.environ, env_vars),
            ):
                config = load_config()
                assert config.api_key == "env-key"
                assert config.api_url == "https://env.api.com"
                assert config.output_format == "json"
                assert config.timeout == 45

    def test_load_config_invalid_timeout(self):
        """Test loading config with invalid timeout in env var."""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            with patch.dict(os.environ, {"ACEIOT_TIMEOUT": "invalid"}):
                config = load_config()
                assert config.timeout == 30  # Should keep default


class TestSaveConfig:
    """Test saving configuration."""

    def test_save_config_default_path(self):
        """Test saving config to default path."""
        config = Config(api_key="test-key")

        with (
            patch("pathlib.Path.mkdir") as mock_mkdir,
            patch("builtins.open", mock_open()) as mock_file,
            patch("aceiot_models_cli.config.get_default_config_path") as mock_get_path,
        ):
            mock_get_path.return_value = Path("/home/user/.config/aceiot-models-cli/config.yaml")
            save_config(config)

            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mock_file.assert_called_once()
            handle = mock_file()
            written_content = "".join(call.args[0] for call in handle.write.call_args_list)
            data = yaml.safe_load(written_content)
            assert data["api_key"] == "test-key"

    def test_save_config_custom_path(self):
        """Test saving config to custom path."""
        config = Config(api_key="test-key")

        with patch("pathlib.Path.mkdir"), patch("builtins.open", mock_open()) as mock_file:
            save_config(config, "/custom/path.yaml")
            mock_file.assert_called_once_with(Path("/custom/path.yaml"), "w")


class TestInitConfig:
    """Test configuration initialization."""

    @patch("click.prompt")
    @patch("click.confirm")
    @patch("aceiot_models_cli.config.save_config")
    def test_init_config_new(self, mock_save, mock_confirm, mock_prompt):
        """Test initializing new configuration."""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            init_config(api_key="test-key", api_url="https://test.api.com")

            mock_confirm.assert_not_called()
            mock_prompt.assert_not_called()
            mock_save.assert_called_once()
            saved_config = mock_save.call_args[0][0]
            assert saved_config.api_key == "test-key"
            assert saved_config.api_url == "https://test.api.com"

    @patch("click.prompt")
    @patch("click.confirm")
    @patch("aceiot_models_cli.config.save_config")
    def test_init_config_overwrite(self, mock_save, mock_confirm, mock_prompt):
        """Test initializing config with existing file."""
        mock_confirm.return_value = True

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            init_config(api_key="test-key")

            mock_confirm.assert_called_once()
            mock_save.assert_called_once()

    @patch("click.confirm")
    @patch("aceiot_models_cli.config.save_config")
    def test_init_config_no_overwrite(self, mock_save, mock_confirm):
        """Test declining to overwrite existing config."""
        mock_confirm.return_value = False

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            init_config(api_key="test-key")

            mock_confirm.assert_called_once()
            mock_save.assert_not_called()

    @patch("click.prompt")
    @patch("aceiot_models_cli.config.save_config")
    def test_init_config_prompt_values(self, mock_save, mock_prompt):
        """Test prompting for values during init."""
        mock_prompt.side_effect = ["prompted-key", "https://prompted.api.com"]

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            init_config()

            assert mock_prompt.call_count == 2
            mock_save.assert_called_once()
            saved_config = mock_save.call_args[0][0]
            assert saved_config.api_key == "prompted-key"
            assert saved_config.api_url == "https://prompted.api.com"

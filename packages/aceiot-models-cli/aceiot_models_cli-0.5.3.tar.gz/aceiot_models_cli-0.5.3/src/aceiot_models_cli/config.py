"""Configuration management for aceiot-models-cli."""

import contextlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click
import yaml


@dataclass
class Config:
    """Configuration for the CLI."""

    api_url: str = "https://flightdeck.aceiot.cloud/api"
    api_key: str | None = None
    output_format: str = "table"
    timeout: int = 30

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """Create config from dictionary."""
        return cls(
            api_url=data.get("api_url", cls.api_url),
            api_key=data.get("api_key"),
            output_format=data.get("output_format", cls.output_format),
            timeout=data.get("timeout", cls.timeout),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "api_url": self.api_url,
            "api_key": self.api_key,
            "output_format": self.output_format,
            "timeout": self.timeout,
        }


def get_default_config_path() -> Path:
    """Get the default configuration file path."""
    # Check XDG_CONFIG_HOME first
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "aceiot-models-cli" / "config.yaml"

    # Fall back to ~/.config
    return Path.home() / ".config" / "aceiot-models-cli" / "config.yaml"


def load_config(config_path: str | None = None) -> Config:
    """Load configuration from file.

    Args:
        config_path: Path to configuration file. If None, uses default paths.

    Returns:
        Config object
    """
    config = Config()

    # Determine config file path
    path = Path(config_path) if config_path else get_default_config_path()

    # Load from file if it exists
    if path.exists():
        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
                config = Config.from_dict(data)
        except Exception as e:
            click.echo(f"Warning: Failed to load config from {path}: {e}", err=True)

    # Override with environment variables
    if os.environ.get("ACEIOT_API_URL"):
        config.api_url = os.environ["ACEIOT_API_URL"]

    if os.environ.get("ACEIOT_API_KEY"):
        config.api_key = os.environ["ACEIOT_API_KEY"]

    if os.environ.get("ACEIOT_OUTPUT_FORMAT"):
        config.output_format = os.environ["ACEIOT_OUTPUT_FORMAT"]

    if os.environ.get("ACEIOT_TIMEOUT"):
        with contextlib.suppress(ValueError):
            config.timeout = int(os.environ["ACEIOT_TIMEOUT"])

    return config


def save_config(config: Config, config_path: str | None = None) -> None:
    """Save configuration to file.

    Args:
        config: Config object to save
        config_path: Path to save configuration. If None, uses default path.
    """
    # Determine config file path
    path = Path(config_path) if config_path else get_default_config_path()

    # Create directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # Save config
    with open(path, "w") as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False)


def init_config(api_key: str | None = None, api_url: str | None = None) -> None:
    """Initialize configuration file with user input.

    Args:
        api_key: API key to use
        api_url: API URL to use
    """
    config_path = get_default_config_path()

    # Check if config already exists
    if config_path.exists() and not click.confirm(
        f"Config file already exists at {config_path}. Overwrite?"
    ):
        return

    # Get values from user if not provided
    if not api_key:
        api_key = click.prompt("Enter your API key", hide_input=True)

    if not api_url:
        api_url = click.prompt(
            "Enter the API URL",
            default="https://flightdeck.aceiot.cloud/api",
        )

    # Create config
    config = Config(api_url=api_url or "https://flightdeck.aceiot.cloud/api", api_key=api_key)

    # Save config
    save_config(config)
    click.echo(f"Configuration saved to {config_path}")

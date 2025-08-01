"""Output formatters for the CLI."""

import json
from typing import Any

import click
from rich.console import Console
from rich.table import Table

console = Console()


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as JSON string."""
    return json.dumps(data, indent=indent, default=str)


def format_table(headers: list[str], rows: list[list[Any]], title: str | None = None) -> str:
    """Format data as a table using rich."""
    table = Table(title=title, show_header=True, header_style="bold cyan")

    # Add columns
    for header in headers:
        table.add_column(header)

    # Add rows
    for row in rows:
        # Convert all values to strings
        str_row = [str(val) for val in row]
        table.add_row(*str_row)

    # Render to string
    with console.capture() as capture:
        console.print(table)

    return capture.get()


def print_success(message: str) -> None:
    """Print a success message in green."""
    click.echo(click.style(f"✓ {message}", fg="green"))


def print_error(message: str) -> None:
    """Print an error message in red."""
    click.echo(click.style(f"✗ {message}", fg="red"), err=True)


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    click.echo(click.style(f"⚠ {message}", fg="yellow"))


def print_info(message: str) -> None:
    """Print an info message in blue."""
    click.echo(click.style(f"ℹ {message}", fg="blue"))


def format_key_value(data: dict[str, Any], indent: str = "  ") -> str:
    """Format dictionary as key-value pairs."""
    lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for sub_key, sub_value in value.items():
                lines.append(f"{indent}{sub_key}: {sub_value}")
        elif isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"{indent}- {item}")
        else:
            lines.append(f"{key}: {value}")

    return "\n".join(lines)


def format_datetime(dt_str: str | None) -> str:
    """Format datetime string for display."""
    if not dt_str:
        return "N/A"

    # Try to parse and format nicely
    try:
        from datetime import datetime

        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        # Fall back to original string
        return dt_str


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate string to maximum length."""
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def format_size(size_bytes: int) -> str:
    """Format byte size as human-readable string."""
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0

    return f"{size:.1f} PB"

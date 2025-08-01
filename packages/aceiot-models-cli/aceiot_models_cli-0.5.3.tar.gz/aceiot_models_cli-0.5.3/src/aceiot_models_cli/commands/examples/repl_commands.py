"""Example: REPL-specific commands using new architecture."""


import click
from rich.table import Table

from ...repl.context import ContextType, ReplContext
from ..decorators import repl_command


@repl_command(
    name="use",
    description="Switch to a context",
    aliases=["cd", "switch"]
)
def use_command(args: list[str], context: ReplContext, executor: Any) -> str:
    """Handle 'use <type> [<name>]' command."""
    if len(args) < 1:
        return "Usage: use <client|site|gateway|volttron> [<name>]"

    context_type_str = args[0].lower()

    try:
        context_type = ContextType(context_type_str)
    except ValueError:
        return f"Invalid context type: {context_type_str}. Valid types: client, site, gateway, volttron"

    # If name provided, use it directly
    if len(args) >= 2:
        name = args[1]
        return executor._switch_to_context(context_type, name, context)
    # No name provided - list available resources and let user choose
    return executor._interactive_context_selection(context_type, context)


@repl_command(
    name="back",
    description="Exit current context",
    aliases=["cd..", "up"]
)
def back_command(args: list[str], context: ReplContext, executor: Any) -> str:
    """Handle 'back' command to exit current context."""
    if context.exit_context():
        return "Exited context"
    return "Already at global context"


@repl_command(
    name="context",
    description="Show current context",
    aliases=["pwd", "whereami"]
)
def context_command(args: list[str], context: ReplContext, executor: Any) -> str:
    """Handle 'context' command to show current context."""
    if context.is_global:
        return "Current context: global"
    path = context.get_context_path()
    return f"Current context: {path}"


@repl_command(
    name="clear",
    description="Clear screen",
    aliases=["cls"]
)
def clear_command(args: list[str], context: ReplContext, executor: Any) -> str:
    """Handle 'clear' command to clear screen."""
    click.clear()
    return ""


@repl_command(
    name="get",
    description="Get current context entity",
    aliases=["show", "info"]
)
def get_command(args: list[str], context: ReplContext, executor: Any) -> str:
    """Handle 'get' command to get current context entity."""
    import json

    # Determine what to get based on context
    if context.is_global:
        return "Error: No context set. Use 'use <type> <name>' to set a context first."

    # Build the appropriate entity info based on context
    if context.current_client and not context.current_site and not context.current_gateway:
        entity_type = "client"
        entity_name = context.current_client
    elif context.current_site and not context.current_gateway:
        entity_type = "site"
        entity_name = context.current_site
    elif context.current_gateway:
        entity_type = "gateway"
        entity_name = context.current_gateway
    else:
        return "Error: Unable to determine context entity"

    # Check for file save option
    save_file = None
    output_format = "json"  # Default to JSON for get command

    # Parse options
    i = 0
    while i < len(args):
        if args[i] in ["-f", "--file", "--save"]:
            if i + 1 < len(args):
                save_file = args[i + 1]
                i += 2
            else:
                return "Error: --file requires a filename"
        elif args[i] in ["-o", "--output"]:
            if i + 1 < len(args):
                output_format = args[i + 1]
                i += 2
            else:
                return "Error: --output requires a format (json or table)"
        else:
            i += 1

    # Get API client from executor
    api_client = executor._get_api_client()
    if not api_client:
        return "Error: API client not configured"

    try:
        # Get the entity data
        if entity_type == "client":
            if entity_name is not None:
                data = api_client.get_client(entity_name)
            else:
                return "Error: Client name cannot be None"
        elif entity_type == "site":
            data = api_client.get_site(entity_name)
        elif entity_type == "gateway":
            if entity_name is not None:
                data = api_client.get_gateway(entity_name)
            else:
                return "Error: Gateway name cannot be None"

        # Format output
        if output_format == "json":
            output = json.dumps(data, indent=2)

            # Save to file if requested
            if save_file:
                try:
                    with open(save_file, 'w') as f:
                        f.write(output)
                    return f"✓ Saved {entity_type} data to {save_file}"
                except OSError as e:
                    return f"Error saving file: {e}"

            return output
        # Table format
        from rich.console import Console
        console = Console()

        table = Table(title=f"{entity_type.title()}: {entity_name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value")

        for key, value in data.items():
            table.add_row(key.replace("_", " ").title(), str(value))

        console.print(table)
        return ""

    except Exception as e:
        return f"Error: Failed to get {entity_type} data: {e}"

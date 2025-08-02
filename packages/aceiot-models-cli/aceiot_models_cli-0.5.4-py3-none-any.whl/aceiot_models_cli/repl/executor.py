"""Command execution for REPL mode."""

from typing import Any

import click
from aceiot_models.api import APIClient
from rich.console import Console
from rich.table import Table

from .context import ContextType, ReplContext
from .parser import ParsedCommand
from .volttron_repl import VolttronReplHandler


class ReplCommandExecutor:
    """Executes commands in REPL mode."""

    def __init__(self, click_group: click.Group, click_ctx: click.Context) -> None:
        self.click_group = click_group
        self.click_ctx = click_ctx
        self.console = Console()
        self.volttron_handler: VolttronReplHandler | None = None  # Will be created when needed

    def execute(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute a parsed command."""
        command_name = parsed_cmd.command_path[0]

        # Handle REPL-specific commands
        repl_commands = ["use", "back", "exit", "quit", "help", "context", "clear", "get"]

        # Add BACnet commands as REPL commands when in gateway context
        if context.current_gateway:
            bacnet_commands = ["trigger-scan", "deploy-points", "enable-bacnet", "disable-bacnet", "bacnet-status"]
            if command_name in bacnet_commands:
                return self._execute_repl_command(parsed_cmd, context)

        if command_name in repl_commands:
            return self._execute_repl_command(parsed_cmd, context)

        # Check if we're in volttron context and handle special commands
        if (
            context.current_frame
            and context.current_frame.type == ContextType.VOLTTRON
            and command_name in ["deploy", "upload", "list", "status"]
        ):
            return self._execute_volttron_command(parsed_cmd, context)

        # Execute CLI command
        return self._execute_cli_command(parsed_cmd, context)

    def _execute_repl_command(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute REPL-specific commands."""
        command = parsed_cmd.command_path[0]
        args = parsed_cmd.arguments

        if command == "use":
            return self._handle_use_command(args, context)
        if command == "back":
            return self._handle_back_command(context)
        if command in ["exit", "quit"]:
            return self._handle_exit_command(context)
        if command == "help":
            return self._handle_help_command(args, context)
        if command == "context":
            return self._handle_context_command(context)
        if command == "clear":
            return self._handle_clear_command()
        if command == "get":
            return self._handle_get_command(args, parsed_cmd, context)
        if command in ["trigger-scan", "deploy-points", "enable-bacnet", "disable-bacnet", "bacnet-status"]:
            return self._handle_bacnet_command(command, args, parsed_cmd, context)
        raise click.ClickException(f"Unknown REPL command: {command}")

    def _execute_cli_command(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute CLI commands with context injection."""
        # Resolve the command
        current_group: click.Command | click.Group = self.click_group
        for cmd_name in parsed_cmd.command_path:
            if isinstance(current_group, click.Group) and cmd_name in current_group.commands:
                current_group = current_group.commands[cmd_name]
            else:
                raise click.ClickException(
                    f"Command not found: {' '.join(parsed_cmd.command_path)}"
                )

        if not isinstance(current_group, click.Command):
            raise click.ClickException(f"Invalid command: {' '.join(parsed_cmd.command_path)}")

        # Special handling for points list command in gateway context
        if (
            parsed_cmd.command_path == ["points", "list"]
            and context.current_gateway
            and "site" not in parsed_cmd.options
        ):
            # Get the gateway's site
            gateway_site = self._get_gateway_site(context.current_gateway)
            if gateway_site:
                # Inject the site into the parsed command
                parsed_cmd.context_args["site"] = gateway_site

        # Special handling for get commands in context
        if len(parsed_cmd.command_path) == 2 and parsed_cmd.command_path[1] == "get":
            entity_type = parsed_cmd.command_path[0]

            # If no argument provided, use current context
            if len(parsed_cmd.arguments) == 0:
                if entity_type == "clients" and context.current_client:
                    parsed_cmd.arguments = [context.current_client]
                elif entity_type == "sites" and context.current_site:
                    parsed_cmd.arguments = [context.current_site]
                elif entity_type == "gateways" and context.current_gateway:
                    parsed_cmd.arguments = [context.current_gateway]
                else:
                    # No context available, let the command fail with its normal error
                    pass

        # Special handling for volttron list-packages command
        if (
            parsed_cmd.command_path == ["volttron", "list-packages"]
            and len(parsed_cmd.arguments) == 0
        ):  # No name argument provided
            # First check if we're in a client context
            if context.current_client:
                # Use the current client directly
                parsed_cmd.arguments = [context.current_client]
            # Otherwise check if we're in a gateway context
            elif context.current_gateway:
                # Use the current gateway directly (command will resolve to client)
                parsed_cmd.arguments = [context.current_gateway]

        # Special handling for BACnet commands in gateway context
        bacnet_gateway_commands = [
            ["gateways", "trigger-scan"],
            ["gateways", "deploy-points"],
            ["gateways", "enable-bacnet"],
            ["gateways", "disable-bacnet"],
            ["gateways", "bacnet-status"],
        ]

        if parsed_cmd.command_path in bacnet_gateway_commands and len(parsed_cmd.arguments) == 0 and context.current_gateway:
            # If no gateway argument provided and we're in gateway context
            parsed_cmd.arguments = [context.current_gateway]

        # Special handling for volttron commands that need gateway in gateway context
        volttron_gateway_commands = [
            ["volttron", "upload-agent"],
            ["volttron", "create-config"],
            ["volttron", "deploy"],
            ["volttron", "quick-deploy"],
            ["volttron", "get-config-package"],
        ]

        if parsed_cmd.command_path in volttron_gateway_commands:
            if parsed_cmd.command_path == ["volttron", "upload-agent"]:
                # upload-agent: path, name (client or gateway)
                if len(parsed_cmd.arguments) == 0:  # No arguments provided
                    raise click.ClickException(
                        "Missing required argument: PATH. Usage: volttron upload-agent <path>"
                    )
                if len(parsed_cmd.arguments) == 1:  # Only path provided
                    if context.current_gateway:
                        parsed_cmd.arguments.append(context.current_gateway)
                    elif context.current_client:
                        parsed_cmd.arguments.append(context.current_client)
                    else:
                        raise click.ClickException(
                            "Missing required argument: NAME. Usage: volttron upload-agent <path> <name>\nTip: Use 'use client <name>' or 'use gateway <name>' to set a context first."
                        )
            elif parsed_cmd.command_path == ["volttron", "create-config"]:
                # create-config: file, gateway
                if len(parsed_cmd.arguments) == 0:  # No arguments provided
                    raise click.ClickException(
                        "Missing required argument: FILE. Usage: volttron create-config <file>"
                    )
                if len(parsed_cmd.arguments) == 1:  # Only file provided
                    if context.current_gateway:
                        parsed_cmd.arguments.append(context.current_gateway)
                    else:
                        raise click.ClickException(
                            "Missing required argument: GATEWAY. Usage: volttron create-config <file> <gateway>\nTip: Use 'use gateway <name>' to set a gateway context first."
                        )
            elif parsed_cmd.command_path == ["volttron", "deploy"]:
                # deploy: gateway
                if len(parsed_cmd.arguments) == 0:  # No gateway provided
                    if context.current_gateway:
                        parsed_cmd.arguments = [context.current_gateway]
                    else:
                        raise click.ClickException(
                            "Missing required argument: GATEWAY. Usage: volttron deploy <gateway>\nTip: Use 'use gateway <name>' to set a gateway context first."
                        )
            elif parsed_cmd.command_path == ["volttron", "quick-deploy"]:
                # quick-deploy: path, config, gateway
                if len(parsed_cmd.arguments) == 0:  # No arguments provided
                    raise click.ClickException(
                        "Missing required arguments: PATH CONFIG. Usage: volttron quick-deploy <path> <config>"
                    )
                if len(parsed_cmd.arguments) == 1:  # Only path provided
                    raise click.ClickException(
                        "Missing required argument: CONFIG. Usage: volttron quick-deploy <path> <config>"
                    )
                if len(parsed_cmd.arguments) == 2:  # Path and config provided
                    if context.current_gateway:
                        parsed_cmd.arguments.append(context.current_gateway)
                    else:
                        raise click.ClickException(
                            "Missing required argument: GATEWAY. Usage: volttron quick-deploy <path> <config> <gateway>\nTip: Use 'use gateway <name>' to set a gateway context first."
                        )
            elif (
                parsed_cmd.command_path == ["volttron", "get-config-package"]
                and len(parsed_cmd.arguments) == 0
            ):
                # get-config-package: gateway - No gateway provided
                if context.current_gateway:
                    parsed_cmd.arguments = [context.current_gateway]
                else:
                    raise click.ClickException(
                        "Missing required argument: GATEWAY. Usage: volttron get-config-package <gateway>\nTip: Use 'use gateway <name>' to set a gateway context first."
                    )

        # Build command line args list with context injection
        args = self._build_command_args(parsed_cmd, current_group)

        # Create a new context for command execution
        try:
            # Parse the args and invoke the command
            with current_group.make_context(
                info_name=" ".join(parsed_cmd.command_path),
                args=args,
                parent=self.click_ctx,
                allow_extra_args=True,
                allow_interspersed_args=False,
            ) as cmd_ctx:
                # Copy parent context object
                cmd_ctx.obj = self.click_ctx.obj
                # Invoke the command with the parsed context
                return current_group.invoke(cmd_ctx)
        except click.ClickException:
            raise
        except Exception as e:
            raise click.ClickException(f"Command execution failed: {e}") from e

    def _merge_parameters(
        self, parsed_cmd: ParsedCommand, command: click.Command
    ) -> dict[str, Any]:
        """Merge user parameters with context parameters."""
        merged = {}

        # Get parameter names for this command
        param_names = {param.name for param in command.params}

        # Add context arguments if they match command parameters
        for key, value in parsed_cmd.context_args.items():
            if key in param_names:
                merged[key] = value

        # Add user options (override context)
        for key, value in parsed_cmd.options.items():
            # Convert short options to long names if needed
            param_name = self._resolve_parameter_name(key, command)
            if param_name and param_name in param_names:
                merged[param_name] = value

        # Add positional arguments
        positional_params = [p for p in command.params if isinstance(p, click.Argument)]
        for i, arg_value in enumerate(parsed_cmd.arguments):
            if i < len(positional_params):
                param_name = positional_params[i].name
                merged[param_name] = arg_value

        return merged

    def _build_command_args(self, parsed_cmd: ParsedCommand, command: click.Command) -> list[str]:
        """Build command line arguments list with context injection."""
        args = []

        # Get parameter info
        param_map = {param.name: param for param in command.params}

        # Add context arguments as options if they match command parameters
        for key, value in parsed_cmd.context_args.items():
            if key in param_map:
                param = param_map[key]
                if isinstance(param, click.Option):
                    # Find the option flag to use
                    opt_flag = None
                    for opt in param.opts:
                        if opt.startswith("--"):
                            opt_flag = opt
                            break
                    if opt_flag:
                        args.extend([opt_flag, str(value)])

        # Add user-provided options (these override context)
        for key, value in parsed_cmd.options.items():
            # Add the option with proper formatting
            if len(key) == 1:
                args.append(f"-{key}")
            else:
                args.append(f"--{key}")
            if value is not True:  # Skip for boolean flags
                args.append(str(value))

        # Add positional arguments
        args.extend(parsed_cmd.arguments)

        return args

    def _resolve_parameter_name(self, key: str, command: click.Command) -> str | None:
        """Resolve short option names to full parameter names."""
        for param in command.params:
            if isinstance(param, click.Option) and (
                key in param.opts or f"-{key}" in param.opts or f"--{key}" in param.opts
            ):
                return param.name
        return key

    def _handle_use_command(self, args: list[str], context: ReplContext) -> str:
        """Handle 'use <type> [<name>]' command with fuzzy matching support."""
        if len(args) < 1:
            return "Usage: use <client|site|gateway|volttron> [<name>]"

        context_type_str = args[0].lower()

        try:
            context_type = ContextType(context_type_str)
        except ValueError:
            return f"Invalid context type: {context_type_str}. Valid types: client, site, gateway, volttron"

        # If name provided, use it with fuzzy matching
        if len(args) >= 2:
            # Join all remaining args for multi-word names
            filter_text = " ".join(args[1:])
            return self._interactive_context_selection(context_type, context, filter_text)
        # No name provided - list all available resources
        return self._interactive_context_selection(context_type, context)

    def _handle_back_command(self, context: ReplContext) -> str:
        """Handle 'back' command to exit current context."""
        if context.exit_context():
            return "Exited context"
        return "Already at global context"

    def _handle_exit_command(self, context: ReplContext) -> str:
        """Handle 'exit' or 'quit' command."""
        # If user is in a context, confirm exit
        if not context.is_global:
            context_path = context.get_context_path()
            if not click.confirm(
                f"\nYou are currently in context: {context_path}\nAre you sure you want to exit?"
            ):
                return "Exit cancelled"

        # Clean exit message
        click.echo("\nGoodbye!")
        raise EOFError("User requested exit")

    def _handle_help_command(self, args: list[str], context: ReplContext) -> str:
        """Handle 'help' command."""
        if not args:
            return self._show_general_help(context)
        # TODO: Show help for specific command
        return f"Help for: {' '.join(args)}"

    def _handle_context_command(self, context: ReplContext) -> str:
        """Handle 'context' command to show current context."""
        if context.is_global:
            return "Current context: global"
        path = context.get_context_path()
        return f"Current context: {path}"

    def _handle_clear_command(self) -> str:
        """Handle 'clear' command to clear screen."""
        click.clear()
        return ""

    def _handle_get_command(self, args: list[str], parsed_cmd: ParsedCommand, context: ReplContext) -> Any:  # noqa: ARG002
        """Handle 'get' command to get current context entity."""
        import json

        # Determine what to get based on context
        if context.is_global:
            return "Error: No context set. Use 'use <type> <name>' to set a context first."

        # Build the appropriate CLI command based on context
        if context.current_client and not context.current_site and not context.current_gateway:
            # In client context
            entity_type = "clients"
            entity_name = context.current_client
        elif context.current_site and not context.current_gateway:
            # In site context
            entity_type = "sites"
            entity_name = context.current_site
        elif context.current_gateway:
            # In gateway context
            entity_type = "gateways"
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

        # Build new parsed command for the appropriate get command
        new_parsed_cmd = ParsedCommand(
            command_path=[entity_type, "get"],
            arguments=[entity_name],
            options={},
            context_args={},
            raw_input=f"{entity_type} get {entity_name}"
        )

        # Temporarily override output format in context
        original_output = self.click_ctx.obj.get("output", "table")
        self.click_ctx.obj["output"] = output_format

        try:
            # Execute the command and capture output
            import sys
            from io import StringIO

            captured_output = StringIO()
            original_stdout = sys.stdout
            sys.stdout = captured_output

            try:
                result = self._execute_cli_command(new_parsed_cmd, context)
                output = captured_output.getvalue()

                # If saving to file and output is JSON
                if save_file and output_format == "json":
                    try:
                        # Parse and pretty-print the JSON
                        json_data = json.loads(output)
                        from pathlib import Path
                        Path(save_file).write_text(json.dumps(json_data, indent=2))
                        return f"✓ Saved {entity_type[:-1]} data to {save_file}"
                    except json.JSONDecodeError:
                        return "Error: Failed to parse JSON output"
                    except OSError as e:
                        return f"Error saving file: {e}"

                # Return the output
                return output.strip() if output else result

            finally:
                sys.stdout = original_stdout

        finally:
            # Restore original output format
            self.click_ctx.obj["output"] = original_output

    def _handle_bacnet_command(self, command: str, args: list[str], parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Handle BACnet commands in gateway context."""
        if not context.current_gateway:
            return "Error: BACnet commands require a gateway context. Use 'use gateway <name>' first."

        # Build the full CLI command
        new_parsed_cmd = ParsedCommand(
            command_path=["gateways", command],
            arguments=[context.current_gateway] + args,  # Inject gateway name
            options=parsed_cmd.options,
            context_args={},
            raw_input=f"gateways {command} {context.current_gateway}"
        )

        # Execute the CLI command
        return self._execute_cli_command(new_parsed_cmd, context)

    def _show_general_help(self, context: ReplContext) -> str:
        """Show general REPL help."""
        help_text = """
ACE IoT Models CLI - Interactive Mode

REPL Commands:
  help [command]         Show help for command or general help
  use <type> [<name>]    Switch to context (client, site, gateway)
                         Without name: list and select interactively
                         With name: fuzzy match and filter results
                         Auto-selects if only one match found
  get [options]          Get current context entity as JSON (default) or table
                         Options: -o/--output <json|table>, -f/--file <filename>
  back                   Exit current context
  context                Show current context
  clear                  Clear screen
  exit, quit             Exit REPL

Context Types:
  client [<name>]        Set client context (exclusive with gateway)
  site [<name>]          Set site context
  gateway [<name>]       Set gateway context (exclusive with client)
  volttron               Enter Volttron deployment context

Examples:
  use site               # List sites and select interactively
  use site demo-site     # Enter site context directly
  use site demo          # Fuzzy match sites containing "demo"
  use gateway west       # Filter gateways with "west" in name
  points list            # List points for current site
  back                   # Exit site context

All regular CLI commands work in REPL mode with automatic context injection.
"""

        # Add context-specific help
        if context.current_gateway:
            help_text += """

Gateway Context Commands:
  get                    Get current gateway details
  trigger-scan           Trigger BACnet scan on current gateway
  deploy-points          Deploy points to current gateway
  enable-bacnet          Enable BACnet on current gateway
  disable-bacnet         Disable BACnet on current gateway
  bacnet-status          Show BACnet configuration status

BACnet Examples:
  trigger-scan --scan-address 192.168.1.0/24
  bacnet-status -o json
  deploy-points
  
Note: You can also use the full 'gateways <command>' form if needed.
"""
        elif context.current_site:
            help_text += """

Site Context Commands:
  sites get              Get current site details
  points list            List points for current site
  timeseries             Export all timeseries data for current site
"""
        elif context.current_client:
            help_text += """

Client Context Commands:
  clients get            Get current client details
  sites list             List sites for current client
"""

        return help_text.strip()

    def _get_api_client(self) -> APIClient | None:
        """Get API client from context."""
        return self.click_ctx.obj.get("client")

    def _get_gateway_site(self, gateway_name: str) -> str | None:
        """Get the site associated with a gateway."""
        api_client = self._get_api_client()
        if not api_client:
            return None

        try:
            if gateway_name is not None:
                gateway = api_client.get_gateway(gateway_name)
            else:
                return None
            # Try both possible field names
            return gateway.get("site") or gateway.get("site_name")
        except Exception:
            # If we can't get the gateway info, return None
            return None

    def _get_gateway_client(self, gateway_name: str) -> str | None:
        """Get the client associated with a gateway."""
        api_client = self._get_api_client()
        if not api_client:
            return None

        try:
            if gateway_name is not None:
                gateway = api_client.get_gateway(gateway_name)
            else:
                return None
            # Try both possible field names
            return gateway.get("client") or gateway.get("client_name")
        except Exception:
            # If we can't get the gateway info, return None
            return None

    def _switch_to_context(self, context_type: ContextType, name: str, context: ReplContext) -> str:
        """Switch to a specific context after validation."""
        # Get API client
        api_client = self._get_api_client()
        if not api_client:
            return "Error: API client not configured. Please set ACEIOT_API_KEY."

        # Check for mutually exclusive contexts
        if context_type == ContextType.CLIENT and context.current_gateway:
            # Exit gateway context first
            context.reset_context()
            return "Exited gateway context. " + self._switch_to_context(
                context_type, name, context
            )
        if context_type == ContextType.GATEWAY and context.current_client:
            # Exit client context first
            context.reset_context()
            return "Exited client context. " + self._switch_to_context(
                context_type, name, context
            )

        # Validate resource exists
        try:
            if context_type == ContextType.CLIENT:
                if name is not None:
                    api_client.get_client(name)
                else:
                    return "Error: Client name cannot be None"
            elif context_type == ContextType.SITE:
                api_client.get_site(name)
            elif context_type == ContextType.GATEWAY:
                # For gateways, we need to list and check
                gateways = api_client.get_gateways()
                gateway_names = [g.get("name", "") for g in gateways.get("items", [])]
                if name not in gateway_names:
                    raise ValueError(f"Gateway '{name}' not found")
            elif context_type == ContextType.VOLTTRON:
                # Volttron context doesn't need validation, it's a mode
                if name and name != "volttron":
                    # Could be a package ID
                    context.enter_context(context_type, name, data={"package_id": name})
                    return f"Switched to volttron context with package: {name}"
                context.enter_context(context_type, "volttron")
                return "Switched to volttron deployment context"

            # If we get here, resource exists (except for volttron which is handled above)
            if context_type != ContextType.VOLTTRON:
                context.enter_context(context_type, name)
                return f"Switched to {context_type.value} context: {name}"
            
            # This should never happen as volttron is handled above
            return "Error: Unexpected context type"

        except Exception as e:
            return f"Error: Could not switch to {context_type.value} '{name}': {e}"

    def _interactive_context_selection(
        self, context_type: ContextType, context: ReplContext, filter_text: str | None = None
    ) -> str:
        """List resources and allow interactive selection with fuzzy matching."""
        # Get API client
        api_client = self._get_api_client()
        if not api_client:
            return "Error: API client not configured. Please set ACEIOT_API_KEY."

        try:
            # Get list of resources based on type
            if context_type == ContextType.CLIENT:
                result = api_client.get_clients(per_page=100)
                items = result.get("items", [])
                choices = [
                    (item.get("name", ""), item.get("nice_name", item.get("name", "")))
                    for item in items
                ]

            elif context_type == ContextType.SITE:
                # If in client context, filter by client
                params: dict[str, Any] = {"per_page": 100}
                if context.current_frame and context.current_frame.type == ContextType.CLIENT:
                    params["client_name"] = context.current_frame.name

                result = api_client.get_sites(**params)
                items = result.get("items", [])
                choices = [
                    (
                        item.get("name", ""),
                        f"{item.get('name', '')} ({item.get('client_name', '')})",
                    )
                    for item in items
                ]

            elif context_type == ContextType.GATEWAY:
                result = api_client.get_gateways(per_page=100)
                items = result.get("items", [])
                choices = [
                    (item.get("name", ""), f"{item.get('name', '')} ({item.get('site_name', '')})")
                    for item in items
                ]

            elif context_type == ContextType.VOLTTRON:
                # For volttron, just enter the context
                choices = [("volttron", "Volttron deployment context")]

            else:
                return f"Interactive selection not implemented for {context_type.value}"

            if not choices:
                return f"No {context_type.value}s found"

            # Apply fuzzy filter if provided
            if filter_text:
                filtered_choices = self._fuzzy_match(filter_text, choices)
                
                if not filtered_choices:
                    # No matches found - show suggestions
                    return f"No {context_type.value}s found matching '{filter_text}'. Use 'use {context_type.value}' without a filter to see all options."
                
                choices = filtered_choices
            
            # If only one choice after filtering, auto-select
            if len(choices) == 1:
                selected_name = choices[0][0]
                click.echo(
                    f"\nAuto-selecting the only {context_type.value} matching filter: {selected_name}"
                )
                return self._switch_to_context(context_type, selected_name, context)

            # Show table of options
            title = f"Available {context_type.value}s"
            if filter_text:
                title += f" (filtered by '{filter_text}')"
            table = Table(title=title)
            table.add_column("#", style="cyan", width=4)
            table.add_column("Name", style="green")
            table.add_column("Description", style="yellow")

            for i, (name, desc) in enumerate(choices, 1):
                table.add_row(str(i), name, desc)

            self.console.print(table)

            # If only one choice (shouldn't reach here due to auto-select above)
            if len(choices) == 1:
                selected_name = choices[0][0]
                click.echo(
                    f"\nAuto-selecting the only available {context_type.value}: {selected_name}"
                )
            else:
                # Ask for selection by number
                click.echo(
                    f"\nEnter number (1-{len(choices)}) or press Ctrl+C to cancel: ", nl=False
                )
                try:
                    selection = click.prompt("", type=int, default=0, show_default=False)
                    if 1 <= selection <= len(choices):
                        selected_name = choices[selection - 1][0]
                    else:
                        return (
                            f"Invalid selection. Please enter a number between 1 and {len(choices)}"
                        )
                except (click.Abort, KeyboardInterrupt):
                    return "\nSelection cancelled"

            # Switch to selected context
            return self._switch_to_context(context_type, selected_name, context)

        except Exception as e:
            return f"Error listing {context_type.value}s: {e}"

    def _execute_volttron_command(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute volttron-specific commands in REPL."""
        command = parsed_cmd.command_path[0]
        args = parsed_cmd.arguments

        # Get or create volttron handler
        if not self.volttron_handler:
            api_client = self._get_api_client()
            if not api_client:
                return "Error: API client not configured"
            self.volttron_handler = VolttronReplHandler(api_client, self.console)

        if command == "deploy":
            if not args:
                # Interactive deployment wizard
                return self.volttron_handler.handle_deploy_wizard(context)
            # Direct deployment with args - delegate to CLI command
            return self._execute_cli_command(parsed_cmd, context)

        if command == "upload":
            # In volttron context, upload means upload agent package
            if not args:
                if context.current_gateway or context.current_client:
                    return "Usage: upload <path> (client/gateway will be auto-detected)"
                return "Usage: upload <path> <name> (client or gateway name)"
            if len(args) == 1:
                if context.current_gateway:
                    # Auto-inject gateway if in gateway context
                    parsed_cmd.arguments.append(context.current_gateway)
                elif context.current_client:
                    # Auto-inject client if in client context
                    parsed_cmd.arguments.append(context.current_client)
            # Delegate to CLI volttron upload-agent
            parsed_cmd.command_path = ["volttron", "upload-agent"]
            return self._execute_cli_command(parsed_cmd, context)

        if command == "list":
            # List packages for a client
            if args and args[0] == "packages":
                if len(args) < 2:
                    # First check if we're in a client context
                    if context.current_client:
                        # Use the current client directly
                        parsed_cmd.command_path = ["volttron", "list-packages"]
                        parsed_cmd.arguments = [context.current_client]
                        return self._execute_cli_command(parsed_cmd, context)
                    # Otherwise check if we're in gateway context
                    if context.current_gateway:
                        # Use the gateway directly (command will resolve to client)
                        parsed_cmd.command_path = ["volttron", "list-packages"]
                        parsed_cmd.arguments = [context.current_gateway]
                        return self._execute_cli_command(parsed_cmd, context)
                    return "Usage: list packages <name> (client or gateway name, or use from context)"
                parsed_cmd.command_path = ["volttron", "list-packages"]
                parsed_cmd.arguments = args[1:]  # Pass client name
                return self._execute_cli_command(parsed_cmd, context)
            if context.current_client or context.current_gateway:
                return (
                    "Usage: list packages (client/gateway will be auto-detected from context)"
                )
            return "Usage: list packages <name> (client or gateway name)"

        if command == "status":
            # Get config package status
            if args:
                parsed_cmd.command_path = ["volttron", "get-config-package"]
                return self._execute_cli_command(parsed_cmd, context)
            if context.current_gateway:
                # Auto-inject gateway if in gateway context
                parsed_cmd.arguments = [context.current_gateway]
                parsed_cmd.command_path = ["volttron", "get-config-package"]
                return self._execute_cli_command(parsed_cmd, context)
            return "Usage: status <gateway> (or use from gateway context)"

        return f"Unknown volttron command: {command}"

    def _fuzzy_match(self, text: str, candidates: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """Perform fuzzy matching on candidates.
        
        Args:
            text: Search text
            candidates: List of (name, description) tuples
            
        Returns:
            Filtered and sorted list of candidates
        """
        if not text:
            return candidates
            
        text_lower = text.lower()
        scored_candidates = []
        
        for name, desc in candidates:
            name_lower = name.lower()
            desc_lower = desc.lower()
            
            # Calculate match score
            score = 0
            
            # Exact match gets highest score
            if text_lower == name_lower:
                score = 1000
            # Prefix match gets high score
            elif name_lower.startswith(text_lower):
                score = 800
            # Contains match
            elif text_lower in name_lower:
                score = 500
                # Bonus for word boundary match
                if f"-{text_lower}" in name_lower or f"_{text_lower}" in name_lower:
                    score += 100
            # Description contains match
            elif text_lower in desc_lower:
                score = 200
            # Partial token matching (e.g., "dem sit" matches "demo-site")
            else:
                tokens = text_lower.split()
                if all(any(token in part for part in name_lower.split("-")) for token in tokens):
                    score = 300
                elif all(token in name_lower for token in tokens):
                    score = 250
                    
            if score > 0:
                scored_candidates.append((score, name, desc))
        
        # Sort by score (descending) and then by name
        scored_candidates.sort(key=lambda x: (-x[0], x[1]))
        
        # Return candidates without scores
        return [(name, desc) for _, name, desc in scored_candidates]

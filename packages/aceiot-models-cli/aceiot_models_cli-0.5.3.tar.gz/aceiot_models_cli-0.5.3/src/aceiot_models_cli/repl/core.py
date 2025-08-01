"""Core REPL implementation for aceiot-models-cli."""

import sys
from pathlib import Path

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from .context import ReplContext
from .executor import ReplCommandExecutor
from .parser import ReplCommandParser


class AceIoTRepl:
    """Main REPL interface for aceiot-models-cli."""

    def __init__(self, ctx: click.Context) -> None:
        self.click_ctx = ctx
        self.context = ReplContext()
        self.parser = ReplCommandParser(self._get_root_group())
        self.executor = ReplCommandExecutor(self._get_root_group(), ctx)

        # Check if we're in an interactive terminal
        self.interactive = sys.stdin.isatty()

        if self.interactive:
            # Set up history file path
            history_path = Path.home() / ".aceiot-repl-history"

            # Set up prompt session for interactive use
            self.session = PromptSession(
                history=FileHistory(str(history_path)),
                complete_while_typing=False,  # Start simple, enhance later
            )
        else:
            self.session = None

    def start(self) -> None:
        """Start the REPL loop."""
        if not self.interactive:
            click.echo("REPL mode requires an interactive terminal")
            return

        click.echo("ACE IoT Models CLI - Interactive Mode")
        click.echo("Type 'help' for available commands or 'exit' to quit")
        click.echo()

        while True:
            try:
                # Build prompt
                prompt_text = self._build_prompt()

                # Get user input
                if self.session is None:
                    click.echo("REPL session not initialized")
                    return
                user_input = self.session.prompt(prompt_text)

                # Skip empty input
                if not user_input.strip():
                    continue

                # Parse and execute command
                try:
                    parsed_cmd = self.parser.parse(user_input, self.context)
                    result = self.executor.execute(parsed_cmd, self.context)

                    # Display result if not empty
                    if result and str(result).strip():
                        click.echo(result)

                except click.ClickException as e:
                    click.echo(f"Error: {e.format_message()}", err=True)
                except EOFError:
                    # Re-raise EOFError so outer handler can process it
                    raise
                except Exception as e:
                    click.echo(f"Unexpected error: {e}", err=True)

            except EOFError:
                # Handle exit command and Ctrl+D
                # Exit message already shown by exit command if used
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                click.echo("\nGoodbye!")
                break
            except Exception as e:
                click.echo(f"REPL error: {e}", err=True)

    def _build_prompt(self) -> str:
        """Build the prompt string with context indicators."""
        base = "aceiot"

        if not self.context.is_global:
            context_path = self.context.get_context_path()
            return f"{base}({context_path})> "

        return f"{base}> "

    def _get_root_group(self) -> click.Group:
        """Get the root CLI group."""
        # Navigate up to find the root group
        ctx = self.click_ctx
        while ctx.parent:
            ctx = ctx.parent
        command = ctx.command
        if not isinstance(command, click.Group):
            raise TypeError("Root command must be a click.Group")
        return command

"""Example: Client commands using new architecture."""


import click

from ...formatters import print_error
from ...repl.context import ContextType
from ..base import BaseCommand, ContextAwareCommand
from ..decorators import command, context_command
from ..utils import ErrorHandlerMixin, OutputFormatterMixin, PaginationMixin


@command(
    name="client-list",
    description="List all clients",
    aliases=["clients", "ls-clients"]
)
class ListClientsCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin, PaginationMixin):
    """List all clients with pagination support."""

    def get_click_command(self) -> click.Command:
        @click.command("list")
        @click.option("--page", default=1, help="Page number")
        @click.option("--per-page", default=10, help="Results per page")
        @click.pass_context
        def list_clients(ctx: click.Context, page: int, per_page: int) -> None:
            """List all clients."""
            try:
                client = self.require_api_client(ctx)
                result = client.get_clients(page=page, per_page=per_page)
                self.format_output(result, ctx, title="Clients")
            except Exception as e:
                self.handle_api_error(e, ctx)

        return list_clients


@command(
    name="client-get",
    description="Get client details",
    aliases=["get-client", "show-client"]
)
class GetClientCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Get details for a specific client."""

    def get_click_command(self) -> click.Command:
        @click.command("get")
        @click.argument("name")
        @click.pass_context
        def get_client(ctx: click.Context, name: str) -> None:
            """Get client details."""
            try:
                client = self.require_api_client(ctx)
                if name is not None:
                    result = client.get_client(name)
                else:
                    print_error("Client name cannot be None")
                    ctx.exit(1)
                self.format_output(result, ctx, title=f"Client: {name}")
            except Exception as e:
                self.handle_api_error(e, ctx)

        return get_client


@context_command(
    name="client-get-current",
    context_types=[ContextType.CLIENT],
    description="Get current client details",
    auto_inject={"name": "client_name"},
    aliases=["get"]
)
class GetCurrentClientCommand(ContextAwareCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Get details for the current client in context."""

    def get_click_command(self) -> click.Command:
        @click.command("get")
        @click.pass_context
        def get_current_client(ctx: click.Context) -> None:
            """Get current client details."""
            # Name will be auto-injected from context
            name = self.current_client
            if not name:
                print_error("No client context set. Use 'use client <name>' first.")
                ctx.exit(1)

            try:
                client = self.require_api_client(ctx)
                if name is not None:
                    result = client.get_client(name)
                else:
                    print_error("Client name cannot be None")
                    ctx.exit(1)
                self.format_output(result, ctx, title=f"Client: {name}")
            except Exception as e:
                self.handle_api_error(e, ctx)

        return get_current_client


@command(
    name="client-create",
    description="Create a new client"
)
class CreateClientCommand(BaseCommand, ErrorHandlerMixin):
    """Create a new client."""

    def get_click_command(self) -> click.Command:
        @click.command("create")
        @click.argument("name")
        @click.option("--nice-name", help="Display name for the client")
        @click.option("--bus-contact", help="Business contact")
        @click.option("--tech-contact", help="Technical contact")
        @click.option("--address", help="Client address")
        @click.option("--phone", help="Client phone number")
        @click.option("--metadata", help="JSON metadata for the client")
        @click.pass_context
        def create_client(
            ctx: click.Context,
            name: str,
            nice_name: str | None,
            bus_contact: str | None,
            tech_contact: str | None,
            address: str | None,
            phone: str | None,
            metadata: str | None
        ) -> None:
            """Create a new client."""
            try:
                import json

                from aceiot_models import ClientCreate

                client_data = ClientCreate(
                    name=name,
                    nice_name=nice_name or name,
                    bus_contact=bus_contact,
                    tech_contact=tech_contact,
                    address=address,
                )

                # Handle optional fields
                if phone:
                    client_data.phone = phone
                if metadata:
                    try:
                        client_data.metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        print_error("Invalid JSON in metadata")
                        ctx.exit(1)

                # Convert model to dict for API
                from aceiot_models.serializers import serialize_for_api

                client_dict = serialize_for_api(client_data)
                api_client = self.require_api_client(ctx)
                result = api_client.create_client(client_dict)

                from ...formatters import print_success
                print_success(f"Client '{name}' created successfully!")

                # Show created client
                self.format_output(result, ctx, title=f"Created Client: {name}")

            except Exception as e:
                self.handle_api_error(e, ctx)

        return create_client

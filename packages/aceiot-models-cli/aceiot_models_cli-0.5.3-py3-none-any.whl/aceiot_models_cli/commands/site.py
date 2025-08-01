"""Site commands using new architecture."""


import click

from ..formatters import print_error
from ..repl.context import ContextType
from .base import BaseCommand, ContextAwareCommand
from .decorators import command, context_command
from .utils import ErrorHandlerMixin, OutputFormatterMixin, PaginationMixin


@command(
    name="sites.list",
    description="List all sites",
    aliases=["ls-sites"]
)
class ListSitesCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin, PaginationMixin):
    """List all sites with optional filtering."""

    def get_click_command(self) -> click.Command:
        @click.command("list")
        @click.option("--page", default=1, help="Page number")
        @click.option("--per-page", default=10, help="Results per page")
        @click.option("--client-name", help="Filter by client name")
        @click.option("--show-archived", is_flag=True, help="Include archived sites")
        @click.pass_context
        def list_sites(
            ctx: click.Context,
            page: int,
            per_page: int,
            client_name: str | None,
            show_archived: bool,
        ) -> None:
            """List all sites."""
            try:
                client = self.require_api_client(ctx)

                # Build filter parameters
                params = {
                    "page": page,
                    "per_page": per_page,
                }
                if client_name:
                    params["client_name"] = client_name
                if show_archived:
                    params["show_archived"] = show_archived

                result = client.get_sites(**params)
                self.format_output(result, ctx, title="Sites")
            except Exception as e:
                self.handle_api_error(e, ctx, "list sites")

        return list_sites


@command(
    name="sites.get",
    description="Get site details"
)
class GetSiteCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Get details for a specific site."""

    def get_click_command(self) -> click.Command:
        @click.command("get")
        @click.argument("site_name")
        @click.pass_context
        def get_site(ctx: click.Context, site_name: str) -> None:
            """Get a specific site by name."""
            try:
                client = self.require_api_client(ctx)
                result = client.get_site(site_name)
                self.format_output(result, ctx, title=f"Site: {site_name}")
            except Exception as e:
                self.handle_api_error(e, ctx, "get site")

        return get_site


@context_command(
    name="get",
    context_types=[ContextType.SITE],
    description="Get current site details",
    auto_inject={"site_name": "site_name"}
)
class GetCurrentSiteCommand(ContextAwareCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Get details for the current site in context."""

    def get_click_command(self) -> click.Command:
        @click.command("get")
        @click.pass_context
        def get_current_site(ctx: click.Context) -> None:
            """Get current site details."""
            # Name will be auto-injected from context
            name = self.current_site
            if not name:
                print_error("No site context set. Use 'use site <name>' first.")
                ctx.exit(1)

            try:
                client = self.require_api_client(ctx)
                result = client.get_site(name)
                self.format_output(result, ctx, title=f"Site: {name}")
            except Exception as e:
                self.handle_api_error(e, ctx, "get site")

        return get_current_site


@context_command(
    name="sites.list",
    context_types=[ContextType.CLIENT],
    description="List sites for current client",
    auto_inject={"client_name": "client_name"}
)
class ListClientSitesCommand(ContextAwareCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """List sites filtered by current client context."""

    def get_click_command(self) -> click.Command:
        @click.command("list")
        @click.option("--page", default=1, help="Page number")
        @click.option("--per-page", default=10, help="Results per page")
        @click.option("--show-archived", is_flag=True, help="Include archived sites")
        @click.pass_context
        def list_client_sites(
            ctx: click.Context,
            page: int,
            per_page: int,
            show_archived: bool,
        ) -> None:
            """List sites for current client."""
            # Client name will be auto-injected from context
            client_name = self.current_client
            if not client_name:
                # Fallback to regular list command
                params = {
                    "page": page,
                    "per_page": per_page,
                }
            else:
                params = {
                    "page": page,
                    "per_page": per_page,
                    "client_name": client_name,
                }

            if show_archived:
                params["show_archived"] = show_archived

            try:
                client = self.require_api_client(ctx)
                result = client.get_sites(**params)

                title = f"Sites for Client: {client_name}" if client_name else "Sites"
                self.format_output(result, ctx, title=title)
            except Exception as e:
                self.handle_api_error(e, ctx, "list sites")

        return list_client_sites

"""Point commands using new architecture."""

from datetime import datetime, timezone

import click

from ..formatters import format_json, print_error
from ..repl.context import ContextType
from .base import BaseCommand, ContextAwareCommand
from .decorators import command, context_command
from .utils import ErrorHandlerMixin, OutputFormatterMixin, PaginationMixin


@command(
    name="points.list",
    description="List all points",
    aliases=["ls-points"]
)
class ListPointsCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin, PaginationMixin):
    """List all points with optional filtering."""

    def get_click_command(self) -> click.Command:
        @click.command("list")
        @click.option("--site", help="Filter by site name")
        @click.option("--page", default=1, help="Page number")
        @click.option("--per-page", default=10, help="Results per page")
        @click.pass_context
        def list_points(
            ctx: click.Context,
            site: str | None,
            page: int,
            per_page: int,
        ) -> None:
            """List all points."""
            try:
                client = self.require_api_client(ctx)

                # Build parameters
                params = {
                    "page": page,
                    "per_page": per_page,
                }
                if site:
                    params["site_name"] = site

                result = client.get_points(**params)
                self.format_output(result, ctx, title="Points")
            except Exception as e:
                self.handle_api_error(e, ctx)

        return list_points


@context_command(
    name="points.list",
    context_types=[ContextType.SITE, ContextType.GATEWAY],
    description="List points for current site/gateway",
    auto_inject={"site": "site_name"}
)
class ListContextPointsCommand(ContextAwareCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """List points filtered by current context."""

    def get_click_command(self) -> click.Command:
        @click.command("list")
        @click.option("--page", default=1, help="Page number")
        @click.option("--per-page", default=10, help="Results per page")
        @click.pass_context
        def list_context_points(
            ctx: click.Context,
            page: int,
            per_page: int,
        ) -> None:
            """List points for current context."""
            # Determine site from context
            site_name = None

            if self.current_site:
                site_name = self.current_site
            elif self.current_gateway and self.context:
                # Get gateway's site
                try:
                    client = self.require_api_client(ctx)
                    if self.current_gateway is not None:
                        gateway = client.get_gateway(self.current_gateway)
                    else:
                        gateway = None
                    site_name = gateway.get("site") or gateway.get("site_name")
                except Exception:
                    pass

            try:
                client = self.require_api_client(ctx)

                params = {
                    "page": page,
                    "per_page": per_page,
                }
                if site_name:
                    params["site_name"] = site_name

                result = client.get_points(**params)
                title = f"Points for Site: {site_name}" if site_name else "Points"
                self.format_output(result, ctx, title=title)
            except Exception as e:
                self.handle_api_error(e, ctx)

        return list_context_points


@command(
    name="points.get-timeseries",
    description="Get timeseries data for a point"
)
class GetTimeseriesCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Get timeseries data for a specific point."""

    def get_click_command(self) -> click.Command:
        @click.command("get-timeseries")
        @click.argument("point_id")
        @click.option("--start", help="Start time (ISO format)")
        @click.option("--end", help="End time (ISO format)")
        @click.option("--limit", type=int, default=100, help="Maximum number of samples")
        @click.pass_context
        def get_timeseries(
            ctx: click.Context,
            point_id: str,
            start: str | None,
            end: str | None,
            limit: int,
        ) -> None:
            """Get timeseries data for a point."""
            try:
                client = self.require_api_client(ctx)

                # Parse timestamps if provided
                start_ts = None
                end_ts = None

                if start:
                    try:
                        start_ts = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    except ValueError:
                        print_error(f"Invalid start time format: {start}")
                        ctx.exit(1)

                if end:
                    try:
                        end_ts = datetime.fromisoformat(end.replace("Z", "+00:00"))
                    except ValueError:
                        print_error(f"Invalid end time format: {end}")
                        ctx.exit(1)

                # Default to last 24 hours if no time range specified
                if not end_ts:
                    end_ts = datetime.now(timezone.utc)
                if not start_ts:
                    start_ts = end_ts.replace(hour=end_ts.hour - 24)

                # Get timeseries data
                result = client.get_point_timeseries(
                    point_id,
                    start=start_ts,
                    end=end_ts,
                    limit=limit,
                )

                if ctx.obj["output"] == "json":
                    click.echo(format_json(result))
                else:
                    # Format as table
                    items = result.get("items", [])
                    if not items:
                        click.echo("No timeseries data found for the specified time range.")
                        return

                    from rich.console import Console
                    from rich.table import Table

                    console = Console()
                    table = Table(title=f"Timeseries Data for Point {point_id}")
                    table.add_column("Timestamp", style="cyan")
                    table.add_column("Value", style="green")
                    table.add_column("Quality", style="yellow")

                    for item in items:
                        table.add_row(
                            item.get("timestamp", ""),
                            str(item.get("value", "")),
                            item.get("quality", ""),
                        )

                    console.print(table)

                    # Show summary
                    total = result.get("total", len(items))
                    if total > len(items):
                        console.print(f"\nShowing {len(items)} of {total} samples")

            except Exception as e:
                self.handle_api_error(e, ctx)

        return get_timeseries

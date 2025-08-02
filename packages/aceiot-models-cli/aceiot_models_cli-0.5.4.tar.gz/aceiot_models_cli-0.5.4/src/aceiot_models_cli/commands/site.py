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


@context_command(
    name="timeseries",
    context_types=[ContextType.SITE],
    description="Export all timeseries data for current site",
    auto_inject={"site_name": "site_name"}
)
class SiteTimeseriesCommand(ContextAwareCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Export all timeseries data for the current site in context."""

    def get_click_command(self) -> click.Command:
        @click.command("timeseries")
        @click.option("--start", help="Start time (ISO format, e.g., 2024-01-01T00:00:00Z)")
        @click.option("--end", help="End time (ISO format, e.g., 2024-01-02T00:00:00Z)")
        @click.option("--output-file", "-o", help="Output file path (defaults to <site>-<start>-<end>.csv)")
        @click.option(
            "--format",
            "-f",
            type=click.Choice(["csv", "parquet", "auto"]),
            default="auto",
            help="Output format (auto detects from file extension, defaults to csv)",
        )
        @click.option("--include-metadata", is_flag=True, help="Include point metadata in output")
        @click.pass_context
        def site_timeseries(
            ctx: click.Context,
            start: str | None,
            end: str | None,
            output_file: str | None,
            format: str,
            include_metadata: bool,
        ) -> None:
            """Export all timeseries data for current site to a file.

            This command fetches all points for the current site and their timeseries data
            within the specified time range, then exports to CSV or Parquet format.

            Examples:
                # Interactive mode (prompts for time range and format)
                timeseries
                
                # With specific time range
                timeseries --start 2024-01-01T00:00:00Z --end 2024-01-02T00:00:00Z
                
                # With custom output
                timeseries --start 2024-01-01T00:00:00Z --end 2024-01-02T00:00:00Z -o data.parquet
            """
            from datetime import datetime, timedelta, timezone
            from pathlib import Path
            import pandas as pd
            from rich.console import Console
            from rich.table import Table
            from rich.prompt import Prompt, IntPrompt

            # Get site name from context
            site_name = self.current_site
            if not site_name:
                print_error("No site context set. Use 'use site <name>' first.")
                ctx.exit(1)

            client = self.require_api_client(ctx)
            console = Console()

            # Interactive mode if no start/end provided
            if not start or not end:
                console.print("\n[bold cyan]📊 Timeseries Export - Interactive Mode[/bold cyan]\n")
                
                # Get current time in UTC
                now = datetime.now(timezone.utc)
                
                # Define time range options
                time_ranges = [
                    ("Last 15 minutes", now - timedelta(minutes=15), now),
                    ("Last hour", now - timedelta(hours=1), now),
                    ("Last 4 hours", now - timedelta(hours=4), now),
                    ("Last 24 hours", now - timedelta(days=1), now),
                    ("Today so far", now.replace(hour=0, minute=0, second=0, microsecond=0), now),
                    ("Yesterday", 
                     (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
                     now.replace(hour=0, minute=0, second=0, microsecond=0)),
                    ("Last 7 days", now - timedelta(days=7), now),
                    ("Last 30 days", now - timedelta(days=30), now),
                    ("Previous hour", now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1),
                     now.replace(minute=0, second=0, microsecond=0)),
                    ("Custom range", None, None),
                ]
                
                # Show time range options
                table = Table(title="Select Time Range")
                table.add_column("#", style="cyan", width=4)
                table.add_column("Time Range", style="green")
                table.add_column("Start", style="yellow")
                table.add_column("End", style="yellow")
                
                for i, (label, start_time, end_time) in enumerate(time_ranges, 1):
                    if start_time and end_time:
                        start_str = start_time.strftime("%Y-%m-%d %H:%M UTC")
                        end_str = end_time.strftime("%Y-%m-%d %H:%M UTC")
                    else:
                        start_str = "Custom"
                        end_str = "Custom"
                    table.add_row(str(i), label, start_str, end_str)
                
                console.print(table)
                
                # Get time range selection
                selection = IntPrompt.ask(
                    "\nEnter time range selection",
                    choices=[str(i) for i in range(1, len(time_ranges) + 1)],
                    default="1"
                )
                
                selected_idx = int(selection) - 1
                if selected_idx < len(time_ranges) - 1:
                    # Use predefined range
                    _, selected_start, selected_end = time_ranges[selected_idx]
                    start = selected_start.isoformat().replace("+00:00", "Z")
                    end = selected_end.isoformat().replace("+00:00", "Z")
                    console.print(f"\n[green]✓ Selected: {time_ranges[selected_idx][0]}[/green]")
                else:
                    # Custom range
                    console.print("\n[yellow]Enter custom time range (ISO format)[/yellow]")
                    start = Prompt.ask("Start time", default=(now - timedelta(hours=1)).isoformat().replace("+00:00", "Z"))
                    end = Prompt.ask("End time", default=now.isoformat().replace("+00:00", "Z"))
                
                # Get format preference if not specified
                if format == "auto" and not output_file:
                    console.print("\n[bold cyan]Select Output Format[/bold cyan]")
                    format_table = Table()
                    format_table.add_column("#", style="cyan", width=4)
                    format_table.add_column("Format", style="green")
                    format_table.add_column("Description", style="yellow")
                    
                    format_table.add_row("1", "CSV", "Comma-separated values (compatible with Excel)")
                    format_table.add_row("2", "Parquet", "Columnar format (efficient for large datasets)")
                    
                    console.print(format_table)
                    
                    format_selection = IntPrompt.ask(
                        "\nEnter format selection",
                        choices=["1", "2"],
                        default="1"
                    )
                    
                    format = "csv" if format_selection == "1" else "parquet"
                    console.print(f"\n[green]✓ Selected format: {format.upper()}[/green]")
                
                # Ask about metadata inclusion if not specified via CLI
                if not include_metadata:  # Only ask if not already set to True
                    include_metadata_prompt = Prompt.ask(
                        "\nInclude point metadata (display name, unit, etc.)?",
                        choices=["y", "n"],
                        default="n"
                    )
                    include_metadata = include_metadata_prompt.lower() == "y"
                    
                console.print("\n[blue]Starting export...[/blue]\n")

            # Determine output format first (before generating filename)
            if not output_file:
                # Need to determine format before creating default filename
                if format == "auto":
                    format = "csv"  # Default to CSV when no file specified

                # Clean up timestamps for filename (remove colons and timezone indicators)
                start_clean = start.replace(":", "-").replace("Z", "").replace("+", "_")
                end_clean = end.replace(":", "-").replace("Z", "").replace("+", "_")

                # Use appropriate extension based on format
                extension = ".parquet" if format == "parquet" else ".csv"
                output_file = f"{site_name}-{start_clean}-{end_clean}{extension}"
                console.print(f"[yellow]Using default output file: {output_file}[/yellow]")

            # Now handle the case where output_file was provided
            output_path = Path(output_file)
            if format == "auto" and output_file:  # Only auto-detect if file was provided
                if output_path.suffix.lower() == ".csv":
                    format = "csv"
                elif output_path.suffix.lower() in [".parquet", ".pq"]:
                    format = "parquet"
                else:
                    # Default to CSV if no extension or unrecognized extension
                    format = "csv"
                    # Add .csv extension if missing
                    if not output_path.suffix:
                        output_path = output_path.with_suffix(".csv")
                        output_file = str(output_path)

            try:
                # Parse timestamps
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))

                # Try to use the site timeseries endpoint first
                console.print(f"[blue]Fetching timeseries data for site '{site_name}'...[/blue]")
                try:
                    # Use the direct site timeseries endpoint
                    result = client.get_site_timeseries(site_name, start, end)
                    
                    # Handle the actual API response format
                    if "point_samples" in result:
                        # This is the expected format from get_site_timeseries
                        all_samples = result["point_samples"]
                        
                        # Convert to our expected format
                        all_data = []
                        for sample in all_samples:
                            all_data.append({
                                "point_name": sample.get("name", ""),
                                "timestamp": sample.get("ts", sample.get("timestamp", "")),
                                "value": sample.get("value")
                            })
                    elif "data" in result:
                        # Alternative format
                        all_data = result["data"]
                    elif isinstance(result, list):
                        # If the result is directly a list
                        all_data = result
                    else:
                        # Log what we got for debugging
                        console.print(f"[red]Unexpected response format from site timeseries endpoint: {list(result.keys()) if isinstance(result, dict) else type(result)}[/red]")
                        # Don't fallback - just exit with error
                        console.print("[red]The site timeseries endpoint returned an unexpected format.[/red]")
                        return
                        
                    # Convert to our expected format if needed
                    if all_data and isinstance(all_data, list):
                        # Check if we need to flatten the data structure
                        if len(all_data) > 0 and "point_name" not in all_data[0]:
                            # Need to restructure the data
                            restructured_data = []
                            for item in all_data:
                                if isinstance(item, dict):
                                    point_name = item.get("point", item.get("point_name", ""))
                                    values = item.get("values", item.get("data", []))
                                    if isinstance(values, list):
                                        for value in values:
                                            restructured_data.append({
                                                "point_name": point_name,
                                                "timestamp": value.get("timestamp", value.get("time", "")),
                                                "value": value.get("value")
                                            })
                                    else:
                                        # Single value format
                                        restructured_data.append({
                                            "point_name": point_name,
                                            "timestamp": item.get("timestamp", ""),
                                            "value": item.get("value")
                                        })
                            all_data = restructured_data
                            
                        if include_metadata and all_data:
                            # Need to fetch point details for metadata
                            console.print(f"[blue]Fetching point metadata...[/blue]")
                            points_result = client.get_site_points(site_name, per_page=1000)
                            points = points_result.get("items", [])
                            
                            # Create a lookup map
                            point_map = {p["name"]: p for p in points}
                            
                            # Add metadata to each data point
                            for row in all_data:
                                point_name = row.get("point_name", "")
                                if point_name in point_map:
                                    point = point_map[point_name]
                                    row.update({
                                        "point_display_name": point.get("display_name", ""),
                                        "point_description": point.get("description", ""),
                                        "point_unit": point.get("unit", ""),
                                        "point_type": point.get("type", ""),
                                        "point_equipment": point.get("equipment", ""),
                                    })
                                    
                except Exception as e:
                    # Don't fallback to individual queries - just report the error
                    console.print(f"[red]Error: Failed to fetch site timeseries data: {str(e)}[/red]")
                    console.print(f"[yellow]Please ensure the site name and time range are correct.[/yellow]")
                    return

                if not all_data:
                    console.print("[yellow]No timeseries data found for the specified time range.[/yellow]")
                    return

                console.print(f"[green]Collected {len(all_data)} data points[/green]")

                # Create DataFrame
                df = pd.DataFrame(all_data)
                
                # Convert timestamp to datetime
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                
                # Sort by point name and timestamp
                df = df.sort_values(["point_name", "timestamp"])

                # Save to file
                console.print(f"[blue]Saving to {output_file} ({format} format)...[/blue]")
                
                if format == "csv":
                    df.to_csv(output_file, index=False)
                else:  # parquet
                    df.to_parquet(output_file, index=False)
                
                console.print(f"[green]✓ Successfully exported {len(all_data)} timeseries records to {output_file}[/green]")
                console.print(f"[blue]Time range: {start_dt} to {end_dt}[/blue]")
                console.print(f"[blue]Points included: {df['point_name'].nunique()}[/blue]")
                
            except Exception as e:
                self.handle_api_error(e, ctx, "export site timeseries")

        return site_timeseries

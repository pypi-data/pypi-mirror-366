"""Main CLI entry point for aceiot-models-cli."""

from typing import Any

import click
from aceiot_models import (
    ClientCreate,
)
from aceiot_models.api import APIClient
from click import Context
from rich.console import Console

from .config import load_config
from .formatters import format_json, format_table, print_error, print_success
from .volttron_commands import volttron

# Import command bridge for dynamic loading
try:
    from .commands.bridge_v2 import integrate_new_commands
    USE_NEW_COMMANDS = True
except ImportError:
    USE_NEW_COMMANDS = False


def require_api_client(ctx: Context) -> APIClient:
    """Ensure API client is available, exit if not."""
    if "client" not in ctx.obj or ctx.obj["client"] is None:
        print_error("API key is required. Set ACEIOT_API_KEY or use --api-key")
        ctx.exit(1)
    return ctx.obj["client"]


# Create main CLI group
@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=False),
    default=None,
    help="Path to configuration file",
)
@click.option(
    "--api-url",
    envvar="ACEIOT_API_URL",
    default="https://flightdeck.aceiot.cloud/api",
    help="API base URL",
)
@click.option(
    "--api-key",
    envvar="ACEIOT_API_KEY",
    help="API key for authentication",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def cli(
    ctx: Context,
    config: str | None,
    api_url: str,
    api_key: str | None,
    output: str,
) -> None:
    """ACE IoT Models CLI - Interact with the ACE IoT API."""
    # Load configuration
    cfg = load_config(config)

    # Override with command line options
    if api_url:
        cfg.api_url = api_url
    if api_key:
        cfg.api_key = api_key

    # Store config in context for subcommands
    ctx.obj = {
        "config": cfg,
        "output": output,
        "client": None,  # Will be set below if API key is available
    }

    # Only create API client if we have an API key
    # Some commands (like init, test-serializers) don't need it
    if cfg.api_key:
        ctx.obj["client"] = APIClient(cfg.api_url, cfg.api_key)


# Client commands group
@cli.group()
@click.pass_context
def clients(ctx: Context) -> None:
    """Manage clients."""


@clients.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=10, help="Results per page")
@click.pass_context
def list_clients(ctx: Context, page: int, per_page: int) -> None:
    """List all clients."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_clients(page=page, per_page=per_page)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as table
            headers = ["ID", "Name", "Nice Name", "Business Contact", "Tech Contact"]
            rows = []
            for item in result.get("items", []):
                rows.append(
                    [
                        item.get("id", ""),
                        item.get("name", ""),
                        item.get("nice_name", ""),
                        item.get("bus_contact", ""),
                        item.get("tech_contact", ""),
                    ]
                )
            click.echo(format_table(headers, rows))
            click.echo(
                f"\nPage {result.get('page')} of {result.get('pages')} (Total: {result.get('total')})"
            )
    except Exception as e:
        print_error(f"Failed to list clients: {e}")
        ctx.exit(1)


@clients.command("get")
@click.argument("client_name")
@click.pass_context
def get_client(ctx: Context, client_name: str) -> None:
    """Get a specific client by name."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        if client_name is not None:
            result = client.get_client(client_name)
        else:
            click.echo("Error: Client name cannot be None")
            ctx.exit(1)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as key-value pairs
            click.echo(f"Client: {result.get('name')}")
            click.echo(f"Nice Name: {result.get('nice_name')}")
            click.echo(f"ID: {result.get('id')}")
            click.echo(f"Business Contact: {result.get('bus_contact')}")
            click.echo(f"Tech Contact: {result.get('tech_contact')}")
            click.echo(f"Address: {result.get('address')}")
    except Exception as e:
        print_error(f"Failed to get client: {e}")
        ctx.exit(1)


@clients.command("create")
@click.option("--name", required=True, help="Client name")
@click.option("--nice-name", help="Nice name for display")
@click.option("--bus-contact", help="Business contact")
@click.option("--tech-contact", help="Technical contact")
@click.option("--address", help="Client address")
@click.pass_context
def create_client(
    ctx: Context,
    name: str,
    nice_name: str | None,
    bus_contact: str | None,
    tech_contact: str | None,
    address: str | None,
) -> None:
    """Create a new client."""
    client = require_api_client(ctx)

    try:
        # Create client model
        client_data = ClientCreate(
            name=name,
            nice_name=nice_name or name,
            bus_contact=bus_contact,
            tech_contact=tech_contact,
            address=address,
        )

        # Convert model to dict for API
        from aceiot_models.serializers import serialize_for_api

        client_dict = serialize_for_api(client_data)
        result = client.create_client(client_dict)
        print_success(f"Client '{name}' created successfully")

        if ctx.obj["output"] == "json":
            click.echo(format_json(result))
    except Exception as e:
        print_error(f"Failed to create client: {e}")
        ctx.exit(1)


# Sites commands group
@cli.group()
@click.pass_context
def sites(ctx: Context) -> None:
    """Manage sites."""


@sites.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=10, help="Results per page")
@click.option("--client-name", help="Filter by client name")
@click.option("--collect-enabled", is_flag=True, help="Only show sites with collect enabled points")
@click.option("--show-archived", is_flag=True, help="Include archived sites")
@click.pass_context
def list_sites(
    ctx: Context,
    page: int,
    per_page: int,
    client_name: str | None,
    collect_enabled: bool,
    show_archived: bool,
) -> None:
    """List all sites."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        # Handle client_name filtering differently
        if client_name:
            # Use get_client_sites for specific client
            result = client.get_client_sites(client_name=client_name, page=page, per_page=per_page)
        else:
            # Get all sites
            result = client.get_sites(
                page=page,
                per_page=per_page,
                collect_enabled=collect_enabled,
                show_archived=show_archived,
            )

        # Check if result is None
        if result is None:
            print_error("API returned no data. Check your API key and connection.")
            ctx.exit(1)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as table
            headers = ["ID", "Name", "Client", "Nice Name", "Address", "Archived"]
            rows = []
            items = result.get("items", [])

            if not items:
                click.echo("No sites found.")
                return

            for item in items:
                address = item.get("address", "")
                # Handle None address gracefully
                address = str(address)[:50] if address is not None else ""

                rows.append(
                    [
                        item.get("id", ""),
                        item.get("name", ""),
                        item.get("client", ""),
                        item.get("nice_name", ""),
                        address,
                        "Yes" if item.get("archived") else "No",
                    ]
                )

            click.echo(format_table(headers, rows))

            # Add pagination info with safe defaults
            page_info = result.get("page", 1)
            pages_info = result.get("pages", 1)
            total_info = result.get("total", len(rows))
            click.echo(f"\nPage {page_info} of {pages_info} (Total: {total_info})")

    except Exception as e:
        print_error(f"Failed to list sites: {e}")
        ctx.exit(1)


@sites.command("get")
@click.argument("site_name")
@click.pass_context
def get_site(ctx: Context, site_name: str) -> None:
    """Get a specific site by name."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_site(site_name)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as key-value pairs
            click.echo(f"Site: {result.get('name')}")
            click.echo(f"Nice Name: {result.get('nice_name')}")
            click.echo(f"ID: {result.get('id')}")
            click.echo(f"Client: {result.get('client')}")
            click.echo(f"Address: {result.get('address')}")
            click.echo(f"Latitude: {result.get('latitude')}")
            click.echo(f"Longitude: {result.get('longitude')}")
            if result.get("timezone"):
                click.echo(f"Timezone: {result.get('timezone')}")
            click.echo(f"Archived: {'Yes' if result.get('archived') else 'No'}")
    except Exception as e:
        print_error(f"Failed to get site: {e}")
        ctx.exit(1)


@sites.command("timeseries")
@click.argument("site_name")
@click.option("--start", required=True, help="Start time (ISO format, e.g., 2024-01-01T00:00:00Z)")
@click.option("--end", required=True, help="End time (ISO format, e.g., 2024-01-02T00:00:00Z)")
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
    ctx: Context,
    site_name: str,
    start: str,
    end: str,
    output_file: str | None,
    format: str,
    include_metadata: bool,
) -> None:
    """Export all timeseries data for a site to a file.

    This command fetches all points for a site and their timeseries data
    within the specified time range, then exports to CSV or Parquet format.

    If no output file is specified, it defaults to:
    <site>-<start>-<end>.<format> in the current directory.

    Examples:
        # Use default CSV format (my-site-2024-01-01T00-00-00-2024-01-02T00-00-00.csv)
        aceiot-models-cli sites timeseries my-site \\
            --start 2024-01-01T00:00:00Z \\
            --end 2024-01-02T00:00:00Z

        # Use default filename with Parquet format (my-site-2024-01-01T00-00-00-2024-01-02T00-00-00.parquet)
        aceiot-models-cli sites timeseries my-site \\
            --start 2024-01-01T00:00:00Z \\
            --end 2024-01-02T00:00:00Z \\
            --format parquet

        # Specify custom output file
        aceiot-models-cli sites timeseries my-site \\
            --start 2024-01-01T00:00:00Z \\
            --end 2024-01-02T00:00:00Z \\
            --output-file site-data.parquet
    """
    from datetime import datetime
    from pathlib import Path

    import pandas as pd

    client = require_api_client(ctx)
    console = Console()

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

    # Ensure output_path is always a Path object
    output_path = Path(output_file)

    try:
        # Validate time format
        try:
            datetime.fromisoformat(start.replace("Z", "+00:00"))
            datetime.fromisoformat(end.replace("Z", "+00:00"))
        except ValueError as e:
            print_error(f"Invalid time format: {e}")
            print_error("Use ISO format, e.g., 2024-01-01T00:00:00Z")
            ctx.exit(1)

        # Fetch timeseries data directly using site endpoint
        console.print(
            f"[cyan]Fetching timeseries data for site '{site_name}' from {start} to {end}...[/cyan]"
        )

        with console.status("Loading data...", spinner="dots"):
            response = client.get_site_timeseries(site_name, start, end)
            all_samples = response.get("point_samples", [])

        if not all_samples:
            print_error("No timeseries data found for the specified time range")
            ctx.exit(1)

        # Get unique points from the data
        unique_points = {sample.get("name") for sample in all_samples if sample.get("name")}
        console.print(
            f"[green]✓ Fetched {len(all_samples)} data samples from {len(unique_points)} points[/green]"
        )

        # If metadata is requested, fetch point details
        point_metadata = {}
        if include_metadata and unique_points:
            console.print("[cyan]Fetching point metadata...[/cyan]")

            # Get site points to extract metadata
            all_points = []
            page = 1
            with console.status("Loading point details...", spinner="dots"):
                while True:
                    result = client.get_site_points(site_name, page=page, per_page=500)
                    items = result.get("items", [])
                    all_points.extend(items)

                    if page >= result.get("pages", 1):
                        break
                    page += 1

            # Build metadata map
            for point in all_points:
                if point.get("name") in unique_points:
                    point_metadata[point["name"]] = {
                        "id": point.get("id"),
                        "site": point.get("site"),
                        "point_type": point.get("point_type"),
                        "unit": point.get("unit"),
                        "description": point.get("description"),
                    }

        # Step 3: Convert to DataFrame
        console.print("\n[cyan]Processing data...[/cyan]")

        # Create DataFrame from samples
        df_data = []
        for sample in all_samples:
            row = {
                "timestamp": sample.get("time"),
                "point_name": sample.get("name"),
                "value": sample.get("value"),
            }

            # Add metadata if requested
            if include_metadata and sample.get("name") in point_metadata:
                metadata = point_metadata[sample.get("name")]
                row.update(
                    {
                        "point_id": metadata["id"],
                        "site": metadata["site"],
                        "point_type": metadata["point_type"],
                        "unit": metadata["unit"],
                        "description": metadata["description"],
                    }
                )

            df_data.append(row)

        df = pd.DataFrame(df_data)

        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Sort by timestamp and point name
        df = df.sort_values(["timestamp", "point_name"])

        # Step 4: Save to file
        console.print(f"\n[cyan]Saving to {output_file} as {format.upper()}...[/cyan]")

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "csv":
            df.to_csv(output_path, index=False)
        else:  # parquet
            df.to_parquet(output_path, index=False, engine="pyarrow")

        # Summary
        console.print(
            f"\n[green]✓ Successfully exported {len(df)} rows to {output_path.name}[/green]"
        )
        console.print(f"  Full path: {output_path.absolute()}")
        console.print(f"  Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        console.print(f"  Unique points: {df['point_name'].nunique()}")
        console.print(f"  File size: {output_path.stat().st_size:,} bytes")

    except Exception as e:
        print_error(f"Failed to export timeseries data: {e}")
        ctx.exit(1)


# Gateways commands group
@cli.group()
@click.pass_context
def gateways(ctx: Context) -> None:
    """Manage gateways."""


@gateways.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=10, help="Results per page")
@click.option("--show-archived", is_flag=True, help="Include archived gateways")
@click.pass_context
def list_gateways(ctx: Context, page: int, per_page: int, show_archived: bool) -> None:
    """List all gateways."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_gateways(page=page, per_page=per_page, show_archived=show_archived)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as table
            headers = ["Name", "Site", "Client", "VPN IP", "Archived", "Updated"]
            rows = []
            for item in result.get("items", []):
                rows.append(
                    [
                        item.get("name", ""),
                        item.get("site", ""),
                        item.get("client", ""),
                        item.get("vpn_ip", ""),
                        "Yes" if item.get("archived") else "No",
                        item.get("updated", "")[:19],  # Truncate timestamp
                    ]
                )
            click.echo(format_table(headers, rows))
            click.echo(
                f"\nPage {result.get('page')} of {result.get('pages')} (Total: {result.get('total')})"
            )
    except Exception as e:
        print_error(f"Failed to list gateways: {e}")
        ctx.exit(1)


@gateways.command("get")
@click.argument("gateway_name")
@click.pass_context
def get_gateway(ctx: Context, gateway_name: str) -> None:
    """Get a specific gateway by name."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        if gateway_name is not None:
            result = client.get_gateway(gateway_name)
        else:
            click.echo("Error: Gateway name cannot be None")
            ctx.exit(1)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as key-value pairs
            click.echo(f"Gateway: {result.get('name')}")
            click.echo(f"Nice Name: {result.get('nice_name')}")
            click.echo(f"ID: {result.get('id')}")
            click.echo(f"Client: {result.get('client')}")
            click.echo(f"Site: {result.get('site')}")
            click.echo(f"VPN IP: {result.get('vpn_ip')}")
            click.echo(f"Archived: {'Yes' if result.get('archived') else 'No'}")
            click.echo(f"Updated: {result.get('updated', '')[:19]}")  # Truncate timestamp

    except Exception as e:
        print_error(f"Failed to get gateway: {e}")
        ctx.exit(1)


# Add BACnet commands to gateways group
from .bacnet_commands import (
    bacnet_status,
    deploy_points,
    disable_bacnet,
    enable_bacnet,
    trigger_bacnet_scan,
)

gateways.add_command(trigger_bacnet_scan)
gateways.add_command(deploy_points)
gateways.add_command(enable_bacnet)
gateways.add_command(disable_bacnet)
gateways.add_command(bacnet_status)


# Points commands group
@cli.group()
@click.pass_context
def points(ctx: Context) -> None:
    """Manage points."""


@points.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=10, help="Results per page")
@click.option("--site", help="Filter by site name")
@click.pass_context
def list_points(ctx: Context, page: int, per_page: int, site: str | None) -> None:
    """List all points."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        if site:
            result = client.get_site_points(site, page=page, per_page=per_page)
        else:
            result = client.get_points(page=page, per_page=per_page)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as table
            headers = ["ID", "Name", "Site", "Type", "Collect", "Interval", "Updated"]
            rows = []
            for item in result.get("items", []):
                rows.append(
                    [
                        item.get("id", ""),
                        item.get("name", "")[:40],  # Truncate long names
                        item.get("site", ""),
                        item.get("point_type", ""),
                        "Yes" if item.get("collect_enabled") else "No",
                        str(item.get("collect_interval", "")),
                        item.get("updated", "")[:10],  # Just date
                    ]
                )
            click.echo(format_table(headers, rows))
            click.echo(
                f"\nPage {result.get('page')} of {result.get('pages')} (Total: {result.get('total')})"
            )
    except Exception as e:
        print_error(f"Failed to list points: {e}")
        ctx.exit(1)


@points.command("timeseries")
@click.argument("point_name")
@click.option("--start", required=True, help="Start time (ISO format)")
@click.option("--end", required=True, help="End time (ISO format)")
@click.pass_context
def get_timeseries(ctx: Context, point_name: str, start: str, end: str) -> None:
    """Get timeseries data for a point."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_point_timeseries(point_name, start, end)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as table
            samples = result.get("point_samples", [])
            if samples:
                headers = ["Time", "Value", "Point"]
                rows = []
                for sample in samples:
                    rows.append(
                        [
                            sample.get("time", ""),
                            sample.get("value", ""),
                            sample.get("name", ""),
                        ]
                    )
                click.echo(format_table(headers, rows))
                click.echo(f"\nTotal samples: {len(samples)}")
            else:
                click.echo("No data found for the specified time range")
    except Exception as e:
        print_error(f"Failed to get timeseries data: {e}")
        ctx.exit(1)


@points.command("discovered")
@click.argument("site_name")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=100, help="Results per page")
@click.pass_context
def list_discovered_points(ctx: Context, site_name: str, page: int, per_page: int) -> None:
    """List discovered BACnet points for a site."""
    from aceiot_models import Point

    from .utils import convert_api_response_to_points

    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        # Use get_site_points as discovered points
        result = client.get_site_points(site_name, page=page, per_page=per_page)

        # Convert to Point objects for better handling
        points = convert_api_response_to_points(result)

        if output_format == "json":
            # Convert Point objects back to dicts for JSON output
            json_result = result.copy()  # Keep original structure
            json_result["items"] = [
                point.model_dump() if isinstance(point, Point) else point for point in points
            ]
            click.echo(format_json(json_result))
        else:
            # Format as table
            headers = ["Name", "Type", "Device", "Object Type", "Object Name", "Present Value"]
            rows = []

            for point in points:
                if isinstance(point, Point) and point.bacnet_data:
                    bacnet = point.bacnet_data
                    device_name = bacnet.device_name or "Unknown"
                    device_id = bacnet.device_id or ""
                    rows.append(
                        [
                            point.name or "",
                            point.point_type or "",
                            f"{device_name} ({device_id})",
                            bacnet.object_type or "",
                            bacnet.object_name or "",
                            bacnet.present_value or "",
                        ]
                    )
                elif isinstance(point, Point):
                    rows.append(
                        [
                            point.name or "",
                            point.point_type or "",
                            "-",
                            "-",
                            "-",
                            "-",
                        ]
                    )
                else:
                    # Fallback for raw dict (if Point creation failed)
                    if point.get("bacnet_data"):
                        bacnet = point["bacnet_data"]
                        rows.append(
                            [
                                point.get("name", ""),
                                point.get("point_type", ""),
                                f"{bacnet.get('device_name', 'Unknown')} ({bacnet.get('device_id', '')})",
                                bacnet.get("object_type", ""),
                                bacnet.get("object_name", ""),
                                bacnet.get("present_value", ""),
                            ]
                        )
                    else:
                        rows.append(
                            [
                                point.get("name", ""),
                                point.get("point_type", ""),
                                "-",
                                "-",
                                "-",
                                "-",
                            ]
                        )

            if rows:
                click.echo(format_table(headers, rows))

                # Add pagination info
                total_pages = result.get("pages", 1)
                total_items = result.get("total", len(rows))
                click.echo(
                    f"\nPage {result.get('page', 1)} of {total_pages} (Total points: {total_items})"
                )
            else:
                click.echo("No discovered points found")
    except Exception as e:
        print_error(f"Failed to get discovered points: {e}")
        ctx.exit(1)


@points.command("batch-timeseries")
@click.option(
    "--points-file",
    "-f",
    type=click.File("r"),
    required=True,
    help="File containing point names (one per line)",
)
@click.option("--start", "-s", required=True, help="Start time (ISO format)")
@click.option("--end", "-e", required=True, help="End time (ISO format)")
@click.option("--batch-size", default=100, help="Points per batch")
@click.pass_context
def batch_timeseries(ctx: Context, points_file, start: str, end: str, batch_size: int) -> None:
    """Get timeseries data for multiple points with automatic batching."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        # Read point names from file
        point_names = [line.strip() for line in points_file if line.strip()]

        if not point_names:
            click.echo("No point names found in file")
            return

        click.echo(f"Processing {len(point_names)} points in batches of {batch_size}...")

        # Get data with batching using batch_process utility
        from aceiot_models.api import batch_process

        all_samples = []

        def process_batch(batch: list[str]) -> None:
            response = client.get_points_timeseries(batch, start, end)
            all_samples.extend(response.get("point_samples", []))

        # Process in batches
        batch_process(point_names, process_batch, batch_size=batch_size)

        result = {"point_samples": all_samples}

        samples = result.get("point_samples", [])

        if output_format == "json":
            click.echo(format_json(result))
        else:
            if samples:
                # Group by point name for summary
                points_data = {}
                for sample in samples:
                    point_name = sample.get("name", "Unknown")
                    if point_name not in points_data:
                        points_data[point_name] = []
                    points_data[point_name].append(sample)

                # Display summary
                headers = ["Point Name", "Sample Count", "First Time", "Last Time"]
                rows = []

                for point_name, point_samples in points_data.items():
                    sorted_samples = sorted(point_samples, key=lambda x: x.get("time", ""))
                    rows.append(
                        [
                            point_name,
                            len(point_samples),
                            sorted_samples[0].get("time", "") if sorted_samples else "-",
                            sorted_samples[-1].get("time", "") if sorted_samples else "-",
                        ]
                    )

                click.echo(format_table(headers, rows))
                click.echo(f"\nTotal samples: {len(samples)} from {len(points_data)} points")
            else:
                click.echo("No data found for the specified time range")
    except Exception as e:
        print_error(f"Failed to get batch timeseries data: {e}")
        ctx.exit(1)


# Init command
@cli.command("init")
@click.option("--api-key", help="API key for authentication")
@click.option("--api-url", help="API base URL")
def init(api_key: str | None, api_url: str | None) -> None:
    """Initialize configuration file."""
    from .config import init_config

    try:
        init_config(api_key=api_key, api_url=api_url)
        print_success("Configuration initialized successfully")
    except Exception as e:
        print_error(f"Failed to initialize configuration: {e}")
        raise click.Abort() from e


# Test serializers command
@cli.command("test-serializers")
def test_serializers() -> None:
    """Test all serializers in the aceiot-models package."""
    try:
        # Try importing from installed tests module
        from aceiot_models_cli.tests.test_serializers_core import run_all_serializer_tests
    except ImportError:
        # Fallback to adding project root to path
        import sys
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        from tests.test_serializers_core import run_all_serializer_tests

    click.echo("Running serializer tests...")
    try:
        results = run_all_serializer_tests()

        # Display results
        total_tests = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total_tests - passed

        click.echo(f"\n{'=' * 60}")
        click.echo("SERIALIZER TEST RESULTS")
        click.echo(f"{'=' * 60}")

        for result in results:
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            click.echo(f"{status} | {result['test_name']}")
            if not result["passed"]:
                click.echo(f"       Error: {result['error']}")

        click.echo(f"{'=' * 60}")
        click.echo(f"Total: {total_tests} | Passed: {passed} | Failed: {failed}")

        if failed > 0:
            import sys

            sys.exit(1)
        else:
            print_success("All serializer tests passed!")
    except Exception as e:
        print_error(f"Failed to run serializer tests: {e}")
        import sys

        sys.exit(1)


# REPL command
@cli.command("repl")
@click.pass_context
def repl_mode(ctx: Context) -> None:
    """Start interactive REPL mode."""
    from .repl.core_new import AceIoTRepl

    repl = AceIoTRepl(ctx)
    repl.start()


# Add the volttron command group to the CLI
cli.add_command(volttron)

# Integrate new command architecture if available
if USE_NEW_COMMANDS:
    integrate_new_commands(cli)


# Entry point
def main() -> None:
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()

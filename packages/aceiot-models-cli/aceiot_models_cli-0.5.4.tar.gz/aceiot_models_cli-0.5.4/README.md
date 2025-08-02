# ACE IoT Models CLI

A command-line interface for interacting with the ACE IoT API using the `aceiot-models` package. This CLI provides comprehensive access to ACE IoT's fleet management capabilities for IoT devices, sites, and data points.

## Requirements

- Python 3.10 or higher
- An ACE IoT API key

## Features

- Complete CLI for ACE IoT API operations
- Support for managing Clients, Sites, Gateways, Points, DER Events, and more
- **Volttron Agent Deployment**: Complete workflow for deploying agents to IoT gateways
- **Interactive REPL Mode**: Context-aware interactive shell with command completion
- **BACnet Support**: API endpoints for discovered points and hierarchical naming
- **Bulk Operations**: Automatic batching for large-scale data retrieval
- **Smart Pagination**: Automatic pagination handling for all list operations
- **Site Timeseries Export**: Export all site data to Parquet or CSV formats
- Comprehensive serializer testing for all aceiot-models
- Multiple output formats (JSON, Table)
- Configuration file and environment variable support
- Robust error handling and user-friendly output

## Installation

### From PyPI (Recommended)

```bash
# Install using pip
pip install aceiot-models-cli

# Or install using uv
uv pip install aceiot-models-cli
```

### From Source

```bash
# Clone the repository
git clone https://github.com/ACE-IoT-Solutions/aceiot-models-cli.git
cd aceiot-models-cli

# Install using uv (recommended for development)
uv pip install -e .

# Or install using pip
pip install -e .
```

## Quick Start

1. Initialize your configuration:
```bash
aceiot-models-cli init
```

2. Or set environment variables:
```bash
export ACEIOT_API_KEY="your-api-key"
export ACEIOT_API_URL="https://flightdeck.aceiot.cloud/api"
```

3. Start using the CLI:
```bash
# List all clients
aceiot-models-cli clients list

# Get a specific site
aceiot-models-cli sites get site-name

# Get point timeseries data
aceiot-models-cli points timeseries point-name --start "2024-01-01T00:00:00Z" --end "2024-01-02T00:00:00Z"

# Or enter interactive REPL mode (new!)
aceiot-models-cli repl
```

## Available Commands

### Global Options
- `--config, -c`: Path to configuration file
- `--api-url`: API base URL (default: https://flightdeck.aceiot.cloud/api)
- `--api-key`: API key for authentication
- `--output, -o`: Output format (json or table, default: table)

### Client Commands
```bash
# List clients
aceiot-models-cli clients list [--page N] [--per-page N]

# Get specific client
aceiot-models-cli clients get CLIENT_NAME

# Create new client
aceiot-models-cli clients create --name NAME [--nice-name NAME] [--bus-contact EMAIL] [--tech-contact EMAIL] [--address ADDR]
```

### Site Commands
```bash
# List sites
aceiot-models-cli sites list [--page N] [--per-page N] [--client-name NAME] [--collect-enabled] [--show-archived]

# Get specific site
aceiot-models-cli sites get SITE_NAME
```

### Gateway Commands
```bash
# List gateways
aceiot-models-cli gateways list [--page N] [--per-page N] [--show-archived]
```

### Point Commands
```bash
# List points
aceiot-models-cli points list [--page N] [--per-page N] [--site SITE_NAME]

# Get timeseries data
aceiot-models-cli points timeseries POINT_NAME --start ISO_TIME --end ISO_TIME

# List discovered BACnet points
aceiot-models-cli points discovered SITE_NAME [--page N] [--per-page N]

# Get batch timeseries data (for many points)
aceiot-models-cli points batch-timeseries -f points.txt --start ISO_TIME --end ISO_TIME [--batch-size 100]

# Export all site timeseries data to file
aceiot-models-cli sites timeseries SITE_NAME --start ISO_TIME --end ISO_TIME --output-file data.parquet
```

### Volttron Agent Deployment Commands
```bash
# Upload an agent package to a client (via gateway context)
# Packages are shared across all gateways for the client
aceiot-models-cli volttron upload-agent PATH GATEWAY --name PACKAGE_NAME [--description DESC]

# Create agent configuration on gateway
aceiot-models-cli volttron create-config CONFIG_FILE GATEWAY --agent-identity IDENTITY [--name CONFIG_NAME]

# Deploy agent (interactive mode - select from existing packages)
aceiot-models-cli volttron deploy GATEWAY
# Interactive prompts guide through:
# 1. Package selection from available uploads
# 2. Agent identity configuration  
# 3. Configuration choice (default or custom file)
# 4. For custom: file path selection with validation

# Deploy agent with specific options
aceiot-models-cli volttron deploy GATEWAY --volttron-agent '{"package_name": "pkg", "agent_identity": "id"}' --agent-config '{"agent_identity": "id", "config_name": "cfg"}'

# Quick deploy - upload, configure, and deploy in one command
aceiot-models-cli volttron quick-deploy AGENT_PATH CONFIG_FILE GATEWAY --agent-identity IDENTITY

# List available packages for a client
aceiot-models-cli volttron list-packages CLIENT_NAME

# Get deployment status for a gateway
aceiot-models-cli volttron get-config-package GATEWAY
```

### Interactive REPL Mode
```bash
# Start interactive REPL mode
aceiot-models-cli repl

# In REPL mode, use context switching:
aceiot> use site demo-site
aceiot(site:demo-site)> points list
aceiot(site:demo-site)> timeseries sensor-temp --start 2024-01-01
aceiot(site:demo-site)> use gateway gw-001
aceiot(site:demo-site/gw:gw-001)> back
aceiot(site:demo-site)> exit

# Volttron deployment context:
aceiot> use gateway gw-001
aceiot(gw:gw-001)> use volttron
aceiot(gw:gw-001/volttron)> deploy
# Interactive deployment wizard starts...

# Interactive exploration - list and select resources:
aceiot> use site
             Available sites              
+------+-----------+---------------------+
| #    | Name      | Description         |
+------+-----------+---------------------+
| 1    | demo-site | demo-site (client1) |
| 2    | test-site | test-site (client2) |
+------+-----------+---------------------+

Enter number (1-2) or press Ctrl+C to cancel: 1
Switched to site context: demo-site
```

#### REPL Features
- **Interactive exploration**: Use `use <type>` without a name to list and select resources
- **Context switching**: Enter site/gateway contexts to avoid repeating parameters
- **Smart filtering**: Sites are filtered by client context when applicable
- **Command completion**: Tab completion for commands and parameters
- **Command history**: Persistent history stored in `~/.aceiot-repl-history`
- **All CLI commands work**: Full compatibility with existing CLI functionality
- **Error recovery**: Graceful error handling without exiting REPL

#### REPL Commands
- `use <type> [<name>]`: Switch to context (client, site, gateway, volttron)
  - With name: Switch directly to that resource
  - Without name: List available resources and select interactively
- `back`: Exit current context
- `context`: Show current context
- `help [command]`: Show help
- `clear`: Clear screen
- `exit` or `quit`: Exit REPL (with confirmation if in context)

### Testing Commands
```bash
# Run comprehensive serializer tests
aceiot-models-cli test-serializers
```

## Configuration

Configuration can be provided through:

1. **Configuration file** (default: `~/.config/aceiot-models-cli/config.yaml`):
```yaml
api_url: https://flightdeck.aceiot.cloud/api
api_key: your-api-key
output_format: table
timeout: 30
```

2. **Environment variables**:
- `ACEIOT_API_URL`: API base URL
- `ACEIOT_API_KEY`: API key for authentication
- `ACEIOT_OUTPUT_FORMAT`: Default output format
- `ACEIOT_TIMEOUT`: Request timeout in seconds

3. **Command-line options** (highest priority)

## Output Formats

### Table Format (default)
Displays data in a formatted table with headers and pagination info.

### JSON Format
Outputs raw JSON data for programmatic processing:
```bash
aceiot-models-cli --output json clients list
```

## Development

### Running Tests
```bash
# Run serializer tests
aceiot-models-cli test-serializers

# Run pytest tests
pytest tests/
```



### Project Structure
```
aceiot-models-cli/
   src/
      aceiot_models_cli/
          __init__.py
          cli.py           # Main CLI entry point
          api_client.py    # API client implementation
          config.py        # Configuration management
          formatters.py    # Output formatters
          test_serializers.py  # Serializer tests
   pyproject.toml
   README.md
```

## New Features

### Volttron Agent Deployment
Complete workflow for deploying Volttron agents to IoT gateways:
- Upload agent packages with automatic directory compression to tar.gz
- Automatic validation of agent directory structure (setup.py required)
- Create and manage agent configurations with local file selection
- Interactive deployment mode with package selection from existing uploads
- Custom configuration support with JSON/YAML file validation
- Context-aware commands in REPL mode (auto-detect gateway/client)
- Progress tracking for file uploads
- Support for client-level package storage (shared across gateways)

### Site Timeseries Export
Export all timeseries data for a site to file:
- Export to Parquet or CSV formats
- Automatic batching for large datasets
- Progress tracking with rich console output
- Metadata inclusion option for point details
- Efficient data collection from multiple points

### BACnet Support
The CLI now includes support for BACnet operations:
- Discovered points endpoint for BACnet scanning results
- Hierarchical naming support (client/site/device/point)
- Table formatting for BACnet device and point data
- Uses aceiot-models Point and BACnetData models for type safety

### Bulk Operations
- Automatic batching for large point lists (100 points per request)
- Batch timeseries retrieval for efficient data collection
- Progress tracking for long-running operations

### Enhanced API Features
- Automatic pagination handling for all list operations
- Generic API helper utilities for custom integrations
- Model conversion methods for API responses
- Context injection for commands (automatic site/client detection)
- Mutually exclusive client/gateway contexts for consistency

## Error Handling

The CLI provides clear error messages and appropriate exit codes:
- Exit code 0: Success
- Exit code 1: Error (with descriptive message)

## License

Copyright (c) 2025 ACE IoT Solutions

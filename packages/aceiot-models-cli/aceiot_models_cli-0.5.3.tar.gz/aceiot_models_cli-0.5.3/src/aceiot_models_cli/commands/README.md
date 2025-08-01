# Dynamic Command Architecture for ACE IoT Models CLI

This new command architecture addresses the issues of duplicate code and boilerplate by providing a unified, extensible system for command management.

## Key Benefits

### 1. **Reduced Duplication**
- Common functionality extracted into mixins (`OutputFormatterMixin`, `ErrorHandlerMixin`, etc.)
- Base classes handle standard operations (API client management, error handling)
- Reusable decorators for command registration

### 2. **Dynamic Registration**
- Commands self-register using decorators
- No more hardcoded command lists
- Easy to add new commands without modifying core files

### 3. **Context-Aware Commands**
- Automatic context injection based on metadata
- Commands can declare their context requirements
- Simplified REPL executor logic

### 4. **Flexible Command Scopes**
- Commands can be CLI-only, REPL-only, or both
- Context-specific commands only appear when relevant
- Cleaner separation of concerns

## Architecture Overview

```
commands/
├── base.py              # Base classes and registry
├── decorators.py        # Registration decorators
├── utils.py            # Mixins and utilities
├── examples/           # Example implementations
│   ├── client_commands.py
│   ├── bacnet_commands.py
│   └── repl_commands.py
└── README.md           # This file
```

## Usage Examples

### 1. Creating a Simple Command

```python
from commands import command, BaseCommand
from commands.utils import OutputFormatterMixin, ErrorHandlerMixin

@command(
    name="list-items",
    description="List all items",
    aliases=["ls", "items"]
)
class ListItemsCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin):
    def get_click_command(self) -> click.Command:
        @click.command("list")
        @click.pass_context
        def list_items(ctx):
            try:
                client = self.require_api_client(ctx)
                result = client.get_items()
                self.format_output(result, ctx, title="Items")
            except Exception as e:
                self.handle_api_error(e, ctx)
        return list_items
```

### 2. Creating a Context-Aware Command

```python
from commands import context_command, ContextAwareCommand
from repl.context import ContextType

@context_command(
    name="get-current",
    context_types=[ContextType.GATEWAY],
    description="Get current gateway details",
    auto_inject={"gateway_name": "gateway_name"}
)
class GetCurrentGatewayCommand(ContextAwareCommand, OutputFormatterMixin):
    def get_click_command(self) -> click.Command:
        @click.command("get")
        @click.pass_context
        def get_current(ctx):
            # gateway_name is auto-injected from context
            gateway_name = self.current_gateway
            # ... implementation
        return get_current
```

### 3. Creating a REPL-Only Command

```python
from commands import repl_command

@repl_command(
    name="clear",
    description="Clear screen",
    aliases=["cls"]
)
def clear_command(args, context, executor):
    """Clear the terminal screen."""
    click.clear()
    return ""
```

## Migration Strategy

### Phase 1: Foundation (Current)
1. ✅ Create base architecture
2. ✅ Implement decorators and registry
3. ✅ Create utility mixins
4. ✅ Provide examples

### Phase 2: Migration
1. Convert existing commands to use new architecture
2. Update REPL executor to use command registry
3. Update CLI builder to use dynamic registration
4. Remove hardcoded command lists

### Phase 3: Enhancement
1. Add command discovery from plugins
2. Add command validation
3. Add command documentation generation
4. Add command testing utilities

## Comparison: Old vs New

### Old Way
```python
# In volttron_commands.py
def get_api_error_detail(error):  # Duplicated in multiple files
    # ...

@click.command()
def some_command():
    # Manual error handling
    # Manual output formatting
    # Manual context checking
```

### New Way
```python
# Using new architecture
@command(name="some-command")
class SomeCommand(BaseCommand, ErrorHandlerMixin, OutputFormatterMixin):
    # Error handling, formatting, and common logic inherited
    # Just implement the unique business logic
```

## Key Improvements

1. **DRY Principle**: Common code in base classes and mixins
2. **Open/Closed**: Easy to extend without modifying existing code
3. **Single Responsibility**: Each class has one clear purpose
4. **Dependency Injection**: Context and dependencies injected automatically
5. **Testability**: Commands are classes that can be easily unit tested
6. **Discoverability**: Registry knows all commands and their metadata

## Future Enhancements

1. **Plugin System**: Load commands from external packages
2. **Command Chaining**: Compose commands together
3. **Command Macros**: Save and replay command sequences
4. **Command History**: Track command usage for analytics
5. **Command Suggestions**: Smart command completion
6. **Command Validation**: Validate arguments before execution
"""Context management system for REPL mode."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ContextType(Enum):
    """Types of available contexts."""

    GLOBAL = "global"
    CLIENT = "client"
    SITE = "site"
    GATEWAY = "gateway"
    VOLTTRON = "volttron"


@dataclass
class ContextFrame:
    """Represents a single context frame."""

    type: ContextType
    name: str
    data: dict[str, Any] = field(default_factory=dict)
    parent: Optional["ContextFrame"] = None


class ReplContext:
    """Manages hierarchical context state for REPL sessions."""

    def __init__(self) -> None:
        self.current_frame: ContextFrame | None = None
        self.stack: list[ContextFrame] = []

    def enter_context(
        self, context_type: ContextType, name: str, data: dict[str, Any] | None = None
    ) -> None:
        """Enter a new context frame."""
        new_frame = ContextFrame(
            type=context_type, name=name, data=data or {}, parent=self.current_frame
        )

        if self.current_frame:
            self.stack.append(self.current_frame)

        self.current_frame = new_frame

    def exit_context(self) -> bool:
        """Exit current context frame. Returns True if exited, False if at root."""
        if not self.stack:
            self.current_frame = None
            return False

        self.current_frame = self.stack.pop()
        return True

    def reset_context(self) -> None:
        """Reset to global context."""
        self.current_frame = None
        self.stack.clear()

    def get_context_args(self) -> dict[str, Any]:
        """Get arguments to inject based on current context."""
        args = {}

        # Walk up the context stack to collect applicable arguments
        frame = self.current_frame
        while frame:
            if frame.type == ContextType.CLIENT:
                args["client_name"] = frame.name
                args["client-name"] = frame.name  # For CLI option format
            elif frame.type == ContextType.SITE:
                args["site_name"] = frame.name
                args["site"] = frame.name  # For --site option
            elif frame.type == ContextType.GATEWAY:
                args["gateway_name"] = frame.name
                args["gateway-name"] = frame.name  # For CLI option format
            elif frame.type == ContextType.VOLTTRON:
                # Volttron context might store package/config IDs
                args.update(frame.data)

            frame = frame.parent

        return args

    def get_context_path(self) -> str:
        """Get the current context path as a string."""
        if not self.current_frame:
            return ""

        parts = []
        frame = self.current_frame

        while frame:
            if frame.type == ContextType.SITE:
                parts.append(f"site:{frame.name}")
            elif frame.type == ContextType.CLIENT:
                parts.append(f"client:{frame.name}")
            elif frame.type == ContextType.GATEWAY:
                parts.append(f"gw:{frame.name}")
            elif frame.type == ContextType.VOLTTRON:
                parts.append(f"volttron:{frame.name}" if frame.name != "volttron" else "volttron")
            frame = frame.parent

        return "/".join(reversed(parts))

    @property
    def is_global(self) -> bool:
        """Check if currently in global context."""
        return self.current_frame is None

    @property
    def current_site(self) -> str | None:
        """Get current site name if in site context."""
        frame = self.current_frame
        while frame:
            if frame.type == ContextType.SITE:
                return frame.name
            frame = frame.parent
        return None

    @property
    def current_gateway(self) -> str | None:
        """Get current gateway name if in gateway context."""
        frame = self.current_frame
        while frame:
            if frame.type == ContextType.GATEWAY:
                return frame.name
            frame = frame.parent
        return None

    @property
    def current_client(self) -> str | None:
        """Get current client name if in client context."""
        frame = self.current_frame
        while frame:
            if frame.type == ContextType.CLIENT:
                return frame.name
            frame = frame.parent
        return None

"""
TextualTerminal: Textual widget that provides terminal emulation.

This module provides the TextualTerminal widget that combines the base
Terminal class with Textual's reactive system and UI components.
"""

from __future__ import annotations

from typing import Any, Optional

from textual.app import ComposeResult
from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message

from bittty import Terminal
from bittty import constants
from .terminal_scroll_view import TerminalScrollView
from ..rich_cache import ansi_to_rich


class TextualTerminal(Terminal, Widget):
    """A terminal emulator widget for Textual applications."""

    # Make terminal focusable so it can receive key events
    can_focus = True

    # Override tab behavior to prevent focus changes
    BINDINGS = [
        ("tab", "pass_to_terminal", ""),
    ]

    DEFAULT_CSS = """
    TextualTerminal {
        background: black;
        color: white;
    }

    TextualTerminal > TerminalScrollView {
        background: black;
        color: white;
        border: none;
        padding: 0;
        margin: 0;
    }
    """

    # Terminal attributes as reactive
    title: str = reactive("Terminal", always_update=True)
    icon_title: str = reactive("Terminal", always_update=True)
    cursor_x: int = reactive(0, always_update=True)
    cursor_y: int = reactive(0, always_update=True)
    command: str = reactive("/bin/bash", always_update=True)
    current_buffer = reactive(None, always_update=True)
    show_mouse: bool = reactive(False, always_update=True)

    def __init__(
        self,
        command: str = "/bin/bash",
        width: int = 80,
        height: int = 24,
        **kwargs: Any,
    ) -> None:
        """Initialize the terminal widget."""
        # Initialize Widget with its kwargs
        Widget.__init__(self, **kwargs)
        # Initialize Terminal with its specific parameters
        Terminal.__init__(self, command, width, height)

        # Set reactive values
        self.command = command

        # Terminal scroll view for display
        self.terminal_view: Optional[TerminalScrollView] = None

        # Set up async PTY handling
        self.set_pty_data_callback(self._handle_pty_data)

        # Initialize current_buffer reactive
        self.current_buffer = self.primary_buffer

    # Message classes for events
    class PTYDataMessage(Message):
        """Message containing PTY data."""

        def __init__(self, data: str) -> None:
            self.data = data
            super().__init__()

    class TitleChanged(Message):
        """Posted when terminal title changes."""

        def __init__(self, title: str) -> None:
            self.title = title
            super().__init__()

    class IconTitleChanged(Message):
        """Posted when terminal icon title changes."""

        def __init__(self, icon_title: str) -> None:
            self.icon_title = icon_title
            super().__init__()

    class ProcessExited(Message):
        """Posted when terminal process exits."""

        def __init__(self, exit_code: int) -> None:
            self.exit_code = exit_code
            super().__init__()

    class Bell(Message):
        """Posted when terminal bell is triggered."""

        pass

    class BufferSwitched(Message):
        """Posted when switching between primary and alternate buffers."""

        def __init__(self, buffer_name: str) -> None:
            self.buffer_name = buffer_name
            super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the terminal widget."""
        self.terminal_view = TerminalScrollView()
        yield self.terminal_view

    async def on_mount(self) -> None:
        """Handle widget mounting."""
        await self.start_process()

    async def on_unmount(self) -> None:
        """Handle widget unmounting."""
        self.stop_process()

    def get_line_rich(self, y: int, width: int = None):
        """Get a single line as Rich Text object (cached)."""
        if width is None:
            width = self.width

        # Get line as ANSI string
        ansi_line = self.current_buffer.get_line(
            y,
            width=width,
            cursor_x=self.cursor_x,
            cursor_y=self.cursor_y,
            show_cursor=self.cursor_visible,
            mouse_x=self.mouse_x,
            mouse_y=self.mouse_y,
            show_mouse=self.show_mouse,
        )

        # Convert ANSI string to Rich Text (cached)
        return ansi_to_rich(ansi_line)

    def _handle_pty_data(self, data: str) -> None:
        """Handle PTY data by posting a Textual message."""
        self.post_message(self.PTYDataMessage(data))

    async def on_textual_terminal_ptydata_message(self, message: PTYDataMessage) -> None:
        """Handle PTY data messages through Textual's message system."""
        # Process the PTY data
        self.parser.feed(message.data)

        # Update display
        await self._update_display()

    async def _update_display(self) -> None:
        """Update the TerminalScrollView display with current screen content."""
        if self.terminal_view is None:
            return

        # Update the scroll view
        self.terminal_view.update_content()

    def stop_process(self) -> None:
        """Override to post message when process exits."""
        # Get exit code before cleaning up the process
        exit_code = 0
        if self.process:
            exit_code = self.process.poll() or 0

        # Call parent method (this will set self.process = None)
        super().stop_process()

        # Post exit message
        self.post_message(self.ProcessExited(exit_code))

    def bell(self) -> None:
        """Override to post bell message."""
        self.post_message(self.Bell())

    def set_title(self, title: str) -> None:
        """Override to trigger reactive update."""
        # Update the reactive attribute (this will trigger watchers)
        self.title = title

    # Reactive watchers
    def watch_title(self, old_title: str, new_title: str) -> None:
        """Called when title changes."""
        self.post_message(self.TitleChanged(new_title))

    def watch_icon_title(self, old_icon_title: str, new_icon_title: str) -> None:
        """Called when icon title changes."""
        self.post_message(self.IconTitleChanged(new_icon_title))

    def watch_current_buffer(self, old_buffer, new_buffer) -> None:
        """Called when current buffer changes."""
        # Determine buffer name
        buffer_name = "alternate" if new_buffer is self.alt_buffer else "primary"
        self.post_message(self.BufferSwitched(buffer_name))

    async def watch_show_mouse(self, old_show_mouse: bool, new_show_mouse: bool) -> None:
        """Called when show_mouse changes."""
        await self._update_display()

    async def on_resize(self, event) -> None:
        """Handle widget resize events from Textual."""
        # Update the base Terminal size
        super().resize(event.size.width, event.size.height)

    # Input handling
    async def on_mouse_move(self, event) -> None:
        """Handle mouse movement events."""
        if self.pty is None:
            return

        self.input_mouse(
            x=event.x + 1,
            y=event.y + 1,
            button=constants.MOUSE_BUTTON_MOVEMENT,
            event_type="move",
            modifiers=self._get_modifiers(event),
        )

        # Trigger display update for mouse cursor
        if self.show_mouse:
            await self._update_display()

    async def on_mouse_down(self, event) -> None:
        """Handle mouse button press events."""
        if self.pty is None:
            return

        button_map = {
            "left": constants.MOUSE_BUTTON_LEFT,
            "middle": constants.MOUSE_BUTTON_MIDDLE,
            "right": constants.MOUSE_BUTTON_RIGHT,
        }
        button = button_map.get(event.button, constants.MOUSE_BUTTON_LEFT)

        self.input_mouse(
            x=event.x + 1,
            y=event.y + 1,
            button=button,
            event_type="press",
            modifiers=self._get_modifiers(event),
        )

    async def on_mouse_up(self, event) -> None:
        """Handle mouse button release events."""
        if self.pty is None:
            return

        button_map = {
            "left": constants.MOUSE_BUTTON_LEFT,
            "middle": constants.MOUSE_BUTTON_MIDDLE,
            "right": constants.MOUSE_BUTTON_RIGHT,
        }
        button = button_map.get(event.button, constants.MOUSE_BUTTON_LEFT)

        self.input_mouse(
            x=event.x + 1,
            y=event.y + 1,
            button=button,
            event_type="release",
            modifiers=self._get_modifiers(event),
        )

    async def on_mouse_scroll_down(self, event) -> None:
        """Handle mouse wheel scroll down events."""
        if self.pty is None:
            return

        # Check if mouse tracking is enabled
        if self.mouse_tracking or self.mouse_button_tracking or self.mouse_any_tracking:
            self.input_mouse(
                x=event.x + 1,
                y=event.y + 1,
                button=constants.MOUSE_BUTTON_WHEEL_DOWN,
                event_type="press",
                modifiers=self._get_modifiers(event),
            )

    async def on_mouse_scroll_up(self, event) -> None:
        """Handle mouse wheel scroll up events."""
        if self.pty is None:
            return

        # Check if mouse tracking is enabled
        if self.mouse_tracking or self.mouse_button_tracking or self.mouse_any_tracking:
            self.input_mouse(
                x=event.x + 1,
                y=event.y + 1,
                button=constants.MOUSE_BUTTON_WHEEL_UP,
                event_type="press",
                modifiers=self._get_modifiers(event),
            )

    async def on_key(self, event) -> None:
        """Handle key events."""
        if self.pty is None:
            return

        # Don't intercept certain app-level keys
        app_keys = {"ctrl+q", "ctrl+n"}  # Add other app bindings as needed
        if event.key in app_keys:
            # Let the app handle these keys
            return

        # Parse key and route to appropriate input method
        if self._handle_key_input(event):
            # Prevent the key from propagating to Textual (important for tab, etc.)
            event.stop()
            return

        # If we couldn't handle the key, let Textual handle it
        # (but this means focus keys like Tab will still work for navigation)

    def _get_modifiers(self, event) -> set[str]:
        """Extract active modifiers from a mouse or key event."""
        modifiers = set()
        if event.shift:
            modifiers.add("shift")
        if event.meta:
            modifiers.add("meta")
        if event.ctrl:
            modifiers.add("ctrl")
        return modifiers

    def _handle_key_input(self, event) -> bool:
        """Parse Textual key event and route to appropriate Terminal input method."""
        key = event.key

        # Parse modifiers from key string
        modifier = self._parse_modifiers(key)
        base_key = self._extract_base_key(key)

        # Handle printable characters first (use event.character if available)
        if hasattr(event, "character") and event.character and len(event.character) == 1:
            self.input_key(event.character, modifier)
            return True
        elif len(base_key) == 1 and base_key.isprintable():
            self.input_key(base_key, modifier)
            return True

        # Handle function keys (f1, f2, etc.)
        if base_key.startswith("f") and base_key[1:].isdigit():
            try:
                fkey_num = int(base_key[1:])
                self.input_fkey(fkey_num, modifier)
                return True
            except ValueError:
                pass

        # Handle cursor and navigation keys
        if base_key in ["up", "down", "left", "right", "home", "end"]:
            self.input_key(base_key, modifier)
            return True

        # Handle backspace through input_key (it might need mode awareness)
        if base_key == "backspace":
            self.input_key(base_key, modifier)
            return True

        # Handle special keys with raw sequences
        special_keys = {
            "enter": constants.CR,
            "tab": constants.HT,
            "escape": constants.ESC,
            "delete": f"{constants.ESC}[3~",
            "pageup": f"{constants.ESC}[5~",
            "pagedown": f"{constants.ESC}[6~",
            "space": " ",
        }

        if base_key in special_keys:
            # TODO: Some of these might need modifier support
            self.input(special_keys[base_key])
            return True

        # Unhandled key
        return False

    def _parse_modifiers(self, key: str) -> int:
        """Extract modifier flags from Textual key string."""
        modifier = constants.KEY_MOD_NONE

        if "ctrl+" in key:
            modifier = constants.KEY_MOD_CTRL
        if "shift+" in key:
            if modifier == constants.KEY_MOD_NONE:
                modifier = constants.KEY_MOD_SHIFT
            elif modifier == constants.KEY_MOD_CTRL:
                modifier = constants.KEY_MOD_SHIFT_CTRL
        if "alt+" in key:
            if modifier == constants.KEY_MOD_NONE:
                modifier = constants.KEY_MOD_ALT
            elif modifier == constants.KEY_MOD_CTRL:
                modifier = constants.KEY_MOD_ALT_CTRL
            elif modifier == constants.KEY_MOD_SHIFT:
                modifier = constants.KEY_MOD_SHIFT_ALT
            elif modifier == constants.KEY_MOD_SHIFT_CTRL:
                modifier = constants.KEY_MOD_SHIFT_ALT_CTRL

        return modifier

    def _extract_base_key(self, key: str) -> str:
        """Extract the base key from a Textual key string (remove modifiers)."""
        # Remove all modifier prefixes
        base = key
        for prefix in ["ctrl+", "shift+", "alt+", "meta+"]:
            base = base.replace(prefix, "")
        return base

    def action_pass_to_terminal(self) -> None:
        """Action handler for keys that should go to terminal."""
        # This will be called for tab key, send it to terminal
        self.input(constants.HT)

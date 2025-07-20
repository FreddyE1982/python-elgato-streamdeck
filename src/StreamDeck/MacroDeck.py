#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#
"""Simple macro framework for StreamDeck devices.

This helper class allows applications to associate callbacks with key, dial
and touch events, manage image and character boards and perform common deck
operations.  A new :func:`reset` helper is included to clear all stored
configuration and return the deck to a blank state.
"""

import subprocess
import time
from collections.abc import Callable
from typing import Any, Iterable
from PIL import Image, ImageDraw, ImageFont

from .ImageHelpers import PILHelper

from .Devices.StreamDeck import StreamDeck, DialEventType, TouchscreenEventType


class MacroDeck:
    """High level wrapper to attach actions to deck events."""

    def __init__(self, deck: StreamDeck):
        self.deck = deck
        self.key_macros: dict[int, Callable[[], Any] | str] = {}
        self.dial_macros: dict[tuple[int, DialEventType], Callable[[Any], Any] | str] = {}
        self.touch_macros: dict[TouchscreenEventType, Callable[[Any], Any] | str] = {}
        self.key_configs: dict[int, dict[str, Any]] = {}
        self.enabled: bool = True
        self.board: list[list[str]] | None = None
        self.image_board: list[list[bytes | None]] | None = None
        self._loop_running: bool = False

        self.deck.set_key_callback(self._handle_key)
        self.deck.set_dial_callback(self._handle_dial)
        self.deck.set_touchscreen_callback(self._handle_touch)

    def enable(self) -> None:
        """Enable macro execution."""
        self.enabled = True

    def disable(self) -> None:
        """Disable macro execution."""
        self.enabled = False

    def is_enabled(self) -> bool:
        """Return ``True`` if macro actions are enabled."""
        return self.enabled

    def reset(self) -> None:
        """Reset all macros and board state, clearing the deck."""

        self.clear_all_key_configurations()
        self.dial_macros.clear()
        self.touch_macros.clear()
        self.board = None
        self.image_board = None
        self.enabled = True
        self.deck.reset()

    def register_key_macro(self, key: int, action: Callable[[], Any] | str) -> None:
        """Register a macro action for a key press."""
        self.key_macros[key] = action

    def register_dial_macro(self, dial: int, event: DialEventType, action: Callable[[Any], Any] | str) -> None:
        """Register a macro action for a dial event."""
        self.dial_macros[(dial, event)] = action

    def register_touch_macro(self, event: TouchscreenEventType, action: Callable[[Any], Any] | str) -> None:
        """Register a macro action for a touchscreen event."""
        self.touch_macros[event] = action

    def unregister_key_macro(self, key: int) -> None:
        """Remove any macro action associated with a key press."""
        self.key_macros.pop(key, None)

    def unregister_dial_macro(self, dial: int, event: DialEventType) -> None:
        """Remove the macro action associated with a dial event."""
        self.dial_macros.pop((dial, event), None)

    def unregister_touch_macro(self, event: TouchscreenEventType) -> None:
        """Remove the macro action associated with a touchscreen event."""
        self.touch_macros.pop(event, None)

    def get_dial_macro(self, dial: int, event: DialEventType) -> Callable[[Any], Any] | str | None:
        """Retrieve the macro action registered for a dial event, if any."""
        return self.dial_macros.get((dial, event))

    def get_touch_macro(self, event: TouchscreenEventType) -> Callable[[Any], Any] | str | None:
        """Retrieve the macro action registered for a touchscreen event, if any."""
        return self.touch_macros.get(event)

    def update_dial_macro(self, dial: int, event: DialEventType, action: Callable[[Any], Any] | str | None) -> None:
        """Update or remove the macro action for a dial event."""
        if action is None:
            self.unregister_dial_macro(dial, event)
        else:
            self.register_dial_macro(dial, event, action)

    def update_touch_macro(self, event: TouchscreenEventType, action: Callable[[Any], Any] | str | None) -> None:
        """Update or remove the macro action for a touchscreen event."""
        if action is None:
            self.unregister_touch_macro(event)
        else:
            self.register_touch_macro(event, action)

    def configured_keys(self) -> list[int]:
        """Return a list of keys that have a stored configuration."""
        return list(self.key_configs.keys())

    def macro_keys(self) -> list[int]:
        """Return a list of keys with registered macros."""
        return list(self.key_macros.keys())

    def macro_dials(self) -> list[tuple[int, DialEventType]]:
        """Return a list of dials with registered macros."""
        return list(self.dial_macros.keys())

    def macro_touches(self) -> list[TouchscreenEventType]:
        """Return a list of touchscreen events with registered macros."""
        return list(self.touch_macros.keys())

    def is_key_configured(self, key: int) -> bool:
        """Return ``True`` if the given key has a stored configuration."""
        return key in self.key_configs

    def copy_key_configuration(self, source: int, destination: int) -> None:
        """Copy the configuration and macro from one key to another."""
        if source == destination:
            return

        config = self.key_configs.get(source)
        if config is not None:
            self.key_configs[destination] = dict(config)
            if self.deck.is_visual() and config.get("up_image") is not None:
                self.deck.set_key_image(destination, config["up_image"])

        if source in self.key_macros:
            self.key_macros[destination] = self.key_macros[source]

    def move_key_configuration(self, source: int, destination: int) -> None:
        """Move the configuration and macro from one key to another."""
        self.copy_key_configuration(source, destination)
        self.clear_key_configuration(source)

    def swap_key_configurations(self, key_a: int, key_b: int) -> None:
        """Swap the configurations and macros of two keys."""
        if key_a == key_b:
            return

        config_a = self.key_configs.get(key_a)
        config_b = self.key_configs.get(key_b)
        macro_a = self.key_macros.get(key_a)
        macro_b = self.key_macros.get(key_b)

        if config_a is not None:
            self.key_configs[key_b] = dict(config_a)
        else:
            self.key_configs.pop(key_b, None)

        if config_b is not None:
            self.key_configs[key_a] = dict(config_b)
        else:
            self.key_configs.pop(key_a, None)

        if macro_a is not None:
            self.key_macros[key_b] = macro_a
        else:
            self.key_macros.pop(key_b, None)

        if macro_b is not None:
            self.key_macros[key_a] = macro_b
        else:
            self.key_macros.pop(key_a, None)

        if self.deck.is_visual():
            if config_a and config_a.get("up_image") is not None:
                self.deck.set_key_image(key_b, config_a["up_image"])
            else:
                self.deck.set_key_image(key_b, None)  # type: ignore[arg-type]

            if config_b and config_b.get("up_image") is not None:
                self.deck.set_key_image(key_a, config_b["up_image"])
            else:
                self.deck.set_key_image(key_a, None)  # type: ignore[arg-type]

    def copy_key_macro(self, source: int, destination: int) -> None:
        """Copy the macro from one key to another."""
        if source == destination:
            return

        if source in self.key_macros:
            self.key_macros[destination] = self.key_macros[source]
        else:
            self.key_macros.pop(destination, None)

    def move_key_macro(self, source: int, destination: int) -> None:
        """Move the macro from one key to another."""
        self.copy_key_macro(source, destination)
        self.unregister_key_macro(source)

    def swap_key_macros(self, key_a: int, key_b: int) -> None:
        """Swap the macros of two keys."""
        if key_a == key_b:
            return

        macro_a = self.key_macros.get(key_a)
        macro_b = self.key_macros.get(key_b)

        if macro_a is not None:
            self.key_macros[key_b] = macro_a
        else:
            self.key_macros.pop(key_b, None)

        if macro_b is not None:
            self.key_macros[key_a] = macro_b
        else:
            self.key_macros.pop(key_a, None)

    def clear_all_key_configurations(self) -> None:
        """Clear the configurations and macros for all keys."""
        keys = set(self.key_configs.keys()) | set(self.key_macros.keys())
        for key in list(keys):
            self.clear_key_configuration(key)

    def register_key_macros(self, macros: dict[int, Callable[[], Any] | str]) -> None:
        """Register multiple key macros in one call."""
        for key, action in macros.items():
            self.register_key_macro(key, action)

    def unregister_key_macros(self, keys: Iterable[int]) -> None:
        """Remove macros for the specified keys."""
        for key in keys:
            self.unregister_key_macro(key)

    def configure_keys(self, configs: dict[int, dict[str, Any]]) -> None:
        """Configure several keys in one call."""
        for key, params in configs.items():
            self.configure_key(
                key,
                upimage=params.get("upimage"),
                downimage=params.get("downimage"),
                uptext=params.get("uptext"),
                downtext=params.get("downtext"),
                pressedcallback=params.get("pressedcallback"),
            )

    def update_key_configurations_bulk(self, configs: dict[int, dict[str, Any]]) -> None:
        """Update multiple key configurations at once."""
        for key, params in configs.items():
            self.update_key_configuration(
                key,
                upimage=params.get("upimage"),
                downimage=params.get("downimage"),
                uptext=params.get("uptext"),
                downtext=params.get("downtext"),
                pressedcallback=params.get("pressedcallback"),
            )

    def clear_key_configurations(self, keys: Iterable[int]) -> None:
        """Clear the configurations for several keys."""
        for key in keys:
            self.clear_key_configuration(key)

    def refresh_key_images(self, keys: Iterable[int] | None = None) -> None:
        """Reapply stored images for the given keys."""
        if not self.deck.is_visual():
            return

        target_keys = keys if keys is not None else self.key_configs.keys()
        for key in target_keys:
            config = self.key_configs.get(key)
            if config and config.get("up_image") is not None:
                self.deck.set_key_image(key, config["up_image"])
            else:
                self.deck.set_key_image(key, None)  # type: ignore[arg-type]

    def get_key_macro(self, key: int) -> Callable[[], Any] | str | None:
        """Retrieve the macro action registered for a key press, if any."""
        return self.key_macros.get(key)

    def get_key_configuration(self, key: int) -> dict[str, Any] | None:
        """Return the stored configuration dictionary for a key, if present."""
        return self.key_configs.get(key)

    def update_key_macro(self, key: int, action: Callable[[], Any] | str | None) -> None:
        """Update or remove the macro action for a key press."""
        if action is None:
            self.unregister_key_macro(key)
        else:
            self.register_key_macro(key, action)

    def update_key_configuration(
        self,
        key: int,
        upimage: str | None = None,
        downimage: str | None = None,
        uptext: str | None = None,
        downtext: str | None = None,
        pressedcallback: Callable[[], Any] | str | None = None,
    ) -> None:
        """Modify an existing key configuration.

        This is an alias to :func:`configure_key` that can be used to update the
        stored configuration for a key. Omitted parameters are left unchanged.
        """

        self.configure_key(
            key,
            upimage=upimage,
            downimage=downimage,
            uptext=uptext,
            downtext=downtext,
            pressedcallback=pressedcallback,
        )

    def clear_key_configuration(self, key: int) -> None:
        """Clear key images and any associated macro callback."""
        self.key_configs.pop(key, None)
        self.unregister_key_macro(key)
        if self.deck.is_visual():
            self.deck.set_key_image(key, None)  # type: ignore[arg-type]

    def configure_key(
        self,
        key: int,
        upimage: str | None = None,
        downimage: str | None = None,
        uptext: str | None = None,
        downtext: str | None = None,
        pressedcallback: Callable[[], Any] | str | None = None,
    ) -> None:
        """Configure images and callback for a key.

        Any combination of parameters can be provided; omitted ones are
        left unchanged.
        """

        config = self.key_configs.get(key, {"up_image": None, "down_image": None})

        if upimage is not None or uptext is not None:
            config["up_image"] = self._build_image(upimage, uptext)

        if downimage is not None or downtext is not None:
            config["down_image"] = self._build_image(downimage, downtext)

        self.key_configs[key] = config

        if pressedcallback is not None:
            self.register_key_macro(key, pressedcallback)

        if config.get("up_image") is not None:
            self.deck.set_key_image(key, config["up_image"])

    def set_key_text(self, key: int, text: str, pressed: bool = False) -> None:
        """Display the given text on a key."""
        if pressed:
            self.update_key_configuration(key, downtext=text)
        else:
            self.update_key_configuration(key, uptext=text)

    def set_key_image_file(self, key: int, path: str, pressed: bool = False) -> None:
        """Display an image from ``path`` on a key."""
        if pressed:
            self.update_key_configuration(key, downimage=path)
        else:
            self.update_key_configuration(key, upimage=path)

    def set_key_image_pil(self, key: int, image: Image.Image, pressed: bool = False) -> None:
        """Display a PIL image on a key."""
        img = PILHelper.to_native_key_format(self.deck, PILHelper.create_scaled_key_image(self.deck, image))
        config = self.key_configs.get(key, {"up_image": None, "down_image": None})
        if pressed:
            config["down_image"] = img
        else:
            config["up_image"] = img
        self.key_configs[key] = config
        if self.deck.is_visual():
            self.deck.set_key_image(key, img)

    def set_key_image_bytes(self, key: int, image: bytes | None, pressed: bool = False) -> None:
        """Display a pre-formatted image on a key."""
        config = self.key_configs.get(key, {"up_image": None, "down_image": None})
        if pressed:
            config["down_image"] = image
        else:
            config["up_image"] = image
        self.key_configs[key] = config
        if self.deck.is_visual():
            self.deck.set_key_image(key, image)

    def get_key_image(self, key: int, pressed: bool = False) -> bytes | None:
        """Return the stored image for ``key`` if present."""
        config = self.key_configs.get(key)
        if config is None:
            return None
        return config.get("down_image" if pressed else "up_image")

    def has_key_image(self, key: int, pressed: bool = False) -> bool:
        """Return ``True`` if ``key`` has an image stored."""
        return self.get_key_image(key, pressed) is not None

    def clear_key_image(self, key: int, pressed: bool | None = None) -> None:
        """Remove stored images from ``key`` without altering its macro."""
        config = self.key_configs.get(key)
        if config is None:
            return
        if pressed is None or not pressed:
            config["up_image"] = None
        if pressed is None or pressed:
            config["down_image"] = None
        if self.deck.is_visual():
            self.deck.set_key_image(key, None)

    def copy_key_image(self, source: int, destination: int, pressed: bool = False) -> None:
        """Copy the image from ``source`` key to ``destination`` key."""
        if source == destination:
            return

        img = self.get_key_image(source, pressed)
        self.set_key_image_bytes(destination, img, pressed)

    def move_key_image(self, source: int, destination: int, pressed: bool = False) -> None:
        """Move the image from ``source`` key to ``destination`` key."""
        self.copy_key_image(source, destination, pressed)
        self.clear_key_image(source, pressed)

    def swap_key_images(self, key_a: int, key_b: int, pressed: bool = False) -> None:
        """Swap the images of ``key_a`` and ``key_b``."""
        if key_a == key_b:
            return

        img_a = self.get_key_image(key_a, pressed)
        img_b = self.get_key_image(key_b, pressed)
        self.set_key_image_bytes(key_a, img_b, pressed)
        self.set_key_image_bytes(key_b, img_a, pressed)

    def get_pressed_keys(self) -> list[int]:
        """Return a list of keys that are currently pressed."""
        return [i for i, state in enumerate(self.deck.key_states()) if state]

    def get_pressed_chars(self) -> list[str]:
        """Return the characters on all currently pressed keys."""
        if self.board is None:
            raise ValueError("Board not initialised")

        chars: list[str] = []
        for key in self.get_pressed_keys():
            row, col = self.key_to_position(key)
            chars.append(self.board[row][col])
        return chars

    def wait_for_key_press(self, timeout: float | None = None) -> int | None:
        """Wait for a key press and return its index or ``None`` on timeout."""
        start = time.time()
        while True:
            pressed = self.get_pressed_keys()
            if pressed:
                return pressed[0]
            if timeout is not None and (time.time() - start) >= timeout:
                return None
            time.sleep(0.01)

    def display_text(self, lines: list[str]) -> None:
        """Display multiple lines of text across the deck."""
        cols = self.deck.KEY_COLS
        rows = self.deck.KEY_ROWS
        for row in range(rows):
            line = lines[row] if row < len(lines) else ""
            for col in range(cols):
                key = row * cols + col
                char = line[col] if col < len(line) else ""
                self.set_key_text(key, char)

    def position_to_key(self, row: int, col: int) -> int:
        """Return the key index for a given ``(row, column)`` position."""
        if not (0 <= row < self.deck.KEY_ROWS) or not (0 <= col < self.deck.KEY_COLS):
            raise IndexError("Invalid row or column")
        return row * self.deck.KEY_COLS + col

    def key_to_position(self, key: int) -> tuple[int, int]:
        """Return the ``(row, column)`` position for a key index."""
        if not (0 <= key < self.deck.key_count()):
            raise IndexError("Invalid key index")
        return divmod(key, self.deck.KEY_COLS)

    def display_board(self, board: list[list[str]]) -> None:
        """Display a 2D array of single characters across the deck."""
        for row in range(self.deck.KEY_ROWS):
            for col in range(self.deck.KEY_COLS):
                char = ""
                if row < len(board) and col < len(board[row]):
                    char = board[row][col]
                self.set_key_text(self.position_to_key(row, col), char)

    # Board helpers -----------------------------------------------------
    def create_board(self, fill: str = " ") -> None:
        """Create an internal character board and display it."""
        self.board = [[fill for _ in range(self.deck.KEY_COLS)] for _ in range(self.deck.KEY_ROWS)]
        self.display_board(self.board)

    def create_board_from_strings(self, lines: list[str], fill: str = " ") -> None:
        """Create an internal board from ``lines`` and display it."""
        rows = self.deck.KEY_ROWS
        cols = self.deck.KEY_COLS
        self.board = [[fill for _ in range(cols)] for _ in range(rows)]
        for r in range(min(rows, len(lines))):
            line = lines[r]
            for c in range(min(cols, len(line))):
                self.board[r][c] = line[c]
        self.display_board(self.board)

    def clear_board(self, fill: str = " ") -> None:
        """Clear the internal board to ``fill`` and redraw it."""
        if self.board is None:
            self.create_board(fill)
            return
        for row in range(self.deck.KEY_ROWS):
            for col in range(self.deck.KEY_COLS):
                self.board[row][col] = fill
        self.display_board(self.board)

    def set_board_char(self, row: int, col: int, char: str) -> None:
        """Set a character on the internal board at ``(row, col)``."""
        if self.board is None:
            self.create_board()
        if not (0 <= row < self.deck.KEY_ROWS) or not (0 <= col < self.deck.KEY_COLS):
            raise IndexError("Invalid row or column")
        self.board[row][col] = char
        self.set_key_text(self.position_to_key(row, col), char)

    def get_board_char(self, row: int, col: int) -> str:
        """Return the character stored at ``(row, col)``."""
        if self.board is None:
            raise ValueError("Board not initialised")
        if not (0 <= row < self.deck.KEY_ROWS) or not (0 <= col < self.deck.KEY_COLS):
            raise IndexError("Invalid row or column")
        return self.board[row][col]

    def get_board(self) -> list[list[str]]:
        """Return a copy of the internal character board."""
        if self.board is None:
            raise ValueError("Board not initialised")
        return [list(r) for r in self.board]

    def get_board_as_strings(self) -> list[str]:
        """Return the internal board as a list of strings."""
        if self.board is None:
            raise ValueError("Board not initialised")
        return ["".join(row) for row in self.board]

    def refresh_board(self) -> None:
        """Redraw the internal board on the deck."""
        if self.board is not None:
            self.display_board(self.board)

    def draw_text(self, row: int, col: int, text: str) -> None:
        """Draw ``text`` onto the internal board starting at ``(row, col)``."""
        if self.board is None:
            self.create_board()
        for offset, char in enumerate(text):
            r = row
            c = col + offset
            if 0 <= r < self.deck.KEY_ROWS and 0 <= c < self.deck.KEY_COLS:
                self.board[r][c] = char
                self.set_key_text(self.position_to_key(r, c), char)

    def draw_multiline_text(self, top: int, left: int, lines: list[str]) -> None:
        """Draw multiple lines of text onto the board starting at ``(top, left)``."""
        if self.board is None:
            self.create_board()
        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                rr = top + r
                cc = left + c
                if 0 <= rr < self.deck.KEY_ROWS and 0 <= cc < self.deck.KEY_COLS:
                    self.board[rr][cc] = char
                    self.set_key_text(self.position_to_key(rr, cc), char)

    def overlay_board(
        self, board: list[list[str]], top: int = 0, left: int = 0
    ) -> None:
        """Overlay ``board`` onto the internal board at ``(top, left)``."""
        if self.board is None:
            self.create_board()

        for r, row_data in enumerate(board):
            for c, char in enumerate(row_data):
                rr = top + r
                cc = left + c
                if 0 <= rr < self.deck.KEY_ROWS and 0 <= cc < self.deck.KEY_COLS:
                    self.board[rr][cc] = char
                    self.set_key_text(self.position_to_key(rr, cc), char)

    def scroll_board(self, dx: int = 0, dy: int = 0, fill: str = " ") -> None:
        """Scroll the board by ``(dx, dy)`` and fill empty cells with ``fill``."""
        if self.board is None:
            self.create_board(fill)

        new_board = [[fill for _ in range(self.deck.KEY_COLS)] for _ in range(self.deck.KEY_ROWS)]

        for r in range(self.deck.KEY_ROWS):
            for c in range(self.deck.KEY_COLS):
                nr = r + dy
                nc = c + dx
                if 0 <= nr < self.deck.KEY_ROWS and 0 <= nc < self.deck.KEY_COLS:
                    new_board[nr][nc] = self.board[r][c]

        self.board = new_board
        self.refresh_board()

    def draw_rect(self, top: int, left: int, height: int, width: int, char: str) -> None:
        """Draw a rectangle on the board using ``char``."""
        if self.board is None:
            self.create_board()

        for r in range(top, top + height):
            if 0 <= r < self.deck.KEY_ROWS:
                if 0 <= left < self.deck.KEY_COLS:
                    self.set_board_char(r, left, char)
                if 0 <= left + width - 1 < self.deck.KEY_COLS:
                    self.set_board_char(r, left + width - 1, char)

        for c in range(left, left + width):
            if 0 <= c < self.deck.KEY_COLS:
                if 0 <= top < self.deck.KEY_ROWS:
                    self.set_board_char(top, c, char)
                if 0 <= top + height - 1 < self.deck.KEY_ROWS:
                    self.set_board_char(top + height - 1, c, char)

    def fill_rect(self, top: int, left: int, height: int, width: int, char: str) -> None:
        """Fill a rectangular region on the board with ``char``."""
        if self.board is None:
            self.create_board()

        for r in range(top, top + height):
            if 0 <= r < self.deck.KEY_ROWS:
                for c in range(left, left + width):
                    if 0 <= c < self.deck.KEY_COLS:
                        self.set_board_char(r, c, char)

    def draw_line(
        self,
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int,
        char: str,
    ) -> None:
        """Draw a straight line on the board using ``char``."""
        if self.board is None:
            self.create_board()

        dr = end_row - start_row
        dc = end_col - start_col
        steps = max(abs(dr), abs(dc))
        if steps == 0:
            if 0 <= start_row < self.deck.KEY_ROWS and 0 <= start_col < self.deck.KEY_COLS:
                self.set_board_char(start_row, start_col, char)
            return

        for i in range(steps + 1):
            r = round(start_row + (dr * i) / steps)
            c = round(start_col + (dc * i) / steps)
            if 0 <= r < self.deck.KEY_ROWS and 0 <= c < self.deck.KEY_COLS:
                self.set_board_char(r, c, char)

    # Image board helpers -------------------------------------------------
    def display_image_board(self, board: list[list[bytes | None]]) -> None:
        """Display a 2D array of key images across the deck."""
        if not self.deck.is_visual():
            return
        for row in range(self.deck.KEY_ROWS):
            for col in range(self.deck.KEY_COLS):
                image = None
                if row < len(board) and col < len(board[row]):
                    image = board[row][col]
                self.deck.set_key_image(self.position_to_key(row, col), image)

    def create_image_board(self, fill: bytes | None = None) -> None:
        """Create an internal image board and display it."""
        self.image_board = [
            [fill for _ in range(self.deck.KEY_COLS)]
            for _ in range(self.deck.KEY_ROWS)
        ]
        self.display_image_board(self.image_board)

    def clear_image_board(self, fill: bytes | None = None) -> None:
        """Clear the internal image board to ``fill`` and redraw it."""
        if self.image_board is None:
            self.create_image_board(fill)
            return
        for row in range(self.deck.KEY_ROWS):
            for col in range(self.deck.KEY_COLS):
                self.image_board[row][col] = fill
        self.display_image_board(self.image_board)

    def set_board_image(self, row: int, col: int, image: bytes | None) -> None:
        """Set an image on the internal board at ``(row, col)``."""
        if self.image_board is None:
            self.create_image_board()
        if not (0 <= row < self.deck.KEY_ROWS) or not (0 <= col < self.deck.KEY_COLS):
            raise IndexError("Invalid row or column")
        self.image_board[row][col] = image
        if self.deck.is_visual():
            self.deck.set_key_image(self.position_to_key(row, col), image)

    def get_board_image(self, row: int, col: int) -> bytes | None:
        """Return the image stored at ``(row, col)``."""
        if self.image_board is None:
            raise ValueError("Image board not initialised")
        if not (0 <= row < self.deck.KEY_ROWS) or not (0 <= col < self.deck.KEY_COLS):
            raise IndexError("Invalid row or column")
        return self.image_board[row][col]

    def get_image_board(self) -> list[list[bytes | None]]:
        """Return a copy of the internal image board."""
        if self.image_board is None:
            raise ValueError("Image board not initialised")
        return [list(r) for r in self.image_board]

    def refresh_image_board(self) -> None:
        """Redraw the internal image board on the deck."""
        if self.image_board is not None:
            self.display_image_board(self.image_board)

    def overlay_image_board(
        self, board: list[list[bytes | None]], top: int = 0, left: int = 0
    ) -> None:
        """Overlay ``board`` onto the internal image board at ``(top, left)``."""
        if self.image_board is None:
            self.create_image_board()

        for r, row_data in enumerate(board):
            for c, image in enumerate(row_data):
                rr = top + r
                cc = left + c
                if 0 <= rr < self.deck.KEY_ROWS and 0 <= cc < self.deck.KEY_COLS:
                    self.image_board[rr][cc] = image
                    if self.deck.is_visual():
                        self.deck.set_key_image(self.position_to_key(rr, cc), image)

    def scroll_image_board(self, dx: int = 0, dy: int = 0, fill: bytes | None = None) -> None:
        """Scroll the image board by ``(dx, dy)`` and fill empty cells with ``fill``."""
        if self.image_board is None:
            self.create_image_board(fill)
            return

        new_board = [
            [fill for _ in range(self.deck.KEY_COLS)] for _ in range(self.deck.KEY_ROWS)
        ]

        for r in range(self.deck.KEY_ROWS):
            for c in range(self.deck.KEY_COLS):
                nr = r + dy
                nc = c + dx
                if 0 <= nr < self.deck.KEY_ROWS and 0 <= nc < self.deck.KEY_COLS:
                    new_board[nr][nc] = self.image_board[r][c]

        self.image_board = new_board
        self.refresh_image_board()

    def display_deck_image(
        self, image: Image.Image, key_spacing: tuple[int, int] = (0, 0)
    ) -> None:
        """Display ``image`` scaled across the entire deck surface.

        The image will be automatically resized to fit the deck and then
        split into per-key tiles before being sent to the device. The
        ``image_board`` state is updated so that the displayed graphics can be
        further manipulated with the other image board helpers.

        Parameters
        ----------
        image
            Source PIL image to display.
        key_spacing
            Horizontal and vertical pixel spacing between keys, used when
            computing the deck surface size.
        """

        if not self.deck.is_visual():
            return

        deck_img = PILHelper.create_deck_sized_image(self.deck, image, key_spacing)
        tiles = PILHelper.split_deck_image(self.deck, deck_img, key_spacing)

        board: list[list[bytes | None]] = []
        for r in range(self.deck.KEY_ROWS):
            row_imgs: list[bytes | None] = []
            for c in range(self.deck.KEY_COLS):
                key = self.position_to_key(r, c)
                tile = tiles[key]
                self.deck.set_key_image(key, tile)
                row_imgs.append(tile)
            board.append(row_imgs)

        self.image_board = board

    def wait_for_char_press(
        self, char_map: dict[int, str], timeout: float | None = None
    ) -> str | None:
        """Wait for a key press and return the mapped character or ``None``."""
        key = self.wait_for_key_press(timeout)
        if key is None:
            return None
        return char_map.get(key)

    def wait_for_board_press(self, timeout: float | None = None) -> str | None:
        """Wait for a key press and return the character shown on the key."""
        if self.board is None:
            raise ValueError("Board not initialised")

        char_map: dict[int, str] = {}
        for r, row in enumerate(self.board):
            for c, char in enumerate(row):
                char_map[self.position_to_key(r, c)] = char

        return self.wait_for_char_press(char_map, timeout)

    def run_loop(
        self,
        frame_callback: Callable[["MacroDeck", float], bool] | None = None,
        fps: int = 30,
    ) -> None:
        """Run a simple blocking game loop using the deck."""
        frame_time = 1.0 / max(fps, 1)
        self._loop_running = True
        last = time.time()
        self.deck.open()
        try:
            while self._loop_running:
                now = time.time()
                delta = now - last
                last = now
                if frame_callback is not None:
                    if frame_callback(self, delta) is False:
                        break
                sleep_time = frame_time - (time.time() - now)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        finally:
            self._loop_running = False
            self.deck.close()

    def stop_loop(self) -> None:
        """Terminate a running game loop started with :func:`run_loop`."""
        self._loop_running = False

    # Internal handlers ---------------------------------------------------
    def _run_action(self, action: Callable | str, *args: Any) -> None:
        if not self.enabled:
            return

        if isinstance(action, str):
            subprocess.Popen(action, shell=True)
        else:
            action(*args)

    # Internal helpers ---------------------------------------------------
    def _build_image(self, path: str | None, text: str | None) -> bytes | None:
        if path is None and text is None:
            return None

        if path is not None:
            image = Image.open(path).convert("RGBA")
            image = PILHelper.create_scaled_key_image(self.deck, image)
        else:
            image = PILHelper.create_key_image(self.deck)

        if text:
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()
            draw.text((image.width / 2, image.height / 2), text=text, anchor="mm", fill="white", font=font)

        return PILHelper.to_native_key_format(self.deck, image)

    def _handle_key(self, deck: StreamDeck, key: int, state: bool) -> None:
        config = self.key_configs.get(key)
        if config:
            if state and config.get("down_image") is not None:
                deck.set_key_image(key, config["down_image"])
            elif not state and config.get("up_image") is not None:
                deck.set_key_image(key, config["up_image"])

        if state:
            action = self.key_macros.get(key)
            if action is not None:
                self._run_action(action)

    def _handle_dial(self, deck: StreamDeck, dial: int, event: DialEventType, value: Any) -> None:
        action = self.dial_macros.get((dial, event))
        if action is not None:
            self._run_action(action, value)

    def _handle_touch(self, deck: StreamDeck, event: TouchscreenEventType, data: Any) -> None:
        action = self.touch_macros.get(event)
        if action is not None:
            self._run_action(action, data)

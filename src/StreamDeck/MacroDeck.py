#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#
"""Simple macro framework for StreamDeck devices."""

import subprocess
from collections.abc import Callable
from typing import Any
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

        self.deck.set_key_callback(self._handle_key)
        self.deck.set_dial_callback(self._handle_dial)
        self.deck.set_touchscreen_callback(self._handle_touch)

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

    # Internal handlers ---------------------------------------------------
    def _run_action(self, action: Callable | str, *args: Any) -> None:
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

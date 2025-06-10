#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#
"""Game framework helpers for StreamDeck devices."""

from __future__ import annotations

import threading
import time

from PIL import Image

from .ImageHelpers import PILHelper
from .Devices.StreamDeck import StreamDeck


class KeyFrameBuffer:
    """Simple framebuffer treating each key as a pixel cell."""

    def __init__(self, deck: StreamDeck, background: str = "black") -> None:
        self.deck = deck
        self.background = background

    def index(self, x: int, y: int) -> int:
        return y * self.deck.KEY_COLS + x

    def clear(self, color: str | None = None) -> None:
        color = self.background if color is None else color
        for key in range(self.deck.KEY_COUNT):
            img = PILHelper.create_key_image(self.deck, background=color)
            self.deck.set_key_image(key, PILHelper.to_native_key_format(self.deck, img))

    def set_key_image(self, x: int, y: int, image: Image.Image) -> None:
        key = self.index(x, y)
        native = PILHelper.to_native_key_format(self.deck, image)
        self.deck.set_key_image(key, native)

    def set_key_color(self, x: int, y: int, color: str) -> None:
        img = PILHelper.create_key_image(self.deck, background=color)
        self.set_key_image(x, y, img)


class Sprite:
    """Sprite representing an image at a fixed key position."""

    def __init__(self, image: Image.Image, x: int, y: int) -> None:
        self.image = image
        self.x = x
        self.y = y

    def draw(self, fb: KeyFrameBuffer) -> None:
        fb.set_key_image(self.x, self.y, self.image)


class Game:
    """Base class for StreamDeck games."""

    def __init__(self, deck: StreamDeck, fps: int = 20) -> None:
        self.deck = deck
        self.fps = fps
        self.running = False
        self.framebuffer = KeyFrameBuffer(deck)
        self._thread: threading.Thread | None = None
        self.deck.set_key_callback(self._handle_key)

    # Game lifecycle ------------------------------------------------------
    def start(self) -> None:
        """Start the game loop in a background thread."""
        if self.running:
            return
        self.running = True
        self.deck.open()
        self.framebuffer.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the game loop."""
        self.running = False
        if self._thread is not None:
            self._thread.join()
            self._thread = None
        self.framebuffer.clear()
        self.deck.close()

    # Overridables --------------------------------------------------------
    def update(self, delta: float) -> None:
        """Update game state."""

    def render(self, fb: KeyFrameBuffer) -> None:
        """Draw a frame to the framebuffer."""

    def on_key(self, x: int, y: int, pressed: bool) -> None:
        """Handle key events."""

    # Internal helpers ----------------------------------------------------
    def _loop(self) -> None:
        last = time.time()
        while self.running:
            now = time.time()
            delta = now - last
            last = now
            self.update(delta)
            self.render(self.framebuffer)
            sleep_time = max(0.0, (1.0 / self.fps) - (time.time() - now))
            time.sleep(sleep_time)
        self.framebuffer.clear()

    def _handle_key(self, deck: StreamDeck, key: int, state: bool) -> None:
        x = key % self.deck.KEY_COLS
        y = key // self.deck.KEY_COLS
        self.on_key(x, y, state)

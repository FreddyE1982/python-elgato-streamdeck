#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#
"""Hot-plug detection utilities for StreamDeck devices."""

import threading
import time
from collections.abc import Callable

from .DeviceManager import DeviceManager
from .Devices.StreamDeck import StreamDeck


class DeviceMonitor:
    """Monitor StreamDeck connections and disconnections."""

    def __init__(self, manager: DeviceManager, interval: float = 1.0):
        self.manager = manager
        self.interval = interval
        self._running = False
        self._thread: threading.Thread | None = None
        self._known: dict[str, StreamDeck] = {}
        self.on_connect: Callable[[StreamDeck], None] | None = None
        self.on_disconnect: Callable[[StreamDeck], None] | None = None

    def start(self, on_connect: Callable[[StreamDeck], None] | None = None,
              on_disconnect: Callable[[StreamDeck], None] | None = None) -> None:
        """Start monitoring for device changes."""
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self._known = {d.id(): d for d in self.manager.enumerate()}
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop monitoring."""
        self._running = False
        if self._thread is not None:
            self._thread.join()
            self._thread = None

    # Internal methods ---------------------------------------------------
    def _run(self) -> None:
        while self._running:
            current = {d.id(): d for d in self.manager.enumerate()}

            new_ids = set(current.keys()) - set(self._known.keys())
            removed_ids = set(self._known.keys()) - set(current.keys())

            for device_id in new_ids:
                if self.on_connect:
                    self.on_connect(current[device_id])
            for device_id in removed_ids:
                if self.on_disconnect:
                    self.on_disconnect(self._known[device_id])

            self._known = current
            time.sleep(self.interval)

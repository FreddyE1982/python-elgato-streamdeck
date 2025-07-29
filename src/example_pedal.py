#!/usr/bin/env python3

#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

"""Demonstrate handling key events from a Stream Deck Pedal."""

import logging
import threading

from StreamDeck.Devices.StreamDeck import StreamDeck

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Transport.Transport import TransportError


def key_change_callback(deck: StreamDeck, key: int, state: bool) -> None:
    logging.info(
        "Deck %s Key %s = %s",
        deck.id(),
        key,
        "down" if state else "up",
    )


if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    logging.info("Found %s Stream Deck(s).", len(streamdecks))

    for index, deck in enumerate(streamdecks):
        deck.open()

        logging.info(
            "Opened '%s' device (serial number: '%s', fw: '%s')",
            deck.deck_type(),
            deck.get_serial_number(),
            deck.get_firmware_version(),
        )

        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)

        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            try:
                t.join()
            except (TransportError, RuntimeError):
                pass

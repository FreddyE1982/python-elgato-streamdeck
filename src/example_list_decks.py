#!/usr/bin/env python3

#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#
"""List all connected Stream Deck devices."""

import logging

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck


def list_decks() -> None:
    """Enumerate devices and print basic information."""
    manager = DeviceManager()
    decks: list[StreamDeck] = manager.enumerate()
    logging.info("Found %s Stream Deck(s).", len(decks))
    for deck in decks:
        deck.open()
        logging.info(
            "%s: %s (serial: %s, fw: %s)",
            deck.id(),
            deck.deck_type(),
            deck.get_serial_number(),
            deck.get_firmware_version(),
        )
        deck.close()


if __name__ == "__main__":
    list_decks()

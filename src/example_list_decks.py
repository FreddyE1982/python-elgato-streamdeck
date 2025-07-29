#!/usr/bin/env python3

#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#
"""List all connected Stream Deck devices."""

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck


def list_decks() -> None:
    """Enumerate devices and print basic information."""
    manager = DeviceManager()
    decks: list[StreamDeck] = manager.enumerate()
    print(f"Found {len(decks)} Stream Deck(s).\n")
    for deck in decks:
        deck.open()
        print(
            f"{deck.id()}: {deck.deck_type()} "
            f"(serial: {deck.get_serial_number()}, fw: {deck.get_firmware_version()})"
        )
        deck.close()


if __name__ == "__main__":
    list_decks()

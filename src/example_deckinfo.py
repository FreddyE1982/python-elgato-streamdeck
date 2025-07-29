#!/usr/bin/env python3

#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

"""Enumerate connected devices and print their information."""

import logging

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck


# Prints diagnostic information about a given StreamDeck.
def print_deck_info(index: int, deck: StreamDeck) -> None:
    key_image_format = deck.key_image_format()
    touchscreen_image_format = deck.touchscreen_image_format()

    flip_description = {
        (False, False): "not mirrored",
        (True, False): "mirrored horizontally",
        (False, True): "mirrored vertically",
        (True, True): "mirrored horizontally/vertically",
    }

    logging.info("Deck %s - %s.", index, deck.deck_type())
    logging.info("\t - ID: %s", deck.id())
    logging.info("\t - Serial: '%s'", deck.get_serial_number())
    logging.info("\t - Firmware Version: '%s'", deck.get_firmware_version())
    logging.info(
        "\t - Key Count: %s (in a %sx%s grid)",
        deck.key_count(),
        deck.key_layout()[0],
        deck.key_layout()[1],
    )
    if deck.is_visual():
        logging.info(
            "\t - Key Images: %sx%s pixels, %s format, rotated %s degrees, %s",
            key_image_format["size"][0],
            key_image_format["size"][1],
            key_image_format["format"],
            key_image_format["rotation"],
            flip_description[key_image_format["flip"]],
        )

        if deck.is_touch():
            logging.info(
                "\t - Touchscreen: %sx%s pixels, %s format, rotated %s degrees, %s",
                touchscreen_image_format["size"][0],
                touchscreen_image_format["size"][1],
                touchscreen_image_format["format"],
                touchscreen_image_format["rotation"],
                flip_description[touchscreen_image_format["flip"]],
            )
    else:
        logging.info("\t - No Visual Output")


if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    logging.info("Found %s Stream Deck(s).", len(streamdecks))

    for index, deck in enumerate(streamdecks):
        deck.open()
        deck.reset()

        print_deck_info(index, deck)

        deck.close()

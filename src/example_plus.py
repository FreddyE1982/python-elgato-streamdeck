#!/usr/bin/env python3

#         Python Stream Deck Library
#      Released under the MIT license
#
#

"""Showcase Stream Deck Plus specific functions."""

import os
import threading
import io
import logging

from PIL import Image
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import (
    DialEventType,
    TouchscreenEventType,
    StreamDeck,
)
from StreamDeck.Transport.Transport import TransportError

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")

# image for idle state
img = Image.new("RGB", (120, 120), color="black")
released_icon = Image.open(os.path.join(ASSETS_PATH, "Released.png")).resize((80, 80))
img.paste(released_icon, (20, 20), released_icon)

img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format="JPEG")
img_released_bytes = img_byte_arr.getvalue()

# image for pressed state
img = Image.new("RGB", (120, 120), color="black")
pressed_icon = Image.open(os.path.join(ASSETS_PATH, "Pressed.png")).resize((80, 80))
img.paste(pressed_icon, (20, 20), pressed_icon)

img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format="JPEG")
img_pressed_bytes = img_byte_arr.getvalue()


# callback when buttons are pressed or released
def key_change_callback(deck: StreamDeck, key: int, key_state: bool) -> None:
    logging.info("Key: %s state: %s", key, key_state)

    deck.set_key_image(key, img_pressed_bytes if key_state else img_released_bytes)


# callback when dials are pressed or released
def dial_change_callback(
    deck: StreamDeck, dial: int, event: DialEventType, value: int
) -> None:
    if event == DialEventType.PUSH:
        logging.info("dial pushed: %s state: %s", dial, value)
        if dial == 3 and value:
            deck.reset()
            deck.close()
        else:
            # build an image for the touch lcd
            img = Image.new("RGB", (800, 100), "black")
            icon = Image.open(os.path.join(ASSETS_PATH, "Exit.png")).resize((80, 80))
            img.paste(icon, (690, 10), icon)

            for k in range(0, deck.DIAL_COUNT - 1):
                img.paste(
                    pressed_icon if (dial == k and value) else released_icon,
                    (30 + (k * 220), 10),
                    pressed_icon if (dial == k and value) else released_icon,
                )

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="JPEG")
            img_byte_arr = img_byte_arr.getvalue()

            deck.set_touchscreen_image(img_byte_arr, 0, 0, 800, 100)
    elif event == DialEventType.TURN:
        logging.info("dial %s turned: %s", dial, value)


# callback when lcd is touched
def touchscreen_event_callback(
    deck: StreamDeck, evt_type: TouchscreenEventType, value: dict[str, int]
) -> None:
    if evt_type == TouchscreenEventType.SHORT:
        logging.info("Short touch @ %s,%s", value["x"], value["y"])

    elif evt_type == TouchscreenEventType.LONG:

        logging.info("Long touch @ %s,%s", value["x"], value["y"])

    elif evt_type == TouchscreenEventType.DRAG:

        logging.info(
            "Drag started @ %s,%s ended @ %s,%s",
            value["x"],
            value["y"],
            value["x_out"],
            value["y_out"],
        )


if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    logging.info("Found %s Stream Deck(s).", len(streamdecks))

    for index, deck in enumerate(streamdecks):
        # This example only works with devices that have screens.

        if deck.DECK_TYPE != "Stream Deck +":
            logging.warning(deck.DECK_TYPE)
            logging.warning("Sorry, this example only works with Stream Deck +")
            continue

        deck.open()
        deck.reset()

        deck.set_key_callback(key_change_callback)
        deck.set_dial_callback(dial_change_callback)
        deck.set_touchscreen_callback(touchscreen_event_callback)

        logging.info(
            "Opened '%s' device (serial number: '%s')",
            deck.deck_type(),
            deck.get_serial_number(),
        )

        # Set initial screen brightness to 30%.
        deck.set_brightness(100)

        for key in range(0, deck.KEY_COUNT):
            deck.set_key_image(key, img_released_bytes)

        # build an image for the touch lcd
        img = Image.new("RGB", (800, 100), "black")
        icon = Image.open(os.path.join(ASSETS_PATH, "Exit.png")).resize((80, 80))
        img.paste(icon, (690, 10), icon)

        for dial in range(0, deck.DIAL_COUNT - 1):
            img.paste(released_icon, (30 + (dial * 220), 10), released_icon)

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        touchscreen_image_bytes = img_bytes.getvalue()

        deck.set_touchscreen_image(touchscreen_image_bytes, 0, 0, 800, 100)

        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            try:
                t.join()
            except (TransportError, RuntimeError):
                pass

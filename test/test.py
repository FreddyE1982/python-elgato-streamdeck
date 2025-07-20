#!/usr/bin/env python3

#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from PIL import ImageDraw
from StreamDeck.MacroDeck import MacroDeck


def test_pil_helpers(deck):
    if not deck.is_visual():
        return

    test_key_image_pil = PILHelper.create_key_image(deck)
    test_scaled_key_image_pil = PILHelper.create_scaled_key_image(deck, test_key_image_pil)     # noqa: F841
    test_key_image_native = PILHelper.to_native_key_format(deck, test_scaled_key_image_pil)     # noqa: F841

    if deck.is_touch():
        test_touchscreen_image_pil = PILHelper.create_touchscreen_image(deck)
        test_scaled_touchscreen_image_pil = PILHelper.create_scaled_touchscreen_image(deck, test_touchscreen_image_pil)     # noqa: F841
        test_touchscreen_image_native = PILHelper.to_native_touchscreen_format(deck, test_scaled_touchscreen_image_pil)     # noqa: F841


def test_basic_apis(deck):
    with deck:
        deck.open()

        connected = deck.connected()     # noqa: F841
        deck_id = deck.id()     # noqa: F841
        key_count = deck.key_count()     # noqa: F841
        vendor_id = deck.vendor_id()     # noqa: F841
        product_id = deck.product_id()     # noqa: F841
        deck_type = deck.deck_type()     # noqa: F841
        key_layout = deck.key_layout()     # noqa: F841
        key_image_format = deck.key_image_format() if deck.is_visual() else None     # noqa: F841
        key_states = deck.key_states()     # noqa: F841
        dial_states = deck.dial_states()     # noqa: F841
        touchscreen_image_format = deck.touchscreen_image_format() if deck.is_touch() else None     # noqa: F841

        deck.set_key_callback(None)
        deck.reset()

        if deck.is_visual():
            deck.set_brightness(30)

            test_key_image_pil = PILHelper.create_key_image(deck)
            test_key_image_native = PILHelper.to_native_key_format(deck, test_key_image_pil)
            deck.set_key_image(0, None)
            deck.set_key_image(0, test_key_image_native)

            if deck.is_touch():
                test_touchscreen_image_pil = PILHelper.create_touchscreen_image(deck)
                test_touchscreen_image_native = PILHelper.to_native_touchscreen_format(deck, test_touchscreen_image_pil)
                deck.set_touchscreen_image(None)
                deck.set_touchscreen_image(test_touchscreen_image_native, 0, 0, test_touchscreen_image_pil.width, test_touchscreen_image_pil.height)

        deck.close()


def test_key_pattern(deck):
    if not deck.is_visual():
        return

    test_key_image = PILHelper.create_key_image(deck)

    draw = ImageDraw.Draw(test_key_image)
    draw.rectangle((0, 0) + test_key_image.size, fill=(0x11, 0x22, 0x33), outline=(0x44, 0x55, 0x66))

    test_key_image = PILHelper.to_native_key_format(deck, test_key_image)

    with deck:
        deck.open()
        deck.set_key_image(0, test_key_image)
        deck.close()


def test_macrodeck_enable_disable(deck):
    if not deck.is_visual():
        return

    macro_results = []

    def sample_action():
        macro_results.append(1)

    mdeck = MacroDeck(deck)
    mdeck.register_key_macro(0, sample_action)

    # Disable and ensure action does not run
    mdeck.disable()
    mdeck._handle_key(deck, 0, True)
    assert len(macro_results) == 0

    # Enable and ensure action runs
    mdeck.enable()
    mdeck._handle_key(deck, 0, True)
    assert macro_results == [1]


def test_run_loop(deck):
    if not deck.is_visual():
        return

    mdeck = MacroDeck(deck)
    frame_counter = []

    def frame(md, dt):
        frame_counter.append(dt)
        if len(frame_counter) >= 2:
            md.stop_loop()
            return False
        return True

    with deck:
        deck.open()
        mdeck.run_loop(frame, fps=10)
        deck.close()
    assert len(frame_counter) >= 2


def test_set_key_text(deck):
    if not deck.is_visual():
        return

    mdeck = MacroDeck(deck)
    with deck:
        deck.open()
        mdeck.set_key_text(0, "X")
        deck.close()
    assert 0 in mdeck.key_configs


def test_display_text_and_wait(deck):
    if not deck.is_visual():
        return

    mdeck = MacroDeck(deck)
    with deck:
        deck.open()
        mdeck.display_text(["AB"])
        pressed = mdeck.wait_for_key_press(timeout=0)
        deck.close()
    assert 0 in mdeck.key_configs and 1 in mdeck.key_configs
    assert pressed is None


def test_game_helpers(deck):
    if not deck.is_visual():
        return

    mdeck = MacroDeck(deck)
    board = [["X" for _ in range(deck.KEY_COLS)] for _ in range(deck.KEY_ROWS)]

    with deck:
        deck.open()
        mdeck.display_board(board)
        mdeck.draw_text(0, 0, "HI")
        mdeck.overlay_board([["Z"]], top=1, left=1)
        pos = mdeck.key_to_position(0)
        idx = mdeck.position_to_key(*pos)
        char = mdeck.wait_for_char_press({0: "A"}, timeout=0)
        deck.close()

    assert idx == 0
    assert char is None


def test_board_state(deck):
    if not deck.is_visual():
        return

    mdeck = MacroDeck(deck)
    with deck:
        deck.open()
        mdeck.create_board()
        mdeck.set_board_char(0, 0, "A")
        char = mdeck.get_board_char(0, 0)
        board = mdeck.get_board()
        mdeck.refresh_board()
        deck.close()

    assert char == "A"
    assert board[0][0] == "A"


def test_board_draw_scroll(deck):
    if not deck.is_visual():
        return

    mdeck = MacroDeck(deck)
    with deck:
        deck.open()
        mdeck.create_board()
        mdeck.fill_rect(0, 0, 2, 2, "A")
        mdeck.draw_rect(0, 0, 2, 2, "B")
        mdeck.scroll_board(1, 1)
        deck.close()

    assert mdeck.get_board_char(1, 1) == "B"


def test_draw_line(deck):
    if not deck.is_visual():
        return

    mdeck = MacroDeck(deck)
    with deck:
        deck.open()
        mdeck.create_board()
        mdeck.draw_line(0, 0, deck.KEY_ROWS - 1, deck.KEY_COLS - 1, "C")
        deck.close()

    assert mdeck.get_board_char(deck.KEY_ROWS - 1, deck.KEY_COLS - 1) == "C"


def test_board_string_helpers(deck):
    if not deck.is_visual():
        return

    mdeck = MacroDeck(deck)
    with deck:
        deck.open()
        mdeck.create_board_from_strings(["AB", "CD"])
        lines = mdeck.get_board_as_strings()
        mdeck.draw_multiline_text(0, 0, ["XY", "Z"])
        deck.close()

    assert lines[0].startswith("AB")
    assert mdeck.get_board_char(1, 0) == "Z"


def test_image_board(deck):
    if not deck.is_visual():
        return

    mdeck = MacroDeck(deck)
    img = PILHelper.to_native_key_format(deck, PILHelper.create_key_image(deck))
    board = [[img for _ in range(deck.KEY_COLS)] for _ in range(deck.KEY_ROWS)]

    with deck:
        deck.open()
        mdeck.create_image_board()
        mdeck.set_board_image(0, 0, img)
        stored = mdeck.get_board_image(0, 0)
        mdeck.display_image_board(board)
        mdeck.scroll_image_board(1, 0)
        deck.close()

    assert stored == img


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)

    parser = argparse.ArgumentParser(description="StreamDeck Library test.")
    parser.add_argument("--model", help="Stream Deck model name to test")
    parser.add_argument("--test", help="Stream Deck test to run")
    args = parser.parse_args()

    manager = DeviceManager(transport="dummy")
    streamdecks = manager.enumerate()

    test_streamdecks = streamdecks
    if args.model:
        test_streamdecks = [deck for deck in test_streamdecks if deck.deck_type() == args.model]

    if len(test_streamdecks) == 0:
        logging.error("Error: No Stream Decks to test. Known models: {}".format([d.deck_type() for d in streamdecks]))
        sys.exit(1)

    tests = {
        "PIL Helpers": test_pil_helpers,
        "Basic APIs": test_basic_apis,
        "Key Pattern": test_key_pattern,
        "MacroDeck Enable": test_macrodeck_enable_disable,
        "Run Loop": test_run_loop,
        "Set Key Text": test_set_key_text,
        "Display Text": test_display_text_and_wait,
        "Game Helpers": test_game_helpers,
        "Board State": test_board_state,
        "Board Draw": test_board_draw_scroll,
        "Draw Line": test_draw_line,
        "Board Strings": test_board_string_helpers,
        "Image Board": test_image_board,
    }

    test_runners = tests
    if args.test:
        test_runners = {name: test for (name, test) in test_runners.items() if name == args.test}

    if len(test_runners) == 0:
        logging.error("Error: No Stream Decks tests to run. Known tests: {}".format([name for name, test in tests.items()]))
        sys.exit(1)

    for deck_index, deck in enumerate(test_streamdecks):
        logging.info("Using Deck Type: {}".format(deck.deck_type()))

        for name, test in test_runners.items():
            logging.info("Running Test: {}".format(name))
            test(deck)
            logging.info("Finished Test: {}".format(name))

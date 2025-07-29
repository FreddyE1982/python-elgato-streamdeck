#!/usr/bin/env python3

#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from StreamDeck.ImageHelpers import PILHelper
from PIL import ImageDraw
from StreamDeck.MacroDeck import MacroDeck


def test_pil_helpers(deck):
    if not deck.is_visual():
        return

    test_key_image_pil = PILHelper.create_key_image(deck)
    _test_scaled_key_image_pil = PILHelper.create_scaled_key_image(
        deck, test_key_image_pil
    )
    _test_key_image_native = PILHelper.to_native_key_format(
        deck, _test_scaled_key_image_pil
    )

    if deck.is_touch():
        test_touchscreen_image_pil = PILHelper.create_touchscreen_image(deck)
        _test_scaled_touchscreen_image_pil = PILHelper.create_scaled_touchscreen_image(
            deck, test_touchscreen_image_pil
        )
        _test_touchscreen_image_native = PILHelper.to_native_touchscreen_format(
            deck, _test_scaled_touchscreen_image_pil
        )


def test_basic_apis(deck):
    with deck:
        deck.open()

        connected = deck.connected()  # noqa: F841
        deck_id = deck.id()  # noqa: F841
        _key_count = deck.key_count()
        _vendor_id = deck.vendor_id()
        _product_id = deck.product_id()
        _deck_type = deck.deck_type()
        _key_layout = deck.key_layout()
        _key_image_format = deck.key_image_format() if deck.is_visual() else None
        _key_states = deck.key_states()
        _dial_states = deck.dial_states()
        _touchscreen_image_format = (
            deck.touchscreen_image_format() if deck.is_touch() else None
        )

        deck.set_key_callback(None)
        deck.reset()

        if deck.is_visual():
            deck.set_brightness(30)

            test_key_image_pil = PILHelper.create_key_image(deck)
            test_key_image_native = PILHelper.to_native_key_format(
                deck, test_key_image_pil
            )
            deck.set_key_image(0, None)
            deck.set_key_image(0, test_key_image_native)

            if deck.is_touch():
                test_touchscreen_image_pil = PILHelper.create_touchscreen_image(deck)
                test_touchscreen_image_native = PILHelper.to_native_touchscreen_format(
                    deck, test_touchscreen_image_pil
                )
                deck.set_touchscreen_image(None)
                deck.set_touchscreen_image(
                    test_touchscreen_image_native,
                    0,
                    0,
                    test_touchscreen_image_pil.width,
                    test_touchscreen_image_pil.height,
                )

        deck.close()


def test_key_pattern(deck):
    if not deck.is_visual():
        return

    test_key_image = PILHelper.create_key_image(deck)

    draw = ImageDraw.Draw(test_key_image)
    draw.rectangle(
        (0, 0) + test_key_image.size,
        fill=(0x11, 0x22, 0x33),
        outline=(0x44, 0x55, 0x66),
    )

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


def test_deck_image_helpers(deck):
    if not deck.is_visual():
        return

    src = PILHelper.create_key_image(deck)
    deck_img = PILHelper.create_deck_sized_image(deck, src)
    tiles = PILHelper.split_deck_image(deck, deck_img)

    assert len(tiles) == deck.key_count()
    assert isinstance(next(iter(tiles.values())), bytes)


def test_display_deck_image(deck):
    if not deck.is_visual():
        return

    mdeck = MacroDeck(deck)
    img = PILHelper.create_key_image(deck)
    deck_img = PILHelper.create_deck_sized_image(deck, img)

    with deck:
        deck.open()
        mdeck.display_deck_image(deck_img)
        deck.close()

    assert mdeck.image_board is not None


def test_key_image_helpers(deck):
    if not deck.is_visual():
        return

    mdeck = MacroDeck(deck)
    img = PILHelper.to_native_key_format(deck, PILHelper.create_key_image(deck))

    with deck:
        deck.open()
        mdeck.set_key_image_bytes(0, img)
        stored = mdeck.get_key_image(0)
        has = mdeck.has_key_image(0)
        mdeck.copy_key_image(0, 1)
        copied = mdeck.get_key_image(1)
        mdeck.move_key_image(1, 2)
        moved = mdeck.get_key_image(2)
        moved_from = mdeck.get_key_image(1)
        img2 = PILHelper.to_native_key_format(deck, PILHelper.create_key_image(deck))
        mdeck.set_key_image_bytes(3, img2)
        mdeck.swap_key_images(2, 3)
        swapped_a = mdeck.get_key_image(2)
        swapped_b = mdeck.get_key_image(3)
        mdeck.clear_key_image(0)
        deck.close()

    assert stored == img
    assert has
    assert copied == img
    assert moved == img
    assert moved_from is None
    assert swapped_a == img2
    assert swapped_b == img
    assert mdeck.get_key_image(0) is None

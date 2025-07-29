#!/usr/bin/env python3
"""Run StreamDeck tests from the command line."""
import argparse
import logging
import sys

from StreamDeck.DeviceManager import DeviceManager
from test.test_streamdeck import (
    test_pil_helpers,
    test_basic_apis,
    test_key_pattern,
    test_macrodeck_enable_disable,
    test_run_loop,
    test_set_key_text,
    test_display_text_and_wait,
    test_game_helpers,
    test_board_state,
    test_board_draw_scroll,
    test_draw_line,
    test_board_string_helpers,
    test_image_board,
    test_deck_image_helpers,
    test_display_deck_image,
    test_key_image_helpers,
)


def main() -> None:
    """Entry point for the command line test runner."""
    logging.basicConfig(level=logging.ERROR)
    parser = argparse.ArgumentParser(description="StreamDeck Library test.")
    parser.add_argument("--model", help="Stream Deck model name to test")
    parser.add_argument("--test", help="Stream Deck test to run")
    args = parser.parse_args()

    manager = DeviceManager(transport="dummy")
    streamdecks = manager.enumerate()

    test_streamdecks = streamdecks
    if args.model:
        test_streamdecks = [d for d in test_streamdecks if d.deck_type() == args.model]

    if not test_streamdecks:
        logging.error(
            "Error: No Stream Decks to test. Known models: %s",
            [d.deck_type() for d in streamdecks],
        )
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
        "Deck Image Helpers": test_deck_image_helpers,
        "Display Deck Image": test_display_deck_image,
        "Key Image Helpers": test_key_image_helpers,
    }

    test_runners = tests
    if args.test:
        test_runners = {n: t for n, t in test_runners.items() if n == args.test}

    if not test_runners:
        logging.error(
            "Error: No Stream Decks tests to run. Known tests: %s", list(tests)
        )
        sys.exit(1)

    for deck in test_streamdecks:
        logging.info("Using Deck Type: %s", deck.deck_type())
        for name, test in test_runners.items():
            logging.info("Running Test: %s", name)
            test(deck)
            logging.info("Finished Test: %s", name)


if __name__ == "__main__":
    main()

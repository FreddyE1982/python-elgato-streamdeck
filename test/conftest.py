import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from StreamDeck.DeviceManager import DeviceManager


@pytest.fixture(scope="module")
def deck():
    manager = DeviceManager(transport="dummy")
    decks = manager.enumerate()
    if not decks:
        pytest.skip("No dummy StreamDecks available")
    return decks[0]

import time
from unittest import mock
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.DeviceMonitor import DeviceMonitor
from StreamDeck.MacroDeck import MacroDeck, DialEventType, TouchscreenEventType


def test_device_manager_enumeration():
    manager = DeviceManager(transport="dummy")
    decks = manager.enumerate()
    assert len(decks) > 0
    assert all(hasattr(d, "open") for d in decks)


def test_macrodeck_macro_management(deck):
    mdeck = MacroDeck(deck)

    action = lambda: None
    mdeck.register_key_macro(0, action)
    assert mdeck.get_key_macro(0) is action
    assert mdeck.macro_keys() == [0]

    mdeck.update_key_macro(0, None)
    assert mdeck.get_key_macro(0) is None

    mdeck.update_key_macro(1, action)
    assert mdeck.get_key_macro(1) is action

    mdeck.register_dial_macro(0, DialEventType.PUSH, action)
    assert mdeck.get_dial_macro(0, DialEventType.PUSH) is action
    mdeck.update_dial_macro(0, DialEventType.PUSH, None)
    assert mdeck.get_dial_macro(0, DialEventType.PUSH) is None

    mdeck.register_touch_macro(TouchscreenEventType.SHORT, action)
    assert mdeck.get_touch_macro(TouchscreenEventType.SHORT) is action
    mdeck.update_touch_macro(TouchscreenEventType.SHORT, None)
    assert mdeck.get_touch_macro(TouchscreenEventType.SHORT) is None


def test_macrodeck_copy_move_swap_macros(deck):
    mdeck = MacroDeck(deck)

    a = lambda: None
    b = lambda: None
    mdeck.register_key_macro(0, a)
    mdeck.copy_key_macro(0, 1)
    assert mdeck.get_key_macro(1) is a

    mdeck.move_key_macro(1, 2)
    assert mdeck.get_key_macro(2) is a
    assert mdeck.get_key_macro(1) is None

    mdeck.register_key_macro(0, b)
    mdeck.swap_key_macros(0, 2)
    assert mdeck.get_key_macro(0) is a
    assert mdeck.get_key_macro(2) is b


def test_position_key_conversion(deck):
    mdeck = MacroDeck(deck)
    for key in range(deck.key_count()):
        row, col = mdeck.key_to_position(key)
        assert mdeck.position_to_key(row, col) == key

    with pytest.raises(IndexError):
        mdeck.position_to_key(-1, 0)
    with pytest.raises(IndexError):
        mdeck.key_to_position(deck.key_count())


def test_device_monitor_callbacks():
    manager = DeviceManager(transport="dummy")
    decks = manager.enumerate()
    dev1, dev2 = decks[0], decks[1]

    sequence = [[dev1], [dev1, dev2], [dev2], [dev2]]
    enum_iter = iter(sequence)

    def side_effect():
        try:
            return next(enum_iter)
        except StopIteration:
            return sequence[-1]

    with mock.patch.object(manager, "enumerate", side_effect=side_effect):
        monitor = DeviceMonitor(manager, interval=0.01)
        connected, disconnected = [], []
        monitor.start(connected.append, disconnected.append)
        time.sleep(0.05)
        monitor.stop()

    assert connected == [dev2]
    assert disconnected == [dev1]

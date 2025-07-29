import time
from unittest import mock
import os
import sys
import logging
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.DeviceMonitor import DeviceMonitor
from StreamDeck.MacroDeck import MacroDeck, DialEventType, TouchscreenEventType


def test_device_manager_enumeration():
    manager = DeviceManager(transport="dummy")
    decks = manager.enumerate()
    assert len(decks) > 0
    assert all(hasattr(d, "open") for d in decks)


def test_dummy_transport_logs(caplog):
    from StreamDeck.Transport.Dummy import Dummy

    caplog.set_level(logging.INFO)
    device = Dummy.Device(vid=1, pid=1)
    with caplog.at_level(logging.INFO):
        device.open()
        device.write_feature(b"\x00\x01")
        device.close()

    assert "Deck opened" in caplog.text
    assert "Deck feature write" in caplog.text
    assert "Deck closed" in caplog.text


def test_macrodeck_macro_management(deck):
    mdeck = MacroDeck(deck)

    def action():
        pass

    mdeck.register_key_macro(0, action)
    assert mdeck.get_key_macro(0) is action
    assert mdeck.macro_keys() == [0]
    assert mdeck.has_key_macro(0)

    mdeck.update_key_macro(0, None)
    assert mdeck.get_key_macro(0) is None
    assert not mdeck.has_key_macro(0)

    mdeck.update_key_macro(1, action)
    assert mdeck.get_key_macro(1) is action
    assert mdeck.has_key_macro(1)

    mdeck.register_dial_macro(0, DialEventType.PUSH, action)
    assert mdeck.get_dial_macro(0, DialEventType.PUSH) is action
    assert mdeck.has_dial_macro(0, DialEventType.PUSH)
    mdeck.update_dial_macro(0, DialEventType.PUSH, None)
    assert mdeck.get_dial_macro(0, DialEventType.PUSH) is None
    assert not mdeck.has_dial_macro(0, DialEventType.PUSH)

    mdeck.register_touch_macro(TouchscreenEventType.SHORT, action)
    assert mdeck.get_touch_macro(TouchscreenEventType.SHORT) is action
    assert mdeck.has_touch_macro(TouchscreenEventType.SHORT)
    mdeck.update_touch_macro(TouchscreenEventType.SHORT, None)
    assert mdeck.get_touch_macro(TouchscreenEventType.SHORT) is None
    assert not mdeck.has_touch_macro(TouchscreenEventType.SHORT)


def test_macrodeck_copy_move_swap_macros(deck):
    mdeck = MacroDeck(deck)

    def a():
        pass

    def b():
        pass

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


def test_device_monitor_start_stop():
    manager = DeviceManager(transport="dummy")
    monitor = DeviceMonitor(manager, interval=0.01)
    monitor.start()
    time.sleep(0.02)
    monitor.stop()
    assert monitor._thread is None


def test_macrodeck_reset(deck):
    mdeck = MacroDeck(deck)

    with deck:
        deck.open()
        mdeck.register_key_macro(0, lambda: None)
        mdeck.register_dial_macro(0, DialEventType.TURN, lambda x: None)
        mdeck.register_touch_macro(TouchscreenEventType.SHORT, lambda x: None)
        mdeck.configure_key(0, uptext="A")
        mdeck.create_board()
        mdeck.create_image_board()
        deck.close()

    mdeck.disable()

    assert mdeck.key_macros
    assert mdeck.dial_macros
    assert mdeck.touch_macros
    assert mdeck.key_configs
    assert mdeck.board is not None
    assert mdeck.image_board is not None
    assert not mdeck.is_enabled()  # disabled above

    deck.open()
    with mock.patch.object(deck, "reset") as reset_mock:
        mdeck.reset()
        reset_mock.assert_called_once()
    deck.close()

    assert mdeck.key_macros == {}
    assert mdeck.dial_macros == {}
    assert mdeck.touch_macros == {}


def test_get_board_char_errors(deck):
    mdeck = MacroDeck(deck)

    with pytest.raises(ValueError):
        mdeck.get_board_char(0, 0)

    with deck:
        deck.open()
        mdeck.create_board()
        with pytest.raises(IndexError):
            mdeck.get_board_char(-1, 0)
        with pytest.raises(IndexError):
            mdeck.get_board_char(0, deck.KEY_COLS)
        deck.close()


def test_macrodeck_bulk_macro_helpers(deck):
    mdeck = MacroDeck(deck)

    def a(value=None):
        pass

    def b(value=None):
        pass

    dial_macros = {
        (0, DialEventType.PUSH): a,
        (1, DialEventType.TURN): b,
    }
    mdeck.register_dial_macros(dial_macros)
    assert mdeck.get_dial_macro(0, DialEventType.PUSH) is a
    assert mdeck.get_dial_macro(1, DialEventType.TURN) is b

    mdeck.unregister_dial_macros([(0, DialEventType.PUSH)])
    assert mdeck.get_dial_macro(0, DialEventType.PUSH) is None
    assert mdeck.get_dial_macro(1, DialEventType.TURN) is b

    touch_macros = {
        TouchscreenEventType.SHORT: a,
        TouchscreenEventType.LONG: b,
    }
    mdeck.register_touch_macros(touch_macros)
    assert mdeck.get_touch_macro(TouchscreenEventType.SHORT) is a
    assert mdeck.get_touch_macro(TouchscreenEventType.LONG) is b

    mdeck.unregister_touch_macros([TouchscreenEventType.SHORT])
    assert mdeck.get_touch_macro(TouchscreenEventType.SHORT) is None
    assert mdeck.get_touch_macro(TouchscreenEventType.LONG) is b

    mdeck.register_key_macro(0, lambda: None)
    mdeck.clear_all_macros()

    assert mdeck.key_macros == {}
    assert mdeck.dial_macros == {}
    assert mdeck.touch_macros == {}

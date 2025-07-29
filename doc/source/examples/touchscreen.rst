*****************************
Touchscreen API Examples
*****************************

The following snippet shows how to display an image on the touchscreen and react
 to touch events using the Stream Deck +::

    from StreamDeck.DeviceManager import DeviceManager
    from StreamDeck.Devices.StreamDeck import StreamDeck, TouchscreenEventType
    from StreamDeck.ImageHelpers import PILHelper

    deck = DeviceManager().enumerate()[0]
    deck.open()

    def touch_callback(deck: StreamDeck, evt_type: TouchscreenEventType, value: dict[str, int]) -> None:
        print(f"Touch at {value['x']}, {value['y']}")

    deck.set_touchscreen_callback(touch_callback)
    img = PILHelper.create_touchscreen_image(deck)
    deck.set_touchscreen_image(PILHelper.to_native_touchscreen_format(deck, img), 0, 0, img.width, img.height)

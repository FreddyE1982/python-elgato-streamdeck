# Python Elgato Stream Deck Library

![Example Deck](ExampleDeck.jpg)

This is an open source Python 3 library to control an
[Elgato Stream Deck](https://www.elgato.com/en/gaming/stream-deck) directly,
without the official software. This can allow you to create your own custom
front-ends, such as a custom control front-end for home automation software.

_________________

[PyPi Project Entry](https://pypi.org/project/streamdeck/) - [Online Documentation](https://python-elgato-streamdeck.readthedocs.io) - [Source Code](https://github.com/abcminiuser/python-elgato-streamdeck)


## Project Status:

Working - you can enumerate devices, set the brightness of the panel(s), set
the images shown on each button, and read the current button states.
Hot-plug monitoring lets applications react to Stream Decks being connected or
removed at runtime, and a simple macro framework is included for mapping
button presses to custom actions. The ``MacroDeck`` helper also provides
``configure_key()`` for quickly assigning images, labels and callbacks to keys.
Individual macros can be removed with ``unregister_*`` helpers and keys reset
via ``clear_key_configuration()``. Additional ``get_*`` and ``update_*``
helpers make it easy to query and modify existing key configurations and
actions, while new listing helpers provide insight into all configured keys and
registered macros for keys, dials and touch events.
Further helpers allow duplicating, moving or swapping key configurations and
checking if a key already has a configuration. Additional helpers let you copy,
move or swap just the registered macros and clear all stored key
configurations in one call. Macro execution can be temporarily disabled and
re-enabled with ``disable()`` and ``enable()``.
Bulk helpers can configure or clear several keys at once, register
multiple macros together and refresh stored images on the device.
``run_loop()`` provides a simple game loop for deck-only games and ``set_key_text()`` displays text directly on a key.
``set_key_image_file()`` and ``set_key_image_pil()`` simplify showing images on individual keys. ``set_key_image_bytes()`` accepts pre-formatted images and ``get_key_image()``, ``has_key_image()``, ``clear_key_image()``, ``copy_key_image()``, ``move_key_image()`` and ``swap_key_images()`` help manage stored key images.
``display_text()`` draws multi-line text across the deck while ``get_pressed_keys()``
and ``wait_for_key_press()`` help reading user input for deck-only games.
``position_to_key()`` and ``key_to_position()`` convert between key indexes and grid
positions. ``display_board()`` renders a 2D array of characters, and
``wait_for_char_press()`` returns the character associated with a pressed key.
``get_pressed_chars()`` lists the characters on pressed keys and
``wait_for_board_press()`` returns the character displayed on the next key press.
``create_board()`` and related helpers manage a persistent character grid for
deck-only games, allowing individual cells to be updated and redrawn easily.
``scroll_board()``, ``draw_line()``, ``draw_rect()`` and ``fill_rect()`` provide additional
helpers for moving and drawing on the board. ``create_board_from_strings()`` quickly
populates a board from lines of text, ``get_board_as_strings()`` returns the board
as text and ``draw_multiline_text()`` overlays several lines at once.
``create_image_board()`` and related helpers manage a board of key images for
deck-only games, allowing graphics to be scrolled or overlaid easily.
``display_deck_image()`` scales a single image across the entire deck and updates the
internal image board for further manipulation.

Currently the following StreamDeck products are supported in multiple hardware
variants:

* StreamDeck Mini
* StreamDeck Neo
* StreamDeck Original
* StreamDeck Pedal
* StreamDeck Plus
* StreamDeck XL

## Package Installation:

Install the library via pip:

```
pip install streamdeck
```

Alternatively, manually clone the project repository:

```
git clone https://github.com/abcminiuser/python-elgato-streamdeck.git
```

For detailed installation instructions, refer to the prebuilt
[online documentation](https://python-elgato-streamdeck.readthedocs.io), or
build the documentation yourself locally by running `make html` from the `docs`
directory.


## Credits:

I've used the reverse engineering notes from
[this GitHub](https://github.com/alvancamp/node-elgato-stream-deck/blob/master/NOTES.md)
repository to implement this library. Thanks Alex Van Camp!

Thank you to the following contributors, large and small, for helping with the
development and maintenance of this library:

- [admiral0](https://github.com/admiral0)
- [Aetherdyne](https://github.com/Aetherdyne)
- [benedikt-bartscher](https://github.com/benedikt-bartscher)
- [brimston3](https://github.com/brimston3)
- [BS-Tek](https://github.com/BS-Tek)
- [Core447](https://github.com/Core447)
- [dirkk0](https://github.com/dirkk0)
- [dodgyrabbit](https://github.com/dodgyrabbit)
- [dubstech](https://github.com/dubstech)
- [Giraut](https://github.com/Giraut)
- [impala454](https://github.com/impala454)
- [iPhoneAddict](https://github.com/iPhoneAddict)
- [itsusony](https://github.com/itsusony)
- [jakobbuis](https://github.com/jakobbuis)
- [jmudge14](https://github.com/jmudge14)
- [Kalle-Wirsch](https://github.com/Kalle-Wirsch)
- [karstlok](https://github.com/karstlok)
- [Lewiscowles1986](https://github.com/Lewiscowles1986)
- [m-weigand](https://github.com/m-weigand)
- [mathben](https://github.com/mathben)
- [matrixinius](https://github.com/matrixinius)
- [phillco](https://github.com/phillco)
- [pointshader](https://github.com/pointshader)
- [shanna](https://github.com/shanna)
- [spidererrol](https://github.com/Spidererrol)
- [spyoungtech](https://github.com/spyoungtech)
- [Subsentient](https://github.com/Subsentient)
- [swedishmike](https://github.com/swedishmike)
- [TheSchmidt](https://github.com/TheSchmidt)
- [theslimshaney](https://github.com/theslimshaney)
- [tjemg](https://github.com/tjemg)
- [VladFlorinIlie](https://github.com/VladFlorinIlie)

If you've contributed in some manner, but I've accidentally missed you in the
list above, please let me know.


## License:

Released under the [MIT license](LICENSE).

## Running Tests

The unit tests require no hardware and run entirely against a virtual Stream Deck device using the library\x27s dummy transport layer. To execute the test suite run:

```bash
pytest
```


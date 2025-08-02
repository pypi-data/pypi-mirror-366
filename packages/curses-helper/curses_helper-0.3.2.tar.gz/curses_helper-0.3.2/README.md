# curses_helper

Provides curses helper stuff.

Install with `pip3 install curses-helper`.

## `@curses_app`
The `@curses_app` decorator can be used as a replacement for wrapper. It takes the following arguments:
- `echo`: Whether to enable echo mode in the terminal. Default=False
- `cbreak`: Whether to enable cbreak mode, allowing reading keyboard input without waiting for enter. Default=True
- `keypad`: Whether to enable curses keypad mode. default=False

## Types
curses_helper provides a types module, providing the following type hinting types:
- `Window`: The curses window type.

All types that cannot be handled at runtime are set to `Any` when the program is being run.
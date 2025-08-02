# Copyright 2025 taitep <taitep@taitep.se>
# 
# This file is licensed under the GNU GPL v3.0 or later.
# See <https://www.gnu.org/licenses/>

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _curses import _CursesWindow

    Window = _CursesWindow
else:
    from typing import Any

    Window = Any

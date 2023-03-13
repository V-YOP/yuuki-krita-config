# SPDX-FileCopyrightText: © 2022 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
The only python file directly run by krita during plugin init phase.

Runs the file with extension by importing everything from it.

Appending this file location to python PATH allows to directly import
main packages instead of using relative imports.
"""

import sys
import os
# 这一行必须在import自定义脚本之前执行，否则会出一堆导入错误
sys.path.append(directory := os.path.dirname(__file__))

from .api_krita import Krita
from .toolbox_modifier import ToolBoxModifier
from .shortcut_composer import ShortcutComposer
from .direct_brush_eraser_switcher import DirectBrushEraserSwitcher

Krita.add_extension(ShortcutComposer)
Krita.add_extension(DirectBrushEraserSwitcher)
Krita.add_extension(ToolBoxModifier)

sys.path.remove(directory)

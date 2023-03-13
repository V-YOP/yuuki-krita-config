"""
提供直接橡皮擦和直接画笔
"""

from api_krita import Krita, Extension  # type: ignore
from api_krita.enums.tool import Tool
from .api_krita.enums.toggle import Toggle


def isEraserMode():
    return Krita.active_tool == Tool.FREEHAND_BRUSH and Toggle.ERASER.state


def isBrushMode():
    return Krita.active_tool == Tool.FREEHAND_BRUSH and not Toggle.ERASER.state


class DirectBrushEraserSwitcher(Extension):

    def __init__(self, parent):
        super().__init__(parent)
        self.lastEraser = None
        self.lastBrush = None

    def brushPresetChanged(self, new, old):
        # 当笔刷改变的时候，检查当前所处模式，如果是橡皮擦模式，修改lastEraser，如果是笔刷模式，修改lastBrush
        if new is None:
            return
        if 'Eraser' in new.name() or 'eraser' in new.name():
            self.lastEraser = new
            self.handleEraser()
        else:
            self.lastBrush = new
            self.handleBrush()

    def handleToggle(self):
        """在直接橡皮擦和画笔之间进行切换"""
        if isBrushMode():
            self.handleEraser()
        elif isEraserMode():
            self.handleBrush()
        else:  # 如果是其他模式，也走笔刷
            self.handleBrush()

    def handleEraser(self):
        """直接橡皮擦：切换到画笔，切换到橡皮擦模式"""
        Krita.get_active_view().show_floating_message("Eraser Mode", 1000, 0)
        if self.lastEraser is not None:
            Krita.get_active_view().brush_preset = self.lastEraser.name()
        Krita.active_tool = Tool.FREEHAND_BRUSH
        Toggle.ERASER.state = True
        # Krita.create_action(window, "direct_eraser/ToolEraser", "Direct Eraser", handleEraser)

    def handleBrush(self):
        """直接画笔：切换到画笔，移除橡皮擦模式"""
        Krita.get_active_view().show_floating_message("Brush Mode", 1000, 0)
        if self.lastBrush is not None:
            Krita.get_active_view().brush_preset = self.lastBrush.name()
        Krita.active_tool = Tool.FREEHAND_BRUSH
        Toggle.ERASER.state = False
        # Krita.create_action(window, "direct_eraser/ToolBrush", "Direct Brush", handleBrush)

    def setup(self):
        Krita.add_brush_preset_changed_callback(self.brushPresetChanged)
        # TODO 读取配置文件，从数据文件中获取当前橡皮擦模式和画笔模式的preset

    def createActions(self, window):
        Krita.create_action(window, "direct_eraser/Toggle", "Toggle", self.handleToggle)

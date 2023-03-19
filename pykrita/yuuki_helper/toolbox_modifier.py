"""
精简工具栏
"""

from api_krita import Krita, Extension  # type: ignore
from PyQt5.QtWidgets import QWidget, QToolButton
from api_krita.enums.tool import Tool

def modifyToolBox():
    DISPLAY_BTNS = [ i.value for i in [
        Tool.FREEHAND_BRUSH,
        Tool.FREEHAND_SELECTION,
        Tool.ASSISTANTS,
        Tool.CROP,
        Tool.REFERENCE,
        Tool.FILL,
        Tool.TRANSFORM,
        Tool.TEXT,
        # 'InteractionTool',
        # 'PathTool',
        # 'SvgTextTool',
        # 'KarbonCalligraphyTool',
        # 'KisToolSelectSimilar',
        # 'KisToolSelectRectangular',
        # 'KisToolSelectPath',
        # 'KisToolSelectPolygonal',
        # 'KisToolSelectMagnetic',
        # 'KisToolSelectOutline',
        # 'KisToolSelectElliptical',
        # 'KisToolSelectContiguous',
        # 'KritaShape/KisToolLazyBrush',
        # 'KritaShape/KisToolSmartPatch',
        # 'KritaFill/KisToolFill',
        # 'KritaSelected/KisToolColorSampler',
        # 'KisToolEncloseAndFill',
        # 'KritaFill/KisToolGradient',
        # 'KritaShape/KisToolRectangle',
        # 'KritaShape/KisToolEllipse',
        # 'KritaShape/KisToolLine',
        # 'KisToolPolygon',
        # 'KisToolPolyline',
        # 'KritaShape/KisToolDyna',
        # 'KisToolPath',
        # 'KritaShape/KisToolMultiBrush',
        # 'KritaShape/KisToolBrush',
        # 'KisToolPencil',
        # 'KritaTransform/KisToolMove',
        # 'KisToolCrop',
        # 'KisToolTransform',
        # 'KisAssistantTool',
        # 'ToolReferenceImages',
        # 'KritaShape/KisToolMeasure',
        # 'PanTool',
        # 'ZoomTool',
    ]]

    def find_tool_box() -> QToolButton:
        qwindow = Krita.get_active_qwindow()
        for qobj in qwindow.findChildren(QWidget):
            if qobj.metaObject().className() == "KoToolBox":
                return qobj

    # 获取所有Btn
    allBtn = find_tool_box().findChildren(QToolButton)

    for btn in allBtn:
        # 仅显示相应Btn
        if len(DISPLAY_BTNS) == 0 or btn.objectName() in DISPLAY_BTNS:
            btn.show()
        else:
            btn.hide()


class ToolBoxModifier(Extension):
    """Krita extension that adds complex actions invoked with keyboard."""

    def __init__(self, parent) -> None:
        """Add callback to reload actions on theme change."""
        super().__init__(parent)

    def setup(self) -> None:
        """Obligatory abstract method override."""
        def callback():
            modifyToolBox()
        Krita.add_window_open_callback(callback)

    def createActions(self, window) -> None:
        """Create window components. Called by krita for each new window."""


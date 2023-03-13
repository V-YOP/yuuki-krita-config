# SPDX-FileCopyrightText: © 2022 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import RLock
from krita import Krita as Api, Extension, qApp
from typing import Callable, Protocol, Any

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QWidgetAction
from PyQt5.QtGui import QKeySequence, QColor, QIcon
from PyQt5.QtCore import QTimer

from .wrappers import (
    ToolDescriptor,
    Document,
    Canvas,
    Cursor,
    View,
)


class KritaInstance:
    """Wraps krita API for typing, documentation and PEP8 compatibility."""

    active_tool = ToolDescriptor()
    """Settable property which lets to set and get active tool from toolbox."""

    def __init__(self) -> None:
        self.instance = Api.instance()
        self.screen_size = QDesktopWidget().screenGeometry(-1).width()
        self.main_window: Any = None

    def get_active_view(self) -> View:
        """Return wrapper of krita `View`."""
        return View(self.instance.activeWindow().activeView())

    def get_active_document(self) -> Document:
        """Return wrapper of krita `Document`."""
        return Document(self.instance.activeDocument())

    def get_active_canvas(self) -> Canvas:
        """Return wrapper of krita `Canvas`."""
        return Canvas(self.instance.activeWindow().activeView().canvas())

    def get_cursor(self) -> Cursor:
        """Return wrapper of krita `Cursor`. Don't use on plugin init phase."""
        qwin = self.get_active_qwindow()
        return Cursor(qwin)

    def trigger_action(self, action_name: str) -> None:
        """Trigger internal krita action called `action_name`."""
        return self.instance.action(action_name).trigger()

    def action_checked(self, action_name: str) -> bool:
        """Return if action is checked or not."""
        return self.instance.action(action_name).isChecked()

    def get_action_shortcut(self, action_name: str) -> QKeySequence:
        """Return shortcut of krita action called `action_name`."""
        return self.instance.action(action_name).shortcut()

    def get_presets(self) -> dict:
        """Return a list of unwrapped preset objects"""
        return self.instance.resources('preset')

    def get_active_qwindow(self) -> QMainWindow:
        """Return qt window of krita. Don't use on plugin init phase."""
        return self.instance.activeWindow().qwindow()

    def get_icon(self, icon_name: str) -> QIcon:
        return self.instance.icon(icon_name)

    def read_setting(self, group: str, name: str, default: str) -> str:
        """Read setting from .kritarc file as string."""
        return self.instance.readSetting(group, name, default)

    def write_setting(self, group: str, name: str, value: Any) -> None:
        """Write setting to .kritarc file. Value type will be lost."""
        self.instance.writeSetting(group, name, str(value))

    def create_action(
        self,
        window: 'KritaWindow',
        name: str,
        group: str = "",
        callback: Callable[[], None] = lambda: None
    ):
        """
        Create a new action in krita.

        Requires providing a krita window received in createActions()
        method of the main extension file.
        """
        krita_action = window.createAction(name, name, group)
        krita_action.setAutoRepeat(False)
        krita_action.triggered.connect(callback)
        return krita_action

    def add_extension(self, extension: Extension) -> None:
        """Add extension/plugin/add-on to krita."""
        self.instance.addExtension(extension(self.instance))

    def add_theme_change_callback(self, callback: Callable[[], None]) -> Any:
        """
        Add method which should be run after the theme is changed.

        Method is delayed with a timer to allow running it on plugin
        initialization phase.
        """
        def connect_callback():
            self.main_window = self.instance.activeWindow()
            if self.main_window is not None:
                self.main_window.themeChanged.connect(callback)
        QTimer.singleShot(1000, connect_callback)

    def add_window_open_callback(self, callback: Callable[[], None]) -> Any:
        """
        添加窗口打开时的callback，基于Notifier
        """
        appNotifier = self.instance.notifier()
        appNotifier.setActive(True)
        appNotifier.windowCreated.connect(callback)

    def _current_brush_preset(self):
        """获取当前笔刷，返回Resource"""
        if (self.instance.activeWindow() is not None and self.instance.activeWindow().activeView() is not None):
            return self.instance.activeWindow().activeView().currentBrushPreset()
        return None

    _brushPresetChangedTimerInited = False
    _brushPresetChangedCallbacks = []
    _BRUSH_PRESET_CHANGED_DELAY = 50
    _brushPresetChangedLastBrush = None
    def add_brush_preset_changed_callback(self, callback: Callable) -> Any:
        """
        添加笔刷修改时的回调，基于QTimer，50ms检查一次
        """
        def helper():
            currentBrush = self._current_brush_preset()
            # 前后笔刷相同，什么都不做
            if currentBrush is self._brushPresetChangedLastBrush:
                return
            # 但用is判断不一定准确，再根据名字去判断
            if (currentBrush is not None and 
                self._brushPresetChangedLastBrush is not None and 
                currentBrush.name() == self._brushPresetChangedLastBrush.name()):
                return
            # 执行每一个回调
            for callback in self._brushPresetChangedCallbacks:
                callback(currentBrush, self._brushPresetChangedLastBrush)
            self._brushPresetChangedLastBrush = currentBrush

        if not self._brushPresetChangedTimerInited:
            timer = QTimer()
            def onMainWindowCreated():
                timer.timeout.connect(helper)
                timer.start(1000)
            def onApplicationClosing():
                timer.stop()
            appNotifier = self.instance.notifier()
            appNotifier.setActive(True)
            appNotifier.windowCreated.connect(onMainWindowCreated)
            appNotifier.applicationClosing.connect(onApplicationClosing)
            self._brushPresetChangedTimerInited = True
        self._brushPresetChangedCallbacks.append(callback)
        
    @property
    def is_light_theme_active(self) -> bool:
        """Return if currently set theme is light using it's main color."""
        main_color: QColor = qApp.palette().window().color()
        average = (main_color.red()+main_color.green()+main_color.blue()) // 3
        return average > 128


class KritaWindow(Protocol):
    """Krita window received in createActions() of main extension file."""

    def createAction(
        self,
        name: str,
        description: str,
        menu: str, /
    ) -> QWidgetAction: ...

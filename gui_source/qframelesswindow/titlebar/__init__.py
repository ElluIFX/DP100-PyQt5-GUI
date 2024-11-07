# coding:utf-8
import sys

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget

from ..utils import startSystemMove
from .title_bar_buttons import (
    CloseButton,
    FullscreenButton,
    MaximizeButton,
    MinimizeButton,
)


class TitleBar(QWidget):
    """Title bar"""

    def __init__(self, parent):
        super().__init__(parent)
        self.minBtn = MinimizeButton(parent=self)
        self.closeBtn = CloseButton(parent=self)
        self.maxBtn = MaximizeButton(parent=self)
        self.fullBtn = FullscreenButton(parent=self)
        self.hBoxLayout = QHBoxLayout(self)

        self.resize(200, 32)
        self.setFixedHeight(32)

        # add buttons to layout
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.fullBtn, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.minBtn, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.maxBtn, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.closeBtn, 0, Qt.AlignRight)
        self.hBoxLayout.setAlignment(Qt.AlignRight)

        # connect signal to slot
        self.minBtn.clicked.connect(self.window().showMinimized)
        self.maxBtn.clicked.connect(self.__toggleMaxState)
        self.closeBtn.clicked.connect(self.window().close)
        self.fullBtn.clicked.connect(self._toggleFullScreen)
        self.minBtnEnabled = True
        self.maxBtnEnabled = True
        self.closeBtnEnabled = True
        self.fullBtnEnabled = True
        self.allowDoubleToggleMax = True

        self.window().installEventFilter(self)

    def set_close_btn_enabled(self, enabled):
        self.closeBtnEnabled = enabled
        if not enabled:
            self.closeBtn.hide()
        else:
            self.closeBtn.show()

    def set_full_btn_enabled(self, enabled):
        self.fullBtnEnabled = enabled
        if not enabled:
            self.fullBtn.hide()
        else:
            self.fullBtn.show()

    def set_min_btn_enabled(self, enabled):
        self.minBtnEnabled = enabled
        if not enabled:
            self.minBtn.hide()
        else:
            self.minBtn.show()

    def set_max_btn_enabled(self, enabled):
        self.maxBtnEnabled = enabled
        if not enabled:
            self.maxBtn.hide()
        else:
            self.maxBtn.show()

    def set_allow_double_toggle_max(self, allow):
        self.allowDoubleToggleMax = allow

    def eventFilter(self, obj, e):
        if obj is self.window():
            if e.type() == QEvent.WindowStateChange:
                self.maxBtn.setMaxState(self.window().isMaximized())
                return False

        return super().eventFilter(obj, e)

    def mouseDoubleClickEvent(self, event):
        """Toggles the maximization state of the window"""
        if event.button() != Qt.LeftButton or not self.allowDoubleToggleMax:
            return

        self.__toggleMaxState()

    def mouseMoveEvent(self, e):
        if sys.platform != "win32" or not self._isDragRegion(e.pos()):
            return

        startSystemMove(self.window(), e.globalPos())

    def mousePressEvent(self, e):
        if (
            sys.platform == "win32"
            or e.button() != Qt.LeftButton
            or not self._isDragRegion(e.pos())
        ):
            return

        startSystemMove(self.window(), e.globalPos())

    def __toggleMaxState(self):
        """Toggles the maximization state of the window and change icon"""
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def _isDragRegion(self, pos):
        """Check whether the pressed point belongs to the area where dragging is allowed"""
        return 0 < pos.x() < self.width() - 46 * 3

    def _toggleFullScreen(self):
        """Toggles the full screen state of the window"""
        if self.window().isFullScreen():
            self.window().showNormal()
            self.fullBtn.setFullscreenState(False)
            if self.maxBtnEnabled:
                self.maxBtn.show()
            if self.minBtnEnabled:
                self.minBtn.show()
        else:
            self.window().showFullScreen()
            self.fullBtn.setFullscreenState(True)
            self.maxBtn.hide()
            self.minBtn.hide()

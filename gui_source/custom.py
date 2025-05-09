from functools import partial
from typing import Any, Callable, List, Tuple

import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
from qframelesswindow import FramelessWindow, TitleBar

global_font = QtGui.QFont()


class FmtAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        self.sync_with = kwargs.pop("sync_with", None)
        self.sync_left_spacing = kwargs.pop("sync_left_spacing", False)
        self.max_string_len = None
        super().__init__(*args, **kwargs)

    def syncWith(self, axis: "FmtAxisItem", left_spacing=False):
        self.sync_with = axis
        self.sync_left_spacing = left_spacing

    def tickStrings(self, values, scale, spacing):
        if len(values) == 0 or max(values) < 1e6:
            strings = super().tickStrings(values, scale, spacing)
        else:
            strings = [f"{v:.2e}" for v in values]
        self.max_string_len = max(len(s) for s in strings)
        if self.sync_with is not None:
            maxl = self.sync_with.max_string_len
            if maxl is not None and maxl > self.max_string_len:
                if self.sync_left_spacing:
                    strings = [s.rjust(maxl) for s in strings]
                else:
                    strings = [s.ljust(maxl) for s in strings]
        return strings


class CustomTitleBar(TitleBar):
    def __init__(self, parent, name):
        super().__init__(parent)
        self.label = QtWidgets.QLabel(name, self)
        self.label.setStyleSheet(
            "QLabel{font: 13px 'Sarasa Fixed SC SemiBold'; margin: 10px}"
        )
        self.label.adjustSize()
        self.darkStyle = {
            "normal": {
                "color": (255, 255, 255),
            }
        }
        self.lightStyle = {
            "normal": {
                "color": (20, 20, 20),
            }
        }

    def set_name(self, name):
        self.label.setText(name)
        self.label.adjustSize()

    def set_theme(self, theme):
        style = getattr(self, f"{theme}Style")
        self.minBtn.updateStyle(style)
        self.maxBtn.updateStyle(style)
        self.closeBtn.updateStyle(style)
        self.fullBtn.updateStyle(style)


class CustomMessageBox(QtWidgets.QDialog, FramelessWindow):
    def __init__(
        self,
        parent,
        title,
        message,
        question=False,
        additional_actions: List[Tuple[str, Callable[[], bool]]] = [],
        override_key_strs: List[str] = [],
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)

        title, message = str(title), str(message)

        # Custom title bar
        self.CustomTitleBar = CustomTitleBar(self, title)
        self.CustomTitleBar.set_allow_double_toggle_max(False)
        self.CustomTitleBar.set_min_btn_enabled(False)
        self.CustomTitleBar.set_max_btn_enabled(False)
        self.CustomTitleBar.set_full_btn_enabled(False)
        self.CustomTitleBar.set_close_btn_enabled(False)
        self.setTitleBar(self.CustomTitleBar)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        self.spaceLabel = QtWidgets.QLabel("", self)
        self.spaceLabel.setFixedHeight(20)
        layout.addWidget(self.spaceLabel)

        # Message label
        self.messageLabel = QtWidgets.QLabel(message, self)
        self.messageLabel.setWordWrap(False)
        self.messageLabel.setFont(global_font)
        self.messageLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )  # Allow horizontal expansion
        layout.addWidget(self.messageLabel, alignment=QtCore.Qt.AlignCenter)

        # Button
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(8)
        layout.addLayout(self.horizontalLayout)
        if not question:
            self.okButton = QtWidgets.QPushButton(
                self.tr("确定") if not override_key_strs else override_key_strs[0], self
            )
            self.okButton.setFont(global_font)
            self.okButton.clicked.connect(self.close)
            self.horizontalLayout.addWidget(self.okButton)
        else:
            self.okButton = QtWidgets.QPushButton(
                self.tr("是") if not override_key_strs else override_key_strs[0], self
            )
            self.okButton.setFont(global_font)
            self.okButton.clicked.connect(self.accept)
            self.horizontalLayout.addWidget(self.okButton)

            self.cancelButton = QtWidgets.QPushButton(
                self.tr("否") if not override_key_strs else override_key_strs[1], self
            )
            self.cancelButton.setFont(global_font)
            self.cancelButton.clicked.connect(self.reject)
            self.horizontalLayout.addWidget(self.cancelButton)

        if additional_actions:
            for text, func in additional_actions:
                button = QtWidgets.QPushButton(text, self)
                button.setFont(global_font)
                button.clicked.connect(partial(self._handle_additional_action, func))
                self.horizontalLayout.addWidget(button)

        self.adjustSize()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.ret = True
        self.exec_()

    def _handle_additional_action(self, func):
        if func():
            self.close()

    def result(self) -> bool:
        return self.ret

    @staticmethod
    def question(parent, title, message):
        dialog = CustomMessageBox(parent, title, message, question=True)
        return dialog.result()

    def accept(self):
        self.ret = True
        return super().accept()

    def reject(self):
        self.ret = False
        return super().reject()


class CustomInputDialog(QtWidgets.QDialog, FramelessWindow):
    def __init__(
        self,
        parent,
        title,
        label,
        input_type="text",
        default_value=None,
        placeholder_text=None,
        min_value=None,
        max_value=None,
        decimals=None,
        step=None,
        prefix=None,
        suffix=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)

        # Custom title bar
        self.CustomTitleBar = CustomTitleBar(self, title)
        self.CustomTitleBar.set_allow_double_toggle_max(False)
        self.CustomTitleBar.set_min_btn_enabled(False)
        self.CustomTitleBar.set_max_btn_enabled(False)
        self.CustomTitleBar.set_full_btn_enabled(False)
        self.CustomTitleBar.set_close_btn_enabled(False)
        self.setTitleBar(self.CustomTitleBar)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        self.spaceLabel = QtWidgets.QLabel("", self)
        self.spaceLabel.setFixedHeight(20)
        layout.addWidget(self.spaceLabel)

        # Input label
        self.inputLabel = QtWidgets.QLabel(label, self)
        self.inputLabel.setFont(global_font)
        layout.addWidget(self.inputLabel, alignment=QtCore.Qt.AlignCenter)

        # Input field
        if input_type == "text":
            self.inputField = QtWidgets.QLineEdit(self)
            if default_value is not None:
                self.inputField.setText(default_value)
            if placeholder_text is not None:
                self.inputField.setPlaceholderText(placeholder_text)
        elif input_type == "int":
            self.inputField = QtWidgets.QSpinBox(self)
        elif input_type == "double":
            self.inputField = QtWidgets.QDoubleSpinBox(self)
            if decimals is not None:
                self.inputField.setDecimals(decimals)
        elif input_type == "datetime":
            self.inputField = QtWidgets.QDateTimeEdit(self)
            self.inputField.setCalendarPopup(True)
            self.inputField.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
            self.resize(self.size().width() + 80, self.size().height())
            if default_value is not None:
                self.inputField.setDateTime(default_value)
            else:
                now = QtCore.QDateTime.currentDateTime()
                self.inputField.setDateTime(now)
            if min_value is not None:
                self.inputField.setMinimumDateTime(min_value)
            if max_value is not None:
                self.inputField.setMaximumDateTime(max_value)
        if input_type in ("int", "double"):
            if min_value is not None:
                self.inputField.setMinimum(min_value)
            if max_value is not None:
                self.inputField.setMaximum(max_value)
            if default_value is not None:
                self.inputField.setValue(default_value)
            if step is not None:
                self.inputField.setSingleStep(step)
            if prefix is not None:
                self.inputField.setPrefix(prefix)
            if suffix is not None:
                self.inputField.setSuffix(suffix)

        self.inputField.setFont(global_font)
        layout.addWidget(self.inputField, alignment=QtCore.Qt.AlignCenter)

        # Buttons
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(8)
        layout.addLayout(self.horizontalLayout)

        self.okButton = QtWidgets.QPushButton("  " + self.tr("确定") + "  ", self)
        self.okButton.setFont(global_font)
        self.okButton.clicked.connect(self.accept)
        self.horizontalLayout.addWidget(self.okButton)

        self.cancelButton = QtWidgets.QPushButton("  " + self.tr("取消") + "  ", self)
        self.cancelButton.setFont(global_font)
        self.cancelButton.clicked.connect(self.reject)
        self.horizontalLayout.addWidget(self.cancelButton)

        self.adjustSize()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.ret = True
        self.exec_()

    def result(self) -> Tuple[Any, bool]:
        if isinstance(self.inputField, QtWidgets.QLineEdit):
            return self.inputField.text(), self.ret
        elif isinstance(self.inputField, QtWidgets.QSpinBox):
            return self.inputField.value(), self.ret
        elif isinstance(self.inputField, QtWidgets.QDoubleSpinBox):
            return self.inputField.value(), self.ret
        elif isinstance(self.inputField, QtWidgets.QDateTimeEdit):
            return self.inputField.dateTime(), self.ret

    def accept(self):
        self.ret = True
        return super().accept()

    def reject(self):
        self.ret = False
        return super().reject()

    @staticmethod
    def getText(
        parent, title, label, default_value="", placeholder_text=None
    ) -> Tuple[str, bool]:
        dialog = CustomInputDialog(
            parent,
            title,
            label,
            input_type="text",
            default_value=default_value,
            placeholder_text=placeholder_text,
        )
        return dialog.result()

    @staticmethod
    def getInt(
        parent,
        title,
        label,
        default_value=0,
        min_value=0,
        max_value=100,
        step=1,
        prefix=None,
        suffix=None,
    ) -> Tuple[int, bool]:
        dialog = CustomInputDialog(
            parent,
            title,
            label,
            input_type="int",
            default_value=default_value,
            min_value=min_value,
            max_value=max_value,
            step=step,
            prefix=prefix,
            suffix=suffix,
        )
        return dialog.result()

    @staticmethod
    def getDouble(
        parent,
        title,
        label,
        default_value=0.0,
        min_value=0.0,
        max_value=100.0,
        decimals=2,
        step=0.01,
        prefix=None,
        suffix=None,
    ) -> Tuple[float, bool]:
        dialog = CustomInputDialog(
            parent,
            title,
            label,
            input_type="double",
            default_value=default_value,
            min_value=min_value,
            max_value=max_value,
            decimals=decimals,
            step=step,
            prefix=prefix,
            suffix=suffix,
        )
        return dialog.result()

    @staticmethod
    def getDateTime(
        parent, title, label, default_value=None, min_value=None, max_value=None
    ) -> Tuple[QtCore.QDateTime, bool]:
        dialog = CustomInputDialog(
            parent,
            title,
            label,
            input_type="datetime",
            default_value=default_value,
            min_value=min_value,
            max_value=max_value,
        )
        return dialog.result()

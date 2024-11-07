# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
##
## Created by: Qt User Interface Compiler version 6.5.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QDialog,
    QDoubleSpinBox, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_DialogSettings(object):
    def setupUi(self, DialogSettings):
        if not DialogSettings.objectName():
            DialogSettings.setObjectName(u"DialogSettings")
        DialogSettings.setWindowModality(Qt.WindowModal)
        DialogSettings.setEnabled(True)
        DialogSettings.resize(335, 434)
        DialogSettings.setMinimumSize(QSize(335, 434))
        DialogSettings.setMaximumSize(QSize(335, 448))
        DialogSettings.setSizeGripEnabled(False)
        DialogSettings.setModal(True)
        self.verticalLayout = QVBoxLayout(DialogSettings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(DialogSettings)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 20))
        self.label.setMaximumSize(QSize(16777215, 20))

        self.verticalLayout.addWidget(self.label)

        self.label_36 = QLabel(DialogSettings)
        self.label_36.setObjectName(u"label_36")
        self.label_36.setMinimumSize(QSize(0, 28))
        font = QFont()
        font.setFamilies([u"Sarasa Fixed SC SemiBold"])
        self.label_36.setFont(font)
        self.label_36.setAlignment(Qt.AlignCenter)
        self.label_36.setMargin(6)

        self.verticalLayout.addWidget(self.label_36)

        self.horizontalLayout_33 = QHBoxLayout()
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.label_34 = QLabel(DialogSettings)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setMinimumSize(QSize(0, 28))
        self.label_34.setFont(font)
        self.label_34.setAlignment(Qt.AlignCenter)
        self.label_34.setMargin(6)

        self.horizontalLayout_33.addWidget(self.label_34)

        self.comboBoxPort = QComboBox(DialogSettings)
        self.comboBoxPort.addItem("")
        self.comboBoxPort.setObjectName(u"comboBoxPort")
        self.comboBoxPort.setFont(font)

        self.horizontalLayout_33.addWidget(self.comboBoxPort)

        self.horizontalLayout_33.setStretch(0, 2)
        self.horizontalLayout_33.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout_33)

        self.horizontalLayout_34 = QHBoxLayout()
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.label_35 = QLabel(DialogSettings)
        self.label_35.setObjectName(u"label_35")
        self.label_35.setMinimumSize(QSize(0, 28))
        self.label_35.setFont(font)
        self.label_35.setAlignment(Qt.AlignCenter)
        self.label_35.setMargin(6)

        self.horizontalLayout_34.addWidget(self.label_35)

        self.spinBoxBaud = QDoubleSpinBox(DialogSettings)
        self.spinBoxBaud.setObjectName(u"spinBoxBaud")
        self.spinBoxBaud.setFont(font)
        self.spinBoxBaud.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.spinBoxBaud.setDecimals(0)
        self.spinBoxBaud.setMinimum(0.000000000000000)
        self.spinBoxBaud.setMaximum(999999999.000000000000000)
        self.spinBoxBaud.setSingleStep(1.000000000000000)
        self.spinBoxBaud.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxBaud.setValue(921600.000000000000000)

        self.horizontalLayout_34.addWidget(self.spinBoxBaud)

        self.horizontalLayout_34.setStretch(0, 2)
        self.horizontalLayout_34.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout_34)

        self.horizontalLayout_35 = QHBoxLayout()
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.label_37 = QLabel(DialogSettings)
        self.label_37.setObjectName(u"label_37")
        self.label_37.setMinimumSize(QSize(0, 28))
        self.label_37.setFont(font)
        self.label_37.setAlignment(Qt.AlignCenter)
        self.label_37.setMargin(6)

        self.horizontalLayout_35.addWidget(self.label_37)

        self.frame = QFrame(DialogSettings)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Plain)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.lineEditAddr1 = QLineEdit(self.frame)
        self.lineEditAddr1.setObjectName(u"lineEditAddr1")
        self.lineEditAddr1.setMaximumSize(QSize(30, 16777215))
        self.lineEditAddr1.setFont(font)
        self.lineEditAddr1.setMaxLength(2)
        self.lineEditAddr1.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.lineEditAddr1)

        self.label_38 = QLabel(self.frame)
        self.label_38.setObjectName(u"label_38")
        self.label_38.setMinimumSize(QSize(0, 28))
        self.label_38.setMaximumSize(QSize(10, 16777215))
        self.label_38.setSizeIncrement(QSize(0, 0))
        self.label_38.setFont(font)
        self.label_38.setAlignment(Qt.AlignCenter)
        self.label_38.setMargin(6)

        self.horizontalLayout.addWidget(self.label_38)

        self.lineEditAddr2 = QLineEdit(self.frame)
        self.lineEditAddr2.setObjectName(u"lineEditAddr2")
        self.lineEditAddr2.setMaximumSize(QSize(30, 16777215))
        self.lineEditAddr2.setFont(font)
        self.lineEditAddr2.setMaxLength(2)
        self.lineEditAddr2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.lineEditAddr2)

        self.label_39 = QLabel(self.frame)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setMinimumSize(QSize(0, 28))
        self.label_39.setMaximumSize(QSize(10, 16777215))
        self.label_39.setSizeIncrement(QSize(0, 0))
        self.label_39.setFont(font)
        self.label_39.setAlignment(Qt.AlignCenter)
        self.label_39.setMargin(6)

        self.horizontalLayout.addWidget(self.label_39)

        self.lineEditAddr3 = QLineEdit(self.frame)
        self.lineEditAddr3.setObjectName(u"lineEditAddr3")
        self.lineEditAddr3.setMaximumSize(QSize(30, 16777215))
        self.lineEditAddr3.setFont(font)
        self.lineEditAddr3.setMaxLength(2)
        self.lineEditAddr3.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.lineEditAddr3)

        self.label_41 = QLabel(self.frame)
        self.label_41.setObjectName(u"label_41")
        self.label_41.setMinimumSize(QSize(0, 28))
        self.label_41.setMaximumSize(QSize(10, 16777215))
        self.label_41.setSizeIncrement(QSize(0, 0))
        self.label_41.setFont(font)
        self.label_41.setAlignment(Qt.AlignCenter)
        self.label_41.setMargin(6)

        self.horizontalLayout.addWidget(self.label_41)

        self.lineEditAddr4 = QLineEdit(self.frame)
        self.lineEditAddr4.setObjectName(u"lineEditAddr4")
        self.lineEditAddr4.setMaximumSize(QSize(30, 16777215))
        self.lineEditAddr4.setFont(font)
        self.lineEditAddr4.setMaxLength(2)
        self.lineEditAddr4.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.lineEditAddr4)

        self.label_40 = QLabel(self.frame)
        self.label_40.setObjectName(u"label_40")
        self.label_40.setMinimumSize(QSize(0, 28))
        self.label_40.setMaximumSize(QSize(10, 16777215))
        self.label_40.setSizeIncrement(QSize(0, 0))
        self.label_40.setFont(font)
        self.label_40.setAlignment(Qt.AlignCenter)
        self.label_40.setMargin(6)

        self.horizontalLayout.addWidget(self.label_40)

        self.lineEditAddr5 = QLineEdit(self.frame)
        self.lineEditAddr5.setObjectName(u"lineEditAddr5")
        self.lineEditAddr5.setMaximumSize(QSize(30, 16777215))
        self.lineEditAddr5.setFont(font)
        self.lineEditAddr5.setMaxLength(2)
        self.lineEditAddr5.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.lineEditAddr5)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)


        self.horizontalLayout_35.addWidget(self.frame)

        self.horizontalLayout_35.setStretch(0, 2)
        self.horizontalLayout_35.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout_35)

        self.horizontalLayout_37 = QHBoxLayout()
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.label_43 = QLabel(DialogSettings)
        self.label_43.setObjectName(u"label_43")
        self.label_43.setMinimumSize(QSize(0, 28))
        self.label_43.setFont(font)
        self.label_43.setAlignment(Qt.AlignCenter)
        self.label_43.setMargin(6)

        self.horizontalLayout_37.addWidget(self.label_43)

        self.spinBoxFreq = QDoubleSpinBox(DialogSettings)
        self.spinBoxFreq.setObjectName(u"spinBoxFreq")
        self.spinBoxFreq.setFont(font)
        self.spinBoxFreq.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.spinBoxFreq.setDecimals(0)
        self.spinBoxFreq.setMinimum(2400.000000000000000)
        self.spinBoxFreq.setMaximum(2525.000000000000000)
        self.spinBoxFreq.setSingleStep(1.000000000000000)
        self.spinBoxFreq.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxFreq.setValue(2521.000000000000000)

        self.horizontalLayout_37.addWidget(self.spinBoxFreq)

        self.horizontalLayout_37.setStretch(0, 2)
        self.horizontalLayout_37.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout_37)

        self.horizontalLayout_36 = QHBoxLayout()
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.label_42 = QLabel(DialogSettings)
        self.label_42.setObjectName(u"label_42")
        self.label_42.setMinimumSize(QSize(0, 28))
        self.label_42.setFont(font)
        self.label_42.setAlignment(Qt.AlignCenter)
        self.label_42.setMargin(6)

        self.horizontalLayout_36.addWidget(self.label_42)

        self.comboBoxPower = QComboBox(DialogSettings)
        self.comboBoxPower.addItem("")
        self.comboBoxPower.addItem("")
        self.comboBoxPower.addItem("")
        self.comboBoxPower.addItem("")
        self.comboBoxPower.addItem("")
        self.comboBoxPower.addItem("")
        self.comboBoxPower.addItem("")
        self.comboBoxPower.addItem("")
        self.comboBoxPower.setObjectName(u"comboBoxPower")
        self.comboBoxPower.setFont(font)

        self.horizontalLayout_36.addWidget(self.comboBoxPower)

        self.horizontalLayout_36.setStretch(0, 2)
        self.horizontalLayout_36.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout_36)

        self.line = QFrame(DialogSettings)
        self.line.setObjectName(u"line")
        self.line.setFrameShadow(QFrame.Plain)
        self.line.setFrameShape(QFrame.HLine)

        self.verticalLayout.addWidget(self.line)

        self.label_44 = QLabel(DialogSettings)
        self.label_44.setObjectName(u"label_44")
        self.label_44.setMinimumSize(QSize(0, 28))
        self.label_44.setFont(font)
        self.label_44.setAlignment(Qt.AlignCenter)
        self.label_44.setMargin(6)

        self.verticalLayout.addWidget(self.label_44)

        self.horizontalLayout_38 = QHBoxLayout()
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.btnMatch = QPushButton(DialogSettings)
        self.btnMatch.setObjectName(u"btnMatch")
        self.btnMatch.setFont(font)

        self.horizontalLayout_38.addWidget(self.btnMatch)

        self.lineEditIdcode = QLineEdit(DialogSettings)
        self.lineEditIdcode.setObjectName(u"lineEditIdcode")
        self.lineEditIdcode.setClearButtonEnabled(True)

        self.horizontalLayout_38.addWidget(self.lineEditIdcode)

        self.horizontalLayout_38.setStretch(0, 2)
        self.horizontalLayout_38.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout_38)

        self.horizontalLayout_40 = QHBoxLayout()
        self.horizontalLayout_40.setObjectName(u"horizontalLayout_40")
        self.label_46 = QLabel(DialogSettings)
        self.label_46.setObjectName(u"label_46")
        self.label_46.setMinimumSize(QSize(0, 28))
        self.label_46.setFont(font)
        self.label_46.setAlignment(Qt.AlignCenter)
        self.label_46.setMargin(6)

        self.horizontalLayout_40.addWidget(self.label_46)

        self.lineEditColor = QLineEdit(DialogSettings)
        self.lineEditColor.setObjectName(u"lineEditColor")

        self.horizontalLayout_40.addWidget(self.lineEditColor)

        self.lineEditColorIndicator = QLineEdit(DialogSettings)
        self.lineEditColorIndicator.setObjectName(u"lineEditColorIndicator")
        self.lineEditColorIndicator.setMinimumSize(QSize(1, 0))
        self.lineEditColorIndicator.setFrame(False)
        self.lineEditColorIndicator.setReadOnly(True)

        self.horizontalLayout_40.addWidget(self.lineEditColorIndicator)

        self.horizontalLayout_40.setStretch(0, 4)
        self.horizontalLayout_40.setStretch(1, 5)
        self.horizontalLayout_40.setStretch(2, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_40)

        self.horizontalLayout_41 = QHBoxLayout()
        self.horizontalLayout_41.setObjectName(u"horizontalLayout_41")
        self.label_47 = QLabel(DialogSettings)
        self.label_47.setObjectName(u"label_47")
        self.label_47.setMinimumSize(QSize(0, 28))
        self.label_47.setFont(font)
        self.label_47.setAlignment(Qt.AlignCenter)
        self.label_47.setMargin(6)

        self.horizontalLayout_41.addWidget(self.label_47)

        self.spinBoxM01 = QDoubleSpinBox(DialogSettings)
        self.spinBoxM01.setObjectName(u"spinBoxM01")
        self.spinBoxM01.setFont(font)
        self.spinBoxM01.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.spinBoxM01.setDecimals(0)
        self.spinBoxM01.setMinimum(0.000000000000000)
        self.spinBoxM01.setMaximum(5.000000000000000)
        self.spinBoxM01.setSingleStep(1.000000000000000)
        self.spinBoxM01.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxM01.setValue(0.000000000000000)

        self.horizontalLayout_41.addWidget(self.spinBoxM01)

        self.horizontalLayout_41.setStretch(0, 2)
        self.horizontalLayout_41.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout_41)

        self.horizontalLayout_42 = QHBoxLayout()
        self.horizontalLayout_42.setObjectName(u"horizontalLayout_42")
        self.label_48 = QLabel(DialogSettings)
        self.label_48.setObjectName(u"label_48")
        self.label_48.setMinimumSize(QSize(0, 28))
        self.label_48.setFont(font)
        self.label_48.setAlignment(Qt.AlignCenter)
        self.label_48.setMargin(6)

        self.horizontalLayout_42.addWidget(self.label_48)

        self.comboBoxBlink = QComboBox(DialogSettings)
        self.comboBoxBlink.addItem("")
        self.comboBoxBlink.addItem("")
        self.comboBoxBlink.setObjectName(u"comboBoxBlink")
        self.comboBoxBlink.setFont(font)

        self.horizontalLayout_42.addWidget(self.comboBoxBlink)

        self.horizontalLayout_42.setStretch(0, 2)
        self.horizontalLayout_42.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout_42)

        self.line_2 = QFrame(DialogSettings)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShadow(QFrame.Plain)
        self.line_2.setFrameShape(QFrame.HLine)

        self.verticalLayout.addWidget(self.line_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.btnSave = QPushButton(DialogSettings)
        self.btnSave.setObjectName(u"btnSave")
        self.btnSave.setFont(font)

        self.horizontalLayout_3.addWidget(self.btnSave)

        self.btnOk = QPushButton(DialogSettings)
        self.btnOk.setObjectName(u"btnOk")
        self.btnOk.setFont(font)

        self.horizontalLayout_3.addWidget(self.btnOk)

        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.retranslateUi(DialogSettings)

        self.comboBoxPower.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(DialogSettings)
    # setupUi

    def retranslateUi(self, DialogSettings):
        DialogSettings.setWindowTitle(QCoreApplication.translate("DialogSettings", u"\u8fde\u63a5\u8bbe\u7f6e", None))
        self.label.setText("")
        self.label_36.setText(QCoreApplication.translate("DialogSettings", u"- NRF24L01 Adapter -", None))
        self.label_34.setText(QCoreApplication.translate("DialogSettings", u"\u4e32\u53e3\u53f7", None))
        self.comboBoxPort.setItemText(0, QCoreApplication.translate("DialogSettings", u"\u81ea\u52a8", None))

        self.label_35.setText(QCoreApplication.translate("DialogSettings", u"\u6ce2\u7279\u7387", None))
        self.label_37.setText(QCoreApplication.translate("DialogSettings", u"\u65e0\u7ebf\u5730\u5740", None))
        self.lineEditAddr1.setText(QCoreApplication.translate("DialogSettings", u"AA", None))
        self.label_38.setText(QCoreApplication.translate("DialogSettings", u":", None))
        self.lineEditAddr2.setText(QCoreApplication.translate("DialogSettings", u"AA", None))
        self.label_39.setText(QCoreApplication.translate("DialogSettings", u":", None))
        self.lineEditAddr3.setText(QCoreApplication.translate("DialogSettings", u"AA", None))
        self.label_41.setText(QCoreApplication.translate("DialogSettings", u":", None))
        self.lineEditAddr4.setText(QCoreApplication.translate("DialogSettings", u"AA", None))
        self.label_40.setText(QCoreApplication.translate("DialogSettings", u":", None))
        self.lineEditAddr5.setText(QCoreApplication.translate("DialogSettings", u"AA", None))
        self.label_43.setText(QCoreApplication.translate("DialogSettings", u"\u65e0\u7ebf\u9891\u9053", None))
        self.spinBoxFreq.setSuffix(QCoreApplication.translate("DialogSettings", u"Mhz", None))
        self.label_42.setText(QCoreApplication.translate("DialogSettings", u"\u65e0\u7ebf\u529f\u7387", None))
        self.comboBoxPower.setItemText(0, QCoreApplication.translate("DialogSettings", u"7dBm", None))
        self.comboBoxPower.setItemText(1, QCoreApplication.translate("DialogSettings", u"4dBm", None))
        self.comboBoxPower.setItemText(2, QCoreApplication.translate("DialogSettings", u"3dBm", None))
        self.comboBoxPower.setItemText(3, QCoreApplication.translate("DialogSettings", u"1dBm", None))
        self.comboBoxPower.setItemText(4, QCoreApplication.translate("DialogSettings", u"0dBm", None))
        self.comboBoxPower.setItemText(5, QCoreApplication.translate("DialogSettings", u"-4dBm", None))
        self.comboBoxPower.setItemText(6, QCoreApplication.translate("DialogSettings", u"-6dBm", None))
        self.comboBoxPower.setItemText(7, QCoreApplication.translate("DialogSettings", u"-12dBm", None))

        self.label_44.setText(QCoreApplication.translate("DialogSettings", u"- MDP-P906 -", None))
        self.btnMatch.setText(QCoreApplication.translate("DialogSettings", u"\u81ea\u52a8\u914d\u5bf9", None))
        self.lineEditIdcode.setText("")
        self.lineEditIdcode.setPlaceholderText(QCoreApplication.translate("DialogSettings", u"IDCODE", None))
        self.label_46.setText(QCoreApplication.translate("DialogSettings", u"\u6eda\u8f6e\u989c\u8272", None))
        self.lineEditColor.setText(QCoreApplication.translate("DialogSettings", u"#66CCFF", None))
        self.lineEditColor.setPlaceholderText(QCoreApplication.translate("DialogSettings", u"#RRGGBB", None))
        self.label_47.setText(QCoreApplication.translate("DialogSettings", u"M01 \u901a\u9053", None))
        self.spinBoxM01.setPrefix(QCoreApplication.translate("DialogSettings", u"CH-", None))
        self.spinBoxM01.setSuffix("")
        self.label_48.setText(QCoreApplication.translate("DialogSettings", u"\u8fde\u63a5\u6307\u793a\u706f", None))
        self.comboBoxBlink.setItemText(0, QCoreApplication.translate("DialogSettings", u"\u5e38\u4eae", None))
        self.comboBoxBlink.setItemText(1, QCoreApplication.translate("DialogSettings", u"\u95ea\u70c1", None))

        self.btnSave.setText(QCoreApplication.translate("DialogSettings", u"\u5e94\u7528 / Apply", None))
        self.btnOk.setText(QCoreApplication.translate("DialogSettings", u"\u786e\u5b9a / OK", None))
    # retranslateUi


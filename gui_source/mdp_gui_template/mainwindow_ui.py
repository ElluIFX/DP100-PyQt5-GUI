# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractSpinBox, QApplication, QCheckBox,
    QComboBox, QDoubleSpinBox, QFrame, QHBoxLayout,
    QLCDNumber, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QTabWidget, QVBoxLayout,
    QWidget)

from pyqtgraph import PlotWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1134, 797)
        MainWindow.setMinimumSize(QSize(0, 0))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_8 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_36 = QLabel(self.centralwidget)
        self.label_36.setObjectName(u"label_36")
        self.label_36.setMinimumSize(QSize(0, 20))
        font = QFont()
        font.setFamilies([u"Sarasa Fixed SC SemiBold"])
        self.label_36.setFont(font)

        self.verticalLayout_8.addWidget(self.label_36)

        self.frameLcd = QFrame(self.centralwidget)
        self.frameLcd.setObjectName(u"frameLcd")
        self.frameLcd.setFont(font)
        self.frameLcd.setFrameShape(QFrame.StyledPanel)
        self.frameLcd.setFrameShadow(QFrame.Plain)
        self.frameLcd.setLineWidth(2)
        self.verticalLayout_19 = QVBoxLayout(self.frameLcd)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setSpacing(8)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frameLcd)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 50))
        font1 = QFont()
        font1.setFamilies([u"Sarasa Fixed SC SemiBold"])
        font1.setPointSize(14)
        self.label.setFont(font1)
        self.label.setScaledContents(False)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMargin(6)

        self.horizontalLayout.addWidget(self.label)

        self.lcdVoltage = QLCDNumber(self.frameLcd)
        self.lcdVoltage.setObjectName(u"lcdVoltage")
        self.lcdVoltage.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lcdVoltage.sizePolicy().hasHeightForWidth())
        self.lcdVoltage.setSizePolicy(sizePolicy)
        self.lcdVoltage.setMaximumSize(QSize(280, 16777215))
        font2 = QFont()
        font2.setFamilies([u"Sarasa Fixed SC SemiBold"])
        font2.setBold(False)
        self.lcdVoltage.setFont(font2)
        self.lcdVoltage.setFrameShape(QFrame.Box)
        self.lcdVoltage.setFrameShadow(QFrame.Plain)
        self.lcdVoltage.setSmallDecimalPoint(True)
        self.lcdVoltage.setDigitCount(6)
        self.lcdVoltage.setMode(QLCDNumber.Dec)
        self.lcdVoltage.setSegmentStyle(QLCDNumber.Flat)
        self.lcdVoltage.setProperty("value", 0.000000000000000)
        self.lcdVoltage.setProperty("intValue", 0)

        self.horizontalLayout.addWidget(self.lcdVoltage)

        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 5)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.frameLcd)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(0, 50))
        self.label_2.setFont(font1)
        self.label_2.setScaledContents(False)
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setMargin(6)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lcdCurrent = QLCDNumber(self.frameLcd)
        self.lcdCurrent.setObjectName(u"lcdCurrent")
        sizePolicy.setHeightForWidth(self.lcdCurrent.sizePolicy().hasHeightForWidth())
        self.lcdCurrent.setSizePolicy(sizePolicy)
        self.lcdCurrent.setMaximumSize(QSize(280, 16777215))
        self.lcdCurrent.setFont(font)
        self.lcdCurrent.setFrameShape(QFrame.Box)
        self.lcdCurrent.setFrameShadow(QFrame.Plain)
        self.lcdCurrent.setSmallDecimalPoint(True)
        self.lcdCurrent.setDigitCount(6)
        self.lcdCurrent.setSegmentStyle(QLCDNumber.Flat)
        self.lcdCurrent.setProperty("value", 0.000000000000000)
        self.lcdCurrent.setProperty("intValue", 0)

        self.horizontalLayout_2.addWidget(self.lcdCurrent)

        self.horizontalLayout_2.setStretch(0, 2)
        self.horizontalLayout_2.setStretch(1, 5)

        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.horizontalLayout_7.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.frameLcd)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font1)
        self.label_3.setScaledContents(False)
        self.label_3.setAlignment(Qt.AlignCenter)
        self.label_3.setMargin(6)

        self.horizontalLayout_3.addWidget(self.label_3)

        self.lcdPower = QLCDNumber(self.frameLcd)
        self.lcdPower.setObjectName(u"lcdPower")
        sizePolicy.setHeightForWidth(self.lcdPower.sizePolicy().hasHeightForWidth())
        self.lcdPower.setSizePolicy(sizePolicy)
        self.lcdPower.setMaximumSize(QSize(280, 16777215))
        self.lcdPower.setFont(font)
        self.lcdPower.setFrameShape(QFrame.Box)
        self.lcdPower.setFrameShadow(QFrame.Plain)
        self.lcdPower.setSmallDecimalPoint(True)
        self.lcdPower.setDigitCount(6)
        self.lcdPower.setSegmentStyle(QLCDNumber.Flat)
        self.lcdPower.setProperty("value", 0.000000000000000)
        self.lcdPower.setProperty("intValue", 0)

        self.horizontalLayout_3.addWidget(self.lcdPower)

        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 5)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(self.frameLcd)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font1)
        self.label_4.setScaledContents(False)
        self.label_4.setAlignment(Qt.AlignCenter)
        self.label_4.setMargin(6)
        self.label_4.setIndent(-1)

        self.horizontalLayout_4.addWidget(self.label_4)

        self.lcdEnerge = QLCDNumber(self.frameLcd)
        self.lcdEnerge.setObjectName(u"lcdEnerge")
        sizePolicy.setHeightForWidth(self.lcdEnerge.sizePolicy().hasHeightForWidth())
        self.lcdEnerge.setSizePolicy(sizePolicy)
        self.lcdEnerge.setMaximumSize(QSize(280, 16777215))
        self.lcdEnerge.setFont(font)
        self.lcdEnerge.setFrameShape(QFrame.Box)
        self.lcdEnerge.setFrameShadow(QFrame.Plain)
        self.lcdEnerge.setSmallDecimalPoint(True)
        self.lcdEnerge.setDigitCount(6)
        self.lcdEnerge.setSegmentStyle(QLCDNumber.Flat)
        self.lcdEnerge.setProperty("value", 0.000000000000000)
        self.lcdEnerge.setProperty("intValue", 0)

        self.horizontalLayout_4.addWidget(self.lcdEnerge)

        self.horizontalLayout_4.setStretch(0, 2)
        self.horizontalLayout_4.setStretch(1, 5)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_7.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(10)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_5 = QLabel(self.frameLcd)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font1)
        self.label_5.setScaledContents(False)
        self.label_5.setAlignment(Qt.AlignCenter)
        self.label_5.setMargin(6)

        self.horizontalLayout_5.addWidget(self.label_5)

        self.lcdAvgPower = QLCDNumber(self.frameLcd)
        self.lcdAvgPower.setObjectName(u"lcdAvgPower")
        sizePolicy.setHeightForWidth(self.lcdAvgPower.sizePolicy().hasHeightForWidth())
        self.lcdAvgPower.setSizePolicy(sizePolicy)
        self.lcdAvgPower.setMaximumSize(QSize(280, 16777215))
        self.lcdAvgPower.setFont(font)
        self.lcdAvgPower.setFrameShape(QFrame.Box)
        self.lcdAvgPower.setFrameShadow(QFrame.Plain)
        self.lcdAvgPower.setSmallDecimalPoint(True)
        self.lcdAvgPower.setDigitCount(6)
        self.lcdAvgPower.setSegmentStyle(QLCDNumber.Flat)
        self.lcdAvgPower.setProperty("value", 0.000000000000000)
        self.lcdAvgPower.setProperty("intValue", 0)

        self.horizontalLayout_5.addWidget(self.lcdAvgPower)

        self.horizontalLayout_5.setStretch(0, 2)
        self.horizontalLayout_5.setStretch(1, 5)

        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_6 = QLabel(self.frameLcd)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font1)
        self.label_6.setScaledContents(False)
        self.label_6.setAlignment(Qt.AlignCenter)
        self.label_6.setMargin(6)

        self.horizontalLayout_6.addWidget(self.label_6)

        self.lcdResistence = QLCDNumber(self.frameLcd)
        self.lcdResistence.setObjectName(u"lcdResistence")
        sizePolicy.setHeightForWidth(self.lcdResistence.sizePolicy().hasHeightForWidth())
        self.lcdResistence.setSizePolicy(sizePolicy)
        self.lcdResistence.setMaximumSize(QSize(280, 16777215))
        self.lcdResistence.setFont(font)
        self.lcdResistence.setFrameShape(QFrame.Box)
        self.lcdResistence.setFrameShadow(QFrame.Plain)
        self.lcdResistence.setSmallDecimalPoint(True)
        self.lcdResistence.setDigitCount(6)
        self.lcdResistence.setSegmentStyle(QLCDNumber.Flat)
        self.lcdResistence.setProperty("value", 0.000000000000000)
        self.lcdResistence.setProperty("intValue", 0)

        self.horizontalLayout_6.addWidget(self.lcdResistence)

        self.horizontalLayout_6.setStretch(0, 2)
        self.horizontalLayout_6.setStretch(1, 5)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)


        self.horizontalLayout_7.addLayout(self.verticalLayout_3)

        self.horizontalLayout_7.setStretch(0, 1)
        self.horizontalLayout_7.setStretch(1, 1)
        self.horizontalLayout_7.setStretch(2, 1)

        self.verticalLayout_19.addLayout(self.horizontalLayout_7)


        self.verticalLayout_8.addWidget(self.frameLcd)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setSpacing(6)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(-1, -1, 0, -1)
        self.frameOutputSetting = QFrame(self.centralwidget)
        self.frameOutputSetting.setObjectName(u"frameOutputSetting")
        self.frameOutputSetting.setEnabled(True)
        self.frameOutputSetting.setFont(font)
        self.frameOutputSetting.setFrameShape(QFrame.StyledPanel)
        self.frameOutputSetting.setFrameShadow(QFrame.Plain)
        self.frameOutputSetting.setLineWidth(1)
        self.verticalLayout_11 = QVBoxLayout(self.frameOutputSetting)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_12 = QLabel(self.frameOutputSetting)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setMinimumSize(QSize(206, 22))
        font3 = QFont()
        font3.setFamilies([u"Sarasa Fixed SC SemiBold"])
        font3.setPointSize(10)
        font3.setItalic(False)
        self.label_12.setFont(font3)
        self.label_12.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_12)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_26 = QHBoxLayout()
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.horizontalLayout_26.setContentsMargins(-1, -1, -1, 0)
        self.labelState = QLabel(self.frameOutputSetting)
        self.labelState.setObjectName(u"labelState")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.labelState.sizePolicy().hasHeightForWidth())
        self.labelState.setSizePolicy(sizePolicy1)
        font4 = QFont()
        font4.setFamilies([u"Sarasa Fixed SC SemiBold"])
        font4.setPointSize(10)
        self.labelState.setFont(font4)
        self.labelState.setAlignment(Qt.AlignCenter)
        self.labelState.setMargin(6)

        self.horizontalLayout_26.addWidget(self.labelState)

        self.checkBoxQuickset = QCheckBox(self.frameOutputSetting)
        self.checkBoxQuickset.setObjectName(u"checkBoxQuickset")
        self.checkBoxQuickset.setFont(font)

        self.horizontalLayout_26.addWidget(self.checkBoxQuickset)

        self.btnOutput = QPushButton(self.frameOutputSetting)
        self.btnOutput.setObjectName(u"btnOutput")
        self.btnOutput.setMinimumSize(QSize(96, 32))
        self.btnOutput.setMaximumSize(QSize(96, 16777215))
        font5 = QFont()
        font5.setFamilies([u"Sarasa Fixed SC SemiBold"])
        font5.setPointSize(11)
        font5.setBold(True)
        self.btnOutput.setFont(font5)

        self.horizontalLayout_26.addWidget(self.btnOutput)


        self.verticalLayout_4.addLayout(self.horizontalLayout_26)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_7 = QLabel(self.frameOutputSetting)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(0, 35))
        self.label_7.setFont(font4)
        self.label_7.setFocusPolicy(Qt.ClickFocus)
        self.label_7.setAcceptDrops(False)
        self.label_7.setAlignment(Qt.AlignCenter)
        self.label_7.setMargin(6)

        self.horizontalLayout_8.addWidget(self.label_7)

        self.spinBoxVoltage = QDoubleSpinBox(self.frameOutputSetting)
        self.spinBoxVoltage.setObjectName(u"spinBoxVoltage")
        self.spinBoxVoltage.setMinimumSize(QSize(0, 24))
        self.spinBoxVoltage.setFont(font4)
        self.spinBoxVoltage.setAlignment(Qt.AlignCenter)
        self.spinBoxVoltage.setDecimals(3)
        self.spinBoxVoltage.setMinimum(0.000000000000000)
        self.spinBoxVoltage.setMaximum(30.000000000000000)
        self.spinBoxVoltage.setSingleStep(0.100000000000000)
        self.spinBoxVoltage.setStepType(QAbstractSpinBox.DefaultStepType)

        self.horizontalLayout_8.addWidget(self.spinBoxVoltage)

        self.horizontalLayout_8.setStretch(0, 2)
        self.horizontalLayout_8.setStretch(1, 3)

        self.verticalLayout_4.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_8 = QLabel(self.frameOutputSetting)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(0, 35))
        self.label_8.setFont(font4)
        self.label_8.setFocusPolicy(Qt.ClickFocus)
        self.label_8.setAlignment(Qt.AlignCenter)
        self.label_8.setMargin(6)

        self.horizontalLayout_9.addWidget(self.label_8)

        self.spinBoxCurrent = QDoubleSpinBox(self.frameOutputSetting)
        self.spinBoxCurrent.setObjectName(u"spinBoxCurrent")
        self.spinBoxCurrent.setMinimumSize(QSize(0, 24))
        self.spinBoxCurrent.setFont(font4)
        self.spinBoxCurrent.setAlignment(Qt.AlignCenter)
        self.spinBoxCurrent.setDecimals(3)
        self.spinBoxCurrent.setMinimum(0.000000000000000)
        self.spinBoxCurrent.setMaximum(10.000000000000000)
        self.spinBoxCurrent.setSingleStep(0.100000000000000)
        self.spinBoxCurrent.setStepType(QAbstractSpinBox.DefaultStepType)

        self.horizontalLayout_9.addWidget(self.spinBoxCurrent)

        self.horizontalLayout_9.setStretch(0, 2)
        self.horizontalLayout_9.setStretch(1, 3)

        self.verticalLayout_4.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_28 = QHBoxLayout()
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.horizontalLayout_28.setContentsMargins(3, 0, 3, 0)
        self.progressBarVoltage = QProgressBar(self.frameOutputSetting)
        self.progressBarVoltage.setObjectName(u"progressBarVoltage")
        self.progressBarVoltage.setMinimumSize(QSize(0, 10))
        self.progressBarVoltage.setMaximumSize(QSize(16777215, 10))
        self.progressBarVoltage.setFont(font)
        self.progressBarVoltage.setStyleSheet(u"QProgressBar::chunk {   background-color: #FF7B5E;}")
        self.progressBarVoltage.setMinimum(0)
        self.progressBarVoltage.setMaximum(1000)
        self.progressBarVoltage.setValue(0)
        self.progressBarVoltage.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.progressBarVoltage.setOrientation(Qt.Horizontal)
        self.progressBarVoltage.setInvertedAppearance(False)

        self.horizontalLayout_28.addWidget(self.progressBarVoltage)


        self.verticalLayout_4.addLayout(self.horizontalLayout_28)

        self.horizontalLayout_36 = QHBoxLayout()
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.horizontalLayout_36.setContentsMargins(3, 0, 3, 0)
        self.progressBarCurrent = QProgressBar(self.frameOutputSetting)
        self.progressBarCurrent.setObjectName(u"progressBarCurrent")
        self.progressBarCurrent.setMinimumSize(QSize(0, 10))
        self.progressBarCurrent.setMaximumSize(QSize(16777215, 10))
        self.progressBarCurrent.setFont(font)
        self.progressBarCurrent.setStyleSheet(u"QProgressBar::chunk {   background-color:#23A173;}")
        self.progressBarCurrent.setMaximum(1000)
        self.progressBarCurrent.setValue(0)
        self.progressBarCurrent.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.progressBarCurrent.setInvertedAppearance(False)

        self.horizontalLayout_36.addWidget(self.progressBarCurrent)


        self.verticalLayout_4.addLayout(self.horizontalLayout_36)


        self.verticalLayout_6.addLayout(self.verticalLayout_4)

        self.line_3 = QFrame(self.frameOutputSetting)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShadow(QFrame.Plain)
        self.line_3.setFrameShape(QFrame.HLine)

        self.verticalLayout_6.addWidget(self.line_3)

        self.label_21 = QLabel(self.frameOutputSetting)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setMinimumSize(QSize(0, 22))
        self.label_21.setFont(font4)
        self.label_21.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_21)

        self.tabWidget = QTabWidget(self.frameOutputSetting)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.tabWidget.setFont(font)
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tabWidget.setElideMode(Qt.ElideNone)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setTabsClosable(False)
        self.tabPreset = QWidget()
        self.tabPreset.setObjectName(u"tabPreset")
        self.verticalLayout_21 = QVBoxLayout(self.tabPreset)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.horizontalLayout_32 = QHBoxLayout()
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.horizontalLayout_32.setContentsMargins(10, -1, 10, -1)
        self.comboPreset = QComboBox(self.tabPreset)
        self.comboPreset.addItem("")
        self.comboPreset.addItem("")
        self.comboPreset.addItem("")
        self.comboPreset.addItem("")
        self.comboPreset.addItem("")
        self.comboPreset.addItem("")
        self.comboPreset.addItem("")
        self.comboPreset.addItem("")
        self.comboPreset.addItem("")
        self.comboPreset.addItem("")
        self.comboPreset.setObjectName(u"comboPreset")
        self.comboPreset.setMaximumSize(QSize(140, 16777215))
        self.comboPreset.setFont(font)

        self.horizontalLayout_32.addWidget(self.comboPreset)

        self.horizontalLayout_32.setStretch(0, 2)

        self.verticalLayout_21.addLayout(self.horizontalLayout_32)

        self.line = QFrame(self.tabPreset)
        self.line.setObjectName(u"line")
        self.line.setFont(font)
        self.line.setFrameShadow(QFrame.Plain)
        self.line.setLineWidth(1)
        self.line.setFrameShape(QFrame.HLine)

        self.verticalLayout_21.addWidget(self.line)

        self.scrollArea_4 = QScrollArea(self.tabPreset)
        self.scrollArea_4.setObjectName(u"scrollArea_4")
        self.scrollArea_4.setFont(font)
        self.scrollArea_4.setFrameShape(QFrame.NoFrame)
        self.scrollArea_4.setLineWidth(0)
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 165, 155))
        self.verticalLayout_20 = QVBoxLayout(self.scrollAreaWidgetContents_4)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.horizontalLayout_33 = QHBoxLayout()
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.label_34 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setMinimumSize(QSize(0, 28))
        self.label_34.setFont(font)
        self.label_34.setAlignment(Qt.AlignCenter)
        self.label_34.setMargin(6)

        self.horizontalLayout_33.addWidget(self.label_34)

        self.comboPresetEdit = QComboBox(self.scrollAreaWidgetContents_4)
        self.comboPresetEdit.addItem("")
        self.comboPresetEdit.addItem("")
        self.comboPresetEdit.addItem("")
        self.comboPresetEdit.addItem("")
        self.comboPresetEdit.addItem("")
        self.comboPresetEdit.addItem("")
        self.comboPresetEdit.addItem("")
        self.comboPresetEdit.addItem("")
        self.comboPresetEdit.addItem("")
        self.comboPresetEdit.setObjectName(u"comboPresetEdit")
        self.comboPresetEdit.setMaximumSize(QSize(80, 16777215))
        font6 = QFont()
        font6.setFamilies([u"Sarasa Fixed SC SemiBold"])
        font6.setPointSize(9)
        font6.setBold(True)
        self.comboPresetEdit.setFont(font6)

        self.horizontalLayout_33.addWidget(self.comboPresetEdit)

        self.horizontalLayout_33.setStretch(0, 1)
        self.horizontalLayout_33.setStretch(1, 2)

        self.verticalLayout_20.addLayout(self.horizontalLayout_33)

        self.horizontalLayout_29 = QHBoxLayout()
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.label_30 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setMinimumSize(QSize(0, 28))
        self.label_30.setFont(font)
        self.label_30.setAlignment(Qt.AlignCenter)
        self.label_30.setMargin(6)

        self.horizontalLayout_29.addWidget(self.label_30)

        self.spinBoxPresetVoltage = QDoubleSpinBox(self.scrollAreaWidgetContents_4)
        self.spinBoxPresetVoltage.setObjectName(u"spinBoxPresetVoltage")
        self.spinBoxPresetVoltage.setMaximumSize(QSize(80, 16777215))
        self.spinBoxPresetVoltage.setFont(font)
        self.spinBoxPresetVoltage.setAlignment(Qt.AlignCenter)
        self.spinBoxPresetVoltage.setDecimals(3)
        self.spinBoxPresetVoltage.setMinimum(0.000000000000000)
        self.spinBoxPresetVoltage.setMaximum(30.000000000000000)
        self.spinBoxPresetVoltage.setSingleStep(0.100000000000000)
        self.spinBoxPresetVoltage.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)

        self.horizontalLayout_29.addWidget(self.spinBoxPresetVoltage)

        self.horizontalLayout_29.setStretch(0, 1)
        self.horizontalLayout_29.setStretch(1, 2)

        self.verticalLayout_20.addLayout(self.horizontalLayout_29)

        self.horizontalLayout_30 = QHBoxLayout()
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.label_31 = QLabel(self.scrollAreaWidgetContents_4)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setMinimumSize(QSize(0, 28))
        self.label_31.setFont(font)
        self.label_31.setAlignment(Qt.AlignCenter)
        self.label_31.setMargin(6)

        self.horizontalLayout_30.addWidget(self.label_31)

        self.spinBoxPresetCurrent = QDoubleSpinBox(self.scrollAreaWidgetContents_4)
        self.spinBoxPresetCurrent.setObjectName(u"spinBoxPresetCurrent")
        self.spinBoxPresetCurrent.setMaximumSize(QSize(80, 16777215))
        self.spinBoxPresetCurrent.setFont(font)
        self.spinBoxPresetCurrent.setAlignment(Qt.AlignCenter)
        self.spinBoxPresetCurrent.setDecimals(3)
        self.spinBoxPresetCurrent.setMinimum(0.000000000000000)
        self.spinBoxPresetCurrent.setMaximum(10.000000000000000)
        self.spinBoxPresetCurrent.setSingleStep(0.100000000000000)
        self.spinBoxPresetCurrent.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxPresetCurrent.setValue(0.000000000000000)

        self.horizontalLayout_30.addWidget(self.spinBoxPresetCurrent)

        self.horizontalLayout_30.setStretch(0, 1)
        self.horizontalLayout_30.setStretch(1, 2)

        self.verticalLayout_20.addLayout(self.horizontalLayout_30)

        self.btnPresetSave = QPushButton(self.scrollAreaWidgetContents_4)
        self.btnPresetSave.setObjectName(u"btnPresetSave")
        self.btnPresetSave.setFont(font)

        self.verticalLayout_20.addWidget(self.btnPresetSave)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_20.addItem(self.verticalSpacer_4)

        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_4)

        self.verticalLayout_21.addWidget(self.scrollArea_4)

        self.tabWidget.addTab(self.tabPreset, "")
        self.tabPower = QWidget()
        self.tabPower.setObjectName(u"tabPower")
        self.verticalLayout_5 = QVBoxLayout(self.tabPower)
        self.verticalLayout_5.setSpacing(4)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.btnKeepPower = QPushButton(self.tabPower)
        self.btnKeepPower.setObjectName(u"btnKeepPower")

        self.verticalLayout_5.addWidget(self.btnKeepPower)

        self.scrollAreaKeepPower = QScrollArea(self.tabPower)
        self.scrollAreaKeepPower.setObjectName(u"scrollAreaKeepPower")
        self.scrollAreaKeepPower.setFrameShape(QFrame.NoFrame)
        self.scrollAreaKeepPower.setLineWidth(0)
        self.scrollAreaKeepPower.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 165, 162))
        self.verticalLayout_15 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_9 = QLabel(self.scrollAreaWidgetContents)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMinimumSize(QSize(0, 28))
        font7 = QFont()
        font7.setFamilies([u"Sarasa Fixed SC SemiBold"])
        font7.setBold(True)
        self.label_9.setFont(font7)
        self.label_9.setAlignment(Qt.AlignCenter)
        self.label_9.setMargin(6)

        self.horizontalLayout_10.addWidget(self.label_9)

        self.spinBoxKeepPowerSet = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.spinBoxKeepPowerSet.setObjectName(u"spinBoxKeepPowerSet")
        self.spinBoxKeepPowerSet.setMaximumSize(QSize(80, 16777215))
        self.spinBoxKeepPowerSet.setFont(font7)
        self.spinBoxKeepPowerSet.setAlignment(Qt.AlignCenter)
        self.spinBoxKeepPowerSet.setDecimals(2)
        self.spinBoxKeepPowerSet.setMinimum(0.000000000000000)
        self.spinBoxKeepPowerSet.setMaximum(100.000000000000000)
        self.spinBoxKeepPowerSet.setSingleStep(0.100000000000000)
        self.spinBoxKeepPowerSet.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)

        self.horizontalLayout_10.addWidget(self.spinBoxKeepPowerSet)

        self.horizontalLayout_10.setStretch(0, 1)
        self.horizontalLayout_10.setStretch(1, 2)

        self.verticalLayout_15.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_10 = QLabel(self.scrollAreaWidgetContents)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(0, 28))
        self.label_10.setFont(font7)
        self.label_10.setAlignment(Qt.AlignCenter)
        self.label_10.setMargin(6)

        self.horizontalLayout_11.addWidget(self.label_10)

        self.spinBoxKeepPowerPi = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.spinBoxKeepPowerPi.setObjectName(u"spinBoxKeepPowerPi")
        self.spinBoxKeepPowerPi.setMaximumSize(QSize(80, 16777215))
        self.spinBoxKeepPowerPi.setFont(font7)
        self.spinBoxKeepPowerPi.setAlignment(Qt.AlignCenter)
        self.spinBoxKeepPowerPi.setDecimals(2)
        self.spinBoxKeepPowerPi.setMinimum(0.000000000000000)
        self.spinBoxKeepPowerPi.setMaximum(40.000000000000000)
        self.spinBoxKeepPowerPi.setSingleStep(0.100000000000000)
        self.spinBoxKeepPowerPi.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxKeepPowerPi.setValue(2.500000000000000)

        self.horizontalLayout_11.addWidget(self.spinBoxKeepPowerPi)

        self.horizontalLayout_11.setStretch(0, 1)
        self.horizontalLayout_11.setStretch(1, 2)

        self.verticalLayout_15.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_35 = QHBoxLayout()
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.label_28 = QLabel(self.scrollAreaWidgetContents)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setMinimumSize(QSize(0, 28))
        self.label_28.setFont(font7)
        self.label_28.setAlignment(Qt.AlignCenter)
        self.label_28.setMargin(6)

        self.horizontalLayout_35.addWidget(self.label_28)

        self.spinBoxKeepPowerMaxV = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.spinBoxKeepPowerMaxV.setObjectName(u"spinBoxKeepPowerMaxV")
        self.spinBoxKeepPowerMaxV.setMaximumSize(QSize(80, 16777215))
        self.spinBoxKeepPowerMaxV.setFont(font7)
        self.spinBoxKeepPowerMaxV.setAlignment(Qt.AlignCenter)
        self.spinBoxKeepPowerMaxV.setDecimals(1)
        self.spinBoxKeepPowerMaxV.setMinimum(0.000000000000000)
        self.spinBoxKeepPowerMaxV.setMaximum(30.000000000000000)
        self.spinBoxKeepPowerMaxV.setSingleStep(0.100000000000000)
        self.spinBoxKeepPowerMaxV.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxKeepPowerMaxV.setValue(30.000000000000000)

        self.horizontalLayout_35.addWidget(self.spinBoxKeepPowerMaxV)

        self.horizontalLayout_35.setStretch(0, 1)
        self.horizontalLayout_35.setStretch(1, 2)

        self.verticalLayout_15.addLayout(self.horizontalLayout_35)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.label_19 = QLabel(self.scrollAreaWidgetContents)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setMinimumSize(QSize(0, 28))
        self.label_19.setFont(font7)
        self.label_19.setAlignment(Qt.AlignCenter)
        self.label_19.setMargin(6)

        self.horizontalLayout_19.addWidget(self.label_19)

        self.spinBoxKeepPowerLoopFreq = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.spinBoxKeepPowerLoopFreq.setObjectName(u"spinBoxKeepPowerLoopFreq")
        self.spinBoxKeepPowerLoopFreq.setMaximumSize(QSize(80, 16777215))
        self.spinBoxKeepPowerLoopFreq.setFont(font7)
        self.spinBoxKeepPowerLoopFreq.setAlignment(Qt.AlignCenter)
        self.spinBoxKeepPowerLoopFreq.setDecimals(1)
        self.spinBoxKeepPowerLoopFreq.setMinimum(0.000000000000000)
        self.spinBoxKeepPowerLoopFreq.setMaximum(100.000000000000000)
        self.spinBoxKeepPowerLoopFreq.setSingleStep(0.100000000000000)
        self.spinBoxKeepPowerLoopFreq.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxKeepPowerLoopFreq.setValue(30.000000000000000)

        self.horizontalLayout_19.addWidget(self.spinBoxKeepPowerLoopFreq)

        self.horizontalLayout_19.setStretch(0, 1)
        self.horizontalLayout_19.setStretch(1, 2)

        self.verticalLayout_15.addLayout(self.horizontalLayout_19)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer)

        self.scrollAreaKeepPower.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_5.addWidget(self.scrollAreaKeepPower)

        self.tabWidget.addTab(self.tabPower, "")
        self.tabSweep = QWidget()
        self.tabSweep.setObjectName(u"tabSweep")
        self.verticalLayout_9 = QVBoxLayout(self.tabSweep)
        self.verticalLayout_9.setSpacing(4)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.btnSweep = QPushButton(self.tabSweep)
        self.btnSweep.setObjectName(u"btnSweep")

        self.verticalLayout_9.addWidget(self.btnSweep)

        self.scrollAreaSweep = QScrollArea(self.tabSweep)
        self.scrollAreaSweep.setObjectName(u"scrollAreaSweep")
        self.scrollAreaSweep.setFrameShape(QFrame.NoFrame)
        self.scrollAreaSweep.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 165, 198))
        self.verticalLayout_16 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setSpacing(6)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_11 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMinimumSize(QSize(0, 28))
        self.label_11.setFont(font7)
        self.label_11.setAlignment(Qt.AlignCenter)
        self.label_11.setMargin(6)

        self.horizontalLayout_14.addWidget(self.label_11)

        self.comboSweepTarget = QComboBox(self.scrollAreaWidgetContents_2)
        self.comboSweepTarget.addItem("")
        self.comboSweepTarget.addItem("")
        self.comboSweepTarget.setObjectName(u"comboSweepTarget")
        self.comboSweepTarget.setMaximumSize(QSize(80, 16777215))
        self.comboSweepTarget.setFont(font7)
        self.comboSweepTarget.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)

        self.horizontalLayout_14.addWidget(self.comboSweepTarget)

        self.horizontalLayout_14.setStretch(0, 1)
        self.horizontalLayout_14.setStretch(1, 2)

        self.verticalLayout_16.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_15 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setMinimumSize(QSize(0, 28))
        self.label_15.setFont(font7)
        self.label_15.setAlignment(Qt.AlignCenter)
        self.label_15.setMargin(6)

        self.horizontalLayout_15.addWidget(self.label_15)

        self.spinBoxSweepStart = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.spinBoxSweepStart.setObjectName(u"spinBoxSweepStart")
        self.spinBoxSweepStart.setMaximumSize(QSize(80, 16777215))
        self.spinBoxSweepStart.setFont(font7)
        self.spinBoxSweepStart.setAlignment(Qt.AlignCenter)
        self.spinBoxSweepStart.setDecimals(3)
        self.spinBoxSweepStart.setMinimum(0.000000000000000)
        self.spinBoxSweepStart.setMaximum(100.000000000000000)
        self.spinBoxSweepStart.setSingleStep(0.100000000000000)
        self.spinBoxSweepStart.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)

        self.horizontalLayout_15.addWidget(self.spinBoxSweepStart)

        self.horizontalLayout_15.setStretch(0, 1)
        self.horizontalLayout_15.setStretch(1, 2)

        self.verticalLayout_16.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.label_16 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setMinimumSize(QSize(0, 28))
        self.label_16.setFont(font7)
        self.label_16.setAlignment(Qt.AlignCenter)
        self.label_16.setMargin(6)

        self.horizontalLayout_16.addWidget(self.label_16)

        self.spinBoxSweepStop = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.spinBoxSweepStop.setObjectName(u"spinBoxSweepStop")
        self.spinBoxSweepStop.setMaximumSize(QSize(80, 16777215))
        self.spinBoxSweepStop.setFont(font7)
        self.spinBoxSweepStop.setAlignment(Qt.AlignCenter)
        self.spinBoxSweepStop.setDecimals(3)
        self.spinBoxSweepStop.setMinimum(0.000000000000000)
        self.spinBoxSweepStop.setMaximum(100.000000000000000)
        self.spinBoxSweepStop.setSingleStep(0.100000000000000)
        self.spinBoxSweepStop.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxSweepStop.setValue(5.000000000000000)

        self.horizontalLayout_16.addWidget(self.spinBoxSweepStop)

        self.horizontalLayout_16.setStretch(0, 1)
        self.horizontalLayout_16.setStretch(1, 2)

        self.verticalLayout_16.addLayout(self.horizontalLayout_16)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.label_17 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setMinimumSize(QSize(0, 28))
        self.label_17.setFont(font7)
        self.label_17.setAlignment(Qt.AlignCenter)
        self.label_17.setMargin(6)

        self.horizontalLayout_17.addWidget(self.label_17)

        self.spinBoxSweepStep = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.spinBoxSweepStep.setObjectName(u"spinBoxSweepStep")
        self.spinBoxSweepStep.setMaximumSize(QSize(80, 16777215))
        self.spinBoxSweepStep.setFont(font7)
        self.spinBoxSweepStep.setAlignment(Qt.AlignCenter)
        self.spinBoxSweepStep.setDecimals(3)
        self.spinBoxSweepStep.setMinimum(0.001000000000000)
        self.spinBoxSweepStep.setMaximum(100.000000000000000)
        self.spinBoxSweepStep.setSingleStep(0.100000000000000)
        self.spinBoxSweepStep.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxSweepStep.setValue(0.001000000000000)

        self.horizontalLayout_17.addWidget(self.spinBoxSweepStep)

        self.horizontalLayout_17.setStretch(0, 1)
        self.horizontalLayout_17.setStretch(1, 2)

        self.verticalLayout_16.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.label_18 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setMinimumSize(QSize(0, 28))
        self.label_18.setFont(font7)
        self.label_18.setAlignment(Qt.AlignCenter)
        self.label_18.setMargin(6)

        self.horizontalLayout_18.addWidget(self.label_18)

        self.spinBoxSweepDelay = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.spinBoxSweepDelay.setObjectName(u"spinBoxSweepDelay")
        self.spinBoxSweepDelay.setMaximumSize(QSize(80, 16777215))
        self.spinBoxSweepDelay.setFont(font7)
        self.spinBoxSweepDelay.setAlignment(Qt.AlignCenter)
        self.spinBoxSweepDelay.setDecimals(2)
        self.spinBoxSweepDelay.setMinimum(0.010000000000000)
        self.spinBoxSweepDelay.setMaximum(999999.000000000000000)
        self.spinBoxSweepDelay.setSingleStep(0.100000000000000)
        self.spinBoxSweepDelay.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)

        self.horizontalLayout_18.addWidget(self.spinBoxSweepDelay)

        self.horizontalLayout_18.setStretch(0, 1)
        self.horizontalLayout_18.setStretch(1, 2)

        self.verticalLayout_16.addLayout(self.horizontalLayout_18)

        self.verticalSpacer_2 = QSpacerItem(20, 36, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_2)

        self.scrollAreaSweep.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_9.addWidget(self.scrollAreaSweep)

        self.tabWidget.addTab(self.tabSweep, "")
        self.tabWaveGen = QWidget()
        self.tabWaveGen.setObjectName(u"tabWaveGen")
        self.verticalLayout_10 = QVBoxLayout(self.tabWaveGen)
        self.verticalLayout_10.setSpacing(4)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.btnWaveGen = QPushButton(self.tabWaveGen)
        self.btnWaveGen.setObjectName(u"btnWaveGen")

        self.verticalLayout_10.addWidget(self.btnWaveGen)

        self.scrollAreaWaveGen = QScrollArea(self.tabWaveGen)
        self.scrollAreaWaveGen.setObjectName(u"scrollAreaWaveGen")
        self.scrollAreaWaveGen.setFrameShape(QFrame.NoFrame)
        self.scrollAreaWaveGen.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 165, 198))
        self.verticalLayout_17 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.label_23 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setMinimumSize(QSize(0, 28))
        self.label_23.setFont(font7)
        self.label_23.setAlignment(Qt.AlignCenter)
        self.label_23.setMargin(6)

        self.horizontalLayout_23.addWidget(self.label_23)

        self.comboWaveGenType = QComboBox(self.scrollAreaWidgetContents_3)
        self.comboWaveGenType.addItem("")
        self.comboWaveGenType.addItem("")
        self.comboWaveGenType.addItem("")
        self.comboWaveGenType.addItem("")
        self.comboWaveGenType.addItem("")
        self.comboWaveGenType.setObjectName(u"comboWaveGenType")
        self.comboWaveGenType.setMaximumSize(QSize(80, 16777215))
        self.comboWaveGenType.setFont(font7)

        self.horizontalLayout_23.addWidget(self.comboWaveGenType)

        self.horizontalLayout_23.setStretch(0, 1)
        self.horizontalLayout_23.setStretch(1, 2)

        self.verticalLayout_17.addLayout(self.horizontalLayout_23)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.label_22 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setMinimumSize(QSize(0, 28))
        self.label_22.setFont(font7)
        self.label_22.setAlignment(Qt.AlignCenter)
        self.label_22.setMargin(6)

        self.horizontalLayout_22.addWidget(self.label_22)

        self.spinBoxWaveGenPeriod = QDoubleSpinBox(self.scrollAreaWidgetContents_3)
        self.spinBoxWaveGenPeriod.setObjectName(u"spinBoxWaveGenPeriod")
        self.spinBoxWaveGenPeriod.setMaximumSize(QSize(80, 16777215))
        self.spinBoxWaveGenPeriod.setFont(font7)
        self.spinBoxWaveGenPeriod.setAlignment(Qt.AlignCenter)
        self.spinBoxWaveGenPeriod.setDecimals(2)
        self.spinBoxWaveGenPeriod.setMinimum(0.000000000000000)
        self.spinBoxWaveGenPeriod.setMaximum(100.000000000000000)
        self.spinBoxWaveGenPeriod.setSingleStep(0.100000000000000)
        self.spinBoxWaveGenPeriod.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxWaveGenPeriod.setValue(1.000000000000000)

        self.horizontalLayout_22.addWidget(self.spinBoxWaveGenPeriod)

        self.horizontalLayout_22.setStretch(0, 1)
        self.horizontalLayout_22.setStretch(1, 2)

        self.verticalLayout_17.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.label_25 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setMinimumSize(QSize(0, 28))
        self.label_25.setFont(font7)
        self.label_25.setAlignment(Qt.AlignCenter)
        self.label_25.setMargin(6)

        self.horizontalLayout_25.addWidget(self.label_25)

        self.spinBoxWaveGenHigh = QDoubleSpinBox(self.scrollAreaWidgetContents_3)
        self.spinBoxWaveGenHigh.setObjectName(u"spinBoxWaveGenHigh")
        self.spinBoxWaveGenHigh.setMaximumSize(QSize(80, 16777215))
        self.spinBoxWaveGenHigh.setFont(font7)
        self.spinBoxWaveGenHigh.setAlignment(Qt.AlignCenter)
        self.spinBoxWaveGenHigh.setDecimals(3)
        self.spinBoxWaveGenHigh.setMinimum(0.000000000000000)
        self.spinBoxWaveGenHigh.setMaximum(100.000000000000000)
        self.spinBoxWaveGenHigh.setSingleStep(0.100000000000000)
        self.spinBoxWaveGenHigh.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxWaveGenHigh.setValue(5.000000000000000)

        self.horizontalLayout_25.addWidget(self.spinBoxWaveGenHigh)

        self.horizontalLayout_25.setStretch(0, 1)
        self.horizontalLayout_25.setStretch(1, 2)

        self.verticalLayout_17.addLayout(self.horizontalLayout_25)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.label_24 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setMinimumSize(QSize(0, 28))
        self.label_24.setFont(font7)
        self.label_24.setAlignment(Qt.AlignCenter)
        self.label_24.setMargin(6)

        self.horizontalLayout_24.addWidget(self.label_24)

        self.spinBoxWaveGenLow = QDoubleSpinBox(self.scrollAreaWidgetContents_3)
        self.spinBoxWaveGenLow.setObjectName(u"spinBoxWaveGenLow")
        self.spinBoxWaveGenLow.setMaximumSize(QSize(80, 16777215))
        self.spinBoxWaveGenLow.setFont(font7)
        self.spinBoxWaveGenLow.setAlignment(Qt.AlignCenter)
        self.spinBoxWaveGenLow.setDecimals(3)
        self.spinBoxWaveGenLow.setMinimum(0.000000000000000)
        self.spinBoxWaveGenLow.setMaximum(100.000000000000000)
        self.spinBoxWaveGenLow.setSingleStep(0.100000000000000)
        self.spinBoxWaveGenLow.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)

        self.horizontalLayout_24.addWidget(self.spinBoxWaveGenLow)

        self.horizontalLayout_24.setStretch(0, 1)
        self.horizontalLayout_24.setStretch(1, 2)

        self.verticalLayout_17.addLayout(self.horizontalLayout_24)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.label_20 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setMinimumSize(QSize(0, 28))
        self.label_20.setFont(font7)
        self.label_20.setAlignment(Qt.AlignCenter)
        self.label_20.setMargin(6)

        self.horizontalLayout_20.addWidget(self.label_20)

        self.spinBoxWaveGenLoopFreq = QDoubleSpinBox(self.scrollAreaWidgetContents_3)
        self.spinBoxWaveGenLoopFreq.setObjectName(u"spinBoxWaveGenLoopFreq")
        self.spinBoxWaveGenLoopFreq.setMaximumSize(QSize(80, 16777215))
        self.spinBoxWaveGenLoopFreq.setFont(font7)
        self.spinBoxWaveGenLoopFreq.setAlignment(Qt.AlignCenter)
        self.spinBoxWaveGenLoopFreq.setDecimals(1)
        self.spinBoxWaveGenLoopFreq.setMinimum(0.000000000000000)
        self.spinBoxWaveGenLoopFreq.setMaximum(100.000000000000000)
        self.spinBoxWaveGenLoopFreq.setSingleStep(0.100000000000000)
        self.spinBoxWaveGenLoopFreq.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxWaveGenLoopFreq.setValue(30.000000000000000)

        self.horizontalLayout_20.addWidget(self.spinBoxWaveGenLoopFreq)

        self.horizontalLayout_20.setStretch(0, 1)
        self.horizontalLayout_20.setStretch(1, 2)

        self.verticalLayout_17.addLayout(self.horizontalLayout_20)

        self.verticalSpacer_3 = QSpacerItem(20, 36, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_17.addItem(self.verticalSpacer_3)

        self.scrollAreaWaveGen.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout_10.addWidget(self.scrollAreaWaveGen)

        self.tabWidget.addTab(self.tabWaveGen, "")
        self.tabSeq = QWidget()
        self.tabSeq.setObjectName(u"tabSeq")
        self.verticalLayout_22 = QVBoxLayout(self.tabSeq)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.listSeq = QListWidget(self.tabSeq)
        self.listSeq.setObjectName(u"listSeq")
        sizePolicy2 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.listSeq.sizePolicy().hasHeightForWidth())
        self.listSeq.setSizePolicy(sizePolicy2)
        self.listSeq.setFrameShadow(QFrame.Plain)
        self.listSeq.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.listSeq.setDragEnabled(True)
        self.listSeq.setDragDropMode(QAbstractItemView.DragDrop)
        self.listSeq.setDefaultDropAction(Qt.MoveAction)
        self.listSeq.setAlternatingRowColors(False)
        self.listSeq.setSelectionMode(QAbstractItemView.SingleSelection)
        self.listSeq.setSortingEnabled(False)

        self.verticalLayout_22.addWidget(self.listSeq)

        self.horizontalLayout_37 = QHBoxLayout()
        self.horizontalLayout_37.setSpacing(1)
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.horizontalLayout_37.setContentsMargins(-1, -1, -1, 0)
        self.btnSeqDelay = QPushButton(self.tabSeq)
        self.btnSeqDelay.setObjectName(u"btnSeqDelay")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.btnSeqDelay.sizePolicy().hasHeightForWidth())
        self.btnSeqDelay.setSizePolicy(sizePolicy3)
        self.btnSeqDelay.setMinimumSize(QSize(0, 0))
        self.btnSeqDelay.setMaximumSize(QSize(40, 16777215))
        font8 = QFont()
        font8.setFamilies([u"Sarasa Fixed SC SemiBold"])
        font8.setPointSize(8)
        font8.setBold(True)
        self.btnSeqDelay.setFont(font8)

        self.horizontalLayout_37.addWidget(self.btnSeqDelay)

        self.btnSeqWaitTime = QPushButton(self.tabSeq)
        self.btnSeqWaitTime.setObjectName(u"btnSeqWaitTime")
        sizePolicy3.setHeightForWidth(self.btnSeqWaitTime.sizePolicy().hasHeightForWidth())
        self.btnSeqWaitTime.setSizePolicy(sizePolicy3)
        self.btnSeqWaitTime.setMinimumSize(QSize(0, 0))
        self.btnSeqWaitTime.setMaximumSize(QSize(40, 16777215))
        self.btnSeqWaitTime.setFont(font8)

        self.horizontalLayout_37.addWidget(self.btnSeqWaitTime)

        self.btnSeqVoltage = QPushButton(self.tabSeq)
        self.btnSeqVoltage.setObjectName(u"btnSeqVoltage")
        sizePolicy3.setHeightForWidth(self.btnSeqVoltage.sizePolicy().hasHeightForWidth())
        self.btnSeqVoltage.setSizePolicy(sizePolicy3)
        self.btnSeqVoltage.setMinimumSize(QSize(0, 0))
        self.btnSeqVoltage.setMaximumSize(QSize(40, 16777215))
        self.btnSeqVoltage.setFont(font8)

        self.horizontalLayout_37.addWidget(self.btnSeqVoltage)

        self.btnSeqCurrent = QPushButton(self.tabSeq)
        self.btnSeqCurrent.setObjectName(u"btnSeqCurrent")
        sizePolicy3.setHeightForWidth(self.btnSeqCurrent.sizePolicy().hasHeightForWidth())
        self.btnSeqCurrent.setSizePolicy(sizePolicy3)
        self.btnSeqCurrent.setMinimumSize(QSize(0, 0))
        self.btnSeqCurrent.setMaximumSize(QSize(40, 16777215))
        self.btnSeqCurrent.setFont(font8)

        self.horizontalLayout_37.addWidget(self.btnSeqCurrent)


        self.verticalLayout_22.addLayout(self.horizontalLayout_37)

        self.layoutSeqAction = QHBoxLayout()
        self.layoutSeqAction.setSpacing(1)
        self.layoutSeqAction.setObjectName(u"layoutSeqAction")
        self.layoutSeqAction.setContentsMargins(-1, -1, -1, 0)
        self.btnSeqSave = QPushButton(self.tabSeq)
        self.btnSeqSave.setObjectName(u"btnSeqSave")
        sizePolicy3.setHeightForWidth(self.btnSeqSave.sizePolicy().hasHeightForWidth())
        self.btnSeqSave.setSizePolicy(sizePolicy3)
        self.btnSeqSave.setMinimumSize(QSize(0, 0))
        self.btnSeqSave.setMaximumSize(QSize(40, 16777215))
        self.btnSeqSave.setFont(font8)

        self.layoutSeqAction.addWidget(self.btnSeqSave)

        self.btnSeqLoad = QPushButton(self.tabSeq)
        self.btnSeqLoad.setObjectName(u"btnSeqLoad")
        sizePolicy3.setHeightForWidth(self.btnSeqLoad.sizePolicy().hasHeightForWidth())
        self.btnSeqLoad.setSizePolicy(sizePolicy3)
        self.btnSeqLoad.setMinimumSize(QSize(0, 0))
        self.btnSeqLoad.setMaximumSize(QSize(40, 16777215))
        self.btnSeqLoad.setFont(font8)

        self.layoutSeqAction.addWidget(self.btnSeqLoad)

        self.btnSeqSingle = QPushButton(self.tabSeq)
        self.btnSeqSingle.setObjectName(u"btnSeqSingle")
        sizePolicy3.setHeightForWidth(self.btnSeqSingle.sizePolicy().hasHeightForWidth())
        self.btnSeqSingle.setSizePolicy(sizePolicy3)
        self.btnSeqSingle.setMinimumSize(QSize(0, 0))
        self.btnSeqSingle.setMaximumSize(QSize(40, 16777215))
        self.btnSeqSingle.setFont(font8)

        self.layoutSeqAction.addWidget(self.btnSeqSingle)

        self.btnSeqLoop = QPushButton(self.tabSeq)
        self.btnSeqLoop.setObjectName(u"btnSeqLoop")
        sizePolicy3.setHeightForWidth(self.btnSeqLoop.sizePolicy().hasHeightForWidth())
        self.btnSeqLoop.setSizePolicy(sizePolicy3)
        self.btnSeqLoop.setMinimumSize(QSize(0, 0))
        self.btnSeqLoop.setMaximumSize(QSize(40, 16777215))
        self.btnSeqLoop.setFont(font8)

        self.layoutSeqAction.addWidget(self.btnSeqLoop)


        self.verticalLayout_22.addLayout(self.layoutSeqAction)

        self.horizontalLayout_38 = QHBoxLayout()
        self.horizontalLayout_38.setSpacing(1)
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.horizontalLayout_38.setContentsMargins(-1, -1, -1, 0)

        self.verticalLayout_22.addLayout(self.horizontalLayout_38)

        self.btnSeqStop = QPushButton(self.tabSeq)
        self.btnSeqStop.setObjectName(u"btnSeqStop")
        sizePolicy3.setHeightForWidth(self.btnSeqStop.sizePolicy().hasHeightForWidth())
        self.btnSeqStop.setSizePolicy(sizePolicy3)
        self.btnSeqStop.setMinimumSize(QSize(0, 0))
        self.btnSeqStop.setMaximumSize(QSize(999, 16777215))

        self.verticalLayout_22.addWidget(self.btnSeqStop)

        self.tabWidget.addTab(self.tabSeq, "")

        self.verticalLayout_6.addWidget(self.tabWidget)


        self.verticalLayout_11.addLayout(self.verticalLayout_6)


        self.verticalLayout_12.addWidget(self.frameOutputSetting)

        self.frameSystemState = QFrame(self.centralwidget)
        self.frameSystemState.setObjectName(u"frameSystemState")
        self.frameSystemState.setMinimumSize(QSize(0, 0))
        self.frameSystemState.setFont(font)
        self.frameSystemState.setFrameShape(QFrame.StyledPanel)
        self.frameSystemState.setFrameShadow(QFrame.Plain)
        self.verticalLayout_23 = QVBoxLayout(self.frameSystemState)
        self.verticalLayout_23.setSpacing(3)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout_24 = QVBoxLayout()
        self.verticalLayout_24.setSpacing(0)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.label_27 = QLabel(self.frameSystemState)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setMinimumSize(QSize(206, 22))
        self.label_27.setFont(font3)
        self.label_27.setAlignment(Qt.AlignCenter)

        self.verticalLayout_24.addWidget(self.label_27)

        self.horizontalLayout_40 = QHBoxLayout()
        self.horizontalLayout_40.setObjectName(u"horizontalLayout_40")
        self.horizontalLayout_40.setContentsMargins(-1, 0, -1, -1)
        self.labelComSpeed = QLabel(self.frameSystemState)
        self.labelComSpeed.setObjectName(u"labelComSpeed")
        self.labelComSpeed.setFont(font)
        self.labelComSpeed.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_40.addWidget(self.labelComSpeed)

        self.labelErrRate = QLabel(self.frameSystemState)
        self.labelErrRate.setObjectName(u"labelErrRate")
        self.labelErrRate.setFont(font)
        self.labelErrRate.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_40.addWidget(self.labelErrRate)


        self.verticalLayout_24.addLayout(self.horizontalLayout_40)

        self.horizontalLayout_31 = QHBoxLayout()
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.horizontalLayout_31.setContentsMargins(-1, 0, -1, -1)
        self.labelError = QLabel(self.frameSystemState)
        self.labelError.setObjectName(u"labelError")
        self.labelError.setFont(font)
        self.labelError.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_31.addWidget(self.labelError)

        self.labelInputVals = QLabel(self.frameSystemState)
        self.labelInputVals.setObjectName(u"labelInputVals")
        self.labelInputVals.setFont(font)
        self.labelInputVals.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_31.addWidget(self.labelInputVals)


        self.verticalLayout_24.addLayout(self.horizontalLayout_31)

        self.horizontalLayout_34 = QHBoxLayout()
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.horizontalLayout_34.setContentsMargins(-1, 0, -1, -1)
        self.labelLockState = QLabel(self.frameSystemState)
        self.labelLockState.setObjectName(u"labelLockState")
        self.labelLockState.setFont(font)
        self.labelLockState.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_34.addWidget(self.labelLockState)

        self.labelTemperature = QLabel(self.frameSystemState)
        self.labelTemperature.setObjectName(u"labelTemperature")
        self.labelTemperature.setFont(font)
        self.labelTemperature.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_34.addWidget(self.labelTemperature)


        self.verticalLayout_24.addLayout(self.horizontalLayout_34)


        self.verticalLayout_23.addLayout(self.verticalLayout_24)


        self.verticalLayout_12.addWidget(self.frameSystemState)

        self.frameSystemSetting = QFrame(self.centralwidget)
        self.frameSystemSetting.setObjectName(u"frameSystemSetting")
        self.frameSystemSetting.setMinimumSize(QSize(0, 0))
        self.frameSystemSetting.setFont(font)
        self.frameSystemSetting.setFrameShape(QFrame.StyledPanel)
        self.frameSystemSetting.setFrameShadow(QFrame.Plain)
        self.verticalLayout_13 = QVBoxLayout(self.frameSystemSetting)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setSpacing(3)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalLayout_21.setContentsMargins(-1, 0, -1, -1)
        self.btnGraphics = QPushButton(self.frameSystemSetting)
        self.btnGraphics.setObjectName(u"btnGraphics")
        self.btnGraphics.setMinimumSize(QSize(0, 30))
        self.btnGraphics.setMaximumSize(QSize(999, 16777215))
        self.btnGraphics.setFont(font)

        self.horizontalLayout_21.addWidget(self.btnGraphics)

        self.btnSettings = QPushButton(self.frameSystemSetting)
        self.btnSettings.setObjectName(u"btnSettings")
        self.btnSettings.setMinimumSize(QSize(0, 30))
        self.btnSettings.setMaximumSize(QSize(999, 16777215))
        self.btnSettings.setFont(font)

        self.horizontalLayout_21.addWidget(self.btnSettings)


        self.verticalLayout_14.addLayout(self.horizontalLayout_21)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.labelConnectState = QLabel(self.frameSystemSetting)
        self.labelConnectState.setObjectName(u"labelConnectState")
        font9 = QFont()
        font9.setFamilies([u"Sarasa Fixed SC SemiBold"])
        font9.setBold(False)
        font9.setItalic(False)
        self.labelConnectState.setFont(font9)
        self.labelConnectState.setTextFormat(Qt.AutoText)
        self.labelConnectState.setAlignment(Qt.AlignCenter)
        self.labelConnectState.setMargin(3)

        self.horizontalLayout_12.addWidget(self.labelConnectState)

        self.btnConnect = QPushButton(self.frameSystemSetting)
        self.btnConnect.setObjectName(u"btnConnect")
        self.btnConnect.setMinimumSize(QSize(0, 30))
        self.btnConnect.setFont(font)

        self.horizontalLayout_12.addWidget(self.btnConnect)

        self.horizontalLayout_12.setStretch(0, 1)
        self.horizontalLayout_12.setStretch(1, 1)

        self.verticalLayout_14.addLayout(self.horizontalLayout_12)


        self.verticalLayout_13.addLayout(self.verticalLayout_14)


        self.verticalLayout_12.addWidget(self.frameSystemSetting)

        self.verticalLayout_12.setStretch(0, 1)

        self.horizontalLayout_13.addLayout(self.verticalLayout_12)

        self.frameGraph = QFrame(self.centralwidget)
        self.frameGraph.setObjectName(u"frameGraph")
        self.frameGraph.setEnabled(True)
        self.frameGraph.setFont(font)
        self.frameGraph.setFrameShape(QFrame.StyledPanel)
        self.frameGraph.setFrameShadow(QFrame.Plain)
        self.frameGraph.setLineWidth(2)
        self.verticalLayout_18 = QVBoxLayout(self.frameGraph)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setSpacing(6)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(3, 0, 3, 6)
        self.label_14 = QLabel(self.frameGraph)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setMinimumSize(QSize(500, 22))
        self.label_14.setFont(font3)
        self.label_14.setAlignment(Qt.AlignCenter)

        self.verticalLayout_7.addWidget(self.label_14)

        self.horizontalLayout_27 = QHBoxLayout()
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.horizontalLayout_27.setContentsMargins(-1, 2, -1, 2)
        self.label_13 = QLabel(self.frameGraph)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFont(font)
        self.label_13.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_27.addWidget(self.label_13)

        self.comboGraph1Data = QComboBox(self.frameGraph)
        self.comboGraph1Data.addItem("")
        self.comboGraph1Data.addItem("")
        self.comboGraph1Data.addItem("")
        self.comboGraph1Data.addItem("")
        self.comboGraph1Data.addItem("")
        self.comboGraph1Data.setObjectName(u"comboGraph1Data")
        self.comboGraph1Data.setMinimumSize(QSize(60, 0))
        self.comboGraph1Data.setMaximumSize(QSize(80, 16777215))
        self.comboGraph1Data.setFont(font)

        self.horizontalLayout_27.addWidget(self.comboGraph1Data)

        self.comboGraph2Data = QComboBox(self.frameGraph)
        self.comboGraph2Data.addItem("")
        self.comboGraph2Data.addItem("")
        self.comboGraph2Data.addItem("")
        self.comboGraph2Data.addItem("")
        self.comboGraph2Data.addItem("")
        self.comboGraph2Data.setObjectName(u"comboGraph2Data")
        self.comboGraph2Data.setMinimumSize(QSize(60, 0))
        self.comboGraph2Data.setMaximumSize(QSize(80, 16777215))
        self.comboGraph2Data.setFont(font)

        self.horizontalLayout_27.addWidget(self.comboGraph2Data)

        self.label_29 = QLabel(self.frameGraph)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setMinimumSize(QSize(50, 0))
        self.label_29.setFont(font)
        self.label_29.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_27.addWidget(self.label_29)

        self.comboDataFps = QComboBox(self.frameGraph)
        self.comboDataFps.addItem("")
        self.comboDataFps.addItem("")
        self.comboDataFps.addItem("")
        self.comboDataFps.addItem("")
        self.comboDataFps.addItem("")
        self.comboDataFps.addItem("")
        self.comboDataFps.addItem("")
        self.comboDataFps.addItem("")
        self.comboDataFps.addItem("")
        self.comboDataFps.addItem("")
        self.comboDataFps.setObjectName(u"comboDataFps")
        self.comboDataFps.setMinimumSize(QSize(60, 0))
        self.comboDataFps.setMaximumSize(QSize(55, 16777215))
        self.comboDataFps.setFont(font)

        self.horizontalLayout_27.addWidget(self.comboDataFps)

        self.labelFps = QLabel(self.frameGraph)
        self.labelFps.setObjectName(u"labelFps")
        self.labelFps.setMinimumSize(QSize(50, 0))
        self.labelFps.setFont(font)
        self.labelFps.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_27.addWidget(self.labelFps)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_27.addItem(self.horizontalSpacer)

        self.btnGraphRecord = QPushButton(self.frameGraph)
        self.btnGraphRecord.setObjectName(u"btnGraphRecord")
        self.btnGraphRecord.setMaximumSize(QSize(60, 16777215))
        self.btnGraphRecord.setFont(font)

        self.horizontalLayout_27.addWidget(self.btnGraphRecord)

        self.btnGraphAutoScale = QPushButton(self.frameGraph)
        self.btnGraphAutoScale.setObjectName(u"btnGraphAutoScale")
        self.btnGraphAutoScale.setMaximumSize(QSize(60, 16777215))
        self.btnGraphAutoScale.setFont(font)

        self.horizontalLayout_27.addWidget(self.btnGraphAutoScale)

        self.btnGraphKeep = QPushButton(self.frameGraph)
        self.btnGraphKeep.setObjectName(u"btnGraphKeep")
        self.btnGraphKeep.setMaximumSize(QSize(60, 16777215))
        self.btnGraphKeep.setFont(font)

        self.horizontalLayout_27.addWidget(self.btnGraphKeep)

        self.btnGraphClear = QPushButton(self.frameGraph)
        self.btnGraphClear.setObjectName(u"btnGraphClear")
        self.btnGraphClear.setMaximumSize(QSize(60, 16777215))
        self.btnGraphClear.setFont(font)

        self.horizontalLayout_27.addWidget(self.btnGraphClear)

        self.btnRecordClear = QPushButton(self.frameGraph)
        self.btnRecordClear.setObjectName(u"btnRecordClear")
        self.btnRecordClear.setMaximumSize(QSize(60, 16777215))
        self.btnRecordClear.setFont(font)

        self.horizontalLayout_27.addWidget(self.btnRecordClear)


        self.verticalLayout_7.addLayout(self.horizontalLayout_27)

        self.widgetGraph1 = PlotWidget(self.frameGraph)
        self.widgetGraph1.setObjectName(u"widgetGraph1")
        self.widgetGraph1.setSizeIncrement(QSize(0, 0))
        self.widgetGraph1.setFont(font)

        self.verticalLayout_7.addWidget(self.widgetGraph1)

        self.widgetGraph2 = PlotWidget(self.frameGraph)
        self.widgetGraph2.setObjectName(u"widgetGraph2")
        self.widgetGraph2.setFont(font)

        self.verticalLayout_7.addWidget(self.widgetGraph2)

        self.verticalSpacer_5 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_5)

        self.horizontalLayout_39 = QHBoxLayout()
        self.horizontalLayout_39.setSpacing(0)
        self.horizontalLayout_39.setObjectName(u"horizontalLayout_39")
        self.horizontalLayout_39.setContentsMargins(-1, -1, -1, 0)
        self.labelGraphInfo = QLabel(self.frameGraph)
        self.labelGraphInfo.setObjectName(u"labelGraphInfo")
        sizePolicy1.setHeightForWidth(self.labelGraphInfo.sizePolicy().hasHeightForWidth())
        self.labelGraphInfo.setSizePolicy(sizePolicy1)
        self.labelGraphInfo.setMinimumSize(QSize(0, 0))
        font10 = QFont()
        font10.setFamilies([u"Sarasa Fixed SC SemiBold"])
        font10.setPointSize(10)
        font10.setBold(True)
        font10.setItalic(False)
        self.labelGraphInfo.setFont(font10)
        self.labelGraphInfo.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_39.addWidget(self.labelGraphInfo)

        self.horizontalLayout_39.setStretch(0, 1)

        self.verticalLayout_7.addLayout(self.horizontalLayout_39)

        self.verticalLayout_7.setStretch(2, 1)
        self.verticalLayout_7.setStretch(3, 1)

        self.verticalLayout_18.addLayout(self.verticalLayout_7)


        self.horizontalLayout_13.addWidget(self.frameGraph)

        self.horizontalLayout_13.setStretch(1, 1)

        self.verticalLayout_8.addLayout(self.horizontalLayout_13)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.comboGraph2Data.setCurrentIndex(1)
        self.comboDataFps.setCurrentIndex(5)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MDP-P906 \u6570\u63a7\u7535\u6e90\u4e0a\u4f4d\u673a", None))
        self.label_36.setText("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u7535\u538b (V)", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u7535\u6d41 (A)", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u529f\u7387 (W)", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u80fd\u91cf (J)", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u5e73\u5747\u529f\u7387", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u8d1f\u8f7d\u963b\u503c", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"\u8f93\u51fa\u8bbe\u5b9a / OUTPUT", None))
        self.labelState.setText(QCoreApplication.translate("MainWindow", u"\u8f93\u51fa\u72b6\u6001", None))
#if QT_CONFIG(tooltip)
        self.checkBoxQuickset.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.checkBoxQuickset.setText("")
        self.btnOutput.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u5b9a\u7535\u538b", None))
        self.spinBoxVoltage.setSuffix(QCoreApplication.translate("MainWindow", u"V", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u5b9a\u7535\u6d41", None))
        self.spinBoxCurrent.setSuffix(QCoreApplication.translate("MainWindow", u"A", None))
        self.progressBarVoltage.setFormat("")
        self.progressBarCurrent.setFormat("")
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"\u8f85\u52a9\u529f\u80fd / AUX FUNC", None))
        self.comboPreset.setItemText(0, QCoreApplication.translate("MainWindow", u"None", None))
        self.comboPreset.setItemText(1, QCoreApplication.translate("MainWindow", u"1", None))
        self.comboPreset.setItemText(2, QCoreApplication.translate("MainWindow", u"2", None))
        self.comboPreset.setItemText(3, QCoreApplication.translate("MainWindow", u"3", None))
        self.comboPreset.setItemText(4, QCoreApplication.translate("MainWindow", u"4", None))
        self.comboPreset.setItemText(5, QCoreApplication.translate("MainWindow", u"5", None))
        self.comboPreset.setItemText(6, QCoreApplication.translate("MainWindow", u"6", None))
        self.comboPreset.setItemText(7, QCoreApplication.translate("MainWindow", u"7", None))
        self.comboPreset.setItemText(8, QCoreApplication.translate("MainWindow", u"8", None))
        self.comboPreset.setItemText(9, QCoreApplication.translate("MainWindow", u"9", None))

        self.label_34.setText(QCoreApplication.translate("MainWindow", u"\u4fee\u6539\u9884\u8bbe", None))
        self.comboPresetEdit.setItemText(0, QCoreApplication.translate("MainWindow", u"1", None))
        self.comboPresetEdit.setItemText(1, QCoreApplication.translate("MainWindow", u"2", None))
        self.comboPresetEdit.setItemText(2, QCoreApplication.translate("MainWindow", u"3", None))
        self.comboPresetEdit.setItemText(3, QCoreApplication.translate("MainWindow", u"4", None))
        self.comboPresetEdit.setItemText(4, QCoreApplication.translate("MainWindow", u"5", None))
        self.comboPresetEdit.setItemText(5, QCoreApplication.translate("MainWindow", u"6", None))
        self.comboPresetEdit.setItemText(6, QCoreApplication.translate("MainWindow", u"7", None))
        self.comboPresetEdit.setItemText(7, QCoreApplication.translate("MainWindow", u"8", None))
        self.comboPresetEdit.setItemText(8, QCoreApplication.translate("MainWindow", u"9", None))

        self.label_30.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u5b9a\u7535\u538b", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u5b9a\u7535\u6d41", None))
        self.btnPresetSave.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPreset), QCoreApplication.translate("MainWindow", u"\u9884\u8bbe\u7ec4", None))
        self.btnKeepPower.setText(QCoreApplication.translate("MainWindow", u"\u529f\u80fd\u5df2\u5173\u95ed", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"\u76ee\u6807\u529f\u7387", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"\u95ed\u73af\u53c2\u6570", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"\u7535\u538b\u4e0a\u9650", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"\u6267\u884c\u9891\u7387", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPower), QCoreApplication.translate("MainWindow", u"\u529f\u7387\u73af", None))
        self.btnSweep.setText(QCoreApplication.translate("MainWindow", u"\u529f\u80fd\u5df2\u5173\u95ed", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"\u76ee\u6807\u53c2\u6570", None))
        self.comboSweepTarget.setItemText(0, QCoreApplication.translate("MainWindow", u"\u7535\u538b", None))
        self.comboSweepTarget.setItemText(1, QCoreApplication.translate("MainWindow", u"\u7535\u6d41", None))

        self.label_15.setText(QCoreApplication.translate("MainWindow", u"\u8d77\u59cb\u70b9", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"\u7ed3\u675f\u70b9", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"\u6b65\u8fdb\u503c", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"\u5ef6\u8fdf(s)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSweep), QCoreApplication.translate("MainWindow", u"\u626b\u63cf", None))
        self.btnWaveGen.setText(QCoreApplication.translate("MainWindow", u"\u529f\u80fd\u5df2\u5173\u95ed", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"\u6ce2\u5f62\u7c7b\u578b", None))
        self.comboWaveGenType.setItemText(0, QCoreApplication.translate("MainWindow", u"\u65b9\u6ce2", None))
        self.comboWaveGenType.setItemText(1, QCoreApplication.translate("MainWindow", u"\u6b63\u5f26\u6ce2", None))
        self.comboWaveGenType.setItemText(2, QCoreApplication.translate("MainWindow", u"\u4e09\u89d2\u6ce2", None))
        self.comboWaveGenType.setItemText(3, QCoreApplication.translate("MainWindow", u"\u952f\u9f7f\u6ce2", None))
        self.comboWaveGenType.setItemText(4, QCoreApplication.translate("MainWindow", u"\u566a\u97f3", None))

        self.label_22.setText(QCoreApplication.translate("MainWindow", u" \u5468\u671f ", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"\u9ad8\u7535\u5e73", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"\u4f4e\u7535\u5e73", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"\u6267\u884c\u9891\u7387", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWaveGen), QCoreApplication.translate("MainWindow", u"\u51fd\u6570", None))
#if QT_CONFIG(tooltip)
        self.listSeq.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.btnSeqDelay.setText(QCoreApplication.translate("MainWindow", u"\u5ef6\u8fdf", None))
        self.btnSeqWaitTime.setText(QCoreApplication.translate("MainWindow", u"\u7b49\u5f85", None))
        self.btnSeqVoltage.setText(QCoreApplication.translate("MainWindow", u"\u7535\u538b", None))
        self.btnSeqCurrent.setText(QCoreApplication.translate("MainWindow", u"\u7535\u6d41", None))
        self.btnSeqSave.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58", None))
        self.btnSeqLoad.setText(QCoreApplication.translate("MainWindow", u"\u8f7d\u5165", None))
        self.btnSeqSingle.setText(QCoreApplication.translate("MainWindow", u"\u5355\u6b21", None))
        self.btnSeqLoop.setText(QCoreApplication.translate("MainWindow", u"\u5faa\u73af", None))
        self.btnSeqStop.setText(QCoreApplication.translate("MainWindow", u"\u505c\u6b62", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSeq), QCoreApplication.translate("MainWindow", u"\u5e8f\u5217", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"\u7cfb\u7edf\u72b6\u6001 / SYSTEM STATE", None))
        self.labelComSpeed.setText(QCoreApplication.translate("MainWindow", u"0kBps", None))
        self.labelErrRate.setText(QCoreApplication.translate("MainWindow", u"CON-ERR 0%", None))
        self.labelError.setText(QCoreApplication.translate("MainWindow", u"NO ERROR", None))
        self.labelInputVals.setText(QCoreApplication.translate("MainWindow", u"0.00V 0.00A", None))
        self.labelLockState.setText(QCoreApplication.translate("MainWindow", u"UNLOCKED", None))
        self.labelTemperature.setText(QCoreApplication.translate("MainWindow", u"TEMP 30.0\u2103", None))
        self.btnGraphics.setText(QCoreApplication.translate("MainWindow", u"\u56fe\u5f62\u8bbe\u7f6e", None))
        self.btnSettings.setText(QCoreApplication.translate("MainWindow", u"\u8fde\u63a5\u8bbe\u7f6e", None))
        self.labelConnectState.setText(QCoreApplication.translate("MainWindow", u"\u672a\u8fde\u63a5", None))
        self.btnConnect.setText(QCoreApplication.translate("MainWindow", u"\u8fde\u63a5/\u65ad\u5f00", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"\u6570\u636e\u6ce2\u5f62 / LINE CHART", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"\u663e\u793a\u6570\u636e:", None))
        self.comboGraph1Data.setItemText(0, QCoreApplication.translate("MainWindow", u"\u7535\u538b", None))
        self.comboGraph1Data.setItemText(1, QCoreApplication.translate("MainWindow", u"\u7535\u6d41", None))
        self.comboGraph1Data.setItemText(2, QCoreApplication.translate("MainWindow", u"\u529f\u7387", None))
        self.comboGraph1Data.setItemText(3, QCoreApplication.translate("MainWindow", u"\u963b\u503c", None))
        self.comboGraph1Data.setItemText(4, QCoreApplication.translate("MainWindow", u"\u65e0", None))

        self.comboGraph2Data.setItemText(0, QCoreApplication.translate("MainWindow", u"\u7535\u538b", None))
        self.comboGraph2Data.setItemText(1, QCoreApplication.translate("MainWindow", u"\u7535\u6d41", None))
        self.comboGraph2Data.setItemText(2, QCoreApplication.translate("MainWindow", u"\u529f\u7387", None))
        self.comboGraph2Data.setItemText(3, QCoreApplication.translate("MainWindow", u"\u963b\u503c", None))
        self.comboGraph2Data.setItemText(4, QCoreApplication.translate("MainWindow", u"\u65e0", None))

        self.label_29.setText(QCoreApplication.translate("MainWindow", u"\u91c7\u6837\u7387:", None))
        self.comboDataFps.setItemText(0, QCoreApplication.translate("MainWindow", u"10Hz", None))
        self.comboDataFps.setItemText(1, QCoreApplication.translate("MainWindow", u"20Hz", None))
        self.comboDataFps.setItemText(2, QCoreApplication.translate("MainWindow", u"30Hz", None))
        self.comboDataFps.setItemText(3, QCoreApplication.translate("MainWindow", u"40Hz", None))
        self.comboDataFps.setItemText(4, QCoreApplication.translate("MainWindow", u"50Hz", None))
        self.comboDataFps.setItemText(5, QCoreApplication.translate("MainWindow", u"60Hz", None))
        self.comboDataFps.setItemText(6, QCoreApplication.translate("MainWindow", u"70Hz", None))
        self.comboDataFps.setItemText(7, QCoreApplication.translate("MainWindow", u"80Hz", None))
        self.comboDataFps.setItemText(8, QCoreApplication.translate("MainWindow", u"90Hz", None))
        self.comboDataFps.setItemText(9, QCoreApplication.translate("MainWindow", u"100Hz", None))

        self.labelFps.setText(QCoreApplication.translate("MainWindow", u"0.0Hz", None))
        self.btnGraphRecord.setText(QCoreApplication.translate("MainWindow", u"\u5f55\u5236", None))
        self.btnGraphAutoScale.setText(QCoreApplication.translate("MainWindow", u"\u9002\u5e94", None))
        self.btnGraphKeep.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u6301", None))
        self.btnGraphClear.setText(QCoreApplication.translate("MainWindow", u"\u6e05\u7a7a", None))
        self.btnRecordClear.setText(QCoreApplication.translate("MainWindow", u"\u56de\u96f6", None))
        self.labelGraphInfo.setText(QCoreApplication.translate("MainWindow", u"No Info", None))
    # retranslateUi


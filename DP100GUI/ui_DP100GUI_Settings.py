# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\PersonalDocument\Code\git\DP100\DP100GUI\DP100GUI_Settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogSettings(object):
    def setupUi(self, DialogSettings):
        DialogSettings.setObjectName("DialogSettings")
        DialogSettings.setWindowModality(QtCore.Qt.WindowModal)
        DialogSettings.setEnabled(True)
        DialogSettings.resize(210, 250)
        DialogSettings.setMinimumSize(QtCore.QSize(210, 250))
        DialogSettings.setMaximumSize(QtCore.QSize(210, 250))
        DialogSettings.setSizeGripEnabled(False)
        DialogSettings.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogSettings)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_33 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_33.setObjectName("horizontalLayout_33")
        self.label_34 = QtWidgets.QLabel(DialogSettings)
        self.label_34.setMinimumSize(QtCore.QSize(0, 28))
        self.label_34.setAlignment(QtCore.Qt.AlignCenter)
        self.label_34.setObjectName("label_34")
        self.horizontalLayout_33.addWidget(self.label_34)
        self.spinBoxBacklight = QtWidgets.QDoubleSpinBox(DialogSettings)
        self.spinBoxBacklight.setAlignment(QtCore.Qt.AlignCenter)
        self.spinBoxBacklight.setDecimals(0)
        self.spinBoxBacklight.setMinimum(0.0)
        self.spinBoxBacklight.setMaximum(4.0)
        self.spinBoxBacklight.setSingleStep(0.1)
        self.spinBoxBacklight.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxBacklight.setProperty("value", 4.0)
        self.spinBoxBacklight.setObjectName("spinBoxBacklight")
        self.horizontalLayout_33.addWidget(self.spinBoxBacklight)
        self.horizontalLayout_33.setStretch(0, 1)
        self.horizontalLayout_33.setStretch(1, 2)
        self.verticalLayout.addLayout(self.horizontalLayout_33)
        self.horizontalLayout_34 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_34.setObjectName("horizontalLayout_34")
        self.label_35 = QtWidgets.QLabel(DialogSettings)
        self.label_35.setMinimumSize(QtCore.QSize(0, 28))
        self.label_35.setAlignment(QtCore.Qt.AlignCenter)
        self.label_35.setObjectName("label_35")
        self.horizontalLayout_34.addWidget(self.label_35)
        self.spinBoxVolume = QtWidgets.QDoubleSpinBox(DialogSettings)
        self.spinBoxVolume.setAlignment(QtCore.Qt.AlignCenter)
        self.spinBoxVolume.setDecimals(0)
        self.spinBoxVolume.setMinimum(0.0)
        self.spinBoxVolume.setMaximum(4.0)
        self.spinBoxVolume.setSingleStep(0.1)
        self.spinBoxVolume.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxVolume.setProperty("value", 4.0)
        self.spinBoxVolume.setObjectName("spinBoxVolume")
        self.horizontalLayout_34.addWidget(self.spinBoxVolume)
        self.horizontalLayout_34.setStretch(0, 1)
        self.horizontalLayout_34.setStretch(1, 2)
        self.verticalLayout.addLayout(self.horizontalLayout_34)
        self.horizontalLayout_31 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_31.setObjectName("horizontalLayout_31")
        self.label_32 = QtWidgets.QLabel(DialogSettings)
        self.label_32.setMinimumSize(QtCore.QSize(0, 28))
        self.label_32.setAlignment(QtCore.Qt.AlignCenter)
        self.label_32.setObjectName("label_32")
        self.horizontalLayout_31.addWidget(self.label_32)
        self.spinBoxOpp = QtWidgets.QDoubleSpinBox(DialogSettings)
        self.spinBoxOpp.setAlignment(QtCore.Qt.AlignCenter)
        self.spinBoxOpp.setDecimals(2)
        self.spinBoxOpp.setMinimum(0.0)
        self.spinBoxOpp.setMaximum(105.0)
        self.spinBoxOpp.setSingleStep(0.1)
        self.spinBoxOpp.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxOpp.setProperty("value", 0.0)
        self.spinBoxOpp.setObjectName("spinBoxOpp")
        self.horizontalLayout_31.addWidget(self.spinBoxOpp)
        self.horizontalLayout_31.setStretch(0, 1)
        self.horizontalLayout_31.setStretch(1, 2)
        self.verticalLayout.addLayout(self.horizontalLayout_31)
        self.horizontalLayout_32 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_32.setObjectName("horizontalLayout_32")
        self.label_33 = QtWidgets.QLabel(DialogSettings)
        self.label_33.setMinimumSize(QtCore.QSize(0, 28))
        self.label_33.setAlignment(QtCore.Qt.AlignCenter)
        self.label_33.setObjectName("label_33")
        self.horizontalLayout_32.addWidget(self.label_33)
        self.spinBoxOtp = QtWidgets.QDoubleSpinBox(DialogSettings)
        self.spinBoxOtp.setAlignment(QtCore.Qt.AlignCenter)
        self.spinBoxOtp.setDecimals(0)
        self.spinBoxOtp.setMinimum(50.0)
        self.spinBoxOtp.setMaximum(80.0)
        self.spinBoxOtp.setSingleStep(0.1)
        self.spinBoxOtp.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.spinBoxOtp.setProperty("value", 50.0)
        self.spinBoxOtp.setObjectName("spinBoxOtp")
        self.horizontalLayout_32.addWidget(self.spinBoxOtp)
        self.horizontalLayout_32.setStretch(0, 1)
        self.horizontalLayout_32.setStretch(1, 2)
        self.verticalLayout.addLayout(self.horizontalLayout_32)
        self.horizontalLayout_35 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_35.setObjectName("horizontalLayout_35")
        self.label_36 = QtWidgets.QLabel(DialogSettings)
        self.label_36.setMinimumSize(QtCore.QSize(0, 28))
        self.label_36.setAlignment(QtCore.Qt.AlignCenter)
        self.label_36.setObjectName("label_36")
        self.horizontalLayout_35.addWidget(self.label_36)
        self.checkBoxRevProtect = QtWidgets.QCheckBox(DialogSettings)
        self.checkBoxRevProtect.setObjectName("checkBoxRevProtect")
        self.horizontalLayout_35.addWidget(self.checkBoxRevProtect)
        self.horizontalLayout_35.setStretch(0, 1)
        self.horizontalLayout_35.setStretch(1, 2)
        self.verticalLayout.addLayout(self.horizontalLayout_35)
        self.horizontalLayout_36 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_36.setObjectName("horizontalLayout_36")
        self.label_37 = QtWidgets.QLabel(DialogSettings)
        self.label_37.setMinimumSize(QtCore.QSize(0, 28))
        self.label_37.setAlignment(QtCore.Qt.AlignCenter)
        self.label_37.setObjectName("label_37")
        self.horizontalLayout_36.addWidget(self.label_37)
        self.checkBoxAuto = QtWidgets.QCheckBox(DialogSettings)
        self.checkBoxAuto.setObjectName("checkBoxAuto")
        self.horizontalLayout_36.addWidget(self.checkBoxAuto)
        self.horizontalLayout_36.setStretch(0, 1)
        self.horizontalLayout_36.setStretch(1, 2)
        self.verticalLayout.addLayout(self.horizontalLayout_36)
        self.btnSave = QtWidgets.QPushButton(DialogSettings)
        self.btnSave.setObjectName("btnSave")
        self.verticalLayout.addWidget(self.btnSave)

        self.retranslateUi(DialogSettings)
        QtCore.QMetaObject.connectSlotsByName(DialogSettings)

    def retranslateUi(self, DialogSettings):
        _translate = QtCore.QCoreApplication.translate
        DialogSettings.setWindowTitle(_translate("DialogSettings", "Power Settings"))
        self.label_34.setText(_translate("DialogSettings", "Backlight Brightness"))
        self.label_35.setText(_translate("DialogSettings", "Volume Level"))
        self.label_32.setText(_translate("DialogSettings", "Power Protection"))
        self.label_33.setText(_translate("DialogSettings", "High Temperature Protection"))
        self.label_36.setText(_translate("DialogSettings", "Reverse Connection Protection"))
        self.checkBoxRevProtect.setText(_translate("DialogSettings", "Enable"))
        self.label_37.setText(_translate("DialogSettings", "Power-on Output"))
        self.checkBoxAuto.setText(_translate("DialogSettings", "Enable"))
        self.btnSave.setText(_translate("DialogSettings", "Save"))

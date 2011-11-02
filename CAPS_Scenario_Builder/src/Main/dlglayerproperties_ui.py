# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
#
# Form implementation generated from reading ui file 
#
# Created: Sun Jun 05 23:12:18 2011
#      by: PyQt4 UI code generator 4.5.2
#
#-----------------------------------------------------------------------------------------
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_LayerProperties(object):
    def setupUi(self, LayerProperties):
        LayerProperties.setObjectName("LayerProperties")
        LayerProperties.resize(313, 277)
        self.gridLayout_2 = QtGui.QGridLayout(LayerProperties)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(LayerProperties)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.txtLayerName = QtGui.QLineEdit(LayerProperties)
        self.txtLayerName.setMinimumSize(QtCore.QSize(140, 0))
        self.txtLayerName.setMaximumSize(QtCore.QSize(200, 21))
        self.txtLayerName.setCursorPosition(0)
        self.txtLayerName.setObjectName("txtLayerName")
        self.horizontalLayout.addWidget(self.txtLayerName)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lblDisplayField = QtGui.QLabel(LayerProperties)
        self.lblDisplayField.setObjectName("lblDisplayField")
        self.horizontalLayout_2.addWidget(self.lblDisplayField)
        self.cboDisplayFieldName = QtGui.QComboBox(LayerProperties)
        self.cboDisplayFieldName.setMinimumSize(QtCore.QSize(140, 0))
        self.cboDisplayFieldName.setMaximumSize(QtCore.QSize(200, 21))
        self.cboDisplayFieldName.setObjectName("cboDisplayFieldName")
        self.horizontalLayout_2.addWidget(self.cboDisplayFieldName)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 15, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.gridLayout_2.addItem(spacerItem1, 2, 0, 1, 1)
        self.frame = QtGui.QFrame(LayerProperties)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(-1, 0, -1, -1)
        self.gridLayout.setObjectName("gridLayout")
        self.chkScale = QtGui.QCheckBox(self.frame)
        self.chkScale.setObjectName("chkScale")
        self.gridLayout.addWidget(self.chkScale, 0, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem2 = QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.lblMaxScale = QtGui.QLabel(self.frame)
        self.lblMaxScale.setEnabled(True)
        self.lblMaxScale.setObjectName("lblMaxScale")
        self.horizontalLayout_4.addWidget(self.lblMaxScale)
        self.maxScaleSpinBox = QtGui.QSpinBox(self.frame)
        self.maxScaleSpinBox.setEnabled(True)
        self.maxScaleSpinBox.setMinimumSize(QtCore.QSize(140, 0))
        self.maxScaleSpinBox.setMaximumSize(QtCore.QSize(16777215, 21))
        self.maxScaleSpinBox.setMinimum(1)
        self.maxScaleSpinBox.setMaximum(100000000)
        self.maxScaleSpinBox.setSingleStep(1000)
        self.maxScaleSpinBox.setProperty("value", QtCore.QVariant(1000))
        self.maxScaleSpinBox.setObjectName("maxScaleSpinBox")
        self.horizontalLayout_4.addWidget(self.maxScaleSpinBox)
        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem3 = QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.lblMinScale = QtGui.QLabel(self.frame)
        self.lblMinScale.setEnabled(True)
        self.lblMinScale.setObjectName("lblMinScale")
        self.horizontalLayout_3.addWidget(self.lblMinScale)
        self.minScaleSpinBox = QtGui.QSpinBox(self.frame)
        self.minScaleSpinBox.setEnabled(True)
        self.minScaleSpinBox.setMinimumSize(QtCore.QSize(140, 0))
        self.minScaleSpinBox.setMaximumSize(QtCore.QSize(16777215, 21))
        self.minScaleSpinBox.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.minScaleSpinBox.setAccelerated(True)
        self.minScaleSpinBox.setMinimum(1)
        self.minScaleSpinBox.setMaximum(100000000)
        self.minScaleSpinBox.setSingleStep(1000)
        self.minScaleSpinBox.setProperty("value", QtCore.QVariant(1000000))
        self.minScaleSpinBox.setObjectName("minScaleSpinBox")
        self.horizontalLayout_3.addWidget(self.minScaleSpinBox)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.frame, 3, 0, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(20, 15, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.gridLayout_2.addItem(spacerItem4, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(LayerProperties)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 5, 0, 1, 1)

        self.retranslateUi(LayerProperties)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), LayerProperties.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), LayerProperties.reject)
        QtCore.QMetaObject.connectSlotsByName(LayerProperties)

    def retranslateUi(self, LayerProperties):
        LayerProperties.setWindowTitle(QtGui.QApplication.translate("LayerProperties", "Layer properties", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("LayerProperties", "Layer name", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDisplayField.setText(QtGui.QApplication.translate("LayerProperties", "Display field", None, QtGui.QApplication.UnicodeUTF8))
        self.chkScale.setText(QtGui.QApplication.translate("LayerProperties", "Use scale dependent rendering", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMaxScale.setText(QtGui.QApplication.translate("LayerProperties", "Maximum scale", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMinScale.setText(QtGui.QApplication.translate("LayerProperties", "Minimum scale", None, QtGui.QApplication.UnicodeUTF8))

# The code below will create the interface
# describe by the code above
# when run from an OS command console.
# This code is normally not used.
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    LayerProperties = QtGui.QDialog()
    ui = Ui_LayerProperties()
    ui.setupUi(LayerProperties)
    LayerProperties.show()
    sys.exit(app.exec_())


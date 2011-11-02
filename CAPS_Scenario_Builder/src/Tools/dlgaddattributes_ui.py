# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlgaddattributes.ui'
#
# Created: Mon Sep 19 16:07:41 2011
#      by: PyQt4 UI code generator 4.5.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_dlgAddAttributes(object):
    def setupUi(self, dlgAddAttributes):
        dlgAddAttributes.setObjectName("dlgAddAttributes")
        dlgAddAttributes.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(dlgAddAttributes)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Label = QtGui.QLabel(dlgAddAttributes)
        self.Label.setObjectName("Label")
        self.horizontalLayout.addWidget(self.Label)
        self.Field = QtGui.QLineEdit(dlgAddAttributes)
        self.Field.setObjectName("Field")
        self.horizontalLayout.addWidget(self.Field)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 181, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(dlgAddAttributes)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)

        self.retranslateUi(dlgAddAttributes)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), dlgAddAttributes.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), dlgAddAttributes.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgAddAttributes)

    def retranslateUi(self, dlgAddAttributes):
        dlgAddAttributes.setWindowTitle(QtGui.QApplication.translate("dlgAddAttributes", "Add Attributes", None, QtGui.QApplication.UnicodeUTF8))
        self.Label.setText(QtGui.QApplication.translate("dlgAddAttributes", "maximum8", None, QtGui.QApplication.UnicodeUTF8))


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlgscenarioeditypes.ui'
#
# Created: Mon Sep 19 13:57:07 2011
#      by: PyQt4 UI code generator 4.5.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DlgScenarioEditTypes(object):
    def setupUi(self, DlgScenarioEditTypes):
        DlgScenarioEditTypes.setObjectName("DlgScenarioEditTypes")
        DlgScenarioEditTypes.resize(405, 243)
        self.gridLayout = QtGui.QGridLayout(DlgScenarioEditTypes)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.typesLabel = QtGui.QLabel(DlgScenarioEditTypes)
        self.typesLabel.setObjectName("typesLabel")
        self.horizontalLayout.addWidget(self.typesLabel)
        self.typesComboBox = QtGui.QComboBox(DlgScenarioEditTypes)
        self.typesComboBox.setObjectName("typesComboBox")
        # add the items from the ScenarioTypesList 
        #found at the beginning of the mainwindow
        '''
        self.typesComboBox.addItems(ScenarioTypesList)
        self.typesComboBox.addItem(QtCore.QString())
        self.typesComboBox.addItem(QtCore.QString())
        self.typesComboBox.addItem(QtCore.QString())
        self.typesComboBox.addItem(QtCore.QString())
        self.typesComboBox.addItem(QtCore.QString())
        self.typesComboBox.addItem(QtCore.QString())
        self.typesComboBox.addItem(QtCore.QString())'''
        self.horizontalLayout.addWidget(self.typesComboBox)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 152, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.typesButtonBox = QtGui.QDialogButtonBox(DlgScenarioEditTypes)
        self.typesButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.typesButtonBox.setObjectName("typesButtonBox")
        self.gridLayout.addWidget(self.typesButtonBox, 2, 0, 1, 1)

        self.retranslateUi(DlgScenarioEditTypes)
        QtCore.QObject.connect(self.typesButtonBox, QtCore.SIGNAL("accepted()"), DlgScenarioEditTypes.accept)
        QtCore.QObject.connect(self.typesButtonBox, QtCore.SIGNAL("rejected()"), DlgScenarioEditTypes.reject)
        QtCore.QMetaObject.connectSlotsByName(DlgScenarioEditTypes)

    def retranslateUi(self, DlgScenarioEditTypes):
        DlgScenarioEditTypes.setWindowTitle(QtGui.QApplication.translate("DlgScenarioEditTypes", "Edit Scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.typesLabel.setText(QtGui.QApplication.translate("DlgScenarioEditTypes", "Choose a scenario edit type:", None, QtGui.QApplication.UnicodeUTF8))
        # set above from the scenario types list
        '''self.typesComboBox.setItemText(0, QtGui.QApplication.translate("DlgScenarioEditTypes", "Road stream crossing", None, QtGui.QApplication.UnicodeUTF8))
        self.typesComboBox.setItemText(1, QtGui.QApplication.translate("DlgScenarioEditTypes", "Dam addition or removal", None, QtGui.QApplication.UnicodeUTF8))
        self.typesComboBox.setItemText(2, QtGui.QApplication.translate("DlgScenarioEditTypes", "Wildlife crossing", None, QtGui.QApplication.UnicodeUTF8))
        self.typesComboBox.setItemText(3, QtGui.QApplication.translate("DlgScenarioEditTypes", "Tidal restriction", None, QtGui.QApplication.UnicodeUTF8))
        self.typesComboBox.setItemText(4, QtGui.QApplication.translate("DlgScenarioEditTypes", "Land use change (add points)", None, QtGui.QApplication.UnicodeUTF8))
        self.typesComboBox.setItemText(5, QtGui.QApplication.translate("DlgScenarioEditTypes", "Land use change (add lines)", None, QtGui.QApplication.UnicodeUTF8))
        self.typesComboBox.setItemText(6, QtGui.QApplication.translate("DlgScenarioEditTypes", "Land use change (add polygons)", None, QtGui.QApplication.UnicodeUTF8))'''


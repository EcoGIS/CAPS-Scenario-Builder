# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlgmanageprojects.ui'
#
# Created: Fri May 11 15:13:00 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DlgManageProjects(object):
    def setupUi(self, DlgManageProjects):
        DlgManageProjects.setObjectName(_fromUtf8("DlgManageProjects"))
        DlgManageProjects.resize(1174, 590)
        self.gridLayout = QtGui.QGridLayout(DlgManageProjects)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(-1, -1, 10, -1)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.senderNameLabel = QtGui.QLabel(DlgManageProjects)
        self.senderNameLabel.setMargin(0)
        self.senderNameLabel.setObjectName(_fromUtf8("senderNameLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.senderNameLabel)
        self.senderNameEdit = QtGui.QLineEdit(DlgManageProjects)
        self.senderNameEdit.setObjectName(_fromUtf8("senderNameEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.senderNameEdit)
        self.senderEmailLabel = QtGui.QLabel(DlgManageProjects)
        self.senderEmailLabel.setMargin(0)
        self.senderEmailLabel.setObjectName(_fromUtf8("senderEmailLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.senderEmailLabel)
        self.sendersEmailEdit = QtGui.QLineEdit(DlgManageProjects)
        self.sendersEmailEdit.setObjectName(_fromUtf8("sendersEmailEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.sendersEmailEdit)
        self.dateSentLabel = QtGui.QLabel(DlgManageProjects)
        self.dateSentLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.dateSentLabel.setObjectName(_fromUtf8("dateSentLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.dateSentLabel)
        self.dateSentTextLabel = QtGui.QLabel(DlgManageProjects)
        self.dateSentTextLabel.setObjectName(_fromUtf8("dateSentTextLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.dateSentTextLabel)
        self.verticalLayout_4.addLayout(self.formLayout)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.messageLabel = QtGui.QLabel(DlgManageProjects)
        self.messageLabel.setObjectName(_fromUtf8("messageLabel"))
        self.verticalLayout.addWidget(self.messageLabel)
        self.textBrowser = QtGui.QTextBrowser(DlgManageProjects)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.verticalLayout.addWidget(self.textBrowser)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, 20, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.projectsButtonBox = QtGui.QDialogButtonBox(DlgManageProjects)
        self.projectsButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Discard|QtGui.QDialogButtonBox.Save)
        self.projectsButtonBox.setCenterButtons(False)
        self.projectsButtonBox.setObjectName(_fromUtf8("projectsButtonBox"))
        self.horizontalLayout.addWidget(self.projectsButtonBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.sendButton = QtGui.QPushButton(DlgManageProjects)
        self.sendButton.setObjectName(_fromUtf8("sendButton"))
        self.horizontalLayout.addWidget(self.sendButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_4.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.verticalLayout_4, 0, 0, 6, 1)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, 7, -1, -1)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.selectProjectLabel = QtGui.QLabel(DlgManageProjects)
        self.selectProjectLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.selectProjectLabel.setMargin(0)
        self.selectProjectLabel.setObjectName(_fromUtf8("selectProjectLabel"))
        self.verticalLayout_2.addWidget(self.selectProjectLabel)
        self.comboBox_2 = QtGui.QComboBox(DlgManageProjects)
        self.comboBox_2.setEditable(True)
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.verticalLayout_2.addWidget(self.comboBox_2)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 1, 1, 3)
        self.splitter = QtGui.QSplitter(DlgManageProjects)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.scenarioListLabel = QtGui.QLabel(self.splitter)
        self.scenarioListLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.scenarioListLabel.setObjectName(_fromUtf8("scenarioListLabel"))
        self.existingScenarioFileList = QtGui.QListWidget(self.splitter)
        self.existingScenarioFileList.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.existingScenarioFileList.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.existingScenarioFileList.setSelectionRectVisible(True)
        self.existingScenarioFileList.setObjectName(_fromUtf8("existingScenarioFileList"))
        self.gridLayout.addWidget(self.splitter, 1, 1, 5, 1)
        self.splitter_2 = QtGui.QSplitter(DlgManageProjects)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.projectListLabel = QtGui.QLabel(self.splitter_2)
        self.projectListLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.projectListLabel.setObjectName(_fromUtf8("projectListLabel"))
        self.projectScenarioFileList = QtGui.QListWidget(self.splitter_2)
        self.projectScenarioFileList.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.projectScenarioFileList.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.projectScenarioFileList.setSelectionRectVisible(True)
        self.projectScenarioFileList.setObjectName(_fromUtf8("projectScenarioFileList"))
        self.gridLayout.addWidget(self.splitter_2, 1, 3, 5, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 50, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 2, 1, 1)
        self.addScenarioButton = QtGui.QPushButton(DlgManageProjects)
        self.addScenarioButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.addScenarioButton.setCursor(QtCore.Qt.BusyCursor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/moveForward.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addScenarioButton.setIcon(icon)
        self.addScenarioButton.setObjectName(_fromUtf8("addScenarioButton"))
        self.gridLayout.addWidget(self.addScenarioButton, 3, 2, 1, 1)
        self.removeScenarioButton = QtGui.QPushButton(DlgManageProjects)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/moveBack.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.removeScenarioButton.setIcon(icon1)
        self.removeScenarioButton.setObjectName(_fromUtf8("removeScenarioButton"))
        self.gridLayout.addWidget(self.removeScenarioButton, 4, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 366, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 5, 2, 1, 1)

        self.retranslateUi(DlgManageProjects)
        '''QtCore.QObject.connect(self.sendButton, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), DlgManageProjects.sendProject)
        QtCore.QObject.connect(self.projectsButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DlgManageProjects.saveProject)
        QtCore.QObject.connect(self.projectsButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DlgManageProjects.reject)
        QtCore.QObject.connect(self.projectsButtonBox, QtCore.SIGNAL(_fromUtf8("destroyed()")), DlgManageProjects.deleteProject)
        QtCore.QObject.connect(self.addScenarioButton, QtCore.SIGNAL(_fromUtf8("clicked()")), DlgManageProjects.addScenarioToProject)
        QtCore.QObject.connect(self.removeScenarioButton, QtCore.SIGNAL(_fromUtf8("clicked()")), DlgManageProjects.removeScenarioFromProject)'''
        QtCore.QMetaObject.connectSlotsByName(DlgManageProjects)

    def retranslateUi(self, DlgManageProjects):
        DlgManageProjects.setWindowTitle(QtGui.QApplication.translate("DlgManageProjects", "Manage Projects", None, QtGui.QApplication.UnicodeUTF8))
        DlgManageProjects.setToolTip(QtGui.QApplication.translate("DlgManageProjects", "Create, ", None, QtGui.QApplication.UnicodeUTF8))
        self.senderNameLabel.setText(QtGui.QApplication.translate("DlgManageProjects", "Sender\'s name:", None, QtGui.QApplication.UnicodeUTF8))
        self.senderEmailLabel.setText(QtGui.QApplication.translate("DlgManageProjects", "Sender\'s email:", None, QtGui.QApplication.UnicodeUTF8))
        self.dateSentLabel.setText(QtGui.QApplication.translate("DlgManageProjects", "Date sent:", None, QtGui.QApplication.UnicodeUTF8))
        self.dateSentTextLabel.setText(QtGui.QApplication.translate("DlgManageProjects", "Unsent", None, QtGui.QApplication.UnicodeUTF8))
        self.messageLabel.setText(QtGui.QApplication.translate("DlgManageProjects", "Message or comments:", None, QtGui.QApplication.UnicodeUTF8))
        self.sendButton.setText(QtGui.QApplication.translate("DlgManageProjects", "Send to UMass", None, QtGui.QApplication.UnicodeUTF8))
        self.selectProjectLabel.setToolTip(QtGui.QApplication.translate("DlgManageProjects", "Create a new project or open, copy or rename an existing project.", None, QtGui.QApplication.UnicodeUTF8))
        self.selectProjectLabel.setText(QtGui.QApplication.translate("DlgManageProjects", "Project Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.scenarioListLabel.setText(QtGui.QApplication.translate("DlgManageProjects", "Existing Scenario files:", None, QtGui.QApplication.UnicodeUTF8))
        self.projectListLabel.setText(QtGui.QApplication.translate("DlgManageProjects", "Scenario files in Project:", None, QtGui.QApplication.UnicodeUTF8))
        self.addScenarioButton.setToolTip(QtGui.QApplication.translate("DlgManageProjects", "Add selected scenario(s) to the project.", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

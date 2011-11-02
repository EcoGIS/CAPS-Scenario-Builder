# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Wed Oct 26 13:08:23 2011
#      by: PyQt4 UI code generator 4.5.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 700)
        MainWindow.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/CAPS_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.centralwidget.setObjectName("centralwidget")
        self.gridlayout = QtGui.QGridLayout(self.centralwidget)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridlayout.addWidget(self.frame, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 26))
        self.menubar.setObjectName("menubar")
        self.menuScenario = QtGui.QMenu(self.menubar)
        self.menuScenario.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.menuScenario.setObjectName("menuScenario")
        self.menuLayer = QtGui.QMenu(self.menubar)
        self.menuLayer.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.menuLayer.setObjectName("menuLayer")
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.mpActionAddRasterLayer = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/mActionAddRasterLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionAddRasterLayer.setIcon(icon1)
        self.mpActionAddRasterLayer.setObjectName("mpActionAddRasterLayer")
        self.mpActionNewScenario = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/mActionFileNew.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionNewScenario.setIcon(icon2)
        self.mpActionNewScenario.setObjectName("mpActionNewScenario")
        self.mpActionAddVectorLayer = QtGui.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/images/mActionAddOgrLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionAddVectorLayer.setIcon(icon3)
        self.mpActionAddVectorLayer.setObjectName("mpActionAddVectorLayer")
        self.mpActionZoomIn = QtGui.QAction(MainWindow)
        self.mpActionZoomIn.setCheckable(True)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/images/mActionZoomIn.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionZoomIn.setIcon(icon4)
        self.mpActionZoomIn.setObjectName("mpActionZoomIn")
        self.mpActionZoomOut = QtGui.QAction(MainWindow)
        self.mpActionZoomOut.setCheckable(True)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/images/mActionZoomOut.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionZoomOut.setIcon(icon5)
        self.mpActionZoomOut.setObjectName("mpActionZoomOut")
        self.mpActionPan = QtGui.QAction(MainWindow)
        self.mpActionPan.setCheckable(True)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/images/mActionPan.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionPan.setIcon(icon6)
        self.mpActionPan.setObjectName("mpActionPan")
        self.mpActionZoomtoMapExtent = QtGui.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/images/mActionZoomFullExtent.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionZoomtoMapExtent.setIcon(icon7)
        self.mpActionZoomtoMapExtent.setObjectName("mpActionZoomtoMapExtent")
        self.mpActionOpenScenario = QtGui.QAction(MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/images/mActionFileOpen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionOpenScenario.setIcon(icon8)
        self.mpActionOpenScenario.setObjectName("mpActionOpenScenario")
        self.mpActionSaveScenario = QtGui.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/images/mActionFileSave.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionSaveScenario.setIcon(icon9)
        self.mpActionSaveScenario.setObjectName("mpActionSaveScenario")
        self.mpActionSaveScenarioAs = QtGui.QAction(MainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/images/mActionFileSaveAs.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionSaveScenarioAs.setIcon(icon10)
        self.mpActionSaveScenarioAs.setObjectName("mpActionSaveScenarioAs")
        self.mpActionSelectFeatures = QtGui.QAction(MainWindow)
        self.mpActionSelectFeatures.setCheckable(True)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/images/mActionSelect.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionSelectFeatures.setIcon(icon11)
        self.mpActionSelectFeatures.setObjectName("mpActionSelectFeatures")
        self.mpActionDeleteFeatures = QtGui.QAction(MainWindow)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(":/images/mActionDeleteSelected.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionDeleteFeatures.setIcon(icon12)
        self.mpActionDeleteFeatures.setObjectName("mpActionDeleteFeatures")
        self.mpActionPasteFeatures = QtGui.QAction(MainWindow)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(":/images/mActionEditPaste.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionPasteFeatures.setIcon(icon13)
        self.mpActionPasteFeatures.setObjectName("mpActionPasteFeatures")
        self.mpActionCopyFeatures = QtGui.QAction(MainWindow)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(":/images/mActionCopySelected.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionCopyFeatures.setIcon(icon14)
        self.mpActionCopyFeatures.setObjectName("mpActionCopyFeatures")
        self.mpActionAddPoints = QtGui.QAction(MainWindow)
        self.mpActionAddPoints.setCheckable(True)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(":/images/mActionCapturePoint.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionAddPoints.setIcon(icon15)
        self.mpActionAddPoints.setObjectName("mpActionAddPoints")
        self.mpActionAddLines = QtGui.QAction(MainWindow)
        self.mpActionAddLines.setCheckable(True)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap(":/images/mActionCaptureLine.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionAddLines.setIcon(icon16)
        self.mpActionAddLines.setObjectName("mpActionAddLines")
        self.mpActionAddPolygons = QtGui.QAction(MainWindow)
        self.mpActionAddPolygons.setCheckable(True)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap(":/images/mActionCapturePolygon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionAddPolygons.setIcon(icon17)
        self.mpActionAddPolygons.setObjectName("mpActionAddPolygons")
        self.mpActionExportScenario = QtGui.QAction(MainWindow)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(QtGui.QPixmap(":/images/scenario_export.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionExportScenario.setIcon(icon18)
        self.mpActionExportScenario.setObjectName("mpActionExportScenario")
        self.mpActionOpenRasterCategoryTable = QtGui.QAction(MainWindow)
        icon19 = QtGui.QIcon()
        icon19.addPixmap(QtGui.QPixmap(":/images/mIconTableLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionOpenRasterCategoryTable.setIcon(icon19)
        self.mpActionOpenRasterCategoryTable.setObjectName("mpActionOpenRasterCategoryTable")
        self.mpActionOpenVectorAttributeTable = QtGui.QAction(MainWindow)
        icon20 = QtGui.QIcon()
        icon20.addPixmap(QtGui.QPixmap(":/images/attributes.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionOpenVectorAttributeTable.setIcon(icon20)
        self.mpActionOpenVectorAttributeTable.setObjectName("mpActionOpenVectorAttributeTable")
        self.mpActionEditScenario = QtGui.QAction(MainWindow)
        self.mpActionEditScenario.setCheckable(True)
        icon21 = QtGui.QIcon()
        icon21.addPixmap(QtGui.QPixmap(":/images/mActionToggleEditing.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionEditScenario.setIcon(icon21)
        self.mpActionEditScenario.setObjectName("mpActionEditScenario")
        self.mpActionSaveEdits = QtGui.QAction(MainWindow)
        icon22 = QtGui.QIcon()
        icon22.addPixmap(QtGui.QPixmap(":/images/mActionSaveEdits.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionSaveEdits.setIcon(icon22)
        self.mpActionSaveEdits.setObjectName("mpActionSaveEdits")
        self.mpActionDeselectFeatures = QtGui.QAction(MainWindow)
        icon23 = QtGui.QIcon()
        icon23.addPixmap(QtGui.QPixmap(":/images/mActionDeselectAll.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionDeselectFeatures.setIcon(icon23)
        self.mpActionDeselectFeatures.setObjectName("mpActionDeselectFeatures")
        self.mpActionAppExit = QtGui.QAction(MainWindow)
        icon24 = QtGui.QIcon()
        icon24.addPixmap(QtGui.QPixmap(":/images/mActionAppExit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionAppExit.setIcon(icon24)
        self.mpActionAppExit.setObjectName("mpActionAppExit")
        self.mpActionIdentifyFeatures = QtGui.QAction(MainWindow)
        self.mpActionIdentifyFeatures.setCheckable(True)
        icon25 = QtGui.QIcon()
        icon25.addPixmap(QtGui.QPixmap(":/images/mActionIdentify.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionIdentifyFeatures.setIcon(icon25)
        self.mpActionIdentifyFeatures.setObjectName("mpActionIdentifyFeatures")
        self.mpActionModifyPoints = QtGui.QAction(MainWindow)
        icon26 = QtGui.QIcon()
        icon26.addPixmap(QtGui.QPixmap(":/images/mActionModifyPoints.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpActionModifyPoints.setIcon(icon26)
        self.mpActionModifyPoints.setObjectName("mpActionModifyPoints")
        self.menuScenario.addAction(self.mpActionNewScenario)
        self.menuScenario.addAction(self.mpActionOpenScenario)
        self.menuScenario.addAction(self.mpActionSaveScenario)
        self.menuScenario.addAction(self.mpActionSaveScenarioAs)
        self.menuScenario.addAction(self.mpActionExportScenario)
        self.menuScenario.addAction(self.mpActionAppExit)
        self.menuLayer.addAction(self.mpActionAddVectorLayer)
        self.menuLayer.addAction(self.mpActionAddRasterLayer)
        self.menuLayer.addAction(self.mpActionOpenVectorAttributeTable)
        self.menuLayer.addAction(self.mpActionOpenRasterCategoryTable)
        self.menuLayer.addSeparator()
        self.menuEdit.addAction(self.mpActionSelectFeatures)
        self.menuEdit.addAction(self.mpActionDeselectFeatures)
        self.menuEdit.addAction(self.mpActionModifyPoints)
        self.menuEdit.addAction(self.mpActionDeleteFeatures)
        self.menuEdit.addAction(self.mpActionCopyFeatures)
        self.menuEdit.addAction(self.mpActionPasteFeatures)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.mpActionEditScenario)
        self.menuEdit.addAction(self.mpActionAddPoints)
        self.menuEdit.addAction(self.mpActionAddLines)
        self.menuEdit.addAction(self.mpActionAddPolygons)
        self.menuEdit.addAction(self.mpActionSaveEdits)
        self.menuEdit.addSeparator()
        self.menuEdit.addSeparator()
        self.menuView.addAction(self.mpActionZoomIn)
        self.menuView.addAction(self.mpActionZoomOut)
        self.menuView.addAction(self.mpActionPan)
        self.menuView.addAction(self.mpActionZoomtoMapExtent)
        self.menuView.addAction(self.mpActionIdentifyFeatures)
        self.menubar.addAction(self.menuScenario.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuLayer.menuAction())
        self.toolBar.addAction(self.mpActionNewScenario)
        self.toolBar.addAction(self.mpActionOpenScenario)
        self.toolBar.addAction(self.mpActionSaveScenario)
        self.toolBar.addAction(self.mpActionSaveScenarioAs)
        self.toolBar.addAction(self.mpActionExportScenario)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.mpActionSelectFeatures)
        self.toolBar.addAction(self.mpActionDeselectFeatures)
        self.toolBar.addAction(self.mpActionModifyPoints)
        self.toolBar.addAction(self.mpActionDeleteFeatures)
        self.toolBar.addAction(self.mpActionCopyFeatures)
        self.toolBar.addAction(self.mpActionPasteFeatures)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.mpActionEditScenario)
        self.toolBar.addAction(self.mpActionAddPoints)
        self.toolBar.addAction(self.mpActionAddLines)
        self.toolBar.addAction(self.mpActionAddPolygons)
        self.toolBar.addAction(self.mpActionSaveEdits)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.mpActionIdentifyFeatures)
        self.toolBar.addAction(self.mpActionPan)
        self.toolBar.addAction(self.mpActionZoomIn)
        self.toolBar.addAction(self.mpActionZoomOut)
        self.toolBar.addAction(self.mpActionZoomtoMapExtent)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.mpActionAddVectorLayer)
        self.toolBar.addAction(self.mpActionAddRasterLayer)
        self.toolBar.addAction(self.mpActionOpenVectorAttributeTable)
        self.toolBar.addAction(self.mpActionOpenRasterCategoryTable)
        self.toolBar.addSeparator()

        self.retranslateUi(MainWindow)
        '''QtCore.QObject.connect(self.mpActionNewScenario, QtCore.SIGNAL("triggered()"), MainWindow.newScenario)
        QtCore.QObject.connect(self.mpActionSaveScenario, QtCore.SIGNAL("triggered()"), MainWindow.saveScenario)
        QtCore.QObject.connect(self.mpActionOpenScenario, QtCore.SIGNAL("triggered()"), MainWindow.openScenario)
        QtCore.QObject.connect(self.mpActionSaveScenarioAs, QtCore.SIGNAL("triggered()"), MainWindow.saveScenarioAs)
        QtCore.QObject.connect(self.mpActionExportScenario, QtCore.SIGNAL("triggered()"), MainWindow.exportScenario)
        QtCore.QObject.connect(self.mpActionSelectFeatures, QtCore.SIGNAL("toggled(bool)"), MainWindow.selectFeatures)
        QtCore.QObject.connect(self.mpActionDeselectFeatures, QtCore.SIGNAL("triggered()"), MainWindow.deselectFeatures)
        QtCore.QObject.connect(self.mpActionCopyFeatures, QtCore.SIGNAL("triggered()"), MainWindow.copyFeatures)
        QtCore.QObject.connect(self.mpActionDeleteFeatures, QtCore.SIGNAL("triggered()"), MainWindow.deleteFeatures)
        QtCore.QObject.connect(self.mpActionPasteFeatures, QtCore.SIGNAL("triggered()"), MainWindow.pasteFeatures)
        QtCore.QObject.connect(self.mpActionAddPoints, QtCore.SIGNAL("toggled(bool)"), MainWindow.addPoints)
        QtCore.QObject.connect(self.mpActionAddLines, QtCore.SIGNAL("toggled(bool)"), MainWindow.addLines)
        QtCore.QObject.connect(self.mpActionAddPolygons, QtCore.SIGNAL("toggled(bool)"), MainWindow.addPolygons)
        QtCore.QObject.connect(self.mpActionZoomIn, QtCore.SIGNAL("toggled(bool)"), MainWindow.zoomIn)
        QtCore.QObject.connect(self.mpActionZoomOut, QtCore.SIGNAL("toggled(bool)"), MainWindow.zoomOut)
        QtCore.QObject.connect(self.mpActionZoomtoMapExtent, QtCore.SIGNAL("triggered()"), MainWindow.zoomToMapExtent)
        QtCore.QObject.connect(self.mpActionAddVectorLayer, QtCore.SIGNAL("triggered()"), MainWindow.addVectorLayer)
        QtCore.QObject.connect(self.mpActionAddRasterLayer, QtCore.SIGNAL("triggered()"), MainWindow.addRasterLayer)
        QtCore.QObject.connect(self.mpActionOpenRasterCategoryTable, QtCore.SIGNAL("triggered()"), MainWindow.openRasterCategoryTable)
        QtCore.QObject.connect(self.mpActionOpenVectorAttributeTable, QtCore.SIGNAL("triggered()"), MainWindow.openVectorAttributeTable)
        QtCore.QObject.connect(self.mpActionEditScenario, QtCore.SIGNAL("toggled(bool)"), MainWindow.editScenario)
        QtCore.QObject.connect(self.mpActionSaveEdits, QtCore.SIGNAL("triggered()"), MainWindow.saveEdits)
        QtCore.QObject.connect(self.mpActionPan, QtCore.SIGNAL("toggled(bool)"), MainWindow.pan)
        QtCore.QObject.connect(self.mpActionAppExit, QtCore.SIGNAL("triggered()"), MainWindow.close)
        QtCore.QObject.connect(self.mpActionIdentifyFeatures, QtCore.SIGNAL("toggled(bool)"), MainWindow.identifyFeatures)
        QtCore.QObject.connect(self.mpActionModifyPoints, QtCore.SIGNAL("triggered()"), MainWindow.ModifyPoints)'''
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Conservation Assessment and Prioritization System (CAPS) Scenario Builder", None, QtGui.QApplication.UnicodeUTF8))
        self.menuScenario.setTitle(QtGui.QApplication.translate("MainWindow", "Scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.menuLayer.setTitle(QtGui.QApplication.translate("MainWindow", "Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEdit.setTitle(QtGui.QApplication.translate("MainWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menuView.setTitle(QtGui.QApplication.translate("MainWindow", "View", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionAddRasterLayer.setText(QtGui.QApplication.translate("MainWindow", "Add Raster Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionNewScenario.setText(QtGui.QApplication.translate("MainWindow", "New Scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionNewScenario.setIconText(QtGui.QApplication.translate("MainWindow", "New Scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionNewScenario.setToolTip(QtGui.QApplication.translate("MainWindow", "New Scenario: create a new scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionAddVectorLayer.setText(QtGui.QApplication.translate("MainWindow", "Add Vector Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionAddVectorLayer.setToolTip(QtGui.QApplication.translate("MainWindow", "Add Vector Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionZoomIn.setText(QtGui.QApplication.translate("MainWindow", "Zoom In", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionZoomIn.setToolTip(QtGui.QApplication.translate("MainWindow", "Zoom In: click or draw rectangle", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionZoomOut.setText(QtGui.QApplication.translate("MainWindow", "Zoom Out", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionPan.setText(QtGui.QApplication.translate("MainWindow", "Pan", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionZoomtoMapExtent.setText(QtGui.QApplication.translate("MainWindow", "Zoom to Map Extent", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionZoomtoMapExtent.setToolTip(QtGui.QApplication.translate("MainWindow", "Zoom to Map Extent: zooms to the extent of all visible layers", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionOpenScenario.setText(QtGui.QApplication.translate("MainWindow", "Open Scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionOpenScenario.setToolTip(QtGui.QApplication.translate("MainWindow", "Open Scenario: open a previously saved scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionSaveScenario.setText(QtGui.QApplication.translate("MainWindow", "Save Scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionSaveScenarioAs.setText(QtGui.QApplication.translate("MainWindow", "Save Scenario As ...", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionSaveScenarioAs.setToolTip(QtGui.QApplication.translate("MainWindow", "Save Scenario As ... : copy the open scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionSelectFeatures.setText(QtGui.QApplication.translate("MainWindow", "Select Features", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionDeleteFeatures.setText(QtGui.QApplication.translate("MainWindow", "Delete Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionDeleteFeatures.setToolTip(QtGui.QApplication.translate("MainWindow", "Delete Selected: delete selected features", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionPasteFeatures.setText(QtGui.QApplication.translate("MainWindow", "Paste Features", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionPasteFeatures.setToolTip(QtGui.QApplication.translate("MainWindow", "Paste Selected: paste selected features to another layer", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionCopyFeatures.setText(QtGui.QApplication.translate("MainWindow", "Copy Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionCopyFeatures.setToolTip(QtGui.QApplication.translate("MainWindow", "Copy Selected: copy selected features", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionAddPoints.setText(QtGui.QApplication.translate("MainWindow", "Add Points", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionAddLines.setText(QtGui.QApplication.translate("MainWindow", "Add Lines", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionAddPolygons.setText(QtGui.QApplication.translate("MainWindow", "Add Polygons", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionExportScenario.setText(QtGui.QApplication.translate("MainWindow", "Export Scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionExportScenario.setToolTip(QtGui.QApplication.translate("MainWindow", "Export Scenario: make file to send to the CAPS staff", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionOpenRasterCategoryTable.setText(QtGui.QApplication.translate("MainWindow", "Open Raster Category Tables", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionOpenVectorAttributeTable.setText(QtGui.QApplication.translate("MainWindow", "Open Vector Attribute Table", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionEditScenario.setText(QtGui.QApplication.translate("MainWindow", "Edit Scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionEditScenario.setToolTip(QtGui.QApplication.translate("MainWindow", "Edit Scenario: open a dialog to choose/change the scenario edit type", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionSaveEdits.setText(QtGui.QApplication.translate("MainWindow", "Save Edits", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionSaveEdits.setToolTip(QtGui.QApplication.translate("MainWindow", "Save Edits: save your scenario changes", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionDeselectFeatures.setText(QtGui.QApplication.translate("MainWindow", "Deselect Features", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionAppExit.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionIdentifyFeatures.setText(QtGui.QApplication.translate("MainWindow", "Identify Features", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionIdentifyFeatures.setToolTip(QtGui.QApplication.translate("MainWindow", "Identify Features: get feature attributes and raster values", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionModifyPoints.setText(QtGui.QApplication.translate("MainWindow", "Modify Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.mpActionModifyPoints.setToolTip(QtGui.QApplication.translate("MainWindow", "Modify selected base layer points", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

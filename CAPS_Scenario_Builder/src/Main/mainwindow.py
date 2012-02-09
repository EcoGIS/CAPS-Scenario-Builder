# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
#
# Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
#
#--------------------------------------------------------------------- 
# Original sources Copyright (c) 2006 by Tim Sutton
#
# ported to Python by Martin Dobias
#
# Copyright (C) 2007  Ecotrust
# Copyright (C) 2007  Aaron Racicot
# Copyright (C) 2011  Robert English: Daystar Computing (http://edaystar.com)
#---------------------------------------------------------------------
# 
# licensed under the terms of GNU GPLv3
# 
# This file is part of CAPS.

# CAPS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# CAPS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with CAPS.  If not, see <http://www.gnu.org/licenses/>..
# 
#---------------------------------------------------------------------
# general python imports
import os, shutil, time, os.path #  copy, subprocess, sys,  stat,
# import Qt libraries
from PyQt4 import QtCore, QtGui
# import qgis API
from qgis.core import *  
from qgis.gui import *
# import code generated in Qt designer
from Main.mainwindow_ui import *
# import GeoTux layer widget
from Main.legend import *
# CAPS application imports
from Tools.mapcoords import MapCoords
from Tools.addpoints import AddPoints
from Tools.selectfeatures import SelectTool
from Tools.dlgaddattributes import DlgAddAttributes
from Tools.addlinespolygons import *
from Tools.identify import Identify
from Main.dlgscenarioedittypes import DlgScenarioEditTypes
import Tools.shared
import config


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    ''' Display the main window and manage all user actions '''
    def __init__(self, splash):
        QtGui.QMainWindow.__init__(self)
    
        # add the Qt4 designer code elements to the MainWindow
        self.setupUi(self)
        # get the splash screen
        self.splash = splash
        
        ''' Set instance variables '''
        # LISTS
        self.originalScenarioLayers = []
        self.currentLayers = []
        self.copiedFeats = []
        self.originalEditLayerFeats = []
        self.originalScenarioLayersNames = []
        
        # FLAGS
        self.scenarioDirty = False
        self.origScenarioLyrsLoaded = False 
        self.copyFlag = False # True if selections copied
        self.editDirty = False # True if edits unsaved, false if no unsaved edits
        self.editMode = False # True if "Toggle Edits" is activated
        # used to remember if edit_scenario(polygons).shp was loaded from a scenario file
        self.editingPolygon = False
        self.openingOrientingLayers = False
        self.openingScenario = False 
                
        # OBJECTS
        self.attrTable = None
        self.dwAttrTable = None
        self.dwRasterTable = None
        self.scenarioInfo = None
        self.dlgDisplayIdentify = None
        self.dlgScenarioEditTypes = None
        self.windModifyInfo = None
        # MA State Plane coordinate system used by MassGIS
        self.crs = QgsCoordinateReferenceSystem(26986, QgsCoordinateReferenceSystem.EpsgCrsId)
        # The rough extents of Massachusetts
        self.rectExtentMA = QgsRectangle(26000, 747000, 350000, 989000)
        # get active vlayer to pass to edit tools
        # this variable is updated by self.activeLayerChanged
        self.activeVLayer = None
        self.activeRLayer = None
        self.provider = None
        #set tool variables
        self.toolSelect = None
        self.toolAddPoints = None
        self.toolAddLinesPolygons = None
        self.editTypeLabel = None
     
        # VALUES
        self.scenarioFilePath = None
        self.scenarioFileName = None
        self.scenarioEditType = None
        self.currentLayersCount = None
        self.layerType = None
        # geometry of the activeVLayer
        self.geom = None #0 point, 1 line, 2 polygon
        # This saves an editing layer's color so that it gets refreshed
        # when the layer loads after updating extents (see shared.updateExtents
        self.layerColor = None
        self.editLayerName = None

        ''' Begin construction of main window '''
        
        # create map canvas
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QtGui.QColor(255,255,255))
        
        self.canvas.enableAntiAliasing(True)
        self.canvas.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.gridlayout.addWidget(self.canvas)
        
        self.mapRenderer = self.canvas.mapRenderer()
        # False disables "on the fly" projections; True enables them
        self.mapRenderer.setProjectionsEnabled(False)
        # sets the project crs
        self.mapRenderer.setDestinationCrs(self.crs)

        # set the QDockWidget that holds the legend
        self.legendDock = QtGui.QDockWidget("Layers", self)
        self.legendDock.setObjectName("legend")
        self.legendDock.setStyleSheet("background-color: white")
        # without "NoDockWidgetFeatures, the user could close the legend with no way to reopen it
        self.legendDock.setFeatures(self.legendDock.NoDockWidgetFeatures)
        self.legendDock.setContentsMargins (1, 1, 1, 1)
        # create the legend from legend.py
        self.legend = Legend(self)
        self.legend.setObjectName("theMapLegend")
        # add the legend to the dock widget
        self.legendDock.setWidget(self.legend)
        # add the dock widget to the main window and show it
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.legendDock)
        self.legendDock.show()
        
        # now that we have self.legend, get active layer changed signal
        # connect the Python 'short circuit' signal from legend.py to the handler
        self.connect( self.legend, QtCore.SIGNAL("activeLayerChanged"), self.activeLayerChanged)
        
        # Create the actions and link to their behaviors.
        # pasted from mainwindow_ui.py and then change MainWindow.* to self.*
        QtCore.QObject.connect(self.mpActionNewScenario, QtCore.SIGNAL("triggered()"), self.newScenario)
        QtCore.QObject.connect(self.mpActionSaveScenario, QtCore.SIGNAL("triggered()"), self.saveScenario)
        QtCore.QObject.connect(self.mpActionOpenScenario, QtCore.SIGNAL("triggered()"), self.openScenario)
        QtCore.QObject.connect(self.mpActionSaveScenarioAs, QtCore.SIGNAL("triggered()"), self.saveScenarioAs)
        QtCore.QObject.connect(self.mpActionExportScenario, QtCore.SIGNAL("triggered()"), self.exportScenario)
        QtCore.QObject.connect(self.mpActionSelectFeatures, QtCore.SIGNAL("toggled(bool)"), self.selectFeatures)
        QtCore.QObject.connect(self.mpActionDeselectFeatures, QtCore.SIGNAL("triggered()"), self.deselectFeatures)
        QtCore.QObject.connect(self.mpActionCopyFeatures, QtCore.SIGNAL("triggered()"), self.copyFeatures)
        QtCore.QObject.connect(self.mpActionDeleteFeatures, QtCore.SIGNAL("triggered()"), self.deleteFeatures)
        QtCore.QObject.connect(self.mpActionPasteFeatures, QtCore.SIGNAL("triggered()"), self.pasteFeatures)
        QtCore.QObject.connect(self.mpActionAddPoints, QtCore.SIGNAL("toggled(bool)"), self.addPoints)
        QtCore.QObject.connect(self.mpActionAddLines, QtCore.SIGNAL("toggled(bool)"), self.addLines)
        QtCore.QObject.connect(self.mpActionAddPolygons, QtCore.SIGNAL("toggled(bool)"), self.addPolygons)
        QtCore.QObject.connect(self.mpActionZoomIn, QtCore.SIGNAL("toggled(bool)"), self.zoomIn)
        QtCore.QObject.connect(self.mpActionZoomOut, QtCore.SIGNAL("toggled(bool)"), self.zoomOut)
        QtCore.QObject.connect(self.mpActionZoomtoMapExtent, QtCore.SIGNAL("triggered()"), self.zoomToMapExtent)
        QtCore.QObject.connect(self.mpActionAddVectorLayer, QtCore.SIGNAL("triggered()"), self.addVectorLayer)
        QtCore.QObject.connect(self.mpActionAddRasterLayer, QtCore.SIGNAL("triggered()"), self.addRasterLayer)
        QtCore.QObject.connect(self.mpActionOpenRasterCategoryTable, QtCore.SIGNAL("triggered()"), self.openRasterCategoryTable)
        QtCore.QObject.connect(self.mpActionOpenVectorAttributeTable, QtCore.SIGNAL("triggered()"), self.openVectorAttributeTable)
        QtCore.QObject.connect(self.mpActionEditScenario, QtCore.SIGNAL("toggled(bool)"), self.editScenario)
        QtCore.QObject.connect(self.mpActionSaveEdits, QtCore.SIGNAL("triggered()"), self.saveEdits)
        QtCore.QObject.connect(self.mpActionPan, QtCore.SIGNAL("toggled(bool)"), self.pan)
        QtCore.QObject.connect(self.mpActionAppExit, QtCore.SIGNAL("triggered()"), self.close)
        QtCore.QObject.connect(self.mpActionIdentifyFeatures, QtCore.SIGNAL("toggled(bool)"), self.identifyFeatures)
        QtCore.QObject.connect(QgsProject.instance(), QtCore.SIGNAL("layerLoaded(int, int)"), self.getOriginalScenarioLayers)
        QtCore.QObject.connect(self.mpActionModifyPoints, QtCore.SIGNAL("triggered()"), self.modifyFeatures)
        
        # Instantiate all tools.  They are written so their variables update from
        # the main window, so there is no need to repeat the instantiation process 
        # when layers or other variables change.
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False) # false = in
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out
        self.toolIdentify = Identify(self)
        self.toolSelect = SelectTool(self)
        self.toolAddPoints = AddPoints(self)
        self.toolAddLinesPolygons = AddLinesPolygons(self)
        
        # Create a QActionGroup to manage map tool actions states.
        # If an action is set as "checkable" in mainwindow_ui.py and
        # the action is in a tool group, only one action in the 
        # group can be active at a time. All other buttons 
        # are deactivated.  A toolGroup also makes it possible to
        # easily set all actions in the group as enabled or disabled.
        self.mapToolGroup = QtGui.QActionGroup(self) # 8 actions of 26 total
        # The four actions below are usually disabled
        self.mapToolGroup.addAction(self.mpActionSelectFeatures)
        self.mapToolGroup.addAction(self.mpActionAddPoints)
        self.mapToolGroup.addAction(self.mpActionAddLines)
        self.mapToolGroup.addAction(self.mpActionAddPolygons)
        # The four actions below are always enabled when a layer is loaded
        self.mapToolGroup.addAction(self.mpActionIdentifyFeatures)
        self.mapToolGroup.addAction(self.mpActionPan)
        self.mapToolGroup.addAction(self.mpActionZoomIn)
        self.mapToolGroup.addAction(self.mpActionZoomOut)
       
        # The following actions are usually disabled (8 actions of 26 total)
        self.mpActionDeselectFeatures.setDisabled(True)
        self.mpActionModifyPoints.setDisabled(True)
        self.mpActionDeleteFeatures.setDisabled(True)
        self.mpActionCopyFeatures.setDisabled(True)
        self.mpActionPasteFeatures.setDisabled(True)
        self.mpActionSaveEdits.setDisabled(True)
        self.mpActionExportScenario.setDisabled(True)
        self.mpActionOpenVectorAttributeTable.setDisabled(True)
                        
        # Set initial action states; all disabled except ten actions are always enabled (by default).
        # New Scenario, Open Scenario, Save Scenario, Save Scenario As, Edit Scenario
        # Add Vector, Add Raster and Open Raster Category Table, Exit and Zoom to Map Extent are on 
        self.mapToolGroup.setDisabled(True)
        
        # close splash screen
        time.sleep(2)
        self.splash.hide()
        
        # make sure the mainwindow paints properly
        self.menubar.show()
        self.toolBar.show()
        self.statusBar.show()
        self.setVisible(True)
        self.update()
        self.activateWindow()
        # if the mainwindow is not maximized on opening we get painting problems
        # on all versions of MS Windows
        self.showMaximized() 
        
        # set the map coordinates display in the status bar
        self.mapcoords = MapCoords(self)

        # load the orienting layers
        self.openOrientingLayers()

        # The V2 renderers get the selection color from the old renderer.
        # This sets the selection color once, when the app starts
        self.setSelectionColor()

############################################################################################   
    ''' SCENARIO MENU CUSTOM SLOTS AND METHODS'''
############################################################################################  
         
    def newScenario(self):
        ''' Scenario menu SLOT '''
        # debugging
        print "Main.mainwindow.newScenario()"
        print "Main.mainwindow.newScenario() start dirty? " + str(self.scenarioDirty)
        
        # check for unsaved edits and scenario changes
        if self.appStateChanged("newScenario") == "Cancel":
            # debugging
            print "canceling Main.mainwindow.newScenario()"
            return
 
        # new scenario so remove layers from the legend and the canvas layer set
        self.legend.removeAll()
        # remove all layers from the QgsMapLayerRegistry
        QgsMapLayerRegistry.instance().removeAllMapLayers()

        # go back to app opening state
        self.setInitialAppState()
                
        # debugging
        print "Main.mainwindow.newScenario() end dirty? " + str(self.scenarioDirty)
   
    def openScenario(self):
        ''' Scenario menu SLOT '''
        # debugging
        print "Main.mainwindow.openScenario()"
        print "self.scenarioDirty begin is " + str(self.scenarioDirty)
        
        # check for unsaved edits and scenario changes
        if self.appStateChanged("openScenario") == "Cancel":
            # debugging
            print "canceling Main.mainwindow.openScenario()"
            return
     
        # open file dialog to find scenarios to open
        qd = QtGui.QFileDialog()
        filterString = "CAPS Scenario (*.cap)" # syntax for showing all files \nAll Files(*)")
        # get the path to the directory for the saved file using Python
        directory = os.path.dirname(config.scenariosPath)
        # Convert QStrings to unicode unless they are used immediately in a Qt method. 
        # This ensures that we never ask Python to slice a QString, which produces a type error.
        scenarioFilePath = unicode(qd.getOpenFileName(self, QtCore.QString
                                                ("Open Scenario"), directory, filterString))
        # Check for cancel of file dialog
        if len(scenarioFilePath) == 0: return
        
        # So we are going to open a saved scenario.  Set initial app state to start.
        self.setInitialAppState(False)
 
        # Remember the file info to use elsewhere, change to unicode in case
        # we need to use Python string operations somewhere (they do not work on QString types)
        self.scenarioFilePath = scenarioFilePath # unicode
        self.scenarioInfo = QtCore.QFileInfo(scenarioFilePath) # an object
        # get the filename without the path
        self.scenarioFileName = unicode(self.scenarioInfo.fileName())
        
        #debugging
        print "Main.mainwindow.openScenario() " + scenarioFilePath
     
        # remove old layers from the legend and the canvas layer set
        self.legend.removeAll()
        # remove all layers from the registry
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        # set the originalScenarioLayers to None
        self.originalScenarioLayers = []
        
        # debugging
        print "Main.mainwindow.openScenario() after remove registry count " + str(QgsMapLayerRegistry.instance().count())
     
        # Set the self.editingPolygon flag to False because we don't know if the 
        # edit_scenario(polygons) layer is in this scenario
        self.editingPolygon = False
        
        # Set a flag to indicate a scenario is opening.  This flag is used in 
        # Main.legend.LegendItem() class to help set layer visibility
        self.openingScenario = True  
        
        # Create a scenario instance and read the scenario from disk.
        # Note that QgsProject gets the extents, creates map layers and registers them
        scenario = QgsProject.instance()
        scenario.read(self.scenarioInfo)
        
        # check for error
        if scenario.error():
                QtGui.QMessageBox.warning(self, "File Error", "CAPS cannot read this file.")
                # QgsProject has no "close()" method, so, if error, close the project instance
                scenario = None
                return
        else: # no error so we have newly opened scenario but note that it might have no layers!
            scenario = None # close the instance of QgsProject
            self.openingScenario = False
             
        # The scenario file (i.e. *.cap) does not save the files in order so:
        self.arrangeOrientingLayers()
        
        # give the user some file info
        self.setWindowTitle("Conservation Assessment and \
Prioritization System (CAPS) Scenario Builder - " + self.scenarioFileName)
        
        # debugging
        print "Main.mainwindow.openScenario() after scenario load registry count " + str(QgsMapLayerRegistry.instance().count())
        print "Main.mainwindow.openScenario() scenario filename is " + self.scenarioFileName
        print "Main.mainwindow.openScenario() end dirty? " + str(self.scenarioDirty)
        
    def saveScenario(self):
        ''' Scenario menu SLOT '''
        # debugging
        print "Main.mainwindow.saveScenario() start dirty? " + str(self.scenarioDirty)
        
        # check for unsaved edits
        if self.appStateChanged("saveScenario") == "Cancel":
            # debugging
            print "canceling Main.mainwindow.openScenario()"
            return
         
        # if there is an open project to save
        if self.scenarioFilePath:
            # check if there is a scenario directory
            scenarioDirectoryName = self.scenarioInfo.completeBaseName() # returns a QString
            # PyQt handles concatenating a Python string and a QString
            if not QtCore.QDir(config.scenariosPath + scenarioDirectoryName).exists():  
                self.makeScenarioDirectory()
            # start a project instance
            scenario = QgsProject.instance()
            
            # try to write (save) the file
            scenario.write(self.scenarioInfo)
            # check for error
            if scenario.error():
                QtGui.QMessageBox.warning(self, "Failed to save:", "Please check if this \
scenario file is open in another program.")
                # QgsProject has no "close()" method, so, if error, close the project instance
                scenario = None
                return # return on error
            else: # no error so we have saved the scenario
                scenario = None
                self.setScenarioSaved()
                print "Main.mainwindow.saveScenario() end dirty? " + str(self.scenarioDirty)
        else: self.saveScenarioAs() # no open project so call saveScenarioAs()

    def saveScenarioAs(self):
        ''' 
            Scenario menu SLOT to save an unsaved scenario with a new name; overwrite an existing scenario 
            with a different scenario; or save an existing scenario with a new name (i.e. copy).
            
            This method includes making a copy of the scenario's '.cap' file,
            the scenario's associated directory, any editing shapefiles in the scenario's 
            directory, and any existing 'Scenario Export' files.  In other words, this makes
            a "deep" copy of all the important scenario files.
        '''
        
        # debugging
        print "Main.mainwindow.saveScenarioAs()"
        print "Main.mainwindow.saveScenarioAs() start dirty? " + str(self.scenarioDirty)
        
        # check for unsaved edits
        if self.appStateChanged("saveScenarioAs") == "Cancel":
            # debugging
            print "canceling Main.mainwindow.saveScenarioAs()"
            return
        
        ''' GET THE FILE PATH THE USER CHOOSES '''
        
        qd = QtGui.QFileDialog()
        qd.setDefaultSuffix(".cap")
        filterString = "CAPS Scenario (*.cap)" #\nAll Files(*)")
        # get the path to the default scenario's directory 
        defaultDir = config.scenariosPath
        # Get the new file path and change the QString to unicode so that Python 
        # can slice it for the directory name. 
        scenarioFilePath = unicode(qd.getSaveFileName(self, QtCore.QString
                                    ("Save scenario as ..."), defaultDir, filterString))
        
        # debugging
        print "scenarioFilePath is: " + scenarioFilePath
        print "defaultDir is " + defaultDir

        # Check for cancel of the file dialog
        if len(scenarioFilePath) == 0: return "Cancel"
        
        # The user can browse to anywhere and try to save the scenario with
        # any extension, so check for an incorrect directory or file extension
        if not self.checkScenarioDirectoryPath(defaultDir, scenarioFilePath): return
      
        # We have a new valid file path. We start by storing the old path (if one exists) for use
        # below and storing the new file path for use in saveScenario()
        oldScenarioFilePath = self.scenarioFilePath # unicode
        oldScenarioInfo = self.scenarioInfo # an object
        self.scenarioFilePath = scenarioFilePath # unicode
        self.scenarioInfo = QtCore.QFileInfo(scenarioFilePath)
        scenarioDirectoryName = unicode(self.scenarioInfo.completeBaseName())
        
        ''' CHECK FOR CONDITIONS THAT ELIMINATE THE NEED TO COPY THE SCENARIO DIRECTORY CONTENTS '''
        
        # This is the case where the user clicks "Save Scenario As..." to save an open scenario
        # Check if the new path is the same as the old path, and if it is, just call save 
        # scenario to overwrite the scenario file. No need to do anything about editing files
        if self.scenarioFilePath == oldScenarioFilePath:
            self.saveScenario()
            print "Main.mainwindow.saveScenarioAs(): overwriting existing file"
            return

        # We are saving to a new path, so find out if there are any editing files open.
        editLayerLegendItems = []
        for editLayer in config.editLayersBaseNames:
            # This method returns a list of matches
            items = self.legend.findItems(editLayer, QtCore.Qt.MatchFixedString, 0)
            if len(items) > 0: editLayerLegendItems.append(items[0]) # a list of QTreeWidgetItems

        # If there are no editing layers open, we can just write the new editing file 
        # directory, call saveScenario, and set the variables for a successfully saved
        # scenario and return. Any previously existing 'Export Scenario' file would have
        # been deleted when the editing shapefile was removed. 
        # Note that this could be a case where we are saving the scenario
        # for the first time, or saving an existing scenario with a new 
        # name, or overwriting an existing scenario after opening the app or after clicking 
        # "New Scenario.  In each case the needed actions are the same.
        if len(editLayerLegendItems) == 0:
            self.makeScenarioDirectory()
            self.saveScenario()
            self.setScenarioSaved()
            return

        ''' 
            WE NEED TO COPY THE SCENARIO DIRECTORY'S CONTENTS (I.E. EDITING SHAPEFILES)
            AND ANY EXISTING EXPORT SCENARIO FILE 
        '''
        
        self.copyScenario(oldScenarioInfo, scenarioDirectoryName, editLayerLegendItems)
        
        
        ''' NOW DO SOME HOUSEKEEPING '''

        self.setScenarioSaved()
        
        # debugging
        print "Main.mainwindow.saveScenarioAs(): end dirty? " + str(self.scenarioDirty)
 
    def exportScenario(self):
        ''' Scenario menu SLOT to export scenario edits as a CSV file '''
        # debugging
        print "Main.mainwindow.exportScenario()"
        
        # check the app state for unsaved edits and scenario changes
        if self.appStateChanged("exportScenario") == "Cancel":
            # debugging
            print "Main.mainwindow.exportScenario(): canceling exportScenario()"
            return

        # The exportScenario() method action is only enabled if a scenario is open
        # set some needed variables 
        scenarioDirectoryName = unicode(self.scenarioInfo.completeBaseName())
        scenarioDirectoryPath = config.scenariosPath + scenarioDirectoryName
        exportFileName = scenarioDirectoryName + ".csv"
        exportPath = config.scenarioExportsPath + exportFileName
        
        # List the edit files in the scenario's edit file directory.  Returns False if the 
        # directory does not exist or is empty.  The method warns the user on errors.
        scenarioEditFileList = self.listScenarioEditFiles(scenarioDirectoryPath)
        if not scenarioEditFileList: return

        # Delete any old export files before writing a new one. 
        # This method warns the user on errors.
        self.deleteExportScenarioFile()

        # Get a count of the number of editing shapefiles for use below.
        shapefileCount = 0
        for fileName in scenarioEditFileList:
            if not ".shp" in fileName: continue # only looking for the .shp files
            shapefileCount += 1
        
        # Iterate through the editing shapefiles in the current scenario's edit file
        # directory and write them as a CSV format shapefile.  
        # Finally, append the editing CSV shapefile file to the scenario CSV export file,
        # which will consist of all edits to the current scenario in CSV format.
        exportFileWritten = False
        loopCount = 0
        for fileName in scenarioEditFileList: # a list of all files in the scenario's directory
            if not ".shp" in fileName: continue # only looking for the .shp files
            loopCount += 1
            print "Main.mainwindow.exportScenario(): The loopCount begin is " + str(loopCount)
            # get the path to write the csv file to
            csvInfo = QtCore.QFileInfo(fileName)
            csvBaseName = unicode(csvInfo.completeBaseName()) # csvBaseName = editing shapefile BaseName
            csvFileName = csvBaseName + ".csv"
            csvPath = scenarioDirectoryPath + "/" + csvFileName
            
            # debugging
            print "Main.mainwindow.exportScenario(): current csvBaseName is: " + csvBaseName
            print "Main.mainwindow.exportScenario(): current csvFileName is: " + csvFileName
            print "Main.mainwindow.exportScenario(): current csvPath is: " + csvPath
            print "Main.mainwindow.exportScenario(): current exportPath is: " + exportPath
            
            # get a handle to the editing file (returns a maplayer) so it can be converted to CSV format
            # If the layer exists in the scenario's directory but is not open in the
            # legend, the user is prompted with a warning, and the return value = False.
            vlayer = self.getEditLayerToExport(csvBaseName, scenarioDirectoryPath, fileName)
            if not vlayer:  return

            # Check if there are any features in the layer because the QgsVectorFileWriter fails to 
            # write the csv file if there are no features and does NOT return an error!!
            print "Main.mainwindow.chkEditLayerFeatureCount: The vlayer feature count is " + str(vlayer.featureCount())
            if vlayer.featureCount() == 0:
                # keep trying until the last layer in the scenarioEditFileList
                print "Main.mainwindow.chkEditLayerFeatureCount:: the shapefileCount is " + str(shapefileCount)
                print "Main.mainwindow.chkEditLayerFeatureCount:: the loopCount is " + str(loopCount)
                if loopCount < shapefileCount:
                    continue
                elif exportFileWritten: # loopCount = shapefileCount and something exported
                    break
                elif not exportFileWritten: # loopCount = shapefileCount and nothing exported
                    QtGui.QMessageBox.warning(self, "Export Scenario Error:", "There are no features to export.  Please \
make some edits to your scenario and try again.")
                    return   
            
            # Delete previously written CSV shapefiles so current ones can take their place.
            # Return if deletion fails (deleteOldCsvSapefile() warns on error)
            if not self.deleteOldCsvShapefile(csvPath, csvFileName): return
            
            # round values to shorten csv file output (roundGeometryValues() warns on error)
            vlayer = self.roundGeometryValues(vlayer, "export")
            if not vlayer: return
        
            ''' Convert the editing shapefiles to CSV format '''
                
            # Returns False if the write operation failed and writeCsvShapefile warns on error
            if not self.writeCsvShapefile(vlayer, csvPath, csvFileName): return
        
            ''' Now append the CSV shapefile text to the CSV file to be exported to UMass (use Python) '''
            
            # writeCsvExportFile returns True if successful False if not and warns user on error
            exportFileWritten = self.writeCsvExportFile(exportPath, csvPath, exportFileName)
            if not exportFileWritten: return
            
        # We have exited the for loop, so let the user know things worked.
        exportFileInfo = QtCore.QFileInfo(exportPath)
        findExportPath = exportFileInfo.absolutePath()
        QtGui.QMessageBox.information(self, 'Export Scenario Succeeded:', "The export file is named "\
 + exportFileName + ". It can be found in " + findExportPath)
     
    # Scenario Methods -----------------------------------------------------------------------------------------------    
    
    def getEditLayerToExport(self, csvBaseName, scenarioDirectoryPath, fileName):
        '''Scenario method to get the layer id of an editing layer to convert to CSV format '''
        # debugging
        print "Main.mainwindow.getEditLayerToExport"
        
        items = self.legend.findItems(csvBaseName, QtCore.Qt.MatchFixedString, 0)
        print "Main.mainwindow.exportScenario(): length of items list is " + str(len(items))
        if len(items) == 0:
            # This should never happen.  If an editing layer exists in the scenario's directory
            # then it should be open because removing an editing layer from the legend deletes
            # it from the file system. This would be some sort of user error, if it happened.
            QtGui.QMessageBox.warning(self, 'Export Scenario Error:', "An editing shapefile named " \
+ fileName + " exists in " + scenarioDirectoryPath + " , but is not open in the layer list panel. \
You must either delete this editing layer, or open it if it contains features you wish to be part \
of your scenario export file.") 
            return None
        else:
            vlayerId = items[0].layerId
            vlayer = QgsMapLayerRegistry.instance().mapLayer(vlayerId)
            return vlayer

    def deleteOldCsvShapefile(self, csvPath, csvFileName):
        ''' Scenario method to delete previously written CSV shapefiles so new ones can be written '''
        # debugging
        print "Main.mainwindow.deleteOldCsvShapefile()"

        error = None
        currentCsvFile = QtCore.QFile(csvPath)
        if currentCsvFile.exists():
            print "Main.mainwindow.delteOldCSVShapefile(): currentCsvFile exists"
            try:
                currentCsvFile.remove()
            except (IOError, OSError), e:
                error = unicode(e)
            if error:
                print error
                QtGui.QMessageBox.warning(self, "Export Scenario Error:", "An old editing layer \
csv file '" + csvFileName + " could not be deleted.  Please check if the file is open in \
another program and then try again.")
                return False
            else: return True
        else: return True

    def writeCsvShapefile(self, vlayer, csvPath, csvFileName):
        ''' Scenario method to write the CSV shapefile '''
        # debugging
        print "Main.mainwindow.writeCSVShapefile()"

        # Create an empty datasource and errorMessage option for the 
        # QgsVectorFileWriter parameters list
        datasourceOptions = QtCore.QStringList(QtCore.QString())
        errorMessage = QtCore.QString()
        # Need to include the creationOptions or the geometry will not be written.
        creationOptions = QtCore.QStringList("GEOMETRY=AS_WKT")
        # write csv file in MA State Plane coordinates and check for error
        error = QgsVectorFileWriter.writeAsVectorFormat(vlayer, csvPath, "utf-8", 
                    self.crs, "CSV", False, errorMessage, datasourceOptions, creationOptions)
        if error: # != QgsVectorFileWriter.NoError:
            QtGui.QMessageBox.warning(self, "Export Scenario Error:", "The file " + csvFileName + " \
was not written.  Please check that a file with the same name is not open in another program.")
            return False
        else: 
            print "The csv file " + csvPath + " was successfully written."
            return True

    def writeCsvExportFile(self, exportPath, csvPath, exportFileName):
        ''' Scenario method to write the CSV export file '''
        # debugging
        print "Main.mainwindow.writeCsvEportFile"
        
        error = None
        try:
            csvExportScenario = open(exportPath, 'a')
            csvEditingShapefile = open(csvPath, 'r')
            csvText = csvEditingShapefile.read()
            csvEditingShapefile.close()
            csvExportScenario.write(csvText)
            csvExportScenario.close()
        except (IOError, OSError), e:
            error = unicode(e)
        if error:
            print e
            QtGui.QMessageBox.warning(self, 'Export Scenario Error:', 'The export file, ' \
+ exportFileName + ' could not be written.  Please try again.')
            return False
        return True

    def listScenarioEditFiles(self, scenarioDirectoryPath):
        ''' A scenario method to list the files in the scenario's edit file directory '''
        #debugging
        print "Main.mainwindow.listScenarioEditFiles()"

        error = None
        try: # trap error if directory is missing for some reason
            scenarioEditFileList = os.listdir(scenarioDirectoryPath) # use Python os module here
        except (IOError, OSError), e:
            error = e
            if error:
                print error
                QtGui.QMessageBox.warning(self, "Export Scenario Error:", "The files in this \
scenario's directory could not be listed.  Please save the scenario and try again")
                return False
              
        if scenarioEditFileList == []:
            QtGui.QMessageBox.warning(self, "Export Scenario Error:", "You have not made any scenario edits to export. \
Please choose 'Edit Scenario' from the Edit menu, make some edits, and then try again." )
            return False
        else: return scenarioEditFileList
        
    def getOriginalScenarioLayersNames(self):
        # debugging
        print "Main.mainwindow.getOriginalScenarioLayersNames()"
        
        self.originalScenarioLayersNames = []
        for layer in self.originalScenarioLayers: 
            self.originalScenarioLayersNames.append(unicode(layer.name())) # change QString to unicode
        return self.originalScenarioLayersNames
    
    def getOriginalScenarioLayers(self, i, count):                  
        ''' This scenario method is called when a scenario is opened.  The call
            originates each time QgsProject emits a "layerLoaded" signal
        '''
        # debugging
        print "Main.mainwindow.getOriginalScenarioLayers()"
        print "Main.mainwindow.getOriginalScenarioLayers(): int begin " + str(i)
        print "Main.mainwindow.getOriginalScenarioLayers(): count " + str(count)
    
        # QgsProject SIGNAL starts with i = 0, and no layer has been loaded yet.
        # The SIGNAL emits a count of the number of layers to be loaded (say = 3) 
        # on the first signal.  After that we get 1,3; 2,3; and 3,3 for parameters
        # for a 3 layer scenario file.  In the end self.originalScenarioLayers has 3 values.
        if i == count:
            self.originalScenarioLayers = []
            # The line below fails when layers are hidden in the layer list panel
            #self.originalScenarioLayers = self.canvas.layers()
            # self.getCurrentLayers() returns a dictionary of QgsMapLayers
            # self.originalScenarioLayers is a list of QgsMapLayer objects
            self.originalScenarioLayers = self.getCurrentLayers().values()
            # This method sets the instance variable self.getOriginalScenarioLayersNames
            self.getOriginalScenarioLayersNames()
            self.origScenarioLyrsLoaded = True
            # inform user of missing layers
            if len(self.originalScenarioLayers) < count:
                QtGui.QMessageBox.warning(self, "File Error", "Some layers in the scenario have \
failed to load. Either the file name or the location of the file has probably changed. You may reload \
missing files by using the 'Add Vector Layer' or 'Add Raster Layer buttons.'")
   
        # debugging
        print "Main.mainwindow.getOriginalScenarioLayers(): originalScenarioLayers are " 
        for layer in self.originalScenarioLayers: print layer.name()
        print "Main.mainwindow.getOriginalScenarioLayers() currentLayers are " 
        if i > 0: 
            for layer in self.getCurrentLayers().values(): print layer.name()

    def setScenarioDirty(self):
        ''' A scenario method to set the scenarioDirty flag '''
        # debugging
        print "Main.mainwindow.setScenarioDirty()"
        print "Main.mainwindow.setScenarioDirty(): self.origScenarioLyrsLoaded is " + str(self.origScenarioLyrsLoaded)
        print "Main.mainwindow.setScenarioDirty(): self.setScenarioDirty() begin is " + str(self.scenarioDirty)
        print "Main.mainwindow.setScenarioDirty(): self.scenarioFileName is " + str(self.scenarioFileName)
        print "Main.mainwindow.setScenarioDirty(): self.openingOrientingLayers is " + str(self.openingOrientingLayers)
        
        # The line below fails because it returns false if the layer order changes
        # self.originalScenarioLayers == self.currentLayers.values()

        self.getCurrentLayersCount()
        print "Main.mainwindow.setScenarioDirty(): self.currentLayersCount is " + str(self.currentLayersCount)
        
        # if in the process of opening the orienting layers, just return
        if self.openingOrientingLayers:
            self.scenarioDirty = False
            print "Main.mainwindow.setScenarioDirty(): self.setScenarioDirty() end is " + str(self.scenarioDirty)
            return
        
        # If no scenario is open and the loaded layers are the orienting baselayers,
        # The user is probably either opening the app or has chosen "New Scenario." 
        # We don't want the scenario to be dirty because the user will get prompted
        # to save the current scenario if she wants to open a scenario or if she closes the app.
        # Under these conditions, the user will only be prompted to save the scenario when the 
        # "Edit Scenario" function is checked. 
        if self.currentLayersCount == len(config.allOrientingLayers) and self.scenarioFileName == None:
            print "Main.mainwindow.setScenarioDirty(): Entered length = allOrientingLayers loop"
            orientingLayerNames = []
            for fileName in config.allOrientingLayers:
                info = QtCore.QFileInfo(fileName)  
                name = info.completeBaseName()
                orientingLayerNames.append(name)
            legendLayerNames = []
            # legendLayers are QgsMapCanvasLayers
            legendLayers = self.legend.getLayerSet()
            for layer in legendLayers: legendLayerNames.append(layer.layer().name())
            print "Main.mainwindow.setScenarioDirty(): orientingLayerNames are"
            for name in orientingLayerNames: print name.toUtf8()  
            print "Main.mainwindow.setScenarioDirty(): legendLayerNames are "
            for name in legendLayerNames: print name.toUtf8()
            difference = [name for name in orientingLayerNames if name not in legendLayerNames]
            print "Main.mainwindow.setScenarioDirty(): difference is"
            print difference
            if difference == []:
                self.scenarioDirty = False
                print "Main.mainwindow.setScenarioDirty(): setScenarioDirty() difference == []"
                print "Main.mainwindow.setScenarioDirty(): self.setScenarioDirty() end is " + str(self.scenarioDirty)
                return
        
        # If the above is not true and if the layer count is > 0 and there is no scenario open 
        # then the scenario is dirty. This would and should be true even
        # if the user removed all the intially loaded layers and then loaded an orienting
        # baselayer, because that might be a scenario they want to save for some reason.  
        if self.currentLayersCount > 0 and self.scenarioFileName == None:
            self.scenarioDirty = True
            print "Main.mainwindow.setScenarioDirty(): layer count > 0 if statement"
            print "Main.mainwindow.setScenarioDirty(): self.setScenarioDirty() end is " + str(self.scenarioDirty)
            return
    
        # Now we handle if a scenario is open
        # Check the flag to see if all scenario layers are loaded
        if self.origScenarioLyrsLoaded:
            # compare the lenth of the list for the original and current layers
            if len(self.originalScenarioLayers) != self.currentLayersCount:
                # if they are not the same length, the scenario is dirty
                self.scenarioDirty = True
                print "Main.mainwindow.setScenarioDirty(): self.setScenarioDirty() end is " + str(self.scenarioDirty)
                return
            
            # the layers are the same length but do they have the same members?
            differences = []
            # this is what Python calls a "list comprehension"
            differences = [name for name in self.getCurrentLayersNames() if name not in 
                                                            self.originalScenarioLayersNames]
            # debugging
            print "Main.mainwindow.setScenarioDirty(): currentLayersNames are"
            for name in self.getCurrentLayersNames(): print name
            print "Main.mainwindow.setScenarioDirty(): self.originalScenarioLayersNames are"
            for name in self.originalScenarioLayersNames: print name
            print "Main.mainwindow.setScenarioDirty(): differences are "
            for name in differences: print name
            
            if differences: self.scenarioDirty = True # if there are differences
            else: self.scenarioDirty = False
        
        # debugging
        print "Main.mainwindow.setScenarioDirty(): self.scenarioDirty end is " + str(self.scenarioDirty)

    def setScenarioSaved(self):
        ''' Scenario method to do the housekeeping for a successfully saved scenario '''
        # debugging
        print "Main.mainwindow.setScenarioSaved()"
        # no errors so scenario saved and not dirty
        self.scenarioDirty = False
        # all scenario layers are loaded so set flag
        self.origScenarioLyrsLoaded = True
        # Reset the original scenario layers so we can delete editing layers
        # that have not been saved when closing a scenario or the app.
        # We also use this to check if the scenario is dirty.
        self.originalScenarioLayers = self.getCurrentLayers().values()
        # sets the instance variable self.originalScenarioLayersNames
        self.getOriginalScenarioLayersNames()
        # get the complete filename without the path
        self.scenarioFileName = unicode(self.scenarioInfo.fileName())
        # give the user some info
        self.setWindowTitle("Conservation Assessment and \
Prioritization System (CAPS) Scenario Builder - " + self.scenarioFileName)

    def makeScenarioDirectory(self):
        ''' Scenario method to create a directory to store a scenario's editing files '''
        # debugging
        print "Main.mainwindow.makeScenarioDirectory()"
        
        # We are creating a new scenario, so remove any old edit files directory 
        # (and files), or exported scenarios with same name.
        scenarioDirectoryName = self.scenarioInfo.completeBaseName()
        dirPath = unicode(self.scenarioInfo.path() + "/" + scenarioDirectoryName)
        exportFileName = unicode(scenarioDirectoryName + ".csv")
        exportPath = unicode(config.scenarioExportsPath + exportFileName)

        # debugging
        print "Main.mainwindow.makeScenarioDirectory(): scenarioDirectoryName is " + str(scenarioDirectoryName)
        print "Main.mainwindow.makeScenarioDirectory(): directoryPath is " + str(dirPath)
        
        error = None
        if QtCore.QDir(config.scenariosPath + scenarioDirectoryName).exists():    
            try:
                if os.path.exists(exportPath):
                    os.remove(exportPath) # use Python here
                shutil.rmtree(dirPath)
                # Give the os some time to delete files before trying to create new directory
                # with the same name
                time.sleep(1) 
            except (IOError, OSError), e:
                error = unicode(e)
            if error:
                print e
                QtGui.QMessageBox.warning(self, "Deletion error:", "The scenario editing \
file directory or export files could not be completely removed. Please check if one of the \
files in the scenario is open in another program and then try again.")
                return "Error"
        # now make the new directory        
        if QtCore.QDir().mkdir(config.scenariosPath + scenarioDirectoryName):
                print "Main.mainwindow.makeScenarioDirectory(): directory made"
        else: 
            QtGui.QMessageBox.warning(self, "Failed to create directory:", "The scenario \
editing file directory could not be created. Please try to save the project again, or save it with a \
different name.")
            return "Error"

    def checkScenarioDirectoryPath(self, defaultDir, scenarioFilePath):
        ''' A scenario method to check if the user is saving scenario's to the proper directory '''
        # debugging
        print "Main.mainwindow.checkScenarioDirectoryPath()"
        
        dirInfo = QtCore.QFileInfo(defaultDir)
        defaultScenarioDirectoryPath = unicode(dirInfo.absoluteFilePath())
        print "Main.mainwindow.checkScenarioDirectoryPath(): defaultScenarioDirectoryPath is " + defaultScenarioDirectoryPath # Python can concatenate QStrings
        scenarioFileInfo = QtCore.QFileInfo(scenarioFilePath)
        scenarioDirectoryPath = unicode(scenarioFileInfo.absolutePath())
        fileName = unicode(scenarioFileInfo.fileName()) # change to unicode for Python string operations
        print "Main.mainwindow.checkScenarioDirectoryPath(): The scenarioDirectoryPath is " + scenarioDirectoryPath
        print "Main.mainwindow.checkScenarioDirectoryPath(): The fileName is " + fileName

        if (scenarioDirectoryPath != defaultScenarioDirectoryPath  and 
            scenarioDirectoryPath != defaultScenarioDirectoryPath[:-1]): # not fileName.endswith(".cap")
            QtGui.QMessageBox.warning(self, "File Save Error:", "Scenarios must be saved in the 'Scenarios' directory, \
which the 'Save Scenario as...' dialog opens by default.  Also, the file name must end with the extension \
'.cap'. If you save a scenario name without adding an extension, the file dialog will add the '.cap' extension for you. \n\n\
Your scenario was not saved.  Please try again.")
            return False
        else: return True

    def copyScenario(self, oldScenarioInfo, scenarioDirectoryName, editLayerLegendItems):
        ''' A scenario method to copy all the files of an existing scenario. '''
        # debugging
        print "Main.mainwindow.copyScenario()" 
        
        # So we have editing files open so create the new scenario directory to write them to.
        # This method deletes any old directory and any old "Scenario Export" files having the
        # same name as the new scenario name.  So if we are overwriting an old scenario, we
        # start fresh.
        self.makeScenarioDirectory()
        
        # Now copy any existing "Export Scenario" file 
        oldScenarioDirectoryName = unicode(oldScenarioInfo.completeBaseName())
        oldExportFileName = oldScenarioDirectoryName + ".csv" # Python elevates to unicode
        oldExportPath = config.scenarioExportsPath + oldExportFileName # so unicode too
        newExportFileName = scenarioDirectoryName + ".csv" # unicode
        newExportFilePath = config.scenarioExportsPath + newExportFileName # unicode
        
        oldExportFile = QtCore.QFile(oldExportPath)
        error = None
        if oldExportFile.exists():
            try:
                oldExportFile.copy(newExportFilePath)
            except (IOError, OSError), e:
                error = unicode(e)
            if error:
                print error
                QtGui.QMessageBox.warning(self, 'Deletion Error:', 'The previously saved scenario export file'\
+ oldExportFileName + ' could not be renamed.  Please try again.')
        
        # While the editing layers are open, copy them to the new scenario directory
        # and record the paths to open them later.
        scenarioDirectoryPath = unicode(config.scenariosPath + scenarioDirectoryName)
        copyPaths = []
        editLayerIds = []
        for item in editLayerLegendItems:
            vlayerId = item.layerId
            editLayerIds.append(vlayerId)
            vlayer = QgsMapLayerRegistry.instance().mapLayer(vlayerId)
            vlayerName = vlayer.name() + ".shp"
            copyPath = scenarioDirectoryPath + "/" + vlayerName
            copyPaths.append(copyPath)
            print "Main.mainwindow.copyScenario(): copyPath is " + copyPath
            error = QgsVectorFileWriter.writeAsVectorFormat(vlayer, copyPath , "utf-8", 
                                                                self.crs, "ESRI Shapefile")
            if error != QgsVectorFileWriter.NoError:
                QtGui.QMessageBox.warning(self, "Write Error:", "The file " + vlayerName + " \
was not written.  Please check that a file with the same name is not open in another program.")
                return
            else: print "Main.mainwindow.copyScenario(): Success, editing layers copied!"

        # debugging
        print "Main.mainwindow.copyScenario(): copyPaths are:"
        print copyPaths
        
        # Now we can close the editing layers associated with the old scenario path
        # and then open the ones we wrote to the new directory.  This will allow us 
        # to save a new scenario file (i.e. '.cap' file) that contains the correct
        # paths to the copied editing shapefiles. No need for emitting signals here.
        self.legend.blockSignals(True)
        self.legend.removeLayers(editLayerIds) # this method also removes the files from the registry
        self.legend.blockSignals(False)
        print "Main.mainwindow.copyScenario(): CLOSED OLD EDIT SHAPEFILES"
        
        # The old activeVLayer may have been deleted so set all associated variables to "None"
        #  or we would get runtime errors due to the underlying C++ object being deleted.
        # The activeVLayer will be reset when we load the layers below.
        self.legend.setActiveLayerVariables()
        self.originalScenarioLayers = []
        # Open the copied editing shapefiles (they will open at the top of the layer panel)
        # The last one opened will become the new activeVLayer
        for path in copyPaths:
            # return on error, openVectorLayer() provides the error message box
            if not self.openVectorLayer(path): return
            
        # if we have opened a scenario edit type
        if self.dlgScenarioEditTypes:
            # We opened new editing layers, so color the text of the editing and base layers.
            # The below works because the instance variable remains active
            self.dlgScenarioEditTypes.colorEditBaseConstraintLayers(self.legend)
            # Now we position the editing layer and any base layer or constraints layer that exists
            # for the current scenario edit type.
            self.dlgScenarioEditTypes.moveLayer(self.legend, self.dlgScenarioEditTypes.editLayerBaseName, 0)
            if (self.dlgScenarioEditTypes.baseLayerBaseName and 
                            self.dlgScenarioEditTypes.baseLayerBaseName != config.polygonBaseLayersBaseNames[1]): 
                self.dlgScenarioEditTypes.moveLayer(self.legend, self.dlgScenarioEditTypes.baseLayerBaseName, 1)
            if self.dlgScenarioEditTypes.constraintLayerBaseName:
                if self.dlgScenarioEditTypes.baseLayerBaseName: position = 2
                else: position = 1 
                self.dlgScenarioEditTypes.moveLayer(self.legend, self.dlgScenarioEditTypes.constraintLayerBaseName, position)
                         
        # Finally, write the project information to a scenario file using QgsProject
        scenario = QgsProject.instance()
        scenario.write(self.scenarioInfo)
        # check for write error
        if scenario.error():
            QtGui.QMessageBox.warning(self, "Failed to save:", "Please check \
if this scenario file is open in another program.")
            # QgsProject has no "close()" method, so, if error, close the project instance
            scenario = None
            return
        scenario = None # if no error close the QgsProject.instance()

############################################################################################   
    ''' EDIT MENU CUSTOM SLOTS AND METHODS '''
############################################################################################
 
    def selectFeatures(self, state):
        ''' Edit menu SLOT '''
        # debugging
        print "Main.mainwindow.selectFeatures() " + str(state)
  
        if state: # for action selected state = True
            # debugging
            print "Main.mainwindow.selectFeatures() state is True"
            # Need this to stop user from taking this action if making line or polygon edits
            if self.appStateChanged("selectFeatures") == "Cancel":
                #self.mpActionSelectFeatures.blockSignals(True)
                #self.mpActionSelectFeatures.setChecked(False)
                #self.mpActionSelectFeatures.blockSignals(False)
                return
            
            # select action is selected so enable these tools
            self.canvas.setMapTool(self.toolSelect)
            self.enableSelectSubActions()
        else: # action deselected (state = False)
            # debugging
            print "Main.mainwindow.selectFeatures() state is False"
            # select action is not selected so disable the select sub actions if no selections have been made
            if len(self.activeVLayer.selectedFeatures()) == 0:
                self.disableSelectActions()  
 
    def deselectFeatures(self):
        ''' Edit menu SLOT to clear the selected features without deleting them '''
        # debugging
        print "Main.mainwindow.deselectFeatures()"
        
        # selectedFeatures() returns a QgsFeatureList
        count = self.activeVLayer.selectedFeatureCount()
        
        # check if there are any features to deselect 
        if count == 0:
            title = "Deselect Features"
            text = "You must select at least one feature \
before you can deselect."
            QtGui.QMessageBox.information(self, title, text, QtGui.QMessageBox.Ok)
        else:
            # The boolean parameter "False" is whether to emit a signal or not
            self.activeVLayer.removeSelection(False)
            self.canvas.refresh()

    def copyFeatures(self):
        ''' Edit menu SLOT to handle copying features '''
        # debugging
        print "Main.mainwindow.copyFeatures()"

        self.copyFlag = False
        # store the feature geometry and count as an instance variable 
        # for use in pasteFeatures()
        self.copiedFeatCount = self.activeVLayer.selectedFeatureCount()
        # check if there are any features to copy 
        if self.copiedFeatCount == 0:
            title = "Copy Features"
            text = "You must select at least one feature to copy."
            QtGui.QMessageBox.information(self, title, text, QtGui.QMessageBox.Ok)
        else: # so we have features to copy
            # This method copies the features, but the same method is used in deleteFeatures
            self.copyFeaturesShared()
        # we have copied features so enable the paste action
        self.mpActionPasteFeatures.setDisabled(False)
 
    def modifyFeatures(self):
        ''' Edit menu SLOT to allow the user to modify points on base layers and features on any editing layer'''
        # debugging
        print "Main.mainwindow.modifyFeatures()"
        
        # check if there are any features selected to modify 
        count = self.activeVLayer.selectedFeatureCount()
        if count == 0:
            title = "Modify Selected Features"
            text = "You must select at least one feature on the points base layer or \
or an editing layer for the current scenario edit type before you can modify it. \
If you have correctly selected points and you get this message then you need to make \
sure that the layer you want to modify is the currently active layer."
            # pop up message box to inform user that nothing is selected
            QtGui.QMessageBox.information(self, title, text, QtGui.QMessageBox.Ok)
            return
        
        # Note that the "Modify Features" action only becomes enabled when a 
        # base layer or editing layer is active.
        # Check whether we are modifying base layer or editing layer features.
        name = unicode(self.activeVLayer.name())
        if name in config.pointBaseLayersBaseNames:
            # Now check if the base layer  matches the scenario edit type.  If it does not, we get
            # incorrect entries in the editing shapefile attribute table! The method warns on error.
            title = "Modify Point Error:"
            text = "modify"
            if not self.checkBaseLayerMatch(title, text): return
            # We have features selected from the correct base layer, so copy them
            self.copyFeaturesShared()
            # Warn if "edit_scenario(points).shp if it is not open. If open, make it the activeLayer
            items = self.legend.findItems(config.editLayersBaseNames[0], QtCore.Qt.MatchFixedString, 0)
            if len(items) == 0:
                QtGui.QMessageBox.warning(self, "Modify Selected Error", "The 'edit_scenario(points)' layer \
must be open for you to modify point features.  Please click the 'Edit Scenario' button twice, choose the \
scenario edit type that has the features you wish to modify, and then try again.")
                return
            else: 
                # **  could the user have moved the edit points layer?? Should I move to the top?? **
                self.legend.setCurrentItem(items[0])
                self.legend.currentItem().setCheckState(0, QtCore.Qt.Checked)
                self.pasteModifiedBaseLayerFeats()
        elif name in config.editLayersBaseNames:
            # Force the user to save or discard unsaved edits before we bother to modify them.
            if self.appStateChanged("modifyingEdits") == "Cancel":
                    return
            # check if editing layer chosen is correct for the current scenario edit type 
            # (this method warns the user and returns false if no match)
            if not shared.checkSelectedLayer(self, self.scenarioEditType, name):
                return
            # So we have the edit layer for the current scenario edit type but do the selected features
            # all match the current scenario edit type?
            editLayer = self.getLayerFromName(self.editLayerName) # use the instance variable as a double check
            features = editLayer.selectedFeatures()
            print "Main.mainwindow.modifyFeatures(): The selected feature count is " + str(editLayer.selectedFeatureCount())
            # This method checks if the attribute values for all the selected features match the
            # current scenario edit type. The method warns and returns false if one or more do not match.
            if not self.checkEditFeatureMatch(editLayer, features):
                return
            # Now check for a user attempting to delete "deletions" on a point editing layer
            if editLayer.geometryType() == 0:
                if not self.checkForDeletions(editLayer, features):
                    return
            # so we have proper features of the current scenario edit type to modify
            self.copyFeaturesShared()
            self.modifyEditLayerFeatures()
  
    def deleteFeatures(self):
        ''' 
            Edit menu SLOT to delete selected features. This method handles deleting (i.e. undoing)
            edits made to editing layers, deleting features from base layers (i.e. pasting them into
            an editing layer), and a user deleting features from a layer belonging to the user.
         '''
        # debugging
        print "Main.mainwindow.deleteFeatures(): activeVLayer.name() is " + self.activeVLayer.name()

        # selectedFeatures() returns the selected features as a QgsFeatureList
        selectedFeats = self.activeVLayer.selectedFeatures()
        count = self.activeVLayer.selectedFeatureCount()

        # check if there are any features to delete 
        if count == 0:
            title = "Delete Selected Features"
            text = "You must select at least one feature before you can delete."
            # pop up message box to inform user that nothing is selected
            QtGui.QMessageBox.information(self, title, text, QtGui.QMessageBox.Ok)
            return
        
        vfileName = unicode(self.activeVLayer.name())
        # Check what the user is deleting and set appropriate message
        if vfileName in config.editLayersBaseNames:
            title = "Delete Scenario Edits:"
            text = "Do you want to delete, that is undo, "  + unicode(count) + \
" scenario edit(s)?  Please note that no changes will be made to any base layer."
        elif vfileName in config.pointBaseLayersBaseNames: # deleting points from a base layer
            title = "Delete Selected Features:"
            text = "Delete " + unicode(count) + " feature(s)? Please note that no \
changes will be made to the base layer."
        else: # deleting points from a user's layer
            title = "Delete Selected Features"
            text = "Permanently delete " + unicode(count) + " feature(s)?"
        
        # Now check with the user about deleting the features 
        reply = QtGui.QMessageBox.question(self, title, text, QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Ok)
        if reply == QtGui.QMessageBox.Ok: # if yes, then do the deletion
            if vfileName in config.pointBaseLayersBaseNames: # deleting base layer features
                # This method checks if the base layer matches the scenario edit type. The method warns the user and
                # returns false on error (title = "Deletion Error:" # (title = "Deletion Error:" text = "delete from")
                if not self.checkBaseLayerMatch("Deletion Error:", "delete from"): return
                else:
                    # We do not allow deleting features from a base layer.  Rather, we copy
                    # the features the user wants to delete, and paste them into an editing shapefile.
                    self.copyFeaturesShared()
                    baseLayerName = vfileName # just for code readability
                    self.pasteBaseLayerDeletions(baseLayerName)
                    return
            else: # handles the cases where we are deleting editing layer features or features on a user's layer
                pyList = [] # make a Python list of features to delete
                feat = QgsFeature()
                for feat in selectedFeats:
                    print "Main.mainwindow.deleteFeatures(): starting ids of deleted features " + str(feat.id())
                    pyList.append(feat.id())
    
                # provider.deleteFeatures only works with a Python list as a parameter.  
                # Note that the spaces between the list brackets and parentheses
                # are necessary or it doesn't work!! We delete and check for error 
                # in the same if statement
                if not self.provider.deleteFeatures( pyList ): # returns false on failed deletion
                    QtGui.QMessageBox.warning(self, "Failed to delete features", "Please check if " + vfileName + 
                                                                    " is open in another program and then try again.")
                    return # delete failed so return
               
                ''' Features successfully deleted '''
                
                # if this is an editing layer, reset the id numbers for the layer
                if vfileName in config.editLayersBaseNames:
                    shared.resetIdNumbers(self.provider, self.geom)
                    self.editDirty = True
                # empty the selections cache when done or it stays at 'count'
                self.activeVLayer.removeSelection(False) # false indicates whether to emit a signal
                # reset the select tool
                self.disableSelectActions()
                # update all the extents for the user's layer (will close and reopen editing layer to set extents)
                shared.updateExtents(self, self.activeVLayer, self.canvas)
                # update Vector Attribute Table if open
                if self.attrTable != None and self.attrTable.isVisible():
                    self.openVectorAttributeTable()
        else: return # user has cancelled in the dialog       

    def pasteFeatures(self):
        ''' 
            Edit menu SLOT. This method handles pasting features from a user's file into an editing shapefile.
            
            Pasting features can only be done in "Edit Scenario" mode.  Features 
            can be copied from any user's file, but can only be pasted into an editing shapefile.
            
        ''' 
        # debugging
        print "Main.mainwindow.pasteFeatures()"
        print "Main.mainwindow.pasteFeatures(): copied feat count = " + str(self.copiedFeatCount)
        print "Main.mainwindow.pasteFeatures(): copied feat geometry " + str(self.copiedFeatGeom)
        print "Main.mainwindow.pasteFeatures(): self.geom is " + str(self.geom)
  
        ''' CHECK FOR USER ERROR AND SET INTIAL CONDITIONS '''
 
        # Check if user has chosen the correct editing shapefile to paste to
        vlayerName = unicode(self.activeVLayer.name())
        # This method checks if the active layer is the baselayer that corresponds to the current scenario edit type.
        # The method warns the user and returns False on error.
        if not shared.checkSelectedLayer(self, self.scenarioEditType, vlayerName):
            return
       
        # The activeVLayer is the correct editing layer, but for insurance against any bugs, use the name 
        # of the current edit Layer set by DlgScenarioEditTypeswhen the scenario edit type was chosen
        editLayerName = self.editLayerName
        editLayer = self.getLayerFromName(editLayerName)
        editLayerProvider = editLayer.dataProvider() 
                
        # Inform user if attempting to paste into incompatible layer type. This can happen if the user
        # copies features from a layer with different geometry than the current scenario edit type.
        copyGeom = self.getGeometryName(self.copiedFeatGeom)
        activeGeom = self.getGeometryName(self.geom) #0 point, 1 line, 2 polygon
        if self.geom != None:
            if self.geom != self.copiedFeatGeom:  
                title = "Paste Features"
                text = "You cannot paste " + copyGeom + " into a " + activeGeom + " vector layer."
                QtGui.QMessageBox.information(self, title, text, QtGui.QMessageBox.Ok)
                return
 
        # If a pasted point(s) or lines, make sure constraints are met.  Method checks point and line features.
        # The method warns user and returns False if constraints are not met
        if not self.checkPastedFeatureConstraints():
            return
        
        # Now that we have good features and a correct layer to paste to:
        # The user could have added features or made other edits to the editing layer without
        # saving them as of yet, so we cannot use the variable self.originalEditLayerFeats here.
        # Rather, we set tempOriginalFeats (the list of ids of current edit layer features)  
        # in case the user wants to cancel the pasting process and discard the pasted features below.
        tempOriginalEditFeats = shared.listOriginalFeatures(self, editLayerName)
        
        ''' 
            PASTE THE FEATURES WITH EMPTY ATTRIBUTE DATA SO THEY CAN BE SELECTED ON THE 
            MAP CANVAS WHEN THE USER INPUTS NEW ATTRIBUTE DATA FOR EACH FEATURE.    
        '''
        
        # We can paste points, lines or polygons so we get the field names for the scenario edit
        # type, set the attributes of the pasted features to empty and paste into the editing layer.
        # Pasting features with empty attributes allows us to select each 
        # feature on the map canvas when the user inputs data for that feature.   
        if not self.pasteEmptyFeatures(editLayerProvider):
            return
        
        # The provider gives the pasted features new id's when they are added
        # to the editing shapefile.  Here we compare the editing layer's feature ids  
        # before and after pasting and then return the difference between the two
        # to get the new ids.  pastedFeatureIDS is a python list.
        pastedFeatureIds = shared.getFeatsToDelete(editLayerProvider, tempOriginalEditFeats)
        
        print "Main.mainwindow.pasteFeatures(): The pasteFeatureIDS[] are:"
        print pastedFeatureIds
         
        '''  
            WE NEED TO ITERATE THROUGH THE PASTED FEATURES, SELECT EACH ONE
            ON THE MAP CANVAS(FOR THE USER'S CONVENIENCE), OPEN THE "ADD ATTRIBUTES" DIALOG
            AND GET THE USER INPUT DATA FOR EACH FEATURE. 
        '''
        
        # This method opens the Add Attributes dialog and a window to provide the user with information about the 
        # feature she is pasting.  It warns the user and returns False on error
        if not self.getAttsForPastedOrModifiedFeats(pastedFeatureIds, editLayer, tempOriginalEditFeats, "userlayer", False):
            return
        
        '''PASTING COMPLETED, SO DO SOME HOUSEKEEPING '''
        
        self.setPasteModifySuccess()
            
    def editScenario(self, state):
        ''' Edit menu SLOT that handles starting and stopping editing mode '''
        # debugging
        print "Main.mainwindow.editScenario() " + str(state)

        if state: # True if action activated
            
            '''# handle user cancel
            if self.appStateChanged("startingEditing") == "Cancel":
                self.mpActionEditScenario.blockSignals(True)
                self.mpActionEditScenario.setChecked(False)
                self.mpActionEditScenario.blockSignals(False)
                return'''
            
            # We cannot make edits unless there is a named 
            # scenario open.  Check for open scenario here.
            if not self.scenarioFileName:
                QtGui.QMessageBox.warning(self, "Scenario Editing Error", "The scenario must have a name \
before you can make edits.  Please save the current scenario or open an existing scenario.")
                self.mpActionEditScenario.blockSignals(True)
                self.mpActionEditScenario.setChecked(False)
                self.mpActionEditScenario.blockSignals(False)
                return
            
            # open the dialog to get the scenario edit type
            self.dlgScenarioEditTypes = DlgScenarioEditTypes(self)
            if not self.dlgScenarioEditTypes.exec_():
                print "Main.mainwindow.editScenario(): user cancelled DlgScenarioEditTypes"
                # If the user cancels, or there is an error opening the editing file then
                # uncheck the Edit Scenario button and  return
                self.mpActionEditScenario.blockSignals(True)
                self.mpActionEditScenario.setChecked(False)
                self.mpActionEditScenario.blockSignals(False)
                return 

            # set the paste action
            if self.copyFlag: self.mpActionPasteFeatures.setDisabled(False)
         
            # add scenarioEditType to statusbar
            if self.editTypeLabel: # for insurance
                self.statusBar.removeWidget(self.editTypeLabel)
            self.editTypeLabel = QtGui.QLabel(self.statusBar)
            captureString = "Scenario edit type:  '" + self.scenarioEditType + "'"
            self.editTypeLabel.setText(captureString)
            self.statusBar.insertPermanentWidget(0, self.editTypeLabel)        
        else: #False action deactivated
            # check for unsaved edits when deselecting "Edit Scenario"
            # return mpActionEditScenario to previous state on cancel
            if self.appStateChanged("stoppingEditing") == "Cancel":
                self.mpActionEditScenario.blockSignals(True)
                self.mpActionEditScenario.setChecked(True)
                self.mpActionEditScenario.blockSignals(False)
                return
            
            self.editMode = False
            self.editLayerName = None
            # unset the select tool
            self.mpActionSelectFeatures.setDisabled(True)
            # remo ve any selections
            if self.activeVLayer: self.activeVLayer.removeSelection(False)
            self.disableSelectActions()
            
            # unset the paste action (only active  in edit mode)
            self.mpActionPasteFeatures.setDisabled(True)
            # unset edit tool actions
            self.disableEditActions()
            print "Main.mainwindow.editScenario(): setDisabled = True"
            
            self.editDirty = False
            
            # remove the 'editTypeLabel' permanent message from the statusBar
            self.statusBar.removeWidget(self.editTypeLabel)
            self.editTypeLabel = None

    def addPoints(self, state):
        ''' Edit menu SLOT that activates/deactivates the add points tool'''
        # debugging
        print "Main.mainwindow.addPoints() " + str(state)
        
        if state: self.canvas.setMapTool(self.toolAddPoints)
        else: self.canvas.unsetMapTool(self.toolAddPoints)
    
    def addLines(self, state):
        ''' Edit menu SLOT that activates/deactivates the add lines tool'''
        # debugging
        print "Main.mainwindow.addLines()"
        if state: self.canvas.setMapTool(self.toolAddLinesPolygons)
        else:  self.canvas.unsetMapTool(self.toolAddLinesPolygons)
          
    def addPolygons(self, state):
        ''' Edit menu SLOT that activates/deactivates the add polygons tool'''
        # debugging
        print "Main.mainwindow.addPolygons()"
        
        self.addLines(state)
        
    def saveEdits(self):
        ''' Edit menu SLOT that manages the save edits action'''
        # debugging
        print "Main.mainwindow.saveEdits(): self.scenarioDirty begin is " + str(self.scenarioDirty)
        print "Main.mainwindow.saveEdits(): self.editDirty begin is " + str(self.editDirty)
             
        # This gives a save message only if the user clicks the Save Edits action
        # or if there are no edtis to save.
        title = "Save Edits"
        if not self.editDirty: 
            text = "You have not made any edits to save!"
            QtGui.QMessageBox.information(self, title, text, QtGui.QMessageBox.Ok)
            
        # The editing tools save the edits to disk as they are made. So, to delete
        # new features, we list the original features when editing starts and delete
        # any feature not in the list.  To save features, we just run listOriginalFeatures
        # again with the editing layer provider
        self.originalEditLayerFeats = shared.listOriginalFeatures(self, self.editLayerName)

        # Set "Save Edits" action to disabled to let user know edits are saved.
        # Clean up
        self.mpActionSaveEdits.setDisabled(True)
        self.scenarioDirty = True
        self.editDirty = False

    # Edit Methods -----------------------------------------------------------------------------------------------    
    
    def getAttsForPastedOrModifiedFeats(self, pastedFeatureIds, editLayer, tempOriginalEditFeats, msgFlag, modifyFlag):
        '''
            This is the core edit method for the modify/paste features functionality of the application.
            
            This method gets and writes attributes for features that the user is pasting from their own layer.
            It also gets and writes attributes for base layer features that are being modified.
            Finally, this method will get and write attributes for editing layer features that the user wants to modify.
            
            This method also calls methods that provide the user with information about features being modified.
        '''

        # debugging
        print "Main.mainwindow.getAttsForPastedOrModifiedFeats()" 
        
        self.msgFlag = msgFlag # msgFlag can be "baselayer", "userlayer" or  "editlayer"
        self.tempOriginalEditFeats = tempOriginalEditFeats
        self.modifyFlag = modifyFlag # Currently true or false
       
        # set some variables based on recording the id of the layer features were copied from
        # The id was recorded in Main.mainwindow.copyFeaturesShared().
        editLayerProvider = editLayer.dataProvider()
        copyLayer = self.copyLayer
        copyLayerName = unicode(copyLayer.name())
        #self.copyLayerName = unicode(copyLayer.name())
        # this is the same as the editLayerProvider if edit layer features are being modified
        copyLayerProvider = copyLayer.dataProvider()
        allCopyAttrs = copyLayerProvider.attributeIndexes()
        self.reply = None
        # pastedFeatureIds are actually selected feature ids when modifying edit layer features
        for count, featId in enumerate(pastedFeatureIds):
            print "Main.mainwindow.getAttsForPastedOrModifiedFeats(): feat.id is " + str(featId)
            # select the feature
            editLayer.setSelectedFeatures( [featId] )
            self.canvas.zoomToSelected(self.activeVLayer)
            # set the extent so that the user can see some surrounding features
            self.setPastingExtent()
            # open the Add Attributes dialog
            self.dlgAddAtts = DlgAddAttributes(self)
            self.dlgAddAtts.setGeometry(0, 500, 200, 200)
            # display information about the copied feature for reference when adding new attributes
            self.displayCopiedFeatInfo(copyLayerProvider, allCopyAttrs, count)
            # This dialog's "reject()" method is overridden to warn the user about aborting the paste or 
            # modify operation.  If the user choses NOT to abort the method returns to the dialog and the
            # user can continue where they left off.  If the user chooses to abort,
            #  the reject() method closes the dialog and returns False.
            if self.dlgAddAtts.exec_(): # open DlgAddAttributes and then if user clicks OK it returns true
                # if this is an editing layer modification, we need to get the type of edit so that we can
                # mark it correctly in the attribute table.
                if msgFlag == "editlayer" and self.copiedFeatGeom == 0: # points edit layer
                    modifyFlag = self.isAlteredFeature(editLayer, featId) # returns True if altered, otherwise False
                # if "modified" the points are new pasted base layer modifications or edit layer points that were modifications
                if modifyFlag: 
                    # if user is modifying a point, set the altered field to 'y' by passing 'True' flag
                    attributes = self.dlgAddAtts.getNewAttributes(True)
                else: attributes = self.dlgAddAtts.getNewAttributes() # flag False for pasting user feats, modifying edits
                changedAttributes = {featId : attributes} # create a "QgsChangedAttributesMap"
                try:
                    editLayerProvider.changeAttributeValues(changedAttributes) # here is the "write" operation
                except (IOError, OSError), e:
                    error = unicode(e)
                    print "Main.mainwindow.getAttsForPastedOrModifiedFeats(): error is " + error 
                    title = "Failed to modify attributes:"
                    editLayerName = editLayer.name()
                    QtGui.QMessageBox.warning(self, title, "Please check if "
                                + editLayerName + " is open in another program and then start again.")
                    # Make sure we delete any features that may have been added to the editing layer and clean up.
                    # In the case of modifying editing layer features, the tempOriginalEditFeats are the same as
                    # the current features on the editing layer so nothing will be deleted.
                    shared.deleteEdits(self, editLayerName, tempOriginalEditFeats)
                    if msgFlag == "editlayer": self.setPasteModifySuccess(True) # some features may have been modified
                    else: self.setPasteModifyDone() # all pastes have been deleted
                    self.windModifyInfo.close()
                    # reset the active layer to the base layer being modified
                    if modifyFlag: self.setBaseLayerActive(copyLayerName)
                    return False
                self.activeVLayer.removeSelection(False) # false means do not emit signal
                self.canvas.refresh()
                if self.windModifyInfo and count == len(pastedFeatureIds) - 1:
                    self.windModifyInfo.close()
                continue
            else : # dlgAddAtts.reject() returns False (user chose to discard changes)
                # reverse the edits
                editLayerName = editLayer.name()
                # Make sure we delete any features that may have been added to the editing layer and clean up.
                # In the case of modifying editing layer features, the tempOriginalEditFeats are the same as
                # the current features on the editing layer so nothing will be deleted.
                shared.deleteEdits(self, editLayerName, tempOriginalEditFeats)
                if msgFlag == "editlayer": self.setPasteModifySuccess(True) # some features have been modified
                else: self.setPasteModifyDone() # all pastes have been deleted
                #self.mpActionModifyPoints.setDisabled(True)
                self.windModifyInfo.close()
                # reset the active layer to the base layer being modified
                if modifyFlag: self.setBaseLayerActive(copyLayerName)
                return False
                #else: continue # if reply is no, self.dlgAddAtts remains active and the loop continues        
        # loop ended successfully so
        return True
            
    def setBaseLayerActive(self, copyLayerName):
        ''' Edit method to activate the base layer containing features that were modified '''
        # debugging
        print "Main.mainwindow.setBaseLayerActive()"   
        
        items = self.legend.findItems(copyLayerName, QtCore.Qt.MatchFixedString, 0)
        print "Main.mainwindow.setBaseLayerActive(): copyLayerName is: " + copyLayerName
        if len(items) > 0:
            self.legend.setCurrentItem(items[0])
            self.legend.currentItem().setCheckState(0, QtCore.Qt.Checked)
            
    def setPasteModifyDone(self):
        ''' Edit method to clean up after pasting or modifying '''
        # debugging
        print "Main.mainwindow.setPasteMofifyDone()"
        
        self.copiedFeats = None
        self.copiedFeatGeom = None
        self.copyFlag = False
        # the paste action is turned on in copyFeatures and it is turned off here.
        self.mpActionPasteFeatures.setDisabled(True)
        
    def setPasteModifySuccess(self, modifyEdit=False):
        ''' Edit method to clean up after a successful paste or modify operation '''
        # debugging
        print "Main.mainwindow.setPasteModifySuccess()"
        
        # Note that when features are deleted, the id numbers can become inconsistent.
        # So, reset the id values.
        editLayer = self.getLayerFromName(self.editLayerName)
        editLayerProvider = editLayer.dataProvider()
        geometry = editLayer.geometryType()
        shared.resetIdNumbers(editLayerProvider, geometry)
        # Set the editDirty flag to True on pasting base layer modifications or user's 
        # features. Leave it (should be false) if modifying editing layer features.
        # Note that shared.listOriginalFeatures() will be called when the edits
        # (i.e. pasted features) are saved, so we don't need to do that here.
        if not modifyEdit:
            self.editDirty = True
        # enable the save edits button for all cases but modifying edits
        if not modifyEdit:
            self.mpActionSaveEdits.setDisabled(False)    
        # clean up copy variables and paste action
        self.setPasteModifyDone()
        # update Vector Attribute Table if open
        if self.attrTable != None and self.attrTable.isVisible():
            self.openVectorAttributeTable()
        # update all the extents and refresh to show features for all cases but modifying edits
        # since we do not add or remove any features when modifying edits, extents have not changed
        if not modifyEdit:
            shared.updateExtents(self, editLayer, self.canvas)

    def enablePointsOrLinesOrPolygons(self):
        ''' Edit method to set action states '''
        if "base" in unicode(self.activeVLayer.name()): return
        if self.geom == 0:  #0 point, 1 line, 2 polygon
            self.mpActionAddPoints.setDisabled(False)
            print "Main.mainwindow.enablePointsOrLinesOrPolygons(): geom 0" 
        elif self.geom == 1:
            self.mpActionAddLines.setDisabled(False)
            print "Main.mainwindow.enablePointsOrLinesOrPolygons(): geom 1"
        elif self.geom == 2:
            self.mpActionAddPolygons.setDisabled(False)
            print "Main.mainwindow.enablePointsOrLinesOrPolygons(): geom 2"

    def enableSelectSubActions(self):
        ''' Edit method to set action states '''
        # debugging
        print "Main.mainwindow.enableSelectSubActions()"
        if unicode(self.activeVLayer.name()) in (config.pointBaseLayersBaseNames + config.editLayersBaseNames):
            self.mpActionModifyPoints.setDisabled(False)
            # cannot copy features from a base layer or edit layer, can only select and delete or modify
            self.mpActionCopyFeatures.setDisabled(True)
        else: self.mpActionCopyFeatures.setDisabled(False)
        self.mpActionDeselectFeatures.setDisabled(False)
        self.mpActionDeleteFeatures.setDisabled(False)
   
    def disableEditActions(self):
        ''' Edit method to set action states '''
        # debugging
        print "Main.mainwindow.disableEditActions()"
        
        self.mpActionAddPoints.setChecked(False)
        self.mpActionAddPoints.setDisabled(True)
        self.mpActionAddLines.setChecked(False)
        self.mpActionAddLines.setDisabled(True)
        self.mpActionAddPolygons.setChecked(False)
        self.mpActionAddPolygons.setDisabled(True)
        #self.mpActionSaveEdits.setDisabled(True)
        
    def disableSelectActions(self):
        ''' Edit method to set action states '''
        # debugging
        print "Main.mainwindow.disableSelectActions()"
        
        self.canvas.unsetMapTool(self.toolSelect)
        # Apparently mpActionSelectFeatures--a toggled action that is part of a QActionGroup--
        # does not emit a signal if the action's state has not changed. 
        self.mpActionSelectFeatures.setChecked(False)
        self.mpActionDeselectFeatures.setDisabled(True)
        self.mpActionDeselectFeatures.setChecked(False)
        self.mpActionModifyPoints.setDisabled(True)
        self.mpActionModifyPoints.setChecked(False)
        self.mpActionDeleteFeatures.setDisabled(True)
        self.mpActionDeleteFeatures.setChecked(False)
        self.mpActionCopyFeatures.setDisabled(True)
        self.mpActionCopyFeatures.setChecked(False)
 
    def copyFeaturesShared(self):
        ''' 
            This edit method copies features and is used by Main.mainwindow.copyFeatures(), 
            Main.mainwindow. modifyFeatures, mainwindow.deleteFeatures() 
            (when deleting from config.pointBaseLayersBaseNames)
        '''
        # get the id of the layer we are copying from for use in paste features
        self.copyLayer = self.activeVLayer
        
        # make copy as instance variable so we can paste features into another layer
        # "selectedFeatures" is a QgsFeatureList (a Python list of QgsFeature objects)
        self.copiedFeats = self.activeVLayer.selectedFeatures()
        self.copiedFeatCount = self.activeVLayer.selectedFeatureCount()
        self.copiedFeatGeom = self.activeVLayer.geometryType()
        self.copyFlag = True
        
        # remove the selection from the activeVLayer and reset the select tool
        self.activeVLayer.removeSelection(False) # false means no signal emitted
        print "mainwindow.copyFeaturesShared() removed selection and selected features count is " + str(self.activeVLayer.selectedFeatureCount())
        self.activeVLayer.triggerRepaint()
        self.canvas.unsetMapTool(self.toolSelect)
        self.mpActionSelectFeatures.setChecked(False)

    def pasteBaseLayerDeletions(self, baseLayerName):
        ''' This edit method adds attribute data to pasted base layer deletions '''
        # debugging
        print "Main.mainwindow.pasteBaseLayerDeletions()"
        # Check if "edit_scenario(points) is open, and if not then warn.
        editingLayerName = config.editLayersBaseNames[0]
        items = self.legend.findItems(editingLayerName, QtCore.Qt.MatchFixedString, 0)
        print "Main.mainwindow.pasteBaseLayerDeletions(): length of item list is " + str(len(items))
        if len(items) > 0:
            self.legend.setCurrentItem(items[0])
            self.legend.currentItem().setCheckState(0, QtCore.Qt.Checked) # so we made edit_scenario(points).shp the active layer
        else:
            QtGui.QMessageBox.warning(self, "File Error", "The 'edit_scenario(points)' layer \
must be open for you to complete this action.  Please click 'Edit Scenario' twice, select \
the appropriate scenario edit type, and try again.")
            return
        
        # even though we know the active layer is edit_scenario(points) and self.provider is the correct provider
        # let's set the provider from self.editLayerName just to guard against any bugs.
        editLayer = self.getLayerFromName(self.editLayerName)
        editLayerProvider = editLayer.dataProvider()
        
        # debugging
        print "Main.mainwindow.pasteBaseLayerDeletions(): featureCount begin = " + str(self.copiedFeatCount)
      
        # get the list of fields for the current scenario edit type
        for (count, scenarioEditType) in enumerate(config.scenarioEditTypesList):
            if scenarioEditType == self.scenarioEditType:
                inputFieldNames = eval("config.inputFieldNames" + str(count))
                break
        
        # debugging 
        print "Main.mainwindow.pasteBaseLayerDeletions(): inputFieldNames are:"
        print inputFieldNames

        # get a list of all the editing layer attribute fields for the 
        # geometry type associated with the deleted features
        geom = editLayer.geometryType() 
        editFields = self.getEditFields(geom)
        a = {} # Python dictionary of attributes for the current editing layer
        # Simply add an id value and set the altered field to n and the deleted field to 'y'
        feat = QgsFeature()
        for feat in self.copiedFeats:
            subListCount = 1 # this keeps track of where we are in the inputFieldNames list
            print "Main.mainwindow.pasteBaseLayerDeletions(): feat.id is " + str(feat.id())    
            for (count, field) in enumerate(editFields):
                # Fields that are in the editing shapefile but are not used for  
                # the current scenario type are set to empty values here.
                if field not in inputFieldNames:
                    a[count] = QtCore.QVariant()
                    print "Main.mainwindow.pasteBaseLayerDeletions(): not in field names count = " + str(count)
                    continue
                # set the id field first
                if subListCount == 1:
                    a[count] = QtCore.QVariant(1)
                    subListCount = 2
                    print "Main.mainwindow.pasteBaseLayerDeletions(): first field (id) count = " + str(count)
                    continue
                # if a point layer, set the altered and deleted fields
                if geom == 0 and subListCount == 2:
                    a[count] = QtCore.QVariant("n")
                    subListCount = 3
                    print "Main.mainwindow.pasteBaseLayerDeletions(): second field (altered) count = " + str(count)
                    continue
                if geom == 0 and subListCount == 3:
                    a[count] = QtCore.QVariant("y")
                    print "Main.mainwindow.pasteBaseLayerDeletions(): third field (deleted) count = " + str(count)
                    subListCount = 4
                    continue
                # set the rest of the input fields to empty for deleted features
                a[count] = QtCore.QVariant()
                print "Main.mainwindow.pasteBaseLayerDeletions(): Set the remaining input field to empty, count = " + str(count)
            feat.setAttributeMap(a)
            try:
                editLayerProvider.addFeatures( [feat] ) 
            except (IOError, OSError), e:
                error = unicode(e)
                print error
                QtGui.QMessageBox.warning(self, "Failed to paste feature(s)", "Please check if "
                                 + self.editLayerName + " is open in another program and then try again.")    

        # reorder the id numbers
        shared.resetIdNumbers(editLayerProvider, geom)
        
        # Set the editDirty flag so that the user will be prompted to save edits or not.  
        # self.originalEditLayerFeats will be called when the edits (i.e. pasted features) are saved, so 
        # saved, so we don't need to do that here.
        self.editDirty = True
        self.mpActionSaveEdits.setDisabled(False)
        
        # the paste action is turned on in copyFeatures
        # it is turned off here or in pasteFeatures
        self.setPasteModifyDone()
        
        # update Vector Attribute Table if open
        if self.attrTable != None and self.attrTable.isVisible():
            self.openVectorAttributeTable()
        # update the extents and refresh so the features show (this will close and reopen the editing layer)
        shared.updateExtents(self, editLayer, self.canvas)
        
        # reset the base layer to be the active layer
        self.setBaseLayerActive(baseLayerName)

    def pasteEmptyFeatures(self, editLayerProvider):
        ''' An edit method that creates empty attributes for the current edit layer geometry,  
            associates the empty attributes with the feature geometry and pastes the features.
        '''
        # debugging
        print "Main.mainwindow.pasteEmptyFeatures()"
        
        # We can paste features from a user's layer of any geometry type into an editing 
        # layer, so get the list of editing shapefile fields for the current scenario edit type.
        geom = self.getLayerFromName(self.editLayerName).geometryType()
        editFields = self.getEditFields(geom)
        
        # Create an attribute map (a python dictionary) of empty values
        # for the current editing shapefile.
        keys = range(len(editFields))
        values = [QtCore.QVariant()]*len(editFields)
        attributes = dict(zip(keys, values))
        
        # debugging
        print "Main.mainwindow.pasteEmptyFeatures(): The empty attributes are:"
        print attributes
        
        # Set the attributes of the features to empty and paste.
        # Pasting features with empty attributes allows us to select each 
        # feature on the map canvas when the user inputs data for that feature.                 
        feat = QgsFeature()
        for feat in self.copiedFeats:
            feat.setAttributeMap(attributes)
            try:
                editLayerProvider.addFeatures( [feat] )
            except (IOError, OSError), e:
                error = unicode(e)
                print error                    
                QtGui.QMessageBox.warning(self, "Failed to paste feature(s)", "Please check if "
                            + self.editLayerName + " is open in another program and then try again.")
                return False
        else: return True
        
    def setPastingExtent(self):
        ''' 
            An edit method that ensures that the extents for pasted features are large enough to 
            allow the user to locate the feature on an orienting map.
        '''
        # debugging
        print "Main.mainwindow.setPastingExtent()"
        
        # make the extents a minimum of 500 meters across
        rect = self.canvas.extent()
        print "Main.mainwindow.setPastingExtent(): The original paste extents are:"
        print ("(" + str(rect.xMinimum()) + ", " + str(rect.yMinimum()) + ", " + 
                 str(rect.xMaximum()) + ", " + str(rect.yMaximum()) + ")")
        if rect.width() < 500 or rect.height() < 500:
            centerPointX = rect.center().x() 
            rect.setXMinimum(centerPointX - 250)
            rect.setXMaximum(centerPointX + 250)
            print "Main.mainwindow.setPastingExtent(): The adjusted paste extents are:"
            print ("(" + str(rect.xMinimum()) + ", " + str(rect.yMinimum()) + ", " + 
                 str(rect.xMaximum()) + ", " + str(rect.yMaximum()) + ")")
            self.canvas.setExtent(rect)
            self.canvas.refresh()

    def displayCopiedFeatInfo(self, copyLayerProvider, allCopyAttrs, count):
        ''' An edit method that opens a dialog to display informatio about features being pasted or modified '''
        # debugging
        print "Main.mainwindow.displayCopiedFeatInfo()"
        
        # get the data for the current feature
        copiedFeatId = self.copiedFeats[count].id()
        copiedFeat = QgsFeature()
        copyLayerProvider.featureAtId(copiedFeatId, copiedFeat, True, allCopyAttrs)
        # A QgsAttributeMap is a Python dictionary (key = field id : value = 
        # the field's value as a QtCore.QVariant()object
        attrs = copiedFeat.attributeMap()
        print "Main.mainwindow.displayCopiedFeatInfo(): length of attrs is " + str(len(attrs))
        # return the features geometry as coordinates
        featGeom = copiedFeat.geometry()
        # create the text for the geometry in display window
        text = "Feature ID %d: %s\n" % (copiedFeat.id()+1, featGeom.exportToWkt())
        print "Main.mainwindow.displayCopiedFeatInfo(): The Feat ID and Wkt is " + text
        # get the field name and attribute data for each attribue and add to the text
        # fields() returns a dictionary with the field key and the name of the field
        fieldNamesDict = copyLayerProvider.fields()
        print "Main.mainwindow.displayCopiedFeatInfo(): The field names dict is "
        print fieldNamesDict
        for (key, attr) in attrs.iteritems():
            print "Main.mainwindow.displayCopiedFeatInfo(): key is: " + str(key)
            text += "%s: %s\n" % (fieldNamesDict.get(key).name(), attr.toString())
        # set the title for the display window
        title = "Unmodified Feature's Geometry and Attribute Information"
        self.openModifyInfoWindow(title, text)

    def openModifyInfoWindow(self, title, text):
        ''' An edit method to create the window to display information about a vector or raster layer '''
        # debugging
        print "Main.mainwindow.identify.displayInformation()"
        
        # See Main.mainwindow.openRasterCategoryTable() for a description of the following code: 
        self.windModifyInfo = QtGui.QDockWidget(title, self.dlgAddAtts)
        self.windModifyInfo.setFloating(True)
        self.windModifyInfo.setAllowedAreas(QtCore.Qt.NoDockWidgetArea)
        self.windModifyInfo.setMinimumSize(QtCore.QSize(450, 300))
        self.windModifyInfo.show()
        self.textBrowserModifyInfo = QtGui.QTextBrowser()
        self.textBrowserModifyInfo.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.textBrowserModifyInfo.setFontPointSize(9.0)
        self.textBrowserModifyInfo.setText(text)
        self.windModifyInfo.setWidget(self.textBrowserModifyInfo)

    def pasteModifiedBaseLayerFeats(self):
        ''' An edit method to paste modified base layer features '''
        # debugging
        print "Main.mainwindow.pasteModifiedFeatures()"
        
        ''' 
            This method handles the user choosing the "Modify Features" action after selecting
            features from the base layer corresponding to the current scenario edit type.
            
            Note that this method duplicates some code and commenting in Main.mainwindow.pasteFeatures(),
            but we accept the extra code to reduce confusion and facilitate debugging and future modifications.
        '''
        # debugging
        print "Main.mainwindow.pasteModifiedBaseLayerFeats()"

        # If we are modifying a point, we checked that the base layer matched the scenario edit type
        # and programmatically selected the correct edit layer to paste to in Main.mainwindow.modifyFeatures()
        # self.editLayerName was set by DlgScenarioEditTypeswhen the scenario edit type was chosen.
        editLayerName = self.editLayerName 
        editLayer = self.getLayerFromName(editLayerName)
        editLayerProvider = editLayer.dataProvider() 
        
        # Set some variables based on recording the id of the layer features were copied from.
        # The id was recorded in Main.mainwindow.copyFeaturesShared().
        copyLayer = self.copyLayer
        copyLayerName = unicode(copyLayer.name())
                
        # Set tempOriginalFeats (the list of ids of current edit layer features) 
        # in case the user wants to delete the pasted features below.
        tempOriginalEditFeats = shared.listOriginalFeatures(self, editLayerName)
        
        ''' 
            PASTE THE FEATURES WITH EMPTY ATTRIBUTE DATA SO THEY CAN BE SELECTED ON THE 
            MAP CANVAS WHEN THE USER INPUTS NEW ATTRIBUTE DATA FOR EACH FEATURE.    
        '''
        
        # Set the attributes of the features to empty and paste into the editing layer.
        # Pasting features with empty attributes allows us to select each 
        # feature on the map canvas when the user inputs data for that feature.   
        if not self.pasteEmptyFeatures(editLayerProvider):
            return
        
        # The provider gives the pasted features new id's when they are added
        # to the editing shapefile.  Here we compare the editing layer's feature ids  
        # before and after pasting and then return the difference between the two
        # to get the new ids.  pastedFeatureIDS is a python list.
        
        pastedFeatureIds = shared.getFeatsToDelete(editLayerProvider, tempOriginalEditFeats)

        '''  
            WE NEED TO ITERATE THROUGH THE PASTED FEATURES, SELECT EACH ONE
            ON THE MAP CANVAS(FOR THE USER'S CONVENIENCE), OPEN THE "ADD ATTRIBUTES" DIALOG
            AND GET THE USER INPUT DATA FOR EACH FEATURE. 
        '''
        
        # This method opens the Add Attributes dialog and a window to provide the user with information  
        # about the feature she is pasting.  It warns the user and returns False on error
        if not self.getAttsForPastedOrModifiedFeats(pastedFeatureIds, editLayer, tempOriginalEditFeats, "baselayer", True):
            return
        
        '''PASTING COMPLETED, SO DO SOME HOUSEKEEPING '''
        
        # reset the layer we were copying or modifying to be the active layer
        self.setPasteModifySuccess()         
        self.setBaseLayerActive(copyLayerName)
         
    def modifyEditLayerFeatures(self):
        ''' This edit method provides the ability to modify features on editing layers of all geometry types. '''
        # debugging
        print "Main.mainwindow.modifyEditLayerFeatures()" 
        
        # So we have some edit layer features copied and the user wants to modify them.
        # first get  a list of the copied feature ids so they can be selected
        copiedFeatIds = []
        for feat in self.copiedFeats: copiedFeatIds.append(feat.id())
        print "Main.mainwindow.modifyEditLayerFeatures(): copiedFeatIds are "
        print copiedFeatIds
        
        # next get the editLayer
        editLayer = self.getLayerFromName(self.editLayerName)
        
        # Now call this method, which gives the user info about the features they are modifying,
        # and also opens the Add Attributes dialog, which allows them to input the attribute changes.
        # Setting the self.originalEditLayerFeats parameter, which is the current state of editing layer features,
        # ensures that no features will be deleted if the user chooses "cancel" when modifying attributes.
        # This method warns the user and returns False on error            
        if not self.getAttsForPastedOrModifiedFeats(copiedFeatIds, editLayer, self.originalEditLayerFeats, "editlayer", False):
            return
        
        # now clean up and renumber the features
        self.setPasteModifySuccess(True)
        
    def checkEditFeatureMatch(self, editLayer, features):
        ''' 
            This edit method checks whether editing layer features that the user wishes to modify
            match the current scenario edit type.
        
        '''
        # debugging
        print "Main.mainwindow.checkEditFeatureMatch()"
        
        editLayerProvider = editLayer.dataProvider()
        for feat in features:
            attrs = feat.attributeMap()
            for key, value in attrs.iteritems():
                print "Main.mainwindow.checkEditFeatureMatch(): The key is " + str(key)
                print "Main.mainwindow.checkEditFeatureMatch(): The value is " + value.toString()
                if unicode(value.toString()) == "": continue
                else:
                    fieldMap = editLayerProvider.fields()
                    fieldName = unicode(fieldMap[key].name())
                    print "Main.mainwindow.checkEditFeatureMatch(): The fieldName is " +  fieldName
                    if not self.checkFieldNameMatch(fieldName):
                        QtGui.QMessageBox.warning(self, "Modify Edits Error", "At least one of the features that you selected \
was not created by using the current scenario edit type.  After choosing a particular scenario edit type, you can only \
modify edits created using that scenario edit type. Please use the 'Identify Features' tool to \
find what scenario edit type was used to create the features you wish to modify and then choose the matching \
scenario edit type to modify them.  Your modifications were not made. Please try again.")
                        return False
                    else: break
        else: return True             
        
    def checkFieldNameMatch(self, fieldName):
        ''' An edit method that checks whether the name of a field matches the current scenario edit type '''
        # debugging
        print "Main.mainwindow.checkFieldNameMatch()"
        
        editType = self.scenarioEditType
        if fieldName == 'cross_id' and editType == config.scenarioEditTypesList[0]: return True
        elif fieldName == 'dam_id' and editType == config.scenarioEditTypesList[1]: return True
        elif fieldName == 'wildlf_id' and editType == config.scenarioEditTypesList[2]: return True
        elif fieldName == 'restr_id' and editType == config.scenarioEditTypesList[3]: return True
        elif fieldName == 'newrd_id' and editType == config.scenarioEditTypesList[4]: return True
        elif fieldName == 'modrd_id' and editType == config.scenarioEditTypesList[5]: return True
        elif fieldName == 'ldcvr_id' and editType == config.scenarioEditTypesList[6]: return True
        else: return False
            
    def isAlteredFeature(self, editLayer, featId):
        ''' 
            This edit method checks whether editing layer features that the user wishes to modify
            match the current scenario edit type.
        
        '''
        # debugging
        print "Main.mainwindow.isAlteredFeature()"
        
        editLayerProvider = editLayer.dataProvider()
        allAttrs = editLayerProvider.attributeIndexes()
        feat = QgsFeature()
        if not editLayerProvider.featureAtId(featId, feat, False, allAttrs):
            QtGui.QMessageBox.warning(self, "Modify Edits Error", "This feature could not be found. Please deselect \
these features and try again.") 
        attrs = feat.attributeMap()
        subcount = None
        for key, value in attrs.iteritems():
            print "Main.mainwindow.isAlteredFeature(): key = " + str(key)
            print "Main.mainwindow.isAlteredFeature(): subcount = " + str(subcount)
            print "Main.mainwindow.isAlteredFeature(): The value is " + value.toString()
            if unicode(value.toString()) == "": continue
            elif subcount == None:                   
                subcount = key
                print "Main.mainwindow.isAlteredFeature(): subcount first set at " + str(subcount) 
                continue
            if key == subcount + 1 and unicode(value.toString()) == "y":
                return True
            else: return False
            
    def checkForDeletions(self, editLayer, features):
        ''' This edit method checks if a user is attempting to modify deletions on an editing layer '''
        # debugging
        print "Main.mainwindow.checkForDeletions()"
        
        for feat in features:
            attrs = feat.attributeMap()
            subcount = None
            for key, value in attrs.iteritems():
                print "Main.mainwindow.checkForDeletions(): key = " + str(key)
                print "Main.mainwindow.checkForDeletions(): The subcount is " + str(subcount)
                print "Main.mainwindow.checkForDeletions(): The value is " + value.toString()
                if unicode(value.toString()) == "": continue
                elif subcount == None:                   
                    subcount = key
                    print "Main.mainwindow.checkForDeletions(): subcount first set at " + str(subcount) 
                    continue
                if key == subcount + 2:
                    if unicode(value.toString()) == "y":
                        QtGui.QMessageBox.warning(self, "Modify Edits Error", "You cannont modify deleted features. \
If you wish to remove a deleted feature from an editing layer then select it and choose 'Delete Selected.'")
                        return False
                    else: break
        else: return True # if no features are deleted edit layer features
                                            
############################################################################################  
    ''' VIEW MENU SLOTS '''
############################################################################################   
    
    def zoomIn(self, state):
        ''' View menu SLOT '''
        print "Main.mainwindow.zoomIn() " + str(state)
        
        if state: 
            # Need this to handle if user tries to addVector while adding a line or polygon
            # check app state and handle user cancel
            if self.appStateChanged("zoomIn") == "Cancel":
                return
            self.canvas.setMapTool(self.toolZoomIn)
        else: self.canvas.unsetMapTool(self.toolZoomIn)    

    def zoomOut(self, state):
        ''' View menu SLOT '''
        # debugging
        print "Main.mainwindow.zoomOut() "  + str(state)
        
        if state:
            # Need this to handle if user tries to addVector while adding a line or polygon
            # check app state and handle user cancel
            if self.appStateChanged("zoomOut") == "Cancel":
                return
            self.canvas.setMapTool(self.toolZoomOut)
        else: self.canvas.unsetMapTool(self.toolZoomOut)
                    
    def pan(self, state):
        ''' View menu SLOT '''
        # debugging
        print "Main.mainwindow.pan " + str(state)
        
        if state:
            # Need this to handle if user tries to addVector while adding a line or polygon
            # check app state and handle user cancel
            if self.appStateChanged("pan") == "Cancel":
                return
            self.canvas.setMapTool(self.toolPan)
        else: self.canvas.unsetMapTool(self.toolPan)
 
    def zoomToMapExtent(self):
        ''' View menu SLOT to set zoom to full extent of visible layers '''
        # debugging
        print "Main.mainwindow.zoomToMapExtent()"
        
        # Need this to handle if user tries to addVector while adding a line or polygon
        # check app state and handle user cancel
        if self.appStateChanged("zoomToMapExtent") == "Cancel":
            return
        
        extent = self.canvas.fullExtent()
        # without this some of the layer is off the canvas
        extent.scale(1.05)
        self.canvas.setExtent(extent)
        self.canvas.refresh()
        
    def identifyFeatures(self, state):
        ''' View menu SLOT to handle the identify features tool'''
        # debugging
        print "Main.mainwindow.identifyFeatures()"
        
        if state: # for action selected state = True
            print "Main.mainwindow.identifyFeatures() state is True"
            # Need this to handle if user tries to addVector while adding a line or polygon
            # check app state and handle user cancel
            if self.appStateChanged("identifyFeatures") == "Cancel":
                return
            # identifyFeatures action is selected so enable this tool
            self.canvas.setMapTool(self.toolIdentify)
        else: # action deselected (state = False)
            print "Main.mainwindow.identifyFeatures() state is false"
            self.canvas.unsetMapTool(self.toolIdentify)
       
############################################################################################  
    ''' LAYER MENU CUSTOM SLOTS '''
############################################################################################
               
    def addVectorLayer(self):
        ''' Layer menu SLOT to handle adding vector layers to the map canvas '''
        # debugging
        print "Main.mainwindow.addVectorLayer()"
        
        # Need this to handle if user tries to addVector while adding a line or polygon
        # check app state and handle user cancel
        if self.appStateChanged("addVector") == "Cancel":
            return
        
        # open the file dialog
        qd = QtGui.QFileDialog()
        filterString = "ESRI Shapefile(*.shp *.SHP)\nComma Separated Value\
(*.csv *.CSV)\nGeography Markup Language(*.gml *.GML)\nGPX(*.gpx *.GPX)\nKML(*.kml *.KML)\
SQLite(*.sqlite *.SQLITE)\nArc\\Info ASCII Coverage(*.e00 *.E00)\nAll Files(*)"
        # get the path to the directory containing the opened file using Python
        directory = config.baseLayersPath
                                
        # change the QString to unicode so that Python can slice it for the directory name 
        vfilePath = unicode(qd.getOpenFileName(self, "Add Vector Layer",
                                            directory, filterString))
        # Check for cancel
        if len(vfilePath) == 0: return

        self.openVectorLayer(vfilePath)
            
    def addRasterLayer(self):
        ''' Layer menu SLOT to handle adding raster layers to the map canvas '''
        # debugging
        print "Main.mainwindow.addRasterLayer()"
        
        # Need this to handle if the user tries to addRaster while making line or polygon edits
        # check app state and handle user cancel
        if self.appStateChanged("addRaster") == "Cancel": return
        
        # open file dialog
        qd = QtGui.QFileDialog()
        filterString = "All Files(*)\nMrSID(*.sid *.SID)\nGeoTIFF\
(*.tif *.tiff *.TIF *.TIFF)\nArc/Info Binary Grid(*.adf *.ADF)\n\
JPEG(*.jpg *.jpeg *.JPG *.JPEG)"
        # get the path to the directory containing the opened file using Python
        directory = config.baseLayersPath        
        
        # change QString to unicode so Python can slice it for the directory name
        rfilePath = unicode(qd.getOpenFileName(self, "Add Raster Layer",
                                    directory, filterString))
        # Check for cancel
        if len(rfilePath) == 0: return

        #create the layer
        self.openRasterLayer(rfilePath)
          
    def openRasterCategoryTable(self):
        ''' Layer menu SLOT to handle opening the raster category table '''
        # debugging
        print "Main.mainwindow.openRasterCategoryTable()"
        
        # Need this to handle if user tries to addVector while adding a line or polygon
        # check app state and handle user cancel
        if self.appStateChanged("openRasterCategoryTable") == "Cancel":
            return
        
        # Raster Categories file kept in the Base_layers folder
        fname = "./RasterCategoryTable.htm"
        
        # use a QDockWidget to create floating window 
        # with the MainWindow as parent 
        self.dwRasterTable = QtGui.QDockWidget("Raster Category Tables", self)
        self.dwRasterTable.setFloating(True)
        # The line below prevents the dock widget from distorting the window when dragged.
        self.dwRasterTable.setAllowedAreas(QtCore.Qt.NoDockWidgetArea)
        self.dwRasterTable.setMinimumSize(QtCore.QSize(800, 600))
        # Show the QDockWidget and make it a separate floating window
        self.dwRasterTable.show()
        
        # create a QTextBrowser to display the file
        # *Note: using QTextBrowser alone
        # results in an orphaned window that the app does not close
        self.browserRaster = QtGui.QTextBrowser()
        
        # Open the file and create a text stream to read
        fh = QtCore.QFile(fname)
        if not fh.open(QtCore.QIODevice.ReadOnly): raise IOError, unicode(fh.errorString())
        stream = QtCore.QTextStream(fh)
    
        # add the QTextBrowser to the QDockWidget
        self.dwRasterTable.setWidget(self.browserRaster)
        
        # display the html file in the browser
        self.browserRaster.setHtml(stream.readAll())
        self.browserRaster.setFontPointSize(20.0)
        #self.browser.setSizePolicy()
        
    def openVectorAttributeTable(self):
        ''' Layer menu SLOT to handle opening the vector attribute table '''
        # debugging
        print "Main.mainwindow.openVectorAttributeTable()"
        
        # Need this to handle if user tries to addVector while adding a line or polygon
        # check app state and handle user cancel
        if self.appStateChanged("openVectorAttributeTable") == "Cancel":
            return
        
        if not self.activeVLayer:
            return

        if unicode(self.activeVLayer.name()) == config.slowLoadingLayers[0]:
            reply = QtGui.QMessageBox.question(self, "Vector Attribute Table", "This layer's \
attribute table is very large and can take a few seconds to load.  Do you want to continue?", 
                                                    QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.Cancel: return

        names = []
        feat = QgsFeature()

        # get the field names 
        fields = self.provider.fields()
        for value in fields.itervalues():
            names.append( unicode(value.name()) )
      
        # configure the table to the activeVLayer
        self.attrTable = QtGui.QTableWidget()
        self.attrTable.clear()
        self.attrTable.setRowCount(self.activeVLayer.featureCount())
        self.attrTable.setColumnCount(self.provider.fieldCount())
        self.attrTable.setHorizontalHeaderLabels((names))
        self.attrTable.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.attrTable.setSelectionBehavior(QtGui.QTableWidget.SelectRows)
        self.attrTable.setSelectionMode(QtGui.QTableWidget.SingleSelection)

        # get all the geographic and attribute data
        allAttrs = self.provider.attributeIndexes()
        # the select() method initializes retrieval of data
        self.provider.select(allAttrs)
        # populate the table with attribute data
        # the nextFeature() method operates on a "provider.select()" initialized provider
        setItem = self.attrTable.setItem
        item = QtGui.QTableWidgetItem
        while self.provider.nextFeature(feat): 
            # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
            featId = feat.id()
            attrMap = feat.attributeMap()
            for k, attr in attrMap.iteritems():
                setItem(featId, k, item(attr.toString())) # feat.id() = row, key = the column number  
      
        self.attrTable.resizeColumnsToContents()
        self.attrTable.setMinimumSize(QtCore.QSize(400,250))
        #self.attrTable.adjustSize()
      
        # Show the QDockWidget and make it a separate floating window
        # (Need a dock widget to handle separate window properly)
        # if it is already open don't open another window
        if self.dwAttrTable == None:  
            # debugging
            print "Main.mainwindow.openVectorAttributeTable(): dwAttrTable not open"
            self.dwAttrTable = QtGui.QDockWidget("Vector Attribute Table", self)
            self.dwAttrTable.setFloating(True)
            self.dwAttrTable.setAllowedAreas(QtCore.Qt.NoDockWidgetArea)
            self.dwAttrTable.setMinimumSize(QtCore.QSize(400,250))
            self.dwAttrTable.show()
            
            # add the attribute table to the dock widget
        elif self.dwAttrTable.isHidden():
            self.dwAttrTable.setMinimumSize(QtCore.QSize(400,250))
            self.dwAttrTable.show()
            
        self.dwAttrTable.setWidget(self.attrTable)
        self.dwAttrTable.setMinimumSize(QtCore.QSize(400,250))
        self.dwAttrTable.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        #self.dwAttrTable.adjustSize()
        self.dwAttrTable.show()
     
############################################################################################  
    ''' QT AND PYTHON SHORT CIRCUIT SIGNAL SLOTS TO HANDLE APP STATE CHANGES '''
############################################################################################    
    
    # this Pythono short-circuit signal found in legend.currentItemChanged()
    def activeLayerChanged(self, layerType):
        ''' 
            A controller for handling app state changes originating from the legend.
            This method is called whenever the "current item" in the legend has changed.
        '''

        #**************************************************************************     
        ''' Debugging Code '''
        print "MAIN.MAINWINDOW.ALC() STARTING"
        print "alc layer type is " + str(layerType)
        if not self.activeVLayer: print "alc no active vlayer"
        else: print "alc old active vlayer " + self.activeVLayer.name()
        if self.activeRLayer == None: print "alc no active rlayer"
        else: print "alc old active rlayer " + self.activeRLayer.name()
        print "alc self.editMode is " + str(self.editMode)
        print "alc self.editDirty is " + str(self.editDirty)
        print "alc self.scenarioDirty is " + str(self.scenarioDirty)
        print "alc Crs Transform is enabled? " + str(self.canvas.hasCrsTransformEnabled())
        print "alc The destination crs description is " + str(self.canvas.mapRenderer().destinationCrs().description())
        print "alc The destination authority identifier is " + str(self.canvas.mapRenderer().destinationCrs().authid())
        print "alc self.openingOrientingLayers is " + str(self.openingOrientingLayers)
        
        #**************************************************************************        
        
        # keep track of the active layer type for use in other methods
        # LayerType can be none if all layers are removed from the legend.
        self.layerType = layerType # 0 = vector; 1 = raster
 
        # Set active layer variables to none because we will either configure
        # a new active layer, or there are no layers open in the legend.
        self.activeVLayer = None
        self.activeRLayer = None
        
        ''' Set app state for the new active layer '''
        # layerType is the QgsMapLayer type        
        if layerType == 1: # raster 
            # set active raster layer
            self.activeRLayer = self.legend.activeLayer().layer()
            
            # debugging
            print "alc The layer's authority id is " + str(self.activeRLayer.crs().authid())
            print "alc The description of the layer crs is " + str(self.activeRLayer.crs().description())
            print "ALC THE ACTIVE RLAYER NAME IS " + self.activeRLayer.name()
            
            # For some reason, the USGS.sid will not render unless we include this line of code.
            # The USGS.sid layer reports that it is in geographic coordinates WGS 84.
            self.activeRLayer.setCrs(self.crs)
            # set extents
            self.setExtents()
            # set the layer geometry
            self.geom = None
            self.provider = None
            
            ''' 
                A new raster layer has been selected or opened so set action states. 
            ''' 
            
            # Since we are loading a layer, enable the navigation map tools 
            self.mapToolGroup.setDisabled(False)
            # Disable (gray out) select tool actions if raster layer loaded.
            # Note that this tool is disabled in mainwindow.init() but enabled
            # whenever a vector layer is loaded while editing a scenario.
            self.mpActionSelectFeatures.setDisabled(True)
            # This disables 4 usuallyDisabledToolGroup actions that may have been enabled
            # when a vector layer was active while editing a scenario.
            self.disableSelectActions()
            # can't paste features to a raster so disable paste action
            self.mpActionPasteFeatures.setDisabled(True)
            # disable edit actions since we can't edit a raster 
            self.disableEditActions()
            # if self.editsDirty enable save edits
            if self.editDirty: self.mpActionSaveEdits.setDisabled(False)
            # Disable the vector attribute table action, which may have been
            # enabled by loading a vector layer.
            self.mpActionOpenVectorAttributeTable.setDisabled(True)
            
            # New layer loaded so check about seting the scenarioDirty flag.  
            # Note: This gets called unnecessarily when a different layer is selected in the layer panel.
            # However, it returns immediately if the layer count has not changed.
            # It also returns immediately if a scenario is in the process of loading
            # or if the orienting layers are loading.
            # There is no need to check if the scenario is already dirty.  Once a scenario
            # is dirty, the policy is it stays dirty until the user saves it.
            if not self.scenarioDirty: self.setScenarioDirty()
          
            # There could be something to export if a scenario is open so enable Export Scenario
            # A user could open a scenario that has edits to editing layers and export it.
            if self.scenarioFilePath:
                self.mpActionExportScenario.setDisabled(False)

            # debugging
            print "alc self.scenarioDirty end is " + str(self.scenarioDirty)
            print "alc originalScenarioLayers are "
            for layer in self.originalScenarioLayers: print layer.name()
            print "alc currentLayers are "
            for layer in self.getCurrentLayers().values(): print layer.name()
      
        elif layerType == 0: #vector
            # debugging
            print "alc Setting app state for vector layer" 
            print "alc copyFlag is " + str(self.copyFlag)
            
            # set the active vector layer
            self.activeVLayer = self.legend.activeLayer().layer()
            # set the data provider
            self.provider = self.activeVLayer.dataProvider()
            # set the geometry of the layer
            self.geom = self.activeVLayer.geometryType() #0 point, 1 line, 2 polygon
            # set extents if not within MA state extents
            self.setExtents()
                      
            # New layer loaded so set the scenarioDirty flag.  Note: This gets called
            # unnecessarily when a different layer is selected in the layer panel.
            # However, it returns immediately if the layer count has not changed. 
            # There is no need to check if the scenario is already dirty.  Once a scenario
            # is dirty, the policy is it stays dirty until the user saves it.
            if not self.scenarioDirty: self.setScenarioDirty()
            
            # debugging 
            print "ALC THE ACTIVE VLAYER NAME IS " + self.activeVLayer.name()
            print "alc The layers authid is " + str(self.activeVLayer.crs().authid())
            print "alc The description of the srs is " + str(self.activeVLayer.crs().description())

            # This method sets colors, marker types and other properties for certain vector layers
            print "alc The activeVLayer renderer type is " + self.activeVLayer.rendererV2().type()
            self.setRendererV2()
            
            # refresh attribute table if open
            if self.attrTable != None and self.attrTable.isVisible():
                self.openVectorAttributeTable() 

            '''
            A New Vector layer has been selected or opened, so set action states.
            '''
            
            # Enable map navigation tools
            self.mapToolGroup.setDisabled(False) # map tools can't be enabled if the group is off
            
            # We are changing the activeVLayer, so we need to handle editMode
            if self.editMode: # handle select actions first
                self.mpActionSelectFeatures.setDisabled(False) # select always enabled in edit mode
                if self.mpActionSelectFeatures.isChecked():
                    # The user has checked Select Features, so leave select features activated.
                    # Also activate the select sub actions.
                    # Note that "Modify Selected" will only be enabled if the active layer
                    # is one of the point base layers
                    self.enableSelectSubActions() # enable deselect, modify, delete and copy features
                elif len(self.activeVLayer.selectedFeatures()) != 0:
                    # We have selected features, so enable all the selected features actions
                    # Note that "Modify Selected" will only be enabled if the active layer
                    # is an editable point base layer or an editing layer.
                    self.mpActionSelectFeatures.setChecked(True)
                    self.enableSelectSubActions()
            else:
                # Select tool only enabled if in editMode
                self.mpActionSelectFeatures.setDisabled(True)
                self.disableSelectActions()
            
            # This could be combined with the above, but for clarity, keep separate.
            if self.editMode: # now handle enabling add points, lines or polygons
                # loading a new active layer so enable the proper edit action if an editing layer
                if unicode(self.activeVLayer.name()) in config.editLayersBaseNames: # so is an editing layer
                    # But is the editing layer the correct layer for the scenario edit type?
                    currentLayerName = unicode(self.activeVLayer.name())
                    if shared.checkSelectedLayer(self, self.scenarioEditType, currentLayerName, False):
                        # So the editing tool will ONLY be enabled if the editing layer is the correct
                        # layer for the current scenario edit type.
                        self.enablePointsOrLinesOrPolygons()
                    else: # so is an editing layer but not the right one for the scenario edit type  
                        self.disableEditActions() # disable add points, lines, polygons
                else: # we are in edit mode and a non-editing vector layer has been selected
                    self.disableEditActions()
                     
            else: # not in edit mode
                # to be safe, but this should have already been called by the editScenario action
                self.disableEditActions() 
                      
            # handle the paste action
            if self.copyFlag and self.editMode:
                self.mpActionPasteFeatures.setDisabled(False)
            else: self.mpActionPasteFeatures.setDisabled(True)
           
            # if self.editDirty is False, the save edits action should be disabled
            if self.editDirty:
                self.mpActionSaveEdits.setDisabled(False)
            else: 
                self.mpActionSaveEdits.setDisabled(True)
        
            # enable the  "Open Vector Attribute Table" action    
            self.mpActionOpenVectorAttributeTable.setDisabled(False)
    
            # There could be something to export if a scenario is open so enable Export Scenario
            # A user could open a scenario that has edits to editing layers and export it.
            if  self.scenarioFilePath:
                self.mpActionExportScenario.setDisabled(False)
                
            # debugging
            print "alc self.scenarioDirty end is " + str(self.scenarioDirty)
            print "alc originalScenarioLayers are "
            for layer in self.originalScenarioLayers: print layer.name()
            print "alc currentLayers are "
            for layer in self.getCurrentLayers().values(): print layer.name()
                       
        # debugging
        else: print "alc Geometry type unknown"
        
    def closeEvent(self, event):
        ''' Slot to handle signal emitted when user exits app '''

        if self.appStateChanged("appClosing") == "Cancel": event.ignore()

############################################################################################   
    ''' METHODS TO MANAGE APPLICATION STATE CHANGES '''
############################################################################################
    
    def appStateChanged(self, callingAction):
        ''' 
            Manage the application state changes from user actions. 
            
            Actions that call this method are: newScenario, openScenario, saveScenario, saveScenarioAs, 
            exportScenario, appClosing, selectFeatures, stoppingEditing, zoomIn, zoomOut, pan,
            zoomToMapExtent, identifyFeatures, addVector, addRaster, openVectorAttributeTable, 
            openRasterCategoryTable, legendMousePress.
        '''
        
        # If no layer is loaded then user is loading first layer after app start (num layers = 0),
        # or loading first layer after deleting the only layer in the legend (num layers = 0).
        # If there are no layers in the scenario, no need to save the scenario or edits.
        if len(self.legend.getLayerIDs()) == 0:  return

        # If user in the middle of a line or polygon edit, warn when they choose another action.
        if self.toolAddLinesPolygons and self.toolAddLinesPolygons.started:
            QtGui.QMessageBox.warning(self, "Editing Error", "Please complete your edit \
before taking another action!")
            # reset the correct action
            if self.toolAddLinesPolygons.geom:
                self.mpActionAddPolygons.setChecked(True)
            else: 
                self.mpActionAddLines.setChecked(True)
            return "Cancel" 
        
        #**********************************************************       
        ''' Debugging code '''
        print "MAIN.MAINWINDOW.APP_STATE_CHANGED() STARTING: callingAction is " + callingAction
        if self.activeVLayer == None: print "asc no active vlayer" 
        else: print "asc current active " + self.activeVLayer.name()
        if self.activeRLayer == None: print "asc no active rlayer"
        else: print "asc current active rlayer " + self.activeRLayer.name()
        print "asc num layers " + str(len(self.legend.getLayerIDs()))
        print "asc registry count " + str(QgsMapLayerRegistry.instance().count())
        print "asc the layer type is " + str(self.layerType)
        print "asc self.editDirty is " + str(self.editDirty)
        print "asc self.editMode is " + str(self.editMode)
        print "asc self.scenarioDirty is " + str(self.scenarioDirty)
        print "asc scenarioFilePath " + str(self.scenarioFilePath) 
        #******************************************************************
 
        ''' 
        On any other user action, check for unsaved edits and unsaved scenarios.
       
        '''

        # We should check for unsaved edits when stopping editing,
        # on all scenario menu actions, or on closing the app.  
        callingList = ["newScenario", "openScenario", "saveScenario", "saveScenarioAs", "exportScenario",
                       "appClosing", "modifyingEdits", "stoppingEditing"] # "startingEditing",,  
        if self.editDirty:
            if callingAction in callingList:
                if self.checkEditsState(callingAction) == "Cancel": return "Cancel"

        # We only want to check for a dirty scenario when:
        # creating a new scenario, opening a scenario, 
        # exporting a scenario, or closing the app.
        callingList = ["newScenario", "openScenario", "exportScenario", "appClosing"]
        if self.scenarioDirty:
            if callingAction in callingList:
                if self.checkScenarioState(callingAction) == "Cancel": return "Cancel"

        # debugging
        print "Main.mainwindow.appStateChanged() has returned nothing"

    def checkEditsState(self, callingAction):
        ''' Prompt the user about unsaved edits '''
        # debugging
        print "Main.mainwindow.checkEditsState()"
        
        # Prompt the user about clearing selections/edits
        # and deactivate the action if necessary.
        title = "Save Edits"
        text = "Do you want to save your edits to " + self.editLayerName + "?"
        # Once in edit mode, it is impossible to exit edit mode, or do anything else, without
        # either saving or discarding changes. So, this dialog is only called when in edit mode.
        callingList = ["saveScenario", "saveScenarioAs", "exportScenario"]
        reply = QtGui.QMessageBox.question(self, title, text, 
                QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Save|QtGui.QMessageBox.Discard )
        if reply == QtGui.QMessageBox.Save: # so save edits
            # debugging
            print "Main.mainwindow.checkEditsState(): msgBoxSaveDiscardCancel = Save"
            # There is no need to handle editing state or app state here.  
            # App state should be handled by the calling action on return and at the 
            # last possible moment before the action takes effect. 
            self.saveEdits()
        elif reply == QtGui.QMessageBox.Discard: # so handle as above but discard edits
            # debugging
            print "Main.mainwindow.checkEditsState(): msgBoxYesDiscardCancel = Discard"
            # Under these situations just discard edits and leave editing state as is
            # but update the attribute table if open.
            if callingAction in callingList:
                shared.deleteEdits(self, self.editLayerName, self.originalEditLayerFeats)
                if self.attrTable != None and self.attrTable.isVisible():
                    self.openVectorAttributeTable()
            elif callingAction == "modifyingEdits":
                # Warn the user that they must save edits to modify them and return "cancel."
                QtGui.QMessageBox.information(self, "Modify Features Information", "You must save all edits before \
you can modify any of them. Please click OK and try again if you still wish to modify edits.")
                return "Cancel"
            # If opening new scenario, opening a saved scenario, closing the app or stopping editing.
            # discard the edits. The calling method will handle editing state or app state on return.
            else:
                shared.deleteEdits(self, self.editLayerName, self.originalEditLayerFeats)
        elif reply == QtGui.QMessageBox.Cancel:
            if callingAction == "stoppingEditing" and self.editMode:
                    self.mpActionEditScenario.blockSignals(True)
                    self.mpActionEditScenario.setChecked(True)
                    self.mpActionEditScenario.blockSignals(False) 
            print "Main.mainwindow.checkEditsState(): returning 'cancel'"
            return "Cancel"
        
    def checkScenarioState(self, callingAction):
        ''' Prompt the user about unsaved scenario changes '''
        # debugging
        print "Main.mainwindow.checkScenarioState()"
        
        # Prompt the user about a dirty scenario.
        title = "Save Scenario"
        text = "Do you want to save the current scenario?"

        reply = QtGui.QMessageBox.question(self, title, text, 
                QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Save|QtGui.QMessageBox.Discard )
        if reply == QtGui.QMessageBox.Save: # user chose to save scenario
            # debugging
            print "Main.mainwindow.checkScenarioState(): msgBoxSaveDiscardCancel = Save"
            if self.scenarioFilePath: self.saveScenario()
            elif self.saveScenarioAs() == "Cancel": return "Cancel"
        elif reply == QtGui.QMessageBox.Discard:
            # debugging
            print "Main.mainwindow.checkScenarioState(): msgBoxYesDiscardCancel = Discard"
            if callingAction == "exportScenario":
                QtGui.QMessageBox.information(self, "Export Scenario Information", "You must save the scenario before \
you can export it. Please click OK and try again if you still wish to export the scenario.")
                return "Cancel"
            
            # If the user wants to close a scenario without saving it, we need to check
            # for editing layers that were not part of the last save for this scenario   
            # and delete them. If an editing layer is open but has not been saved with the scenario, 
            # and the user doesn't choose to save the scenario, then that editing layer will not appear
            # if the scenario is reopened. However, it would remain in the scenario's folder
            # where it will be read and included in an export.  This would certainly  lead to 
            # erroneous scenario exports!!
            # Self.currentLayersNames() returns a list of names of open layers.
            # We check this for differences with the names of layers included when the the scenario.
            # was last saved.
            differences = [name for name in self.getCurrentLayersNames() if name not in 
                                                            self.originalScenarioLayersNames]                                                    
            # debugging
            print "Main.mainwindow.checkScenarioState(): These are the originalScenarioLayersNames"
            for name in self.originalScenarioLayersNames: print name
            print "Main.mainwindow.checkScenarioState(): These are the CurrentLayersNames()"
            for name in self.getCurrentLayersNames(): print name
            print "Main.mainwindow.checkScenarioState(): These are the differences:"
            for name in differences: print name
            
            for name in differences:
                if name in config.editLayersBaseNames:
                    # get the layer object from the name
                    layer = self.getLayerFromName(name)
                    editFilePath = layer.source()
                    print "Main.mainwindow.checkScenarioState() path to remove is: " + editFilePath
                    layerId = layer.id()
                    # need to remove layer from registry before delete.
                    self.legend.removeEditLayerFromRegistry(layer, layerId)
                    if not self.legend.deleteEditingLayer(editFilePath):
                        # Warn and return
                        QtGui.QMessageBox.warning(self, "Deletion Error:", "Caps Scenario Builder \
could not delete an editing layer that you have chosen not to save with your scenario.  This \
editing layer will not appear when you reopen this scenario, but it could be mistakenly included if you \
choose 'Export Scenario' for this scenario in the future.")
                        return "Cancel"
        elif reply == QtGui.QMessageBox.Cancel:
            print "Main.mainwindow.checkScenarioState() returning 'cancel'"
            return "Cancel"
 
    def setInitialAppState(self, newScenario=True):
        ''' Set the app state to be its first opened state '''
        # debugging
        print "Main.mainwindow.setInitialAppState()"
        
        if self.dwAttrTable: self.dwAttrTable.close()
        if self.dwRasterTable: self.dwRasterTable.close()
        if self.toolAddLinesPolygons: self.canvas.unsetMapTool(self.toolAddLinesPolygons)
        if self.toolAddPoints: self.canvas.unsetMapTool(self.toolAddPoints)
        if self.toolIdentify: self.canvas.unsetMapTool(self.toolIdentify)
        if self.toolSelect: self.canvas.unsetMapTool(self.toolSelect)
        self.activeRLayer = None
        self.activeVLayer = None
        self.attrTable = None
        self.copiedFeats = []
        self.copyFlag = False
        self.currentLayers = []
        self.currentLayersCount = None
        self.dlgDisplayIdentify = None
        self.dlgScenarioEditTypes = None
        self.dwAttrTable = None
        self.dwRasterTable = None
        self.editDirty = False
        self.editingPolygon = False
        self.editLayerName = None
        self.editMode = False 
        self.statusBar.removeWidget(self.editTypeLabel)
        self.editTypeLabel = None
        self.geom = None
        self.layerColor = None
        self.layerType = None
        self.mapToolGroup.setDisabled(True)
        self.mpActionIdentifyFeatures.setChecked(False)
        self.mpActionEditScenario.setChecked(False)
        self.mpActionEditScenario.setDisabled(False)
        self.mpActionExportScenario.setDisabled(True)
        self.mpActionOpenVectorAttributeTable.setDisabled(True)
        self.mpActionSaveEdits.setDisabled(True)
        self.openingOrientingLayers = False
        self.openingScenario = False
        self.originalEditLayerFeats = []
        self.originalScenarioLayers = []
        self.originalScenarioLayersNames = []
        self.origScenarioLyrsLoaded = False
        self.provider = None
        self.scenarioDirty = False
        self.scenarioEditType = None
        self.scenarioFileName = None
        self.scenarioFilePath = None
        self.scenarioInfo = None
        self.setWindowTitle("Conservation Assessment and Prioritization System (CAPS) Scenario Builder")
        self.statusBar.removeWidget(self.editTypeLabel)
        self.windModifyInfo = None
        # This must be last so app sets variables when layers opened
        if newScenario:
            self.openOrientingLayers()

############################################################################################
    ''' UTILITY METHODS '''
############################################################################################
        
    def getCurrentLayersCount(self):
        # debugging
        print "Main.mainwindow.getCurrentLayersCount()"
        
        self.currentLayersCount = None
        self.currentLayersCount = QgsMapLayerRegistry.instance().count()
        return self.currentLayersCount
 
    def getGeometryName(self, layerGeom):
        # debugging
        print "Main.mainwindow.getGeometryName()"
        geometry = "No Geometry"
        if layerGeom != None: # None if raster loaded
            if layerGeom == 0: geometry = "point(s)"
            elif layerGeom == 1: geometry = "line(s)"
            elif layerGeom == 2: geometry = "polygon(s)"
            else: geometry = "Unknown Geometry"
            return geometry
    
    def getCurrentLayers(self):
        ''' Get the layers currently registered in the QgsMapLayerRegistry '''
        # debugging
        print "Main.mainwindow.getCurrentLayers()"
        
        self.currentLayers = {}
        # note: returns a dictionary of QgsMapLayers
        self.currentLayers = QgsMapLayerRegistry.instance().mapLayers()
        return self.currentLayers
        
    def getCurrentLayersNames(self):
        # debugging
        print "Main.mainwindow.getCurrentLayersNames()"
        
        currentLayersNames = []
        for layer in self.getCurrentLayers().values():
            currentLayersNames.append(layer.name())
  
        return currentLayersNames
        
    def getLayerFromName(self, layerName):
        # debugging
        print "Main.mainwindow.getLayerFromName()"
        
        for layer in self.getCurrentLayers().values():
            if layerName == layer.name(): return layer
        else:
            QtGui.QMessageBox.warning(self, "Get Layer Error:", "The layer "
                                                    + layerName + " is not open in the layer list panel.")
            return False
   
    def getEditFields(self, geom):
        # debugging
        print "Main.mainwindow.getEditFields()"
        
        # 0 point, 1 line, 2 polygon
        if geom == 0: editFields = config.editPointsFields  
        elif geom == 1: editFields = config.editLinesFields
        elif geom == 2: editFields = config.editPolygonsFields   
                
        return editFields
    
    def openVectorLayer(self, vfilePath):
        ''' Open a vector layer '''
        # debugging
        print "Main.mainwindow.openVectorLayer()"
        print "Main.mainwindow.openVectorLayer(): vfilePath is " + vfilePath
        
        # create the file info object to get info about the vfile
        info = QtCore.QFileInfo(vfilePath)
        #create the layer
        #QFileInfo.completeBaseName() returns just the filename without the extension
        try:
            vlayer = QgsVectorLayer(vfilePath, info.completeBaseName(), "ogr")       
        except (IOError, OSError), e:
            error = unicode(e)
            print error
        
        # This double checks for loading errors and pops up a message box if the layer doesn't open
        if not self.checkLayerLoadError(vlayer): return False
        
        # add layer to layer registry and set extent if necessary   
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        self.activeVLayer = vlayer
        return True
    
    def openHiddenVectorLayer(self, vfilePath):
        # debugging
        print "Main.mainwindow.openHiddenVectorLayer()"
        
        # create the file info object to get info about the vfile
        info = QtCore.QFileInfo(vfilePath)
        #create the layer
        #QFileInfo.completeBaseName() returns just the filename
        try:
            vlayer = QgsVectorLayer(vfilePath, info.completeBaseName(), "ogr")
        except (IOError, OSError), e:
            error = unicode(e)
            print error                
        # double check for error using qgis methods
        if not self.checkLayerLoadError(vlayer): return False
 
    def openRasterLayer(self, rfilePath):
        ''' Open a raster layer '''
        info = QtCore.QFileInfo(rfilePath)
        
        try:
            rlayer = QgsRasterLayer(info.filePath(), info.completeBaseName())
        except (IOError, OSError), e:
            error = unicode(e)
            print error
        # double check for error using qgis methods    
        if not self.checkLayerLoadError(rlayer): return False
        
        # add layer to layer registry and set extent
        reg = QgsMapLayerRegistry.instance()
        reg.addMapLayer(rlayer)

    def openOrientingLayers(self):
        ''' Open orienting layers when the app is started '''
        path = config.baseLayersPath
        
        # debugging
        info = QtCore.QFileInfo(path)
        path2 = info.absolutePath()
        path3 = info.absoluteFilePath()
        path4 = info.canonicalFilePath()
        print "Main.mainwindow.openOrientingLayers(): The config path is " + path
        print "Main.mainwindow.openOrientingLayers(): The absolutePath of config is " + path2
        print "Main.mainwindow.openOrientingLayers(): The absoluteFilePath of config is " + path3
        print "Main.mainwindow.openOrientingLayers(): The canonicalFilePath of config is " + path4
        
        vlayers = config.orientingVectorLayers
        rlayers = config.orientingRasterLayers
        # layers opened first will be on the bottom of the layer list panel
        for rlayer in rlayers:
            tempPath = None
            tempPath = path + rlayer
            # QGIS 1.73 was not interpreting ./ correctly.  When the tempPath = ./base_layers/someraster.tif
            # QGIS writes ./base_layers/someraster.tif to the scenario file (i.e. the '.cap' file).  When QGIS opens the
            # project file, it interprets ./ to be the "Scenarios" directory where the .cap file is located rather than the
            # program directory where the base_files are located. This is corrected when the raster files are opened using
            # absolute file path.  In that case, QGIS writes '../' to the scenario file and layers open properly.  The two
            # lies below convert the relative paths to absolute paths so that config.baseLayersPath can remain "./base_layers/"
            # If there are problems with the Windows installer, I could convert all paths to absolute paths to solve the problem. 
            print "Main.mainwindow.openOrientingLayers(): The tempPath is " + tempPath
            #print "The absolute file path is " + info.absoluteFilePath()
            self.openingOrientingLayers = True
            self.openRasterLayer(tempPath)
 
        for vlayer in vlayers:
            tempPath = None
            tempPath = path + vlayer
            print "Main.mainwindow.openOrientingLayers(): The tempPath is " + tempPath
            self.openingOrientingLayers = True
            self.openVectorLayer(tempPath)
        
        # all orienting layers opened so set flag
        self.openingOrientingLayers = False

    def arrangeOrientingLayers(self):
        ''' The QgsProject instance does not set layer position in our layer panel,
            so we set it here, but only for orienting layers.
        '''
        # debugging
        print "Main.mainwindow.arrangeOrientingLayers()"

        legend = self.legend
        legendLayers = legend.getLayerIDs()
        numLegendLayers = len(legendLayers)
        oRLayers = config.orientingRasterLayers
        oVLayers = config.orientingVectorLayers
 
        # debugging
        # Note that the index of the legend layers starts with zero.
        # For a legend having 10 layers the indexes run from 0 to 9.
        # If you try to insert a layer  into the QTreeWidget at an index
        # that doesn't exist, the layer will not be inserted and will not appear.
        print "Main.mainwindow.arrangeOrientingLayers(): numLegendLayers is " + str(numLegendLayers)
 
        # First load the raster layers
        for orientingLayer in oRLayers:
            info = QtCore.QFileInfo(orientingLayer)
            orientingLayerName = info.completeBaseName()
            print "Main.mainwindow.arrangeOrientingLayers(): orientingLayerName is " + orientingLayerName
            item = legend.findItems(orientingLayerName, QtCore.Qt.MatchFixedString, 0) 
            print "Main.mainwindow.arrangeOrientingLayers(): length of item list is " + str(len(item))
            if len(item) != 0:
                itemToMove = item[0]
                print "Main.mainwindow.arrangeOrientingLayers(): is this a legendLayer? " + str(legend.isLegendLayer(itemToMove))
                print "Main.mainwindow.arrangeOrientingLayers(): item to move is " + itemToMove.text(0)
                position = numLegendLayers - (oRLayers.index(orientingLayer) + 1) # itemToMove is the base layer
                print "Main.mainwindow.arrangeOrientingLayers(): r position is " + str(position)
                itemToMove.storeAppearanceSettings() # Store settings 
                legend.takeTopLevelItem(legend.indexOfTopLevelItem(itemToMove))
                legend.insertTopLevelItem(position, itemToMove)
                legend.insertTopLevelItem(1, itemToMove)
                itemToMove.restoreAppearanceSettings()

        # then load the vector layers
        for orientingLayer in oVLayers:
            info = QtCore.QFileInfo(orientingLayer)
            orientingLayerName = info.completeBaseName()
            print "Main.mainwindow.arrangeOrientingLayers(): orientingLayerName is " + orientingLayerName
            item = legend.findItems(orientingLayerName, 
                                          QtCore.Qt.MatchFixedString, 0)
            print "Main.mainwindow.arrangeOrientingLayers(): length of item list is " + str(len(item))
            if len(item) != 0:
                itemToMove = item[0]
                print str(legend.isLegendLayer(itemToMove))
                print "Main.mainwindow.arrangeOrientingLayers(): item to move is " + itemToMove.text(0)
                position = (numLegendLayers - (oVLayers.index(orientingLayer)
                                                           + (len(oRLayers) + 1)))
                print "Main.mainwindow.arrangeOrientingLayers(): v position is " + str(position)
                itemToMove.storeAppearanceSettings() # Store settings 
                legend.takeTopLevelItem(legend.indexOfTopLevelItem(itemToMove))
                legend.insertTopLevelItem(position, itemToMove)
                itemToMove.restoreAppearanceSettings()
                
        # now update the layer set to ensure proper rendering by QGIS
        self.legend.updateLayerSet()
                
    def setExtents(self):
        ''' Empty editing shapefiles do not have extents. We need to set extents often. '''
        # debugging
        print "Main.mainwindow.setExtents()"
        
        rect = self.canvas.extent()
        rectExtentMA = self.rectExtentMA
        smallRectExtentMA = QgsRectangle(27000, 780050, 336500, 964950)
        
        print "Main.mainwindow.setExtents(): The canvas extents on loading are:"
        print ("(" + str(rect.xMinimum()) + ", " + str(rect.yMinimum()) + ", " + 
                     str(rect.xMaximum()) + ", " + str(rect.yMaximum()) + ")")
        print "Main.mainwindow.setExtents(): rectExtentMA is "
        print ("(" + str(rectExtentMA.xMinimum()) + ", " + str(rectExtentMA.yMinimum()) + ", " + 
                     str(rectExtentMA.xMaximum()) + ", " + str(rectExtentMA.yMaximum()) + ")")
        # set extents no bigger than MA state extents
        if rect.contains(rectExtentMA) or not rect.intersects(rectExtentMA):
            print "Main.mainwindow.setExtents(): canvas extent contains or does not intersect MA"
            # set the canvas extents to be a little smaller than the MA Extent
            self.canvas.setExtent(smallRectExtentMA)
            self.canvas.updateFullExtent()
            self.canvas.refresh()
            print "Main.mainwindow.setExtents(): SET CANVAS TO MA EXTENT"
        else: print "Main.mainwindow.setExtents(): THE EXTENTS WERE NOT CHANGED" 
        
       
        # debugging
        rect = self.canvas.extent()
        print "Main.mainwindow.setExtents(): The canvas extents after loading are:"
        print ("(" + str(rect.xMinimum()) + ", " + str(rect.yMinimum()) + ", " + 
                     str(rect.xMaximum()) + ", " + str(rect.yMaximum()) + ")")
        print "Main.mainwindow.setExtents(): The scaled rectangle is "
        print ("(" + str(smallRectExtentMA.xMinimum()) + ", " + str(smallRectExtentMA.yMinimum()) + ", " + 
                     str(smallRectExtentMA.xMaximum()) + ", " + str(smallRectExtentMA.yMaximum()) + ")")
  
    def deleteExportScenarioFile(self):
        ''' Delete the scenario's export file.  Used by mainwindow.exportScenario()
            and legend.Legend.deleteEditingLayer()
        '''
        # debugging
        print "Main.mainwindow.deleteExportScenarioFile()"
        
        scenarioDirectoryName = unicode(self.scenarioInfo.completeBaseName())
        exportFileName = scenarioDirectoryName + ".csv"
        exportPath = config.scenarioExportsPath + exportFileName
 
        # if the scenario export file exists
        exportFile = QtCore.QFile(exportPath)
        error = None
        if exportFile.exists():
            try:
                exportFile.remove()
            except (IOError, OSError), e:
                error = unicode(e)
            if error:
                print error
                QtGui.QMessageBox.warning(self, 'Export Scenario Error:', 'The previously saved scenario '\
+ exportFileName + ' could not be deleted.  Please try again.')
          
    def setRendererV2(self):
        # debugging
        print "Main.mainWindow.setRendererV2()"
        print "Main.mainWindow.setRendererV2(): self.geom is :" + str(self.geom)
      
        if unicode(self.activeVLayer.name()) == config.editLayersBaseNames[0]: # edit_scenario(points) layer
            print "Main.mainWindow.setRendererV2(): Setting Rule Based Renderer for 'edit_scenario(points).shp"
            # if rule renderer is already set then no need to do anything, just return
            if self.activeVLayer.rendererV2().type() == "RuleRenderer": 
                print "Main.mainWindow.setRendererV2(): RuleRenderer returned"
                return
            # This returns a QgsSymbolV2().  In particular a QgsMarkerSymbolV2()
            # This also returns a QgsMarkerSymbolLayerV2() layer.
            # In particular a QgsSimpleMarkerSymbolLayerV2(). 
            symbol = QgsSymbolV2.defaultSymbol(QGis.Point)
            # renderer only needs a symbol to be instantiated
            rendererV2 = QgsRuleBasedRendererV2(symbol)
            # get the symbols list and symbol (usually only one symbol)
            symbol = rendererV2.symbols()[0]
            # return the symbol's symbol layer (usually only one layer)
            symbolLayer = symbol.symbolLayer(0)
            # This variable is set in Tools.shared.updateExtents() when reopening the editing layer.
            # after editing.  If the user had set a color, we reset it here. 
            if self.layerColor: 
                symbolLayer.setColor(self.layerColor)
                self.layerColor = None
                # color the preview icon
                self.legend.currentItem().vectorLayerSymbology(self.activeVLayer)
            else: symbolLayer.setColor(QtGui.QColor("red"))
            # create a new symbol layer for the delete symbol (i.e. a red cross)
            newSymbol = QgsSymbolV2.defaultSymbol(QGis.Point)
            map1 = {"name": "cross", "color": "255,0,0,255", 
                   "color_border": "255,0,0,255", "size": "7.0", "angle": "45.0"}
            deleteSymbol = newSymbol.createSimple(map1)
            deleteLayer = deleteSymbol.symbolLayer(0)
            # create a new symbol layer for the altered symbol (i.e. a green triangle
            map2 = {"name": "equilateral_triangle", "color": "0,0,0,0", 
                   "color_border": "255,0,0,255", "size": "7.0", "angle": "DEFAULT_SIMPLEMARKER_ANGLE"} 
            alteredSymbol = newSymbol.createSimple(map2)
            alteredLayer = alteredSymbol.symbolLayer(0)
            
            # make the rule, using the delete symbol, and add it
            rule1 = rendererV2.Rule(deleteSymbol, 0, 0, 
                "c_deleted='y' or d_deleted='y' or w_deleted='y' or r_deleted='y'")
            rendererV2.addRule(rule1)
            rule2 = rendererV2.Rule(alteredSymbol, 0, 0, 
                "c_altered = 'y' or d_altered = 'y' or w_altered = 'y' or r_altered = 'y'")
            rendererV2.addRule(rule2)
            # associate the new renderer with the activeVLayer
            self.activeVLayer.setRendererV2(rendererV2)
            # color the preview icon
            self.legend.currentItem().vectorLayerSymbology(self.activeVLayer)
            self.activeVLayer.triggerRepaint()
            # debugging
            #print "The delete layers name is: " + deleteLayer.name()
            print "Main.mainWindow.setRendererV2(): The number of symbols is: " + str(len(rendererV2.symbols()))
            print "Main.mainWindow.setRendererV2(): The number of rules is: " + str(rendererV2.ruleCount())
            print "Main.mainWindow.setRendererV2(): The symbolLayer properties are: "
            for k, v in symbolLayer.properties().iteritems():
                print "%s: %s" % (k, v)
            print "Main.mainWindow.setRendererV2(): The deleteLayer properties are: "
            for k, v in deleteLayer.properties().iteritems():
                print "%s: %s" % (k, v)
            print "Main.mainWindow.setRendererV2(): The alteredLayer properties are: "
            for k, v in alteredLayer.properties().iteritems():
                print "%s: %s" % (k, v)    
        elif unicode(self.activeVLayer.name()) == config.editLayersBaseNames[1]: # edit_scenario(lines).shp
            print "Main.mainWindow.setRendererV2(): Setting color and line width for edit_scenario(lines).shp"
            # this is a QgsLineSymbolLayerV2()
            symbolLayer = self.activeVLayer.rendererV2().symbols()[0].symbolLayer(0)
            if symbolLayer.width() == (0.4): # if line width and color already set then return
                return
            if self.layerColor: # we saved color in Tools.shared.setExtents()
                print "Main.mainWindow.setRendererV2(): THERE IS A LINE COLOR"
                symbolLayer.setColor(self.layerColor)
                self.layerColor = None
                # color the preview icon
                self.legend.currentItem().vectorLayerSymbology(self.activeVLayer)
            else: symbolLayer.setColor(QtGui.QColor("red")) # default to red if user has not chosen other color   
            symbolLayer.setWidth(0.4)
            # color the preview icon
            self.legend.currentItem().vectorLayerSymbology(self.activeVLayer)
            self.activeVLayer.triggerRepaint() 
        elif unicode(self.activeVLayer.name()) == config.editLayersBaseNames[2]: #edit_scenario(polygons).shp
            print "Main.mainWindow.setRendererV2(): Setting color for edit_scenario(polygons).shp"
        
            symbolLayer = self.activeVLayer.rendererV2().symbols()[0].symbolLayer(0)
            # if the layer is being reloaded by update extents after editing then set the color
            if self.layerColor: # we saved color in Tools.shared.setExtents()
                print "Main.mainWindow.setRendererV2(): THERE IS A POLYGON COLOR"
                symbolLayer.setColor(self.layerColor)
                self.layerColor = None
                # color the preview icon
                self.legend.currentItem().vectorLayerSymbology(self.activeVLayer)
                self.activeVLayer.triggerRepaint()
                return
            # If the layer is being loaded from a scenario file return so that the
            #  layer color will be set to the color property in the scenario file.
            if self.origScenarioLyrsLoaded == False:
                print "Main.mainWindow.setRendererV2(): The " + config.editLayersBaseNames[2] + "is loading from a scenario"
                self.editingPolygon = True
                return
            # If the layer was loaded from a scenario file then return because
            # we don't want to change the user's color selection.
            if self.editingPolygon == True:
                return
            # if the layer being loaded into the scenario for the first time default to red
            symbolLayer.setColor(QtGui.QColor("red"))
            # color the preview icon
            self.legend.currentItem().vectorLayerSymbology(self.activeVLayer)
            self.activeVLayer.triggerRepaint()
        elif unicode(self.activeVLayer.name()) == config.orientingLayersChecked[0]: # the base_towns layer
            print "Main.mainWindow.setRendererV2(): This is the base_towns layer"
            # Set the base_towns layer fill color to none
            rendererV2 = self.activeVLayer.rendererV2()
            symbol = rendererV2.symbols()[0]
            symbolMap = {"color": "255, 255, 255, 0", "style": "no", 
                              "color_border": "DEFAULT_SIMPLEFILL_BORDERCOLOR", 
                              "style_border": "DEFAULT_SIMPLEFILL_BORDERSTYLE", 
                              "width_border": "0.3" }
            simpleSymbol = symbol.createSimple(symbolMap)
            rendererV2.setSymbol(simpleSymbol)
            self.legend.currentItem().vectorLayerSymbology(self.activeVLayer)
            self.activeVLayer.triggerRepaint()
        elif self.geom == 1: # set line width for all line layers
            # debugging
            print "Main.mainWindow.setRendererV2(): geometry = 1"
            symbolLayer = self.activeVLayer.rendererV2().symbols()[0].symbolLayer(0)
            print "Main.mainWindow.setRendererV2(): The line width before setting is: " + str(symbolLayer.width())
            symbolLayer.setWidth(0.4)
            print "Main.mainWindow.setRendererV2(): The line width after setting is: " + str(symbolLayer.width())
            self.activeVLayer.triggerRepaint()
        # debugging
        if self.activeVLayer.isUsingRendererV2():
            rendererV2 = self.activeVLayer.rendererV2()
            symbols = rendererV2.symbols()
            # only 1 symbol in symbols and only one layer
            symbol = symbols[0]
            symbolLayer = symbol.symbolLayer(0)
            print "Main.mainWindow.setRendererV2(): rendererV2.dump is:" + rendererV2.dump()
            print "Main.mainWindow.setRendererV2(): The layer properties are: "
            for k, v in symbolLayer.properties().iteritems():
                print "%s: %s" % (k, v)
            print "Main.mainWindow.setRendererV2(): The number of symbols is: " + str(len(symbols))
            print "Main.mainWindow.setRendererV2(): The number of layers in symbols[0] is: " + str(symbol.symbolLayerCount())
            print "Main.mainWindow.setRendererV2(): The layer type is: " + str(symbolLayer.layerType())
       
    def checkLayerLoadError(self, layer):
        # debugging
        print "Main.mainwindow.checkLayerLoadError()"
        # check for error
        if not layer.isValid():
            QtGui.QMessageBox.warning(self, "File Error", "Layer failed to load!")
            return False
        else: return True

    def checkBaseLayerMatch(self, title, text):
        ''' Checks whether the base layer selected matches the current scenario edit type '''
        # debugging
        print 'Main.mainwindow.checkBaseLayerMatch()'
        name = unicode(self.activeVLayer.name())
        editType = self.scenarioEditType
        if (editType == config.scenarioEditTypesList[0] and name != config.pointBaseLayersBaseNames[0] or
             editType == config.scenarioEditTypesList[1] and name != config.pointBaseLayersBaseNames[1] or
             editType == config.scenarioEditTypesList[2] and name != config.pointBaseLayersBaseNames[2] or
             editType == config.scenarioEditTypesList[3] and name != config.pointBaseLayersBaseNames[3]):
            QtGui.QMessageBox.warning(self, title, "The point base layer which \
you are trying to " + text + " does not match the scenario edit type you have chosen. \
For example. If you have chosen to edit 'dams,' then you can only " + text + " the layer \
'base_dams'")
            return False
        else: return True

    def setSelectionColor(self):
        # debugging
        print 'Main.mainwindow.setSelectionColor()'
        renderer = QgsSingleSymbolRenderer(QGis.Point)
        color = QtGui.QColor("yellow")
        renderer.setSelectionColor(color)
        print "Main.mainwindow.setSelectionColor(): The renderer name is: " + renderer.name()
        print "Main.mainwindow.setSelectionColor(): The renderer.selectionColor() is: " + renderer.selectionColor().name()
    
    def roundGeometryValues(self, vlayer):
        ''' Rounds geometry values of editing layers just before converting to csv layers '''
        # debug
        print "Main.mainwindow.roundGeometryValues()"

        provider = vlayer.dataProvider()
        feat = QgsFeature()
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        retval = False
        if vlayer.geometryType() == 0: # point
            roundPointGeom = None
            while provider.nextFeature(feat):
                point = feat.geometry().asPoint()
                roundPointGeom = QgsGeometry.fromPoint(QgsPoint(round(point.x(), 2), round(point.y(), 2)))
                retval = provider.changeGeometryValues({feat.id(): roundPointGeom})
        elif vlayer.geometryType() == 1: # line
            while provider.nextFeature(feat):
                roundedLine = []
                line = feat.geometry().asPolyline()
                for point in line: 
                    roundedLine.append(QgsPoint(round(point.x(), 2), round(point.y(), 2)))
                retval = provider.changeGeometryValues({feat.id(): QgsGeometry.fromPolyline(roundedLine)})
        elif vlayer.geometryType() == 2: # polygon
            while provider.nextFeature(feat):
                # a list of lists because polygons can have nested polygons
                allPolygons = feat.geometry().asPolygon()
                allPolygonsRounded = [] 
                for polygon in (allPolygons):
                    roundedPolygon = []
                    for point in polygon:
                        roundedPolygon.append(QgsPoint(round(point.x(), 2), round(point.y(), 2)))
                    allPolygonsRounded.append(roundedPolygon)        
                retval = provider.changeGeometryValues({feat.id(): QgsGeometry.fromPolygon(allPolygonsRounded)})
                print allPolygonsRounded
        if retval: return vlayer
        else: 
            QtGui.QMessageBox.warning(self, "Export Scenario Error:", "Rounding the coordinate values in the \
CSV export file failed. Please try again.")
            return False
        
    def checkPastedFeatureConstraints(self):
        ''' Utility method to check constraints for pasted features '''
        # debugging
        print "Main.mainwindow.checkPastedFeatureConstraints()"
        
        #xform = self.canvas.getCoordinateTransform() # returns the QgsMapToPixel() class for the map canvas
        qPoint = None
        if self.geom == 0:
            for feat in self.copiedFeats:
                qgsPoint = feat.geometry().asPoint()
                # xform.transform(qgsPoint) # QgsMapToPixel.transform() changes map coords to device coords
                featId = feat.id()
                print "Main.mainwindow.checkPastedFeatureConstraints(): The point is " + str(qgsPoint) 
                if not shared.checkConstraints(self, qgsPoint, qPoint, featId): 
                    # check constraints failed so undo the copy and disable the paste action
                    self.copiedFeats = None
                    self.copyFlag = False
                    self.mpActionPasteFeatures.setDisabled(True)
                    return False
            else: return True
        elif self.geom == 1:
            for feat in self.copiedFeats:
                featId = feat.id()
                line = feat.geometry().asPolyline()
                endCount = len(line)
                for count, point in enumerate(line): # get the first point and last point of the line
                    if count == 0:
                        firstPoint = point
                        print "Main.mainwindow.checkPastedFeatureConstraints(): firstPoint is (" + str(point.x()) + ", " + str(point.y()) + ")" 
                    elif count == endCount-1:
                        lastPoint = point
                        print "Main.mainwindow.checkPastedFeatureConstraints(): lastPoint is (" + str(point.x()) + ", " + str(point.y()) + ")"
                for count, qgsPoint in enumerate([firstPoint, lastPoint]):
                    #qPoint = None #xform.transform(qgsPoint) # QgsMapToPixel.transform() changes map coords to device coords
                    if shared.checkRoadConstraints(self, config.baseLayersPath, qgsPoint, qPoint, self.scenarioEditType, featId):
                        break # feat meets constraints, so go to next feat
                    elif count == 0: continue
                    else: 
                        QtGui.QMessageBox.warning(self, "Constraints Error:", "All pasted features must fall \
on a road in the 'base_traffic' layer. The feature in row " + str(featId+1) + " in the attribute table of \
the layer you copied from does not meet this constraint.  Please check all your points carefully and try again.")
                        return False
            else: return True    
        else: return True                
#**************************************************************
    ''' Testing '''
#**************************************************************
                   
    def printFields(self):
        ''' Testing '''
        # debugging
        print "Main.mainwindow.printFields(): Testing"
        
        #field = QgsField()
        names = []
        provider = self.activeVLayer.dataProvider()
        provider.reloadData()
        fields = provider.fields()
        print fields
        for value in fields.itervalues():
            print value
            print unicode( value )
            print unicode(value.name())
            print value.name()
            names.append( unicode(value.name()) )
            
        print names
        print fields.values()
 
    def printFeatures(self):
        ''' Testing '''
        # debugging
        print "Main.mainwindow.printFields(): Testing"
        
        provider = self.activeVLayer.dataProvider()
        provider.reloadData()
        feat = QgsFeature()
        
        #self.featsAdded = 5
        #provider.deleteFeatures( [3, 4] )
        #self.canvas.refresh()
        #check if our feature was really written to the file
        print provider.featureCount()
        
        # get all the data for the layer (a QgsAttributeList)
        allAttrs = provider.attributeIndexes()
        # the select() method initializes retrieval of data
        provider.select(allAttrs)
        # the nextFeature() method operates on a select initialized provider
        while provider.nextFeature(feat):
            # fetch the feature geometry, which is the feature's spatial coordinates
            fgeom = feat.geometry()
            # This prints the feature's ID and its spatial coordinates
            print "Feature ID %d: %s\n" % (feat.id(), fgeom.exportToWkt()) 
            print type(feat.id())
            # a QgsAttributeMap is a pointer to a series of QtCore.QVariant objects
            attrs = feat.attributeMap() 
             
            # the map first prints the Qgs feature ID and 
            # then it prints the field key (starting with 0 for the first field) and the field's value.
            # note: the QgsAttribute map is a Python dictionary (key = field id : field value)
            for (key, attr) in attrs.iteritems():
                print "%d: %s" % (key, attr.toString())
                

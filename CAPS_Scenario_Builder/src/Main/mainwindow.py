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

#CAPS is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#CAPS is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with CAPS.  If not, see <http://www.gnu.org/licenses/>..
# 
#---------------------------------------------------------------------
# general python built_in imports
import os,  shutil, time, os.path #  copy, subprocess, sys,  stat,
# third-party utility modules
#from lockfile import LockFile
# the below is a standard python library
# from fcntl import flock

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
import Tools.shared
from Main.dlgscenariotypes import DlgScenarioTypes
import config


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, splash):
        QtGui.QMainWindow.__init__(self)
    
        # add the Qt4 designer code elements to the MainWindow
        self.setupUi(self)
        # get the splash screen
        self.splash = splash

        # save the filename of the last opened raster or vector file (unicode)
        # a Python string or unicode object, a QLatin1String or a QChar 
        # may be used whenever a QString is expected
   
        # LISTS
        self.originalScenarioLayers = []
        self.currentLayers = []
        self.copiedFeats = []
        self.originalFeats = []
     
        # FLAGS
        self.scenarioDirty = False
        self.origScenarioLyrsLoaded = False 
        self.copyFlag = False # True if selections copied
        self.exportFileFlag = False
        self.isBaseLayerDeletions = False
        # if editDirty contains activeVLayer name, edits are unsaved
        self.editDirty = False #if editDirty false edits saved
        self.editMode = False # True if "Toggle Edits" is activated
        
        # OBJECTS
        self.attrTable = None
        self.dwAttrTable = None
        self.dwRasterTable = None
        self.scenarioInfo = None
        # get active vlayer to pass to edit tools
        # this variable is updated by self.activeLayerChanged
        self.activeVLayer = None
        self.activeRLayer = None
        self.provider = None
        #set tool variables
        self.toolSelect = None
        self.toolAddPoints = None
        self.toolAddLinesPolygons = None
     
        # VALUES
        self.scenarioFilePath = None
        self.scenarioFileName = None
        self.scenarioType = None
        self.currentLayersCount = None
        self.layerType = None
        # get the geometry of the activeVLayer
        self.geom = None #0 point, 1 line, 2 polygon
        # This saves an editing layer's color so that it gets refreshed
        # when the layer loads after updating extents (see shared.updateExtents
        self.layerColor = None     

        
        # create map canvas
        self.canvas = QgsMapCanvas()
        self.mapRenderer = self.canvas.mapRenderer()
        self.mapRenderer.setDestinationCrs(config.crs)
        self.mapRenderer.setExtent(config.rectExtentMA)
        self.canvas.setCanvasColor(QtGui.QColor(255,255,255))
        self.canvas.enableAntiAliasing(True)
        self.canvas.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.canvas.setExtent(config.rectExtentMA)# MA state extents
        self.canvas.show()

        # lay our canvas out in the main window with 
        # 'self.frame' as the parent
        self.canvaslayout = QtGui.QVBoxLayout(self.frame)
        self.canvaslayout.addWidget(self.canvas)
      
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
        QtCore.QObject.connect(self.mpActionModifyPoints, QtCore.SIGNAL("triggered()"), self.modifyPoints)
        
        # Instantiate all tools.  They are written so variables update
        # from the main window, so there is no need to repeat the process 
        # when layers or other variables change.
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False) # false = in
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out
        self.toolIdentify = Identify(self)
        self.toolSelect = SelectTool(self)
        self.toolAddPoints = AddPoints(self)
        self.toolAddLinesPolygons = AddLinesPolygons(self)
        
        # Create a QActionGroup to manage edit actions states
        # If an action is set as "checkable" in mainwindow_ui.py and
        # the action is in a tool group, only one action in the 
        # group can be active at a time (). All other buttons 
        # are deactivated.  A toolGroup also makes it possible to
        # easily set all actions in the group as enabled or disabled.
        self.toolGroup = QtGui.QActionGroup(self)
        self.toolGroup.addAction(self.mpActionPan)
        self.toolGroup.addAction(self.mpActionZoomIn)
        self.toolGroup.addAction(self.mpActionZoomOut)
        self.toolGroup.addAction(self.mpActionZoomtoMapExtent)
        self.toolGroup.addAction(self.mpActionIdentifyFeatures)
        self.toolGroup.addAction(self.mpActionSelectFeatures)
        self.toolGroup.addAction(self.mpActionDeselectFeatures)
        #self.toolGroup.addAction(self.mpActionModifyPoints)
        self.toolGroup.addAction(self.mpActionDeleteFeatures)
        self.toolGroup.addAction(self.mpActionCopyFeatures)
        self.toolGroup.addAction(self.mpActionPasteFeatures)
        self.toolGroup.addAction(self.mpActionAddPoints)
        self.toolGroup.addAction(self.mpActionAddLines)
        self.toolGroup.addAction(self.mpActionAddPolygons)
        #self.toolGroup.addAction(self.mpActionOpenVectorAttributeTable)
        #self.toolGroup.addAction(self.mpActionSaveEdits)
        #self.toolGroup.addAction(self.mpActionExportScenario)
                         
        # set initial action states; all disabled except:
        # New Scenario, Open Scenario, Save Scenario, Save Scenario As,
        # Add Vector, Add Raster and Open Raster Category Table are on 
        self.toolGroup.setDisabled(True)
        #self.mpActionEditScenario.setDisabled(False)
        self.mpActionOpenVectorAttributeTable.setDisabled(True)
        self.mpActionSaveEdits.setDisabled(True)
        self.mpActionExportScenario.setDisabled(True)
        self.mpActionModifyPoints.setDisabled(True)
 
        # set the map coordinates display in the status bar
        self.mapcoords = MapCoords(self)
        
        # create the legend from legend.py
        self.legend = Legend(self)
        self.legend.setCanvas(self.canvas)
        self.legend.setObjectName("theMapLegend")
        # set the QDockWidget that holds the legend
        self.LegendDock = QtGui.QDockWidget("Layers", self)
        self.LegendDock.setObjectName("legend")
        # without "NoDockWidgetFeatures, the user could close the legend with no way to reopen it
        self.LegendDock.setFeatures(self.LegendDock.NoDockWidgetFeatures)
        self.LegendDock.setWidget(self.legend)
        self.LegendDock.setContentsMargins (9, 9, 9, 9)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.LegendDock)

        # now that we have self.legend, get active layer changed signal
        # connect the Python 'short circuit' signal from legend.py to the handler
        self.connect( self.legend, QtCore.SIGNAL("activeLayerChanged"), self.activeLayerChanged)
         
        # close splash screen
        time.sleep(2)
        self.splash.hide()
        
        # set the selection color
        #self.setSelectionColor()
        # load the orienting layers
        self.openOrientingLayers()

############################################################################################   
    ''' SCENARIO MENU CUSTOM SLOTS '''
############################################################################################  
         
    def newScenario(self):
        # debugging
        print "newScenario()"
        print "newScenario() start dirty? " + str(self.scenarioDirty)
        
        # check for unsaved edits and scenario changes
        if self.appStateChanged("newScenario") == "Cancel":
            # debugging
            print "canceling newScenario"
            return
 
        # new scenario so remove layers from the legend and the canvas layer set
        self.legend.removeAll()
        # remove all layers from the QgsMapLayerRegistry
        QgsMapLayerRegistry.instance().removeAllMapLayers()

        # go back to app opening state
        self.setInitialAppState()
                
        # debugging
        print "newScenario() setIntialAppState()"
        print "newScenario() end dirty? " + str(self.scenarioDirty)
   
    def openScenario(self):
        # debugging
        print "openScenario()"
        print "self.scenarioDirty begin is " + str(self.scenarioDirty)
        
        # check for unsaved edits and scenario changes
        if self.appStateChanged("openScenario") == "Cancel":
            # debugging
            print "canceling openScenario()"
            return
     
        # open file dialog to find scenarios to open
        qd = QtGui.QFileDialog()
        filterString = QtCore.QString("CAPS Scenario (*.cap)\nAll Files(*)")
        # get the path to the directory for the saved file using Python
        dir = QtCore.QString(os.path.dirname(config.scenariosPath))
        # change QString to unicode so Python can slice it for the directory name
        scenarioFilePath = unicode(qd.getOpenFileName(self, QtCore.QString
                                                ("Open Scenario"), dir, filterString))
        # Check for cancel
        if len(scenarioFilePath) == 0:
            return
        
        # remember the file info to use in saveScenario()
        self.scenarioFilePath = scenarioFilePath
        self.scenarioInfo = QtCore.QFileInfo(QtCore.QString(scenarioFilePath))
        # get the filename without the path
        self.scenarioFileName = self.scenarioInfo.fileName()
        
        #debugging
        print "openScenario() " + scenarioFilePath
     
        # remove old layers from the legend and the canvas layer set
        self.legend.removeAll()
        # remove all layers from the registry
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        # set the originalScenarioLayers to None
        self.originalScenarioLayers = []
        
        # debugging
        print "openScenario() after remove registry count " + str(QgsMapLayerRegistry.instance().count())
     
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
        else: # no error so we have newly opened scenario
            scenario = None 
            self.scenarioDirty = False
             
        # The scenario file (i.e. *.cap) does not save the files in order so:
        self.arrangeOrientingLayers()
        
        # I like the towns layer to be selected so if it is open, I do it here.
        for checked in config.baseLayersChecked:
            items = self.legend.findItems(checked, QtCore.Qt.MatchFixedString, 0)
            print "the length of items is " + str(len(items))
            if len(items) > 0:
                item = items[0]
                item.setCheckState(0, QtCore.Qt.Checked)    

        # give the user some file info
        self.setWindowTitle("Conservation Assessment and \
Prioritization System (CAPS) Scenario Builder - " + self.scenarioFileName)
        
        # debugging
        print "openScenario() after scenario load registry count " + str(QgsMapLayerRegistry.instance().count())
        print "openScenario() scenario filename is " + self.scenarioFileName
        print "openScenario() end dirty? " + str(self.scenarioDirty)
        
    def saveScenario(self):
        # debugging
        print "saveScenario()"
        print "saveScenario() start dirty? " + str(self.scenarioDirty)
        
        # check for unsaved edits
        if self.appStateChanged("saveScenario") == "Cancel":
            # debugging
            print "canceling openScenario()"
            return
        
        
        # if there is an open project to save
        if self.scenarioFilePath:
            # check if there is a scenario directory
            scenarioDirectoryName = self.scenarioInfo.completeBaseName()
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
                print "saveScenario() end dirty? " + str(self.scenarioDirty)
        else: self.saveScenarioAs() # no open project so call saveScenarioAs()

    def saveScenarioAs(self):
        ''' 
            Save an unsaved scenario with a new name; save the current scenario with the same name;
            overwrite an existing scenario with a different scenario; or save an existing scenario 
            with a new name.
            
            This method includes making a copy of the scenario's '.cap' file,
            the scenario's associated directory, any editing shapefiles in the scenario's 
            directory, and any existing 'Scenario Export' files.  In other words, this makes
            a "deep" copy of all the important scenario files.
        '''
        
        # debugging
        print "saveScenarioAs()"
        print "saveScenarioAs() start dirty? " + str(self.scenarioDirty)
        
        # check for unsaved edits
        if self.appStateChanged("saveScenarioAs") == "Cancel":
            # debugging
            print "canceling openScenario()"
            return
        
        ''' GET THE FILE PATH THE USER CHOOSES '''
        
        qd = QtGui.QFileDialog()
        filterString = QtCore.QString("CAPS Scenario (*.cap)\nAll Files(*)")
        # get the path to the directory for the saved file (use Python)
        dir = os.path.dirname(config.scenariosPath)
        # Get the new file path and change the QString to unicode so that Python 
        # can slice it for the directory name. 
        scenarioFilePath = unicode(qd.getSaveFileName(self, QtCore.QString
                                    ("Save scenario as ..."), dir, filterString))
        
        # debugging
        print "scenarioFilePath is: " + scenarioFilePath
        
        # Check for cancel
        if len(scenarioFilePath) == 0:
            return "Cancel"
    
        # We have a new file path. We start by storing the old path (if one exists) for use
        # below and storing the new file path for use in saveScenario()
        oldScenarioFilePath = self.scenarioFilePath
        oldScenarioInfo = self.scenarioInfo
        self.scenarioFilePath = scenarioFilePath
        self.scenarioInfo = QtCore.QFileInfo(QtCore.QString(scenarioFilePath))
        scenarioDirectoryName = self.scenarioInfo.completeBaseName()
        
        ''' CHECK FOR CONDITIONS THAT ELIMINATE THE NEED TO COPY THE SCENARIO DIRECTORY CONTENTS '''
        
        # Check if the new path is the same as the old path, and if it is, just call save 
        # scenario to overwrite the scenario file. No need to do anything about editing files
        if self.scenarioFilePath == oldScenarioFilePath:
            self.saveScenario()
            print "overwriting existing file"
            return

        # We are saving to a new path, so find out if there are any editing files open.
        editLayerLegendItems = []
        for editLayer in config.editLayersBaseNames:
            # This method returns a list of matches
            items = self.legend.findItems(editLayer, QtCore.Qt.MatchFixedString, 0)
            if len(items) > 0:    
                editLayerLegendItems.append(items[0])

        # If there are no editing layers open, we can just write the new editing file 
        # directory, call saveScenario, and set the variables for a successfully saved
        # scenario and return. Any previously existing 'Export Scenario' file would have
        # been deleted when the editing shapefile was removed. 
        # Note that this could be a case where we are saving the scenario
        # for the first time, or saving an existing scenario with a new 
        # name.  In either case the needed actions are the same.
        if len(editLayerLegendItems) == 0:
            self.makeScenarioDirectory()
            self.saveScenario()
            self.setScenarioSaved()
            return

        ''' 
            WE NEED TO COPY THE SCENARIO DIRECTORY'S CONTENTS (I.E. EDITING SHAPEFILES)
            AND ANY EXISTING EXPORT SCENARIO FILE, SO START THE PROCESS 
        '''
        
        # So we have editing files open so create the new scenario directory to write them to.
        # This method deletes any old directory and any old "Scenario Export" files having the
        # same name as the new scenario name.  So if we are overwriting an old scenario, we
        # start fresh.
        self.makeScenarioDirectory()
        
        # Now copy any existing "Export Scenario" file 
        oldScenarioDirectoryName = oldScenarioInfo.completeBaseName()
        oldExportFileName = unicode(oldScenarioDirectoryName + ".csv")
        oldExportPath = QtCore.QString(config.scenarioExportsPath + oldExportFileName)
        newExportFileName = QtCore.QString(scenarioDirectoryName + ".csv")
        newExportFilePath = QtCore.QString(config.scenarioExportsPath + newExportFileName)
        
        oldExportFile = QtCore.QFile(oldExportPath)
        error = None
        if oldExportFile.exists():
            try:
                oldExportFile.copy(newExportFilePath)
            except (IOError, OSError), e:
                error = unicode(e)
            if error:
                print error
                QtGui.QMessageBox.warning(self, 'Deletion Error:', 'The previously saved scenario '\
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
            copyPath = QtCore.QString(scenarioDirectoryPath + "/" + vlayerName)
            copyPaths.append(copyPath)
            print "copyPath is " + copyPath
            error = QgsVectorFileWriter.writeAsVectorFormat(vlayer, copyPath , "utf-8", 
                                                                config.crs, "ESRI Shapefile")
            if error != QgsVectorFileWriter.NoError:
                QtGui.QMessageBox.warning(self, "Write Error:", "The file " + vlayerName + " \
was not written.  Please check that a file with the same name is not open in another program.")
                return
            else: print "Success!"

        # debugging
        print "copyPaths are:"
        print copyPaths
        
        # Now we can close the editing layers associated with the old scenario path
        # and then open the ones we wrote to the new directory.  This will allow us 
        # to save a new scenario file (i.e. '.cap' file) that contains the correct
        # paths to the copied editing shapefiles. No need for emitting signals here.
        self.legend.blockSignals(True)
        self.legend.removeLayers(editLayerIds) # this method also removes the files from the registry
        self.legend.blockSignals(False)
        print "CLOSED OLD EDIT SHAPEFILES"
        
        # The old activeVLayer may have been deleted so set to none or we get
        # RunTime errors due to the underlying C++ object being deleted.
        # The activeVLayer will be reset when we load the layers below.
        self.activeVLayer = None
        self.originalScenarioLayers = []
        # Open the copied editing shapefiles (they will open at the top of the layer panel)
        # The last one opened will become the new activeVLayer
        for path in copyPaths:
            if not self.openVectorLayer(path): return
            
        self.originalScenarioLayers = self.getCurrentLayers().values()
        
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
     
        ''' NOW DO SOME HOUSEKEEPING '''    
 
        self.setScenarioSaved()
        
        # debugging
        print "saveScenarioAs() end dirty? " + str(self.scenarioDirty)
   
    def exportScenario(self):
        # debugging
        print "exportScenario()"
        
        # check the app state for unsaved edits and scenario changes
        if self.appStateChanged("exportScenario") == "Cancel":
            # debugging
            print "canceling exportScenario()"
            return

        scenarioDirectoryName = self.scenarioInfo.completeBaseName()
        scenarioDirectoryPath = unicode(config.scenariosPath + scenarioDirectoryName)
        scenarioDirectoryFileList = os.listdir(scenarioDirectoryPath) # use Python os module here
        exportFileName = unicode(scenarioDirectoryName + ".csv")
        exportPath = unicode(config.scenarioExportsPath + exportFileName)
        
        self.deleteExportScenarioFile()

        # Iterate through the editing shapefiles in the current scenario's directory.
        # Open the file if it is not already open, and write it as a csv file.  
        # Finally, append the editing shapefile csv file to the scenario export file,
        # which will consist of all edits to the current scenario in csv format.
        for fileName in scenarioDirectoryFileList:
            if not ".shp" in fileName: # only looking for the .shp files
                continue
            # get the path to write the csv file to
            csvInfo = QtCore.QFileInfo(fileName)
            csvBaseName = csvInfo.completeBaseName() # csvBaseName = editing shapefile BaseName
            csvFileName = csvBaseName + ".csv"
            csvPath = QtCore.QString(scenarioDirectoryPath + "/" + csvFileName)
            
            # debugging
            print "current csvBaseName is: " + csvBaseName
            print "current csvFileName is: " + csvFileName
            print "current csvPath is: " + csvPath
            print "current exportPath is: " + exportPath
            
            # The app crashes when trying to open an already open vector layer.
            # Even the "ogr" provider misses the IO error.  It seems impossible to trap this
            # error with Python (i.e. try: except), so we need rely on checking 
            # if the editing shapefile is open in the layer panel.
            items = self.legend.findItems(csvBaseName, QtCore.Qt.MatchFixedString, 0)
            print "length of items list is " + str(len(items))
            if len(items) == 0:
                # if not open, open the file without making it visible to the user
                editingShapefilePath = unicode(scenarioDirectoryPath + "/" + fileName)
                print "current editingShapefilePath is: " + editingShapefilePath
                vlayer = self.openHiddenVectorLayer(editingShapefilePath)
                if not vlayer: return
            else:
                vlayerID = items[0].layerId
                vlayer = QgsMapLayerRegistry.instance().mapLayer(vlayerID)
            
            # We need to delete any existing editing shapefile exports for this editing shapefile
            # before we write a new one. The ogr driver creates a directory named "csvBaseName" 
            # and then puts the .csv file in it. The ogr CSV driver does not seem to support 
            # "-overwrite", so we delete the directory and its contents.
            error = None
            
            if QtCore.QDir(csvPath).exists():
                csvPath = unicode(csvPath) # python needs a python string
                print "csv directory exists " + csvPath    
                try:
                    shutil.rmtree(csvPath) # use python here
                except (IOError, OSError), e:
                    error = unicode(e)
                if error:
                    print e
                    QtGui.QMessageBox.warning(self, "Deletion Error:", "The folder \
containing " + csvFileName + " could not be completely removed. Please check if the file \
is open in another program.")
                    break
            
            # Create an empty datasource and errorMessage option for the 
            # QgsVectorFileWriter parameters list
            datasourceOptions = QtCore.QStringList(QtCore.QString())
            errorMessage = QtCore.QString()
            # Need to include the creationOptions or the geometry will not be written.
            creationOptions = QtCore.QStringList(QtCore.QString("GEOMETRY=AS_WKT"))
            # write csv file in MA State Plane coordinates and check for error
            error = QgsVectorFileWriter.writeAsVectorFormat(vlayer, csvPath, "utf-8", 
                        config.crs, "CSV", False, errorMessage  , datasourceOptions, creationOptions)
            if error != QgsVectorFileWriter.NoError:
                QtGui.QMessageBox.warning(self, "Write Error:", "The file " + csvFileName + " \
was not written.  Please check that a file with the same name is not open in another program.")
            else: print "Success!"
            
            # Now write the csv to the file to be exported to UMass using python
            try:
                csvExportScenario = open(exportPath, 'a')
                csvEditingShapefile = open(csvPath + '/' + csvFileName, 'r')
                csvText = csvEditingShapefile.read()
                csvEditingShapefile.close()
                csvExportScenario.write(csvText)
                csvExportScenario.close()
            except (IOError, OSError), e:
                error = unicode(e)
            if error:
                print e
                QtGui.QMessageBox.warning(self, 'Export Error:', 'The export file, ' \
+ exportFileName + ' could not be written.  Please try again.')
                
        # Exited the for loop, so let the user know things worked
        QtGui.QMessageBox.information(self, 'Export Succeeded:', "The export file is named "\
 + exportFileName + ". It can be found in the CAPS Scenario Builder program directory \
in the Exported Scenarios folder." )
          
      
############################################################################################   
    ''' EDITING MENU CUSTOM SLOTS '''
############################################################################################
 
    def selectFeatures(self, state):
        ''' Slot to handle user clicking the "Select Features" action '''
        # debugging
        print "selectFeatures() " + str(state)
        
        if self.appStateChanged("selectFeatures") == "Cancel":
            self.mpActionSelectFeatures.blockSignals(True)
            self.mpActionSelectFeatures.setChecked(False)
            self.mpActionSelectFeatures.blockSignals(False)
            return
  
        if state: # for action selected state = True
            # select action is selected so enable these tools
            self.canvas.setMapTool(self.toolSelect)
            self.enableSelectSubActions()
        else: # action deselected (state = False)
            # debugging
            print "selectFeatures() state is false"
            # select action is not selected so disable these tools
            self.disableSelectActions()  
 
    def deselectFeatures(self):
        ''' Slot to clear the selected features without deleting them '''
        # debugging
        print "deselectFeatures()"
        
        # selectedFeatures() returns a QgsFeatureList
        count = self.activeVLayer.selectedFeatureCount()
        
        # debugging
        print "num features " + str(count)
        
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
        ''' Slot to handle copying features '''
        # debugging
        print "copyFeatures()"

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
        self.mpActionPasteFeatures.setEnabled(True)
                 
    def modifyPoints(self):
        ''' Allow the user to modify points on base layers '''
        # check if there are any features selected to modify 
        count = self.activeVLayer.selectedFeatureCount()
        if count == 0:
            title = "Modify Selected Features"
            text = "You must select at least one feature on a points base layer before you\
 can modify it.  If you have correctly selected points and you get this message then you need to make \
 sure that the base layer you want to modify is the currently active layer."
            # pop up message box to inform user that nothing is selected
            QtGui.QMessageBox.information(self, title, text, QtGui.QMessageBox.Ok)
            return
        
        # Check if the base layer matches the scenario type.  If it does not, we get
        # incorrect entries in the editing shapefile attribute table!
        title = "Modify Point Error:"
        text = "modify"
        if not self.checkBaseLayerMatch(title, text):
            return
        
        # we have selected features so copy them
        self.copyFeaturesShared()
        
        # While we have a handle to the base layer, hide it so the user can see the pasted points.
        self.legend.currentItem().setCheckState(0, QtCore.Qt.Unchecked)
        
        # Open "edit_scenario(points).shp if it is not open. If open, make it the activeLayer
        items = self.legend.findItems(config.editLayersBaseNames[0], QtCore.Qt.MatchFixedString, 0)
        if len(items) == 0:
            vfilePath = config.baseLayersPath + config.editLayersBaseNames[0] + ".shp"
            self.openVectorLayer(vfilePath)
        else: 
            self.legend.setCurrentItem(items[0])
            self.legend.currentItem().setCheckState(0, QtCore.Qt.Checked)
        # Now paste the features into the editing layer
        # This is almost exactly the same action as pasting base layer deletions
        # except we have to pass a "modifyFlag" so that DlgAddAttributes.getNewAttributes
        # sets the altered flag to "y."  Also the flag serves to set the text of any error 
        # any error messages correctly.
        self.pasteFeatures(True)
 
    def deleteFeatures(self):
        ''' Slot to delete selected features '''
        # debugging
        print "deleteFeatures()"
        print self.activeVLayer.name()
 
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
        
        # if the user is deleting baselayer features
        name = self.activeVLayer.name()
        type = self.scenarioType
        if name in config.pointBaseLayers:
            title = "Deletion Error:"
            text = "delete from"
            if not self.checkBaseLayerMatch(title, text):
                return
            else:
                print "Features are in a base layer that matches"
                # We do not allow deleting features from a base layer.  Rather, we copy
                # the features the user wants to delete, and paste them into an editing shapefile.
                self.copyFeaturesShared()
                self.pasteBaseLayerDeletions()
                return
                
        # so we have some features to delete
        vfilePath = self.activeVLayer.source()
        info = QtCore.QFileInfo(QtCore.QString(vfilePath))
        vfileName = info.completeBaseName()
        
        # Check if the user is deleting scenario edits and set appropriate warning
        if self.activeVLayer.name() in config.editLayersBaseNames:
            title = "Delete Scenario Edits"
            text = "Do you want to delete, that is undo, "  + unicode(count) + \
" scenario edit(s)?  Please note that no changes will be made to any base layer."
        else:
            title = "Delete Selected Features"
            text = "Delete " + unicode(count) + " feature(s)?" 
        
        '''if sys.platform == 'win32':    
            # process name = qgis.exe
            for line in os.popen("TASKLIST"):
                fields  = line.split()
                imageName = fields[0]
                if imageName.find('qgis.exe') > 0:
                    text = "File Warning: Please make sure that " + vfileName + " is not open \
            in the QGIS program before you click OK!\n Delete " + unicode(count) + " feature(s)?"
                else: text = "Delete " + unicode(count) + " feature(s)?"'''
            
        # Now check with the user about deleting the features 
        reply = QtGui.QMessageBox.question(self, title, text, QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Ok)
        if reply == QtGui.QMessageBox.Ok:
            # make a Python list of features to delete
            pyList = []
            feat = QgsFeature()
            for feat in selectedFeats:
                print "starting ids of deleted features " + str(feat.id())
                pyList.append(feat.id())

            # provider.deleteFeatures only works with a Python list as a parameter.  
            # Note that the spaces between the list brackets and parentheses
            # are necessary or it doesn't work!! We delete and check for error 
            # in the same if statement
            if not self.provider.deleteFeatures( pyList ): # returns false on failed deletion
                QtGui.QMessageBox.warning(self, "Failed to delete features", 
                                            "Please check if " + vfileName + 
                                            " is open in another program and then try again.")
                # delete failed so
                return
            # features successfully deleted so reset the original features count for the layer
            self.originalFeats = shared.listOriginalFeatures(self.provider)
            # if this is an editing layer, reset the id numbers for the layer
            if self.activeVLayer.name() in config.editLayersBaseNames:
                shared.resetIdNumbers(self.provider, self.geom)
            # empty the selections cache when done or it stays at 'count'
            self.activeVLayer.removeSelection(False) # false indicates whether to emit a signal
            # reset the select tool
            self.disableSelectActions()
            # update all the extents
            shared.updateExtents(self, self.provider, self.activeVLayer, self.canvas)
            # update Vector Attribute Table if open
            if self.attrTable != None and self.attrTable.isVisible():
                self.openVectorAttributeTable()
         
    def pasteFeatures(self, modifyFlag=False):
        ''' Pasting features can only be done in "Edit Scenario" mode.  Features can be copied
            from any file, but can only be pasted into an editing shapefile.
        ''' 
        # debugging
        print "mainwindow.pasteFeatures()"
        print "copied feat count = " + str(self.copiedFeatCount)
        print "copied feat geometry " + str(self.copiedFeatGeom)
        print "self.geom is " + str(self.geom)
        print "modifyFlag"
  
        ''' CHECK FOR USER ERROR AND SET INTIAL CONDITIONS '''
 
        # check if user has chosen the correct editing shapefile to paste to
        vlayerName = self.activeVLayer.name()
        if shared.checkSelectedLayer(self, self.scenarioType, vlayerName) == "Cancel":
                return
 
        # Inform user if attempting to paste into incompatible layer type. This can happen if the user
        #  copies features from a layer with different geometry than the current edit scenario type.
        copyGeom = self.getGeometryName(self.copiedFeatGeom)
        activeGeom = self.getGeometryName(self.geom) #0 point, 1 line, 2 polygon
        if self.geom != None:
            if self.geom != self.copiedFeatGeom:  
                title = "Paste Features"
                text = "You cannot paste " + copyGeom + " into a " + activeGeom + " vector layer."
                QtGui.QMessageBox.information(self, title, text, QtGui.QMessageBox.Ok)
                return
 
        # Now that we have a correct layer to paste to:
        # Set self.originalFeats in case the user wants to delete pasted features
        # The self.originalFeats list is only set when the AddPoints or AddLinesPolygons
        # tools are initiated, at the end of self.deleteFeatures(), and when self.saveEdits is called.
        # In other words, self.originalFeats is set before the features in a layer might change,
        # and after the user has accepted feature changes to a layer.
        # The AddPoints or AddLinesPolygons tools are initiated whenever an edit action
        # is selected (i.e edit points, lines or polygons).  
        self.originalFeats = shared.listOriginalFeatures(self.provider)
        
        ''' 
            PASTE THE FEATURES WITH EMPTY ATTRIBUTE DATA SO THEY CAN BE SELECTED ON THE 
            MAP CANVAS WHEN THE USER INPUTS NEW DATA FOR EACH FEATURE.    
        '''
     
        # Get the list of editing shapefile fields for the current scenario edit type.
        editFields = self.getEditFields()
        
        # Create an attribute map (a python dictionary) of empty values
        # for the current editing shapefile.
        keys = range(len(editFields))
        values = [QtCore.QVariant()]*len(editFields)
        attributes = dict(zip(keys, values))
       
        # Set the attributes of the features to empty and paste.
        # Pasting features with empty attributes allows us to select each 
        # feature on the map canvas when the user inputs data for that feature.                 
        feat = QgsFeature()
        for feat in self.copiedFeats:
            feat.setAttributeMap(attributes)
            try:
                self.provider.addFeatures( [feat] )
            except (IOError, OSError), e:
                error = unicode(e)
                print error                    
                QtGui.QMessageBox.warning(self, "Failed to paste feature(s)", "Please check if "
                            + vlayerName + " is open in another program and then try again.")
    
        # update extents and refresh to show feature(s)
        #shared.updateExtents(self, self.provider, self.activeVLayer, self.canvas)
           
        # The provider gives the pasted features new id's when they are added
        # to the editing shapefile.  Here we use the same method as we use
        # to get deleted feature ids to get the pasted feature ids after pasting.
        # pastedFeatureIDS is a python list.
        pastedFeatureIDS = shared.getFeatsToDelete(self.provider, self.originalFeats)        # now get the difference
          
        # debugging
        print "The empty attributes are:"
        print attributes
        print "The pasteFeatureIDS[] are:"
        print pastedFeatureIDS
         
        '''  
            WE NEED TO ITERATE THROUGH THE PASTED FEATURES, SELECT EACH ONE
            ON THE MAP CANVAS(FOR THE USER'S CONVENIENCE), OPEN THE "ADD ATTRIBUTES" DIALOG
            AND GET THE USER INPUT DATA FOR EACH FEATURE. 
        '''

        reply = None
        for id in pastedFeatureIDS:
            print "feat.id is " + str(id)
            #select the feature
            self.activeVLayer.setSelectedFeatures( [id] )
            self.canvas.zoomToSelected(self.activeVLayer)
            self.canvas.refresh()
            self.dlg = DlgAddAttributes(self)
            self.dlg.setGeometry(0, 500, 200, 200)
            if self.dlg.exec_(): # open the dialog and then if user clicks OK returns true
                # validate user input
                if modifyFlag: attributes = self.dlg.getNewAttributes(True)
                else: attributes = self.dlg.getNewAttributes()
                changedAttributes = {id : attributes} # create a "QgsChangedAttributesMap"
                try:
                    self.provider.changeAttributeValues(changedAttributes)
                except (IOError, OSError), e:
                    error = unicode(e)
                    print error 
                    if modifyFlag: title = "Failed to modify feature(s)"
                    else: title = "Failed to delete feature(s)"
                    vlayerName = self.activeVLayer.name()    
                    QtGui.QMessageBox.warning(self, title, "Please check if "
                                + vlayerName + " is open in another program and then try again.")
                self.activeVLayer.removeSelection(False) # false means do not emit signal
                self.canvas.refresh()
                continue
            else: #if user clicks "Cancel"
                if modifyFlag:
                    title = "Modify Features Warning"
                    text = "If you click 'Yes' in this dialog, any modifications you have made \
will be lost. If you still want to modify features, you will will need to start over. Do you \
want to stop modifying features?"
                else:
                    title = "Paste Features Warning"
                    text = "If you click 'Yes' in this dialog, any features you have pasted \
will be lost. If you still want to paste features, you will will need to start over. Do you \
want to stop pasting?"
                reply = QtGui.QMessageBox.warning(self, title, text, 
                                                    QtGui.QMessageBox.No|QtGui.QMessageBox.Yes)
                if reply == QtGui.QMessageBox.Yes: # if reply is no, self.dlg remains active
                    # reverse the edits
                    shared.deleteEdits(self, self.provider, self.activeVLayer, 
                                                        self.canvas, self.originalFeats)
                    # Nothing has been pasted/changed so just do housekeeping and return
                    self.copiedFeats = None
                    self.copyFlag = False
                    if modifyFlag: self.mpActionModifyPoints.setDisabled(True)
                    else: self.mpActionPasteFeatures.setDisabled(True)
                    #self.mpAction
                    return 
 
        '''PASTING COMPLETED, SO NOW WE DO SOME HOUSEKEEPING '''
        
        # Note that when features are deleted, the id numbers can become inconsistent.
        # Also we could have the same id number in different editing layers.
        # So, reset the id values.
        shared.resetIdNumbers(self.provider, self.geom)
        
        # Set the editDirty flag.  Note that shared.listOriginalFeatures()
        # will be called when the edits (i.e. pasted features) are saved, so 
        # we don't need to do that here.
        self.editDirty = self.activeVLayer.name()
        
        # enable the save edits button
        self.mpActionSaveEdits.setDisabled(False)    
        
        
        # reset the copy flag
        self.copiedFeats = None
        self.copiedFeatGeom = None
        self.copyFlag = False
        
        # the paste action is turned on in copyFeatures
        # it is turned off here.
        self.mpActionPasteFeatures.setDisabled(True)
        
        # update Vector Attribute Table if open
        if self.attrTable != None and self.attrTable.isVisible():
            self.openVectorAttributeTable()
            
        # update all the extents and refresh to show feature
        shared.updateExtents(self, self.provider, self.activeVLayer, self.canvas)
            
    def editScenario(self, state):
        # debugging
        print "editScenario() " + str(state)

        if state: # True if action activated
            # handle user cancel
            if self.appStateChanged("startingEditing") == "Cancel":
                self.mpActionEditScenario.blockSignals(True)
                self.mpActionEditScenario.setChecked(False)
                self.mpActionEditScenario.blockSignals(False)
                return
            
            # We cannot make edits unless there is a named 
            # scenario open.  Check for open scenario here.
            if not self.scenarioFileName:
                QtGui.QMessageBox.warning(self, "Scenario Editing Error", "The scenario must have a name \
before you can make edits.  Please save the current scenario or open an existing scenario.")
                self.mpActionEditScenario.blockSignals(True)
                self.mpActionEditScenario.setChecked(False)
                self.mpActionEditScenario.blockSignals(False)
                return
            
            # set the edit flag
            self.editMode = True
            
            # set the select action for edit mode
            self.mpActionSelectFeatures.setDisabled(False)

            # set the paste action
            if self.copyFlag:
                self.mpActionPasteFeatures.setDisabled(False)
                 
            # call the dialog to get the scenario change type
            self.scenarioTypes = DlgScenarioTypes(self)
            self.scenarioTypes.exec_()
                
        else: #False action deactivated
            # check for unsaved edits when deselecting "Edit Scenario"
            # return mpActionEditScenario to previous state on cancel
            if self.appStateChanged("stoppingEditing") == "Cancel":
                self.mpActionEditScenario.blockSignals(True)
                self.mpActionEditScenario.setChecked(True)
                self.mpActionEditScenario.blockSignals(False)
                return
            self.editMode = False
            
            # unset the select tool
            self.mpActionSelectFeatures.setDisabled(True)
            self.disableSelectActions()
            
            # unset the paste action (only active in edit mode)
            self.mpActionPasteFeatures.setDisabled(True)
            # unset edit tool actions
            self.disableEditActions()
            print "setDisabled = True"
            
    
    
    def addPoints(self, state):
        # debugging
        print "addPoints() " + str(state)
        
        if state:
            self.canvas.setMapTool(self.toolAddPoints)
        else:
            self.canvas.unsetMapTool(self.toolAddPoints)
     
    def addLines(self, state):
        # debugging
        print "addLines()"
        if state:
            self.canvas.setMapTool(self.toolAddLinesPolygons)
        else: 
            self.canvas.unsetMapTool(self.toolAddLinesPolygons)
            
    def addPolygons(self, state):
        # debugging
        print "addPolygons()"
        
        self.addLines(state)
        
    def saveEdits(self, isSignal=True):
        # debugging
        print "saveEdits()"
        print "self.scenarioDirty begin is " + str(self.scenarioDirty)
        print "self.editDirty begin is " + str(self.editDirty)
        
        # The editing tools save the edits to disk as they are made. So, to delete
        # new features, we list the original features when editing starts and delete
        # any feature not in the list.  To save features, we just run listOriginalFeatures
        # again.
        self.originalFeats = shared.listOriginalFeatures(self.provider)
             
        # This gives a save message only if the user clicks the Save Edits action
        # or if there are no edtis to save.
        title = "Save Edits"
        if isSignal and self.editDirty:
            text = "Your edits have been saved!"
            # give user feedback 
            QtGui.QMessageBox.information(self, title, text, QtGui.QMessageBox.Ok)
        elif not self.editDirty: 
            text = "You have not made any edits to save!"
            QtGui.QMessageBox.information(self, title, text, QtGui.QMessageBox.Ok)

        self.scenarioDirty = True
        self.editDirty = False    
            
############################################################################################  
    ''' VIEW MENU SLOTS '''
############################################################################################   
    
    def zoomIn(self, state):
        print "zoomIn() " + str(state)
        
        if state:
            self.canvas.setMapTool(self.toolZoomIn)
        else: self.canvas.unsetMapTool(self.toolZoomIn)    

    def zoomOut(self, state):
        print "zoomOut() "  + str(state)
        
        if state:
            self.canvas.setMapTool(self.toolZoomOut)
        else: self.canvas.unsetMapTool(self.toolZoomOut)
                    
    def pan(self, state):
        print "pan " + str(state)
        
        if state:
            self.canvas.setMapTool(self.toolPan)
        else: self.canvas.unsetMapTool(self.toolPan)
 
    def zoomToMapExtent(self):
        """ set zoom to full extent """
        # debugging
        print "zoomToMapExtent()"
        
        extent = self.canvas.fullExtent()
        # without this some of the layer is off the canvas
        extent.scale(1.05)
        self.canvas.setExtent(extent)
        self.canvas.refresh()
        
        #self.setExtents()
        
    def identifyFeatures(self, state):
        # debugging
        print "mainwindow.identifyFeatures()"
        
        if state: # for action selected state = True
            print "mainwindow.identifyFeatures() state is True"
            # identifyFeatures action is selected so enable this tool
            self.canvas.setMapTool(self.toolIdentify)
        else: # action deselected (state = False)
            print "mainwindow.identifyFeatures() state is false"
            self.canvas.unsetMapTool(self.toolIdentify)
       
############################################################################################  
    ''' LAYER MENU CUSTOM SLOTS '''
############################################################################################
               
    def addVectorLayer(self):
        # check app state and handle user cancel
        if self.appStateChanged("addVector") == "Cancel":
            # debugging
            print "canceling addVectorLayer()"
            return
        # open the file dialog
        qd = QtGui.QFileDialog()
        filterString = QtCore.QString("ESRI Shapefile(*.shp *.SHP)\nComma Separated Value\
(*.csv *.CSV)\nGeography Markup Language(*.gml *.GML)\nGPX(*.gpx *.GPX)\nKML(*.kml *.KML)\
SQLite(*.sqlite *.SQLITE)\nArc\\Info ASCII Coverage(*.e00 *.E00)\nAll Files(*)")
        # get the path to the directory containing the opened file using Python
        dir = config.baseLayersPath
                                
        # change the QString to unicode so that Python can slice it for the directory name 
        vfilePath = unicode(qd.getOpenFileName(self, QtCore.QString("Add Vector Layer"),
                                            dir, filterString))
        # Check for cancel
        if len(vfilePath) == 0:
            return
        
        self.openVectorLayer(vfilePath)
            
    def addRasterLayer(self):
        # check app state and handle user cancel
        if self.appStateChanged("addRaster") == "Cancel":
            return
        # open file dialog
        qd = QtGui.QFileDialog()
        filterString = QtCore.QString("All Files(*)\nMrSID(*.sid *.SID)\nGeoTIFF\
(*.tif *.tiff *.TIF *.TIFF)\nArc/Info Binary Grid(*.adf *.ADF)\n\
JPEG(*.jpg *.jpeg *.JPG *.JPEG)")
        # get the path to the directory containing the opened file using Python
        dir = config.baseLayersPath        
        
        # change QString to unicode so Python can slice it for the directory name
        rfilePath = unicode(qd.getOpenFileName(self, QtCore.QString("Add Raster Layer"),
                                    dir, filterString))
        # Check for cancel
        if len(rfilePath) == 0:
            return
        
        #create the layer
        self.openRasterLayer(rfilePath)
          
    def openRasterCategoryTable(self):
        # Raster Categories file kept in the Base_layers folder
        fname = QtCore.QString("./RasterCategoryTable.htm")
        
        # use a QDockWidget to create floating window 
        # with the MainWindow as parent 
        self.dwRasterTable = QtGui.QDockWidget("Raster Category Tables", self)
        
        # create a QTextBrowser to display the file
        # *Note: using QTextBrowser alone
        # results in an orphaned window that the app does not close
        self.browserRaster = QtGui.QTextBrowser()
        
        # Open the file and create a text stream to read
        fh = QtCore.QFile(fname)
        if not fh.open(QtCore.QIODevice.ReadOnly):
                raise IOError, unicode(fh.errorString())
        stream = QtCore.QTextStream(fh)
        
        # Show the QDockWidget and make it a separate floating window
        self.dwRasterTable.show()
        self.dwRasterTable.setFloating(True)
        self.dwRasterTable.setMinimumSize(QtCore.QSize(800, 600))
        
        # add the QTextBrowser to the QDockWidget
        self.dwRasterTable.setWidget(self.browserRaster)
        
        # display the html file in the browser
        self.browserRaster.setHtml(stream.readAll())
        self.browserRaster.setFontPointSize(20.0)
        #self.browser.setSizePolicy()
        
    def openVectorAttributeTable(self):
        # debugging
        print "openVectorAttributeTable()"
        print "openVectorAttributeTable() type is " + str(type(self.dwAttrTable))
        
        if self.activeVLayer.name() == config.slowLoadingLayers[0]:
            reply = QtGui.QMessageBox.question(self, "Vector Attribute Table", "This layer's \
attribute table is very large and can take a few seconds to load.  Do you want to continue?", 
                                                    QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.Cancel:
                return
        
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
        while self.provider.nextFeature(feat): 
            # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
            attrs = feat.attributeMap()
            row = feat.id()
            for k, attr in attrs.iteritems():
                column = k     
                item = QtGui.QTableWidgetItem(attr.toString())
                self.attrTable.setItem(row, column, item)    
        
        self.attrTable.resizeColumnsToContents()
        self.attrTable.setMinimumSize(QtCore.QSize(400,250))
        #self.attrTable.adjustSize()
        
        
        # Show the QDockWidget and make it a separate floating window
        # (Need a dock widget to handle separate window properly)
        # if it is already open don't open another window
        if self.dwAttrTable == None:  
            # debugging
            print "dwAttrTable not open"
            self.dwAttrTable = QtGui.QDockWidget("Vector Attribute Table", self)
            self.dwAttrTable.show()
            self.dwAttrTable.setFloating(True)
            self.dwAttrTable.setMinimumSize(QtCore.QSize(400,250))
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
        ''' A controller for handling app state changes from the legend '''

        #**************************************************************************     
        ''' Debugging Code '''
        print "ALC() STARTING"
        print "alc layer type is " + str(layerType)
        if not self.activeVLayer: 
            print "alc no active vlayer"
        else: print "alc old active vlayer " + self.activeVLayer.name()
        if self.activeRLayer == None:
            print "alc no active rlayer"
        else: print "alc old active rlayer " + self.activeRLayer.name()
        print "self.editMode is " + str(self.editMode)
        print "self.editDirty is " + str(self.editDirty)
        print "self.scenarioDirty is " + str(self.scenarioDirty)
        
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
            # ensure that the canvas always shows Mass State Plane coordinates
            self.activeRLayer.setCrs(config.crs)
            # set extents
            self.setExtents()
            # set the layer geometry
            self.geom = None
            self.provider = None
            # set extents if not within MA state extents
            #self.setExtents()
  
            # debugging
            print "alc opened active layer is " + self.activeRLayer.name()
            print "alc self.editDirty is " + str(self.editDirty)
            
            # Start with all tool group actions enabled 
            # and then disable as necessary
            self.toolGroup.setEnabled(True)
            # Disable (gray out) select tool actions
            # if raster layer loaded.
            self.mpActionSelectFeatures.setDisabled(True)
            self.disableSelectActions()
            # can't paste features to a raster so disable paste action
            self.mpActionPasteFeatures.setDisabled(True)
            # edit scenario should always be on
            self.mpActionEditScenario.setDisabled(False)
            # disable edit actions except if self.editsDirty enable save edits
            self.disableEditActions()
            if self.editDirty:
                self.mpActionSaveEdits.setDisabled(False)
            # disable the vector attribute table action
            self.mpActionOpenVectorAttributeTable.setDisabled(True)
            
            # New layer loaded so set the scenarioDirty flag.  Note: This gets called
            # unnecessarily when a different layer is selected in the layer panel.
            # However, it returns immediately if the layer count has not changed.
            # It also returns immediately if a scenario is in the process of loading
            # There is no need to check if the scenario is already dirty.  Once a scenario
            # is dirty, the policy is it stays dirty until the user saves it.
            if not self.scenarioDirty:
                self.setScenarioDirty()
            
            # if there could be something to export
            if self.scenarioDirty or self.scenarioFilePath:
                self.mpActionExportScenario.setDisabled(False)
            
            # debugging
            print "alc self.scenarioDirty is " + str(self.scenarioDirty)
            print "alc originalScenarioLayers are "
            for layer in self.originalScenarioLayers: print layer.name()
            print "alc currentLayers are "
            for layer in self.getCurrentLayers().values(): print layer.name()
      
        elif layerType == 0: #vector
            # debugging
            print "alc Setting app state for vector layer" 
            print "copyFlag is " + str(self.copyFlag)
            
            # ensure that the canvas always shows Mass State Plane coordinates
            #self.activeVLayer.setCrs(config.crs)

            # set the active vector layer
            self.activeVLayer = self.legend.activeLayer().layer()
            # set the geometry of the layer
            self.geom = self.activeVLayer.geometryType() #0 point, 1 line, 2 polygon
            # set extents if not within MA state extents
            self.setExtents()
            # set the data provider
            self.provider = self.activeVLayer.dataProvider()
            
            # The V2 renderers get the selection color from the old renderer.
            # This sets the selection color for the layer only on the first vector 
            # layer load before we replace the old renderer with the V2 renderers. 
            # (i.e setRendererV2(rendererV2)
            
            
            
            # set the rendererV2 if it is not already set (i.e. layer loaded for the first time)
            if not self.activeVLayer.rendererV2(): self.setRendererV2()
            
            # refresh attribute table if open
            if self.attrTable != None and self.attrTable.isVisible():
                self.openVectorAttributeTable()

            '''
            A New Vector layer has been selected or opened, so set action states.
            '''
            
            # Enable map navigation tools, select tools, edit 
            # tools, andcopy, delete, paste features
            self.toolGroup.setEnabled(True)
            
            # if self.editDirty is True, the save edits action should be enabled
            if self.editDirty:
                self.mpActionSaveEdits.setDisabled(False)
            else: self.mpActionSaveEdits.setDisabled(True)
            
            # Manage the Edit Scenario action. 
            # note: "Edit Scenario" is not part of self.toolGroup
            # The Edit Scenario action is always on!
            self.mpActionEditScenario.setDisabled(False)
            if self.editMode:
                self.mpActionEditScenario.setChecked(True)
                # new active layer loading so disable previous edit actions
                self.disableEditActions()
                # loading a new active layer so enable the proper edit buttons
                self.enablePointsOrLinesOrPolygons()
            else: # not in edit mode
                self.mpActionEditScenario.setChecked(False)
                # gray out edit sub actions until user starts editing
                self.disableEditActions()
            
            # enable the  "Open Vector Attribute Table" action    
            self.mpActionOpenVectorAttributeTable.setDisabled(False)
            
            # We are changing the activeVLayer, so we need to set select actions
            if self.editMode and self.mpActionSelectFeatures.isChecked():
                # So the user has checked Select Features. Leave select features activated
                # Note that "Modify Selected" will only be enabled if the active layer
                # is one of the point base layers
                self.mpActionSelectFeatures.setDisabled(False)
                self.mpActionSelectFeatures.setChecked(True)
                self.enableSelectSubActions()
            elif self.editMode and len(self.activeVLayer.selectedFeatures()) != 0:
                # We have selected features, so enable all the selected features actions
                # Note that "Modify Selected" will only be enabled if the active layer
                # is an editable point base layer.
                self.mpActionSelectFeatures.setDisabled(False)
                self.mpActionSelectFeatures.setChecked(True)
                self.enableSelectSubActions()
            # If in editMode, make sure the select action is enabled, but not selected.
            elif self.editMode: # enable select features but disable sub actions
                self.mpActionSelectFeatures.setDisabled(False)
                self.disableSelectActions()
            else: # not in edit mode so disable "Select Features"
                self.mpActionSelectFeatures.setDisabled(True)
                self.disableSelectActions()
                
            # handle the copy action
            if self.copyFlag and self.editMode:
                self.mpActionPasteFeatures.setDisabled(False)
            else: self.mpActionPasteFeatures.setDisabled(True)
        
            # New layer loaded so set the scenarioDirty flag.  Note: This gets called
            # unnecessarily when a different layer is selected in the layer panel.
            # However, it returns immediately if the layer count has not changed. 
            # There is no need to check if the scenario is already dirty.  Once a scenario
            # is dirty, the policy is it stays dirty until the user saves it.
            if not self.scenarioDirty:
                self.setScenarioDirty()
            
            # if there could be something to export
            if self.scenarioDirty or self.scenarioFilePath:
                self.mpActionExportScenario.setDisabled(False)
                
            # debugging
            print "alc self.scenarioDirty is " + str(self.scenarioDirty)
            print "alc originalScenarioLayers are "
            for layer in self.originalScenarioLayers: print layer.name()
            print "alc currentLayers are "
            for layer in self.getCurrentLayers().values(): print layer.name()
                       
        # debugging
        else: print "Geometry type unknown"
        
    def closeEvent(self, event):
        ''' Slot to handle signal emitted when user exits app '''

        if self.appStateChanged("appClosing") == "Cancel":
            event.ignore()

############################################################################################   
    ''' METHODS TO MANAGE APPLICATION STATE CHANGES '''
############################################################################################
    
    def appStateChanged(self, callingAction):
        ''' Manage the application state changes from all user actions '''
        # If no layer is loaded then user is loading first layer after app start (num layers = 0),
        # or loading first layer after deleting the only layer in the legend (num layers = 0).
        # If there are no layers in the scenario, no need to scave the scenario or edits.
        if len(self.legend.getLayerIDs()) == 0: 
            return
        
        # If user in the middle of a line or polygon edit, warn
        if self.toolAddLinesPolygons and self.toolAddLinesPolygons.started:
            QtGui.QMessageBox.warning(self, "Editing Error", "Please complete your edit \
before taking another action!")
            return "Cancel" 
        
        #**********************************************************       
        ''' Debug code '''
        print "APP_STATE_CHANGED() STARTING: callingAction is " + callingAction
        if self.activeVLayer == None: 
            print "asc no active vlayer"
        else: print "asc current active " + self.activeVLayer.name()
        if self.activeRLayer == None:
            print "asc no active rlayer"
        else: print "asc current active rlayer " + self.activeRLayer.name()
        print "asc num layers " + str(len(self.legend.getLayerIDs()))
        print "asc registry count " + str(QgsMapLayerRegistry.instance().count())
        print "asc the layer type is " + str(self.layerType)
        print "asc self.editDirty is " + str(self.editDirty)
        print "asc self.editMode = " + str(self.editMode)
        print "asc self.scenarioDirty is " + str(self.scenarioDirty)
        print "asc scenarioFilePath " + str(self.scenarioFilePath) 
        #******************************************************************
 
        ''' 
        On any other user action, check for unsaved scenarios and unsaved edits.
        
        Actions that call this method are: addVector, addRaster, removeCurrentLayer, 
        legendMousePress, startingEditing, stoppingEditing, appClosing, newScenario, 
        openScenario, saveScenario, saveScenarioAs, exportScenario
        
        '''
  
        # Changing layers (legendMousePress, removeCurrentLayer, addVector, addRaster)
        # requires editing tools to be reset, so it is wise to check for unsaved edits
        # on those actions. Also we should check for unsaved edits when starting/stopping 
        # editing, on all scenario menu actions, or on closing the app.  In other words
        # we check for unsaved edits on all callingActions, but that behavior can be changed here. 
        if self.editDirty:
            if self.chkEditsState(callingAction) == "Cancel":
                return "Cancel"
         
        # We only want to check for a dirty scenario when:
        # creating a new scenario, opening a scenario, 
        # exporting a scenario, or closing the app.
        list = ["newScenario", "openScenario", "exportScenario", "appClosing"]
        if self.scenarioDirty:
            if callingAction in list:
                if self.chkScenarioState(callingAction) == "Cancel":
                    return "Cancel"                
        
        # If there were no unsaved edits or scenarios that handled 
        # removal of the last layer in legend, then handle it here.    
        if callingAction == "removeCurrentLayer" and len(self.legend.getLayerIDs()) == 1:
            # Layer has been loaded previously so user deleting only layer in legend
            print "asc set app to initial state"
            self.setInitialAppState()
            return
        
        # debugging
        print "appStateChanged has returned nothing"

    def chkEditsState(self, callingAction):
        ''' Prompt the user about unsaved edits '''
        # debugging
        print "chkEditsState()"
        
        # Prompt the user about clearing selections/edits
        # and deactivate the action if necessary.
        title = "Save Edits"
        text = "Do you want to save your edits to " + unicode(self.editDirty) + "?"
        list = ["saveScenario", "saveScenarioAs", "selectFeatures", 
                    "deleteFeatures", "removeCurrentLayer"]
        # Once in edit mode, it is impossible to exit edit mode, or do anything else, without
        # either saving or discarding changes. So, this dialog is only called when in edit mode.
        reply = QtGui.QMessageBox.question(self, title, text, 
                QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Save|QtGui.QMessageBox.Discard )
        if reply == QtGui.QMessageBox.Save:
            # debugging
            print "msgBoxSaveDiscardCancel = Save"
            if callingAction == "removeCurrentLayer" and len(self.legend.getLayerIDs()) == 1:
                # A layer has been loaded previously so user deleting only layer in legend
                print "asc set app to initial state"
                self.saveEdits(False)
                self.setInitialAppState()
            # No need to change editing state if saving the scenario, selecting features
            # deleting features, or removing a layer.  Note that a user is warned about
            # deleting a base layer or an editing layer in legend.removeCurrentLayer.
            # If user deletes one of their own layers, there is no need to disable editing
            elif callingAction in list:
                self.saveEdits(False)
            # if opening new layer or changing layers just disable edit actions
            elif callingAction == "addVector" or "addRaster" or "legendMousePress":
                self.saveEdits(False)
                self.disableEditActions()
            else:
                # opening new scenario, exporting scenario or closing app
                # save the edits and disable "Edit Scenario" mode
                self.saveEdits(False)
                self.disableEditing()                
        elif reply == QtGui.QMessageBox.Discard:
            # debugging
            print "msgBoxYesDiscardCancel = Discard"
            # so handle as above but discard edits 
            if callingAction == "removeCurrentLayer" and len(self.legend.getLayerIDs()) == 1:
                # A layer has been loaded previously so user deleting only layer in legend
                shared.deleteEdits(self, self.provider, self.activeVLayer, 
                                                            self.canvas, self.originalFeats)
                if self.attrTable != None and self.attrTable.isVisible():
                    self.openVectorAttributeTable()
                self.mainwindow.editDirty = False
                print "asc set app to initial state"
                self.setInitialAppState()
            # under these situation just discard edits and leave editing state as is
            elif callingAction in list:
                shared.deleteEdits(self, self.provider, self.activeVLayer, 
                                                    self.canvas, self.originalFeats)
                if self.attrTable != None and self.attrTable.isVisible():
                    self.openVectorAttributeTable()
                self.mainwindow.editDirty = False
            # if opening new layer or changing layers just disable edit actions
            elif callingAction == ("addVector" or "addRaster" or 
                                    "legendMousePress"):
                shared.deleteEdits(self, self.provider, self.activeVLayer, 
                                                    self.canvas, self.originalFeats)
                if self.attrTable != None and self.attrTable.isVisible():
                    self.openVectorAttributeTable()
                self.mainwindow.editDirty = False
                self.disableEditActions()
            # if opening new scenario, exporting scenario or closing the app
            # discard the edits and disable editing mode
            else:
                shared.deleteEdits(self, self.provider, self.activeVLayer, 
                                                    self.canvas, self.originalFeats)
                self.disableEditing()
        elif reply == QtGui.QMessageBox.Cancel:
            if callingAction == "stoppingEditing" and self.editMode:
                    self.mpActionEditScenario.blockSignals(True)
                    self.mpActionEditScenario.setChecked(True)
                    self.mpActionEditScenario.blockSignals(False) 
            print "chkEditsState() returning cancel"
            return "Cancel"
        
    def chkScenarioState(self, callingAction):
        ''' Prompt the user about unsaved scenario changes '''
        # debugging
        print "chkScenarioState()"
        
        # Prompt the user about a dirty scenario.
        # Note that qgis handles the dirty flag for scenarios 
        title = "Save Scenario"
        text = "Do you want to save the current scenario?"

        reply = QtGui.QMessageBox.question(self, title, text, 
                QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Save|QtGui.QMessageBox.Discard )
        if reply == QtGui.QMessageBox.Save:
            # debugging
            print "msgBoxSaveDiscardCancel = Save"
            if self.scenarioFilePath:
                self.saveScenario()
            elif self.saveScenarioAs() == "Cancel":
                return "Cancel"
        elif reply == QtGui.QMessageBox.Discard:
            # debugging
            print "msgBoxYesDiscardCancel = Discard"
            # If the user wants to close a scenario without saving it, we need to check
            # for unsaved editing layers.  If an editing layer is open, and the user doesn't
            # save the scenario, then that editing layer will not appear if the scenario is 
            # reopened.  However, it will remain in the scenario's folder where it will be read
            # for an export.  This would certainly  lead to erroneous scenario exports!!
            # Self.currentLayers returns a dictionary of open layers.
            # We check this for differences with the layers saved in the scenario.
            differences = [layer for layer in self.currentLayers.values() if layer not in 
                                                                self.originalScenarioLayers]
            print "These are the differences:"
            for layer in differences: print  layer.name()
            for layer in differences:
                if layer.name() in config.editLayersBaseNames:
                    editFilePath = layer.source()
                    layerID = layer.id()
                    # need to remove layer from registry before delete.
                    self.legend.removeEditLayerFromRegistry(layer, layerID)
                    if not self.legend.deleteEditingLayer(editFilePath):
                        # Warn and return
                        QtGui.QMessageBox.warning(self, "Deletion Error:", "Caps Scenario Builder \
could not delete an editing layer that you have chosen not to save along with your scenario.  This \
editing layer will not appear when you reopen this scenario, but it could be mistakenly included if you \
choose 'Export Scenario' for this scenario in the future.")
                        return "Cancel"
        elif reply == QtGui.QMessageBox.Cancel:
            print "chkScenarioState() returning cancel"
            return "Cancel"
 
    def setInitialAppState(self):
        ''' Set the app state to be its first opened state '''
        # debugging
        print "setInitialAppState()"
        if self.toolSelect:
            self.canvas.unsetMapTool(self.toolSelect)
        if self.toolIdentify:
            self.canvas.unsetMapTool(self.toolIdentify)
        if self.toolAddPoints:
            self.canvas.unsetMapTool(self.toolAddPoints)
        if self.toolAddLinesPolygons:
            self.canvas.unsetMapTool(self.toolAddLinesPolygons)
        if self.dwAttrTable:
            self.dwAttrTable.close()
        if self.dwRasterTable:
            self.dwRasterTable.close()
        self.setWindowTitle("Conservation Assessment and \
Prioritization System (CAPS) Scenario Builder")
        self.scenarioFilePath = None
        self.scenarioInfo = None
        self.scenarioFileName = None
        self.scenarioDirty = False
        self.origScenarioLyrsLoaded = False
        self.originalScenarioLayers = []
        self.currentLayers = []
        self.currentLayersCount = None
        self.copiedFeats = []
        self.originalFeats = []
        self.scenarioType = None
        self.copyFlag = False
        self.exportFileFlag = False
        self.isBaseLayerDeletions = False
        self.editDirty = False
        self.editMode = False 
        self.attrTable = None
        self.dwAttrTable = None
        self.dwRasterTable = None
        self.activeVLayer = None
        self.activeRLayer = None
        self.layerType = None
        self.provider = None
        self.geom = None
        self.layerColor = None
        self.toolGroup.setDisabled(True)
        #self.canvas.setExtent(self.extent)
        self.mpActionOpenVectorAttributeTable.setDisabled(True)
        self.mpActionSaveEdits.setDisabled(True)
        self.mpActionEditScenario.setDisabled(False)
        self.mpActionEditScenario.setChecked(False)
        self.mpActionExportScenario.setDisabled(True)
        self.openOrientingLayers()

############################################################################################
    ''' UTILITY METHODS '''
############################################################################################
 
    def getGeometryName(self, layerGeom):
        geometry = "No Geometry"
        if layerGeom != None: # None if raster loaded
            if layerGeom == 0:
                geometry = "point(s)"
            elif layerGeom == 1:
                geometry = "line(s)"
            elif layerGeom == 2:
                geometry = "polygon(s)"
            else: geometry = "Unknown Geometry"
            return geometry
        
    def enablePointsOrLinesOrPolygons(self):
        if "base" in self.activeVLayer.name():
            return
        if self.geom == 0:  #0 point, 1 line, 2 polygon
            self.mpActionAddPoints.setDisabled(False)
            print "enablePointsOrLinesOrPolygons() geom 0" 
        elif self.geom == 1:
            self.mpActionAddLines.setDisabled(False)
            print "enablePointsOrLinesOrPolygons() geom 1"
        elif self.geom == 2:
            self.mpActionAddPolygons.setDisabled(False)
            print "enablePointsOrLinesOrPolygons() geom 2"

    def disableEditActions(self):
        # debugging
        print "disableEditActions()"
        
        self.mpActionAddPoints.setChecked(False)
        self.mpActionAddPoints.setDisabled(True)
        self.mpActionAddLines.setChecked(False)
        self.mpActionAddLines.setDisabled(True)
        self.mpActionAddPolygons.setChecked(False)
        self.mpActionAddPolygons.setDisabled(True)
        #self.mpActionSaveEdits.setDisabled(True)
        
    def disableSelectActions(self):
        # debugging
        print "disableSelectActions()"
        
        self.canvas.unsetMapTool(self.toolSelect)
        self.mpActionSelectFeatures.setChecked(False)
        self.mpActionDeselectFeatures.setDisabled(True)
        self.mpActionDeselectFeatures.setChecked(False)
        self.mpActionModifyPoints.setDisabled(True)
        self.mpActionModifyPoints.setChecked(False)
        self.mpActionDeleteFeatures.setDisabled(True)
        self.mpActionDeleteFeatures.setChecked(False)
        self.mpActionCopyFeatures.setDisabled(True)
        self.mpActionCopyFeatures.setChecked(False)
        
    def enableSelectSubActions(self):
        if self.activeVLayer.name() in config.pointBaseLayers:
            self.mpActionModifyPoints.setDisabled(False)
            self.mpActionCopyFeatures.setDisabled(True)
        else: self.mpActionCopyFeatures.setDisabled(False)
        self.mpActionDeselectFeatures.setDisabled(False)
        self.mpActionDeleteFeatures.setDisabled(False)
        
    def disableSelectSubActions(self):
        self.mpActionModifyPoints.setDisabled(True)
        self.mpActionDeselectFeatures.setDisabled(True)
        self.mpActionCopyFeatures.setDisabled(True)
        self.mpActionDeleteFeatures.setDisabled(True)
        
    def disableEditing(self):
        # We need to block the signals or we get a feedback loop
        # that toggles the edits on and off repeatedly.
        self.mpActionEditScenario.blockSignals(True)
        self.mpActionEditScenario.setChecked(False)
        self.disableEditActions()
        self.mpActionEditScenario.blockSignals(False)
        self.canvas.unsetMapTool(self.toolAddPoints)
        self.canvas.unsetMapTool(self.toolAddLinesPolygons)
        self.editMode = False
        
    def getCurrentLayersCount(self):
        # debugging
        print "getCurrentLayersCount()"
        
        self.currentLayersCount = None
        self.currentLayersCount = QgsMapLayerRegistry.instance().count()
        return self.currentLayersCount
 
    def getCurrentLayers(self):
        ''' Get the layers currently registered in the QgsMapLayerRegistry '''
        # debugging
        print "getCurrentLayers()"
        
        self.currentLayers = {}
        # note: returns a dictionary of QgsMapLayers
        self.currentLayers = QgsMapLayerRegistry.instance().mapLayers()
        return self.currentLayers
        
    def getCurrentLayersNames(self):
        # debugging
        print "getCurrentLayersNames()"
        
        self.currentLayersNames = []
        for layer in self.getCurrentLayers().values():
            self.currentLayersNames.append(layer.name())
            
        print "self.currentLayersNames are "
        for name in self.currentLayersNames: print name
     
    def getOriginalScenarioLayers(self, i, count):                  
        ''' This method is called when a scenario is loaded.  The call
            originates each time QgsProject emits a "layerLoaded" signal
        '''
        # debugging
        print "Main.mainwindow.getOriginalScenarioLayers()"
        print "int begin " + str(i)
        print "count " + str(count)
    
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
            self.origScenarioLyrsLoaded = True
            # inform user of missing layers
            if len(self.originalScenarioLayers) < count:
                QtGui.QMessageBox.warning(self, "File Error", "Some layers in the scenario have \
failed to load. Either the file name or the location of the file has probably changed. You may reload \
missing files by using the 'Add Vector Layer' or 'Add Raster Layer buttons.'")
   
        # debugging
        print "getOriginalScenarioLayers() originalScenarioLayers are " 
        for layer in self.originalScenarioLayers: print layer.name()
        print "getOriginalScenarioLayers() currentLayers are " 
        for layer in self.getCurrentLayers().values(): print layer.name()
   
    def setScenarioDirty(self):
        ''' Set the scenarioDirty flag '''
        # debugging
        print "setScenarioDirty()"
        print "self.origScenarioLyrsLoaded is " + str(self.origScenarioLyrsLoaded)
        print "self.scenarioDirty begin is " + str(self.scenarioDirty)
        print "self.scenarioFileName is " + str(self.scenarioFileName)
        
        # The line below fails because it returns false if the layer order changes
        # self.originalScenarioLayers == self.currentLayers.values()

        self.getCurrentLayersCount()
        print "self.currentLayersCount is " + str(self.currentLayersCount)
        
        # If no scenario is open and the loaded layers are the orienting baselayers,
        # The user is probably either opening the app or has chosen "New Scenario." 
        # We don't want the scenario to be dirty because the user will get prompted
        # to save the current scenario if she wants to open a scenario or if she closes the app.
        # Under these conditions, the user will only be prompted to save the scenario when the 
        # "Edit Scenario" function is checked. 
        if self.currentLayersCount == len(config.allOrientingLayers) and self.scenarioFileName == None:
            print "Entered "
            orientingLayerNames = []
            for fileName in config.allOrientingLayers:
                info = QtCore.QFileInfo(fileName)  
                name = info.completeBaseName()
                orientingLayerNames.append(name)
            legendLayerNames = []
            # legendLayers are QgsMapCanvasLayers
            legendLayers = self.legend.getLayerSet()
            for layer in legendLayers: legendLayerNames.append(layer.layer().name())
            print "orientingLayerNames are"
            for name in orientingLayerNames: print name.toUtf8()  
            print "legendLayerNames are "
            for name in legendLayerNames: print name.toUtf8()
            difference = [name for name in orientingLayerNames if name not in legendLayerNames]
            print "difference is"
            print difference
            if difference == []:
                self.scenarioDirty = False
                print "setScenarioDirty() return"
                return
 
        
        # If some layer is opened when the layer count is other than 5 and there is no scenario 
        # loaded then the scenario is dirty. This would and should be true even
        # if the user removed all the intially loaded layers and then loaded an orienting
        #  baselayer, because that might be a scenario they want to save for some reason.  
        if self.currentLayersCount > 0 and self.scenarioFileName == None:
            self.scenarioDirty = True
            return
    
        # Now we handle if a scenario is open
        # Check the flag to see if all scenario layers are loaded
        if self.origScenarioLyrsLoaded:
            # compare the lenth of the list for the original and current layers
            if len(self.originalScenarioLayers) != self.currentLayersCount:
                # if they are not the same length, the scenario is dirty
                self.scenarioDirty = True
                return
            
            # the layers are the same length but do they have the same members?
            differences = []
            # this is what Python calls a "list comprehension"
            differences = [i for i in self.currentLayers.values() if i not in 
                                                        self.originalScenarioLayers]
            # debugging
            print "differences are "
            for layer in differences: print layer.name()
            
            if differences: # if there are differences
                self.scenarioDirty = True
            else: self.scenarioDirty = False
        
        # debugging
        print "self.scenarioDirty end is " + str(self.scenarioDirty)
             
    def openVectorLayer(self, vfilePath):
        ''' Open a vector layer '''
        # debugging
        print "openVectorLayer()"
        print "vfilePath is " + vfilePath
        
        # create the file info object to get info about the vfile
        info = QtCore.QFileInfo(QtCore.QString(vfilePath))
        #create the layer
        #QFileInfo.completeBaseName() returns just the filename
        try:
            vlayer = QgsVectorLayer(QtCore.QString(vfilePath), info.completeBaseName(), "ogr")       
        except (IOError, OSError), e:
            error = unicode(e)
            print error
        
        # This double checks for loading errors using qgis methods
        if not self.checkLayerLoadError(vlayer): return False
        
        capture_string = QtCore.QString(vfilePath)
        self.statusBar.showMessage(capture_string, 8000)
        
        # add layer to layer registry and set extent if necessary   
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        return True
    
    def openHiddenVectorLayer(self, vfilePath):
        # debugging
        print "mainwindow.openHiddenVectorLayer()"
        
        # create the file info object to get info about the vfile
        info = QtCore.QFileInfo(QtCore.QString(vfilePath))
        #create the layer
        #QFileInfo.completeBaseName() returns just the filename
        try:
            vlayer = QgsVectorLayer(QtCore.QString(vfilePath), info.completeBaseName(), "ogr")
        except (IOError, OSError), e:
            error = unicode(e)
            print error                
        # double check for error using qgis methods
        if not self.checkLayerLoadError(vlayer): return False
 
    def openRasterLayer(self, rfilePath):
        ''' Open a raster layer '''
        info = QtCore.QFileInfo(QtCore.QString(rfilePath))
        
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

        # add filename to statusbar with 8 sec. timeout         
        capture_string = QtCore.QString(rfilePath)
        self.statusBar.showMessage(capture_string, 8000)
    
    def openOrientingLayers(self):
        ''' Open orienting layers when the app is started '''
        path = config.baseLayersPath
        
        info = QtCore.QFileInfo(QtCore.QString(path))
        path2 = info.absolutePath()
        print "The path is " + path
        print "The path is " + path2
        vlayers = config.orientingVectorLayers
        rlayers = config.orientingRasterLayers

        # layers opened first will be on the bottom
        for rlayer in rlayers:
            tempPath = None
            tempPath = path + rlayer
            info = QtCore.QFileInfo(QtCore.QString(tempPath))
            print "The path is " + info.absoluteFilePath()
            self.openRasterLayer(tempPath)
 
        for vlayer in vlayers:
            tempPath = None
            tempPath = path + vlayer
            self.openVectorLayer(tempPath)
           
        # In config.py you, can set the baselyer(s) of your choice to be visible 
        for checked in config.baseLayersChecked:
            items = self.legend.findItems(checked, QtCore.Qt.MatchFixedString, 0)
            print "the length of items is " + str(len(items))
            if len(items) > 0:
                item = items[0]
                item.setCheckState(0, QtCore.Qt.Checked)
         
        self.scenarioDirty = False       
       
    def arrangeOrientingLayers(self):
        ''' The QgsProject instance does not set layer position in our layer panel,
            so we set it here.
        '''
        # debugging
        print "arrangeOrientingLayers()"

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
        print "numLegendLayers is " + str(numLegendLayers)
 
        # First load the raster layers
        for orientingLayer in oRLayers:
            info = QtCore.QFileInfo(orientingLayer)
            orientingLayerName = info.completeBaseName()
            print "orientingLayerName is " + orientingLayerName
            item = legend.findItems(orientingLayerName, 
                                          QtCore.Qt.MatchFixedString, 0)
            print "length of item list is " + str(len(item))
            itemToMove = item[0]
            print "is this a legendLayer? " + str(legend.isLegendLayer(itemToMove))
            print "item to move is " + itemToMove.text(0)
            position = numLegendLayers - (oRLayers.index(orientingLayer) + 1) # itemToMove is the base layer
            print "r position is " + str(position)
            itemToMove.storeAppearanceSettings() # Store settings 
            legend.takeTopLevelItem(legend.indexOfTopLevelItem(itemToMove))
            legend.insertTopLevelItem(position, itemToMove)
            legend.insertTopLevelItem(1, itemToMove)
            itemToMove.restoreAppearanceSettings()

        # then load the vector layers
        for orientingLayer in oVLayers:
            info = QtCore.QFileInfo(orientingLayer)
            orientingLayerName = info.completeBaseName()
            print "orientingLayerName is " + orientingLayerName
            item = legend.findItems(orientingLayerName, 
                                          QtCore.Qt.MatchFixedString, 0)
            print "length of item list is " + str(len(item))
            itemToMove = item[0]
            print str(legend.isLegendLayer(itemToMove))
            print "item to move is " + itemToMove.text(0)
            position = (numLegendLayers - (oVLayers.index(orientingLayer)
                                                       + (len(oRLayers) + 1)))
            print "v position is " + str(position)
            itemToMove.storeAppearanceSettings() # Store settings 
            legend.takeTopLevelItem(legend.indexOfTopLevelItem(itemToMove))
            legend.insertTopLevelItem(position, itemToMove)
            itemToMove.restoreAppearanceSettings()
                
    def setExtents(self):
        ''' Empty editing shapefiles do not have extents. We need to set extents often. '''
        # debugging
        print "Main.mainwindow.setExtents()"
        
        rect = self.canvas.extent()
        if self.activeVLayer:
            lrect = self.activeVLayer.extent()
        else: lrect = self.activeRLayer.extent()
        
        rectExtentMA = config.rectExtentMA
        # debugging
        print "The layer extents on loading are:"
        print ("(" + str(lrect.xMinimum()) + ", " + str(lrect.yMinimum()) + ", " + 
                     str(lrect.xMaximum()) + ", " + str(lrect.yMaximum()) + ")")
        print "The canvas extents on loading are:"
        print ("(" + str(rect.xMinimum()) + ", " + str(rect.yMinimum()) + ", " + 
                     str(rect.xMaximum()) + ", " + str(rect.yMaximum()) + ")")
        print "extentMA is (32000, 780000, 330000, 965000)"
   
        # set extents no bigger than MA state extents
        if rect.contains(rectExtentMA) or not rect.intersects(rectExtentMA):
            print "canvas extent contains or does not intersect MA"
            if (rectExtentMA.contains(lrect) or lrect.intersects(rectExtentMA) 
                                                 or not lrect.isEmpty()):
                print "layer extent is not empty and either is within or intersects MA extents"
                print "SET CANVAS TO LAYER EXTENTS"
                lrect.scale(1.05)
                self.canvas.setExtent(lrect)
                self.canvas.updateFullExtent()
                self.canvas.refresh()
            else:
                print "SET CANVAS TO MA EXTENTS"
                config.rectExtentMA.scale(1.05)
                self.canvas.setExtent(rectExtentMA)
                if self.activeVLayer:
                    self.activeVLayer.setCacheImage(None)
                else: self.activeRLayer.setCacheImage(None)    
                self.canvas.refresh()
                self.canvas.updateFullExtent()
                print "SET CANVAS TO MA EXTENT"
                print "lrect.isEmpty " + str(lrect.isEmpty())
        else: print "THE EXTENTS WERE NOT CHANGED"       
        
        
        # debugging
        print "The layer extents after loading are:"
        print ("(" + str(lrect.xMinimum()) + ", " + str(lrect.yMinimum()) + ", " + 
                     str(lrect.xMaximum()) + ", " + str(lrect.yMaximum()) + ")")
        print "The canvas extents after loading are:"
        print ("(" + str(rect.xMinimum()) + ", " + str(rect.yMinimum()) + ", " + 
                     str(rect.xMaximum()) + ", " + str(rect.yMaximum()) + ")")
        print "extentMA is (32000, 780000, 330000, 965000)"
                
    def getEditFields(self):
        # debugging
        print "mainwindow.getEditFields()"
        
        geom = self.geom
        if geom == 0:  #0 point, 1 line, 2 polygon
            editFields = config.editPointsFields
        elif geom == 1:
            editFields = config.editLinesFields
        elif geom == 2:
            editFields = config.editPolygonsFields        
        return editFields
    
    def copyFeaturesShared(self):
        ''' 
            This method copies features and is used by mainwindow.copyFeatures and
            mainwindow.deleteFeatures (when deleting from config.pointBaseLayers)
        '''
        # make copy as instance variable so we can paste features into another layer
        # "selectedFeatures" is a QgsFeatureList (a Python list of QgsFeature objects)
        self.copiedFeats = self.activeVLayer.selectedFeatures()
        self.copiedFeatCount = self.activeVLayer.selectedFeatureCount()
        self.copiedFeatGeom = self.activeVLayer.geometryType()
        self.copyFlag = True
        
        # remove the selection from the activeVLayer and reset the select tool
        self.activeVLayer.removeSelection(False) # false means no signal emitted
        print "mainwindow.copyFeaturesShared() removed selection and slected features count is " + str(self.activeVLayer.selectedFeatureCount())
        self.activeVLayer.triggerRepaint()
        self.canvas.unsetMapTool(self.toolSelect)
        self.mpActionSelectFeatures.setChecked(False)
  
    def pasteBaseLayerDeletions(self):
        ''' Add attribute data to pasted base layer deletions '''
        # debugging
        print "mainwindow.pasteBaseLayerDeletions(self)"
        # Check if "edit_scenario(points) is open, and if not then warn.
        editingLayerName = QtCore.QString(config.editLayersBaseNames[0])
        items = self.legend.findItems(editingLayerName, QtCore.Qt.MatchFixedString, 0)
        print "length of item list is " + str(len(items))
        if len(items) > 0:
            self.legend.setCurrentItem(items[0])
            self.legend.currentItem().setCheckState(0, QtCore.Qt.Checked)
        else:
            QtGui.QMessageBox.warning(self, "File Error", "The 'edit_scenario(points)' layer \
must be open for you to complete this action.  Please click 'Edit Scenario' twice, select \
the appropriate scenario edit type, and try again.")
            return
        
        # get the original features in case the user wants to cancel the paste                                                                                                 
        shared.listOriginalFeatures(self.provider)
        
        print "featureCount begin = " + str(self.copiedFeatCount)
      
        # get the list of fields for the current scenario edit type
        for (count, scenarioType) in enumerate(config.scenarioTypesList):
            if scenarioType == self.scenarioType:
                inputFieldNames = eval("config.inputFieldNames" + str(count))
                break
        
        # debugging 
        print "inputFieldNames are:"
        print inputFieldNames

        # Simply add an id value and set the altered field to n and the deletion field to 'y' 
        editFields = self.getEditFields()
        a = {} # Python dictionary of attributes for the current editing layer
 
        feat = QgsFeature()
        for feat in self.copiedFeats:
            subListCount = 1 # this keeps track of where we are in the inputFieldNames list
            print "feat.id is " + str(feat.id())    
            for (count, field) in enumerate(editFields):
                # Fields that are in the editing shapefile but are not used for  
                # the current scenario type are set to empty values here.
                if field not in inputFieldNames:
                    a[count] = QtCore.QVariant()
                    print "not in field names count = " + str(count)
                    continue
                # set the id field first
                if subListCount == 1:
                    a[count] = QtCore.QVariant(1)
                    subListCount = 2
                    print "first field (id) count = " + str(count)
                    continue
                # if a point layer, set the altered and deleted fields
                if self.geom == 0 and subListCount == 2:
                    a[count] = QtCore.QVariant("n")
                    subListCount = 3
                    print "second field (altered) count = " + str(count)
                    continue
                if self.geom == 0 and subListCount == 3:
                    a[count] = QtCore.QVariant("y")
                    print "third field (deleted) count = " + str(count)
                    subListCount = 4
                    continue
                # set the rest of the input fields to empty for deleted features
                a[count] = QtCore.QVariant()
                print "Set the remaining input field to empty, count = " + str(count)
            feat.setAttributeMap(a)
            try:
                self.provider.addFeatures( [feat] )     
            except (IOError, OSError), e:
                error = unicode(e)
                print error
                vlayerName = self.activeVLayer.name()
                QtGui.QMessageBox.warning(self, "Failed to paste feature(s)", "Please check if "
                                 + vlayerName + " is open in another program and then try again.")    
        
        # reset the id numbers
        shared.resetIdNumbers(self.provider, self.geom)
         
        # Set the editDirty flag so that the user will be prompted to save edits or not.  
        # will be called when the edits (i.e. pasted features) are saved, so 
        # we don't need to do that here.
        self.editDirty = self.activeVLayer.name()
        self.mpActionSaveEdits.setDisabled(False)
        # set the edit dirty flag
        # reset the copy flag
        self.copiedFeats = None
        self.copiedFeatGeom = None
        self.copyFlag = False
        # the paste action is turned on in copyFeatures
        # it is turned off here or in pasteFeatures
        self.mpActionPasteFeatures.setDisabled(True)
        # update Vector Attribute Table if open
        if self.attrTable != None and self.attrTable.isVisible():
            self.openVectorAttributeTable()
        # update the extents and refresh so the features show
        shared.updateExtents(self, self.provider, self.activeVLayer, self.canvas)    
                 
    def setScenarioSaved(self):
        ''' Do the housekeeping for a successfully saved scenario '''
        # no errors so scenario saved and not dirty
        self.scenarioDirty = False
        # all scenario layers are loaded so set flag
        self.origScenarioLyrsLoaded = True
        # Reset the original scenario layers so we can delete editing layers
        # that have not been saved when closing a scenario or the app.
        # We also use this to check if the scenario is dirty.
        self.originalScenarioLayers = self.getCurrentLayers().values()
        # get the complete filename without the path
        self.scenarioFileName = self.scenarioInfo.fileName()
        # give the user some info
        self.setWindowTitle("Conservation Assessment and \
Prioritization System (CAPS) Scenario Builder - " + self.scenarioFileName)
    
    def deleteExportScenarioFile(self):
        ''' Delete the scenario's export file.  Used by mainwindow.exportScenario()
            and legend.Legend.deleteEditingLayer()
        '''
        scenarioDirectoryName = self.scenarioInfo.completeBaseName()
        exportFileName = unicode(scenarioDirectoryName + ".csv")
        exportPath = unicode(config.scenarioExportsPath + exportFileName)
 
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
                QtGui.QMessageBox.warning(self, 'Deletion Error:', 'The previously saved scenario '\
+ exportFileName + ' could not be deleted.  Please try again.')
          
    def setRendererV2(self):
        # debugging
        print "main.MainWindow.setRendererV2()"
        print "self.geom is :" + str(self.geom)
        
        '''# add our custom red cross layer to the layer registry
        #QgsSymbolLayerV2Registry.instance().addSymbolLayerType( RedCrossSymbolMarkerLayerMetadata() ) 
        list = QgsSymbolLayerV2Registry.instance().symbolLayersForType(QgsSymbolV2.Marker)
        for item in list:
            print item'''
            
        # set to use new generation symbology
        #self.activeVLayer.setUsingRendererV2(True)
        
        '''# Will need this when I write new class for red X
        rendererRegistry = QgsRendererV2Registry.instance()
        renderersList = rendererRegistry.renderersList()
        for item in renderersList:
            print str(item)'''
        # rendererV2 = None
        if self.geom == 0:
            if self.activeVLayer.name() == config.editLayersBaseNames[0]:
                #self.activeVLayer.rendererV2().name() ==):
                
                # the edit_scenario(points) layer
                print "Entered rule based renderer setup"
                #self.activeVLayer.setUsingRendererV2(True)
                # This returns a QgsSymbolV2().  In particular a QgsMarkerSymbolV2()
                # This also returns a QgsMarkerSymbolLayerV2() layer.
                # In particular a QgsSimpleMarkerSymbolLayerV2(). 
                symbol = QgsSymbolV2.defaultSymbol(QGis.Point)
                # renderer only needs a symbol to be instantiated
                rendererV2 = QgsRuleBasedRendererV2(symbol)
                #self.activeVLayer.setRendererV2(rendererV2)
                
                symbols = rendererV2.symbols()
                symbol = symbols[0]
                if self.layerColor:
                    symbol.setColor(self.layerColor)
                symbolLayer = symbol.symbolLayer(0)
                                                   
                #deleteLayer = RedCrossSymbolMarkerLayer()
                deleteSymbol = QgsSymbolV2.defaultSymbol(QGis.Point)
                deleteLayer = deleteSymbol.symbolLayer(0)
                deleteLayer.setSize(4.0)
                deleteLayer.setColor(QtGui.QColor(255, 0, 0, 150))

                # make the rule and add it
                rule1 = rendererV2.Rule(deleteSymbol, 0, 0, 
                    QtCore.QString("c_deleted='y' or d_deleted='y' or w_deleted='y' or r_deleted='y'"))
                rendererV2.addRule(rule1)
                
                self.activeVLayer.setRendererV2(rendererV2)
               
                # debugging
                print "The renderer's name is: " + self.activeVLayer.rendererV2().name()
                print "The number of symbols is: " + str(len(rendererV2.symbols()))
                print "The symbolLayer properties are: "
                for k, v in symbolLayer.properties().iteritems():
                    print "%s: %s" % (k, v)
                print "The deleteLayer properties are: "
                for k, v in deleteLayer.properties().iteritems():
                    print "%s: %s" % (k, v)
            else:
                self.activeVLayer.setUsingRendererV2(True)
                rendererV2 = QgsSingleSymbolRendererV2.defaultRenderer(QGis.Point)
                self.activeVLayer.setRendererV2(rendererV2)
        elif self.geom == 1:
            print "geometry = 1"
            self.activeVLayer.setUsingRendererV2(True)
            rendererV2 = QgsSingleSymbolRendererV2.defaultRenderer(QGis.Line)
            symbol = rendererV2.symbols()[0]
            # this is a QgsLineSymbolLayerV2()
            layer = symbol.symbolLayer(0)
            print "The layer width is: " + str(layer.width())
            layer.setWidth(0.4)
            if self.layerColor: # we saved color in Tools.shared.setExtents()
                print "THERE IS A LINE COLOR"
                layer.setColor(self.layerColor)
            self.activeVLayer.setRendererV2(rendererV2)    
        elif self.geom == 2 and self.activeVLayer.name() == config.baseLayersChecked[0]:
                print "This is the base_towns layer"
                self.activeVLayer.setUsingRendererV2(True)
                symbol = self.activeVLayer.rendererV2().symbols()[0]
                layer = symbol.symbolLayer(0)
                layer.setBrushStyle(QtCore.Qt.NoBrush)
                layer.setColor(QtGui.QColor(255,255,255,0))
                symbol.setLineWidth(0.4)
                self.activeVLayer.setRendererV2(rendererV2)
        elif self.geom == 2:
            self.activeVLayer.setUsingRendererV2(True)
            rendererV2 = QgsSingleSymbolRendererV2.defaultRenderer(QGis.Polygon)
            symbol = rendererV2.symbols()[0]
            # this is a QgsLineSymbolLayerV2()
            layer = symbol.symbolLayer(0)
            if self.layerColor:
                layer.setColor(self.layerColor)
            self.activeVLayer.setRendererV2(rendererV2)   
 
        # make an instance variable of the V2 renderer
        self.rendererV2 = rendererV2
     
        # debugging
        
        if self.activeVLayer.isUsingRendererV2():
        # new symbology - subclass of QgsFeatureRendererV2 class
            # returns a list of symbols for the V2 renderer
            symbols = self.rendererV2.symbols()
            # only 1 symbol in symbols and only one layer
            symbol = symbols[0]
            layer = symbol.symbolLayer(0)
            print "rendererV2.dump is:" + self.rendererV2.dump()
            print "The layer properties are: "
            for k, v in layer.properties().iteritems():
                print "%s: %s" % (k, v)
            print "The number of symbols is: " + str(len(symbols))
            print "The number of layers in symbols[0] is: " + str(symbol.symbolLayerCount())
            print "The layer type is: " + str(layer.layerType())
        else:
            # old symbology - subclass of QgsRenderer class
            renderer = self.activeVLayer.renderer()
            symbols = renderer.symbols()
            print "old renderer"
            print "The number of symbols is: " + str(len(symbols))
            print symbols 
        
        # debugging
        print "alc opened active layer is " + self.activeVLayer.name()
        print "alc opened active layer source is " + self.activeVLayer.source()
        print "alc num selected feats " + str(len(self.activeVLayer.selectedFeatures()))

    def makeScenarioDirectory(self):
        ''' Create a directory to store a scenario's editing files '''
        # debugging
        print "makeScenarioDirectory()"
        
        # We are creating a new scenario, so remove any old edit files directory 
        # (and files), or exported scenarios with same name.
        scenarioDirectoryName = self.scenarioInfo.completeBaseName()
        dirPath = unicode(self.scenarioInfo.path() + "/" + scenarioDirectoryName)
        exportFileName = unicode(scenarioDirectoryName + ".csv")
        exportPath = unicode(config.scenarioExportsPath + exportFileName)

        # debugging
        print "scenarioDirectoryName is " + str(scenarioDirectoryName)
        print "directoryPath is " + str(dirPath)
        
        error = None
        if QtCore.QDir(config.scenariosPath + scenarioDirectoryName).exists():    
            try:
                if os.path.exists(exportPath):
                    os.remove(exportPath) # use Python here
                shutil.rmtree(dirPath) 
            except (IOError, OSError), e:
                error = unicode(e)
            if error:
                print e
                QtGui.QMessageBox.warning(self, "Deletion error:", "The scenario editing \
file directory or export files could not be completely removed. Please check if one of the \
files in the scenario is open in another program and then try again.")
                return "Error"
        # now make the new directory        
        try:
            QtCore.QDir().mkdir(config.scenariosPath + scenarioDirectoryName)
        except (IOError, OSError), e:
                error = unicode(e)
        if error:
            print e
            QtGui.QMessageBox.warning(self, "Failed to create directory:", "The scenario \
editing file directory could not be created. Please try to save the project again, or save it with a \
different name.")
            return "Error"
       
    def checkLayerLoadError(self, layer):
        # check for error
        if not layer.isValid():
            QtGui.QMessageBox.warning(self, "File Error", "Layer failed to load!")
            return False
        else: return True

    def checkBaseLayerMatch(self, title, text):
        name = self.activeVLayer.name()
        type = self.scenarioType
        if (type == config.scenarioTypesList[0] and name != config.pointBaseLayers[0] or
             type == config.scenarioTypesList[1] and name != config.pointBaseLayers[1] or
             type == config.scenarioTypesList[2] and name != config.pointBaseLayers[2] or
             type == config.scenarioTypesList[3] and name != config.pointBaseLayers[3]):
            QtGui.QMessageBox.warning(self, title, "The point base layer which \
you are trying to " + text + " does not match the scenario edit type you have chosen. \
For example. If you have chosen to edit 'dams,' then you can only " + text + " the layer \
'base_dams'")
            return False
        else: return True
    
#**************************************************************
    ''' Testing '''
#**************************************************************
                   
    def printFields(self):
        ''' Testing '''
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
                

# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
#
# Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
#
#--------------------------------------------------------------------- 
# 
# Copyright (C) 2011  Robert English: Daystar Computing (http://edaystar.com)
#
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
# import Qt libraries
from PyQt4 import QtCore, QtGui
# import qgis API
from qgis.core import *
# import the ui made with Qt Designer
from dlgscenarioedittypes_ui import Ui_DlgScenarioEditTypes
# CAPS application imports
import config


class DlgScenarioEditTypes(QtGui.QDialog, Ui_DlgScenarioEditTypes):
    """ Open a dialog to select the type of scenario change """
    def __init__(self, mainwindow):
        QtGui.QDialog.__init__(self, mainwindow)
        self.setupUi(self)
        
        self.mainwindow = mainwindow
        # get the list of scenario types from main window
        self.scenarioEditTypesList = config.scenarioEditTypesList

        # debugging
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes() scenarioEditTypesList is: "
        print self.scenarioEditTypesList
        
        # add the scenario types list to the combo box drop down
        self.typesComboBox.addItems(self.scenarioEditTypesList)
    
        QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self, QtCore.SIGNAL("rejected()"), self.reject)
                
#################################################################################
    ''' Custom slots '''
#################################################################################    
    
    def accept(self):
        ''' User has chosen a scenario type to edit, so
            open needed layers for the scenario change type 
        '''
        # debugging
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes().accept()"
        
        # The user has clicked "OK," so we have entered edit mode
        self.mainwindow.editMode = True
        
        # we are starting a new edit type, so disable previous edit actions 
        self.mainwindow.disableEditActions() #(i.e. Add points, lines, polygons) 
        
        # set needed variables
        self.editLayerBaseName = None
        self.editLayerFileName = None
        self.baseLayerBaseName = None
        self.baseLayerFileName = None
        self.constraintLayerBaseName = None
        self.constraintLayerFileName = None
        self.editLayerOpen = False
        self.baseLayerOpen = False
        self.constraintLayerOpen = False
        legend = self.mainwindow.legend
        
        # Get the scenario type chosen from the dialog and save
        # to a main window variable for use in other modules
        scenarioEditType = unicode(self.typesComboBox.currentText()) # convert the QString
        self.mainwindow.scenarioEditType = scenarioEditType

        # get the needed editingLayer, baseLayer and constraintLayer names for the current scenarioEditType
        # note that some names may have a value of None
        self.getEditBaseConstraintLayerNames(scenarioEditType)
        
        # set paths (edit file directory has same name as the scenario file (i.e. somedirectory.caps))
        self.baseLayersPath = config.baseLayersPath
        self.scenariosPath = config.scenariosPath

        # I convert QStrings to unicode unless they are used immediately in a Qt method. 
        # This ensures that we never ask Python to slice a QString, which produces a type error.
        # the QFileInfo for the scenario file path
        self.scenarioInfo = self.mainwindow.scenarioInfo # is an object
        self.scenarioDirectory = unicode(self.mainwindow.scenarioInfo.completeBaseName())
        self.newEditLayerPath = (config.scenariosPath + self.scenarioDirectory + "/" + self.editLayerFileName) 
        self.baseFilePath = None
        if self.baseLayerFileName: # The Add roads (lines) scenario edit type has no base layer
            self.baseFilePath = (self.baseLayersPath + self.baseLayerFileName)
        self.constraintFilePath = None
        if self.constraintLayerFileName: # The polygon scenario edit types do not have constraints
            self.constraintFilePath = (self.baseLayersPath + self.constraintLayerFileName)

        # see if the editLayer, baseLayer or constraintLayer is open in the layer panel
        self.editLayerOpen = self.isLayerOpen(legend, self.editLayerBaseName)
        self.baseLayerOpen = self.isLayerOpen(legend, self.baseLayerBaseName)
        self.constraintLayerOpen = self.isLayerOpen(legend, self.constraintLayerBaseName)
 
        # debugging
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.scenarioEditType is " + scenarioEditType 
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.editLayerBaseName is " + self.editLayerBaseName
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.baseLayerBaseName is " + str(self.baseLayerBaseName)
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.constraintLayerBaseName is " + str(self.constraintLayerBaseName)
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.baseLayerFileName is " + str(self.baseLayerFileName)
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.constraintLayerFileName is " + str(self.constraintLayerFileName)
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.editLayerOpen flag is " + str(self.editLayerOpen)
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.baseLayerOpen flag is " + str(self.baseLayerOpen)
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.constraintLayerOpen flag is " + str(self.constraintLayerOpen)
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.newEditLayerPath is " + self.newEditLayerPath
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.baseFilePath is " + str(self.baseFilePath)
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes(): self.constraintFilePath is " + str(self.constraintFilePath)
      
        
        # if the editing layer is not open, create it
        # note: If the editing layer is not open in the scenario, then it does not exist because
        # the editing layer is deleted if removed from the scenario. This is done to ensure that 
        # the user cannot forget that he has made edits to an editing layer and unknowingly submit
        # an incorrect scenario!
        if not self.editLayerOpen:
            self.writeNewEditingShapefile()
            if not self.mainwindow.openVectorLayer(self.newEditLayerPath): 
                # opening the editing layer failed so exit
                # done sets the result code for _exec() to rejected (i.e. cancel)
                self.setResult(0)
                self.hide()
                return
        
        # if the base or constraint layer is not open then open it
        if not self.baseLayerOpen and self.baseFilePath:
            self.openBaseOrConstaintsLayer(self.baseFilePath)
        if not self.constraintLayerOpen and self.constraintFilePath: 
            self.openConstraintLayer(self.constraintFilePath)
 
        # now that the layers are open, highlight them
        self.colorEditBaseConstraintLayers(legend)
            
        ''' Set the position and visibility of needed edit and base layers '''      
        
        # First, hide all editing layers and base layers not used for orientation.
        self.hideEditBaseLayers(legend)
                    
        # Move the needed editing layer to the top, select, check and make visible.
        # The editing layer goes to position 0, and must be moved before the 
        # baselayer (position 1).  If the base layer is moved to position 1 first, 
        # and a layer other than the correct editLayer is at position 0, then the
        # baseLayer will end up at position 3 when the correct editing layer is inserted.
        self.moveLayer(legend, self.editLayerBaseName, 0)
   
        # If it exists in this scenario edit type, move the needed base layer to second in list, 
        # check and make visible.
        # We do not want to change position or visibility of the orienting base layer, "base_land"
        if self.baseLayerBaseName and self.baseLayerBaseName != config.polygonBaseLayersBaseNames[1]: 
            self.moveLayer(legend, self.baseLayerBaseName, 1)
        
        # If it exists in this scenario edit type, move the needed constraint layer 
        # to third in list, check and make visible
        if self.constraintLayerBaseName:
            if self.baseLayerBaseName: position = 2
            else: position = 1 
            self.moveLayer(legend, self.constraintLayerBaseName, position)

        self.setResult(1)
        self.hide()    

    def reject(self):
        print "DlgScenarioEditTypes.reject(): user closed the dialog"
        self.hide()
        return
    
#################################################################################   
    ''' Core methods '''   
#################################################################################
    
    def getEditBaseConstraintLayerNames(self, scenarioEditType):
        ''' Get the needed editingLayer and baseLayer file names '''
        if scenarioEditType == self.scenarioEditTypesList[0]:
            self.editLayerBaseName = config.editLayersBaseNames[0]
            self.editLayerFileName = config.editLayersFileNames[0]
            self.baseLayerBaseName = config.pointBaseLayersBaseNames[0]
            self.baseLayerFileName = config.pointBaseLayersFileNames[0]
            self.constraintLayerBaseName = config.scenarioConstraintLayersBaseNames[0]
            self.constraintLayerFileName = config.scenarioConstraintLayersFileNames[0]
        elif scenarioEditType == self.scenarioEditTypesList[1]:
            self.editLayerBaseName = config.editLayersBaseNames[0]
            self.editLayerFileName = config.editLayersFileNames[0]
            self.baseLayerBaseName = config.pointBaseLayersBaseNames[1]
            self.baseLayerFileName = config.pointBaseLayersFileNames[1]
            self.constraintLayerBaseName = config.scenarioConstraintLayersBaseNames[0]
            self.constraintLayerFileName = config.scenarioConstraintLayersFileNames[0]
        elif scenarioEditType == self.scenarioEditTypesList[2]:
            self.editLayerBaseName = config.editLayersBaseNames[0]
            self.editLayerFileName = config.editLayersFileNames[0]
            self.baseLayerBaseName = config.pointBaseLayersBaseNames[2]
            self.baseLayerFileName = config.pointBaseLayersFileNames[2]
            self.constraintLayerBaseName = config.scenarioConstraintLayersBaseNames[1]
            self.constraintLayerFileName = config.scenarioConstraintLayersFileNames[1]
        elif scenarioEditType == self.scenarioEditTypesList[3]:
            self.editLayerBaseName = config.editLayersBaseNames[0]
            self.editLayerFileName = config.editLayersFileNames[0]
            self.baseLayerBaseName = config.pointBaseLayersBaseNames[3]
            self.baseLayerFileName = config.pointBaseLayersFileNames[3]
            self.constraintLayerBaseName = config.scenarioConstraintLayersBaseNames[0]
            self.constraintLayerFileName = config.scenarioConstraintLayersFileNames[0]
        elif scenarioEditType == self.scenarioEditTypesList[4]:
            self.editLayerBaseName = config.editLayersBaseNames[1]
            self.editLayerFileName = config.editLayersFileNames[1]
            self.constraintLayerBaseName = config.scenarioConstraintLayersBaseNames[1]
            self.constraintLayerFileName = config.scenarioConstraintLayersFileNames[1]
        elif scenarioEditType == self.scenarioEditTypesList[5]:
            self.editLayerBaseName = config.editLayersBaseNames[2]
            self.editLayerFileName = config.editLayersFileNames[2]
            self.baseLayerBaseName = config.polygonBaseLayersBaseNames[0]
            self.baseLayerFileName = config.polygonBaseLayersFileNames[0]
        elif scenarioEditType == self.scenarioEditTypesList[6]:
            self.editLayerBaseName = config.editLayersBaseNames[2]
            self.editLayerFileName = config.editLayersFileNames[2]    
            self.baseLayerBaseName = config.polygonBaseLayersBaseNames[1]
            self.baseLayerFileName = config.polygonBaseLayersFileNames[1]
        else: print "No baseLayer Found"    

    def isLayerOpen(self, legend, layerBaseName):
        ''' Check if editLayer or baseLayer is open in the layer panel '''
        # debugging
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes.isEditLayerOpen()"
        
        if not layerBaseName: return False # if this layers name is None
        items = legend.findItems(layerBaseName, QtCore.Qt.MatchFixedString, 0)
        print "length of item list is " + str(len(items))
        if len(items) > 0: return True
        else: return False # set the editLayerOpen flag
  
    def writeNewEditingShapefile(self):
        ''' Write a new editing shapefile for the current scenario type '''
        # debugging
        print "DlgScenarioEditTypes.writeNewEditingShapefile()"
        
        if "points" in self.editLayerBaseName: 
            values = config.editPointsFields
            keys = range(len(config.editPointsFields))
            geometry = QGis.WKBPoint
            print "points"
        elif "lines" in self.editLayerBaseName:
            values = config.editLinesFields
            keys = range(len(config.editLinesFields))
            geometry = QGis.WKBLineString
            print "lines"
        elif "polygons" in self.editLayerBaseName:
            values = config.editPolygonsFields
            keys = range(len(config.editPolygonsFields))
            geometry = QGis.WKBPolygon
            print "polygons"
        
        print "the length of values is " + str(len(values))
        
        # turn the values list into a list of QgsField objects
        fieldObjects = [0]*len(values)
        for (counter, value) in enumerate(values):
            print "counter is " + str(counter)
            fieldObjects[counter] = QgsField(QtCore.QString(value), QtCore.QVariant.String)
        
        # create a dictionary from the current fields list
        fields = dict(zip(keys, fieldObjects))
        print "the fields dictionary is "
        for field in fields.values(): print field.name()

        path = self.newEditLayerPath
        writer = QgsVectorFileWriter(path, "utf-8", fields, geometry, self.mainwindow.crs, "ESRI Shapefile")
        
        if writer.hasError() != QgsVectorFileWriter.NoError:
            print "Error when creating shapefile: ", writer.hasError()
    
    def openBaseOrConstaintsLayer(self, filePath):
        ''' Open the baseLayer needed for the current scenarioEditType '''
        # debugging
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes().openBaseOrConstraintsLayer()"
        
        # if the file exists, open it (automatically goes to the top of the layer panel)
        qFile = QtCore.QFile(filePath)
        fileName = qFile.fileName()
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes().openBaseOrConstraintsLayer(): the fileName is " + fileName
        
        if qFile.exists():
            print "Main.dlgscenarioedittypes.DlgScenarioEditTypes().openBaseOrConstraintsLayer(): file exists is True"
            if ".shp" in fileName: self.mainwindow.openVectorLayer(filePath)
            else: self.mainwindow.openRasterLayer(filePath)
        else:
            QtGui.QMessageBox.warning(self, "File Error", "The needed base file, "\
                                                + self.fileName + ", could not be found.")
       
    def hideEditBaseLayers(self, legend):
        ''' Hide all editing layers and base layers not used for orientation '''
        hideList = config.hideEditLayers
        for layer in hideList:
            items = legend.findItems(layer, QtCore.Qt.MatchFixedString, 0)
            if len(items) > 0:
                item = items[0]
                legend.blockSignals( True )
                item.setCheckState(0, QtCore.Qt.Unchecked)
                item.canvasLayer.setVisible(False)
                legend.blockSignals( False )
                print "unchecked " + str(items[0].canvasLayer.layer().name())

    def moveLayer(self, legend, layerBaseName, position):
        ''' Move the needed editLayer to the top of the layer panel
            and select, check and make visible.
        '''
        items = legend.findItems(layerBaseName, QtCore.Qt.MatchFixedString, 0)
        itemToMove = items[0]
        
        # debugging
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes.moveLayer()" 
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes.moveLayer(): length of item list is " + str(len(items))
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes.moveLayer(): is this a legendLayer? " + str(legend.isLegendLayer(itemToMove))
        print "Main.dlgscenarioedittypes.DlgScenarioEditTypes.moveLayer(): item to move is " + itemToMove.text(0)
        
        # just moving editing layer, no need for signals
        legend.blockSignals(True)
        itemToMove.storeAppearanceSettings() # Store settings 
        legend.takeTopLevelItem(legend.indexOfTopLevelItem(itemToMove))
        legend.insertTopLevelItem(position, itemToMove)
        itemToMove.restoreAppearanceSettings()
        legend.blockSignals(False)
        itemToMove.setCheckState(0, QtCore.Qt.Checked)
        if 'edit' in layerBaseName:
            legend.setCurrentItem(itemToMove)
        
        
    def colorEditBaseConstraintLayers(self, legend):
        ''' A method to highlight the editing layer and base layer for the
            current scenario edit type.
        '''
        # First remove any previous highlighting
        brush = QtGui.QBrush()
        brush.setColor(QtCore.Qt.black)
        
        legend.blockSignals(True)
        for i in range(legend.topLevelItemCount()):
            legend.topLevelItem(i).setForeground(0, brush)
        
    
        # now color the layers
        color = QtGui.QColor(0, 0, 255)
        brush.setColor(color) # (QtCore.Qt.darkGreen)
        
        editItems = legend.findItems(self.editLayerBaseName, QtCore.Qt.MatchFixedString, 0)
        legend.blockSignals(True)
        editItems[0].setForeground(0, brush)
        legend.blockSignals(False)
        
        if self.baseLayerBaseName:
            baseItems = legend.findItems(self.baseLayerBaseName, QtCore.Qt.MatchFixedString, 0)
            legend.blockSignals(True)
            baseItems[0].setForeground(0, brush)
            legend.blockSignals(False)
            
        if self.constraintLayerBaseName:
            constraintItems = legend.findItems(self.constraintLayerBaseName, QtCore.Qt.MatchFixedString, 0)
            legend.blockSignals(True)
            constraintItems[0].setForeground(0, brush)
            legend.blockSignals(False)
            
        #debugging
        print "Main.dlgscenariotypes.colorEditBaseConstraintLayers()"
        print "Main.dlgscenariotypes.colorEditBaseConstraintLayers(): The editing layer name is: " + editItems[0].text(0)
        if self.baseLayerBaseName:
            print "Main.dlgscenariotypes.colorEditBaseConstraintLayers(): The base layer name is: " + baseItems[0].text(0)
        if self.constraintLayerBaseName:
            print "Main.dlgscenariotypes.colorEditBaseConstraintLayers(): The constraint layer name is: " + constraintItems[0].text(0) 
        print "Main.dlgscenariotypes.colorEditBaseConstraintLayers(): The brush color is: " + str(brush.color())
        
        

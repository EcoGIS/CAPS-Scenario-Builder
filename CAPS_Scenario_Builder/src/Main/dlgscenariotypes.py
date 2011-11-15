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

# import Qt libraries
from PyQt4 import QtCore, QtGui
# import qgis API
from qgis.core import *
# import the ui made with Qt Designer
from dlgscenariotypes_ui import Ui_DlgScenarioTypes
# CAPS application imports
import config


class DlgScenarioTypes(QtGui.QDialog, Ui_DlgScenarioTypes):
    """ Open a dialog to select the type of scenario change """
    def __init__(self, mainwindow):
        QtGui.QDialog.__init__(self, mainwindow)
        self.setupUi(self)
        
        self.mainwindow = mainwindow
        # get the list of scenario types from main window
        self.scenarioEditTypesList = config.scenarioEditTypesList

        # debugging
        print "Class DlgScenarioTypes() scenarioEditTypesList is: "
        print self.scenarioEditTypesList
        
        # add the scenario types list to the combo box drop down
        self.typesComboBox.addItems(self.scenarioEditTypesList)
    
        QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"), self.apply)
        QtCore.QObject.connect(self, QtCore.SIGNAL("rejected()"), self.cancel)
                
#################################################################################
    ''' Custom slots '''
#################################################################################    
    
    def apply(self):
        ''' User has chosen a scenario type to edit, so
            Open needed layers for the scenario change type 
        '''
        # debugging
        print "DlgScenarioTypes.apply()"
        
        # we are starting a new edit type, so disable previous edit actions 
        #(i.e. Add points, lines, polygons) 
        self.mainwindow.disableEditActions()
        
        # set needed variables
        self.editLayer = None
        self.baseLayerName = None
        self.baseLayerFileName = None
        self.editLayerOpen = False
        self.baseLayerOpen = False
        legend = self.mainwindow.legend

        # Get the scenario type chosen from the dialog and save
        # to a main window variable for use in other modules
        scenarioEditType = unicode(self.typesComboBox.currentText())
        self.mainwindow.scenarioEditType = scenarioEditType

        # get the needed editingLayer and baseLayer names for the current scenarioEditType
        self.getEditAndBaseLayerNames(scenarioEditType)
        
        # set paths (edit file directory has same name as the scenario file (i.e. somedirectory.caps))
        self.baseLayersPath = config.baseLayersPath
        #self.dataDirectoryPath = config.dataDirectoryPath
        self.scenariosPath = config.scenariosPath
        # the QFileInfo for the scenario file path
        self.scenarioInfo = self.mainwindow.scenarioInfo
        self.scenarioDirectory = unicode(self.mainwindow.scenarioInfo.completeBaseName()) 
        self.baseFilePath = unicode(self.baseLayersPath + self.baseLayerFileName)
        #self.editLayerPath = unicode(self.scenariosPath + self.scenarioDirectory
        #                                                     + self.editLayer + ".shp")
        self.newEditLayerPath = unicode(config.scenariosPath + 
                                 self.scenarioDirectory + "/" + self.editLayer + ".shp")

        # see if the editLayer or baseLayer is open in the layer panel
        self.isEditLayerOpen(legend)
        self.isBaseLayerOpen(legend)
        
        # debugging
        print "The self.scenarioEditType is " + scenarioEditType 
        print "The self.editingLayer is " + self.editLayer
        print "The self.baseLayerName is " + self.baseLayerName
        print "The self.baseLayerFileName is " + self.baseLayerFileName
        print "The self.editLayerOpen flag is " + str(self.editLayerOpen)
        print "The self.baseLayerOpen flag is " + str(self.editLayerOpen)
        print "self.newEditLayerPath is " + self.newEditLayerPath
        print "The self.baseFilePath is " + self.baseFilePath
      
        # if the edit layer is not open, create it
        # note: If the edit layer is not open in the scenario, then it does not exist because
        # the edit layer is deleted if removed from the scenario. This is done to ensure that 
        # the user cannot forget that he has made edits to an editing layer and unknowingly submit
        # an incorrect scenario!
        if not self.editLayerOpen:
            self.writeNewEditingShapefile()
            if not self.mainwindow.openVectorLayer(self.newEditLayerPath): return
        
        # if the base layer is not open then open it
        if not self.baseLayerOpen:
            self.openBaseLayer()
            
        # now that the layers are open, highlight them
        self.colorEditBaseLayers(legend)
            
        ''' Set the position and visibility of needed edit and base layers '''      
        
        # First, hide all edit layers and base layers not used for orientation.
        self.hideEditBaseLayers(legend)

                    
        # Move the needed editing layer to the top, select, check and make visible.
        # The edit layer goes to position 0, and must be moved before the 
        # baselayer (position 1).  If the base layer is moved to position 1 first, 
        # and a layer other than the correct editLayer is at position 0, then the
        # baseLayer will end up at position 3 when the correct edit layer is inserted.
        self.moveEditLayer(legend)
   
        # Move the needed base layer to second in list, check and make visible
        # We do not want to change position or visibility of the orienting base layer, "base_land"
        if self.baseLayerName != "base_land":
            self.moveBaseLayer(legend)
        
        # I like the towns layer to be selected so if it is open, I do it here.
        for checked in config.baseLayersChecked:
            items = legend.findItems(checked, QtCore.Qt.MatchFixedString, 0)
            print "the length of items is " + str(len(items))
            if len(items) > 0:
                item = items[0]
                item.setCheckState(0, QtCore.Qt.Checked)    
            

    def cancel(self):
        print "closed the dialog"
        # reset the edit scenario button
        self.mainwindow.mpActionEditScenario.setChecked(False)
        self.mainwindow.scenarioEditType = None
        return      
    
#################################################################################   
    ''' Core methods '''   
#################################################################################
    
    def getEditAndBaseLayerNames(self, scenarioEditType):
        ''' Get the needed editingLayer and baseLayer file names '''
        if scenarioEditType == self.scenarioEditTypesList[0]:
            self.editLayer = config.editLayersBaseNames[0]
            self.baseLayerName = config.pointBaseLayersBaseNames[0]
            self.baseLayerFileName = config.pointBaseLayersBaseNames[0] + ".shp"
        elif scenarioEditType == self.scenarioEditTypesList[1]:
            self.editLayer = config.editLayersBaseNames[0]
            self.baseLayerName = config.pointBaseLayersBaseNames[1]
            self.baseLayerFileName = config.pointBaseLayersBaseNames[1] + ".shp"
        elif scenarioEditType == self.scenarioEditTypesList[2]:
            self.editLayer = config.editLayersBaseNames[0]
            self.baseLayerName = config.pointBaseLayersBaseNames[2]
            self.baseLayerFileName = config.pointBaseLayersBaseNames[2] + ".shp"
        elif scenarioEditType == self.scenarioEditTypesList[3]:
            self.editLayer = config.editLayersBaseNames[0]
            self.baseLayerName = config.pointBaseLayersBaseNames[3]
            self.baseLayerFileName = config.pointBaseLayersBaseNames[3] + ".shp"
        elif scenarioEditType == self.scenarioEditTypesList[4]:
            self.editLayer = config.editLayersBaseNames[1]
            self.baseLayerName = config.lineBaseLayersBaseNames[0]
            self.baseLayerFileName = config.lineBaseLayersBaseNames[0] + ".tif"
        elif scenarioEditType == self.scenarioEditTypesList[5]:
            self.editLayer = config.editLayersBaseNames[2]
            self.baseLayerName = config.polygonBaseLayersBaseNames[0]
            self.baseLayerFileName = config.polygonBaseLayersBaseNames[0] + ".tif"
        elif scenarioEditType == self.scenarioEditTypesList[6]:
            self.editLayer = config.editLayersBaseNames[2]    
            self.baseLayerName = config.polygonBaseLayersBaseNames[1]
            self.baseLayerFileName = config.polygonBaseLayersBaseNames[1] + ".tif"
        else: print "No baseLayer Found"    

    def isEditLayerOpen(self, legend):
        ''' Check if editLayer or baseLayer is open in the layer panel '''
        # debugging
        print "isEditLayerOpen()"
        
        items = legend.findItems(self.editLayer, QtCore.Qt.MatchFixedString, 0)
        print "length of item list is " + str(len(items))
        if len(items) > 0:
            self.editLayerOpen = True # set the editLayerOpen flag

    def isBaseLayerOpen(self, legend):
        ''' Check if editLayer or baseLayer is open in the layer panel '''
        # debugging
        print "isBaseLayerOpen()"
        
        items = legend.findItems(self.baseLayerName, QtCore.Qt.MatchFixedString, 0)
        print "length of item list is " + str(len(items))
        if len(items) > 0:
            self.baseLayerOpen = True # set the editLayerOpen flag
    
    def writeNewEditingShapefile(self):
        ''' Write a new editing shapefile for the current scenario type '''
        # debugging
        print "writeNewEditingShapefile()"
        
        if "points" in self.editLayer:
            values = config.editPointsFields
            keys = range(len(config.editPointsFields))
            geometry = QGis.WKBPoint
            print "points"
        elif "lines" in self.editLayer:
            values = config.editLinesFields
            keys = range(len(config.editLinesFields))
            geometry = QGis.WKBLineString
            print "lines"
        elif "polygons" in self.editLayer:
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

        path = QtCore.QString(self.newEditLayerPath)
        writer = QgsVectorFileWriter(path, "utf-8", fields, geometry, config.crs, "ESRI Shapefile")
        
        if writer.hasError() != QgsVectorFileWriter.NoError:
            print "Error when creating shapefile: ", writer.hasError()
    
    def openBaseLayer(self):
        ''' Open the baseLayer needed for the current scenarioEditType '''
        # debugging
        print "openBaseLayer()"
        
        # if the file exists, open it (automatically goes to the top of the layer panel)
        baseFile = QtCore.QFile(self.baseFilePath)
        baseFileName = baseFile.fileName()
        print "baseFile.fileName() is " + baseFile.fileName()
        
        if baseFile.exists():
            print "baseFile exists is True"
            if ".shp" in baseFileName: 
                self.mainwindow.openVectorLayer(self.baseFilePath)
            else: self.mainwindow.openRasterLayer(self.baseFilePath)
        else:
            QtGui.QMessageBox.warning(self, "File Error", "The needed base file, "\
                                                + self.baseLayerFileName + ", could not be found.")
        
    def hideEditBaseLayers(self, legend):
        ''' Hide all edit layers and base layers not used for orientation '''
        list = config.hideEditLayers
        for layer in list:
            items = legend.findItems(layer, QtCore.Qt.MatchFixedString, 0)
            if len(items) > 0:
                item = items[0]
                legend.blockSignals( True )
                item.setCheckState(0, QtCore.Qt.Unchecked)
                item.canvasLayer.setVisible(False)
                legend.blockSignals( False )
                print "unchecked " + str(items[0].canvasLayer.layer().name())

    def moveEditLayer(self, legend):
        ''' Move the needed editLayer to the top of the layer panel
            and select, check and make visible.
        '''
        # debugging
        print "moveEditLayer()" 
        items = legend.findItems(self.editLayer, QtCore.Qt.MatchFixedString, 0)
        print "length of item list is " + str(len(items))
        itemToMove = items[0]
        print "is this a legendLayer? " + str(legend.isLegendLayer(itemToMove))
        print "item to move is " + itemToMove.text(0)
        # just moving edit layer, no need for signals
        legend.blockSignals(True)
        itemToMove.storeAppearanceSettings() # Store settings 
        legend.takeTopLevelItem(legend.indexOfTopLevelItem(itemToMove))
        legend.insertTopLevelItem(0, itemToMove)
        itemToMove.restoreAppearanceSettings()
        legend.blockSignals(False)
        legend.setCurrentItem(itemToMove)
        itemToMove.setCheckState(0, QtCore.Qt.Checked)
    
    def moveBaseLayer(self, legend):
        ''' Move the needed baseLayer to second the layer panel, 
            check and make visible.
        '''
        # debugging
        print "moveBaseLayer()"

        items = legend.findItems(self.baseLayerName, QtCore.Qt.MatchFixedString, 0)
        print "length of item list is " + str(len(items))
        itemToMove = items[0]
        print "is this a legendLayer? " + str(legend.isLegendLayer(itemToMove))
        print "item to move is " + itemToMove.text(0)
        # just moving base layer, no need for signals 
        legend.blockSignals(True) # just moving layers, no need to signal
        itemToMove.storeAppearanceSettings() # Store settings 
        legend.takeTopLevelItem(legend.indexOfTopLevelItem(itemToMove))
        legend.insertTopLevelItem(1, itemToMove)
        itemToMove.restoreAppearanceSettings()
        legend.blockSignals(False)
        #itemToMove.setCheckState(0, QtCore.Qt.Checked)
        
    def colorEditBaseLayers(self, legend):
        ''' A method to highlight the edit layer and base layer for the
            current scenario edit type.
        '''
        brush = QtGui.QBrush()
        brush.setColor(QtCore.Qt.black)
        # First remove any previous highlighting
        for i in range(legend.topLevelItemCount()):
            legend.topLevelItem(i).setForeground(0, brush)
    
        # now color the layers
        brush.setColor(QtCore.Qt.darkGreen)
        editItems = legend.findItems(self.editLayer, QtCore.Qt.MatchFixedString, 0)
        editItems[0].setForeground(0, brush)
        baseItems = legend.findItems(self.baseLayerName, QtCore.Qt.MatchFixedString, 0)
        baseItems[0].setForeground(0, brush)
        
        #debugging
        print "Main.dlgscenariotypes.colorEditBaseLayers()"
        print "The edit layer name is: " + editItems[0].text(0)
        print "The base layer name is: " + baseItems[0].text(0)
        print "The brush color is: " + str(brush.color())
        
        

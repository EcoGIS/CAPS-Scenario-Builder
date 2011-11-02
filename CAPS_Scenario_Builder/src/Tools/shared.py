# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
#
# Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
#
#--------------------------------------------------------------------- 
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

# PyQt4 includes for python bindings to QT
from PyQt4 import QtGui, QtCore 
# QGIS bindings for mapping functions
from qgis.core import *
from qgis.gui import *
# CAPS application imports
import config


   
def listOriginalFeatures(provider):
        ''' Track original features so we can delete unsaved added features '''
        # debugging
        print "Tools.shared.listOriginalFeatures()"
        
        originalFeats = []
        
        # debugging
        print "Tools.shared originalFeats begin "
        print originalFeats
        
        feat = QgsFeature()
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        while provider.nextFeature(feat):
            originalFeats.append(feat.id())
            
        # debugging     
        print "Tools.shared.originalFeats end " 
        print originalFeats
        
        return originalFeats
    
def checkSelectedLayer(mainwindow, scenarioType, currentLayerName):
        # debugging
        scenarioTypesList = config.scenarioTypesList
        print "Tools.shared.checkSelectedLayer()"
        print "scenarioType is " + scenarioType
        print "scenarioTypesList is "
        print scenarioTypesList
        print "currentLayerName is " + currentLayerName
        

        if scenarioType in scenarioTypesList[:4] and currentLayerName != "edit_scenario(points)":
            print "edit points"
            QtGui.QMessageBox.warning(mainwindow, "Scenario Editing Error", "You must select the layer \
named 'edit_scenario(points)' in the layer list panel to make the scenario edit type you have chosen.")
            return "Cancel"
        elif scenarioType == scenarioTypesList[4] and currentLayerName != "edit_scenario(lines)":
            print "edit lines"
            QtGui.QMessageBox.warning(mainwindow, "Scenario Editing Error", "You must select the layer \
named 'edit_scenario(lines)' in the layer list panel to make the scenario edit type you have chosen.")
            return "Cancel"
        elif scenarioType in scenarioTypesList[5:7] and currentLayerName != "edit_scenario(polygons)":
            print "edit polygons"
            QtGui.QMessageBox.warning(mainwindow, "Scenario Editing Error", "You must select the layer \
named 'edit_scenario(polygons)' in the layer list panel to make the scenario edit type you have chosen.") 
            return "Cancel"           

def getFeatsToDelete(provider, originalFeats):
        # debugging
        print "Tools.shared.getFeatsToDelete"
        
        feat = QgsFeature()
        currentFeats = []
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        while provider.nextFeature(feat):
            currentFeats.append(feat.id())
        featsToDelete = [i for i in currentFeats if i not in originalFeats]
        return featsToDelete
    
def deleteEdits(mainwindow, provider, activeVLayer, canvas, originalFeats):
        ''' Delete scenario edits added to editing layers since the last save.
            This method is only called from Main.mainwindow.chkEditsState()
        '''
        
        vlayerName = mainwindow.activeVLayer.name()
        
        # getFeatsToDelete returns a python list
        toDelete = getFeatsToDelete(provider, originalFeats)
        
        # debugging
        print "Tools.shared.deleteEdits()"
        print "original features are: ", originalFeats
        print "features toDelete are:", toDelete
        
        # provider.deleteFeatures only works with a Python list as a parameter
        # AND the spaces must be in the parameter list!
        try:
            provider.deleteFeatures( toDelete )
        except (IOError, OSError), e:
            error = unicode(e)
            print error                    
            QtGui.QMessageBox.warning(mainwindow, "Failed to delete edit(s)", "Please check if "
                                 + vlayerName + " is open in another program and then try again.")

        activeVLayer.triggerRepaint()
        
        # update the attribute table if open
        if mainwindow.attrTable != None and mainwindow.attrTable.isVisible():
            mainwindow.openVectorAttributeTable()
        mainwindow.editDirty = False
        
        # update the originalFeats list to be safe
        mainwindow.originalFeats = listOriginalFeatures(provider)
        
        # debugging  
        print "the remaining features are"
        printFeatures(provider)
        updateExtents(mainwindow, provider, activeVLayer, canvas)
        
def numberFeaturesAdded(activeVLayer, originalFeats):
        # debugging
        print "Tools.shared.numberFeaturesAdded"
        
        newFeats = activeVLayer.featureCount()- len(originalFeats)
        return newFeats
    
def updateExtents(mainwindow, provider, activeVLayer, canvas):
        # debugging
        print "Tools.shared.updateExtents()"
        print "The active layer feature count is " + str(activeVLayer.featureCount())
        vfilePath = activeVLayer.source()
        # I tried every update method I could find, but nothing other than closing
        # and reopening the layer seems to reset the layer extents.  So I do that here!
        if activeVLayer.name() in config.editLayersBaseNames:
            layerID = activeVLayer.getLayerID()
            # save the color so we can keep the same color when reopening the layer
            mainwindow.layerColor = mainwindow.activeVLayer.rendererV2().symbols()[0].color()
            # remove the layer from the originalScenarioLayers list, reset the 
            # variables associated with the layer we are removing (to avoid runtime errors)
            # and remove the layer from the registry.  Finally remove from legend and update
            # the legend's layer set
            mainwindow.legend.removeEditLayerFromRegistry(activeVLayer, layerID)
            # now reopen the layer
            mainwindow.openVectorLayer(vfilePath)
            # Make the layer visible.  This will cause a signal to be sent
            # and the legend will update the layer's status if not visible.
            # because we have just opened it, it is the active layer
            mainwindow.legend.currentItem().setCheckState(0, QtCore.Qt.Checked)
            return # opening the layer will update the extents, so just return
        
        provider.updateExtents()
        canvas.updateFullExtent()
        canvas.refresh()

def checkConstraints(mainwindow, geometry):
    ''' Checks constraints on scenario edits.  Currently only point edits are checked, 
        but this could change in the future, so the geometry parameter is generic.
    '''
    # debugging
    print "shared.checkConstraints()"
    
    basePath = config.baseLayersPath
    type = mainwindow.scenarioType
    list = config.scenarioTypesList
    pointsList = [list[0], list[1], list[3]]
    if type in pointsList: # crossing, dam removal or tidal restriction
        # Load the raster layer, but do not add it to the registry
        # so that it doesn't appear to the user
        point = geometry # The geometry is a point for these scenario edit types.
        rfilePath = basePath + "base_streams.tif"
        rlayer = openHiddenRasterLayer(mainwindow, rfilePath) # returns false if the file failed to open
        if rlayer == False:    # if the file failed to open, the constraints have not be met.
            # if the file failed to open, the constraints have not be met.
            return False
        # rlayer.identify returns a tuple with the result code (True or False) and a dictionary
        # with key = band and value = raster value for that band. We only have one band, so the 
        # key = "Band 1"
        result, identifyDict = rlayer.identify(point) 
        if not result: # if the identify method fails, we have not met constraints
            print "base_streams.tif identify failed"
            return False
        if unicode(identifyDict.get(QtCore.QString("Band 1"))) != u"1": # stream centerlines have a value of 1
            print "base_streams return False value = " + unicode(identifyDict.get(QtCore.QString("Band 1")))
            QtGui.QMessageBox.warning(mainwindow, "Constriants Error:", "The added feature must \
fall on the centerline of a stream (dark blue color) in the base_streams layer.  Please make the base_streams layer \
visible on your map, and try again. If the base_streams layer is not open in your scenario, you may \
open it by clicking 'Add Raster' on the toolbar or in the 'Layer' menu.")
            # add the layer to the registry here if it is not already open
            return False # constraints have not been met
        else: 
            return True # base file opened and constraints have been met.'''
        
        # debugging
        print "The rfilePath is " + rfilePath
        print "The raster value for base_streams.tif is " + unicode(identifyDict.get(QtCore.QString("Band 1")))
        print "The constraints were met and the return value is 'True'"
        
    elif type == list[2]: # a terrestrial wildlife crossing
        point = geometry
        rfilePath = basePath + "base_traffic.tif"
        rlayer = openHiddenRasterLayer(mainwindow, rfilePath) # returns false if the file failed to open
        if rlayer == False: # if the file failed to open, the constraints have not be met.
            return False
        result, identifyDict = rlayer.identify(point)
        print "The raster value for base_traffic.tif is " + unicode(identifyDict.get(QtCore.QString("Band 1"))) 
        if not result: # if the identify method fails, we have not met constraints
            print "base_traffic.tif identify failed"
            return False
        if unicode(identifyDict.get(QtCore.QString("Band 1"))) == u"null (no data)": # value for areas not on roads is null 
            print "base_traffic return False value = " + unicode(identifyDict.get(QtCore.QString("Band 1")))
            QtGui.QMessageBox.warning(mainwindow, "Constraints Error:", "The added feature must \
fall on a road in the 'base_traffic' layer.  Please make the base_traffic layer \
visible on your map, and try again. If the base_traffic layer is not open in your scenario, you may \
open it by clicking 'Add Raster' on the toolbar or in the 'Layer' menu.")
            # add the layer to the registry here if it is not already open
            return False # constraints have not been met
        else: return True # base file opened and constraints have been met.
    
        # debugging
        "The rfilePath is " + rfilePath
        "The raster value for base_traffic.tif is " + unicode(identifyDict.get(QtCore.QString("Band 1")))
        "The constraints were met and the return value is 'True'"
    else: print "Layer does not need contraints checked"
    
def openHiddenRasterLayer(mainwindow, rfilePath):    
    info = QtCore.QFileInfo(QtCore.QString(rfilePath))
    rlayer = QgsRasterLayer(info.filePath(), info.completeBaseName())
    
    if not mainwindow.checkLayerLoadError(rlayer): return False
    else: return rlayer

def makeSelectRect (geom, point, transform):
        # make rectangle in display pixels
        if geom == 0 or geom == 1:
            boxSize = 5
            xTopLeft = point.x() - boxSize
            yTopLeft = point.y() - boxSize 
            xBottomRight = point.x() + boxSize
            yBottomRight = point.y() + boxSize 
        elif geom == 2:
            boxSize = 1
            xTopLeft = point.x() - boxSize
            yTopLeft = point.y() - boxSize 
            xBottomRight = point.x() + boxSize
            yBottomRight = point.y() + boxSize
        else: print "Main.mainwindow.geometry unknown or None"
        
        # then convert to map coordinates
        topLeft = transform.toMapCoordinates(xTopLeft, yTopLeft)
        bottomRight = transform.toMapCoordinates(xBottomRight, yBottomRight)
        selectRect = QgsRectangle(topLeft, bottomRight)
        return selectRect
        
#**************************************************************
''' Testing '''
#**************************************************************

def printFeatures(provider):       
        "starting printFeatures()"
        #self.provider.reloadData()
        feat = QgsFeature()
        allAttrs = provider.attributeIndexes()
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

def resetIdNumbers(provider, geom):
        ''' Set the values of id field to start at 1 and finish with the number of features
            in the current editing shapefile.  Append p, l, pg for point, line and polygon.
        '''    
        # debugging
        print "shared.resetIDNumbers()"
        
        # get the geometry of the layer and set the 'append' variable
        if geom == 0: append = 'P'
        elif geom == 1: append = 'L'
        else: append = 'PG'
        feat = QgsFeature()

        # get all the data for the layer (a QgsAttributeList)
        allAttrs = provider.attributeIndexes()
        # the select() method initializes retrieval of data
        provider.select(allAttrs)
        # the nextFeature() method operates on a select initialized provider
        while provider.nextFeature(feat):
            print "The current feature id is " + str(feat.id())
            # A QgsAttributeMap is a pointer to a python dictionary where the key is
            # the feature id and the values are QtCore.QVariant objects.
            attrs = feat.attributeMap()
            for key, attr in attrs.iteritems():
                print "The attribute value is " + attr.toString()
                if not attr.toString(): continue
                else: 
                    print "We have the id field"
                    idString = str(feat.id()+1) + append
                    attrs[key] = QtCore.QVariant(idString)    
                    changedAttributes = {feat.id() : attrs} # create a "QgsChangedAttributesMap"
                    try:
                        provider.changeAttributeValues(changedAttributes)
                    except (IOError, OSError), e:
                        error = unicode(e)
                        print error     
                    break
                

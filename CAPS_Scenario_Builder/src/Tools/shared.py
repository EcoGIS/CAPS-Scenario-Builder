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
#--------------------------------------------------------------------------------------------
# PyQt4 includes for python bindings to QT
from PyQt4 import QtGui, QtCore 
# QGIS bindings for mapping functions
from qgis.core import *
from qgis.gui import *
# CAPS application imports
import config

  
def listOriginalFeatures(mainwindow, editingLayerName):
        ''' Track original features so we can delete unsaved added features '''
        # debugging
        print "Tools.shared.listOriginalFeatures()"
        
        legend = mainwindow.legend
        originalEditLayerFeats = []
        
        editingLayer = getEditingLayer(mainwindow, legend, editingLayerName)
        if not editingLayer:
            return
        provider = editingLayer.dataProvider()
        
        # debugging
        print "Tools.shared.listOriginalFeatures(): begin "
        print originalEditLayerFeats
        
        feat = QgsFeature()
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        while provider.nextFeature(feat):
            originalEditLayerFeats.append(feat.id())
            
        # debugging     
        print "Tools.shared.listOriginalFeatures():  end, originalEditLayerFeats are" 
        print originalEditLayerFeats
        
        return originalEditLayerFeats
    
def checkSelectedLayer(mainwindow, scenarioEditType, currentLayerName):
        ''' 
            Check to make sure the user has selected the correct 
            editing layer when adding or pasting features 
        '''
        scenarioEditTypesList = config.scenarioEditTypesList
        
        # debugging
        print "Tools.shared.checkSelectedLayer()"
        print "Tools.shared.checkSelectedLayer(): scenarioEditType is " + scenarioEditType
        print "Tools.shared.checkSelectedLayer(): currentLayerName is " + currentLayerName

        if scenarioEditType in scenarioEditTypesList[:4] and currentLayerName != config.editLayersBaseNames[0]:
            print "Tools.shared.checkSelectedLayer(): edit points"
            QtGui.QMessageBox.warning(mainwindow, "Scenario Editing Error", "You must select the layer \
named 'edit_scenario(points)' in the layer list panel to make the scenario edit type you have chosen.")
            return False
        elif scenarioEditType == scenarioEditTypesList[4] and currentLayerName != config.editLayersBaseNames[1]:
            print "Tools.shared.checkSelectedLayer(): edit lines"
            QtGui.QMessageBox.warning(mainwindow, "Scenario Editing Error", "You must select the layer \
named 'edit_scenario(lines)' in the layer list panel to make the scenario edit type you have chosen.")
            return False
        elif scenarioEditType in scenarioEditTypesList[5:7] and currentLayerName != config.editLayersBaseNames[2]:
            print "Tools.shared.checkSelectedLayer(): edit polygons"
            QtGui.QMessageBox.warning(mainwindow, "Scenario Editing Error", "You must select the layer \
named 'edit_scenario(polygons)' in the layer list panel to make the scenario edit type you have chosen.") 
            return False
        else: return True           

def getFeatsToDelete(provider, originalEditLayerFeats):
        # debugging
        print "Tools.shared.getFeatsToDelete()"
        
        feat = QgsFeature()
        currentFeats = []
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        while provider.nextFeature(feat):
            currentFeats.append(feat.id())
        featsToDelete = [i for i in currentFeats if i not in originalEditLayerFeats]
        return featsToDelete
      
def deleteEdits(mainwindow, editingLayerName, originalEditLayerFeats):
        ''' Delete scenario edits added to editing layers since the last save.
            This method is called from Main.mainwindow.checkEditsState() and
            Main.mainwindow.pasteFeatures().
        '''
        # debugging
        print "Tools.shared.deleteEdits()"
        print "Tools.shared.deleteEdits(): editingLayerName is :" + editingLayerName
        print "Tools.shared.deleteEdits(): original features are: ", originalEditLayerFeats
        
        # Tools.shared.deleteEdits should be impossible to call with an editingLayerName that is not
        # an editing layer; however, if it ever were to be called, we could accidentally delete users' data.
        # The code below is insurance against such a serious bug. 
        if editingLayerName not in config.editLayersBaseNames:
            QtGui.QMessageBox.warning(mainwindow, "Deletion Error", "Tools.shared.deleteEdits() is attempting \
to delete edits from a vector layer other than an editing layer.")
            return 
        
        legend = mainwindow.legend
        canvas = mainwindow.canvas
        # Now that we know we have an editing layer, get the provider from the name
        editingLayer = getEditingLayer(mainwindow, legend, editingLayerName)
        if not editingLayer:
            return
        provider = editingLayer.dataProvider()
        
        # getFeatsToDelete returns a python list
        toDelete = getFeatsToDelete(provider, originalEditLayerFeats)
        
        # debugging
        print "Tools.shared.deleteEdits(): features toDelete are:", toDelete
        
        # provider.deleteFeatures only works with a Python list as a parameter
        # AND the spaces must be in the parameter list!
        try:
            provider.deleteFeatures( toDelete )
        except (IOError, OSError), e:
            error = unicode(e)
            print error                    
            QtGui.QMessageBox.warning(mainwindow, "Failed to delete edit(s)", "Please check if "
                                 + editingLayerName + " is open in another program and then try again.")

        editingLayer.triggerRepaint()
        
        # update the attribute table if open
        if mainwindow.attrTable != None and mainwindow.attrTable.isVisible():
            mainwindow.openVectorAttributeTable()
        
        # we are back to the originalEditLayerFeats so
        mainwindow.editDirty = False
        
        # features have been deleted, so update the originalEditLayerFeats list to be safe
        mainwindow.originalEditLayerFeats = listOriginalFeatures(mainwindow, editingLayerName)
        
        # debugging  
        print "Tools.shared.deleteEdits(): the remaining features are"
        printFeatures(provider)
        updateExtents(mainwindow, provider, editingLayer, canvas)

def numberFeaturesAdded(activeVLayer, originalEditLayerFeats):
        # debugging
        print "Tools.shared.numberFeaturesAdded()"
        
        newFeats = activeVLayer.featureCount()- len(originalEditLayerFeats)
        return newFeats
    
def updateExtents(mainwindow, provider, activeVLayer, canvas):
        # debugging
        print "Tools.shared.updateExtents()"
        print "The active layer feature count is " + str(activeVLayer.featureCount())
        vfilePath = unicode(activeVLayer.source())
        # I tried every update method I could find, but nothing other than closing
        # and reopening the layer seems to reset the layer extents on the canvas.  
        # So I do that here.
        vlayerName = unicode(activeVLayer.name())
        if vlayerName in config.editLayersBaseNames:
            layerId = activeVLayer.id()
            # save the color so we can keep the same color when reopening the layer
            mainwindow.layerColor = activeVLayer.rendererV2().symbols()[0].color()
            # The method below removes the layer from the originalScenarioLayers list if the 
            # editing layer was in self.originalScenarioLayers and returns True if it was
            # or False if it was not.  The method resets the 
            # variables associated with the layer we are removing (to avoid runtime errors
            # associated with deleting underlying C++ objects)
            # and removes the layer from the registry.  Finally it removes the layer 
            # from the legend and updates the legend's layer set.
            inOriginalScenario = mainwindow.legend.removeEditLayerFromRegistry(activeVLayer, layerId)
            # now reopen the layer
            mainwindow.openVectorLayer(vfilePath)
            
            # if the layer was in self.originalSceenarioLayers then add it back 
            if inOriginalScenario:
                mainwindow.originalScenarioLayers.append(mainwindow.activeVLayer)
                # although layer names shouldn't have changed, update anyway
                mainwindow.getOriginalScenarioLayersNames()
                print " appended editing layer"
            
            # debugging
            for layer in mainwindow.originalScenarioLayers: print "Tools.shared.updateExtents(): " + layer.name()

            # now highlight the layer as it was before
            brush = QtGui.QBrush()
            color = QtGui.QColor(0, 0, 255)
            brush.setColor(color)
            editItems = mainwindow.legend.findItems(vlayerName, QtCore.Qt.MatchFixedString, 0)
            editItems[0].setForeground(0, brush)
            # Make the layer visible.  This will cause a signal to be sent
            # and the legend will update the layer's status if not visible.
            # because we have just opened it, it is the active layer
            mainwindow.legend.currentItem().setCheckState(0, QtCore.Qt.Checked)
            return # opening the layer will update the extents, so just return
        
        # none of these work for updating the extents of a vector layer after editing
        #activeVLayer.clearCacheImage()
        #provider.reloadData()
        #activeVLayer.reload()
        activeVLayer.updateExtents()
        provider.updateExtents()
        #canvas.mapRenderer().updateFullExtent()
        canvas.updateFullExtent()
        #canvas.map().render()
        canvas.refresh()

def checkConstraints(mainwindow, geometry, featId = None):
    ''' Checks constraints on scenario edits.  Currently only point edits are checked, 
        but this could change in the future, so the geometry parameter is generic.
    '''
    # debugging
    print "Tools.shared.checkConstraints()"
    print "Tools.shared.checkConstraints(): The featId is " + str(featId)
    
    basePath = config.baseLayersPath
    streamsFileName = config.scenarioConstraintLayersFileNames[0]
    editType = mainwindow.scenarioEditType
    typesList = config.scenarioEditTypesList
    pointsList = [typesList[0], typesList[1], typesList[3]]
    if editType in pointsList: # crossing, dam removal or tidal restriction
        # Load the raster layer, but do not add it to the registry
        # so that it doesn't appear to the user
        point = geometry # The geometry is a point for these scenario edit types.
        rfilePath = basePath + streamsFileName
        rlayer = openHiddenRasterLayer(mainwindow, rfilePath) # returns false if the file failed to open
        if rlayer == False:    # if the file failed to open, the constraints have not be met.
            # if the file failed to open, the constraints have not be met.
            return False
        # rlayer.identify returns a tuple with the result code (True or False) and a dictionary
        # with key = band and value = raster value for that band. We only have one band, so the 
        # key = "Band 1"
        result, identifyDict = rlayer.identify(point) 
        if not result: # if the identify method fails, we have not met constraints
            print "Tools.shared.checkConstraints(): base_streams.tif identify failed"
            return False
        if unicode(identifyDict.get(QtCore.QString("Band 1"))) != u"1": # stream centerlines have a value of 1
            print "Tools.shared.checkConstraints(): base_streams return False value = " \
                                                            + unicode(identifyDict.get(QtCore.QString("Band 1")))
            if featId != None:
                text = "All pasted features must fall on the centerline of a stream (dark blue color) \
in the base_streams layer. The feature in row " + unicode(featId+1) + " in the attribute table of the layer you \
copied from does not meet this constraint.  Please check all your points carefully and try again."
            else:
                text = "The added feature must fall on the centerline of a stream (dark blue color) \
in the base_streams layer.  Please make the base_streams layer visible on your map, and try again. \
If the base_streams layer is not open in your scenario, you may open it by clicking 'Add Raster Layer' \
on the toolbar or in the 'Layer' menu."
            QtGui.QMessageBox.warning(mainwindow, "Constraints Error:", text)
            # add the layer to the registry here if it is not already open
            return False # constraints have not been met
        else: 
            return True # base file opened and constraints have been met.'''
        
        # debugging
        print "Tools.shared.checkConstraints(): The rfilePath is " + rfilePath
        print "Tools.shared.checkConstraints(): The raster value for base_streams.tif is " \
                                                            + unicode(identifyDict.get(QtCore.QString("Band 1")))
        print "Tools.shared.checkConstraints(): The constraints were met and the return value is 'True'"
        
    elif editType == typesList[2]: # a terrestrial wildlife crossing
        point = geometry
        trafficLayerName = config.scenarioConstraintLayersFileNames[1]
        rfilePath = basePath + trafficLayerName
        rlayer = openHiddenRasterLayer(mainwindow, rfilePath) # returns false if the file failed to open
        if rlayer == False: # if the file failed to open, the constraints have not be met.
            return False
        result, identifyDict = rlayer.identify(point)
        print "Tools.shared.checkConstraints(): The raster value for base_traffic.tif is " \
                                                                + unicode(identifyDict.get(QtCore.QString("Band 1"))) 
        if not result: # if the identify method fails, we have not met constraints
            print "Tools.shared.checkConstraints(): base_traffic.tif identify failed"
            return False
        if unicode(identifyDict.get(QtCore.QString("Band 1"))) == u"null (no data)": # value for areas not on roads is null 
            print "base_traffic return False value = " + unicode(identifyDict.get(QtCore.QString("Band 1")))
            if featId != None:
                text = "All pasted features must fall on a road in the 'base_traffic' layer. \
The feature in row " + str(featId+1) + " in the attribute table of the layer you copied from does not meet \
this constraint.  Please check all your points carefully and try again."
            else:
                text = "The added feature must fall on a road in the 'base_traffic' layer. Please make \
the base_traffic layer visible on your map, and try again. If the base_traffic layer is not open \
in your scenario, you may open it by clicking 'Add Raster' on the toolbar or in the 'Layer' menu."
            QtGui.QMessageBox.warning(mainwindow, "Constraints Error:", text)
            # add the layer to the registry here if it is not already open
            return False # constraints have not been met
        else: return True # base file opened and constraints have been met.
    
        # debugging
        "Tools.shared.checkConstraints(): The rfilePath is " + rfilePath
        "Tools.shared.checkConstraints(): The raster value for base_traffic.tif is " \
                                                        + unicode(identifyDict.get(QtCore.QString("Band 1")))
        "Tools.shared.checkConstraints(): The constraints were met and the return value is 'True'"
    else: print "Tools.shared.checkConstraints(): Layer does not need constraints checked"
    
def openHiddenRasterLayer(mainwindow, rfilePath):
    ''' Open a raster layer without adding to the registry, so it is not visible to the user '''    
    info = QtCore.QFileInfo(rfilePath)
    rlayer = QgsRasterLayer(info.filePath(), info.completeBaseName())
    
    if not mainwindow.checkLayerLoadError(rlayer): return False
    else: return rlayer

def makeSelectRect (geom, point, transform):
        ''' Make a rectangle to use for selecting features '''
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
        else: print "Tools.shared.makeSelectRect(): .geometry unknown or None"
        
        # then convert to map coordinates
        topLeft = transform.toMapCoordinates(xTopLeft, yTopLeft)
        bottomRight = transform.toMapCoordinates(xBottomRight, yBottomRight)
        selectRect = QgsRectangle(topLeft, bottomRight)
        return selectRect

def resetIdNumbers(provider, geom):
        ''' Set the values of id field to start at 1 and finish with the number of features
            in the current editing shapefile.  Append p, l, pg for point, line and polygon.
        '''    
        # debugging
        print "Tools.shared.resetIDNumbers()"
        
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
            print "Tools.shared.resetIDNumbers(): The current feature id is " + str(feat.id())
            # A QgsAttributeMap is a pointer to a python dictionary where the key is
            # the feature id and the values are QtCore.QVariant objects.
            attrs = feat.attributeMap()
            for key, attr in attrs.iteritems():
                print "Tools.shared.resetIDNumbers(): The attribute value is " + attr.toString()
                if not attr.toString(): continue
                else: 
                    print "Tools.shared.resetIDNumbers(): We have the id field"
                    idString = unicode(feat.id()+1) + append
                    attrs[key] = QtCore.QVariant(idString)    
                    changedAttributes = {feat.id() : attrs} # create a "QgsChangedAttributesMap"
                    try:
                        provider.changeAttributeValues(changedAttributes)
                    except (IOError, OSError), e:
                        error = unicode(e)
                        print error     
                    break
                
def newRoadExists(mainwindow):
    ''' Check if the editing shapefile associated with a new road exists '''
    # debugging
    print "Tools.shared.newRoadExists()"
    
    newRoadEditFileName = config.editLayersBaseNames[1] + ".shp"
    scenarioDirectoryName = mainwindow.scenarioInfo.completeBaseName()
    newRoadEditFilePath = config.scenariosPath + scenarioDirectoryName + "/" + newRoadEditFileName
    newRoadEditFile = QtCore.QFile(newRoadEditFilePath)
    print "Tools.shared.newRoadExists(): The newRoadEditFileName is " + newRoadEditFileName
    print "Tools.shared.newRoadExists(): The newRoadEditFilePath is " + newRoadEditFilePath
    
    if newRoadEditFile.exists(): 
        print "Tools.shared.newRoadExists(): The new road exists"
        return True 
    else: 
        print "Tools.shared.newRoadExists(): The new road does not exist"
        return False
        
def snapToNewRoad(mainwindow, point):
    # debugging
    print "Tools.shared.snapToNewRoad()"
    
    # remember the original edit points layer
    pointsEditLayer = mainwindow.activeVLayer
    
    # set the editing shapefile for new roads to be the active layer
    newRoadEditFileBaseName = config.editLayersBaseNames[1]
    items = mainwindow.legend.findItems(newRoadEditFileBaseName, QtCore.Qt.MatchFixedString, 0)
    if len(items) > 0:
        item = items[0]
        newRoadEditFileId = item.layerId
        layer = QgsMapLayerRegistry.instance().mapLayer(newRoadEditFileId)
        mainwindow.canvas.setCurrentLayer(layer)
    else: print "Tools.shared.snapToNewRoad(): Could not find the new roads editing shapefile in the legend, although it exists!"
    
    # Now that the line layer is the active layer, snap the wildlife crossing point to the line.
    snapper = QgsMapCanvasSnapper(mainwindow.canvas)
    (retval, result) = snapper.snapToCurrentLayer(point, QgsSnapper.SnapToSegment)
    # Set the current layer back to the layer that was clicked (i.e. edit_scenario(points))
    mainwindow.canvas.setCurrentLayer(pointsEditLayer)
    
    # debugging
    print "Tools.shared.newRoadExists(): the length of items is " + str(len(items))
    print "Tools.shared.newRoadExists(): retval is " + str(retval)
    print "Tools.shared.newRoadExists(): result is "
    print result
    print "Tools.shared.newRoadExists(): The clicked points in device coordinates is " + str(point)
    transform = mainwindow.canvas.getCoordinateTransform()
    qgsPoint = transform.toMapCoordinates(point.x(), point.y())
    print "Tools.shared.newRoadExists(): The clicked point in map coords is " + str(qgsPoint)
    
    if result:
        print "Tools.shared.newRoadExists(): The snapped layer is " + str(result[0].layer.name())
        print "Tools.shared.newRoadExists(): The snapped point is " +  str(result[0].snappedVertex)
        print "Tools.shared.newRoadExists(): The snapped geometry is " + str(result[0].snappedAtGeometry)
        # Note that the result object will be destroyed by QGIS when this method ends,
        # so we need to make a new variable that contains deep copies of the information
        # we want.  !!It took a while for me to figure this out!!
        qgsPoint = result[0].snappedVertex
        x = qgsPoint.x()
        y = qgsPoint.y()
        snappedQgsPoint = QgsPoint(x, y)
        return snappedQgsPoint

#**************************************************************
''' Testing '''
#**************************************************************

def printFeatures(provider):       
        # debugging
        print "Tools.shared.printFeatures(): Testing"
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
                
def getEditingLayer(mainwindow, legend, editingLayerName):
    items = legend.findItems(editingLayerName, QtCore.Qt.MatchFixedString, 0)
    if len(items) == 0:
        QtGui.QMessageBox.warning(mainwindow, "Editing Layer Error:", "The editing layer "
                                                    + editingLayerName + " is not open in the layer list panel.")
        return False
    else: 
        return items[0].canvasLayer.layer()
                        
# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
#
# Conservation Assessment and Prioritization System (CAPS) Scenario Builder - An Open Source  
# GIS tool to create scenarios for environmental modeling.
#
#--------------------------------------------------------------------- 
# Copyright (C) 2011  Robert English: Daystar Computing (http://edaystar.com)
#---------------------------------------------------------------------
# 
# licensed under the terms of GNU GPLv3
# 
# This file is part of CAPS Scenario Builder.

# CAPS Scenario Builder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# CAPS Scenario Builder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with CAPS Scenario Builder.  If not, see <http://www.gnu.org/licenses/>..
#
#--------------------------------------------------------------------------------------------
# general python imports
import time
# PyQt4 includes for python bindings to QT
from PyQt4 import QtGui, QtCore 
# QGIS bindings for mapping functions
from qgis.core import *
from qgis.gui import *
# CAPS Scenario Builder application imports
import config

  
def listOriginalFeatures(mainwindow, editingLayerName):
        ''' Track original features so we can delete unsaved added features '''
        # debugging
        print "Tools.shared.listOriginalFeatures()"
        
        originalEditLayerFeats = []
        
        editingLayer = mainwindow.getLayerFromName(editingLayerName)
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
    
def checkSelectedLayer(mainwindow, scenarioEditType, activeLayerName, msgFlag=True):
        ''' 
            Check to make sure the user has selected the correct 
            editing layer when adding or pasting features 
        '''
        scenarioEditTypesList = config.scenarioEditTypesList

        # debugging
        print "Tools.shared.checkSelectedLayer()"
        print "Tools.shared.checkSelectedLayer(): scenarioEditType is " + scenarioEditType
        print "Tools.shared.checkSelectedLayer(): activeLayerName is " + activeLayerName

        if scenarioEditType in scenarioEditTypesList[:4] and activeLayerName != config.editLayersBaseNames[0]:
            print "Tools.shared.checkSelectedLayer(): edit points"
            if msgFlag:
                QtGui.QMessageBox.warning(mainwindow, "Scenario Editing Error", "You must select the layer \
named 'edit_scenario(points)' in the layer list panel to make the scenario edit type you have chosen.")
            return False
        elif scenarioEditType == scenarioEditTypesList[4] and activeLayerName != config.editLayersBaseNames[1]:
            print "Tools.shared.checkSelectedLayer(): edit lines"
            if msgFlag:
                QtGui.QMessageBox.warning(mainwindow, "Scenario Editing Error", "You must select the layer \
named 'edit_scenario(lines)' in the layer list panel to make the scenario edit type you have chosen.")
            return False
        elif scenarioEditType in scenarioEditTypesList[5:7] and activeLayerName != config.editLayersBaseNames[2]:
            print "Tools.shared.checkSelectedLayer(): edit polygons"
            if msgFlag:
                QtGui.QMessageBox.warning(mainwindow, "Scenario Editing Error", "You must select the layer \
named 'edit_scenario(polygons)' in the layer list panel to make the scenario edit type you have chosen.") 
            return False
        else: return True           

def getCurrentFeats(provider):
    # debugging
    print "Tools.shared.getCurrentFeats()"
    
    feat = QgsFeature()
    currentFeats = []
    allAttrs = provider.attributeIndexes()
    provider.select(allAttrs)
    while provider.nextFeature(feat):
        currentFeats.append(feat.id())
    return currentFeats

def getFeatsToDelete(provider, originalEditLayerFeats):
        # debugging
        print "Tools.shared.getFeatsToDelete()"
        
        currentFeats = getCurrentFeats(provider)
        featsToDelete = [i for i in currentFeats if i not in originalEditLayerFeats]
        return featsToDelete
      
def deleteEdits(mainwindow, editingLayerName, currentEditLayerFeats):
        ''' 
            Delete scenario edits added to editing layers since the last save.
            This method is called from Main.mainwindow.checkEditsState() and
            Main.mainwindow.pasteFeatures().
        '''
        # debugging
        print "Tools.shared.deleteEdits()"
        print "Tools.shared.deleteEdits(): editingLayerName is :" + editingLayerName
        print "Tools.shared.deleteEdits(): original features are: ", currentEditLayerFeats
        
        # Tools.shared.deleteEdits should be impossible to call with an editingLayerName that is not
        # an editing layer; however, if it ever were to be called, we could accidentally delete users' data.
        # The code below is insurance against such a serious bug. 
        if editingLayerName not in config.editLayersBaseNames:
            QtGui.QMessageBox.warning(mainwindow, "Deletion Error", "Tools.shared.deleteEdits() is attempting \
to delete edits from a vector layer other than an editing layer.")
            return

        # Now that we know we have an editing layer, get the provider from the name
        editingLayer = mainwindow.getLayerFromName(editingLayerName)
        if not editingLayer:
            return
        provider = editingLayer.dataProvider()
        
        # getFeatsToDelete returns a python list
        # If the currentEditLayer feats include some added since the last save then
        # this method will return the difference between the current edit layer state
        # and the state that was passed to this method.
        toDelete = getFeatsToDelete(provider, currentEditLayerFeats)
        
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
        
        # If we are back to the originalEditLayerFeats (i.e. state of last save) then 
        # set editDirty = False, otherwise set it to true
        currentFeats = getCurrentFeats(provider)
        if currentFeats == mainwindow.originalEditLayerFeats:
            mainwindow.editDirty = False
            print "Tools.shared.deleteEdits(): currentEditLayerFeats = originalEditLayerFeats; editDirty = False"
        else: 
            mainwindow.editDirty = True
            print "Tools.shared.deleteEdits(): currentEditLayerFeats != originalEditLayerFeats; editDirty = True"
            
        # debugging  
        print "Tools.shared.deleteEdits(): the remaining features are"
        printFeatures(provider)
        
        updateExtents(mainwindow, editingLayer, mainwindow.canvas)

def numberFeaturesAdded(activeVLayer, originalEditLayerFeats):
        # debugging
        print "Tools.shared.numberFeaturesAdded()"
        
        newFeats = activeVLayer.featureCount()- len(originalEditLayerFeats)
        return newFeats
    
def updateExtents(mainwindow, activeVLayer, canvas):
        # debugging
        print "Tools.shared.updateExtents()"
        print "The active layer feature count is " + str(activeVLayer.featureCount())
        vfilePath = unicode(activeVLayer.source())
        provider = activeVLayer.dataProvider()
        # I tried every update method I could find, but nothing other than closing
        # and reopening the layer seems to reset the layer extents on the canvas.  
        # So I do that here.
        vlayerName = unicode(activeVLayer.name())
        if vlayerName in config.editLayersBaseNames:
            layerId = activeVLayer.id()
            # if not the default color of red save the color so we can keep the same color when reopening the layer
            if not activeVLayer.rendererV2().symbols()[0].color() == QtGui.QColor(255, 0, 0, 255):
                mainwindow.coloredLayers[vlayerName] = activeVLayer.rendererV2().symbols()[0].color()
            # The method below removes the layer from the originalScenarioLayers list if the 
            # editing layer was in self.originalScenarioLayers and returns True if it was
            # or False if it was not.  The method resets the 
            # variables associated with the layer we are removing (to avoid runtime errors
            # associated with deleting underlying C++ objects)
            # and removes the layer from the registry.  Finally it removes the layer 
            # from the legend and updates the legend's layer set.
            inOriginalScenario = mainwindow.legend.removeLayerFromRegistry(activeVLayer, layerId)
            # now reopen the layer but give some time to be removed first
            time.sleep(0.1)
            mainwindow.openVectorLayer(vfilePath)
            
            # if the layer was in self.originalScenarioLayers then add it back 
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

def checkConstraints(mainwindow, qgsPoint, qPoint, featId = None):
    ''' 
        Checks constraints for scenario edits that are new features or pasted features.  Currently point and line  
        features are checked. If the feature can be snapped to a new road, constraints are considered met and the 
        geometry of the new feature is adjusted to be the snapped point. If the features have been pasted, 
        a "featId" is passed as a parameter.  Snapping is not used for checking pasted feature constraints
        
    '''
    # debugging
    print "Tools.shared.checkConstraints()"
    print "Tools.shared.checkConstraints(): The featId is " + str(featId)
    
    basePath = config.baseLayersPath
    editType = mainwindow.scenarioEditType
    typesList = config.scenarioEditTypesList
    
    ''' Check whether the qgs point falls on a stream for a culvert/bridge, dam or tidal restriction'''
    
    pointsList = [typesList[0], typesList[1], typesList[3]] # culverts/bridges, dams, tidal restrictions
    if editType in pointsList:
        if checkStreamsConstraint(mainwindow, basePath, qgsPoint, featId):
            return True
        else: return False

    ''' Check whether the point falls on an existing or new road for a terrestrial wildlife passage structure '''
      
    if editType == typesList[2]: # a terrestrial wildlife structure
        if checkRoadConstraints(mainwindow, basePath, qgsPoint, qPoint, editType, featId):
            return True
        else: return False
    
    ''' Check whether the first point of a new line falls on an existing or new road '''
        
    if editType == typesList[4]: # a new road; repeated code for clarity
        if checkRoadConstraints(mainwindow, basePath, qgsPoint, qPoint, editType, featId):
            return True
        else: return False
    else: print "Tools.shared.checkConstraints(): Layer does not need constraints checked"    
        
def checkStreamsConstraint(mainwindow, basePath, qgsPoint, featId):
    ''' Checks whether a new culvert/bridge, dam, or tidal restriction falls on a stream '''
    # debugging
    print "Tools.shared.checkStreamsConstraint()"
    
    # set some variables
    streamsFileName = config.scenarioConstraintLayersFileNames[0]
    rfilePath = basePath + streamsFileName
    
    # Load the raster layer, but do not add it to the registry so that it doesn't appear to the user.
    # Note we could check to see if the rlayer is already open and use it if it is, but 
    # we would still need this code if it was not open, so why bother?
    rlayer = openHiddenRasterLayer(mainwindow, rfilePath) # returns false if the file failed to open
    if rlayer == False:    # if the file failed to open, the constraints have not be met.
        # if the file failed to open, the constraints have not be met.
        return False
    
    # rlayer.identify returns a tuple with the result code (True or False) and a dictionary
    # with key = band and value = raster value for that band. We only have one band in the   
    # base_streams layer so the key = "Band 1"
    result, identifyDict = rlayer.identify(qgsPoint)
        
    # Now that we have a result, remove the layer from the registry
    QgsMapLayerRegistry.instance().removeMapLayer(rlayer.id())
     
    if not result: # if the identify method fails, we have not met constraints
        print "Tools.shared.checkStreamsConstraint(): base_streams.tif identify failed"
        return False
    
    if unicode(identifyDict.get(QtCore.QString("Band 1"))) != u"1": # stream centerlines have a value of 1
        print "Tools.shared.checkStreamsConstraint(): base_streams return False value = " \
                                                        + unicode(identifyDict.get(QtCore.QString("Band 1")))
        if featId != None:
            text = "All pasted features must fall on the centerline of a stream (dark blue color) \
in the base_streams layer. The feature in row " + unicode(featId+1) + " in the attribute table of the layer you \
copied from does not meet this constraint.  Please check all your points carefully and try again."
        else:
            text = "The added feature must fall on the centerline of a stream (dark blue color) \
in the base_streams layer. If the base_streams layer is not open in your scenario, you may open it by choosing \
'Add Raster Layer' from the toolbar or the 'Layer' menu.\n\n\
If you are adding a culvert/bridge to a new road, please click as close as possible\
to the intersection of the stream's center and the new road so that the culvert will 'snap' to the new road."

        QtGui.QMessageBox.warning(mainwindow, "Constraints Error:", text)
        # add the layer to the registry here if it is not already open
        return False # constraints have not been met
    else: 
        return True # base file opened and constraints have been met because the value was "1".
    
    # debugging
    print "Tools.shared.checkStreamsConstraint(): The rfilePath is " + rfilePath
    print "Tools.shared.checkStreamsConstraint(): The constraints were met and the return value is 'True'"
    
def checkRoadConstraints(mainwindow, basePath, qgsPoint, qPoint, editType, featId):
    ''' Checks whether a new terrestrial wildlife structure or new road falls on an existing or new road '''
    # debugging
    print "Tools.shared.checkRoadConstraints()" 
    
    # set variables
    trafficLayerName = config.scenarioConstraintLayersFileNames[1]
    rfilePath = basePath + trafficLayerName
    typesList = config.scenarioEditTypesList
    
    # Load the raster layer, but do not add it to the registry so that it doesn't appear to the user.
    # Note we could check to see if the rlayer is already open and use it if it is, but 
    # we would still need this code if it was not open, so why bother?
    rlayer = openHiddenRasterLayer(mainwindow, rfilePath) # warns and returns false if the file failed to open
    if rlayer == False: # if the file failed to open, the constraints have not be met.
        return False
    result, identifyDict = rlayer.identify(qgsPoint)
        
    # Now that we have a result, remove the layer from the registry
    QgsMapLayerRegistry.instance().removeMapLayer(rlayer.id())

    if not result: # if the identify method fails, we have not met constraints
        print "Tools.shared.checkRoadConstraints(): base_traffic.tif identify failed"
        return False
    
    # debugging
    print "Tools.shared.checkRoadConstraints(): The raster value for base_traffic.tif is " \
                                                            + unicode(identifyDict.get(QtCore.QString("Band 1"))) 
    # value for areas not on roads is null
    if unicode(identifyDict.get(QtCore.QString("Band 1"))) == u"null (no data)":  
        # The point (a wildlife structure or the beginning point of a new road) is not on an existing road 
        # so now see if the point can be snapped to a "new" road (i.e. a road created by the user).
        # We only check snapping for new features NOT pasted features
        if featId == None and newRoadExists(mainwindow):
            snappedQgsPoint = snapToNewRoad(mainwindow, qPoint)
            print "Tools.shared.checkRoadConstraints(): The returned snappedPoint is " + str(snappedQgsPoint)
            if snappedQgsPoint:
                # Constraints for new features are satisfied because snapped point is on a new road. 
                # Set the new wildlife structures's point or the first point of a new road
                # to be the snapped point on the previously saved new road.
                if editType == typesList[2]: # wildlife crossing
                    mainwindow.toolAddPoints.qgsPoint = snappedQgsPoint
                    return True
                elif editType == typesList[4]: # new road
                    mainwindow.toolAddLinesPolygons.qgsPoint = snappedQgsPoint
                    return True
        # constraints for a new wildlife structure or new road have not been met by by 
        # being/starting on an existing road, or by snapping to a new road or  so inform the user.
        if featId == None:  
            QtGui.QMessageBox.warning(mainwindow, "Constraints Error:", "The added feature must fall \
on a road in the base_traffic layer, or it must be close to a 'new' road that you have created so that it \
can be 'snapped' to the new road. If the base_traffic layer is not open in your scenario, you may open it \
by clicking 'Add Raster' on the toolbar or in the 'Layer' menu. You may see new roads you have created by \
making the edit_scenario(lines) layer visible and zooming to its extents.")
            return False
        elif featId and editType == typesList[2]: # constraints for a pasted structure have not been met
            QtGui.QMessageBox.warning(mainwindow, "Constraints Error:", "All pasted features must fall \
on a road in the 'base_traffic' layer. The feature in row " + str(featId+1) + " in the attribute table of \
the layer you copied from does not meet this constraint.  Please check all your points carefully and try again.")
            return False # constraints have not been met
        elif featId and editType == typesList[4]: # we check beginning and end point for pasted roads, so no msgbox here.
            return False
    else: return True # Constraints have been met. The wildlife structure or new road's beginning is on an existing road.

    # debugging
    print "Tools.shared.checkRoadConstraints(): The rfilePath is " + rfilePath
    print "Tools.shared.checkRoadConstraints(): The raster value for base_traffic.tif is " \
                                                    + unicode(identifyDict.get(QtCore.QString("Band 1")))
    print "Tools.shared.checkRoadConstraints(): The constraints were met and the return value is 'True'"   

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
        
def snapToNewRoad(mainwindow, qPoint):
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
    else: print "Tools.shared.snapToNewRoad(): Could not find the new roads editing shapefile in the legend"
    
    # Now that the line layer is the active layer, snap the wildlife or culvert/bridge point to the line.
    snapper = QgsMapCanvasSnapper(mainwindow.canvas)
    (retval, result) = snapper.snapToCurrentLayer(qPoint, QgsSnapper.SnapToSegment)
    # Set the current layer back to the layer that was clicked (i.e. edit_scenario(points))
    mainwindow.canvas.setCurrentLayer(pointsEditLayer)
    
    # debugging
    print "Tools.shared.snapToNewRoad(): the length of items is " + str(len(items))
    print "Tools.shared.snapToNewRoad(): retval is " + str(retval)
    print "Tools.shared.snapToNewRoad(): result is "
    print result
    print "Tools.shared.snapToNewRoad(): The clicked points in device coordinates is " + str(qPoint)
    transform = mainwindow.canvas.getCoordinateTransform()
    qgsPoint = transform.toMapCoordinates(qPoint.x(), qPoint.y())
    print "Tools.shared.snapToNewRoad(): The clicked point in map coords is " + str(qgsPoint)
    
    if result:
        print "Tools.shared.snapToNewRoad(): The snapped layer is " + str(result[0].layer.name())
        print "Tools.shared.snapToNewRoad(): The snapped point is " +  str(result[0].snappedVertex)
        print "Tools.shared.snapToNewRoad(): The snapped geometry is " + str(result[0].snappedAtGeometry)
        # Note that the result object will be destroyed by QGIS when this method ends,
        # so we need to make a new variable that contains deep copies of the information
        # we want.  !!It took a while for me to figure this out!!
        qgsPoint = result[0].snappedVertex
        x = qgsPoint.x()
        y = qgsPoint.y()
        snappedQgsPoint = QgsPoint(x, y)
        return snappedQgsPoint
    else: return False # will return false without this line, but for clarity

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
                        
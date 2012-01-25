# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
# 
# Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
# 
#---------------------------------------------------------------------
# Visor Geográfico
#
# Copyright (C) 2007  Ecotrust
# Copyright (C) 2007  Aaron Racicot
# Copyright (C) 2009  Germ�n Carrillo (http://geotux.tuxfamily.org)
# Copyright (C) 2011  Robert English (bobeng@gmail.com; http://edaystar.com)
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
# General system includes
from os.path import isfile
# PyQt4 includes for python bindings to QT
from PyQt4 import QtCore, QtGui
# QGIS bindings for mapping functions
from qgis.core import * #QGis, QgsMapLayerRegistry
from qgis.gui import * #QgsMapCanvasLayer
# CAPS application imports
import config

#icons for the legend are compiled in resources_rc.py
resources_prefix = ":/images/"

class LegendItem(QtGui.QTreeWidgetItem):
    """ Provide a widget to show and manage the properties of one single layer """
    def __init__(self, parent, canvasLayer):
        QtGui.QTreeWidgetItem.__init__(self)
        self.legend = parent
        self.canvasLayer = canvasLayer
        self.canvasLayer.layer().setLayerName(self.legend.normalizeLayerName(unicode(self.canvasLayer.layer().name())))
        self.setText(0, self.canvasLayer.layer().name())
        self.isVect = (self.canvasLayer.layer().type() == 0) # 0: Vector, 1: Raster
        self.layerId = self.canvasLayer.layer().id()

        if self.isVect:
            geom = self.canvasLayer.layer().dataProvider().geometryType()

        ''' The 4 lines below set whether layers are visible when first opened '''
        #self.setCheckState(0, QtCore.Qt.Checked)
        self.setCheckState(0, QtCore.Qt.Unchecked)
        #self.canvasLayer.setVisible(True)
        self.canvasLayer.setVisible(False)

        pm = QtGui.QPixmap(20, 20)
        icon = QtGui.QIcon()

        if self.isVect:
            if geom == 1 or geom == 4 or geom == 8 or geom == 11: # Point
                icon.addPixmap(QtGui.QPixmap(resources_prefix + "mIconPointLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            elif geom == 2 or geom == 5 or geom == 9 or geom == 12: # Polyline
                icon.addPixmap(QtGui.QPixmap(resources_prefix + "mIconLineLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            elif geom == 3 or geom == 6 or geom == 10 or geom == 13: # Polygon
                icon.addPixmap(QtGui.QPixmap(resources_prefix + "mIconPolygonLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            else: # Not a valid WKT Geometry
                geom = self.canvasLayer.layer().geometryType() # QGis Geometry
                if geom == 0: # Point
                    icon.addPixmap(QtGui.QPixmap(resources_prefix + "mIconPointLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                elif geom == 1: # Line
                    icon.addPixmap(QtGui.QPixmap(resources_prefix + "mIconLineLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                elif geom == 2: # Polygon
                    icon.addPixmap(QtGui.QPixmap(resources_prefix + "mIconPolygonLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                else: raise RuntimeError, u'Unknown geometry: ' + unicode(geom)
            self.vectorLayerSymbology(self.canvasLayer.layer())
        else:
            self.canvasLayer.layer().thumbnailAsPixmap(pm)
            icon.addPixmap(pm)
            self.child = QtGui.QTreeWidgetItem(self)
            iconChild = QtGui.QIcon()
            iconChild.addPixmap(self.canvasLayer.layer().legendAsPixmap().scaled(15, 15, QtCore.Qt.KeepAspectRatio))
            self.child.setSizeHint (0, QtCore.QSize(15, 15))
            self.child.setIcon(0, iconChild)

        self.setIcon(0, icon)

        self.setToolTip(0, self.canvasLayer.layer().publicSource())
        layerFont = QtGui.QFont()
        layerFont.setBold(True)
        self.setFont(0, layerFont)

    def nextSibling(self):
        """ Return the next layer item """
        return self.legend.nextSibling(self)

    def storeAppearanceSettings(self):
        """ Store the appearance of the layer item """
        self.__itemIsExpanded = self.isExpanded()

    def restoreAppearanceSettings(self):
        """ Restore the appearance of the layer item """
        self.setExpanded(self.__itemIsExpanded)

    def vectorLayerSymbology(self, vlayer):
        ''' Set the child icon that shows layer color '''
        rendererV2 = vlayer.rendererV2()
        symbol = rendererV2.symbols()[0]

        # a QImage object
        image = symbol.bigSymbolPreviewImage()
        pixmap = QtGui.QPixmap(100, 100)
        pixmap = pixmap.fromImage(image) 

        self.changeSymbologySettings(vlayer, pixmap)
        
    def changeSymbologySettings(self, theMapLayer, pixmap):
        ''' Update the symbology settings on loading or changing layer color '''
        if not theMapLayer: return

        # Remove previous symbology items
        self.takeChildren()
        self.child = QtGui.QTreeWidgetItem(self)
        iconChild = QtGui.QIcon()
        iconChild.addPixmap(pixmap)
        self.child.setIcon(0, iconChild)

        childFont = QtGui.QFont()
        childFont.setPointSize(9)
        self.child.setFont(0, childFont)

class Legend(QtGui.QTreeWidget):
    """
      Provide a widget that manages map layers and their symbology as tree items
    """
    def __init__(self, parent):
        QtGui.QTreeWidget.__init__(self, parent)
        
        self.mainwindow = parent
        self.canvas = parent.canvas
        self.layers = self.getLayerSet()
        
        self.bMousePressedFlag = False
        self.itemBeingMoved = None

        # QTreeWidget properties
        self.setSortingEnabled(False)
        self.setDragEnabled(False)
        self.setAutoScroll(True)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # added by be
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        #self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
 
        self.connect(self, QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
            self.showMenu)
        self.connect(QgsMapLayerRegistry.instance(), QtCore.SIGNAL("layerWasAdded(QgsMapLayer *)"),
            self.addLayerToLegend)
        #self.connect(QgsMapLayerRegistry.instance(), QtCore.SIGNAL("removedAll()"),
            #self.removeAll)
        self.connect(self, QtCore.SIGNAL("itemChanged(QTreeWidgetItem *,int)"),
            self.updateLayerStatus) 
        self.connect(self, QtCore.SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"),
            self.currentItemChanged)

    def setCanvas(self, canvas):
        """ Set the base canvas """
        self.canvas = canvas

    def showMenu(self, pos):
        """ Show a context menu for the active layer in the legend """
        item = self.itemAt(pos)
        if item:
            if self.isLegendLayer(item):
                self.setCurrentItem(item)
                self.menu = self.getMenu(item.isVect, item.canvasLayer)
                self.menu.popup(QtCore.QPoint(self.mapToGlobal(pos).x() + 5, self.mapToGlobal(pos).y()))

    def getMenu(self, isVect, canvasLayer):
        """ Create a context menu for a layer """
        menu = QtGui.QMenu()
        menu.addAction(QtGui.QIcon(resources_prefix + "mActionZoomToLayer.png"), 
                                                "&Zoom to layer extent", self.zoomToLayer)

        if isVect :
            menu.addAction(QtGui.QIcon(resources_prefix + "symbology.png"), 
                                                        "&Symbology...", self.layerSymbology)

        menu.addSeparator()
        menu.addAction(QtGui.QIcon(resources_prefix + "collapse.png"), "&Collapse all", self.collapseAll)
        menu.addAction(QtGui.QIcon(resources_prefix + "expand.png"), "&Expand all", self.expandAll)

        menu.addSeparator()
        menu.addAction(QtGui.QIcon(resources_prefix + "mActionRemoveLayer.png"), "&Remove layer", self.removeCurrentLayer)
        return menu

    def mousePressEvent(self, event):
        """ Mouse press event to manage the layers drag """
        p = QtCore.QPoint(event.pos())
        item = self.itemAt(p)
 
        if (item and item != self.currentItem()): 
            print "legend.mousePressEvent" 
            if self.mainwindow.appStateChanged("legendMousePress") == "Cancel": return
        if (event.button() == QtCore.Qt.LeftButton):
            self.lastPressPos = event.pos()
            self.bMousePressedFlag = True
        QtGui.QTreeWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """ Mouse move event to manage the layers drag """
        if (self.bMousePressedFlag):
            # Set the flag back such that the else if(mItemBeingMoved)
            # code part is passed during the next mouse moves
            self.bMousePressedFlag = False

            # Remember the item that has been pressed
            item = self.itemAt(self.lastPressPos)
            if (item):
                if (self.isLegendLayer(item)):
                    self.itemBeingMoved = item
                    self.storeInitialPosition() # Store the initial layers order
                    self.setCursor(QtCore.Qt.SizeVerCursor)
                else:
                    self.setCursor(QtCore.Qt.ForbiddenCursor)
        elif (self.itemBeingMoved):
            p = QtCore.QPoint(event.pos())
            self.lastPressPos = p

            # Change the cursor
            item = self.itemAt(p)
            origin = self.itemBeingMoved
            dest = item

            if not item: self.setCursor(QtCore.Qt.ForbiddenCursor)

            if (item and (item != self.itemBeingMoved)):
                if (self.yCoordAboveCenter(dest, event.y())): # Above center of the item
                    if self.isLegendLayer(dest): # The item is a layer
                        if (origin.nextSibling() != dest):
                            self.moveItem(dest, origin)
                        self.setCurrentItem(origin)
                        self.setCursor(QtCore.Qt.SizeVerCursor)
                    else:
                        self.setCursor(QtCore.Qt.ForbiddenCursor)
                else: # Below center of the item
                    if self.isLegendLayer(dest): # The item is a layer
                        if (self.itemBeingMoved != dest.nextSibling()):
                            self.moveItem(origin, dest)
                        self.setCurrentItem(origin)
                        self.setCursor(QtCore.Qt.SizeVerCursor)
                    else:
                        self.setCursor(QtCore.Qt.ForbiddenCursor)

    def mouseReleaseEvent(self, event):
        """ Mouse release event to manage the layers drag """
        QtGui.QTreeWidget.mouseReleaseEvent(self, event)
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.bMousePressedFlag = False

        if (not self.itemBeingMoved): return

        dest = self.itemAt(event.pos())
        origin = self.itemBeingMoved
        if ((not dest) or (not origin)): # Release out of the legend
            self.checkLayerOrderUpdate()
            return

        self.checkLayerOrderUpdate()
        self.itemBeingMoved = None

    def addLayerToLegend(self, mapLayer):
        """ Slot. Create and add a legend item based on a layer """
        legendLayer = LegendItem(self, QgsMapCanvasLayer(mapLayer))
        self.addLayer(legendLayer)

    def addLayer(self, legendLayer):
        """ Add a legend item to the legend widget """
        self.insertTopLevelItem (0, legendLayer)
        
        # be moved to here to slow active layer changed signal
        self.updateLayerSet()
        self.expandItem(legendLayer)
        self.setCurrentItem(legendLayer)

    def updateLayerStatus(self, item):
        """ Update the layer status """
        # debugging
        print "Main.legend.updateLayerStatus()"
        
        if (item):
            if self.isLegendLayer(item): # Is the item a layer item?
                print "Main.legend.updateLayerStatus(): This is a legend layer item" 
                for i in self.layers:
                    if i.layer().id() == item.layerId:
                        if item.checkState(0) == QtCore.Qt.Unchecked:
                            print "Main.legend.updateLayerStatus(): is not checked"
                            i.setVisible(False)
                        else:
                            print "Main.legend.updateLayerStatus(): is checked"
                            i.setVisible(True)
                        self.canvas.setLayerSet(self.layers)
                        return
              
                print "Main.legend.updateLayerStatus(): This is not a legend layer item"
                print "Main.legend.updateLayerStatus(): The item's text is " + str(item.text)
                  
    def currentItemChanged(self, newItem, oldItem):
        """ Slot. Capture a new currentItem and emit a SIGNAL to inform the new type 
            It could be used to activate/deactivate GUI buttons according the layer type
        """
        layerType = None
        if self.currentItem():
            if self.isLegendLayer(newItem):
                layerType = newItem.canvasLayer.layer().type()
                self.canvas.setCurrentLayer(newItem.canvasLayer.layer())
            else:
                layerType = newItem.parent().canvasLayer.layer().type()
                self.canvas.setCurrentLayer(newItem.parent().canvasLayer.layer())

        # be Create a Python "short-circuit" signal (note no "SIGNAL" parentheses)
        self.emit(QtCore.SIGNAL("activeLayerChanged"), layerType)

    def zoomToLayer(self):
        """ Slot. Manage the zoomToLayer action in the context Menu """
        self.zoomToLegendLayer(self.currentItem())
 
    def removeCurrentLayer(self):
        """ Slot. Manage the removeCurrentLayer action in the context Menu """
        # debugging
        print "Mainwindow.legend.removeCurrentLayer()"
       
        # be Check app state and give user a chance to cancel.
        if self.mainwindow.appStateChanged("removeCurrentLayer") == "Cancel": return
            
        # Check and warn on removing an editing layer
        name = self.currentItem().canvasLayer.layer().name()
        if name in config.editLayersBaseNames:
            reply = QtGui.QMessageBox.warning(self, "Warning!", "Removing '" + name + "' \
from the legend will cause all that layer's files and any associated 'Export Scenario' file to be deleted from \
the file system. All changes to these files will be lost. Do you want to delete this file(s)?", 
                                                        QtGui.QMessageBox.No|QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.No: return # user canceled so don't remove layer
            else: 
                # user chose ok so we can delete the file but must remove from registry first!
                layer = self.currentItem().canvasLayer.layer()
                name = layer.name() 
                layerId = self.currentItem().canvasLayer.layer().id()
                # get the path before we set the activeVLayer to none
                editFilePath = self.mainwindow.activeVLayer.source()
                # since we are deleting an editing layer we should be safe and 
                # remove any exported scenario files.
                self.mainwindow.deleteExportScenarioFile()
                # remove the layer from the registry
                self.removeEditLayerFromRegistry(layer, layerId, True)
                # and delete the editing layer
                self.deleteEditingLayer(editFilePath)
                # if the editing layer is edit_scenario(polygons) then reset the flag
                if name ==config.editLayersBaseNames[2]:
                    self.mainwindow.editingPolygon = False
                return # we are done deleting the layer so return
        # Note that this section handles a layer whether it is a raster or vector
        # and not an editing layer.
        # Remove the layer from the "mainwindow.originalScenarioLayers" list and 
        # set the scenario as dirty, since it has been changed.
        if self.currentItem().canvasLayer.layer() in self.mainwindow.originalScenarioLayers:
            layerToDelete = self.currentItem().canvasLayer.layer()
            print "length originalScenarioLayers before removal " + str(len(self.mainwindow.originalScenarioLayers))
            self.mainwindow.originalScenarioLayers.remove(layerToDelete)
            print "length originalScenarioLayers after removal " + str(len(self.mainwindow.originalScenarioLayers))
            self.mainwindow.scenarioDirty = True
            print "layer was removed from originalScenarioLayers"
            
        # be Layer ready to be removed so reset active layer variables to none or we could
        #  get C++ object deleted runtime errors from deleting an object underlying a python variable.
        self.setActiveLayerVariables()
        
        # remove layer from the registry
        layerId = self.currentItem().canvasLayer.layer().id()
        QgsMapLayerRegistry.instance().removeMapLayer(layerId)
        self.removeLegendLayer(self.currentItem())
        self.updateLayerSet()

    def layerSymbology(self):
        """ Change the features color of a vector layer """
        legendLayer = self.currentItem()
        
        if legendLayer.isVect == True:
            geom = legendLayer.canvasLayer.layer().geometryType() # QGis Geometry
            for i in self.layers:
                if i.layer().id() == legendLayer.layerId:
                    color = QtGui.QColorDialog.getColor(i.layer().rendererV2().symbols()[ 0 ].color(), self.mainwindow)
                    break

            if color.isValid():
                legendLayer.canvasLayer.layer().rendererV2().symbols()[0].setColor(color)
                self.refreshLayerSymbology(legendLayer.canvasLayer.layer())

    def zoomToLegendLayer(self, legendLayer):
        """ Zoom the map to a layer extent """
        for i in self.layers:
            if i.layer().id() == legendLayer.layerId:
                extent = i.layer().extent()
                extent.scale(1.05)
                self.canvas.setExtent(extent)
                self.canvas.refresh()
                break
 
    def removeLegendLayer(self, legendLayer):
        """ Remove a layer item in the legend """
        if self.topLevelItemCount() == 1: self.clear()
        else: # Manage the currentLayer before the remove
            indice = self.indexOfTopLevelItem(legendLayer)
            if indice == 0:
                newCurrentItem = self.topLevelItem(indice + 1)
            else:
                newCurrentItem = self.topLevelItem(indice - 1)

            self.setCurrentItem(newCurrentItem)
            self.takeTopLevelItem(self.indexOfTopLevelItem(legendLayer))

    def setStatusForAllLayers(self):
        """ Show/Hide all layers in the map """
        # debugging
        print "Main.legend.setStatusForAllLayers()"
        # Block SIGNALS to avoid setLayerSet for each item status changed
        self.blockSignals(True)

        for i in range(self.topLevelItemCount()):
            if self.topLevelItem(i).checkState(0) == QtCore.Qt.Checked:
                self.topLevelItem(i).canvasLayer.setVisible(True)
            else: self.topLevelItem(i).canvasLayer.setVisible(False)

        self.blockSignals(False)

        self.updateLayerSet() # Finally, update the layer set

    def updateLayerSet(self):
        """ Update the LayerSet and set it to canvas """
        self.layers = self.getLayerSet()
        self.canvas.setLayerSet(self.layers)
 
    def getLayerSet(self):
        """ Get the LayerSet by reading the layer items in the legend """
        layers = []
        for i in range(self.topLevelItemCount()):
            layers.append(self.topLevelItem(i).canvasLayer)
        return layers

    def activeLayer(self):
        """ Return the selected layer """
        if self.currentItem():
            if self.isLegendLayer(self.currentItem()):
                return self.currentItem().canvasLayer
            else: return self.currentItem().parent().canvasLayer
        else: return None

    def collapseAll(self):
        """ Collapse all layer items in the legend """
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            self.collapseItem(item)

    def expandAll(self):
        """ Expand all layer items in the legend """
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            self.expandItem(item)

    def isLegendLayer(self, item):
        """ Check if a given item is a layer item """
        return not item.parent()

    def storeInitialPosition(self):
        """ Store the layers order """
        self.__beforeDragStateLayers = self.getLayerIDs()

    def getLayerIDs(self):
        """ Return a list with the layers ids """
        layers = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            layers.append(item.layerId)
        return layers

    def nextSibling(self, item):
        """ Return the next layer item based on a given item """
        for i in range(self.topLevelItemCount()):
            if item.layerId == self.topLevelItem(i).layerId: break
        if i < self.topLevelItemCount(): return self.topLevelItem(i + 1)                                           
        else: return None
 
    def moveItem(self, itemToMove, afterItem):
        """ Move the itemToMove after the afterItem in the legend """
        itemToMove.storeAppearanceSettings() # Store settings in the moved item
        self.takeTopLevelItem(self.indexOfTopLevelItem(itemToMove))
        self.insertTopLevelItem(self.indexOfTopLevelItem(afterItem) + 1, itemToMove)
        itemToMove.restoreAppearanceSettings() # Apply the settings again

    def checkLayerOrderUpdate(self):
        """
            Check if the initial layers order is equal to the final one.
            This is used to refresh the legend in the release event.
        """
        self.__afterDragStateLayers = self.getLayerIDs()
        if self.__afterDragStateLayers != self.__beforeDragStateLayers: self.updateLayerSet()

    def yCoordAboveCenter(self, legendItem, ycoord):
        """
            Return a bool to know if the ycoord is in the above center of the legendItem

            legendItem: The base item to get the above center and the below center
            ycoord: The coordinate of the comparison
        """
        rect = self.visualItemRect(legendItem)
        height = rect.height()
        top = rect.top()
        mid = top + (height / 2)
        if (ycoord > mid):  return False # Bottom, remember the y-coordinate increases downwards
        else: return True # Top

    def normalizeLayerName(self, name):
        """ Create an alias to put in the legend and avoid to repeat names """
        # Remove the extension
        if len(name) > 4:
            if name[-4] == '.': name = name[:-4]
        return self.createUniqueName(name)

    def createUniqueName(self, name):
        """ Avoid to repeat layers names """
        import re
        name_validation = re.compile("\s\(\d+\)$", re.UNICODE) # Strings like " (1)"

        bRepetida = True
        i = 1
        while bRepetida:
            bRepetida = False

            # If necessary add a sufix like " (1)" to avoid to repeat names in the legend
            for j in range(self.topLevelItemCount()):
                item = self.topLevelItem(j)
                if item.text(0) == name:
                    bRepetida = True
                    if name_validation.search(name): # The name already have numeration
                        name = name[ :-4 ]  + ' (' + unicode(i) + ')'
                    else: # Add numeration because the name doesn't have it
                        name = name + ' (' + unicode(i) + ')'
                    i += 1
        return name

    def refreshLayerSymbology(self, layer):
        """ Refresh the layer symbology """
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if layer.id() == item.layerId:
                item.vectorLayerSymbology(layer)
                self.canvas.refresh()
                break

    def removeLayers(self, layerIds):
        """ Remove layers from their ids. For plugins. """
        for layerId in layerIds:
            QgsMapLayerRegistry.instance().removeMapLayer(layerId)

            # Remove the legend item
            self.removeLayerFromLegendById(layerId)

        self.updateLayerSet()
        
    def deleteEditingLayer(self, editFilePath):
        ''' Removes an editing shapefile and any associated "Export Scenario" file. '''
        # debugging
        print "Main.legend.deleteEditingLayer()"
        print "editFilePath is " + editFilePath

        editFile = QtCore.QFile(editFilePath)
        if editFile.exists():
            print "editFile exists is True"
            writer = QgsVectorFileWriter.deleteShapeFile(editFilePath)
        if not writer: # writer returns true if delete successful
            QtGui.QMessageBox.warning(self, "File Error", "The editing shapefile could not be deleted. \
Please check if it is open in another program and try again.")
            return False
        else: return True
     
    def removeEditLayerFromRegistry(self, layer, layerId, removeCurrentLayer = False):
        ''' Remove an editing layer from the registry, but clean up first. '''
        # debugging
        print "Main.legend.removeEditLayerFrom Registry()"
        
        inOriginalScenario = False
        originalScenarioLayers = self.mainwindow.originalScenarioLayers
        if layer in originalScenarioLayers:
            print "length originalScenarioLayers before removal " + str(len(originalScenarioLayers))
            originalScenarioLayers.remove(layer)
            self.mainwindow.scenarioDirty = True
            print 'The activeVLayer was removed from the originalScenarioLayers'
            print 'length originalScenarioLayers after removal ' + str(len(originalScenarioLayers))
            inOriginalScenario = True
        
        # This method is called by self.removeCurrentLayer() and Tools.shared.updateExtents().
        # The method is also called by Main.mainwindow.checkScenarioState(), where the layer to 
        # be removed is probably not the activeVLayer. In fact the activeVLayer
        # could be "None," or the active layer could be a raster. If the layer is the 
        # activeVLayer, we need to reset activeVLayer variables after removing the layer from the 
        # registry, so we need to record the layer id of the activeVLayer before we delete it.
        activeVLayerId = None
        if self.mainwindow.activeVLayer:
            activeVLayerId = self.mainwindow.activeVLayer.id()
        
        # Remove the layer from the registry
        QgsMapLayerRegistry.instance().removeMapLayer(layerId)
        
        # if the removed layer is the current activeVLayer, reset all associated variables
        if activeVLayerId == layerId:
            self.setActiveLayerVariables() 
       
        # If the calling action is removeCurrent layer, we need to let signals proceed normally.
        # If the calling action is shared.updateExtents or mainwindow.chkScenarioState then
        # we do not because either a new layer will immediately load or the app will close.
        if removeCurrentLayer:
            # Layer is successfully removed from registry so remove it from legend.
            self.removeLayerFromLegendById(layerId)
            self.updateLayerSet()
        else:
            self.blockSignals(True)
            self.removeLayerFromLegendById(layerId)
            self.updateLayerSet()
            self.blockSignals(False)
            return inOriginalScenario
 
    def setActiveLayerVariables(self):
        ''' Reset the variable to avoid c++ runtime errors for deleted objects '''
        # debugging
        print "Main.legend.setActiveLayerVariables()"
        
        self.mainwindow.activeRLayer = None
        self.mainwindow.activeVLayer = None 
        self.mainwindow.geom = None # reset activeVLayer information
        self.mainwindow.provider = None
        self.mainwindow.layerType = None

    def removeLayerFromLegendById(self, layerId):
        # Remove the legend item
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if layerId == item.layerId:
                self.removeLegendLayer(item)
                break
            
    def removeAll(self):
        """ Remove all legend items """
        self.clear()
        self.updateLayerSet()         
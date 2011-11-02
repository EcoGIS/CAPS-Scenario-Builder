# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
# 
#Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
# 
#---------------------------------------------------------------------
#Visor Geogr�fico
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
# General system includes
from os.path import isfile
# PyQt4 includes for python bindings to QT
# used this import format to be consistent with the Qt Designer ui file format
# and because it works better with eclipse
from PyQt4 import QtCore, QtGui
# QGIS bindings for mapping functions
from qgis.core import * #QGis, QgsMapLayerRegistry
from qgis.gui import * #QgsMapCanvasLayer
# CAPS application imports
from dlglayerproperties import LayerProperties
import config
import Tools.shared

#icons for the legend are compiled in resources_rc.py
resources_prefix = ":/images/"

class LegendItem( QtGui.QTreeWidgetItem ):
    """ Provide a widget to show and manage the properties of one single layer """
    def __init__( self, parent, canvasLayer ):
        QtGui.QTreeWidgetItem.__init__( self )
        self.legend = parent
        self.canvasLayer = canvasLayer
        self.canvasLayer.layer().setLayerName( self.legend.normalizeLayerName
                                               ( unicode( self.canvasLayer.layer().name() ) ) )
        self.setText( 0, self.canvasLayer.layer().name() )
        self.isVect = ( self.canvasLayer.layer().type() == 0 ) # 0: Vector, 1: Raster
        self.layerId = self.canvasLayer.layer().getLayerID()

        if self.isVect:
            geom = self.canvasLayer.layer().dataProvider().geometryType()

        #self.setCheckState( 0, QtCore.Qt.Checked )
        self.setCheckState( 0, QtCore.Qt.Unchecked)
        #self.canvasLayer.setVisible( visible )
        self.canvasLayer.setVisible(False)

        pm = QtGui.QPixmap( 20, 20 )
        icon = QtGui.QIcon()

        if self.isVect:
            if geom == 1 or geom == 4 or geom == 8 or geom == 11: # Point
                icon.addPixmap( QtGui.QPixmap( resources_prefix + "mIconPointLayer.png" ), QtGui.QIcon.Normal, QtGui.QIcon.On)
            elif geom == 2 or geom == 5 or geom == 9 or geom == 12: # Polyline
                icon.addPixmap( QtGui.QPixmap( resources_prefix + "mIconLineLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            elif geom == 3 or geom == 6 or geom == 10 or geom == 13: # Polygon
                icon.addPixmap( QtGui.QPixmap( resources_prefix + "mIconPolygonLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            else: # Not a valid WKT Geometry
                geom = self.canvasLayer.layer().geometryType() # QGis Geometry
                if geom == 0: # Point
                    icon.addPixmap( QtGui.QPixmap( resources_prefix + "mIconPointLayer.png" ), QtGui.QIcon.Normal, QtGui.QIcon.On)
                elif geom == 1: # Line
                    icon.addPixmap( QtGui.QPixmap( resources_prefix + "mIconLineLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                elif geom == 2: # Polygon
                    icon.addPixmap( QtGui.QPixmap( resources_prefix + "mIconPolygonLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                else:
                    raise RuntimeError, 'Unknown geometry: ' + str( geom )
            #self.vectorLayerSymbology( self.canvasLayer.layer() )
        else:
            self.canvasLayer.layer().thumbnailAsPixmap( pm )
            icon.addPixmap( pm )
            self.child = QtGui.QTreeWidgetItem( self )
            iconChild = QtGui.QIcon()
            iconChild.addPixmap( self.canvasLayer.layer().legendAsPixmap().scaled( 15, 15, QtCore.Qt.KeepAspectRatio ) )
            self.child.setSizeHint ( 0, QtCore.QSize( 15, 15 ) )
            self.child.setIcon( 0, iconChild )

        self.setIcon( 0, icon )

        self.setToolTip( 0, self.canvasLayer.layer().publicSource() )
        layerFont = QtGui.QFont()
        layerFont.setBold( True )
        self.setFont( 0, layerFont )

    def nextSibling( self ):
        """ Return the next layer item """
        return self.legend.nextSibling( self )

    def storeAppearanceSettings( self ):
        """ Store the appearance of the layer item """
        self.__itemIsExpanded = self.isExpanded()

    def restoreAppearanceSettings( self ):
        """ Restore the appearance of the layer item """
        self.setExpanded( self.__itemIsExpanded )

    def vectorLayerSymbology( self, layer ):
        itemList = [] # Symbology List

        # Add the new items
        lw = ''
        uv = ''
        label = ''
        renderer = layer.renderer()
        sym = renderer.symbols()

        for it in sym:
            img = QtGui.QImage()
            if it.type() == QGis.Point:
                img = it.getPointSymbolAsImage(4) # 4: A convenience scale
            elif it.type() == QGis.Line:
                img = it.getLineSymbolAsImage()
            else: #polygon
                img = it.getPolygonSymbolAsImage()

            values = ''
            lw = it.lowerValue()
            if not lw.isEmpty():
                values += lw

            uv = it.upperValue()
            if not uv.isEmpty():
                values += " - "
                values += uv

            label = it.label()
            if not label.isEmpty():
                values += " "
                values += label

            pix = QtGui.QPixmap( 20, 20 )
            pix = QtGui.QPixmap().fromImage( img )
            itemList.append( [ values, pix ] )

        #self.changeSymbologySettings( layer, itemList )

    def changeSymbologySettings( self, theMapLayer, itemList ):
        if not theMapLayer:
            return

        # Remove previous symbology items
        self.takeChildren()

        # Add the name of classification field as the first symbology item
        renderer = theMapLayer.renderer()
        if renderer.name() == "Graduated Symbol" or \
            renderer.name() == "Unique Value":
            fields = theMapLayer.pendingFields()
            self.child = QtGui.QTreeWidgetItem( self )
            self.child.setText( 0, fields[ renderer.classificationAttributes()[ 0 ] ].name() )
            childFont = QtGui.QFont()
            childFont.setItalic( True )
            self.child.setFont( 0, childFont )

        # Add the new symbology items
        for i in range( len( itemList ) ):
            self.child = QtGui.QTreeWidgetItem( self )
            self.child.setText( 0, unicode( itemList[ i ][ 0 ] ) )
            iconChild = QtGui.QIcon()
            iconChild.addPixmap( itemList[ i ][ 1 ] )
            self.child.setIcon( 0, iconChild )

            childFont = QtGui.QFont()
            childFont.setPointSize( 9 )
            self.child.setFont( 0, childFont )


class Legend( QtGui.QTreeWidget ):
    """
      Provide a widget that manages map layers and their symbology as tree items
    """
    def __init__( self, parent ):
        QtGui.QTreeWidget.__init__( self, parent )
        
        self.mainwindow = parent
        self.canvas = None
        self.layers = self.getLayerSet()
        
        self.bMousePressedFlag = False
        self.itemBeingMoved = None

        # QTreeWidget properties
        self.setSortingEnabled( False )
        self.setDragEnabled( False )
        self.setAutoScroll( True )
        self.setHeaderHidden( True )
        self.setRootIsDecorated( True )
        self.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        # added by be
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        #self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
   
        self.connect( self, QtCore.SIGNAL( "customContextMenuRequested(QPoint)" ),
            self.showMenu )
        self.connect( QgsMapLayerRegistry.instance(), QtCore.SIGNAL("layerWasAdded(QgsMapLayer *)"),
            self.addLayerToLegend)
        self.connect( QgsMapLayerRegistry.instance(), QtCore.SIGNAL( "removedAll()" ),
            self.removeAll )
        self.connect( self, QtCore.SIGNAL("itemChanged(QTreeWidgetItem *,int)"),
            self.updateLayerStatus )
        self.connect( self, QtCore.SIGNAL( "currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)" ),
            self.currentItemChanged )

    def setCanvas( self, canvas ):
        """ Set the base canvas """
        self.canvas = canvas

    def showMenu( self, pos ):
        """ Show a context menu for the active layer in the legend """
        item = self.itemAt( pos )
        if item:
            if self.isLegendLayer( item ):
                self.setCurrentItem( item )
                self.menu = self.getMenu( item.isVect, item.canvasLayer )
                self.menu.popup( QtCore.QPoint( self.mapToGlobal( pos ).x() + 5, self.mapToGlobal( pos ).y() ) )

    def getMenu( self, isVect, canvasLayer ):
        """ Create a context menu for a layer """
        menu = QtGui.QMenu()
        menu.addAction( QtGui.QIcon( resources_prefix + "mActionZoomToLayer.png" ), "&Zoom to layer extent", self.zoomToLayer )
        
        #Removed by BE.  Not needed in CAPS.
        #self.actionOV = menu.addAction( "Show in &overview", self.showInOverview )
        #self.actionOV.setCheckable( True )
        #self.actionOV.setChecked( canvasLayer.isInOverview() )
        
        #menu.addSeparator()
        #menu.addAction( QtGui.QIcon( resources_prefix + "mIconProperties.png" ), "&Properties...", self.setLayerProperties )
        if isVect :
            menu.addAction( QtGui.QIcon( resources_prefix + "symbology.png" ), "&Symbology...", self.layerSymbology )
            
            #Removed by BE.  Not needed in CAPS
            #menu.addAction( QtGui.QIcon( resources_prefix + "mActionFileOpen.png" ), "&Load style...", self.loadSymbologyFile )
            #menu.addAction( QtGui.QIcon( resources_prefix + "mActionFileSave.png" ), "Save s&tyle as...", self.saveSymbologyFile )

        menu.addSeparator()
        menu.addAction( QtGui.QIcon( resources_prefix + "collapse.png" ), "&Collapse all", self.collapseAll )
        menu.addAction( QtGui.QIcon( resources_prefix + "expand.png" ), "&Expand all", self.expandAll )

        menu.addSeparator()
        menu.addAction( QtGui.QIcon( resources_prefix + "mActionRemoveLayer.png" ), "&Remove layer", self.removeCurrentLayer )
        return menu

    def mousePressEvent(self, event):
        """ Mouse press event to manage the layers drag """
        p = QtCore.QPoint( event.pos() )
        item = self.itemAt( p )
 
        if (item and item != self.currentItem()): 
            print "legend.mousePressEvent" 
            if self.mainwindow.appStateChanged("legendMousePress") == "Cancel":
                return
        if ( event.button() == QtCore.Qt.LeftButton ):
            self.lastPressPos = event.pos()
            self.bMousePressedFlag = True
        QtGui.QTreeWidget.mousePressEvent( self, event )

    def mouseMoveEvent(self, event):
        """ Mouse move event to manage the layers drag """
        if ( self.bMousePressedFlag ):
            # Set the flag back such that the else if(mItemBeingMoved)
            # code part is passed during the next mouse moves
            self.bMousePressedFlag = False

            # Remember the item that has been pressed
            item = self.itemAt( self.lastPressPos )
            if ( item ):
                if ( self.isLegendLayer( item ) ):
                    self.itemBeingMoved = item
                    self.storeInitialPosition() # Store the initial layers order
                    self.setCursor( QtCore.Qt.SizeVerCursor )
                else:
                    self.setCursor( QtCore.Qt.ForbiddenCursor )
        elif ( self.itemBeingMoved ):
            p = QtCore.QPoint( event.pos() )
            self.lastPressPos = p

            # Change the cursor
            item = self.itemAt( p )
            origin = self.itemBeingMoved
            dest = item

            if not item:
                self.setCursor( QtCore.Qt.ForbiddenCursor )

            if ( item and ( item != self.itemBeingMoved ) ):
                if ( self.yCoordAboveCenter( dest, event.y() ) ): # Above center of the item
                    if self.isLegendLayer( dest ): # The item is a layer
                        if ( origin.nextSibling() != dest ):
                            self.moveItem( dest, origin )
                        self.setCurrentItem( origin )
                        self.setCursor( QtCore.Qt.SizeVerCursor )
                    else:
                        self.setCursor( QtCore.Qt.ForbiddenCursor )
                else: # Below center of the item
                    if self.isLegendLayer( dest ): # The item is a layer
                        if ( self.itemBeingMoved != dest.nextSibling() ):
                            self.moveItem( origin, dest )
                        self.setCurrentItem( origin )
                        self.setCursor( QtCore.Qt.SizeVerCursor )
                    else:
                        self.setCursor( QtCore.Qt.ForbiddenCursor )

    def mouseReleaseEvent( self, event ):
        """ Mouse release event to manage the layers drag """
        QtGui.QTreeWidget.mouseReleaseEvent( self, event )
        self.setCursor( QtCore.Qt.ArrowCursor )
        self.bMousePressedFlag = False

        if ( not self.itemBeingMoved ):
            #print "*** Legend drag: No itemBeingMoved ***"
            return

        dest = self.itemAt( event.pos() )
        origin = self.itemBeingMoved
        if ( ( not dest ) or ( not origin ) ): # Release out of the legend
            self.checkLayerOrderUpdate()
            return

        self.checkLayerOrderUpdate()
        self.itemBeingMoved = None

    def addLayerToLegend( self, mapLayer ):
        """ Slot. Create and add a legend item based on a layer """
     
        legendLayer = LegendItem( self, QgsMapCanvasLayer( mapLayer ) )
        self.addLayer( legendLayer )

    def addLayer( self, legendLayer ):
        """ Add a legend item to the legend widget """
        self.insertTopLevelItem ( 0, legendLayer )
        
        # be moved to here to slow active layer changed signal
        self.updateLayerSet()
        self.expandItem( legendLayer )
        self.setCurrentItem( legendLayer )
        #self.updateLayerSet()

    def updateLayerStatus( self, item ):
        """ Update the layer status """
        # debugging
        print "legend.updateLayerStatus()"
        print item
        
        if (item):
            if self.isLegendLayer(item): # Is the item a layer item?
                print "This is a legend layer item" 
                for i in self.layers:
                    if i.layer().getLayerID() == item.layerId:
                        if item.checkState( 0 ) == QtCore.Qt.Unchecked:
                            print "is checked"
                            i.setVisible(False)
                        else:
                            print "is not checked"
                            i.setVisible(True)
                        self.canvas.setLayerSet(self.layers)
                        return
              
                print "This is not a legend layer item"
                print "The item's text is " + str(item.text)
                  
    def currentItemChanged( self, newItem, oldItem ):
        """ Slot. Capture a new currentItem and emit a SIGNAL to inform the new type 
            It could be used to activate/deactivate GUI buttons according the layer type
        """
        layerType = None
        item = None
        if self.currentItem():
            if self.isLegendLayer(newItem):
                layerType = newItem.canvasLayer.layer().type()
                self.canvas.setCurrentLayer(newItem.canvasLayer.layer())
                item = newItem
            else:
                layerType = newItem.parent().canvasLayer.layer().type()
                self.canvas.setCurrentLayer(newItem.parent().canvasLayer.layer())
                item = newItem.parent()
        
        # be Create a Python "short-circuit" signal (note no "SIGNAL" parentheses)
        self.emit( QtCore.SIGNAL( "activeLayerChanged" ), layerType )

    def zoomToLayer( self ):
        """ Slot. Manage the zoomToLayer action in the context Menu """
        self.zoomToLegendLayer( self.currentItem() )
        
        '''rect = self.canvas.extent()
        
        # debugging
        print "Main.MainWindow.setExtents()"
        print "The canvas extents on loading are:"
        print ("(" + str(rect.xMinimum()) + ", " + str(rect.yMinimum()) + ", " + 
                     str(rect.xMaximum()) + ", " + str(rect.yMaximum()) + ")")
        print "extentMA is (32000, 780000, 330000, 965000)"
        
        # set extents no bigger than MA state extents
        extentMA = QgsRectangle(32000, 780000, 330000, 965000)
        if (self.canvas.extent().contains(extentMA) or 
            not self.canvas.extent().intersects(extentMA)):
            print "canvas extent contains or does not intersect MA"
            print "SET MA EXTENT"
            extentMA.scale(1.05)
            self.canvas.setExtent(extentMA)
            self.canvas.refresh()'''

    def removeCurrentLayer( self ):
        """ Slot. Manage the removeCurrentLayer action in the context Menu """
        # debugging
        print "Mainwindow.legend.removeCurrentLayer()"
       
        # be Check app state and give user a chance to cancel.
        if self.mainwindow.appStateChanged("removeCurrentLayer") == "Cancel":
            return
        
        
        # Check and warn on removing an editing layer
        name = self.currentItem().canvasLayer.layer().name()
        if name in config.editLayersBaseNames:
            reply = QtGui.QMessageBox.warning(self, "Warning!", "Removing '" + name + "' \
from the legend will cause that file and any 'Export Scenario' file to be deleted from \
the file system. All changes to these files will be lost. Do you want to delete this file(s)?", 
                                                        QtGui.QMessageBox.No|QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.No:
                return # user canceled so don't remove layer
            else: 
                # user chose ok so we can delete the file but must remove from registry first!
                layer = self.currentItem().canvasLayer.layer()
                layerID = self.currentItem().canvasLayer.layer().getLayerID()
                # get the path before we set the activeVLayer to none
                editFilePath = self.mainwindow.activeVLayer.source()
                # since we are deleting an editing layer we should be safe and 
                # remove any exported scenario files.
                self.mainwindow.deleteExportScenarioFile()
                # remove the layer from the registry
                self.removeEditLayerFromRegistry(layer, layerID)
                # and delete the editing layer
                self.deleteEditingLayer(editFilePath)
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
            
        # be layer ready to be removed so reset active layer variables to none or could
        #  get C++ object deleted runtime errors from deleting referenced variable
        self.setActiveLayerVariables()
        
        # remove layer from the registry
        QgsMapLayerRegistry.instance().removeMapLayer(layerID)
        self.removeLegendLayer( self.currentItem() )
        self.updateLayerSet()

    def setLayerProperties( self ):
        """ Slot. Open a dialog to set the layer properties """
        if self.currentItem():
            item = self.currentItem()
            self.dlgProperties = None
            self.dlgProperties = LayerProperties( self.mainwindow, item.canvasLayer.layer() )
            self.connect( self.dlgProperties, QtCore.SIGNAL( "layerNameChanged(PyQt_PyObject)" ), self.updateLayerName )
            self.dlgProperties.mostrar()

    def updateLayerName( self, layer ):
        """ Update the layer name in the legend """
        for i in range( self.topLevelItemCount() ):
            if self.topLevelItem( i ).layerId == layer.getLayerID():
                layer.setLayerName( self.createUniqueName( unicode( layer.name() ) ) )
                self.topLevelItem( i ).setText( 0, layer.name() )
                break

    def layerSymbology( self ):
        """ Change the features color of a vector layer """
        legendLayer = self.currentItem()
        
        if legendLayer.isVect == True:
            geom = legendLayer.canvasLayer.layer().geometryType() # QGis Geometry
            for i in self.layers:
                if i.layer().getLayerID() == legendLayer.layerId:
                    color = QtGui.QColorDialog.getColor( i.layer().rendererV2().symbols()[ 0 ].color(), self.mainwindow )
                    '''if geom == 1: # Line
                        color = QtGui.QColorDialog.getColor( i.layer().rendererV2().symbols()[ 0 ].color(), self.mainwindow )
                    else:
                        color = QtGui.QColorDialog.getColor( i.layer().rendererV2().symbols()[ 0 ].fillColor(), self.mainwindow )'''
                    break

            if color.isValid():
                #pm = QtGui.QPixmap()
                #iconChild = QtGui.QIcon()
                legendLayer.canvasLayer.layer().rendererV2().symbols()[ 0 ].setColor( color )
                '''if geom == 1: # Line
                    legendLayer.canvasLayer.layer().rendererV2().symbols()[ 0 ].setColor( color )                                       
                else:  
                    legendLayer.canvasLayer.layer().rendererV2().symbols()[ 0 ].setFillColor( color )'''

                self.refreshLayerSymbology( legendLayer.canvasLayer.layer() )

    def loadSymbologyFile( self ):
        """ Load a QML file to set the layer style """
        settings = QtCore.QSettings()
        ultimaRutaQml = settings.value( 'Paths/qml', QtCore.QVariant('.') ).toString()
        symPath = QtGui.QFileDialog.getOpenFileName(self, "Open a style file (.qml)",
            ultimaRutaQml, "QGIS Layer Style File (*.qml)")

        if isfile( symPath ):
            res = self.currentItem().canvasLayer.layer().loadNamedStyle( symPath )

            if res[ 1 ]:
                self.refreshLayerSymbology( self.currentItem().canvasLayer.layer() )
                self.showMessage( self, 'Load style',
                    'The style file has been succesfully applied to the layer ' +
                    self.currentItem().text( 0 ) + '.', QtGui.QMessageBox.Information )
            else:
                self.showMessage( self, 'Load style',
                    'It was not possible to load the style file. Make sure the file ' \
                    'matches the structure of the layer ' + self.currentItem().text( 0 ) + '.',
                    QtGui.QMessageBox.Warning )

            symInfo = QtCore.QFileInfo( symPath )
            settings.setValue( 'Paths/qml', QtCore.QVariant( symInfo.absolutePath() ) )

    def saveSymbologyFile( self ):
        """ Save a QML file to set the layer style """
        settings = QtCore.QSettings()
        ultimaRutaQml = settings.value( 'Paths/qml', QtCore.QVariant('.') ).toString()
        symPath = QtGui.QFileDialog.getSaveFileName( self, "Save layer properties as a style file",
            ultimaRutaQml, "QGIS Layer Style File (*.qml)" )

        if symPath:
            symInfo = QtCore.QFileInfo( symPath )
            settings.setValue( 'Paths/qml', QtCore.QVariant( symInfo.absolutePath() ) )

            if not symPath.toUpper().endsWith( '.QML' ):
                symPath += '.qml'

            res = self.currentItem().canvasLayer.layer().saveNamedStyle( symPath )

            if res[ 1 ]:
                self.refreshLayerSymbology( self.currentItem().canvasLayer.layer() )
                self.showMessage( self, 'Save style file',
                    'The style file has been saved succesfully.',
                    QtGui.QMessageBox.Information )
            else:
                self.showMessage( self, 'Save style file',
                    res[ 0 ], QtGui.QMessageBox.Warning )

    def showMessage( self, parent, title, desc, icon=None ):
        """ Method to create messages to be shown to the users """
        msg = QtGui.QMessageBox( parent )
        msg.setText( desc )
        msg.setWindowTitle( title )
        if icon:
            msg.setIcon( icon )
        msg.addButton( 'Close', QtGui.QMessageBox.RejectRole )
        msg.exec_()

    def zoomToLegendLayer( self, legendLayer ):
        """ Zoom the map to a layer extent """
        
        for i in self.layers:
            if i.layer().getLayerID() == legendLayer.layerId:
                extent = i.layer().extent()
                extent.scale( 1.05 )
                self.canvas.setExtent( extent )
                self.canvas.refresh()
                break
 
    def removeLegendLayer( self, legendLayer ):
        """ Remove a layer item in the legend """
        if self.topLevelItemCount() == 1:
            self.clear()
        else: # Manage the currentLayer before the remove
            indice = self.indexOfTopLevelItem( legendLayer )
            if indice == 0:
                newCurrentItem = self.topLevelItem( indice + 1 )
            else:
                newCurrentItem = self.topLevelItem( indice - 1 )

            self.setCurrentItem( newCurrentItem )
            self.takeTopLevelItem( self.indexOfTopLevelItem( legendLayer ) )

    def setStatusForAllLayers( self, visible ):
        """ Show/Hide all layers in the map """
        # Block SIGNALS to avoid setLayerSet for each item status changed
        self.blockSignals( True )

        status = QtCore.Qt.Checked if visible else QtCore.Qt.Unchecked
        for i in range( self.topLevelItemCount() ):
            self.topLevelItem( i ).setCheckState( 0, status )
            self.topLevelItem( i ).canvasLayer.setVisible( visible )

        self.blockSignals( False )

        self.updateLayerSet() # Finally, update the layer set

    def removeAll( self ):
        """ Remove all legend items """
        self.clear()
        self.updateLayerSet()

    def allLayersInOverview( self, visible ):
        """ Show/Hide all layers in Overview """
        for i in range( self.topLevelItemCount() ):
            self.topLevelItem( i ).canvasLayer.setInOverview( visible )
        self.updateLayerSet()
        self.canvas.updateOverview()

    def showInOverview( self ):
        """ Toggle the active layer in Overview Map """
        self.currentItem().canvasLayer.setInOverview( not( self.currentItem().canvasLayer.isInOverview() ) )
        self.updateLayerSet()
        self.canvas.updateOverview()

    def updateLayerSet( self ):
        """ Update the LayerSet and set it to canvas """
        self.layers = self.getLayerSet()
        self.canvas.setLayerSet( self.layers )

    def getLayerSet( self ):
        """ Get the LayerSet by reading the layer items in the legend """
        layers = []
        for i in range( self.topLevelItemCount() ):
            layers.append( self.topLevelItem( i ).canvasLayer )
        return layers

    def activeLayer( self ):
        """ Return the selected layer """
        if self.currentItem():
            if self.isLegendLayer( self.currentItem() ):
                return self.currentItem().canvasLayer
            else:
                return self.currentItem().parent().canvasLayer
        else:
            return None

    def collapseAll( self ):
        """ Collapse all layer items in the legend """
        for i in range( self.topLevelItemCount() ):
            item = self.topLevelItem( i )
            self.collapseItem( item )

    def expandAll( self ):
        """ Expand all layer items in the legend """
        for i in range( self.topLevelItemCount() ):
            item = self.topLevelItem( i )
            self.expandItem( item )

    def isLegendLayer( self, item ):
        """ Check if a given item is a layer item """
        return not item.parent()

    def storeInitialPosition( self ):
        """ Store the layers order """
        self.__beforeDragStateLayers = self.getLayerIDs()

    def getLayerIDs( self ):
        """ Return a list with the layers ids """
        layers = []
        for i in range( self.topLevelItemCount() ):
            item = self.topLevelItem( i )
            layers.append( item.layerId )
        return layers

    def nextSibling( self, item ):
        """ Return the next layer item based on a given item """
        for i in range( self.topLevelItemCount() ):
            if item.layerId == self.topLevelItem( i ).layerId:
                break
        if i < self.topLevelItemCount():                                            
            return self.topLevelItem( i + 1 )
        else:
            return None

    def moveItem( self, itemToMove, afterItem ):
        """ Move the itemToMove after the afterItem in the legend """
        itemToMove.storeAppearanceSettings() # Store settings in the moved item
        self.takeTopLevelItem( self.indexOfTopLevelItem( itemToMove ) )
        self.insertTopLevelItem( self.indexOfTopLevelItem( afterItem ) + 1, itemToMove )
        itemToMove.restoreAppearanceSettings() # Apply the settings again

    def checkLayerOrderUpdate( self ):
        """
            Check if the initial layers order is equal to the final one.
            This is used to refresh the legend in the release event.
        """
        self.__afterDragStateLayers = self.getLayerIDs()
        if self.__afterDragStateLayers != self.__beforeDragStateLayers:
            self.updateLayerSet()
            #print "*** Drag legend layer done. Updating canvas ***"

    def yCoordAboveCenter( self, legendItem, ycoord ):
        """
            Return a bool to know if the ycoord is in the above center of the legendItem

            legendItem: The base item to get the above center and the below center
            ycoord: The coordinate of the comparison
        """
        rect = self.visualItemRect( legendItem )
        height = rect.height()
        top = rect.top()
        mid = top + ( height / 2 )
        if ( ycoord > mid ): # Bottom, remember the y-coordinate increases downwards
            return False
        else: # Top
            return True

    def normalizeLayerName( self, name ):
        """ Create an alias to put in the legend and avoid to repeat names """
        # Remove the extension
        if len( name ) > 4:
            if name[ -4 ] == '.':
                name = name[ :-4 ]
        return self.createUniqueName( name )

    def createUniqueName( self, name ):
        """ Avoid to repeat layers names """
        import re
        name_validation = re.compile( "\s\(\d+\)$", re.UNICODE ) # Strings like " (1)"

        bRepetida = True
        i = 1
        while bRepetida:
            bRepetida = False

            # If necessary add a sufix like " (1)" to avoid to repeat names in the legend
            for j in range( self.topLevelItemCount() ):
                item = self.topLevelItem( j )
                if item.text( 0 ) == name:
                    bRepetida = True
                    if name_validation.search( name ): # The name already have numeration
                        name = name[ :-4 ]  + ' (' + str( i ) + ')'
                    else: # Add numeration because the name doesn't have it
                        name = name + ' (' + str( i ) + ')'
                    i += 1
        return name

    def refreshLayerSymbology( self, layer ):
        """ Refresh the layer symbology. For plugins. """
        for i in range( self.topLevelItemCount() ):
            item = self.topLevelItem( i )
            if layer.getLayerID() == item.layerId:
                #item.vectorLayerSymbology( layer )
                self.canvas.refresh()
                break

    def removeLayers( self, layerIds ):
        """ Remove layers from their ids. For plugins. """
        for layerId in layerIds:
            QgsMapLayerRegistry.instance().removeMapLayer( layerId )

            # Remove the legend item
            for i in range( self.topLevelItemCount() ):
                item = self.topLevelItem( i )
                if layerId == item.layerId:
                    self.removeLegendLayer( item )
                    break

        self.updateLayerSet()
        
    def deleteEditingLayer(self, editFilePath):
        ''' Removes an editing shapefile and any associated export scenario file. '''
        # debugging
        print "deleteEditingLayer()"
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
     
    def removeEditLayerFromRegistry(self, layer, layerID):
        ''' Remove an editing layer from the registry, but clean up first '''
        # debugging
        print "Main.legend.removeEditLayerFrom Registry()"
     
        originalScenarioLayers = self.mainwindow.originalScenarioLayers
        if layer in originalScenarioLayers:
            print "length originalScenarioLayers before removal " + str(len(originalScenarioLayers))
            originalScenarioLayers.remove(layer)
            self.mainwindow.scenarioDirty = True
            print 'The activeVLayer was removed from the originalScenarioLayers'
            print 'length originalScenarioLayers after removal' + str(len(originalScenarioLayers))
        
        # Reset all variables associated with the layer and then remove from 
        # registry and delete it.
        self.setActiveLayerVariables()
        QgsMapLayerRegistry.instance().removeMapLayer(layerID)
        
        # Layer is successfully removed from registry so remove from legend.
        self.removeLegendLayer(self.currentItem())
        self.updateLayerSet()
 
    def setActiveLayerVariables(self):
        ''' Reset the variable to avoid c++ runtime errors for deleted objects '''
        # debugging
        print "Main.legend.setActiveLayerVariables()"
        
        self.mainwindow.activeRLayer = None
        self.mainwindow.activeVLayer.rendererV2 = None
        self.mainwindow.activeVLayer = None 
        self.mainwindow.geom = None # reset activeVLayer information
        self.mainwindow.provider = None
        self.mainwindow.layerType = None        
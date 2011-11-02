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
from PyQt4 import QtCore
from PyQt4 import QtGui
# QGIS bindings for mapping functions
from qgis.core import * #QGis, QgsMapLayerRegistry
from qgis.gui import * #QgsMapCanvasLayer
# CAPS application imports
from dlgLayerProperties import LayerProperties



#icons for the legend are compiled in resources_rc.py
resources_prefix = ":/images/"

class LegendItem( QtGui.QTreeWidgetItem ):
    """ Provide a widget to show and manage the properties of one single layer """
    # b initiated from Legend.addLayerToLegend() with name legendLayer
    # b instance is passed the parameter Legend() for parent 
    # b and canvasLayer is a QgsMapCanvasLayer() instance
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

        self.setCheckState( 0, QtCore.Qt.Checked )
        # b QPixmap class is an off-screen image representation 
        # b that can be used as a paint device
        pm = QtGui.QPixmap( 20, 20 )
        # b The QIcon class provides scalable icons in different modes and states
        icon = QtGui.QIcon()
        # sets some layer images
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
            # b simply sets images and labels in layer pane    
            self.vectorLayerSymbology( self.canvasLayer.layer() )
        else:
            # gets the raster image from qgis api
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
        # setFont ( int column, const QFont & font )
        self.setFont( 0, layerFont )

    def nextSibling( self ):
        """ Return the next layer item """
        return self.legend.nextSibling( self )

    def storeAppearanceSettings( self ):
        """ Store the appearance of the layer item """
        #QTreeWidgetItem::isExpanded () const Returns true if the item is expanded
        self.__itemIsExpanded = self.isExpanded()

    def restoreAppearanceSettings( self ):
        """ Restore the appearance of the layer item """
        self.setExpanded( self.__itemIsExpanded )

    def vectorLayerSymbology( self, layer ):
        """b Sets the layer symbology to display """
        itemList = [] # Symbology List

        # Add the new items
        lw = ''
        uv = ''
        label = ''
        renderer = layer.renderer()
        sym = renderer.symbols()
        # for item in symbols() list
        for it in sym:
            img = QtGui.QImage()
            if it.type() == QGis.Point:
                img = it.getPointSymbolAsImage( 4 ) # 4: A convenience scale
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

        self.changeSymbologySettings( layer, itemList )

    def changeSymbologySettings( self, theMapLayer, itemList ):
        if not theMapLayer:
            return

        # Remove previous symbology items
        self.takeChildren()

        # Add the name of classification field as the first symbology item
        renderer = theMapLayer.renderer()
        #b looked up the names in qgsgraduatedsymbolrenderer.cpp line 331 cool!
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

         # should do "print itemList" here to learn   
class Legend( QtGui.QTreeWidget ):
    """
      Provide a widget that manages map layers and their symbology as tree items
    """
    # b called from mainwindow.py and passed mainwindow as parent
    def __init__( self, parent ):
        QtGui.QTreeWidget.__init__( self, parent )
        
        # so self.pyQGisApp is the mainwindow
        self.pyQGisApp = parent
        self.canvas = None
        # b returns a list of layer objects that appear in the legend
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
        # b context menu requested with a right click on a legend item
        # b apparently passes a QPoint to self.showMenu
        self.connect( self, QtCore.SIGNAL( "customContextMenuRequested(QPoint)" ),
            self.showMenu )
        # b Signal emitted by QgsMapLayerRegistry
        # b QgsMapLayerRegistry.instance() is pointer to new layer
        # b addLayerToLegend calls LegendItem() to create new QTreeWidgetItem 
        self.connect( QgsMapLayerRegistry.instance(), QtCore.SIGNAL("layerWasAdded(QgsMapLayer *)"),
            self.addLayerToLegend)
        # b this connection does not seem to be implemented in CAPS
        self.connect( QgsMapLayerRegistry.instance(), QtCore.SIGNAL( "removedAll()" ),
            self.removeAll )
        self.connect( self, QtCore.SIGNAL("itemChanged(QTreeWidgetItem *,int)"),
            self.updateLayerStatus )
        self.connect( self, QtCore.SIGNAL( "currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)" ),
            self.currentItemChanged )
    # b called from mainwindow method createLegendWidget
    def setCanvas( self, canvas ):
        """ Set the base canvas """
        self.canvas = canvas

    def showMenu( self, pos ):
        """ Show a context menu for the active layer in the legend """
        item = self.itemAt( pos )
        if item:
            if self.isLegendLayer( item ):
                # b a QTreeWidget method 'setCurrentItem
                self.setCurrentItem( item )
                self.menu = self.getMenu( item.isVect, item.canvasLayer )
                self.menu.popup( QtCore.QPoint( self.mapToGlobal( pos ).x() + 5, self.mapToGlobal( pos ).y() ) )

    def getMenu( self, isVect, canvasLayer ):
        """ Create a context menu for a layer """
        menu = QtGui.QMenu()
        menu.addAction( QtGui.QIcon( resources_prefix + "mActionZoomToLayer.png" ), "&Zoom to layer extent", self.zoomToLayer )
        
        # Removed by BE.  Not needed in CAPS.
        #self.actionOV = menu.addAction( "Show in &overview", self.showInOverview )
        #self.actionOV.setCheckable( True )
        #self.actionOV.setChecked( canvasLayer.isInOverview() )
        
        # b after all other GIS functions are done (i.e save project and edit tools)
        # b then modify the dlgLayerProperties dialog to change line thickness and 
        # b use alternate symbols 
        #menu.addSeparator()
        #menu.addAction( QtGui.QIcon( resources_prefix + "mIconProperties.png" ), "&Properties...", self.setLayerProperties )
        
        if isVect :
            # b see the layerSymbology slot for modifying symbology
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

    # b This reimplemented event handler just sets the bMousePressedFlag 
    # b to true and then passes the event back to Qt to handle
    # b "event" is the info passed by the Qt class
    # b in this case QMouseEvent
    def mousePressEvent(self, event):
        """ Mouse press event to manage the layers drag """
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
                # b local "isLegendLayer" method just checks for a parent
                # b to establish that the "item" is a layer
                # b top level items in the QTreeWidget have no parent
                if ( self.isLegendLayer( item ) ):
                    # b local variable "self.itemBeingMoved"
                    self.itemBeingMoved = item
                    # b storeInitialPosition just calls getLayerIDs and stores in a local private variable
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
                        # b just sets mouse cursor for the widget when layer is dragged
                        # b Qt has a large number of cursors available
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

    def addLayerToLegend( self, canvasLayer ):
        """ Slot. Create and add a legend item based on a layer """
        # b canvasLayer is actually a layer not a canvas layer
        # passed from the a connection as a QgsMapLayerRegistry.instance()
        # b this turns the layer into a QgsMapCanvasLayer
        legendLayer = LegendItem( self, QgsMapCanvasLayer( canvasLayer ) )
        self.addLayer( legendLayer )

    # don't know why this isn't incorporated into the above method
    def addLayer( self, legendLayer ):
        """ Add a legend item to the legend widget """
        self.insertTopLevelItem ( 0, legendLayer )
        self.expandItem( legendLayer )
        self.setCurrentItem( legendLayer )
        self.updateLayerSet()

    # b this method sets visibility based on the checkState of the widget
    def updateLayerStatus( self, item ):
        """ Update the layer status """
        if ( item ):
            if self.isLegendLayer( item ): # Is the item a layer item?
                for i in self.layers:
                    if i.layer().getLayerID() == item.layerId:
                        if item.checkState( 0 ) == QtCore.Qt.Unchecked:
                            i.setVisible( False )
                        else:
                            i.setVisible( True )
                        self.canvas.setLayerSet( self.layers )
                        return
    # the "currentItem is the item selected, not the item checked
    def currentItemChanged( self, newItem, oldItem ):
        """ Slot. Capture a new currentItem and emit a SIGNAL to inform the new type 
            It could be used to activate/deactivate GUI buttons according the layer type
        """
        layerType = None

        if self.currentItem():
            if self.isLegendLayer( newItem ):
                layerType = newItem.canvasLayer.layer().type()
                self.canvas.setCurrentLayer( newItem.canvasLayer.layer() )
            else:
                layerType = newItem.parent().canvasLayer.layer().type()
                self.canvas.setCurrentLayer( newItem.parent().canvasLayer.layer() )

        self.emit( QtCore.SIGNAL( "activeLayerChanged" ), layerType )
    
    # b not sure why we couldn't just call zoomToLegendLayer from the calling action
    def zoomToLayer( self ):
        """ Slot. Manage the zoomToLayer action in the context Menu """
        self.zoomToLegendLayer( self.currentItem() )

    def removeCurrentLayer( self ):
        """ Slot. Manage the removeCurrentLayer action in the context Menu """
        QgsMapLayerRegistry.instance().removeMapLayer( self.currentItem().canvasLayer.layer().getLayerID() )
        self.removeLegendLayer( self.currentItem() )
        self.updateLayerSet()
    
    # b instantiates properties dialog with mainwindow as parent and passes a qgis layer
    # b disabled by BE.  Not needed in CAPS at the moment, but may be reactivated
    # b to set line thickness and color
    def setLayerProperties( self ):
        """ Slot. Open a dialog to set the layer properties """
        if self.currentItem():
            item = self.currentItem()
            self.dlgProperties = None
            self.dlgProperties = LayerProperties( self.pyQGisApp, item.canvasLayer.layer() )
            self.connect( self.dlgProperties, QtCore.SIGNAL( "layerNameChanged(PyQt_PyObject)" ), self.updateLayerName )
            self.dlgProperties.mostrar()

    # b called by the properties dialog to rename the layer
    # b We do not want to allow renaming in CAPS.  Base layers and editing layers
    # b should have fixed names in CAPS
    def updateLayerName( self, layer ):
        """ Update the layer name in the legend """
        for i in range( self.topLevelItemCount() ):
            if self.topLevelItem( i ).layerId == layer.getLayerID():
                layer.setLayerName( self.createUniqueName( unicode( layer.name() ) ) )
                self.topLevelItem( i ).setText( 0, layer.name() )
                break
    
    # b refer to this method to change line thickness and point symbols
    # b also refer to http://www.qgis.org/pyqgis-cookbook/vector.html#appearance-symbology-of-vector-layers
    def layerSymbology( self ):
        """ Change the features color of a vector layer """
        legendLayer = self.currentItem()
        
        if legendLayer.isVect == True:
            geom = legendLayer.canvasLayer.layer().geometryType() # QGis Geometry
            for i in self.layers: #self.layers is a list of QgsCanvasLayer objects
                if i.layer().getLayerID() == legendLayer.layerId:
                    if geom == 1: # Line
                        color = QtGui.QColorDialog.getColor( i.layer().renderer().symbols()[ 0 ].color(), self.pyQGisApp )
                    else:
                        color = QtGui.QColorDialog.getColor( i.layer().renderer().symbols()[ 0 ].fillColor(), self.pyQGisApp )
                    break

            if color.isValid():
                pm = QtGui.QPixmap()
                iconChild = QtGui.QIcon()
                if geom == 1: # Line
                    legendLayer.canvasLayer.layer().renderer().symbols()[ 0 ].setColor( color )                                       
                else:  
                    legendLayer.canvasLayer.layer().renderer().symbols()[ 0 ].setFillColor( color )

                self.refreshLayerSymbology( legendLayer.canvasLayer.layer() )

    # b not used in caps, but worth looking at sometime
    # b this is related to saving "scenarios" perhaps
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

    # not used in CAPS
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

    # b OK. if I need to display a lot of messages, this is how to do it.
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
    
    # b interesting that it needs to set a new "CurrentItem" before deleting
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

    # b note the "blockSignals" Qt method! 
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

   # b this method does not appear to be implemented in CAPS
    def removeAll( self ):
        """ Remove all legend items """
        self.clear()
        self.updateLayerSet()

    # b don't need overview for CAPS
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
    
    # b updates the QgsMapCanvas layer set
    def updateLayerSet( self ):
        """ Update the LayerSet and set it to canvas """
        self.layers = self.getLayerSet()
        self.canvas.setLayerSet( self.layers )
    
    # b used to set the variable self.layers equal to the layer list
    def getLayerSet( self ):
        """ Get the LayerSet by reading the layer items in the legend """
        layers = []
        # b in the LegendItem class the QTreeWidgetItems are 
        # b set to be qgis QgsCanvasLayers with method
        # b addLayerToLegend
        for i in range( self.topLevelItemCount() ):
            layers.append( self.topLevelItem( i ).canvasLayer )
        return layers
    
    # this returns the active layer even if the layer symbols icons are selected
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

    # b interesting method because of its simplicity.  A top level item in
    # b QTreeWidget doesn't have a parent.  So this returns "True" if the 
    # layer is a top level item and thus a qgis layer
    def isLegendLayer( self, item ):
        """ Check if a given item is a layer item """
        return not item.parent()

    # related to the drag and drop functionality of the layer pane
    def storeInitialPosition( self ):
        """ Store the layers order """
        self.__beforeDragStateLayers = self.getLayerIDs()

    # b OK. So I can easily get a list of layer Id's
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
                item.vectorLayerSymbology( layer )
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

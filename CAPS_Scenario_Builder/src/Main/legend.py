# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
# 
# Conservation Assessment and Prioritization System (CAPS) Scenario Builder - An Open Source  
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
#---------------------------------------------------------------------
# General system includes
import sys, os
from os.path import isfile
# PyQt4 includes for python bindings to QT
from PyQt4 import QtCore, QtGui
# QGIS bindings for mapping functions
from qgis.core import * #QGis, QgsMapLayerRegistry
from qgis.gui import * #QgsMapCanvasLayer
# CAPS Scenario Builder application imports
import config

#icons for the legend are compiled in resources_rc.py
resources_prefix = ":/images/"

class LegendItem(QtGui.QTreeWidgetItem):
    """ Provide a widget to show and manage the properties of one single layer """
    def __init__(self, parent, canvasLayer):
        QtGui.QTreeWidgetItem.__init__(self)
        
        # debugging
        print "Main.legend.LegendItem() class"
        print 'Main.legend.LegendItem(): The system path is', sys.path

        self.legend = parent
        self.canvasLayer = canvasLayer
        
        # Convert QStrings to unicode unless they are used immediately in a Qt method. 
        # This ensures that we never ask Python to slice a QString, which produces a type error.
        self.layerName = unicode(self.canvasLayer.layer().name())
        
        #debugging
        print 'Main.legend.LegendItem.layerName before is: ', self.layerName
        
        self.canvasLayer.layer().setLayerName(self.legend.normalizeLayerName(self.layerName))
        self.layerName = unicode(self.canvasLayer.layer().name())
        self.setText(0, self.layerName)
        self.isVect = (self.canvasLayer.layer().type() == 0) # 0: Vector, 1: Raster
        self.layerId = self.canvasLayer.layer().id()
        self.openingScenario = self.legend.mainwindow.openingScenario
        

        ''' 
            This class is instantiated by the legend.Legend() class immediately after a layer is registered by QGIS.
            It creates a legend item that represents a map layer. Since this is very close to the first access we 
            have to newly added layers, we set scenarioDirty here. We set the rendererV2 properties here because
            they only need to be set when a layer is loaded rather than every time a layer is changed (as in
            Main.mainwindow.activeLayerChanged()).  This is also the first chance to set layer properties, 
            so we set visibility and color for all newly opened layers here.
             
        '''
        
        # Each time a layer is loaded (or removed) we set the scenarioDirty flag.
        # There is no need to set it if the scenario is already dirty.  Once a scenario
        # is dirty, the policy is it stays dirty until the user saves it.
        if not self.legend.mainwindow.scenarioDirty: self.legend.mainwindow.setScenarioDirty()
        
        # This method sets the renderer colors, marker types and other properties for certain vector layers.
        # Since the scenario's '.cap' file stores rendererV2 settings, we don't need to call the
        # method when opening a scenario.
        if self.isVect and not self.openingScenario:
            self.setRendererV2(self.canvasLayer.layer())

        # handle layer visibility when opening the app, "New Scenario" or "Open Scenario."
        if self.openingScenario or self.legend.mainwindow.openingOrientingLayers:
            # Make any layer in config.orientingLayersChecked visible
            if self.layerName in config.orientingLayersChecked:
                self.setCheckState(0, QtCore.Qt.Checked)
                self.canvasLayer.setVisible(True)
            else: # all other layers loaded will be hidden
                self.setCheckState(0, QtCore.Qt.Unchecked) 
                self.canvasLayer.setVisible(False)
        else: # User chose "Add Vector Layer" or "Add Raster Layer" to add a single layer, so make visible.
            self.setCheckState(0, QtCore.Qt.Checked)    
            self.canvasLayer.setVisible(True)

        # Get colors when opening a saved scenario and save to the coloredLayers dictionary. 
        # We have to do this for all vector layers to know what layers are colored by the user
        # so we don't set default colors for them. Note that if the user later changes feature color 
        # for a layer, it will be updated in the dictionary (see legend.Legend.layerSymbology())
        if self.isVect and self.openingScenario:
            self.addLayerToColoredLayers()
        
        # Now set colors for layers not colored in a scenario file or 
        # specifically colored by the user (i.e. not in the coloredLayers dictionary).
        if self.isVect:
            if not self.legend.mainwindow.coloredLayers.get(self.layerName):
                if self.legend.currentColor == None or self.legend.currentColor == len(self.legend.mainwindow.defaultColors):
                    self.legend.currentColor = 0 # when we open the app or get to the end of the color list, we start again.
                print "Main.legend.LegendItem() class self.legend.currentColor is " + str(self.legend.currentColor)
                defColor = self.legend.mainwindow.defaultColors[self.legend.currentColor]
                self.canvasLayer.layer().rendererV2().symbols()[0].setColor(defColor)
                self.legend.currentColor += 1
        
        # debugging
        print "Main.legend.LegendItem() class: The coloredLayers are: "
        for k, v in self.legend.mainwindow.coloredLayers.iteritems():
            print "%s: %s" % (k, str(v.getRgb()))
        
        ''' Now set icons etc. for legend item '''
        
        pm = QtGui.QPixmap(20, 20)
        icon = QtGui.QIcon()

        if self.isVect:
            geom = self.canvasLayer.layer().geometryType() # QGis Geometry
            if geom == 0: # Point
                icon.addPixmap(QtGui.QPixmap(resources_prefix + "mIconPointLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            elif geom == 1: # Line
                icon.addPixmap(QtGui.QPixmap(resources_prefix + "mIconLineLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            elif geom == 2: # Polygon
                icon.addPixmap(QtGui.QPixmap(resources_prefix + "mIconPolygonLayer.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            else: print 'Unknown geometry: ' + unicode(geom)
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
        
    def setRendererV2(self, vlayer):
        # debugging
        print "Main.legend.LegendItem.setRendererV2()"
        print "Main.legend.LegendItem.setRendererV2(): vlayer geometry is :" + str(vlayer.geometryType())
        
        red = QtGui.QColor(255, 0, 0, 255)
        vlayerName = unicode(vlayer.name())
        if vlayerName == config.editLayersBaseNames[0]: # edit_scenario(points) layer
            print "Main.legend.LegendItem.setRendererV2(): Setting Rule Based Renderer for 'edit_scenario(points).shp"
            
            ''' 
                We are opening 'edit_scenario(points)' for the first time.  Either it has been reopened by
                Tools.shared.updateExtents(), Main.mainwindow.copyScenario() or it has been newly written by
                Main.mainwindow.dlgscenarioedittypes.
                
            '''
            
            self.setPointsRuleRendererV2(vlayer, red, vlayerName) # sets up the rule renderer for edit_scenario(points)
            
        elif vlayerName == config.editLayersBaseNames[1]: # edit_scenario(lines).shp
            print "Main.legend.LegendItem.setRendererV2(): Setting color and line width for edit_scenario(lines).shp"
            
            ''' 
                We are opening 'edit_scenario(lines)' for the first time.  Either it has been reopened by
                Tools.shared.updateExtents(), Main.mainwindow.copyScenario() or it has been newly written by
                Main.mainwindow.dlgscenarioedittypes.
                
            '''
            
            self.setLineColorAndWidth(vlayer, red, vlayerName) # sets color and width for edit_scenario(lines)
             
        elif vlayerName == config.editLayersBaseNames[2]: # edit_scenario(polygons).shp
            print "Main.legend.LegendItem.setRendererV2(): Setting color for edit_scenario(polygons).shp"
        
            ''' 
                We are opening 'edit_scenario(polygons)' for the first time.  Either it has been reopened by
                Tools.shared.updateExtents(), Main.mainwindow.copyScenario() or it has been newly written by
                Main.mainwindow.dlgscenarioedittypes.
                
            '''
            
            self.setPolygonColor(vlayer, red, vlayerName) # sets color for edit_scenario Polygons
            
        elif vlayerName == config.orientingLayersChecked[0]: # the base_towns layer
            print "Main.legend.LegendItem.setRendererV2(): This is the base_towns layer"
            
            
            # The user could be opening this layer with 'Add Vector' or the app could be opening orienting layers
            self.setBaseTownsProperties(vlayer) # sets this layer to transparent with black borders
                        
        elif vlayer.geometryType() == 1: # set line width for all line layers
            # debugging
            print "Main.legend.LegendItem.setRendererV2(): geometry = 1"
            symbolLayer = vlayer.rendererV2().symbols()[0].symbolLayer(0)
            print "Main.legend.LegendItem.setRendererV2(): The line width before setting is: " + str(symbolLayer.width())
            symbolLayer.setWidth(0.4)
            print "Main.legend.LegendItem.setRendererV2(): The line width after setting is: " + str(symbolLayer.width())
            vlayer.triggerRepaint()
        
        # debugging
        if vlayer.isUsingRendererV2():
            rendererV2 = vlayer.rendererV2()
            symbols = rendererV2.symbols()
            # only 1 symbol in symbols and only one layer
            symbol = symbols[0]
            symbolLayer = symbol.symbolLayer(0)
            print "Main.legend.LegendItem.setRendererV2(): rendererV2.dump is:" + rendererV2.dump()
            print "Main.legend.LegendItem.setRendererV2(): The layer properties are: "
            for k, v in symbolLayer.properties().iteritems():
                print "%s: %s" % (k, v)
            print "Main.legend.LegendItem.setRendererV2(): The number of symbols is: " + str(len(symbols))
            print "Main.legend.LegendItem.setRendererV2(): The number of layers in symbols[0] is: " + str(symbol.symbolLayerCount())
            print "Main.legend.LegendItem.setRendererV2(): The layer type is: " + str(symbolLayer.layerType())        

    def addLayerToColoredLayers(self):
        # debugging
        print "Main.legend.LegendItem.addLayerToColoredLayers()"
                       
        color = self.canvasLayer.layer().rendererV2().symbols()[0].color()
        self.legend.mainwindow.coloredLayers[self.layerName] = color
        
    def setPointsRuleRendererV2(self, vlayer, red, vlayerName):
        # debugging
        print "Main.legend.LegendItem.setPointsRuleRenderer()"
        
        ''' Create the rule based renderer. '''
         
        # This returns a QgsSymbolV2(). In particular a QgsMarkerSymbolV2().
        # This also returns a QgsMarkerSymbolLayerV2() layer. In particular a QgsSimpleMarkerSymbolLayerV2().
        symbol = QgsSymbolV2.defaultSymbol(QGis.Point)
        # renderer only needs a symbol to be instantiated
        rendererV2 = QgsRuleBasedRendererV2(symbol)
        
        # get the symbols list and symbol (usually only one symbol)
        symbol = rendererV2.symbols()[0]
        symbolLayer = symbol.symbolLayer(0)
        symbolLayer.setSize(2.0)
        symbolLayer.setColor(red)
        
        
        '''
            Now we set the rules for rendering different scenario edits, so that the user can
            easily determine what features represent.
            
            Choices for symbols are: circle, rectangle, diamond, pentagon, cross, cross2, triangle, 
            equilateral_triangle, star, regular_star, arrow.
            
        '''
        
        newSymbol = QgsSymbolV2.defaultSymbol(QGis.Point)
        # dams
        map1 = {"name": "rectangle", "color": "255,0,0,255", "offset": "0,0",
               "color_border": "0,0,0,255", "size": "2.0", "angle": "DEFAULT_SIMPLEMARKER_ANGLE"} 
        damSymbol = newSymbol.createSimple(map1)
        damLayer = damSymbol.symbolLayer(0)
        # terrestrial crossing
        map2 = {"name": "pentagon", "color": "255,0,0,255", "offset": "0,0",
               "color_border": "0,0,0,255", "size": "3.0", "angle": "DEFAULT_SIMPLEMARKER_ANGLE"} 
        terrSymbol = newSymbol.createSimple(map2)
        terrLayer = terrSymbol.symbolLayer(0)
        # tidal restriction
        map3 = {"name": "regular_star", "color": "255,0,0,255", "offset": "0,0",
               "color_border": "0,0,0,255", "size": "4.0", "angle": "DEFAULT_SIMPLEMARKER_ANGLE"} 
        tidalSymbol = newSymbol.createSimple(map3)
        tidalLayer = tidalSymbol.symbolLayer(0)
        # create a new symbol layer for the delete symbol (i.e. a red cross)
        map4 = {"name": "cross", "color": "255,0,0,255", "offset": "0,0",
               "color_border": "255,0,0,255", "size": "7.0", "angle": "45.0"}
        deleteSymbol = newSymbol.createSimple(map4)
        deleteLayer = deleteSymbol.symbolLayer(0)
        # create a new symbol layer for the altered symbol (i.e. a red triangle)
        map5 = {"name": "equilateral_triangle", "color": "0,0,0,0", "offset": "0,0",
               "color_border": "255,0,0,255", "size": "7.0", "angle": "DEFAULT_SIMPLEMARKER_ANGLE"} 
        alteredSymbol = newSymbol.createSimple(map5)
        alteredLayer = alteredSymbol.symbolLayer(0)
        
        # rule that makes dam symbol a rectangle
        rule1 = rendererV2.Rule(damSymbol, 0, 0, "dam_id!=''")
        rendererV2.addRule(rule1)
        # rule that makes terrestrial crossing structures a diamond
        rule2 = rendererV2.Rule(terrSymbol, 0, 0, "wildlf_id!=''")
        rendererV2.addRule(rule2)
        # rule that makes tidal restrictions a star
        rule3 = rendererV2.Rule(tidalSymbol, 0, 0, "restr_id!=''")
        rendererV2.addRule(rule3)
        # make the rule, using the delete symbol, and add it
        rule4 = rendererV2.Rule(deleteSymbol, 0, 0, 
            "c_deleted='y' or d_deleted='y' or w_deleted='y' or r_deleted='y'")
        rendererV2.addRule(rule4)
        # rule for altered symbol
        rule5 = rendererV2.Rule(alteredSymbol, 0, 0, 
            "c_altered = 'y' or d_altered = 'y' or w_altered = 'y' or r_altered = 'y'")
        rendererV2.addRule(rule5)
        
        # associate the new renderer with the activeVLayer
        vlayer.setRendererV2(rendererV2)
        
        # The coloredLayers dictionary is set when a saved scenario is opened, in Tools.shared.updateExtents() 
        # when reopening the editing layer after editing, in which case the rule renderer not set.  
        # If the user had set a color other than the default color red, we reset it here. 
        retval = self.legend.mainwindow.coloredLayers.get(vlayerName)
        # color set by user (either in scenario file or in this session) and being opened by updateExtents() or copyScenario
        if retval and retval != red: 
            symbols = rendererV2.symbols()
            print  "Main.legend.LegendItem.setRendererV2(): There is a layer color" + str(retval.getRgb())
            symbols[0].setColor(retval)
            symbols[1].setColor(retval)
            symbols[2].setColor(retval)
            symbols[3].setColor(retval)
        # This is the case where updateExtents or copyScenario is opening editing layers that are in coloredLayers with default red 
        # color. The layer was opened with a some unknown QGIS color but we reset the layer's color to red above, so pass.
        elif retval and retval == red: # for code clarity
            pass # color set above as default color
        # layer newly created with default colors so add the layer to the coloredLayers dictionary
        elif not retval: self.addLayerToColoredLayers() 
        else: print "Main.legend.LegendItem.setRendererV2(): There is a 'retval' error"
        
        # color the preview icon
        #self.legend.currentItem().vectorLayerSymbology(vlayer)
        vlayer.triggerRepaint()
        
        # debugging
        #print "The delete layers name is: " + deleteLayer.name()
        print "Main.legend.LegendItem.setRendererV2(): The number of symbols is: " + str(len(rendererV2.symbols()))
        print "Main.legend.LegendItem.setRendererV2(): The number of rules is: " + str(rendererV2.ruleCount())
        print "Main.legend.LegendItem.setRendererV2(): The symbolLayer properties are: "
        for k, v in symbolLayer.properties().iteritems():
            print "%s: %s" % (k, v)
        print "Main.legend.LegendItem.setRendererV2(): The damLayer properties are: "
        for k, v in damLayer.properties().iteritems():
            print "%s: %s" % (k, v) 
        print "Main.legend.LegendItem.setRendererV2(): The terrLayer properties are: "
        for k, v in terrLayer.properties().iteritems():
            print "%s: %s" % (k, v) 
        print "Main.legend.LegendItem.setRendererV2(): The tidalLayer properties are: "
        for k, v in tidalLayer.properties().iteritems():
            print "%s: %s" % (k, v) 
        print "Main.legend.LegendItem.setRendererV2(): The deleteLayer properties are: "
        for k, v in deleteLayer.properties().iteritems():
            print "%s: %s" % (k, v)
        print "Main.legend.LegendItem.setRendererV2(): The alteredLayer properties are: "
        for k, v in alteredLayer.properties().iteritems():
            print "%s: %s" % (k, v)
        print "Main.legend.LegendItem.setRendererV2(): The damLayer properties are: "
        for k, v in damLayer.properties().iteritems():
            print "%s: %s" % (k, v)
            
    def setLineColorAndWidth(self, vlayer, red, vlayerName):
        # debugging
        print "Main.legend.LegendItem.setLineColorAndWidth()"
        
        # this is a QgsLineSymbolLayerV2()
        symbolLayer = vlayer.rendererV2().symbols()[0].symbolLayer(0)
        
        # This dictionary (coloredLayers) is set when a saved scenario is opened, when an editing layer is created 
        # (in dlgscenarioedittypes) or in Tools.shared.updateExtents() when reopening the editing layer after editing. 
        # If the user had set a color other than the default,we reset it here. 
        retval = self.legend.mainwindow.coloredLayers.get(vlayerName)
        if retval and retval != red: # being opened by updateExtents or copyScenario and user set color
            print "Main.legend.LegendItem.setRendererV2(): THERE IS A LINE COLOR"
            symbolLayer.setColor(retval)
        # being opened by updateExtents or copyScenario with some unknown QGIS color so we reset to red here
        elif retval and retval == red: 
            symbolLayer.setColor(retval)
        # newly opened layer (not in coloredLayers) so default to red if the layer is being opened for the first time
        elif not retval:    
            symbolLayer.setColor(red)
            self.addLayerToColoredLayers() 
        else: print "Main.legend.LegendItem.setRendererVretvalThere is a 'retval' error"
        
        symbolLayer.setWidth(0.4)
        vlayer.triggerRepaint()
        
    def setPolygonColor(self, vlayer, red, vlayerName):
        # debugging
        print "Main.legend.LegendItem.setPolygonColor()" 
        
        # This dictionary (coloredLayers) is set when a saved scenario is opened, when an editing layer is created 
        # (in dlgscenarioedittypes) or in Tools.shared.updateExtents() when reopening the editing layer after editing. 
        # If the user had set a color other than the default,we reset it here.
        symbolLayer = vlayer.rendererV2().symbols()[0].symbolLayer(0)
        retval = self.legend.mainwindow.coloredLayers.get(vlayerName)
        if retval and retval != red: # being opened by updateExtents or copyScenario and user has set color
            print "Main.legend.LegendItem.setRendererV2(): THERE IS A POLYGON COLOR"
            symbolLayer.setColor(retval)
            return
        # being opened by updateExtents or copyScenario with some unknown QGIS color so we reset to red here
        elif retval and retval == red: # being opened by copyScenario
            symbolLayer.setColor(retval)
        else: # if the layer being loaded into the scenario for the first time default to red
            symbolLayer.setColor(red)
            self.addLayerToColoredLayers()
        vlayer.triggerRepaint()
        
    def setBaseTownsProperties(self, vlayer):
        # debugging
        print "Main.legend.LegendItem.setBaseTownsProperties()"
        
        # Set the base_towns layer fill color to none
        rendererV2 = vlayer.rendererV2()
        symbol = rendererV2.symbols()[0]
        
        symbolMap = {"color": "255, 255, 255, 255", "style": "no", 
                          "color_border": "DEFAULT_SIMPLEFILL_BORDERCOLOR", 
                          "style_border": "DEFAULT_SIMPLEFILL_BORDERSTYLE", 
                          "width_border": "0.3" }
        
        simpleSymbol = symbol.createSimple(symbolMap)
        rendererV2.setSymbol(simpleSymbol)
        self.addLayerToColoredLayers()
        vlayer.triggerRepaint()

class Legend(QtGui.QTreeWidget):
    """
      Provide a widget that manages map layers and their symbology as tree items
    """
    def __init__(self, parent):
        QtGui.QTreeWidget.__init__(self, parent)
        
        # debugging
        print "Main.legend.Legend() class"
        
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
        self.currentColor = None
 
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
        
        # Need this to stop user from clicking the legend while making line or polygon edits.
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

        # set some variables
        layer = self.currentItem().canvasLayer.layer()
        layerId = self.currentItem().canvasLayer.layer().id()
        name = unicode(layer.name())

        ''' Check and warn on removing an editing layer '''

        if name in config.editLayersBaseNames:
            reply = QtGui.QMessageBox.warning(self, "Warning!", "Removing '" + name + "' \
from the legend will cause all that layer's files and any associated 'Export Scenario' file to be deleted from \
the file system. All changes to these files will be lost. Do you want to delete this file(s)?", 
                                                        QtGui.QMessageBox.No|QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.No: return # user canceled so don't remove layer
            else: # user chose ok
                # since we are deleting an editing layer we should be safe and 
                # remove any exported scenario files.
                self.mainwindow.deleteExportScenarioFile()
                # So we can delete the editing shapefile but must remove from registry first!
                # Note that this method also checks if the layer is in the originalScenarioLayers
                # list, sets self.mainwindow.scenarioDirty = True, enables the 'Save Scenario' button
                # and removes the layer from the originalScenarioLayers list.
                self.removeLayerFromRegistry(layer, layerId, True)
                # Finally, delete the editing layer
                editFilePath = unicode(layer.source())
                self.deleteEditingLayer(editFilePath)
                # If the layer name exists in coloredLayers dictionary, remove it.
                self.mainwindow.coloredLayers.pop(name, None)

                # debugging
                print "Mainwindow.legend.removeCurrentLayer(): layer was removed from originalScenarioLayers"
                print "Main.legend.Legend.removeCurrentLayer(): The coloredLayers are: "
                for k, v in self.mainwindow.coloredLayers.iteritems():
                    print "%s: %s" % (k, str(v.getRgb()))

                # If we have deleted the edit layer for current scenario edit type, then
                # reset the editLayerName and the editDirty flag.
                if name == self.mainwindow.editLayerName:
                    self.mainwindow.editLayerName = None
                    self.mainwindow.editDirty = False
                return # we are done deleting the layer so return

        ''' 
            Note that this section handles a layer whether it is a raster or vector
            and NOT an editing layer.  The layer could still be an originalScenarioLayer.
        '''

        # Remove the layer from the registry. Note that this method also checks if the layer is in the originalScenarioLayers
        # list and sets self.mainwindow.scenarioDirty = True and removes the layer from the originalScenarioLayers list.
        self.removeLayerFromRegistry(layer, layerId, True)

        # debugging
        print ("Mainwindow.legend.removeCurrentLayer(): length originalScenarioLayers after removal " 
                                                                        + str(len(self.mainwindow.originalScenarioLayers)))
        print "Main.legend.Legend.removeCurrentLayer(): The coloredLayers are: "
        for k, v in self.mainwindow.coloredLayers.iteritems():
            print "%s: %s" % (k, str(v.getRgb()))
        print "Mainwindow.legend.removeCurrentLayer(): The deleted color is " + str(self.mainwindow.coloredLayers.pop(name, None))

    def layerSymbology(self):
        """ Change the features color of a vector layer """
        # debugging
        print "Main.legend.layerSymbology()"
        legendLayer = self.currentItem()
        
        if legendLayer.isVect == True:
            geom = legendLayer.canvasLayer.layer().geometryType() # QGis Geometry
            for i in self.layers:
                if i.layer().id() == legendLayer.layerId:
                    color = QtGui.QColorDialog.getColor(i.layer().rendererV2().symbols()[ 0 ].color(), self.mainwindow)
                    break

            if color.isValid():
                legendLayer.canvasLayer.layer().rendererV2().symbols()[0].setColor(color)
                name = unicode(legendLayer.canvasLayer.layer().name())
                # remember the layer's name and color, or reset the color if the name is in the dictionary
                self.mainwindow.coloredLayers[name] = color
                if unicode(legendLayer.canvasLayer.layer().name()) == unicode(config.editLayersBaseNames[0]):
                    print "Main.legend.layerSymbology(): is edit_scenario(points)"
                    # if edit_scenario points, we need to set the color for all the symbols (i.e. box, pentagon and star) 
                    legendLayer.canvasLayer.layer().rendererV2().symbols()[1].setColor(color)
                    legendLayer.canvasLayer.layer().rendererV2().symbols()[2].setColor(color)
                    legendLayer.canvasLayer.layer().rendererV2().symbols()[3].setColor(color)
                
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
        # debugging
        print "Main.legend.updateLayerSet()"
        
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
        # debugging
        print 'Main.legend.Legend.normalizeLayerName()'
        # Remove the extension
        if len(name) > 4:
            if name[-4] == '.': name = name[:-4]

        return self.createUniqueName(name)

    def createUniqueName(self, name):
        """ Avoid to repeat layers names """
        # debugging
        print 'Main.legend.Legend.createUniqueName()'
        
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
        ''' Removes an editing shapefile. '''
        # debugging
        print "Main.legend.deleteEditingLayer()"
        print "Main.legend.deleteEditingLayer(): editFilePath is " + editFilePath

        editFile = QtCore.QFile(editFilePath)
        if editFile.exists():
            print "Main.legend.deleteEditingLayer(): editFile exists is True"
            writer = QgsVectorFileWriter.deleteShapeFile(editFilePath)
        if not writer: # writer returns true if delete successful
            QtGui.QMessageBox.warning(self, "File Error", "The editing shapefile could not be deleted. \
Please check if it is open in another program and try again.")
            return False
        else: return True
     
    def removeLayerFromRegistry(self, layer, layerId, removeCurrentLayer = False):
        ''' Remove a layer from the registry. This method is called by self.removeCurrentLayer() and 
            Tools.shared.updateExtents(). This method is also called by Main.mainwindow.checkScenarioState()
            (when discarding scenario changes) where the layer to be removed is probably not the activeVLayer. 
            In fact the activeVLayer could be "None," or the active layer could be a raster. If the layer is 
            the activeVLayer, we need to reset activeVLayer variables after removing the layer from the registry.
        '''
        # debugging
        print "Main.legend.removeLayerFrom Registry()"

        # We need to record some variables before we delete the layer.
        name = unicode(layer.name())
        # 
        activeLayerId = None
        if self.mainwindow.activeVLayer:
            activeLayerId = self.mainwindow.activeVLayer.id()
        elif self.mainwindow.activeRLayer:
            activeLayerId = self.mainwindow.activeRLayer.id()

        # Check if the layer to be moved is in the originalScenarioLayers list and remove if it is. This needs to be done before 
        # removing the layer from the registry, which calls Main.mainwindow.MainWindow.activeLayerChanged(), or we sometimes 
        # get an "underlying C++ object deleted when debugging or other code tries to read originalScenarioLayers list.
        inOriginalScenario = False
        originalScenarioLayers = self.mainwindow.originalScenarioLayers
        layerToRemove = None
        if layer in originalScenarioLayers:
            print ("Main.legend.removeEditLayerFrom Registry(): length originalScenarioLayers before removal "
                                                                                + str(len(originalScenarioLayers)))
            layerToRemove = layer
            originalScenarioLayers.remove(layerToRemove)
            self.mainwindow.scenarioDirty = True
            self.mainwindow.mpActionSaveScenario.setDisabled(False)
            print 'Main.legend.removeEditLayerFrom Registry(): The activeVLayer was removed from the originalScenarioLayers'
            print ('Main.legend.removeEditLayerFrom Registry(): length originalScenarioLayers after removal ' 
                                                                                        + str(len(originalScenarioLayers)))
            inOriginalScenario = True

        # Remove the layer from the registry
        QgsMapLayerRegistry.instance().removeMapLayer(layerId)
        
        # if the removed layer is the current activeVLayer, reset all associated variables
        if activeLayerId == layerId:
            self.setActiveLayerVariables() 

        # If the calling action is removeCurrent layer, we need to let signals proceed normally.
        # If the calling action is shared.updateExtents or mainwindow.chkScenarioState then
        # we do not because either a new layer will immediately load or the app will close.
        if removeCurrentLayer:
            # Layer is successfully removed from registry so remove it from legend.
            self.removeLayerFromLegendById(layerId)
            self.updateLayerSet()
            self.mainwindow.coloredLayers.pop(name, None)
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
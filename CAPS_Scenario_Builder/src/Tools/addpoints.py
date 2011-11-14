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
from PyQt4 import QtCore, QtGui 
# QGIS bindings for mapping functions
from qgis.core import *
from qgis.gui import *
# CAPS application imports
from dlgaddattributes import DlgAddAttributes
import shared

class AddPoints(QgsMapTool):
    ''' Provide a tool to add new points and their attributes to an editing shapefile '''
    def __init__(self, parent):
        QgsMapTool.__init__(self, parent.canvas)
        
        # debugging
        print "Class AddPoints()"
        
        ''' This class is initiated whenever the add points action is
            selected.  The add points action is set to unselected
            whenever the active layer is changed, so the instance variables below
            always get updated whenever the active layer changes.
        '''
        
        # make handle to mainwindow
        self.mainwindow = parent
        self.canvas = parent.canvas

#######################################################################
    ''' Overridden QgsMapTool Events '''
#######################################################################

    def canvasPressEvent(self, event):
        ''' Get point and transform to map coordinates '''
        # get the current activeVLayer from mainwindow
        self.activeVLayer = self.mainwindow.activeVLayer
        if self.activeVLayer == None:
            return
        point = event.pos()
        transform = self.canvas.getCoordinateTransform()
        # returns a QgsPoint object in map coordinates
        self.qgsPoint = transform.toMapCoordinates(point.x(), point.y())
        print "The point is " + str(self.qgsPoint)
        
        # check if the proper editing layer is selected
        currentLayerName = self.mainwindow.legend.currentItem().canvasLayer.layer().name()
        if shared.checkSelectedLayer(self.mainwindow, self.mainwindow.scenarioType, 
                                                         currentLayerName) == "Cancel":
            self.qgsPoint = None
            return # if wrong edit layer cancel drawing
        
        ''' 
            Check constraints on the added point for the scenario edit type, 
            and prompt the user if constraints are not met.
        '''
        
        # First check if the point can be snapped to a new road in the scenario
        if shared.newRoadExists(self.mainwindow):
            if shared.snapToNewRoad(self.mainwindow, point) != []:
                return

        # If not editing a new road.
        # This method returns False if the constraints are not met.
        if not shared.checkConstraints(self.mainwindow, self.qgsPoint):
            self.qgsPoint = None
            return
        else: pass
        
        # correct editing layer selected and constraints check OK so get the new attributes
        self.getNewAttributes()

    def canvasReleaseEvent(self, event):
        pass
     
######################################################################
    ''' Core Methods '''
######################################################################
 
    def getNewAttributes(self):
        # debugging
        print "Class AddPoints() getNewAttributes()"
        
        self.dlg = DlgAddAttributes(self.mainwindow)

        if self.dlg.exec_(): # The user has clicked "OK"
            attributes = self.dlg.getNewAttributes() # method has the same name in DlgAddAttributes()
            #attributes = {0 : QtCore.QVariant(id), 1 : QtCore.QVariant(type)}
            self.markPoint(attributes) 
    
    def markPoint(self, attributes):
        ''' Add the new feature and display '''
        # debugging
        print "markPoint starting"
        # set the current provider
        self.provider = self.mainwindow.provider
        # make a list of the original points in the active layer
        self.originalFeats = shared.listOriginalFeatures(self.provider)
        # need to update the mainwindow instance variable for call to Tools.shared.deleteEdits
        self.mainwindow.originalFeats = self.originalFeats
        
        feat = QgsFeature()
        vlayerName = self.mainwindow.activeVLayer.name()
        # add the point geometry to the feature
        feat.setGeometry(QgsGeometry.fromPoint(self.qgsPoint))
        feat.setAttributeMap(attributes)
        # this actually writes the added point to disk!
        try:
            self.mainwindow.provider.addFeatures( [ feat ] )
        except (IOError, OSError), e:
            error = unicode(e)
            print error                    
            QtGui.QMessageBox.warning(self, "Failed to add feature(s)", "Please check if "
                                 + vlayerName + " is open in another program and then try again.")
        
        
        
        # reset the id numbers for the editing layer
        shared.resetIdNumbers(self.provider, self.mainwindow.geom)
        
        # update the attribute table if open
        if self.mainwindow.attrTable and self.mainwindow.attrTable.isVisible():
            self.mainwindow.openVectorAttributeTable()
        
        # set the edit flag to unsaved
        self.mainwindow.editDirty = self.activeVLayer.name()
        # enable the save edits action
        self.mainwindow.mpActionSaveEdits.setDisabled(False)
        
        # debugging
        print "the edit flag was set to " + self.activeVLayer.name() + " by MarkPoint."
        print "the number of features added is " + str(shared.numberFeaturesAdded
                                                         (self.activeVLayer, self.originalFeats))
        # The method below works for deleting features, but it doesn't work
        # for adding features.  The extents are NOT updated in any variation.
        shared.updateExtents(self.mainwindow, self.mainwindow.provider, self.mainwindow.activeVLayer, 
                                                                    self.mainwindow.canvas)
        
#**************************************************************
    ''' Testing '''
#**************************************************************

    def printFeatures(self):       
        "startingPrintFeatures"
        #self.provider.reloadData()
        feat = QgsFeature()
        allAttrs = self.provider.attributeIndexes()
        self.provider.select(allAttrs)
        # the nextFeature() method operates on a select initialized provider
        while self.provider.nextFeature(feat):
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

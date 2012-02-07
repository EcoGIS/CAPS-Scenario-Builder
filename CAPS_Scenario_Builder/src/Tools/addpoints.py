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
# -----------------------------------------------------------------------------------
# PyQt4 includes for python bindings to QT
from PyQt4 import QtCore, QtGui 
# QGIS bindings for mapping functions
from qgis.core import *
from qgis.gui import *
# CAPS application imports
from dlgaddattributes import DlgAddAttributes
import shared, config

class AddPoints(QgsMapTool):
    ''' Provide a tool to add new points and their attributes to an editing shapefile '''
    def __init__(self, parent):
        QgsMapTool.__init__(self, parent.canvas)
        
        # debugging
        print "Tools.addpoints.AddPoints() class"
        
        ''' 
        This class is instantiated once when Main.mainwindow is instantiated. The instance 
        variables below always get updated from the mainwindow whenever the active layer 
        changes, so there is no need to instantiate this class more than once.
        
        '''
        
        # make handle to mainwindow
        self.mainwindow = parent
        self.canvas = parent.canvas

#######################################################################
    ''' Overridden QgsMapTool Events '''
#######################################################################

    def canvasPressEvent(self, event):
        ''' Get point and transform to map coordinates '''
        # Set the active vector layer. Note that this method cannot be called unless the
        # currently active layer is the correct editing layer for the scenario edit type.
        self.activeVLayer = self.mainwindow.activeVLayer
        if self.activeVLayer == None: return
       
        qPoint = event.pos()
        transform = self.canvas.getCoordinateTransform()
        # returns a QgsPoint object in map coordinates
        self.qgsPoint = transform.toMapCoordinates(qPoint.x(), qPoint.y())
        
        #debugging
        print "Tools.addpoints.AddPoints().canvasPressEvent(): The original clicked point in map coordinates is " + str(self.qgsPoint)
        
        ''' 
            Check constraints on the added point for the scenario edit type, 
            and prompt the user if constraints are not met.
        '''
 
        '''# First check if the point can be snapped to a new road in the scenario
        if shared.newRoadExists(self.mainwindow):
            snappedQgsPoint = shared.snapToNewRoad(self.mainwindow, point)
            print "Tools.addpoints.AddPoints().canvasPressEvent(): The returned snappedPoint is " + str(snappedQgsPoint)
            if snappedQgsPoint:
                # constraints are satisfied because clicked point is on a new road
                # set the new wildlife crossing's point to be the point on the new road
                self.qgsPoint = snappedQgsPoint
                self.getNewAttributes()
                return '''   
        # If not editing a new road check constraints.
        # This method returns False if the constraints are not met.
        if not shared.checkConstraints(self.mainwindow, self.qgsPoint, qPoint):
            self.qgsPoint = None
            return
        # correct editing layer selected and constraints check OK so get the new attributes
        else: self.getNewAttributes()

    def canvasReleaseEvent(self, event):
        pass
     
######################################################################
    ''' Core Methods '''
######################################################################
 
    def getNewAttributes(self):
        # debugging
        print "Tools.addpoints.AddPoints().getNewAttributes()"
        
        self.dlg = DlgAddAttributes(self.mainwindow)

        if self.dlg.exec_(): # The user has clicked "OK"
            attributes = self.dlg.getNewAttributes() # method has the same name in DlgAddAttributes()
            self.markPoint(attributes) 
 
    def markPoint(self, attributes):
        ''' Add the new feature and display '''
        # debugging
        print "Tools.addpoints.AddPoints().markPoint(): markPoint starting"
        print "Tools.addpoints.AddPoints().markPoint(): The self.qgsPoint is " + str(self.qgsPoint)
        
        # set the current provider
        self.provider = self.mainwindow.provider
        
        feat = QgsFeature()
        geometry = QgsGeometry()
        # Convert QStrings to unicode unless they are used immediately in a Qt method. 
        # This ensures that we never ask Python to slice a QString, which produces a type error.
        vlayerName = unicode(self.activeVLayer.name())
        # add the point geometry to the feature
        feat.setGeometry(geometry.fromPoint(self.qgsPoint))
        # add the user's input attributes to the feature
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
        self.mainwindow.editDirty = True
        
        # debugging
        print "Tools.addpoints.AddPoints().markPoint(): the edit flag was set to " + vlayerName 
        print "Tools.addpoints.AddPoints().markPoint(): The vlayer name is " + vlayerName
        print "Tools.addpoints.AddPoints().markPoint(): the number of features added is " + str(
                                                shared.numberFeaturesAdded(self.activeVLayer, self.mainwindow.originalEditLayerFeats))
        
        # enable the save edits action
        self.mainwindow.mpActionSaveEdits.setDisabled(False)
        # refresh the extents of the map on the canvas
        shared.updateExtents(self.mainwindow, self.activeVLayer, self.canvas)

#**************************************************************
    ''' Testing '''
#**************************************************************

    def printFeatures(self):       
        "Tools.addpoints.AddPoints().printFeatures: (Testing)"
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

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
import shared
import config

# Select tool class - Used to select features
class SelectTool(QgsMapTool):
    ''' Provide a tool to select features '''
    def __init__(self, parent):
        QgsMapTool.__init__(self, parent.canvas)
     
        # Make handle to mainwindow and call all variables needed for methods from mainwindow.
        # This allows variables to be updated when the active layer changes so that 
        # re-instantiating the class every time a layer changes is not necessary.
        self.mainwindow = parent
        self.transform = None

#######################################################################
    ''' Overridden QgsMapTool Events '''
#######################################################################
 
    def canvasPressEvent(self, event):
        if self.mainwindow.activeVLayer == None: return
        
        # do not allow selecting or deleting from an orientingBaseLayer (i.e. base_towns)
        name = self.mainwindow.activeVLayer.name()
        fileName = name + '.shp'
        if fileName in config.orientingVectorLayers:
            QtGui.QMessageBox.warning(self.mainwindow, "Selection Error:", 
                     "You cannot select or delete features from the " + name + " base layer." )
            return
        point = event.pos()
        self.transform = self.mainwindow.canvas.getCoordinateTransform()
        self.selectFeat(point)
 
    def canvasReleaseEvent(self, event):
        pass      
    
#######################################################################
    ''' Core Methods '''
#######################################################################  

    def selectFeat(self, point):
        # debugging
        print "SelectTool(): selectFeat"
        activeVLayer = self.mainwindow.activeVLayer
        selectRect = shared.makeSelectRect(self.mainwindow.geom, point, self.transform)        
        activeVLayer.select(selectRect, True)
        #self.mainwindow.canvas.refresh()


        
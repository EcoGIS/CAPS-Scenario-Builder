## -*- coding:utf-8 -*-
#--------------------------------------------------------------------- 
#
# Conservation Assessment and Prioritization System (CAPS) Scenario Builder - An Open Source  
# GIS tool to create scenarios for environmental modeling.
#
#---------------------------------------------------------------------- 
# Copyright (C) 2007  Ecotrust
# Copyright (C) 2007  Aaron Racicot
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
#---------------------------------------------------------------------
# General system includes
import sys, string
# PyQt4 includes for python bindings to QT
from PyQt4 import QtCore
from PyQt4 import QtGui
# QGIS bindings for mapping functions
from qgis.core import *
from qgis.gui import *
  
class MapCoords(object):
    ''' Display mouse position in map coordinates in the statusbar '''
    def __init__(self, parent):
        self.parent = parent
        
        # debugging
        print "Tools.mapcoords.MapCoords() class"
    
        # This captures the mouse move for coordinate display
        QtCore.QObject.connect(parent.canvas, QtCore.SIGNAL("xyCoordinates(const QgsPoint &)"),
                        self.updateCoordsDisplay)
        self.latlon = QtGui.QLabel("0.0 , 0.0")
        self.latlon.setFixedWidth(150)
        self.latlon.setAlignment(QtCore.Qt.AlignHCenter)
        self.parent.statusBar.addPermanentWidget(self.latlon)

    # Signal handler for updating coord display
    def updateCoordsDisplay(self, p):
        capture_string = "%.2f" % float(p.x()) + " , " + "%.2f" % float(p.y())
        self.latlon.setText(capture_string)

  

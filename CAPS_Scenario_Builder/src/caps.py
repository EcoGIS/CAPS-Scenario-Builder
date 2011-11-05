#!/usr/bin/python
# The line above alerts linux/unix systems about where to find python
# 
# -*- coding:utf-8 -*-
#------------------------------------------------------------
# 
# Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
# self.mpActionToggleEditing.blockSignals(True)
# -----------------------------------------------
# Copyright (C) 2007  Ecotrust
# Copyright (C) 2007  Aaron Racicot
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
# 
#---------------------------------------------------------------------
# #@UnresolvedImport blocks import errors
# General system includes
import sys, os
# import Qt libraries
from PyQt4 import QtGui, QtCore
# QGIS bindings for mapping functions
# This format eliminates import errors in 
# Eclipse Pydev when qgis is added to Eclipse builtins
from qgis.core import * 
from qgis.gui import *
# CAPS application imports
from Main.mainwindow import MainWindow

# Version variable in case the app changes later
__version__ = "1.0.0"

# Path to local QGIS install
#qgis_prefix = "C:\\Program Files\\Quantum GIS Copiapo\\apps\\qgis"
qgis_prefix = os.getenv("qgis_prefix")

# the below does not work on Windows in any variation
#QgsApplication.setPrefixPath("C:\Program Files\Quantum GIS Copiapo\apps\qgis", True)

# Main entry to program.  Set up the main app and create a new window.
def main(argv):
    
    # create Qt application
    app = QtGui.QApplication(argv, True)
        
    # add a splash screen on startup   
    mySplashPix = QtGui.QPixmap(QtCore.QString("./src/CAPS_splash.png"))
    mySplashPixScaled = mySplashPix.scaled(500,300,QtCore.Qt.KeepAspectRatio)
    mySplash = QtGui.QSplashScreen(mySplashPixScaled)
    mySplash.show()
   
    # initialize qgis libraries
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
    
    # create main window
    mainwindow = MainWindow(mySplash)
    mainwindow.show()

    # Start the app up 
    retval = app.exec_()

    # For some unknown reason, 
    # close app needs to be referenced before the connection below 
    def closeApp():
        ''' Manage app termination '''
        print "caps.closeApp() called"
            
        app.closeAllWindows
        app.quit() 

        # We exited the Qt app so time to clean up the Qgis app
        QgsApplication.exitQgis()
    
        #app.exitQgis()
        sys.exit(retval)
    
    # Create connection for app finish
    QtCore.QObject.connect(app, QtCore.SIGNAL("aboutToQuit()"), closeApp())
    #app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))

if __name__ == "__main__":
    main(sys.argv)

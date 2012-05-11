# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
#
# Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
#
#--------------------------------------------------------------------- 
# 
# Copyright (C) 2011  Robert English: Daystar Computing (http://edaystar.com)
#
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
# import Qt libraries
from PyQt4 import QtCore, QtGui
# import qgis API
#from qgis.core import *
# import the ui made with Qt Designer
from dlgmanageprojects_ui import Ui_DlgManageProjects
# CAPS application imports
#import config
#import Tools.shared


class DlgManageProjects(QtGui.QDialog, Ui_DlgManageProjects):
    """ Open a dialog to create, copy, edit, or send projects """
    def __init__(self, mainwindow):
        QtGui.QDialog.__init__(self, mainwindow)
        self.setupUi(self)
        
        # debugging
        print "Main.dlgmanageprojects.DlgManageProjects class"
        
        self.mainwindow = mainwindow
       
        QtCore.QObject.connect(self.sendButton, QtCore.SIGNAL(("clicked()")), self.sendProject)
        QtCore.QObject.connect(self.projectsButtonBox, QtCore.SIGNAL(("accepted()")), self.saveProject)
        QtCore.QObject.connect(self.projectsButtonBox, QtCore.SIGNAL(("rejected()")), self.reject)
        QtCore.QObject.connect(self.projectsButtonBox, QtCore.SIGNAL(("clicked(QAbstractButton*)")), self.deleteProject)
        QtCore.QObject.connect(self.addScenarioButton, QtCore.SIGNAL(("clicked()")), self.addScenarioToProject)
        QtCore.QObject.connect(self.removeScenarioButton, QtCore.SIGNAL(("clicked()")), self.removeScenarioFromProject)
                
#################################################################################
    ''' Custom slots '''
#################################################################################    
    
    def reject(self):
        ''' User clicked the "Cancel" button. '''
        print "Main.manageprojects.DlgManageProjects().reject(): user closed the dialog"
        self.hide()
        #return
        
    def sendProject(self):
        ''' Send the project file and associated scenario files to UMass via SFTP. '''
        print "Main.manageprojects.DlgManageProjects().sendProject()"
    
    def saveProject(self):
        ''' Write the project information to a text file. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().saveProject()"
        
    def deleteProject(self, button):
        ''' Delete the current project file and leave the dialog open. '''
        if unicode(button.text()) == "Discard":
            print "Main.manageprojects.DlgManageProjects().deleteProject()"
            print unicode(button.text())
        
    def addScenarioToProject(self):
        ''' 
            Write the selected project name(s) from the "Existing Scenario files" list widget
            to the "Scenario files in Project" list widget. 
        '''
        print "Main.manageprojects.DlgManageProjects().addScenarioToProject()"
        
    def removeScenarioFromProject(self):
        ''' Remove the selected file name(s) from the "Scenario files in Project" list widget. '''    
        print "Main.manageprojects.DlgManageProjects().removeScenarioFromProject()"
        
#################################################################################   
    ''' Core methods '''   
#################################################################################
    
    def writeProjectFile(self):
        ''' A method to write the project file to disk. '''
        print "Main.manageprojects.DlgManageProjects().writeProjectFile()"
    
    def readProjectFile(self):
        ''' A method to parse the project file to populate the widgets in this dialog. '''
        print "Main.manageprojects.DlgManageProjects().readProjectFile()"
        
     
    

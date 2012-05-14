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
# general python imports
import os #, shutil, time, os.path #  copy, subprocess, sys,  stat,
# import Qt libraries
from PyQt4 import QtCore, QtGui
# import qgis API
#from qgis.core import *
# import the ui made with Qt Designer
from dlgmanageprojects_ui import Ui_DlgManageProjects
# CAPS application imports
import config
#import Tools.shared


class DlgManageProjects(QtGui.QDialog, Ui_DlgManageProjects):
    """ Open a dialog to create, copy, edit, or send projects """
    def __init__(self, mainwindow):
        QtGui.QDialog.__init__(self, mainwindow)
        self.setupUi(self)
        
        # debugging
        print "Main.dlgmanageprojects.DlgManageProjects class"
        
        self.mainwindow = mainwindow
        
        ''' Set the initial dialog display to 'create a new project' mode ''' 
        self.setCreateNewProjectMode()     
      
        QtCore.QObject.connect(self.sendButton, QtCore.SIGNAL(("clicked()")), self.sendProject)
        QtCore.QObject.connect(self.projectsButtonBox, QtCore.SIGNAL(("accepted()")), self.saveProject)
        QtCore.QObject.connect(self.projectsButtonBox, QtCore.SIGNAL(("rejected()")), self.reject)
        QtCore.QObject.connect(self.projectsButtonBox, QtCore.SIGNAL(("clicked(QAbstractButton*)")), self.deleteProject)
        QtCore.QObject.connect(self.addScenarioButton, QtCore.SIGNAL(("clicked()")), self.addScenarioToProject)
        QtCore.QObject.connect(self.removeScenarioButton, QtCore.SIGNAL(("clicked()")), self.removeScenarioFromProject)
        QtCore.QObject.connect(self.selectProjectComboBox, QtCore.SIGNAL(("currentIndexChanged(QString)")), self.displayProjectInfo)
                
#################################################################################
    ''' Custom slots '''
#################################################################################    
            
    def displayProjectInfo(self, filename):        
        ''' Display the project information for the project selected in selectProjectComboBox. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().displayProjectInfo"
        print "Project Name is: " + filename 
        
        # If the filename == "" then check if project is dirty and warn the user about losing data.
        if not filename:
            self.checkIsProjectDirty()
            self.setCreateNewProjectMode()
        
        # Parse the project file to set needed instance variables with project information.
        self.readProjectFile()
        
        # If there are no project scenario files then display the following message.
        if self.scenariosInProject == []:
            noScenariosMessage = ["You have not added any Scenarios."]
            self.projectScenarioFileList.clear()
            self.projectScenarioFileList.addItems(noScenariosMessage)
        
        # We are opening a project so check if all the scenario files listed in the project's text file
        # actually exist in the Scenarios directory.
        self.checkIfScenarioFilesExist()
                     
    def addScenarioToProject(self):
        ''' 
            Write the selected project name(s) from the "Existing Scenario files" list widget
            to the "Scenario files in Project" list widget. 
        '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().addScenarioToProject()"
        print "The selected items are: " 

        existingList =  self.existingScenarioFileList
        projectList = self.projectScenarioFileList
        
        # if noting is selected in the list widget tell the user.
        if existingList.selectedItems() == [] or existingList.item(0).text() == "You have not created any Scenarios.":
            QtGui.QMessageBox.warning(self, "Add Scenario error:", "You must select at least one scenario from the \
'Existing Scenario files:' list before you can add  a scenario to the project.")
        else:
            # If the 'newProject' text was set then clear the projectScenarioFileList widget.             
            if projectList.item(0):
                if projectList.item(0).text() == "To create a new project," or projectList.item(0).text() == "You have not added any Scenarios.":
                    projectList.clear()
              
            addScenarioList = []
            for selectedItem in existingList.selectedItems():
                addScenarioList.append(selectedItem.text())
                existingList.takeItem(existingList.row(selectedItem))
            projectList.addItems(addScenarioList)
    
    def removeScenarioFromProject(self):
        ''' Remove the selected file name(s) from the "Scenario files in Project" list widget. '''    
        # debugging
        print "Main.manageprojects.DlgManageProjects().removeScenarioFromProject()"
        
        existingList =  self.existingScenarioFileList
        projectList = self.projectScenarioFileList
        
        # if nothing is selected in the list widget tell the user.
        if (projectList.selectedItems() == [] or projectList.item(0).text() == "To create a new project,"
                                              or projectList.item(0).text() == "You have not added any Scenarios."):
            QtGui.QMessageBox.warning(self, "Remove Scenario error:", "You must select at least one scenario from the \
'Scenario files in Project:' list before you can remove a scenario from the project.")
        else:
            removeScenarioList = []
            for selectedItem in projectList.selectedItems():
                removeScenarioList.append(selectedItem.text())
                projectList.takeItem(projectList.row(selectedItem))
            existingList.addItems(removeScenarioList)    
    
    def saveProject(self):
        ''' Write the project information to a text file. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().saveProject()"
        
        # make sure project list is refreshed if a new project.
        
    def deleteProject(self, button):
        ''' Delete the current project file and leave the dialog open. '''
        # debugging
        if unicode(button.text()) == "Discard":
            print "Main.manageprojects.DlgManageProjects().deleteProject()"
            print unicode(button.text())

    def reject(self):
        ''' User clicked the "Cancel" button. '''
        # debugging
        
        print "Main.manageprojects.DlgManageProjects().reject(): user closed the dialog"
        self.hide()
        
    def sendProject(self):
        ''' Send the project file and associated scenario files to UMass via SFTP. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().sendProject()"
        
#################################################################################   
    ''' Core methods '''   
#################################################################################
    
    def writeProjectFile(self):
        ''' A method to write the project file to disk. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().writeProjectFile()"
    
    def readProjectFile(self):
        ''' A method to parse the project file to populate the widgets in this dialog. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().readProjectFile()"
        
        self.scenariosInProject = []
        
    def listFiles(self, path):
        ''' A method to return the list of scenario files in the Scenarios directory '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().listFiles()"
        print "The path is: " + path
        
        directoryList = []
        filesList = []
        try: # trap error if directory is missing for some reason
            directoryList = os.listdir(path) # use Python os module here
        except (IOError, OSError), e:
            error = e
            if error:
                print error
                QtGui.QMessageBox.warning(self, "Export Scenario Error:", "The files in the \
'Projects' or 'Scenarios' directory could not be listed.  Please try again")
                return False
    
        if path == "./Projects/":
            filesList = ["",]
            for dirItem in directoryList:
                if dirItem.endswith((".cpj", ".CPJ")):
                    filesList.append(dirItem)
            if filesList == []:
                filesList = ["You have not created any Projects."]                    
        elif path == "./Scenarios/":
            for dirItem in directoryList:
                    if dirItem.endswith((".cap", ".CAP")):
                        filesList.append(dirItem)
            if filesList == []:
                filesList = ["You have not created any Scenarios."]
        
        return filesList
    
    def parseProjectFile(self, filename):
        ''' A method to read various information from the project file '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().parseProjectFile()"
       
    def checkIfScenarioFilesExist(self):
        ''' 
            A method to verify that scenario files listed in the project's text file actually exist in the file system, 
            and warn the user if they do not.  This method also sets the 'Existing Scenario files" list widget to show 
            only files in the file system but not in the project, and sets the 'Scenario files in Project' only to show 
            files that are in the project's text file and actually exist in the file system.
        '''
    
        # debugging
        print "Main.manageprojects.DlgManageProjects().checkIfScenarioFilesExist()"
    
    def setCreateNewProjectMode(self):
        ''' A method to set the Manage Projects dialog configuration to create a new project. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().setCreateProjectMode()"
        
        # Populate the 'selectProjectComboBox' widget and set the displayed item to none.
        # This ComboBox is editable, so the user can enter a new project name.
        self.selectProjectComboBox.clear()
        self.selectProjectComboBox.addItems(self.listFiles(config.projectsPath))
        self.selectProjectComboBox.setCurrentIndex(0)
        
        # populate the 'Existing Scenario files' list widget
        self.existingScenarioFileList.clear()
        self.existingScenarioFileList.addItems(self.listFiles(config.scenariosPath))

        # Populate the 'Project Scenario files list' with a "newProjectMessage."
        if self.selectProjectComboBox.currentIndex() == 0:
            newProjectMessage = ["To create a new project,", "type a Project Name above,", "optionally add a scenario here,", "and click 'Save'"] 
            self.projectScenarioFileList.addItems(newProjectMessage)
        
    def checkIsProjectDirty(self):
        ''' A method to check if the user has modified the dialog values and warn about losing data. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().checkIsProjectDirty"
        
        
        
        
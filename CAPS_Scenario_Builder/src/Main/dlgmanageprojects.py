# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
#
# Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
#
#--------------------------------------------------------------------- 
# 
# Copyright (c) 2007-8 Qtrac Ltd.
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
import os, re, codecs, datetime #, shutil, time, os.path #  copy, subprocess, sys,  stat,
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
                
        ''' Set the initial dialog to display 'create a new project' mode ''' 
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
        '''
         Display the project information for the project selected in selectProjectComboBox. This method
         is called when the current item is changed in the selectProjectComboBox widget. 

        '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().displayProjectInfo"
        print "Project Name is: " + filename 
        
        
        # Convert the QString to unicode
        filename = unicode(filename)
        
        # If the user has chosen to 'Create a new project'
        if filename == "Create a new project (type name here)":
            # check if project is dirty and warn user then set the 'Create a new project' mode.
            self.checkIsProjectDirty()
            self.setCreateNewProjectMode()
            return
        
        # Parse the project file to set needed instance variables with project information.
        # This method warns the user and returns "False" if the read operation fails.
        path = config.projectsPath + filename
        print path
        if self.readProjectFile(path):
                        
            # Display the 'Sender's name:
            self.senderNameEdit.clear()
            self.senderNameEdit.setText(self.sender)
            
            # Display the 'Sender's email'
            self.sendersEmailEdit.clear()
            self.sendersEmailEdit.setText(self.senderEmail)
            
            # Display the date sent if it exists.
            if self.dateSent:
                self.dateSentLabel.clear()
                self.dateSentLabel.setText(self.dateSent)
            
            # Clear the list and populate the 'Existing Exported Scenarios' list widget 
            # with the existing exported scenario files that are NOT already in the project.
            self.existingScenarioFileList.clear()
            self.existingScenarioFileList.addItems(self.existingScenariosNotInProject)
            
            # Display the scenario files in the project (if they exist in the file system).
            # If there are no project scenario files then display the following message.
            if self.scenariosInProjectThatExist == []:
                noScenariosMessage = ["You have not added any Exported Scenarios."]
                self.projectScenarioFileList.clear()
                self.projectScenarioFileList.addItems(noScenariosMessage)
            else:
                self.projectScenarioFileList.clear()
                self.projectScenarioFileList.addItems(self.scenariosInProjectThatExist)
             
            # Display any saved message
            self.messageTextEdit.clear()
            self.messageTextEdit.setText(self.message)
                    
    def addScenarioToProject(self):
        ''' 
            Write the selected project name(s) from the "Existing Scenario files" list widget
            to the "Scenario files in Project" list widget. 
        '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().addScenarioToProject()"

        # Shorten the names of the QT list widgets
        existingList =  self.existingScenarioFileList
        projectList = self.projectScenarioFileList
        
        # if noting is selected in the list widget tell the user.
        if existingList.selectedItems() == [] or existingList.item(0).text() == "You have not created any Exported Scenarios.":
            QtGui.QMessageBox.warning(self, "Add Exported Scenario Error:", "You must select at least one Exported Scenario from the \
'Existing Exported Scenarios:' list before you can add an Exported Scenario to the project.")
        else:
            # If the 'new project' text was set then clear the projectScenarioFileList widget.             
            if projectList.item(0):
                if projectList.item(0).text() == "To create a new project," or projectList.item(0).text() == "You have not added any Exported Scenarios.":
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
        
        # Shorten the names of the QT list widgets
        existingList =  self.existingScenarioFileList
        projectList = self.projectScenarioFileList
        
        # if nothing is selected in the list widget tell the user.
        if (projectList.selectedItems() == [] or projectList.item(0).text() == "To create a new project,"
                                              or projectList.item(0).text() == "You have not added any Exported Scenarios."):
            QtGui.QMessageBox.warning(self, "Remove Exported Scenario Error:", "You must select at least one Exported Scenario from the \
'Exported Scenarios in Project:' list before you can remove an Exported Scenario from the project.")
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
                
        # validate the data input from the user
        if self.validateSaveData(""):
            
            # writeProjectFile() returns a valid file name
            projectFileName = self.writeProjectFile()
            
            # Block signals to prevent calling self.displayProjectInfo()
            self.selectProjectComboBox.blockSignals(True)
            
            # see if the project name is already in the combo box drop down menu
            index = self.selectProjectComboBox.findText(projectFileName, QtCore.Qt.MatchCaseSensitive)
            if index == -1: # -1 returned if item not found   
                # add the file name to the combo box
                self.selectProjectComboBox.addItem(projectFileName)
           
            # find the index and set the combo box to display the new projectFileName
            index = self.selectProjectComboBox.findText(projectFileName, QtCore.Qt.MatchCaseSensitive)
            self.selectProjectComboBox.setCurrentIndex(index)
            self.selectProjectComboBox.blockSignals(False)
        
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
        ''' Send the project file and associated Exported Scenario files to UMass via SFTP. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().sendProject()"
        
        # make sure to save project before sending.
        if self.validateSendData():
            projectFileName = self.writeProjectFile()
            
            #add sftp code here
            
            # once the project has been successfully sent, display it to show the date sent
            self.displayProjectInfo(projectFileName)
            
        
#################################################################################   
    ''' Core methods '''   
#################################################################################
    
    def writeProjectFile(self):
        ''' A method to write the project file to disk. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().writeProjectFile()"
       
        projectFileName = self.getProjectFileName()
        path = config.projectsPath + projectFileName
        now = datetime.datetime.now()
        print "The path is: " + path
        error = None
        fh = None
        
        try:
            fh = codecs.open(unicode(path), "w", "UTF-8")
            fh.write(u"-*- all files encoded using: utf-8 -*-\n")
            fh.write(u"{{SENDER}}: %s\n" % unicode(self.senderNameEdit.text()))
            fh.write(u"{{SENDER_EMAIL}}: %s\n" % unicode(self.sendersEmailEdit.text()))
            fh.write(u"{{PROJECT_NAME}}: %s\n" % unicode(self.selectProjectComboBox.currentText()))
            fh.write(u"{{DATE_SENT}}: %s\n" % unicode(now.strftime("%Y-%m-%d %H:%M")))
            projectList = self.projectScenarioFileList
            if projectList.item(0):
                text = unicode(projectList.item(0).text())
                print "text is: " + text
            if ((projectList.item(0) and text != "To create a new project,") and 
                (projectList.item(0) and text != "You have not added any Exported Scenarios.")):
                fh.write(u"{{SCENARIOS}}: ")
                for index in range(0, self.projectScenarioFileList.count()):
                    fh.write(u"%s, " % unicode(self.projectScenarioFileList.item(index).text()))
                fh.write(u"\n")
            else:
                fh.write(u"{{SCENARIOS}}:\n")
            fh.write(u"{{MESSAGE}}:\n" )
            fh.write(u"%s\n" % unicode(self.messageTextEdit.document().toPlainText()))
            fh.write(u"{{END_MESSAGE}}\n")        
        except (IOError, OSError), e:
            error = unicode(e)
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                print error
                QtGui.QMessageBox.warning(self, "Save Project Error: ", "The project file could not be written. \
Please check if a project file with the same name is already open and try again.")

        return projectFileName
    
    def readProjectFile(self, path):
        ''' A method to parse the project file to populate the widgets in this dialog. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().readProjectFile()"

        error = None
        fh = None
        try:
            # Mode "rU" opens as a text file as platform independent and all line terminations
            # are seen by Python as '\n'
            fh = codecs.open(unicode(path), "rU", "UTF-8")
            lino = 0
            while True:
                self.sender = self.senderEmail = self.projectName = self.dateSent = self.scenariosInProjectFile = self.message = None
                # line 1
                line = fh.readline()
                if not line:
                    break
                lino += 1
                if not line.startswith("-*- all files encoded using: utf-8 -*-"):
                    raise ValueError, "utf-8 header missing"
                
                # line 2 (this user QLineEdit input is limited to 75 characters and the QLineEdit does not accept newlines, \n)
                line = fh.readline()
                print "The line is: " + line
                if not line:
                    raise ValueError, "premature end of file"
                lino += 1
                if not line.startswith("{{SENDER}}:"):
                    raise ValueError, "sender is missing"
                else:
                    self.sender = line.strip("{{SENDER}}:")
                    
                # line 3 (this user QLineEdit input is limited to 75 characters and the QLineEdit does not accept newlines, \n)
                line = fh.readline()
                if not line:
                    raise ValueError, "premature end of file"
                lino += 1
                if not line.startswith("{{SENDER_EMAIL}}:"):
                    raise ValueError, "sender's email is missing"
                else:
                    self.senderEmail = line.strip("{{SENDER_EMAIL}}:")
                
                # line 4 (this user QLineEdit input is limited to 50 characters and the QLineEdit does not accept newlines, \n)
                line = fh.readline()
                if not line:
                    raise ValueError, "premature end of file"
                lino += 1
                if not line.startswith("{{PROJECT_NAME}}:"):
                    raise ValueError, "project name is missing"
                else:
                    self.projectName = line.strip("{{PROJECT_NAME}}:")
                
                # line 5 (the date is inserted by self.writeProjectFile() and is a text string)
                line = fh.readline()
                if not line:
                    raise ValueError, "premature end of file"
                lino += 1
                if not line.startswith("{{DATE_SENT}}:"):
                    raise ValueError, "date sent is missing"
                else:
                    self.dateSent = line.strip("{{DATE_SENT}}:")
                
                # line 6 (the scenarios in the project are written by self.writeProjectFile() and have no \n newlines)
                line = fh.readline()
                if not line:
                    raise ValueError, "premature end of file"
                lino += 1
                if not line.startswith("{{SCENARIOS}}:"):
                    raise ValueError, "scenarios is missing"
                else:
                    self.scenariosInProjectFile = line.strip("{{SCENARIOS}}:")
                
                # lines 7+ (this user input has no length limit and does accept newlines, \n)
                line = fh.readline()
                if not line:
                    raise ValueError, "premature end of file"
                lino += 1
                if not line.startswith("{{MESSAGE}}:"):
                    raise ValueError, "message header is missing"
                else:
                    self.message = ""
                    while True:
                        line = fh.readline()
                        lino += 1
                        if line == "{{END_MESSAGE}}\n":
                            if self.sender is None or self.senderEmail is None or self.projectName is None or self.dateSent is None or \
                                                    self.scenariosInProjectFile is None or self.message is None:
                                raise ValueError, "incomplete record"
                            break
                        else:
                            self.message += line
                break                
        except (IOError, OSError, ValueError), e:
            print "Failed to load: %s on line %d" % (e, lino)
            error = unicode(e)
            QtGui.QMessageBox.warning(self, "Read Project Error: ", "The project file could not be read. \
The error on line " + str(lino) + " is '" + error + "'.")
            if fh is not None:
                fh.close()
            return False

        # We are opening a project so check if all the Exported Scenario files listed in the project's text file
        # actually exist in the Exported Scenarios directory.  Also use this function to set the self.scenariosInProjectThatExist
        # and self.existingScenariosNotInProject variables
        self.checkIfScenarioFilesExist()
        return True
        
    def listFiles(self, path):
        ''' A method to return the list of Exported Scenarios files in the Exported Scenarios directory '''
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
                QtGui.QMessageBox.warning(self, "Read Directory Error:", "The files in the \
'Projects' or 'Exported Scenarios' directory could not be listed.  Please try again")
                return False
    
        if path == "./Projects/":
            filesList = ["Create a new project (type name here)"]
            for dirItem in directoryList:
                if dirItem.endswith((".cpj", ".CPJ")):
                    filesList.append(dirItem)
        elif path == "./Exported Scenarios/":
            for dirItem in directoryList:
                    if dirItem.endswith((".csv", ".CSV")):
                        filesList.append(dirItem)
            if filesList == []:
                filesList = ["You have not created any Exported Scenarios."]
        
        return filesList
    
    def checkIfScenarioFilesExist(self):
        ''' 
            A method to verify that Exported Scenarios listed in the project's text file actually exist in the file system, 
            and warn the user if they do not.  This method also sets the 'Existing Exported Scenarios" list widget to show 
            only files in the file system but not in the project, and sets the 'Exported Scenarios in Project' only to show 
            files that are in the project's text file and actually exist in the file system.
        '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().checkIfScenarioFilesExist()"
        
        # list the scenarios in the project but not in the file system and warn the user.
        
        
        # These two variables will be the variables used to populate the list widgets when an existing project is opened.
        self.scenariosInProjectThatExist = ["test"]
        self.existingScenariosNotInProject = ["test"]
    
    def setCreateNewProjectMode(self):
        ''' 
            A method to set the Manage Projects dialog configuration to create a new project. This method is called
            when the Manage Projects dialog is first loaded and whenever the user chooses 'Create new project' from 
            the selectProjectComboBox.
        '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().setCreateNewProjectMode()"
        
        # Clear the Sender's name, Sender's email, Date sent and any Messages.
        self.senderNameEdit.clear()
        self.sendersEmailEdit.clear()
        self.dateSentLabel.setText("Unsent")
        self.messageTextEdit.clear()
        
        # Block signals to prevent self.displayProject() from being called
        self.selectProjectComboBox.blockSignals(True)
        # Clear the 'selectProjectComboBox' in case the user has chosen 'Create a new project (type name here)' 
        # creating or viewing other projects.
        self.selectProjectComboBox.clear()
        # Populate the 'selectProjectComboBox' widget and set the displayed item to 'Create a new project (type name here)'
        # This ComboBox is editable, so the user can enter a new project name.
        self.listedProjectFiles = self.listFiles(config.projectsPath)
        self.selectProjectComboBox.addItems(self.listedProjectFiles)
        self.selectProjectComboBox.setCurrentIndex(0)
        # Turn signals back on
        self.selectProjectComboBox.blockSignals(False)
                
        # Clear the list and populate the 'Existing Scenario files' list widget
        self.existingScenarioFileList.clear()
        self.existingScenarioFileList.addItems(self.listFiles(config.scenarioExportsPath))

        # Populate the 'Project Scenario files list' with a "newProjectMessage."
        if self.selectProjectComboBox.currentIndex() == 0:
            newProjectMessage = ["To create a new project,", "fill in the text boxes above,", "optionally add a scenario here,", "and click 'Save'"] 
            self.projectScenarioFileList.clear()
            self.projectScenarioFileList.addItems(newProjectMessage)
        
    def checkIsProjectDirty(self):
        ''' A method to check if the user has modified the dialog values and warn about losing data. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().checkIsProjectDirty"
        
    def validateSaveData(self, informationText):
        ''' A method to validate the user inputs to the Manage Projects dialog when saving a project. '''
        #debugging
        print "Main.manageproject.DlgManageProjects().validateSaveData()"
      
        comboBoxText = unicode(self.selectProjectComboBox.currentText())
        if comboBoxText == "Create a new project (type name here)" or comboBoxText == "":
            informationText += "Please enter the 'Project name:'\n"
        if not self.validateFileName(comboBoxText):
            informationText += "Please limit your project name to letters, numbers and -_.()\n"
        if unicode(self.senderNameEdit.text()) == "":
            informationText += "Please enter the 'Sender's name:'\n"
        if not self.validateEmail(unicode(self.sendersEmailEdit.text())):
            informationText += "Please enter a valid email address.\n"
            
        if informationText:
            validateMessage = QtGui.QMessageBox()
            validateMessage.setMinimumWidth(400)
            validateMessage.setWindowTitle("Save Project Error:")
            validateMessage.setText(informationText)
            validateMessage.exec_()
        else: return True
            
    def validateSendData(self):
        ''' A method to validate the user inputs to the Manage Projects dialog when sending a project. '''        
        # debugging
        print "Main.manageproject.DlgManageProjects().validateSendData()"    
        
        projectList = self.projectScenarioFileList
        if projectList.item(0):
            text = unicode(projectList.item(0).text())
        
        # if the "Exported Scenarios in Project" list widget is empty, or the dialog is in "create a new project" mode, 
        # or if no scenario files have yet been added to the project then validation fails.
        if not projectList.item(0) or text ==  "To create a new project," or text == "You have not added any Exported Scenarios.":
            informationText = "Please add an Exported Scenario before sending.\n"
        else: informationText = ""

        # now  validate the remaining data needed to send.
        if self.validateSaveData(informationText):
            return True
        
    def validateEmail(self, email):
        ''' A method to validate email addresses. '''
        # debugging
        print "Main.manageproject.DlgManageProjects().validateEmail()"
        
        if re.match(r"^[a-zA-Z0-9._%-+]+\@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,}$", email) !=  None: 
            return True
        else: return False
        
    def validateFileName(self, fileName):
        ''' A method to ensure that a string is a valid file name. '''
        # debugging
        print "Main.manageproject.DlgManageProjects().validateFileName()"
        
        validCharacters = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        for c in fileName:
            if not c in validCharacters:
                return False
        return True
   
    def getProjectFileName(self):
        ''' Check for the '.cpj' or '.CPJ' file extension in the projectName and add it if missing. '''
        # debugging
        print "Main.dlgmanageprojects.DlgManageProjects.getProjectFileName()"
        
        
        projectName = self.selectProjectComboBox.currentText()
        if unicode(projectName).endswith((".cpj", ".CPJ")):
            return projectName
        else: return projectName + ".cpj"
            
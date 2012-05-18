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
import os, re, codecs, datetime, string
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
        
        # This turns off auto complete in the selectProjectComboBox
        completer = QtGui.QCompleter()
        self.selectProjectComboBox.setCompleter(completer)
                
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
        
        
        
        # The user is changing the displayed project or has selected the option to create a new project.
        # In either case, the data displayed in the dialog will be lost. The isProjectDirty() method prompts
        # the user if the project is dirty and returns True if they decide to cancel.
        if self.isProjectDirty():
            # need to reset the Project name: combo box to "filename"
            return
        else:
            # Convert the QString to unicode
            filename = unicode(filename)
           
            # If the user has chosen to 'Create a new project'
            if filename == "Create a new project (type name here)":
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
                    self.dateSentTextLabel.clear()
                    self.dateSentTextLabel.setText(self.dateSent)
                else:
                    self.dateSentTextLabel.clear()
                    self.dateSentTextLabel.setText("Unsent")
                
                # Clear the list and populate the 'Existing Exported Scenarios' list widget 
                # with the existing exported scenario files that are NOT already in the project.
                self.existingScenarioFileList.clear()
                self.existingScenarioFileList.addItems(self.existingScenariosNotInProject)
                
                # Display the scenario files in the project (if they exist in the file system).
                # If there are no project scenario files then display the following message.
                if self.scenariosInProjectThatExist == []:
                    noScenariosMessage = ["You have not added Scenarios."]
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
        if existingList.selectedItems() == [] or existingList.item(0).text() == "There are no Exported Scenarios.":
            QtGui.QMessageBox.warning(self, "Add Exported Scenario Error:", "You must select at least one Exported Scenario from the \
'Existing Exported Scenarios:' list before you can add an Exported Scenario to the project.")
        else:
            # If the 'new project' text was set then clear the projectScenarioFileList widget.             
            if projectList.item(0):
                if projectList.item(0).text() == "To create a new project," or projectList.item(0).text() == "You have not added Scenarios.":
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
                                              or projectList.item(0).text() == "You have not added Scenarios."):
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
                
        if self.dateSentTextLabel.text() != 'Unsent':
            QtGui.QMessageBox.warning(self, "Send Project Error: ", "This project has already been send to UMass, and cannot be changed.")
            return
        
        # Validate the data input from the user. This method warns the user on bad data and returns True if data is OK
        if self.validateSaveData(""):
            
            # Now that we have a valid project name get the name of the file to be written from the
            # self.selectProjectComboBox.  This method adds the ".cpj" extension if it is not already there.
            projectFileName = self.getProjectFileName()
            
            # writeProjectFile() warns user on write error and returns True on successful write operation.
            if self.writeProjectFile(projectFileName):
                
                # Now that the file is successfully written update the self.selectProjectComboBox
                # because the file extension may have been added to the project name. 
                # There is no need to read the project file to update  the other dialog fields, 
                # since they were just saved with current values.
                self.refreshSelectProjectComboBox(projectFileName)
         
    def deleteProject(self, button):
        ''' Delete the current project file and leave the dialog open. '''
        # debugging
        if unicode(button.text()) == "Discard":
            print "Main.manageprojects.DlgManageProjects().deleteProject()"
            
            if self.dateSentTextLabel.text() != 'Unsent':
                QtGui.QMessageBox.warning(self, "Delete Project Error: ", "This project has already been send to UMass, \
and should not be discarded. If you really want to delete it, please search for it and remove by using your operating system.")
                return
            
            # Get the name of the file to delete and create the path.
            projectFileName = unicode(self.selectProjectComboBox.currentText())
            path = config.projectsPath + projectFileName
            
            if projectFileName != "Create a new project (type name here)":
                try:
                    os.remove(path)
                except (IOError, OSError), e:
                    print e
                    QtGui.QMessageBox.warning(self, "Discard Project Error: ", "The project file could not be deleted \
from the file system. Please check if the project file is open in another program and try again.")
                    return
                # set the dialog to create new project mode to reflect that the file is deleted.
                self.setCreateNewProjectMode()

    def reject(self):
        ''' User clicked the "Cancel" button. '''
        # debugging
        
        print "Main.manageprojects.DlgManageProjects().reject(): user closed the dialog"
        self.hide()
        
    def sendProject(self):
        ''' Send the project file and associated Exported Scenario files to UMass via SFTP. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().sendProject()"
        
        # Check if the date sent is set and if it is warn and 
        if self.dateSentTextLabel.text() != 'Unsent':
            QtGui.QMessageBox.warning(self, "Send Project Error: ", "This project has already been sent to UMass.")
            return
        
        # Make sure to validate the data before sending. This method warns the user on bad data and returns True if data is OK.
        if self.validateSendData():
            
            # Now that we have a valid project name get the name of the file to be written from the 
            # self.selectProjectComboBox. This method adds the ".cpj" extension if it is not already there.
            projectFileName = self.getProjectFileName()
            
            # The user may have created a new project and clicked 'Send' without saving first, or
            # the user may have opened an existing project and modified it before sending.  Rather
            # than check if the project is dirty and prompt the user to save, we just save the project.
            # writeProjectFile() warns user on write error and returns True on successful write operation.
            # The "True" parameter is a "sendFlag" to tell the method to write the "DATE_SENT" to the project file.
            if self.writeProjectFile(projectFileName, True):
                
                # Now send the project
                #add sftp code here
                                
                # once the project has been successfully sent, display it to show the date sent.
                self.displayProjectInfo(projectFileName)
            
        
#################################################################################   
    ''' Core methods '''   
#################################################################################
    
    def writeProjectFile(self, projectFileName, sendFlag=False):
        ''' A method to write the project file to disk. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().writeProjectFile()"
       
        path = config.projectsPath + projectFileName
        now = datetime.datetime.now()
        
        #debugging
        print "Main.manageprojects.DlgManageProjects().writeProjectFile(): The path is " + path
        error = None
        fh = None
        
        try:
            fh = codecs.open(unicode(path), "w", "UTF-8")
            fh.write(u"-*- all files encoded using: utf-8 -*-\n")
            fh.write(u"{{SENDER}}: %s\n" % unicode(self.senderNameEdit.text()))
            fh.write(u"{{SENDER_EMAIL}}: %s\n" % unicode(self.sendersEmailEdit.text()))
            fh.write(u"{{PROJECT_NAME}}: %s\n" % unicode(self.selectProjectComboBox.currentText()))
            # Only write the date sent if the file is being sent.
            if sendFlag:
                fh.write(u"{{DATE_SENT}}: %s\n" % unicode(now.strftime("%Y-%m-%d %H:%M")))
            else: fh.write(u"{{DATE_SENT}}: ")
            projectList = self.projectScenarioFileList
            if projectList.item(0):
                text = unicode(projectList.item(0).text())
            if ((projectList.item(0) and text != "To create a new project,") and 
                (projectList.item(0) and text != "You have not added Scenarios.")):
                fh.write(u"{{SCENARIOS}}: ")
                cnt = self.projectScenarioFileList.count()
                for index in range(0, cnt):
                    if index == cnt - 1:
                        fh.write(u"%s" % unicode(self.projectScenarioFileList.item(index).text()))
                    else: fh.write(u"%s, " % unicode(self.projectScenarioFileList.item(index).text()))
                fh.write(u"\n")
            else:
                fh.write(u"{{SCENARIOS}}: \n")
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
                return False
        return True
    
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
                if not line:
                    raise ValueError, "premature end of file"
                lino += 1
                if not line.startswith("{{SENDER}}:"):
                    raise ValueError, "sender is missing"
                else:
                    self.sender = line.lstrip("{{SENDER}}: ").strip()

                # line 3 (this user QLineEdit input is limited to 75 characters and the QLineEdit does not accept newlines, \n)
                line = fh.readline()
                if not line:
                    raise ValueError, "premature end of file"
                lino += 1
                if not line.startswith("{{SENDER_EMAIL}}:"):
                    raise ValueError, "sender's email is missing"
                else:
                    self.senderEmail = line.lstrip("{{SENDER_EMAIL}}: ").strip()
                
                # line 4 (this user QLineEdit input is limited to 50 characters and the QLineEdit does not accept newlines, \n)
                line = fh.readline()
                if not line:
                    raise ValueError, "premature end of file"
                lino += 1
                if not line.startswith("{{PROJECT_NAME}}:"):
                    raise ValueError, "project name is missing"
                else:
                    self.projectName = line.lstrip("{{PROJECT_NAME}}: ").strip()
                
                # line 5 (the date is inserted by self.writeProjectFile() and is a text string)
                line = fh.readline()
                if not line:
                    raise ValueError, "premature end of file"
                lino += 1
                if not line.startswith("{{DATE_SENT}}:"):
                    raise ValueError, "date sent is missing"
                else:
                    self.dateSent = line.lstrip("{{DATE_SENT}}: ").strip()
                
                # line 6 (the scenarios in the project are written by self.writeProjectFile() and have no \n newlines)
                line = fh.readline()
                if not line:
                    raise ValueError, "premature end of file"
                lino += 1
                if not line.startswith("{{SCENARIOS}}:"):
                    raise ValueError, "scenarios is missing"
                else:
                    self.scenariosInProjectFile = line.lstrip("{{SCENARIOS}}: ").strip()
                
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
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False   

        # We are opening a project so check if all the Exported Scenario files listed in the project's text file
        # actually exist in the Exported Scenarios directory.  Also use this function to set the self.scenariosInProjectThatExist
        # and self.existingScenariosNotInProject variables
        projectFileName = os.path.basename(path)
        self.checkIfScenarioFilesExist(projectFileName)
        return True
        
    def listFiles(self, path):
        ''' 
            A method to return the list of Exported Scenarios files in the Exported Scenarios directory. This method is 
            called by self.setCreateNewProjectMode whenever the Manage Projects dialog is first opened or if 
            'Create a new project (type name here)' is selected from the "Project name:" combo box.  This method is also
            called by self.saveProject() to update the "Project name:" combo box after saving a new project.
        '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().listFiles()"
        print "Main.manageprojects.DlgManageProjects().listFiles(): The path is " + path
        
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
                filesList = ["There are no Exported Scenarios."]
        
        return filesList
    
    def checkIfScenarioFilesExist(self, projectFileName):
        ''' 
            A method to verify that Exported Scenarios listed in the project's text file actually exist in the file system, 
            and warn the user if they do not.  This method also creates the 'Existing Exported Scenarios" list to show 
            files existing in the file system but not in the project, and creates the 'Exported Scenarios in Project' list to show 
            files that are in the project's text file and actually exist in the file system. This method is called by
            self.readProjectFile() whenever a project is opened.
        '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().checkIfScenarioFilesExist()"
        
        # Get a current list of the exported scenarios in the file system. 
        allExportedScenarios = self.listFiles(config.scenarioExportsPath)
        
        # Convert the unicode string self.scenariosInProjectFile into a simple string and then
        # to a Python list.  Unicode strings are preceded by 'u' when converted into a list.
        scenariosInProjectFileList = str(self.scenariosInProjectFile).split(', ')
        
        # list the scenarios in the project but not in the file system and warn the user if there are some missing.
        missingScenarios = [scenario for scenario in scenariosInProjectFileList if scenario not in allExportedScenarios] 

        # create a string from the list to display in the message box
        ms = ','.join(missingScenarios)
        
        if ms: 
            QtGui.QMessageBox.warning(self, "Missing Files Error: ", "The exported scenario(s) (" + ms + ") \
listed in " + projectFileName + " no longer exist in the Exported Scenarios directory and will not be displayed as part of \
the project.  You may have moved or deleted them.  If you can locate them and put them in the Exported Scenarios directory \
you may close the 'Manage Projects' dialog and then try to open the project again.  If you no longer want the missing scenarios \
in the project, just save the project as it is displayed to overwrite the old project file.")
        
        # Create the list of scenarios in the project that actually exist in the file system.
        self.scenariosInProjectThatExist = list(set(scenariosInProjectFileList) - set(missingScenarios))
        
        # Create the list of scenarios that are in the file system but not in the project
        self.existingScenariosNotInProject = list(set(allExportedScenarios) - set(self.scenariosInProjectThatExist))
    
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
        self.dateSentTextLabel.setText("Unsent")
        self.messageTextEdit.clear()
        
        # Refresh the combo box to ensure the list of projects is current, or to set
        # it if the dialog is being opened.
        self.refreshSelectProjectComboBox(None, True)
        
        # Clear the list and populate the 'Existing Scenario files' list widget
        self.existingScenarioFileList.clear()
        self.existingScenarioFileList.addItems(self.listFiles(config.scenarioExportsPath))

        # Populate the 'Project Scenario files list' with a "newProjectMessage."
        if self.selectProjectComboBox.currentIndex() == 0:
            newProjectMessage = ["To create a new project,", "fill in the text boxes above,", "optionally add a scenario here,", "and click 'Save'"] 
            self.projectScenarioFileList.clear()
            self.projectScenarioFileList.addItems(newProjectMessage)
        
    def isProjectDirty(self):
        ''' A method to check if the user has modified the dialog values and warn about losing data. '''
        # debugging
        print "Main.manageprojects.DlgManageProjects().isProjectDirty"
        
        # First check if the project is set to create project mode and return False if it is.
        return False
        
        # Then check the value of each field against the instance variables set in readProjectFile,
        # and prompt if they are not. If the user clicks OK return False, othewise return True.
        data = 'good'
        if data == 'bad':
            text = "You are taking an action that will cause the \
data you have entered to be lost. If you want to save the data, click 'Cancel.'  To continue click 'OK.'"
            reply = QtGui.QMessageBox.question(self, "Confirm", text, QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Ok)
            
            # User has chosen to continue
            if reply == QtGui.QMessageBox.Ok: 
                return False
            else: return True
        
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
        if not projectList.item(0) or text ==  "To create a new project," or text == "You have not added Scenarios.":
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
        
    def refreshSelectProjectComboBox(self, projectFileName, createFlag=False):
        ''' 
            Update the self.selectProjectComboBox with the files existing in the "Projects" directory.
            This method is called by self.setCreateNewProjectMode()and self.saveProject().
        '''
        # debugging
        print "Main.dlgmanageprojects.DlgManageProjects.refreshSelectProjectComboBox()"    
            
        # Block signals to prevent calling self.displayProjectInfo()
        self.selectProjectComboBox.blockSignals(True)
        
        # Clear the list of old items.
        self.selectProjectComboBox.clear()
        
        # Get the current file list from the directory because the user can always add or delete files
        # by using operating system functions.
        self.selectProjectComboBox.addItems(self.listFiles(config.projectsPath))
       
        if createFlag:
            self.selectProjectComboBox.setCurrentIndex(0)
        else: 
            # find the index and set the combo box to display the new projectFileName
            index = self.selectProjectComboBox.findText(projectFileName, QtCore.Qt.MatchCaseSensitive)
            self.selectProjectComboBox.setCurrentIndex(index)
        
        # Unblock the signals
        self.selectProjectComboBox.blockSignals(False)    
            
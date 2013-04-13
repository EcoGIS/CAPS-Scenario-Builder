# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
#
# Conservation Assessment and Prioritization System (CAPS) Scenario Builder - An Open Source  
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
# general python imports
#import  os, re, codecs, datetime, traceback, sys
# import Qt libraries
from PyQt4 import QtCore, QtGui
# import the ui made with Qt Designer
from dlgsftpproperties_ui import Ui_DlgSftpProperties
# CAPS Scenario Builder application imports
import config
#import Tools.shared


class DlgSftpProperties(QtGui.QDialog, Ui_DlgSftpProperties):
    """ Open a dialog to create, copy, edit, or send projects """
    def __init__(self, mainwindow):
        QtGui.QDialog.__init__(self, mainwindow)
        self.setupUi(self)

        # debugging
        print "Main.dlgsftpproperties.DlgSftpProperties class"
        
        # Since this dialog should be rarely used, if it is opened we destroy it rather than hide it on closing.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.mainwindow = mainwindow

        # Populate the dialog with the settings stored in the windows registry
        # settings = QtCore.QSettings()
        self.hostEdit.setText(self.mainwindow.sftpHost)
        self.userEdit.setText(self.mainwindow.sftpUser)
        self.passwordEdit.setText(self.mainwindow.sftpPassword)
        self.pathEdit.setText(self.mainwindow.sftpPath)

        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)

#################################################################################
    ''' Custom slots '''
################################################################################  

    def accept(self):
        ''' User clicked the "OK" button. '''
        # debugging
        print "Main.dlgsftpproperties.DlgSftpProperties.reject(): user closed the dialog"
        
        # The user has clicked OK, so store the settings in the registry and they will be used for sftp settings when the app loads.
        settings = QtCore.QSettings()
        settings.setValue("sftpHost", self.hostEdit.text())
        settings.setValue("sftpUser", self.userEdit.text())
        settings.setValue("sftpPassword", self.passwordEdit.text())
        settings.setValue("sftpPath", self.pathEdit.text())
        
        # reset the instance variables that are used in dlgmanageprojects.DlgManageProjects.sftpUpload() to make connections.
        self.mainwindow.sftpHost = unicode(self.hostEdit.text())
        self.mainwindow.sftpUser = unicode(self.userEdit.text())
        self.mainwindow.sftpPassword = unicode(self.passwordEdit.text())
        self.mainwindow.sftpPath = unicode(self.pathEdit.text())

        QtGui.QDialog.accept(self)


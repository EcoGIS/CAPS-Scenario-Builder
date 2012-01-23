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

from PyQt4 import QtCore, QtGui
# CAPS application imports
import config

class DlgAddAttributes(QtGui.QDialog):
    def __init__(self, mainwindow):
        QtGui.QDialog.__init__(self, mainwindow)
        
        # get a handle to the main window
        self.mainwindow = mainwindow
        # get the list of Scenario Types from mainwindow
        scenarioEditTypesList = config.scenarioEditTypesList
        # get the current user-chosen scenarioEditType from mainwindow 
        scenarioEditType = self.mainwindow.scenarioEditType
        
        # debugging
        print "DlgAddAttributes class initiated: scenario type is " + scenarioEditType
     
        # Get the lists of field labels, combobox drop down values, and 
        # input field names for the current scenarioEditType.
        self.fieldLabels = [] # labels for the combo box
        self.comboBoxOptions = [] # values in the combobox drop down menu that the user can choose
        self.inputFieldNames = [] # all the field names needing input for the current scenario type
        i = 0
        while i < len(scenarioEditTypesList):
            if scenarioEditTypesList[i] == scenarioEditType:
                self.fieldLabels = eval("config.fieldLabels" + unicode(i))
                self.comboBoxOptions = eval("config.comboBoxOptions" + unicode(i))
                self.inputFieldNames = eval("config.inputFieldNames" + unicode(i))
                break
            i += 1
        else:
            print "Scenario Edit Type not found"

#######################################################################
        ''' Dynamically create the "Add Attributes" dialog '''
#######################################################################  

        self.setObjectName("dlgAddAttributes")
        self.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
 
        # dynamically create the field labels and input line edits
        # from the labels list for the current scenario type
        self.labelWidgets = [0]*len(self.fieldLabels)
        self.comboBoxWidgets = [0]*len(self.fieldLabels)
        self.spacerItems = [0]*len(self.fieldLabels)
        for c, label in enumerate(self.fieldLabels):
            # associate the field name with the widget names 
            # for easy reference to these objects
            labelName = unicode("Label" + str(c))
            comboBoxName = unicode("ComboBox" + str(c))
            #lineEditName = unicode(self.fieldsLabels[self.count] + "LineEdit")
            
            # make each label widget          
            self.labelWidgets[c] = QtGui.QLabel(self)
            self.labelWidgets[c].setObjectName(labelName)
            self.labelWidgets[c].setText(label)
            self.gridLayout.addWidget(self.labelWidgets[c], c, 0, 1, 1)
            
            # make each combo box
            self.comboBoxWidgets[c] = QtGui.QComboBox(self)
            self.comboBoxWidgets[c].setEditable(True)
            self.comboBoxWidgets[c].setObjectName(comboBoxName)
            self.comboBoxWidgets[c].addItems(self.comboBoxOptions[c])
            self.gridLayout.addWidget(self.comboBoxWidgets[c], c, 1, 1, 1)
            #self.lineEditName = QtGui.QLineEdit(self)
            #self.lineEditName.setObjectName(lineEditName)
            #self.gridLayout.addWidget(self.lineEditName, self.count, 1, 1, 1)
            
            self.spacerItems[c] = QtGui.QSpacerItem(120, 20, QtGui.QSizePolicy.Expanding,
                                                                QtGui.QSizePolicy.Minimum)
            self.gridLayout.addItem(self.spacerItems[c], c, 3, 1, 1)
            
            # debugging
            print labelName
            print comboBoxName
            print "count is " + str(c)
        print "The final count is + " + str(c)
      
        # every scenario type change needs a description line edit input
        self.labelDescription = QtGui.QLabel(self)
        self.labelDescription.setObjectName("labelDescription")
        self.labelDescription.setText("Description:")
        self.gridLayout.addWidget(self.labelDescription, c+1, 0, 1, 1)
        self.lineEditDescription = QtGui.QLineEdit(self)
        self.lineEditDescription.setObjectName("lineEditDescription")
        self.gridLayout.addWidget(self.lineEditDescription, c+1, 1, 1, 1)
        spacerItem100 = QtGui.QSpacerItem(120, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem100, c+1, 3, 1, 1)
        # finally, add the buttons and spacers for the buttons
        spacerItem200 = QtGui.QSpacerItem(20, 120, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem200, c+2, 3, 1, 1)
        spacerItem300 = QtGui.QSpacerItem(175, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem300, c+3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, c+3, 2, 1, 2)
        self.setWindowTitle("Add Attributes: " + scenarioEditType)
        
        # These connections close the dialog
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        # These connections connect to the methods in this class
        QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"), self.apply)
        QtCore.QObject.connect(self, QtCore.SIGNAL("rejected()"), self.cancel)
        QtCore.QMetaObject.connectSlotsByName(self)

#######################################################################
    ''' Custom Slots '''
#######################################################################    
    
    def apply(self):
        pass
    
    def accept(self):
        # debugging 
        print "accept()"
        # validation 
        
        for widget in self.comboBoxWidgets:
            print "the length of comboBoxWidgets is " + str(len(self.comboBoxWidgets))
            print "current text is " + widget.currentText()
            if not widget.currentText():
                QtGui.QMessageBox.warning(self, "Value Error:", "You must enter a \
value for every item except the 'Description':") 
                return
        QtGui.QDialog.accept(self)
        
    def cancel(self):
        # debugging
        print "DlgAddAttributes.cancel()"
        if self.mainwindow.toolAddLinesPolygons.rubberBand:
            self.mainwindow.toolAddLinesPolygons.resetDraw()
        #return True
    
#######################################################################
    ''' Core Method '''
#######################################################################

    def getNewAttributes(self, modifyFlag = False):
        # debugging
        print "DlgAddAttributes.getNewAttributes()"
        print "The modifyFlag is " + str(modifyFlag)
        
        geom = self.mainwindow.geom # geometry of the active layer

        # get the editFields for the current editing shapefile
        editFields = self.mainwindow.getEditFields()
        
        # debugging
        print "The editing fields are " + str(editFields)
        
        # Get the field values from the "Add Attributes" dialog.
        # note: We need to set all the field values in the editing layer,
        # even those that are not used by the current scenario type change. 
        a = {} # Python dictionary of attributes for the current editing layer
        subListCount = 1
        i = 0
        for count, field in enumerate(editFields):
            # Fields that are in the editing shapefile but are not used for  
            # the current scenario type are set to empty values here.
            if field not in self.inputFieldNames:
                a[count] = QtCore.QVariant()
                print "not in field names k = " + str(count)
                continue
            # set the id field first, will be renumbered later
            if subListCount == 1:
                a[count] = QtCore.QVariant(1)
                subListCount = 2
                print "first field (id) k = " + str(count)
                continue
            # if a point layer, set the altered and deleted fields
            if geom == 0 and subListCount == 2:
                if modifyFlag: a[count] = QtCore.QVariant("y")
                else: a[count] = QtCore.QVariant("n")
                subListCount = 3
                print "second field (altered) k = " + str(count)
                continue
            if geom == 0 and subListCount == 3:
                a[count] = QtCore.QVariant("n")
                subListCount = 4
                print "third field (deleted) k = " + str(count)
                continue
            # Finally, set the values for the user input fields     
            if subListCount < len(self.inputFieldNames):
                text = unicode(self.comboBoxWidgets[i].currentText())
                # returns the value associated with the option chosen by the user
                value = text[:text.find('-')-1]
                # value = self.valuesDictionaryList[i].get(text)
                print "The type is "
                print "is value a string? " + str(isinstance(value, str))
                print "Value is " + value
                print "The index for this item is " + str(self.comboBoxWidgets[i].currentIndex())
                a[count] = QtCore.QVariant(value)
                subListCount += 1
                i += 1
                print "user input field k = " + str(count)
                print unicode(text)
                continue
            else:
                # this is the last field for all scenario types, the description field
                a[count] = QtCore.QVariant(self.lineEditDescription.text())
                print "user input field count = " + str(count)
                print "Description Field"
        return a
   
    
            
            
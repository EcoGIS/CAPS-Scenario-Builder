# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
#
# Conservation Assessment and Prioritization System (CAPS) Scenario Builder - An Open Source  
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
# PyQt4 includes for python bindings to QT
from PyQt4 import QtCore, QtGui
# CAPS Scenario Builder application imports
import config
import shared

class DlgAddAttributes(QtGui.QDialog):
    ''' Create the dialog to get needed attribute data from users '''
    def __init__(self, mainwindow):
        QtGui.QDialog.__init__(self, mainwindow)
        
        # get a handle to the main window
        self.mainwindow = mainwindow
        # get the list of Scenario Types from mainwindow
        scenarioEditTypesList = config.scenarioEditTypesList
        # get the current user-chosen scenarioEditType from mainwindow 
        scenarioEditType = self.mainwindow.scenarioEditType
        
        # debugging
        print "Tools.dlgaddattributes.DlgAddAttributes() class initiated: scenario type is " + scenarioEditType
     
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
            print "Tools.dlgaddattributes.DlgAddAttributes(): Scenario Edit Type not found"

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
            #self.comboBoxWidgets[c].setEditable(True)
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
            print "Tools.dlgaddattributes.DlgAddAttributes(): Label Name is: " + labelName
            print "Tools.dlgaddattributes.DlgAddAttributes(): comboBoxName is: " + comboBoxName
            print "Tools.dlgaddattributes.DlgAddAttributes(): count is " + str(c)
        print "Tools.dlgaddattributes.DlgAddAttributes(): The final count is + " + str(c)
      
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
        print "Tools.dlgaddattributes.DlgAddAttributes().accept()"
        # validation 
        
        for widget in self.comboBoxWidgets:
            print "Tools.dlgaddattributes.DlgAddAttributes().accept(): the length of comboBoxWidgets is " + str(len(self.comboBoxWidgets))
            print "Tools.dlgaddattributes.DlgAddAttributes().accept(): current text is " + widget.currentText()
            if not widget.currentText():
                QtGui.QMessageBox.warning(self, "Value Error:", "You must enter a \
value for every item except the 'Description':") 
                return
        QtGui.QDialog.accept(self)
        
    def cancel(self):
        # debugging
        print "Tools.dlgaddattributes.DlgAddAttributes().cancel()"
        
        if self.mainwindow.toolAddLinesPolygons.rubberBand:
            self.mainwindow.toolAddLinesPolygons.resetDraw()
    
    def reject(self):
        # debugging
        print "Tools.dlgaddattributes.DlgAddAttributes().reject()"
        
        if not self.mainwindow.msgFlag:
            QtGui.QDialog.reject(self)
            return

        if self.mainwindow.msgFlag == "baselayer":
            title = "Modify Features Warning"
            text = "If you click 'Yes' in this dialog, any modifications you have made \
will be lost. If you still want to modify base layer features, you will will need to start over. Do you \
want to stop modifying features?"
        elif self.mainwindow.msgFlag == "userlayer":
            title = "Paste Features Warning"
            text = "If you click 'Yes' in this dialog, any features you have pasted \
will be lost. If you still want to paste features, you will will need to start over. Do you \
want to stop pasting?"
        elif self.mainwindow.msgFlag == "editlayer": # just for clarity
            title = "Modify Features Warning"
            text = "If you click 'Yes' in this dialog, any edit layer modifications you have already \
made will be saved, but any remaining features you have selected will not be modified. If \
you still want to modify the remaining features, you will will need to select them again and choose \
'Modify Features'. Do you want to stop modifying features?"
        reply = QtGui.QMessageBox.warning(self, title, text, 
                                                    QtGui.QMessageBox.No|QtGui.QMessageBox.Yes)
        
        if reply == QtGui.QMessageBox.No:
            # in effect cancels the "Cancel"
            return
        else: QtGui.QDialog.reject(self) # returns false to self.mainwindow.dlgAddAtts.exec_()
     
#######################################################################
    ''' Core Method '''
#######################################################################

    def getNewAttributes(self, modifyFlag = False):
        # debugging
        print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes()"
        print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): The modifyFlag is " + str(modifyFlag)
        
        geom = self.mainwindow.geom # geometry of the active layer

        # get the editFields for the current editing shapefile
        editFields = self.mainwindow.getEditFields(geom)
        
        # debugging
        print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): The editing fields are " + str(editFields)
        
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
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): not in field names k = " + str(count)
                continue
            # set the id field first, will be renumbered later
            if subListCount == 1:
                a[count] = QtCore.QVariant(1)
                subListCount = 2
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): first field (id) k = " + str(count)
                continue
            # if a point layer, set the altered and deleted fields
            if geom == 0 and subListCount == 2:
                if modifyFlag: a[count] = QtCore.QVariant("y")
                else: a[count] = QtCore.QVariant("n")
                subListCount = 3
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): second field (altered) k = " + str(count)
                continue
            if geom == 0 and subListCount == 3:
                a[count] = QtCore.QVariant("n")
                subListCount = 4
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): third field (deleted) k = " + str(count)
                continue
            # Finally, set the values for the user input fields
            # Convert QStrings to unicode unless they are used immediately in a Qt method. 
            # This ensures that we never ask Python to slice a QString, which produces a type error.     
            if subListCount < len(self.inputFieldNames):
                text = unicode(self.comboBoxWidgets[i].currentText())
                # returns the value associated with the option chosen by the user
                value = text[:text.find('-')-1]
                # value = self.valuesDictionaryList[i].get(text)
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): The type is "
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): is value a string? " + str(isinstance(value, str))
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): Value is " + value
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): The index for this item is " + str(self.comboBoxWidgets[i].currentIndex())
                a[count] = QtCore.QVariant(value)
                subListCount += 1
                i += 1
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): user input field k = " + str(count)
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): " + unicode(text)
                continue
            else:
                # this is the last field for all scenario types, the description field
                a[count] = QtCore.QVariant(self.lineEditDescription.text())
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): user input field count = " + str(count)
                print "Tools.dlgaddattributes.DlgAddAttributes().getNewAttributes(): Description Field"
        return a
   
    
            
            
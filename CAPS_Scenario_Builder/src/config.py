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
#-----------------------------------------------------------------------

# import Qt libraries
from PyQt4.QtGui import QColor
# import qgis API
from qgis.core import QgsCoordinateReferenceSystem, QgsRectangle

############################################################################################
''' APPLICATION CONFIGURATION '''
############################################################################################
''' 
The following are variables that might change over time.
They can be altered throughout the application by changing values here.

Changing field labels, field values and field names will be reflected in the 'Add Attributes' dialog
and the editing shapefiles created for the 7 scenario edit types. Note that the numbers 0-6 in the 
variable names below each correspond to a single scenario edit type.  For example, the number 0 corresponds
to the 'Culverts/bridges (points)' scenario edit type in all variables below.  The remaining numbers are in the
order that the scenario edit types appear in the 'Edit Scenario' dialog.  Although you cannot add a new scenario
edit type, you can add, remove or edit combination box labels, combination boxes and combination box dropdown
choices in "Add Attributes" dialog for each scenario edit type.  When doing this, you must also add a new field
to the attribute table for the editing shapefile corresponding to that scenario edit type.  Each section has a 
more detailed explanation below. 
  
''' 
   
# Paths to important files.  
# These cannot change for most users without altering the application installer.
# Sophisticated users who have a version of caps.exe that allows access to config.py can move these folders and change
# the paths to the new locations here.  The paths may be relative or absolute.

#baseLayersPath =  'C:/egit_repositories/CAPS-Scenario-Builder/CAPS_Scenario_Builder/src/base_layers/'
baseLayersPath =  './base_layers/'
#scenariosPath = 'C:/egit_repositories/CAPS-Scenario-Builder/CAPS_Scenario_Builder/src/Scenarios/' 
scenariosPath = './Scenarios/' 
#projectsPath = 'C:/Projects'
projectsPath = './Projects/'
#scenarioExportsPath = 'C:/Exported Scenarios/' 
scenarioExportsPath = './Exported Scenarios/'


''' Field names, which appear in the editing layer attribute table, for each scenario edit type. '''     
# To change the data users input into the application in the 'Add Attributes' dialog,
# a new field name for the editing shapefile attribute table must be inserted,
# in the correct position, in the corresponding list here. Each field name must be unique,
# so I recommend staying with the convention of a letter and underscore preceding any
# newly inserted field name.
# Please note that you MUST NOT delete or change the list position of the id, 
# altered, deleted or description field names. The values for these fields are added 
# programmatically and depend on their positions in the list.
inputFieldNames0 = ['cross_id', 'c_altered', 'c_deleted', 'c_aqua_scr', 'c_terr_scr', 'c_describe'] 
inputFieldNames1 = ['dam_id', 'd_altered', 'd_deleted', 'd_aqua_scr', 'd_describe']
inputFieldNames2 = ['wildlf_id', 'w_altered', 'w_deleted', 'w_terr_scr', 'w_describe']
inputFieldNames3 = ['restr_id', 'r_altered', 'r_deleted', 'r_rest_scr', 'r_describe']
inputFieldNames4 = ['newrd_id', 'newrd_rate', 'nrd_class', 'nrd_descr']
inputFieldNames5 = ['modrd_id', 'modrd_rate', 'nrd_class', 'mrd_descr']
inputFieldNames6 = ['ldcvr_id', 'ldcvr_cls', 'l_describe']


''' Labels for the combo boxes in the 'Add Attributes' dialog '''
# If you add a new field label here, it will create a corresponding combo box
# in the 'Add Attributes' dialog for the corresponding scenarioEditType. A new 'field values' 
# list for the new combobox's drop down list must also be added below. In addition, 
# you must add a new field name to the fieldNames list above, so the field will be 
# added to the editing layer attribute table when it is created on the fly. 
# Finally, you need to add the values to be entered in the attribute table to the valuesDictionaryList. 
# THE ORDER WITHIN THE LISTS IS CRITICAL, SINCE THEY ARE LOOPED THROUGH AND MATCHED
# Of course, any old scenarios the user has stored that use the editing layer that 
# has been modified will become obsolete.  The users would need to be notified of this.
fieldLabels0 = ['Aquatic crossing score:', 'Terrestrial crossing score:']
fieldLabels1 = ['Aquatic crossing score:']
fieldLabels2 = ['Terrestrial crossing score:']
fieldLabels3 = ['Tidal Restriction severity:']
fieldLabels4 = ['New road traffic rate:', 'New road class:'] 
fieldLabels5 = ['Modified road traffic rate:', 'New road class:']
fieldLabels6 = ['Land cover class:']


''' Field values for the comboBox dropdown lists '''
# If a fieldLabel is added above, a python list [] of field values for the
# new combobox must be added, in the proper position, to the corresponding 
# 'list of lists' here. These will appear in the dropdown list for the comboboxes
# corresponding to the scenario edit type. Each integer appended
#  to 'comboBoxOptions' represents a scenario edit type.  Each scenario
# edit type must have a dropdown list for each comboBox needed for that edit type.  Thus we 
# have a 'list of lists' for each edit type
comboBoxOptions0 = [['', '1.0 - Full passage', '0.8 - Minor barrier', '0.6 - Moderate barrier', 
                 '0.4 - Significant barrier', '0.2 - Severe barrier'], ['', '1.0 - Full passage (bear, moose)', 
                 '0.75 - Large animals (fox, coyote, fisher, bobcat, otter)', 
                 '0.5 - Medium animals (rabbit, skunk, mink, opossum, raccoon)', 
                 '0.2 - Small animals (amphibians, reptiles, mice, voles, chipmunk, weasel)', 
                 '0.0 - No passage structure']]
comboBoxOptions1 = [['', '0.6 - Fishway/breached dam', '0.2 - Eel passage only', '0.0 - Full barrier']]
comboBoxOptions2 = [['', '1.0 - Full passage (bear, moose)', 
                 '0.75 - Large animals (fox, coyote, fisher, bobcat, otter)', 
                 '0.5 - Medium animals (rabbit, skunk, mink, opossum, raccoon)', 
                 '0.2 - Small animals (amphibians, reptiles, mice, voles, chipmunk, weasel)', 
                 '0.0 - No passage structure']]
comboBoxOptions3 = [['', '0.0 m - No restriction', '0.5 m - Minor restriction', 
                 '1.0 m - Moderate restriction', '2.0 m - Severe restriction']]
comboBoxOptions4 = [['','0.0 - none(closed road; 0 cars/day)', '0.025 - very low(tiny road; 100 cars/day)',
                 '0.2 - low(minor road; 800 cars/day)', '0.5 - medium(collector; 2500 cars/day)',
                 '0.75 - medium-high(secondary highway; 5000 cars/day)', 
                 '0.94 - high(primary highway; 10,000 cars/day)',  '1.0 - extreme(expressway; >40,000 cars/day)'],
                   ['', '81 - Expressway', '82 - Primary highway', '83 - Secondary highway', '84 - Light duty road',
                   '85 - Unpaved road', '90 - Railroad', '91 - Abandoned railbed', '92 - Rail trail']] 
comboBoxOptions5 = [['','0.0 - none(closed road; 0 cars/day)', '0.025 - very low(tiny road; 100 cars/day)',
                '0.2 - low(minor road; 800 cars/day)', '0.5 - medium(collector; 2500 cars/day)',
                '0.75 - medium-high(secondary highway; 5000 cars/day)', 
                '0.94 - high(primary highway; 10,000 cars/day)', 
                '1.0 - extreme(expressway; >40,000 cars/day)'], ['', '81 - Expressway', '82 - Primary highway', 
                '83 - Secondary highway', '84 - Light duty road', '85 - Unpaved road', '90 - Railroad', 
                '91 - Abandoned railbed', '92 - Rail trail']]
comboBoxOptions6 = [['', '1 - Commercial', '2 - Industrial', '3 - Urban open', '4 - Urban public ', 
                     '5 - Transportation ', '6 - Mining', '7 - Waste disposal', '8 - Junkyard', 
                     '10 - Multi-family  residential', '11 - High-density residential', 
                     '12 - Medium-density residential', '13 - Low-density residential', 
                     '20 - Spectator recreation', '21 - Participatory recreation', 
                     '22 - Golf', '23 - Water based recreation ', '24 - Marina', 
                     '30 - Cropland', '31 - Cranberry bog ', '32 - Nursery', '33 - Orchard', 
                     '34 - Cemetery', '35 - Pasture', '36 - Powerline shrubland', '37 - Open land', 
                     '40 - Forest', '41 - Deciduous forested wetland', '42 - Mixed forested wetland', 
                     '43 - Coniferous forested wetland', '44 - Shrub swamp', '45 - Bog', '46 - Shallow marsh', 
                     '47 - Deep marsh', '48 - Vernal pool', '55 - Pond', '56 - Lake', '60 - Sea cliff', 
                     '61 - Vegetated dune ', '62 - Coastal dune', '63 - Coastal beach', '70 - Salt marsh', 
                     '71 - Tidal flat', '72 - Rocky intertidal', '75 - Salt pond/bay']]

# This Python dictionary is used to look up values for the identify tool.  If new values are added to the 'base_land' raster,
# they should also be added here with the corresponding description.
baseLandLookup = {1: 'Commercial', 2: 'Industrial', 3: 'Urban open', 4: 'Urban public ', 
                  5: 'Transportation', 6: 'Mining', 7: 'Waste disposal', 8: 'Junkyard', 
                 10: 'Multi-family  residential', 11: 'High-density residential', 
                 12: 'Medium-density residential', 13: 'Low-density residential', 
                 20: 'Spectator recreation', 21: 'Participatory recreation', 
                 22: 'Golf', 23: 'Water based recreation ', 24: 'Marina', 
                 30: 'Cropland', 31: 'Cranberry bog ', 32: 'Nursery', 33: 'Orchard', 
                 34: 'Cemetery', 35: 'Pasture', 36: 'Powerline shrubland', 37: 'Open land', 
                 40: 'Forest', 41: 'Deciduous forested wetland', 42: 'Mixed forested wetland', 
                 43: 'Coniferous forested wetland', 44: 'Shrub swamp', 45: 'Bog', 46: 'Shallow marsh', 
                 47: 'Deep marsh', 48: 'Vernal pool', 50: 'Water (lentic)', 51: 'Water(loic)', 55: 'Pond', 
                 56: 'Lake', 60: 'Sea cliff', 61: 'Vegetated dune', 62: 'Coastal dune', 63: 'Coastal beach', 
                 70: 'Salt marsh', 71: 'Tidal flat', 72: 'Rocky intertidal', 74: 'Ocean', 75: 'Salt pond/bay',
                 81: 'Expressway', 82: 'Primary highway', 83: 'Secondary highway', 84: 'Light duty road', 
                 90: 'Railroad', 91: 'Abandoned raibed', 92: 'Rail trail', 95: 'Bridge/culvert', 96: 'Dam'}

# If the raster value falls between the two numbers in baseTrafficKeys[x] then displayed value is baseTrafficValues[x]
# these numbers and values can be modified as needed as long is there is a one-to-one correspondence in order.
baseTrafficValues = [[-1, 0], [1, 60], [61, 121], [122, 182], [183, 244], [245, 255]]
baseTrafficDisplay = ['No road', 'Unpaved road', 'Light duty road', 'Secondary highway', 'Primary highway', 'Expressway']

''' The fields lists for the three editing shapefiles '''
# no changes should be made to the code under this heading
editPointsFields = (inputFieldNames0 + inputFieldNames1
                         + inputFieldNames2 + inputFieldNames3) # 21 fields
editLinesFields = inputFieldNames4 # 4 fields
editPolygonsFields = inputFieldNames5 + inputFieldNames6 # 7 fields

# The list of scenario edit types for populating the 'Edit Scenario' dialog.
# Changing these values will only change the names shown in the 'ScenarioEditTypes' dialog
# Adding a value here will NOT create a new scenario type complete with base layers
# and editing shapefile fields.
scenarioEditTypesList = ['Culverts/bridges (points)', 'Dams (points)',  
                          'Terrestrial passage structures (points)', 'Tidal restrictions (points)',
                          'Add roads (lines)', 'Modify roads (polygons)',       
                          'Land cover change (polygons)']

# This list is used to open the proper constraint layer for the scenario edit type
scenarioConstraintLayersBaseNames = ['base_streams', 'base_traffic']
scenarioConstraintLayersFileNames = ['base_streams.tif', 'base_traffic.tif']


# The below are used in various places to check that correct layers are active for editing operations.
# The spelling of these names can be changed, but not the number or order of them.
pointBaseLayersBaseNames = ['base_culverts_bridges', 'base_dams', 'base_terrestrial_passage',
                             'base_tidal_restrictions']
pointBaseLayersFileNames = ['base_culverts_bridges.shp', 'base_dams.shp', 'base_terrestrial_passage.shp',
                             'base_tidal_restrictions.shp']
polygonBaseLayersBaseNames = ['base_traffic', 'base_land']
polygonBaseLayersFileNames   = ['base_traffic.tif', 'base_land.tif']

# This is used to warn users of slow loading attribute tables.
slowLoadingLayers = ['base_culverts_bridges']

# names of just the editing layers (used in Main.legend.removeCurrentLayer()
# and Main.mainwindow.deleteFeatures()).  These should not be changed unless
# major changes are made to the application.
editLayersBaseNames = ['edit_scenario(points)', 'edit_scenario(lines)',
                       'edit_scenario(polygons)']
editLayersFileNames = ['edit_scenario(points).shp', 'edit_scenario(lines).shp',
                       'edit_scenario(polygons).shp']

# These are the lists of layers that open when the app is first opened
# or when the 'New Scenario' action is clicked.  The orienting layers that
# open can be changed by changing the lists below, assuming they exist in the 
# config.baseLayersPath folder. Layers open in the order they appear in the lists.
# Raster layers open before vector layers, and the layers will be stacked in 
# the opening order with the first layer opened on the bottom in the layer panel 
# (i.e. legend).
orientingRasterLayers = ['USGS.SID', 'base_land.tif', 'base_streams.tif', 'base_traffic.tif']
orientingVectorLayers = ['base_towns.shp']
orientingVectorLayersBaseNames = ['base_towns']
allOrientingLayers = orientingRasterLayers + orientingVectorLayers

# Orienting base layer names can be added here to make them visible (i.e. checked) when they are opened.
orientingLayersChecked = ['base_towns']

# A list of the non-orienting base layers and editing layers. 
# Main.dlgscenarioedittypes.hideEditBaseLayers() uses this list to hide (uncheck) unneeded layers.
# Adding a name to this list will hide (uncheck) that layer if not needed when opening a
# new scenario edit type. 
hideEditLayers = ['edit_scenario(points)', 'edit_scenario(lines)',
                  'edit_scenario(polygons)', 'base_culverts_bridges', 'base_dams',
                  'base_terrestrial_passage', 'base_tidal_restrictions', 'base_traffic', 'base_streams']


############################################################################################
''' Configuration variables that need to be executed to be set '''

def setDefaultColors():
    # debugging
    print "config.setDefaultColors()"
    
    defaultColors = [QColor('darkorange'), QColor('fuchsia'), QColor('blueviolet'), QColor('lime'), 
                    QColor('mediumorchid'),QColor('plum'), QColor('aqua')]
                    
    return defaultColors

def setCrs():
    # debugging
    print "config.setCrs()"
    
    # MA State Plane coordinate system used by MassGIS
    crs = QgsCoordinateReferenceSystem(26986, QgsCoordinateReferenceSystem.EpsgCrsId)
    return crs

def setExtentMA():
    # debugging
    print "config.setExtentMA"
    extentMA = QgsRectangle(26000, 747000, 350000, 989000)
    return extentMA
